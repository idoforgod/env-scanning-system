#!/usr/bin/env python3
"""
환경스캐닝 신호 우선순위 산정 시스템
2026-01-11

우선순위 = (영향도 × 0.40) + (발생가능성 × 0.30) + (긴급도 × 0.20) + (신규성 × 0.10)
"""

import json
from pathlib import Path


class PriorityRanker:
    def __init__(self):
        self.base_dir = Path("/Users/cys/Desktop/ENVscanning-system-main/env-scanning")
        self.classified_file = self.base_dir / "structured/classified-signals-2026-01-11-ALT.json"
        self.impact_file = self.base_dir / "analysis/impact-analysis-2026-01-11-ALT.json"

    def load_json(self, filepath):
        """JSON 파일 로드"""
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)

    def calculate_impact_score(self, signal: dict) -> tuple:
        """영향도(Impact) 점수 계산 - 40%"""
        # 신호 중요도와 영향 범위 기반
        significance = signal.get("significance", 3)
        category = signal.get("category", {}).get("primary", "Unknown")
        secondary_cats = len(signal.get("category", {}).get("secondary", []))

        # 신호 중요도(1-5)를 10점 만점으로 변환
        base_score = (significance / 5.0) * 10

        # 다중 도메인 영향도
        domain_bonus = min(secondary_cats * 0.5, 2)

        # 카테고리 별 가중치
        category_weight = {
            "Technological": 1.1,
            "Political": 1.2,
            "Economic": 1.1,
            "Environmental": 1.15,
            "Social": 1.0,
            "Spiritual": 0.9,
        }

        weight = category_weight.get(category, 1.0)

        impact_score = min((base_score + domain_bonus) * weight, 10.0)

        rationale = (
            f"신호 중요도: {significance}/5 → {base_score:.1f}점, "
            f"다중도메인: +{domain_bonus:.1f}, "
            f"카테고리({category}): ×{weight}"
        )

        return impact_score, rationale

    def calculate_probability_score(self, signal: dict, impact_data: dict = None) -> tuple:
        """발생가능성(Probability) 점수 계산 - 30%"""
        significance = signal.get("significance", 3)
        status = signal.get("status", "emerging")

        # 상태별 기본 점수
        status_score = {"mature": 9.5, "developing": 7.5, "emerging": 5.5}.get(status, 5.0)

        # 신호 중요도가 높을수록 발생 가능성 높음
        significance_bonus = (significance / 5.0) * 2

        # 영향 분석 데이터가 있으면 활용
        likelihood_boost = 0
        if impact_data:
            primary_impacts = impact_data.get("primary_impacts", [])
            if primary_impacts:
                avg_likelihood = (
                    sum(p.get("likelihood", 0.5) for p in primary_impacts) / len(primary_impacts)
                    if primary_impacts
                    else 0.5
                )
                likelihood_boost = avg_likelihood * 3

        probability_score = min(status_score + significance_bonus + likelihood_boost, 10.0)

        rationale = (
            f"상태({status}): {status_score:.1f}점, "
            f"중요도 가중: +{significance_bonus:.1f}, "
            f"영향분석 기반: +{likelihood_boost:.1f}"
        )

        return probability_score, rationale

    def calculate_urgency_score(self, signal: dict, impact_data: dict = None) -> tuple:
        """긴급도(Urgency) 점수 계산 - 20%"""
        significance = signal.get("significance", 3)
        status = signal.get("status", "emerging")

        # 임박한 신호는 높은 긴급도
        urgency_base = {"mature": 3.0, "developing": 6.0, "emerging": 4.0}.get(status, 4.0)

        # 중요도가 높을수록 긴급
        significance_weight = (significance / 5.0) * 4

        # 영향 데이터의 timeframe 확인
        timeframe_boost = 0
        if impact_data:
            primary_impacts = impact_data.get("primary_impacts", [])
            for impact in primary_impacts:
                timeframe = impact.get("timeframe", "long_term")
                if timeframe == "immediate":
                    timeframe_boost = max(timeframe_boost, 3.5)
                elif timeframe == "short_term":
                    timeframe_boost = max(timeframe_boost, 2.5)
                elif timeframe == "mid_term":
                    timeframe_boost = max(timeframe_boost, 1.5)

        urgency_score = min(urgency_base + significance_weight + timeframe_boost, 10.0)

        rationale = (
            f"상태({status}): {urgency_base:.1f}점, "
            f"중요도: +{significance_weight:.1f}, "
            f"시간 프레임: +{timeframe_boost:.1f}"
        )

        return urgency_score, rationale

    def calculate_novelty_score(self, signal: dict) -> tuple:
        """신규성(Novelty) 점수 계산 - 10%"""
        # 신호의 특성 분석
        full_desc = signal.get("full_description", "").lower()
        summary = signal.get("summary", "").lower()
        combined_text = full_desc + " " + summary

        # 신규성 키워드
        high_novelty_keywords = [
            "first",
            "첫",
            "new",
            "새로운",
            "unprecedented",
            "전례없는",
            "breakthrough",
            "돌파",
            "novel",
            "참신한",
            "unveils",
            "공개",
            "inaugural",
            "초대형",
            "revolutionary",
            "혁명적",
        ]

        medium_novelty_keywords = [
            "emerging",
            "등장",
            "develop",
            "개발",
            "advance",
            "진전",
            "expansion",
            "확장",
            "shift",
            "전환",
            "integration",
            "통합",
        ]

        # 키워드 카운팅
        high_count = sum(1 for kw in high_novelty_keywords if kw in combined_text)
        medium_count = sum(1 for kw in medium_novelty_keywords if kw in combined_text)

        novelty_score = min(3.0 + (high_count * 1.5) + (medium_count * 0.5), 10.0)

        # 신호 상태에 기반한 조정
        status = signal.get("status", "emerging")
        if status == "emerging":
            novelty_score = min(novelty_score + 1.5, 10.0)
        elif status == "mature":
            novelty_score = max(novelty_score - 1.0, 1.0)

        rationale = (
            f"신규 키워드: {high_count}개, "
            f"진화 키워드: {medium_count}개, "
            f"상태 조정({status}): 기본 3.0 + 가중치 = {novelty_score:.1f}"
        )

        return novelty_score, rationale

    def rank_signals(self) -> dict:
        """전체 신호 우선순위 산정"""
        # 데이터 로드
        classified_data = self.load_json(self.classified_file)
        impact_data = self.load_json(self.impact_file)

        # 영향 분석 인덱싱
        impact_map = {}
        for assessment in impact_data.get("impact_assessments", []):
            signal_id = assessment.get("signal_id")
            impact_map[signal_id] = assessment

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

            # 가중 점수 계산
            weighted_score = (
                (impact_score * 0.40) + (probability_score * 0.30) + (urgency_score * 0.20) + (novelty_score * 0.10)
            )

            # 100점 만점으로 변환
            final_score = (weighted_score / 10.0) * 100

            # 등급 부여
            if final_score >= 80:
                grade = "A"
            elif final_score >= 60:
                grade = "B"
            elif final_score >= 40:
                grade = "C"
            else:
                grade = "D"

            # 모니터링 주기
            if grade == "A":
                monitoring_cycle = "주간 (Weekly)"
            elif grade == "B":
                monitoring_cycle = "월간 (Monthly)"
            elif grade == "C":
                monitoring_cycle = "분기 (Quarterly)"
            else:
                monitoring_cycle = "반기 (Semi-annual)"

            # 대응 권고
            if grade == "A":
                recommendation = "즉시 대응 필요. 임원진 보고 및 전략 수립 시작"
            elif grade == "B":
                recommendation = "중점 모니터링. 관련 부서 정보 공유 및 대응 준비"
            elif grade == "C":
                recommendation = "정기 추적. 산업 보고서에 포함 및 변화 감시"
            else:
                recommendation = "참고 관찰. 데이터베이스에 기록 및 주기적 검토"

            ranked_signals.append(
                {
                    "signal_id": signal_id,
                    "title": signal.get("title", ""),
                    "category": signal.get("category", {}).get("primary", "Unknown"),
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

        # 최종 점수로 정렬
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

        # 카테고리별 분포
        category_dist = {}
        for signal in ranked_signals:
            cat = signal.get("category", "Unknown")
            category_dist[cat] = category_dist.get(cat, 0) + 1

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
                    "count": grade_dist["A"],
                    "threshold": 80,
                    "percentage": round((grade_dist["A"] / total * 100), 1) if total > 0 else 0,
                },
                "medium_priority": {
                    "count": grade_dist["B"],
                    "threshold": 60,
                    "percentage": round((grade_dist["B"] / total * 100), 1) if total > 0 else 0,
                },
                "low_priority": {
                    "count": grade_dist["C"] + grade_dist["D"],
                    "threshold": 0,
                    "percentage": round(((grade_dist["C"] + grade_dist["D"]) / total * 100), 1) if total > 0 else 0,
                },
            },
            "category_distribution": category_dist,
            "average_scores": {
                "impact": round(sum(s["scores"]["impact"] for s in ranked_signals) / total, 2) if total > 0 else 0,
                "probability": round(sum(s["scores"]["probability"] for s in ranked_signals) / total, 2)
                if total > 0
                else 0,
                "urgency": round(sum(s["scores"]["urgency"] for s in ranked_signals) / total, 2) if total > 0 else 0,
                "novelty": round(sum(s["scores"]["novelty"] for s in ranked_signals) / total, 2) if total > 0 else 0,
            },
        }

    def run(self):
        """메인 실행"""
        print("우선순위 산정 시작...")

        # 신호 순위 산정
        ranked_signals, classified_data = self.rank_signals()

        # 요약 생성
        summary = self.generate_summary(ranked_signals)

        # 최종 출력 구조
        output = {
            "ranking_date": summary["ranking_date"],
            "total_ranked": summary["total_ranked"],
            "top_10_summary": summary["top_10_summary"],
            "distribution": summary["distribution"],
            "category_distribution": summary["category_distribution"],
            "average_scores": summary["average_scores"],
            "rankings": ranked_signals,
        }

        # 파일 저장
        output_file = self.base_dir / "analysis/priority-ranking-2026-01-11-ALT.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"우선순위 산정 완료: {output_file}")

        # 통계 출력
        print("\n" + "=" * 60)
        print("우선순위 산정 결과 요약")
        print("=" * 60)
        print(f"총 분석 신호: {summary['total_ranked']}개")
        print(
            f"\nA등급(즉시 대응): {summary['distribution']['high_priority']['count']}개 ({summary['distribution']['high_priority']['percentage']}%)"
        )
        print(
            f"B등급(중점 모니터링): {summary['distribution']['medium_priority']['count']}개 ({summary['distribution']['medium_priority']['percentage']}%)"
        )
        print(
            f"C/D등급(정기 추적/참고): {summary['distribution']['low_priority']['count']}개 ({summary['distribution']['low_priority']['percentage']}%)"
        )

        print("\n카테고리 분포:")
        for cat, count in summary["category_distribution"].items():
            print(f"  {cat}: {count}개")

        print("\n평균 점수:")
        print(f"  영향도: {summary['average_scores']['impact']}/10")
        print(f"  발생가능성: {summary['average_scores']['probability']}/10")
        print(f"  긴급도: {summary['average_scores']['urgency']}/10")
        print(f"  신규성: {summary['average_scores']['novelty']}/10")

        print("\n상위 10대 신호:")
        for i, sig in enumerate(ranked_signals[:10], 1):
            print(
                f"  {i}. {sig['signal_id']}: {sig['title'][:50]}... (점수: {sig['final_score']}/100, {sig['grade']}등급)"
            )

        print("=" * 60)


if __name__ == "__main__":
    ranker = PriorityRanker()
    ranker.run()
