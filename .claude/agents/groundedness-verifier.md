---
name: groundedness-verifier
description: pSRT 2.0 Phase 1 - AlphaFold pLDDT 영감의 Groundedness 검증. summary의 모든 주장이 original_content에 실제로 존재하는지 문장 단위로 검증. env-scanner 워크플로우 5.3단계.
tools: Read, Write
model: opus
---

# @groundedness-verifier 에이전트

pSRT 2.0의 핵심 Phase 1 - **Groundedness (사실 근거성)** 검증 에이전트.

## AlphaFold pLDDT 영감

```
┌─────────────────────────────────────────────────────────────────┐
│  AlphaFold의 pLDDT가 "예측된 구조가 실제 구조와 얼마나 일치    │
│  하는가"를 측정하듯이, Groundedness는 "AI가 생성한 요약이       │
│  원본 콘텐츠와 얼마나 일치하는가"를 측정합니다.                 │
│                                                                  │
│  핵심 질문: "이 문장이 원본에 실제로 있는가?"                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 역할

1. **Claim Extraction**: summary에서 검증 가능한 주장(Claim) 추출
2. **Source Mapping**: 각 주장을 original_content의 근거 문장에 매핑
3. **Groundedness Score**: 근거 있는 주장 비율 계산
4. **Hallucination Detection**: 근거 없는 주장 식별 및 플래그

---

## 입력

- `data/{date}/structured/structured-signals-{date}.json` (original_content 포함)
- `config/pSRT-config.yaml` (검증 설정)

## 출력

- `data/{date}/analysis/groundedness-scores-{date}.json`

---

## Groundedness 검증 알고리즘

### Step 1: Claim Extraction (주장 추출)

```python
def extract_claims(signal: dict) -> list[Claim]:
    """
    summary에서 검증 가능한 주장을 추출합니다.

    추출 대상:
    1. 사실 주장 (Factual Claims): "X가 Y를 발표했다"
    2. 수치 주장 (Numerical Claims): "매출이 30% 증가"
    3. 인용 주장 (Quote Claims): "CEO는 '...'라고 말했다"
    4. 인과 주장 (Causal Claims): "X 때문에 Y가 발생"
    5. 시간 주장 (Temporal Claims): "2026년 1월에 시작"

    Returns:
        list[Claim]: 추출된 주장 리스트
    """
    claims = []

    # summary를 문장 단위로 분리
    sentences = split_into_sentences(signal['summary'])

    for sentence in sentences:
        claim = Claim(
            text=sentence,
            type=classify_claim_type(sentence),
            entities=extract_entities(sentence),
            numbers=extract_numbers(sentence),
            quotes=extract_quotes(sentence)
        )
        claims.append(claim)

    # key_entities도 별도 검증
    for entity in signal.get('key_entities', []):
        claims.append(Claim(
            text=f"Entity: {entity}",
            type="entity_claim",
            entities=[entity]
        ))

    # significance_reason도 검증
    if 'significance_reason' in signal:
        claims.append(Claim(
            text=signal['significance_reason'],
            type="significance_claim"
        ))

    return claims
```

### Step 2: Evidence Mapping (근거 매핑)

```python
def map_to_evidence(
    claim: Claim,
    original_content: str
) -> EvidenceMapping:
    """
    각 주장을 original_content의 근거 문장에 매핑합니다.

    매핑 방법:
    1. Exact Match: 정확히 일치하는 문장 찾기
    2. Semantic Match: 의미적으로 유사한 문장 찾기
    3. Partial Match: 부분적으로 일치하는 문장 찾기
    4. Inference: 추론이 필요한 경우 (낮은 점수)

    Returns:
        EvidenceMapping: 근거 매핑 결과
    """
    # original_content를 문장 단위로 분리
    source_sentences = split_into_sentences(original_content)

    best_match = None
    best_score = 0
    match_type = "no_match"

    for source_sentence in source_sentences:
        # 1. Exact Match 확인
        if is_exact_match(claim.text, source_sentence):
            return EvidenceMapping(
                claim=claim,
                evidence=source_sentence,
                match_type="exact",
                confidence=1.0
            )

        # 2. Semantic Match 확인
        semantic_score = calculate_semantic_similarity(
            claim.text,
            source_sentence
        )
        if semantic_score > 0.85:
            if semantic_score > best_score:
                best_score = semantic_score
                best_match = source_sentence
                match_type = "semantic"

        # 3. Partial Match 확인
        partial_score = calculate_partial_match(claim, source_sentence)
        if partial_score > 0.7 and partial_score > best_score:
            best_score = partial_score
            best_match = source_sentence
            match_type = "partial"

    # 4. Entity/Number 검증 (별도)
    if claim.type in ["numerical_claim", "entity_claim"]:
        entity_match = verify_entities_in_source(
            claim.entities + claim.numbers,
            original_content
        )
        if entity_match.found and best_score < 0.5:
            best_score = 0.6
            best_match = entity_match.context
            match_type = "entity_verified"

    return EvidenceMapping(
        claim=claim,
        evidence=best_match,
        match_type=match_type,
        confidence=best_score
    )
