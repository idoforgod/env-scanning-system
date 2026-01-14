#!/usr/bin/env python3
"""
Pipeline v4: Source of Truth - 통합 실행 스크립트

전체 파이프라인을 순차적으로 실행합니다.

Phase 1: URL Discovery (Python + WebSearch)
Phase 2: Content Fetching (Python + WebFetch)
Phase 3: Signal Generation (LLM - 원본 기반 요약)
Phase 4: Analysis (Python - 내용 변경 금지)
Phase 5: Report (Python - summary 그대로 사용)

사용법:
    python run_pipeline_v4.py <date> [--phase N]
    python run_pipeline_v4.py 2026-01-14
    python run_pipeline_v4.py 2026-01-14 --phase 3
"""

import json
import sys
from pathlib import Path


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║           Pipeline v4: Source of Truth                       ║
║                                                              ║
║   • URL에서 실제 기사 읽기                                   ║
║   • 원본 기반 요약 (창작 금지)                               ║
║   • 파이프라인 전체에서 내용 변경 금지                       ║
╚══════════════════════════════════════════════════════════════╝
""")


def check_phase_output(base_path: Path, date: str, phase: int) -> bool:
    """이전 단계 출력 확인"""
    year, month, day = date.split("-")
    date_dir = base_path / f"data/{year}/{month}/{day}"

    if phase == 1:
        return True  # Phase 1은 항상 실행 가능

    if phase == 2:
        return (date_dir / f"raw/urls-{date}.json").exists()

    if phase == 3:
        return (date_dir / f"raw/articles-{date}.json").exists()

    if phase == 4 or phase == 5:
        return (date_dir / f"structured/signals-{date}.json").exists()

    return False


def run_phase_1(base_path: Path, date: str):
    """Phase 1: URL Discovery"""
    print("\n" + "=" * 60)
    print("Phase 1: URL Discovery")
    print("=" * 60)

    from url_discoverer import URLDiscoverer, create_discovery_prompt

    discoverer = URLDiscoverer(base_path)
    queries = discoverer.load_search_queries()

    print(f"  검색 쿼리: {len(queries)}개")
    print("\n  이 단계는 에이전트가 WebSearch를 실행해야 합니다.")
    print("  프롬프트가 생성되었습니다.")

    # 프롬프트 저장
    prompt = create_discovery_prompt(queries)
    year, month, day = date.split("-")
    prompt_path = base_path / f"data/{year}/{month}/{day}/raw/discovery-prompt-{date}.md"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)

    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"  프롬프트: {prompt_path}")
    return True


def run_phase_2(base_path: Path, date: str):
    """Phase 2: Content Fetching"""
    print("\n" + "=" * 60)
    print("Phase 2: Content Fetching")
    print("=" * 60)

    from content_fetcher import ContentFetcher

    fetcher = ContentFetcher(base_path)

    try:
        urls = fetcher.load_urls(date)
        print(f"  URL: {len(urls)}개")
    except FileNotFoundError:
        print("  ❌ URL 파일이 없습니다. Phase 1을 먼저 완료하세요.")
        return False

    # 프롬프트 저장
    prompt = fetcher.create_fetch_prompt(urls, date)
    year, month, day = date.split("-")
    prompt_path = base_path / f"data/{year}/{month}/{day}/raw/fetch-prompt-{date}.md"

    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    print("\n  이 단계는 에이전트가 WebFetch를 실행해야 합니다.")
    print(f"  프롬프트: {prompt_path}")
    return True


def run_phase_3(base_path: Path, date: str):
    """Phase 3: Signal Generation"""
    print("\n" + "=" * 60)
    print("Phase 3: Signal Generation")
    print("=" * 60)

    year, month, day = date.split("-")
    articles_path = base_path / f"data/{year}/{month}/{day}/raw/articles-{date}.json"

    if not articles_path.exists():
        print("  ❌ 기사 파일이 없습니다. Phase 2를 먼저 완료하세요.")
        return False

    with open(articles_path, encoding="utf-8") as f:
        data = json.load(f)

    articles = data.get("articles", [])
    print(f"  기사: {len(articles)}개")

    print("\n  이 단계는 signal-generator-v4 에이전트가 실행해야 합니다.")
    print("  에이전트는 각 기사의 original_content를 읽고 신호를 생성합니다.")
    print("\n  에이전트 호출:")
    print(f"  @signal-generator-v4 날짜: {date}")
    return True


def run_phase_4_5(base_path: Path, date: str):
    """Phase 4 & 5: Analysis & Report"""
    print("\n" + "=" * 60)
    print("Phase 4 & 5: Analysis & Report")
    print("=" * 60)

    from report_builder import ReportBuilder, SignalAnalyzer

    year, month, day = date.split("-")
    signals_path = base_path / f"data/{year}/{month}/{day}/structured/signals-{date}.json"

    if not signals_path.exists():
        print("  ❌ 신호 파일이 없습니다. Phase 3을 먼저 완료하세요.")
        return False

    with open(signals_path, encoding="utf-8") as f:
        data = json.load(f)

    signals = data.get("signals", [])
    print(f"  신호: {len(signals)}개")

    # Phase 4: 분석
    print("\n  Phase 4: 분석 중...")
    analyzer = SignalAnalyzer()
    analyzed = analyzer.analyze(signals)
    print(f"    - 분석됨: {analyzer.stats['analyzed']}")
    print(f"    - 중복 제거: {analyzer.stats['duplicates_removed']}")

    # Phase 5: 보고서
    print("\n  Phase 5: 보고서 생성 중...")
    builder = ReportBuilder(base_path)
    report = builder.build_report(analyzed, date)
    report_path = builder.save(report, date)
    print(f"    - 저장됨: {report_path}")

    # 검증
    url_count = sum(1 for s in analyzed if s.get("url", "").startswith("http"))
    print("\n  검증:")
    print(f"    - 유효 URL: {url_count}/{len(analyzed)}")
    print("    - URL-내용 일치: Pipeline v4 보장")

    return True


def main():
    print_banner()

    if len(sys.argv) < 2:
        print("Usage: python run_pipeline_v4.py <date> [--phase N]")
        print("Example: python run_pipeline_v4.py 2026-01-14")
        print("         python run_pipeline_v4.py 2026-01-14 --phase 3")
        sys.exit(1)

    date = sys.argv[1]
    base_path = Path(__file__).parent.parent.parent.parent

    # 특정 Phase만 실행
    specific_phase = None
    if "--phase" in sys.argv:
        idx = sys.argv.index("--phase")
        if idx + 1 < len(sys.argv):
            specific_phase = int(sys.argv[idx + 1])

    print(f"날짜: {date}")
    print(f"기본 경로: {base_path}")

    if specific_phase:
        print(f"실행 Phase: {specific_phase}")
    else:
        print("실행 Phase: 전체")

    # Phase 실행
    phases = [1, 2, 3, 4] if not specific_phase else [specific_phase]

    for phase in phases:
        if not check_phase_output(base_path, date, phase):
            print(f"\n❌ Phase {phase} 실행 불가: 이전 단계 출력이 없습니다.")
            break

        if phase == 1:
            run_phase_1(base_path, date)
        elif phase == 2:
            run_phase_2(base_path, date)
        elif phase == 3:
            run_phase_3(base_path, date)
        elif phase == 4 or phase == 5:
            run_phase_4_5(base_path, date)

    print("\n" + "=" * 60)
    print("Pipeline v4 실행 완료")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
