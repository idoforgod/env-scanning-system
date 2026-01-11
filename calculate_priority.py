#!/usr/bin/env python3
"""
환경스캐닝 신호 우선순위 산정 - 인라인 실행
"""

import json
from pathlib import Path

# 파일 경로
base_dir = Path("/Users/cys/Desktop/ENVscanning-system-main/env-scanning")
classified_file = base_dir / "structured/classified-signals-2026-01-11-ALT.json"
impact_file = base_dir / "analysis/impact-analysis-2026-01-11-ALT.json"
output_file = base_dir / "analysis/priority-ranking-2026-01-11-ALT.json"

print("파일 로드 중...")
with open(classified_file, encoding="utf-8") as f:
    classified_data = json.load(f)

with open(impact_file, encoding="utf-8") as f:
    impact_data = json.load(f)

print(f"로드 완료: {len(classified_data.get('signals', []))}개 신호")

# 영향 분석 인덱싱
impact_map = {}
for assessment in impact_data.get("impact_assessments", []):
    signal_id = assessment.get("signal_id")
    impact_map[signal_id] = assessment

print(f"영향 분석: {len(impact_map)}개 신호")


# 점수 계산 함수들
def calc_impact(signal, impact_assessment):
    significance = signal.get("significance", 3)
    category = signal.get("category", {}).get("primary", "Unknown")
    secondary_cats = len(signal.get("category", {}).get("secondary", []))

    base_score = (significance / 5.0) * 10.0
    domain_bonus = min(secondary_cats * 0.8, 2.0)

    category_weight = {
        "Political": 1.25,
        "Technological": 1.15,
        "Environmental": 1.15,
        "Economic": 1.10,
        "Social": 1.00,
        "Spiritual": 0.85,
    }
    weight = category_weight.get(category, 1.0)

    impact_score = min((base_score + domain_bonus) * weight, 10.0)
    rationale = f"기본값({significance}/5): {base_score:.1f} | 다중도메인({secondary_cats}): +{domain_bonus:.1f} | 카테고리({category}): ×{weight}"

    return impact_score, rationale


def calc_probability(signal, impact_assessment):
    significance = signal.get("significance", 3)
    status = signal.get("status", "emerging")

    status_score = {"mature": 9.0, "developing": 7.5, "emerging": 5.5}.get(status, 5.0)
    significance_bonus = (significance / 5.0) * 2.0

    likelihood_boost = 0.0
    if impact_assessment:
        primary_impacts = impact_assessment.get("primary_impacts", [])
        if primary_impacts:
            avg_likelihood = sum(p.get("likelihood", 0.5) for p in primary_impacts) / len(primary_impacts)
            likelihood_boost = avg_likelihood * 3.5

    probability_score = min(status_score + significance_bonus + likelihood_boost, 10.0)
    rationale = f"상태({status}): {status_score:.1f} | 중요도(×{significance}): +{significance_bonus:.1f} | 영향분석: +{likelihood_boost:.1f}"

    return probability_score, rationale


def calc_urgency(signal, impact_assessment):
    significance = signal.get("significance", 3)
    status = signal.get("status", "emerging")

    urgency_base = {"developing": 7.0, "mature": 8.5, "emerging": 4.5}.get(status, 4.0)
    significance_weight = (significance / 5.0) * 3.0

    timeframe_boost = 0.0
    if impact_assessment:
        primary_impacts = impact_assessment.get("primary_impacts", [])
        timeframe_scores = {"immediate": 3.5, "short_term": 2.5, "mid_term": 1.0, "long_term": 0.0}
        for impact in primary_impacts:
            timeframe = impact.get("timeframe", "long_term")
            boost = timeframe_scores.get(timeframe, 0.0)
            timeframe_boost = max(timeframe_boost, boost)

    urgency_score = min(urgency_base + significance_weight + timeframe_boost, 10.0)
    rationale = f"상태({status}): {urgency_base:.1f} | 중요도(×{significance}): +{significance_weight:.1f} | 타이밍: +{timeframe_boost:.1f}"

    return urgency_score, rationale


