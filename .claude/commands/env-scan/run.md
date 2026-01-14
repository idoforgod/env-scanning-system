---
description: 일일 환경스캐닝 워크플로우 전체 실행 (v4 - Source of Truth)
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task, WebSearch, WebFetch
argument-hint: [--fast | --with-review | --phase <1|2|3> | --resume]
---

# 환경스캐닝 워크플로우 v4 - Source of Truth

오늘 날짜: !`date +%Y-%m-%d`
옵션: $ARGUMENTS

---

## ⚠️ v4 핵심 원칙 (필수)

```
┌─────────────────────────────────────────────────────────────┐
│  v4 Source of Truth 원칙                                    │
│                                                              │
│  1. URL만 수집 → 실제 기사 본문 추출 → 본문 기반 요약       │
│  2. LLM 요약은 signal-classifier에서 1회만                  │
│  3. 이후 단계에서 summary/original_content 수정 금지         │
│  4. 보고서는 Python 템플릿으로 생성 (LLM 재작성 금지)       │
└─────────────────────────────────────────────────────────────┘
```

---

## 워크플로우 구조 (v4)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR v4                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 1: Research (URL 수집 → 본문 추출 → 중복제거)                │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 1. archive-loader                                            │    │
│  │         ↓                                                    │    │
│  │ 2. Stage A: URL Discovery (4개 크롤러 병렬)                  │    │
│  │    ┌────────────┬────────────┬────────────┬────────────┐     │    │
│  │    │ naver-news │ global-news│ google-news│ WebSearch  │     │    │
│  │    │  (URL만)   │  (URL만)   │  (URL만)   │ (URL만)    │     │    │
│  │    └─────┬──────┴─────┬──────┴─────┬──────┴─────┬──────┘     │    │
│  │          └────────────┴────────────┴────────────┘            │    │
│  │                           ↓                                  │    │
│  │ 3. URL Merger (URL 통합 + 중복 제거)                         │    │
│  │    출력: urls-{date}.json                                    │    │
│  │                           ↓                                  │    │
│  │ 4. Stage B: Content Fetching (WebFetch로 본문 수집)          │    │
│  │    출력: articles-{date}.json (Source of Truth!)             │    │
│  │                           ↓                                  │    │
│  │ 5. dedup-filter (URL 기반 중복 제거)                         │    │
│  └─────────────────────────────────────────────────────────────┘    │
│         ↓                                                            │
│     [Gate 1 - articles-{date}.json 필수!]                            │
│                                                                      │
│  Phase 2: Planning (Source of Truth 적용)                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 6. signal-classifier (유일한 LLM 요약 단계!)                 │    │
│  │    입력: articles-{date}.json (실제 기사 본문)               │    │
│  │    출력: structured-signals-{date}.json                      │    │
│  │         ↓                                                    │    │
│  │ 7-8. confidence + hallucination (summary ↔ content 검증)     │    │
│  │         ↓                                                    │    │
│  │ 9-10. impact + priority (메타데이터만, 내용 변경 금지!)       │    │
│  └─────────────────────────────────────────────────────────────┘    │
│         ↓                                                            │
│     [Gate 2 - hallucination-report 필수!]                            │
│                                                                      │
│  Phase 3: Implementation (Python 템플릿)                             │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 11-12. db-updater + report-generator (병렬)                  │    │
│  │    report-generator: Python 스크립트 호출 (LLM 재작성 금지!)  │    │
│  │         ↓                                                    │    │
│  │ 13. archive-notifier                                         │    │
│  └─────────────────────────────────────────────────────────────┘    │
│         ↓                                                            │
│     [Gate 3 - report.md 생성 확인]                                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 실행 단계 (Orchestrator 강제 수행)

### Step 0: Pre-Scan Checks (자동) ⚠️ 구조적 문제 방지

스캔 시작 전 사전 검증 수행:

```bash
# 0-1. 의존성 검증 (구조적 문제 3 방지: 외부 의존성 취약)
python3 src/scripts/validators/dependency_checker.py --crawler
# 실패 시: python3 src/scripts/validators/dependency_checker.py --fix

# 0-2. 리뷰 일정 확인
python3 src/scripts/analytics/review_scheduler.py check
```

**의존성 검증 실패 시**: `--fix` 옵션으로 자동 설치 후 재시도

---

### Phase 1: Research (정보 수집)

**Step 1: Archive Loader**
```
Task @archive-loader:
  날짜: {date}
  입력: signals/database.json
  출력: context/archive-summary-{date}.json, context/dedup-index-{date}.json
```

---

## ⚠️ Step 2: Stage A - URL Discovery (4개 크롤러 병렬) ⚠️

**v4 핵심**: URL만 수집합니다. 본문은 Stage B에서 WebFetch로 수집합니다.

