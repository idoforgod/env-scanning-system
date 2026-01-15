#!/usr/bin/env python3
"""
네이버 뉴스 URL 수집기 v4
v4 Source of Truth 규칙에 따라 URL과 메타데이터만 수집 (본문 수집 금지)

사용법:
    python naver_url_collector.py --output data/2026/01/14/raw/naver-urls-2026-01-14.json
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

# STEEPS 키워드 정의
STEEPS_KEYWORDS = {
    "Social": [
        "사회변화",
        "인구구조",
        "세대갈등",
        "라이프스타일",
        "인구",
        "출산",
        "고령화",
        "교육",
        "복지",
        "주거",
        "세대",
        "노동",
        "일자리",
        "격차",
    ],
    "Technological": [
        "AI",
        "인공지능",
        "양자컴퓨팅",
        "양자",
        "로봇",
        "바이오테크",
        "바이오",
        "우주기술",
        "우주",
        "반도체",
        "자율주행",
        "메타버스",
        "블록체인",
        "6G",
        "GPU",
        "LLM",
        "딥러닝",
        "머신러닝",
    ],
    "Economic": [
        "경제전망",
        "금융혁신",
        "일자리변화",
        "산업구조",
        "금리",
        "환율",
        "증시",
        "투자",
        "IPO",
        "M&A",
        "스타트업",
        "수출",
        "무역",
        "인플레이션",
        "GDP",
    ],
    "Environmental": [
        "기후변화",
        "에너지전환",
        "탄소중립",
        "환경정책",
        "탄소",
        "기후",
        "ESG",
        "재생에너지",
        "전기차",
        "수소",
        "태양광",
        "풍력",
        "온실가스",
        "넷제로",
    ],
    "Political": [
        "정책변화",
        "규제동향",
        "국제관계",
        "거버넌스",
        "정책",
        "규제",
        "국회",
        "안보",
        "외교",
        "북한",
        "미중",
        "선거",
        "정당",
        "법안",
    ],
    "Spiritual": [
        "가치관변화",
        "웰빙",
        "정신건강",
        "문화트렌드",
        "명상",
        "웰니스",
        "힐링",
        "마음",
        "종교",
        "윤리",
        "가치",
        "철학",
        "심리",
    ],
}


class NaverURLCollector:
    """네이버 뉴스 URL 수집기 (v4 - URL only)"""

    BASE_URL = "https://news.naver.com"
    SEARCH_URL = "https://search.naver.com/search.naver"

    def __init__(self, delay: float = 1.0):
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

    def search_urls(self, keyword: str, max_urls: int = 5) -> list[dict]:
        """
        키워드로 네이버 뉴스 검색하여 URL 수집
        본문은 수집하지 않고 URL, 제목, 출처만 수집
        """
        urls = []

        # 검색 URL (최근 1주일, 최신순)
        search_url = f"{self.SEARCH_URL}?where=news&query={quote(keyword)}&sort=1&nso=so:dd,p:1w"

        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # 네이버 뉴스 링크 추출
            news_items = soup.select("div.news_area")

            for item in news_items[:max_urls]:
                try:
                    # URL
                    link = item.select_one("a.news_tit")
                    if not link:
                        continue

                    url = link.get("href", "")
                    if not url or "/article/" not in url:
                        continue

                    # 제목
                    title = link.get("title") or link.text.strip()

                    # 언론사
                    press = item.select_one("a.info.press")
                    source_name = press.text.strip() if press else "Unknown"

                    # 중복 체크
                    if any(u["url"] == url for u in urls):
                        continue

                    urls.append(
                        {
                            "url": url,
                            "title": title,
                            "source": "naver",
                            "source_name": source_name,
                            "steeps_category": None,  # 나중에 설정
                            "search_keyword": keyword,
                        }
                    )

                except Exception as e:
                    print(f"  [WARN] 아이템 파싱 실패: {e}", file=sys.stderr)
                    continue

            time.sleep(self.delay)

        except Exception as e:
            print(f"  [ERROR] 검색 실패 ({keyword}): {e}", file=sys.stderr)

        return urls

    def collect_by_steeps(self, max_per_category: int = 5) -> dict:
        """
        STEEPS 카테고리별 키워드로 URL 수집
        """
        all_urls = []
        stats = {}

        print("\n" + "=" * 60)
        print("네이버 뉴스 URL 수집 시작 (v4 - URL only)")
        print("=" * 60)

        for category, keywords in STEEPS_KEYWORDS.items():
            print(f"\n[{category}] 카테고리 스캔 중...")
            category_urls = []

            # 각 카테고리에서 상위 3개 키워드 사용
            for keyword in keywords[:3]:
                print(f"  검색: '{keyword}'")
                urls = self.search_urls(keyword, max_urls=max_per_category)

                # STEEPS 카테고리 설정
                for url_item in urls:
                    url_item["steeps_category"] = category

                    # 중복 체크
                    if not any(u["url"] == url_item["url"] for u in category_urls):
                        category_urls.append(url_item)

                if len(category_urls) >= max_per_category:
                    break

            all_urls.extend(category_urls)
            stats[category] = len(category_urls)
            print(f"  {category}: {len(category_urls)}개 URL 수집")

        # 중복 제거 (최종)
        seen_urls = set()
        unique_urls = []
        for item in all_urls:
            if item["url"] not in seen_urls:
                seen_urls.add(item["url"])
                unique_urls.append(item)

        print(f"\n총 {len(unique_urls)}개 URL 수집 (중복 제거 후)")

        return {
            "collection_date": datetime.now().strftime("%Y-%m-%d"),
            "collection_time": datetime.now().strftime("%H:%M:%S"),
            "source": "naver_url_collector_v4",
            "total_urls": len(unique_urls),
            "by_category": stats,
            "urls": unique_urls,
        }


def main():
    """CLI 엔트리포인트"""
    parser = argparse.ArgumentParser(
        description="네이버 뉴스 URL 수집기 v4 (URL only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # STEEPS 키워드로 URL 수집 (기본)
  python naver_url_collector.py --output naver-urls-2026-01-14.json

  # 카테고리당 최대 개수 지정
  python naver_url_collector.py --max 10 --output naver-urls.json
        """,
    )

    parser.add_argument("--output", "-o", type=str, required=True, help="출력 파일 경로 (JSON)")
    parser.add_argument("--max", type=int, default=5, help="카테고리당 최대 URL 수 (기본: 5)")
    parser.add_argument("--delay", type=float, default=1.0, help="요청 간 딜레이 초 (기본: 1.0)")

    args = parser.parse_args()

    # 출력 디렉토리 생성
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"디렉토리 생성: {output_dir}")

    # 수집 실행
    collector = NaverURLCollector(delay=args.delay)
    result = collector.collect_by_steeps(max_per_category=args.max)

    # 검증
    if result["total_urls"] < 15:
        print(f"\n[WARNING] 최소 15개 URL이 필요하지만 {result['total_urls']}개만 수집됨")
        print("딜레이를 늘리거나 max 값을 증가시켜 재시도하세요.")

    # 저장
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n출력 저장: {args.output}")
    print("=" * 60)

    # 요약 출력
    print("\n[수집 요약]")
    for category, count in result["by_category"].items():
        print(f"  {category}: {count}개")
    print(f"\n총 {result['total_urls']}개 URL 수집 완료")

    return result


if __name__ == "__main__":
    main()
