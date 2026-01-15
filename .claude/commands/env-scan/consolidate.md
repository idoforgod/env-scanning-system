---
description: 주간 환경스캐닝 종합 보고서 생성 (중복 제거 및 통합)
allowed-tools: Read, Write, Glob, Grep, Bash, Task
argument-hint: [--week <YYYY-Www> | --range <start-date> <end-date> | --current]
---

# 주간 환경스캐닝 종합 보고서 생성

오늘 날짜: !`date +%Y-%m-%d`
현재 주차: !`date +%Y-W%V`
옵션: $ARGUMENTS

---

## 1. 옵션 해석

```yaml
옵션 처리:
  --current: 현재 주차 보고서 생성 (기본값)
  --week YYYY-Www: 특정 주차 보고서 생성 (예: 2026-W03)
  --range start end: 날짜 범위 지정 (예: 2026-01-12 2026-01-15)
```

---

## 2. 워크플로우 (12단계)

### Phase 1: 데이터 수집 (4단계)

```yaml
Step 1-1: 대상 기간 결정
  - 옵션에 따라 시작/종료 날짜 설정
  - 주차 계산 (ISO Week Number)

Step 1-2: structured-signals 파일 검색
  - Glob: data/YYYY/MM/DD/structured/structured-signals-*.json
  - 대상 기간 내 모든 파일 목록화

Step 1-3: 각 파일 요약 정보 수집
  - total_classified
  - by_category
  - pSRT_summary
  - 날짜별로 정리

Step 1-4: 신호 통계 집계
  - 총 신호 수 계산
  - 카테고리별 합산
  - pSRT 평균 계산
```

### Phase 2: 분석 및 통합 (4단계)

```yaml
Step 2-1: 중복 패턴 분석
  - URL 기반 중복 감지
  - 제목 유사도 검사 (선택적)
  - 중복 클러스터 식별

Step 2-2: 주요 트렌드 추출
  - 카테고리별 핵심 신호 선별
  - 반복 등장 주제 식별
  - 신규 부상 신호(Emerging) 태깅

Step 2-3: 연관 신호 클러스터링
  - 주제별 그룹화
  - 대표 신호 선정
  - 관계 맵 생성

Step 2-4: 시사점 도출
  - 주간 핵심 트렌드 5개 선정
  - 다음 주 모니터링 우선순위
  - 스캐닝 개선 제안
```

### Phase 3: 보고서 생성 (4단계)

```yaml
Step 3-1: 폴더 구조 생성
  - mkdir -p data/consolidated/weekly/YYYY-Www/

Step 3-2: 요약 JSON 생성
  - week-summary.json
  - 메타데이터, 통계, 핵심 트렌드

Step 3-3: 종합 보고서 생성
  - weekly-consolidated-report.md
  - 8개 섹션 포함 (개요~부록)

Step 3-4: 완료 확인
  - 파일 생성 검증
  - 결과 요약 출력
```

---

## 3. 출력 구조

```
data/consolidated/weekly/YYYY-Www/
├── week-summary.json              # 요약 데이터
├── weekly-consolidated-report.md  # 종합 보고서
└── signals-merged.json            # (선택) 병합된 전체 신호
```

---

## 4. 종합 보고서 템플릿

```markdown
# 주간 환경스캐닝 종합 보고서
## YYYY년 W주차 (시작일 ~ 종료일)

## 1. 개요
- 기간, 총 신호 수, 소스 파일 수

## 2. 일별 신호 현황
- 날짜별 신호 수 및 주요 특징

## 3. STEEPS 카테고리별 분석
- 전체 분포 (차트)
- 카테고리별 주요 신호

## 4. 신뢰도(pSRT) 분석
- 일별 평균 pSRT
- 고신뢰도 신호 목록

## 5. 주요 트렌드 및 시사점
- 핵심 트렌드 5개
- 신규 부상 신호

## 6. 중복 및 연관 신호 분석
- 중복 패턴 감지
- 연관 신호 클러스터

## 7. 권고사항
- 다음 주 모니터링 우선순위
- 스캐닝 개선 제안

## 8. 부록
- 데이터 소스 통계
- 파일 구조
```

---

## 5. 실행 예시

```bash
# 현재 주차 종합 보고서
/env-scan:consolidate

# 특정 주차 지정
/env-scan:consolidate --week 2026-W03

# 날짜 범위 지정
/env-scan:consolidate --range 2026-01-12 2026-01-15
```

---

## 6. 실행 시작

**TodoWrite로 12단계를 등록하고 순차적으로 실행하세요.**

```yaml
todos:
  - content: "1-1: 대상 기간 결정"
    status: pending
    activeForm: "대상 기간 설정 중"
  - content: "1-2: structured-signals 파일 검색"
    status: pending
    activeForm: "신호 파일 검색 중"
  - content: "1-3: 각 파일 요약 정보 수집"
    status: pending
    activeForm: "요약 정보 수집 중"
  - content: "1-4: 신호 통계 집계"
    status: pending
    activeForm: "통계 집계 중"
  - content: "2-1: 중복 패턴 분석"
    status: pending
    activeForm: "중복 분석 중"
  - content: "2-2: 주요 트렌드 추출"
    status: pending
    activeForm: "트렌드 추출 중"
  - content: "2-3: 연관 신호 클러스터링"
    status: pending
    activeForm: "클러스터링 중"
  - content: "2-4: 시사점 도출"
    status: pending
    activeForm: "시사점 도출 중"
  - content: "3-1: 폴더 구조 생성"
    status: pending
    activeForm: "폴더 생성 중"
  - content: "3-2: 요약 JSON 생성"
    status: pending
    activeForm: "JSON 생성 중"
  - content: "3-3: 종합 보고서 생성"
    status: pending
    activeForm: "보고서 작성 중"
  - content: "3-4: 완료 확인"
    status: pending
    activeForm: "검증 중"
```

---

## 7. 주의사항

1. **파일 크기 제한**: structured-signals 파일이 256KB 초과 시 청크 단위로 읽기
2. **중복 제거 기준**: URL 완전 일치 + 제목 80% 이상 유사도
3. **폴더 누적**: 매주 새 폴더 생성하여 히스토리 보존
4. **월간/분기 보고서**: 추후 `/env-scan:consolidate --monthly` 등 확장 예정
