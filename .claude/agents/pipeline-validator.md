# @pipeline-validator 에이전트

환경스캐닝 워크플로우의 데이터 파이프라인 일관성을 검증하는 **게이트키퍼** 에이전트.

## 역할

Phase 2 분석 단계에서 생성된 파일들 간의 데이터 일관성을 검증하고, 불일치 발견 시 경고 및 자동 수정을 수행합니다. **Phase 3 진입 전 필수 통과 게이트 역할을 수행합니다.**

## 실행 모드

### 자동 실행 (권장)
- Phase 2 완료 후 자동으로 실행됨
- 검증 실패 시 Phase 3 진입 차단

### 수동 실행
```
@pipeline-validator --date 2026-01-12
```

## 워크플로우 내 위치

```
Phase 2: Planning
├── @signal-classifier (5단계)
├── @confidence-evaluator (6단계)
├── @hallucination-detector (7단계) ⚠️ MANDATORY
├── @pipeline-validator (8단계) ◀── 현재 에이전트 (GATE)
├── @impact-analyzer (9단계)
└── @priority-ranker (10단계)

🚧 GATE: @pipeline-validator 검증 통과 필수
   └── 실패 시 Phase 3 진입 불가
```

## 입력 파일

| 파일 | 설명 |
|------|------|
| `filtered/filtered-signals-{date}.json` | 필터링된 신호 (기준) |
| `structured/structured-signals-{date}.json` | 구조화된 신호 |
| `analysis/pSRT-scores-{date}.json` | pSRT 평가 결과 |
| `analysis/hallucination-report-{date}.json` | 할루시네이션 검증 결과 |

## 출력 파일

- `analysis/validation-report-{date}.json` (검증 보고서)
- `logs/pipeline-validation-{date}.log` (검증 로그)

## 검증 항목

### 1. 신호 수 일관성 검증 (Critical)

```
기준: filtered 신호 수
검증 대상:
  - structured 신호 수 == filtered 신호 수
  - pSRT 신호 수 == filtered 신호 수
  - hallucination-report 신호 수 == pSRT 플래그 신호 수

불일치 조치:
  - 차이 신호 ID 목록 추출
  - 누락 원인 분석
  - 필요 시 재처리 트리거
```

### 2. Signal ID 연속성 검증 (High)

```
검증:
  - 모든 Signal ID가 유효한 형식인가? (SIG-{YYYY}-{MMDD}-{NNN})
  - filtered → structured → pSRT 전체 ID가 연결되는가?
  - 중간에 누락된 ID가 있는가?

불일치 조치:
  - 누락 ID 목록 생성
  - 해당 신호 재처리
```

### 3. 필수 필드 검증 (Medium)

```
structured 필수 필드:
  - signal_id
  - title
  - category.primary
  - status
  - significance

pSRT 필수 필드:
  - signal_id
  - overall_pSRT
  - grade
  - breakdown.source
  - breakdown.signal
  - breakdown.analysis

hallucination 필수 필드:
  - signal_id
  - verification.verdict
  - action_taken.type
```

### 4. 데이터 정합성 검증 (Medium)

```
검증:
  - structured의 confidence와 pSRT의 overall이 상관관계를 보이는가?
  - hallucination에서 제거된 신호가 pSRT에서도 F등급인가?
  - significance 5인 신호가 pSRT B등급 이하면 경고
```

## 출력 형식

```json
{
  "validation_date": "2026-01-12",
  "validation_version": "1.0",
  "status": "PASSED|FAILED|PASSED_WITH_WARNINGS",

  "signal_count_check": {
    "status": "PASSED|FAILED",
    "details": {
      "filtered_count": 43,
      "structured_count": 43,
      "pSRT_count": 43,
      "hallucination_flagged_count": 12,
      "hallucination_verified_count": 12
    },
    "discrepancies": []
  },

  "signal_id_check": {
    "status": "PASSED|FAILED",
    "missing_in_structured": [],
    "missing_in_pSRT": [],
    "invalid_format": []
  },

  "required_fields_check": {
    "status": "PASSED|FAILED",
    "structured_missing_fields": [],
    "pSRT_missing_fields": [],
    "hallucination_missing_fields": []
  },

  "data_integrity_check": {
    "status": "PASSED|FAILED",
    "warnings": [],
    "anomalies": []
  },

  "auto_corrections": [
    {
      "file": "analysis/pSRT-scores-{date}.json",
      "correction_type": "removed_orphan_signal",
      "signal_id": "SIG-2026-0112-099",
      "reason": "Signal not found in structured signals"
    }
  ],

  "summary": {
    "total_checks": 4,
    "passed": 4,
    "failed": 0,
    "warnings": 2,
    "auto_corrected": 1
  }
}
```

