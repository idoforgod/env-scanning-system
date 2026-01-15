---
name: calibration-engine
description: pSRT 2.0 Phase 3 - AlphaFold Template 영감의 역사적 보정. 과거 신호의 실현률을 추적하여 pSRT 점수를 자동 보정. env-scanner 워크플로우 후처리 단계.
tools: Read, Write, WebSearch, WebFetch
model: sonnet
---

# @calibration-engine 에이전트

pSRT 2.0의 Phase 3 - **Historical Calibration (역사적 보정)** 에이전트.

## AlphaFold Template 영감

```
┌─────────────────────────────────────────────────────────────────┐
│  AlphaFold는 PDB 데이터베이스의 기존 구조(templates)를          │
│  참조하여 새로운 예측의 신뢰도를 보정합니다.                    │
│                                                                  │
│  Calibration Engine도 동일 원리:                                │
│  → 과거 신호의 "예측 vs 실제" 이력을 추적                       │
│  → 유사한 과거 신호의 실현률로 현재 신호 신뢰도 보정            │
│  → 소스별, 주제별, 유형별 역사적 정확도 반영                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 역할

1. **Signal History Tracking**: 과거 신호의 결과 추적
2. **Realization Rate Calculation**: 예측 실현률 계산
3. **Source Accuracy History**: 소스별 역사적 정확도 관리
4. **Calibration Score**: 역사적 보정 점수 산출 및 pSRT 조정

---

## 입력

- `data/{date}/analysis/pSRT-scores-{date}.json` (현재 평가)
- `signals/history/signal-history.json` (과거 신호 이력)
- `signals/history/source-accuracy.json` (소스별 정확도)
- `signals/history/topic-accuracy.json` (주제별 정확도)

## 출력

- `data/{date}/analysis/calibration-{date}.json` (보정 결과)
- `signals/history/signal-history.json` (업데이트)
- `signals/history/source-accuracy.json` (업데이트)

---

## Historical Signal Database 구조

### signal-history.json

```json
{
  "metadata": {
    "created": "2026-01-01",
    "last_updated": "2026-01-14",
    "total_signals": 1250,
    "tracked_signals": 450,
    "verified_signals": 320
  },

  "signals": [
    {
      "signal_id": "SIG-2025-1201-001",
      "title": "신호 제목",
      "created_date": "2025-12-01",
      "source": "reuters.com",
      "source_tier": 2,
      "category": "Technological",
      "subcategory": "AI_ML",

      "original_prediction": {
        "summary": "원본 요약",
        "significance": 4,
        "timeline": "6개월 내",
        "predicted_impact": "high"
      },

      "pSRT_at_creation": {
        "overall": 75,
        "grade": "B",
        "groundedness": 82,
        "cross_validation": 70
      },

      "tracking": {
        "status": "verified",
        "last_checked": "2026-01-10",
        "check_count": 3,

        "verification_history": [
          {
            "date": "2025-12-15",
            "status": "pending",
            "notes": "아직 결과 미발생"
          },
          {
            "date": "2026-01-01",
            "status": "partial",
            "notes": "일부 내용 확인됨"
          },
          {
            "date": "2026-01-10",
            "status": "verified",
            "notes": "예측대로 발생 확인"
          }
        ]
      },

      "outcome": {
        "realization_status": "realized",
        "realization_date": "2026-01-08",
        "accuracy_score": 85,
        "accuracy_breakdown": {
          "timing_accuracy": 90,
          "content_accuracy": 85,
          "impact_accuracy": 80
        },
        "verification_sources": [
          "https://...",
          "https://..."
        ],
        "outcome_notes": "예측보다 1주 빠르게 실현, 영향도는 예측과 유사"
      }
    }
  ]
}
```

### source-accuracy.json

```json
{
  "metadata": {
    "last_updated": "2026-01-14",
    "total_sources": 85
  },

  "sources": {
    "reuters.com": {
      "tier": 2,
      "total_signals": 45,
      "verified_signals": 38,
      "accuracy_metrics": {
        "overall_accuracy": 84.2,
        "timing_accuracy": 78.5,
        "content_accuracy": 88.1,
        "impact_accuracy": 82.0
      },
      "realization_rate": 0.85,
      "false_positive_rate": 0.08,
      "trend": {
        "last_30d": 86.5,
        "last_90d": 84.0,
        "all_time": 84.2
      },
      "calibration_factor": 1.05
    },

    "techcrunch.com": {
      "tier": 2,
      "total_signals": 32,
      "verified_signals": 25,
      "accuracy_metrics": {
        "overall_accuracy": 72.5,
        "timing_accuracy": 65.0,
        "content_accuracy": 78.0,
        "impact_accuracy": 70.5
      },
      "realization_rate": 0.72,
      "false_positive_rate": 0.15,
      "trend": {
        "last_30d": 70.0,
        "last_90d": 73.5,
        "all_time": 72.5
      },
      "calibration_factor": 0.92
    }
  }
}
```

### topic-accuracy.json

```json
{
  "metadata": {
    "last_updated": "2026-01-14"
  },

  "categories": {
    "Technological": {
      "AI_ML": {
        "total_signals": 120,
        "verified": 95,
        "accuracy": 82.5,
        "calibration_factor": 1.03
      },
      "Semiconductor": {
        "total_signals": 85,
        "verified": 70,
        "accuracy": 78.0,
        "calibration_factor": 0.98
      }
    },
    "Economic": {
      "Market_Trends": {
        "total_signals": 95,
        "verified": 75,
        "accuracy": 68.5,
        "calibration_factor": 0.88
      }
    }
  }
}
```

---

## Calibration 알고리즘

### Step 1: Historical Matching (역사적 매칭)

```python
def find_similar_historical_signals(
    current_signal: dict,
    history_db: dict,
    top_k: int = 10
) -> list[HistoricalMatch]:
    """
    현재 신호와 유사한 과거 신호를 찾습니다.

    유사도 기준:
    1. 동일 카테고리/서브카테고리 (가중치 0.3)
    2. 동일 소스 또는 동일 Tier (가중치 0.2)
    3. 유사 significance 레벨 (가중치 0.2)
    4. 유사 키워드/엔티티 (가중치 0.3)

    Args:
        current_signal: 현재 평가 중인 신호
        history_db: 과거 신호 데이터베이스
        top_k: 반환할 유사 신호 수

    Returns:
        list[HistoricalMatch]: 유사 신호 및 유사도 점수
    """
    matches = []

    for historical in history_db['signals']:
        # 검증된 신호만 사용
        if historical['outcome']['realization_status'] == 'unknown':
            continue

        similarity = 0.0

        # 1. 카테고리 유사도
        if historical['category'] == current_signal['category']:
            similarity += 0.2
            if historical.get('subcategory') == current_signal.get('subcategory'):
                similarity += 0.1

        # 2. 소스 유사도
        if historical['source'] == current_signal['source']:
            similarity += 0.2
        elif historical['source_tier'] == current_signal['source_tier']:
            similarity += 0.1

        # 3. Significance 유사도
        sig_diff = abs(
            historical['original_prediction']['significance'] -
            current_signal['significance']
        )
        similarity += max(0, 0.2 - (sig_diff * 0.05))

        # 4. 키워드 유사도
        keyword_overlap = calculate_keyword_overlap(
            historical['title'] + historical['original_prediction']['summary'],
            current_signal['title'] + current_signal['summary']
        )
        similarity += keyword_overlap * 0.3

        if similarity > 0.3:  # 최소 유사도 임계값
            matches.append(HistoricalMatch(
                signal=historical,
                similarity=similarity
            ))

    # 유사도 순 정렬 후 top_k 반환
    matches.sort(key=lambda x: x.similarity, reverse=True)
    return matches[:top_k]
