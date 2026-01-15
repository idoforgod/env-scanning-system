#!/usr/bin/env python3
"""
신호 분석 및 중복 검사
"""

import difflib
import json

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

print("=== 신호 분석 ===")
print(f"스캔 신호: {len(scanned_signals)}")
print(f"기존 신호: {len(existing_signals)}")
print()


def similarity_ratio(a, b):
    """두 텍스트 유사도 계산"""
    a = str(a).lower()
    b = str(b).lower()
    return difflib.SequenceMatcher(None, a, b).ratio()


# URL 기반 중복 검사
url_duplicates = []
for signal in scanned_signals:
    url = signal.get("source_url", "")
    if url in dedup_urls:
        url_duplicates.append((signal["id"], signal["title"], url))

print(f"URL 일치: {len(url_duplicates)}")
for sig_id, title, url in url_duplicates:
    print(f"  - {sig_id}: {title[:50]}")
    # 매칭된 기존 신호 찾기
    for ex_id, ex_sig in existing_signals.items():
        if ex_sig.get("url") == url:
            print(f"    매칭: {ex_id}")
            break

print()

# 제목 기반 중복 검사 (>=85%)
title_duplicates = []
for signal in scanned_signals:
    for ex_id, ex_sig in existing_signals.items():
        sim = similarity_ratio(signal["title"], ex_sig["title"])
        if sim >= 0.85 and sim < 1.0:  # 완벽한 일치 제외
            title_duplicates.append((signal["id"], signal["title"], ex_id, ex_sig["title"], sim))

print(f"제목 유사도 (>=85%): {len(title_duplicates)}")
for raw_id, raw_title, _ex_id, ex_title, sim in title_duplicates[:5]:
    print(f"  - {raw_id} ({sim:.2%})")
    print(f"    신: {raw_title[:60]}")
    print(f"    기: {ex_title[:60]}")

print()

# 내용/키워드 기반 중복 검사
content_duplicates = []
for signal in scanned_signals:
    raw_keywords = {k.lower() for k in signal.get("keywords", [])}

    for ex_id, ex_sig in existing_signals.items():
        ex_keywords = {k.lower() for k in ex_sig.get("keywords", [])}

        if raw_keywords and ex_keywords:
            overlap = len(raw_keywords & ex_keywords)
            total = len(raw_keywords | ex_keywords)
            entity_overlap = overlap / total if total > 0 else 0

            # 엔티티 70% 이상 + 내용 85% 이상
            if entity_overlap >= 0.70:
                content_sim = similarity_ratio(signal.get("summary", ""), ex_sig.get("summary", ""))

                if content_sim >= 0.85:
                    content_duplicates.append((signal["id"], signal["title"], ex_id, entity_overlap, content_sim))

print(f"내용 유사도 (엔티티>=70% + 내용>=85%): {len(content_duplicates)}")
for raw_id, title, ex_id, entity_ov, content_sim in content_duplicates[:3]:
    print(f"  - {raw_id} -> {ex_id}")
    print(f"    엔티티: {entity_ov:.2%}, 내용: {content_sim:.2%}")
    print(f"    제목: {title[:60]}")

print()

# 신규 신호 식별
duplicates_set = set(url_duplicates) | {d[0] for d in title_duplicates} | {d[0] for d in content_duplicates}
new_signals = [
    s for s in scanned_signals if s["id"] not in [d[0] for d in url_duplicates + title_duplicates + content_duplicates]
]

print(f"신규 신호: {len(new_signals)}")
print(f"중복 제거됨: {len(url_duplicates) + len(title_duplicates) + len(content_duplicates)}")
