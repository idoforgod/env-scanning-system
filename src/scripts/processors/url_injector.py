#!/usr/bin/env python3
"""
URL Injector - 보고서의 플레이스홀더를 실제 URL로 치환

이 스크립트는 LLM이 생성한 보고서에서 {{SOURCE:신호ID}} 플레이스홀더를
실제 URL로 치환합니다. LLM의 URL hallucination을 완전히 방지합니다.

사용법:
    python url_injector.py <date>
    python url_injector.py 2026-01-14
"""

import json
import re
import sys
from pathlib import Path


class URLInjector:
    """보고서의 플레이스홀더를 실제 URL로 치환"""

    def __init__(self, base_path: str | None = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.url_map = {}
        self.stats = {"placeholders_found": 0, "replaced_with_url": 0, "replaced_without_url": 0, "not_found": 0}

    def load_url_mapping(self, date: str) -> bool:
        """URL 매핑 파일 로드"""

        year, month, day = date.split("-")
        mapping_path = self.base_path / f"data/{year}/{month}/{day}/analysis/url-mapping-{date}.json"

        if mapping_path.exists():
            with open(mapping_path, encoding="utf-8") as f:
                data = json.load(f)
                self.url_map = data.get("mapping", {})
                print(f"  Loaded {len(self.url_map)} URL mappings from {mapping_path.name}")
                return True

        # 매핑 파일 없으면 structured-signals에서 직접 로드
        print("  URL mapping not found, loading from structured-signals...")
        return self._load_from_structured(date)

    def _load_from_structured(self, date: str) -> bool:
        """structured-signals에서 직접 URL 매핑 로드"""

        year, month, day = date.split("-")
        structured_path = self.base_path / f"data/{year}/{month}/{day}/structured/structured-signals-{date}.json"

        if not structured_path.exists():
            print(f"  ERROR: Structured signals not found: {structured_path}")
            return False

        with open(structured_path, encoding="utf-8") as f:
            data = json.load(f)

        for signal in data.get("signals", []):
            signal_id = signal.get("id", "")
            source = signal.get("source", {})

            self.url_map[signal_id] = {
                "url": source.get("url"),
                "source_name": source.get("name", "Unknown"),
                "published_date": source.get("published_date", "N/A"),
            }

        print(f"  Loaded {len(self.url_map)} signals from structured-signals")
        return True

    def get_source_line(self, signal_id: str) -> str:
        """신호 ID에 대한 출처 마크다운 라인 생성"""

        if signal_id not in self.url_map:
            self.stats["not_found"] += 1
            return f"[신호 {signal_id} 정보 없음]"

        info = self.url_map[signal_id]
        name = info.get("source_name", "Unknown")
        url = info.get("url")
        pub_date = info.get("published_date", "N/A")

        if url and isinstance(url, str) and url.startswith("http"):
            self.stats["replaced_with_url"] += 1
            return f"**출처**: [{name}]({url}) | 발행일: {pub_date}"
        else:
            self.stats["replaced_without_url"] += 1
            return f"**출처**: {name} [출처 미확인] | 발행일: {pub_date}"

    def generate_source_list(self) -> str:
        """전체 출처 목록 생성"""

        lines = []
        with_url = []
        without_url = []

        for signal_id, info in sorted(self.url_map.items()):
            name = info.get("source_name", "Unknown")
            url = info.get("url")

            if url and isinstance(url, str) and url.startswith("http"):
                with_url.append(f"- [{name}]({url}) ({signal_id})")
            else:
                without_url.append(f"- {name} [출처 미확인] ({signal_id})")

        if with_url:
            lines.append("### 검증된 출처 (URL 확인됨)")
            lines.extend(with_url[:30])  # 최대 30개
            if len(with_url) > 30:
                lines.append(f"... 외 {len(with_url) - 30}개")

        if without_url:
            lines.append("\n### 미확인 출처 (URL 없음)")
            lines.extend(without_url[:10])  # 최대 10개
            if len(without_url) > 10:
                lines.append(f"... 외 {len(without_url) - 10}개")

        return "\n".join(lines)

    def process_report(self, report_content: str) -> str:
        """보고서의 모든 플레이스홀더 치환"""

        # {{SOURCE:신호ID}} 패턴 찾기
        source_pattern = r"\{\{SOURCE:([^}]+)\}\}"

        def replace_source(match):
            signal_id = match.group(1)
            self.stats["placeholders_found"] += 1
            return self.get_source_line(signal_id)

        # 개별 출처 플레이스홀더 치환
        result = re.sub(source_pattern, replace_source, report_content)

        # {{SOURCE_LIST}} 플레이스홀더 치환
        if "{{SOURCE_LIST}}" in result:
            source_list = self.generate_source_list()
            result = result.replace("{{SOURCE_LIST}}", source_list)

        return result

    def inject(self, date: str) -> bool:
        """메인 처리 함수"""

        year, month, day = date.split("-")

        # 1. URL 매핑 로드
        if not self.load_url_mapping(date):
            return False

        # 2. 보고서 파일 찾기
        report_dir = self.base_path / f"data/{year}/{month}/{day}/reports"
        report_files = list(report_dir.glob(f"environmental-scan-{date}*.md"))

        if not report_files:
            print(f"  ERROR: No report files found in {report_dir}")
            return False

        # 3. 각 보고서 처리
        for report_path in report_files:
            print(f"\n  Processing: {report_path.name}")

            with open(report_path, encoding="utf-8") as f:
                original_content = f.read()

            # 플레이스홀더 존재 확인
            placeholder_count = len(re.findall(r"\{\{SOURCE:[^}]+\}\}", original_content))

            if placeholder_count == 0:
                # 플레이스홀더가 없으면 직접 URL 작성 여부 확인
                direct_url_count = len(re.findall(r"\*\*출처\*\*: \[[^\]]+\]\(https?://[^)]+\)", original_content))
                if direct_url_count > 0:
                    print(f"    ⚠ WARNING: {direct_url_count} direct URLs found (LLM hallucination risk)")
                    print("    → Attempting to fix by matching with URL map...")
                    processed = self._fix_direct_urls(original_content)
                else:
                    print("    No placeholders or direct URLs found")
                    continue
            else:
                print(f"    Found {placeholder_count} placeholders")
                processed = self.process_report(original_content)

            # 4. 결과 저장 (원본 덮어쓰기)
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(processed)

            print(f"    ✓ Saved: {report_path.name}")

        return True

    def _fix_direct_urls(self, content: str) -> str:
        """직접 작성된 URL을 실제 URL로 교체 (백업 메커니즘)"""

        # 출처 라인 패턴: **출처**: [소스명](URL) | 발행일: ...
        pattern = r"\*\*출처\*\*: \[([^\]]+)\]\(https?://[^)]+\) \| 발행일: ([0-9-]+)"

        def fix_source_line(match):
            source_name = match.group(1)
            pub_date = match.group(2)

            # 소스명으로 URL 매핑 찾기
            for _signal_id, info in self.url_map.items():
                if info.get("source_name", "") == source_name:
                    url = info.get("url")
                    if url and url.startswith("http"):
                        self.stats["replaced_with_url"] += 1
                        return f"**출처**: [{source_name}]({url}) | 발행일: {pub_date}"

            # 매핑 없으면 [출처 미확인]으로 변경
            self.stats["replaced_without_url"] += 1
            return f"**출처**: {source_name} [출처 미확인] | 발행일: {pub_date}"

        return re.sub(pattern, fix_source_line, content)


def main():
    if len(sys.argv) < 2:
        print("Usage: python url_injector.py <date>")
        print("Example: python url_injector.py 2026-01-14")
        sys.exit(1)

    date = sys.argv[1]
    base_path = Path(__file__).parent.parent.parent.parent  # src/scripts/processors → project root

    injector = URLInjector(base_path)

    print(f"=== URL Injector: {date} ===\n")

    # 1. URL 주입 실행
    print("1. Loading URL mappings...")
    success = injector.inject(date)

    if not success:
        print("\n❌ URL injection failed")
        sys.exit(1)

    # 2. 통계 출력
    print("\n=== Summary ===")
    print(f"Placeholders found: {injector.stats['placeholders_found']}")
    print(f"Replaced with URL: {injector.stats['replaced_with_url']}")
    print(f"Replaced without URL: {injector.stats['replaced_without_url']}")
    print(f"Not found in mapping: {injector.stats['not_found']}")

    print("\n✅ URL injection complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
