# Marathon Controller Agent

## Marathon Mode 정의

**Marathon Mode = 다중 소스 스캐닝 단계만 3시간으로 확장하는 모드**

- 영향 받는 단계: `@multi-source-scanner` (Phase 1의 2단계)만 해당
- 영향 받지 않는 단계: 나머지 모든 단계 (dedup, classifier, analyzer, report 등)는 기존과 동일

```
┌─────────────────────────────────────────────────────────────────────┐
│                    환경스캐닝 전체 워크플로우                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Phase 1: Research (정보 수집)                                      │
│  ─────────────────────────────                                      │
│  1. @archive-loader (기존과 동일)                                   │
│  2. @multi-source-scanner ◀─── [Marathon Mode: 3시간 확장]         │
│  3. @dedup-filter (기존과 동일)                                     │
│                                                                     │
│  Phase 2: Planning (분석)                                           │
│  ────────────────────────                                           │
│  4-8. classifier, analyzer, ranker 등 (기존과 동일)                │
│                                                                     │
│  Phase 3: Implementation (보고서)                                   │
│  ─────────────────────────────                                      │
│  9-11. db-updater, report-generator 등 (기존과 동일)               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Marathon Mode 핵심 구조: 2단계

### Stage 1: 기존 소스 스캔 (Existing Sources Scan)

**기존 방식 그대로 실행**
- DB 로딩 → 등록된 소스 스캔 → 신호 수집
- 네이버/글로벌/구글 뉴스 크롤러 병렬 실행
- 소요 시간 측정 (stage1_duration)

### Stage 2: 신규 소스 탐험 (New Source Discovery)

**완전히 새로운 소스 발굴** - 이전 환경스캐닝에서 **한 번도 스캔하지 않은** 소스 탐색

```
잔여 시간 = 180분 - stage1_duration
잔여 시간 전체를 Stage 2에 강제 배정
```

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Marathon Mode: 3시간 = 180분                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐                                                │
│  │   Stage 1       │  기존 소스 스캔                                │
│  │   (가변)        │  • DB에 등록된 소스 순차 스캔                  │
│  │                 │  • 소요 시간 측정                              │
│  └────────┬────────┘                                                │
│           │                                                         │
│           ▼                                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                        Stage 2                               │   │
│  │               (잔여 시간 전체 강제 배정)                     │   │
│  │                                                              │   │
│  │   완전히 새로운 소스 탐험                                    │   │
│  │   • 이전에 한 번도 스캔하지 않은 소스 발굴                   │   │
│  │   • 4개 전문 에이전트 순차/병렬 실행                        │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Stage 2: 전문화된 다중 에이전트 구조

```
┌─────────────────────────────────────────────────────────────────────┐
│                    STAGE 2: 신규 소스 탐험                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Step 2-1: @gap-analyzer (분석 단계)                         │   │
│  │  ───────────────────────────────────                         │   │
│  │  • 현재 소스 DB 분석                                         │   │
│  │  • STEEPS 카테고리별 갭 식별                                 │   │
│  │  • 지역별 갭 식별                                            │   │
│  │  • 언어별 갭 식별                                            │   │
│  │  • 탐험 우선순위 맵 생성                                     │   │
│  │                                                              │   │
│  │  출력: context/exploration-priorities-{date}.json            │   │
│  └──────────────────────────┬──────────────────────────────────┘   │
│                             │                                       │
│                             ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Step 2-2: @frontier-explorer + @citation-chaser (병렬)      │   │
│  ├─────────────────────────┬───────────────────────────────────┤   │
│  │  @frontier-explorer     │  @citation-chaser                 │   │
│  │  (60% 시간)             │  (40% 시간)                       │   │
│  │  ──────────────────     │  ─────────────────                │   │
│  │  • 미개척 지역 탐험     │  • Stage 1 신호 인용 추적         │   │
│  │  • 비영어권 소스 발굴   │  • 원천 → 원천의 원천 역추적     │   │
│  │  • 신규 플랫폼 탐색     │  • 학술/싱크탱크 발굴             │   │
│  │  • 틈새 전문 매체 발견  │  • 정부/국제기구 소스 발견        │   │
│  │                         │                                   │   │
│  │  (갭 우선순위 기반)     │  (신호 품질 기반)                 │   │
│  └─────────────────────────┴───────────────────────────────────┘   │
│                             │                                       │
│                             ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Step 2-3: @rapid-validator (실시간 검증)                    │   │
│  │  ─────────────────────────────────────                       │   │
│  │  • 발견된 소스 즉시 평가 (100점 척도)                        │   │
│  │  • 70점+ → 자동 승격 (Tier 3)                               │   │
│  │  • 50-69점 → 보류 (다음 검토)                               │   │
│  │  • 49점 이하 → 폐기                                         │   │
│  │  • 기존 소스 DB 중복 최종 체크                               │   │
│  │                                                              │   │
│  │  출력: config/regular-sources.json (승격 시)                 │   │
│  │        config/discovered-sources.json (후보 관리)            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Stage 2 실행 프로토콜

### Step 2-1: 갭 분석

```
Task @gap-analyzer:
  입력: config/regular-sources.json, signals/database.json
  출력: context/exploration-priorities-{date}.json
  모델: haiku (빠른 분석)
```

### Step 2-2: 병렬 탐험

