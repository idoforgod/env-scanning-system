#!/usr/bin/env python3
"""
네이버 뉴스 URL 제목 보강 스크립트
수집된 URL에서 실제 제목을 추출하여 업데이트

사용법:
    python enrich_titles.py --input naver-urls.json --output naver-urls-enriched.json
"""

import argparse
import json
import sys
import time

import requests
from bs4 import BeautifulSoup


def fetch_title(url: str, session: requests.Session) -> tuple[str, str]:
    """
    URL에서 실제 제목과 언론사 추출
    Returns: (title, source_name)
    """
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 제목 추출
        title_elem = soup.select_one("h2.media_end_head_headline, #title_area span")
        title = title_elem.text.strip() if title_elem else "네이버뉴스"

        # 언론사 추출
        press_elem = soup.select_one("a.media_end_head_top_logo img, em.media_end_linked_more_point")
        source_name = press_elem.get("alt") or press_elem.text.strip() if press_elem else "Unknown"

        return title, source_name

    except Exception as e:
        print(f"  [WARN] 제목 추출 실패: {url[:50]}... - {e}", file=sys.stderr)
        return "네이버뉴스", "Unknown"


def enrich_titles(input_file: str, output_file: str, delay: float = 1.0):
    """
    수집된 URL 목록에서 제목을 보강
    """
    # 입력 파일 읽기
    with open(input_file, encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n총 {data['total_urls']}개 URL 제목 보강 시작")
    print("=" * 60)

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9",
        }
    )

    enriched_count = 0

    for i, item in enumerate(data["urls"], 1):
        if item["title"] == "네이버뉴스":
            print(f"[{i}/{data['total_urls']}] {item['url'][:60]}...")

            title, source_name = fetch_title(item["url"], session)

            if title != "네이버뉴스":
                item["title"] = title
                item["source_name"] = source_name
                enriched_count += 1
                print(f"  → {title[:50]}... ({source_name})")
            else:
                print("  → 제목 추출 실패")

            time.sleep(delay)
        else:
            print(f"[{i}/{data['total_urls']}] 이미 제목 있음: {item['title'][:40]}...")

    # 출력 파일 저장
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("=" * 60)
    print(f"\n총 {enriched_count}개 제목 보강 완료")
    print(f"출력 저장: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="네이버 뉴스 URL 제목 보강")
    parser.add_argument("--input", "-i", type=str, required=True, help="입력 JSON 파일")
    parser.add_argument("--output", "-o", type=str, required=True, help="출력 JSON 파일")
    parser.add_argument("--delay", type=float, default=1.0, help="요청 간 딜레이 초 (기본: 1.0)")

    args = parser.parse_args()

    enrich_titles(args.input, args.output, args.delay)


if __name__ == "__main__":
    main()
