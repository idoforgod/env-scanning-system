---
description: 분기별 키워드 전체 재검토 수행
---

# 분기별 키워드 전체 재검토

오늘 날짜: {{datetime}}
인자: $ARGUMENTS

---

## 재검토 개요

분기마다 전체 STEEPS 키워드를 체계적으로 재검토합니다.

**실행 주기**: 3월, 6월, 9월, 12월 (분기 말)

---

## 재검토 범위

```
┌─────────────────────────────────────────────────────────────────┐
│  분기별 재검토 범위                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. 효과성 분석 (3개월 누적)                                     │
│     - 전체 키워드 성과 평가                                      │
│     - 카테고리별 균형 점검                                       │
│     - 언어별 (한국어/영어) 비율 확인                             │
│                                                                  │
│  2. 키워드 갱신                                                  │
│     - 퇴출 대상 최종 결정                                        │
│     - 신규 키워드 정식 추가                                      │
│     - 계층 레벨 재조정                                           │
│                                                                  │
│  3. 선정 원칙 점검                                               │
│     - 균형 접근 (미래영향력:뉴스빈도:약한신호 = 1:1:1)           │
│     - 포함/제외 기준 적절성 검토                                 │
│                                                                  │
│  4. 트렌드 반영                                                  │
│     - 신규 트렌드 키워드 후보 식별                               │
│     - 시의성 상실 키워드 퇴출                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 실행 절차

### Step 1: 3개월 메트릭 집계

```bash
# 지난 3개월 리포트 조회
python3 -c "
from src.scripts.utils.keyword_manager import KeywordManager
manager = KeywordManager()

# 최근 3개월 리뷰
import datetime
today = datetime.date.today()
for i in range(3):
    month = (today.replace(day=1) - datetime.timedelta(days=i*30)).strftime('%Y-%m')
    print(f'=== {month} ===')
    result = manager.monthly_review(month)
    print(f'Keywords: {result.get(\"summary\", {}).get(\"total_keywords\", 0)}')
    print(f'Grades: {result.get(\"summary\", {}).get(\"grade_distribution\", {})}')
    print()
"
```

### Step 2: 퇴출 후보 확정

```bash
# 3개월 연속 0건 키워드 조회
python3 src/scripts/utils/keyword_tracker.py retire
```

퇴출 후보 키워드에 대해:
1. 미래 영향력 재평가 (혁신 잠재력 있는지?)
2. 약한 신호 가능성 검토 (아직 주류가 아닌 것인지?)
3. 최종 퇴출 여부 결정

### Step 3: 카테고리 균형 점검

```bash
# 현재 키워드 통계
python3 src/scripts/utils/keyword_manager.py stats
```

**권장 비율**:
- 각 카테고리: 40-60개 (±20% 균형)
- 한국어: 75-85%
- 영어: 15-25%

### Step 4: 신규 키워드 후보 식별

다음 소스에서 신규 트렌드 키워드 후보 탐색:

| 소스 | 확인 항목 |
|------|-----------|
| Gartner Hype Cycle | 신규 기술 트렌드 |
| MIT Technology Review | 10 Breakthrough Technologies |
| 트렌드 보고서 | 연간 트렌드 예측 |
| 최근 스캔 결과 | 자주 등장하는 새 용어 |

### Step 5: 키워드 갱신 실행

```bash
# 퇴출 실행 (확정된 경우)
python3 src/scripts/utils/keyword_manager.py remove {category} "{keyword}"

# 신규 추가 (검증된 경우)
python3 src/scripts/utils/keyword_manager.py add {category} "{keyword}"
```

### Step 6: 재검토 보고서 생성

```
┌─────────────────────────────────────────────────────────────────┐
│  Q{N} 분기별 키워드 재검토 보고서                                │
│  기간: {YYYY-MM} ~ {YYYY-MM}                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. 분기 요약                                                    │
│     - 총 스캔 횟수: {N}회                                        │
│     - 총 수집 URL: {N}건                                         │
│     - 총 생성 신호: {N}건                                        │
│     - 평균 전환율: {N}%                                          │
│                                                                  │
│  2. 키워드 변동                                                  │
│     - 기존 키워드: {N}개                                         │
│     - 퇴출 키워드: {N}개 [목록]                                  │
│     - 추가 키워드: {N}개 [목록]                                  │
│     - 현재 키워드: {N}개                                         │
│                                                                  │
│  3. 카테고리별 현황                                              │
│     | 카테고리 | 키워드 수 | 평균 수집 | 평균 전환율 |           │
│     |----------|-----------|-----------|-------------|           │
│     | Social   | {N}       | {N}       | {N}%        |           │
│     | Tech     | {N}       | {N}       | {N}%        |           │
│     | Economic | {N}       | {N}       | {N}%        |           │
│     | Environ  | {N}       | {N}       | {N}%        |           │
│     | Political| {N}       | {N}       | {N}%        |           │
│     | Spiritual| {N}       | {N}       | {N}%        |           │
│                                                                  │
│  4. 다음 분기 권고                                               │
│     - [권고 사항 1]                                              │
│     - [권고 사항 2]                                              │
│     - [권고 사항 3]                                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Step 7: 결과 저장

```
저장 위치: data/metrics/quarterly-review-{YYYY}-Q{N}.json
```

---

## 분기별 일정

| 분기 | 실행 시기 | 대상 기간 |
|------|-----------|-----------|
| Q1 | 3월 마지막 주 | 1월~3월 |
| Q2 | 6월 마지막 주 | 4월~6월 |
| Q3 | 9월 마지막 주 | 7월~9월 |
| Q4 | 12월 마지막 주 | 10월~12월 |

---

## 연관 명령어

- `/keyword:review` - 월간 리뷰
- `/keyword:stats` - 현재 통계
- `/keyword:add` - 키워드 추가
- `/keyword:remove` - 키워드 삭제
