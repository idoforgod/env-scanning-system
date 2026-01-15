---
name: cross-validator
description: pSRT 2.0 Phase 2 - AlphaFold Ensemble 영감의 교차 검증 자동화. 독립적인 다중 소스에서 신호의 핵심 주장을 자동으로 검증. env-scanner 워크플로우 5.5단계.
tools: Read, Write, WebSearch, WebFetch
model: sonnet
---

# @cross-validator 에이전트

pSRT 2.0의 Phase 2 - **Cross-Validation (교차 검증)** 자동화 에이전트.

## AlphaFold Ensemble 영감

```
┌─────────────────────────────────────────────────────────────────┐
│  AlphaFold는 5개의 독립적인 모델 예측 간 일관성(Ensemble       │
│  Consistency)을 측정하여 신뢰도를 결정합니다.                   │
│                                                                  │
│  Cross-Validator도 동일 원리:                                   │
│  → 다수의 독립 소스에서 동일 정보가 확인되면 높은 신뢰도       │
│  → 소스 간 불일치가 있으면 낮은 신뢰도 + 플래그                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 역할

1. **Automatic Source Discovery**: 신호 주장에 대한 독립 소스 자동 검색
2. **Consistency Scoring**: 소스 간 일관성 점수 계산
3. **Contradiction Detection**: 상충되는 정보 감지
4. **Cross-Validation Score**: 종합 교차 검증 점수 산출

---

## 입력

- `data/{date}/analysis/groundedness-scores-{date}.json`
- `data/{date}/structured/structured-signals-{date}.json`
- `config/pSRT-config.yaml`
- `config/sources.yaml`

## 출력

- `data/{date}/analysis/cross-validation-{date}.json`

---

## 교차 검증 알고리즘

### Step 1: Key Claim Extraction (핵심 주장 추출)

```python
def extract_key_claims(signal: dict) -> list[KeyClaim]:
    """
    교차 검증이 필요한 핵심 주장을 추출합니다.

    우선순위:
    1. Groundedness에서 플래그된 주장
    2. significance_reason의 핵심 내용
    3. 수치/통계 포함 주장
    4. 인과관계 주장

    Returns:
        list[KeyClaim]: 검증할 핵심 주장 리스트
    """
    key_claims = []

    # 1. Groundedness 플래그된 주장 우선
    for flag in signal.get('groundedness', {}).get('hallucination_flags', []):
        key_claims.append(KeyClaim(
            text=flag['claim_text'],
            priority="critical",
            reason="groundedness_flagged"
        ))

    # 2. significance_reason
    if signal.get('significance_reason'):
        key_claims.append(KeyClaim(
            text=signal['significance_reason'],
            priority="high",
            reason="significance_claim"
        ))

    # 3. 수치 포함 주장
    for claim in extract_numerical_claims(signal['summary']):
        if claim not in [c.text for c in key_claims]:
            key_claims.append(KeyClaim(
                text=claim,
                priority="high",
                reason="numerical_claim"
            ))

    return key_claims
```

### Step 2: Independent Source Search (독립 소스 검색)

```python
async def search_independent_sources(
    claim: KeyClaim,
    original_source: str,
    config: dict
) -> list[IndependentSource]:
    """
    핵심 주장에 대한 독립 소스를 검색합니다.

    검색 전략:
    1. 주장의 핵심 키워드로 WebSearch
    2. 원본 소스와 다른 도메인만 필터링
    3. 신뢰도 Tier 2 이상 우선
    4. 최신성 (7일 이내) 우선

    Args:
        claim: 검증할 주장
        original_source: 원본 소스 URL (제외용)
        config: 검색 설정

    Returns:
        list[IndependentSource]: 발견된 독립 소스 리스트
    """
    # 검색 쿼리 생성
    queries = generate_search_queries(claim)

    independent_sources = []

    for query in queries:
        # WebSearch 실행
        results = await WebSearch(query)

        for result in results:
            # 원본 소스와 같은 도메인 제외
            if is_same_domain(result.url, original_source):
                continue

            # 신뢰도 확인
            source_tier = get_source_tier(result.domain)
            if source_tier > 3:  # Tier 4 이하 제외
                continue

            # 콘텐츠 추출
            content = await WebFetch(
                result.url,
                prompt="Extract the main claims about: " + claim.text
            )

            independent_sources.append(IndependentSource(
                url=result.url,
                domain=result.domain,
                title=result.title,
                content=content,
                tier=source_tier,
                publish_date=result.date
            ))

        # 최소 3개 소스 수집 목표
        if len(independent_sources) >= 3:
            break

    return independent_sources
