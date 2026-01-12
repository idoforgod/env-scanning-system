#!/usr/bin/env python3
"""
Environment Scanning System - TDD Pipeline Test Suite
=====================================================
Tests completeness, integrity, and data consistency across the entire pipeline.

Test Categories:
1. Agent Definition Tests - All agents properly defined
2. Schema Validation Tests - All files follow expected schemas
3. Pipeline Data Flow Tests - Data consistency between stages
4. Required Field Tests - Mandatory fields present
5. Signal ID Consistency Tests - ID format and linkage
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

# Configuration
BASE_PATH = Path("/Users/cys/Desktop/ENVscanning-system-main/env-scanning")
AGENTS_PATH = Path("/Users/cys/Desktop/ENVscanning-system-main/.claude/agents")
TEST_DATE = "2026-01-12"

# Test Results Storage
test_results = {
    "test_date": datetime.now().isoformat(),
    "target_date": TEST_DATE,
    "categories": {},
    "summary": {"total_tests": 0, "passed": 0, "failed": 0, "warnings": 0},
}


def add_test_result(category: str, test_name: str, status: str, details: str = "", data: Any = None):
    """Add a test result to the results storage."""
    if category not in test_results["categories"]:
        test_results["categories"][category] = []

    result = {
        "test": test_name,
        "status": status,  # PASS, FAIL, WARN
        "details": details,
    }
    if data:
        result["data"] = data

    test_results["categories"][category].append(result)
    test_results["summary"]["total_tests"] += 1

    if status == "PASS":
        test_results["summary"]["passed"] += 1
    elif status == "FAIL":
        test_results["summary"]["failed"] += 1
    else:
        test_results["summary"]["warnings"] += 1


def load_json_file(filepath: Path) -> dict:
    """Load a JSON file and return its contents."""
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


# ============================================================
# TEST CATEGORY 1: Agent Definition Tests
# ============================================================


def test_agent_definitions():
    """Test that all required agents are properly defined."""
    print("\n" + "=" * 60)
    print("TEST CATEGORY 1: Agent Definition Tests")
    print("=" * 60)

    required_agents = [
        # Phase 1
        "archive-loader",
        "multi-source-scanner",
        "dedup-filter",
        # Phase 2
        "signal-classifier",
        "confidence-evaluator",
        "hallucination-detector",
        "pipeline-validator",
        "impact-analyzer",
        "priority-ranker",
        # Phase 3
        "db-updater",
        "report-generator",
        "archive-notifier",
        "source-evolver",
        "file-organizer",
    ]

    existing_agents = []
    missing_agents = []

    for agent in required_agents:
        agent_file = AGENTS_PATH / f"{agent}.md"
        if agent_file.exists():
            existing_agents.append(agent)
        else:
            missing_agents.append(agent)

    # Test: All required agents exist
    if not missing_agents:
        add_test_result(
            "Agent Definition",
            "Required Agents Exist",
            "PASS",
            f"All {len(required_agents)} required agents are defined",
            {"existing": existing_agents},
        )
        print(f"✅ PASS: All {len(required_agents)} required agents exist")
    else:
        add_test_result(
            "Agent Definition",
            "Required Agents Exist",
            "FAIL",
            f"Missing {len(missing_agents)} agents",
            {"missing": missing_agents, "existing": existing_agents},
        )
        print(f"❌ FAIL: Missing agents: {missing_agents}")

    # Test: Agent files have required sections
    # Accept various documentation patterns
    required_section_patterns = [
        ["## 역할", "# Role", "## Task", "## Role"],  # Role/Task
        ["## 입력", "# Input", "## Process", "## Inputs", "1. **Load"],  # Input/Process
        ["## 출력", "# Output", "## Output Format", "## Outputs", "## Output"],  # Output
    ]
    agents_with_issues = []

    for agent in existing_agents:
        agent_file = AGENTS_PATH / f"{agent}.md"
        content = agent_file.read_text(encoding="utf-8")
        missing_sections = []
        for patterns in required_section_patterns:
            if not any(p in content for p in patterns):
                missing_sections.append(patterns[0])  # Report first pattern as missing
        if missing_sections:
            agents_with_issues.append({"agent": agent, "missing": missing_sections})

    if not agents_with_issues:
        add_test_result(
            "Agent Definition",
            "Agent Documentation Complete",
            "PASS",
            "All agents have required documentation sections",
        )
        print("✅ PASS: All agents have required documentation sections")
    else:
        add_test_result(
            "Agent Definition",
            "Agent Documentation Complete",
            "WARN",
            f"{len(agents_with_issues)} agents have incomplete documentation",
            agents_with_issues,
        )
        print(f"⚠️ WARN: {len(agents_with_issues)} agents have incomplete documentation")


# ============================================================
# TEST CATEGORY 2: Schema Validation Tests
# ============================================================


def test_schema_validation():
    """Test that all data files follow expected schemas."""
    print("\n" + "=" * 60)
    print("TEST CATEGORY 2: Schema Validation Tests")
    print("=" * 60)

    # Test: Database schema
    db_path = BASE_PATH / "signals" / "database.json"
    if db_path.exists():
        db = load_json_file(db_path)
        required_db_fields = ["metadata", "statistics", "signals"]
        missing_fields = [f for f in required_db_fields if f not in db]

        if not missing_fields:
            add_test_result(
                "Schema Validation",
                "Database Schema Valid",
                "PASS",
                f"Database has all required fields, {db['metadata'].get('total_signals', 0)} signals",
            )
            print(f"✅ PASS: Database schema valid ({db['metadata'].get('total_signals', 0)} signals)")
        else:
            add_test_result(
                "Schema Validation", "Database Schema Valid", "FAIL", f"Database missing fields: {missing_fields}"
            )
            print(f"❌ FAIL: Database missing fields: {missing_fields}")

    # Test: Filtered signals schema
    filtered_path = BASE_PATH / "filtered" / "2026" / "01" / "12" / f"filtered-signals-{TEST_DATE}.json"
    if filtered_path.exists():
        filtered = load_json_file(filtered_path)
        required_filtered_fields = ["filter_date", "new_signals"]
        missing = [f for f in required_filtered_fields if f not in filtered]

        if not missing:
            signal_count = len(filtered.get("new_signals", []))
            add_test_result(
                "Schema Validation",
                "Filtered Signals Schema Valid",
                "PASS",
                f"Filtered signals has correct schema, {signal_count} signals",
            )
            print(f"✅ PASS: Filtered signals schema valid ({signal_count} signals)")
        else:
            add_test_result("Schema Validation", "Filtered Signals Schema Valid", "FAIL", f"Missing fields: {missing}")
            print(f"❌ FAIL: Filtered signals missing fields: {missing}")
    else:
        add_test_result(
            "Schema Validation", "Filtered Signals Schema Valid", "FAIL", f"File not found: {filtered_path}"
        )
        print("❌ FAIL: Filtered signals file not found")

    # Test: Structured signals schema
    structured_path = BASE_PATH / "structured" / "2026" / "01" / "12" / f"structured-signals-{TEST_DATE}.json"
    if structured_path.exists():
        structured = load_json_file(structured_path)
        required_structured_fields = ["classification_date", "signals"]
        missing = [f for f in required_structured_fields if f not in structured]

        if not missing:
            signal_count = len(structured.get("signals", []))
            add_test_result(
                "Schema Validation",
                "Structured Signals Schema Valid",
                "PASS",
                f"Structured signals has correct schema, {signal_count} signals",
            )
            print(f"✅ PASS: Structured signals schema valid ({signal_count} signals)")
        else:
            add_test_result(
                "Schema Validation", "Structured Signals Schema Valid", "FAIL", f"Missing fields: {missing}"
            )
            print(f"❌ FAIL: Structured signals missing fields: {missing}")
    else:
        add_test_result(
            "Schema Validation", "Structured Signals Schema Valid", "FAIL", f"File not found: {structured_path}"
        )
        print("❌ FAIL: Structured signals file not found")

    # Test: pSRT scores schema
    psrt_path = BASE_PATH / "analysis" / "2026" / "01" / "12" / f"pSRT-scores-{TEST_DATE}.json"
    if psrt_path.exists():
        psrt = load_json_file(psrt_path)
        required_psrt_fields = ["calculation_date", "pSRT_scores"]
        missing = [f for f in required_psrt_fields if f not in psrt]

        if not missing:
            signal_count = len(psrt.get("pSRT_scores", []))
            add_test_result(
                "Schema Validation",
                "pSRT Scores Schema Valid",
                "PASS",
                f"pSRT scores has correct schema, {signal_count} signals",
            )
            print(f"✅ PASS: pSRT scores schema valid ({signal_count} signals)")
        else:
            add_test_result("Schema Validation", "pSRT Scores Schema Valid", "FAIL", f"Missing fields: {missing}")
            print(f"❌ FAIL: pSRT scores missing fields: {missing}")
    else:
        add_test_result("Schema Validation", "pSRT Scores Schema Valid", "FAIL", f"File not found: {psrt_path}")
        print("❌ FAIL: pSRT scores file not found")

    # Test: Priority ranking schema
    priority_path = BASE_PATH / "analysis" / "2026" / "01" / "12" / f"priority-ranked-{TEST_DATE}.json"
    if priority_path.exists():
        priority = load_json_file(priority_path)
        required_priority_fields = ["ranking_date", "formula"]
        missing = [f for f in required_priority_fields if f not in priority]

        if not missing:
            signal_count = priority.get("total_ranked", 0)
            add_test_result(
                "Schema Validation",
                "Priority Ranking Schema Valid",
                "PASS",
                f"Priority ranking has correct schema, {signal_count} signals",
            )
            print(f"✅ PASS: Priority ranking schema valid ({signal_count} signals)")
        else:
            add_test_result("Schema Validation", "Priority Ranking Schema Valid", "FAIL", f"Missing fields: {missing}")
            print(f"❌ FAIL: Priority ranking missing fields: {missing}")


# ============================================================
# TEST CATEGORY 3: Pipeline Data Flow Tests
# ============================================================


def test_pipeline_data_flow():
    """Test data consistency between pipeline stages."""
    print("\n" + "=" * 60)
    print("TEST CATEGORY 3: Pipeline Data Flow Tests")
    print("=" * 60)

    # Load all pipeline files
    filtered_path = BASE_PATH / "filtered" / "2026" / "01" / "12" / f"filtered-signals-{TEST_DATE}.json"
    structured_path = BASE_PATH / "structured" / "2026" / "01" / "12" / f"structured-signals-{TEST_DATE}.json"
    psrt_path = BASE_PATH / "analysis" / "2026" / "01" / "12" / f"pSRT-scores-{TEST_DATE}.json"
    priority_path = BASE_PATH / "analysis" / "2026" / "01" / "12" / f"priority-ranked-{TEST_DATE}.json"

    counts = {}
    ids = {}

    # Get filtered signals (exclude duplicates - they are intentionally not structured)
    if filtered_path.exists():
        filtered = load_json_file(filtered_path)
        all_signals = filtered.get("new_signals", [])
        # Only count signals that are NOT marked as duplicates
        non_duplicate_signals = [s for s in all_signals if s.get("classification") != "duplicate"]
        counts["filtered"] = len(non_duplicate_signals)
        counts["filtered_total"] = len(all_signals)  # For reporting
        counts["filtered_duplicates"] = len(all_signals) - len(non_duplicate_signals)
        ids["filtered"] = set(s.get("raw_id", "") for s in non_duplicate_signals)

    # Get structured signals
    if structured_path.exists():
        structured = load_json_file(structured_path)
        counts["structured"] = len(structured.get("signals", []))
        ids["structured"] = set(s.get("signal_id", "") for s in structured.get("signals", []))

    # Get pSRT scores
    if psrt_path.exists():
        psrt = load_json_file(psrt_path)
        counts["pSRT"] = len(psrt.get("pSRT_scores", []))
        ids["pSRT"] = set(s.get("signal_id", "") for s in psrt.get("pSRT_scores", []))

    # Get priority ranking
    if priority_path.exists():
        priority = load_json_file(priority_path)
        counts["priority"] = priority.get("total_ranked", 0)

    print("\n📊 Pipeline Signal Counts:")
    for stage, count in counts.items():
        if stage == "filtered":
            dup_count = counts.get("filtered_duplicates", 0)
            total = counts.get("filtered_total", count)
            if dup_count > 0:
                print(f"   {stage}: {count} (total: {total}, duplicates excluded: {dup_count})")
            else:
                print(f"   {stage}: {count}")
        elif stage not in ["filtered_total", "filtered_duplicates"]:
            print(f"   {stage}: {count}")

    # Test: Filtered → Structured consistency
    if "filtered" in counts and "structured" in counts:
        if counts["filtered"] == counts["structured"]:
            add_test_result(
                "Pipeline Data Flow",
                "Filtered → Structured Count Match",
                "PASS",
                f"Both have {counts['filtered']} signals",
            )
            print(f"✅ PASS: Filtered → Structured count match ({counts['filtered']})")
        else:
            diff = counts["filtered"] - counts["structured"]
            add_test_result(
                "Pipeline Data Flow",
                "Filtered → Structured Count Match",
                "FAIL",
                f"Filtered: {counts['filtered']}, Structured: {counts['structured']}, Diff: {diff}",
                {"filtered": counts["filtered"], "structured": counts["structured"]},
            )
            print(f"❌ FAIL: Filtered → Structured count mismatch (diff: {diff})")

    # Test: Structured → pSRT consistency
    if "structured" in counts and "pSRT" in counts:
        if counts["structured"] == counts["pSRT"]:
            add_test_result(
                "Pipeline Data Flow",
                "Structured → pSRT Count Match",
                "PASS",
                f"Both have {counts['structured']} signals",
            )
            print(f"✅ PASS: Structured → pSRT count match ({counts['structured']})")
        else:
            diff = counts["pSRT"] - counts["structured"]
            add_test_result(
                "Pipeline Data Flow",
                "Structured → pSRT Count Match",
                "FAIL",
                f"Structured: {counts['structured']}, pSRT: {counts['pSRT']}, Diff: {diff}",
                {"structured": counts["structured"], "pSRT": counts["pSRT"]},
            )
            print(f"❌ FAIL: Structured → pSRT count mismatch (diff: {diff})")

            # Find discrepancies
            if "structured" in ids and "pSRT" in ids:
                only_in_psrt = ids["pSRT"] - ids["structured"]
                only_in_structured = ids["structured"] - ids["pSRT"]
                if only_in_psrt:
                    print(f"   ↳ Only in pSRT: {only_in_psrt}")
                if only_in_structured:
                    print(f"   ↳ Only in Structured: {only_in_structured}")

    # Test: pSRT → Priority consistency
    if "pSRT" in counts and "priority" in counts:
        if counts["pSRT"] == counts["priority"]:
            add_test_result(
                "Pipeline Data Flow", "pSRT → Priority Count Match", "PASS", f"Both have {counts['pSRT']} signals"
            )
            print(f"✅ PASS: pSRT → Priority count match ({counts['pSRT']})")
        else:
            diff = counts["pSRT"] - counts["priority"]
            add_test_result(
                "Pipeline Data Flow",
                "pSRT → Priority Count Match",
                "FAIL",
                f"pSRT: {counts['pSRT']}, Priority: {counts['priority']}, Diff: {diff}",
            )
            print(f"❌ FAIL: pSRT → Priority count mismatch (diff: {diff})")


# ============================================================
# TEST CATEGORY 4: Required Field Tests
# ============================================================


def test_required_fields():
    """Test that all signals have required fields."""
    print("\n" + "=" * 60)
    print("TEST CATEGORY 4: Required Field Tests")
    print("=" * 60)

    # Structured signals required fields
    structured_path = BASE_PATH / "structured" / "2026" / "01" / "12" / f"structured-signals-{TEST_DATE}.json"
    if structured_path.exists():
        structured = load_json_file(structured_path)
        signals = structured.get("signals", [])

        required_fields = ["signal_id", "title", "category", "status", "significance", "confidence"]
        signals_missing_fields = []

        for signal in signals:
            missing = [f for f in required_fields if f not in signal or signal[f] is None]
            if missing:
                signals_missing_fields.append({"signal_id": signal.get("signal_id", "UNKNOWN"), "missing": missing})

        if not signals_missing_fields:
            add_test_result(
                "Required Fields",
                "Structured Signals Complete",
                "PASS",
                f"All {len(signals)} signals have required fields",
            )
            print(f"✅ PASS: All {len(signals)} structured signals have required fields")
        else:
            add_test_result(
                "Required Fields",
                "Structured Signals Complete",
                "FAIL",
                f"{len(signals_missing_fields)} signals missing required fields",
                signals_missing_fields[:5],  # First 5 examples
            )
            print(f"❌ FAIL: {len(signals_missing_fields)} signals missing required fields")

    # pSRT scores required fields
    psrt_path = BASE_PATH / "analysis" / "2026" / "01" / "12" / f"pSRT-scores-{TEST_DATE}.json"
    if psrt_path.exists():
        psrt = load_json_file(psrt_path)
        scores = psrt.get("pSRT_scores", [])

        required_fields = ["signal_id", "overall_pSRT", "grade", "component_scores"]
        signals_missing_fields = []

        for score in scores:
            missing = [f for f in required_fields if f not in score or score[f] is None]
            if missing:
                signals_missing_fields.append({"signal_id": score.get("signal_id", "UNKNOWN"), "missing": missing})

        if not signals_missing_fields:
            add_test_result(
                "Required Fields", "pSRT Scores Complete", "PASS", f"All {len(scores)} pSRT scores have required fields"
            )
            print(f"✅ PASS: All {len(scores)} pSRT scores have required fields")
        else:
            add_test_result(
                "Required Fields",
                "pSRT Scores Complete",
                "FAIL",
                f"{len(signals_missing_fields)} scores missing required fields",
                signals_missing_fields[:5],
            )
            print(f"❌ FAIL: {len(signals_missing_fields)} pSRT scores missing required fields")


# ============================================================
# TEST CATEGORY 5: Signal ID Consistency Tests
# ============================================================


def test_signal_id_consistency():
    """Test Signal ID format and linkage consistency."""
    print("\n" + "=" * 60)
    print("TEST CATEGORY 5: Signal ID Consistency Tests")
    print("=" * 60)

    # Signal ID format: SIG-{YYYY}-{MMDD}-{NNN}
    id_pattern = re.compile(r"^SIG-\d{4}-\d{4}-\d{3}$")

    structured_path = BASE_PATH / "structured" / "2026" / "01" / "12" / f"structured-signals-{TEST_DATE}.json"
    if structured_path.exists():
        structured = load_json_file(structured_path)
        signals = structured.get("signals", [])

        invalid_ids = []
        valid_ids = []

        for signal in signals:
            signal_id = signal.get("signal_id", "")
            if id_pattern.match(signal_id):
                valid_ids.append(signal_id)
            else:
                invalid_ids.append(signal_id)

        if not invalid_ids:
            add_test_result(
                "Signal ID Consistency",
                "Signal ID Format Valid",
                "PASS",
                f"All {len(valid_ids)} signal IDs follow correct format",
            )
            print(f"✅ PASS: All {len(valid_ids)} signal IDs have valid format")
        else:
            add_test_result(
                "Signal ID Consistency",
                "Signal ID Format Valid",
                "FAIL",
                f"{len(invalid_ids)} signal IDs have invalid format",
                {"invalid_ids": invalid_ids[:10]},
            )
            print(f"❌ FAIL: {len(invalid_ids)} signal IDs have invalid format")
            print(f"   ↳ Examples: {invalid_ids[:5]}")

    # Test: Signal ID date consistency
    date_pattern = re.compile(r"^SIG-(\d{4})-(\d{2})(\d{2})-\d{3}$")
    date_mismatches = []

    for signal in structured.get("signals", []):
        signal_id = signal.get("signal_id", "")
        match = date_pattern.match(signal_id)
        if match:
            id_year, id_month, id_day = match.groups()
            id_date = f"{id_year}-{id_month}-{id_day}"
            # Check if ID date matches test date
            if id_date != TEST_DATE:
                date_mismatches.append({"signal_id": signal_id, "id_date": id_date, "expected": TEST_DATE})

    # Note: Mixed dates are expected (updates to older signals)
    if date_mismatches:
        add_test_result(
            "Signal ID Consistency",
            "Signal ID Date Check",
            "WARN",
            f"{len(date_mismatches)} signals have IDs from different dates (expected for updates)",
            {"count": len(date_mismatches)},
        )
        print(f"⚠️ WARN: {len(date_mismatches)} signals have IDs from different dates (updates)")
    else:
        add_test_result("Signal ID Consistency", "Signal ID Date Check", "PASS", f"All signal IDs are from {TEST_DATE}")
        print(f"✅ PASS: All signal IDs are from {TEST_DATE}")


# ============================================================
# TEST CATEGORY 6: Hallucination Detection Tests
# ============================================================


def test_hallucination_detection():
    """Test hallucination detection pipeline."""
    print("\n" + "=" * 60)
    print("TEST CATEGORY 6: Hallucination Detection Tests")
    print("=" * 60)

    # Test: Hallucination report exists
    hall_path = BASE_PATH / "analysis" / "2026" / "01" / "12" / f"hallucination-report-{TEST_DATE}.json"

    if hall_path.exists():
        add_test_result(
            "Hallucination Detection", "Hallucination Report Exists", "PASS", "Hallucination report file found"
        )
        print("✅ PASS: Hallucination report exists")

        # Validate structure
        hall = load_json_file(hall_path)
        required_fields = ["detection_date", "flagged_signals"]
        missing = [f for f in required_fields if f not in hall]

        if not missing:
            flagged_count = len(hall.get("flagged_signals", []))
            add_test_result(
                "Hallucination Detection",
                "Hallucination Report Schema",
                "PASS",
                f"Valid schema with {flagged_count} flagged signals",
            )
            print(f"✅ PASS: Hallucination report schema valid ({flagged_count} flagged)")
        else:
            add_test_result(
                "Hallucination Detection", "Hallucination Report Schema", "FAIL", f"Missing fields: {missing}"
            )
            print(f"❌ FAIL: Hallucination report missing fields: {missing}")
    else:
        add_test_result(
            "Hallucination Detection",
            "Hallucination Report Exists",
            "FAIL",
            "Hallucination report not found - MANDATORY step skipped!",
            {"expected_path": str(hall_path)},
        )
        print("❌ FAIL: Hallucination report NOT FOUND (MANDATORY step skipped!)")
        print(f"   ↳ Expected: {hall_path}")

    # Test: pSRT has hallucination flags
    psrt_path = BASE_PATH / "analysis" / "2026" / "01" / "12" / f"pSRT-scores-{TEST_DATE}.json"
    if psrt_path.exists():
        psrt = load_json_file(psrt_path)
        scores = psrt.get("pSRT_scores", [])

        flagged_signals = [s for s in scores if s.get("flags")]
        low_grade_signals = [s for s in scores if s.get("grade") in ["E", "F"]]

        add_test_result(
            "Hallucination Detection",
            "pSRT Flagging Status",
            "PASS" if flagged_signals or low_grade_signals else "WARN",
            f"Flagged: {len(flagged_signals)}, Low Grade (E/F): {len(low_grade_signals)}",
            {"flagged_count": len(flagged_signals), "low_grade_count": len(low_grade_signals)},
        )
        print(f"📊 pSRT Status: {len(flagged_signals)} flagged, {len(low_grade_signals)} low grade (E/F)")


# ============================================================
# TEST CATEGORY 7: Database Integrity Tests
# ============================================================


def test_database_integrity():
    """Test database integrity and consistency."""
    print("\n" + "=" * 60)
    print("TEST CATEGORY 7: Database Integrity Tests")
    print("=" * 60)

    db_path = BASE_PATH / "signals" / "database.json"
    if not db_path.exists():
        add_test_result("Database Integrity", "Database File Exists", "FAIL", "Database file not found")
        print("❌ FAIL: Database file not found")
        return

    db = load_json_file(db_path)

    # Test: Metadata consistency
    metadata = db.get("metadata", {})
    signals = db.get("signals", [])
    actual_count = len(signals)
    reported_count = metadata.get("total_signals", 0)

    if actual_count == reported_count:
        add_test_result(
            "Database Integrity",
            "Signal Count Metadata Match",
            "PASS",
            f"Metadata reports {reported_count}, actual count {actual_count}",
        )
        print(f"✅ PASS: Database signal count consistent ({actual_count})")
    else:
        add_test_result(
            "Database Integrity",
            "Signal Count Metadata Match",
            "FAIL",
            f"Metadata reports {reported_count}, actual count {actual_count}",
            {"metadata_count": reported_count, "actual_count": actual_count},
        )
        print(f"❌ FAIL: Database count mismatch (metadata: {reported_count}, actual: {actual_count})")

    # Test: Category statistics
    stats = db.get("statistics", {}).get("by_category", {})
    category_counts = {}
    for signal in signals:
        cat = signal.get("category", {}).get("primary", "Unknown")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    mismatches = []
    for cat, count in stats.items():
        if category_counts.get(cat, 0) != count:
            mismatches.append({"category": cat, "reported": count, "actual": category_counts.get(cat, 0)})

    if not mismatches:
        add_test_result(
            "Database Integrity", "Category Statistics Match", "PASS", "All category statistics are accurate"
        )
        print("✅ PASS: Category statistics are accurate")
    else:
        add_test_result(
            "Database Integrity",
            "Category Statistics Match",
            "WARN",
            f"{len(mismatches)} category statistics mismatches",
            mismatches,
        )
        print(f"⚠️ WARN: {len(mismatches)} category statistics mismatches")

    # Test: Unique signal IDs
    signal_ids = [s.get("id") for s in signals]
    duplicate_ids = set([x for x in signal_ids if signal_ids.count(x) > 1])

    if not duplicate_ids:
        add_test_result("Database Integrity", "Unique Signal IDs", "PASS", "All signal IDs are unique")
        print("✅ PASS: All signal IDs are unique")
    else:
        add_test_result(
            "Database Integrity",
            "Unique Signal IDs",
            "FAIL",
            f"{len(duplicate_ids)} duplicate signal IDs found",
            {"duplicates": list(duplicate_ids)},
        )
        print(f"❌ FAIL: {len(duplicate_ids)} duplicate signal IDs found")


# ============================================================
# TEST CATEGORY 8: Source URL Validation Tests
# ============================================================


def test_source_url_validation():
    """Test that all source URLs are valid."""
    print("\n" + "=" * 60)
    print("TEST CATEGORY 8: Source URL Validation Tests")
    print("=" * 60)

    import urllib.parse

    structured_path = BASE_PATH / "structured" / "2026" / "01" / "12" / f"structured-signals-{TEST_DATE}.json"
    if not structured_path.exists():
        add_test_result("URL Validation", "Structured File Exists", "FAIL", "Structured signals file not found")
        print("❌ FAIL: Structured signals file not found")
        return

    structured = load_json_file(structured_path)
    signals = structured.get("signals", [])

    # URL format validation
    invalid_urls = []
    missing_urls = []
    valid_urls = 0

    for signal in signals:
        source = signal.get("source", {})
        url = source.get("url", "")

        if not url:
            missing_urls.append(signal.get("signal_id", "UNKNOWN"))
            continue

        # Basic URL validation
        try:
            parsed = urllib.parse.urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                invalid_urls.append({"signal_id": signal.get("signal_id"), "url": url, "reason": "Invalid URL format"})
            elif parsed.scheme not in ["http", "https"]:
                invalid_urls.append(
                    {"signal_id": signal.get("signal_id"), "url": url, "reason": f"Invalid scheme: {parsed.scheme}"}
                )
            else:
                valid_urls += 1
        except Exception as e:
            invalid_urls.append({"signal_id": signal.get("signal_id"), "url": url, "reason": str(e)})

    # Test: All signals have URLs
    if not missing_urls:
        add_test_result(
            "URL Validation", "All Signals Have URLs", "PASS", f"All {len(signals)} signals have source URLs"
        )
        print(f"✅ PASS: All {len(signals)} signals have source URLs")
    else:
        add_test_result(
            "URL Validation",
            "All Signals Have URLs",
            "WARN",
            f"{len(missing_urls)} signals missing URLs",
            {"missing_count": len(missing_urls), "examples": missing_urls[:5]},
        )
        print(f"⚠️ WARN: {len(missing_urls)} signals missing URLs")

    # Test: All URLs are valid format
    if not invalid_urls:
        add_test_result("URL Validation", "URL Format Valid", "PASS", f"All {valid_urls} URLs have valid format")
        print(f"✅ PASS: All {valid_urls} URLs have valid format")
    else:
        add_test_result(
            "URL Validation", "URL Format Valid", "WARN", f"{len(invalid_urls)} invalid URLs found", invalid_urls[:5]
        )
        print(f"⚠️ WARN: {len(invalid_urls)} invalid URLs found")


# ============================================================
# TEST CATEGORY 9: pSRT Calculation Accuracy Tests
# ============================================================


def test_psrt_calculation_accuracy():
    """Test pSRT score calculation accuracy."""
    print("\n" + "=" * 60)
    print("TEST CATEGORY 9: pSRT Calculation Accuracy Tests")
    print("=" * 60)

    psrt_path = BASE_PATH / "analysis" / "2026" / "01" / "12" / f"pSRT-scores-{TEST_DATE}.json"
    if not psrt_path.exists():
        add_test_result("pSRT Accuracy", "pSRT File Exists", "FAIL", "pSRT scores file not found")
        print("❌ FAIL: pSRT scores file not found")
        return

    psrt = load_json_file(psrt_path)
    scores = psrt.get("pSRT_scores", [])

    # Grade mapping
    grade_ranges = {
        "A+": (90, 100),
        "A": (80, 89),
        "B": (70, 79),
        "C": (60, 69),
        "D": (50, 59),
        "E": (40, 49),
        "F": (0, 39),
    }

    grade_mismatches = []
    score_anomalies = []
    valid_grades = 0

    for score in scores:
        overall = score.get("overall_pSRT", 0)
        grade = score.get("grade", "")
        signal_id = score.get("signal_id", "UNKNOWN")

        # Check grade matches score
        expected_grade = None
        for g, (low, high) in grade_ranges.items():
            if low <= overall <= high:
                expected_grade = g
                break

        if expected_grade and grade != expected_grade:
            grade_mismatches.append(
                {"signal_id": signal_id, "score": overall, "actual_grade": grade, "expected_grade": expected_grade}
            )
        else:
            valid_grades += 1

        # Check for anomalies
        if overall < 0 or overall > 100:
            score_anomalies.append({"signal_id": signal_id, "score": overall, "issue": "Score out of range (0-100)"})

        # Check component scores exist
        components = score.get("component_scores", {})
        if not components:
            score_anomalies.append({"signal_id": signal_id, "issue": "Missing component scores"})

    # Test: Grades match scores
    if not grade_mismatches:
        add_test_result(
            "pSRT Accuracy", "Grade-Score Consistency", "PASS", f"All {valid_grades} grades match their scores"
        )
        print(f"✅ PASS: All {valid_grades} grades match their scores")
    else:
        add_test_result(
            "pSRT Accuracy",
            "Grade-Score Consistency",
            "FAIL",
            f"{len(grade_mismatches)} grade-score mismatches",
            grade_mismatches[:5],
        )
        print(f"❌ FAIL: {len(grade_mismatches)} grade-score mismatches")

    # Test: No score anomalies
    if not score_anomalies:
        add_test_result("pSRT Accuracy", "Score Validity", "PASS", "All scores are within valid range with components")
        print("✅ PASS: All scores are within valid range")
    else:
        add_test_result(
            "pSRT Accuracy",
            "Score Validity",
            "WARN",
            f"{len(score_anomalies)} score anomalies found",
            score_anomalies[:5],
        )
        print(f"⚠️ WARN: {len(score_anomalies)} score anomalies found")

    # Test: Grade distribution is reasonable
    grade_counts = {}
    for score in scores:
        g = score.get("grade", "Unknown")
        grade_counts[g] = grade_counts.get(g, 0) + 1

    # Check if all scores are F (suspicious)
    f_rate = grade_counts.get("F", 0) / len(scores) * 100 if scores else 0
    if f_rate > 50:
        add_test_result(
            "pSRT Accuracy",
            "Grade Distribution",
            "WARN",
            f"High F-grade rate: {f_rate:.1f}% (may indicate scoring issues)",
            {"distribution": grade_counts},
        )
        print(f"⚠️ WARN: High F-grade rate ({f_rate:.1f}%)")
    else:
        add_test_result(
            "pSRT Accuracy",
            "Grade Distribution",
            "PASS",
            "Grade distribution is reasonable",
            {"distribution": grade_counts},
        )
        print("✅ PASS: Grade distribution is reasonable")
        print(f"   ↳ Distribution: {grade_counts}")


# ============================================================
# MAIN EXECUTION
# ============================================================


def main():
    """Run all tests and generate report."""
    print("\n" + "=" * 70)
    print("   ENVIRONMENT SCANNING SYSTEM - TDD TEST SUITE v2.0")
    print(f"   Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Target Data: {TEST_DATE}")
    print("=" * 70)

    # Run all test categories
    test_agent_definitions()
    test_schema_validation()
    test_pipeline_data_flow()
    test_required_fields()
    test_signal_id_consistency()
    test_hallucination_detection()
    test_database_integrity()
    test_source_url_validation()
    test_psrt_calculation_accuracy()

    # Print summary
    print("\n" + "=" * 70)
    print("   TEST SUMMARY")
    print("=" * 70)

    summary = test_results["summary"]
    total = summary["total_tests"]
    passed = summary["passed"]
    failed = summary["failed"]
    warnings = summary["warnings"]

    pass_rate = (passed / total * 100) if total > 0 else 0

    print(f"\n📊 Results: {total} tests executed")
    print(f"   ✅ Passed:   {passed} ({passed / total * 100:.1f}%)" if total > 0 else "   ✅ Passed:   0")
    print(f"   ❌ Failed:   {failed} ({failed / total * 100:.1f}%)" if total > 0 else "   ❌ Failed:   0")
    print(f"   ⚠️  Warnings: {warnings} ({warnings / total * 100:.1f}%)" if total > 0 else "   ⚠️  Warnings: 0")
    print(f"\n   Overall Pass Rate: {pass_rate:.1f}%")

    # Determine overall status
    if failed == 0 and warnings == 0:
        overall_status = "PASS"
        print("\n   🎉 STATUS: ALL TESTS PASSED")
    elif failed == 0:
        overall_status = "PASS_WITH_WARNINGS"
        print("\n   ⚠️ STATUS: PASSED WITH WARNINGS")
    else:
        overall_status = "FAIL"
        print("\n   ❌ STATUS: TESTS FAILED")

    test_results["overall_status"] = overall_status
    test_results["pass_rate"] = pass_rate

    # Save results
    output_path = BASE_PATH / "tests" / f"tdd-test-results-{TEST_DATE}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)

    print(f"\n📁 Results saved to: {output_path}")
    print("=" * 70)

    return test_results


if __name__ == "__main__":
    main()
