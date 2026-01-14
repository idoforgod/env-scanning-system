#!/usr/bin/env python3
"""
URL Accessibility Validator
===========================
URL 수집 후, 본문 추출 전에 접근성을 사전 검증

구조적 문제 5.1 해결:
- "URL 수집 ≠ 본문 접근성" 문제 방지
- 접근 불가 URL을 사전에 필터링하여 리소스 낭비 방지

Usage:
    python url_validator.py --input urls.json --output validated-urls.json
    python url_validator.py --url "https://example.com" --quick
"""

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar
from urllib.parse import urlparse

import requests

# 타임아웃 설정
REQUEST_TIMEOUT = 10  # 초
MAX_WORKERS = 10  # 동시 요청 수


@dataclass
class ValidationResult:
    """URL 검증 결과"""

    url: str
    accessible: bool
    status_code: int | None
    reason: str
    response_time_ms: int
    content_type: str | None
    has_paywall: bool
    redirect_url: str | None


class URLValidator:
    """URL 접근성 검증기"""

    # 페이월/차단 감지 키워드
    PAYWALL_INDICATORS: ClassVar[list[str]] = [
        "subscribe",
        "subscription",
        "paywall",
        "premium",
        "login required",
        "sign in to continue",
        "members only",
        "구독",
        "로그인",
        "유료",
    ]

    # 차단 도메인 (역사적으로 실패율 높은 도메인)
    BLOCKED_DOMAINS: ClassVar[list[str]] = [
        "economist.com",  # 페이월
        "wsj.com",  # 페이월
        "ft.com",  # 페이월
        "nytimes.com",  # 일부 페이월
        "bloomberg.com",  # 일부 페이월
    ]

    # 우선 타겟 도메인 (오픈 액세스)
    PREFERRED_DOMAINS: ClassVar[list[str]] = [
        "arxiv.org",
        "nature.com",  # 일부 오픈
        "bbc.com",
        "reuters.com",
        "apnews.com",
        "theguardian.com",
        "techcrunch.com",
        "wired.com",
        "arstechnica.com",
        "mit.edu",
        "hani.co.kr",
        "khan.co.kr",
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            }
        )

    def _is_blocked_domain(self, url: str) -> bool:
        """차단 도메인 여부 확인"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        return any(blocked in domain for blocked in self.BLOCKED_DOMAINS)

    def _is_preferred_domain(self, url: str) -> bool:
        """우선 도메인 여부 확인"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        return any(preferred in domain for preferred in self.PREFERRED_DOMAINS)

    def _detect_paywall(self, html: str) -> bool:
        """페이월 감지"""
        html_lower = html.lower()
        return any(indicator in html_lower for indicator in self.PAYWALL_INDICATORS)

    def validate_url(self, url: str, quick_mode: bool = False) -> ValidationResult:
        """
        단일 URL 검증

        Args:
            url: 검증할 URL
            quick_mode: True면 HEAD 요청만 (빠름), False면 GET 요청 (정확)

        Returns:
            ValidationResult
        """
        start_time = time.time()

        # 차단 도메인 사전 체크
        if self._is_blocked_domain(url):
            return ValidationResult(
                url=url,
                accessible=False,
                status_code=None,
                reason="BLOCKED_DOMAIN",
                response_time_ms=0,
                content_type=None,
                has_paywall=True,
                redirect_url=None,
            )

        try:
            if quick_mode:
                response = self.session.head(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            else:
                response = self.session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)

            response_time = int((time.time() - start_time) * 1000)
            content_type = response.headers.get("Content-Type", "")

            # 리다이렉트 확인
            redirect_url = None
            if response.history:
                redirect_url = response.url

            # 페이월 감지 (GET 요청 시에만)
            has_paywall = False
            if not quick_mode and response.status_code == 200:
                has_paywall = self._detect_paywall(response.text[:5000])

            # 접근성 판단
            accessible = response.status_code == 200 and not has_paywall and "text/html" in content_type

            # 이유 결정
            if response.status_code != 200:
                reason = f"HTTP_{response.status_code}"
            elif has_paywall:
                reason = "PAYWALL_DETECTED"
            elif "text/html" not in content_type:
                reason = f"WRONG_CONTENT_TYPE: {content_type[:30]}"
            else:
                reason = "OK"

            return ValidationResult(
                url=url,
                accessible=accessible,
                status_code=response.status_code,
                reason=reason,
                response_time_ms=response_time,
                content_type=content_type[:50] if content_type else None,
                has_paywall=has_paywall,
                redirect_url=redirect_url,
            )

        except requests.exceptions.Timeout:
            return ValidationResult(
                url=url,
                accessible=False,
                status_code=None,
                reason="TIMEOUT",
                response_time_ms=REQUEST_TIMEOUT * 1000,
                content_type=None,
                has_paywall=False,
                redirect_url=None,
            )
        except requests.exceptions.ConnectionError:
            return ValidationResult(
                url=url,
                accessible=False,
                status_code=None,
                reason="CONNECTION_ERROR",
                response_time_ms=int((time.time() - start_time) * 1000),
                content_type=None,
                has_paywall=False,
                redirect_url=None,
            )
        except Exception as e:
            return ValidationResult(
                url=url,
                accessible=False,
                status_code=None,
                reason=f"ERROR: {str(e)[:50]}",
                response_time_ms=int((time.time() - start_time) * 1000),
                content_type=None,
                has_paywall=False,
                redirect_url=None,
            )

    def validate_urls(
        self, urls: list[str], quick_mode: bool = False, max_workers: int = MAX_WORKERS
    ) -> list[ValidationResult]:
        """
        다중 URL 병렬 검증

        Args:
            urls: 검증할 URL 목록
            quick_mode: HEAD 요청 사용 여부
            max_workers: 동시 요청 수

        Returns:
            ValidationResult 목록
        """
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.validate_url, url, quick_mode): url for url in urls}

            for future in as_completed(future_to_url):
                result = future.result()
                results.append(result)

        return results

    def filter_accessible_urls(self, url_entries: list[dict], quick_mode: bool = True) -> dict[str, Any]:
        """
        접근 가능한 URL만 필터링 (파이프라인 형식 유지)

        Args:
            url_entries: URL 엔트리 목록 (url_merger.py 출력 형식)
                         [{"url": "...", "title_hint": "...", ...}, ...]
            quick_mode: 빠른 검증 모드

        Returns:
            url_merger.py 출력과 동일한 형식 (호환성 유지)
            {
                "urls": [...],  # 접근 가능한 URL만 필터링
                "validation": {...}  # 검증 메타데이터 추가
            }
        """
        # URL 문자열 추출
        urls = [entry.get("url", entry) if isinstance(entry, dict) else entry for entry in url_entries]

        print(f"Validating {len(urls)} URLs...")
        start_time = time.time()

        results = self.validate_urls(urls, quick_mode=quick_mode)

        # URL → 원본 엔트리 매핑
        url_to_entry = {(entry.get("url", entry) if isinstance(entry, dict) else entry): entry for entry in url_entries}

        accessible_entries = []
        blocked = []

        for result in results:
            original_entry = url_to_entry.get(result.url, {"url": result.url})

            if result.accessible:
                # 원본 엔트리에 검증 메타데이터 추가
                entry_copy = dict(original_entry) if isinstance(original_entry, dict) else {"url": original_entry}
                entry_copy["_validation"] = {
                    "response_time_ms": result.response_time_ms,
                    "preferred_domain": self._is_preferred_domain(result.url),
                }
                accessible_entries.append(entry_copy)
            else:
                blocked.append(
                    {
                        "url": result.url,
                        "reason": result.reason,
                        "status_code": result.status_code,
                    }
                )

        # 우선 도메인 먼저 정렬
        accessible_entries.sort(
            key=lambda x: (
                not x.get("_validation", {}).get("preferred_domain", False),
                x.get("_validation", {}).get("response_time_ms", 9999),
            )
        )

        elapsed = time.time() - start_time

        return {
            "validated_at": datetime.now().isoformat(),
            "pipeline_version": "v4",
            "stage": "URL Validation",
            # 파이프라인 호환 형식 유지
            "urls": accessible_entries,
            # 검증 통계 (별도 섹션)
            "validation": {
                "total_urls": len(urls),
                "accessible_count": len(accessible_entries),
                "blocked_count": len(blocked),
                "accessibility_rate": round(len(accessible_entries) / len(urls) * 100, 1) if urls else 0,
                "validation_time_sec": round(elapsed, 2),
                "blocked_urls": blocked,
                "stats": {
                    "by_reason": self._count_by_reason(results),
                    "preferred_domain_count": sum(
                        1 for e in accessible_entries if e.get("_validation", {}).get("preferred_domain")
                    ),
                },
            },
        }

    def _count_by_reason(self, results: list[ValidationResult]) -> dict[str, int]:
        """이유별 카운트"""
        counts: dict[str, int] = {}
        for result in results:
            reason = result.reason.split(":")[0]  # 상세 내용 제외
            counts[reason] = counts.get(reason, 0) + 1
        return counts


