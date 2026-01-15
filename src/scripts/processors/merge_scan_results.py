#!/usr/bin/env python3
"""
스캔 결과 병합 스크립트
네이버 크롤링 결과와 글로벌 WebSearch 결과를 하나의 파일로 통합

Usage:
    python merge_scan_results.py --date 2026-01-12
    python merge_scan_results.py --date 2026-01-12 --output custom-output.json
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


class ScanResultMerger:
    """다양한 소스의 스캔 결과를 병합"""

    def __init__(self, base_dir: str = "env-scanning"):
        self.base_dir = Path(base_dir)
        self.raw_dir = self.base_dir / "raw"

    def find_scan_files(self, date: str) -> dict[str, Path]:
        """해당 날짜의 모든 스캔 파일 찾기"""
        files = {}

        # 가능한 파일 패턴들
        patterns = [
            f"naver-scan-{date}.json",  # 네이버 크롤링
            f"naver-scan-test-{date}.json",  # 네이버 테스트
            f"global-news-{date}.json",  # 글로벌 6개국 신문
            f"global-news-*-{date}.json",  # 국가별 글로벌 뉴스
            f"google-news-{date}.json",  # 구글 뉴스 STEEPS 검색
            f"google-news-*-{date}.json",  # 카테고리별 구글 뉴스
            f"daily-scan-{date}.json",  # WebSearch 일반
            f"scanned-signals-{date}.json",  # 기존 스캔 결과
            f"scanned-signals-{date}-*.json",  # 마라톤 모드 등
            f"tech-signals-{date}.json",  # 기술 신호
            f"social-signals-{date}.json",  # 사회 신호
            f"economic-scan-{date}.json",  # 경제 스캔
            f"political-scan-{date}.json",  # 정치 스캔
            f"environmental-signals-{date}.json",  # 환경 신호
        ]

        for pattern in patterns:
            if "*" in pattern:
                # 와일드카드 패턴
                import glob

                matches = glob.glob(str(self.raw_dir / pattern))
                for match in matches:
                    p = Path(match)
                    files[p.stem] = p
            else:
                path = self.raw_dir / pattern
                if path.exists():
                    files[path.stem] = path

        # 날짜 포함된 모든 json 파일 추가 검색
        for f in self.raw_dir.glob(f"*{date}*.json"):
            if f.stem not in files:
                files[f.stem] = f

        return files

    def load_json(self, path: Path) -> dict:
        """JSON 파일 로드"""
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"  [WARN] {path.name} 로드 실패: {e}")
            return {}

    def extract_items(self, data: dict) -> list[dict]:
        """다양한 형식에서 신호 항목 추출"""
        # 가능한 키들
        item_keys = ["items", "signals", "new_signals", "raw_signals"]

        for key in item_keys:
            if key in data and isinstance(data[key], list):
                return data[key]

        # 데이터 자체가 리스트인 경우
        if isinstance(data, list):
            return data

        return []

    def deduplicate_by_url(self, items: list[dict]) -> list[dict]:
        """URL 기준 중복 제거"""
        seen_urls: set[str] = set()
        unique_items = []

        for item in items:
            url = item.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_items.append(item)
            elif not url:
                # URL 없는 항목은 제목으로 중복 체크
                title = item.get("title", "")
                if title and title not in seen_urls:
                    seen_urls.add(title)
                    unique_items.append(item)

        return unique_items

    def renumber_raw_ids(self, items: list[dict], date: str) -> list[dict]:
        """raw_id 재부여 (병합 후 일련번호 정리)"""
        date_compact = date.replace("-", "")

        for idx, item in enumerate(items, 1):
            old_id = item.get("raw_id", "")

            # 소스 접두어 유지
            prefix = f"RAW-NAVER-{date_compact}" if "NAVER" in old_id else f"RAW-{date_compact}"

            item["raw_id"] = f"{prefix}-{idx:03d}"

        return items

    def calculate_category_stats(self, items: list[dict]) -> dict[str, int]:
        """카테고리별 통계 계산"""
        stats = {"Social": 0, "Technological": 0, "Economic": 0, "Environmental": 0, "Political": 0, "Spiritual": 0}

        for item in items:
            category = item.get("category_hint", item.get("category", "Unknown"))
            if category in stats:
                stats[category] += 1

        # 0인 카테고리 제거
        return {k: v for k, v in stats.items() if v > 0}

    def merge(self, date: str, output_file: str | None = None) -> dict:
        """스캔 결과 병합 실행"""
        print(f"\n{'=' * 60}")
        print(f"스캔 결과 병합 - {date}")
        print(f"{'=' * 60}")

        # 1. 스캔 파일 찾기
        scan_files = self.find_scan_files(date)
        print(f"\n발견된 스캔 파일: {len(scan_files)}개")

        if not scan_files:
            print("  [ERROR] 병합할 파일이 없습니다.")
            return {}

        # 2. 모든 파일에서 항목 수집
        all_items = []
        source_stats = {}

        for name, path in scan_files.items():
            print(f"  - {path.name}")
            data = self.load_json(path)
            items = self.extract_items(data)

            if items:
                print(f"    → {len(items)}건 추출")
                source_stats[name] = len(items)
                all_items.extend(items)
            else:
                print("    → 항목 없음")

        print(f"\n총 수집: {len(all_items)}건")

        # 3. URL 기준 중복 제거
        unique_items = self.deduplicate_by_url(all_items)
        duplicates_removed = len(all_items) - len(unique_items)
        print(f"중복 제거: {duplicates_removed}건")
        print(f"최종 결과: {len(unique_items)}건")

        # 4. raw_id 재부여
        unique_items = self.renumber_raw_ids(unique_items, date)

        # 5. 카테고리 통계
        category_stats = self.calculate_category_stats(unique_items)

        # 6. 결과 구조화
        now = datetime.now()
        result = {
            "scan_date": date,
            "scan_time": now.strftime("%H:%M:%S"),
            "merged_at": now.isoformat(),
            "source": "merged_scan_results",
            "total_scanned": len(unique_items),
            "by_category": category_stats,
            "merge_stats": {
                "files_merged": len(scan_files),
                "total_before_dedup": len(all_items),
                "duplicates_removed": duplicates_removed,
                "source_breakdown": source_stats,
            },
            "items": unique_items,
        }

        # 7. 결과 저장
        if output_file is None:
            output_file = f"scanned-signals-{date}-merged.json"

        output_path = self.raw_dir / output_file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n결과 저장: {output_path}")
        print("\n카테고리별 분포:")
        for cat, count in category_stats.items():
            print(f"  - {cat}: {count}건")

        return result


def main():
    parser = argparse.ArgumentParser(description="스캔 결과 병합")
    parser.add_argument("--date", required=True, help="스캔 날짜 (YYYY-MM-DD)")
    parser.add_argument("--output", help="출력 파일명")
    parser.add_argument("--base-dir", default="env-scanning", help="기본 디렉토리")

    args = parser.parse_args()

    merger = ScanResultMerger(args.base_dir)
    result = merger.merge(args.date, args.output)

    if result:
        print(f"\n✅ 병합 완료: {result['total_scanned']}건")
    else:
        print("\n❌ 병합 실패")
        exit(1)


if __name__ == "__main__":
    main()