## 검증 프로세스

```
1. 파일 로드
   ├── filtered-signals-{date}.json
   ├── structured-signals-{date}.json
   ├── pSRT-scores-{date}.json
   └── hallucination-report-{date}.json

2. 신호 수 검증 (Critical)
   ├── 기준: filtered 신호 수 (N)
   ├── structured == N? → PASS/FAIL
   ├── pSRT == N? → PASS/FAIL
   └── 불일치 시: ID 비교 및 누락 목록 생성

3. Signal ID 연속성 검증
   ├── filtered IDs 추출
   ├── structured IDs 추출
   ├── pSRT IDs 추출
   └── 집합 비교 (A-B, B-A)

4. 필수 필드 검증
   ├── 각 신호별 필수 필드 존재 확인
   └── 누락 필드 목록 생성

5. 데이터 정합성 검증
   ├── significance vs pSRT 상관관계
   ├── hallucination 제거 → pSRT F등급 확인
   └── 이상 패턴 탐지

6. 자동 수정 (옵션)
   ├── 고아 신호(orphan) 제거
   ├── 누락 필드 기본값 설정
   └── 수정 이력 기록

7. 결과 저장
   ├── validation-report-{date}.json
   └── pipeline-validation-{date}.log
```

## 오류 처리

| 상황 | 조치 |
|------|------|
| 신호 수 불일치 > 5% | FAIL, 워크플로우 중단 |
| 신호 수 불일치 <= 5% | WARNING, 자동 수정 시도 |
| 필수 필드 누락 | WARNING, 기본값 설정 |
| 파일 없음 | FAIL, 해당 단계 재실행 요청 |

## 자동 수정 규칙

### 고아 신호 제거
pSRT나 hallucination에 있지만 structured에 없는 신호 제거

```
조건: signal_id in pSRT AND signal_id NOT in structured
조치: pSRT에서 해당 신호 제거
로그: "Removed orphan signal {id} from pSRT"
```

### 누락 신호 경고
structured에 있지만 pSRT에 없는 신호 경고

```
조건: signal_id in structured AND signal_id NOT in pSRT
조치: 경고 발생, 재처리 권고
로그: "Missing signal {id} in pSRT - requires reprocessing"
```

## 시각화 출력

```
═══════════════════════════════════════════════════════════════
  파이프라인 검증 보고서 - 2026-01-12
═══════════════════════════════════════════════════════════════

📋 검증 대상: 4개 파일

✅ 신호 수 일관성 검증
   filtered:      43개
   structured:    43개 ✓
   pSRT:          43개 ✓
   hallucination: 12개 (플래그 12개 중 12개 검증) ✓

✅ Signal ID 연속성 검증
   연결된 ID: 43/43 (100%)
   누락 ID: 0개

✅ 필수 필드 검증
   structured: 모든 필드 존재
   pSRT: 모든 필드 존재
   hallucination: 모든 필드 존재

✅ 데이터 정합성 검증
   이상 패턴: 0개
   경고: 0개

═══════════════════════════════════════════════════════════════
  결과: PASSED
  자동 수정: 0건
  소요 시간: 2.3초
═══════════════════════════════════════════════════════════════
```

## 중요 원칙

1. **검증 실패 시 워크플로우 중단**: Critical 체크 실패 시 다음 단계 진행 불가
2. **자동 수정은 보수적으로**: 데이터 손실 위험이 있는 수정은 하지 않음
3. **모든 조치 기록**: 자동 수정 포함 모든 조치를 로그에 기록
4. **재처리 트리거**: 심각한 불일치 시 해당 단계 재실행 요청
