#!/usr/bin/env python3
"""
Initialize environmental scanning directory structure and configuration.
Usage: python scripts/init_scanning.py [--reset]
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("env-scanning")

DIRECTORIES = [
    "signals/snapshots",
    "reports/daily",
    "reports/archive",
    "raw",
    "filtered",
    "structured",
    "analysis",
    "context",
    "logs",
    "config",
]


def create_directories():
    """Create all required directories."""
    for dir_path in DIRECTORIES:
        full_path = BASE_DIR / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created {full_path}")


def init_database():
    """Initialize empty signal database."""
    db_path = BASE_DIR / "signals" / "database.json"
    if not db_path.exists():
        db = {
            "metadata": {
                "version": "1.0",
                "created": datetime.now().strftime("%Y-%m-%d"),
                "last_updated": None,
                "total_signals": 0,
            },
            "statistics": {
                "by_status": {"emerging": 0, "developing": 0, "mature": 0, "declining": 0},
                "by_category": {"Social": 0, "Technological": 0, "Economic": 0, "Environmental": 0, "Political": 0},
            },
            "signals": [],
        }
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"  ✓ Created {db_path}")
    else:
        print(f"  • {db_path} already exists (skipped)")


def init_workflow_status():
    """Initialize workflow status file."""
    status_path = BASE_DIR / "logs" / "workflow-status.json"
    if not status_path.exists():
        status = {"last_run": None, "outputs": {}, "stats": {}, "next_scheduled": None}
        with open(status_path, "w", encoding="utf-8") as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
        print(f"  ✓ Created {status_path}")
    else:
        print(f"  • {status_path} already exists (skipped)")


def reset_all():
    """Reset all data (dangerous!)."""
    import shutil

    if BASE_DIR.exists():
        shutil.rmtree(BASE_DIR)
        print(f"  ✓ Removed {BASE_DIR}")


def main():
    parser = argparse.ArgumentParser(description="Initialize environmental scanning system")
    parser.add_argument("--reset", action="store_true", help="Reset all data (dangerous!)")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  Environmental Scanning System Initialization")
    print("=" * 60 + "\n")

    if args.reset:
        confirm = input("⚠️  This will DELETE all existing data. Type 'yes' to confirm: ")
        if confirm.lower() == "yes":
            reset_all()
        else:
            print("  Aborted.")
            return

    print("Creating directories...")
    create_directories()

    print("\nInitializing database...")
    init_database()

    print("\nInitializing workflow status...")
    init_workflow_status()

    print("\n" + "=" * 60)
    print("  ✅ Initialization Complete!")
    print("=" * 60)
    print(f"""
Next steps:
  1. Configure domains: data/config/domains.yaml
  2. Configure sources: data/config/sources.yaml
  3. Run scanning: /run-scan

Directory structure:
  {BASE_DIR}/
  ├── signals/database.json     # Master signal DB
  ├── reports/daily/            # Daily reports
  ├── reports/archive/          # Archived reports
  ├── raw/                      # Raw scan data
  ├── filtered/                 # Deduplicated signals
  ├── structured/               # Classified signals
  ├── analysis/                 # Impact & priority analysis
  ├── context/                  # Context for deduplication
  ├── logs/                     # Execution logs
  └── config/                   # Configuration files
""")


if __name__ == "__main__":
    main()
