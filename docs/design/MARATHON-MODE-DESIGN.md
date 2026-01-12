# Marathon Mode 재설계: 자기개선형 소스 탐색 시스템

## 1. 핵심 목적 재정의

### 기존 목적 (폐기)
- 전체 워크플로우를 3시간 동안 실행

### 새로운 목적
- **Phase 1: Research의 multi-source-scanner 단계를 3시간 동안 실행**
- **목표**: 더 많은 소스를 무작위로 탐색하여 좋은 소스를 발견
- **효과**: 환경스캐닝을 거듭할수록 더 좋은 자료를 찾는 '자기개선' 달성

---

## 2. 자기개선 메커니즘 설계

### 2.1 소스 탐색 전략 (3시간 배분)

```
┌─────────────────────────────────────────────────────────────┐
│                    3시간 마라톤 타임라인                      │
├─────────────────────────────────────────────────────────────┤
│ 0:00-0:30  │ Phase A: 기존 Tier 1 소스 스캔 (30분)         │
│ 0:30-1:30  │ Phase B: 무작위 탐험 스캔 (60분)              │
│ 1:30-2:30  │ Phase C: 링크 추적 & 새 소스 발견 (60분)      │
│ 2:30-3:00  │ Phase D: 발견된 소스 검증 & 평가 (30분)       │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 각 Phase 상세

#### Phase A: 기존 Tier 1 소스 스캔 (30분)
- 목적: 핵심 신뢰 소스에서 기본 신호 수집
- 대상: regular-sources.json의 Tier 1 소스 (약 50개)
- 방법: 빠른 헤드라인 스캔

#### Phase B: 무작위 탐험 스캔 (60분)
- 목적: 새로운 소스 발견을 위한 무작위 탐색
- 방법:
  1. **키워드 변이 검색**: STEEPS 키워드 + 무작위 조합
  2. **지역 확장**: 기존에 없는 국가/언어권 검색
  3. **시간대 확장**: 다른 시간대의 뉴스 소스 탐색
  4. **도메인 탐험**: .edu, .gov, .org 새 사이트 발견

#### Phase C: 링크 추적 & 새 소스 발견 (60분)
- 목적: 발견한 기사에서 인용된 소스 추적
- 방법:
  1. 기사 내 인용 링크 추출
  2. 참고문헌/출처 추적
  3. "관련 기사" 링크 탐색
  4. 새 소스 후보 목록 생성

#### Phase D: 발견된 소스 검증 & 평가 (30분)
- 목적: 새 소스의 품질 평가 및 등록 결정
- 평가 기준:
  1. 업데이트 빈도
  2. 콘텐츠 품질
  3. STEEPS 커버리지
  4. 접근성 (페이월, 언어)

---

## 3. 소스 품질 자동 학습 시스템

### 3.1 소스 성과 추적

```json
{
  "source_performance": {
    "nature.com": {
      "total_scans": 45,
      "signals_found": 23,
      "high_quality_signals": 18,
      "signal_to_scan_ratio": 0.51,
      "average_significance": 4.2,
      "trend": "improving",
      "last_valuable_signal": "2026-01-12"
    }
  }
}
```

### 3.2 동적 우선순위 조정

| 성과 지표 | 조정 방향 |
|-----------|----------|
| signal_to_scan_ratio > 0.5 | 스캔 빈도 증가 |
| signal_to_scan_ratio < 0.1 | 스캔 빈도 감소 |
| average_significance > 4.0 | Tier 승격 검토 |
| 30일간 signal = 0 | 비활성화 검토 |

### 3.3 자기개선 피드백 루프

```
┌────────────────────────────────────────────────────────────┐
│                    자기개선 사이클                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐             │
│   │  스캔   │ ──> │  평가   │ ──> │  학습   │             │
│   └─────────┘     └─────────┘     └─────────┘             │
│        │                               │                   │
│        │         ┌─────────┐           │                   │
│        └──────── │  적용   │ <─────────┘                   │
│                  └─────────┘                               │
│                                                            │
│   - 스캔: 소스에서 신호 수집                               │
│   - 평가: 신호 품질 및 소스 성과 측정                      │
│   - 학습: 성과 기반 소스 점수 조정                         │
│   - 적용: 다음 스캔 시 우선순위 반영                       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 4. 새 소스 발견 전략

