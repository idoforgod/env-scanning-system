# Environmental Scanning System

미래 연구(Futures Research)를 위한 환경스캐닝 자동화 시스템.

## 프로젝트 개요

변화의 조기 징후(약한 신호, weak signals)를 체계적으로 탐지하고 분석하여 일일 보고서를 생성합니다.

## 핵심 명령어

| 명령어 | 설명 |
|--------|------|
| `/env-scan:run` | **기본값: Marathon Mode (심층 스캔, 크롤러 강제 호출)** |
| `/env-scan:run --fast` | Fast Mode (구글 뉴스만 빠르게 스캔) |
| `/env-scan:run --with-review` | Human Review 포함 (각 Phase 후 검토) |
| `/env-scan:resume` | 체크포인트에서 재개 |
| `/env-scan:status` | 현재 상태 확인 |
| `/env-scan:consolidate` | **주간 종합 보고서 생성 (중복 제거 및 통합)** |
| `/env-scan:consolidate --week 2026-W03` | 특정 주차 보고서 생성 |
| `/env-scan:consolidate-monthly` | **월간 종합 보고서 생성 (심층 분석)** |
| `/env-scan:consolidate-monthly --month 2026-01` | 특정 월 보고서 생성 |
| `/env-scan:consolidate-quarterly` | **분기 종합 보고서 생성 (메타 분석 및 품질 평가)** |
| `/env-scan:consolidate-quarterly --quarter 2026-Q1` | 특정 분기 보고서 생성 |

---

## v3.2 주요 변경 (2026-01-13)

### 워크플로우 순서 수정

**v3.1 결함**: Marathon Stage 2 신호가 signal-merger/dedup-filter를 거치지 않음
**v3.2 해결**: **모든 데이터 수집 후 병합** - 워크플로우 순서 수정

```
v2.x (문제):
  multi-source-scanner → WebSearch만 (크롤러 무시)

v3.0 (불완전):
  3개 크롤러만 → 기존 WebSearch 스캐닝 누락

v3.1 (결함):
  스캐너 → merger → dedup → Marathon Stage 2 → Gate 1
  ❌ Marathon 신호가 병합/중복제거 안됨

v3.2 (수정):
  스캐너 → Marathon Stage 2 → merger (6개 통합) → dedup → Gate 1
  ✓ 모든 신호가 병합/중복제거됨
```

### Gate 1 강화

**필수 파일 8개** (하나라도 없으면 Phase 2 진입 불가):

**4개 스캐너 출력:**
- `naver-scan-{date}.json` - 네이버 뉴스 크롤러
- `global-news-{date}.json` - 글로벌 뉴스 크롤러
- `google-news-{date}.json` - 구글 뉴스 크롤러
- `steeps-scan-{date}.json` - STEEPS WebSearch 스캐너

**Marathon Stage 2 출력:**
- `gap-analysis-{date}.json` - Gap 분석
- `frontier-signals-{date}.json` - Frontier 탐험
- `citation-signals-{date}.json` - Citation 추적
- `validated-sources-{date}.json` - 소스 검증

---

## Orchestrator 패턴 v3.2

### 핵심 원칙

1. **6개 소스 통합 병합**: 4개 스캐너 + 2개 Marathon 출력 통합
2. **파일 기반 게이트**: 8개 출력 파일 필수 검증
3. **병렬 실행**: 스캐너 4개 동시, Marathon 탐험 2개 동시
4. **올바른 순서**: 데이터 수집 → 병합 → 중복제거

### Phase 1 워크플로우 (v3.2 - 수정된 순서)

```
Step 1: archive-loader
        ↓
Step 2: 4개 스캐너 병렬 (강제!)
        ┌────────────┬────────────┬────────────┬────────────┐
        │ naver-news │ global-news│ google-news│ STEEPS     │
        │  crawler   │  crawler   │  crawler   │ scanner    │
        └─────┬──────┴─────┬──────┴─────┬──────┴─────┬──────┘
              └────────────┴────────────┴────────────┘
                           ↓
Step 3: Marathon Stage 2 (강제!) - 스캐너 완료 후 실행
        ┌────────────────────────────────────────────┐
        │ 3-1: gap-analyzer (선행)                   │
        │         ↓                                  │
        │ 3-2: frontier-explorer + citation-chaser  │
        │         ↓                                  │
        │ 3-3: rapid-validator (후행)               │
        └────────────────────────────────────────────┘
                           ↓
Step 4: signal-merger (6개 소스 통합!)
        입력: naver + global + google + steeps + frontier + citation
        ↓
Step 5: dedup-filter (모든 신호 중복 제거)
        ↓
     [Gate 1 - 8개 파일 필수!]
```

### 설정 파일

- `config/workflow-definition-v3.yaml`: v3.2 워크플로우 정의
- `.claude/commands/env-scan/run.md`: v3.2 실행 프로토콜
- `.claude/agents/signal-merger.md`: 6개 소스 결과 병합 에이전트

---

## Marathon Mode (기본값): 심층 소스 탐험

### 핵심 목적
- 다중 소스 스캐닝 단계를 **확장**하여 심층 탐색 수행
- **이전에 한 번도 스캔하지 않은** 완전히 새로운 소스 발굴
- Stage 1 완료 후 잔여 시간 **전체**를 Stage 2에 **강제 배정**

