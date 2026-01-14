#!/usr/bin/env python3
"""
Pipeline v4 - Phase 1: URL Discovery

웹 검색을 통해 URL만 수집합니다.
스니펫은 참고용으로만 저장하고, 신호 생성에는 사용하지 않습니다.

원칙:
- URL만 수집, 내용 수집은 Phase 2에서
- 스니펫 기반 창작 금지
- 중복 URL 제거

사용법:
    python url_discoverer.py <date>
    python url_discoverer.py 2026-01-14
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class URLDiscoverer:
    """URL 수집기 - 검색 결과에서 URL만 추출"""

    def __init__(self, base_path: str | None = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.urls = []
        self.stats = {"queries_executed": 0, "total_results": 0, "unique_urls": 0, "duplicates_removed": 0}

    def load_search_queries(self) -> list[dict[str, Any]]:
        """검색 쿼리 목록 로드"""

        # STEEPS 카테고리별 검색 쿼리
        queries = [
            # Social
            {"query": "인구 변화 트렌드 2026", "category": "Social"},
            {"query": "세대 갈등 사회 변화", "category": "Social"},
            {"query": "원격근무 하이브리드 근무 트렌드", "category": "Social"},
            # Technological
            {"query": "AI 인공지능 최신 동향 2026", "category": "Technological"},
            {"query": "반도체 수출 규제 기술", "category": "Technological"},
            {"query": "양자컴퓨터 기술 발전", "category": "Technological"},
            {"query": "자율주행 로보택시 허가", "category": "Technological"},
            # Economic
            {"query": "고용 시장 취업자 동향 2026", "category": "Economic"},
            {"query": "금리 인플레이션 경제 전망", "category": "Economic"},
            {"query": "스타트업 투자 유니콘", "category": "Economic"},
            # Environmental
            {"query": "기후변화 탄소중립 정책 2026", "category": "Environmental"},
            {"query": "재생에너지 태양광 풍력", "category": "Environmental"},
            {"query": "ESG 환경 투자 동향", "category": "Environmental"},
            # Political
            {"query": "정치 정책 변화 2026", "category": "Political"},
            {"query": "국제 관계 지정학 갈등", "category": "Political"},
            {"query": "규제 정책 입법 동향", "category": "Political"},
        ]

        return queries

    def discover_urls(self, search_results: list[dict]) -> None:
        """검색 결과에서 URL 추출 (실제로는 에이전트가 WebSearch 실행)"""

        for result in search_results:
            url = result.get("url", "")

            if not url or not url.startswith("http"):
                continue

            # URL 정규화
            url = self.normalize_url(url)

            self.urls.append(
                {
                    "url": url,
                    "search_query": result.get("query", ""),
                    "title_hint": result.get("title", ""),  # 힌트용, 신호 생성에 사용 안함
                    "snippet_hint": result.get("snippet", ""),  # 힌트용, 신호 생성에 사용 안함
                    "category_hint": result.get("category", ""),
                    "discovered_at": datetime.now().isoformat(),
                }
            )

            self.stats["total_results"] += 1

    def normalize_url(self, url: str) -> str:
        """URL 정규화"""
        # 쿼리 파라미터 중 불필요한 것 제거
        import urllib.parse

        parsed = urllib.parse.urlparse(url)

        # 추적 파라미터 제거
        tracking_params = ["utm_source", "utm_medium", "utm_campaign", "fbclid", "gclid"]
        query_params = urllib.parse.parse_qs(parsed.query)
        filtered_params = {k: v for k, v in query_params.items() if k not in tracking_params}

        new_query = urllib.parse.urlencode(filtered_params, doseq=True)
        normalized = parsed._replace(query=new_query, fragment="")

        return urllib.parse.urlunparse(normalized)

    def deduplicate(self) -> None:
        """중복 URL 제거"""
        seen_urls = set()
        unique_urls = []

        for entry in self.urls:
            url = entry["url"]
            if url not in seen_urls:
                seen_urls.add(url)
                unique_urls.append(entry)
            else:
                self.stats["duplicates_removed"] += 1

        self.urls = unique_urls
        self.stats["unique_urls"] = len(unique_urls)

    def save(self, date: str) -> str:
        """결과 저장"""
        year, month, day = date.split("-")
        output_dir = self.base_path / f"data/{year}/{month}/{day}/raw"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"urls-{date}.json"

        output = {
            "scan_date": date,
            "generated_at": datetime.now().isoformat(),
            "phase": "Phase 1: URL Discovery",
            "stats": self.stats,
            "note": "snippet_hint와 title_hint는 참고용입니다. 신호 생성에는 실제 기사 본문만 사용하세요.",
            "urls": self.urls,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        return str(output_path)


def create_discovery_prompt(queries: list[dict]) -> str:
    """에이전트용 검색 프롬프트 생성"""

    prompt = """## URL Discovery Task

다음 검색 쿼리들을 WebSearch로 실행하고, 결과 URL을 수집하세요.

### 규칙
1. 각 쿼리당 최대 10개 URL 수집
2. 뉴스 기사 URL만 수집 (블로그, 커뮤니티 제외)
3. 최근 7일 이내 기사 우선
4. URL만 수집, 내용 요약 금지

### 검색 쿼리 목록
"""

    for q in queries:
        prompt += f"- [{q['category']}] {q['query']}\n"

    prompt += """
### 출력 형식

각 검색 결과에 대해:
```json
{
  "url": "https://...",
  "query": "검색어",
  "title": "기사 제목 (검색 결과에서)",
  "snippet": "스니펫 (검색 결과에서)",
  "category": "STEEPS 카테고리"
}
```

※ title과 snippet은 참고용입니다. Phase 2에서 실제 기사를 읽습니다.
"""

    return prompt


def main():
    if len(sys.argv) < 2:
        print("Usage: python url_discoverer.py <date>")
        print("Example: python url_discoverer.py 2026-01-14")
        sys.exit(1)

    date = sys.argv[1]
    base_path = Path(__file__).parent.parent.parent.parent

    discoverer = URLDiscoverer(base_path)

    print(f"=== Phase 1: URL Discovery - {date} ===\n")

    # 검색 쿼리 로드
    queries = discoverer.load_search_queries()
    print(f"1. Loaded {len(queries)} search queries")

    # 에이전트 프롬프트 생성 (실제 실행은 에이전트가)
    prompt = create_discovery_prompt(queries)
    prompt_path = (
        base_path
        / f"data/{date.replace('-', '/')[:7].replace('-', '/')}/{date.split('-')[2]}/raw/discovery-prompt-{date}.md"
    )
    prompt_path.parent.mkdir(parents=True, exist_ok=True)

    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"2. Discovery prompt saved: {prompt_path.name}")
    print("\n다음 단계:")
    print("  1. 에이전트가 위 프롬프트로 WebSearch 실행")
    print(f"  2. 결과를 urls-{date}.json으로 저장")
    print("  3. Phase 2 (content_fetcher.py) 실행")

    return 0


if __name__ == "__main__":
    sys.exit(main())
