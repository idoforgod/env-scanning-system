# Pipeline v4: Source of Truth Architecture

## 개요

환경스캐닝 파이프라인의 근본적 재설계.
두 가지 치명적 오류를 해결하기 위한 아키텍처.

## 해결해야 할 문제

### 문제 1: 검색 스니펫 기반 창작
- 현재: WebSearch 결과의 스니펫만 보고 LLM이 신호 "창작"
- 결과: 신호 내용 ≠ 실제 기사 내용

### 문제 2: 파이프라인 내용 변형
- 현재: 각 단계마다 LLM이 내용을 "재해석"
- 결과: 파이프라인을 거칠수록 원본에서 멀어짐

---

## 핵심 원칙

### 1. Source of Truth (원본 우선)
```
모든 신호는 반드시 실제 URL의 실제 본문에서 출발한다.
원본 본문은 별도 필드로 보존되며, 절대 변경되지 않는다.
```

### 2. Single Summarization (단일 요약)
```
LLM 요약은 파이프라인 전체에서 딱 1회만 수행된다.
이후 단계에서는 이 요약을 그대로 사용한다.
```

### 3. Separation of Concerns (분류와 내용 분리)
```
- 내용 생성: Phase 3에서만 (1회)
- 분류/평가: 메타데이터 추가만 (내용 변경 금지)
- 보고서: 기존 요약 사용 (재작성 금지)
```

### 4. URL-Content Integrity (URL-내용 일치)
```
보고서의 URL을 클릭하면, 신호 설명의 근거가 되는
실제 기사를 볼 수 있어야 한다.
```

---

## 새로운 파이프라인 구조

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Pipeline v4: Source of Truth                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 1: URL Discovery (Python)                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ WebSearch → URL 목록만 수집 (내용 수집 안함)                    │ │
│  │ 출력: urls-{date}.json                                          │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              ↓                                       │
│  Phase 2: Content Fetching (Python + WebFetch)                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ 각 URL → WebFetch → 실제 기사 본문 추출                        │ │
│  │ 출력: articles-{date}.json                                      │ │
│  │   - url (원본)                                                  │ │
│  │   - original_title (원본 제목)                                  │ │
│  │   - original_content (원본 본문 전체)                           │ │
│  │   - source_name, published_date, fetched_at                     │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              ↓                                       │
│  Phase 3: Signal Generation (LLM - 1회만!)                           │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ 원본 기사 읽기 → 신호 생성 (요약, 분류, 평가)                   │ │
│  │ 출력: signals-{date}.json                                       │ │
│  │   - url (보존)                                                  │ │
│  │   - original_title (보존)                                       │ │
│  │   - original_content (보존, 읽기 전용)                          │ │
│  │   - summary (LLM 생성 - 원본 기반)                              │ │
│  │   - category, significance, confidence, etc.                    │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              ↓                                       │
│  Phase 4: Analysis (Python 규칙 기반 - 내용 변경 금지)               │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ - 중복 필터링 (URL/제목 비교)                                   │ │
│  │ - pSRT 점수 계산 (규칙 기반)                                    │ │
│  │ - 우선순위 계산 (규칙 기반)                                     │ │
│  │ ※ 신호 내용(summary) 변경 금지!                                 │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              ↓                                       │
│  Phase 5: Report (Python 템플릿)                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ - Python으로 보고서 구조 생성                                   │ │
│  │ - summary 필드 그대로 삽입 (재작성 금지!)                       │ │
│  │ - URL 필드 그대로 삽입 (생성 금지!)                             │ │
│  │ - LLM은 "전략적 시사점" 섹션만 담당                             │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 데이터 스키마

### urls-{date}.json (Phase 1 출력)
```json
{
  "scan_date": "2026-01-14",
  "source": "websearch",
  "urls": [
    {
      "url": "https://...",
      "search_query": "AI 반도체 수출 규제",
      "snippet": "검색 결과 스니펫 (참고용, 신호 생성에 사용 안함)",
      "discovered_at": "2026-01-14T10:00:00Z"
    }
  ]
}
```

