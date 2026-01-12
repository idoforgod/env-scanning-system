#!/usr/bin/env python3
"""
글로벌 뉴스 크롤러 v1.0
========================
6개 국가 주요 신문 뉴스 크롤링

지원 국가/신문:
- Korea: 조선일보, 중앙일보, 한겨레, 동아일보, 한국경제
- USA: NYT, WaPo, WSJ, LA Times, USA Today
- UK: Guardian, The Times, FT, Telegraph, Independent
- China: SCMP, Global Times, Caixin, China Daily, Sixth Tone
- Japan: Japan Times, Nikkei, Asahi, Yomiuri, Mainichi
- Saudi Arabia: Arab News, Saudi Gazette, Al Arabiya, Asharq Al-Awsat, Argaam

Usage:
    python global_news_crawler.py --country usa --max 10
    python global_news_crawler.py --all-countries --max 5
    python global_news_crawler.py --paper "The Guardian" --max 15
"""

import argparse
import json
import random
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("필요한 패키지를 설치해주세요: pip install requests beautifulsoup4")
    exit(1)


class GlobalNewsCrawler:
    """글로벌 뉴스 크롤러 - 6개국 주요 신문"""

    # 국가별 신문 설정
    NEWSPAPERS = {
        "korea": {
            "조선일보": {
                "url": "https://www.chosun.com",
                "rss": None,
                "selectors": {
                    "articles": "a[href*='/article/']",
                    "title": "h1, .article-title",
                    "content": ".article-body, .news-content",
                },
                "steeps": ["Political", "Economic", "Social"],
                "language": "ko",
            },
            "중앙일보": {
                "url": "https://www.joongang.co.kr",
                "rss": "https://rss.joins.com/joins_news_list.xml",
                "selectors": {"articles": "a[href*='/article/']", "title": "h1.headline", "content": ".article_body"},
                "steeps": ["Political", "Economic", "Social"],
                "language": "ko",
            },
            "한겨레": {
                "url": "https://www.hani.co.kr",
                "rss": "https://www.hani.co.kr/rss/",
                "selectors": {"articles": "a[href*='/arti/']", "title": "h4.title, h1", "content": ".article-text"},
                "steeps": ["Political", "Social"],
                "language": "ko",
            },
            "동아일보": {
                "url": "https://www.donga.com",
                "rss": None,
                "selectors": {"articles": "a[href*='/news/']", "title": "h1.title", "content": ".article_txt"},
                "steeps": ["Political", "Economic"],
                "language": "ko",
            },
            "한국경제": {
                "url": "https://www.hankyung.com",
                "rss": "https://www.hankyung.com/feed/all-news",
                "selectors": {"articles": "a[href*='/article/']", "title": "h1.headline", "content": "#articletxt"},
                "steeps": ["Economic", "Technological"],
                "language": "ko",
            },
        },
        "usa": {
            "The New York Times": {
                "url": "https://www.nytimes.com",
                "rss": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
                "selectors": {"articles": "a[href*='/202']", "title": "h1", "content": "article p"},
                "steeps": ["Political", "Economic", "Social", "Technological"],
                "language": "en",
            },
            "The Washington Post": {
                "url": "https://www.washingtonpost.com",
                "rss": None,
                "selectors": {"articles": "a[href*='/202']", "title": "h1", "content": "article p"},
                "steeps": ["Political", "Economic"],
                "language": "en",
            },
            "The Wall Street Journal": {
                "url": "https://www.wsj.com",
                "rss": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
                "selectors": {"articles": "a[href*='/articles/']", "title": "h1", "content": "article p"},
                "steeps": ["Economic", "Political", "Technological"],
                "language": "en",
            },
            "Los Angeles Times": {
                "url": "https://www.latimes.com",
                "rss": "https://www.latimes.com/rss2.0.xml",
                "selectors": {"articles": "a[href*='/story/']", "title": "h1", "content": ".page-article-body p"},
                "steeps": ["Political", "Social", "Environmental"],
                "language": "en",
            },
            "USA Today": {
                "url": "https://www.usatoday.com",
                "rss": "http://rssfeeds.usatoday.com/usatoday-NewsTopStories",
                "selectors": {"articles": "a[href*='/story/']", "title": "h1", "content": "article p"},
                "steeps": ["Political", "Social"],
                "language": "en",
            },
        },
        "uk": {
            "The Guardian": {
                "url": "https://www.theguardian.com",
                "rss": "https://www.theguardian.com/world/rss",
                "selectors": {
                    "articles": "a[href*='/202']",
                    "title": "h1",
                    "content": ".article-body-viewer-selector p",
                },
                "steeps": ["Political", "Environmental", "Social"],
                "language": "en",
            },
            "The Times": {
                "url": "https://www.thetimes.com",
                "rss": None,
                "selectors": {"articles": "a[href*='/article/']", "title": "h1", "content": "article p"},
                "steeps": ["Political", "Economic"],
                "language": "en",
            },
            "Financial Times": {
                "url": "https://www.ft.com",
                "rss": None,
                "selectors": {"articles": "a[href*='/content/']", "title": "h1", "content": ".article__body p"},
                "steeps": ["Economic", "Political", "Technological"],
                "language": "en",
            },
            "The Telegraph": {
                "url": "https://www.telegraph.co.uk",
                "rss": "https://www.telegraph.co.uk/rss.xml",
                "selectors": {"articles": "a[href*='/news/']", "title": "h1", "content": "article p"},
                "steeps": ["Political", "Economic"],
                "language": "en",
            },
            "The Independent": {
                "url": "https://www.independent.co.uk",
                "rss": "https://www.independent.co.uk/rss",
                "selectors": {"articles": "a[href*='/news/']", "title": "h1", "content": "#main p"},
                "steeps": ["Political", "Social"],
                "language": "en",
            },
        },
        "china": {
            "South China Morning Post": {
                "url": "https://www.scmp.com",
                "rss": "https://www.scmp.com/rss/91/feed",
                "selectors": {"articles": "a[href*='/article/']", "title": "h1", "content": ".article__body p"},
                "steeps": ["Political", "Economic", "Technological"],
                "language": "en",
            },
            "Global Times": {
                "url": "https://www.globaltimes.cn",
                "rss": None,
                "selectors": {"articles": "a[href*='/page/']", "title": "h3, h1", "content": ".article p"},
                "steeps": ["Political", "Economic"],
                "language": "en",
            },
            "Caixin Global": {
                "url": "https://www.caixinglobal.com",
                "rss": None,
                "selectors": {"articles": "a[href*='/202']", "title": "h1", "content": ".article-content p"},
                "steeps": ["Economic", "Technological"],
                "language": "en",
            },
            "China Daily": {
                "url": "https://www.chinadaily.com.cn",
                "rss": "https://www.chinadaily.com.cn/rss/world_rss.xml",
                "selectors": {"articles": "a[href*='/a/']", "title": "h1", "content": "#Content p"},
                "steeps": ["Political", "Economic"],
                "language": "en",
            },
            "Sixth Tone": {
                "url": "https://www.sixthtone.com",
                "rss": None,
                "selectors": {"articles": "a[href*='/news/']", "title": "h1", "content": ".article-content p"},
                "steeps": ["Social", "Political"],
                "language": "en",
            },
        },
        "japan": {
            "The Japan Times": {
                "url": "https://www.japantimes.co.jp",
                "rss": "https://www.japantimes.co.jp/feed/",
                "selectors": {"articles": "a[href*='/news/']", "title": "h1", "content": ".article-body p"},
                "steeps": ["Political", "Economic", "Social"],
                "language": "en",
            },
            "Nikkei Asia": {
                "url": "https://asia.nikkei.com",
                "rss": "https://asia.nikkei.com/rss/feed/nar",
                "selectors": {"articles": "a[href*='/']", "title": "h1", "content": ".article__body p"},
                "steeps": ["Economic", "Technological"],
                "language": "en",
            },
            "Asahi Shimbun": {
                "url": "https://www.asahi.com/ajw/",
                "rss": None,
                "selectors": {"articles": "a[href*='/articles/']", "title": "h1", "content": ".ArticleText p"},
                "steeps": ["Political", "Social"],
                "language": "en",
            },
            "NHK World": {
                "url": "https://www3.nhk.or.jp/nhkworld/en/news/",
                "rss": "https://www3.nhk.or.jp/rss/news/cat0.xml",
                "selectors": {"articles": "a[href*='/news/']", "title": "h1", "content": ".article-body p"},
                "steeps": ["Political", "Economic"],
                "language": "en",
            },
            "Mainichi": {
                "url": "https://mainichi.jp/english/",
                "rss": None,
                "selectors": {"articles": "a[href*='/articles/']", "title": "h1", "content": ".article-body p"},
                "steeps": ["Political", "Social"],
                "language": "en",
            },
        },
        "saudi_arabia": {
            "Arab News": {
                "url": "https://www.arabnews.com",
                "rss": "https://www.arabnews.com/rss.xml",
                "selectors": {"articles": "a[href*='/node/']", "title": "h1", "content": ".field-body p"},
                "steeps": ["Political", "Economic"],
                "language": "en",
            },
            "Saudi Gazette": {
                "url": "https://www.saudigazette.com.sa",
                "rss": None,
                "selectors": {"articles": "a[href*='/article/']", "title": "h1", "content": ".article-content p"},
                "steeps": ["Political", "Economic", "Social"],
                "language": "en",
            },
            "Al Arabiya English": {
                "url": "https://english.alarabiya.net",
                "rss": "https://english.alarabiya.net/tools/rss",
                "selectors": {"articles": "a[href*='/News/']", "title": "h1", "content": ".article-body p"},
                "steeps": ["Political", "Economic"],
                "language": "en",
            },
            "Asharq Al-Awsat": {
                "url": "https://english.aawsat.com",
                "rss": None,
                "selectors": {"articles": "a[href*='/home/']", "title": "h1", "content": ".article-text p"},
                "steeps": ["Political", "Economic"],
                "language": "en",
            },
            "Gulf News": {
                "url": "https://gulfnews.com",
                "rss": "https://gulfnews.com/rss",
                "selectors": {"articles": "a[href*='/']", "title": "h1", "content": ".article-body p"},
                "steeps": ["Economic", "Political"],
                "language": "en",
            },
        },
    }

    # User-Agent 로테이션
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]

    def __init__(self, delay: float = 1.0):
        self.delay = delay
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

    def _extract_article_links(self, html: str, base_url: str, selector: str) -> list[str]:
        """기사 링크 추출"""
        soup = BeautifulSoup(html, "html.parser")
        links = []
        seen = set()

        for a in soup.select(selector):
            href = a.get("href", "")
            if not href:
                continue

            # 상대 URL 처리
            if href.startswith("/"):
                href = urljoin(base_url, href)
            elif not href.startswith("http"):
                continue

            # 중복 제거
            if href in seen:
                continue
            seen.add(href)

            # 같은 도메인만
            if urlparse(base_url).netloc in href:
                links.append(href)

        return links

    def _extract_article_content(self, url: str, config: dict) -> dict | None:
        """기사 내용 추출"""
        html = self._fetch_page(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        # 제목 추출
        title = ""
        for sel in config["selectors"]["title"].split(", "):
            title_elem = soup.select_one(sel)
            if title_elem:
                title = title_elem.get_text(strip=True)
                break

        if not title:
            return None

        # 내용 추출
        content_parts = []
        for sel in config["selectors"]["content"].split(", "):
            for elem in soup.select(sel)[:10]:  # 최대 10개 단락
                text = elem.get_text(strip=True)
                if len(text) > 50:  # 의미있는 텍스트만
                    content_parts.append(text)

        summary = " ".join(content_parts)[:500] if content_parts else ""

        return {"title": title, "summary": summary, "url": url}

    def _try_rss_feed(self, paper_name: str, config: dict, max_items: int) -> list[dict]:
        """RSS 피드 시도"""
        if not config.get("rss"):
            return []

        try:
            import feedparser

            feed = feedparser.parse(config["rss"])

            articles = []
            for entry in feed.entries[:max_items]:
                articles.append(
                    {
                        "title": entry.get("title", ""),
                        "summary": entry.get("summary", entry.get("description", ""))[:500],
                        "url": entry.get("link", ""),
                        "published_date": entry.get("published", datetime.now().strftime("%Y-%m-%d")),
                    }
                )
            return articles
        except Exception as e:
            self.errors.append(f"RSS error for {paper_name}: {e!s}")
            return []

    def crawl_newspaper(self, country: str, paper_name: str, max_items: int = 10) -> list[dict]:
        """단일 신문 크롤링"""
        if country not in self.NEWSPAPERS:
            return []

        papers = self.NEWSPAPERS[country]
        if paper_name not in papers:
            return []

        config = papers[paper_name]
        print(f"  [INFO] {paper_name} ({country}) 크롤링 시작...")

        articles = []

        # 1. RSS 피드 시도 (가능한 경우)
        rss_articles = self._try_rss_feed(paper_name, config, max_items)
        if rss_articles:
            print(f"    → RSS에서 {len(rss_articles)}건 수집")
            for art in rss_articles:
                art["source_name"] = paper_name
                art["country"] = country
                art["language"] = config["language"]
                art["steeps"] = config["steeps"]
            return rss_articles

        # 2. 직접 크롤링
        html = self._fetch_page(config["url"])
        if not html:
            print("    → 메인 페이지 접근 실패")
            return []

        # 기사 링크 추출
        links = self._extract_article_links(html, config["url"], config["selectors"]["articles"])
        print(f"    → 발견된 링크: {len(links)}개")

        # 상위 N개 기사 내용 추출
        for link in links[:max_items]:
            time.sleep(self.delay)

            article = self._extract_article_content(link, config)
            if article:
                article["source_name"] = paper_name
                article["country"] = country
                article["language"] = config["language"]
                article["steeps"] = config["steeps"]
                article["published_date"] = datetime.now().strftime("%Y-%m-%d")
                articles.append(article)

        print(f"    → 수집 완료: {len(articles)}건")
        return articles

    def crawl_country(self, country: str, max_per_paper: int = 5) -> list[dict]:
        """국가별 전체 신문 크롤링"""
        if country not in self.NEWSPAPERS:
            print(f"[ERROR] 지원하지 않는 국가: {country}")
            return []

        print(f"\n[INFO] {country.upper()} 신문 크롤링 시작")

        all_articles = []
        for paper_name in self.NEWSPAPERS[country]:
            articles = self.crawl_newspaper(country, paper_name, max_per_paper)
            all_articles.extend(articles)
            time.sleep(self.delay * 2)  # 신문간 추가 딜레이

        return all_articles

    def crawl_all_countries(self, max_per_paper: int = 3) -> list[dict]:
        """전체 국가 크롤링"""
        all_articles = []

        for country in self.NEWSPAPERS:
            articles = self.crawl_country(country, max_per_paper)
            all_articles.extend(articles)

        return all_articles

    def to_raw_format(self, articles: list[dict], date: str) -> dict:
        """환경스캐닝 표준 형식으로 변환"""
        date_compact = date.replace("-", "")

        # STEEPS 카테고리별 카운트
        by_category = {}
        items = []

        for idx, art in enumerate(articles, 1):
            # 주요 카테고리 결정
            steeps = art.get("steeps", ["Social"])
            primary_category = steeps[0] if steeps else "Social"

            if primary_category not in by_category:
                by_category[primary_category] = 0
            by_category[primary_category] += 1

            country_code = art.get("country", "unknown").upper()[:2]
            raw_id = f"RAW-GLOBAL-{country_code}-{date_compact}-{idx:03d}"

            items.append(
                {
                    "raw_id": raw_id,
                    "title": art.get("title", ""),
                    "url": art.get("url", ""),
                    "source_name": art.get("source_name", ""),
                    "source_type": "newspaper",
                    "published_date": art.get("published_date", date),
                    "category_hint": primary_category,
                    "summary": art.get("summary", ""),
                    "search_keyword": "",
                    "key_entities": [],
                    "language": art.get("language", "en"),
                    "country": art.get("country", ""),
                    "scanned_at": datetime.now().isoformat() + "+09:00",
                }
            )

        return {
            "scan_date": date,
            "scan_time": datetime.now().strftime("%H:%M:%S"),
            "source": "global_news_crawler_v1",
            "total_scanned": len(items),
            "by_category": by_category,
            "by_country": self._count_by_country(items),
            "items": items,
        }

    def _count_by_country(self, items: list[dict]) -> dict[str, int]:
        """국가별 카운트"""
        counts = {}
        for item in items:
            country = item.get("country", "unknown")
            if country not in counts:
                counts[country] = 0
            counts[country] += 1
        return counts


def main():
    parser = argparse.ArgumentParser(description="글로벌 뉴스 크롤러")
    parser.add_argument("--country", help="특정 국가만 크롤링 (korea, usa, uk, china, japan, saudi_arabia)")
    parser.add_argument("--paper", help="특정 신문만 크롤링")
    parser.add_argument("--all-countries", action="store_true", help="전체 국가 크롤링")
    parser.add_argument("--max", type=int, default=5, help="신문당 최대 기사 수")
    parser.add_argument("--delay", type=float, default=1.0, help="요청 간 딜레이 (초)")
    parser.add_argument("--output", help="출력 파일")
    parser.add_argument("--raw-format", action="store_true", help="환경스캐닝 형식으로 출력")
    parser.add_argument("--list-papers", action="store_true", help="지원 신문 목록 출력")

    args = parser.parse_args()

    print("=" * 60)
    print("글로벌 뉴스 크롤러 v1.0 - 환경스캐닝 시스템")
    print("=" * 60)

    crawler = GlobalNewsCrawler(delay=args.delay)

    if args.list_papers:
        print("\n지원 신문 목록:")
        for country, papers in crawler.NEWSPAPERS.items():
            print(f"\n{country.upper()}:")
            for paper in papers:
                print(f"  - {paper}")
        return

    # 크롤링 실행
    articles = []

    if args.paper and args.country:
        articles = crawler.crawl_newspaper(args.country, args.paper, args.max)
    elif args.country:
        articles = crawler.crawl_country(args.country, args.max)
    elif args.all_countries:
        articles = crawler.crawl_all_countries(args.max)
    else:
        print("\n사용법:")
        print("  --country usa --max 5         : 미국 신문 크롤링")
        print("  --all-countries --max 3       : 전체 국가 크롤링")
        print("  --list-papers                 : 지원 신문 목록")
        return

    print(f"\n총 {len(articles)}건 수집 완료")

    # 출력
    today = datetime.now().strftime("%Y-%m-%d")

    if args.raw_format:
        result = crawler.to_raw_format(articles, today)
    else:
        result = {"total": len(articles), "items": articles}

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
