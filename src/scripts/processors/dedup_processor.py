"""
Dedup Processor - 결정론적 중복 신호 제거
==========================================
토큰 절감: 기존 6K-10K → 1K-2K (60-80% 절감)

LLM이 수행하던 유사도 판단을 결정론적 알고리즘으로 외부화.
TF-IDF 및 코사인 유사도 기반 중복 탐지.
"""

import hashlib
import json
import math
import re
from collections import Counter
from datetime import datetime
from typing import Any


class DedupProcessor:
    """결정론적 중복 신호 제거 프로세서"""

    def __init__(self, similarity_threshold: float = 0.85, time_window_days: int = 7, min_token_overlap: float = 0.6):
        """
        Args:
            similarity_threshold: 중복 판정 유사도 임계값 (0-1)
            time_window_days: 중복 검사 시간 윈도우 (일)
            min_token_overlap: 최소 토큰 겹침 비율
        """
        self.similarity_threshold = similarity_threshold
        self.time_window_days = time_window_days
        self.min_token_overlap = min_token_overlap

        # 한국어/영어 불용어
        self.stopwords = {
            # 한국어
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
            "까지",
            "부터",
            "에게",
            "한테",
            "께",
            "더",
            "그",
            "저",
            "이런",
            "그런",
            "저런",
            "어떤",
            "무슨",
            "어느",
            "및",
            "등",
            "또한",
            "그리고",
            "하지만",
            "그러나",
            "따라서",
            "때문에",
            "것",
            "수",
            "때",
            "바",
            "거",
            "등등",
            "에서는",
            "으로는",
            "에게는",
            # 영어
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "to",
            "of",
            "in",
            "for",
            "on",
            "with",
            "at",
            "by",
            "from",
            "as",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "under",
            "again",
            "and",
            "but",
            "or",
            "nor",
            "so",
            "yet",
            "both",
            "either",
            "neither",
            "this",
            "that",
            "these",
            "those",
            "it",
            "its",
            "their",
            "they",
        }

    def tokenize(self, text: str) -> list[str]:
        """텍스트 토큰화 (한국어/영어 혼합 지원)"""
        # 소문자 변환 및 특수문자 제거
        text = text.lower()
        text = re.sub(r"[^\w\s가-힣]", " ", text)

        # 토큰 분리
        tokens = text.split()

        # 불용어 제거 및 최소 길이 필터
        tokens = [t for t in tokens if t not in self.stopwords and len(t) > 1]

        return tokens

    def compute_signature(self, text: str) -> str:
        """텍스트 시그니처 (해시) 생성"""
        tokens = self.tokenize(text)
        normalized = " ".join(sorted(set(tokens)))
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def compute_similarity(self, text1: str, text2: str) -> float:
        """두 텍스트 간 코사인 유사도 계산 (TF 기반)"""
        tokens1 = self.tokenize(text1)
        tokens2 = self.tokenize(text2)

        if not tokens1 or not tokens2:
            return 0.0

        # TF 벡터 생성
        tf1 = Counter(tokens1)
        tf2 = Counter(tokens2)

        # 공통 어휘
        common_terms = set(tf1.keys()) & set(tf2.keys())

        if not common_terms:
            return 0.0

        # 코사인 유사도
        dot_product = sum(tf1[t] * tf2[t] for t in common_terms)
        norm1 = math.sqrt(sum(v**2 for v in tf1.values()))
        norm2 = math.sqrt(sum(v**2 for v in tf2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def compute_jaccard(self, text1: str, text2: str) -> float:
        """Jaccard 유사도 계산"""
        tokens1 = set(self.tokenize(text1))
        tokens2 = set(self.tokenize(text2))

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def is_within_time_window(self, date1: str, date2: str) -> bool:
        """두 날짜가 시간 윈도우 내에 있는지 확인"""
        try:
            d1 = datetime.strptime(date1[:10], "%Y-%m-%d")
            d2 = datetime.strptime(date2[:10], "%Y-%m-%d")
            return abs((d1 - d2).days) <= self.time_window_days
        except (ValueError, TypeError):
            return True  # 날짜 파싱 실패 시 시간 조건 무시

    def extract_signal_text(self, signal: dict) -> str:
        """신호에서 비교용 텍스트 추출"""
        parts = [
            signal.get("title", ""),
            signal.get("description", ""),
            signal.get("summary", ""),  # 네이버 크롤링 등에서 사용
        ]
        # 태그도 포함
        tags = signal.get("tags", [])
        if tags:
            parts.append(" ".join(tags))
        # key_entities도 포함
        entities = signal.get("key_entities", [])
        if entities:
            parts.append(" ".join(entities))

        return " ".join(filter(None, parts))

    def find_duplicates(self, new_signals: list[dict], existing_signals: list[dict]) -> dict[str, Any]:
        """
        새 신호 중 기존 신호와 중복되는 것 탐지

        Args:
            new_signals: 새로 수집된 신호 리스트
            existing_signals: 기존 DB의 신호 리스트

        Returns:
            {
                "duplicates": [
                    {
                        "new_signal_id": "...",
                        "matched_with": "...",
                        "similarity": 0.92,
                        "match_type": "exact" | "high" | "moderate"
                    }
                ],
                "unique": [...],
                "statistics": {...}
            }
        """
        duplicates = []
        unique = []
        exact_matches = 0
        high_similarity_matches = 0

        # 기존 신호 인덱싱
        existing_texts = {}
        existing_signatures = {}
        for sig in existing_signals:
            sig_id = sig.get("id", sig.get("signal_id", ""))
            text = self.extract_signal_text(sig)
            existing_texts[sig_id] = text
            existing_signatures[self.compute_signature(text)] = sig_id

        for new_sig in new_signals:
            new_id = new_sig.get("id", new_sig.get("raw_id", f"NEW-{len(duplicates) + len(unique)}"))
            new_text = self.extract_signal_text(new_sig)
            new_signature = self.compute_signature(new_text)
            # 다양한 날짜 형식 지원
            source = new_sig.get("source", {})
            if isinstance(source, dict):
                new_date = source.get("published_date", "")
            else:
                new_date = new_sig.get("published_date", "")

            is_duplicate = False
            matched_id = None
            max_similarity = 0.0
            match_type = None

            # 1. 시그니처 정확 매칭 (가장 빠름)
            if new_signature in existing_signatures:
                is_duplicate = True
                matched_id = existing_signatures[new_signature]
                max_similarity = 1.0
                match_type = "exact"
                exact_matches += 1
            else:
                # 2. 유사도 기반 매칭
                for exist_id, exist_text in existing_texts.items():
                    # 시간 윈도우 체크
                    exist_sig = next(
                        (s for s in existing_signals if s.get("id", s.get("signal_id", "")) == exist_id), {}
                    )
                    # 다양한 날짜 형식 지원
                    exist_source = exist_sig.get("source", {})
                    if isinstance(exist_source, dict):
                        exist_date = exist_source.get("published_date", "")
                    else:
                        exist_date = exist_sig.get("published_date", "")

                    if not self.is_within_time_window(new_date, exist_date):
                        continue

                    similarity = self.compute_similarity(new_text, exist_text)

                    if similarity > max_similarity:
                        max_similarity = similarity

                    if similarity >= self.similarity_threshold:
                        is_duplicate = True
                        matched_id = exist_id
                        match_type = "high" if similarity >= 0.95 else "moderate"
                        high_similarity_matches += 1
                        break

            if is_duplicate:
                duplicates.append(
                    {
                        "new_signal_id": new_id,
                        "new_title": new_sig.get("title", ""),
                        "matched_with": matched_id,
                        "similarity": round(max_similarity, 3),
                        "match_type": match_type,
                    }
                )
            else:
                unique.append(new_sig)

        return {
            "duplicates": duplicates,
            "unique": unique,
            "statistics": {
                "total_new_signals": len(new_signals),
                "total_existing_signals": len(existing_signals),
                "duplicates_found": len(duplicates),
                "unique_signals": len(unique),
                "exact_matches": exact_matches,
                "high_similarity_matches": high_similarity_matches,
                "duplicate_rate": round(len(duplicates) / len(new_signals) * 100, 1) if new_signals else 0,
            },
        }

    def batch_similarity_matrix(self, signals: list[dict], top_n: int = 5) -> dict[str, Any]:
        """
        신호 간 유사도 매트릭스 계산 (배치)

        Args:
            signals: 신호 리스트
            top_n: 각 신호당 상위 N개 유사 신호

        Returns:
            {
                "matrix": {
                    "SIG-001": [
                        {"signal_id": "SIG-002", "similarity": 0.75},
                        ...
                    ]
                },
                "clusters": [...],
                "statistics": {...}
            }
        """
        n = len(signals)
        if n < 2:
            return {"matrix": {}, "clusters": [], "statistics": {"total_pairs": 0}}

        # 텍스트 추출
        texts = {}
        for sig in signals:
            sig_id = sig.get("id", sig.get("signal_id", ""))
            texts[sig_id] = self.extract_signal_text(sig)

        # 유사도 계산
        matrix = {}
        high_similarity_pairs = []

        sig_ids = list(texts.keys())
        total_pairs = 0

        for i, id1 in enumerate(sig_ids):
            similarities = []
            for j, id2 in enumerate(sig_ids):
                if i >= j:  # 자기 자신 및 중복 쌍 제외
                    continue

                sim = self.compute_similarity(texts[id1], texts[id2])
                total_pairs += 1

                if sim >= 0.5:  # 50% 이상만 기록
                    similarities.append({"signal_id": id2, "similarity": round(sim, 3)})

                if sim >= self.similarity_threshold:
                    high_similarity_pairs.append({"signal_1": id1, "signal_2": id2, "similarity": round(sim, 3)})

            # 상위 N개만 유지
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            matrix[id1] = similarities[:top_n]

        # 클러스터링 (간단한 연결 기반)
        clusters = self._find_clusters(high_similarity_pairs, sig_ids)

        return {
            "matrix": matrix,
            "high_similarity_pairs": high_similarity_pairs,
            "clusters": clusters,
            "statistics": {
                "total_signals": n,
                "total_pairs_checked": total_pairs,
                "high_similarity_count": len(high_similarity_pairs),
                "cluster_count": len(clusters),
            },
        }

    def _find_clusters(self, pairs: list[dict], all_ids: list[str]) -> list[list[str]]:
        """유사 신호 클러스터 탐지 (Union-Find)"""
        parent = {id_: id_ for id_ in all_ids}

        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py

        for pair in pairs:
            union(pair["signal_1"], pair["signal_2"])

        # 클러스터 수집
        clusters_dict = {}
        for id_ in all_ids:
            root = find(id_)
            if root not in clusters_dict:
                clusters_dict[root] = []
            clusters_dict[root].append(id_)

        # 2개 이상인 클러스터만 반환
        return [members for members in clusters_dict.values() if len(members) > 1]

    def generate_dedup_index(self, signals: list[dict]) -> dict[str, Any]:
        """
        중복 체크용 인덱스 생성 (캐싱용)

        Args:
            signals: 기존 신호 리스트

        Returns:
            {
                "signatures": {"hash": "signal_id", ...},
                "titles_normalized": {"normalized_title": "signal_id", ...},
                "created": "2026-01-12T00:00:00Z",
                "total_indexed": N
            }
        """
        signatures = {}
        titles = {}

        for sig in signals:
            sig_id = sig.get("id", sig.get("signal_id", ""))
            text = self.extract_signal_text(sig)
            signature = self.compute_signature(text)
            signatures[signature] = sig_id

            # 정규화된 타이틀
            title = sig.get("title", "")
            if title:
                normalized_title = " ".join(self.tokenize(title))
                titles[normalized_title] = sig_id

        return {
            "signatures": signatures,
            "titles_normalized": titles,
            "created": datetime.now().isoformat() + "Z",
            "total_indexed": len(signals),
        }

    def quick_dedup_check(self, new_signal: dict, index: dict) -> dict | None:
        """
        인덱스를 이용한 빠른 중복 체크

        Args:
            new_signal: 새 신호
            index: generate_dedup_index()로 생성된 인덱스

        Returns:
            중복인 경우: {"is_duplicate": True, "matched_with": "...", ...}
            고유한 경우: None
        """
        text = self.extract_signal_text(new_signal)
        signature = self.compute_signature(text)

        # 시그니처 매칭
        if signature in index.get("signatures", {}):
            return {
                "is_duplicate": True,
                "matched_with": index["signatures"][signature],
                "match_type": "signature_exact",
            }

        # 타이틀 매칭
        title = new_signal.get("title", "")
        if title:
            normalized_title = " ".join(self.tokenize(title))
            if normalized_title in index.get("titles_normalized", {}):
                return {
                    "is_duplicate": True,
                    "matched_with": index["titles_normalized"][normalized_title],
                    "match_type": "title_exact",
                }

        return None


def main():
    """CLI 실행 예제"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python dedup_processor.py <new_signals_json> [existing_signals_json]")
        print("       python dedup_processor.py --test")
        sys.exit(1)

    if sys.argv[1] == "--test":
        processor = DedupProcessor()

        # 테스트 데이터
        existing = [
            {
                "id": "SIG-2026-0111-001",
                "title": "OpenAI, GPT-5 발표 임박",
                "description": "OpenAI가 차세대 AI 모델 GPT-5를 곧 발표할 예정이다.",
                "source": {"published_date": "2026-01-11"},
            },
            {
                "id": "SIG-2026-0110-001",
                "title": "테슬라 자율주행 Level 4 인증",
                "description": "테슬라가 미국에서 자율주행 Level 4 인증을 획득했다.",
                "source": {"published_date": "2026-01-10"},
            },
        ]

        new = [
            {
                "raw_id": "RAW-2026-0112-001",
                "title": "OpenAI GPT-5 발표 예정",  # 유사
                "description": "OpenAI가 GPT-5 모델을 조만간 발표할 것으로 알려졌다.",
                "source": {"published_date": "2026-01-12"},
            },
            {
                "raw_id": "RAW-2026-0112-002",
                "title": "삼성전자 AI 칩 양산 시작",  # 고유
                "description": "삼성전자가 AI 전용 칩의 대량 생산을 시작했다.",
                "source": {"published_date": "2026-01-12"},
            },
        ]

        result = processor.find_duplicates(new, existing)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        with open(sys.argv[1], encoding="utf-8") as f:
            new_data = json.load(f)

        # 다양한 키 지원: signals, items, new_signals
        new_signals = (
            new_data.get("signals")
            or new_data.get("items")
            or new_data.get("new_signals")
            or (new_data if isinstance(new_data, list) else [new_data])
        )

        existing_signals = []
        if len(sys.argv) > 2:
            with open(sys.argv[2], encoding="utf-8") as f:
                exist_data = json.load(f)
            # 다양한 키 지원
            existing_signals = (
                exist_data.get("signals")
                or exist_data.get("items")
                or (exist_data if isinstance(exist_data, list) else [exist_data])
            )

        processor = DedupProcessor()
        result = processor.find_duplicates(new_signals, existing_signals)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
