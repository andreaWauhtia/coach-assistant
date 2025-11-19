#!/usr/bin/env python3
"""Utility to provision and validate match analysis folders."""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence

DEFAULT_BASE_DIR = Path(".memory-bank") / "competitions" / "analysis"
REQUIRED_FILES = ("match_{matchday}.json", "{matchday}.md")


def matchday_type(value: str) -> str:
    """Ensure the provided matchday follows YYYY-MM-DD."""
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:  # pragma: no cover - argparse surfaces message
        raise argparse.ArgumentTypeError(
            "matchday must use YYYY-MM-DD"
        ) from exc
    return value


def ensure_structure(match_dir: Path) -> None:
    """Create the match directory and core subfolders if they do not exist."""
    match_dir.mkdir(parents=True, exist_ok=True)


def find_missing_assets(match_dir: Path, matchday: str) -> list[str]:
    """Return a list describing any required asset that is missing."""
    missing: list[str] = []
    expected_files = [pattern.format(matchday=matchday) for pattern in REQUIRED_FILES]
    for filename in expected_files:
        if not (match_dir / filename).is_file():
            missing.append(filename)

    return missing


def guard(matchday: str, base_dir: Path = DEFAULT_BASE_DIR, check_assets: bool = False) -> tuple[bool, Sequence[str], Path]:
    """Ensure folder structure exists and optionally validate asset presence."""
    resolved_base = Path(base_dir)
    match_dir = resolved_base / matchday
    ensure_structure(match_dir)

    if not check_assets:
        return True, (), match_dir

    missing = find_missing_assets(match_dir, matchday)
    return (not missing), missing, match_dir


def format_missing_entries(entries: Iterable[str]) -> str:
    return "\n".join(f"  - {entry}" for entry in entries)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Provision and validate .memory-bank/competitions/analysis/{matchday}/ "
            "folders before running performance agent workflows."
        )
    )
    parser.add_argument(
        "--matchday",
        required=True,
        type=matchday_type,
        help="Match date in YYYY-MM-DD format; becomes the folder name.",
    )
    parser.add_argument(
        "--base-dir",
        default=str(DEFAULT_BASE_DIR),
        help="Root directory that stores per-match analysis folders.",
    )
    parser.add_argument(
        "--check-assets",
        action="store_true",
        help="Validate that required JSON/Markdown files and raw images exist.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    ok, missing, match_dir = guard(
        matchday=args.matchday,
        base_dir=Path(args.base_dir),
        check_assets=args.check_assets,
    )

    if ok and not args.check_assets:
        print(f"📁 Ensured analysis folder at {match_dir}")
        return 0

    if ok:
        print(f"✅ All required assets present for matchday {args.matchday}.")
        return 0

    print(
        "❌ Missing assets for matchday "
        f"{args.matchday} under {match_dir}:\n" + format_missing_entries(missing)
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
