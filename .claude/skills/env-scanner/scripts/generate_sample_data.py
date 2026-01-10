#!/usr/bin/env python3
"""
Generate sample signal data for testing.
Usage: python scripts/generate_sample_data.py [--count N]
"""

import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path("env-scanning")

SAMPLE_SIGNALS = [
    {
        "category": "Technological",
        "title": "OpenAI, GPT-5 개발 완료 임박 발표",
        "description": "OpenAI가 차세대 언어모델 GPT-5의 개발이 최종 단계에 접어들었다고 발표. 멀티모달 능력과 추론 능력이 대폭 향상될 것으로 예상.",
        "source_type": "news",
        "significance": 5,
        "tags": ["AI", "LLM", "OpenAI"],
    },
    {
        "category": "Political",
        "title": "EU, AI 에이전트 책임 규정 초안 발표",
        "description": "유럽연합이 자율적으로 행동하는 AI 에이전트에 대한 법적 책임 프레임워크 초안을 발표.",
        "source_type": "policy",
        "significance": 5,
        "tags": ["AI 규제", "EU", "법률"],
    },
    {
        "category": "Economic",
        "title": "글로벌 반도체 공급망 재편 가속화",
        "description": "미중 기술 갈등 심화로 주요 반도체 기업들의 생산기지 다변화 움직임 본격화.",
        "source_type": "news",
        "significance": 4,
        "tags": ["반도체", "공급망", "지정학"],
    },
    {
        "category": "Environmental",
        "title": "탄소포집기술 상용화 돌파구 마련",
        "description": "MIT 연구팀이 기존 대비 10배 효율적인 탄소포집 기술 개발에 성공.",
        "source_type": "academic",
        "significance": 4,
        "tags": ["탄소중립", "기후기술", "연구"],
    },
    {
        "category": "Social",
        "title": "Z세대 '디지털 디톡스' 트렌드 확산",
        "description": "젊은 세대를 중심으로 의도적인 디지털 기기 사용 절제 움직임이 전 세계적으로 확산.",
        "source_type": "report",
        "significance": 3,
        "tags": ["MZ세대", "라이프스타일", "디지털"],
    },
    {
        "category": "Technological",
        "title": "양자컴퓨터 오류 수정 획기적 진전",
        "description": "Google 양자AI팀이 양자 오류 수정률 99.9% 달성, 실용화 앞당겨.",
        "source_type": "news",
        "significance": 5,
        "tags": ["양자컴퓨팅", "Google", "기술혁신"],
    },
    {
        "category": "Economic",
        "title": "글로벌 스타트업 투자 회복세 전환",
        "description": "2년간의 침체 끝에 AI 스타트업 중심으로 벤처투자 회복 신호.",
        "source_type": "news",
        "significance": 3,
        "tags": ["스타트업", "투자", "AI"],
    },
    {
        "category": "Political",
        "title": "미국, 첨단기술 수출통제 확대 검토",
        "description": "바이든 행정부가 AI 칩 수출통제를 동맹국까지 확대하는 방안 검토.",
        "source_type": "policy",
        "significance": 4,
        "tags": ["수출통제", "미국", "반도체"],
    },
    {
        "category": "Environmental",
        "title": "북극 해빙 속도 예측치 초과",
        "description": "2025년 북극 해빙이 과학자들의 최악 시나리오보다 빠르게 진행 중.",
        "source_type": "academic",
        "significance": 4,
        "tags": ["기후변화", "북극", "환경"],
    },
    {
        "category": "Social",
        "title": "원격근무 영구화 기업 급증",
        "description": "Fortune 500 기업 중 40%가 하이브리드/원격근무를 영구 정책으로 채택.",
        "source_type": "report",
        "significance": 3,
        "tags": ["원격근무", "고용", "기업문화"],
    },
]


def generate_signal_id(date: datetime, seq: int) -> str:
    return f"SIG-{date.strftime('%Y')}-{date.strftime('%m%d')}-{seq:03d}"


def generate_raw_id(date: datetime, seq: int) -> str:
    return f"RAW-{date.strftime('%Y')}-{date.strftime('%m%d')}-{seq:03d}"


def generate_signals(count: int) -> list:
    signals = []
    today = datetime.now()

    for i in range(count):
        sample = random.choice(SAMPLE_SIGNALS)
        date = today - timedelta(days=random.randint(0, 6))

        signal = {
            "id": generate_signal_id(date, i + 1),
            "category": {"primary": sample["category"], "secondary": []},
            "title": f"{sample['title']} (샘플 {i + 1})",
            "description": sample["description"],
            "source": {
                "name": f"Sample Source {i + 1}",
                "url": f"https://example.com/article/{i + 1}",
                "type": sample["source_type"],
                "published_date": date.strftime("%Y-%m-%d"),
            },
            "leading_indicator": "미래 변화의 선행 지표",
            "significance": sample["significance"],
            "significance_reason": "샘플 데이터 - 테스트용",
            "potential_impact": {
                "short_term": "단기 영향 설명",
                "mid_term": "중기 영향 설명",
                "long_term": "장기 영향 설명",
            },
            "actors": [{"name": "Actor A", "type": "company", "role": "주요 행위자"}],
            "status": random.choice(["emerging", "developing"]),
            "first_detected": date.strftime("%Y-%m-%d"),
            "last_updated": today.strftime("%Y-%m-%d"),
            "confidence": round(random.uniform(0.6, 0.95), 2),
            "tags": sample["tags"],
            "priority_score": round(random.uniform(5.0, 9.0), 1),
            "history": [],
        }
        signals.append(signal)

    return signals


def main():
    parser = argparse.ArgumentParser(description="Generate sample signal data")
    parser.add_argument("--count", type=int, default=20, help="Number of signals to generate")
    args = parser.parse_args()

    signals = generate_signals(args.count)

    # Update database
    db_path = BASE_DIR / "signals" / "database.json"
    if db_path.exists():
        with open(db_path, encoding="utf-8") as f:
            db = json.load(f)
    else:
        db = {"signals": [], "metadata": {}, "statistics": {}}

    db["signals"] = signals
    db["metadata"]["last_updated"] = datetime.now().isoformat()
    db["metadata"]["total_signals"] = len(signals)

    # Update statistics
    stats = {"by_status": {}, "by_category": {}}
    for s in signals:
        status = s["status"]
        cat = s["category"]["primary"]
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
    db["statistics"] = stats

    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"✓ Generated {len(signals)} sample signals")
    print(f"✓ Updated {db_path}")
    print("\nCategory distribution:")
    for cat, count in stats["by_category"].items():
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
