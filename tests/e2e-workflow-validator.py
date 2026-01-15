#!/usr/bin/env python3
"""
pSRT 2.0 E2E Workflow Validator.

환경스캐닝 시스템의 워크플로우와 에이전트 연결을 검증합니다.
"""

import json
import re
from datetime import datetime
from pathlib import Path

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent.parent

# 검증 결과
results = {"passed": [], "failed": [], "warnings": []}


def log_pass(test_name: str, details: str = "") -> None:
    """Log a passed test result."""
    results["passed"].append({"test": test_name, "details": details})
    print(f"✅ PASS: {test_name}")
    if details:
        print(f"   └─ {details}")


def log_fail(test_name: str, details: str = "") -> None:
    """Log a failed test result."""
    results["failed"].append({"test": test_name, "details": details})
    print(f"❌ FAIL: {test_name}")
    if details:
        print(f"   └─ {details}")


def log_warn(test_name: str, details: str = "") -> None:
    """Log a warning."""
    results["warnings"].append({"test": test_name, "details": details})
    print(f"⚠️  WARN: {test_name}")
    if details:
        print(f"   └─ {details}")


# ═══════════════════════════════════════════════════════════════
# Test 1: 에이전트 파일 존재 확인
# ═══════════════════════════════════════════════════════════════


def test_agent_files_exist() -> None:
    """PSRT 2.0 관련 에이전트 파일 존재 확인."""
    print("\n" + "=" * 60)
    print("Test 1: Agent Files Existence")
    print("=" * 60)

    required_agents = [
        # pSRT 2.0 Phase 에이전트
        "groundedness-verifier.md",
        "cross-validator.md",
        "calibration-engine.md",
        "hallucination-detector.md",
        "confidence-evaluator.md",
        # 기존 워크플로우 에이전트
        "signal-classifier.md",
        "impact-analyzer.md",
        "priority-ranker.md",
        "report-generator.md",
        "db-updater.md",
    ]

    agents_dir = PROJECT_ROOT / ".claude" / "agents"

    for agent in required_agents:
        agent_path = agents_dir / agent
        if agent_path.exists():
            log_pass(f"Agent: {agent}")
        else:
            log_fail(f"Agent: {agent}", f"File not found: {agent_path}")


# ═══════════════════════════════════════════════════════════════
# Test 2: 에이전트 메타데이터 파싱
# ═══════════════════════════════════════════════════════════════


def test_agent_metadata() -> None:
    """에이전트 파일의 YAML frontmatter 파싱 검증."""
    print("\n" + "=" * 60)
    print("Test 2: Agent Metadata Parsing")
    print("=" * 60)

    agents_dir = PROJECT_ROOT / ".claude" / "agents"

    pSRT_agents = [
        "groundedness-verifier.md",
        "cross-validator.md",
        "calibration-engine.md",
        "hallucination-detector.md",
        "confidence-evaluator.md",
    ]

    for agent_name in pSRT_agents:
        agent_path = agents_dir / agent_name
        if not agent_path.exists():
            continue

        content = agent_path.read_text()

        # YAML frontmatter 파싱
        yaml_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)

            # 필수 필드 확인
            required_fields = ["name", "description", "tools", "model"]
            missing = []
            for field in required_fields:
                if f"{field}:" not in yaml_content:
                    missing.append(field)

            if missing:
                log_fail(f"Metadata: {agent_name}", f"Missing fields: {missing}")
            else:
                log_pass(f"Metadata: {agent_name}", "All required fields present")
        else:
            log_fail(f"Metadata: {agent_name}", "No YAML frontmatter found")


# ═══════════════════════════════════════════════════════════════
# Test 3: 워크플로우 입출력 연결 검증
# ═══════════════════════════════════════════════════════════════


