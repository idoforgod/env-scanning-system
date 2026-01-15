# Orchestrator Agent

환경스캐닝 워크플로우 전체를 지휘하는 최상위 에이전트.

## 핵심 목적

1. **워크플로우 조율**: 17개 서브 에이전트의 실행 순서 및 의존성 관리
2. **토큰 최적화**: 컨텍스트 사용량 60-70% 절감
3. **성능 향상**: 병렬 실행, 조기 종료, 캐시 활용
4. **품질 보장**: 게이트 검증, 오류 복구, 일관성 유지

---

## 아키텍처

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR                                  │
│                    (최상위 지휘 에이전트)                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Phase 1    │  │   Phase 2    │  │   Phase 3    │              │
│  │  Dispatcher  │→ │  Dispatcher  │→ │  Dispatcher  │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                       │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐              │
│  │ archive-     │  │ signal-      │  │ db-updater   │              │
│  │ loader       │  │ classifier   │  │              │              │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤              │
│  │ multi-source │  │ ╔═══════════╗│  │ report-      │              │
│  │ -scanner     │  │ ║pSRT 2.0   ║│  │ generator    │              │
│  ├──────────────┤  │ ║ 4-Phase   ║│  ├──────────────┤              │
│  │ dedup-filter │  │ ╠═══════════╣│  │ archive-     │              │
│  │              │  │ ║groundness ║│  │ notifier     │              │
│  └──────────────┘  │ ║cross-val  ║│  └──────────────┘              │
│                    │ ║confidence ║│                                 │
│                    │ ║hallucinat ║│                                 │
│                    │ ║calibration║│                                 │
│                    │ ╚═══════════╝│                                 │
│                    ├──────────────┤                                 │
│                    │ impact-      │                                 │
│                    │ analyzer     │                                 │
│                    ├──────────────┤                                 │
│                    │ priority-    │                                 │
│                    │ ranker       │                                 │
│                    └──────────────┘                                 │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                     Shared Services                             │ │
│  │  • State Manager  • Gate Validator  • Token Counter            │ │
│  │  • Checkpoint     • Error Handler   • Progress Tracker         │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 토큰 최적화 전략

### 1. 최소 컨텍스트 원칙 (Minimal Context Principle)

각 서브 에이전트에게 **필요한 최소 정보만** 전달:

```
기존 방식 (비효율):
┌─────────────────────────────────────────────────────────────────┐
│ 전체 워크플로우 설명 + 이전 모든 단계 결과 + 현재 작업 지시     │
│ (토큰: ~5,000-10,000)                                           │
└─────────────────────────────────────────────────────────────────┘

최적화 방식:
┌─────────────────────────────────────────────────────────────────┐
│ 날짜 + 입력파일 경로 + 출력파일 경로 + 핵심 지시사항             │
│ (토큰: ~500-1,000)                                              │
└─────────────────────────────────────────────────────────────────┘
```

### 2. 파일 기반 통신 (File-Based Communication)

에이전트 간 데이터는 **파일**로 전달, 메시지는 **경로만** 포함:

```json
{
  "task": "signal-classifier",
  "date": "2026-01-13",
  "input": "data/2026/01/13/filtered/filtered-signals.json",
  "output": "data/2026/01/13/structured/structured-signals.json",
  "config": "config/steeps-taxonomy.yaml"
}
```

### 3. 결과 압축 (Result Compression)

서브 에이전트 결과는 **요약본**만 Orchestrator에 반환:

```json
{
  "status": "success",
  "metrics": {
    "input_count": 68,
    "output_count": 68,
    "duration_seconds": 45
  },
  "next_input": "data/2026/01/13/structured/structured-signals.json"
}
```

### 4. 선언적 워크플로우 (Declarative Workflow)

**JSON으로 워크플로우 정의** → 반복적 설명 제거:

```yaml
# config/workflow-definition.yaml
phases:
  - id: phase1
    name: Research
    steps:
      - agent: archive-loader
        parallel: false
      - agent: multi-source-scanner
        parallel: false
        marathon_enabled: true
      - agent: dedup-filter
        parallel: false
    gate: gate1

  - id: phase2
    name: Planning
    steps:
      - agent: signal-classifier
        parallel: false
      # pSRT 2.0 4-Phase Pipeline
      - agent: groundedness-verifier     # Phase 1: 근거성 검증
        parallel: false
        mandatory: true
      - agent: cross-validator           # Phase 2: 교차 검증
        parallel: false
        mandatory: true
      - agent: confidence-evaluator      # pSRT 2.0 통합 평가
        parallel: false
        mandatory: true
      - agent: hallucination-detector    # Phase 4: 할루시네이션 감지
        parallel: false
        mandatory: true
      - agent: calibration-engine        # Phase 3: 역사적 보정
        parallel: false
        mandatory: true
      # End of pSRT 2.0 Pipeline
      - agent: [impact-analyzer, priority-ranker]
        parallel: true  # 병렬 실행
    gate: gate2

  - id: phase3
    name: Implementation
    steps:
      - agent: [db-updater, report-generator]
        parallel: true  # 병렬 실행
      - agent: archive-notifier
        parallel: false
```