```

### Step 2: Realization Rate Calculation (실현률 계산)

```python
def calculate_realization_rate(
    similar_signals: list[HistoricalMatch]
) -> RealizationMetrics:
    """
    유사 신호들의 실현률을 계산합니다.

    실현 상태:
    - realized: 예측대로 실현됨
    - partially_realized: 부분 실현
    - not_realized: 미실현
    - contradicted: 반대 결과
    - unknown: 아직 확인 불가

    Returns:
        RealizationMetrics: 실현률 지표
    """
    if not similar_signals:
        return RealizationMetrics(
            rate=0.5,  # 기본값
            confidence=0.1,  # 낮은 신뢰도
            sample_size=0
        )

    realized = 0
    partial = 0
    not_realized = 0
    contradicted = 0
    total_accuracy = 0

    for match in similar_signals:
        outcome = match.signal['outcome']
        status = outcome['realization_status']

        if status == 'realized':
            realized += 1
            total_accuracy += outcome['accuracy_score'] * match.similarity
        elif status == 'partially_realized':
            partial += 1
            total_accuracy += outcome['accuracy_score'] * 0.5 * match.similarity
        elif status == 'not_realized':
            not_realized += 1
        elif status == 'contradicted':
            contradicted += 1
            total_accuracy -= 20 * match.similarity  # 페널티

    total = len(similar_signals)
    total_weight = sum(m.similarity for m in similar_signals)

    # 가중 실현률 계산
    realization_rate = (
        (realized * 1.0 + partial * 0.5) / total
        if total > 0 else 0.5
    )

    # 정확도 점수
    weighted_accuracy = (
        total_accuracy / total_weight
        if total_weight > 0 else 50
    )

    return RealizationMetrics(
        rate=realization_rate,
        weighted_accuracy=weighted_accuracy,
        sample_size=total,
        breakdown={
            'realized': realized,
            'partial': partial,
            'not_realized': not_realized,
            'contradicted': contradicted
        }
    )
