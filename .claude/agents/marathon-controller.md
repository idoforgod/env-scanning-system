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

### Stage 1: 기존 소스 스캔 (Existing Sources)

**기존 방식 그대로 실행**
- DB 로딩 → 등록된 소스 스캔 → 신호 수집
- 소요 시간 측정 (stage1_duration)

### Stage 2: 신규 소스 탐험 (New Source Discovery)

**완전히 새로운 소스 발굴** - 이전 환경스캐닝에서 **한 번도 스캔하지 않은** 소스 탐색
- 잔여 시간 = 180분 - stage1_duration
- 잔여 시간 **전체**를 Stage 2에 **강제 배정**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Marathon Mode: 3시간 = 180분                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐                                                │
│  │   Stage 1       │  기존 소스 스캔                                │
│  │   (가변 시간)   │  • DB에 등록된 소스 순차 스캔                  │
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
│  ──────                                                             │
│  Stage 1: 10분 소요 → Stage 2: 170분 강제 배정 (2시간 50분)        │
│  Stage 1: 30분 소요 → Stage 2: 150분 강제 배정 (2시간 30분)        │
│  Stage 1: 60분 소요 → Stage 2: 120분 강제 배정 (2시간)             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Stage 2: 신규 소스 탐험 전략

Stage 2의 목적은 **기존 소스 DB에 없는, 완전히 새로운 소스**를 발굴하는 것.

### 4가지 탐험 전략 (각 25% 시간 배분)

#### 전략 1: 인용 추적 (Citation Tracking)
```
1. Stage 1에서 수집한 고품질 신호 선택
2. 해당 신호의 원문에서 인용된 소스 추출
3. 자주 인용되는 새로운 도메인 발견
4. pending-sources.json에 후보 등록
```

#### 전략 2: 도메인 탐험 (Domain Exploration)
```
1. 기존 소스 도메인 패턴 분석
   예: stanford.edu가 있으면 → berkeley.edu, mit.edu 탐색
2. 유사 도메인에서 신호 검색
3. 가치 있는 새 소스 발견 시 후보 등록
```

#### 전략 3: 키워드 확장 (Keyword Expansion)
```
1. STEEPS 6개 카테고리 균형 분석
2. 부족한 카테고리 키워드 생성
3. 웹 검색으로 새 소스 발굴
4. 검증 후 후보 등록
```

#### 전략 4: 지역 확장 (Regional Expansion)
```
1. 현재 소스의 지역 분포 분석
2. 미개척 지역 (라틴아메리카, 아프리카, 동남아 등) 식별
3. 해당 지역 전문 소스 탐색
4. 검증 후 후보 등록
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
        Stage 2에 배정할 시간 (분)
    """
    TOTAL_MARATHON = 180  # 3시간 = 180분

    # Stage 2 시간 = 전체 - Stage 1 소요 시간
    stage2_time = TOTAL_MARATHON - stage1_duration

    # Stage 2 시간을 4가지 전략에 균등 배분
    per_strategy = stage2_time / 4

    return {
        "stage2_total": stage2_time,
        "citation_tracking": per_strategy,
        "domain_exploration": per_strategy,
        "keyword_expansion": per_strategy,
        "regional_expansion": per_strategy
    }

# 예시
# stage1_duration = 10분 → stage2_time = 170분 (각 전략 42.5분)
# stage1_duration = 30분 → stage2_time = 150분 (각 전략 37.5분)
```

---

## 실행 흐름

```
[Marathon Mode 시작]
       │
       ▼
┌──────────────────────────────────────────────────────┐
│  Stage 1: 기존 소스 스캔                              │
│  ────────────────────────                             │
│  • start_time = now()                                 │
│  • DB 로딩                                           │
│  • 등록된 소스 스캔 (Tier 1 → Tier 2 → ...)         │
│  • stage1_end = now()                                │
│  • stage1_duration = stage1_end - start_time         │
└──────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│  Stage 2: 신규 소스 탐험                              │
│  ────────────────────────                             │
│  • stage2_time = 180분 - stage1_duration             │
│  • 4가지 탐험 전략 순환 실행                         │
│  • 발견된 소스 → pending-sources.json               │
└──────────────────────────────────────────────────────┘
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
• @source-evolver (발견된 소스 평가/등록)
• @file-organizer (파일 정리)
```

---

## 시간 추적 로그 구조

```json
{
  "marathon_session": {
    "date": "2026-01-12",
    "total_duration_minutes": 180,

    "stage1_existing_sources": {
      "start": "2026-01-12T06:00:00Z",
      "end": "2026-01-12T06:10:00Z",
      "duration_minutes": 10,
      "sources_scanned": 177,
      "signals_found": 73
    },

    "stage2_new_source_discovery": {
      "start": "2026-01-12T06:10:00Z",
      "end": "2026-01-12T09:00:00Z",
      "duration_minutes": 170,
      "forced_allocation": true,
      "strategies": {
        "citation_tracking": {
          "duration_minutes": 42.5,
          "sources_discovered": 8
        },
        "domain_exploration": {
          "duration_minutes": 42.5,
          "sources_discovered": 12
        },
        "keyword_expansion": {
          "duration_minutes": 42.5,
          "sources_discovered": 6
        },
        "regional_expansion": {
          "duration_minutes": 42.5,
          "sources_discovered": 9
        }
      },
      "total_new_sources_discovered": 35
    }
  }
}
```

---

## 발견된 소스 처리

Stage 2에서 발견된 신규 소스는:

1. `evolution/pending-sources.json`에 후보로 등록
2. Marathon 종료 후 `@source-evolver`가 품질 평가
3. 품질 점수 70점 이상 → 자동 승격 (Tier 3으로 등록)
4. 50-69점 → 보류 (다음 검토)
5. 49점 이하 → 폐기

---

## 성과 지표

| 지표 | 목표 | 측정 |
|------|------|------|
| Stage 1 효율 | ≤ 30분 | stage1_duration |
| Stage 2 시간 확보 | ≥ 150분 | stage2_duration |
| 신규 소스 발견 | ≥ 20개 | total_new_sources_discovered |
| 소스 승격률 | ≥ 30% | approved / discovered |

---

## 호출 방법

```bash
# Marathon Mode 실행 (전체 워크플로우)
/env-scan:run --marathon --skip-human

# Marathon Mode 상태 확인
/env-scan:status
```
