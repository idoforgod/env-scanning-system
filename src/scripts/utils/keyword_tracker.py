"""
Keyword Effectiveness Tracker
=============================
키워드별 효과성 측정 및 성과 등급 산정

메트릭:
- 수집 건수: 키워드별 URL 수집 수
- 신호 전환율: 수집 URL → 최종 신호 비율
- 우선순위 점수: 생성된 신호의 평균 우선순위
- 0건 비율: 결과 없는 키워드 비율

성과 등급:
- A (우수): 월 20건+, 전환율 20%+
- B (양호): 월 10-19건, 전환율 15%+
- C (보통): 월 5-9건, 전환율 10%+
- D (저조): 월 1-4건, 전환율 <10%
- F (비효과): 3개월 연속 0건
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


class KeywordTracker:
    """키워드 효과성 추적기"""

    def __init__(self, base_path: str | None = None):
        if base_path is None:
            self.base_path = Path(__file__).parent.parent.parent.parent
        else:
            self.base_path = Path(base_path)

        self.metrics_dir = self.base_path / "data" / "metrics"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        self.metrics_file = self.metrics_dir / "keyword-effectiveness.json"
        self._load_metrics()

    def _load_metrics(self) -> None:
        """기존 메트릭 로드"""
        if self.metrics_file.exists():
            with open(self.metrics_file, encoding="utf-8") as f:
                self._metrics = json.load(f)
        else:
            self._metrics = {
                "last_updated": None,
                "monthly_data": {},
                "keyword_stats": {},
                "category_stats": {},
            }

    def _save_metrics(self) -> None:
        """메트릭 저장"""
        self._metrics["last_updated"] = datetime.now().isoformat()
        with open(self.metrics_file, "w", encoding="utf-8") as f:
            json.dump(self._metrics, f, ensure_ascii=False, indent=2)

    def record_collection(self, date: str, keyword: str, category: str, urls_collected: int) -> None:
        """
        URL 수집 결과 기록

        Args:
            date: 스캔 날짜 (YYYY-MM-DD)
            keyword: 사용된 키워드
            category: STEEPS 카테고리
            urls_collected: 수집된 URL 수
        """
        month = date[:7]  # YYYY-MM

        if month not in self._metrics["monthly_data"]:
            self._metrics["monthly_data"][month] = {}

        if keyword not in self._metrics["monthly_data"][month]:
            self._metrics["monthly_data"][month][keyword] = {
                "category": category,
                "total_collected": 0,
                "total_converted": 0,
                "priority_scores": [],
                "daily_counts": {},
            }

        entry = self._metrics["monthly_data"][month][keyword]
        entry["total_collected"] += urls_collected
        entry["daily_counts"][date] = entry["daily_counts"].get(date, 0) + urls_collected

        self._save_metrics()

    def record_conversion(self, date: str, keyword: str, signals_created: int, priority_scores: list[float]) -> None:
        """
        신호 전환 결과 기록

        Args:
            date: 스캔 날짜
            keyword: 키워드
            signals_created: 생성된 신호 수
            priority_scores: 생성된 신호들의 우선순위 점수
        """
        month = date[:7]

        if month not in self._metrics["monthly_data"]:
            return
        if keyword not in self._metrics["monthly_data"][month]:
            return

        entry = self._metrics["monthly_data"][month][keyword]
        entry["total_converted"] += signals_created
        entry["priority_scores"].extend(priority_scores)

        self._save_metrics()

    def calculate_grade(self, collected: int, conversion_rate: float) -> str:
        """
        성과 등급 계산

        Args:
            collected: 월간 수집 건수
            conversion_rate: 신호 전환율 (0-1)

        Returns:
            등급 (A, B, C, D, F)
        """
        if collected >= 20 and conversion_rate >= 0.20:
            return "A"
        elif collected >= 10 and conversion_rate >= 0.15:
            return "B"
        elif collected >= 5 and conversion_rate >= 0.10:
            return "C"
        elif collected >= 1:
            return "D"
        else:
            return "F"

    def get_monthly_report(self, month: str) -> dict[str, Any]:
        """
        월간 키워드 효과성 리포트

        Args:
            month: 대상 월 (YYYY-MM)

        Returns:
            월간 리포트 딕셔너리
        """
        if month not in self._metrics["monthly_data"]:
            return {"error": f"No data for {month}"}

        data = self._metrics["monthly_data"][month]
        report = {
            "month": month,
            "total_keywords_used": len(data),
            "keywords": [],
            "by_category": defaultdict(list),
            "by_grade": defaultdict(list),
            "summary": {},
        }

        total_collected = 0
        total_converted = 0
        zero_count = 0

        for keyword, stats in data.items():
            collected = stats["total_collected"]
            converted = stats["total_converted"]
            conversion_rate = converted / collected if collected > 0 else 0
            avg_priority = (
                sum(stats["priority_scores"]) / len(stats["priority_scores"]) if stats["priority_scores"] else 0
            )
            grade = self.calculate_grade(collected, conversion_rate)

            keyword_report = {
                "keyword": keyword,
                "category": stats["category"],
                "collected": collected,
                "converted": converted,
                "conversion_rate": round(conversion_rate * 100, 1),
                "avg_priority": round(avg_priority, 2),
                "grade": grade,
            }

            report["keywords"].append(keyword_report)
            report["by_category"][stats["category"]].append(keyword_report)
            report["by_grade"][grade].append(keyword)

            total_collected += collected
            total_converted += converted
            if collected == 0:
                zero_count += 1

        # 정렬 (수집 건수 기준 내림차순)
        report["keywords"].sort(key=lambda x: x["collected"], reverse=True)

        # 요약 통계
        overall_conversion = total_converted / total_collected if total_collected > 0 else 0
        report["summary"] = {
            "total_collected": total_collected,
            "total_converted": total_converted,
            "overall_conversion_rate": round(overall_conversion * 100, 1),
            "zero_result_keywords": zero_count,
            "zero_result_rate": round(zero_count / len(data) * 100, 1) if data else 0,
            "grade_distribution": {grade: len(keywords) for grade, keywords in report["by_grade"].items()},
        }

        return report

    def get_retirement_candidates(self, months: int = 3) -> list[str]:
        """
        퇴출 후보 키워드 식별 (연속 F등급)

        Args:
            months: 연속 F등급 기준 개월 수

        Returns:
            퇴출 후보 키워드 목록
        """
        monthly_data = self._metrics.get("monthly_data", {})
        sorted_months = sorted(monthly_data.keys(), reverse=True)[:months]

        if len(sorted_months) < months:
            return []

        # 모든 월에서 F등급인 키워드 찾기
        f_grade_sets = []
        for month in sorted_months:
            f_keywords = set()
            for keyword, stats in monthly_data[month].items():
                if stats["total_collected"] == 0:
                    f_keywords.add(keyword)
            f_grade_sets.append(f_keywords)

        # 교집합 = 연속 F등급
        if f_grade_sets:
            candidates = f_grade_sets[0]
            for s in f_grade_sets[1:]:
                candidates = candidates.intersection(s)
            return list(candidates)

        return []

    def get_top_performers(self, month: str, top_n: int = 10) -> list[dict]:
        """
        상위 성과 키워드 조회

        Args:
            month: 대상 월
            top_n: 상위 N개

        Returns:
            상위 성과 키워드 목록
        """
        report = self.get_monthly_report(month)
        if "error" in report:
            return []

        return report["keywords"][:top_n]

    def analyze_scan_results(self, date: str) -> dict[str, Any]:
        """
        일일 스캔 결과 분석 및 메트릭 추출

        Args:
            date: 스캔 날짜 (YYYY-MM-DD)

        Returns:
            분석 결과
        """
        year, month, day = date.split("-")
        data_dir = self.base_path / "data" / year / month / day

        result = {
            "date": date,
            "keywords_analyzed": 0,
            "by_category": {},
            "by_source": {},
        }

        # raw 폴더에서 URL 수집 결과 분석
        raw_dir = data_dir / "raw"
        if raw_dir.exists():
            for file in raw_dir.glob("*-urls-*.json"):
                try:
                    with open(file, encoding="utf-8") as f:
                        data = json.load(f)
                    # URL 수집 파일 구조에 따라 분석
                    if isinstance(data, list):
                        result["by_source"][file.stem] = len(data)
                    elif isinstance(data, dict) and "urls" in data:
                        result["by_source"][file.stem] = len(data["urls"])
                except (json.JSONDecodeError, KeyError):
                    continue

        # structured 폴더에서 신호 전환 결과 분석
        structured_dir = data_dir / "structured"
        if structured_dir.exists():
            signals_file = structured_dir / f"structured-signals-{date}.json"
            if signals_file.exists():
                try:
                    with open(signals_file, encoding="utf-8") as f:
                        signals = json.load(f)
                    if isinstance(signals, dict) and "signals" in signals:
                        for signal in signals["signals"]:
                            category = signal.get("category", "Unknown")
                            if category not in result["by_category"]:
                                result["by_category"][category] = {
                                    "count": 0,
                                    "priority_scores": [],
                                }
                            result["by_category"][category]["count"] += 1
                            if "priority_score" in signal:
                                result["by_category"][category]["priority_scores"].append(signal["priority_score"])
                except (json.JSONDecodeError, KeyError):
                    pass

        return result


def main():
    """CLI 실행"""
    import sys

    tracker = KeywordTracker()

    if len(sys.argv) < 2:
        print("Usage: python keyword_tracker.py <command> [args]")
        print("Commands:")
        print("  report <YYYY-MM>  - 월간 리포트 출력")
        print("  top <YYYY-MM>     - 상위 성과 키워드")
        print("  retire            - 퇴출 후보 키워드")
        print("  analyze <date>    - 일일 스캔 결과 분석")
        sys.exit(1)

    command = sys.argv[1]

    if command == "report" and len(sys.argv) > 2:
        report = tracker.get_monthly_report(sys.argv[2])
        print(json.dumps(report, ensure_ascii=False, indent=2))

    elif command == "top" and len(sys.argv) > 2:
        top = tracker.get_top_performers(sys.argv[2])
        for i, kw in enumerate(top, 1):
            print(f"{i}. {kw['keyword']} ({kw['category']}): {kw['collected']}건, 전환율 {kw['conversion_rate']}%")

    elif command == "retire":
        candidates = tracker.get_retirement_candidates()
        if candidates:
            print("퇴출 후보 키워드 (3개월 연속 0건):")
            for kw in candidates:
                print(f"  - {kw}")
        else:
            print("퇴출 후보 없음")

    elif command == "analyze" and len(sys.argv) > 2:
        result = tracker.analyze_scan_results(sys.argv[2])
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
