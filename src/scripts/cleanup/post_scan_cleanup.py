#!/usr/bin/env python3
"""
Post-Scan Cleanup (Step 17 자동화)
==================================
환경스캐닝 워크플로우 완료 후 임시 파일 자동 정리

Gate 3 조건 검증 후 실행:
- Step 17-A: 루트 디렉토리 임시 파일 삭제
- Step 17-B: data 폴더 중간 산출물 정리

Usage:
    python post_scan_cleanup.py --date 2026-01-14
    python post_scan_cleanup.py --date 2026-01-14 --dry-run
    python post_scan_cleanup.py --date 2026-01-14 --force
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import ClassVar


class PostScanCleanup:
    """Step 17 자동화 - 워크플로우 완료 후 정리"""

    # 보호 파일 (절대 삭제 금지)
    PROTECTED_FILES: ClassVar[set[str]] = {
        "CLAUDE.md",
        "README.md",
        "WARP.md",
        "LICENSE",
        ".gitignore",
        ".pre-commit-config.yaml",
        ".python-version",
        "pyproject.toml",
    }

    # 보호 디렉토리 (삭제 금지)
    PROTECTED_DIRS: ClassVar[set[str]] = {
        ".git",
        ".claude",
        "src",
        "config",
        "signals",
        "context",
        "docs",
        "tests",
        "logs",
    }

    def __init__(self, base_path: str | None = None, dry_run: bool = False):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.dry_run = dry_run
        self.stats = {
            "root_files_deleted": 0,
            "data_files_deleted": 0,
            "data_dirs_deleted": 0,
            "errors": [],
        }

    def verify_gate3(self, date: str) -> bool:
        """
        Gate 3 조건 검증: report.md 생성 확인

        Args:
            date: 스캔 날짜 (YYYY-MM-DD)

        Returns:
            True if Gate 3 passed
        """
        year, month, day = date.split("-")
        report_path = self.base_path / "data" / year / month / day / "reports" / f"environmental-scan-{date}.md"

        if report_path.exists():
            print(f"✓ Gate 3 통과: {report_path.name} 존재")
            return True
        else:
            print(f"✗ Gate 3 실패: {report_path} 미존재")
            return False

    def cleanup_root_directory(self, date: str) -> None:
        """
        Step 17-A: 루트 디렉토리 임시 파일 삭제

        삭제 대상:
        - *-{date}.md, *-{date}.txt, *-{date}.json, *-{date}.py
        - *.sh (임시 쉘 스크립트)
        - FINAL_RUN.py, EXECUTE_UPDATE.py 등
        """
        print("\n=== Step 17-A: 루트 디렉토리 정리 ===\n")

        # 날짜별 패턴
        date_patterns = [
            f"*-{date}.md",
            f"*-{date}.txt",
            f"*-{date}.json",
            f"*-{date}.py",
            f"*{date}*.md",
            f"*{date}*.txt",
        ]

        # 고정 패턴
        fixed_patterns = [
            "FINAL_RUN.py",
            "EXECUTE_UPDATE.py",
            "*_updater*.py",
            "*_update*.py",
            "*_ranking*.py",
            "execute_*.py",
            "test_*.py",
            "verify_*.py",
            "run_*.sh",
            "*.sh",
        ]

        deleted_files = []

        # 루트 디렉토리 파일 순회
        for item in self.base_path.iterdir():
            if not item.is_file():
                continue

            # 보호 파일 확인
            if item.name in self.PROTECTED_FILES:
                continue

            should_delete = False
            matched_pattern = None

            # 날짜별 패턴 매칭
            for pattern in date_patterns:
                if item.match(pattern):
                    should_delete = True
                    matched_pattern = pattern
                    break

            # 고정 패턴 매칭
            if not should_delete:
                for pattern in fixed_patterns:
                    if item.match(pattern):
                        # .sh 파일 중 보호 대상 확인
                        if pattern == "*.sh" and item.name in self.PROTECTED_FILES:
                            continue
                        should_delete = True
                        matched_pattern = pattern
                        break

            if should_delete:
                if self.dry_run:
                    print(f"  [DRY-RUN] 삭제 예정: {item.name} (패턴: {matched_pattern})")
                else:
                    try:
                        item.unlink()
                        print(f"  ✓ 삭제: {item.name}")
                        deleted_files.append(item.name)
                        self.stats["root_files_deleted"] += 1
                    except Exception as e:
                        print(f"  ✗ 삭제 실패: {item.name} - {e}")
                        self.stats["errors"].append(f"root/{item.name}: {e}")

        if not deleted_files and not self.dry_run:
            print("  (삭제할 파일 없음)")

    def cleanup_data_directory(self, date: str) -> None:
        """
        Step 17-B: data 폴더 중간 산출물 정리

        유지 파일:
        - structured/structured-signals-{date}.json
        - reports/environmental-scan-{date}.md
        - analysis/priority-ranked-{date}.json
        - analysis/keyword-analytics-{date}.json

        삭제 대상:
        - raw/ 폴더 전체
        - filtered/ 폴더 전체
        - execution/ 폴더 전체
        - 기타 중간 산출물
        """
        print("\n=== Step 17-B: data 폴더 정리 ===\n")

        year, month, day = date.split("-")
        data_dir = self.base_path / "data" / year / month / day

        if not data_dir.exists():
            print(f"  데이터 디렉토리 없음: {data_dir}")
            return

        # 삭제 대상 폴더
        dirs_to_delete = ["raw", "filtered", "execution"]

        for dir_name in dirs_to_delete:
            target_dir = data_dir / dir_name
            if target_dir.exists():
                if self.dry_run:
                    file_count = sum(1 for _ in target_dir.rglob("*") if _.is_file())
                    print(f"  [DRY-RUN] 삭제 예정: {dir_name}/ ({file_count}개 파일)")
                else:
                    try:
                        file_count = sum(1 for _ in target_dir.rglob("*") if _.is_file())
                        shutil.rmtree(target_dir)
                        print(f"  ✓ 삭제: {dir_name}/ ({file_count}개 파일)")
                        self.stats["data_dirs_deleted"] += 1
                        self.stats["data_files_deleted"] += file_count
                    except Exception as e:
                        print(f"  ✗ 삭제 실패: {dir_name}/ - {e}")
                        self.stats["errors"].append(f"data/{dir_name}: {e}")

        # analysis 폴더 정리 (priority-ranked, keyword-analytics만 유지)
        analysis_dir = data_dir / "analysis"
        if analysis_dir.exists():
            keep_patterns = [
                f"priority-ranked-{date}.json",
                f"keyword-analytics-{date}.json",
            ]

            for item in analysis_dir.iterdir():
                if item.is_file() and item.name not in keep_patterns:
                    if self.dry_run:
                        print(f"  [DRY-RUN] 삭제 예정: analysis/{item.name}")
                    else:
                        try:
                            item.unlink()
                            print(f"  ✓ 삭제: analysis/{item.name}")
                            self.stats["data_files_deleted"] += 1
                        except Exception as e:
                            print(f"  ✗ 삭제 실패: analysis/{item.name} - {e}")
                            self.stats["errors"].append(f"analysis/{item.name}: {e}")

    def cleanup(self, date: str, force: bool = False) -> dict:
        """
        전체 정리 실행

        Args:
            date: 스캔 날짜 (YYYY-MM-DD)
            force: Gate 3 검증 생략

        Returns:
            정리 결과 통계
        """
        print("═" * 60)
        print("  Post-Scan Cleanup (Step 17)")
        print(f"  날짜: {date}")
        print(f"  모드: {'DRY-RUN (미리보기)' if self.dry_run else '실제 삭제'}")
        print("═" * 60)

        # Gate 3 검증
        if not force and not self.verify_gate3(date):
            print("\n⚠️ Gate 3 미통과. --force 옵션으로 강제 실행 가능.")
            return {"status": "gate3_failed", "stats": self.stats}

        # Step 17-A: 루트 정리
        self.cleanup_root_directory(date)

        # Step 17-B: data 폴더 정리
        self.cleanup_data_directory(date)

        # 결과 요약
        print("\n" + "═" * 60)
        print("  정리 완료!")
        print(f"  루트 파일 삭제: {self.stats['root_files_deleted']}개")
        print(f"  data 폴더 삭제: {self.stats['data_dirs_deleted']}개")
        print(f"  data 파일 삭제: {self.stats['data_files_deleted']}개")
        if self.stats["errors"]:
            print(f"  오류: {len(self.stats['errors'])}건")
            for err in self.stats["errors"]:
                print(f"    - {err}")
        print("═" * 60)

        return {"status": "completed", "stats": self.stats}


def main():
    parser = argparse.ArgumentParser(description="Post-Scan Cleanup (Step 17)")
    parser.add_argument("--date", required=True, help="Scan date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="미리보기 (실제 삭제 안함)")
    parser.add_argument("--force", action="store_true", help="Gate 3 검증 생략")

    args = parser.parse_args()

    # 날짜 형식 검증
    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print(f"Error: 잘못된 날짜 형식: {args.date} (YYYY-MM-DD 필요)")
        sys.exit(1)

    cleanup = PostScanCleanup(dry_run=args.dry_run)
    result = cleanup.cleanup(args.date, force=args.force)

    if result["status"] != "completed":
        sys.exit(1)


if __name__ == "__main__":
    main()