---

## 토큰 절감 비교

| 단계 | 기존 방식 | Orchestrator | 절감률 |
|------|-----------|--------------|--------|
| Phase 1 호출 | ~8,000 토큰 | ~2,500 토큰 | 69% |
| Phase 2 호출 | ~12,000 토큰 | ~3,500 토큰 | 71% |
| Phase 3 호출 | ~6,000 토큰 | ~2,000 토큰 | 67% |
| **총합** | **~26,000** | **~8,000** | **69%** |

---

## 병렬 실행 최적화

### 병렬 가능 작업 식별

```
Phase 2:
  ┌─────────────────┐     ┌─────────────────┐
  │ impact-analyzer │ ──▶ │                 │
  └─────────────────┘     │  priority-      │
                          │  ranker         │ (순차)
  ┌─────────────────┐     │                 │
  │ hallucination-  │ ──▶ │                 │
  │ detector        │     └─────────────────┘
  └─────────────────┘

  최적화 후:
  ┌─────────────────┐
  │ impact-analyzer │ ──┐
  └─────────────────┘   │
                        ├──▶ priority-ranker (둘 다 완료 후)
  ┌─────────────────┐   │
  │ hallucination-  │ ──┘
  │ detector        │
  └─────────────────┘

Phase 3:
  ┌─────────────────┐
  │ db-updater      │ ──┐
  └─────────────────┘   │
                        ├──▶ archive-notifier (둘 다 완료 후)
  ┌─────────────────┐   │
  │ report-generator│ ──┘
  └─────────────────┘
```

---

## 실행 프로토콜

### 1. 초기화 (Initialize)

```python
def initialize(date, options):
    # 1. 체크포인트 확인
    checkpoint = load_checkpoint(date)
    if checkpoint and options.resume:
        return resume_from_checkpoint(checkpoint)

    # 2. 상태 초기화
    state = {
        "date": date,
        "mode": "marathon" if options.marathon else "standard",
        "current_phase": 1,
        "current_step": 0,
        "token_usage": 0,
        "start_time": now()
    }

    # 3. 워크플로우 로드
    workflow = load_workflow_definition()

    return state, workflow
```

### 2. 단계 실행 (Execute Step)

```python
def execute_step(agent_name, state):
    # 1. 최소 컨텍스트 생성
    context = build_minimal_context(agent_name, state)

    # 2. 에이전트 호출 (토큰 추적)
    before_tokens = get_token_count()
    result = invoke_agent(agent_name, context)
    after_tokens = get_token_count()

    # 3. 결과 압축
    compressed = compress_result(result)

    # 4. 상태 업데이트
    state["token_usage"] += (after_tokens - before_tokens)
    state["current_step"] += 1

    # 5. 체크포인트 저장
    save_checkpoint(state)

    return compressed
```

### 3. 게이트 검증 (Gate Validation)

```python
def validate_gate(gate_id, state):
    validations = {
        "gate1": [
            ("filtered-signals.json exists", check_file_exists),
            ("signal count > 0", check_signal_count),
            ("dedup-index exists", check_dedup_index)
        ],
        "gate2": [
            ("hallucination-report exists", check_hallucination_report),
            ("pSRT-scores exists", check_psrt_scores),
            ("signal count match", check_signal_count_match)
        ],
        "gate3": [
            ("report generated", check_report_exists),
            ("database updated", check_db_updated)
        ]
    }

    results = []
    for name, check_fn in validations[gate_id]:
        passed = check_fn(state)
        results.append({"check": name, "passed": passed})

    all_passed = all(r["passed"] for r in results)
    return all_passed, results
```

---

## 상태 파일 구조

```json
// logs/orchestrator-state-{date}.json
{
  "session_id": "orch-2026-0113-001",
  "date": "2026-01-13",
  "mode": "marathon",
  "status": "running",

  "phases": {
    "phase1": {
      "status": "completed",
      "start_time": "2026-01-13T06:00:00Z",
      "end_time": "2026-01-13T09:15:00Z",
      "steps": [
        {"agent": "archive-loader", "status": "completed", "duration": 120},
        {"agent": "multi-source-scanner", "status": "completed", "duration": 10800},
        {"agent": "dedup-filter", "status": "completed", "duration": 180}
      ],
      "gate_passed": true
    },
    "phase2": {
      "status": "in_progress",
      "current_step": "impact-analyzer"
    },
    "phase3": {
      "status": "pending"
    }
  },

  "metrics": {
    "total_tokens": 45000,
    "signals_processed": 68,
    "errors_recovered": 0,
    "checkpoints_saved": 5
  },

  "files": {
    "raw": "data/2026/01/13/raw/scanned-signals.json",
    "filtered": "data/2026/01/13/filtered/filtered-signals.json",
    "structured": "data/2026/01/13/structured/structured-signals.json",
    "report": "data/2026/01/13/reports/environmental-scan-2026-01-13.md"
  }
}
```

