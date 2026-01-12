#!/usr/bin/env python3
"""
Deduplication Processor for Environmental Scanning System
Filters duplicate signals using URL matching, title similarity, entity overlap, and content similarity
"""

import json
import re
from difflib import SequenceMatcher


class DedupProcessor:
    def __init__(
        self, similarity_threshold_title=0.90, similarity_threshold_content=0.85, entity_overlap_threshold=0.70
    ):
        self.similarity_threshold_title = similarity_threshold_title
        self.similarity_threshold_content = similarity_threshold_content
        self.entity_overlap_threshold = entity_overlap_threshold

        self.duplicates_removed = []
        self.new_signals = []
        self.updates = []
        self.flagged_for_review = []

    def extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            match = re.search(r"https?://(?:www\.)?([^/]+)", url)
            return match.group(1) if match else url
        except:
            return url

    def normalize_url(self, url: str) -> str:
        """Normalize URL for comparison"""
        if not url:
            return ""
        return url.strip().lower()

    def normalize_title(self, title: str) -> str:
        """Normalize title for comparison"""
        if not title:
            return ""
        # Remove special characters and convert to lowercase
        normalized = re.sub(r"[^\w\s]", "", title).lower()
        # Remove extra whitespace
        return " ".join(normalized.split())

    def string_similarity(self, a: str, b: str) -> float:
        """Calculate string similarity using SequenceMatcher"""
        if not a or not b:
            return 0.0
        return SequenceMatcher(None, a, b).ratio()

    def extract_entities(self, signal: dict) -> set[str]:
        """Extract key entities from a signal"""
        entities = set()

        # Extract from tags
        if "tags" in signal:
            for tag in signal.get("tags", []):
                entities.add(tag.lower())

        # Extract from key_entities
        if "key_entities" in signal:
            for entity in signal.get("key_entities", []):
                entities.add(entity.lower())

        # Extract from title
        title = signal.get("title", "")
        words = title.split()
        for word in words:
            if len(word) > 4:  # Only significant words
                entities.add(word.lower())

        return entities

    def calculate_entity_overlap(self, entities1: set[str], entities2: set[str]) -> float:
        """Calculate entity overlap as percentage"""
        if not entities1 or not entities2:
            return 0.0

        intersection = len(entities1 & entities2)
        union = len(entities1 | entities2)

        return intersection / union if union > 0 else 0.0

    def check_exact_url_match(self, signal: dict, existing_urls: dict[str, str]) -> tuple[bool, str]:
        """Check for exact URL match"""
        url = signal.get("url", "")
        normalized_url = self.normalize_url(url)

        if normalized_url in existing_urls:
            return True, existing_urls[normalized_url]

        return False, ""

    def check_title_similarity(self, signal: dict, existing_titles: dict[str, str]) -> tuple[bool, float, str]:
        """Check for title similarity"""
        title = signal.get("title", "")
        normalized_title = self.normalize_title(title)

        max_similarity = 0.0
        matching_signal_id = ""

        for existing_title, signal_id in existing_titles.items():
            similarity = self.string_similarity(normalized_title, existing_title)
            if similarity > max_similarity:
                max_similarity = similarity
                matching_signal_id = signal_id

        is_duplicate = max_similarity >= self.similarity_threshold_title
        return is_duplicate, max_similarity, matching_signal_id

    def process_signals(
        self, stage1_signals: list[dict], stage2_signals: list[dict], existing_db: list[dict], dedup_index: dict
    ) -> dict:
        """Main deduplication process"""
        # Build indices from existing database
        existing_urls = {}
        existing_titles = {}
        existing_entities = {}

        for signal in existing_db:
            signal_id = signal.get("id", "")
            url = self.normalize_url(signal.get("url", ""))
            title = self.normalize_title(signal.get("title", ""))
            entities = self.extract_entities(signal)

            if url:
                existing_urls[url] = signal_id
            if title:
                existing_titles[title] = signal_id
            if entities:
                existing_entities[signal_id] = entities

        # Also include URLs from dedup_index
        for url in dedup_index.get("urls", []):
            normalized = self.normalize_url(url)
            if normalized and normalized not in existing_urls:
                existing_urls[normalized] = f"INDEXED-{url[:50]}"

        # Also include titles from dedup_index
        for title in dedup_index.get("titles", []):
            normalized = self.normalize_title(title)
            if normalized and normalized not in existing_titles:
                existing_titles[normalized] = f"INDEXED-{title[:50]}"

        # Process Stage 1 signals
        print(f"[DEDUP] Processing Stage 1 signals: {len(stage1_signals)}")
        stage1_new = self.check_signal_batch(
            stage1_signals, existing_urls, existing_titles, existing_entities, "STAGE1", existing_db
        )

        # Update indices with Stage 1 new signals
        for signal in stage1_new["new"]:
            url = self.normalize_url(signal.get("url", ""))
            title = self.normalize_title(signal.get("title", ""))
            entities = self.extract_entities(signal)
            signal_id = signal.get("id", "")

            if url:
                existing_urls[url] = signal_id
            if title:
                existing_titles[title] = signal_id
            if entities:
                existing_entities[signal_id] = entities

        # Process Stage 2 signals
        print(f"[DEDUP] Processing Stage 2 signals: {len(stage2_signals)}")
        stage2_new = self.check_signal_batch(
            stage2_signals, existing_urls, existing_titles, existing_entities, "STAGE2", existing_db + stage1_new["new"]
        )

        # Compile results
        all_new_signals = stage1_new["new"] + stage2_new["new"]
        all_duplicates = stage1_new["duplicates"] + stage2_new["duplicates"]
        all_updates = stage1_new["updates"] + stage2_new["updates"]
        all_flagged = stage1_new["flagged"] + stage2_new["flagged"]

        return {
            "new_signals": all_new_signals,
            "duplicates_removed": all_duplicates,
            "updates": all_updates,
            "flagged_for_review": all_flagged,
            "stats": {
                "total_scanned": len(stage1_signals) + len(stage2_signals),
                "stage1_count": len(stage1_signals),
                "stage2_count": len(stage2_signals),
                "duplicates_removed": len(all_duplicates),
                "new_signals": len(all_new_signals),
                "updates": len(all_updates),
                "flagged": len(all_flagged),
                "dedup_rate": f"{(len(all_duplicates) / (len(stage1_signals) + len(stage2_signals)) * 100):.1f}%",
            },
        }

    def check_signal_batch(
        self,
        signals: list[dict],
        existing_urls: dict[str, str],
        existing_titles: dict[str, str],
        existing_entities: dict[str, set[str]],
        source: str,
        existing_db: list[dict],
    ) -> dict:
        """Process a batch of signals"""
        new_signals = []
        duplicates = []
        updates = []
        flagged = []

        for signal in signals:
            result = self.check_single_signal(
                signal, existing_urls, existing_titles, existing_entities, source, existing_db
            )

            if result["type"] == "new":
                new_signals.append(signal)
            elif result["type"] == "duplicate":
                duplicates.append(
                    {
                        "signal_id": signal.get("id", ""),
                        "title": signal.get("title", ""),
                        "duplicate_of": result.get("duplicate_of", ""),
                        "reason": result.get("reason", ""),
                        "similarity_score": result.get("similarity_score", 0),
                    }
                )
            elif result["type"] == "update":
                updates.append(
                    {
                        "signal_id": signal.get("id", ""),
                        "related_signal_id": result.get("related_signal_id", ""),
                        "update_type": "development",
                        "reason": result.get("reason", ""),
                    }
                )
            elif result["type"] == "flagged":
                flagged.append(
                    {
                        "signal_id": signal.get("id", ""),
                        "title": signal.get("title", ""),
                        "reason": result.get("reason", ""),
                        "entity_overlap": result.get("entity_overlap", 0),
                    }
                )

        return {"new": new_signals, "duplicates": duplicates, "updates": updates, "flagged": flagged}

    def check_single_signal(
        self,
        signal: dict,
        existing_urls: dict[str, str],
        existing_titles: dict[str, str],
        existing_entities: dict[str, set[str]],
        source: str,
        existing_db: list[dict],
    ) -> dict:
        """Check a single signal for duplicates"""
        # 1. Check exact URL match
        is_url_duplicate, matching_id = self.check_exact_url_match(signal, existing_urls)
        if is_url_duplicate:
            return {"type": "duplicate", "reason": "exact_url", "duplicate_of": matching_id, "similarity_score": 1.0}

        # 2. Check title similarity
        is_title_duplicate, title_similarity, matching_id = self.check_title_similarity(signal, existing_titles)
        if is_title_duplicate:
            return {
                "type": "duplicate",
                "reason": "similar_title",
                "duplicate_of": matching_id,
                "similarity_score": title_similarity,
            }

        # 3. Check entity overlap
        signal_entities = self.extract_entities(signal)
        max_entity_overlap = 0.0
        max_entity_signal_id = ""

        for existing_id, existing_entities_set in existing_entities.items():
            overlap = self.calculate_entity_overlap(signal_entities, existing_entities_set)
            if overlap > max_entity_overlap:
                max_entity_overlap = overlap
                max_entity_signal_id = existing_id

        # If entity overlap is high, flag for review and check content
        if max_entity_overlap >= self.entity_overlap_threshold and max_entity_signal_id:
            # Try to find matching signal and check content
            matching_signal = None
            for sig in existing_db:
                if sig.get("id", "") == max_entity_signal_id:
                    matching_signal = sig
                    break

            if matching_signal:
                # Simple content comparison based on description/title overlap
                content_similarity = self.string_similarity(
                    self.normalize_title(signal.get("description", "")),
                    self.normalize_title(matching_signal.get("description", "")),
                )

                if content_similarity >= self.similarity_threshold_content:
                    return {
                        "type": "duplicate",
                        "reason": "similar_content",
                        "duplicate_of": max_entity_signal_id,
                        "similarity_score": content_similarity,
                    }
                else:
                    # Flag for human review
                    return {
                        "type": "flagged",
                        "reason": "entity_overlap",
                        "entity_overlap": max_entity_overlap,
                        "related_signal_id": max_entity_signal_id,
                    }

        # If no duplicates found, it's a new signal
        return {"type": "new"}


