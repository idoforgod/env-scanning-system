"""
Pipeline v4: Source of Truth

환경스캐닝 파이프라인의 근본적 재설계.
URL에서 실제 기사를 읽고, 원본 기반 신호를 생성합니다.

핵심 원칙:
1. Source of Truth: 모든 신호는 실제 URL의 실제 본문에서 출발
2. Single Summarization: LLM 요약은 1회만
3. No Content Modification: 분석 단계에서 내용 변경 금지
4. URL-Content Integrity: 보고서 URL은 반드시 실제 기사와 일치

모듈:
- url_discoverer: Phase 1 - URL 수집
- url_merger: Phase 1.5 - URL 병합 및 중복 제거
- content_fetcher: Phase 2 - 본문 수집 (에이전트 프롬프트)
- batch_content_fetcher: Phase 2 - 본문 수집 (직접 배치 처리)
- signal_generator_v4: Phase 3 - 신호 생성 (에이전트)
- report_builder: Phase 4 & 5 - 분석 및 보고서

데이터 흐름:
  url_discoverer → url_merger → [url_validator] → batch_content_fetcher
                                                        ↓
                                              signal_generator_v4
                                                        ↓
                                                  report_builder
"""

from pathlib import Path

__version__ = "4.1.0"  # 구조적 문제 방지 시스템 추가
__author__ = "Environmental Scanning System"

PIPELINE_DIR = Path(__file__).parent


# 모듈 export (지연 로드를 위해 함수로 제공)
def get_url_merger():
    from .url_merger import URLMerger

    return URLMerger


def get_content_fetcher():
    from .content_fetcher import ContentFetcher

    return ContentFetcher


def get_batch_content_fetcher():
    from .batch_content_fetcher import BatchContentFetcher

    return BatchContentFetcher