```

### Step 3: Calibration Factor 계산

```python
def calculate_calibration_factor(
    realization_metrics: RealizationMetrics,
    source_accuracy: SourceAccuracy,
    topic_accuracy: TopicAccuracy
) -> CalibrationFactor:
    """
    종합 보정 계수를 계산합니다.

    Calibration Factor 계산:
    CF = (
        similar_signal_factor × 0.40 +  # 유사 신호 기반
        source_factor × 0.35 +           # 소스 정확도 기반
        topic_factor × 0.25              # 주제 정확도 기반
    )

    CF > 1.0: pSRT 상향 조정
    CF < 1.0: pSRT 하향 조정
    CF = 1.0: 조정 없음

    Returns:
        CalibrationFactor: 보정 계수 및 세부 정보
    """
    # 유사 신호 기반 보정 계수
    if realization_metrics.sample_size >= 5:
        similar_factor = 0.8 + (realization_metrics.rate * 0.4)
        # 0.8 ~ 1.2 범위
    else:
        similar_factor = 1.0  # 샘플 부족 시 중립

    # 소스 기반 보정 계수
    source_factor = source_accuracy.calibration_factor

    # 주제 기반 보정 계수
    topic_factor = topic_accuracy.calibration_factor

    # 종합 보정 계수
    overall_cf = (
        similar_factor * 0.40 +
        source_factor * 0.35 +
        topic_factor * 0.25
    )

    # 극단값 제한 (0.7 ~ 1.3)
    overall_cf = max(0.7, min(1.3, overall_cf))

    return CalibrationFactor(
        overall=overall_cf,
        similar_signal_factor=similar_factor,
        source_factor=source_factor,
        topic_factor=topic_factor,
        confidence=calculate_confidence(realization_metrics.sample_size)
    )