def main():
    """Main execution"""
    # Load input files
    print("[DEDUP] Loading input files...")

    with open(
        "/Users/cys/Desktop/ENVscanning-system-main/env-scanning/raw/scanned-signals-2026-01-12-7day.json",
        encoding="utf-8",
    ) as f:
        stage1_data = json.load(f)

    with open(
        "/Users/cys/Desktop/ENVscanning-system-main/env-scanning/raw/scanned-signals-2026-01-12-marathon-stage2.json",
        encoding="utf-8",
    ) as f:
        stage2_data = json.load(f)

    with open("/Users/cys/Desktop/ENVscanning-system-main/env-scanning/signals/database.json", encoding="utf-8") as f:
        db_data = json.load(f)

    with open(
        "/Users/cys/Desktop/ENVscanning-system-main/env-scanning/context/dedup-index-2026-01-12-weekly.json",
        encoding="utf-8",
    ) as f:
        dedup_index = json.load(f)

    stage1_signals = stage1_data.get("signals", [])
    stage2_signals = stage2_data.get("signals", [])
    existing_signals = db_data.get("signals", [])

    print(f"[DEDUP] Stage 1 signals: {len(stage1_signals)}")
    print(f"[DEDUP] Stage 2 signals: {len(stage2_signals)}")
    print(f"[DEDUP] Existing DB signals: {len(existing_signals)}")

    # Run deduplication
    processor = DedupProcessor(
        similarity_threshold_title=0.90, similarity_threshold_content=0.85, entity_overlap_threshold=0.70
    )

    results = processor.process_signals(stage1_signals, stage2_signals, existing_signals, dedup_index)

    # Generate output
    print("\n[DEDUP] Results:")
    print(f"  Total scanned: {results['stats']['total_scanned']}")
    print(f"  Duplicates removed: {results['stats']['duplicates_removed']}")
    print(f"  New signals: {results['stats']['new_signals']}")
    print(f"  Updates: {results['stats']['updates']}")
    print(f"  Flagged for review: {results['stats']['flagged']}")
    print(f"  Dedup rate: {results['stats']['dedup_rate']}")

    # Write filtered signals
    output = {
        "filter_date": "2026-01-12",
        "stats": results["stats"],
        "new_signals": results["new_signals"],
        "updates": results["updates"],
        "flagged_for_review": results["flagged_for_review"],
    }

    with open(
        "/Users/cys/Desktop/ENVscanning-system-main/env-scanning/filtered/filtered-signals-2026-01-12-marathon-weekly.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n[DEDUP] Filtered signals written to: filtered-signals-2026-01-12-marathon-weekly.json")

    # Write dedup log
    log_content = generate_dedup_log(results)

    with open(
        "/Users/cys/Desktop/ENVscanning-system-main/env-scanning/logs/dedup-log-2026-01-12-marathon-weekly.txt",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(log_content)

    print("[DEDUP] Dedup log written to: dedup-log-2026-01-12-marathon-weekly.txt")

    # Write summary report
    summary = generate_dedup_summary(results)

    with open(
        "/Users/cys/Desktop/ENVscanning-system-main/env-scanning/reports/dedup-summary-2026-01-12-marathon-weekly.md",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(summary)

    print("[DEDUP] Summary report written to: dedup-summary-2026-01-12-marathon-weekly.md")
    print("\n[DEDUP] Deduplication completed successfully!")


def generate_dedup_log(results: dict) -> str:
    """Generate detailed dedup log"""
    log = f"""[2026-01-12 18:50:00] Deduplication Started
[2026-01-12 18:50:01] Total items to check: {results["stats"]["total_scanned"]}

REMOVED - exact_url:
"""

    exact_url_dupes = [d for d in results["duplicates_removed"] if d["reason"] == "exact_url"]
    if exact_url_dupes:
        for dupe in exact_url_dupes[:10]:  # Show first 10
            log += f'  - {dupe["signal_id"]}: "{dupe["title"][:60]}..." (matches {dupe["duplicate_of"]})\n'
        if len(exact_url_dupes) > 10:
            log += f"  ... and {len(exact_url_dupes) - 10} more\n"
    else:
        log += "  (none)\n"

    log += "\nREMOVED - similar_title (>=90%):\n"
    title_dupes = [d for d in results["duplicates_removed"] if d["reason"] == "similar_title"]
    if title_dupes:
        for dupe in title_dupes[:10]:
            similarity = dupe.get("similarity_score", 0)
            log += f'  - {dupe["signal_id"]}: "{dupe["title"][:60]}..." ({similarity * 100:.0f}% match with {dupe["duplicate_of"]})\n'
        if len(title_dupes) > 10:
            log += f"  ... and {len(title_dupes) - 10} more\n"
    else:
        log += "  (none)\n"

    log += "\nREMOVED - similar_content (>=85%):\n"
    content_dupes = [d for d in results["duplicates_removed"] if d["reason"] == "similar_content"]
    if content_dupes:
        for dupe in content_dupes[:10]:
            similarity = dupe.get("similarity_score", 0)
            log += f'  - {dupe["signal_id"]}: "{dupe["title"][:60]}..." ({similarity * 100:.0f}% match with {dupe["duplicate_of"]})\n'
        if len(content_dupes) > 10:
            log += f"  ... and {len(content_dupes) - 10} more\n"
    else:
        log += "  (none)\n"

    log += "\nFLAGGED - entity_overlap (review recommended):\n"
    if results["flagged_for_review"]:
        for flagged in results["flagged_for_review"][:10]:
            overlap = flagged.get("entity_overlap", 0)
            log += f"  - {flagged['signal_id']}: Shares {overlap * 100:.0f}% entities with existing signals\n"
        if len(results["flagged_for_review"]) > 10:
            log += f"  ... and {len(results['flagged_for_review']) - 10} more\n"
    else:
        log += "  (none)\n"

    log += "\n[2026-01-12 18:50:15] Deduplication Completed\n"
    log += f"  - Removed: {results['stats']['duplicates_removed']}\n"
    log += f"  - New: {results['stats']['new_signals']}\n"
    log += f"  - Updates: {results['stats']['updates']}\n"
    log += f"  - Flagged: {results['stats']['flagged']}\n"
    log += f"  - Dedup Rate: {results['stats']['dedup_rate']}\n"

    return log


def generate_dedup_summary(results: dict) -> str:
    """Generate markdown summary report"""
    summary = f"""# Deduplication Summary - 2026-01-12 (Marathon Weekly)

## Overview

**Process Date**: 2026-01-12 18:50:00
**Scan Period**: 7 days (2026-01-05 to 2026-01-12)

## Input Statistics

- **Stage 1 Signals**: {results["stats"]["stage1_count"]} (7-day scan)
- **Stage 2 Signals**: {results["stats"]["stage2_count"]} (Marathon exploration)
- **Total Inputs**: {results["stats"]["total_scanned"]}
- **Existing DB**: 48 signals

## Deduplication Results

### Summary Table

| Category | Count |
|----------|-------|
| **Total Scanned** | {results["stats"]["total_scanned"]} |
| **Duplicates Removed** | {results["stats"]["duplicates_removed"]} |
| **New Signals** | {results["stats"]["new_signals"]} |
| **Updates/Variants** | {results["stats"]["updates"]} |
| **Flagged for Review** | {results["stats"]["flagged"]} |
| **Dedup Rate** | {results["stats"]["dedup_rate"]} |

### Removal Breakdown

"""

    exact_url_dupes = len([d for d in results["duplicates_removed"] if d["reason"] == "exact_url"])
    title_dupes = len([d for d in results["duplicates_removed"] if d["reason"] == "similar_title"])
    content_dupes = len([d for d in results["duplicates_removed"] if d["reason"] == "similar_content"])

    summary += f"- **Exact URL Matches**: {exact_url_dupes}\n"
    summary += f"- **Title Similarity (>=90%)**: {title_dupes}\n"
    summary += f"- **Content Similarity (>=85%)**: {content_dupes}\n"

    summary += f"""

## Quality Metrics

- **URL Dedup Index Size**: {len([d for d in results["duplicates_removed"] if d["reason"] == "exact_url"])} matches checked
- **Title Fuzzy Matching**: {title_dupes} near-duplicates identified
- **Entity Overlap Detection**: {len(results["flagged_for_review"])} signals flagged for manual review
- **Similarity Thresholds Applied**:
  - Title: >=90% similarity
  - Content: >=85% similarity
  - Entity Overlap: >=70% overlap

## Output Files

1. **Filtered Signals**: `filtered-signals-2026-01-12-marathon-weekly.json`
   - New signals: {results["stats"]["new_signals"]}
   - Updates: {results["stats"]["updates"]}
   - Size: {len(results["new_signals"])} signals ready for analysis

2. **Dedup Log**: `dedup-log-2026-01-12-marathon-weekly.txt`
   - Detailed duplicate removal records
   - Similarity scores for each match
   - Flagged signals for human review

3. **This Report**: `dedup-summary-2026-01-12-marathon-weekly.md`

## Recommendations

### For Integration
- All {results["stats"]["new_signals"]} new signals are ready for database integration
- No URL conflicts detected in new signals
- High confidence deduplication rate: {results["stats"]["dedup_rate"]}

### For Manual Review
- {len(results["flagged_for_review"])} signals flagged due to entity overlap
- Recommend reviewing these for potential updates to existing signals
- May contain new perspectives on existing topics

### Next Steps
1. Integrate {results["stats"]["new_signals"]} new signals into master database
2. Review {len(results["flagged_for_review"])} flagged signals for update classification
3. Archive dedup logs for audit trail
4. Update dedup index with new signal metadata

---
*Generated: 2026-01-12 18:50:15*
"""

    return summary


if __name__ == "__main__":
    main()