### 4.1 탐험 방향

| 탐험 유형 | 방법 | 예시 |
|-----------|------|------|
| **수평 확장** | 동일 분야 다른 소스 | Nature → Science → PNAS |
| **수직 심화** | 전문 분야 소스 | AI 일반 → AI 로보틱스 전문 |
| **지역 확장** | 새 국가/언어권 | 영미권 → 라틴아메리카, 중동 |
| **형식 다양화** | 팟캐스트, 유튜브, 뉴스레터 | 텍스트 → 멀티미디어 |

### 4.2 무작위 탐험 키워드 생성

```python
# 의사 코드
def generate_exploration_keywords():
    steeps_base = ["AI breakthrough", "climate policy", "gen z trends", ...]
    modifiers = ["2026", "emerging", "first time", "unprecedented", ...]
    regions = ["Asia", "Europe", "Latin America", "Africa", "Middle East"]
    languages = ["Korean", "Japanese", "Spanish", "German", "Chinese"]

    # 무작위 조합 생성
    keyword = random.choice(steeps_base) + " " + random.choice(modifiers)
    keyword += " " + random.choice(regions)  # 50% 확률

    return keyword
```

### 4.3 링크 추적 알고리즘

```
기사 A 발견
    │
    ├── 인용된 연구 논문 링크 추출 → 새 학술 소스 후보
    │
    ├── "출처: XXX 보고서" 추적 → 새 싱크탱크/기관 후보
    │
    ├── 관련 기사 링크 → 새 뉴스 소스 후보
    │
    └── 저자 소속 기관 → 새 연구기관 후보
```

---

## 5. 발견된 소스 평가 기준

### 5.1 자동 평가 점수 (0-100)

| 항목 | 가중치 | 평가 방법 |
|------|--------|----------|
| 업데이트 빈도 | 25% | 최근 30일 게시물 수 |
| 콘텐츠 깊이 | 25% | 평균 기사 길이, 인용 수 |
| STEEPS 적합성 | 20% | 키워드 매칭률 |
| 접근성 | 15% | 페이월 여부, 언어 |
| 신뢰도 지표 | 15% | 도메인 유형, 인용 빈도 |

### 5.2 소스 등록 임계값

- **자동 등록**: 점수 70+ → Tier 3로 자동 추가
- **검토 대기**: 점수 50-69 → 후보 목록에 추가, 다음 스캔에서 재평가
- **제외**: 점수 <50 → 무시

---

## 6. 데이터 구조 변경

### 6.1 새로운 파일 구조

```
env-scanning/
├── config/
│   ├── regular-sources.json      # 기존 (유지)
│   ├── discovered-sources.json   # 새로 발견된 소스 후보
│   └── source-performance.json   # 소스별 성과 통계
├── logs/
│   ├── marathon-exploration-{date}.json  # 탐험 로그
│   └── source-discovery-{date}.json      # 발견 소스 상세
```

### 6.2 source-performance.json 구조

```json
{
  "metadata": {
    "last_updated": "2026-01-12",
    "total_sources_tracked": 177,
    "total_marathons_completed": 5
  },
  "sources": {
    "nature.com": {
      "tier": 1,
      "category": "academic",
      "steeps_coverage": ["Technological", "Environmental"],
      "performance": {
        "scans": 45,
        "signals_found": 23,
        "high_quality": 18,
        "ratio": 0.51,
        "avg_significance": 4.2,
        "trend": "stable"
      },
      "history": [
        {"date": "2026-01-10", "signals": 3, "quality": 4.5},
        {"date": "2026-01-11", "signals": 2, "quality": 4.0}
      ]
    }
  },
  "tier_recommendations": {
    "upgrade": ["sciencedaily.com"],
    "downgrade": [],
    "deactivate": []
  }
}
```

### 6.3 discovered-sources.json 구조

