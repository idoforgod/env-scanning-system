# GitHub Actions 환경스캐닝 자동화 설정

## 필수 설정

### 1. GitHub Secrets 설정

Repository Settings > Secrets and variables > Actions에서 다음 시크릿을 추가하세요:

```
ANTHROPIC_API_KEY: sk-ant-api03-xxxxx...
```

Anthropic API 키는 https://console.anthropic.com/settings/keys 에서 발급받을 수 있습니다.

### 2. GitHub Actions 권한 설정

Repository Settings > Actions > General에서:

- **Workflow permissions**: "Read and write permissions" 선택
- **Allow GitHub Actions to create and approve pull requests**: 체크

---

## 워크플로우 일정

| 스캔 유형 | 일정 | 설명 |
|----------|------|------|
| **일일 스캔** | 매일 06:00 KST | Tier 1+2 소스 (68개) |
| **주간 심층** | 매주 월요일 | 전체 소스 + 메타 분석 |

---

## 수동 실행 방법

### GitHub UI에서 실행

1. Actions 탭 이동
2. "Daily Environmental Scan" 워크플로우 선택
3. "Run workflow" 버튼 클릭
4. 스캔 유형 선택:
   - `daily`: 일일 스캔
   - `weekly-deep`: 주간 심층 분석
   - `alt-sources`: 대안 소스 스캔

### CLI에서 실행

```bash
# 일일 스캔 실행
gh workflow run daily-scan.yml --ref main

# 주간 심층 스캔
gh workflow run daily-scan.yml --ref main -f scan_type=weekly-deep

# 대안 소스 스캔
gh workflow run daily-scan.yml --ref main -f scan_type=alt-sources

# 결과 커밋 없이 테스트
gh workflow run daily-scan.yml --ref main -f skip_commit=true
```

---

## 워크플로우 출력

### 생성되는 파일

```
env-scanning/
├── raw/
│   └── scanned-signals-YYYY-MM-DD.json    # 원시 스캔 데이터
├── filtered/
│   └── filtered-signals-YYYY-MM-DD.json   # 필터링된 신호
├── structured/
│   └── classified-signals-YYYY-MM-DD.json # 분류된 신호
├── analysis/
│   ├── impact-analysis-YYYY-MM-DD.json    # 영향 분석
│   └── priority-ranking-YYYY-MM-DD.json   # 우선순위
├── signals/
│   └── database.json                       # 마스터 DB (업데이트됨)
├── reports/
│   ├── daily/YYYY-MM-DD.md                # 일일 보고서
│   └── weekly/YYYY-WXX.md                 # 주간 보고서
└── logs/
    └── workflow-complete-YYYY-MM-DD.log   # 완료 로그
```

### Artifacts

각 실행마다 90일간 보관되는 아티팩트:
- `scan-results-YYYY-MM-DD`: 보고서 및 로그

---

## 알림 설정 (선택사항)

### Slack 알림 추가

Secrets에 `SLACK_WEBHOOK_URL` 추가 후, 워크플로우에 다음 step 추가:

```yaml
- name: Notify Slack
  if: always()
  uses: slackapi/slack-github-action@v1.24.0
  with:
    payload: |
      {
        "text": "환경스캐닝 완료: ${{ steps.date.outputs.date }}\n상태: ${{ job.status }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 이메일 알림

실패 시 자동으로 GitHub Issue가 생성됩니다. Watch 설정으로 이메일 알림을 받을 수 있습니다.

---

## 문제 해결

### API 키 오류

```
Error: ANTHROPIC_API_KEY is not set
```
→ Secrets에 `ANTHROPIC_API_KEY` 추가 확인

### 권한 오류

```
Error: refusing to allow a GitHub App to create or update workflow
```
→ Repository Settings > Actions > General에서 권한 설정 확인

### 타임아웃

일일 스캔은 60분, 주간 스캔은 120분 제한이 있습니다.
초과 시 `timeout-minutes` 값을 조정하세요.

---

## 비용 고려

- Claude API 호출 비용이 발생합니다
- 일일 스캔 기준 약 $5-10 예상 (신호 수에 따라 변동)
- 월간 약 $150-300 예상

비용 절감을 위해:
- `--max-turns` 값 조정
- 스캔 빈도 조정 (주 3-5회)
- Tier 3+ 소스는 주간 스캔으로 제한
