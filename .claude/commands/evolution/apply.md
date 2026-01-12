---
name: evolution:apply
description: 진화 규칙을 수동으로 적용하여 소스 Tier 조정
---

# Evolution Apply

현재 성과 데이터를 기반으로 진화 규칙을 수동 적용합니다.

## 실행 단계

### 1. 사전 준비
1. 현재 config 스냅샷 저장
2. evolution-config.json에서 규칙 로드
3. source-performance.json에서 성과 데이터 로드

### 2. 후보 식별

#### 승격 후보 (Promotion)
```
조건:
- pSRT 평균 ≥ 70
- 스캔 횟수 ≥ 3
- 트렌드 = "improving"
- 발견 신호 ≥ 2
```

#### 강등 후보 (Demotion)
```
조건:
- pSRT 평균 ≤ 40
- 스캔 횟수 ≥ 3
- 트렌드 = "declining"
```

#### 비활성화 후보 (Deactivation)
```
조건:
- pSRT 평균 ≤ 30
- 스캔 횟수 ≥ 5
- 발견 신호 = 0
```

### 3. 안전장치 적용

1. **화이트리스트 확인**: evolution-whitelist.json
   - absolute 소스: 변경 불가
   - conditional 소스: min_tier 이상 유지

2. **블랙리스트 확인**: evolution-blacklist.json
   - 차단 도메인 제외

3. **상한선 적용**
   - Tier 변경: 최대 5개
   - 비활성화: 최대 3개
   - 초과분은 pending으로 이동

4. **STEEPS 균형 확인**
   - 카테고리별 최소 소스 수 유지

5. **이상 탐지**
   - pSRT 급락 30% 이상: 경고
   - 신호 수 급감 50% 이상: 경고
   - 대량 강등 10개 이상: 일시정지

### 4. 변경 적용
- regular-sources.json 업데이트
- evolution-log.json에 기록

### 5. 결과 리포트

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Evolution Applied                                │
│                    {date}                                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ✅ Promotions ({count})                                           │
│     • {source}: Tier {from} → Tier {to} (pSRT: {score})            │
│                                                                     │
│  ⬇️ Demotions ({count})                                            │
│     • {source}: Tier {from} → Tier {to} (pSRT: {score})            │
│                                                                     │
│  🔴 Deactivations ({count})                                        │
│     • {source}: deactivated (pSRT: {score}, signals: 0)            │
│                                                                     │
│  ⏸️ Pending ({count})                                              │
│     • {count} changes queued (limit exceeded)                       │
│                                                                     │
│  🔒 Protected ({count})                                            │
│     • {count} sources protected by whitelist                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 사용 예시

```bash
# 진화 규칙 적용
/evolution:apply

# 드라이런 (실제 적용 없이 미리보기)
/evolution:apply --dry-run
```

## 관련 파일

- `config/evolution-config.json`: 규칙 정의
- `config/evolution-whitelist.json`: 보호 소스
- `config/source-performance.json`: 성과 데이터
- `evolution/evolution-log.json`: 변경 이력
