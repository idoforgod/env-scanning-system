---
description: 일일 환경스캐닝 워크플로우 전체 실행 (Orchestrator 사용)
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task
argument-hint: [--marathon | --skip-human | --phase <1|2|3> | --resume]
---

# 환경스캐닝 워크플로우 - Orchestrator Mode

오늘 날짜: !`date +%Y-%m-%d`
옵션: $ARGUMENTS

---

## Orchestrator 실행 프로토콜

**토큰 최적화 원칙**:
1. 각 에이전트에 **최소 컨텍스트**만 전달 (config/agent-prompts.yaml 참조)
2. 병렬 가능 작업은 **동시 실행** (Task 도구로 여러 에이전트 동시 호출)
3. 모든 데이터는 **파일 기반 통신** (메시지에 경로만 포함)
4. 결과는 **요약본**만 수신 (상세는 파일에서 읽기)

---

## 워크플로우 구조

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 1: Research          Phase 2: Planning      Phase 3: Impl    │
│  ┌─────────────────┐       ┌─────────────────┐    ┌──────────────┐  │
│  │ archive-loader  │       │ signal-classif  │    │ db-updater   │  │
│  │       ↓         │       │       ↓         │    │      ↓       │  │
│  │ multi-source    │  →    │ hallucination   │ →  │ report-gen   │  │
│  │ -scanner        │       │ [PARALLEL]      │    │ [PARALLEL]   │  │
│  │       ↓         │       │ impact+priority │    │      ↓       │  │
│  │ dedup-filter    │       └─────────────────┘    │ archive-     │  │
│  └─────────────────┘                              │ notifier     │  │
│         ↓                          ↓              └──────────────┘  │
│     [Gate 1]                   [Gate 2]               [Gate 3]      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 실행 단계 (Orchestrator가 자동 수행)

### Phase 1: Research

**Step 1.1: Archive Loader**
```
Task @archive-loader:
  날짜: {date}
  입력: signals/database.json
  출력: context/archive-summary-{date}.json
```

**Step 1.2: Multi-Source Scanner**
```
Task @multi-source-scanner:
  날짜: {date}
  모드: {marathon | standard}
  출력: data/{date}/raw/scanned-signals.json
```

**Step 1.3: Dedup Filter**
```
Task @dedup-filter:
  날짜: {date}
  입력: data/{date}/raw/scanned-signals.json
  출력: data/{date}/filtered/filtered-signals.json
```

**Gate 1 검증**: filtered-signals.json 존재 + 신호수 > 0

---

### Phase 2: Planning

**Step 2.1: Signal Classifier**
```
Task @signal-classifier:
  날짜: {date}
  입력: data/{date}/filtered/filtered-signals.json
  출력: data/{date}/structured/structured-signals.json, data/{date}/analysis/pSRT-scores.json
```

**Step 2.2: Hallucination Detector [필수]**
```
Task @hallucination-detector (general-purpose):
  날짜: {date}
  입력: data/{date}/analysis/pSRT-scores.json
  출력: data/{date}/analysis/hallucination-report.json
```

**Step 2.3: Impact + Priority [병렬]**
```
Task @impact-analyzer + @priority-ranker (PARALLEL):
  날짜: {date}
  입력: data/{date}/structured/structured-signals.json
  출력: data/{date}/analysis/impact-assessment.json, data/{date}/analysis/priority-ranked.json
```

**Gate 2 검증**: hallucination-report.json 존재 (필수)

---

### Phase 3: Implementation

**Step 3.1: DB + Report [병렬]**
```
Task @db-updater + @report-generator (PARALLEL):
  날짜: {date}
  입력: data/{date}/structured/, data/{date}/analysis/
  출력: signals/database.json, data/{date}/reports/environmental-scan-{date}.md
```

**Step 3.2: Archive Notifier**
```
Task @archive-notifier:
  날짜: {date}
  출력: logs/archive-notifier-report-{date}.md
```

**Gate 3 검증**: report 생성 완료

---

## Marathon Mode

**Marathon = multi-source-scanner만 3시간 확장**

```
Stage 1 (가변): 등록된 소스 스캔
       ↓
Stage 2 (잔여 시간 전체): 신규 소스 탐험
  - 인용 추적 (25%)
  - 도메인 탐험 (25%)
  - 키워드 확장 (25%)
  - 지역 확장 (25%)
```

---

## 데이터 경로

```
data/{YYYY}/{MM}/{DD}/
├── raw/scanned-signals.json
├── filtered/filtered-signals.json
├── structured/structured-signals.json
├── analysis/
│   ├── pSRT-scores.json
│   ├── hallucination-report.json
│   ├── impact-assessment.json
│   └── priority-ranked.json
└── reports/environmental-scan-{date}.md
```

---

## 품질 게이트

| Gate | 검증 항목 | 실패 시 |
|------|----------|---------|
| Gate 1 | filtered-signals.json 존재, 신호수 > 0 | Phase 2 진입 불가 |
| Gate 2 | hallucination-report.json 존재 (필수) | Phase 3 진입 불가 |
| Gate 3 | report.md 생성 완료 | 경고 표시 |

---

## 토큰 예산

| 구분 | 예상 토큰 |
|------|----------|
| Phase 1 에이전트 | ~2,500 |
| Phase 2 에이전트 | ~3,500 |
| Phase 3 에이전트 | ~2,000 |
| Orchestrator 오버헤드 | ~500 |
| **총합** | **~8,500** |

기존 방식 대비 **69% 절감** (26,000 → 8,500)

---

## 체크포인트

각 단계 완료 시 자동 저장:
- `logs/checkpoint-{date}.json`
- `logs/orchestrator-state-{date}.json`

Context low 발생 시:
1. 즉시 체크포인트 저장
2. `/env-scan:resume`로 재개

---

## 실행 예시

```bash
# Marathon 모드 (3시간 확장)
/env-scan:run --marathon --skip-human

# 일반 모드
/env-scan:run

# 특정 Phase만
/env-scan:run --phase 1
/env-scan:run --phase 2
/env-scan:run --phase 3

# 체크포인트에서 재개
/env-scan:run --resume
```
