---
description: 보고서 수정 요청
argument-hint: [feedback]
---

# 보고서 수정 요청

오늘 날짜: !`date +%Y-%m-%d`

## 수정 피드백

$ARGUMENTS

## 수정 프로세스

1. **피드백 분석**
   - 수정 요청 내용 파악
   - 영향 받는 섹션 식별

2. **수정 적용**
   - 해당 에이전트 재실행 또는 직접 수정
   - 가능한 수정 범위:
     - 신호 분류 수정 (`@signal-classifier`)
     - 영향도 분석 수정 (`@impact-analyzer`)
     - 우선순위 조정 (`@priority-ranker`)
     - 보고서 내용 수정 (`@report-generator`)

3. **재생성**
   - 수정된 내용으로 보고서 재생성
   - `env-scanning/reports/daily/environmental-scan-{date}.md` 덮어쓰기

4. **재검토 요청**
   - 수정된 보고서 제시
   - `/approve-report` 또는 추가 `/request-revision`

## 수정 유형

| 유형 | 예시 | 재실행 에이전트 |
|------|------|-----------------|
| 분류 오류 | "SIG-001은 Economic이 아니라 Political" | signal-classifier |
| 중요도 조정 | "SIG-015의 중요도를 4에서 5로" | priority-ranker |
| 영향 분석 보완 | "SIG-023의 2차 영향 추가 필요" | impact-analyzer |
| 보고서 포맷 | "Executive Summary 수정" | report-generator |
| 내용 추가 | "특정 시사점 강조 필요" | report-generator |

## 이전 버전 보존

수정 전 보고서를 백업:
```
reports/daily/environmental-scan-{date}.md
→ reports/daily/environmental-scan-{date}.v1.md
```

피드백을 분석하고 적절한 수정을 진행합니다.
