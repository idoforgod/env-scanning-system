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

## 워크플로우 구조 (17단계 전체 유지)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 1: Research          Phase 2: Planning      Phase 3: Impl    │
│  ┌─────────────────┐       ┌─────────────────┐    ┌──────────────┐  │
│  │ 1.archive-loader│       │ 5.signal-classif│    │12.db-updater │  │
│  │       ↓         │       │       ↓         │    │13.report-gen │  │
│  │ 2.multi-source  │       │ 6.confidence-   │    │  [PARALLEL]  │  │
│  │   -scanner      │  →    │   evaluator     │ →  │      ↓       │  │
│  │       ↓         │       │       ↓         │    │14.archive-   │  │
│  │ 3.dedup-filter  │       │ 7.hallucination │    │   notifier   │  │
│  │       ↓         │       │       ↓         │    │      ↓       │  │
│  │ 4.[Human Review]│       │ 8.pipeline-     │    │15.source-    │  │
│  └─────────────────┘       │   validator     │    │   evolver    │  │
│         ↓                  │       ↓         │    │16.file-      │  │
│     [Gate 1]               │ 9.impact-analyz │    │   organizer  │  │
│                            │10.priority-rank │    │  [PARALLEL]  │  │
│                            │  [PARALLEL]     │    │      ↓       │  │
│                            │       ↓         │    │17.[Approval] │  │
│                            │11.[Human Review]│    └──────────────┘  │
│                            └─────────────────┘         ↓            │
│                                    ↓                [Gate 3]        │
│                                [Gate 2]                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 실행 단계 (Orchestrator가 자동 수행)

### Phase 1: Research (정보 수집)

**Step 1: Archive Loader**
```
Task @archive-loader:
  날짜: {date}
  입력: signals/database.json
  출력: context/archive-summary-{date}.json, context/dedup-index-{date}.json
```

**Step 2: Multi-Source Scanner**
```
Task @multi-source-scanner:
  날짜: {date}
  모드: {marathon | standard}
  입력: config/regular-sources.json
  출력: data/{date}/raw/scanned-signals.json
```

**Step 3: Dedup Filter**
```
Task @dedup-filter:
  날짜: {date}
  입력: data/{date}/raw/scanned-signals.json, context/dedup-index-{date}.json
  출력: data/{date}/filtered/filtered-signals.json
```

**Step 4: [Human Review]** (--skip-human 시 생략)
```
/env-scan:review-filter 로 결과 검토
```

**Gate 1 검증**: filtered-signals.json 존재 + 신호수 > 0

---

### Phase 2: Planning (분석 및 구조화)

**Step 5: Signal Classifier**
```
Task @signal-classifier:
  날짜: {date}
  입력: data/{date}/filtered/filtered-signals.json
  출력: data/{date}/structured/structured-signals.json, data/{date}/analysis/pSRT-scores.json
```

**Step 6: Confidence Evaluator**
```
Task @confidence-evaluator:
  날짜: {date}
  입력: data/{date}/analysis/pSRT-scores.json
  출력: data/{date}/analysis/confidence-evaluation.json
  작업: pSRT 심층 평가 및 할루시네이션 플래그 생성
```

**Step 7: Hallucination Detector [필수]**
```
Task @hallucination-detector:
  날짜: {date}
  입력: data/{date}/analysis/pSRT-scores.json, data/{date}/analysis/confidence-evaluation.json
  출력: data/{date}/analysis/hallucination-report.json
  ⚠️ 이 단계를 건너뛰면 워크플로우 실패로 처리
```

**Step 8: Pipeline Validator**
```
Task @pipeline-validator:
  날짜: {date}
  입력: data/{date}/structured/structured-signals.json, data/{date}/analysis/pSRT-scores.json
  출력: data/{date}/analysis/validation-report.json
  작업: pSRT 신호 수와 structured 신호 수 일치 확인
```

**Step 9-10: Impact + Priority [병렬]**
```
Task @impact-analyzer + @priority-ranker (PARALLEL):
  날짜: {date}
  입력: data/{date}/structured/structured-signals.json
  출력: data/{date}/analysis/impact-assessment.json, data/{date}/analysis/priority-ranked.json
```

**Step 11: [Human Review]** (--skip-human 시 생략)
```
/env-scan:review-analysis 로 결과 검토
```

**Gate 2 검증**: hallucination-report.json + validation-report.json 존재 (필수)

---

### Phase 3: Implementation (보고서 생성)

**Step 12-13: DB + Report [병렬]**
```
Task @db-updater + @report-generator (PARALLEL):
  날짜: {date}
  입력: data/{date}/structured/, data/{date}/analysis/
  출력: signals/database.json, data/{date}/reports/environmental-scan-{date}.md
```

**Step 14: Archive Notifier**
```
Task @archive-notifier:
  날짜: {date}
  입력: data/{date}/ (전체 폴더)
  출력: logs/archive-notifier-report-{date}.md
```

**Step 15-16: Source Evolver + File Organizer [병렬, 선택적]**
```
Task @source-evolver + @file-organizer (PARALLEL, optional):
  날짜: {date}
  입력: config/evolution/pending-sources.json, data/{date}/
  출력: config/evolution/evolution-log.json
  ※ Marathon 모드 후 실행, 실패해도 워크플로우 계속
```

**Step 17: [Human Approval]** (--skip-human 시 생략)
```
/env-scan:approve 또는 /env-scan:revision 으로 최종 승인
```

**Gate 3 검증**: report.md 생성 완료

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
│   ├── confidence-evaluation.json
│   ├── hallucination-report.json
│   ├── validation-report.json
│   ├── impact-assessment.json
│   └── priority-ranked.json
└── reports/environmental-scan-{date}.md
```

---

## 품질 게이트

| Gate | 검증 항목 | 실패 시 |
|------|----------|---------|
| Gate 1 | filtered-signals.json 존재, 신호수 > 0 | Phase 2 진입 불가 |
| Gate 2 | hallucination-report.json + validation-report.json 존재 | Phase 3 진입 불가 |
| Gate 3 | report.md 생성 완료 | 경고 표시 |

---

## 토큰 예산

| 구분 | 예상 토큰 |
|------|----------|
| Phase 1 에이전트 (4단계) | ~2,500 |
| Phase 2 에이전트 (7단계) | ~4,000 |
| Phase 3 에이전트 (6단계) | ~2,500 |
| Orchestrator 오버헤드 | ~500 |
| **총합** | **~9,500** |

기존 방식 대비 **63% 절감** (26,000 → 9,500)

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
