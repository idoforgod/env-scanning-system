# 환경스캐닝 자체 신뢰 평가 척도 설계

## 영감: AlphaFold의 pLDDT

AlphaFold는 단백질 구조 예측의 신뢰도를 측정하기 위해 **pLDDT (predicted Local Distance Difference Test)** 를 개발했습니다:
- 0-100 점수로 각 잔기(residue)의 예측 신뢰도 표시
- 90+ = 매우 높은 신뢰도 (거의 확실)
- 70-90 = 높은 신뢰도 (신뢰할 수 있음)
- 50-70 = 낮은 신뢰도 (주의 필요)
- <50 = 매우 낮은 신뢰도 (불확실)

이를 환경스캐닝에 적용하여 **할루시네이션(잘못된 신호, 과장된 해석)**을 줄이는 자체 신뢰 척도를 설계합니다.

---

## 1. 명칭 정의

### pSRT: predicted Signal Reliability Test
**환경스캐닝 신뢰도 테스트**

```
pSRT = predicted Signal Reliability Test
       (예측된 신호 신뢰도 테스트)
```

pLDDT가 "이 구조 예측이 얼마나 정확한가?"를 측정하듯,
pSRT는 **"이 환경 신호가 얼마나 신뢰할 수 있는가?"**를 측정합니다.

---

## 2. 신뢰도 측정의 4가지 차원

환경스캐닝 워크플로우의 각 단계에서 신뢰도를 측정합니다:

```
┌─────────────────────────────────────────────────────────────────┐
│                    pSRT 4차원 신뢰도 모델                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐     │
│  │  SOURCE  │ → │  SIGNAL  │ → │ ANALYSIS │ → │  REPORT  │     │
│  │   pSRT   │   │   pSRT   │   │   pSRT   │   │   pSRT   │     │
│  │  (소스)  │   │  (신호)  │   │  (분석)  │   │  (보고서) │     │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘     │
│       ↓              ↓              ↓              ↓            │
│    신뢰도 A       신뢰도 B       신뢰도 C       신뢰도 D         │
│                                                                 │
│  ════════════════════════════════════════════════════════════  │
│                           ↓                                     │
│                    종합 pSRT 점수                               │
│                    (0-100점)                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 차원별 상세 설계

### 3.1 Source pSRT (소스 신뢰도) - Phase 1

**"이 정보 출처를 얼마나 신뢰할 수 있는가?"**

| 지표 | 가중치 | 측정 방법 |
|------|--------|----------|
| **출처 권위성** | 30% | Tier 등급 (1=100, 2=75, 3=50, 4=25) |
| **검증 가능성** | 25% | 원본 링크 존재, 인용 추적 가능 여부 |
| **역사적 정확성** | 25% | 해당 소스의 과거 신호 정확도 |
| **교차 검증** | 20% | 다른 소스에서 동일 정보 확인 여부 |

**계산 공식:**
```
Source_pSRT = (Authority × 0.30) + (Verifiability × 0.25) +
              (Historical_Accuracy × 0.25) + (Cross_Validation × 0.20)
```

**점수 해석:**
- 90-100: Tier 1 학술/정부 소스, 완전 검증 가능
- 70-89: Tier 2 주요 언론, 대부분 검증 가능
- 50-69: Tier 3 전문 매체, 부분 검증
- 30-49: Tier 4 블로그/개인, 검증 어려움
- 0-29: 출처 불명, 검증 불가

---

### 3.2 Signal pSRT (신호 신뢰도) - Phase 1-2

**"이 신호가 실제 변화의 징후인가, 아니면 노이즈/할루시네이션인가?"**

| 지표 | 가중치 | 측정 방법 |
|------|--------|----------|
| **구체성** | 25% | 날짜, 수치, 행위자 등 구체적 정보 포함 여부 |
| **신선도** | 20% | 발행일 기준 최신성 (24시간 내 = 100) |
| **독립성** | 20% | 다른 신호와 독립적 (재탕 아님) |
| **측정 가능성** | 20% | 향후 추적/검증 가능한 지표 포함 |
| **패턴 일치** | 15% | 기존 트렌드/패턴과의 일관성 |

**계산 공식:**
```
Signal_pSRT = (Specificity × 0.25) + (Freshness × 0.20) +
              (Independence × 0.20) + (Measurability × 0.20) +
              (Pattern_Fit × 0.15)