```

### Step 3: Consistency Scoring (일관성 점수 계산)

```python
def calculate_consistency_score(
    claim: KeyClaim,
    sources: list[IndependentSource]
) -> ConsistencyResult:
    """
    소스 간 일관성 점수를 계산합니다.

    일관성 유형:
    1. FULL_CONFIRMATION: 모든 소스가 동일 내용 확인 (100점)
    2. MAJORITY_CONFIRMATION: 다수 소스가 확인 (80점)
    3. PARTIAL_CONFIRMATION: 일부 소스만 확인 (60점)
    4. CONTRADICTION: 상충되는 정보 존재 (30점)
    5. NO_CORROBORATION: 확인 불가 (20점)

    Args:
        claim: 검증 대상 주장
        sources: 독립 소스 리스트

    Returns:
        ConsistencyResult: 일관성 점수 및 세부 정보
    """
    if not sources:
        return ConsistencyResult(
            score=20,
            type="NO_CORROBORATION",
            confirming=0,
            contradicting=0,
            neutral=0
        )

    confirming_sources = []
    contradicting_sources = []
    neutral_sources = []

    for source in sources:
        verdict = verify_claim_in_source(claim.text, source.content)

        if verdict.confirms:
            confirming_sources.append(source)
        elif verdict.contradicts:
            contradicting_sources.append(source)
        else:
            neutral_sources.append(source)

    # 점수 계산
    total = len(sources)
    confirm_ratio = len(confirming_sources) / total
    contradict_ratio = len(contradicting_sources) / total

    if contradict_ratio > 0.3:
        return ConsistencyResult(
            score=30,
            type="CONTRADICTION",
            confirming=len(confirming_sources),
            contradicting=len(contradicting_sources),
            neutral=len(neutral_sources),
            contradictions=[s.url for s in contradicting_sources]
        )

    if confirm_ratio >= 0.8:
        return ConsistencyResult(
            score=100,
            type="FULL_CONFIRMATION",
            confirming=len(confirming_sources),
            contradicting=0,
            neutral=len(neutral_sources)
        )

    if confirm_ratio >= 0.5:
        return ConsistencyResult(
            score=80,
            type="MAJORITY_CONFIRMATION",
            confirming=len(confirming_sources),
            contradicting=len(contradicting_sources),
            neutral=len(neutral_sources)
        )

    if confirm_ratio > 0:
        return ConsistencyResult(
            score=60,
            type="PARTIAL_CONFIRMATION",
            confirming=len(confirming_sources),
            contradicting=len(contradicting_sources),
            neutral=len(neutral_sources)
        )

    return ConsistencyResult(
        score=20,
        type="NO_CORROBORATION",
        confirming=0,
        contradicting=0,
        neutral=len(neutral_sources)
    )
```

### Step 4: Cross-Validation Score 산출

```python
def calculate_cross_validation_score(
    claim_results: list[ConsistencyResult],
    source_diversity: float
) -> CrossValidationScore:
    """
    종합 교차 검증 점수를 산출합니다.

    계산:
    CV_Score = (
        avg_consistency × 0.50 +      # 평균 일관성
        diversity_score × 0.25 +       # 소스 다양성
        contradiction_penalty × 0.25   # 상충 페널티
    )

    Args:
        claim_results: 각 주장별 일관성 결과
        source_diversity: 소스 다양성 점수 (0-100)

    Returns:
        CrossValidationScore: 종합 점수
    """
    # 평균 일관성 계산
    avg_consistency = sum(r.score for r in claim_results) / len(claim_results)

    # 상충 페널티 계산
    contradiction_count = sum(
        1 for r in claim_results
        if r.type == "CONTRADICTION"
    )
    contradiction_penalty = max(0, 100 - (contradiction_count * 25))

    # 종합 점수 계산
    cv_score = (
        avg_consistency * 0.50 +
        source_diversity * 0.25 +
        contradiction_penalty * 0.25
    )

    return CrossValidationScore(
        overall=cv_score,
        avg_consistency=avg_consistency,
        source_diversity=source_diversity,
        contradiction_penalty=contradiction_penalty,
        contradiction_count=contradiction_count
    )
