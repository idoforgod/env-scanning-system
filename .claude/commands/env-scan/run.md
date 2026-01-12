---
description: 일일 환경스캐닝 워크플로우 전체 실행
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch
argument-hint: [--marathon | --skip-human | --phase <1|2|3> | --resume]
---

# 환경스캐닝 일일 워크플로우 실행

오늘 날짜: !`date +%Y-%m-%d`

## 실행 옵션
- `--marathon`: **다중 소스 스캐닝 3시간 확장 모드** (Stage 1 + Stage 2)
- `--skip-human`: 모든 human 검토 단계 자동 통과
- `--phase 1`: Phase 1 (Research)만 실행
- `--phase 2`: Phase 2 (Planning)만 실행
- `--phase 3`: Phase 3 (Implementation)만 실행
- `--resume`: 마지막 체크포인트에서 재개

$ARGUMENTS

---

## Marathon Mode 정의

**Marathon Mode = 다중 소스 스캐닝 단계만 3시간으로 확장**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    환경스캐닝 전체 워크플로우                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Phase 1: Research (정보 수집)                                      │
│  ─────────────────────────────                                      │
│  1. @archive-loader (기존과 동일)                                   │
│  2. @multi-source-scanner ◀─── [Marathon Mode: 3시간 확장]         │
│  3. @dedup-filter (기존과 동일)                                     │
│                                                                     │
│  Phase 2: Planning (분석) - 기존과 동일                             │
│  Phase 3: Implementation (보고서) - 기존과 동일                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Marathon Mode 2단계 구조

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Marathon Mode: 3시간 = 180분                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐                                                │
│  │   Stage 1       │  기존 소스 스캔                                │
│  │   (가변 시간)   │  • DB에 등록된 소스 스캔                       │
│  │                 │  • 소요 시간 측정                              │
│  └────────┬────────┘                                                │
│           │                                                         │
│           ▼                                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                        Stage 2                               │   │
│  │                   (잔여 시간 전체)                           │   │
│  │                                                              │   │
│  │   완전히 새로운 소스 탐험                                    │   │
│  │   • 이전에 한 번도 스캔하지 않은 소스 발굴                   │   │
│  │   • 잔여 시간 = 180분 - Stage1 소요 시간                     │   │
│  │   • 이 시간을 전부 신규 소스 탐색에 강제 투여                │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  예시:                                                              │
│  Stage 1: 10분 → Stage 2: 170분 (2시간 50분)                       │
│  Stage 1: 30분 → Stage 2: 150분 (2시간 30분)                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stage 1: 기존 소스 스캔

**기존 방식 그대로 실행**
1. DB 로딩 (`config/regular-sources.json`)
2. 등록된 소스 순차 스캔 (Tier 1 → Tier 2 → ...)
3. 신호 수집
4. **소요 시간 측정**

### Stage 2: 신규 소스 탐험

**완전히 새로운 소스 발굴** - 이전 환경스캐닝에서 **한 번도 스캔하지 않은** 소스 탐색

4가지 탐험 전략 (각 25% 시간 배분):
- **인용 추적**: Stage 1 신호의 원문에서 인용된 소스 추출
- **도메인 탐험**: 기존 소스와 유사한 도메인 탐색 (예: stanford.edu → mit.edu)
- **키워드 확장**: STEEPS 부족 카테고리 키워드로 새 소스 발굴
- **지역 확장**: 미개척 지역 (라틴아메리카, 아프리카 등) 소스 탐색

발견된 신규 소스 → `evolution/pending-sources.json`에 후보 등록

---

## 일반 워크플로우

### Phase 1: Research (정보 수집)
1. `@archive-loader` → 기존 신호 DB 및 아카이브 로딩
2. `@multi-source-scanner` → STEEPS 다중 소스 스캐닝
   - **Marathon 모드**: Stage 1 + Stage 2 (총 3시간)
   - **일반 모드**: Stage 1만 (표준 스캔)
3. `@dedup-filter` → 중복 신호 필터링
4. **[Human Review]** → `/review-filter`로 결과 검토 (--skip-human 시 생략)

### Phase 2: Planning (분석 및 구조화)
5. `@signal-classifier` → 신호 분류, 구조화 및 초기 pSRT 계산
6. `@confidence-evaluator` → pSRT 심층 평가 및 할루시네이션 플래그 생성
7. **[MANDATORY]** `@hallucination-detector` → 플래그된 신호 검증 ⚠️ **필수 실행**
   - 입력: `analysis/pSRT-scores-{date}.json`
   - 출력: `analysis/hallucination-report-{date}.json`
   - **이 단계를 건너뛰면 워크플로우 실패로 처리**
8. **[VALIDATION]** `@pipeline-validator` → 데이터 동기화 검증 ✅ **신규 추가**
   - pSRT 신호 수와 structured 신호 수 일치 확인
   - 불일치 시 경고 및 수정
9. `@impact-analyzer` → Futures Wheel 영향도 분석
10. `@priority-ranker` → 우선순위 산정
11. **[Human Review]** → `/review-analysis`로 결과 검토 (--skip-human 시 생략)

