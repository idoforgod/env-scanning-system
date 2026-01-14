"""
Keyword Manager
===============
STEEPS 키워드 관리 모듈 - 추가, 삭제, 갱신 정책 적용

갱신 주기: 월별
변경 이력 추적 포함
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar

try:
    from .cache_manager import CacheManager
    from .keyword_tracker import KeywordTracker
except ImportError:
    # 직접 실행 시 fallback
    from cache_manager import CacheManager
    from keyword_tracker import KeywordTracker


class KeywordManager:
    """STEEPS 키워드 관리자"""

    CATEGORIES: ClassVar[list[str]] = ["Social", "Technological", "Economic", "Environmental", "Political", "Spiritual"]

    # 키워드 계층 레벨
    LEVEL_CORE = 1  # 핵심 개념
    LEVEL_SUBDOMAIN = 2  # 세부 영역
    LEVEL_TREND = 3  # 구체적 트렌드

    def __init__(self, base_path: str | None = None):
        if base_path is None:
            self.base_path = Path(__file__).parent.parent.parent.parent
        else:
            self.base_path = Path(base_path)

        self.cache_manager = CacheManager(str(self.base_path))
        self.tracker = KeywordTracker(str(self.base_path))

        self.history_file = self.base_path / "data" / "metrics" / "keyword-history.json"
        self._load_history()

    def _load_history(self) -> None:
        """변경 이력 로드"""
        if self.history_file.exists():
            with open(self.history_file, encoding="utf-8") as f:
                self._history = json.load(f)
        else:
            self._history = {"changes": [], "last_review": None}

    def _save_history(self) -> None:
        """변경 이력 저장"""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self._history, f, ensure_ascii=False, indent=2)

    def _record_change(
        self, action: str, category: str, keyword: str, reason: str, metadata: dict | None = None
    ) -> None:
        """변경 이력 기록"""
        change = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "category": category,
            "keyword": keyword,
            "reason": reason,
            "metadata": metadata or {},
        }
        self._history["changes"].append(change)
        self._save_history()

    def get_keywords(self, category: str | None = None) -> dict[str, list[str]]:
        """
        현재 키워드 조회

        Args:
            category: 특정 카테고리 (None이면 전체)

        Returns:
            카테고리별 키워드 딕셔너리
        """
        keywords = self.cache_manager.get_steeps_keywords()
        if category:
            return {category: keywords.get(category, [])}
        return keywords

    def add_keyword(
        self,
        category: str,
        keyword: str,
        level: int = LEVEL_TREND,
        reason: str = "",
        trial: bool = True,
    ) -> dict[str, Any]:
        """
        키워드 추가

        Args:
            category: STEEPS 카테고리
            keyword: 추가할 키워드
            level: 계층 레벨 (1=핵심, 2=세부, 3=트렌드)
            reason: 추가 사유
            trial: 시험 운영 여부 (True면 trial 태그)

        Returns:
            결과 딕셔너리
        """
        if category not in self.CATEGORIES:
            return {"success": False, "error": f"Invalid category: {category}"}

        keywords = self.cache_manager.get_steeps_keywords()

        if keyword in keywords.get(category, []):
            return {"success": False, "error": f"Keyword already exists: {keyword}"}

        # 키워드 추가
        if category not in keywords:
            keywords[category] = []
        keywords[category].append(keyword)

        # 캐시 갱신
        self.cache_manager.set("steeps_keywords", keywords)

        # 이력 기록
        self._record_change(
            action="ADD",
            category=category,
            keyword=keyword,
            reason=reason,
            metadata={"level": level, "trial": trial},
        )

        return {
            "success": True,
            "message": f"Added '{keyword}' to {category}",
            "trial": trial,
        }

    def remove_keyword(self, category: str, keyword: str, reason: str = "") -> dict[str, Any]:
        """
        키워드 삭제

        Args:
            category: STEEPS 카테고리
            keyword: 삭제할 키워드
            reason: 삭제 사유

        Returns:
            결과 딕셔너리
        """
        keywords = self.cache_manager.get_steeps_keywords()

        if keyword not in keywords.get(category, []):
            return {"success": False, "error": f"Keyword not found: {keyword}"}

        # 키워드 삭제
        keywords[category].remove(keyword)

        # 캐시 갱신
        self.cache_manager.set("steeps_keywords", keywords)

        # 이력 기록
        self._record_change(
            action="REMOVE",
            category=category,
            keyword=keyword,
            reason=reason,
        )

        return {"success": True, "message": f"Removed '{keyword}' from {category}"}

    def move_keyword(self, keyword: str, from_category: str, to_category: str, reason: str = "") -> dict[str, Any]:
        """
        키워드 카테고리 이동

        Args:
            keyword: 이동할 키워드
            from_category: 원래 카테고리
            to_category: 대상 카테고리
            reason: 이동 사유

        Returns:
            결과 딕셔너리
        """
        keywords = self.cache_manager.get_steeps_keywords()

        if keyword not in keywords.get(from_category, []):
            return {"success": False, "error": f"Keyword not found in {from_category}"}

        if keyword in keywords.get(to_category, []):
            return {"success": False, "error": f"Keyword already exists in {to_category}"}

        # 이동
        keywords[from_category].remove(keyword)
        if to_category not in keywords:
            keywords[to_category] = []
        keywords[to_category].append(keyword)

        # 캐시 갱신
        self.cache_manager.set("steeps_keywords", keywords)

        # 이력 기록
        self._record_change(
            action="MOVE",
            category=f"{from_category} -> {to_category}",
            keyword=keyword,
            reason=reason,
        )

        return {"success": True, "message": f"Moved '{keyword}' from {from_category} to {to_category}"}

    def validate_inclusion_criteria(self, keyword: str, criteria: dict[str, bool]) -> dict[str, Any]:
        """
        포함 기준 검증

        Args:
            keyword: 검증할 키워드
            criteria: 충족 기준 딕셔너리
                - future_impact: 장기 파급력
                - multi_domain: 다중 영역 영향
                - system_change: 시스템 변화
                - monthly_mentions: 월간 출현
                - increasing_trend: 증가 추세
                - multi_source: 다중 소스
                - early_stage: 초기 단계
                - expert_attention: 전문가 주목
                - innovation_potential: 혁신 잠재력

        Returns:
            검증 결과
        """
        # 카테고리별 필요 기준 수
        future_criteria = ["future_impact", "multi_domain", "system_change"]
        frequency_criteria = ["monthly_mentions", "increasing_trend", "multi_source"]
        weak_signal_criteria = ["early_stage", "expert_attention", "innovation_potential"]

        future_count = sum(1 for c in future_criteria if criteria.get(c, False))
        frequency_count = sum(1 for c in frequency_criteria if criteria.get(c, False))
        weak_signal_count = sum(1 for c in weak_signal_criteria if criteria.get(c, False))

        total_met = sum(criteria.values())
        categories_met = sum(1 for count in [future_count, frequency_count, weak_signal_count] if count > 0)

        # 최소 2개 기준 충족 필요
        passed = total_met >= 2 and categories_met >= 2

        return {
            "keyword": keyword,
            "passed": passed,
            "total_criteria_met": total_met,
            "categories_met": categories_met,
            "breakdown": {
                "future_impact": future_count,
                "frequency": frequency_count,
                "weak_signal": weak_signal_count,
            },
            "recommendation": "Include" if passed else "Exclude",
        }

    def validate_exclusion_criteria(self, keyword: str, criteria: dict[str, bool]) -> dict[str, Any]:
        """
        제외 기준 검증

        Args:
            keyword: 검증할 키워드
            criteria: 제외 기준 딕셔너리
                - too_general: 과도하게 일반적
                - outdated: 시의성 상실
                - duplicate: 중복
                - too_narrow: 너무 좁음
                - short_term_event: 단기 이벤트

        Returns:
            검증 결과
        """
        excluded = any(criteria.values())
        exclusion_reasons = [k for k, v in criteria.items() if v]

        return {
            "keyword": keyword,
            "excluded": excluded,
            "reasons": exclusion_reasons,
            "recommendation": "Exclude" if excluded else "May include",
        }

    def monthly_review(self, month: str) -> dict[str, Any]:
        """
        월간 키워드 리뷰 수행

        Args:
            month: 리뷰 대상 월 (YYYY-MM)

        Returns:
            리뷰 결과
        """
        # 효과성 리포트 가져오기
        effectiveness = self.tracker.get_monthly_report(month)
        if "error" in effectiveness:
            return effectiveness

        # 퇴출 후보 확인
        retirement_candidates = self.tracker.get_retirement_candidates()

        # 등급별 분석
        grade_analysis = effectiveness.get("summary", {}).get("grade_distribution", {})

        review_result = {
            "month": month,
            "review_date": datetime.now().isoformat(),
            "summary": {
                "total_keywords": effectiveness.get("total_keywords_used", 0),
                "grade_distribution": grade_analysis,
                "zero_result_rate": effectiveness.get("summary", {}).get("zero_result_rate", 0),
            },
            "action_items": [],
            "retirement_candidates": retirement_candidates,
            "top_performers": self.tracker.get_top_performers(month, 5),
        }

        # 권고 사항 생성
        if grade_analysis.get("F", 0) > 0:
            review_result["action_items"].append(f"F등급 키워드 {grade_analysis['F']}개 검토 필요")

        if grade_analysis.get("D", 0) > len(effectiveness.get("keywords", [])) * 0.2:
            review_result["action_items"].append("D등급 키워드가 20% 초과 - 키워드 재검토 권고")

        if retirement_candidates:
            review_result["action_items"].append(f"퇴출 후보 {len(retirement_candidates)}개 - 최종 검토 필요")

        # 리뷰 이력 기록
        self._history["last_review"] = {
            "month": month,
            "date": datetime.now().isoformat(),
            "result": review_result,
        }
        self._save_history()

        return review_result

    def get_change_history(self, limit: int = 50) -> list[dict]:
        """
        최근 변경 이력 조회

        Args:
            limit: 최대 조회 건수

        Returns:
            변경 이력 목록
        """
        return self._history.get("changes", [])[-limit:]

    def export_keywords_with_metadata(self) -> dict[str, Any]:
        """
        메타데이터 포함 키워드 전체 내보내기

        Returns:
            키워드 + 메타데이터
        """
        keywords = self.cache_manager.get_steeps_keywords()

        export = {
            "exported_at": datetime.now().isoformat(),
            "version": "1.0",
            "total_keywords": sum(len(v) for v in keywords.values()),
            "by_category": {},
        }

        for category, kw_list in keywords.items():
            export["by_category"][category] = {
                "count": len(kw_list),
                "korean": [k for k in kw_list if not k.isascii()],
                "english": [k for k in kw_list if k.isascii()],
            }

        return export

    def get_statistics(self) -> dict[str, Any]:
        """
        키워드 통계 조회

        Returns:
            통계 딕셔너리
        """
        keywords = self.cache_manager.get_steeps_keywords()

        stats = {
            "total": sum(len(v) for v in keywords.values()),
            "by_category": {},
            "by_language": {"korean": 0, "english": 0, "mixed": 0},
            "last_review": self._history.get("last_review"),
            "recent_changes": len(self._history.get("changes", [])[-30:]),  # 최근 30일
        }

        for category, kw_list in keywords.items():
            korean = len([k for k in kw_list if not k.isascii()])
            english = len([k for k in kw_list if k.isascii()])
            stats["by_category"][category] = {
                "total": len(kw_list),
                "korean": korean,
                "english": english,
            }
            stats["by_language"]["korean"] += korean
            stats["by_language"]["english"] += english

        return stats


def main():
    """CLI 실행"""
    import sys

    manager = KeywordManager()

    if len(sys.argv) < 2:
        print("Usage: python keyword_manager.py <command> [args]")
        print("Commands:")
        print("  list [category]      - 키워드 목록")
        print("  add <cat> <keyword>  - 키워드 추가")
        print("  remove <cat> <kw>    - 키워드 삭제")
        print("  review <YYYY-MM>     - 월간 리뷰")
        print("  history              - 변경 이력")
        print("  stats                - 통계")
        print("  export               - 전체 내보내기")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        category = sys.argv[2] if len(sys.argv) > 2 else None
        keywords = manager.get_keywords(category)
        for cat, kw_list in keywords.items():
            print(f"\n{cat} ({len(kw_list)}개):")
            for kw in kw_list[:10]:
                print(f"  - {kw}")
            if len(kw_list) > 10:
                print(f"  ... 외 {len(kw_list) - 10}개")

    elif command == "add" and len(sys.argv) >= 4:
        result = manager.add_keyword(sys.argv[2], sys.argv[3], reason="CLI 추가")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "remove" and len(sys.argv) >= 4:
        result = manager.remove_keyword(sys.argv[2], sys.argv[3], reason="CLI 삭제")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "review" and len(sys.argv) >= 3:
        result = manager.monthly_review(sys.argv[2])
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "history":
        history = manager.get_change_history()
        for change in history[-10:]:
            print(f"{change['timestamp'][:10]} | {change['action']:6} | {change['category']:15} | {change['keyword']}")

    elif command == "stats":
        stats = manager.get_statistics()
        print(json.dumps(stats, ensure_ascii=False, indent=2))

    elif command == "export":
        export = manager.export_keywords_with_metadata()
        print(json.dumps(export, ensure_ascii=False, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
