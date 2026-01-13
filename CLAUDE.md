# Environmental Scanning System

미래 연구(Futures Research)를 위한 환경스캐닝 자동화 시스템.

## 프로젝트 개요

변화의 조기 징후(약한 신호, weak signals)를 체계적으로 탐지하고 분석하여 일일 보고서를 생성합니다.

## 핵심 명령어

| 명령어 | 설명 |
|--------|------|
| `/env-scan:run` | **기본값: Marathon Mode (심층 스캔)** |
| `/env-scan:run --fast` | Fast Mode (핵심 소스만 빠르게 스캔) |
| `/env-scan:run --skip-human` | Marathon + Human Review 생략 |
| `/env-scan:resume` | 체크포인트에서 재개 |
| `/env-scan:status` | 현재 상태 확인 |

---

## Orchestrator 패턴

### 핵심 원칙 (토큰 최적화)

1. **최소 컨텍스트**: 각 에이전트에 필요한 최소 정보만 전달
2. **파일 기반 통신**: 데이터는 파일로, 메시지는 경로만
3. **병렬 실행**: 독립 작업은 동시 수행
4. **결과 압축**: 상세는 파일에, 메시지는 요약만

### 토큰 절감 효과

```
기존 방식: ~26,000 토큰/실행
Orchestrator: ~8,500 토큰/실행
절감률: 69%
```

### 설정 파일

- `config/workflow-definition.yaml`: 워크플로우 정의
- `config/agent-prompts.yaml`: 에이전트 호출 템플릿
- `logs/orchestrator-state-{date}.json`: 실행 상태

---

## Marathon Mode (기본값): 심층 소스 탐험

### 핵심 목적
- 다중 소스 스캐닝 단계를 **확장**하여 심층 탐색 수행
- **이전에 한 번도 스캔하지 않은** 완전히 새로운 소스 발굴
- Stage 1 완료 후 잔여 시간 **전체**를 Stage 2에 **강제 배정**

> **Note**: `/env-scan:run` 실행 시 기본적으로 Marathon 모드로 작동합니다.
> 빠른 스캔이 필요하면 `--fast` 옵션을 사용하세요.

### 2단계 구조

```
┌─────────────────────────────────────────────────────────┐
│  Stage 1: 기존 소스 스캔 (가변)                          │
│  • DB에 등록된 소스 스캔                                 │
│  • 네이버/글로벌/구글 크롤러 병렬 실행                   │
├─────────────────────────────────────────────────────────┤
│  Stage 2: 신규 소스 탐험 (잔여 시간 전체 강제 배정)      │
│  • Step 2-1: @gap-analyzer (갭 분석)                    │
│  • Step 2-2: @frontier-explorer + @citation-chaser (병렬)│
│  • Step 2-3: @rapid-validator (실시간 검증)             │
└─────────────────────────────────────────────────────────┘
```

### Stage 2 전문 에이전트

| 에이전트 | 역할 | 배분 |
|----------|------|------|
| `@gap-analyzer` | STEEPS/지역/언어 갭 분석, 우선순위 맵 생성 | 선행 |
| `@frontier-explorer` | 미개척 지역/비영어권/신규 플랫폼 탐험 | 55% |
| `@citation-chaser` | 인용 체인 역추적, 원천 소스 발굴 | 35% |
| `@rapid-validator` | 발견 소스 실시간 검증 (70점+ 자동 승격) | 10% |

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