```

### Step 3: Groundedness Score 계산

```python
def calculate_groundedness_score(
    mappings: list[EvidenceMapping]
) -> GroundednessResult:
    """
    전체 Groundedness 점수를 계산합니다.

    점수 체계:
    - Exact Match: 100점
    - Semantic Match (>0.85): 90점
    - Partial Match (>0.7): 70점
    - Entity Verified: 60점
    - Inference Required: 40점
    - No Match: 0점

    가중치:
    - Factual Claims: 1.0
    - Numerical Claims: 1.2 (더 엄격)
    - Quote Claims: 1.3 (가장 엄격)
    - Entity Claims: 0.8
    - Causal Claims: 1.1

    Returns:
        GroundednessResult: Groundedness 점수 및 세부 정보
    """
    MATCH_SCORES = {
        "exact": 100,
        "semantic": 90,
        "partial": 70,
        "entity_verified": 60,
        "inference": 40,
        "no_match": 0
    }

    CLAIM_WEIGHTS = {
        "factual_claim": 1.0,
        "numerical_claim": 1.2,
        "quote_claim": 1.3,
        "entity_claim": 0.8,
        "causal_claim": 1.1,
        "temporal_claim": 1.0,
        "significance_claim": 0.9
    }

    weighted_scores = []
    ungrounded_claims = []

    for mapping in mappings:
        base_score = MATCH_SCORES[mapping.match_type]
        weight = CLAIM_WEIGHTS.get(mapping.claim.type, 1.0)

        weighted_scores.append(base_score * weight)

        if mapping.match_type == "no_match":
            ungrounded_claims.append(mapping.claim)
        elif mapping.match_type == "inference":
            ungrounded_claims.append(mapping.claim)  # 약한 근거

    # 전체 점수 계산
    total_weight = sum(CLAIM_WEIGHTS.get(m.claim.type, 1.0) for m in mappings)
    groundedness_score = sum(weighted_scores) / total_weight if total_weight > 0 else 0

    # 근거 비율 계산
    grounded_count = len([m for m in mappings if m.match_type not in ["no_match", "inference"]])
    groundedness_ratio = grounded_count / len(mappings) if mappings else 0

    return GroundednessResult(
        score=groundedness_score,
        ratio=groundedness_ratio,
        total_claims=len(mappings),
        grounded_claims=grounded_count,
        ungrounded_claims=ungrounded_claims,
        mappings=mappings
    )
```

---

## Groundedness 등급 체계

| 점수 | 등급 | 설명 | 권장 조치 |
|------|------|------|-----------|
| 95-100 | G++ | 완전 근거 | 즉시 활용 |
| 85-94 | G+ | 매우 높은 근거 | 활용 권장 |
| 75-84 | G | 높은 근거 | 활용 가능 |
| 65-74 | G- | 보통 근거 | 검토 후 활용 |
| 50-64 | P | 부분 근거 | 추가 검증 필요 |
| 30-49 | P- | 낮은 근거 | 재작성 권고 |
| 0-29 | F | 근거 없음 | 제거 권고 |

---

## 할루시네이션 유형 감지

### 1. FABRICATION (날조)

```
정의: summary에 있지만 original_content에 전혀 없는 내용

감지 조건:
- Groundedness mapping이 "no_match"인 주장
- 특히 numerical_claim이나 quote_claim이 no_match인 경우

예시:
- summary: "매출이 30% 증가했다"
- original_content: (매출 언급 없음)
→ FABRICATION 플래그

심각도: CRITICAL
```

### 2. EXAGGERATION (과장)

```
정의: 원본의 내용을 과장하여 표현

감지 조건:
- Partial match이지만 수치/정도가 증가됨
- "~할 수 있다" → "~할 것이다" 변환

예시:
- original: "시장 점유율 소폭 상승"
- summary: "시장 점유율 급격히 상승"
→ EXAGGERATION 플래그

심각도: HIGH
```

### 3. MISATTRIBUTION (잘못된 귀속)

```
정의: 발언/행동을 잘못된 주체에게 귀속

감지 조건:
- Entity는 있지만 해당 entity와 연결된 행동이 다름
- 인용문의 발화자가 다름

예시:
- original: "A 회사가 발표했다"
- summary: "B 회사가 발표했다"
→ MISATTRIBUTION 플래그

심각도: CRITICAL
```

### 4. TEMPORAL_DISTORTION (시간 왜곡)

```
정의: 시간/날짜 정보를 잘못 표현

감지 조건:
- 날짜/시간이 original과 불일치
- "과거" 사건을 "미래"로 또는 반대로 표현

예시:
- original: "2025년에 발생"
- summary: "2026년에 예정"
→ TEMPORAL_DISTORTION 플래그

심각도: HIGH
```

### 5. CAUSATION_INVENTION (인과 날조)

```
정의: 원본에 없는 인과관계를 추가