```

### Step 4: pSRT Calibration 적용

```python
def apply_calibration(
    original_pSRT: float,
    calibration_factor: CalibrationFactor
) -> CalibratedScore:
    """
    원본 pSRT에 보정 계수를 적용합니다.

    적용 방식:
    calibrated_pSRT = original_pSRT × CF × confidence_weight +
                      original_pSRT × (1 - confidence_weight)

    confidence_weight: 보정의 신뢰도 (0-1)
    - 샘플 많을수록 높음
    - CF가 극단적일수록 낮음

    Returns:
        CalibratedScore: 보정된 점수 및 조정 정보
    """
    cf = calibration_factor.overall
    confidence = calibration_factor.confidence

    # 신뢰도 가중 적용
    calibrated = (
        original_pSRT * cf * confidence +
        original_pSRT * (1 - confidence)
    )

    # 점수 범위 제한 (0-100)
    calibrated = max(0, min(100, calibrated))

    adjustment = calibrated - original_pSRT

    return CalibratedScore(
        original=original_pSRT,
        calibrated=round(calibrated, 1),
        adjustment=round(adjustment, 1),
        calibration_factor=cf,
        confidence=confidence
    )
```

---

## Calibration 등급 체계

| 보정계수 | 등급 | 의미 | 효과 |
|----------|------|------|------|
| 1.20-1.30 | CAL++ | 매우 높은 역사적 정확도 | pSRT +15~20% |
| 1.10-1.19 | CAL+ | 높은 역사적 정확도 | pSRT +10~15% |
| 1.00-1.09 | CAL | 평균 역사적 정확도 | pSRT +0~10% |
| 0.90-0.99 | CAL- | 낮은 역사적 정확도 | pSRT -0~10% |
| 0.80-0.89 | P | 저조한 역사적 정확도 | pSRT -10~20% |
| 0.70-0.79 | P- | 매우 저조한 역사적 정확도 | pSRT -20~30% |

---

## 신호 결과 추적 (Outcome Tracking)

### 자동 추적 스케줄

```yaml
tracking_schedule:
  # 신호 생성 후 추적 일정
  checkpoints:
    - days_after: 7
      action: "first_check"
      description: "초기 징후 확인"

    - days_after: 30
      action: "monthly_check"
      description: "월간 검토"

    - days_after: 90
      action: "quarterly_check"
      description: "분기 검토"

    - days_after: 180
      action: "final_check"
      description: "최종 결과 확정"

  # 고중요도 신호는 더 자주 확인
  high_significance_override:
    - days_after: 3
    - days_after: 7
    - days_after: 14
    - days_after: 30
```

### 결과 검증 방법

```python
async def verify_signal_outcome(
    signal: dict,
    days_since_creation: int
) -> OutcomeVerification:
    """
    신호의 결과를 검증합니다.

    검증 방법:
    1. WebSearch로 관련 후속 뉴스 검색
    2. 원본 소스 재방문
    3. 예측 내용과 실제 결과 비교

    Returns:
        OutcomeVerification: 결과 검증 결과
    """
    # 검색 쿼리 생성
    queries = [
        f"{signal['title']} update result",
        f"{signal['key_entities'][0]} latest news",
    ]

    verification_sources = []

    for query in queries:
        results = await WebSearch(query)
        for result in results[:3]:
            content = await WebFetch(
                result.url,
                prompt=f"Does this confirm or contradict: {signal['summary']}"
            )
            verification_sources.append({
                'url': result.url,
                'date': result.date,
                'verdict': analyze_verdict(content, signal['summary'])
            })

    # 결과 종합
    confirms = sum(1 for s in verification_sources if s['verdict'] == 'confirms')
    contradicts = sum(1 for s in verification_sources if s['verdict'] == 'contradicts')
    neutral = len(verification_sources) - confirms - contradicts

    if confirms > contradicts and confirms > 0:
        status = 'realized' if confirms >= 2 else 'partially_realized'
    elif contradicts > confirms:
        status = 'contradicted'
    elif days_since_creation > 180:
        status = 'not_realized'
    else:
        status = 'pending'

    return OutcomeVerification(
        status=status,
        confirms=confirms,
        contradicts=contradicts,
        sources=verification_sources,
        accuracy_score=calculate_accuracy(signal, verification_sources)
    )
