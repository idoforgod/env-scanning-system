"""
Similarity Batch - 배치 유사도 계산
===================================
토큰 절감: 기존 5K-8K → 2K-3K (60-70% 절감)

신호 간 유사도 비교를 배치로 처리하여 LLM 컨텍스트 토큰 절감.
관련 신호 그룹화 및 클러스터링 지원.
"""

import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class SimilarityResult:
    """유사도 계산 결과"""

    signal_id_1: str
    signal_id_2: str
    overall_similarity: float
    title_similarity: float
    content_similarity: float
    category_match: bool
    actor_overlap: float


class SimilarityBatch:
    """배치 유사도 계산 프로세서"""

    def __init__(self):
        # 불용어 (한/영)
        self.stopwords = {
            "이",
            "가",
            "은",
            "는",
            "을",
            "를",
            "의",
            "에",
            "에서",
            "로",
            "으로",
            "와",
            "과",
            "도",
            "만",
            "및",
            "등",
            "또한",
            "그리고",
            "하지만",
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "to",
            "of",
            "in",
            "for",
            "on",
            "with",
            "and",
            "but",
            "or",
            "this",
            "that",
            "it",
            "its",
            "they",
        }

        # 카테고리 계층 구조 (유사도 보정용)
        self.category_relations = {
            ("Technological", "Economic"): 0.7,
            ("Social", "Economic"): 0.6,
            ("Environmental", "Economic"): 0.6,
            ("Political", "Economic"): 0.5,
            ("Social", "Political"): 0.6,
            ("Environmental", "Political"): 0.5,
            ("Technological", "Social"): 0.4,
        }

    def tokenize(self, text: str) -> list[str]:
        """텍스트 토큰화"""
        text = text.lower()
        text = re.sub(r"[^\w\s가-힣]", " ", text)
        tokens = text.split()
        return [t for t in tokens if t not in self.stopwords and len(t) > 1]

    def compute_cosine_similarity(self, tokens1: list[str], tokens2: list[str]) -> float:
        """코사인 유사도 계산"""
        if not tokens1 or not tokens2:
            return 0.0

        tf1 = Counter(tokens1)
        tf2 = Counter(tokens2)
        common = set(tf1.keys()) & set(tf2.keys())

        if not common:
            return 0.0

        dot = sum(tf1[t] * tf2[t] for t in common)
        norm1 = math.sqrt(sum(v**2 for v in tf1.values()))
        norm2 = math.sqrt(sum(v**2 for v in tf2.values()))

        return dot / (norm1 * norm2) if norm1 and norm2 else 0.0

    def compute_title_similarity(self, title1: str, title2: str) -> float:
        """제목 유사도 계산"""
        tokens1 = self.tokenize(title1)
        tokens2 = self.tokenize(title2)
        return self.compute_cosine_similarity(tokens1, tokens2)

    def compute_content_similarity(self, sig1: dict, sig2: dict) -> float:
        """콘텐츠 유사도 계산 (제목 + 설명)"""
        text1 = f"{sig1.get('title', '')} {sig1.get('description', '')}"
        text2 = f"{sig2.get('title', '')} {sig2.get('description', '')}"

        tokens1 = self.tokenize(text1)
        tokens2 = self.tokenize(text2)

        return self.compute_cosine_similarity(tokens1, tokens2)

    def check_category_match(self, sig1: dict, sig2: dict) -> tuple[bool, float]:
        """카테고리 매칭 확인"""
        cat1 = sig1.get("category", {})
        cat2 = sig2.get("category", {})

        # 문자열인 경우 처리
        if isinstance(cat1, str):
            cat1 = {"primary": cat1}
        if isinstance(cat2, str):
            cat2 = {"primary": cat2}

        primary1 = cat1.get("primary", "")
        primary2 = cat2.get("primary", "")
        secondary1 = set(cat1.get("secondary", []))
        secondary2 = set(cat2.get("secondary", []))

        # 정확 매치
        if primary1 == primary2:
            return True, 1.0

        # 교차 매치 (primary가 다른 쪽의 secondary에 있음)
        if primary1 in secondary2 or primary2 in secondary1:
            return True, 0.8

        # secondary 교집합
        if secondary1 & secondary2:
            return True, 0.6

        # 관련 카테고리
        pair = tuple(sorted([primary1, primary2]))
        if pair in self.category_relations:
            return False, self.category_relations[pair]

        return False, 0.0

    def compute_actor_overlap(self, sig1: dict, sig2: dict) -> float:
        """행위자 겹침 비율 계산"""
        actors1 = sig1.get("actors", [])
        actors2 = sig2.get("actors", [])

        if not actors1 or not actors2:
            return 0.0

        # 이름 정규화
        names1 = set()
        names2 = set()

        for actor in actors1:
            if isinstance(actor, dict):
                names1.add(actor.get("name", "").lower())
            else:
                names1.add(str(actor).lower())

        for actor in actors2:
            if isinstance(actor, dict):
                names2.add(actor.get("name", "").lower())
            else:
                names2.add(str(actor).lower())

        intersection = len(names1 & names2)
        union = len(names1 | names2)

        return intersection / union if union > 0 else 0.0

    def compute_overall_similarity(self, sig1: dict, sig2: dict) -> SimilarityResult:
        """종합 유사도 계산"""
        sig_id_1 = sig1.get("id", sig1.get("signal_id", "unknown"))
        sig_id_2 = sig2.get("id", sig2.get("signal_id", "unknown"))

        title_sim = self.compute_title_similarity(sig1.get("title", ""), sig2.get("title", ""))
        content_sim = self.compute_content_similarity(sig1, sig2)
        cat_match, cat_sim = self.check_category_match(sig1, sig2)
        actor_overlap = self.compute_actor_overlap(sig1, sig2)

        # 가중 평균 (제목 30%, 콘텐츠 40%, 카테고리 15%, 행위자 15%)
        overall = title_sim * 0.30 + content_sim * 0.40 + cat_sim * 0.15 + actor_overlap * 0.15

        return SimilarityResult(
            signal_id_1=sig_id_1,
            signal_id_2=sig_id_2,
            overall_similarity=round(overall, 3),
            title_similarity=round(title_sim, 3),
            content_similarity=round(content_sim, 3),
            category_match=cat_match,
            actor_overlap=round(actor_overlap, 3),
        )

    def find_related_signals(
        self, target_signal: dict, candidate_signals: list[dict], min_similarity: float = 0.3, max_results: int = 10
    ) -> list[dict]:
        """
        타겟 신호와 관련된 신호 찾기

        Args:
            target_signal: 기준 신호
            candidate_signals: 후보 신호 리스트
            min_similarity: 최소 유사도 임계값
            max_results: 최대 결과 수

        Returns:
            관련 신호 리스트 (유사도 순)
        """
        results = []
        target_id = target_signal.get("id", target_signal.get("signal_id", ""))

        for candidate in candidate_signals:
            cand_id = candidate.get("id", candidate.get("signal_id", ""))
            if cand_id == target_id:
                continue

            sim_result = self.compute_overall_similarity(target_signal, candidate)

            if sim_result.overall_similarity >= min_similarity:
                results.append(
                    {
                        "signal_id": cand_id,
                        "title": candidate.get("title", ""),
                        "overall_similarity": sim_result.overall_similarity,
                        "title_similarity": sim_result.title_similarity,
                        "content_similarity": sim_result.content_similarity,
                        "category_match": sim_result.category_match,
                        "actor_overlap": sim_result.actor_overlap,
                    }
                )

        # 유사도 순 정렬
        results.sort(key=lambda x: x["overall_similarity"], reverse=True)
        return results[:max_results]

    def batch_compute_similarity_matrix(self, signals: list[dict], min_similarity: float = 0.3) -> dict[str, Any]:
        """
        신호 배치 유사도 매트릭스 계산

        Args:
            signals: 신호 리스트
            min_similarity: 최소 유사도 (이 이상만 기록)

        Returns:
            {
                "pairs": [...],
                "matrix": {...},
                "clusters": [...],
                "statistics": {...}
            }
        """
        n = len(signals)
        if n < 2:
            return {"pairs": [], "matrix": {}, "clusters": [], "statistics": {"total_signals": n, "pairs_computed": 0}}

        pairs = []
        matrix = defaultdict(list)
        pairs_computed = 0

        for i in range(n):
            sig1 = signals[i]
            id1 = sig1.get("id", sig1.get("signal_id", f"sig_{i}"))

            for j in range(i + 1, n):
                sig2 = signals[j]
                id2 = sig2.get("id", sig2.get("signal_id", f"sig_{j}"))

                sim_result = self.compute_overall_similarity(sig1, sig2)
                pairs_computed += 1

                if sim_result.overall_similarity >= min_similarity:
                    pair_data = {
                        "signal_id_1": id1,
                        "signal_id_2": id2,
                        "overall_similarity": sim_result.overall_similarity,
                        "title_similarity": sim_result.title_similarity,
                        "content_similarity": sim_result.content_similarity,
                        "category_match": sim_result.category_match,
                        "actor_overlap": sim_result.actor_overlap,
                    }
                    pairs.append(pair_data)
                    matrix[id1].append({"signal_id": id2, "similarity": sim_result.overall_similarity})
                    matrix[id2].append({"signal_id": id1, "similarity": sim_result.overall_similarity})

        # 각 신호의 관련 신호 정렬
        for sig_id in matrix:
            matrix[sig_id].sort(key=lambda x: x["similarity"], reverse=True)

        # 클러스터링
        clusters = self._cluster_signals(
            pairs, [s.get("id", s.get("signal_id", f"sig_{i}")) for i, s in enumerate(signals)]
        )

        # 통계
        similarities = [p["overall_similarity"] for p in pairs]
        stats = {
            "total_signals": n,
            "pairs_computed": pairs_computed,
            "pairs_above_threshold": len(pairs),
            "average_similarity": round(sum(similarities) / len(similarities), 3) if similarities else 0,
            "max_similarity": max(similarities) if similarities else 0,
            "min_similarity": min(similarities) if similarities else 0,
            "cluster_count": len(clusters),
        }

        return {"pairs": pairs, "matrix": dict(matrix), "clusters": clusters, "statistics": stats}

    def _cluster_signals(self, pairs: list[dict], all_ids: list[str]) -> list[dict]:
        """Union-Find 기반 클러스터링"""
        parent = {id_: id_ for id_ in all_ids}
        rank = dict.fromkeys(all_ids, 0)

        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x, y):
            px, py = find(x), find(y)
            if px == py:
                return
            if rank[px] < rank[py]:
                px, py = py, px
            parent[py] = px
            if rank[px] == rank[py]:
                rank[px] += 1

        # 높은 유사도 쌍 연결 (0.5 이상)
        for pair in pairs:
            if pair["overall_similarity"] >= 0.5:
                union(pair["signal_id_1"], pair["signal_id_2"])

        # 클러스터 수집
        clusters_dict = defaultdict(list)
        for id_ in all_ids:
            clusters_dict[find(id_)].append(id_)

        # 클러스터 메타데이터
        result = []
        for _root, members in clusters_dict.items():
            if len(members) > 1:
                # 클러스터 내 평균 유사도 계산
                cluster_pairs = [p for p in pairs if p["signal_id_1"] in members and p["signal_id_2"] in members]
                avg_sim = (
                    sum(p["overall_similarity"] for p in cluster_pairs) / len(cluster_pairs) if cluster_pairs else 0
                )

                result.append(
                    {
                        "cluster_id": f"CLUSTER-{len(result) + 1:03d}",
                        "member_count": len(members),
                        "members": members,
                        "average_internal_similarity": round(avg_sim, 3),
                    }
                )

        # 크기순 정렬
        result.sort(key=lambda x: x["member_count"], reverse=True)
        return result

    def find_cross_category_connections(self, signals: list[dict], min_similarity: float = 0.4) -> list[dict]:
        """
        카테고리 간 연결 신호 탐지

        다른 카테고리에 속하지만 높은 유사도를 보이는 신호 쌍 발견.
        Futures Wheel 분석에 활용.

        Returns:
            [{"signal_1": {...}, "signal_2": {...}, "connection_type": "...", ...}]
        """
        connections = []

        for i, sig1 in enumerate(signals):
            cat1 = sig1.get("category", {})
            if isinstance(cat1, str):
                cat1 = {"primary": cat1}
            primary1 = cat1.get("primary", "Unknown")

            for j, sig2 in enumerate(signals):
                if i >= j:
                    continue

                cat2 = sig2.get("category", {})
                if isinstance(cat2, str):
                    cat2 = {"primary": cat2}
                primary2 = cat2.get("primary", "Unknown")

                # 다른 카테고리만
                if primary1 == primary2:
                    continue

                sim_result = self.compute_overall_similarity(sig1, sig2)

                if sim_result.overall_similarity >= min_similarity:
                    connections.append(
                        {
                            "signal_1": {
                                "id": sig1.get("id", sig1.get("signal_id", "")),
                                "title": sig1.get("title", ""),
                                "category": primary1,
                            },
                            "signal_2": {
                                "id": sig2.get("id", sig2.get("signal_id", "")),
                                "title": sig2.get("title", ""),
                                "category": primary2,
                            },
                            "similarity": sim_result.overall_similarity,
                            "connection_type": f"{primary1}-{primary2}",
                            "shared_actors": sim_result.actor_overlap > 0
                            if hasattr(sim_result, "actor_overlap")
                            else False,
                        }
                    )

        connections.sort(key=lambda x: x["similarity"], reverse=True)
        return connections

    def generate_signal_network(self, signals: list[dict], min_similarity: float = 0.3) -> dict[str, Any]:
        """
        신호 네트워크 그래프 데이터 생성 (시각화용)

        Returns:
            {
                "nodes": [{"id": "...", "title": "...", "category": "...", ...}],
                "edges": [{"source": "...", "target": "...", "weight": ...}],
                "metadata": {...}
            }
        """
        nodes = []
        edges = []
        node_ids = set()

        # 노드 생성
        for sig in signals:
            sig_id = sig.get("id", sig.get("signal_id", ""))
            cat = sig.get("category", {})
            primary_cat = cat if isinstance(cat, str) else cat.get("primary", "Unknown")

            nodes.append(
                {
                    "id": sig_id,
                    "title": sig.get("title", ""),
                    "category": primary_cat,
                    "significance": sig.get("significance", 3),
                    "confidence": sig.get("confidence", 0.5),
                }
            )
            node_ids.add(sig_id)

        # 엣지 생성
        for i, sig1 in enumerate(signals):
            id1 = sig1.get("id", sig1.get("signal_id", ""))

            for j, sig2 in enumerate(signals):
                if i >= j:
                    continue

                id2 = sig2.get("id", sig2.get("signal_id", ""))
                sim_result = self.compute_overall_similarity(sig1, sig2)

                if sim_result.overall_similarity >= min_similarity:
                    edges.append(
                        {
                            "source": id1,
                            "target": id2,
                            "weight": sim_result.overall_similarity,
                            "category_match": sim_result.category_match,
                        }
                    )

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "min_similarity_threshold": min_similarity,
                "generated_at": datetime.now().isoformat(),
            },
        }


