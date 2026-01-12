#!/usr/bin/env python3
"""
중복 필터링 최종 스크립트
"""

import difflib
import json
import os
from datetime import datetime


def similarity_ratio(text1, text2):
    """텍스트 유사도 계산"""
    if not text1 or not text2:
        return 0.0
    text1 = str(text1).lower()
    text2 = str(text2).lower()
    matcher = difflib.SequenceMatcher(None, text1, text2)
    return matcher.ratio()


def entity_overlap_ratio(keywords1, keywords2):
    """키워드 겹침 비율"""
    if not keywords1 or not keywords2:
        return 0.0
    set1 = set(str(k).lower() for k in keywords1)
    set2 = set(str(k).lower() for k in keywords2)
    if not set1 or not set2:
        return 0.0
    overlap = len(set1 & set2)
    union = len(set1 | set2)
    return overlap / union if union > 0 else 0.0


# 데이터 로드
with open(
    "/Users/cys/Desktop/ENVscanning-system-main/env-scanning/raw/scanned-signals-2026-01-11.json", encoding="utf-8"
) as f:
    scanned_data = json.load(f)

with open("/Users/cys/Desktop/ENVscanning-system-main/env-scanning/raw/archive-index.json", encoding="utf-8") as f:
    archive_data = json.load(f)

scanned_signals = scanned_data["signals"]
existing_signals = archive_data["signal_index"]
dedup_urls = set(archive_data["dedup_index"]["urls"])

# 중복 검사
removed_list = []
new_signals_list = []

for raw_signal in scanned_signals:
    is_duplicate = False
    duplicate_reason = None
    duplicate_of = None

    raw_id = raw_signal["id"]
    raw_url = raw_signal.get("source_url", "")
    raw_title = raw_signal.get("title", "")
    raw_keywords = raw_signal.get("keywords", [])
    raw_summary = raw_signal.get("summary", "")

    # 1. URL 정확 일치 검사
    if raw_url and raw_url in dedup_urls:
        for ex_id, ex_sig in existing_signals.items():
            if ex_sig.get("url") == raw_url:
                is_duplicate = True
                duplicate_reason = "exact_url"
                duplicate_of = ex_id
                break

    # 2. 제목 유사도 검사 (85% 이상)
    if not is_duplicate:
        for ex_id, ex_sig in existing_signals.items():
            title_sim = similarity_ratio(raw_title, ex_sig.get("title", ""))
            if title_sim >= 0.85:
                is_duplicate = True
                duplicate_reason = "similar_title"
                duplicate_of = ex_id
                break

    # 3. 내용 유사도 검사 (엔티티 70% + 내용 85%)
    if not is_duplicate:
        for ex_id, ex_sig in existing_signals.items():
            entity_ov = entity_overlap_ratio(raw_keywords, ex_sig.get("keywords", []))

            if entity_ov >= 0.70:
                content_sim = similarity_ratio(raw_summary, ex_sig.get("summary", ""))
                if content_sim >= 0.85:
                    is_duplicate = True
                    duplicate_reason = "similar_content"
                    duplicate_of = ex_id
                    break

    # 4. 순수 내용 유사도 검사 (85% 이상)
    if not is_duplicate:
        for ex_id, ex_sig in existing_signals.items():
            content_sim = similarity_ratio(raw_summary, ex_sig.get("summary", ""))
            if content_sim >= 0.85:
                is_duplicate = True
                duplicate_reason = "similar_content"
                duplicate_of = ex_id
                break

    if is_duplicate:
        removed_list.append({"signal_id": raw_id, "reason": duplicate_reason, "duplicate_of": duplicate_of})
    else:
        new_signals_list.append(raw_signal)

# 결과 JSON 생성
result = {
    "filter_date": "2026-01-11",
    "original_count": len(scanned_signals),
    "filtered_count": len(new_signals_list),
    "removed_count": len(removed_list),
    "signals": new_signals_list,
    "removed": removed_list,
}

# 디렉토리 생성 및 파일 저장
os.makedirs("/Users/cys/Desktop/ENVscanning-system-main/env-scanning/filtered", exist_ok=True)
os.makedirs("/Users/cys/Desktop/ENVscanning-system-main/env-scanning/logs", exist_ok=True)

output_path = "/Users/cys/Desktop/ENVscanning-system-main/env-scanning/filtered/filtered-signals-2026-01-11.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# 로그 파일 작성
log_path = "/Users/cys/Desktop/ENVscanning-system-main/env-scanning/logs/duplicates-removed-2026-01-11.log"
with open(log_path, "w", encoding="utf-8") as f:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f.write(f"[{timestamp}] Deduplication Started\n")
    f.write(f"[{timestamp}] Total items to check: {len(scanned_signals)}\n\n")

    # 이유별 제거 신호 분류
    by_reason = {}
    for item in removed_list:
        reason = item["reason"]
        if reason not in by_reason:
            by_reason[reason] = []
        by_reason[reason].append(item)

    # 이유별 로그 작성
    if "exact_url" in by_reason:
        f.write("REMOVED - exact_url:\n")
        for item in by_reason["exact_url"]:
            # 신호 정보 찾기
            for sig in scanned_signals:
                if sig["id"] == item["signal_id"]:
                    f.write(f'  - {item["signal_id"]}: "{sig["title"]}" (matches {item["duplicate_of"]})\n')
                    break
        f.write("\n")

    if "similar_title" in by_reason:
        f.write("REMOVED - similar_title (>=85%):\n")
        for item in by_reason["similar_title"]:
            for sig in scanned_signals:
                if sig["id"] == item["signal_id"]:
                    f.write(f'  - {item["signal_id"]}: "{sig["title"]}" (similar to {item["duplicate_of"]})\n')
                    break
        f.write("\n")

    if "similar_content" in by_reason:
        f.write("REMOVED - similar_content (>=85%):\n")
        for item in by_reason["similar_content"]:
            for sig in scanned_signals:
                if sig["id"] == item["signal_id"]:
                    f.write(f'  - {item["signal_id"]}: "{sig["title"]}" (similar to {item["duplicate_of"]})\n')
                    break
        f.write("\n")

    timestamp_end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f.write(f"[{timestamp_end}] Deduplication Completed\n")
    f.write(f"  - Removed: {len(removed_list)}\n")
    f.write(f"  - New: {len(new_signals_list)}\n")
    f.write("  - Updates: 0\n")

print("=== 중복 필터링 완료 ===")
print(f"원본 신호: {len(scanned_signals)}")
print(f"필터링 후: {len(new_signals_list)}")
print(f"제거된 중복: {len(removed_list)}")
print()
print(f"결과 파일: {output_path}")
print(f"로그 파일: {log_path}")
