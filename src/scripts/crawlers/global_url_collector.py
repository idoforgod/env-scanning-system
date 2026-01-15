#!/usr/bin/env python3
"""
글로벌 뉴스 URL 수집기 v1.0
================================
Stage A: URL만 수집 (본문은 Stage B에서)

6개국 주요 신문 URL 수집:
- 한국: 한겨레, 경향신문
- 미국: NYT, Washington Post, Reuters
- 영국: Guardian, BBC
- 중국: SCMP, Global Times
- 일본: Japan Times, Nikkei Asia
- 중동: Al Jazeera, Arab News

출력 형식:
{
  "source": "global-news",
  "date": "2026-01-14",
  "total_urls": 25,
  "urls": [
    {
      "url": "https://...",
      "title_hint": "...",
      "region": "usa",
      "newspaper": "The New York Times",
      "category": "Political",
      "language": "en"
    }
  ]
}
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


class GlobalURLCollector:
    """글로벌 뉴스 URL 수집기 - URL만 추출"""

    # 6개국 주요 신문 설정
    NEWSPAPERS = {
        "korea": {
            "한겨레": {
                "url": "https://www.hani.co.kr",
                "rss": "https://www.hani.co.kr/rss/",
                "selectors": {"articles": "a[href*='/arti/']", "title": "h4.title, .article-title, span"},
                "category": "Political",
                "language": "ko",
            },
            "경향신문": {
                "url": "https://www.khan.co.kr",
                "rss": None,
                "selectors": {"articles": "a[href*='/article/']", "title": ".art_tit, .headline"},
                "category": "Political",
                "language": "ko",
            },
        },
        "usa": {
            "The New York Times": {
                "url": "https://www.nytimes.com",
                "rss": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
                "selectors": {"articles": "a[href*='/202']", "title": "h3, span"},
                "category": "Political",
                "language": "en",
            },
            "The Washington Post": {
                "url": "https://www.washingtonpost.com",
                "rss": "https://feeds.washingtonpost.com/rss/world",
                "selectors": {"articles": "a[href*='/202']", "title": "h2, h3, span"},
                "category": "Political",
                "language": "en",
            },
            "Reuters": {
                "url": "https://www.reuters.com/world/",
                "rss": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
                "selectors": {"articles": "a[href*='/world/']", "title": "h3, span, .text__text"},
                "category": "Political",
                "language": "en",
            },
        },
        "uk": {
            "The Guardian": {
                "url": "https://www.theguardian.com/world",
                "rss": "https://www.theguardian.com/world/rss",
                "selectors": {"articles": "a[href*='/202']", "title": "h3, span"},
                "category": "Political",
                "language": "en",
            },
            "BBC News": {
                "url": "https://www.bbc.com/news/world",
                "rss": None,
                "selectors": {"articles": "a[href*='/news/']", "title": "h3, .promo-text"},
                "category": "Social",
                "language": "en",
            },
        },
        "china": {
            "South China Morning Post": {
                "url": "https://www.scmp.com/news/world",
                "rss": "https://www.scmp.com/rss/91/feed",
                "selectors": {"articles": "a[href*='/article/']", "title": "h3, .card__title"},
                "category": "Political",
                "language": "en",
            },
            "Global Times": {
                "url": "https://www.globaltimes.cn/world/",
                "rss": None,
                "selectors": {"articles": "a[href*='/page/']", "title": "h3, .title"},
                "category": "Political",
                "language": "en",
            },
        },
        "japan": {
            "The Japan Times": {
                "url": "https://www.japantimes.co.jp/news/",
                "rss": "https://www.japantimes.co.jp/feed/",
                "selectors": {"articles": "a[href*='/news/']", "title": "h3, .article-title"},
                "category": "Political",
                "language": "en",
            },
            "Nikkei Asia": {
                "url": "https://asia.nikkei.com",
                "rss": "https://asia.nikkei.com/rss/feed/nar",
                "selectors": {"articles": "a[href*='/']", "title": "h3, .title"},
                "category": "Economic",
                "language": "en",
            },
        },
        "middle_east": {
            "Al Jazeera": {
                "url": "https://www.aljazeera.com/news/",
                "rss": None,
                "selectors": {"articles": "a[href*='/news/']", "title": "h3, span.u-clickable-card__link"},
                "category": "Political",
                "language": "en",
            },
            "Arab News": {
                "url": "https://www.arabnews.com",
                "rss": "https://www.arabnews.com/rss.xml",
                "selectors": {"articles": "a[href*='/node/']", "title": "h2, h3"},
                "category": "Political",
                "language": "en",
            },
        },
    }

    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.session = requests.Session()
        self.collected_urls = []
        self.errors = []

    def _get_headers(self) -> dict[str, str]:
        """랜덤 User-Agent 헤더 반환"""
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
            "Connection": "keep-alive",
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

    def _try_rss_feed(self, paper_name: str, config: dict, max_items: int) -> list[dict]:
        """RSS 피드에서 URL 추출"""
        if not config.get("rss"):
            return []

        try:
            import feedparser

            feed = feedparser.parse(config["rss"])
            urls = []

            for entry in feed.entries[:max_items]:
                urls.append(
                    {
                        "url": entry.get("link", ""),
                        "title_hint": entry.get("title", ""),
                        "newspaper": paper_name,
                        "category": config["category"],
                        "language": config["language"],
                        "published_date": entry.get("published", datetime.now().strftime("%Y-%m-%d")),
                    }
                )

            return urls
        except Exception as e:
            self.errors.append(f"RSS error for {paper_name}: {e!s}")
            return []

    def _extract_urls_from_page(self, html: str, base_url: str, selector: str, title_selector: str) -> list[dict]:
        """페이지에서 URL과 제목 힌트 추출"""
        soup = BeautifulSoup(html, "html.parser")
        urls = []
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
            if urlparse(base_url).netloc not in href:
                continue

            # 제목 힌트 추출
            title_hint = ""
            for sel in title_selector.split(", "):
                title_elem = a.select_one(sel)
                if title_elem:
                    title_hint = title_elem.get_text(strip=True)
                    break

            if not title_hint:
                title_hint = a.get_text(strip=True)[:100]

            urls.append({"url": href, "title_hint": title_hint})

        return urls

    def collect_newspaper(self, region: str, paper_name: str, max_items: int = 5) -> list[dict]:
        """단일 신문에서 URL 수집"""
        if region not in self.NEWSPAPERS:
            return []

        papers = self.NEWSPAPERS[region]
        if paper_name not in papers:
            return []

        config = papers[paper_name]
        print(f"  [INFO] {paper_name} ({region}) URL 수집 중...")

        # 1. RSS 시도
        rss_urls = self._try_rss_feed(paper_name, config, max_items)
        if rss_urls:
            print(f"    → RSS에서 {len(rss_urls)}개 URL 수집")
            for url_data in rss_urls:
                url_data["region"] = region
            return rss_urls

        # 2. 직접 크롤링
        html = self._fetch_page(config["url"])
        if not html:
            print("    → 페이지 접근 실패")
            return []

        urls = self._extract_urls_from_page(
            html, config["url"], config["selectors"]["articles"], config["selectors"]["title"]
        )

        print(f"    → {len(urls)}개 URL 발견")

        # 메타데이터 추가
        result = []
        for url_data in urls[:max_items]:
            url_data.update(
                {
                    "region": region,
                    "newspaper": paper_name,
                    "category": config["category"],
                    "language": config["language"],
                    "collected_at": datetime.now().isoformat(),
                }
            )
            result.append(url_data)

        return result

    def collect_all(self, max_per_paper: int = 5) -> dict:
        """전체 신문에서 URL 수집"""
        all_urls = []

        for region in self.NEWSPAPERS:
            print(f"\n[INFO] {region.upper()} 신문 URL 수집 중")

            for paper_name in self.NEWSPAPERS[region]:
                urls = self.collect_newspaper(region, paper_name, max_per_paper)
                all_urls.extend(urls)
                time.sleep(self.delay)

        return {
            "source": "global-news",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "collected_at": datetime.now().isoformat(),
            "total_urls": len(all_urls),
            "by_region": self._count_by_region(all_urls),
            "urls": all_urls,
        }

    def _count_by_region(self, urls: list[dict]) -> dict[str, int]:
        """지역별 카운트"""
        counts = {}
        for url_data in urls:
            region = url_data.get("region", "unknown")
            if region not in counts:
                counts[region] = 0
            counts[region] += 1
        return counts


def main():
    parser = argparse.ArgumentParser(description="글로벌 뉴스 URL 수집기")
    parser.add_argument("--max", type=int, default=5, help="신문당 최대 URL 수")
    parser.add_argument("--delay", type=float, default=1.0, help="요청 간 딜레이 (초)")
    parser.add_argument("--output", required=True, help="출력 파일 경로")

    args = parser.parse_args()

    print("=" * 60)
    print("글로벌 뉴스 URL 수집기 v1.0 - Stage A")
    print("=" * 60)

    collector = GlobalURLCollector(delay=args.delay)
    result = collector.collect_all(max_per_paper=args.max)

    print(f"\n[완료] 총 {result['total_urls']}개 URL 수집")
    print(f"지역별: {result['by_region']}")

    # 파일 저장
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n출력 파일: {args.output}")

    # 오류 보고
    if collector.errors:
        print(f"\n[WARN] {len(collector.errors)}건의 오류 발생:")
        for err in collector.errors[:5]:
            print(f"  - {err}")


if __name__ == "__main__":
    main()