```

**할루시네이션 탐지 플래그:**
```
IF Signal_pSRT < 50:
    FLAG: "LOW_CONFIDENCE - 추가 검증 필요"
IF Specificity < 30:
    FLAG: "VAGUE - 구체성 부족, 할루시네이션 가능성"
IF Independence < 30:
    FLAG: "DUPLICATE_RISK - 재탕 가능성"
```

---

### 3.3 Analysis pSRT (분석 신뢰도) - Phase 2

**"이 분류/영향도/우선순위 분석이 얼마나 정확한가?"**

| 지표 | 가중치 | 측정 방법 |
|------|--------|----------|
| **분류 명확성** | 25% | STEEPS 카테고리 할당의 명확성 |
| **영향도 근거** | 30% | Futures Wheel 분석의 논리적 근거 |
| **우선순위 일관성** | 25% | 4차원 점수의 내부 일관성 |
| **비교 검증** | 20% | 유사 과거 신호와의 비교 적합성 |

**계산 공식:**
```
Analysis_pSRT = (Classification_Clarity × 0.25) + (Impact_Evidence × 0.30) +
                (Priority_Consistency × 0.25) + (Comparative_Validation × 0.20)
```

**과대 해석 탐지:**
```
IF Impact_Evidence < 40 AND Significance >= 4:
    FLAG: "OVERESTIMATION - 근거 대비 중요도 과대평가 가능"
IF Classification_Clarity < 50:
    FLAG: "AMBIGUOUS_CATEGORY - 분류 불명확"
```

---

### 3.4 Report pSRT (보고서 신뢰도) - Phase 3

**"이 최종 보고서의 전체적 신뢰성은 어느 정도인가?"**

| 지표 | 가중치 | 측정 방법 |
|------|--------|----------|
| **신호 품질 평균** | 35% | 포함된 신호들의 평균 Signal_pSRT |
| **소스 다양성** | 20% | 사용된 소스의 다양성 (Tier, 지역, 유형) |
| **내부 일관성** | 25% | 신호 간 상호 모순 여부 |
| **커버리지 균형** | 20% | STEEPS 6개 카테고리 균형 |

**계산 공식:**
```
Report_pSRT = (Avg_Signal_pSRT × 0.35) + (Source_Diversity × 0.20) +
              (Internal_Consistency × 0.25) + (Coverage_Balance × 0.20)
```

---

## 4. 종합 pSRT 점수 (Overall pSRT)

### 4.1 가중 평균 계산

```
Overall_pSRT = (Source_pSRT × 0.20) + (Signal_pSRT × 0.35) +
               (Analysis_pSRT × 0.25) + (Report_pSRT × 0.20)
```

**가중치 근거:**
- Signal_pSRT (35%): 신호 자체의 신뢰도가 가장 중요
- Analysis_pSRT (25%): 분석의 정확성이 의사결정에 영향
- Source_pSRT (20%): 소스 품질은 기본 전제
- Report_pSRT (20%): 최종 산출물의 종합 품질

### 4.2 신뢰도 등급 체계

| 점수 | 등급 | 의미 | 권장 조치 |
|------|------|------|----------|
| **90-100** | A+ (Very High) | 매우 높은 신뢰도 | 즉시 활용 가능 |
| **80-89** | A (High) | 높은 신뢰도 | 활용 권장 |
| **70-79** | B (Good) | 양호한 신뢰도 | 활용 가능, 모니터링 권장 |
| **60-69** | C (Moderate) | 보통 신뢰도 | 추가 검증 후 활용 |
| **50-59** | D (Low) | 낮은 신뢰도 | 교차 검증 필수 |
| **40-49** | E (Very Low) | 매우 낮은 신뢰도 | 참고용으로만 사용 |
| **0-39** | F (Unreliable) | 신뢰 불가 | 제외 권고 |

---

## 5. 할루시네이션 탐지 시스템

### 5.1 할루시네이션 유형 정의

| 유형 | 설명 | 탐지 지표 |
|------|------|----------|
| **Source Hallucination** | 존재하지 않는 소스 인용 | URL 404, 검증 불가 |
| **Signal Fabrication** | 없는 신호 생성 | 원문에 없는 내용, 재탕 |
| **Overinterpretation** | 과대 해석 | 근거 없는 높은 significance |
| **False Pattern** | 없는 패턴 발견 | 통계적 유의성 없음 |
| **Temporal Confusion** | 시간 혼동 | 오래된 정보를 새 것으로 |

### 5.2 자동 플래그 시스템

```python
def detect_hallucination(signal):
    flags = []

    # Source Hallucination
    if not verify_url(signal.source_url):
        flags.append({
            "type": "SOURCE_HALLUCINATION",
            "severity": "critical",
            "action": "remove"
        })

    # Signal Fabrication
    if signal.specificity < 30 and signal.independence < 40:
        flags.append({
            "type": "SIGNAL_FABRICATION_RISK",
            "severity": "high",
            "action": "verify"
        })

    # Overinterpretation
    if signal.significance >= 4 and signal.impact_evidence < 40:
        flags.append({
            "type": "OVERINTERPRETATION",
            "severity": "medium",
            "action": "downgrade"
        })

    # Temporal Confusion
    if signal.freshness < 30:
        flags.append({
            "type": "TEMPORAL_CONFUSION",
            "severity": "medium",
            "action": "verify_date"
        })

    return flags