---

## 호출 방법

### Orchestrator 직접 호출

```
오늘 날짜에 대해 환경스캐닝 전체 워크플로우를 실행해줘.
모드: marathon
옵션: skip-human
```

### 명령어를 통한 호출

```bash
/env-scan:run --marathon --skip-human
```

Orchestrator가 자동으로 활성화되어 전체 워크플로우 지휘.

---

## Orchestrator 실행 흐름

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR EXECUTION FLOW                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  [START] ──▶ Initialize                                             │
│              │                                                       │
│              ▼                                                       │
│         ┌────────────────┐                                          │
│         │ Load Workflow  │                                          │
│         │ Definition     │                                          │
│         └───────┬────────┘                                          │
│                 │                                                    │
│                 ▼                                                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                      PHASE 1 LOOP                             │   │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐        │   │
│  │  │ archive-    │──▶│ multi-src-  │──▶│ dedup-      │        │   │
│  │  │ loader      │   │ scanner     │   │ filter      │        │   │
│  │  │ (minimal)   │   │ (minimal)   │   │ (minimal)   │        │   │
│  │  └─────────────┘   └─────────────┘   └─────────────┘        │   │
│  │                                               │               │   │
│  │                                               ▼               │   │
│  │                                      [Gate 1 Check]          │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                 │                                                    │
│                 ▼ (Gate 1 Passed)                                   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                      PHASE 2 LOOP                             │   │
│  │  ┌─────────────┐   ┌──────────────────────────┐              │   │
│  │  │ signal-     │──▶│ hallucination + impact   │ (parallel)  │   │
│  │  │ classifier  │   │ + priority               │              │   │
│  │  └─────────────┘   └──────────────────────────┘              │   │
│  │                                               │               │   │
│  │                                               ▼               │   │
│  │                                      [Gate 2 Check]          │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                 │                                                    │
│                 ▼ (Gate 2 Passed)                                   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                      PHASE 3 LOOP                             │   │
│  │  ┌──────────────────────────┐   ┌─────────────┐              │   │
│  │  │ db-updater + report-gen  │──▶│ archive-    │              │   │
│  │  │ (parallel)               │   │ notifier    │              │   │
│  │  └──────────────────────────┘   └─────────────┘              │   │
│  │                                               │               │   │
│  │                                               ▼               │   │
│  │                                      [Gate 3 Check]          │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                 │                                                    │
│                 ▼                                                    │
│         ┌────────────────┐                                          │
│         │ Generate Final │                                          │
│         │ Summary        │                                          │
│         └───────┬────────┘                                          │
│                 │                                                    │
│                 ▼                                                    │
│              [END]                                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 에이전트 호출 템플릿

### Phase 1 에이전트 호출

```markdown
## archive-loader 호출
날짜: {date}
작업: 기존 신호 DB 로드
입력: signals/database.json
출력: context/archive-summary-{date}.json, context/dedup-index-{date}.json
지시: 기존 신호 수, 카테고리별 분포, 최근 7일 신호 목록 생성

## multi-source-scanner 호출 (Marathon)
날짜: {date}
모드: marathon (3시간)
Stage 1 출력: data/{date}/raw/stage1-signals.json
Stage 2 출력: data/{date}/raw/exploration-signals.json
병합 출력: data/{date}/raw/scanned-signals.json

## dedup-filter 호출
날짜: {date}
입력: data/{date}/raw/scanned-signals.json
참조: signals/database.json, context/dedup-index-{date}.json
출력: data/{date}/filtered/filtered-signals.json
```

### Phase 2 에이전트 호출

