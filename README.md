# Environmental Scanning System

[![CI](https://github.com/idoforgod/env-scanning-system/actions/workflows/ci.yml/badge.svg)](https://github.com/idoforgod/env-scanning-system/actions/workflows/ci.yml)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

미래 연구(Futures Research)를 위한 환경 스캐닝 시스템입니다. 변화의 조기 징후(약한 신호, weak signals)를 체계적으로 탐지하고 분석하여 일일 보고서를 생성합니다.

## 주요 기능

- **다중 소스 스캐닝**: 뉴스, 학술논문, 특허, 정책 동향 수집
- **STEEPS 분류**: 사회(S), 기술(T), 경제(E), 환경(E), 정치(P), 보안(S) 프레임워크
- **중복 필터링**: 기존 DB와 비교하여 새로운 신호만 추출
- **영향 분석**: Futures Wheel 방식으로 1차, 2차, 교차 영향 분석
- **우선순위 산정**: 영향도(40%), 발생가능성(30%), 긴급도(20%), 신규성(10%)
- **자동 보고서 생성**: 마크다운 형식의 일일 보고서

## 프로젝트 구조

```
env-scanning/
├── signals/          # 신호 마스터 DB
├── reports/          # 일일/아카이브 보고서
├── raw/              # 원시 스캔 데이터
├── filtered/         # 중복 제거된 신호
├── structured/       # STEEPS 분류된 신호
├── analysis/         # 영향/우선순위 분석
├── config/           # 설정 파일
├── logs/             # 실행 로그
└── scripts/          # 자동화 스크립트

.claude/
├── agents/           # 서브에이전트 정의
├── commands/         # 슬래시 커맨드
└── skills/           # Claude Code 스킬
```

## 시작하기

### 요구사항

- Python 3.10+
- Claude Code CLI

### 설치

```bash
# 저장소 클론
git clone https://github.com/idoforgod/env-scanning-system.git
cd env-scanning-system

# 린터 설치
pip install ruff

# pre-commit 설치
pip install pre-commit
pre-commit install
```

### 환경 스캐닝 초기화

```bash
python .claude/skills/env-scanner/scripts/init_scanning.py
```

### 일일 스캔 실행

Claude Code에서:

```
/env-scan:run
```

## 워크플로우

| 단계 | 에이전트 | 설명 |
|------|----------|------|
| 1 | archive-loader | 과거 보고서 및 신호 DB 로딩 |
| 2 | multi-source-scanner | 다양한 소스에서 신호 탐지 |
| 3 | dedup-filter | 중복 신호 필터링 |
| 4 | signal-classifier | STEEPS 분류 |
| 5 | impact-analyzer | 영향 분석 |
| 6 | priority-ranker | 우선순위 산정 |
| 7 | db-updater | 마스터 DB 업데이트 |
| 8 | report-generator | 일일 보고서 생성 |
| 9 | archive-notifier | 아카이빙 및 알림 |

## 슬래시 커맨드

| 커맨드 | 설명 |
|--------|------|
| `/env-scan:run` | 전체 워크플로우 실행 |
| `/env-scan:status` | 현재 상태 확인 |
| `/env-scan:review-filter` | 필터링 결과 검토 |
| `/env-scan:review-analysis` | 분석 결과 검토 |
| `/env-scan:revision` | 보고서 수정 요청 |
| `/env-scan:approve` | 최종 승인 및 배포 |

## 개발

### 린트 실행

```bash
# 검사
ruff check .

# 자동 수정
ruff check --fix .

# 포맷팅
ruff format .
```

### pre-commit

커밋 시 자동으로 린트와 포맷 검사가 실행됩니다.

```bash
# 수동 실행
pre-commit run --all-files
```

## CI/CD

GitHub Actions로 다음 검사가 자동 실행됩니다:

- Ruff 린트/포맷 검사
- YAML/JSON 문법 검사

## 라이선스

MIT License