def calc_novelty(signal):
    full_desc = (signal.get("full_description", "") or "").lower()
    summary = (signal.get("summary", "") or "").lower()
    title = (signal.get("title", "") or "").lower()
    combined = full_desc + " " + summary + " " + title

    high_keywords = [
        "first",
        "첫",
        "inaugural",
        "new",
        "새로운",
        "unprecedented",
        "전례없는",
        "breakthrough",
        "돌파",
        "novel",
        "참신한",
        "discover",
        "발견",
        "규명",
        "invent",
        "발명",
        "revolutionar",
        "혁명적",
        "unveil",
        "공개",
        "launch",
        "개시",
    ]

    medium_keywords = [
        "emerging",
        "등장",
        "develop",
        "개발",
        "advance",
        "진전",
        "expand",
        "확대",
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

    high_count = sum(1 for kw in high_keywords if kw in combined)
    medium_count = sum(1 for kw in medium_keywords if kw in combined)

    novelty_score = min(3.0 + (high_count * 1.8) + (medium_count * 0.6), 10.0)

    status = signal.get("status", "emerging")
    if status == "emerging":
        novelty_score = min(novelty_score + 1.0, 10.0)
        status_adj = "+1.0 (emerging)"
    elif status == "mature":
        novelty_score = max(novelty_score - 1.5, 1.0)
        status_adj = "-1.5 (mature)"
    else:
        status_adj = "0.0"

    rationale = f"고신규도({high_count}): +{high_count * 1.8:.1f} | 진화형({medium_count}): +{medium_count * 0.6:.1f} | 상태({status}): {status_adj}"

    return novelty_score, rationale


def assign_grade(final_score):
    if final_score >= 80:
        return "A"
    elif final_score >= 60:
        return "B"
    elif final_score >= 40:
        return "C"
    else:
        return "D"


# 신호별 점수 계산
print("신호별 점수 계산 중...")
ranked_signals = []

for signal in classified_data.get("signals", []):
    signal_id = signal.get("signal_id")

    impact_score, impact_ratio = calc_impact(signal, impact_map.get(signal_id))
    prob_score, prob_ratio = calc_probability(signal, impact_map.get(signal_id))
    urgency_score, urgency_ratio = calc_urgency(signal, impact_map.get(signal_id))
    novelty_score, novelty_ratio = calc_novelty(signal)

    weighted = (impact_score * 0.40) + (prob_score * 0.30) + (urgency_score * 0.20) + (novelty_score * 0.10)
    final = (weighted / 10.0) * 100.0

    grade = assign_grade(final)

    monitoring_dict = {"A": "주간 (Weekly)", "B": "월간 (Monthly)", "C": "분기 (Quarterly)", "D": "반기 (Semi-annual)"}
    rec_dict = {
        "A": "즉시 대응 필요. 임원진 보고 및 전략 수립 시작",
        "B": "중점 모니터링. 관련 부서 정보 공유 및 대응 준비",
        "C": "정기 추적. 산업 보고서에 포함 및 변화 감시",
        "D": "참고 관찰. 데이터베이스에 기록 및 주기적 검토",
    }

    ranked_signals.append(
        {
            "rank": 0,
            "signal_id": signal_id,
            "title": signal.get("title", ""),
            "category": signal.get("category", {}).get("primary", "Unknown"),
            "subcategory": signal.get("subcategory", ""),
            "significance": signal.get("significance", 0),
            "status": signal.get("status", "emerging"),
            "scores": {
                "impact": round(impact_score, 2),
                "probability": round(prob_score, 2),
                "urgency": round(urgency_score, 2),
                "novelty": round(novelty_score, 2),
            },
            "weighted_score": round(weighted, 2),
            "final_score": round(final, 1),
            "grade": grade,
            "monitoring_cycle": monitoring_dict[grade],
            "recommendation": rec_dict[grade],
            "score_rationale": {
                "impact": impact_ratio,
                "probability": prob_ratio,
                "urgency": urgency_ratio,
                "novelty": novelty_ratio,
            },
        }
    )

# 정렬
ranked_signals.sort(key=lambda x: x["final_score"], reverse=True)
for idx, signal in enumerate(ranked_signals, 1):
    signal["rank"] = idx

print(f"점수 계산 완료: {len(ranked_signals)}개")

# 요약 생성
total = len(ranked_signals)
top_10 = ranked_signals[:10]

grade_dist = {"A": 0, "B": 0, "C": 0, "D": 0}
for sig in ranked_signals:
    grade_dist[sig["grade"]] += 1

cat_dist = {}
for sig in ranked_signals:
    cat = sig["category"]
    cat_dist[cat] = cat_dist.get(cat, 0) + 1

status_dist = {}
for sig in ranked_signals:
    status = sig["status"]
    status_dist[status] = status_dist.get(status, 0) + 1

avg_impact = sum(s["scores"]["impact"] for s in ranked_signals) / total
avg_prob = sum(s["scores"]["probability"] for s in ranked_signals) / total
avg_urgency = sum(s["scores"]["urgency"] for s in ranked_signals) / total
avg_novelty = sum(s["scores"]["novelty"] for s in ranked_signals) / total
avg_final = sum(s["final_score"] for s in ranked_signals) / total

summary = {
    "ranking_date": "2026-01-11",
    "total_ranked": total,
    "top_10_summary": {
        "signals": [s["signal_id"] for s in top_10],
        "categories": {s["category"]: sum(1 for x in top_10 if x["category"] == s["category"]) for s in top_10},
        "avg_priority_score": round(sum(s["final_score"] for s in top_10) / len(top_10) if top_10 else 0, 1),
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
        "A": {"count": grade_dist["A"], "percentage": round((grade_dist["A"] / total * 100), 1) if total > 0 else 0},
        "B": {"count": grade_dist["B"], "percentage": round((grade_dist["B"] / total * 100), 1) if total > 0 else 0},
        "C": {"count": grade_dist["C"], "percentage": round((grade_dist["C"] / total * 100), 1) if total > 0 else 0},
        "D": {"count": grade_dist["D"], "percentage": round((grade_dist["D"] / total * 100), 1) if total > 0 else 0},
    },
    "category_distribution": cat_dist,
    "status_distribution": status_dist,
    "average_scores": {
        "impact": round(avg_impact, 2),
        "probability": round(avg_prob, 2),
        "urgency": round(avg_urgency, 2),
        "novelty": round(avg_novelty, 2),
        "final_score": round(avg_final, 1),
    },
}

# 최종 출력 생성
output = {
    "ranking_date": "2026-01-11",
    "total_ranked": total,
    "methodology": {
        "formula": "(영향도 × 0.40) + (발생가능성 × 0.30) + (긴급도 × 0.20) + (신규성 × 0.10)",
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

# 저장
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n저장 완료: {output_file}")

# 통계 출력
print("\n" + "=" * 70)
print("우선순위 산정 결과 요약")
print("=" * 70)
print(f"\n총 분석 신호: {total}개")
print("\n등급 분포:")
print(f"  A등급 (즉시 대응):     {grade_dist['A']:3d}개 ({(grade_dist['A'] / total * 100):.1f}%)")
print(f"  B등급 (중점 모니터):   {grade_dist['B']:3d}개 ({(grade_dist['B'] / total * 100):.1f}%)")
print(f"  C등급 (정기 추적):     {grade_dist['C']:3d}개 ({(grade_dist['C'] / total * 100):.1f}%)")
print(f"  D등급 (참고 관찰):     {grade_dist['D']:3d}개 ({(grade_dist['D'] / total * 100):.1f}%)")

print("\n카테고리 분포:")
for cat in sorted(cat_dist.keys()):
    count = cat_dist[cat]
    pct = (count / total * 100) if total > 0 else 0
    print(f"  {cat:15s}: {count:3d}개 ({pct:5.1f}%)")

print("\n평균 차원별 점수 (10점 만점):")
print(f"  영향도(Impact):         {avg_impact:5.2f}/10")
print(f"  발생가능성(Probability):{avg_prob:5.2f}/10")
print(f"  긴급도(Urgency):        {avg_urgency:5.2f}/10")
print(f"  신규성(Novelty):        {avg_novelty:5.2f}/10")
print(f"  최종 점수 평균:         {avg_final:5.1f}/100")

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

print("\n" + "=" * 70)
print("우선순위 산정 완료!")
print("=" * 70)
