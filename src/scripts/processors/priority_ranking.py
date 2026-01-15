#!/usr/bin/env python3
"""
환경스캐닝 신호 우선순위 산정 시스템
2026-01-11

가중 우선순위 점수:
(영향도 x 40%) + (발생가능성 x 30%) + (긴급도 x 20%) + (신규성 x 10%)

100점 만점 기준:
- A등급 (80+): 즉시 대응 필요
- B등급 (60-79): 중점 모니터링
- C등급 (40-59): 정기 추적
- D등급 (<40): 참고 관찰
"""

import json
from pathlib import Path


class PriorityRanker:
    def __init__(self):
        self.base_dir = Path("/Users/cys/Desktop/ENVscanning-system-main/env-scanning")
        self.classified_file = self.base_dir / "structured/classified-signals-2026-01-11-ALT.json"
        self.impact_file = self.base_dir / "analysis/impact-analysis-2026-01-11-ALT.json"

    def load_json(self, filepath) -> dict:
        """JSON 파일 로드"""
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)

    def calculate_impact_score(self, signal: dict) -> tuple[float, str]:
        """
        영향도(Impact) 점수 계산 - 40%

        측정 요소:
        - 신호 중요도 (significance): 1-5
        - 다중 도메인 영향
        - 카테고리 가중치
        """
        significance = signal.get("significance", 3)
        category = signal.get("category", {}).get("primary", "Unknown")
        secondary_cats = len(signal.get("category", {}).get("secondary", []))

        # 신호 중요도(1-5)를 10점 만점으로 변환
        base_score = (significance / 5.0) * 10.0

        # 다중 도메인 영향도 (다중 카테고리 = 광범위한 영향)
        domain_bonus = min(secondary_cats * 0.8, 2.0)

        # 카테고리 별 기본 가중치 (중요도에 따라)
        category_weight = {
            "Political": 1.25,
            "Technological": 1.15,
            "Environmental": 1.15,
            "Economic": 1.10,
            "Social": 1.00,
            "Spiritual": 0.85,
        }

        weight = category_weight.get(category, 1.0)

        # 최종 영향도 점수
        impact_score = min((base_score + domain_bonus) * weight, 10.0)

        rationale = (
            f"기본값(중요도 {significance}/5): {base_score:.1f} | "
            f"다중도메인(x{secondary_cats}): +{domain_bonus:.1f} | "
            f"카테고리({category}): x{weight}"
        )

        return impact_score, rationale

    def calculate_probability_score(self, signal: dict, impact_assessment: dict | None = None) -> tuple[float, str]:
        """
        발생가능성(Probability/Likelihood) 점수 계산 - 30%

        측정 요소:
        - 신호 상태 (emerging/developing/mature)
        - 신호 중요도
        - 영향 분석의 가능성(likelihood) 데이터
        """
        significance = signal.get("significance", 3)
        status = signal.get("status", "emerging")

        # 상태별 기본 확률 (낮음 -> 높음)
        status_score = {
            "mature": 9.0,  # 이미 일어나고 있음
            "developing": 7.5,  # 진행 중
            "emerging": 5.5,  # 초기 신호
        }.get(status, 5.0)

        # 중요도가 높을수록 발생 가능성도 높다고 가정
        significance_bonus = (significance / 5.0) * 2.0

        # 영향 분석 데이터가 있으면 활용
        likelihood_boost = 0.0
        if impact_assessment:
            primary_impacts = impact_assessment.get("primary_impacts", [])
            if primary_impacts:
                avg_likelihood = sum(p.get("likelihood", 0.5) for p in primary_impacts) / len(primary_impacts)
                # 평균 가능성을 0-10 스케일로 변환
                likelihood_boost = avg_likelihood * 3.5

        probability_score = min(status_score + significance_bonus + likelihood_boost, 10.0)

        rationale = (
            f"상태({status}): {status_score:.1f} | "
            f"중요도 부스트(x{significance}): +{significance_bonus:.1f} | "
            f"영향분석 기반: +{likelihood_boost:.1f}"
        )

        return probability_score, rationale

    def calculate_urgency_score(self, signal: dict, impact_assessment: dict | None = None) -> tuple[float, str]:
        """
        긴급도(Urgency) 점수 계산 - 20%

        측정 요소:
        - 대응 필요 시간 (timeframe)
        - 신호 상태
        - 변화 속도 (momentum)
        """
        significance = signal.get("significance", 3)
        status = signal.get("status", "emerging")

        # 상태별 기본 긴급도
        urgency_base = {
            "developing": 7.0,  # 진행 중 = 높은 긴급도
            "mature": 8.5,  # 이미 진행 = 매우 높은 긴급도
            "emerging": 4.5,  # 초기 신호 = 낮은 긴급도
        }.get(status, 4.0)

        # 중요도가 높을수록 긴급
        significance_weight = (significance / 5.0) * 3.0

        # 영향 데이터의 timeframe 분석
        timeframe_boost = 0.0
        if impact_assessment:
            primary_impacts = impact_assessment.get("primary_impacts", [])
            timeframe_scores = {"immediate": 3.5, "short_term": 2.5, "mid_term": 1.0, "long_term": 0.0}

            for impact in primary_impacts:
                timeframe = impact.get("timeframe", "long_term")
                boost = timeframe_scores.get(timeframe, 0.0)
                timeframe_boost = max(timeframe_boost, boost)

        urgency_score = min(urgency_base + significance_weight + timeframe_boost, 10.0)

        rationale = (
            f"상태({status}): {urgency_base:.1f} | "
            f"중요도(x{significance}): +{significance_weight:.1f} | "
            f"타이밍: +{timeframe_boost:.1f}"
        )

        return urgency_score, rationale

    def calculate_novelty_score(self, signal: dict) -> tuple[float, str]:
        """
        신규성(Novelty) 점수 계산 - 10%

        측정 요소:
        - 신규성 키워드 (first, new, breakthrough 등)
        - 신호 상태 (emerging = 더 신규적)
        - 기술 혁신성
        """
        full_desc = (signal.get("full_description", "") or "").lower()
        summary = (signal.get("summary", "") or "").lower()
        title = (signal.get("title", "") or "").lower()
        combined_text = full_desc + " " + summary + " " + title

        # 높은 신규성 키워드
        high_novelty_keywords = [
            "first",
            "첫",
            "inaugural",
            "초대형",
            "new",
            "새로운",
            "신규",
            "신규적",
            "unprecedented",
            "전례없는",
            "breakthrough",
            "돌파",
            "혁신",
            "novel",
            "참신한",
            "discover",
            "발견",
            "규명",
            "invent",
            "발명",
            "창안",
            "revolutionar",
            "혁명적",
            "unveil",
            "공개",
            "launch",
            "개시",
            "출시",
        ]

        # 중간 신규성 키워드
        medium_novelty_keywords = [
            "emerging",
            "등장",
            "부상",
            "develop",
            "개발",
            "advance",
            "진전",
            "발전",
            "expand",
            "확대",
            "확장",
            "shift",
            "전환",
            "integrat",
            "통합",
            "commercializ",
            "상용화",
            "transform",
            "전환",
            "reinvigorate",
            "부활",
        ]

        # 키워드 개수 세기
        high_count = sum(1 for kw in high_novelty_keywords if kw in combined_text)
        medium_count = sum(1 for kw in medium_novelty_keywords if kw in combined_text)

        # 기본 점수 + 키워드 가중치
        novelty_score = min(3.0 + (high_count * 1.8) + (medium_count * 0.6), 10.0)

        # 상태별 조정 (emerging이 더 신규적)
        status = signal.get("status", "emerging")
        if status == "emerging":
            novelty_score = min(novelty_score + 1.0, 10.0)
            status_adjustment = "+1.0 (emerging)"
        elif status == "mature":
            novelty_score = max(novelty_score - 1.5, 1.0)
            status_adjustment = "-1.5 (mature)"
        else:
            status_adjustment = "0.0"

        rationale = (
            f"고신규도({high_count}): +{high_count * 1.8:.1f} | "
            f"진화형({medium_count}): +{medium_count * 0.6:.1f} | "
            f"상태({status}): {status_adjustment}"
        )

        return novelty_score, rationale

    def rank_signals(self) -> tuple[list[dict], dict]:
        """전체 신호 우선순위 산정"""
        print("데이터 로드 중...")

        # 데이터 로드
        classified_data = self.load_json(self.classified_file)
        impact_data = self.load_json(self.impact_file)

        # 영향 분석 데이터 인덱싱
        impact_map = {}
        for assessment in impact_data.get("impact_assessments", []):
            signal_id = assessment.get("signal_id")
            impact_map[signal_id] = assessment

        print(f"신호 분석 중... (총 {len(classified_data.get('signals', []))}개)")

        # 각 신호별 점수 계산
        ranked_signals = []

        for signal in classified_data.get("signals", []):
            signal_id = signal.get("signal_id")

            # 각 차원 점수 계산
            impact_score, impact_rationale = self.calculate_impact_score(signal)

            probability_score, probability_rationale = self.calculate_probability_score(
                signal, impact_map.get(signal_id)
            )

            urgency_score, urgency_rationale = self.calculate_urgency_score(signal, impact_map.get(signal_id))

            novelty_score, novelty_rationale = self.calculate_novelty_score(signal)

            # 가중 점수 계산 (10점 만점)
            weighted_score = (
                (impact_score * 0.40) + (probability_score * 0.30) + (urgency_score * 0.20) + (novelty_score * 0.10)
            )

            # 100점 만점으로 변환
            final_score = (weighted_score / 10.0) * 100.0

            # 등급 부여
            if final_score >= 80:
                grade = "A"
                action = "즉시 대응"
            elif final_score >= 60:
                grade = "B"
                action = "중점 모니터링"
            elif final_score >= 40:
                grade = "C"
                action = "정기 추적"
            else:
                grade = "D"
                action = "참고 관찰"

            # 모니터링 주기
            monitoring_cycle_dict = {
                "A": "주간 (Weekly)",
                "B": "월간 (Monthly)",
                "C": "분기 (Quarterly)",
                "D": "반기 (Semi-annual)",
            }
            monitoring_cycle = monitoring_cycle_dict[grade]

            # 대응 권고사항
            recommendation_dict = {
                "A": "즉시 대응 필요. 임원진 보고 및 전략 수립 시작",
                "B": "중점 모니터링. 관련 부서 정보 공유 및 대응 준비",
                "C": "정기 추적. 산업 보고서에 포함 및 변화 감시",
                "D": "참고 관찰. 데이터베이스에 기록 및 주기적 검토",
            }
            recommendation = recommendation_dict[grade]

            ranked_signals.append(
                {
                    "rank": 0,  # 정렬 후 부여
                    "signal_id": signal_id,
                    "title": signal.get("title", ""),
                    "category": signal.get("category", {}).get("primary", "Unknown"),
                    "subcategory": signal.get("subcategory", ""),
                    "significance": signal.get("significance", 0),
                    "status": signal.get("status", "emerging"),
                    "scores": {
                        "impact": round(impact_score, 2),
                        "probability": round(probability_score, 2),
                        "urgency": round(urgency_score, 2),
                        "novelty": round(novelty_score, 2),
                    },
                    "weighted_score": round(weighted_score, 2),
                    "final_score": round(final_score, 1),
                    "grade": grade,
                    "action": action,
                    "monitoring_cycle": monitoring_cycle,
                    "recommendation": recommendation,
                    "score_rationale": {
                        "impact": impact_rationale,
                        "probability": probability_rationale,
                        "urgency": urgency_rationale,
                        "novelty": novelty_rationale,
                    },
                }
            )

        # 최종 점수로 정렬 (내림차순)
        ranked_signals.sort(key=lambda x: x["final_score"], reverse=True)

        # 순위 부여
        for idx, signal in enumerate(ranked_signals, 1):
            signal["rank"] = idx

        return ranked_signals, classified_data

    def generate_summary(self, ranked_signals: list) -> dict:
        """종합 요약 생성"""
        total = len(ranked_signals)

        # 상위 10개
        top_10 = ranked_signals[:10]
        top_10_signals = [s["signal_id"] for s in top_10]

        # 상위 10개 카테고리 분포
        top_10_categories = {}
        for signal in top_10:
            cat = signal.get("category", "Unknown")
            top_10_categories[cat] = top_10_categories.get(cat, 0) + 1

        avg_top_10_score = sum(s["final_score"] for s in top_10) / len(top_10) if top_10 else 0

        # 등급별 분포
        grade_dist = {"A": 0, "B": 0, "C": 0, "D": 0}
        for signal in ranked_signals:
            grade = signal["grade"]
            grade_dist[grade] += 1

        # 카테고리별 전체 분포
        category_dist = {}
        for signal in ranked_signals:
            cat = signal.get("category", "Unknown")
            category_dist[cat] = category_dist.get(cat, 0) + 1

        # 상태별 분포
        status_dist = {}
        for signal in ranked_signals:
            status = signal.get("status", "unknown")
            status_dist[status] = status_dist.get(status, 0) + 1

        # 평균 점수
        if total > 0:
            avg_impact = sum(s["scores"]["impact"] for s in ranked_signals) / total
            avg_probability = sum(s["scores"]["probability"] for s in ranked_signals) / total
            avg_urgency = sum(s["scores"]["urgency"] for s in ranked_signals) / total
            avg_novelty = sum(s["scores"]["novelty"] for s in ranked_signals) / total
            avg_final = sum(s["final_score"] for s in ranked_signals) / total
        else:
            avg_impact = avg_probability = avg_urgency = avg_novelty = avg_final = 0

        return {
            "ranking_date": "2026-01-11",
            "total_ranked": total,
            "top_10_summary": {
                "signals": top_10_signals,
                "categories": top_10_categories,
                "avg_priority_score": round(avg_top_10_score, 1),
            },
            "distribution": {
                "high_priority": {
                    "grade": "A",
                    "count": grade_dist["A"],
                    "threshold": 80,
                    "percentage": round((grade_dist["A"] / total * 100), 1) if total > 0 else 0,
                },
                "medium_priority": {
                    "grade": "B",
                    "count": grade_dist["B"],
                    "threshold": 60,
                    "percentage": round((grade_dist["B"] / total * 100), 1) if total > 0 else 0,
                },
                "low_priority": {
                    "grade": "C-D",
                    "count": grade_dist["C"] + grade_dist["D"],
                    "threshold": 0,
                    "percentage": round(((grade_dist["C"] + grade_dist["D"]) / total * 100), 1) if total > 0 else 0,
                },
            },
            "grade_breakdown": {
                "A": {
                    "count": grade_dist["A"],
                    "percentage": round((grade_dist["A"] / total * 100), 1) if total > 0 else 0,
                },
                "B": {
                    "count": grade_dist["B"],
                    "percentage": round((grade_dist["B"] / total * 100), 1) if total > 0 else 0,
                },
                "C": {
                    "count": grade_dist["C"],
                    "percentage": round((grade_dist["C"] / total * 100), 1) if total > 0 else 0,
                },
                "D": {
                    "count": grade_dist["D"],
                    "percentage": round((grade_dist["D"] / total * 100), 1) if total > 0 else 0,
                },
            },
            "category_distribution": category_dist,
            "status_distribution": status_dist,
            "average_scores": {
                "impact": round(avg_impact, 2),
                "probability": round(avg_probability, 2),
                "urgency": round(avg_urgency, 2),
                "novelty": round(avg_novelty, 2),
                "final_score": round(avg_final, 1),
            },
        }

    def run(self):
        """메인 실행"""
        print("\n" + "=" * 70)
        print("환경스캐닝 신호 우선순위 산정 시스템")
        print("=" * 70)

        # 신호 순위 산정
        ranked_signals, _classified_data = self.rank_signals()

        # 요약 생성
        summary = self.generate_summary(ranked_signals)

        # 최종 출력 구조
        output = {
            "ranking_date": summary["ranking_date"],
            "total_ranked": summary["total_ranked"],
            "methodology": {
                "formula": "(영향도 x 0.40) + (발생가능성 x 0.30) + (긴급도 x 0.20) + (신규성 x 0.10)",
                "scale": "100점 만점",
                "grades": {
                    "A": {"range": "80-100", "action": "즉시 대응"},
                    "B": {"range": "60-79", "action": "중점 모니터링"},
                    "C": {"range": "40-59", "action": "정기 추적"},
                    "D": {"range": "0-39", "action": "참고 관찰"},
                },
            },
            "summary": summary,
            "rankings": ranked_signals,
        }

        # 파일 저장
        output_file = self.base_dir / "analysis/priority-ranking-2026-01-11-ALT.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"\n우선순위 산정 완료: {output_file}")

        # 통계 출력
        self.print_statistics(summary, ranked_signals)

    def print_statistics(self, summary: dict, ranked_signals: list):
        """통계 출력"""
        print("\n" + "=" * 70)
        print("우선순위 산정 결과 요약")
        print("=" * 70)

        total = summary["total_ranked"]

        print(f"\n총 분석 신호: {total}개")

        print("\n등급 분포:")
        print(
            f"  A등급 (즉시 대응):     {summary['grade_breakdown']['A']['count']:3d}개 ({summary['grade_breakdown']['A']['percentage']:5.1f}%)"
        )
        print(
            f"  B등급 (중점 모니터):   {summary['grade_breakdown']['B']['count']:3d}개 ({summary['grade_breakdown']['B']['percentage']:5.1f}%)"
        )
        print(
            f"  C등급 (정기 추적):     {summary['grade_breakdown']['C']['count']:3d}개 ({summary['grade_breakdown']['C']['percentage']:5.1f}%)"
        )
        print(
            f"  D등급 (참고 관찰):     {summary['grade_breakdown']['D']['count']:3d}개 ({summary['grade_breakdown']['D']['percentage']:5.1f}%)"
        )

        print("\n카테고리 분포:")
        for cat in sorted(summary["category_distribution"].keys()):
            count = summary["category_distribution"][cat]
            pct = (count / total * 100) if total > 0 else 0
            print(f"  {cat:15s}: {count:3d}개 ({pct:5.1f}%)")

        print("\n상태별 분포:")
        for status in sorted(summary["status_distribution"].keys()):
            count = summary["status_distribution"][status]
            pct = (count / total * 100) if total > 0 else 0
            print(f"  {status:12s}: {count:3d}개 ({pct:5.1f}%)")

        print("\n평균 차원별 점수 (10점 만점):")
        print(f"  영향도(Impact):         {summary['average_scores']['impact']:5.2f}/10")
        print(f"  발생가능성(Probability):{summary['average_scores']['probability']:5.2f}/10")
        print(f"  긴급도(Urgency):        {summary['average_scores']['urgency']:5.2f}/10")
        print(f"  신규성(Novelty):        {summary['average_scores']['novelty']:5.2f}/10")
        print(f"  최종 점수 평균:         {summary['average_scores']['final_score']:5.1f}/100")

        print("\n상위 15대 신호:")
        print("-" * 70)
        for i, sig in enumerate(ranked_signals[:15], 1):
            title_short = sig["title"][:45].ljust(45)
            print(f"  {i:2d}. [{sig['grade']}] {sig['signal_id']:20s} {title_short}")
            print(
                f"      점수: {sig['final_score']:6.1f}/100 | "
                f"영향도: {sig['scores']['impact']:4.2f} | "
                f"발생: {sig['scores']['probability']:4.2f} | "
                f"긴급: {sig['scores']['urgency']:4.2f} | "
                f"신규: {sig['scores']['novelty']:4.2f}"
            )

        print("=" * 70)


if __name__ == "__main__":
    ranker = PriorityRanker()
    ranker.run()
