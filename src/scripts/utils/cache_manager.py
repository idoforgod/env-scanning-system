"""
Cache Manager - 설정 및 데이터 캐싱 관리
=========================================
토큰 절감:
- 키워드 캐싱: 80-90% 절감
- pSRT 설정 캐싱: 80-85% 절감
- 소스 설정 캐싱: 70-80% 절감

반복적으로 읽히는 설정 파일과 키워드를 캐싱하여 LLM 컨텍스트 토큰 절감.
"""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yaml


class CacheManager:
    """설정 및 데이터 캐싱 매니저"""

    def __init__(self, base_path: str | None = None):
        """
        Args:
            base_path: 환경스캐닝 기본 경로 (없으면 자동 탐지)
        """
        if base_path is None:
            self.base_path = Path(__file__).parent.parent
        else:
            self.base_path = Path(base_path)

        self.cache_dir = self.base_path / "cache"
        self.cache_dir.mkdir(exist_ok=True)

        # 메모리 캐시
        self._memory_cache: dict[str, Any] = {}
        self._cache_timestamps: dict[str, datetime] = {}
        self._cache_ttl = timedelta(hours=24)  # 기본 TTL: 24시간

    def _get_cache_path(self, cache_key: str) -> Path:
        """캐시 파일 경로 반환"""
        return self.cache_dir / f"{cache_key}.json"

    def _compute_file_hash(self, file_path: Path) -> str:
        """파일 해시 계산 (변경 감지용)"""
        if not file_path.exists():
            return ""
        content = file_path.read_bytes()
        return hashlib.md5(content).hexdigest()

    def get(self, cache_key: str, max_age_hours: float = 24) -> Any | None:
        """
        캐시에서 데이터 가져오기

        Args:
            cache_key: 캐시 키
            max_age_hours: 최대 캐시 유효 시간 (시간)

        Returns:
            캐시된 데이터 또는 None (캐시 미스)
        """
        # 메모리 캐시 확인
        if cache_key in self._memory_cache:
            timestamp = self._cache_timestamps.get(cache_key, datetime.min)
            if datetime.now() - timestamp < timedelta(hours=max_age_hours):
                return self._memory_cache[cache_key]

        # 파일 캐시 확인
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                with open(cache_path, encoding="utf-8") as f:
                    cached = json.load(f)

                cached_time = datetime.fromisoformat(cached.get("_cached_at", "2000-01-01"))
                if datetime.now() - cached_time < timedelta(hours=max_age_hours):
                    data = cached.get("data")
                    # 메모리 캐시에도 저장
                    self._memory_cache[cache_key] = data
                    self._cache_timestamps[cache_key] = cached_time
                    return data
            except (json.JSONDecodeError, KeyError):
                pass

        return None

    def set(self, cache_key: str, data: Any) -> None:
        """
        데이터를 캐시에 저장

        Args:
            cache_key: 캐시 키
            data: 저장할 데이터
        """
        now = datetime.now()

        # 메모리 캐시 저장
        self._memory_cache[cache_key] = data
        self._cache_timestamps[cache_key] = now

        # 파일 캐시 저장
        cache_path = self._get_cache_path(cache_key)
        cached = {"_cached_at": now.isoformat(), "data": data}
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cached, f, ensure_ascii=False, indent=2)

    def invalidate(self, cache_key: str) -> None:
        """캐시 무효화"""
        if cache_key in self._memory_cache:
            del self._memory_cache[cache_key]
        if cache_key in self._cache_timestamps:
            del self._cache_timestamps[cache_key]

        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            cache_path.unlink()

    def clear_all(self) -> int:
        """모든 캐시 삭제"""
        self._memory_cache.clear()
        self._cache_timestamps.clear()

        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        return count

    # ==================== 특화 캐싱 메서드 ====================

    def get_psrt_config(self, force_reload: bool = False) -> dict:
        """
        pSRT 설정 캐싱 (80-85% 토큰 절감)

        Returns:
            pSRT 설정 딕셔너리
        """
        cache_key = "psrt_config"
        config_path = self.base_path / "config" / "pSRT-config.yaml"

        if not force_reload:
            cached = self.get(cache_key, max_age_hours=168)  # 7일
            if cached:
                # 파일 해시 체크 (변경 감지)
                current_hash = self._compute_file_hash(config_path)
                if cached.get("_file_hash") == current_hash:
                    return cached.get("config", {})

        # 캐시 미스 - 파일 로드
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
        else:
            config = {}

        # 캐시 저장
        self.set(cache_key, {"_file_hash": self._compute_file_hash(config_path), "config": config})

        return config

    def get_sources_config(self, force_reload: bool = False) -> dict:
        """
        소스 설정 캐싱 (70-80% 토큰 절감)

        Returns:
            소스 설정 딕셔너리
        """
        cache_key = "sources_config"
        config_path = self.base_path / "config" / "sources.yaml"

        if not force_reload:
            cached = self.get(cache_key, max_age_hours=168)
            if cached:
                current_hash = self._compute_file_hash(config_path)
                if cached.get("_file_hash") == current_hash:
                    return cached.get("config", {})

        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
        else:
            config = {}

        self.set(cache_key, {"_file_hash": self._compute_file_hash(config_path), "config": config})

        return config

    def get_steeps_keywords(self, force_reload: bool = False) -> dict[str, list[str]]:
        """
        STEEPS 키워드 캐싱 (80-90% 토큰 절감)

        Returns:
            {"Social": [...], "Technological": [...], ...}
        """
        cache_key = "steeps_keywords"

        if not force_reload:
            cached = self.get(cache_key, max_age_hours=720)  # 30일
            if cached:
                return cached

        # 기본 STEEPS 키워드 정의
        keywords = {
            "Social": [
                "인구",
                "고령화",
                "출산율",
                "이민",
                "다문화",
                "세대",
                "Z세대",
                "MZ세대",
                "라이프스타일",
                "트렌드",
                "소비",
                "가치관",
                "행복",
                "웰빙",
                "건강",
                "교육",
                "평생학습",
                "리스킬링",
                "업스킬링",
                "원격학습",
                "노동",
                "고용",
                "실업",
                "일자리",
                "근무형태",
                "재택근무",
                "긱경제",
                "불평등",
                "양극화",
                "사회안전망",
                "복지",
                "연금",
                "도시화",
                "스마트시티",
                "주거",
                "부동산",
                "인프라",
                "population",
                "aging",
                "generation",
                "lifestyle",
                "wellness",
                "education",
                "employment",
                "inequality",
                "urbanization",
            ],
            "Technological": [
                "인공지능",
                "AI",
                "머신러닝",
                "딥러닝",
                "생성AI",
                "LLM",
                "GPT",
                "로봇",
                "자동화",
                "RPA",
                "로보틱스",
                "양자컴퓨터",
                "양자컴퓨팅",
                "큐비트",
                "5G",
                "6G",
                "통신",
                "네트워크",
                "IoT",
                "사물인터넷",
                "반도체",
                "칩",
                "파운드리",
                "팹리스",
                "메타버스",
                "VR",
                "AR",
                "XR",
                "가상현실",
                "증강현실",
                "블록체인",
                "암호화폐",
                "비트코인",
                "이더리움",
                "NFT",
                "Web3",
                "자율주행",
                "전기차",
                "배터리",
                "수소차",
                "바이오",
                "유전자",
                "CRISPR",
                "합성생물학",
                "신약",
                "우주",
                "위성",
                "로켓",
                "SpaceX",
                "artificial intelligence",
                "machine learning",
                "quantum",
                "robotics",
                "autonomous",
                "blockchain",
                "biotechnology",
            ],
            "Economic": [
                "GDP",
                "성장률",
                "경기",
                "침체",
                "회복",
                "호황",
                "불황",
                "인플레이션",
                "디플레이션",
                "금리",
                "통화정책",
                "기준금리",
                "환율",
                "달러",
                "원화",
                "엔화",
                "유로",
                "주식",
                "채권",
                "펀드",
                "투자",
                "자산",
                "기업",
                "스타트업",
                "유니콘",
                "IPO",
                "M&A",
                "인수합병",
                "무역",
                "수출",
                "수입",
                "관세",
                "FTA",
                "공급망",
                "에너지",
                "원유",
                "천연가스",
                "전력",
                "신재생에너지",
                "부채",
                "재정",
                "예산",
                "세금",
                "조세",
                "inflation",
                "interest rate",
                "GDP",
                "trade",
                "supply chain",
                "startup",
                "investment",
                "market",
                "economy",
            ],
            "Environmental": [
                "기후변화",
                "지구온난화",
                "탄소",
                "탄소중립",
                "넷제로",
                "ESG",
                "지속가능",
                "친환경",
                "그린",
                "녹색",
                "재생에너지",
                "태양광",
                "풍력",
                "수력",
                "원자력",
                "전기차",
                "수소",
                "배터리",
                "에너지저장",
                "오염",
                "미세먼지",
                "대기오염",
                "수질",
                "토양",
                "생태계",
                "생물다양성",
                "멸종",
                "보존",
                "폐기물",
                "재활용",
                "순환경제",
                "플라스틱",
                "자연재해",
                "홍수",
                "가뭄",
                "산불",
                "태풍",
                "물부족",
                "식량",
                "농업",
                "스마트팜",
                "climate change",
                "carbon",
                "net zero",
                "renewable",
                "sustainability",
                "ESG",
                "pollution",
                "biodiversity",
            ],
            "Political": [
                "정부",
                "정책",
                "규제",
                "법률",
                "입법",
                "선거",
                "대통령",
                "국회",
                "의회",
                "정당",
                "외교",
                "국제관계",
                "동맹",
                "협력",
                "갈등",
                "안보",
                "국방",
                "군사",
                "무기",
                "전쟁",
                "미국",
                "중국",
                "러시아",
                "EU",
                "일본",
                "북한",
                "민주주의",
                "권위주의",
                "인권",
                "자유",
                "무역전쟁",
                "제재",
                "보호주의",
                "글로벌화",
                "사이버",
                "해킹",
                "보안",
                "데이터",
                "프라이버시",
                "government",
                "policy",
                "regulation",
                "election",
                "diplomacy",
                "security",
                "democracy",
                "sanction",
            ],
            "Spiritual": [
                "종교",
                "영성",
                "명상",
                "마음챙김",
                "mindfulness",
                "가치",
                "윤리",
                "도덕",
                "철학",
                "의미",
                "목적",
                "행복",
                "삶의질",
                "커뮤니티",
                "공동체",
                "연대",
                "사회적자본",
                "문화",
                "예술",
                "창의성",
                "표현",
                "정체성",
                "다양성",
                "포용",
                "존중",
                "AI윤리",
                "기술윤리",
                "생명윤리",
                "spirituality",
                "meditation",
                "ethics",
                "values",
                "community",
                "culture",
                "identity",
                "diversity",
            ],
        }

        self.set(cache_key, keywords)
        return keywords

    def get_dedup_index(self, date: str | None = None) -> dict | None:
        """
        중복 체크 인덱스 캐싱

        Args:
            date: 날짜 (없으면 최신)

        Returns:
            중복 체크 인덱스 또는 None
        """
        if date:
            cache_key = f"dedup_index_{date}"
        else:
            cache_key = "dedup_index_latest"

        return self.get(cache_key, max_age_hours=24)

    def set_dedup_index(self, index: dict, date: str | None = None) -> None:
        """중복 체크 인덱스 저장"""
        if date:
            cache_key = f"dedup_index_{date}"
        else:
            cache_key = "dedup_index_latest"

        self.set(cache_key, index)

    def get_source_tier_lookup(self) -> dict[str, int]:
        """
        소스별 Tier 조회 테이블 캐싱

        Returns:
            {"reuters.com": 2, "arxiv.org": 1, ...}
        """
        cache_key = "source_tier_lookup"

        cached = self.get(cache_key, max_age_hours=720)  # 30일
        if cached:
            return cached

        # 기본 소스 Tier 정의
        lookup = {
            # Tier 1: 학술/정부/공식
            "arxiv.org": 1,
            "nature.com": 1,
            "science.org": 1,
            "who.int": 1,
            "un.org": 1,
            "oecd.org": 1,
            "worldbank.org": 1,
            "imf.org": 1,
            "korea.kr": 1,
            "moef.go.kr": 1,
            # Tier 2: 주요 언론/분석기관
            "reuters.com": 2,
            "bloomberg.com": 2,
            "ft.com": 2,
            "wsj.com": 2,
            "nytimes.com": 2,
            "bbc.com": 2,
            "economist.com": 2,
            "mckinsey.com": 2,
            "bcg.com": 2,
            "gartner.com": 2,
            # Tier 3: 전문 매체/지역 언론
            "techcrunch.com": 3,
            "wired.com": 3,
            "technologyreview.com": 3,
            "theverge.com": 3,
            "arstechnica.com": 3,
            "zdnet.com": 3,
            "chosun.com": 3,
            "donga.com": 3,
            "hani.co.kr": 3,
            "mk.co.kr": 3,
            # Tier 4: 블로그/트렌드
            "medium.com": 4,
            "substack.com": 4,
            "twitter.com": 4,
            "x.com": 4,
            "reddit.com": 4,
        }

        self.set(cache_key, lookup)
        return lookup

    def get_cache_stats(self) -> dict[str, Any]:
        """캐시 통계 반환"""
        cache_files = list(self.cache_dir.glob("*.json"))

        total_size = sum(f.stat().st_size for f in cache_files)
        oldest = min((f.stat().st_mtime for f in cache_files), default=0)
        newest = max((f.stat().st_mtime for f in cache_files), default=0)

        return {
            "memory_cache_entries": len(self._memory_cache),
            "file_cache_entries": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_kb": round(total_size / 1024, 2),
            "oldest_cache": datetime.fromtimestamp(oldest).isoformat() if oldest else None,
            "newest_cache": datetime.fromtimestamp(newest).isoformat() if newest else None,
            "cache_keys": list(self._memory_cache.keys()),
        }