### articles-{date}.json (Phase 2 출력)
```json
{
  "fetch_date": "2026-01-14",
  "articles": [
    {
      "article_id": "ART-2026-0114-001",
      "url": "https://...",
      "original_title": "실제 기사 제목",
      "original_content": "실제 기사 본문 전체...",
      "source_name": "연합뉴스",
      "published_date": "2026-01-14",
      "fetched_at": "2026-01-14T10:05:00Z",
      "fetch_status": "success",
      "content_length": 1234
    }
  ]
}
```

### signals-{date}.json (Phase 3 출력)
```json
{
  "generation_date": "2026-01-14",
  "signals": [
    {
      "signal_id": "SIG-2026-0114-001",
      "article_id": "ART-2026-0114-001",

      "// 원본 데이터 (불변)": "",
      "url": "https://...",
      "original_title": "실제 기사 제목",
      "original_content": "실제 기사 본문...",
      "source_name": "연합뉴스",
      "published_date": "2026-01-14",

      "// LLM 생성 데이터 (1회만)": "",
      "summary": "기사 내용을 바탕으로 한 신호 요약 (2-3문장)",
      "category": {
        "primary": "Technological",
        "secondary": ["Political"]
      },
      "significance": 4,
      "significance_reason": "중요도 판단 근거",
      "potential_impact": {
        "short_term": "...",
        "mid_term": "...",
        "long_term": "..."
      },
      "key_entities": ["엔비디아", "미국 상무부"],
      "confidence": 0.85,

      "// 메타데이터": "",
      "generated_at": "2026-01-14T10:10:00Z",
      "generator_version": "v4.0"
    }
  ]
}
```

---

## Phase별 구현 상세

### Phase 1: URL Discovery

**담당**: Python 스크립트 (`url_discoverer.py`)
**입력**: 검색 키워드 목록 (config/search-queries.yaml)
**출력**: urls-{date}.json

```python
# 핵심 로직
for query in search_queries:
    results = web_search(query)  # WebSearch 도구 사용
    for result in results:
        urls.append({
            'url': result.url,
            'search_query': query,
            'snippet': result.snippet  # 참고용만
        })

# 중복 URL 제거
unique_urls = deduplicate_by_url(urls)
save_json(f'urls-{date}.json', unique_urls)
```

**주의사항**:
- 스니펫은 참고용으로만 저장
- 신호 생성에 스니펫 사용 금지

---

### Phase 2: Content Fetching

**담당**: Python 스크립트 (`content_fetcher.py`)
**입력**: urls-{date}.json
**출력**: articles-{date}.json

```python
# 핵심 로직
for url_entry in urls:
    content = web_fetch(url_entry['url'])  # WebFetch 도구 사용

    articles.append({
        'article_id': generate_id(),
        'url': url_entry['url'],
        'original_title': extract_title(content),
        'original_content': extract_body(content),
        'source_name': extract_source(content),
        'published_date': extract_date(content),
        'fetched_at': now(),
        'fetch_status': 'success'
    })

save_json(f'articles-{date}.json', articles)
```

**주의사항**:
- 본문 추출 실패 시 해당 URL 제외
- 원본 내용 그대로 저장 (편집 금지)

---

### Phase 3: Signal Generation

**담당**: LLM 에이전트 (`signal-generator`)
**입력**: articles-{date}.json
**출력**: signals-{date}.json

```markdown
## 에이전트 지시사항

당신은 환경스캐닝 신호 생성기입니다.

### 규칙 (반드시 준수)

1. **원본 기사만 읽으세요**: original_content 필드의 내용만 사용
2. **요약은 원본 기반**: 기사에 없는 내용 추가 금지
3. **원본 필드 보존**: url, original_title, original_content는 그대로 복사
4. **창작 금지**: 기사에서 읽은 내용만 요약

### 출력 형식

각 기사에 대해:
1. original_* 필드들은 그대로 복사
2. summary: 원본 기사 내용을 2-3문장으로 요약
3. category: STEEPS 분류
4. significance: 중요도 (1-5)
5. potential_impact: 잠재적 영향
```