```
# ═══════════════════════════════════════════════════════════════
# Task 1: 네이버 뉴스 크롤러 (URL만 수집!)
# ═══════════════════════════════════════════════════════════════
Task @naver-news-crawler:
  subagent_type: naver-news-crawler
  prompt: |
    날짜: {date}
    ⚠️ URL만 추출, 본문 수집은 Stage B에서 수행
    STEEPS 키워드로 네이버 뉴스 URL 수집
    출력: data/{date}/raw/naver-urls-{date}.json
    최소 15개 이상 URL 수집

# ═══════════════════════════════════════════════════════════════
# Task 2: 글로벌 뉴스 크롤러 (URL만 수집!)
# ═══════════════════════════════════════════════════════════════
Task @global-news-crawler:
  subagent_type: global-news-crawler
  prompt: |
    날짜: {date}
    ⚠️ URL만 추출, 본문 수집은 Stage B에서 수행
    6개국 주요 신문 URL 수집 (한국, 미국, 영국, 중국, 일본, 중동)
    출력: data/{date}/raw/global-urls-{date}.json
    최소 20개 이상 URL 수집

# ═══════════════════════════════════════════════════════════════
# Task 3: 구글 뉴스 크롤러 (URL만 수집!)
# ═══════════════════════════════════════════════════════════════
Task @google-news-crawler:
  subagent_type: google-news-crawler
  prompt: |
    날짜: {date}
    ⚠️ URL만 추출, 본문 수집은 Stage B에서 수행
    STEEPS 키워드로 구글 뉴스 URL 수집
    출력: data/{date}/raw/google-urls-{date}.json
    최소 15개 이상 URL 수집

# ═══════════════════════════════════════════════════════════════
# Task 4: STEEPS WebSearch (URL만 수집!)
# ═══════════════════════════════════════════════════════════════
Task @steeps-websearch:
  subagent_type: general-purpose
  prompt: |
    날짜: {date}
    ⚠️ URL만 추출, 스니펫은 힌트용 (신호 생성에 미사용!)
    WebSearch로 STEEPS 카테고리별 URL 수집
    출력: data/{date}/raw/websearch-urls-{date}.json
    총 20개 이상 URL 수집
```

**검증**: 4개 모두 완료될 때까지 대기.

---

## Step 3: URL Merger + Validation ⚠️ 구조적 문제 방지

```bash
# 3-1. URL 병합
python3 src/scripts/pipeline_v4/url_merger.py --date {date}
# 출력: data/{date}/raw/urls-{date}.json

# 3-2. URL 접근성 사전 검증 (구조적 문제 1 방지: URL≠접근성)
python3 src/scripts/validators/url_validator.py \
  --input data/{date}/raw/urls-{date}.json \
  --output data/{date}/raw/validated-urls-{date}.json \
  --quick
```

**접근성 검증 효과**:
- 페이월/차단 도메인 사전 필터링
- 404/403 에러 URL 제거
- 실제 접근 가능한 URL만 Stage B로 전달

---

## ⚠️ Step 4: Stage B - Batch Content Fetching ⚠️ 구조적 문제 방지

**핵심**: 배치 분할 처리로 컨텍스트 과부하 방지 (구조적 문제 2 방지)

```bash
# 배치 단위 본문 수집 (최대 10개씩 분할)
python3 src/scripts/pipeline_v4/batch_content_fetcher.py \
  --date {date} \
  --batch-size 8

# 입력: data/{date}/raw/validated-urls-{date}.json
# 출력: data/{date}/raw/articles-{date}.json
```

**배치 처리 규칙**:
- 배치 크기: 최대 10개 (기본 8개)
- 배치 간 대기: 2초
- 에이전트 컨텍스트 과부하 방지

**⚠️ articles-{date}.json이 신호 생성의 Source of Truth입니다.**

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

### Phase 2: Planning (v4 Source of Truth 적용)

**Step 6: Signal Classifier (유일한 LLM 요약 단계!)**
```
Task @signal-classifier:
  입력: data/{date}/raw/articles-{date}.json (실제 기사 본문!)
  출력: data/{date}/structured/structured-signals-{date}.json

  ⚠️ Source of Truth 규칙:
  1. original_content를 읽고 요약 (창작 금지!)
  2. url, original_title, original_content 그대로 보존
  3. 기사에 없는 내용 추가 금지
  4. 이 단계의 summary가 보고서까지 그대로 사용됨
```

**Step 7: Confidence Evaluator**
**Step 8: Hallucination Detector [필수 - v4 강화]**
```
⚠️ v4 추가 검증:
- summary가 original_content에 근거하는지 확인
- 기사에 없는 수치/인용이 추가되었는지 검증
- SUMMARY_CONTENT_MISMATCH 플래그 시 critical 처리
```

**Step 9: Pipeline Validator**
**Step 10-11: Impact + Priority [병렬]**
```
⚠️ v4 규칙: 메타데이터만 추가, 내용 변경 금지!
```

**Gate 2 검증**: hallucination-report + validation-report 존재 (필수)

---

### Step 11-A: Keyword Analytics (자동)