```markdown
## signal-classifier 호출
날짜: {date}
입력: data/{date}/filtered/filtered-signals.json
출력: data/{date}/structured/structured-signals.json
지시: STEEPS 분류, 요약 생성

## pSRT 2.0 4-Phase Pipeline [SEQUENTIAL - MANDATORY]

### Phase 1: groundedness-verifier 호출
날짜: {date}
입력: data/{date}/structured/structured-signals.json
출력: data/{date}/analysis/groundedness-{date}.json
지시: 원본 대비 모든 주장의 근거성 검증 (30% 가중치)

### Phase 2: cross-validator 호출
날짜: {date}
입력: data/{date}/structured/, data/{date}/analysis/groundedness-{date}.json
출력: data/{date}/analysis/cross-validation-{date}.json
지시: 독립 소스 3개 이상에서 주장 검증 (25% 가중치)

### confidence-evaluator 호출 (통합)
날짜: {date}
입력: groundedness, cross-validation, config/pSRT-config.yaml
출력: data/{date}/analysis/pSRT-scores-{date}.json
지시: 4-Phase 점수 통합, 최종 pSRT 산출

### Phase 4: hallucination-detector 호출 [MANDATORY]
날짜: {date}
입력: data/{date}/analysis/pSRT-scores-{date}.json
출력: data/{date}/analysis/hallucination-report-{date}.json
지시: 6가지 할루시네이션 유형 감지, 페널티 적용

### Phase 3: calibration-engine 호출
날짜: {date}
입력: pSRT-scores, signals/history/
출력: data/{date}/analysis/calibrated-scores-{date}.json
지시: 역사적 정확도로 신뢰도 보정 (20% 가중치)

## impact-analyzer + priority-ranker 호출 [PARALLEL]
날짜: {date}
입력: data/{date}/structured/, data/{date}/analysis/calibrated-scores-{date}.json
출력: data/{date}/analysis/impact-assessment.json, data/{date}/analysis/priority-ranked.json
```

### Phase 3 에이전트 호출

```markdown
## db-updater + report-generator 호출 [PARALLEL]
날짜: {date}
입력: data/{date}/structured/, data/{date}/analysis/
출력: signals/database.json (업데이트), data/{date}/reports/environmental-scan-{date}.md

## archive-notifier 호출
날짜: {date}
작업: 아카이빙, 상태 업데이트, 완료 로그
출력: logs/archive-notifier-report-{date}.md
```

---

## 오류 복구

### 자동 재시도

```python
MAX_RETRIES = 3

def execute_with_retry(agent_name, context):
    for attempt in range(MAX_RETRIES):
        try:
            result = invoke_agent(agent_name, context)
            if result["status"] == "success":
                return result
        except AgentError as e:
            log_error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                wait(backoff_time(attempt))

    # 모든 재시도 실패
    return handle_permanent_failure(agent_name)
```

### 스킵 가능 에이전트

```yaml
skippable_agents:
  - source-evolver      # 실패해도 워크플로우 계속
  - file-organizer      # 실패해도 워크플로우 계속
  - performance-updater # 실패해도 워크플로우 계속

mandatory_agents:
  # pSRT 2.0 4-Phase Pipeline (순서대로 실행 필수)
  - groundedness-verifier   # Phase 1: 근거성 검증
  - cross-validator         # Phase 2: 교차 검증
  - confidence-evaluator    # pSRT 2.0 통합 평가
  - hallucination-detector  # Phase 4: 할루시네이션 감지
  - calibration-engine      # Phase 3: 역사적 보정
  # 기존 필수 에이전트
  - signal-classifier       # 실패 시 워크플로우 중단
  - report-generator        # 실패 시 워크플로우 중단
```

---

## 성능 지표

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| 토큰 절감률 | ≥ 60% | (기존 - 현재) / 기존 |
| 워크플로우 시간 | ≤ 4시간 (Marathon) | end_time - start_time |
| 오류 복구율 | ≥ 90% | 복구성공 / 총오류 |
| 게이트 통과율 | 100% | passed_gates / total_gates |
| 병렬화 효율 | ≥ 30% 시간 절감 | 순차 시간 / 병렬 시간 |

---

## 도구 사용

Orchestrator는 다음 도구만 직접 사용:

```
allowed-tools: Read, Write, Glob, Bash, Task
```

- **Read/Write**: 상태 파일, 체크포인트 관리
- **Glob**: 파일 존재 확인
- **Bash**: 타임스탬프, 간단한 검증
- **Task**: 서브 에이전트 호출

모든 웹 스캔, 분석은 **서브 에이전트에 위임**.

---

## Context Low 대응

```python
def handle_context_low():
    # 1. 즉시 체크포인트 저장
    save_checkpoint(current_state)

    # 2. 진행 요약 생성 (300 토큰 이내)
    summary = generate_compact_summary(current_state)

    # 3. 재개 정보 저장
    save_resume_info({
        "checkpoint_file": f"logs/checkpoint-{date}.json",
        "last_completed": current_state["current_step"],
        "next_action": determine_next_action()
    })

    # 4. 사용자에게 알림
    notify("Context low. Checkpoint saved. Run /env-scan:resume to continue.")
```

---

## 관련 파일

- `config/workflow-definition.yaml`: 워크플로우 정의
- `logs/orchestrator-state-{date}.json`: 실행 상태
- `logs/checkpoint-{date}.json`: 체크포인트
- `logs/token-usage-{date}.json`: 토큰 사용량 추적
