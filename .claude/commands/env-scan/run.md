---
description: 일일 환경스캐닝 워크플로우 전체 실행 (v3.2 - 워크플로우 순서 수정)
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task, WebSearch, WebFetch
argument-hint: [--fast | --with-review | --phase <1|2|3> | --resume]
---

# 환경스캐닝 워크플로우 v3.2 - 완전 스캔

오늘 날짜: !`date +%Y-%m-%d`
옵션: $ARGUMENTS

---

## 핵심 변경 (v3.2)

**v3.1 결함**: Marathon Stage 2 신호가 signal-merger/dedup-filter를 거치지 않음
**v3.2 해결**: 워크플로우 순서 수정 - 모든 데이터 수집 후 병합

```
v3.1 (결함):
  스캐너 → merger → dedup → Marathon Stage 2 → Gate 1
  ❌ Marathon 신호가 병합/중복제거 안됨

v3.2 (수정):
  스캐너 → Marathon Stage 2 → merger (6개 통합) → dedup → Gate 1
  ✓ 모든 신호가 병합/중복제거됨
```

---

## 워크플로우 구조

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR v3.2                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 1: Research (데이터 수집 → 병합 → 중복제거)                   │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 1. archive-loader                                            │    │
│  │         ↓                                                    │    │
│  │ 2. 4개 스캐너 병렬 (강제!)                                    │    │
│  │    ┌────────────┬────────────┬────────────┬────────────┐     │    │
│  │    │ naver-news │ global-news│ google-news│ STEEPS     │     │    │
│  │    │  crawler   │  crawler   │  crawler   │ scanner    │     │    │
│  │    └─────┬──────┴─────┬──────┴─────┬──────┴─────┬──────┘     │    │
│  │          └────────────┴────────────┴────────────┘            │    │
│  │                           ↓                                  │    │
│  │ 3. Marathon Stage 2 (강제!) - 스캐너 완료 후 실행            │    │
│  │    ┌────────────────────────────────────────────────────┐    │    │
│  │    │ 3-1. gap-analyzer (선행)                            │    │    │
│  │    │         ↓                                           │    │    │
│  │    │ 3-2. frontier-explorer + citation-chaser (병렬)     │    │    │
│  │    │         ↓                                           │    │    │
│  │    │ 3-3. rapid-validator (후행)                         │    │    │
│  │    └────────────────────────────────────────────────────┘    │    │
│  │                           ↓                                  │    │
│  │ 4. signal-merger (6개 소스 통합!)                            │    │
│  │    입력: naver + global + google + steeps + frontier + citation │
│  │         ↓                                                    │    │
│  │ 5. dedup-filter (모든 신호 중복 제거)                        │    │
│  └─────────────────────────────────────────────────────────────┘    │
│         ↓                                                            │
│     [Gate 1 - 8개 파일 필수!]                                        │
│                                                                      │
│  Phase 2: Planning (기존과 동일)                                     │
│  Phase 3: Implementation (기존과 동일)                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 실행 단계 (Orchestrator 강제 수행)

### Phase 1: Research (정보 수집)

**Step 1: Archive Loader**
```
Task @archive-loader:
  날짜: {date}
  입력: signals/database.json
  출력: context/archive-summary-{date}.json, context/dedup-index-{date}.json
```

---

## ⚠️ Step 2: 4개 스캐너 병렬 호출 (강제!) ⚠️

**중요**: 아래 4개 Task를 **반드시 모두** 병렬 실행해야 합니다.