def main():
    """CLI 실행 예제"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python similarity_batch.py <signals_json_file>")
        print("       python similarity_batch.py --test")
        sys.exit(1)

    if sys.argv[1] == "--test":
        processor = SimilarityBatch()

        # 테스트 데이터
        test_signals = [
            {
                "id": "SIG-001",
                "title": "삼성전자 AI 반도체 양산 시작",
                "description": "삼성전자가 AI 전용 반도체의 대량 생산을 시작했다.",
                "category": {"primary": "Technological", "secondary": ["Economic"]},
                "actors": [{"name": "Samsung"}],
                "significance": 4,
            },
            {
                "id": "SIG-002",
                "title": "SK하이닉스 AI 메모리 생산 확대",
                "description": "SK하이닉스가 AI 관련 메모리 반도체 생산을 늘린다.",
                "category": {"primary": "Technological", "secondary": ["Economic"]},
                "actors": [{"name": "SK Hynix"}],
                "significance": 4,
            },
            {
                "id": "SIG-003",
                "title": "유럽연합 AI 규제법 시행",
                "description": "EU가 세계 최초 포괄적 AI 규제법을 시행했다.",
                "category": {"primary": "Political", "secondary": ["Technological"]},
                "actors": [{"name": "European Union"}],
                "significance": 5,
            },
            {
                "id": "SIG-004",
                "title": "미국 반도체 지원법 효과 분석",
                "description": "미국 CHIPS Act의 1년 효과를 분석한 보고서가 발표됐다.",
                "category": {"primary": "Political", "secondary": ["Economic"]},
                "actors": [{"name": "US Government"}],
                "significance": 3,
            },
        ]

        # 배치 유사도 계산
        result = processor.batch_compute_similarity_matrix(test_signals, min_similarity=0.2)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        with open(sys.argv[1], encoding="utf-8") as f:
            data = json.load(f)

        signals = data.get("signals", data if isinstance(data, list) else [data])

        processor = SimilarityBatch()
        result = processor.batch_compute_similarity_matrix(signals)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
