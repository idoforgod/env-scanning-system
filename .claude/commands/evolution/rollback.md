---
name: evolution:rollback
description: 지정 날짜의 스냅샷으로 소스 설정 복원
arguments:
  - name: date
    description: 복원할 스냅샷 날짜 (YYYY-MM-DD 형식)
    required: true
---

# Evolution Rollback

소스 설정을 지정된 날짜의 스냅샷으로 복원합니다.

## 실행 단계

### 1. 스냅샷 확인
```
스냅샷 위치: data/evolution/snapshots/{year}/{month}/
```

1. 지정된 날짜의 스냅샷 존재 확인
2. snapshot-manifest.json에서 해당 날짜 정보 확인

### 2. 현재 상태 백업
롤백 전 현재 상태를 `pre-rollback-{timestamp}` 스냅샷으로 저장

### 3. 스냅샷 복원
- `{date}-regular-sources.json` → `config/regular-sources.json`
- `{date}-source-performance.json` → `config/source-performance.json`

### 4. 로그 기록
evolution-log.json에 롤백 이벤트 기록:
```json
{
  "type": "rollback",
  "timestamp": "...",
  "target_date": "{date}",
  "reason": "user_requested",
  "files_restored": ["regular-sources.json", "source-performance.json"]
}
```

### 5. 결과 리포트
```
┌─────────────────────────────────────────────────────────────────────┐
│                    Rollback Complete                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ✅ Restored to: {date}                                            │
│                                                                     │
│  📁 Files restored:                                                 │
│     • config/regular-sources.json                                   │
│     • config/source-performance.json                                │
│                                                                     │
│  💾 Pre-rollback backup saved:                                      │
│     • snapshots/{year}/{month}/pre-rollback-{timestamp}.json       │
│                                                                     │
│  📊 Statistics after rollback:                                      │
│     • Total sources: {count}                                        │
│     • Tier 1: {tier1_count}                                         │
│     • Tier 2: {tier2_count}                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 사용 예시

```bash
# 2026-01-12 스냅샷으로 복원
/evolution:rollback 2026-01-12

# 가장 최근 스냅샷으로 복원
/evolution:rollback latest
```

## 주의사항

1. 롤백은 `regular-sources.json`과 `source-performance.json`만 복원
2. 신호 데이터베이스(`database.json`)는 복원되지 않음
3. 롤백 후 다음 스캔에서 새로운 성과 데이터 수집 시작

## 관련 파일

- `evolution/snapshots/{year}/{month}/snapshot-manifest.json`: 스냅샷 목록
- `evolution/evolution-log.json`: 롤백 이력 기록