```

---

## 교차 검증 등급 체계

| 점수 | 등급 | 설명 | 신뢰도 영향 |
|------|------|------|-------------|
| 90-100 | CV++ | 다수 독립 소스 완전 확인 | pSRT +15 |
| 80-89 | CV+ | 다수 소스 확인 | pSRT +10 |
| 70-79 | CV | 부분 확인 | pSRT +5 |
| 60-69 | CV- | 최소 확인 | pSRT 0 |
| 40-59 | P | 확인 미흡 | pSRT -10 |
| 20-39 | P- | 확인 불가 | pSRT -15 |
| 0-19 | F | 상충 정보 발견 | pSRT -25 |

---

## 상충 감지 (Contradiction Detection)

### 상충 유형

```yaml
NUMERICAL_CONTRADICTION:
  definition: "수치가 다른 소스와 불일치"
  example:
    source_A: "매출 30% 증가"
    source_B: "매출 15% 증가"
  severity: HIGH
  action: "정확한 수치 확인 필요"

FACTUAL_CONTRADICTION:
  definition: "사실 관계가 상충"
  example:
    source_A: "A 회사가 B 회사 인수"
    source_B: "B 회사가 A 회사 인수"
  severity: CRITICAL
  action: "사실 확인 후 수정"

TEMPORAL_CONTRADICTION:
  definition: "시간/날짜 정보 상충"
  example:
    source_A: "2026년 1월 발표"
    source_B: "2026년 3월 발표 예정"
  severity: MEDIUM
  action: "정확한 일정 확인"

SCOPE_CONTRADICTION:
  definition: "범위/규모 정보 상충"
  example:
    source_A: "전국 시행"
    source_B: "수도권만 시행"
  severity: MEDIUM
  action: "정확한 범위 확인"
```

---

## 출력 스키마

```json
{
  "validation_date": "2026-01-14",
  "version": "2.0",
  "total_signals_validated": 45,

  "summary": {
    "average_cv_score": 72.5,
    "grade_distribution": {
      "CV_plus_plus": 5,
      "CV_plus": 15,
      "CV": 12,
      "CV_minus": 8,
      "P": 3,
      "P_minus": 2,
      "F": 0
    },
    "contradictions_found": 3,
    "total_sources_checked": 156,
    "avg_sources_per_signal": 3.5
  },

  "signals": [
    {
      "signal_id": "SIG-2026-0114-001",
      "title": "신호 제목",

      "cross_validation": {
        "score": 85,
        "grade": "CV+",
        "pSRT_adjustment": "+10",

        "claims_validated": [
          {
            "claim_id": "C001",
            "claim_text": "Samsung이 새로운 AI 칩 발표",
            "consistency": {
              "score": 100,
              "type": "FULL_CONFIRMATION",
              "confirming_sources": 3,
              "contradicting_sources": 0
            },
            "independent_sources": [
              {
                "url": "https://reuters.com/...",
                "domain": "reuters.com",
                "tier": 2,
                "excerpt": "Samsung Electronics unveiled...",
                "verdict": "CONFIRMS"
              },
              {
                "url": "https://bloomberg.com/...",
                "domain": "bloomberg.com",
                "tier": 2,
                "excerpt": "The South Korean tech giant...",
                "verdict": "CONFIRMS"
              }
            ]
          },
          {
            "claim_id": "C002",
            "claim_text": "성능 50% 향상",
            "consistency": {
              "score": 30,
              "type": "CONTRADICTION",
              "confirming_sources": 1,
              "contradicting_sources": 2
            },
            "independent_sources": [
              {
                "url": "https://techcrunch.com/...",
                "domain": "techcrunch.com",
                "tier": 2,
                "excerpt": "Performance improved by 35%...",
                "verdict": "CONTRADICTS",
                "contradiction_type": "NUMERICAL_CONTRADICTION"
              }
            ],
            "contradiction_flag": {
              "type": "NUMERICAL_CONTRADICTION",
              "severity": "high",
              "original_value": "50%",
              "contradicting_value": "35%",
              "recommended_action": "정확한 수치 확인 필요"
            }
          }
        ],

        "source_diversity": {
          "score": 80,
          "unique_domains": 5,
          "tier_distribution": {
            "tier_1": 1,
            "tier_2": 3,
            "tier_3": 1
          },
          "language_diversity": ["en", "ko"]
        }
      }
    }
  ],

  "metadata": {
    "total_searches": 89,
    "total_fetches": 156,
    "processing_time_ms": 45000,
    "model_used": "sonnet"
  }
}
```

---

## 실행 프로세스

```
1. 입력 데이터 로드
   ├── groundedness-scores-{date}.json
   └── structured-signals-{date}.json

