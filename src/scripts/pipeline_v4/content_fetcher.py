#!/usr/bin/env python3
"""
Pipeline v4 - Phase 2: Content Fetching

각 URL에서 실제 기사 본문을 가져옵니다.
이 본문이 신호 생성의 유일한 Source of Truth입니다.

원칙:
- 실제 기사 본문 전체 저장
- 원본 그대로 보존 (편집 금지)
- 본문 추출 실패 시 해당 URL 제외

사용법:
    python content_fetcher.py <date>
    python content_fetcher.py 2026-01-14
"""

import json
import sys
from datetime import datetime
from pathlib import Path


class ContentFetcher:
    """본문 수집기 - URL에서 실제 기사 내용 추출"""

    def __init__(self, base_path: str | None = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.articles = []
        self.stats = {"total_urls": 0, "fetch_success": 0, "fetch_failed": 0, "content_too_short": 0}
        self.failed_urls = []

    def load_urls(self, date: str) -> list[dict]:
        """Phase 1에서 생성된 URL 목록 로드"""
        year, month, day = date.split("-")
        urls_path = self.base_path / f"data/{year}/{month}/{day}/raw/urls-{date}.json"

        if not urls_path.exists():
            raise FileNotFoundError(f"URL file not found: {urls_path}")

        with open(urls_path, encoding="utf-8") as f:
            data = json.load(f)

        return data.get("urls", [])

    def generate_article_id(self, date: str, index: int) -> str:
        """기사 ID 생성"""
        return f"ART-{date.replace('-', '')}-{index:03d}"

    def create_fetch_prompt(self, urls: list[dict], date: str) -> str:
        """에이전트용 본문 수집 프롬프트 생성"""

        prompt = f"""## Content Fetching Task - {date}

다음 URL들에서 실제 기사 본문을 수집하세요.

### 핵심 규칙 (반드시 준수)

1. **WebFetch로 실제 페이지 읽기**: 각 URL에 WebFetch 도구 사용
2. **본문 전체 추출**: 기사 본문을 최대한 완전하게 추출
3. **원본 그대로 저장**: 요약하거나 편집하지 말 것
4. **메타데이터 추출**: 제목, 발행일, 매체명도 함께 추출

### URL 목록 ({len(urls)}개)

"""
        for i, url_entry in enumerate(urls[:50], 1):  # 최대 50개
            prompt += f"{i}. {url_entry['url']}\n"
            prompt += f"   힌트: {url_entry.get('title_hint', 'N/A')[:50]}\n\n"

        prompt += """
### 출력 형식 (각 기사에 대해)

```json
{
  "article_id": "ART-20260114-001",
  "url": "https://...",
  "original_title": "기사 원본 제목 (페이지에서 추출)",
  "original_content": "기사 본문 전체 (최소 200자 이상)",
  "source_name": "매체명",
  "published_date": "2026-01-14",
  "fetched_at": "2026-01-14T10:00:00Z",
  "fetch_status": "success"
}
```

### 주의사항

- **본문이 200자 미만이면 제외**
- **광고, 관련기사 목록 제외**
- **로그인 필요 기사는 fetch_status: "login_required"로 표시**
- **접근 불가 시 fetch_status: "failed"로 표시**
- **original_content는 요약 금지, 원본 그대로!**
"""
        return prompt

    def validate_article(self, article: dict) -> bool:
        """기사 유효성 검사"""
        content = article.get("original_content", "")

        # 최소 길이 검사
        if len(content) < 200:
            self.stats["content_too_short"] += 1
            return False

        # 필수 필드 검사
        required_fields = ["url", "original_title", "original_content"]
        return all(article.get(field) for field in required_fields)

    def process_fetched_articles(self, fetched_data: list[dict], date: str) -> None:
        """수집된 기사 처리"""

        for i, article in enumerate(fetched_data, 1):
            article["article_id"] = self.generate_article_id(date, i)

            if article.get("fetch_status") == "success" and self.validate_article(article):
                self.articles.append(article)
                self.stats["fetch_success"] += 1
            else:
                self.failed_urls.append(
                    {"url": article.get("url"), "reason": article.get("fetch_status", "validation_failed")}
                )
                self.stats["fetch_failed"] += 1

    def save(self, date: str) -> str:
        """결과 저장"""
        year, month, day = date.split("-")
        output_dir = self.base_path / f"data/{year}/{month}/{day}/raw"
        output_dir.mkdir(parents=True, exist_ok=True)

        # 기사 저장
        articles_path = output_dir / f"articles-{date}.json"
        output = {
            "fetch_date": date,
            "generated_at": datetime.now().isoformat(),
            "phase": "Phase 2: Content Fetching",
            "stats": self.stats,
            "note": "original_content는 신호 생성의 Source of Truth입니다. 수정 금지.",
            "articles": self.articles,
        }

        with open(articles_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        # 실패 URL 저장
        if self.failed_urls:
            failed_path = output_dir / f"failed-urls-{date}.json"
            with open(failed_path, "w", encoding="utf-8") as f:
                json.dump(self.failed_urls, f, ensure_ascii=False, indent=2)

        return str(articles_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python content_fetcher.py <date>")
        print("Example: python content_fetcher.py 2026-01-14")
        sys.exit(1)

    date = sys.argv[1]
    base_path = Path(__file__).parent.parent.parent.parent

    fetcher = ContentFetcher(base_path)

    print(f"=== Phase 2: Content Fetching - {date} ===\n")

    # URL 로드
    try:
        urls = fetcher.load_urls(date)
        print(f"1. Loaded {len(urls)} URLs from Phase 1")
        fetcher.stats["total_urls"] = len(urls)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("먼저 Phase 1 (url_discoverer.py)을 실행하세요.")
        sys.exit(1)

    # 에이전트 프롬프트 생성
    prompt = fetcher.create_fetch_prompt(urls, date)
    year, month, day = date.split("-")
    prompt_path = base_path / f"data/{year}/{month}/{day}/raw/fetch-prompt-{date}.md"

    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"2. Fetch prompt saved: {prompt_path.name}")
    print("\n다음 단계:")
    print("  1. 에이전트가 위 프롬프트로 WebFetch 실행")
    print(f"  2. 결과를 articles-{date}.json으로 저장")
    print("  3. Phase 3 (signal_generator) 실행")

    return 0


if __name__ == "__main__":
    sys.exit(main())