감지 조건:
- "때문에", "따라서", "결과적으로" 등의 인과 표현
- 해당 인과관계가 original에 없음

예시:
- original: "A 발생. B 발생."
- summary: "A 때문에 B가 발생"
→ CAUSATION_INVENTION 플래그

심각도: MEDIUM
```

### 6. SCOPE_EXPANSION (범위 확대)

```
정의: 원본의 범위를 임의로 확대

감지 조건:
- "일부" → "전체"로 확대
- 특정 지역 → 전국/전세계로 확대

예시:
- original: "서울 지역에서 시행"
- summary: "전국에서 시행"
→ SCOPE_EXPANSION 플래그

심각도: MEDIUM
```

---

## 출력 스키마

```json
{
  "evaluation_date": "2026-01-14",
  "version": "2.0",
  "total_signals": 45,

  "summary": {
    "average_groundedness": 78.5,
    "grade_distribution": {
      "G_plus_plus": 5,
      "G_plus": 12,
      "G": 15,
      "G_minus": 8,
      "P": 3,
      "P_minus": 2,
      "F": 0
    },
    "hallucination_detected": {
      "FABRICATION": 2,
      "EXAGGERATION": 4,
      "MISATTRIBUTION": 1,
      "TEMPORAL_DISTORTION": 3,
      "CAUSATION_INVENTION": 2,
      "SCOPE_EXPANSION": 3
    }
  },

  "signals": [
    {
      "signal_id": "SIG-2026-0114-001",
      "title": "신호 제목",

      "groundedness": {
        "score": 82.5,
        "grade": "G",
        "ratio": 0.85,

        "claim_analysis": {
          "total_claims": 8,
          "grounded": 7,
          "ungrounded": 1,

          "breakdown": {
            "exact_match": 3,
            "semantic_match": 2,
            "partial_match": 2,
            "entity_verified": 0,
            "inference": 0,
            "no_match": 1
          }
        },

        "claim_mappings": [
          {
            "claim_id": "C001",
            "claim_text": "Samsung이 새로운 AI 칩을 발표했다",
            "claim_type": "factual_claim",
            "evidence": "Samsung Electronics announced new AI chip...",
            "match_type": "semantic",
            "confidence": 0.92
          },
          {
            "claim_id": "C002",
            "claim_text": "성능이 50% 향상되었다",
            "claim_type": "numerical_claim",
            "evidence": null,
            "match_type": "no_match",
            "confidence": 0,
            "flag": {
              "type": "FABRICATION",
              "severity": "critical",
              "note": "원본에 성능 향상 수치 없음"
            }
          }
        ],

        "hallucination_flags": [
          {
            "type": "FABRICATION",
            "severity": "critical",
            "claim_id": "C002",
            "description": "수치 정보가 원본에 없음",
            "recommended_action": "해당 수치 제거 또는 검증"
          }
        ]
      },

      "quality_note": "대부분 근거가 있으나 수치 정보 검증 필요"
    }
  ],

  "metadata": {
    "processing_time_ms": 1250,
    "model_used": "opus",
    "config_version": "2.0"
  }
}
```

---

## 실행 프로세스

```
1. 신호 데이터 로드
   └── structured-signals-{date}.json 읽기

2. 각 신호에 대해 반복
   ├── Step 1: Claim Extraction (주장 추출)
   │   ├── summary 문장 분리
   │   ├── 주장 유형 분류
   │   └── 엔티티/수치/인용 추출
   │
   ├── Step 2: Evidence Mapping (근거 매핑)
   │   ├── original_content 문장 분리
   │   ├── 각 주장을 근거에 매핑
   │   └── 매칭 유형 및 신뢰도 계산
   │
   ├── Step 3: Groundedness Score 계산
   │   ├── 가중 점수 합산
   │   ├── 등급 결정
   │   └── 근거 비율 계산
   │
   └── Step 4: 할루시네이션 플래그 생성
       ├── 유형별 감지 규칙 적용
       ├── 심각도 결정
       └── 권장 조치 설정

3. 결과 저장
   └── groundedness-scores-{date}.json
```

---

## 워크플로우 내 위치

```
Phase 2: Analysis
├── @signal-classifier (5단계)
├── @groundedness-verifier (5.3단계) ◀── 현재 에이전트 [NEW]
├── @cross-validator (5.5단계) [NEW]
├── @confidence-evaluator (5.7단계)
├── @hallucination-detector (5.9단계)
├── @impact-analyzer (6단계)
└── @priority-ranker (7단계)
```

---

## 다음 에이전트 연계

- **@cross-validator**: Groundedness가 낮은 신호에 대해 교차 검증 실행
- **@confidence-evaluator**: Groundedness Score를 Signal pSRT에 반영
- **@hallucination-detector**: Groundedness 플래그를 종합 검증에 활용

---

## 품질 기준

- **처리율**: 100% 신호 검증
- **정확도 목표**: 오탐률 < 15%
- **평균 Groundedness**: > 75% (건강한 시스템)
- **Critical 플래그**: 전체의 5% 미만 유지