2. 검증 대상 선별
   ├── Groundedness 점수 < 80인 신호
   ├── 플래그가 있는 신호
   └── 고중요도 신호 (significance >= 4)

3. 각 신호에 대해 반복
   ├── Step 1: Key Claim Extraction
   │
   ├── Step 2: Independent Source Search
   │   ├── WebSearch로 독립 소스 검색
   │   ├── 원본 도메인 제외 필터링
   │   └── WebFetch로 콘텐츠 추출
   │
   ├── Step 3: Consistency Scoring
   │   ├── 각 소스와 주장 비교
   │   ├── 확인/상충/중립 분류
   │   └── 일관성 점수 계산
   │
   └── Step 4: Cross-Validation Score
       ├── 종합 점수 계산
       ├── 상충 플래그 생성
       └── pSRT 조정값 결정

4. 결과 저장
   └── cross-validation-{date}.json
```

---

## 검색 전략

### 쿼리 생성 규칙

```python
def generate_search_queries(claim: KeyClaim) -> list[str]:
    """
    주장에 대한 검색 쿼리를 생성합니다.

    전략:
    1. 핵심 키워드 추출
    2. 엔티티 + 행동/사건 조합
    3. 날짜 범위 제한 (+7일)
    4. 다국어 쿼리 (영어/한국어)
    """
    queries = []

    # 핵심 키워드 추출
    keywords = extract_keywords(claim.text)
    entities = extract_entities(claim.text)

    # 기본 쿼리
    base_query = " ".join(keywords[:3])
    queries.append(base_query)

    # 엔티티 + 키워드 조합
    for entity in entities[:2]:
        queries.append(f"{entity} {keywords[0]}")

    # 영어 번역 쿼리 (한국어 주장인 경우)
    if is_korean(claim.text):
        english_query = translate_to_english(base_query)
        queries.append(english_query)

    return queries[:5]  # 최대 5개 쿼리
```

### 소스 필터링 규칙

```yaml
INCLUDE:
  - Tier 1-3 소스
  - 7일 이내 발행
  - 원본과 다른 도메인
  - 실제 콘텐츠 있음

EXCLUDE:
  - 원본 소스 도메인
  - 원본을 인용만 한 소스
  - Tier 4 이하 소스
  - 30일 이상 오래된 소스
  - 페이월/접근 불가
```

---

## 워크플로우 내 위치

```
Phase 2: Analysis
├── @signal-classifier (5단계)
├── @groundedness-verifier (5.3단계)
├── @cross-validator (5.5단계) ◀── 현재 에이전트 [NEW]
├── @confidence-evaluator (5.7단계)
├── @hallucination-detector (5.9단계)
├── @impact-analyzer (6단계)
└── @priority-ranker (7단계)
```

---

## 다음 에이전트 연계

- **@confidence-evaluator**: CV Score를 Source pSRT의 cross_validation 항목에 반영
- **@hallucination-detector**: 상충 플래그를 종합 검증에 활용
- **@calibration-engine**: 검증 결과를 역사적 보정에 활용

---

## 품질 기준

- **검색 효율**: 주장당 평균 3개 이상 독립 소스
- **검증률**: 고중요도 신호 100% 검증
- **상충 감지율**: 95% 이상
- **오탐률**: 15% 미만
