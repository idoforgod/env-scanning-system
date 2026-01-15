---
description: 월간 환경스캐닝 종합 보고서 생성 (주간 보고서 통합 및 심층 분석)
allowed-tools: Read, Write, Glob, Grep, Bash, Task
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

## 2. 워크플로우 (14단계)

### Phase 1: 데이터 수집 (5단계)

```yaml
Step 1-1: 대상 월 결정
  - 옵션에 따라 대상 월 설정
  - 해당 월의 시작일/종료일 계산

Step 1-2: 주간 보고서 검색
  - Glob: data/consolidated/weekly/YYYY-W*/
  - 해당 월에 속하는 주차 필터링

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

### Phase 3: 보고서 생성 (4단계)

```yaml
Step 3-1: 폴더 구조 생성
  - mkdir -p data/consolidated/monthly/YYYY-MM/

Step 3-2: 월간 요약 JSON 생성
  - month-summary.json
  - 상세 통계, 주차별 비교, 메타 분석

Step 3-3: 월간 종합 보고서 생성
  - monthly-consolidated-report.md
  - Executive Summary 포함
  - 9개 섹션 환경스캐닝 중심

Step 3-4: 완료 확인
  - 파일 생성 검증
  - 결과 요약 출력
```

---

## 3. 출력 구조

```
data/consolidated/monthly/YYYY-MM/
├── month-summary.json              # 월간 요약 데이터
├── monthly-consolidated-report.md  # 월간 종합 보고서
├── weekly-comparison.json          # 주차별 비교 데이터
└── trend-analysis.json             # 트렌드 분석 데이터
```

---

## 4. 월간 종합 보고서 템플릿

```markdown
# 월간 환경스캐닝 종합 보고서
## YYYY년 M월

> 생성: `/env-scan:consolidate-monthly`
> 생성일: YYYY-MM-DD

---

## 1. Executive Summary
- 월간 핵심 발견 (3-5개)
- 주요 수치 요약
- 모니터링 강화 필요 영역

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

## 9. 부록
- 주차별 상세 통계
- 데이터 소스 목록
- 용어 정의
```

---

## 5. 실행 예시

```bash
# 현재 월 종합 보고서
/env-scan:consolidate-monthly

# 특정 월 지정
/env-scan:consolidate-monthly --month 2026-01
```

---

## 6. 실행 시작

**TodoWrite로 14단계를 등록하고 순차적으로 실행하세요.**

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

## 7. 주간 vs 월간 비교

| 항목 | 주간 (consolidate) | 월간 (consolidate-monthly) |
|------|-------------------|---------------------------|
| 단계 수 | 12단계 | 14단계 |
| 분석 깊이 | 기본 통계 | 심층 분석 + 약한 신호 |
| 트렌드 | 현재 트렌드 | 진화 추적 |
| 권고 | 다음 주 모니터링 | 월간 모니터링 계획 |
| 출력 파일 | 2개 | 4개 |

---

## 8. 주의사항

1. **데이터 최소 요건**: 해당 월 최소 2주 이상의 주간 보고서 필요
2. **주간 보고서 선행**: 월간 보고서 생성 전 주간 consolidate 완료 권장
3. **파일 크기**: 월간 데이터는 크므로 청크 단위 읽기 필수
4. **환경스캐닝 집중**: 시나리오/전략 분석은 별도 시스템에서 수행

---

## 9. 환경스캐닝 핵심 가치

이 보고서의 목적은 **전략적 분석이 아닌 환경스캐닝 품질 향상**입니다:

1. **신호 탐지력 강화**: 약한 신호를 놓치지 않기
2. **소스 다양성 확보**: 편향되지 않은 관점 수집
3. **품질 모니터링**: pSRT 기반 신뢰도 관리
4. **트렌드 추적**: 변화의 방향과 속도 파악
5. **커버리지 갭 해소**: 누락 영역 지속 발굴