```
# ═══════════════════════════════════════════════════════════════
# Task 1: 네이버 뉴스 크롤러 (필수)
# ═══════════════════════════════════════════════════════════════
Task @naver-news-crawler:
  subagent_type: naver-news-crawler
  prompt: |
    날짜: {date}
    STEEPS 키워드로 네이버 뉴스 검색
    출력: data/{date}/raw/naver-scan-{date}.json
    최소 5개 이상 신호 수집

# ═══════════════════════════════════════════════════════════════
# Task 2: 글로벌 뉴스 크롤러 (필수)
# ═══════════════════════════════════════════════════════════════
Task @global-news-crawler:
  subagent_type: global-news-crawler
  prompt: |
    날짜: {date}
    6개국 주요 신문 크롤링 (한국, 미국, 영국, 중국, 일본, 중동)
    출력: data/{date}/raw/global-news-{date}.json
    최소 10개 이상 신호 수집

# ═══════════════════════════════════════════════════════════════
# Task 3: 구글 뉴스 크롤러 (필수)
# ═══════════════════════════════════════════════════════════════
Task @google-news-crawler:
  subagent_type: google-news-crawler
  prompt: |
    날짜: {date}
    STEEPS 키워드로 구글 뉴스 검색
    출력: data/{date}/raw/google-news-{date}.json
    최소 5개 이상 신호 수집

# ═══════════════════════════════════════════════════════════════
# Task 4: STEEPS WebSearch 스캐너 (필수)
# ═══════════════════════════════════════════════════════════════
Task @steeps-scanner:
  subagent_type: general-purpose
  prompt: |
    날짜: {date}
    WebSearch로 STEEPS 카테고리별 미래 변화 신호 수집
    출력: data/{date}/raw/steeps-scan-{date}.json
    총 15개 이상 신호 수집
```

**검증**: 4개 모두 완료될 때까지 대기.

---

## ⚠️ Step 3: Marathon Stage 2 (강제!) ⚠️

**중요**: 4개 스캐너 완료 후 **반드시** 실행해야 합니다.

```
# ═══════════════════════════════════════════════════════════════
# Step 3-1: Gap Analyzer (선행)
# ═══════════════════════════════════════════════════════════════
Task @gap-analyzer:
  subagent_type: gap-analyzer
  prompt: |
    날짜: {date}
    4개 스캐너 결과 분석하여 STEEPS/지역/언어 갭 식별
    입력: data/{date}/raw/ 폴더의 4개 스캔 파일
    출력: data/{date}/analysis/gap-analysis-{date}.json

# ═══════════════════════════════════════════════════════════════
# Step 3-2: Frontier Explorer + Citation Chaser (병렬)
# ═══════════════════════════════════════════════════════════════
Task @frontier-explorer (병렬):
  subagent_type: frontier-explorer
  prompt: |
    날짜: {date}
    Gap 분석 결과 기반 미개척 영역 탐험
    출력: data/{date}/raw/frontier-signals-{date}.json

Task @citation-chaser (병렬):
  subagent_type: citation-chaser
  prompt: |
    날짜: {date}
    기존 신호의 인용/참고문헌 역추적
    출력: data/{date}/raw/citation-signals-{date}.json

# ═══════════════════════════════════════════════════════════════
# Step 3-3: Rapid Validator (후행)
# ═══════════════════════════════════════════════════════════════
Task @rapid-validator:
  subagent_type: rapid-validator
  prompt: |
    날짜: {date}
    발견된 소스 검증, 70점+ 자동 승격
    출력: data/{date}/analysis/validated-sources-{date}.json
```

---

## Step 4: Signal Merger (6개 소스 통합!)

**핵심**: 이제 signal-merger는 **6개 소스**를 통합합니다.

```
Task @signal-merger:
  날짜: {date}
  입력 (6개 필수):
    # 4개 스캐너 출력
    - data/{date}/raw/naver-scan-{date}.json
    - data/{date}/raw/global-news-{date}.json
    - data/{date}/raw/google-news-{date}.json
    - data/{date}/raw/steeps-scan-{date}.json
    # Marathon Stage 2 출력
    - data/{date}/raw/frontier-signals-{date}.json
    - data/{date}/raw/citation-signals-{date}.json
  출력: data/{date}/raw/scanned-signals-{date}.json
```

---

## Step 5: Dedup Filter

```
Task @dedup-filter:
  날짜: {date}
  입력: data/{date}/raw/scanned-signals-{date}.json, context/dedup-index-{date}.json
  출력: data/{date}/filtered/filtered-signals-{date}.json
```

---

## ⚠️ Gate 1 검증 (강화!) ⚠️

**필수 파일 8개** - 하나라도 없으면 Phase 2 진입 불가:

