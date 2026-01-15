---
description: 월간 환경스캐닝 종합 보고서 생성 (주간 보고서 통합 + 심층 리서치)
allowed-tools: Read, Write, Glob, Grep, Bash, Task, WebSearch, WebFetch
argument-hint: [--month <YYYY-MM> | --current]
---

# 월간 환경스캐닝 종합 보고서 생성

오늘 날짜: !`date +%Y-%m-%d`
현재 월: !`date +%Y-%m`
옵션: $ARGUMENTS

---

## 1. 옵션 해석

```yaml
옵션 처리:
  --current: 현재 월 보고서 생성 (기본값)
  --month YYYY-MM: 특정 월 보고서 생성 (예: 2026-01)
```

---

## 2. 워크플로우 (17단계)

### Phase 1: 데이터 수집 (5단계)

```yaml
Step 1-1: 대상 월 결정
  - 옵션에 따라 대상 월 설정
  - 해당 월의 시작일/종료일 계산

Step 1-2: 주간 보고서 검색
  - Glob: data/consolidated/weekly/YYYY-W*/
  - 해당 월에 속하는 주차 필터링 (4주)

Step 1-3: 일일 structured-signals 검색
  - Glob: data/YYYY/MM/*/structured/structured-signals-*.json
  - 해당 월의 모든 일일 데이터

Step 1-4: 주간 요약 통합
  - 각 week-summary.json 읽기
  - 주차별 신호 수, 카테고리 분포 집계

Step 1-5: 월간 통계 집계
  - 총 신호 수 합산
  - 카테고리별 누적 분포
  - 주차별 트렌드 비교
```

### Phase 2: 환경스캐닝 심층 분석 (5단계)

```yaml
Step 2-1: 신호 품질 분석
  - pSRT 점수 분포 분석
  - 고신뢰도 신호 (80+) 목록화
  - 저신뢰도 신호 원인 분석
  - 소스별 평균 품질 비교

Step 2-2: 트렌드 진화 분석
  - 주차별 키워드 변화 추적
  - 상승/하락 트렌드 식별
  - 신규 vs 지속 신호 분류
  - 트렌드 가속/감속 패턴

Step 2-3: 약한 신호(Weak Signals) 심층 분석
  - 저빈도 고영향 신호 식별
  - 단일 소스 신호 모니터링 대상
  - 신규 부상 주제 탐지
  - 교차 카테고리 연결점

Step 2-4: 소스 커버리지 분석
  - STEEPS 카테고리별 소스 분포
  - 지역별/언어별 커버리지 갭
  - 소스 다양성 지수
  - 누락된 관점 식별

Step 2-5: 모니터링 권고 도출
  - 강화 모니터링 대상 키워드
  - 추가 소스 발굴 영역
  - 스캐닝 품질 개선 제안
```

### Phase 2.5: 심층 리서치 (3단계) - NEW

```yaml
Step 2.5-1: 핵심 이슈 추출
  목적: 4주간 신호에서 심층 분석 대상 이슈 선정

  작업:
    - 4주간 weekly-consolidated-report.md 분석
    - 반복 등장 주제 클러스터링
    - 가중치 적용: 빈도(30%) × 중요도(40%) × 신규성(20%) × 교차성(10%)
    - 상위 3-5개 핵심 이슈 선정

  출력:
    - 핵심 이슈 목록 (issue_id, title, signal_count, weeks_appeared)
    - 각 이슈별 관련 신호 ID 목록

Step 2.5-2: 심층 리서치 수행
  목적: 각 이슈에 대한 박사급 다차원 리서치

  작업:
    - Task @deep-research-analyst 호출
    - 이슈별 다차원 리서치 수행:
      • 학술적 관점 (Academic): 최신 연구, 이론, 전문가 견해
      • 정책적 관점 (Policy): 규제 현황, 정책 동향, 국제 협력
      • 산업적 관점 (Industry): 시장 현황, 기업 동향, 투자 흐름
    - 인과관계 분석:
      • 근본 원인 (Root Causes)
      • 동인 (Drivers) / 억제요인 (Inhibitors)
      • 상호작용 구조 및 피드백 루프
    - 불확실성 식별:
      • 주요 불확실성 요인
      • 모니터링 지표

  출력:
    - 이슈별 심층 리서치 보고서 (issue-N-[이슈명].md)

Step 2.5-3: 리서치 결과 통합
  목적: 개별 리서치 종합 및 전략 시스템 연계 데이터 생성

  작업:
    - 개별 이슈 리서치 결과 병합
    - 교차 이슈 연결점 식별
    - 전체 관통 주제 도출
    - 종합 불확실성 목록 정리

  출력:
    - research-synthesis.json (전략적 분석 시스템 연계용)
```