```

---

## 6. pSRT 데이터 구조

### 6.1 신호별 pSRT 기록

```json
{
  "signal_id": "SIG-2026-0112-001",
  "title": "...",
  "pSRT": {
    "overall": 78,
    "grade": "B",
    "breakdown": {
      "source": {
        "score": 85,
        "authority": 90,
        "verifiability": 80,
        "historical_accuracy": 85,
        "cross_validation": 80
      },
      "signal": {
        "score": 75,
        "specificity": 80,
        "freshness": 90,
        "independence": 70,
        "measurability": 65,
        "pattern_fit": 70
      },
      "analysis": {
        "score": 72,
        "classification_clarity": 80,
        "impact_evidence": 65,
        "priority_consistency": 75,
        "comparative_validation": 70
      }
    },
    "flags": [],
    "confidence_level": "good",
    "recommended_action": "use_with_monitoring"
  }
}
```

### 6.2 보고서 pSRT 요약

```json
{
  "report_date": "2026-01-12",
  "report_pSRT": {
    "overall": 74,
    "grade": "B",
    "breakdown": {
      "avg_signal_pSRT": 76,
      "source_diversity": 70,
      "internal_consistency": 78,
      "coverage_balance": 72
    },
    "signal_distribution": {
      "A_grade": 5,
      "B_grade": 18,
      "C_grade": 12,
      "D_grade": 8,
      "E_grade": 3,
      "F_grade": 0
    },
    "hallucination_flags": {
      "total": 4,
      "critical": 0,
      "high": 1,
      "medium": 3
    },
    "reliability_statement": "이 보고서는 양호한 신뢰도(B등급)를 가지며, 대부분의 신호가 검증 가능합니다. 3건의 중간 수준 플래그가 있으며 추가 모니터링을 권장합니다."
  }
}
```

---

## 7. 워크플로우 통합

### 7.1 각 Phase에서 pSRT 계산

```
Phase 1: Research
├── @archive-loader
├── @multi-source-scanner
│   └── Calculate Source_pSRT for each source
├── @dedup-filter
│   └── Calculate Signal_pSRT (independence)
└── [Output: raw signals with Source_pSRT, partial Signal_pSRT]

Phase 2: Planning
├── @signal-classifier
│   └── Calculate Signal_pSRT (specificity, pattern_fit)
├── @impact-analyzer
│   └── Calculate Analysis_pSRT (impact_evidence)
├── @priority-ranker
│   └── Calculate Analysis_pSRT (priority_consistency)
└── [Output: analyzed signals with full pSRT]