**주의사항**:
- 이 단계가 LLM이 내용을 생성하는 유일한 단계
- 이후 단계에서는 summary 필드 변경 금지

---

### Phase 4: Analysis

**담당**: Python 스크립트 (규칙 기반)
**입력**: signals-{date}.json
**출력**: analyzed-signals-{date}.json

```python
# 핵심 로직
for signal in signals:
    # 중복 체크 (URL, 제목 기준)
    if is_duplicate(signal):
        continue

    # pSRT 점수 계산 (규칙 기반)
    signal['pSRT'] = calculate_pSRT(signal)

    # 우선순위 계산 (규칙 기반)
    signal['priority_score'] = calculate_priority(signal)

    # ⚠️ summary, original_content 변경 금지!

    analyzed_signals.append(signal)
```

**주의사항**:
- 내용 필드(summary, original_content) 변경 절대 금지
- 메타데이터 추가만 허용

---

### Phase 5: Report Generation

**담당**: Python 템플릿 + LLM (제한적)
**입력**: analyzed-signals-{date}.json
**출력**: environmental-scan-{date}.md

```python
# Python이 담당하는 부분
report = generate_report_structure(signals)

for signal in top_signals:
    section = f"""
### {signal['signal_id']}: {signal['original_title']}
- **카테고리**: {signal['category']['primary']}
- **중요도**: {'★' * signal['significance']}

**요약**
{signal['summary']}  # ← 그대로 삽입, 재작성 금지!

**출처**: [{signal['source_name']}]({signal['url']}) | 발행일: {signal['published_date']}
"""
    report += section

# LLM이 담당하는 부분 (전략적 시사점만)
strategic_insights = llm_generate_insights(signals)
report += strategic_insights
```

**주의사항**:
- 신호 설명 = summary 필드 그대로 사용
- URL = url 필드 그대로 사용
- LLM은 "전략적 시사점" 섹션만 담당

---

## 검증 체크리스트

### URL-내용 일치 검증
```python
for signal in signals:
    # URL의 실제 내용 다시 fetch
    actual_content = web_fetch(signal['url'])

    # 저장된 original_content와 비교
    if actual_content != signal['original_content']:
        flag_mismatch(signal)

    # summary가 original_content 기반인지 확인
    if not is_based_on(signal['summary'], signal['original_content']):
        flag_hallucination(signal)
```

### 파이프라인 무결성 검증
```python
# Phase 3 출력과 Phase 5 출력 비교
phase3_summary = signals['SIG-001']['summary']
phase5_summary = extract_summary_from_report('SIG-001')

assert phase3_summary == phase5_summary, "Summary was modified!"
```

---

## 마이그레이션 계획

### 단계 1: 새 스크립트 구현
- [ ] url_discoverer.py
- [ ] content_fetcher.py
- [ ] signal_generator.md (에이전트)
- [ ] report_builder.py

### 단계 2: 기존 에이전트 수정
- [ ] 크롤러 에이전트 → URL 수집만
- [ ] 분류기 에이전트 → 제거 또는 Phase 3에 통합
- [ ] 보고서 에이전트 → Python 템플릿으로 대체

### 단계 3: 테스트
- [ ] URL-내용 일치율 100% 확인
- [ ] 파이프라인 전후 summary 일치 확인
- [ ] 실제 링크 클릭 테스트

---

## 예상 효과

| 항목 | 현재 (v3) | 개선 후 (v4) |
|------|----------|-------------|
| URL-내용 일치율 | 0% | 100% |
| 신호 신뢰도 | 낮음 | 높음 |
| 파이프라인 변형 | 매 단계 | 없음 |
| LLM 요약 횟수 | 3-4회 | 1회 |
| 창작/할루시네이션 | 다수 | 0 |