### Phase 3: 보고서 생성 (4단계)

```yaml
Step 3-1: 폴더 구조 생성
  - mkdir -p data/consolidated/monthly/YYYY-MM/
  - mkdir -p data/consolidated/monthly/YYYY-MM/deep-research/

Step 3-2: 월간 요약 JSON 생성
  - month-summary.json
  - 상세 통계, 주차별 비교, 메타 분석, 심층 리서치 요약

Step 3-3: 월간 종합 보고서 생성
  - monthly-consolidated-report.md
  - Executive Summary 포함
  - 10개 섹션 (심층 리서치 요약 포함)

Step 3-4: 완료 확인
  - 파일 생성 검증
  - 결과 요약 출력
```

---

## 3. 출력 구조

```
data/consolidated/monthly/YYYY-MM/
├── month-summary.json              # 월간 요약 데이터
├── monthly-consolidated-report.md  # 월간 종합 보고서 (10개 섹션)
├── weekly-comparison.json          # 주차별 비교 데이터
├── trend-analysis.json             # 트렌드 분석 데이터
│
└── deep-research/                  # 심층 리서치 (NEW)
    ├── issue-1-[이슈명].md         # 개별 이슈 리서치 보고서
    ├── issue-2-[이슈명].md
    ├── issue-3-[이슈명].md
    └── research-synthesis.json     # 전략 시스템 연계용 종합
```

---

## 4. 월간 종합 보고서 템플릿

```markdown
# 월간 환경스캐닝 종합 보고서
## YYYY년 M월

> 생성: `/env-scan:consolidate-monthly`
> 생성일: YYYY-MM-DD
> 버전: v3.0 (심층 리서치 포함)

---

## 1. Executive Summary
- 월간 핵심 발견 (3-5개)
- 주요 수치 요약
- 모니터링 강화 필요 영역
- 심층 리서치 핵심 인사이트

## 2. 월간 개요
- 기간, 총 신호 수, 주차별 분포
- 데이터 소스 현황
- 스캔 품질 지표 (pSRT 분포)

## 3. 주차별 동향
- 각 주차 핵심 요약
- 주간 변화 추이
- 특이 사항

## 4. STEEPS 카테고리 분석
- 카테고리별 월간 동향
- 카테고리 간 교차 패턴
- 불균형 영역 식별

## 5. 트렌드 진화
- 월간 Top 키워드 변화
- 상승/하락 트렌드
- 신규 부상 주제

## 6. 약한 신호 탐지
- 저빈도 고영향 신호 목록
- 신규 발견 주제
- 지속 모니터링 대상

## 7. 소스 품질 및 커버리지
- 소스별 신호 품질
- 지역/언어 커버리지
- 개선 필요 영역

## 8. 모니터링 권고
- 강화 모니터링 키워드
- 추가 소스 발굴 영역
- 스캐닝 프로세스 개선

## 9. 심층 리서치 요약 (NEW)
- 핵심 이슈 3-5개 개요
- 각 이슈별 핵심 발견 (Key Findings)
- 인과관계 요약
- 주요 불확실성 종합
- 상세 리서치 링크

## 10. 부록
- 주차별 상세 통계
- 데이터 소스 목록
- 용어 정의
```

---

## 5. 심층 리서치 상세 가이드

### 5.1 핵심 이슈 추출 기준

