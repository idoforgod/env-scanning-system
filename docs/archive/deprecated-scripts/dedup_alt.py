#!/usr/bin/env python3

import json
import re
from datetime import datetime
from difflib import SequenceMatcher
from urllib.parse import urlparse


def normalize_url(url):
    """URL 정규화"""
    if not url:
        return ""
    # 프로토콜 제거, 쿼리 파라미터 제거, 슬래시 정규화
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    path = parsed.path.rstrip("/")
    return f"{domain}{path}".lower()


def calculate_similarity(text1, text2):
    """문자열 유사도 계산"""
    if not text1 or not text2:
        return 0
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def extract_entities(signal):
    """신호에서 엔티티 추출"""
    entities = set()

    # key_entities 추출
    if signal.get("key_entities"):
        entities.update([str(e).lower() for e in signal["key_entities"]])

    # title에서 주요 단어 추출 (10자 이상)
    if "title" in signal:
        title = signal["title"].lower()
        words = re.findall(r"\b\w+\b", title)
        for word in words:
            if len(word) > 3:
                entities.add(word)

    return entities


def load_json(file_path):
    """JSON 파일 로드"""
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}


def dedup_filtering(raw_signals, database, dedup_index):
    """
    중복 필터링 수행

    기준:
    1. URL 정확 일치 → 중복
    2. 제목 유사도 85% 이상 → 중복
    3. 핵심 엔티티 80% 이상 겹침 + 동일 주제 → 중복 검토
    """
    results = {
        "total_scanned": len(raw_signals),
        "new_signals": [],
        "duplicates": {"exact_url": [], "similar_title": [], "similar_content": [], "entity_overlap": []},
        "updates": [],
        "filter_date": datetime.now().strftime("%Y-%m-%d"),
        "filter_time": datetime.now().strftime("%H:%M:%S"),
    }

    # 기존 데이터베이스 신호에서 URL과 제목 수집
    existing_urls = {}
    existing_titles = {}
    existing_entities = {}

    for sig in database.get("signals", []):
        sig_id = sig.get("id", "")
        if "url" in sig:
            url_norm = normalize_url(sig.get("url", ""))
            if url_norm:
                existing_urls[url_norm] = sig_id

        if "title" in sig:
            title = sig.get("title", "")
            existing_titles[title] = sig_id

        # 엔티티 저장
        entities = extract_entities(sig)
        existing_entities[sig_id] = entities

    # dedup_index에서 추가 URL 수집
    for url in dedup_index.get("dedup_index", {}).get("url_dedup_keys", []):
        url_norm = normalize_url(url)
        if url_norm:
            existing_urls[url_norm] = "ARCHIVE"

    # 각 raw signal 검사
    for raw_signal in raw_signals:
        raw_id = raw_signal.get("raw_id", "")
        title = raw_signal.get("title", "")
        url = raw_signal.get("url", "")

        is_duplicate = False
        duplicate_reason = None
        matched_signal = None

        # 1. URL 정확 일치 검사
        url_norm = normalize_url(url)
        if url_norm and url_norm in existing_urls:
            is_duplicate = True
            duplicate_reason = "exact_url"
            matched_signal = existing_urls[url_norm]
            results["duplicates"]["exact_url"].append(
                {"raw_id": raw_id, "title": title, "matched_signal": matched_signal, "url": url}
            )

        # 2. 제목 유사도 검사 (중복이 아닌 경우만)
        elif title:
            best_match_score = 0
            best_match_id = None

            for existing_title, existing_id in existing_titles.items():
                similarity = calculate_similarity(title, existing_title)
                if similarity > best_match_score:
                    best_match_score = similarity
                    best_match_id = existing_id

            # 85% 이상 유사도이면 중복
            if best_match_score >= 0.85:
                is_duplicate = True
                duplicate_reason = "similar_title"
                matched_signal = best_match_id
                results["duplicates"]["similar_title"].append(
                    {
                        "raw_id": raw_id,
                        "title": title,
                        "similarity": round(best_match_score * 100, 1),
                        "matched_signal": best_match_id,
                    }
                )

        # 3. 엔티티 오버랩 검사 (중복이 아닌 경우만)
        if not is_duplicate:
            raw_entities = extract_entities(raw_signal)

            for existing_id, existing_ents in existing_entities.items():
                if raw_entities and existing_ents:
                    overlap = len(raw_entities & existing_ents) / max(len(raw_entities), len(existing_ents))

                    # 80% 이상 겹침 + 유사 내용
                    if overlap >= 0.80:
                        # 내용 유사도 추가 검사
                        summary1 = raw_signal.get("summary", "")
                        # summary2는 database에서 찾아야 함
                        content_sim = 0

                        for db_sig in database.get("signals", []):
                            if db_sig.get("id") == existing_id:
                                summary2 = db_sig.get("summary", "")
                                content_sim = calculate_similarity(summary1, summary2)
                                break

                        # 내용 유사도 85% 이상이면 중복
                        if content_sim >= 0.85:
                            is_duplicate = True
                            duplicate_reason = "similar_content"
                            matched_signal = existing_id
                            results["duplicates"]["similar_content"].append(
                                {
                                    "raw_id": raw_id,
                                    "title": title,
                                    "content_similarity": round(content_sim * 100, 1),
                                    "entity_overlap": round(overlap * 100, 1),
                                    "matched_signal": existing_id,
                                }
                            )
                            break
                        else:
                            # 플래그만 설정
                            results["duplicates"]["entity_overlap"].append(
                                {
                                    "raw_id": raw_id,
                                    "title": title,
                                    "entity_overlap": round(overlap * 100, 1),
                                    "content_similarity": round(content_sim * 100, 1),
                                    "matched_signal": existing_id,
                                    "recommendation": "REVIEW",
                                }
                            )

        # 새 신호 추가
        if not is_duplicate:
            results["new_signals"].append(
                {
                    "raw_id": raw_id,
                    "title": title,
                    "url": url,
                    "source_name": raw_signal.get("source_name", ""),
                    "published_date": raw_signal.get("published_date", ""),
                    "summary": raw_signal.get("summary", ""),
                    "category_hint": raw_signal.get("category_hint", ""),
                    "significance": raw_signal.get("significance", 3),
                    "key_entities": raw_signal.get("key_entities", []),
                }
            )

    return results