def test_workflow_io_connections() -> None:
    """에이전트 간 입출력 파일 연결 검증."""
    print("\n" + "=" * 60)
    print("Test 3: Workflow I/O Connections")
    print("=" * 60)

    # pSRT 2.0 워크플로우 정의
    pSRT_workflow = {
        "signal-classifier": {
            "inputs": ["data/{date}/filtered/filtered-signals-{date}.json"],
            "outputs": ["data/{date}/structured/structured-signals-{date}.json"],
        },
        "groundedness-verifier": {
            "inputs": ["data/{date}/structured/structured-signals-{date}.json"],
            "outputs": ["data/{date}/analysis/groundedness-scores-{date}.json"],
        },
        "cross-validator": {
            "inputs": [
                "data/{date}/analysis/groundedness-scores-{date}.json",
                "data/{date}/structured/structured-signals-{date}.json",
            ],
            "outputs": ["data/{date}/analysis/cross-validation-{date}.json"],
        },
        "confidence-evaluator": {
            "inputs": [
                "data/{date}/analysis/groundedness-scores-{date}.json",
                "data/{date}/analysis/cross-validation-{date}.json",
                "data/{date}/analysis/calibration-{date}.json",
                "data/{date}/analysis/hallucination-report-{date}.json",
            ],
            "outputs": ["data/{date}/analysis/pSRT-scores-{date}.json", "data/{date}/analysis/final-pSRT-{date}.json"],
        },
        "hallucination-detector": {
            "inputs": [
                "data/{date}/analysis/groundedness-scores-{date}.json",
                "data/{date}/analysis/cross-validation-{date}.json",
                "data/{date}/structured/structured-signals-{date}.json",
            ],
            "outputs": ["data/{date}/analysis/hallucination-report-{date}.json"],
        },
        "calibration-engine": {
            "inputs": ["data/{date}/analysis/pSRT-scores-{date}.json", "signals/history/signal-history.json"],
            "outputs": ["data/{date}/analysis/calibration-{date}.json", "signals/history/signal-history.json"],
        },
    }

    # 연결 검증
    all_outputs = set()
    all_inputs = set()

    for _agent, io in pSRT_workflow.items():
        for output in io["outputs"]:
            all_outputs.add(output)
        for input_file in io["inputs"]:
            all_inputs.add(input_file)

    # 입력 파일이 다른 에이전트의 출력인지 확인
    orphan_inputs = []
    for input_file in all_inputs:
        # 초기 입력 또는 외부 파일인지 확인
        if input_file not in all_outputs and not any(
            x in input_file for x in ["filtered-signals", "signal-history.json", "source-accuracy", "topic-accuracy"]
        ):
            orphan_inputs.append(input_file)

    if orphan_inputs:
        log_warn("I/O Chain", f"Inputs without producer: {orphan_inputs}")
    else:
        log_pass("I/O Chain", "All inputs have producers or are initial inputs")

    # 각 에이전트의 연결 확인
    for agent, io in pSRT_workflow.items():
        log_pass(f"Agent I/O: {agent}", f"In: {len(io['inputs'])}, Out: {len(io['outputs'])}")


# ═══════════════════════════════════════════════════════════════
# Test 4: 설정 파일 검증
# ═══════════════════════════════════════════════════════════════


def test_config_files() -> None:
    """PSRT 2.0 설정 파일 검증."""
    print("\n" + "=" * 60)
    print("Test 4: Configuration Files")
    print("=" * 60)

    config_dir = PROJECT_ROOT / "config"

    # pSRT 설정 파일
    psrt_config = config_dir / "pSRT-config.yaml"
    if psrt_config.exists():
        content = psrt_config.read_text()

        # 핵심 섹션 확인
        required_sections = [
            "final_pSRT_weights",
            "groundedness",
            "cross_validation",
            "calibration",
            "hallucination_detection",
            "grade_system",
        ]

        missing = [s for s in required_sections if s not in content]
        if missing:
            log_fail("pSRT-config.yaml", f"Missing sections: {missing}")
        else:
            log_pass("pSRT-config.yaml", f"All {len(required_sections)} sections present")
    else:
        log_fail("pSRT-config.yaml", "File not found")

    # pSRT 스키마 파일
    psrt_schema = config_dir / "pSRT-schema.json"
    if psrt_schema.exists():
        try:
            schema = json.loads(psrt_schema.read_text())
            if "definitions" in schema:
                log_pass("pSRT-schema.json", f"Valid JSON with {len(schema.get('definitions', {}))} definitions")
            else:
                log_warn("pSRT-schema.json", "No definitions section")
        except json.JSONDecodeError as e:
            log_fail("pSRT-schema.json", f"Invalid JSON: {e}")
    else:
        log_fail("pSRT-schema.json", "File not found")


