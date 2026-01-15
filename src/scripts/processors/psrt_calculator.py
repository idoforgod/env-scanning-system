"""
pSRT Calculator - predicted Signal Reliability Test 점수 계산기
================================================================
토큰 절감: 기존 8K-12K → 2K-3K (70-75% 절감)

LLM이 수행하던 pSRT 점수 계산을 결정론적 Python 로직으로 외부화.
설정 파일(pSRT-config.yaml)을 로드하여 일관된 점수 산정.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


class PSRTCalculator:
    """pSRT (predicted Signal Reliability Test) 점수 계산기"""

    def __init__(self, config_path: str | None = None):
        """
        Args:
            config_path: pSRT-config.yaml 파일 경로 (없으면 기본 경로 사용)
        """
        if config_path is None:
            base_path = Path(__file__).parent.parent
            config_path = base_path / "config" / "pSRT-config.yaml"

        self.config = self._load_config(config_path)
        self.grade_ranges = self._build_grade_ranges()

    def _load_config(self, config_path: str | Path) -> dict:
        """설정 파일 로드"""
        config_path = Path(config_path)
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        else:
            # 기본 설정 반환
            return self._get_default_config()

    def _get_default_config(self) -> dict:
        """기본 설정값"""
        return {
            "overall_weights": {"source_pSRT": 0.20, "signal_pSRT": 0.35, "analysis_pSRT": 0.25, "report_pSRT": 0.20},
            "source_pSRT": {
                "authority_scores": {"tier_1": 100, "tier_2": 75, "tier_3": 50, "tier_4": 25, "unknown": 10},
                "verifiability_scores": {
                    "full_verification": 100,
                    "partial_verification": 70,
                    "indirect_verification": 40,
                    "no_verification": 10,
                },
            },
            "signal_pSRT": {
                "specificity_criteria": {
                    "has_date": 20,
                    "has_numbers": 20,
                    "has_actors": 20,
                    "has_location": 20,
                    "has_mechanism": 20,
                },
                "freshness_decay": {
                    "within_24h": 100,
                    "within_48h": 85,
                    "within_72h": 70,
                    "within_7d": 50,
                    "within_30d": 30,
                    "older": 10,
                },
            },
            "grade_system": {
                "A_plus": {"range": [90, 100]},
                "A": {"range": [80, 89]},
                "B": {"range": [70, 79]},
                "C": {"range": [60, 69]},
                "D": {"range": [50, 59]},
                "E": {"range": [40, 49]},
                "F": {"range": [0, 39]},
            },
        }

    def _build_grade_ranges(self) -> list[tuple[str, int, int]]:
        """등급 범위 빌드"""
        grades = self.config.get("grade_system", {})
        result = []
        for grade_name, grade_info in grades.items():
            range_vals = grade_info.get("range", [0, 100])
            result.append((grade_name, range_vals[0], range_vals[1]))
        # 점수 내림차순 정렬
        return sorted(result, key=lambda x: x[1], reverse=True)

    def calculate_source_psrt(self, signal: dict) -> dict[str, Any]:
        """
        Source pSRT 계산 - 소스의 신뢰도 평가

        Returns:
            {
                "score": 0-100,
                "breakdown": {"authority": x, "verifiability": y, ...},
                "factors": ["tier_2 source", ...]
            }
        """
        source = signal.get("source", {})
        source_config = self.config.get("source_pSRT", {})

        # 1. Authority Score (권위성)
        tier = source.get("tier", 4)
        tier_key = f"tier_{tier}" if isinstance(tier, int) else "unknown"
        authority_scores = source_config.get("authority_scores", {})
        authority = authority_scores.get(tier_key, 10)

        # 2. Verifiability Score (검증 가능성)
        url = source.get("url", "")
        verifiability = 70 if url and url.startswith("http") else 10

        # 3. Historical Accuracy (역사적 정확성) - 기본값 사용
        historical = 60

        # 4. Cross Validation (교차 검증)
        cross_val = 50  # 기본값

        # 가중치 적용
        weights = source_config.get(
            "weights", {"authority": 0.30, "verifiability": 0.25, "historical_accuracy": 0.25, "cross_validation": 0.20}
        )

        score = (
            authority * weights.get("authority", 0.30)
            + verifiability * weights.get("verifiability", 0.25)
            + historical * weights.get("historical_accuracy", 0.25)
            + cross_val * weights.get("cross_validation", 0.20)
        )

        factors = []
        if tier <= 2:
            factors.append(f"tier_{tier}_high_authority")
        if url:
            factors.append("url_verifiable")

        return {
            "score": round(score, 1),
            "breakdown": {
                "authority": authority,
                "verifiability": verifiability,
                "historical_accuracy": historical,
                "cross_validation": cross_val,
            },
            "factors": factors,
        }

    def calculate_signal_psrt(self, signal: dict) -> dict[str, Any]:
        """
        Signal pSRT 계산 - 신호 자체의 신뢰도 평가

        Returns:
            {
                "score": 0-100,
                "breakdown": {"specificity": x, "freshness": y, ...},
                "factors": ["has_date", "has_numbers", ...]
            }
        """
        signal_config = self.config.get("signal_pSRT", {})
        spec_criteria = signal_config.get("specificity_criteria", {})

        title = signal.get("title", "")
        description = signal.get("description", "")
        content = f"{title} {description}"

        # 1. Specificity (구체성)
        specificity = 0
        factors = []

        # has_date: 날짜 패턴 검출
        date_patterns = [
            r"\d{4}[-/]\d{1,2}[-/]\d{1,2}",
            r"\d{1,2}월\s*\d{1,2}일",
            r"202[4-9]년",
            r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}",
        ]
        if any(re.search(p, content, re.I) for p in date_patterns):
            specificity += spec_criteria.get("has_date", 20)
            factors.append("has_date")

        # has_numbers: 수치 데이터 검출
        number_patterns = [
            r"\d+%",
            r"\$\d+",
            r"₩\d+",
            r"\d+억",
            r"\d+만",
            r"\d+\.\d+",
            r"\d{1,3}(,\d{3})+",
        ]
        if any(re.search(p, content) for p in number_patterns):
            specificity += spec_criteria.get("has_numbers", 20)
            factors.append("has_numbers")

        # has_actors: 행위자 검출
        actors = signal.get("actors", [])
        if actors or re.search(r"(기업|회사|정부|연구소|대학|기관|Inc\.|Corp\.|Ltd\.)", content):
            specificity += spec_criteria.get("has_actors", 20)
            factors.append("has_actors")

        # has_location: 지역/장소 검출
        location_patterns = [
            r"(서울|부산|대구|인천|광주|대전|울산|경기|강원)",
            r"(미국|중국|일본|유럽|EU|영국|독일|프랑스)",
            r"(Silicon Valley|Washington|Beijing|Tokyo|London)",
        ]
        if any(re.search(p, content, re.I) for p in location_patterns):
            specificity += spec_criteria.get("has_location", 20)
            factors.append("has_location")

        # has_mechanism: 메커니즘 설명 검출
        mechanism_patterns = [
            r"(통해|인해|때문에|결과|효과|영향|가능)",
            r"(through|because|due to|as a result|enables|affects)",
        ]
        if any(re.search(p, content, re.I) for p in mechanism_patterns):
            specificity += spec_criteria.get("has_mechanism", 20)
            factors.append("has_mechanism")

        # 2. Freshness (신선도)
        freshness_decay = signal_config.get("freshness_decay", {})
        published_date = signal.get("source", {}).get("published_date", "")
        freshness = self._calculate_freshness(published_date, freshness_decay)

        # 3. Independence (독립성)
        independence = 60  # 기본값

        # 4. Measurability (측정 가능성)
        measurability = 50 if "has_numbers" in factors else 30

        # 5. Pattern Fit (패턴 일치)
        pattern_fit = 50

        # 가중치 적용
        weights = signal_config.get(
            "weights",
            {"specificity": 0.25, "freshness": 0.20, "independence": 0.20, "measurability": 0.20, "pattern_fit": 0.15},
        )

        score = (
            specificity * weights.get("specificity", 0.25)
            + freshness * weights.get("freshness", 0.20)
            + independence * weights.get("independence", 0.20)
            + measurability * weights.get("measurability", 0.20)
            + pattern_fit * weights.get("pattern_fit", 0.15)
        )

        return {
            "score": round(score, 1),
            "breakdown": {
                "specificity": specificity,
                "freshness": freshness,
                "independence": independence,
                "measurability": measurability,
                "pattern_fit": pattern_fit,
            },
            "factors": factors,
        }

    def _calculate_freshness(self, published_date: str, decay_config: dict) -> int:
        """발행일 기준 신선도 계산"""
        if not published_date:
            return decay_config.get("older", 10)

        try:
            # 다양한 날짜 형식 파싱
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    pub_dt = datetime.strptime(published_date[:10], fmt[: 10 if "T" not in fmt else fmt.find("T")])
                    break
                except ValueError:
                    continue
            else:
                pub_dt = datetime.strptime(published_date[:10], "%Y-%m-%d")

            now = datetime.now()
            days_ago = (now - pub_dt).days

            if days_ago <= 1:
                return decay_config.get("within_24h", 100)
            elif days_ago <= 2:
                return decay_config.get("within_48h", 85)
            elif days_ago <= 3:
                return decay_config.get("within_72h", 70)
            elif days_ago <= 7:
                return decay_config.get("within_7d", 50)
            elif days_ago <= 30:
                return decay_config.get("within_30d", 30)
            else:
                return decay_config.get("older", 10)
        except Exception:
            return decay_config.get("within_7d", 50)

    def calculate_analysis_psrt(self, signal: dict) -> dict[str, Any]:
        """
        Analysis pSRT 계산 - 분석의 신뢰도 평가

        Returns:
            {
                "score": 0-100,
                "breakdown": {"classification_clarity": x, ...},
                "factors": [...]
            }
        """
        analysis_config = self.config.get("analysis_pSRT", {})

        # 1. Classification Clarity (분류 명확성)
        category = signal.get("category", {})
        classification_clarity = 0
        factors = []

        if isinstance(category, dict):
            primary = category.get("primary", "")
            secondary = category.get("secondary", [])
            if primary:
                classification_clarity += 40
                factors.append("has_primary_category")
            if secondary:
                classification_clarity += 30
                factors.append("has_secondary_category")
        elif category:
            classification_clarity += 40
            factors.append("has_category")

        # 태그 존재 여부
        tags = signal.get("tags", [])
        if tags and len(tags) >= 2:
            classification_clarity += 30
            factors.append("has_relevant_tags")

        # 2. Impact Evidence (영향도 근거)
        impact_evidence = 0

        potential_impact = signal.get("potential_impact", {})
        if potential_impact:
            if potential_impact.get("short_term"):
                impact_evidence += 30
            if potential_impact.get("mid_term"):
                impact_evidence += 20
            if potential_impact.get("long_term"):
                impact_evidence += 20
            factors.append("has_impact_assessment")

        significance_reason = signal.get("significance_reason", "")
        if significance_reason and len(significance_reason) > 20:
            impact_evidence += 30
            factors.append("has_significance_reason")

        # 3. Priority Consistency (우선순위 일관성)
        significance = signal.get("significance", 3)
        confidence = signal.get("confidence", 0.5)

        # significance와 confidence의 일관성 체크
        priority_consistency = 50
        if significance >= 4 and confidence >= 0.7:
            priority_consistency = 80
            factors.append("high_priority_consistent")
        elif significance <= 2 and confidence <= 0.5:
            priority_consistency = 70
            factors.append("low_priority_consistent")
        elif significance >= 4 and confidence < 0.5:
            priority_consistency = 30  # 불일치
            factors.append("priority_inconsistent")

        # 4. Comparative Validation (비교 검증)
        comparative = 50  # 기본값

        # 가중치 적용
        weights = analysis_config.get(
            "weights",
            {
                "classification_clarity": 0.25,
                "impact_evidence": 0.30,
                "priority_consistency": 0.25,
                "comparative_validation": 0.20,
            },
        )

        score = (
            classification_clarity * weights.get("classification_clarity", 0.25)
            + impact_evidence * weights.get("impact_evidence", 0.30)
            + priority_consistency * weights.get("priority_consistency", 0.25)
            + comparative * weights.get("comparative_validation", 0.20)
        )

        return {
            "score": round(score, 1),
            "breakdown": {
                "classification_clarity": classification_clarity,
                "impact_evidence": impact_evidence,
                "priority_consistency": priority_consistency,
                "comparative_validation": comparative,
            },
            "factors": factors,
        }

    def calculate_overall_psrt(self, signal: dict) -> dict[str, Any]:
        """
        종합 pSRT 점수 계산

        Returns:
            {
                "overall": 0-100,
                "grade": "A+" | "A" | "B" | ... | "F",
                "breakdown": {
                    "source": {...},
                    "signal": {...},
                    "analysis": {...}
                },
                "flags": [...],
                "action": "즉시 활용 가능" | ...
            }
        """
        source_result = self.calculate_source_psrt(signal)
        signal_result = self.calculate_signal_psrt(signal)
        analysis_result = self.calculate_analysis_psrt(signal)

        weights = self.config.get("overall_weights", {})

        overall = (
            source_result["score"] * weights.get("source_pSRT", 0.20)
            + signal_result["score"] * weights.get("signal_pSRT", 0.35)
            + analysis_result["score"] * weights.get("analysis_pSRT", 0.25)
        )
        # report_pSRT는 개별 신호에 적용 안함
        # 가중치 합계 조정 (0.80으로 나눠서 100점 만점 스케일)
        overall = overall / 0.80
        overall = min(100, max(0, round(overall, 1)))

        grade = self._score_to_grade(overall)
        flags = self._detect_hallucination_flags(signal, source_result, signal_result, analysis_result)
        action = self._get_action_recommendation(grade, flags)

        return {
            "overall": overall,
            "grade": grade,
            "breakdown": {
                "source": source_result["score"],
                "signal": signal_result["score"],
                "analysis": analysis_result["score"],
            },
            "detailed_breakdown": {"source": source_result, "signal": signal_result, "analysis": analysis_result},
            "flags": flags,
            "action": action,
        }

    def _score_to_grade(self, score: float) -> str:
        """점수를 등급으로 변환"""
        for grade_name, min_score, max_score in self.grade_ranges:
            if min_score <= score <= max_score:
                return grade_name.replace("_", "+") if "_" in grade_name else grade_name
        return "F"

    def _detect_hallucination_flags(
        self, signal: dict, source_result: dict, signal_result: dict, analysis_result: dict
    ) -> list[dict]:
        """할루시네이션 플래그 탐지"""
        flags = []
        self.config.get("hallucination_detection", {}).get("rules", {})

        specificity = signal_result["breakdown"]["specificity"]
        independence = signal_result["breakdown"]["independence"]
        significance = signal.get("significance", 3)
        impact_evidence = analysis_result["breakdown"]["impact_evidence"]
        freshness = signal_result["breakdown"]["freshness"]
        source_score = source_result["score"]

        # signal_fabrication_risk
        if specificity < 30 and independence < 40:
            flags.append(
                {
                    "type": "SIGNAL_FABRICATION_RISK",
                    "severity": "high",
                    "reason": f"Low specificity ({specificity}) and independence ({independence})",
                    "action": "verify",
                }
            )

        # overinterpretation
        if significance >= 4 and impact_evidence < 40:
            flags.append(
                {
                    "type": "OVERINTERPRETATION",
                    "severity": "medium",
                    "reason": f"High significance ({significance}) but low evidence ({impact_evidence})",
                    "action": "downgrade",
                }
            )

        # temporal_confusion
        if freshness < 30:
            flags.append(
                {
                    "type": "TEMPORAL_CONFUSION",
                    "severity": "medium",
                    "reason": f"Low freshness score ({freshness})",
                    "action": "verify_date",
                }
            )

        # vague_signal
        if specificity < 30:
            flags.append(
                {
                    "type": "VAGUE_SIGNAL",
                    "severity": "medium",
                    "reason": f"Very low specificity ({specificity})",
                    "action": "verify",
                }
            )

        # low_source_quality
        if source_score < 50 and significance >= 4:
            flags.append(
                {
                    "type": "LOW_SOURCE_QUALITY",
                    "severity": "medium",
                    "reason": f"Low source score ({source_score}) with high significance ({significance})",
                    "action": "verify",
                }
            )

        return flags

    def _get_action_recommendation(self, grade: str, flags: list[dict]) -> str:
        """등급과 플래그 기반 조치 권장"""
        grade_system = self.config.get("grade_system", {})

        # 심각한 플래그가 있으면 조치 변경
        has_high_flag = any(f.get("severity") == "high" for f in flags)
        has_critical_flag = any(f.get("severity") == "critical" for f in flags)

        if has_critical_flag:
            return "즉시 검토 필요"

        if has_high_flag:
            return "추가 검증 필수"

        # 등급별 기본 조치
        grade_key = grade.replace("+", "_plus")
        grade_info = grade_system.get(grade_key, {})
        return grade_info.get("action", "검토 필요")

    def process_batch(self, signals: list[dict]) -> dict[str, Any]:
        """
        신호 배치 처리

        Args:
            signals: 신호 리스트

        Returns:
            {
                "processed_count": N,
                "results": [...],
                "summary": {
                    "average_pSRT": X,
                    "by_grade": {...},
                    "flags_count": {...}
                }
            }
        """
        results = []
        by_grade = {}
        flags_count = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        total_score = 0

        for signal in signals:
            psrt_result = self.calculate_overall_psrt(signal)

            result = {
                "signal_id": signal.get("id", signal.get("signal_id", "unknown")),
                "title": signal.get("title", ""),
                "pSRT": psrt_result,
            }
            results.append(result)

            # 통계 수집
            grade = psrt_result["grade"]
            by_grade[grade] = by_grade.get(grade, 0) + 1
            total_score += psrt_result["overall"]

            for flag in psrt_result.get("flags", []):
                severity = flag.get("severity", "low")
                flags_count[severity] = flags_count.get(severity, 0) + 1

        return {
            "processed_count": len(signals),
            "results": results,
            "summary": {
                "average_pSRT": round(total_score / len(signals), 1) if signals else 0,
                "by_grade": by_grade,
                "flags_count": flags_count,
            },
        }


def main():
    """CLI 실행 예제"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python psrt_calculator.py <signals_json_file>")
        print("       python psrt_calculator.py --test")
        sys.exit(1)

    if sys.argv[1] == "--test":
        # 테스트 실행
        calculator = PSRTCalculator()
        test_signal = {
            "id": "SIG-2026-0112-001",
            "title": "삼성전자, 2026년 AI 반도체 매출 50% 증가 전망",
            "description": "삼성전자가 2026년 AI 반도체 매출이 전년 대비 50% 증가할 것으로 전망했다.",
            "category": {"primary": "Technological", "secondary": ["Economic"]},
            "source": {
                "name": "Reuters",
                "url": "https://reuters.com/example",
                "tier": 2,
                "published_date": "2026-01-11",
            },
            "significance": 4,
            "significance_reason": "AI 반도체 시장의 급성장을 나타내는 중요 지표",
            "confidence": 0.85,
            "actors": [{"name": "Samsung Electronics", "type": "company"}],
            "tags": ["AI", "semiconductor", "Samsung"],
            "potential_impact": {
                "short_term": "반도체 주가 상승",
                "mid_term": "AI 인프라 투자 확대",
                "long_term": "AI 생태계 재편",
            },
        }

        result = calculator.calculate_overall_psrt(test_signal)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 파일 처리
        with open(sys.argv[1], encoding="utf-8") as f:
            data = json.load(f)

        signals = data.get("signals", data if isinstance(data, list) else [data])
        calculator = PSRTCalculator()
        result = calculator.process_batch(signals)

        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
