---
name: evolution:status
description: 현재 진화 시스템 상태 확인
---

# Evolution Status

자기개선 시스템의 현재 상태를 확인합니다.

## 표시 정보

### 1. 시스템 설정
- 자동화 레벨 (level_1, level_2, level_3)
- 활성화된 규칙 (승격, 강등, 비활성화)
- 안전장치 상태

### 2. 소스 통계
- 총 소스 수
- Tier별 분포
- STEEPS 커버리지

### 3. 성과 현황
- 평균 pSRT
- 트렌드 분포 (improving, stable, declining)
- 최근 변경 이력

### 4. 대기 중인 변경
- pending 승격/강등
- probation 중인 소스

### 5. 스냅샷 정보
- 마지막 스냅샷 날짜
- 총 스냅샷 수

## 출력 예시

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Evolution System Status                          │
│                    {current_date}                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  📊 System Configuration                                            │
│     • Automation Level: Level 2 (Conditional)                       │
│     • Promotion Rules: ✅ Enabled                                  │
│     • Demotion Rules: ✅ Enabled                                   │
│     • Deactivation Rules: ✅ Enabled                               │
│                                                                     │
│  📈 Source Statistics                                               │
│     • Total Sources: 177                                            │
│     • Tier 1: 50 (28%)                                              │
│     • Tier 2: 65 (37%)                                              │
│     • Tier 3: 42 (24%)                                              │
│     • Tier 4: 20 (11%)                                              │
│                                                                     │
│  🌐 STEEPS Coverage                                                 │
│     • Social: 28 sources ████████░░ 80%                            │
│     • Technological: 52 sources ██████████ 100%                    │
│     • Economic: 35 sources ██████████ 100%                         │
│     • Environmental: 22 sources ██████████ 100%                    │
│     • Political: 28 sources ██████████ 100%                        │
│     • Spiritual: 12 sources ██████░░░░ 60% ⚠️                      │
│                                                                     │
│  📉 Performance Summary                                             │
│     • Average pSRT: 49.6                                            │
│     • Improving: 15 sources                                         │
│     • Stable: 140 sources                                           │
│     • Declining: 22 sources                                         │
│                                                                     │
│  ⏳ Pending Changes                                                 │
│     • Promotions: 2                                                 │
│     • Demotions: 1                                                  │
│     • Probation Sources: 0                                          │
│                                                                     │
│  💾 Snapshots                                                       │
│     • Last Snapshot: 2026-01-12                                     │
│     • Total Snapshots: 1                                            │
│     • Retention: 90 days                                            │
│                                                                     │
│  📝 Recent Changes                                                  │
│     • (no changes yet)                                              │
│                                                                     │
│  🔒 Safety Status                                                   │
│     • Whitelist: 11 absolute + 8 conditional + 3 regional          │
│     • Blacklist: 25 domains blocked                                 │
│     • Anomaly Detection: ✅ Active                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 사용 예시

```bash
# 전체 상태 확인
/evolution:status

# 간단 요약만
/evolution:status --brief
```

## 관련 파일

- `config/evolution-config.json`: 시스템 설정
- `evolution/evolution-log.json`: 변경 이력
- `evolution/pending-sources.json`: 대기 소스
- `evolution/snapshots/`: 스냅샷