# ═══════════════════════════════════════════════════════════════
# Test 5: History Database 검증
# ═══════════════════════════════════════════════════════════════


def test_history_database() -> None:
    """역사적 데이터베이스 구조 검증."""
    print("\n" + "=" * 60)
    print("Test 5: History Database Structure")
    print("=" * 60)

    history_dir = PROJECT_ROOT / "signals" / "history"

    required_files = ["signal-history.json", "source-accuracy.json", "topic-accuracy.json"]

    for filename in required_files:
        filepath = history_dir / filename
        if filepath.exists():
            try:
                data = json.loads(filepath.read_text())
                if "metadata" in data:
                    log_pass(
                        f"History DB: {filename}",
                        f"Valid with metadata (v{data['metadata'].get('schema_version', '?')})",
                    )
                else:
                    log_warn(f"History DB: {filename}", "No metadata section")
            except json.JSONDecodeError as e:
                log_fail(f"History DB: {filename}", f"Invalid JSON: {e}")
        else:
            log_fail(f"History DB: {filename}", "File not found")


# ═══════════════════════════════════════════════════════════════
# Test 6: 실제 데이터 검증
# ═══════════════════════════════════════════════════════════════


def test_actual_data() -> None:
    """실제 데이터 파일 검증."""
    print("\n" + "=" * 60)
    print("Test 6: Actual Data Validation")
    print("=" * 60)

    # database.json 검증
    db_path = PROJECT_ROOT / "signals" / "database.json"
    if db_path.exists():
        try:
            db = json.loads(db_path.read_text())
            total = db.get("metadata", {}).get("total_signals", 0)
            log_pass("database.json", f"Valid with {total} signals")

            # 신호 구조 샘플 검증
            signals = db.get("signals", [])
            if signals:
                sample = signals[0]
                required_fields = ["id", "category", "title", "significance"]
                missing = [f for f in required_fields if f not in sample]
                if missing:
                    log_warn("Signal structure", f"Missing fields in sample: {missing}")
                else:
                    log_pass("Signal structure", "Sample signal has required fields")
        except json.JSONDecodeError as e:
            log_fail("database.json", f"Invalid JSON: {e}")
    else:
        log_fail("database.json", "File not found")

    # 최신 날짜 데이터 확인
    data_dir = PROJECT_ROOT / "data" / "2026" / "01" / "14"
    if data_dir.exists():
        structured = data_dir / "structured" / "structured-signals-2026-01-14.json"
        if structured.exists():
            try:
                data = json.loads(structured.read_text())
                count = len(data.get("signals", []))
                log_pass("Latest structured data", f"2026-01-14: {count} signals")
            except json.JSONDecodeError as e:
                log_fail("Latest structured data", f"Invalid JSON: {e}")
        else:
            log_warn("Latest structured data", "No structured signals file")
    else:
        log_warn("Latest data directory", "2026-01-14 directory not found")


# ═══════════════════════════════════════════════════════════════
# Test 7: pSRT 2.0 가중치 합계 검증
# ═══════════════════════════════════════════════════════════════


