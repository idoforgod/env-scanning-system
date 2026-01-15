---
description: 분기 환경스캐닝 종합 보고서 생성 (월간 보고서 통합 및 메타 분석)
allowed-tools: Read, Write, Glob, Grep, Bash, Task
argument-hint: [--quarter <YYYY-Qn> | --current]
---

# 분기 환경스캐닝 종합 보고서 생성

오늘 날짜: !`date +%Y-%m-%d`
현재 분기: !`echo "$(date +%Y)-Q$(( ($(date +%-m) - 1) / 3 + 1 ))"`
옵션: $ARGUMENTS

---

## 1. 옵션 해석

```yaml
옵션 처리:
  --current: 현재 분기 보고서 생성 (기본값)
  --quarter YYYY-Qn: 특정 분기 보고서 생성 (예: 2026-Q1)

분기 정의:
  Q1: 1월 - 3월
  Q2: 4월 - 6월
  Q3: 7월 - 9월
  Q4: 10월 - 12월
```

---

## 2. 워크플로우 (14단계)

### Phase 1: 데이터 수집 (5단계)

```yaml
Step 1-1: 대상 분기 결정
  - 옵션에 따라 대상 분기 설정
  - 해당 분기의 시작월/종료월 계산

Step 1-2: 월간 보고서 검색
  - Glob: data/consolidated/monthly/YYYY-MM/
  - 해당 분기에 속하는 월 필터링 (3개월)

Step 1-3: 주간 보고서 검색
  - Glob: data/consolidated/weekly/YYYY-W*/
  - 해당 분기에 속하는 주차 필터링 (~13주)

Step 1-4: 월간 요약 통합
  - 각 month-summary.json 읽기
  - 월별 신호 수, 카테고리 분포 집계

Step 1-5: 분기 통계 집계
  - 총 신호 수 합산
  - 카테고리별 분기 누적 분포
  - 월별/주별 트렌드 비교
```

### Phase 2: 환경스캐닝 메타 분석 (5단계)

```yaml
Step 2-1: 분기 메가트렌드 분석
  - 월별 메타트렌드 진화 추적
  - 트렌드 가속/감속/전환 식별
  - 신규 메가트렌드 발굴

Step 2-2: 약한 신호 → 강한 신호 전환 분석
  - 분기 초 약한 신호 → 분기 말 상태 추적
  - 성공적 조기 탐지 사례 식별
  - 놓친 신호 분석 (사후 검토)

Step 2-3: 소스 효과성 종합 평가
  - 소스별 분기 성과 분석
  - 신호 발굴 기여도 평가
  - 소스 Tier 승격/강등 권고

Step 2-4: 커버리지 갭 종합 분석
  - STEEPS 카테고리 균형 평가
  - 지역별/언어별 커버리지
  - 누락 영역 체계적 식별

Step 2-5: 스캐닝 품질 트렌드
  - pSRT 분포 분기 변화
  - 품질 개선/악화 요인 분석
  - 다음 분기 품질 목표 설정
```

### Phase 3: 보고서 생성 (4단계)

```yaml
Step 3-1: 폴더 구조 생성
  - mkdir -p data/consolidated/quarterly/YYYY-Qn/

Step 3-2: 분기 요약 JSON 생성
  - quarter-summary.json
  - 상세 통계, 월별 비교, 메가트렌드

Step 3-3: 분기 종합 보고서 생성
  - quarterly-consolidated-report.md
  - Executive Summary + 10개 섹션 환경스캐닝 분석

Step 3-4: 완료 확인
  - 파일 생성 검증
  - 결과 요약 출력
```

---

## 3. 출력 구조

```
data/consolidated/quarterly/YYYY-Qn/
├── quarter-summary.json              # 분기 요약 데이터
├── quarterly-consolidated-report.md  # 분기 종합 보고서
├── monthly-comparison.json           # 월별 비교 데이터
└── trend-evolution.json              # 트렌드 진화 분석
```

---

## 4. 분기 종합 보고서 템플릿

```markdown
# 분기 환경스캐닝 종합 보고서
## YYYY년 Qn분기

> 생성: `/env-scan:consolidate-quarterly`
> 생성일: YYYY-MM-DD

---

## 1. Executive Summary
- 분기 핵심 발견 (5-7개)
- 주요 수치 요약
- 스캐닝 품질 평가
- 다음 분기 중점 영역

## 2. 분기 개요
- 기간, 총 신호 수, 월별 분포
- 데이터 소스 현황
- 품질 지표 추이

## 3. 월별 동향 비교
- 각 월 핵심 요약
- 월간 변화 추이 차트
- 특이 사항 및 전환점

## 4. 메가트렌드 진화
- 분기 초 vs 분기 말 비교
- 가속/감속/전환 트렌드
- 신규 부상 메가트렌드

## 5. STEEPS 심층 분석
- 카테고리별 분기 동향
- 교차 카테고리 패턴
- 카테고리 균형 평가

## 6. 약한 신호 → 강한 신호 전환
- 성공적 조기 탐지 사례
- 신호 진화 패턴
- 놓친 신호 사후 분석

## 7. 소스 효과성 평가
- 소스별 분기 성과
- 신호 발굴 기여도
- Tier 조정 권고

## 8. 커버리지 분석
- 카테고리/지역/언어 커버리지
- 갭 영역 식별
- 개선 우선순위

## 9. 스캐닝 품질 리뷰
- pSRT 트렌드 분석
- 품질 개선 요인
- 다음 분기 목표

## 10. 다음 분기 권고
- 중점 모니터링 영역
- 소스 확충 계획
- 프로세스 개선 사항

## 11. 부록
- 월별 상세 통계
- 데이터 소스 목록
- 방법론 설명
```