```
Task @frontier-explorer (PARALLEL):
  입력: context/exploration-priorities-{date}.json
  출력: config/discovered-sources.json (추가)
  시간: Stage 2 잔여 시간의 60%

Task @citation-chaser (PARALLEL):
  입력: data/{date}/raw/scanned-signals.json
  출력: config/discovered-sources.json (추가)
  시간: Stage 2 잔여 시간의 40%
```

### Step 2-3: 실시간 검증

```
Task @rapid-validator:
  입력: config/discovered-sources.json (validation_status: pending)
  출력:
    - config/regular-sources.json (승격된 소스 추가)
    - config/discovered-sources.json (상태 업데이트)
  모델: haiku (빠른 검증)
```

---

## 시간 배정 로직

```python
def marathon_time_allocation(stage1_duration):
    """
    Marathon Mode 시간 배정

    Args:
        stage1_duration: Stage 1 (기존 소스 스캔) 소요 시간 (분)

    Returns:
        Stage 2 에이전트별 시간 배정
    """
    TOTAL_MARATHON = 180  # 3시간 = 180분

    # Stage 2 시간 = 전체 - Stage 1 소요 시간
    stage2_time = TOTAL_MARATHON - stage1_duration

    return {
        "stage2_total": stage2_time,
        "gap_analyzer": 5,  # 고정 (빠른 분석)
        "frontier_explorer": (stage2_time - 5) * 0.55,  # 55%
        "citation_chaser": (stage2_time - 5) * 0.35,    # 35%
        "rapid_validator": (stage2_time - 5) * 0.10     # 10%
    }

# 예시
# stage1_duration = 10분 → stage2_time = 170분
#   gap_analyzer: 5분
#   frontier_explorer: 90분
#   citation_chaser: 58분
#   rapid_validator: 17분
```

---

## 전체 실행 흐름

```
[Marathon Mode 시작]
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Stage 1: 기존 소스 스캔                                      │
│  ────────────────────────                                     │
│  • start_time = now()                                         │
│  • @archive-loader 실행                                      │
│  • @multi-source-scanner (기존 소스) 실행                    │
│    - 네이버/글로벌/구글 크롤러 병렬 실행                     │
│  • stage1_end = now()                                        │
│  • stage1_duration = stage1_end - start_time                 │
│  • 수집된 신호 → data/{date}/raw/scanned-signals.json        │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Stage 2: 신규 소스 탐험                                      │
│  ────────────────────────                                     │
│  • stage2_time = 180분 - stage1_duration (강제 배정)         │
│                                                              │
│  Step 2-1: @gap-analyzer                                     │
│    → context/exploration-priorities-{date}.json              │
│                                                              │
│  Step 2-2: @frontier-explorer + @citation-chaser (병렬)      │
│    → config/discovered-sources.json                          │
│                                                              │
│  Step 2-3: @rapid-validator                                  │
│    → 70점+ 소스 → config/regular-sources.json 승격          │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
[Marathon Mode 종료 - 3시간 완료]
       │
       ▼
[이후 단계는 기존과 동일]
• @dedup-filter
• @signal-classifier
• @impact-analyzer
• @priority-ranker
• @db-updater
• @report-generator
• @archive-notifier
```

---

## 시간 추적 로그 구조

```json
{
  "marathon_session": {
    "date": "2026-01-13",
    "mode": "marathon",
    "total_duration_minutes": 180,

    "stage1_existing_sources": {
      "start": "2026-01-13T06:00:00Z",
      "end": "2026-01-13T06:15:00Z",
      "duration_minutes": 15,
      "sources_scanned": 177,
      "signals_found": 82
    },

    "stage2_new_source_discovery": {
      "start": "2026-01-13T06:15:00Z",
      "end": "2026-01-13T09:00:00Z",
      "duration_minutes": 165,
      "forced_allocation": true,

      "agents": {
        "gap_analyzer": {
          "duration_minutes": 5,
          "gaps_identified": {
            "steeps": ["Spiritual", "Political"],
            "regions": ["Africa", "Middle East"],
            "languages": ["Spanish", "Arabic"]
          }
        },
        "frontier_explorer": {
          "duration_minutes": 88,
          "sources_discovered": 35
        },
        "citation_chaser": {
          "duration_minutes": 55,
          "sources_discovered": 22
        },
        "rapid_validator": {
          "duration_minutes": 17,
          "sources_validated": 57,
          "promoted": 15,
          "pending": 25,
          "rejected": 17
        }
      },

      "total_new_sources_discovered": 57,
      "total_sources_promoted": 15
    }
  }
}
```

---

## 발견된 소스 처리

Stage 2에서 발견된 신규 소스는:

1. `config/discovered-sources.json`에 후보로 등록
2. `@rapid-validator`가 실시간 품질 평가
3. 품질 점수 70점 이상 → **자동 승격** (Tier 3으로 등록)
4. 50-69점 → 보류 (다음 Marathon에서 재검토)
5. 49점 이하 → 폐기 (기록은 유지)

---

## 성과 지표

| 지표 | 목표 | 측정 |
|------|------|------|
| Stage 1 효율 | ≤ 30분 | stage1_duration |
| Stage 2 시간 확보 | ≥ 150분 | stage2_duration |
| 신규 소스 발견 | ≥ 40개 | total_new_sources_discovered |
| 소스 승격 | ≥ 10개 | total_sources_promoted |
| 승격률 | ≥ 25% | promoted / discovered |

---

## 호출 방법

```bash
# Marathon Mode 실행 (전체 워크플로우)
/env-scan:run --marathon --skip-human

# Marathon Mode 상태 확인
/env-scan:status
```
