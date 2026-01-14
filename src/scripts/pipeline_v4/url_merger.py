#!/usr/bin/env python3
"""
Pipeline v4 - URL Merger

여러 크롤러에서 수집한 URL을 통합하고 중복을 제거합니다.

입력:
- data/{date}/raw/naver-urls-{date}.json
- data/{date}/raw/global-urls-{date}.json
- data/{date}/raw/google-urls-{date}.json
- data/{date}/raw/websearch-urls-{date}.json

출력:
- data/{date}/raw/urls-{date}.json

사용법:
    python url_merger.py <date>
    python url_merger.py 2026-01-14
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


class URLMerger:
    """URL 병합기 - 여러 소스의 URL을 통합"""

    def __init__(self, base_path: str | None = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.urls: list[dict] = []
        self.seen_urls: set[str] = set()
        self.stats = {"sources_loaded": 0, "total_raw": 0, "duplicates_removed": 0, "unique_urls": 0}

    def normalize_url(self, url: str) -> str:
        """URL 정규화 (중복 체크용)"""
        try:
            parsed = urlparse(url)
            # 프로토콜과 www 제거하여 정규화
            host = parsed.netloc.lower().replace("www.", "")
            path = parsed.path.rstrip("/")
            return f"{host}{path}"
        except Exception:
            return url.lower()

    def load_source(self, file_path: Path, source_name: str) -> int:
        """단일 소스 파일 로드"""
        if not file_path.exists():
            print(f"  [SKIP] {source_name}: 파일 없음")
            return 0

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"  [ERROR] {source_name}: JSON 파싱 오류")
            return 0

        # 다양한 형식 지원
        urls_list = data.get("urls", []) or data.get("items", []) or data.get("signals", [])

        count = 0
        for item in urls_list:
            url = item.get("url", "") or item.get("link", "")
            if not url or not url.startswith("http"):
                continue

            normalized = self.normalize_url(url)
            if normalized in self.seen_urls:
                self.stats["duplicates_removed"] += 1
                continue

            self.seen_urls.add(normalized)
            self.urls.append(
                {
                    "url": url,
                    "title_hint": item.get("title_hint", "") or item.get("title", "") or item.get("original_title", ""),
                    "snippet_hint": item.get("snippet_hint", "") or item.get("snippet", "") or item.get("summary", ""),
                    "source_name": item.get("source_name", source_name),
                    "source_type": item.get("source_type", "news"),
                    "discovered_from": source_name,
                    "discovered_at": datetime.now().isoformat(),
                }
            )
            count += 1

        self.stats["sources_loaded"] += 1
        print(f"  [OK] {source_name}: {count}개 URL 추가")
        return count

    def merge(self, date: str) -> None:
        """모든 소스 파일 병합"""
        year, month, day = date.split("-")
        raw_dir = self.base_path / f"data/{year}/{month}/{day}/raw"

        print(f"\n=== URL Merger - {date} ===\n")
        print("소스 파일 로드 중...")

        # 4개 크롤러 출력 파일
        sources = [
            (raw_dir / f"naver-urls-{date}.json", "naver-news"),
            (raw_dir / f"global-urls-{date}.json", "global-news"),
            (raw_dir / f"google-urls-{date}.json", "google-news"),
            (raw_dir / f"websearch-urls-{date}.json", "websearch"),
            # 기존 형식 호환
            (raw_dir / f"naver-scan-{date}.json", "naver-news-legacy"),
            (raw_dir / f"global-news-{date}.json", "global-news-legacy"),
            (raw_dir / f"google-news-{date}.json", "google-news-legacy"),
            (raw_dir / f"steeps-scan-{date}.json", "steeps-legacy"),
        ]

        for file_path, source_name in sources:
            loaded = self.load_source(file_path, source_name)
            self.stats["total_raw"] += loaded

        self.stats["unique_urls"] = len(self.urls)

    def save(self, date: str) -> str:
        """병합 결과 저장"""
        year, month, day = date.split("-")
        output_dir = self.base_path / f"data/{year}/{month}/{day}/raw"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"urls-{date}.json"

        output = {
            "discovery_date": date,
            "generated_at": datetime.now().isoformat(),
            "stage": "Stage A: URL Discovery",
            "pipeline_version": "v4",
            "stats": self.stats,
            "note": "이 URL 목록에서 Stage B가 실제 기사 본문을 수집합니다.",
            "urls": self.urls,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        return str(output_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python url_merger.py <date>")
        print("Example: python url_merger.py 2026-01-14")
        sys.exit(1)

    date = sys.argv[1]
    base_path = Path(__file__).parent.parent.parent.parent

    merger = URLMerger(base_path)
    merger.merge(date)

    output_path = merger.save(date)

    print("\n=== 병합 완료 ===")
    print(f"  총 원시 URL: {merger.stats['total_raw']}")
    print(f"  중복 제거: {merger.stats['duplicates_removed']}")
    print(f"  최종 URL: {merger.stats['unique_urls']}")
    print(f"  출력: {output_path}")

    print("\n다음 단계: Stage B (Content Fetching)")
    print(f"  python src/scripts/pipeline_v4/content_fetcher.py {date}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