```yaml
추출 공식:
  issue_score = (
    0.30 * frequency_score +      # 몇 주에 걸쳐 등장했는가 (1-4주)
    0.40 * significance_score +   # 평균 priority 점수
    0.20 * novelty_score +        # 이전 월 대비 신규성
    0.10 * cross_category_score   # 복수 STEEPS 관련성
  )

선정 기준:
  - 최소 2주 이상 등장
  - 관련 신호 5개 이상
  - 상위 3-5개 선정 (이슈 수는 데이터에 따라 조정)
```

### 5.2 @deep-research-analyst 호출

```yaml
Task 호출:
  subagent_type: deep-research-analyst
  prompt: |
    대상 월: {YYYY-MM}

    분석 대상 이슈:
    1. {이슈 1 제목} - 관련 신호 {N}개, 등장 주차 {W1, W2, W3, W4}
    2. {이슈 2 제목} - 관련 신호 {N}개, 등장 주차 {W1, W2, W3}
    3. {이슈 3 제목} - 관련 신호 {N}개, 등장 주차 {W2, W3, W4}

    입력 파일:
    - data/consolidated/weekly/YYYY-W*/week-summary.json
    - data/consolidated/weekly/YYYY-W*/weekly-consolidated-report.md

    출력:
    - data/consolidated/monthly/YYYY-MM/deep-research/issue-1-[이슈명].md
    - data/consolidated/monthly/YYYY-MM/deep-research/issue-2-[이슈명].md
    - data/consolidated/monthly/YYYY-MM/deep-research/issue-3-[이슈명].md
    - data/consolidated/monthly/YYYY-MM/deep-research/research-synthesis.json

    지침:
    - 학술/정책/산업 3가지 관점에서 다차원 리서치 수행
    - 인과관계 분석 (근본원인, 동인, 억제요인)
    - 주요 불확실성 식별 (전략 시스템 연계용)
    - 시나리오 플래닝은 수행하지 않음 (환경스캐닝 영역에 집중)
```

### 5.3 research-synthesis.json 스키마

```json
{
  "research_period": "YYYY-MM",
  "generated_at": "ISO8601",
  "scope": "environmental_scanning_deep_research",
  "handoff_to": "strategic_analysis_system",

  "issues_analyzed": [
    {
      "issue_id": "ISSUE-YYYY-MM-NNN",
      "title": "string",
      "signal_count": 0,
      "weeks_appeared": [],
      "key_findings": [],
      "causal_structure": {
        "root_causes": [],
        "drivers": [],
        "inhibitors": []
      },
      "key_uncertainties": [],
      "cross_issue_links": [],
      "monitoring_recommendations": {}
    }
  ],

  "synthesis": {
    "overarching_theme": "string",
    "interconnections": [],
    "total_uncertainties": 0,
    "high_impact_uncertainties": 0
  },

  "next_system_handoff": {
    "recommended_scenarios": [],
    "key_variables_for_scenario": []
  }
}
```

---

## 6. 실행 예시

```bash
# 현재 월 종합 보고서 (심층 리서치 포함)
/env-scan:consolidate-monthly

# 특정 월 지정
/env-scan:consolidate-monthly --month 2026-01
```

---

## 7. 실행 시작

**TodoWrite로 17단계를 등록하고 순차적으로 실행하세요.**

