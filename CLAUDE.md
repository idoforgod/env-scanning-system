# Environmental Scanning System

미래 연구(Futures Research)를 위한 환경스캐닝 자동화 시스템.

## 프로젝트 개요

변화의 조기 징후(약한 신호, weak signals)를 체계적으로 탐지하고 분석하여 일일 보고서를 생성합니다.

## 핵심 명령어

| 명령어 | 설명 |
|--------|------|
| `/env-scan:run --marathon` | **3시간 자기개선형 소스 탐색** |
| `/env-scan:run` | 일반 환경스캐닝 실행 |
| `/env-scan:resume` | 체크포인트에서 재개 |
| `/env-scan:status` | 현재 상태 확인 |

---

## Marathon Mode: 자기개선형 소스 탐색

### 핵심 목적
- Phase 1의 multi-source-scanner를 **3시간** 동안 실행
- 더 많은 소스를 **무작위로 탐색**하여 좋은 소스 발견
- 시간이 갈수록 더 좋은 자료를 찾는 **'자기개선'** 달성

### 3시간 타임라인
```
0:00-0:30  Phase A: Tier 1 핵심 소스 스캔
0:30-1:30  Phase B: 무작위 탐험 스캔 (@exploration-scanner)
1:30-2:30  Phase C: 링크 추적 & 새 소스 발견 (@link-tracker)
2:30-3:00  Phase D: 발견된 소스 검증 & 평가 (@source-evaluator)
```

### Marathon 전용 에이전트
| 에이전트 | 역할 |
|----------|------|
| `@exploration-scanner` | 무작위 탐험, 새 소스 발견 |
| `@link-tracker` | 인용/참고문헌 추적 |
| `@source-evaluator` | 소스 품질 평가 및 승격 |
| `@performance-updater` | 성과 통계 갱신 |

---

## MARATHON MODE 자동화 지침 (중요)

### Context Low 진입 시 자동 프로토콜

**Marathon Mode 실행 중 Context low가 감지되면 반드시 다음을 수행:**

1. **즉시 체크포인트 저장**
   ```
   Write to: logs/{YYYY}/{MM}/checkpoint-{DD}.json
   Write to: context/resume-summary-{date}.md
   ```

2. **사용자에게 알림**
   ```
   "Context low 감지. 체크포인트 저장 완료. /compact 실행 후 자동 재개합니다."
   ```

3. **Compact 후 자동 재개**
   - 새 세션 시작 시 체크포인트 파일 확인
   - `logs/{YYYY}/{MM}/checkpoint-{DD}.json` 존재 시 자동 재개

---

## 데이터 구조 (v2.0)

```
프로젝트/
├── .claude/                    # Claude Code 설정
│   ├── agents/                 # 에이전트 정의
│   ├── commands/               # 명령어 정의
│   └── skills/                 # 스킬 정의
│
├── src/                        # 소스 코드
│   └── scripts/
│       ├── crawlers/           # 크롤러 (naver, global, google)
│       ├── processors/         # 처리 모듈 (dedup, psrt 등)
│       ├── utils/              # 유틸리티
│       └── runners/            # 실행 스크립트
│
├── config/                     # 설정 파일
│   ├── automation.yaml         # 자동화 설정
│   ├── sources.yaml            # 소스 목록
│   ├── domains.yaml            # 스캐닝 도메인
│   ├── thresholds.yaml         # 임계값 설정
│   ├── regular-sources.json    # 정규 소스 목록
│   └── evolution/              # 진화 관련 설정
│
├── data/                       # 결과 데이터 (날짜별)
│   ├── YYYY/MM/DD/
│   │   ├── raw/                # 원시 스캔 데이터
│   │   ├── filtered/           # 필터링된 신호
│   │   ├── structured/         # 구조화된 신호
│   │   ├── analysis/           # 분석 결과
│   │   └── reports/            # 일일 보고서
│   └── weekly/                 # 주간 집계
│       └── YYYY/W{WW}/
│
├── signals/                    # 신호 DB (별도 관리)
│   ├── database.json           # 마스터 DB
│   ├── snapshots/              # 스냅샷
│   └── backups/                # 백업
│
├── context/                    # 컨텍스트 파일
├── logs/YYYY/MM/               # 로그 (날짜별)
├── docs/                       # 문서
│   ├── design/                 # 설계 문서
│   └── archive/                # 보관 문서
│
├── cache/                      # 캐시
├── CLAUDE.md                   # 프로젝트 지침
└── README.md                   # 프로젝트 설명
```

## STEEPS 분류 (6개 카테고리)

- **S**ocial (사회)
- **T**echnological (기술)
- **E**conomic (경제)
- **E**nvironmental (환경)
- **P**olitical (정치)
- **S**piritual (정신/영성)