def generate_dedup_log(results):
    """중복 필터링 로그 생성"""
    log_lines = []
    log_lines.append(f"[{results['filter_date']} {results['filter_time']}] Deduplication Started")
    log_lines.append(f"[{results['filter_date']}] Total items to check: {results['total_scanned']}\n")

    # 정확 URL 중복
    if results["duplicates"]["exact_url"]:
        log_lines.append(f"REMOVED - exact_url ({len(results['duplicates']['exact_url'])}):")
        for dup in results["duplicates"]["exact_url"]:
            log_lines.append(f'  - {dup["raw_id"]}: "{dup["title"][:60]}..." (matches {dup["matched_signal"]})')
        log_lines.append("")

    # 제목 유사도
    if results["duplicates"]["similar_title"]:
        log_lines.append(f"REMOVED - similar_title (>=85%) ({len(results['duplicates']['similar_title'])}):")
        for dup in results["duplicates"]["similar_title"]:
            log_lines.append(
                f'  - {dup["raw_id"]}: "{dup["title"][:60]}..." ({dup["similarity"]}% match with {dup["matched_signal"]})'
            )
        log_lines.append("")

    # 유사 콘텐츠
    if results["duplicates"]["similar_content"]:
        log_lines.append(f"REMOVED - similar_content (>=85%) ({len(results['duplicates']['similar_content'])}):")
        for dup in results["duplicates"]["similar_content"]:
            log_lines.append(
                f'  - {dup["raw_id"]}: "{dup["title"][:60]}..." ({dup["content_similarity"]}% match with {dup["matched_signal"]})'
            )
        log_lines.append("")

    # 엔티티 오버랩 (검토 권장)
    if results["duplicates"]["entity_overlap"]:
        log_lines.append(
            f"FLAGGED - entity_overlap (review recommended) ({len(results['duplicates']['entity_overlap'])}):"
        )
        for flag in results["duplicates"]["entity_overlap"]:
            log_lines.append(
                f"  - {flag['raw_id']}: Shares {flag['entity_overlap']}% entities with {flag['matched_signal']} (content: {flag['content_similarity']}%)"
            )
        log_lines.append("")

    log_lines.append(f"[{results['filter_date']}] Deduplication Completed")
    log_lines.append(f"  - Total Scanned: {results['total_scanned']}")
    log_lines.append(f"  - Exact URL Duplicates: {len(results['duplicates']['exact_url'])}")
    log_lines.append(f"  - Title Duplicates: {len(results['duplicates']['similar_title'])}")
    log_lines.append(f"  - Content Duplicates: {len(results['duplicates']['similar_content'])}")
    log_lines.append(f"  - Entity Overlap Flags: {len(results['duplicates']['entity_overlap'])}")
    log_lines.append(f"  - New Signals: {len(results['new_signals'])}")
    log_lines.append(f"  - Duplicates Removed: {results['total_scanned'] - len(results['new_signals'])}")

    return "\n".join(log_lines)


