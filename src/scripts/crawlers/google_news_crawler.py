#!/usr/bin/env python3
"""
구글 뉴스 크롤러 v1.0
======================
Google News에서 STEEPS 카테고리별 뉴스 수집

기능:
- STEEPS 키워드 기반 검색
- 국가/언어별 필터링
- RSS 피드 및 직접 크롤링 지원
- 24시간 이내 뉴스 필터링

Usage:
    python google_news_crawler.py --category Technological --max 20
    python google_news_crawler.py --all-categories --max 10
    python google_news_crawler.py --query "AI breakthrough" --max 15
    python google_news_crawler.py --country KR --language ko --max 20
"""

import argparse
import json
import random
import time
from datetime import datetime, timedelta
from typing import ClassVar
from urllib.parse import quote_plus

try:
    import requests

    # SSL 경고 억제 (Google News SSL 인증서 문제 대응)
    import urllib3
    from bs4 import BeautifulSoup

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    print("필요한 패키지를 설치해주세요: pip install requests beautifulsoup4")
    exit(1)

try:
    import feedparser

    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False
    print("[WARN] feedparser 없음 - RSS 기능 제한됨. pip install feedparser")


class GoogleNewsCrawler:
    """구글 뉴스 크롤러"""

    # Google News RSS 기본 URL
    RSS_BASE: ClassVar[str] = "https://news.google.com/rss"
    SEARCH_RSS: ClassVar[str] = "https://news.google.com/rss/search"

    # STEEPS 카테고리별 검색 키워드
    STEEPS_KEYWORDS: ClassVar[dict[str, list[str]]] = {
        "Social": [
            "population crisis",
            "demographic shift",
            "mental health crisis",
            "education reform",
            "social inequality",
            "aging society",
            "인구 위기",
            "고령화 사회",
            "교육 혁신",
            "사회 변화",
            "Gen Z trends",
            "workforce transformation",
            "remote work",
        ],
        "Technological": [
            "AI breakthrough",
            "quantum computing",
            "robotics advancement",
            "semiconductor chip",
            "autonomous vehicle",
            "space technology",
            "인공지능 혁신",
            "양자컴퓨터",
            "로봇 기술",
            "반도체",
            "GPT",
            "neural network",
            "biotech innovation",
        ],
        "Economic": [
            "global economy",
            "inflation rate",
            "interest rate decision",
            "stock market crash",
            "cryptocurrency regulation",
            "trade war",
            "경제 전망",
            "금리 인상",
            "주식시장",
            "무역분쟁",
            "startup funding",
            "venture capital",
            "IPO",
        ],
        "Environmental": [
            "climate change",
            "renewable energy",
            "carbon emission",
            "extreme weather",
            "biodiversity loss",
            "net zero",
            "기후변화",
            "탄소중립",
            "재생에너지",
            "환경오염",
            "ESG investment",
            "green technology",
            "sustainable",
        ],
        "Political": [
            "geopolitical tension",
            "election result",
            "policy reform",
            "international sanctions",
            "military conflict",
            "trade agreement",
            "지정학 리스크",
            "정책 변화",
            "국제관계",
            "안보",
            "democracy",
            "government regulation",
            "diplomacy",
        ],
        "Spiritual": [
            "mindfulness trend",
            "wellness industry",
            "meditation",
            "religious movement",
            "ethical AI",
            "meaning of life",
            "명상",
            "웰니스",
            "영성",
            "종교 트렌드",
            "work-life balance",
            "mental wellness",
            "spiritual health",
        ],
    }

    # User-Agent 로테이션
    USER_AGENTS: ClassVar[list[str]] = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]

    # 국가 코드 매핑
    COUNTRY_CODES: ClassVar[dict[str, dict[str, str]]] = {
        "KR": {"hl": "ko", "gl": "KR", "ceid": "KR:ko"},
        "US": {"hl": "en-US", "gl": "US", "ceid": "US:en"},
        "GB": {"hl": "en-GB", "gl": "GB", "ceid": "GB:en"},
        "JP": {"hl": "ja", "gl": "JP", "ceid": "JP:ja"},
        "CN": {"hl": "zh-CN", "gl": "CN", "ceid": "CN:zh-Hans"},
        "DE": {"hl": "de", "gl": "DE", "ceid": "DE:de"},
        "FR": {"hl": "fr", "gl": "FR", "ceid": "FR:fr"},
    }

    def __init__(self, delay: float = 1.0, country: str = "US"):
        self.delay = delay
        self.country = country
        self.session = requests.Session()
        self.collected_articles = []
        self.errors = []

    def _get_headers(self) -> dict[str, str]:
        """랜덤 User-Agent 헤더 반환"""
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def _fetch_page(self, url: str) -> str | None:
        """페이지 HTML 가져오기"""
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=15, allow_redirects=True)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.errors.append(f"Fetch error for {url}: {e!s}")
            return None

    def _build_search_url(self, query: str, country: str | None = None) -> str:
        """검색 RSS URL 생성"""
        country = country or self.country
        params = self.COUNTRY_CODES.get(country, self.COUNTRY_CODES["US"])

        encoded_query = quote_plus(query)
        url = f"{self.SEARCH_RSS}?q={encoded_query}&hl={params['hl']}&gl={params['gl']}&ceid={params['ceid']}"

        return url

    def _parse_rss_feed(self, url: str) -> list[dict]:
        """RSS 피드 파싱 (requests로 먼저 가져온 후 feedparser로 파싱)"""
        if not HAS_FEEDPARSER:
            return []

        try:
            # SSL 인증서 문제 우회: requests로 먼저 가져온 후 feedparser로 파싱
            response = self.session.get(url, headers=self._get_headers(), timeout=15, verify=False)
            if response.status_code != 200 or not response.text.strip():
                return []

            feed = feedparser.parse(response.text)
            articles = []

            for entry in feed.entries:
                # 발행일 파싱
                published = entry.get("published", "")
                try:
                    pub_date = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %Z")
                    pub_date_str = pub_date.strftime("%Y-%m-%d")
                except Exception:
                    pub_date_str = datetime.now().strftime("%Y-%m-%d")

                # 소스 추출
                source = entry.get("source", {})
                source_name = source.get("title", "Google News") if isinstance(source, dict) else "Google News"

                articles.append(
                    {
                        "title": entry.get("title", ""),
                        "url": entry.get("link", ""),
                        "summary": self._clean_html(entry.get("summary", entry.get("description", ""))),
                        "source_name": source_name,
                        "published_date": pub_date_str,
                        "published_raw": published,
                    }
                )

            return articles
        except Exception as e:
            self.errors.append(f"RSS parse error for {url}: {e!s}")
            return []

    def _clean_html(self, html: str) -> str:
        """HTML 태그 제거"""
        if not html:
            return ""
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        return text[:500]

    def _is_recent(self, pub_date: str, hours: int = 168) -> bool:
        """최근 N시간 이내인지 확인 (기본: 7일)"""
        try:
            pub = datetime.strptime(pub_date, "%Y-%m-%d")
            cutoff = datetime.now() - timedelta(hours=hours)
            return pub >= cutoff.replace(hour=0, minute=0, second=0)
        except Exception:
            return True  # 파싱 실패 시 포함

    def search_news(self, query: str, max_items: int = 10, country: str | None = None) -> list[dict]:
        """키워드로 뉴스 검색"""
        print(f"  [INFO] 검색: '{query[:30]}...' (최대 {max_items}건)")

        url = self._build_search_url(query, country)
        articles = self._parse_rss_feed(url)

        if not articles:
            # RSS 실패 시 직접 크롤링 시도
            articles = self._crawl_search_page(query, country)

        # 최근 기사만 필터링
        recent_articles = [a for a in articles if self._is_recent(a.get("published_date", ""))]

        return recent_articles[:max_items]

    def _crawl_search_page(self, query: str, country: str | None = None) -> list[dict]:
        """직접 크롤링 (RSS 실패 시 대체)"""
        country = country or self.country
        params = self.COUNTRY_CODES.get(country, self.COUNTRY_CODES["US"])

        encoded_query = quote_plus(query)
        url = f"https://news.google.com/search?q={encoded_query}&hl={params['hl']}&gl={params['gl']}"

        html = self._fetch_page(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # Google News의 기사 링크 패턴
        for article in soup.select("article")[:20]:
            title_elem = article.select_one("h3, h4")
            link_elem = article.select_one('a[href^="./articles/"]')

            if title_elem and link_elem:
                title = title_elem.get_text(strip=True)
                href = link_elem.get("href", "")

                if href.startswith("./"):
                    href = "https://news.google.com" + href[1:]

                articles.append(
                    {
                        "title": title,
                        "url": href,
                        "summary": "",
                        "source_name": "Google News",
                        "published_date": datetime.now().strftime("%Y-%m-%d"),
                    }
                )

        return articles

    def search_by_category(self, category: str, max_per_keyword: int = 5) -> list[dict]:
        """STEEPS 카테고리별 검색"""
        if category not in self.STEEPS_KEYWORDS:
            print(f"[ERROR] 지원하지 않는 카테고리: {category}")
            return []

        print(f"\n[INFO] {category} 카테고리 검색 시작")

        keywords = self.STEEPS_KEYWORDS[category]
        all_articles = []
        seen_titles = set()

        for keyword in keywords:
            time.sleep(self.delay)
            articles = self.search_news(keyword, max_per_keyword)

            for art in articles:
                # 중복 제거 (제목 기준)
                title_key = art.get("title", "")[:50].lower()
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    art["category_hint"] = category
                    art["search_keyword"] = keyword
                    all_articles.append(art)

        print(f"  → {category} 총 수집: {len(all_articles)}건")
        return all_articles

    def search_all_categories(self, max_per_keyword: int = 3) -> list[dict]:
        """전체 STEEPS 카테고리 검색"""
        all_articles = []

        for category in self.STEEPS_KEYWORDS:
            articles = self.search_by_category(category, max_per_keyword)
            all_articles.extend(articles)

        return all_articles

    def search_trending(self, country: str | None = None, max_items: int = 20) -> list[dict]:
        """트렌딩 뉴스 수집"""
        country = country or self.country
        params = self.COUNTRY_CODES.get(country, self.COUNTRY_CODES["US"])

        print(f"\n[INFO] {country} 트렌딩 뉴스 수집")

        # 트렌딩 RSS
        url = f"{self.RSS_BASE}?hl={params['hl']}&gl={params['gl']}&ceid={params['ceid']}"
        articles = self._parse_rss_feed(url)

        for art in articles:
            art["category_hint"] = self._guess_category(art.get("title", ""))
            art["search_keyword"] = "trending"

        return articles[:max_items]

    def _guess_category(self, title: str) -> str:
        """제목에서 카테고리 추측"""
        title_lower = title.lower()

        # 키워드 매칭으로 카테고리 추측
        category_patterns = {
            "Technological": ["ai", "tech", "robot", "quantum", "chip", "software", "digital", "cyber"],
            "Economic": ["economy", "market", "stock", "trade", "inflation", "gdp", "bank", "finance"],
            "Political": ["election", "government", "policy", "war", "military", "president", "minister"],
            "Environmental": ["climate", "carbon", "energy", "green", "emission", "weather", "environment"],
            "Social": ["health", "education", "population", "society", "community", "culture"],
            "Spiritual": ["wellness", "mindful", "meditation", "religion", "spiritual", "mental health"],
        }

        for category, keywords in category_patterns.items():
            for kw in keywords:
                if kw in title_lower:
                    return category

        return "Social"  # 기본값

    def to_raw_format(self, articles: list[dict], date: str) -> dict:
        """환경스캐닝 표준 형식으로 변환"""
        date_compact = date.replace("-", "")

        # STEEPS 카테고리별 카운트
        by_category = {}
        items = []

        for idx, art in enumerate(articles, 1):
            category = art.get("category_hint", "Social")

            if category not in by_category:
                by_category[category] = 0
            by_category[category] += 1

            raw_id = f"RAW-GOOGLE-{date_compact}-{idx:03d}"

            items.append(
                {
                    "raw_id": raw_id,
                    "title": art.get("title", ""),
                    "url": art.get("url", ""),
                    "source_name": art.get("source_name", "Google News"),
                    "source_type": "news_aggregator",
                    "published_date": art.get("published_date", date),
                    "category_hint": category,
                    "summary": art.get("summary", ""),
                    "search_keyword": art.get("search_keyword", ""),
                    "key_entities": [],
                    "language": "en",
                    "scanned_at": datetime.now().isoformat() + "+09:00",
                }
            )

        return {
            "scan_date": date,
            "scan_time": datetime.now().strftime("%H:%M:%S"),
            "source": "google_news_crawler_v1",
            "total_scanned": len(items),
            "by_category": by_category,
            "items": items,
        }


def main():
    parser = argparse.ArgumentParser(description="구글 뉴스 크롤러")
    parser.add_argument("--category", help="특정 STEEPS 카테고리 검색")
    parser.add_argument("--all-categories", action="store_true", help="전체 STEEPS 카테고리 검색")
    parser.add_argument("--query", help="직접 검색어 입력")
    parser.add_argument("--trending", action="store_true", help="트렌딩 뉴스 수집")
    parser.add_argument("--country", default="US", help="국가 코드 (US, KR, GB, JP, CN, DE, FR)")
    parser.add_argument("--max", type=int, default=10, help="카테고리/키워드당 최대 기사 수")
    parser.add_argument("--delay", type=float, default=1.0, help="요청 간 딜레이 (초)")
    parser.add_argument("--output", help="출력 파일")
    parser.add_argument("--raw-format", action="store_true", help="환경스캐닝 형식으로 출력")
    parser.add_argument("--list-categories", action="store_true", help="지원 카테고리 목록")

    args = parser.parse_args()

    print("=" * 60)
    print("구글 뉴스 크롤러 v1.0 - 환경스캐닝 시스템")
    print("=" * 60)

    crawler = GoogleNewsCrawler(delay=args.delay, country=args.country)

    if args.list_categories:
        print("\n지원 STEEPS 카테고리:")
        for cat, keywords in crawler.STEEPS_KEYWORDS.items():
            print(f"\n{cat}:")
            for kw in keywords[:5]:
                print(f"  - {kw}")
            print(f"  ... ({len(keywords)}개 키워드)")
        return

    # 크롤링 실행
    articles = []

    if args.query:
        articles = crawler.search_news(args.query, args.max)
        for art in articles:
            art["category_hint"] = crawler._guess_category(art.get("title", ""))
            art["search_keyword"] = args.query
    elif args.category:
        articles = crawler.search_by_category(args.category, args.max)
    elif args.all_categories:
        articles = crawler.search_all_categories(args.max)
    elif args.trending:
        articles = crawler.search_trending(args.country, args.max)
    else:
        print("\n사용법:")
        print("  --all-categories --max 5    : 전체 STEEPS 카테고리 검색")
        print("  --category Technological    : 특정 카테고리 검색")
        print("  --query 'AI breakthrough'   : 직접 검색")
        print("  --trending                  : 트렌딩 뉴스")
        print("  --list-categories           : 카테고리 목록")
        return

    print(f"\n총 {len(articles)}건 수집 완료")

    # 출력
    today = datetime.now().strftime("%Y-%m-%d")

    result = crawler.to_raw_format(articles, today) if args.raw_format else {"total": len(articles), "items": articles}

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"결과 저장: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
        if len(str(result)) > 2000:
            print("\n... (결과 생략, --output으로 파일 저장 권장)")

    # 오류 보고
    if crawler.errors:
        print(f"\n[WARN] {len(crawler.errors)}건의 오류 발생:")
        for err in crawler.errors[:5]:
            print(f"  - {err}")


if __name__ == "__main__":
    main()