> **Note**: `/env-scan:run` 실행 시 기본적으로 Marathon 모드로 작동합니다.
> 빠른 스캔이 필요하면 `--fast` 옵션을 사용하세요.

### 2단계 구조

```
┌─────────────────────────────────────────────────────────┐
│  Stage 1: 크롤러 강제 호출                               │
│  • naver-news-crawler (한국 뉴스)                       │
│  • global-news-crawler (6개국 신문)                     │
│  • google-news-crawler (글로벌 뉴스)                    │
│  • signal-merger (결과 병합)                            │
├─────────────────────────────────────────────────────────┤
│  Stage 2: 신규 소스 탐험 (잔여 시간 전체 강제 배정)      │
│  • Step 2-1: @gap-analyzer (갭 분석)                    │
│  • Step 2-2: @frontier-explorer + @citation-chaser (병렬)│
│  • Step 2-3: @rapid-validator (실시간 검증)             │
└─────────────────────────────────────────────────────────┘
```

### Stage 2 전문 에이전트

| 에이전트 | 역할 | 배분 |
|----------|------|------|
| `@gap-analyzer` | STEEPS/지역/언어 갭 분석, 우선순위 맵 생성 | 선행 |
| `@frontier-explorer` | 미개척 지역/비영어권/신규 플랫폼 탐험 | 55% |
| `@citation-chaser` | 인용 체인 역추적, 원천 소스 발굴 | 35% |
| `@rapid-validator` | 발견 소스 실시간 검증 (70점+ 자동 승격) | 10% |

---

## 금지 사항 (v3.2)

1. **multi-source-scanner 위임 금지**: 스캐너를 직접 호출해야 함
2. **스캐너/Marathon 생략 금지**: 6개 소스 모두 실행 필수
3. **출력 없이 진행 금지**: Gate 1에서 8개 파일 확인
4. **순서 변경 금지**: 스캐너 → Marathon → merger → dedup 순서 준수

---

## MARATHON MODE 자동화 지침 (중요)

### Context Low 진입 시 자동 프로토콜

**Marathon Mode 실행 중 Context low가 감지되면 반드시 다음을 수행:**

1. **즉시 체크포인트 저장**
   ```
   Write to: logs/{YYYY}/{MM}/checkpoint-{DD}.json
   Write to: context/resume-summary-{date}.md
   ```

2. **사용자에게 알림**
   ```
   "Context low 감지. 체크포인트 저장 완료. /compact 실행 후 자동 재개합니다."
   ```

3. **Compact 후 자동 재개**
   - 새 세션 시작 시 체크포인트 파일 확인
   - `logs/{YYYY}/{MM}/checkpoint-{DD}.json` 존재 시 자동 재개

---

## 데이터 구조 (v3.2)

```
프로젝트/
├── .claude/                    # Claude Code 설정
│   ├── agents/                 # 에이전트 정의
│   │   ├── naver-news-crawler.md
│   │   ├── global-news-crawler.md
│   │   ├── google-news-crawler.md
│   │   ├── gap-analyzer.md     # Marathon: 갭 분석
│   │   ├── frontier-explorer.md # Marathon: 미개척 탐험
│   │   ├── citation-chaser.md  # Marathon: 인용 추적
│   │   ├── rapid-validator.md  # Marathon: 실시간 검증
│   │   └── signal-merger.md    # 6개 소스 결과 병합
│   ├── commands/               # 명령어 정의
│   └── skills/                 # 스킬 정의
│
├── config/                     # 설정 파일
│   ├── workflow-definition-v3.yaml  # v3.2 워크플로우
│   ├── regular-sources.json    # 정규 소스 목록
│   └── evolution/              # 진화 관련 설정
│
├── data/                       # 결과 데이터 (날짜별)
│   └── YYYY/MM/DD/
│       ├── raw/
│       │   ├── naver-scan-{date}.json        # 스캐너 1 (필수)
│       │   ├── global-news-{date}.json       # 스캐너 2 (필수)
│       │   ├── google-news-{date}.json       # 스캐너 3 (필수)
│       │   ├── steeps-scan-{date}.json       # 스캐너 4 (필수)
│       │   ├── frontier-signals-{date}.json  # Marathon (필수)
│       │   ├── citation-signals-{date}.json  # Marathon (필수)
│       │   └── scanned-signals-{date}.json   # 6개 통합 결과
│       ├── filtered/
│       │   └── filtered-signals-{date}.json  # 중복 제거 결과
│       ├── analysis/
│       │   ├── gap-analysis-{date}.json      # Marathon: Gap 분석
│       │   └── validated-sources-{date}.json # Marathon: 검증 결과
│       ├── structured/
│       └── reports/
│
├── signals/                    # 신호 DB
│   ├── database.json
│   └── snapshots/
│
├── context/                    # 컨텍스트 파일
├── logs/                       # 로그
├── CLAUDE.md                   # 프로젝트 지침
└── README.md
```

## STEEPS 분류 (6개 카테고리)

- **S**ocial (사회)
- **T**echnological (기술)
- **E**conomic (경제)
- **E**nvironmental (환경)
- **P**olitical (정치)
- **S**piritual (정신/영성)
