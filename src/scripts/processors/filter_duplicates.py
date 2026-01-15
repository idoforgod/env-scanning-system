#!/usr/bin/env python3
"""
중복 필터링 스크립트
2026-01-11 스캔 신호 vs 기존 DB 비교
"""

import difflib
import json
import os
from collections import defaultdict
from datetime import datetime


def calculate_similarity(text1, text2):
    """두 텍스트 유사도 계산 (0-1)"""
    if not text1 or not text2:
        return 0.0
    text1 = text1.lower().strip()
    text2 = text2.lower().strip()
    # SequenceMatcher 사용
    matcher = difflib.SequenceMatcher(None, text1, text2)
    return matcher.ratio()


def extract_entities(keywords, actors_list):
    """신호에서 엔티티 추출"""
    entities = set()
    if isinstance(keywords, list):
        entities.update([k.lower() for k in keywords])
    return entities


def calculate_entity_overlap(entities1, entities2):
    """엔티티 겹침 비율 계산"""
    if not entities1 or not entities2:
        return 0.0
    overlap = len(entities1 & entities2)
    total = len(entities1 | entities2)
    return overlap / total if total > 0 else 0.0


def check_duplicate(raw_signal, existing_signals, dedup_index, archive_actors):
    """신호가 중복인지 판정"""
    raw_signal["id"]
    raw_url = raw_signal.get("source_url", "")
    raw_title = raw_signal.get("title", "")
    raw_keywords = raw_signal.get("keywords", [])
    raw_summary = raw_signal.get("summary", "")

    raw_entities = extract_entities(raw_keywords, archive_actors)

    # 1. URL 정확 일치 확인
    if raw_url and raw_url in dedup_index["urls"]:
        # URL이 어느 신호와 일치하는지 찾기
        for sig_id, sig_data in existing_signals.items():
            if sig_data.get("url") == raw_url:
                return True, "exact_url", sig_id

    # 2. 제목 유사도 확인 (>=85%)
    for sig_id, sig_data in existing_signals.items():
        existing_title = sig_data.get("title", "")
        title_sim = calculate_similarity(raw_title, existing_title)

        if title_sim >= 0.85:
            return True, "similar_title", sig_id

    # 3. 엔티티 겹침 확인 (>=70%)
    for sig_id, sig_data in existing_signals.items():
        existing_keywords = sig_data.get("keywords", [])
        existing_entities = extract_entities(existing_keywords, archive_actors)

        entity_overlap = calculate_entity_overlap(raw_entities, existing_entities)

        if entity_overlap >= 0.70:
            # 엔티티 겹침이 높으면 내용 유사도도 확인
            existing_summary = sig_data.get("summary", "")
            content_sim = calculate_similarity(raw_summary, existing_summary)

            if content_sim >= 0.85:
                return True, "similar_content", sig_id

    # 4. 내용 유사도 직접 확인 (>=85%)
    for sig_id, sig_data in existing_signals.items():
        existing_summary = sig_data.get("summary", "")
        content_sim = calculate_similarity(raw_summary, existing_summary)

        if content_sim >= 0.85:
            return True, "similar_content", sig_id

    return False, None, None


def main():
    # 입력 파일 로드
    with open(
        "/Users/cys/Desktop/ENVscanning-system-main/env-scanning/raw/scanned-signals-2026-01-11.json", encoding="utf-8"
    ) as f:
        scanned_data = json.load(f)

    with open("/Users/cys/Desktop/ENVscanning-system-main/env-scanning/raw/archive-index.json", encoding="utf-8") as f:
        archive_data = json.load(f)

    scanned_signals = scanned_data["signals"]
    existing_signals = archive_data["signal_index"]
    dedup_index = archive_data["dedup_index"]
    archive_actors = dedup_index.get("actors", [])

    # 결과 저장용
    new_signals = []
    updates = []
    removed = []

    removal_stats = defaultdict(list)

    # 각 신호 검사
    for signal in scanned_signals:
        is_dup, reason, related_sig_id = check_duplicate(signal, existing_signals, dedup_index, archive_actors)

        if is_dup:
            removed.append({"signal_id": signal["id"], "reason": reason, "duplicate_of": related_sig_id})
            removal_stats[reason].append({"id": signal["id"], "title": signal["title"], "related": related_sig_id})
        else:
            new_signals.append(signal)

    # 결과 구성
    result = {
        "filter_date": "2026-01-11",
        "original_count": len(scanned_signals),
        "filtered_count": len(new_signals),
        "removed_count": len(removed),
        "signals": new_signals,
        "removed": removed,
    }

    # 디렉토리 생성
    filtered_dir = "/Users/cys/Desktop/ENVscanning-system-main/env-scanning/filtered"
    logs_dir = "/Users/cys/Desktop/ENVscanning-system-main/env-scanning/logs"
    os.makedirs(filtered_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    # 결과 저장
    output_path = os.path.join(filtered_dir, "filtered-signals-2026-01-11.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 로그 작성
    log_path = os.path.join(logs_dir, "duplicates-removed-2026-01-11.log")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"[2026-01-11 {datetime.now().strftime('%H:%M:%S')}] Deduplication Started\n")
        f.write(f"[2026-01-11 {datetime.now().strftime('%H:%M:%S')}] Total items to check: {len(scanned_signals)}\n\n")

        if removal_stats["exact_url"]:
            f.write("REMOVED - exact_url:\n")
            for item in removal_stats["exact_url"]:
                f.write(f'  - {item["id"]}: "{item["title"]}" (matches {item["related"]})\n')
            f.write("\n")

        if removal_stats["similar_title"]:
            f.write("REMOVED - similar_title (>=85%):\n")
            for item in removal_stats["similar_title"]:
                f.write(f'  - {item["id"]}: "{item["title"]}" (similar to {item["related"]})\n')
            f.write("\n")

        if removal_stats["similar_content"]:
            f.write("REMOVED - similar_content (>=85%):\n")
            for item in removal_stats["similar_content"]:
                f.write(f'  - {item["id"]}: "{item["title"]}" (similar to {item["related"]})\n')
            f.write("\n")

        f.write(f"[2026-01-11 {datetime.now().strftime('%H:%M:%S')}] Deduplication Completed\n")
        f.write(f"  - Removed: {len(removed)}\n")
        f.write(f"  - New: {len(new_signals)}\n")
        f.write(f"  - Updates: {len(updates)}\n")

    # 콘솔 출력
    print("\n=== 중복 필터링 완료 ===")
    print(f"원본 신호: {len(scanned_signals)}")
    print(f"필터링 후: {len(new_signals)}")
    print(f"제거된 중복: {len(removed)}")
    print("\n제거 이유별:")
    for reason, items in removal_stats.items():
        print(f"  {reason}: {len(items)}개")

    print("\n결과 저장:")
    print(f"  - 필터링된 신호: {output_path}")
    print(f"  - 로그: {log_path}")


if __name__ == "__main__":
    main()
