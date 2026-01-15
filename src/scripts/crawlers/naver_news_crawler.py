#!/usr/bin/env python3
"""
네이버 뉴스 크롤러 v2
환경스캐닝 시스템용 네이버 뉴스 수집 모듈

사용법:
    python naver_news_crawler.py --section it-science --max 20
    python naver_news_crawler.py --all-sections --max 10
    python naver_news_crawler.py --keyword "AI 인공지능" --max 15
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from typing import ClassVar, timedelta
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class NaverNewsCrawler:
    """네이버 뉴스 크롤러 클래스 v2"""

    BASE_URL = "https://news.naver.com"

    # 네이버 뉴스 섹션 ID
    SECTIONS: ClassVar[dict] = {
        "politics": {"sid": 100, "name": "정치", "steeps": "Political"},
        "economy": {"sid": 101, "name": "경제", "steeps": "Economic"},
        "society": {"sid": 102, "name": "사회", "steeps": "Social"},
        "life-culture": {"sid": 103, "name": "생활/문화", "steeps": "Social"},
        "world": {"sid": 104, "name": "세계", "steeps": "Political"},
        "it-science": {"sid": 105, "name": "IT/과학", "steeps": "Technological"},
    }

    # STEEPS 매핑용 키워드
    STEEPS_KEYWORDS: ClassVar[dict] = {
        "Technological": [
            "AI",
            "인공지능",
            "반도체",
            "로봇",
            "양자",
            "배터리",
            "자율주행",
            "메타버스",
            "블록체인",
            "우주",
            "6G",
            "GPU",
            "LLM",
        ],
        "Environmental": [
            "탄소",
            "기후",
            "환경",
            "ESG",
            "재생에너지",
            "전기차",
            "수소",
            "태양광",
            "풍력",
            "온실가스",
            "넷제로",
        ],
        "Economic": ["금리", "환율", "증시", "투자", "IPO", "M&A", "스타트업", "수출", "무역", "인플레이션", "GDP"],
        "Political": ["정책", "규제", "국회", "안보", "외교", "북한", "미중", "선거", "정당", "법안"],
        "Social": ["인구", "출산", "고령화", "교육", "복지", "주거", "세대", "노동", "일자리", "격차"],
        "Spiritual": ["명상", "웰니스", "힐링", "마음", "종교", "윤리", "가치", "철학", "심리"],
    }

    def __init__(self, delay: float = 0.5):
        """초기화"""
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://news.naver.com/",
            }
        )

    def _get_section_url(self, section: str, page: int = 1) -> str:
        """섹션 URL 생성"""
        if section not in self.SECTIONS:
            raise ValueError(f"Unknown section: {section}")

        sid = self.SECTIONS[section]["sid"]
        return f"{self.BASE_URL}/main/list.naver?mode=LSD&mid=sec&sid1={sid}&page={page}"

    def _classify_steeps(self, title: str, content: str = "") -> str:
        """제목과 내용으로 STEEPS 카테고리 분류"""
        text = (title + " " + content).lower()

        scores = {}
        for category, keywords in self.STEEPS_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text)
            if score > 0:
                scores[category] = score

        if scores:
            return max(scores, key=scores.get)
        return "Social"  # 기본값

    def _parse_date(self, date_str: str) -> tuple[str, bool]:
        """
        날짜 파싱
        Returns: (ISO 날짜 문자열, 24시간 이내 여부)
        """
        now = datetime.now()
        is_recent = False

        # "N분 전" 패턴
        if "분 전" in date_str:
            minutes = int(re.search(r"(\d+)분", date_str).group(1))
            result = now - timedelta(minutes=minutes)
            is_recent = True
            return result.strftime("%Y-%m-%d %H:%M"), is_recent

        # "N시간 전" 패턴
        if "시간 전" in date_str:
            hours = int(re.search(r"(\d+)시간", date_str).group(1))
            result = now - timedelta(hours=hours)
            is_recent = hours <= 24
            return result.strftime("%Y-%m-%d %H:%M"), is_recent

        # "N일 전" 패턴
        if "일 전" in date_str:
            days = int(re.search(r"(\d+)일", date_str).group(1))
            result = now - timedelta(days=days)
            is_recent = days <= 1
            return result.strftime("%Y-%m-%d"), is_recent

        # "YYYY.MM.DD. HH:MM" 패턴
        match = re.search(r"(\d{4})\.(\d{2})\.(\d{2})\.\s*(\d{2}):(\d{2})", date_str)
        if match:
            dt = datetime(
                int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)), int(match.group(5))
            )
            is_recent = (now - dt).total_seconds() < 86400
            return dt.strftime("%Y-%m-%d %H:%M"), is_recent

        # "YYYY.MM.DD." 패턴
        match = re.search(r"(\d{4})\.(\d{2})\.(\d{2})", date_str)
        if match:
            dt = datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
            is_recent = (now - dt).days <= 1
            return dt.strftime("%Y-%m-%d"), is_recent

        return now.strftime("%Y-%m-%d"), True

    def fetch_article_detail(self, url: str) -> dict | None:
        """기사 상세 정보 추출"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            article = {}

            # 제목
            title_elem = soup.select_one("h2.media_end_head_headline, #title_area span")
            article["title"] = title_elem.text.strip() if title_elem else ""

            # 언론사
            press_elem = soup.select_one("a.media_end_head_top_logo img, em.media_end_linked_more_point")
            if press_elem:
                article["press"] = press_elem.get("alt") or press_elem.text.strip()
            else:
                article["press"] = "Unknown"

            # 날짜
            date_elem = soup.select_one("span.media_end_head_info_datestamp_time, span._ARTICLE_DATE_TIME")
            if date_elem:
                date_text = date_elem.get("data-date-time") or date_elem.text.strip()
                article["published_date"], article["is_recent"] = self._parse_date(date_text)
            else:
                article["published_date"] = datetime.now().strftime("%Y-%m-%d")
                article["is_recent"] = True

            # 본문 요약 (첫 200자)
            content_elem = soup.select_one("#dic_area, article#dic_area")
            if content_elem:
                # 불필요한 요소 제거
                for tag in content_elem.select("script, style, span.end_photo_org"):
                    tag.decompose()
                content = content_elem.text.strip()
                article["summary"] = content[:300] + "..." if len(content) > 300 else content
            else:
                article["summary"] = ""

            # STEEPS 분류
            article["category_hint"] = self._classify_steeps(article["title"], article["summary"])

            article["url"] = url
            article["source_type"] = "news"
            article["language"] = "ko"

            return article

        except Exception as e:
            print(f"[WARN] 기사 상세 추출 실패: {url[:50]}... - {e}", file=sys.stderr)
            return None

    def fetch_section_articles(self, section: str, max_articles: int = 20) -> list[dict]:
        """섹션별 기사 목록 수집"""
        articles = []
        page = 1

        section_info = self.SECTIONS.get(section, {})
        default_steeps = section_info.get("steeps", "Social")

        print(f"\n[INFO] {section_info.get('name', section)} 섹션 스캔 시작")

        while len(articles) < max_articles:
            url = self._get_section_url(section, page)

            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                # 기사 링크 추출
                article_links = soup.select("ul.type06_headline li a, ul.type06 li a")

                if not article_links:
                    # 대안 선택자
                    article_links = soup.select('div.list_body a[href*="/article/"]')

                if not article_links:
                    break

                for link in article_links:
                    if len(articles) >= max_articles:
                        break

                    href = link.get("href", "")
                    if "/article/" not in href:
                        continue

                    article_url = urljoin(self.BASE_URL, href)

                    # 중복 체크
                    if any(a["url"] == article_url for a in articles):
                        continue

                    # 기사 상세 수집
                    time.sleep(self.delay)
                    article = self.fetch_article_detail(article_url)

                    if article and article.get("title"):
                        # 기본 STEEPS 설정 (분류 실패 시)
                        if article["category_hint"] == "Social" and default_steeps != "Social":
                            article["category_hint"] = default_steeps

                        articles.append(article)
                        print(f"  [{len(articles)}] {article['title'][:40]}...")

                page += 1
                time.sleep(self.delay)

            except Exception as e:
                print(f"[ERROR] 섹션 페이지 오류: {e}", file=sys.stderr)
                break

        return articles

    def fetch_main_headlines(self, max_articles: int = 30) -> list[dict]:
        """메인 페이지 헤드라인 수집"""
        articles = []

        print("\n[INFO] 메인 헤드라인 스캔")

        try:
            response = self.session.get(self.BASE_URL, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # 메인 페이지의 뉴스 링크 추출
            news_links = soup.find_all("a", href=True)
            article_urls = []

            for link in news_links:
                href = link.get("href", "")
                if "/article/" in href:
                    full_url = urljoin(self.BASE_URL, href)
                    if full_url not in article_urls:
                        article_urls.append(full_url)

            print(f"  발견된 기사 링크: {len(article_urls)}개")

            for url in article_urls[:max_articles]:
                time.sleep(self.delay)
                article = self.fetch_article_detail(url)

                if article and article.get("title"):
                    articles.append(article)
                    print(f"  [{len(articles)}] {article['title'][:40]}...")

        except Exception as e:
            print(f"[ERROR] 메인 페이지 오류: {e}", file=sys.stderr)

        return articles

    def search_by_keyword(self, keyword: str, max_articles: int = 20) -> list[dict]:
        """
        키워드 검색 (네이버 뉴스 검색 결과에서 네이버 뉴스 링크만 추출)
        """
        articles = []

        print(f"\n[INFO] 키워드 검색: '{keyword}'")

        # 검색 URL (네이버 뉴스 링크만)
        search_url = f"https://search.naver.com/search.naver?where=news&query={quote(keyword)}&sort=1&nso=so:dd,p:1w"

        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # 네이버 뉴스 링크 추출
            news_links = soup.find_all(
                "a", href=lambda x: x and ("n.news.naver.com" in x or "news.naver.com/article" in x)
            )

            seen_urls = set()
            article_urls = []

            for link in news_links:
                href = link.get("href", "")
                if href not in seen_urls and "/article/" in href:
                    seen_urls.add(href)
                    article_urls.append(href)

            print(f"  발견된 네이버 뉴스 링크: {len(article_urls)}개")

            for url in article_urls[:max_articles]:
                time.sleep(self.delay)
                article = self.fetch_article_detail(url)

                if article and article.get("title"):
                    article["search_keyword"] = keyword
                    articles.append(article)
                    print(f"  [{len(articles)}] {article['title'][:40]}...")

        except Exception as e:
            print(f"[ERROR] 검색 오류: {e}", file=sys.stderr)

        return articles

    def fetch_all_sections(self, max_per_section: int = 10) -> dict[str, list[dict]]:
        """전체 섹션 스캔"""
        results = {}

        for section in self.SECTIONS:
            results[section] = self.fetch_section_articles(section, max_per_section)

        return results

    def filter_recent(self, articles: list[dict], hours: int = 24) -> list[dict]:
        """최근 N시간 기사만 필터링"""
        return [a for a in articles if a.get("is_recent", True)]

    def to_raw_signal_format(self, articles: list[dict], scan_date: str | None = None) -> dict:
        """환경스캐닝 raw signal 형식으로 변환"""
        if scan_date is None:
            scan_date = datetime.now().strftime("%Y-%m-%d")

        scan_time = datetime.now().strftime("%H:%M:%S")

        # 카테고리별 집계
        by_category = {}
        for item in articles:
            cat = item.get("category_hint", "Unknown")
            by_category[cat] = by_category.get(cat, 0) + 1

        # raw_id 생성
        formatted_items = []
        for i, item in enumerate(articles, 1):
            raw_id = f"RAW-NAVER-{scan_date.replace('-', '')}-{i:03d}"

            formatted_items.append(
                {
                    "raw_id": raw_id,
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "source_name": item.get("press", "Unknown"),
                    "source_type": "news",
                    "published_date": item.get("published_date", scan_date),
                    "category_hint": item.get("category_hint", "Unknown"),
                    "summary": item.get("summary", ""),
                    "search_keyword": item.get("search_keyword", ""),
                    "key_entities": [],
                    "language": "ko",
                    "scanned_at": f"{scan_date}T{scan_time}+09:00",
                }
            )

        return {
            "scan_date": scan_date,
            "scan_time": scan_time,
            "source": "naver_news_crawler_v2",
            "total_scanned": len(formatted_items),
            "by_category": by_category,
            "items": formatted_items,
        }


def main():
    """CLI 엔트리포인트"""
    parser = argparse.ArgumentParser(
        description="네이버 뉴스 크롤러 v2 - 환경스캐닝 시스템용",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 메인 헤드라인 수집
  python naver_news_crawler.py --headlines --max 20

  # 특정 섹션 스캔
  python naver_news_crawler.py --section it-science --max 15

  # 전체 섹션 스캔
  python naver_news_crawler.py --all-sections --max 10

  # 키워드 검색
  python naver_news_crawler.py --keyword "AI 인공지능" --max 20

  # 결과를 파일로 저장
  python naver_news_crawler.py --headlines --output naver-scan.json --raw-format

섹션 목록:
  politics    : 정치
  economy     : 경제
  society     : 사회
  life-culture: 생활/문화
  world       : 세계
  it-science  : IT/과학
        """,
    )

    parser.add_argument("--headlines", action="store_true", help="메인 헤드라인 수집")
    parser.add_argument(
        "--section",
        "-s",
        type=str,
        choices=["politics", "economy", "society", "life-culture", "world", "it-science"],
        help="스캔할 섹션",
    )
    parser.add_argument("--all-sections", action="store_true", help="전체 섹션 스캔")
    parser.add_argument("--keyword", "-k", type=str, help="키워드 검색")
    parser.add_argument("--max", type=int, default=20, help="최대 기사 수 (기본: 20)")
    parser.add_argument("--delay", type=float, default=0.5, help="요청 간 딜레이 초 (기본: 0.5)")
    parser.add_argument("--recent-only", action="store_true", help="최근 24시간 기사만")
    parser.add_argument("--output", "-o", type=str, help="출력 파일 경로 (JSON)")
    parser.add_argument("--raw-format", action="store_true", help="환경스캐닝 raw signal 형식으로 출력")

    args = parser.parse_args()

    # 모드 확인
    if not (args.headlines or args.section or args.all_sections or args.keyword):
        parser.print_help()
        print("\n[ERROR] --headlines, --section, --all-sections, 또는 --keyword 중 하나를 지정하세요.")
        sys.exit(1)

    # 크롤러 초기화
    crawler = NaverNewsCrawler(delay=args.delay)

    print("=" * 60)
    print("네이버 뉴스 크롤러 v2 - 환경스캐닝 시스템")
    print("=" * 60)

    articles = []

    # 스캔 실행
    if args.headlines:
        articles = crawler.fetch_main_headlines(args.max)

    elif args.section:
        articles = crawler.fetch_section_articles(args.section, args.max)

    elif args.all_sections:
        all_results = crawler.fetch_all_sections(args.max)
        for section_articles in all_results.values():
            articles.extend(section_articles)

    elif args.keyword:
        articles = crawler.search_by_keyword(args.keyword, args.max)

    # 최근 기사만 필터링
    if args.recent_only:
        original = len(articles)
        articles = crawler.filter_recent(articles)
        print(f"\n최근 24시간 필터: {original}건 → {len(articles)}건")

    # 중복 제거
    seen_urls = set()
    unique_articles = []
    for article in articles:
        if article["url"] not in seen_urls:
            seen_urls.add(article["url"])
            unique_articles.append(article)
    articles = unique_articles

    print(f"\n총 {len(articles)}건 수집 완료")

    # 출력 형식
    if args.raw_format:
        output_data = crawler.to_raw_signal_format(articles)
    else:
        output_data = {"total": len(articles), "items": articles}

    # 결과 출력/저장
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"결과 저장: {args.output}")
    else:
        print("\n" + "=" * 60)
        print(json.dumps(output_data, ensure_ascii=False, indent=2)[:3000])
        if len(json.dumps(output_data)) > 3000:
            print("\n... (결과 생략, --output으로 파일 저장 권장)")

    return output_data


if __name__ == "__main__":
    main()
