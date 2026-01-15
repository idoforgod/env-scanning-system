---
name: env-scanner
description: 미래 연구(Futures Research)를 위한 환경스캐닝 워크플로우. 변화의 조기 징후(약한 신호, weak signals)를 체계적으로 탐지하고 분석하여 일일 보고서 생성. /run-scan으로 시작하거나 "환경스캐닝", "신호 탐지", "daily scan", "weak signal" 등 요청 시 사용.
---

# Environmental Scanning Workflow

미래 변화의 조기 징후를 탐지하고 분석하는 AI 자동화 워크플로우.

## 핵심 원칙 (Critical - 반드시 준수)

1. **과거 보고서 우선 확인**: 새 스캐닝 전 `data/reports/archive/` 및 `data/signals/database.json` 반드시 검토
2. **중복 신호 제외**: 기존 DB 신호 자동 제외 (의미적 유사도 85% 이상 = 중복)
3. **신규 신호만 탐지**: 7일 내 최초 등장, DB 미등록 신호만 최종 보고서에 포함
4. **상태 변화 추적**: 기존 신호의 강화/약화는 별도 섹션에서 추적

## 워크플로우 실행

### 전체 실행
```
/run-scan
```

### 단계별 수동 실행
- Phase 1: `@archive-loader` → `@multi-source-scanner` → `@dedup-filter`
- Phase 2: `@signal-classifier` → `@confidence-evaluator` → **`@hallucination-detector`** (필수) → `@pipeline-validator` → `@impact-analyzer` → `@priority-ranker`
- Phase 3: `@db-updater` → `@report-generator` → `@archive-notifier`

## Phase 1: Research (정보 수집)

| 단계 | 에이전트 | 입력 | 출력 |
|------|----------|------|------|
| 1 | `@archive-loader` | signals/database.json, reports/archive/ | context/previous-signals.json |
| 2 | `@multi-source-scanner` | config/domains.yaml, config/sources.yaml | raw/daily-scan-{date}.json |
| 3 | `@dedup-filter` | raw/, context/ | filtered/new-signals-{date}.json |
| 4 | **(human)** `/review-filter` | 필터링 결과 검토 | - |

## Phase 2: Planning (분석 및 구조화)

### pSRT 2.0 4-Phase 신뢰도 평가 파이프라인

