#!/usr/bin/env python3
"""
Review Scheduler
================
월간/분기별 키워드 리뷰 일정 관리 및 자동 실행

Usage:
    python review_scheduler.py check        # 리뷰 필요 여부 확인
    python review_scheduler.py monthly      # 월간 리뷰 실행
    python review_scheduler.py quarterly    # 분기별 리뷰 실행
    python review_scheduler.py status       # 리뷰 상태 확인
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.scripts.utils.keyword_manager import KeywordManager
from src.scripts.utils.keyword_tracker import KeywordTracker


class ReviewScheduler:
    """리뷰 일정 관리자"""

    def __init__(self, base_path: str | None = None):
        if base_path is None:
            self.base_path = Path(__file__).parent.parent.parent.parent
        else:
            self.base_path = Path(base_path)

        self.manager = KeywordManager(str(self.base_path))
        self.tracker = KeywordTracker(str(self.base_path))

        self.schedule_file = self.base_path / "data" / "metrics" / "review-schedule.json"
        self._load_schedule()

    def _load_schedule(self) -> None:
        """일정 로드"""
        if self.schedule_file.exists():
            with open(self.schedule_file, encoding="utf-8") as f:
                self._schedule = json.load(f)
        else:
            self._schedule = {
                "last_monthly_review": None,
                "last_quarterly_review": None,
                "next_monthly_due": None,
                "next_quarterly_due": None,
                "review_history": [],
            }

    def _save_schedule(self) -> None:
        """일정 저장"""
        self.schedule_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.schedule_file, "w", encoding="utf-8") as f:
            json.dump(self._schedule, f, ensure_ascii=False, indent=2)

    def get_current_quarter(self, date: datetime | None = None) -> tuple[int, int]:
        """현재 분기 반환 (년도, 분기)"""
        if date is None:
            date = datetime.now()
        quarter = (date.month - 1) // 3 + 1
        return date.year, quarter

    def is_month_end(self, days_before: int = 3) -> bool:
        """월말 여부 확인 (N일 전부터 True)"""
        today = datetime.now()
        # 다음 달 1일
        if today.month == 12:
            next_month_1st = datetime(today.year + 1, 1, 1)
        else:
            next_month_1st = datetime(today.year, today.month + 1, 1)

        days_until_month_end = (next_month_1st - today).days
        return days_until_month_end <= days_before

    def is_quarter_end(self, days_before: int = 7) -> bool:
        """분기말 여부 확인 (N일 전부터 True)"""
        today = datetime.now()
        quarter_end_months = [3, 6, 9, 12]

        if today.month in quarter_end_months:
            return self.is_month_end(days_before)
        return False

    def check_review_needed(self) -> dict:
        """리뷰 필요 여부 확인"""
        today = datetime.now()
        current_month = today.strftime("%Y-%m")
        current_year, current_quarter = self.get_current_quarter()
        current_quarter_str = f"{current_year}-Q{current_quarter}"

        result = {
            "date": today.isoformat(),
            "monthly_review_needed": False,
            "quarterly_review_needed": False,
            "messages": [],
        }

        # 월간 리뷰 체크
        last_monthly = self._schedule.get("last_monthly_review")
        if last_monthly:
            last_month = last_monthly[:7]
            if last_month != current_month and self.is_month_end():
                result["monthly_review_needed"] = True
                result["messages"].append(f"월간 키워드 리뷰 필요 (마지막: {last_month}, 현재: {current_month})")
        elif self.is_month_end():
            result["monthly_review_needed"] = True
            result["messages"].append("월간 키워드 리뷰가 한 번도 실행되지 않음")

        # 분기별 리뷰 체크
        last_quarterly = self._schedule.get("last_quarterly_review")
        if last_quarterly:
            if last_quarterly != current_quarter_str and self.is_quarter_end():
                result["quarterly_review_needed"] = True
                result["messages"].append(
                    f"분기별 키워드 리뷰 필요 (마지막: {last_quarterly}, 현재: {current_quarter_str})"
                )
        elif self.is_quarter_end():
            result["quarterly_review_needed"] = True
            result["messages"].append("분기별 키워드 리뷰가 한 번도 실행되지 않음")

        if not result["messages"]:
            result["messages"].append("현재 리뷰 일정 없음")

        return result

    def run_monthly_review(self, month: str | None = None) -> dict:
        """월간 리뷰 실행"""
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        print(f"=== 월간 키워드 리뷰 시작: {month} ===\n")

        # KeywordManager로 리뷰 실행
        review_result = self.manager.monthly_review(month)

        # 일정 업데이트
        self._schedule["last_monthly_review"] = datetime.now().isoformat()
        self._schedule["review_history"].append(
            {
                "type": "monthly",
                "month": month,
                "date": datetime.now().isoformat(),
                "summary": review_result.get("summary", {}),
            }
        )
        self._save_schedule()

        # 결과 출력
        print("\n📊 리뷰 결과 요약:")
        summary = review_result.get("summary", {})
        print(f"  - 총 키워드: {summary.get('total_keywords', 'N/A')}개")
        print(f"  - 등급 분포: {summary.get('grade_distribution', {})}")
        print(f"  - 0건 비율: {summary.get('zero_result_rate', 'N/A')}%")

        if review_result.get("action_items"):
            print("\n⚠️ 권고 조치:")
            for item in review_result["action_items"]:
                print(f"  - {item}")

        if review_result.get("retirement_candidates"):
            print("\n🗑️ 퇴출 후보:")
            for kw in review_result["retirement_candidates"]:
                print(f"  - {kw}")

        return review_result

    def run_quarterly_review(self, quarter: str | None = None) -> dict:
        """분기별 리뷰 실행"""
        if quarter is None:
            year, q = self.get_current_quarter()
            quarter = f"{year}-Q{q}"

        print(f"=== 분기별 키워드 재검토 시작: {quarter} ===\n")

        # 최근 3개월 리뷰 결과 집계
        year = int(quarter[:4])
        q_num = int(quarter[-1])

        # 분기 내 월 계산
        quarter_months = []
        for i in range(3):
            month_num = (q_num - 1) * 3 + i + 1
            quarter_months.append(f"{year}-{month_num:02d}")

        print(f"대상 월: {quarter_months}\n")

        # 각 월 리뷰 결과
        monthly_results = []
        for month in quarter_months:
            try:
                result = self.tracker.get_monthly_report(month)
                if "error" not in result:
                    monthly_results.append(result)
                    print(f"✓ {month}: {result.get('total_keywords_used', 0)}개 키워드")
            except Exception as e:
                print(f"✗ {month}: 데이터 없음 ({e})")

        # 퇴출 후보 확인
        retirement_candidates = self.tracker.get_retirement_candidates()

        # 현재 키워드 통계
        stats = self.manager.get_statistics()

        # 종합 결과
        result = {
            "quarter": quarter,
            "reviewed_at": datetime.now().isoformat(),
            "months_analyzed": len(monthly_results),
            "current_stats": stats,
            "retirement_candidates": retirement_candidates,
            "recommendations": [],
        }

        # 권고 사항 생성
        if retirement_candidates:
            result["recommendations"].append(f"퇴출 후보 {len(retirement_candidates)}개 키워드 최종 검토 필요")

        # 카테고리 불균형 체크
        by_cat = stats.get("by_category", {})
        cat_counts = [v.get("total", 0) for v in by_cat.values()]
        if cat_counts:
            avg = sum(cat_counts) / len(cat_counts)
            for cat, data in by_cat.items():
                if data.get("total", 0) < avg * 0.7:
                    result["recommendations"].append(f"{cat} 카테고리 키워드 보강 권고 (현재 {data.get('total')}개)")

        # 언어 비율 체크
        lang = stats.get("by_language", {})
        korean = lang.get("korean", 0)
        english = lang.get("english", 0)
        total = korean + english
        if total > 0:
            english_ratio = english / total * 100
            if english_ratio < 15:
                result["recommendations"].append(f"영어 키워드 비율 보강 권고 (현재 {english_ratio:.1f}%)")
            elif english_ratio > 30:
                result["recommendations"].append(f"영어 키워드 비율 과다 (현재 {english_ratio:.1f}%)")

        # 일정 업데이트
        self._schedule["last_quarterly_review"] = quarter
        self._schedule["review_history"].append(
            {
                "type": "quarterly",
                "quarter": quarter,
                "date": datetime.now().isoformat(),
                "summary": {
                    "months_analyzed": len(monthly_results),
                    "retirement_candidates": len(retirement_candidates),
                    "recommendations": len(result["recommendations"]),
                },
            }
        )
        self._save_schedule()

        # 결과 출력
        print("\n📊 분기별 리뷰 결과:")
        print(f"  - 분석 월: {len(monthly_results)}개월")
        print(f"  - 현재 총 키워드: {stats.get('total', 'N/A')}개")
        print(f"  - 퇴출 후보: {len(retirement_candidates)}개")

        if result["recommendations"]:
            print("\n⚠️ 권고 사항:")
            for rec in result["recommendations"]:
                print(f"  - {rec}")

        # 결과 저장
        output_file = self.base_path / "data" / "metrics" / f"quarterly-review-{quarter}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n결과 저장: {output_file}")

        return result

    def get_status(self) -> dict:
        """리뷰 상태 확인"""
        check = self.check_review_needed()

        status = {
            "current_date": datetime.now().isoformat(),
            "last_monthly_review": self._schedule.get("last_monthly_review"),
            "last_quarterly_review": self._schedule.get("last_quarterly_review"),
            "review_needed": check,
            "recent_history": self._schedule.get("review_history", [])[-5:],
        }

        return status


def main():
    parser = argparse.ArgumentParser(description="Keyword Review Scheduler")
    parser.add_argument(
        "command",
        choices=["check", "monthly", "quarterly", "status"],
        help="Command to run",
    )
    parser.add_argument("--month", help="Target month for monthly review (YYYY-MM)")
    parser.add_argument("--quarter", help="Target quarter for quarterly review (YYYY-QN)")

    args = parser.parse_args()

    scheduler = ReviewScheduler()

    if args.command == "check":
        result = scheduler.check_review_needed()
        print(json.dumps(result, ensure_ascii=False, indent=2))

        # 리뷰 필요시 알림
        if result.get("monthly_review_needed"):
            print("\n💡 월간 리뷰 실행: python review_scheduler.py monthly")
        if result.get("quarterly_review_needed"):
            print("\n💡 분기별 리뷰 실행: python review_scheduler.py quarterly")

    elif args.command == "monthly":
        scheduler.run_monthly_review(args.month)

    elif args.command == "quarterly":
        scheduler.run_quarterly_review(args.quarter)

    elif args.command == "status":
        status = scheduler.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
