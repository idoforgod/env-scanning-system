#!/usr/bin/env python3
"""
Batch Content Fetcher
=====================
대량 URL의 본문 수집을 안전한 배치 단위로 분할 처리

구조적 문제 5.1 해결:
- "에이전트 컨텍스트 한계" 문제 방지
- 배치 크기를 10개 이하로 제한하여 컨텍스트 과부하 방지

Usage:
    python batch_content_fetcher.py --date 2026-01-14 --batch-size 8
    python batch_content_fetcher.py --input urls.json --output articles.json
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# 배치 설정 (구조적 문제 해결을 위한 제한)
MAX_BATCH_SIZE = 10  # 최대 배치 크기 (컨텍스트 한계 방지)
DEFAULT_BATCH_SIZE = 8  # 기본 배치 크기 (안전 마진)
REQUEST_TIMEOUT = 15  # 요청 타임아웃 (초)
BATCH_DELAY = 2  # 배치 간 대기 시간 (초)
MIN_CONTENT_LENGTH = 200  # 최소 본문 길이 (자)


@dataclass
class FetchResult:
    """본문 수집 결과"""

    url: str
    success: bool
    title: str | None
    content: str | None
    content_length: int
    error: str | None
    fetch_time_ms: int


class BatchContentFetcher:
    """배치 단위 본문 수집기"""

    def __init__(self, batch_size: int = DEFAULT_BATCH_SIZE):
        """
        Args:
            batch_size: 배치 크기 (최대 10)
        """
        if batch_size > MAX_BATCH_SIZE:
            print(f"⚠️ 배치 크기 {batch_size}는 최대값 {MAX_BATCH_SIZE}로 제한됩니다.")
            batch_size = MAX_BATCH_SIZE

        self.batch_size = batch_size
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            }
        )

    def _extract_content(self, html: str, url: str) -> tuple[str | None, str | None]:
        """
        HTML에서 제목과 본문 추출

        Returns:
            (title, content)
        """
        try:
            soup = BeautifulSoup(html, "html.parser")

            # 제목 추출
            title = None
            if soup.title:
                title = soup.title.string
            if not title:
                h1 = soup.find("h1")
                if h1:
                    title = h1.get_text(strip=True)

            # 불필요한 요소 제거
            for tag in soup(["script", "style", "nav", "header", "footer", "aside", "ads"]):
                tag.decompose()

            # 본문 추출 (article > main > body 우선순위)
            content = None
            for selector in ["article", "main", "[role='main']", ".content", "#content", "body"]:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(separator="\n", strip=True)
                    if len(content) > MIN_CONTENT_LENGTH:
                        break

            # 본문이 너무 짧으면 전체 body 사용
            if not content or len(content) < MIN_CONTENT_LENGTH:
                content = soup.get_text(separator="\n", strip=True)

            return title, content

        except Exception as e:
            print(f"  Content extraction error: {e}")
            return None, None

    def fetch_url(self, url: str) -> FetchResult:
        """
        단일 URL 본문 수집

        Args:
            url: 수집할 URL

        Returns:
            FetchResult
        """
        start_time = time.time()

        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            fetch_time = int((time.time() - start_time) * 1000)

            if response.status_code != 200:
                return FetchResult(
                    url=url,
                    success=False,
                    title=None,
                    content=None,
                    content_length=0,
                    error=f"HTTP_{response.status_code}",
                    fetch_time_ms=fetch_time,
                )

            # 인코딩 처리
            response.encoding = response.apparent_encoding or "utf-8"

            # 본문 추출
            title, content = self._extract_content(response.text, url)

            if not content or len(content) < MIN_CONTENT_LENGTH:
                return FetchResult(
                    url=url,
                    success=False,
                    title=title,
                    content=None,
                    content_length=len(content) if content else 0,
                    error="CONTENT_TOO_SHORT",
                    fetch_time_ms=fetch_time,
                )

            return FetchResult(
                url=url,
                success=True,
                title=title,
                content=content[:10000],  # 최대 10000자로 제한
                content_length=len(content),
                error=None,
                fetch_time_ms=fetch_time,
            )

        except requests.exceptions.Timeout:
            return FetchResult(
                url=url,
                success=False,
                title=None,
                content=None,
                content_length=0,
                error="TIMEOUT",
                fetch_time_ms=REQUEST_TIMEOUT * 1000,
            )
        except requests.exceptions.ConnectionError:
            return FetchResult(
                url=url,
                success=False,
                title=None,
                content=None,
                content_length=0,
                error="CONNECTION_ERROR",
                fetch_time_ms=int((time.time() - start_time) * 1000),
            )
        except Exception as e:
            return FetchResult(
                url=url,
                success=False,
                title=None,
                content=None,
                content_length=0,
                error=f"ERROR: {str(e)[:50]}",
                fetch_time_ms=int((time.time() - start_time) * 1000),
            )

    def fetch_batch(self, urls: list[str], batch_num: int = 1) -> list[FetchResult]:
        """
        단일 배치 처리

        Args:
            urls: URL 목록 (최대 batch_size개)
            batch_num: 배치 번호

        Returns:
            FetchResult 목록
        """
        results = []
        print(f"\n📦 배치 {batch_num} 처리 중 ({len(urls)}개 URL)...")

        for i, url in enumerate(urls, 1):
            print(f"  [{i}/{len(urls)}] {url[:60]}...", end=" ")
            result = self.fetch_url(url)

            if result.success:
                print(f"✓ ({result.content_length}자)")
            else:
                print(f"✗ {result.error}")

            results.append(result)
            time.sleep(0.5)  # Rate limiting

        return results

    def fetch_all(self, urls: list[str]) -> dict:
        """
        전체 URL 배치 분할 처리

        Args:
            urls: 전체 URL 목록

        Returns:
            {
                "articles": [...],
                "stats": {...}
            }
        """
        total_urls = len(urls)
        num_batches = (total_urls + self.batch_size - 1) // self.batch_size

        print("═══════════════════════════════════════════════════════════")
        print("  Batch Content Fetcher")
        print(f"  총 URL: {total_urls}개")
        print(f"  배치 크기: {self.batch_size}개 (최대 {MAX_BATCH_SIZE})")
        print(f"  총 배치 수: {num_batches}개")
        print("═══════════════════════════════════════════════════════════")

        all_results = []
        start_time = time.time()

        for batch_num in range(num_batches):
            batch_start = batch_num * self.batch_size
            batch_end = min(batch_start + self.batch_size, total_urls)
            batch_urls = urls[batch_start:batch_end]

            results = self.fetch_batch(batch_urls, batch_num + 1)
            all_results.extend(results)

            # 배치 간 대기 (마지막 배치 제외)
            if batch_num < num_batches - 1:
                print(f"  ⏳ 다음 배치까지 {BATCH_DELAY}초 대기...")
                time.sleep(BATCH_DELAY)

        elapsed = time.time() - start_time

        # 결과 정리
        successful = [r for r in all_results if r.success]
        failed = [r for r in all_results if not r.success]

        # 기사 형식으로 변환
        articles = []
        for result in successful:
            articles.append(
                {
                    "url": result.url,
                    "original_title": result.title,
                    "original_content": result.content,
                    "content_length": result.content_length,
                    "fetched_at": datetime.now().isoformat(),
                }
            )

        # 에러 통계
        error_counts: dict[str, int] = {}
        for result in failed:
            error = result.error or "UNKNOWN"
            error_counts[error] = error_counts.get(error, 0) + 1

        output = {
            "fetched_at": datetime.now().isoformat(),
            "batch_size": self.batch_size,
            "total_batches": num_batches,
            "total_time_sec": round(elapsed, 2),
            "stats": {
                "total_urls": total_urls,
                "success_count": len(successful),
                "fail_count": len(failed),
                "success_rate": round(len(successful) / total_urls * 100, 1) if total_urls else 0,
                "errors_by_type": error_counts,
            },
            "articles": articles,
            "failed_urls": [{"url": r.url, "error": r.error} for r in failed],
        }

        # 요약 출력
        print("\n═══════════════════════════════════════════════════════════")
        print("  완료!")
        print(f"  성공: {len(successful)}/{total_urls} ({output['stats']['success_rate']}%)")
        print(f"  실패: {len(failed)}")
        print(f"  소요 시간: {elapsed:.1f}초")
        print("═══════════════════════════════════════════════════════════")

        return output


def main():
    parser = argparse.ArgumentParser(description="Batch Content Fetcher")
    parser.add_argument("--date", help="Scan date (YYYY-MM-DD)")
    parser.add_argument("--input", help="Input JSON file with URLs")
    parser.add_argument("--output", help="Output JSON file for articles")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Batch size (max {MAX_BATCH_SIZE})",
    )

    args = parser.parse_args()

    fetcher = BatchContentFetcher(batch_size=args.batch_size)

    # 입력 파일 결정
    if args.date:
        year, month, day = args.date.split("-")
        base_path = Path(__file__).parent.parent.parent.parent
        input_path = base_path / "data" / year / month / day / "raw" / f"validated-urls-{args.date}.json"
        if not input_path.exists():
            input_path = base_path / "data" / year / month / day / "raw" / f"urls-{args.date}.json"
        output_path = base_path / "data" / year / month / day / "raw" / f"articles-{args.date}.json"
    elif args.input:
        input_path = Path(args.input)
        output_path = Path(args.output) if args.output else input_path.with_name("articles.json")
    else:
        parser.print_help()
        sys.exit(1)

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    # URL 로드
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    # URL 추출 (통일된 형식: urls 배열)
    if isinstance(data, list):
        url_entries = data
    elif isinstance(data, dict):
        # 통일된 파이프라인 형식: "urls" 배열 사용
        url_entries = data.get("urls", data.get("articles", []))
    else:
        print("Error: Invalid input format")
        sys.exit(1)

    # URL 문자열 추출
    urls = [entry.get("url", entry) if isinstance(entry, dict) else entry for entry in url_entries]

    # 본문 수집
    result = fetcher.fetch_all(urls)

    # 결과 저장
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n결과 저장: {output_path}")


if __name__ == "__main__":
    main()
