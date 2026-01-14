#!/usr/bin/env python3
"""
Post-Scan Analytics
===================
스캔 완료 후 키워드 효과성 분석 및 기록

워크플로우 연동:
- Phase 1 완료 후 자동 호출
- URL 수집 결과를 키워드별로 분석
- 신호 전환 결과 추적

Usage:
    python post_scan_analytics.py --date 2026-01-14
    python post_scan_analytics.py --date 2026-01-14 --phase collection
    python post_scan_analytics.py --date 2026-01-14 --phase conversion
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.scripts.utils.cache_manager import CacheManager
from src.scripts.utils.keyword_tracker import KeywordTracker


class PostScanAnalytics:
    """스캔 후 분석 및 키워드 효과성 추적"""

    def __init__(self, base_path: str | None = None):
        if base_path is None:
            self.base_path = Path(__file__).parent.parent.parent.parent
        else:
            self.base_path = Path(base_path)

        self.tracker = KeywordTracker(str(self.base_path))
        self.cache = CacheManager(str(self.base_path))
        self.steeps_keywords = self.cache.get_steeps_keywords()

    def _match_keyword_to_content(self, text: str) -> list[tuple[str, str]]:
        """
        텍스트에서 STEEPS 키워드 매칭

        Returns:
            [(keyword, category), ...]
        """
        matches = []
        text_lower = text.lower()

        for category, keywords in self.steeps_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matches.append((keyword, category))

        return matches

    def analyze_url_collection(self, date: str) -> dict:
        """
        URL 수집 결과 분석 (Phase 1: Stage A 완료 후)

        Args:
            date: 스캔 날짜 (YYYY-MM-DD)

        Returns:
            분석 결과
        """
        year, month, day = date.split("-")
        raw_dir = self.base_path / "data" / year / month / day / "raw"

        result = {
            "date": date,
            "phase": "collection",
            "analyzed_at": datetime.now().isoformat(),
            "sources": {},
            "by_keyword": defaultdict(lambda: {"count": 0, "sources": []}),
            "by_category": defaultdict(int),
            "total_urls": 0,
        }

        if not raw_dir.exists():
            result["error"] = f"Raw directory not found: {raw_dir}"
            return result

        # 각 크롤러 출력 파일 분석
        source_files = [
            ("naver", f"naver-urls-{date}.json"),
            ("naver_scan", f"naver-scan-{date}.json"),
            ("google", f"google-urls-{date}.json"),
            ("google_news", f"google-news-{date}.json"),
            ("global", f"global-urls-{date}.json"),
            ("global_news", f"global-news-{date}.json"),
            ("websearch", f"websearch-urls-{date}.json"),
            ("steeps", f"steeps-scan-{date}.json"),
        ]

        for source_name, filename in source_files:
            file_path = raw_dir / filename
            if not file_path.exists():
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)

                urls = []
                if isinstance(data, list):
                    urls = data
                elif isinstance(data, dict):
                    urls = data.get("urls", data.get("articles", data.get("signals", [])))

                result["sources"][source_name] = {
                    "file": filename,
                    "count": len(urls),
                }
                result["total_urls"] += len(urls)

                # 각 URL의 제목/내용에서 키워드 매칭
                for item in urls:
                    if isinstance(item, dict):
                        text = " ".join(
                            [
                                str(item.get("title", "")),
                                str(item.get("original_title", "")),
                                str(item.get("description", "")),
                                str(item.get("keyword", "")),
                            ]
                        )
                    else:
                        text = str(item)

                    matches = self._match_keyword_to_content(text)
                    for keyword, category in matches:
                        result["by_keyword"][keyword]["count"] += 1
                        if source_name not in result["by_keyword"][keyword]["sources"]:
                            result["by_keyword"][keyword]["sources"].append(source_name)
                        result["by_category"][category] += 1

            except (json.JSONDecodeError, KeyError) as e:
                result["sources"][source_name] = {"file": filename, "error": str(e)}

        # KeywordTracker에 기록
        for keyword, stats in result["by_keyword"].items():
            # 카테고리 찾기
            category = None
            for cat, kws in self.steeps_keywords.items():
                if keyword in kws:
                    category = cat
                    break

            if category:
                self.tracker.record_collection(
                    date=date,
                    keyword=keyword,
                    category=category,
                    urls_collected=stats["count"],
                )

        # defaultdict를 일반 dict로 변환
        result["by_keyword"] = dict(result["by_keyword"])
        result["by_category"] = dict(result["by_category"])

        return result

    def analyze_signal_conversion(self, date: str) -> dict:
        """
        신호 전환 결과 분석 (Phase 2 완료 후)

        Args:
            date: 스캔 날짜

        Returns:
            분석 결과
        """
        year, month, day = date.split("-")
        structured_dir = self.base_path / "data" / year / month / day / "structured"
        analysis_dir = self.base_path / "data" / year / month / day / "analysis"

        result = {
            "date": date,
            "phase": "conversion",
            "analyzed_at": datetime.now().isoformat(),
            "total_signals": 0,
            "by_category": defaultdict(lambda: {"count": 0, "avg_priority": 0, "priorities": []}),
            "by_keyword": defaultdict(lambda: {"count": 0, "priorities": []}),
        }

        # 구조화된 신호 파일 읽기
        signals_file = structured_dir / f"structured-signals-{date}.json"
        priority_file = analysis_dir / f"priority-ranked-{date}.json"

        if not signals_file.exists():
            result["error"] = f"Signals file not found: {signals_file}"
            return result

        try:
            with open(signals_file, encoding="utf-8") as f:
                data = json.load(f)

            signals = data.get("signals", [])
            result["total_signals"] = len(signals)

            # 우선순위 정보 로드
            priority_map = {}
            if priority_file.exists():
                with open(priority_file, encoding="utf-8") as f:
                    priority_data = json.load(f)
                for ranking in priority_data.get("rankings", []):
                    signal_id = ranking.get("signal_id")
                    priority_map[signal_id] = ranking.get("weighted_score", 0)

            # 각 신호 분석
            for signal in signals:
                category = signal.get("category", "Unknown")
                signal_id = signal.get("signal_id", "")
                priority = priority_map.get(signal_id, signal.get("priority_score", 5.0))

                result["by_category"][category]["count"] += 1
                result["by_category"][category]["priorities"].append(priority)

                # 신호 내용에서 키워드 매칭
                text = " ".join(
                    [
                        str(signal.get("title", "")),
                        str(signal.get("summary", "")),
                        str(signal.get("original_title", "")),
                    ]
                )

                matches = self._match_keyword_to_content(text)
                for keyword, _ in matches:
                    result["by_keyword"][keyword]["count"] += 1
                    result["by_keyword"][keyword]["priorities"].append(priority)

            # 평균 우선순위 계산
            for _category, stats in result["by_category"].items():
                if stats["priorities"]:
                    stats["avg_priority"] = round(sum(stats["priorities"]) / len(stats["priorities"]), 2)

            # KeywordTracker에 전환 기록
            for keyword, stats in result["by_keyword"].items():
                if stats["count"] > 0:
                    self.tracker.record_conversion(
                        date=date,
                        keyword=keyword,
                        signals_created=stats["count"],
                        priority_scores=stats["priorities"],
                    )

        except (json.JSONDecodeError, KeyError) as e:
            result["error"] = str(e)

        # defaultdict를 일반 dict로 변환
        result["by_category"] = {
            k: {"count": v["count"], "avg_priority": v["avg_priority"]} for k, v in result["by_category"].items()
        }
        result["by_keyword"] = {
            k: {
                "count": v["count"],
                "avg_priority": round(sum(v["priorities"]) / len(v["priorities"]), 2) if v["priorities"] else 0,
            }
            for k, v in result["by_keyword"].items()
        }

        return result

    def run_full_analysis(self, date: str) -> dict:
        """
        전체 분석 실행 (수집 + 전환)

        Args:
            date: 스캔 날짜

        Returns:
            전체 분석 결과
        """
        collection = self.analyze_url_collection(date)
        conversion = self.analyze_signal_conversion(date)

        # 결과 저장
        year, month, day = date.split("-")
        metrics_dir = self.base_path / "data" / year / month / day / "analysis"
        metrics_dir.mkdir(parents=True, exist_ok=True)

        output_file = metrics_dir / f"keyword-analytics-{date}.json"
        result = {
            "date": date,
            "analyzed_at": datetime.now().isoformat(),
            "collection": collection,
            "conversion": conversion,
            "summary": {
                "total_urls_collected": collection.get("total_urls", 0),
                "total_signals_created": conversion.get("total_signals", 0),
                "conversion_rate": round(
                    conversion.get("total_signals", 0) / max(collection.get("total_urls", 0), 1) * 100, 1
                ),
                "keywords_tracked": len(collection.get("by_keyword", {})),
            },
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"Analysis saved to: {output_file}")
        return result


def main():
    parser = argparse.ArgumentParser(description="Post-scan keyword analytics")
    parser.add_argument("--date", required=True, help="Scan date (YYYY-MM-DD)")
    parser.add_argument(
        "--phase",
        choices=["collection", "conversion", "full"],
        default="full",
        help="Analysis phase",
    )
    parser.add_argument("--output", help="Output file path (optional)")

    args = parser.parse_args()

    analytics = PostScanAnalytics()

    if args.phase == "collection":
        result = analytics.analyze_url_collection(args.date)
    elif args.phase == "conversion":
        result = analytics.analyze_signal_conversion(args.date)
    else:
        result = analytics.run_full_analysis(args.date)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Output saved to: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