def main():
    # 파일 로드
    print("Loading files...")
    raw_signals = load_json(
        "/Users/cys/Desktop/ENVscanning-system-main/env-scanning/raw/scanned-signals-2026-01-11-ALT.json"
    )
    database = load_json("/Users/cys/Desktop/ENVscanning-system-main/env-scanning/signals/database.json")
    dedup_index = load_json(
        "/Users/cys/Desktop/ENVscanning-system-main/env-scanning/context/dedup-index-2026-01-11.json"
    )

    raw_items = raw_signals.get("items", [])
    print(f"Loaded {len(raw_items)} raw signals")

    # 중복 필터링 수행
    print("Running deduplication...")
    results = dedup_filtering(raw_items, database, dedup_index)

    # 통계 계산
    total_duplicates = (
        len(results["duplicates"]["exact_url"])
        + len(results["duplicates"]["similar_title"])
        + len(results["duplicates"]["similar_content"])
    )

    print("\nDeduplication Results:")
    print(f"  Total scanned: {results['total_scanned']}")
    print(f"  New signals: {len(results['new_signals'])}")
    print(f"  Duplicates removed: {total_duplicates}")
    print(f"    - Exact URL: {len(results['duplicates']['exact_url'])}")
    print(f"    - Similar title: {len(results['duplicates']['similar_title'])}")
    print(f"    - Similar content: {len(results['duplicates']['similar_content'])}")
    print(f"  Entity overlaps (flagged): {len(results['duplicates']['entity_overlap'])}")

    # 필터링된 신호 저장
    output = {
        "filter_date": results["filter_date"],
        "filter_time": results["filter_time"],
        "stats": {
            "total_scanned": results["total_scanned"],
            "duplicates_removed": total_duplicates,
            "new_signals": len(results["new_signals"]),
            "entity_overlap_flags": len(results["duplicates"]["entity_overlap"]),
            "breakdowns": {
                "exact_url": len(results["duplicates"]["exact_url"]),
                "similar_title": len(results["duplicates"]["similar_title"]),
                "similar_content": len(results["duplicates"]["similar_content"]),
            },
        },
        "new_signals": results["new_signals"],
        "duplicates_detail": results["duplicates"],
    }

    with open(
        "/Users/cys/Desktop/ENVscanning-system-main/env-scanning/filtered/filtered-signals-2026-01-11-ALT.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # 로그 생성
    log = generate_dedup_log(results)
    with open(
        "/Users/cys/Desktop/ENVscanning-system-main/env-scanning/logs/dedup-log-2026-01-11-ALT.txt",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(log)

    print("\nFiles saved:")
    print("  - Filtered signals: env-scanning/filtered/filtered-signals-2026-01-11-ALT.json")
    print("  - Dedup log: env-scanning/logs/dedup-log-2026-01-11-ALT.txt")


if __name__ == "__main__":
    main()