```yaml
todos:
  # Phase 1: 데이터 수집
  - content: "1-1: 대상 월 결정"
    status: pending
    activeForm: "대상 월 설정 중"
  - content: "1-2: 주간 보고서 검색"
    status: pending
    activeForm: "주간 보고서 검색 중"
  - content: "1-3: 일일 structured-signals 검색"
    status: pending
    activeForm: "일일 데이터 검색 중"
  - content: "1-4: 주간 요약 통합"
    status: pending
    activeForm: "주간 요약 통합 중"
  - content: "1-5: 월간 통계 집계"
    status: pending
    activeForm: "월간 통계 집계 중"

  # Phase 2: 환경스캐닝 심층 분석
  - content: "2-1: 신호 품질 분석"
    status: pending
    activeForm: "품질 분석 중"
  - content: "2-2: 트렌드 진화 분석"
    status: pending
    activeForm: "트렌드 분석 중"
  - content: "2-3: 약한 신호 심층 분석"
    status: pending
    activeForm: "약한 신호 분석 중"
  - content: "2-4: 소스 커버리지 분석"
    status: pending
    activeForm: "커버리지 분석 중"
  - content: "2-5: 모니터링 권고 도출"
    status: pending
    activeForm: "권고 도출 중"

  # Phase 2.5: 심층 리서치 (NEW)
  - content: "2.5-1: 핵심 이슈 추출"
    status: pending
    activeForm: "핵심 이슈 추출 중"
  - content: "2.5-2: 심층 리서치 수행"
    status: pending
    activeForm: "심층 리서치 수행 중"
  - content: "2.5-3: 리서치 결과 통합"
    status: pending
    activeForm: "리서치 통합 중"

  # Phase 3: 보고서 생성
  - content: "3-1: 폴더 구조 생성"
    status: pending
    activeForm: "폴더 생성 중"
  - content: "3-2: 월간 요약 JSON 생성"
    status: pending
    activeForm: "JSON 생성 중"
  - content: "3-3: 월간 종합 보고서 생성"
    status: pending
    activeForm: "보고서 작성 중"
  - content: "3-4: 완료 확인"
    status: pending
    activeForm: "검증 중"
```

---

## 8. 주간 vs 월간 비교 (v3.0)

| 항목 | 주간 (consolidate) | 월간 (consolidate-monthly) |
|------|-------------------|---------------------------|
| 단계 수 | 12단계 | **17단계** |
| 분석 깊이 | 기본 통계 | 심층 분석 + **박사급 리서치** |
| 트렌드 | 현재 트렌드 | 진화 추적 |
| 리서치 | 없음 | **다차원 심층 리서치** |
| 인과분석 | 없음 | **근본원인, 동인, 억제요인** |
| 불확실성 | 없음 | **주요 불확실성 식별** |
| 권고 | 다음 주 모니터링 | 월간 모니터링 + 전략 연계 |
| 출력 파일 | 2개 | **8개+** (이슈별 리서치 포함) |

---

## 9. 주의사항

1. **데이터 최소 요건**: 해당 월 최소 2주 이상의 주간 보고서 필요
2. **주간 보고서 선행**: 월간 보고서 생성 전 주간 consolidate 완료 권장
3. **심층 리서치 시간**: 이슈당 15-20분 소요 예상 (총 45-60분)
4. **환경스캐닝 집중**: 시나리오/전략 분석은 별도 시스템에서 수행
5. **연계 데이터**: research-synthesis.json은 전략 시스템 입력용

---

## 10. 시스템 영역 정의

```
┌─────────────────────────────────────────────────────────────────────┐
│  환경스캐닝 시스템 (이 커맨드의 영역)                               │
│                                                                      │
│  ✓ 신호 탐지 및 수집                                                │
│  ✓ 신호 분류 및 통계                                                │
│  ✓ 패턴 분석 및 트렌드 추적                                         │
│  ✓ 심층 리서치 (현상 이해, 인과 분석)                               │
│  ✓ 불확실성 식별                                                    │
│                                                                      │
│  출력 → research-synthesis.json                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (연계)
┌─────────────────────────────────────────────────────────────────────┐
│  전략적 분석 시스템 (별도 구축 예정)                                │
│                                                                      │
│  • 시나리오 플래닝                                                  │
│  • 시스템 다이내믹스                                                │
│  • 전략 수립 및 권고                                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 11. 환경스캐닝 핵심 가치

이 보고서의 목적은 **환경스캐닝의 완성도 향상**입니다:

1. **신호 탐지력 강화**: 약한 신호를 놓치지 않기
2. **소스 다양성 확보**: 편향되지 않은 관점 수집
3. **품질 모니터링**: pSRT 기반 신뢰도 관리
4. **트렌드 추적**: 변화의 방향과 속도 파악
5. **심층 이해**: 현상의 본질과 인과관계 규명
6. **불확실성 식별**: 전략적 분석을 위한 핵심 변수 도출