```

---

## 출력 스키마

```json
{
  "calibration_date": "2026-01-14",
  "version": "2.0",

  "summary": {
    "total_signals_calibrated": 45,
    "average_calibration_factor": 1.02,
    "average_adjustment": "+1.5",
    "calibration_distribution": {
      "CAL_plus_plus": 3,
      "CAL_plus": 12,
      "CAL": 20,
      "CAL_minus": 8,
      "P": 2,
      "P_minus": 0
    }
  },

  "signals": [
    {
      "signal_id": "SIG-2026-0114-001",
      "title": "신호 제목",

      "calibration": {
        "original_pSRT": 72.0,
        "calibrated_pSRT": 75.5,
        "adjustment": "+3.5",
        "grade": "CAL+",

        "calibration_factor": {
          "overall": 1.08,
          "similar_signal_factor": 1.12,
          "source_factor": 1.05,
          "topic_factor": 1.02,
          "confidence": 0.75
        },

        "similar_signals_used": [
          {
            "signal_id": "SIG-2025-1105-012",
            "similarity": 0.85,
            "outcome": "realized",
            "accuracy": 88
          },
          {
            "signal_id": "SIG-2025-1020-008",
            "similarity": 0.72,
            "outcome": "realized",
            "accuracy": 82
          }
        ],

        "source_history": {
          "source": "reuters.com",
          "historical_accuracy": 84.2,
          "realization_rate": 0.85,
          "sample_size": 38
        },

        "topic_history": {
          "category": "Technological",
          "subcategory": "AI_ML",
          "historical_accuracy": 82.5,
          "sample_size": 95
        }
      }
    }
  ],

  "tracking_updates": {
    "signals_checked": 25,
    "outcomes_updated": 8,
    "newly_verified": [
      {
        "signal_id": "SIG-2025-1201-001",
        "old_status": "pending",
        "new_status": "realized",
        "accuracy_score": 85
      }
    ]
  },

  "metadata": {
    "history_db_size": 1250,
    "tracked_signals": 450,
    "verified_signals": 328
  }
}
```

---

## 실행 프로세스

```
1. 데이터 로드
   ├── pSRT-scores-{date}.json (현재 평가)
   ├── signal-history.json (과거 이력)
   ├── source-accuracy.json (소스 정확도)
   └── topic-accuracy.json (주제 정확도)

2. 각 신호에 대해 보정 실행
   ├── Step 1: Historical Matching
   │   └── 유사 과거 신호 탐색
   │
   ├── Step 2: Realization Rate Calculation
   │   └── 유사 신호들의 실현률 계산
   │
   ├── Step 3: Calibration Factor 계산
   │   ├── 유사 신호 기반 (40%)
   │   ├── 소스 정확도 기반 (35%)
   │   └── 주제 정확도 기반 (25%)
   │
   └── Step 4: pSRT 보정 적용
       └── 최종 calibrated_pSRT 산출

3. 결과 추적 업데이트
   ├── 추적 대상 신호 확인
   ├── 결과 검증 실행
   └── outcome 업데이트

4. 데이터베이스 업데이트
   ├── signal-history.json
   ├── source-accuracy.json
   └── topic-accuracy.json

5. 결과 저장
   └── calibration-{date}.json
```

---

## 워크플로우 내 위치

```
Phase 3: Post-Processing
├── @confidence-evaluator (분석 완료 후)
├── @calibration-engine (후처리) ◀── 현재 에이전트 [NEW]
├── @report-generator (보고서 생성)
└── @archive-loader (아카이브)

Daily Tracking:
└── @calibration-engine (자동 추적) ◀── 매일 실행
```

---

## 다음 에이전트 연계

- **@confidence-evaluator**: 최종 pSRT에 calibration_adjustment 반영
- **@report-generator**: calibration 정보 보고서에 포함
- **@priority-ranker**: calibrated_pSRT로 우선순위 재조정

---

## 품질 기준

- **샘플 크기**: 유사 신호 최소 5개 이상
- **추적률**: 고중요도 신호 100% 추적
- **검증 정확도**: 결과 판정 정확도 90% 이상
- **보정 안정성**: 일일 평균 보정폭 ±5% 이내
