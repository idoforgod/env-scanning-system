---
description: 일일 환경스캐닝 워크플로우 전체 실행
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch
argument-hint: [--skip-human | --phase <1|2|3>]
---

# 환경스캐닝 일일 워크플로우 실행

오늘 날짜: !`date +%Y-%m-%d`

## 실행 옵션
- `--skip-human`: 모든 human 검토 단계 자동 통과
- `--phase 1`: Phase 1 (Research)만 실행
- `--phase 2`: Phase 2 (Planning)만 실행
- `--phase 3`: Phase 3 (Implementation)만 실행

$ARGUMENTS

## 워크플로우

### Phase 1: Research (정보 수집)
1. `@archive-loader` → 기존 신호 DB 및 아카이브 로딩
2. `@multi-source-scanner` → STEEP 다중 소스 스캐닝
3. `@dedup-filter` → 중복 신호 필터링
4. **[Human Review]** → `/review-filter`로 결과 검토

### Phase 2: Planning (분석 및 구조화)
5. `@signal-classifier` → 신호 분류 및 구조화
6. `@impact-analyzer` → Futures Wheel 영향도 분석
7. `@priority-ranker` → 우선순위 산정
8. **[Human Review]** → `/review-analysis`로 결과 검토

### Phase 3: Implementation (보고서 생성)
9. `@db-updater` → 마스터 신호 DB 업데이트
10. `@report-generator` → 일일 보고서 생성 (markdown)
11. `@archive-notifier` → 아카이빙 및 완료 처리
12. **[Human Approval]** → `/approve-report` 또는 `/request-revision`

## 핵심 원칙 (반드시 준수)

1. **과거 보고서 우선 확인**: 스캐닝 전 기존 DB 검토
2. **중복 신호 제외**: 유사도 85% 이상 = 중복
3. **신규 신호만 탐지**: 7일 내 최초 등장만 포함
4. **상태 변화 추적**: 기존 신호의 변화는 별도 섹션

## 데이터 경로

- 설정: `env-scanning/config/`
- 원시 데이터: `env-scanning/raw/`
- 필터링 결과: `env-scanning/filtered/`
- 구조화 데이터: `env-scanning/structured/`
- 분석 결과: `env-scanning/analysis/`
- 보고서: `env-scanning/reports/daily/`
- 신호 DB: `env-scanning/signals/database.json`

순차적으로 각 에이전트를 호출하고, human 단계에서는 사용자에게 검토를 요청하세요.
