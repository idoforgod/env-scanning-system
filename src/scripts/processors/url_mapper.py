#!/usr/bin/env python3
"""
URL Mapper - 보고서 생성을 위한 URL 매핑 테이블 생성

이 스크립트는 LLM의 URL hallucination을 방지하기 위해
structured-signals에서 신호 ID → URL 매핑을 추출합니다.

사용법:
    python url_mapper.py <date>
    python url_mapper.py 2026-01-14
"""

import json
import sys
from datetime import datetime
from pathlib import Path


class URLMapper:
    """신호 ID와 URL 간의 매핑을 관리"""

    def __init__(self, base_path: str | None = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.url_map = {}
        self.stats = {"total_signals": 0, "with_url": 0, "without_url": 0, "invalid_url": 0}

    def extract_from_structured(self, date: str) -> dict:
        """structured-signals에서 URL 매핑 추출"""

        # 날짜 형식 파싱 (2026-01-14 → 2026/01/14)
        date.replace("-", "/")
        year, month, day = date.split("-")

        structured_path = self.base_path / f"data/{year}/{month}/{day}/structured/structured-signals-{date}.json"

        if not structured_path.exists():
            raise FileNotFoundError(f"Structured signals not found: {structured_path}")

        with open(structured_path, encoding="utf-8") as f:
            data = json.load(f)

        signals = data.get("signals", [])
        self.stats["total_signals"] = len(signals)

        for signal in signals:
            signal_id = signal.get("id", "")
            source = signal.get("source", {})

            # URL 추출 (다양한 필드명 지원)
            url = source.get("url") or source.get("source_url") or source.get("link")
            source_name = source.get("name", "Unknown")
            published_date = source.get("published_date", "")

            # URL 유효성 검사
            if url and isinstance(url, str) and url.startswith("http"):
                self.url_map[signal_id] = {
                    "url": url,
                    "source_name": source_name,
                    "published_date": published_date,
                    "status": "VALID",
                }
                self.stats["with_url"] += 1
            elif url in [None, "", "null", "NO_URL", "N/A"]:
                self.url_map[signal_id] = {
                    "url": None,
                    "source_name": source_name,
                    "published_date": published_date,
                    "status": "MISSING",
                }
                self.stats["without_url"] += 1
            else:
                self.url_map[signal_id] = {
                    "url": None,
                    "source_name": source_name,
                    "published_date": published_date,
                    "status": "INVALID",
                    "original_value": str(url)[:100],
                }
                self.stats["invalid_url"] += 1

        return self.url_map

    def extract_from_raw(self, date: str) -> dict:
        """raw 데이터에서 직접 URL 매핑 추출 (백업용)"""

        year, month, day = date.split("-")
        raw_dir = self.base_path / f"data/{year}/{month}/{day}/raw"

        if not raw_dir.exists():
            return {}

        raw_urls = {}

        for json_file in raw_dir.glob("*.json"):
            try:
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)

                # 다양한 키 지원
                signals = data.get("signals", []) or data.get("items", []) or data.get("articles", [])

                for signal in signals:
                    raw_id = signal.get("raw_id", "")
                    url = signal.get("url") or signal.get("source_url") or signal.get("link")

                    if raw_id and url and url.startswith("http"):
                        raw_urls[raw_id] = {
                            "url": url,
                            "source_name": signal.get("source_name", ""),
                            "source_file": json_file.name,
                        }
            except Exception as e:
                print(f"Warning: Failed to parse {json_file}: {e}")

        return raw_urls

    def save_mapping(self, date: str, output_path: str | None = None) -> str:
        """URL 매핑 테이블을 JSON 파일로 저장"""

        year, month, day = date.split("-")

        if output_path:
            out_path = Path(output_path)
        else:
            out_path = self.base_path / f"data/{year}/{month}/{day}/analysis/url-mapping-{date}.json"

        out_path.parent.mkdir(parents=True, exist_ok=True)

        output = {
            "generated_at": datetime.now().isoformat(),
            "date": date,
            "stats": self.stats,
            "mapping": self.url_map,
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        return str(out_path)

    def get_source_line(self, signal_id: str) -> str:
        """신호 ID에 대한 출처 마크다운 라인 생성"""

        if signal_id not in self.url_map:
            return "출처 정보 없음"

        info = self.url_map[signal_id]
        name = info.get("source_name", "Unknown")
        url = info.get("url")
        date = info.get("published_date", "N/A")

        if url:
            return f"**출처**: [{name}]({url}) | 발행일: {date}"
        else:
            return f"**출처**: {name} [출처 미확인] | 발행일: {date}"

    def generate_placeholder_guide(self) -> str:
        """LLM을 위한 플레이스홀더 사용 가이드 생성"""

        guide = """## URL 플레이스홀더 가이드

보고서 작성 시 출처 표시에 다음 플레이스홀더를 사용하세요:

### 형식
```
{{URL:신호ID}}
```

### 예시
```markdown
**출처**: {{URL:SIG-2026-0114-001}}
**출처**: {{URL:SIG-2026-0114-002}}
```

### 사용 가능한 신호 ID 목록
"""
        for signal_id in sorted(self.url_map.keys())[:20]:
            info = self.url_map[signal_id]
            status = "✓" if info.get("url") else "✗"
            guide += f"- {signal_id} {status}\n"

        if len(self.url_map) > 20:
            guide += f"... 외 {len(self.url_map) - 20}개\n"

        return guide


def main():
    if len(sys.argv) < 2:
        print("Usage: python url_mapper.py <date>")
        print("Example: python url_mapper.py 2026-01-14")
        sys.exit(1)

    date = sys.argv[1]
    base_path = Path(__file__).parent.parent.parent.parent  # src/scripts/processors → project root

    mapper = URLMapper(base_path)

    print(f"=== URL Mapper: {date} ===\n")

    # 1. Structured signals에서 추출
    print("1. Extracting from structured-signals...")
    try:
        mapper.extract_from_structured(date)
        print(f"   Total: {mapper.stats['total_signals']}")
        print(f"   With URL: {mapper.stats['with_url']}")
        print(f"   Without URL: {mapper.stats['without_url']}")
    except FileNotFoundError as e:
        print(f"   Error: {e}")
        sys.exit(1)

    # 2. Raw 데이터에서 백업 추출
    print("\n2. Extracting from raw data (backup)...")
    raw_urls = mapper.extract_from_raw(date)
    print(f"   Raw URLs found: {len(raw_urls)}")

    # 3. 매핑 저장
    print("\n3. Saving URL mapping...")
    output_path = mapper.save_mapping(date)
    print(f"   Saved to: {output_path}")

    # 4. 통계 출력
    print("\n=== Summary ===")
    print(
        f"URL Coverage: {mapper.stats['with_url']}/{mapper.stats['total_signals']} ({mapper.stats['with_url'] / mapper.stats['total_signals'] * 100:.1f}%)"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