---

## 5. 실행 예시

```bash
# 현재 분기 종합 보고서
/env-scan:consolidate-quarterly

# 특정 분기 지정
/env-scan:consolidate-quarterly --quarter 2026-Q1
```

---

## 6. 실행 시작

**TodoWrite로 14단계를 등록하고 순차적으로 실행하세요.**

```yaml
todos:
  # Phase 1: 데이터 수집 (5단계)
  - content: "1-1: 대상 분기 결정"
    status: pending
    activeForm: "대상 분기 설정 중"
  - content: "1-2: 월간 보고서 검색"
    status: pending
    activeForm: "월간 보고서 검색 중"
  - content: "1-3: 주간 보고서 검색"
    status: pending
    activeForm: "주간 보고서 검색 중"
  - content: "1-4: 월간 요약 통합"
    status: pending
    activeForm: "월간 요약 통합 중"
  - content: "1-5: 분기 통계 집계"
    status: pending
    activeForm: "분기 통계 집계 중"

  # Phase 2: 환경스캐닝 메타 분석 (5단계)
  - content: "2-1: 분기 메가트렌드 분석"
    status: pending
    activeForm: "메가트렌드 분석 중"
  - content: "2-2: 약한→강한 신호 전환 분석"
    status: pending
    activeForm: "신호 전환 분석 중"
  - content: "2-3: 소스 효과성 종합 평가"
    status: pending
    activeForm: "소스 평가 중"
  - content: "2-4: 커버리지 갭 종합 분석"
    status: pending
    activeForm: "커버리지 분석 중"
  - content: "2-5: 스캐닝 품질 트렌드"
    status: pending
    activeForm: "품질 분석 중"

  # Phase 3: 보고서 생성 (4단계)
  - content: "3-1: 폴더 구조 생성"
    status: pending
    activeForm: "폴더 생성 중"
  - content: "3-2: 분기 요약 JSON 생성"
    status: pending
    activeForm: "JSON 생성 중"
  - content: "3-3: 분기 종합 보고서 생성"
    status: pending
    activeForm: "보고서 작성 중"
  - content: "3-4: 완료 확인"
    status: pending
    activeForm: "검증 중"
```

---

## 7. 보고서 계층 비교

| 항목 | 주간 | 월간 | 분기 |
|------|------|------|------|
| **단계 수** | 12 | 14 | 14 |
| **분석 깊이** | 기본 통계 | 심층 분석 | 메타 분석 |
| **트렌드** | 현재 | 진화 추적 | 메가트렌드 |
| **신호 분석** | 탐지 | 약한 신호 식별 | 전환 추적 |
| **시사점** | 다음 주 | 월간 계획 | 분기 계획 |
| **출력 파일** | 2개 | 4개 | 4개 |
| **대상 독자** | 실무자 | 관리자 | 관리자/의사결정자 |

---

## 8. 환경스캐닝 중심 분석 프레임워크

### 8.1 약한 신호 전환 추적

```
분기 초 상태 → 분기 말 상태:
- Emerging → Rising: 성공적 조기 탐지
- Emerging → Stable: 유효한 지속 모니터링
- Emerging → Faded: 일시적 현상 (기록용)
- Missed → Rising: 사후 분석 필요
```

### 8.2 소스 효과성 평가 기준

```
소스 Tier 산정:
- Tier 1 (핵심): 고빈도 + 고품질 (pSRT 75+)
- Tier 2 (보조): 중빈도 + 중품질 (pSRT 60-74)
- Tier 3 (탐색): 저빈도 + 잠재력 (새로운 관점)
- 강등 후보: 저빈도 + 저품질 (pSRT 40-)
```

### 8.3 커버리지 균형 매트릭스

```
STEEPS 균형 목표:
- 각 카테고리 최소 10% 이상 비중
- 특정 카테고리 40% 초과 시 불균형 경고
- 지역: 최소 3개 대륙 커버
- 언어: 최소 3개 언어권 커버
```

---

## 9. 주의사항

1. **데이터 최소 요건**: 해당 분기 최소 2개월 이상의 월간 보고서 필요
2. **월간 보고서 선행**: 분기 보고서 생성 전 월간 consolidate 완료 권장
3. **환경스캐닝 집중**: 시나리오 플래닝, 시스템 다이내믹스는 별도 시스템에서 수행
4. **연간 보고서 확장**: `/env-scan:consolidate-yearly` 추후 지원 예정
5. **품질 개선 사이클**: 분기 보고서의 권고사항 → 다음 분기 실행

---

## 10. 환경스캐닝 핵심 가치

이 보고서의 목적은 **환경스캐닝 시스템 자체의 품질 향상**입니다:

1. **조기 탐지력 평가**: 약한 신호를 얼마나 일찍 잡았는가?
2. **소스 효과성**: 어떤 소스가 가치 있는 신호를 제공하는가?
3. **커버리지 완성도**: 어떤 영역이 사각지대인가?
4. **품질 개선**: pSRT 점수가 향상되고 있는가?
5. **메가트렌드 식별**: 개별 신호들이 어떤 큰 흐름을 보여주는가?

> **Note**: 시나리오 플래닝, 시스템 다이내믹스, 와일드카드 분석 등 전략적 분석은
> 별도의 에이전트 시스템에서 수행합니다. 이 보고서는 환경스캐닝의 "입력" 품질에 집중합니다.
