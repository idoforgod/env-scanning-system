---
name: env-scanner
description: 미래 연구(Futures Research)를 위한 환경스캐닝 워크플로우. 변화의 조기 징후(약한 신호, weak signals)를 체계적으로 탐지하고 분석하여 일일 보고서 생성. /run-scan으로 시작하거나 "환경스캐닝", "신호 탐지", "daily scan", "weak signal" 등 요청 시 사용.
---

# Environmental Scanning Workflow

미래 변화의 조기 징후를 탐지하고 분석하는 AI 자동화 워크플로우.

## 핵심 원칙 (Critical - 반드시 준수)

1. **과거 보고서 우선 확인**: 새 스캐닝 전 `env-scanning/reports/archive/` 및 `env-scanning/signals/database.json` 반드시 검토
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
- Phase 2: `@signal-classifier` → `@impact-analyzer` → `@priority-ranker`
- Phase 3: `@db-updater` → `@report-generator` → `@archive-notifier`

## Phase 1: Research (정보 수집)

| 단계 | 에이전트 | 입력 | 출력 |
|------|----------|------|------|
| 1 | `@archive-loader` | signals/database.json, reports/archive/ | context/previous-signals.json |
| 2 | `@multi-source-scanner` | config/domains.yaml, config/sources.yaml | raw/daily-scan-{date}.json |
| 3 | `@dedup-filter` | raw/, context/ | filtered/new-signals-{date}.json |
| 4 | **(human)** `/review-filter` | 필터링 결과 검토 | - |

## Phase 2: Planning (분석 및 구조화)

| 단계 | 에이전트 | 입력 | 출력 |
|------|----------|------|------|
| 5 | `@signal-classifier` | filtered/ | structured/classified-signals-{date}.json |
| 6 | `@impact-analyzer` | structured/ | analysis/impact-assessment-{date}.json |
| 7 | `@priority-ranker` | analysis/impact- | analysis/priority-ranked-{date}.json |
| 8 | **(human)** `/review-analysis` | 분석 결과 검토 | - |

## Phase 3: Implementation (보고서 생성)

| 단계 | 에이전트 | 입력 | 출력 |
|------|----------|------|------|
| 9 | `@db-updater` | analysis/, signals/database.json | signals/database.json (updated) |
| 10 | `@report-generator` | analysis/, structured/ | reports/daily/environmental-scan-{date}.md |
| 11 | `@archive-notifier` | reports/daily/ | reports/archive/, logs/ |
| 12 | **(human)** `/approve` or `/revision` | 최종 승인 | - |

## 데이터 경로

```
env-scanning/
├── signals/database.json          # 마스터 신호 DB
├── reports/daily/                 # 일일 보고서
├── reports/archive/{year}/{month}/ # 아카이브
├── raw/daily-scan-{date}.json     # 원시 수집 데이터
├── filtered/new-signals-{date}.json # 필터링된 신규 신호
├── structured/classified-signals-{date}.json # 구조화된 신호
├── analysis/                      # 영향도, 우선순위 분석
├── context/previous-signals.json  # 중복 체크용 컨텍스트
└── logs/                          # 실행 로그
```

## 슬래시 커맨드

| 커맨드 | 설명 |
|--------|------|
| `/run-scan` | 전체 워크플로우 실행 |
| `/scan-status` | 현재 진행 상태 확인 |
| `/review-filter` | 필터링 결과 검토 |
| `/review-analysis` | 분석 결과 검토 |
| `/approve-report` | 보고서 승인 및 배포 |
| `/request-revision` | 보고서 수정 요청 |

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