```json
{
  "metadata": {
    "last_marathon": "2026-01-12",
    "total_discovered": 45,
    "pending_review": 12,
    "promoted_to_regular": 8
  },
  "candidates": [
    {
      "url": "https://newsite.org",
      "name": "New Site",
      "discovered_date": "2026-01-12",
      "discovered_via": "link_tracking",
      "parent_source": "nature.com",
      "evaluation_score": 72,
      "steeps_category": ["Technological"],
      "status": "pending_review",
      "scan_count": 2,
      "signals_found": 1
    }
  ],
  "rejected": [
    {
      "url": "https://lowquality.com",
      "reason": "low_score",
      "score": 35
    }
  ]
}
```

---

## 7. 워크플로우 수정

### 7.1 기존 워크플로우

```
Phase 1: Research
├── archive-loader
├── multi-source-scanner (일반 스캔)
└── dedup-filter
```

### 7.2 마라톤 모드 워크플로우

```
Phase 1: Research (Marathon Mode - 3시간)
├── archive-loader
├── multi-source-scanner-marathon
│   ├── Phase A: Tier 1 핵심 스캔 (30분)
│   ├── Phase B: 무작위 탐험 스캔 (60분)
│   ├── Phase C: 링크 추적 & 발견 (60분)
│   └── Phase D: 소스 평가 & 등록 (30분)
├── source-performance-updater (NEW)
└── dedup-filter
```

### 7.3 새로운 에이전트

| 에이전트 | 역할 |
|----------|------|
| `@exploration-scanner` | Phase B: 무작위 탐험 스캔 |
| `@link-tracker` | Phase C: 링크 추적 & 새 소스 발견 |
| `@source-evaluator` | Phase D: 소스 품질 평가 |
| `@performance-updater` | 소스 성과 통계 갱신 |

---

## 8. 자기개선 지표

### 8.1 측정 지표

| 지표 | 설명 | 목표 |
|------|------|------|
| **소스 발견률** | 마라톤당 새 소스 발견 수 | 10+개/회 |
| **소스 승격률** | 발견 → 정규 소스 전환 비율 | 20%+ |
| **신호 품질 향상** | 평균 significance 점수 추세 | 상승 |
| **커버리지 확장** | STEEPS 약점 영역 개선 | Spiritual 3→4 |

### 8.2 장기 목표

```
스캔 1회차: 177개 소스 → 신호 평균 significance 3.8
스캔 5회차: 200개 소스 → 신호 평균 significance 4.0
스캔 10회차: 230개 소스 → 신호 평균 significance 4.2
스캔 20회차: 280개 소스 → 신호 평균 significance 4.5
```

---

## 9. 구현 우선순위

### Phase 1: 기본 인프라 (즉시)
1. [ ] source-performance.json 구조 생성
2. [ ] discovered-sources.json 구조 생성
3. [ ] multi-source-scanner 에이전트 수정

### Phase 2: 탐험 기능 (1주차)
4. [ ] @exploration-scanner 에이전트 생성
5. [ ] 무작위 키워드 생성 로직 구현
6. [ ] 링크 추적 기능 구현

### Phase 3: 평가 시스템 (2주차)
7. [ ] @source-evaluator 에이전트 생성
8. [ ] 자동 평가 점수 산출 로직
9. [ ] 소스 승격/강등 자동화

### Phase 4: 피드백 루프 (3주차)
10. [ ] @performance-updater 에이전트 생성
11. [ ] 성과 기반 우선순위 조정
12. [ ] 자기개선 대시보드

---

## 10. 예상 효과

### 단기 (1개월)
- 소스 수: 177개 → 200개 (+13%)
- STEEPS Spiritual 커버리지: 3점 → 4점

### 중기 (3개월)
- 소스 수: 200개 → 250개 (+40%)
- 평균 신호 품질: 3.8 → 4.2 (+10%)
- 비영어권 소스 비율: 15% → 30%

### 장기 (6개월)
- 소스 수: 250개 → 350개 (+100%)
- 자동 발견 비율: 새 신호의 30%가 자동 발견 소스에서 유래
- 업계 최고 수준의 환경스캐닝 소스 네트워크 구축
