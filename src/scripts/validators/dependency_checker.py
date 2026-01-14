#!/usr/bin/env python3
"""
Dependency Checker
==================
크롤러 실행 전 필수 의존성 사전 검증

구조적 문제 5.1 해결:
- "외부 의존성 취약" 문제 방지
- 스캔 시작 전 필요한 패키지/환경 사전 검증

Usage:
    python dependency_checker.py           # 전체 검증
    python dependency_checker.py --fix     # 누락 패키지 자동 설치
    python dependency_checker.py --crawler # 크롤러 의존성만 검증
"""

import argparse
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar


@dataclass
class DependencyResult:
    """의존성 검증 결과"""

    name: str
    required: bool
    installed: bool
    version: str | None
    error: str | None


class DependencyChecker:
    """의존성 검증기"""

    # 필수 패키지 (크롤러용)
    CRAWLER_DEPENDENCIES: ClassVar[list[tuple[str, bool, str]]] = [
        ("requests", True, "HTTP 요청"),
        ("beautifulsoup4", True, "HTML 파싱"),
        ("feedparser", True, "RSS 피드 파싱"),
        ("lxml", False, "빠른 HTML 파싱 (선택)"),
    ]

    # 분석 패키지
    ANALYSIS_DEPENDENCIES: ClassVar[list[tuple[str, bool, str]]] = [
        ("pyyaml", True, "YAML 설정 파싱"),
        ("python-dateutil", False, "날짜 처리 (선택)"),
    ]

    # 전체 필수 패키지
    ALL_DEPENDENCIES: ClassVar[list[tuple[str, bool, str]]] = CRAWLER_DEPENDENCIES + ANALYSIS_DEPENDENCIES

    def __init__(self):
        self.results: list[DependencyResult] = []

    def _check_package(self, package_name: str) -> tuple[bool, str | None]:
        """
        패키지 설치 여부 확인

        Returns:
            (installed, version)
        """
        # 패키지 이름 매핑 (pip 이름 -> import 이름)
        import_map = {
            "beautifulsoup4": "bs4",
            "pyyaml": "yaml",
            "python-dateutil": "dateutil",
        }

        import_name = import_map.get(package_name, package_name)

        try:
            module = __import__(import_name)
            version = getattr(module, "__version__", "unknown")
            return True, version
        except ImportError:
            return False, None

    def check_all(self, crawler_only: bool = False) -> dict:
        """
        전체 의존성 검증

        Args:
            crawler_only: 크롤러 의존성만 검증

        Returns:
            검증 결과 딕셔너리
        """
        dependencies = self.CRAWLER_DEPENDENCIES if crawler_only else self.ALL_DEPENDENCIES
        self.results = []

        all_ok = True
        required_missing = []

        print("═══════════════════════════════════════════════════════════")
        print("  Dependency Checker")
        print("═══════════════════════════════════════════════════════════\n")

        for package_name, required, description in dependencies:
            installed, version = self._check_package(package_name)

            result = DependencyResult(
                name=package_name,
                required=required,
                installed=installed,
                version=version,
                error=None if installed else "NOT_INSTALLED",
            )
            self.results.append(result)

            # 출력
            status = "✓" if installed else ("✗" if required else "○")
            version_str = f"v{version}" if version else ""
            req_str = "(필수)" if required else "(선택)"

            print(f"  {status} {package_name:20} {version_str:12} {req_str} - {description}")

            if not installed and required:
                all_ok = False
                required_missing.append(package_name)

        print()

        # 결과 요약
        output = {
            "checked_at": datetime.now().isoformat(),
            "all_ok": all_ok,
            "total_checked": len(dependencies),
            "installed_count": sum(1 for r in self.results if r.installed),
            "missing_count": sum(1 for r in self.results if not r.installed),
            "required_missing": required_missing,
            "details": [
                {
                    "name": r.name,
                    "required": r.required,
                    "installed": r.installed,
                    "version": r.version,
                }
                for r in self.results
            ],
        }

        if all_ok:
            print("  ✅ 모든 필수 의존성이 설치되어 있습니다.")
        else:
            print(f"  ⚠️ 누락된 필수 패키지: {', '.join(required_missing)}")
            print(f"     설치 명령: pip install {' '.join(required_missing)}")

        print("═══════════════════════════════════════════════════════════")

        return output

    def fix_missing(self) -> dict:
        """
        누락된 필수 패키지 자동 설치

        Returns:
            설치 결과
        """
        # 먼저 검증
        check_result = self.check_all()

        if check_result["all_ok"]:
            return {"status": "ok", "message": "모든 의존성이 이미 설치됨"}

        missing = check_result["required_missing"]
        installed = []
        failed = []

        print("\n📦 누락된 패키지 설치 중...")

        for package in missing:
            print(f"  Installing {package}...", end=" ")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.returncode == 0:
                    print("✓")
                    installed.append(package)
                else:
                    print(f"✗ ({result.stderr[:50]})")
                    failed.append(package)
            except subprocess.TimeoutExpired:
                print("✗ (timeout)")
                failed.append(package)
            except Exception as e:
                print(f"✗ ({e})")
                failed.append(package)

        return {
            "status": "completed",
            "installed": installed,
            "failed": failed,
            "all_ok": len(failed) == 0,
        }

    def verify_crawler_ready(self) -> bool:
        """
        크롤러 실행 준비 상태 확인

        Returns:
            True if ready
        """
        result = self.check_all(crawler_only=True)
        return result["all_ok"]


def main():
    parser = argparse.ArgumentParser(description="Dependency Checker")
    parser.add_argument("--fix", action="store_true", help="자동으로 누락 패키지 설치")
    parser.add_argument("--crawler", action="store_true", help="크롤러 의존성만 검증")
    parser.add_argument("--json", action="store_true", help="JSON 형식 출력")

    args = parser.parse_args()

    checker = DependencyChecker()

    if args.fix:
        result = checker.fix_missing()
        if args.json:
            import json

            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif not result["all_ok"]:
            print(f"\n⚠️ 설치 실패: {result['failed']}")
            sys.exit(1)
    else:
        result = checker.check_all(crawler_only=args.crawler)
        if args.json:
            import json

            print(json.dumps(result, ensure_ascii=False, indent=2))

        if not result["all_ok"]:
            sys.exit(1)


if __name__ == "__main__":
    main()