**Phase 2 완료 후 키워드 효과성 분석**

```bash
# URL 수집 + 신호 전환 분석 자동 실행
python3 src/scripts/analytics/post_scan_analytics.py --date {date} --phase full
```

**분석 항목**:
- 키워드별 URL 수집 건수
- 키워드별 신호 전환율
- 카테고리별 평균 우선순위 점수
- 효과성 메트릭 DB 업데이트

**출력**: `data/{date}/analysis/keyword-analytics-{date}.json`

---

### Phase 3: Implementation (v4 Python 템플릿)

**Step 12-13: DB + Report [병렬]**
```
Task @report-generator:
  ⚠️ v4 규칙: Python 스크립트로 보고서 생성 (LLM 재작성 금지!)

  Bash: python src/scripts/pipeline_v4/report_builder.py {date}

  - summary 그대로 사용
  - URL 그대로 사용
  - LLM이 내용을 재작성하거나 편집하지 않음
```

**Step 14: Archive Notifier**
**Step 15-16: Source Evolver + File Organizer [병렬, 선택적]**

**Gate 3 검증**: report.md 생성 완료

---

## Step 17: Cleanup (자동)

Gate 3 통과 후 **임시 파일 자동 삭제** (2단계):

### Step 17-A: 루트 디렉토리 정리

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
# - CLAUDE.md, README.md, WARP.md, LICENSE
```

### Step 17-B: data 폴더 정리

```bash
# ═══════════════════════════════════════════════════════════════
# 유지 필수 파일 (다음 스캔에서 참조 또는 아카이브용)
# ═══════════════════════════════════════════════════════════════
# 1. structured/structured-signals-{date}.json  ← DB 대조 및 아카이브
# 2. reports/environmental-scan-{date}.md       ← 최종 보고서
# 3. analysis/priority-ranked-{date}.json       ← 우선순위 기록

# ═══════════════════════════════════════════════════════════════
# 삭제 대상 (중간 산출물, 병합 후 불필요)
# ═══════════════════════════════════════════════════════════════

DATA_DIR="data/{YYYY}/{MM}/{DD}"

# 1. raw/ 폴더 전체 삭제 (병합 완료 후 불필요)
rm -rf ${DATA_DIR}/raw/

# 2. filtered/ 폴더 전체 삭제 (구조화 완료 후 불필요)
rm -rf ${DATA_DIR}/filtered/

# 3. execution/ 폴더 전체 삭제 (실행 로그)
rm -rf ${DATA_DIR}/execution/

# 4. logs/ 폴더 전체 삭제 (dedup 로그)
rm -rf ${DATA_DIR}/logs/

# 5. analysis/ 폴더 정리 (priority-ranked, keyword-analytics 유지)
find ${DATA_DIR}/analysis/ -type f ! -name "priority-ranked-*.json" ! -name "keyword-analytics-*.json" -delete

# 6. data/{date}/ 루트 임시 파일 삭제
rm -f ${DATA_DIR}/*.md ${DATA_DIR}/*.txt ${DATA_DIR}/*.py

# 7. reports/ 내 중복 파일 정리 (최종 보고서만 유지)
rm -rf ${DATA_DIR}/reports/archive/
find ${DATA_DIR}/reports/ -type f ! -name "environmental-scan-*.md" -delete
```

### Step 17-C: weekly 폴더 정리

```bash
# ═══════════════════════════════════════════════════════════════
# weekly 폴더 정리 (주간 집계 후 실행)
# ═══════════════════════════════════════════════════════════════
# 유지: priority-ranked-weekly-*.json, weekly-environmental-scan-*.md
# 삭제: hallucination-report, impact-assessment, 중간 보고서

WEEKLY_DIR="data/weekly/{YYYY}/W{WW}"

# 1. analysis/ 폴더 정리 (priority-ranked만 유지)
find ${WEEKLY_DIR}/analysis/ -type f ! -name "priority-ranked-weekly-*.json" -delete 2>/dev/null

# 2. 루트 임시 보고서 삭제 (최종 보고서만 유지)
find ${WEEKLY_DIR}/ -maxdepth 1 -type f ! -name "weekly-environmental-scan-*.md" -delete 2>/dev/null
```

### 정리 후 data 폴더 구조

```
data/{YYYY}/{MM}/{DD}/
├── structured/
│   └── structured-signals-{date}.json  ← 유지 (아카이브)
├── analysis/
│   ├── priority-ranked-{date}.json     ← 유지 (우선순위 기록)
│   └── keyword-analytics-{date}.json   ← 유지 (키워드 효과성)
└── reports/
    └── environmental-scan-{date}.md    ← 유지 (최종 보고서)

data/weekly/{YYYY}/W{WW}/
├── analysis/
│   └── priority-ranked-weekly-*.json   ← 유지 (주간 우선순위)
└── weekly-environmental-scan-*.md      ← 유지 (주간 보고서)
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