### Phase 3: Implementation (보고서 생성)
12. `@db-updater` → 마스터 신호 DB 업데이트
13. `@report-generator` → 일일 보고서 생성
14. `@archive-notifier` → 아카이빙 및 완료 처리
15. `@source-evolver` → 발견된 소스 평가/등록 (Marathon 후)
16. `@file-organizer` → 파일 자동 정리
17. **[Human Approval]** → `/approve-report` 또는 `/request-revision`

---

## pSRT 신뢰도 평가 (Phase 2)

### pSRT란?
**pSRT (predicted Signal Reliability Test)**: AI가 생성한 정보의 할루시네이션 위험을 줄이고 신뢰도를 객관적으로 평가하는 척도.

### 평가 차원 (4가지)
| 차원 | 가중치 | 평가 항목 |
|------|--------|-----------|
| Source pSRT | 20% | 소스 권위성, 검증 가능성 |
| Signal pSRT | 35% | 구체성, 신선도, 독립성 |
| Analysis pSRT | 25% | 분류 명확성, 영향도 근거 |
| Report pSRT | 20% | 소스 다양성, 내부 일관성 |

### 등급 체계
| 등급 | 점수 | 권장 조치 |
|------|------|-----------|
| A+ | 90-100 | 즉시 활용 가능 |
| A | 80-89 | 활용 권장 |
| B | 70-79 | 모니터링 권장 |
| C | 60-69 | 추가 검증 후 활용 |
| D | 50-59 | 교차 검증 필수 |
| E | 40-49 | 참고용만 |
| F | 0-39 | 제외 |

---

## 데이터 경로

### 기존 경로
- 설정: `config/`
- 원시 데이터: `data/{date}/raw/`
- 필터링 결과: `data/{date}/filtered/`
- 구조화 데이터: `data/{date}/structured/`
- 분석 결과: `data/{date}/analysis/`
- 보고서: `data/{date}/reports/`
- 신호 DB: `signals/database.json`

### Marathon 모드 추가 경로
- 발견 소스: `data/evolution/pending-sources.json`
- 시간 로그: `logs/marathon-time-{date}.json`
- 소스 성과: `config/source-performance.json`

---

## 워크플로우 게이트 (Quality Gates)

### Gate 1: Phase 1 → Phase 2 전환 검증
```
검증 항목:
✅ filtered-signals-{date}.json 존재
✅ 신호 수 > 0
✅ dedup-index 생성 완료

실패 시: Phase 2 진입 불가, 오류 메시지 출력
```

### Gate 2: Phase 2 필수 단계 검증 (CRITICAL)
```
검증 항목:
⚠️ hallucination-report-{date}.json 존재 (MANDATORY)
✅ pSRT-scores-{date}.json 존재
✅ structured 신호 수 == filtered 신호 수 (± 5% 허용)
✅ pSRT 신호 수 == structured 신호 수

실패 시: Phase 3 진입 불가, 워크플로우 중단
경고: "Hallucination detection is MANDATORY. Cannot proceed without quality assurance."
```

### Gate 3: Phase 3 → 완료 전 TDD 검증
```
검증 항목:
✅ TDD 테스트 스위트 실행 (tests/tdd-pipeline-test.py)
✅ Pass Rate >= 80%
✅ Critical 실패 항목 0개

실패 시: 보고서 생성은 완료하되 WARNING 표시
권고: "TDD test pass rate below threshold. Review recommended."
```

---

## 핵심 원칙 (반드시 준수)

1. **과거 보고서 우선 확인**: 스캐닝 전 기존 DB 검토
2. **중복 신호 제외**: 유사도 85% 이상 = 중복
3. **신규 신호만 탐지**: 7일 내 최초 등장만 포함
4. **상태 변화 추적**: 기존 신호의 변화는 별도 섹션
5. **Marathon Stage 2**: 남은 시간 전체를 신규 소스 탐험에 강제 배정
6. **품질 게이트 통과 필수**: 각 Phase 전환 시 검증 통과 필요
7. **TDD 테스트 통합**: 워크플로우 완료 전 자동 테스트 실행

---

## TDD 테스트 통합

워크플로우 완료 전 자동으로 TDD 테스트 실행:

```bash
# Phase 3 완료 후 자동 실행
python3 data/tests/tdd-pipeline-test.py
```

테스트 결과에 따른 조치:
| Pass Rate | 상태 | 조치 |
|-----------|------|------|
| >= 90% | ✅ PASS | 정상 완료 |
| 80-89% | ⚠️ CONDITIONAL | 경고 표시 후 완료 |
| < 80% | ❌ FAIL | 검토 필요, 문제 목록 출력 |

---

## 실행 예시

### Marathon 모드 (3시간 확장 스캔)
```
/env-scan:run --marathon --skip-human
```

### 일반 일일 스캔
```
/env-scan:run
```

### 특정 Phase만 실행
```
/env-scan:run --phase 1
/env-scan:run --phase 2
/env-scan:run --phase 3
```
