---
description: 최종 보고서 승인 및 배포
---

# 최종 보고서 승인

오늘 날짜: !`date +%Y-%m-%d`

## 승인 전 확인

다음 파일들이 정상 생성되었는지 확인하세요:

1. **일일 보고서**
   - `data/{date}/reports/environmental-scan-{today}.md`

2. **신호 DB**
   - `signals/database.json` (업데이트됨)

3. **분석 데이터**
   - `data/{date}/analysis/priority-ranked-{today}.json`

## 승인 시 수행 작업

1. **보고서 아카이빙**
   - 보고서를 `reports/archive/{year}/{month}/`로 복사
   - JSON 데이터 아카이브 생성

2. **스냅샷 저장**
   - 신호 DB 스냅샷 `signals/snapshots/database-{date}.json`

3. **완료 로그 기록**
   - `logs/daily-summary-{date}.log` 생성
   - `logs/workflow-status.json` 업데이트

4. **최종 확인**
   - 모든 파일 무결성 검증
   - 워크플로우 완료 상태 기록

## 보고서 요약

보고서 내용을 간략히 표시:
- 핵심 발견 Top 3
- 총 신규 신호 수
- 고우선순위 신호 수
- 주요 패턴/테마

## 실행

승인하시면 `@archive-notifier`를 실행하여 아카이빙을 완료합니다.

**승인하시겠습니까?** (예/아니오)

- 예: 아카이빙 및 워크플로우 완료
- 아니오: `/request-revision "피드백"` 으로 수정 요청
