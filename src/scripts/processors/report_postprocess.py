#!/usr/bin/env python3
"""
Report Post-Processor - 보고서 생성 후 URL 주입 통합 스크립트

워크플로우:
1. url_mapper.py: structured-signals에서 URL 매핑 추출
2. (LLM이 보고서 생성 - 플레이스홀더 사용)
3. url_injector.py: 플레이스홀더를 실제 URL로 치환
4. 검증: 최종 보고서의 URL이 원본 데이터와 일치하는지 확인

사용법:
    python report_postprocess.py <date> [--verify-only]
    python report_postprocess.py 2026-01-14
    python report_postprocess.py 2026-01-14 --verify-only
"""

import json
import re
import sys
from pathlib import Path

from url_injector import URLInjector

# 같은 디렉토리의 모듈 임포트
from url_mapper import URLMapper


class ReportPostProcessor:
    """보고서 후처리 통합 클래스"""

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.mapper = URLMapper(base_path)
        self.injector = URLInjector(base_path)

    def process(self, date: str) -> dict:
        """전체 후처리 파이프라인 실행"""

        print(f"\n{'=' * 60}")
        print(f"  Report Post-Processor: {date}")
        print(f"{'=' * 60}\n")

        results = {"date": date, "steps": {}, "success": False}

        # Step 1: URL 매핑 생성
        print("Step 1: Generating URL mapping...")
        try:
            self.mapper.extract_from_structured(date)
            mapping_path = self.mapper.save_mapping(date)
            results["steps"]["mapping"] = {
                "status": "success",
                "total_signals": self.mapper.stats["total_signals"],
                "with_url": self.mapper.stats["with_url"],
                "output": mapping_path,
            }
            print(f"  ✓ {self.mapper.stats['with_url']}/{self.mapper.stats['total_signals']} URLs mapped")
        except Exception as e:
            results["steps"]["mapping"] = {"status": "failed", "error": str(e)}
            print(f"  ✗ Failed: {e}")
            return results

        # Step 2: URL 주입
        print("\nStep 2: Injecting URLs into report...")
        try:
            self.injector.url_map = self.mapper.url_map  # 매핑 공유
            success = self.injector.inject(date)
            results["steps"]["injection"] = {"status": "success" if success else "failed", "stats": self.injector.stats}
            if success:
                print(f"  ✓ {self.injector.stats['replaced_with_url']} URLs injected")
        except Exception as e:
            results["steps"]["injection"] = {"status": "failed", "error": str(e)}
            print(f"  ✗ Failed: {e}")
            return results

        # Step 3: 검증
        print("\nStep 3: Verifying final report...")
        verification = self.verify(date)
        results["steps"]["verification"] = verification
        if verification["status"] == "passed":
            print(f"  ✓ All {verification['total_sources']} source URLs verified")
        else:
            print(f"  ⚠ {verification['issues']} issues found")

        results["success"] = (
            results["steps"]["mapping"]["status"] == "success"
            and results["steps"]["injection"]["status"] == "success"
            and verification["status"] == "passed"
        )

        return results

    def verify(self, date: str) -> dict:
        """최종 보고서 검증"""

        year, month, day = date.split("-")
        report_path = self.base_path / f"data/{year}/{month}/{day}/reports/environmental-scan-{date}.md"

        if not report_path.exists():
            return {"status": "failed", "error": "Report not found"}

        with open(report_path, encoding="utf-8") as f:
            content = f.read()

        # 1. 남은 플레이스홀더 확인
        remaining_placeholders = re.findall(r"\{\{SOURCE:[^}]+\}\}", content)

        # 2. 출처 라인 추출
        source_lines = re.findall(r"\*\*출처\*\*: (.+)", content)

        # 3. URL 추출 및 원본과 비교
        url_pattern = r"\[([^\]]+)\]\((https?://[^)]+)\)"
        report_urls = []
        for line in source_lines:
            match = re.search(url_pattern, line)
            if match:
                report_urls.append(match.group(2))

        # 4. 원본 데이터와 비교
        original_urls = set()
        for info in self.mapper.url_map.values():
            if info.get("url"):
                original_urls.add(info["url"])

        # 보고서 URL이 원본에 있는지 확인
        valid_urls = sum(1 for url in report_urls if url in original_urls)
        invalid_urls = [url for url in report_urls if url not in original_urls]

        issues = len(remaining_placeholders) + len(invalid_urls)

        return {
            "status": "passed" if issues == 0 else "warning",
            "total_sources": len(source_lines),
            "remaining_placeholders": len(remaining_placeholders),
            "urls_in_report": len(report_urls),
            "valid_urls": valid_urls,
            "invalid_urls": invalid_urls[:5],  # 최대 5개만
            "issues": issues,
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python report_postprocess.py <date> [--verify-only]")
        print("Example: python report_postprocess.py 2026-01-14")
        sys.exit(1)

    date = sys.argv[1]
    verify_only = "--verify-only" in sys.argv

    base_path = Path(__file__).parent.parent.parent.parent

    processor = ReportPostProcessor(base_path)

    if verify_only:
        print(f"=== Verification Only: {date} ===\n")
        processor.mapper.extract_from_structured(date)
        result = processor.verify(date)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        result = processor.process(date)

        # 최종 결과
        print(f"\n{'=' * 60}")
        if result["success"]:
            print("  ✅ Report post-processing COMPLETE")
        else:
            print("  ❌ Report post-processing FAILED")
        print(f"{'=' * 60}\n")

        # 결과 저장
        year, month, day = date.split("-")
        log_path = base_path / f"logs/report-postprocess-{date}.json"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Log saved: {log_path}")

    return 0 if (verify_only or result["success"]) else 1


if __name__ == "__main__":
    sys.exit(main())