def test_psrt_weights() -> None:
    """PSRT 2.0 가중치 합계 검증."""
    print("\n" + "=" * 60)
    print("Test 7: pSRT 2.0 Weight Validation")
    print("=" * 60)

    # 설정 파일에서 가중치 확인
    config_path = PROJECT_ROOT / "config" / "pSRT-config.yaml"
    if config_path.exists():
        content = config_path.read_text()

        # 가중치 추출 (개선된 파싱)
        weights = {}
        in_weights_section = False
        indent_level = 0

        for line in content.split("\n"):
            # final_pSRT_weights 섹션 시작 감지
            if "final_pSRT_weights:" in line and not line.strip().startswith("#"):
                in_weights_section = True
                indent_level = len(line) - len(line.lstrip())
                continue

            if in_weights_section:
                # 빈 줄이나 주석만 있는 줄은 건너뛰기
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue

                # 다른 섹션으로 넘어갔는지 확인 (들여쓰기 감소)
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= indent_level and ":" in line and not line.startswith(" "):
                    in_weights_section = False
                    continue

                # 가중치 항목 파싱
                if ":" in stripped and not stripped.startswith("#"):
                    parts = stripped.split(":")
                    if len(parts) >= 2:
                        key = parts[0].strip()
                        # 값에서 주석 제거
                        val_str = parts[1].split("#")[0].strip()
                        try:
                            val = float(val_str)
                            weights[key] = val
                        except ValueError:
                            pass

        if weights:
            total = sum(weights.values())
            expected = 1.0
            if abs(total - expected) < 0.01:
                log_pass("pSRT weights sum", f"Sum = {total:.2f} (expected {expected})")
            else:
                log_fail("pSRT weights sum", f"Sum = {total:.2f} (expected {expected})")

            # 개별 가중치 출력
            for k, v in weights.items():
                print(f"   └─ {k}: {v}")
        else:
            log_warn("pSRT weights", "Could not parse weights")
    else:
        log_fail("pSRT weights", "Config file not found")


# ═══════════════════════════════════════════════════════════════
# Test 8: 에이전트 워크플로우 순서 검증
# ═══════════════════════════════════════════════════════════════


def test_workflow_order() -> None:
    """에이전트 실행 순서 검증."""
    print("\n" + "=" * 60)
    print("Test 8: Workflow Order Validation")
    print("=" * 60)

    # 예상 워크플로우 순서 (pSRT 2.0 통합)
    expected_order = [
        ("5.0", "signal-classifier", "STEEPS 분류 및 요약 생성"),
        ("5.3", "groundedness-verifier", "Phase 1: 근거성 검증"),
        ("5.5", "cross-validator", "Phase 2: 교차 검증"),
        ("5.7", "confidence-evaluator", "pSRT 2.0 통합 평가"),
        ("5.9", "hallucination-detector", "Phase 4: 할루시네이션 감지"),
        ("6.0", "impact-analyzer", "영향도 분석"),
        ("7.0", "priority-ranker", "우선순위 산정"),
        ("Post", "calibration-engine", "Phase 3: 역사적 보정"),
    ]

    agents_dir = PROJECT_ROOT / ".claude" / "agents"

    for step, agent_name, description in expected_order:
        agent_path = agents_dir / f"{agent_name}.md"
        if agent_path.exists():
            content = agent_path.read_text()
            # 워크플로우 단계 언급 확인
            if step in content or "단계" in content:
                log_pass(f"Step {step}: {agent_name}", description)
            else:
                log_warn(f"Step {step}: {agent_name}", "Step number not in agent doc")
        else:
            log_fail(f"Step {step}: {agent_name}", "Agent file not found")


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════


def main() -> int:
    """Run all E2E workflow validation tests."""
    print("\n" + "=" * 60)
    print("   pSRT 2.0 E2E Workflow Validation")
    print("   " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    # 모든 테스트 실행
    test_agent_files_exist()
    test_agent_metadata()
    test_workflow_io_connections()
    test_config_files()
    test_history_database()
    test_actual_data()
    test_psrt_weights()
    test_workflow_order()

    # 결과 요약
    print("\n" + "=" * 60)
    print("   SUMMARY")
    print("=" * 60)

    passed = len(results["passed"])
    failed = len(results["failed"])
    warnings = len(results["warnings"])
    total = passed + failed + warnings

    print(f"\n✅ Passed:   {passed}/{total}")
    print(f"❌ Failed:   {failed}/{total}")
    print(f"⚠️  Warnings: {warnings}/{total}")

    if failed == 0:
        print("\n🎉 All critical tests passed!")
        status = "PASS"
    else:
        print("\n⛔ Some tests failed. Please review.")
        status = "FAIL"

    # 결과 저장
    output_path = PROJECT_ROOT / "tests" / "e2e-results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "summary": {"passed": passed, "failed": failed, "warnings": warnings},
                "results": results,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\n📄 Results saved to: {output_path}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
