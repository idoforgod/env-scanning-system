---
description: 환경스캐닝 워크플로우 현재 상태 확인
---

# 환경스캐닝 워크플로우 상태 확인

오늘 날짜: !`date +%Y-%m-%d`

## 체크 항목

다음 파일들의 존재 여부와 내용을 확인하세요:

1. **워크플로우 상태**
   - @logs/workflow-status.json

2. **오늘의 데이터**
   - `data/{date}/raw/daily-scan-{today}.json` 존재?
   - `data/{date}/filtered/new-signals-{today}.json` 존재?
   - `data/{date}/structured/classified-signals-{today}.json` 존재?
   - `data/{date}/analysis/priority-ranked-{today}.json` 존재?
   - `data/{date}/reports/environmental-scan-{today}.md` 존재?

3. **신호 DB 상태**
   - @signals/database.json 의 last_updated 확인
   - 총 신호 수, 카테고리별 분포

4. **최근 로그**
   - `logs/` 디렉토리의 최신 로그 파일들

## 출력 형식

```
═══════════════════════════════════════════════════════════
  ENVIRONMENTAL SCANNING STATUS - {date}
═══════════════════════════════════════════════════════════

LAST RUN
--------
Date:     {last_run_date}
Status:   {completed/partial/failed}
Duration: {X} minutes

TODAY'S PROGRESS
----------------
[✓] Phase 1: Research
    [✓] Archive Loading
    [✓] Multi-source Scanning
    [✓] Deduplication
    [ ] Human Review (pending)

[ ] Phase 2: Planning
    [ ] Classification
    [ ] Impact Analysis
    [ ] Priority Ranking
    [ ] Human Review

[ ] Phase 3: Implementation
    [ ] DB Update
    [ ] Report Generation
    [ ] Archiving
    [ ] Approval

DATABASE STATS
--------------
Total Signals: {N}
Last Updated:  {datetime}

NEXT ACTION
-----------
{recommended next step}
═══════════════════════════════════════════════════════════
```

env-scanning 디렉토리의 파일들을 확인하고 상태를 보고하세요.