| 검증 항목 | 파일 | 실패 시 |
|-----------|------|---------|
| **4개 스캐너 출력** | | |
| 네이버 크롤러 | `naver-scan-{date}.json` | 워크플로우 중단 |
| 글로벌 뉴스 | `global-news-{date}.json` | 워크플로우 중단 |
| 구글 뉴스 | `google-news-{date}.json` | 워크플로우 중단 |
| STEEPS 스캔 | `steeps-scan-{date}.json` | 워크플로우 중단 |
| **Marathon Stage 2 출력** | | |
| Gap 분석 | `gap-analysis-{date}.json` | 워크플로우 중단 |
| Frontier 탐험 | `frontier-signals-{date}.json` | 워크플로우 중단 |
| Citation 추적 | `citation-signals-{date}.json` | 워크플로우 중단 |
| 소스 검증 | `validated-sources-{date}.json` | 워크플로우 중단 |
| **병합 결과** | | |
| 병합 파일 | `scanned-signals-{date}.json` | 워크플로우 중단 |
| 필터링 파일 | `filtered-signals-{date}.json` | 워크플로우 중단 |

---

### Phase 2: Planning (기존과 동일)

**Step 6: Signal Classifier**
```
Task @signal-classifier:
  입력: data/{date}/filtered/filtered-signals-{date}.json
  출력: data/{date}/structured/structured-signals-{date}.json, data/{date}/analysis/pSRT-scores-{date}.json
```

**Step 7: Confidence Evaluator**
**Step 8: Hallucination Detector [필수]**
**Step 9: Pipeline Validator**
**Step 10-11: Impact + Priority [병렬]**

**Gate 2 검증**: hallucination-report + validation-report 존재 (필수)

---

### Phase 3: Implementation (기존과 동일)

**Step 12-13: DB + Report [병렬]**
**Step 14: Archive Notifier**
**Step 15-16: Source Evolver + File Organizer [병렬, 선택적]**

**Gate 3 검증**: report.md 생성 완료

---

## Step 17: Root Cleanup (자동)

Gate 3 통과 후 **루트 디렉토리 임시 파일 자동 삭제**:

```bash
# 삭제 대상 (루트 디렉토리만)
rm -f ./*-{date}.md      # 날짜별 완료 보고서
rm -f ./*-{date}.txt     # 날짜별 상태 파일
rm -f ./*-{date}.json    # 날짜별 임시 JSON
rm -f ./*-{date}.py      # 날짜별 임시 스크립트
rm -f ./FINAL_RUN.py ./EXECUTE_UPDATE.py  # DB 업데이트 스크립트
rm -f ./*_updater*.py ./*_update*.py      # 업데이터 스크립트
rm -f ./*_ranking*.py ./execute_*.py      # 랭킹/실행 스크립트
rm -f ./test_*.py ./verify_*.py           # 테스트 스크립트
rm -f ./*.sh                              # 임시 쉘 스크립트

# 보호 파일 (절대 삭제 금지)
# - CLAUDE.md
# - README.md
# - WARP.md
```

**삭제 조건**: Gate 3 통과 (report.md 생성 확인) 후에만 실행

---

## 금지 사항

1. **multi-source-scanner 위임 금지**: 스캐너를 직접 호출
2. **스캐너/Marathon 생략 금지**: 모두 실행 필수
3. **순서 변경 금지**: 스캐너 → Marathon → merger → dedup 순서 준수
4. **출력 없이 진행 금지**: Gate 1에서 8개 파일 확인

---

## 데이터 경로

```
data/{YYYY}/{MM}/{DD}/
├── raw/
│   ├── naver-scan-{date}.json        # 스캐너 1
│   ├── global-news-{date}.json       # 스캐너 2
│   ├── google-news-{date}.json       # 스캐너 3
│   ├── steeps-scan-{date}.json       # 스캐너 4
│   ├── frontier-signals-{date}.json  # Marathon: Frontier
│   ├── citation-signals-{date}.json  # Marathon: Citation
│   └── scanned-signals-{date}.json   # 6개 통합 결과
├── filtered/
│   └── filtered-signals-{date}.json  # 중복 제거 결과
├── analysis/
│   ├── gap-analysis-{date}.json      # Marathon: Gap 분석
│   └── validated-sources-{date}.json # Marathon: 검증 결과
└── reports/
```

---

## 실행 예시

```bash
# 기본 실행 (6개 소스 통합 스캔)
/env-scan:run

# Human Review 포함
/env-scan:run --with-review

# Fast Mode (STEEPS 스캔만)
/env-scan:run --fast

# 체크포인트에서 재개
/env-scan:run --resume
```
