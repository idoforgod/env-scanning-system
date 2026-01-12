---
description: 마지막 체크포인트에서 환경스캐닝 재개
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch
---

# 환경스캐닝 재개 (Resume from Checkpoint)

오늘 날짜: !`date +%Y-%m-%d`

## 자동 재개 프로토콜

### 1. 체크포인트 파일 확인

먼저 오늘 날짜의 체크포인트 파일을 확인합니다:

```
Read logs/checkpoint-{date}.json
Read context/resume-summary-{date}.md
```

### 2. 진행 상황 파악

체크포인트에서 다음 정보를 확인:
- 완료된 Phase 및 Step
- 수집된 신호 개수
- 생성된 파일 목록
- 다음 실행할 작업

### 3. 재개 실행

```markdown
========================================
  환경스캐닝 RESUME MODE
  마지막 체크포인트에서 재개
========================================
세션 ID: {session_id}
마지막 체크포인트: {checkpoint_time}
완료된 Phase: {completed_phases}
재개 지점: Phase {N}, Step {step_name}
```

### 4. 다음 단계 자동 실행

체크포인트의 `current_state.step`에 해당하는 에이전트를 호출합니다:

| Step | Agent |
|------|-------|
| archive-loader | `@archive-loader` |
| multi-source-scanner | `@multi-source-scanner` |
| dedup-filter | `@dedup-filter` |
| signal-classifier | `@signal-classifier` |
| impact-analyzer | `@impact-analyzer` |
| priority-ranker | `@priority-ranker` |
| db-updater | `@db-updater` |
| report-generator | `@report-generator` |
| archive-notifier | `@archive-notifier` |

## 체크포인트가 없는 경우

```
오늘 날짜의 체크포인트를 찾을 수 없습니다.
새로운 스캔을 시작하시겠습니까?

옵션:
1. /run-scan --marathon (3시간 연속 실행)
2. /run-scan (일반 실행)
```

## 재개 후 계속 Marathon Mode 유지

재개 시에도 Marathon Mode 설정이 유지됩니다:
- Context low 감지 시 자동 compact
- 체크포인트 자동 저장
- 3시간 목표 시간까지 계속 실행