def main():
    parser = argparse.ArgumentParser(description="URL Accessibility Validator")
    parser.add_argument("--input", help="Input JSON file with URLs")
    parser.add_argument("--output", help="Output JSON file for results")
    parser.add_argument("--url", help="Single URL to validate")
    parser.add_argument("--quick", action="store_true", help="Quick mode (HEAD only)")

    args = parser.parse_args()

    validator = URLValidator()

    if args.url:
        # 단일 URL 검증
        result = validator.validate_url(args.url, quick_mode=args.quick)
        print(f"URL: {result.url}")
        print(f"Accessible: {result.accessible}")
        print(f"Status: {result.status_code}")
        print(f"Reason: {result.reason}")
        print(f"Response Time: {result.response_time_ms}ms")
        if result.has_paywall:
            print("⚠️ Paywall detected")

    elif args.input:
        # 파일에서 URL 로드
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: File not found: {args.input}")
            sys.exit(1)

        with open(input_path, encoding="utf-8") as f:
            data = json.load(f)

        # URL 엔트리 추출 (원본 구조 유지)
        if isinstance(data, list):
            url_entries = data
        elif isinstance(data, dict):
            url_entries = data.get("urls", data.get("articles", []))
        else:
            print("Error: Invalid input format")
            sys.exit(1)

        # 검증 (원본 엔트리 전달)
        result = validator.filter_accessible_urls(url_entries, quick_mode=args.quick)

        # 결과 출력/저장
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"Results saved to: {args.output}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))

        # 요약 출력
        validation = result.get("validation", {})
        print(
            f"\n✓ Accessible: {validation.get('accessible_count', 0)}/{validation.get('total_urls', 0)} "
            f"({validation.get('accessibility_rate', 0)}%)"
        )
        print(f"✗ Blocked: {validation.get('blocked_count', 0)}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
