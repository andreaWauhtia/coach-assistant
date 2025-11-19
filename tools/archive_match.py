#!/usr/bin/env python3
"""Archive a completed match analysis to completed-tasks/ and clean up working memory."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from subprocess import run
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
MEMORY_BANK_ROOT = REPO_ROOT / ".memory-bank"
COMPLETED_TASKS_ROOT = REPO_ROOT / "completed-tasks" / "competitions" / "match_reports"
INDEX_FILE = COMPLETED_TASKS_ROOT / "INDEX.md"


def verify_match_assets(matchday: str) -> bool:
    """Verify required assets exist using match_memory_guard."""
    cmd = [
        "python",
        str(REPO_ROOT / "tools" / "match_memory_guard.py"),
        "--matchday",
        matchday,
        "--check-assets",
    ]
    result = run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def archive_match(matchday: str, dry_run: bool = False) -> None:
    source_dir = MEMORY_BANK_ROOT / "competitions" / "analysis" / matchday
    dest_dir = COMPLETED_TASKS_ROOT / matchday

    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory {source_dir} does not exist.")

    if not verify_match_assets(matchday):
        raise RuntimeError(f"Asset verification failed for {matchday}.")

    if dry_run:
        print(f"Dry run: Would copy {source_dir} to {dest_dir}")
        print(f"Dry run: Would update {INDEX_FILE}")
        print(f"Dry run: Would remove {source_dir}")
        return

    # Copy directory
    shutil.copytree(source_dir, dest_dir)
    print(f"Copied {source_dir} to {dest_dir}")

    # Update INDEX.md
    with INDEX_FILE.open("a") as f:
        f.write(f"| {matchday} | Archived | Completed analysis archived |\n")
    print(f"Updated {INDEX_FILE}")

    # Remove source
    shutil.rmtree(source_dir)
    print(f"Removed {source_dir}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Archive a completed match analysis from .memory-bank/ to completed-tasks/, "
            "update the index, and clean up working memory."
        )
    )
    parser.add_argument(
        "matchday",
        help="Matchday in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without making changes.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        archive_match(args.matchday, args.dry_run)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())