| 단계 | 에이전트 | 입력 | 출력 | 필수 | pSRT Phase |
|------|----------|------|------|------|------------|
| 5.0 | `@signal-classifier` | filtered/ | structured/structured-signals-{date}.json | ✅ | - |
| 5.3 | `@groundedness-verifier` | structured/, original_content | analysis/groundedness-{date}.json | ✅ | **Phase 1** |
| 5.5 | `@cross-validator` | structured/, groundedness | analysis/cross-validation-{date}.json | ✅ | **Phase 2** |
| 5.7 | `@confidence-evaluator` | groundedness, cross-validation, pSRT-config | analysis/pSRT-scores-{date}.json | ✅ | **통합** |
| 5.9 | **`@hallucination-detector`** | pSRT-scores | analysis/hallucination-report-{date}.json | ⚠️ **필수** | **Phase 4** |
| 6.0 | `@calibration-engine` | pSRT-scores, history/*.json | analysis/calibrated-scores-{date}.json | ✅ | **Phase 3** |
| 7 | `@pipeline-validator` | 모든 analysis 결과 | analysis/validation-report-{date}.json | ✅ | - |
| 8 | `@impact-analyzer` | structured/, calibrated-scores | analysis/impact-assessment-{date}.json | ✅ | - |
| 9 | `@priority-ranker` | impact-assessment, calibrated-scores | analysis/priority-ranked-{date}.json | ✅ | - |
| 10 | **(human)** `/review-analysis` | 분석 결과 검토 | - | 옵션 | - |

> ⚠️ **중요**: pSRT 2.0 4-Phase 파이프라인은 반드시 순서대로 실행되어야 합니다:
> 1. **Phase 1 (근거성)**: groundedness-verifier → 원본 대비 주장 검증
> 2. **Phase 2 (교차검증)**: cross-validator → 독립 소스에서 확인
> 3. **Phase 4 (할루시네이션)**: hallucination-detector → 6가지 유형 감지 (필수!)
> 4. **Phase 3 (보정)**: calibration-engine → 역사적 정확도로 보정

## Phase 3: Implementation (보고서 생성)

| 단계 | 에이전트 | 입력 | 출력 |
|------|----------|------|------|
| 12 | `@db-updater` | analysis/, signals/database.json | signals/database.json (updated) |
| 13 | `@report-generator` | analysis/, structured/ | reports/daily/environmental-scan-{date}.md |
| 14 | `@archive-notifier` | reports/daily/ | reports/archive/, logs/ |
| 15 | `@source-evolver` | evolution/pending-sources.json | config/sources.yaml (updated) |
| 16 | `@file-organizer` | 모든 산출물 | 날짜별 정리된 폴더 구조 |
| 17 | **(human)** `/approve` or `/revision` | 최종 승인 | - |

## 데이터 경로

```
data/
├── {YYYY}/{MM}/{DD}/              # 날짜별 데이터 (권장 구조)
│   ├── raw/                       # 원시 수집 데이터
│   ├── filtered/                  # 필터링된 신호
│   ├── structured/                # 구조화된 신호
│   ├── analysis/                  # 분석 결과
│   ├── reports/                   # 일일 보고서
│   └── execution/                 # 실행 요약 (NEW)
├── signals/database.json          # 마스터 신호 DB
├── context/                       # 중복 체크용 컨텍스트
└── logs/                          # 실행 로그
```

### 실행 요약 파일 경로 규칙 (IMPORTANT)

| 파일 유형 | 올바른 경로 | 잘못된 경로 |
|----------|------------|------------|
| Archive 로딩 요약 | `data/{date}/execution/archive-loader-summary.md` | ~~`/ARCHIVE-LOADER-*.md`~~ |
| Dedup 필터 요약 | `data/{date}/execution/dedup-summary.md` | ~~`/DEDUP-*.md`~~ |
| Stage 실행 요약 | `data/{date}/execution/stage-summary.md` | ~~`/STAGE*-*.md`~~ |
| 퀵레퍼런스 | `data/{date}/execution/*-reference.md` | ~~`/*-REFERENCE*.md`~~ |

**모든 실행 요약 파일은 `data/{date}/execution/` 폴더에 저장. 루트 디렉토리 생성 금지.**

## 슬래시 커맨드

| 커맨드 | 설명 |
|--------|------|
| `/run-scan` | 전체 워크플로우 실행 |
| `/run-scan --marathon` | **3시간 연속 실행 (자동 compact 포함)** |
| `/run-scan --resume` | 마지막 체크포인트에서 재개 |
| `/scan-status` | 현재 진행 상태 확인 |
| `/review-filter` | 필터링 결과 검토 |
| `/review-analysis` | 분석 결과 검토 |
| `/approve-report` | 보고서 승인 및 배포 |
| `/request-revision` | 보고서 수정 요청 |

## Marathon Mode (다중 소스 스캐닝 3시간 확장)

### 정의
**Marathon Mode = 다중 소스 스캐닝 단계만 3시간으로 확장하는 모드**

- 영향 받는 단계: `@multi-source-scanner`만 해당
- 영향 받지 않는 단계: 나머지 모든 단계 (dedup, classifier, analyzer 등)는 기존과 동일

### 2단계 구조

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Marathon Mode: 3시간 = 180분                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐                                                │
│  │   Stage 1       │  기존 소스 스캔                                │
│  │   (가변 시간)   │  • DB에 등록된 소스 스캔                       │
│  │                 │  • 소요 시간 측정                              │
│  └────────┬────────┘                                                │
│           │                                                         │
│           ▼                                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                        Stage 2                               │   │
│  │                   (잔여 시간 전체)                           │   │
│  │                                                              │   │
│  │   완전히 새로운 소스 탐험                                    │   │
│  │   • 이전에 한 번도 스캔하지 않은 소스 발굴                   │   │
│  │   • 잔여 시간 = 180분 - Stage1 소요 시간                     │   │
│  │   • 이 시간을 전부 신규 소스 탐색에 강제 투여                │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  예시:                                                              │
│  Stage 1: 10분 → Stage 2: 170분 (2시간 50분)                       │
│  Stage 1: 30분 → Stage 2: 150분 (2시간 30분)                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stage 1: 기존 소스 스캔

**기존 방식 그대로 실행**
- DB 로딩 → 등록된 소스 스캔 → 신호 수집
- 소요 시간 측정 (stage1_duration)

### Stage 2: 신규 소스 탐험

**완전히 새로운 소스 발굴** - 이전 환경스캐닝에서 **한 번도 스캔하지 않은** 소스 탐색

4가지 탐험 전략 (각 25% 시간 배분):
| 전략 | 설명 |
|------|------|
| 인용 추적 | Stage 1 신호의 원문에서 인용된 소스 추출 |
| 도메인 탐험 | 기존 소스와 유사한 도메인 탐색 (예: stanford.edu → mit.edu) |
| 키워드 확장 | STEEPS 부족 카테고리 키워드로 새 소스 발굴 |
| 지역 확장 | 미개척 지역 (라틴아메리카, 아프리카 등) 소스 탐색 |

### 실행 방법
```
/env-scan:run --marathon --skip-human
```

### 관련 파일
- `evolution/pending-sources.json`: 발견된 소스 후보
- `logs/marathon-time-{date}.json`: 시간 추적 로그
- `config/source-performance.json`: 소스별 성과 통계

### 핵심 원칙
**"Stage 1 완료 후 남는 시간 전체를 Stage 2에 강제 배정"**

## Source Evolution System (자동 소스 진화)

### 개요
pSRT 성과 데이터를 기반으로 소스 Tier를 자동 조정하는 자기개선 시스템.

### 자동화 수준: Level 2 (조건부 자동)
- 명확한 조건 충족 시 자동 적용
- 경계 사례는 pending으로 이동
- 모든 변경 이력 로깅

### 진화 규칙

#### 승격 (Promotion)
```
조건: pSRT ≥ 70 AND scans ≥ 3 AND trend = "improving"
조치: Tier -1 (예: Tier 2 → Tier 1)
```

#### 강등 (Demotion)
```
조건: pSRT ≤ 40 AND scans ≥ 3 AND trend = "declining"
조치: Tier +1 (예: Tier 2 → Tier 3)
```

#### 비활성화 (Deactivation)
```
조건: pSRT ≤ 30 AND scans ≥ 5 AND signals = 0
조치: status = "inactive"
```

### 안전장치 (필수)

| 안전장치 | 설명 |
|----------|------|
| 변경 상한선 | 1회당 최대 Tier 변경 5개, 비활성화 3개 |
| 화이트리스트 | 보호 소스는 강등/비활성화 불가 |
| 블랙리스트 | 차단 도메인 자동 등록 방지 |
| 스냅샷 & 롤백 | 변경 전 자동 저장, `/evolution:rollback` 복원 |
| 이상 탐지 | pSRT 급락 30% 시 경고 |

### 진화 커맨드

| 커맨드 | 설명 |
|--------|------|
| `/evolution:apply` | 수동으로 진화 규칙 적용 |
| `/evolution:status` | 현재 진화 상태 확인 |
| `/evolution:rollback [date]` | 지정 날짜 스냅샷으로 복원 |

### 관련 파일
```
data/
├── config/
│   ├── evolution-config.json      # 진화 규칙 정의
│   ├── evolution-whitelist.json   # 보호 소스 목록
│   └── evolution-blacklist.json   # 차단 도메인 목록
└── evolution/
    ├── evolution-log.json         # 변경 이력
    ├── pending-sources.json       # 대기 중인 신규 소스
    └── snapshots/{year}/{month}/  # config 스냅샷
```

## 파일 자동 정리 시스템

### 개요
스캔 완료 후 생성된 파일들을 날짜별/주간별/월간별 폴더로 자동 정리.

### 자동 실행 트리거
- **Marathon Mode 완료 후**: 자동 실행 ✅
- **일일 스캔 완료 후**: 자동 실행 ✅
- **수동 명령**: `/env-scan:organize`

### 폴더 구조
```
data/
├── reports/
│   └── {year}/{month}/
│       ├── daily/{day}/     # 일일 보고서
│       ├── weekly/week-{n}/ # 주간 요약
│       └── monthly/         # 월간 요약
├── raw/{year}/{month}/{day}/
├── analysis/{year}/{month}/{day}/
├── filtered/{year}/{month}/{day}/
└── structured/{year}/{month}/{day}/
```

### Marathon 완료 시 실행 순서
```
Marathon 완료
    ↓
@source-evolver (소스 Tier 자동 조정)
    ↓
@file-organizer (파일 날짜별 정리)
    ↓
완료 로그 저장
```

### 관련 커맨드
| 커맨드 | 설명 |
|--------|------|
| `/env-scan:organize` | 수동 파일 정리 |
| `/env-scan:organize --dry-run` | 미리보기 |
| `/env-scan:organize --weekly` | 주간 폴더 생성 포함 |

## pSRT 신뢰도 평가 시스템

AlphaFold의 pLDDT에서 영감을 받은 **자체 신뢰 평가 척도(pSRT: predicted Signal Reliability Test)**.

### 목적
- AI가 생성한 정보의 할루시네이션 위험 감소
- 신호 신뢰도의 객관적 평가
- 보고서 품질 보증

### 4차원 평가 모델
| 차원 | 가중치 | 평가 항목 |
|------|--------|-----------|
| Source pSRT | 20% | 소스 권위성, 검증 가능성, 역사적 정확도 |
| Signal pSRT | 35% | 구체성, 신선도, 독립성, 측정 가능성 |
| Analysis pSRT | 25% | 분류 명확성, 영향도 근거, 우선순위 일관성 |
| Report pSRT | 20% | 소스 다양성, 내부 일관성, STEEPS 균형 |

### 등급 체계
| 등급 | 점수 범위 | 권장 조치 |
|------|----------|-----------|
| A+ | 90-100 | 즉시 활용 가능 |
| A | 80-89 | 활용 권장 |
| B | 70-79 | 모니터링 권장 |
| C | 60-69 | 추가 검증 후 활용 |
| D | 50-59 | 교차 검증 필수 |
| E | 40-49 | 참고용으로만 사용 |
| F | 0-39 | 제외 권고 |

### 할루시네이션 탐지 유형
| 유형 | 심각도 | 조치 |
|------|--------|------|
| SOURCE_HALLUCINATION | critical | 제거 |
| SIGNAL_FABRICATION_RISK | high | 검증 |
| OVERINTERPRETATION | medium | 다운그레이드 |
| TEMPORAL_CONFUSION | medium | 날짜 검증 |
| VAGUE_SIGNAL | medium | 검증 |
| LOW_SOURCE_QUALITY | medium | 검증 |

### 관련 파일
- `config/pSRT-config.yaml`: 계산 설정
- `config/pSRT-schema.json`: 데이터 스키마
- `analysis/pSRT-scores-{date}.json`: 일일 점수
- `analysis/hallucination-report-{date}.json`: 검증 보고서

## 신호 템플릿

See [references/signal-template.md](references/signal-template.md)

## STEEPS 분류 기준 (6개 카테고리)

- **S**ocial (사회)
- **T**echnological (기술)
- **E**conomic (경제)
- **E**nvironmental (환경)
- **P**olitical (정치)
- **S**piritual (정신/영성)

See [references/steep-framework.md](references/steep-framework.md)

## 보고서 포맷

See [references/report-format.md](references/report-format.md)