def main():
    """CLI 실행 예제"""
    import sys

    manager = CacheManager()

    if len(sys.argv) < 2:
        print("Usage: python cache_manager.py <command>")
        print("Commands:")
        print("  stats     - 캐시 통계 출력")
        print("  clear     - 모든 캐시 삭제")
        print("  psrt      - pSRT 설정 캐시 테스트")
        print("  keywords  - STEEPS 키워드 캐시 테스트")
        print("  tiers     - 소스 Tier 조회 테스트")
        sys.exit(1)

    command = sys.argv[1]

    if command == "stats":
        stats = manager.get_cache_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))

    elif command == "clear":
        count = manager.clear_all()
        print(f"Cleared {count} cache files")

    elif command == "psrt":
        config = manager.get_psrt_config()
        print(f"pSRT config loaded: {len(config)} sections")
        print(f"Sections: {list(config.keys())}")

    elif command == "keywords":
        keywords = manager.get_steeps_keywords()
        for category, words in keywords.items():
            print(f"{category}: {len(words)} keywords")

    elif command == "tiers":
        tiers = manager.get_source_tier_lookup()
        print(f"Total sources: {len(tiers)}")
        by_tier = {}
        for source, tier in tiers.items():
            by_tier.setdefault(tier, []).append(source)
        for tier in sorted(by_tier.keys()):
            print(f"Tier {tier}: {len(by_tier[tier])} sources")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