Phase 3: Implementation
├── @db-updater
├── @report-generator
│   └── Calculate Report_pSRT
│   └── Calculate Overall_pSRT for each signal
│   └── Generate reliability statement
├── @archive-notifier
└── [Output: report with pSRT summary]
```

### 7.2 새 에이전트: @confidence-evaluator

```
Phase 2.5: Confidence Evaluation (신규)
├── @confidence-evaluator
│   ├── 모든 신호의 pSRT 계산
│   ├── 할루시네이션 플래그 생성
│   ├── 저신뢰 신호 필터링/다운그레이드
│   └── 신뢰도 기반 우선순위 조정
└── [Output: confidence-evaluated signals]
```

---

## 8. 신뢰도 기반 의사결정 임계값

### 8.1 자동 조치 임계값

| 조건 | 자동 조치 |
|------|----------|
| Overall_pSRT < 40 | 보고서에서 제외 |
| Overall_pSRT 40-50 | "참고용" 표시 |
| Overall_pSRT 50-60 | "추가 검증 필요" 표시 |
| Critical flag 존재 | 즉시 검토 요청 |
| Signal_pSRT < Source_pSRT - 30 | 소스 대비 신호 품질 이상 경고 |

### 8.2 보고서 출력 임계값

| 보고서 pSRT | 조치 |
|-------------|------|
| Report_pSRT >= 70 | 자동 승인 가능 |
| Report_pSRT 60-69 | 검토 후 승인 |
| Report_pSRT 50-59 | 수정 권고 |
| Report_pSRT < 50 | 재작성 필요 |

---

## 9. 시각화 방안

### 9.1 신호별 pSRT 표시 (AlphaFold 스타일)

```
신호: "AI 단백질/DNA 설계 생물안보 경고"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
pSRT: ████████████████████░░░░░ 82/100 [A]
      ├─ Source:   ███████████████████░ 90
      ├─ Signal:   ████████████████░░░░ 78
      └─ Analysis: ████████████████░░░░ 75
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Flags: None
Confidence: HIGH - 즉시 활용 가능
```

### 9.2 보고서 신뢰도 대시보드

```
╔═══════════════════════════════════════════════════════╗
║  2026-01-12 환경스캐닝 보고서 신뢰도 대시보드         ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║  Overall pSRT: 74/100  [B - Good]                    ║
║  ████████████████████████████░░░░░░░░░░░             ║
║                                                       ║
║  ┌─────────────────────────────────────────────────┐ ║
║  │ 신호 등급 분포                                   │ ║
║  │ A: ████████ 5                                   │ ║
║  │ B: ████████████████████████████████████ 18     │ ║
║  │ C: ████████████████████████ 12                 │ ║
║  │ D: ████████████████ 8                          │ ║
║  │ E: ██████ 3                                    │ ║
║  │ F: 0                                           │ ║
║  └─────────────────────────────────────────────────┘ ║
║                                                       ║
║  할루시네이션 플래그: 4건 (Critical: 0, High: 1)      ║
║  권장 조치: 활용 가능, 1건 추가 검증 필요            ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
```

---

## 10. 구현 우선순위

### Phase 1: 기본 인프라 (즉시)
1. [ ] pSRT 데이터 구조 정의 (JSON 스키마)
2. [ ] Source_pSRT 계산 로직 구현
3. [ ] Signal_pSRT 계산 로직 구현

### Phase 2: 분석 통합 (1주차)
4. [ ] Analysis_pSRT 계산 로직 구현
5. [ ] @confidence-evaluator 에이전트 생성
6. [ ] 할루시네이션 탐지 시스템 구현

### Phase 3: 보고서 통합 (2주차)
7. [ ] Report_pSRT 계산 로직 구현
8. [ ] 보고서에 pSRT 요약 섹션 추가
9. [ ] 시각화 템플릿 생성

### Phase 4: 피드백 루프 (3주차)
10. [ ] pSRT 기반 자동 필터링
11. [ ] 과거 pSRT 정확도 추적
12. [ ] pSRT 모델 자체 개선 메커니즘

---

## 11. 예상 효과

### 할루시네이션 감소
- 저신뢰 신호 자동 필터링
- 과대 해석 조기 탐지
- 소스 검증 강화

### 의사결정 품질 향상
- 신뢰도 기반 우선순위 조정
- 불확실성 명시적 표현
- 검증 필요 영역 명확화

### 시스템 신뢰성 향상
- 자체 신뢰도 추적
- 시간에 따른 정확도 개선
- 투명한 품질 지표 제공
