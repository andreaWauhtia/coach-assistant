#!/usr/bin/env python3
"""Validate the structure of rapport_analyse_complete.md files."""
from __future__ import annotations

import argparse
import difflib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = REPO_ROOT / "templates" / "rapport_analyse_complete.md"


@dataclass(frozen=True)
class StructureToken:
    """Represents a structural element (heading or table header)."""

    kind: str
    value: str

    def to_line(self) -> str:
        return f"{self.kind.upper()}|{self.value}"


def normalize_heading(line: str) -> str:
    return " ".join(line.strip().split())


def normalize_table_header(line: str) -> str:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return " | ".join(cells)


def is_table_separator(line: str) -> bool:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return False

    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    return all(cell and set(cell) <= {"-", ":"} for cell in cells)


def extract_structure(text: str) -> list[StructureToken]:
    tokens: list[StructureToken] = []
    lines = text.splitlines()
    total_lines = len(lines)
    index = 0

    while index < total_lines:
        current = lines[index]
        stripped = current.strip()
        if not stripped:
            index += 1
            continue

        if stripped.startswith("#"):
            tokens.append(StructureToken("heading", normalize_heading(stripped)))
            index += 1
            continue

        next_line = lines[index + 1] if (index + 1) < total_lines else ""
        if stripped.startswith("|") and stripped.endswith("|") and is_table_separator(next_line):
            tokens.append(StructureToken("table", normalize_table_header(stripped)))
            index += 2
            continue

        index += 1

    return tokens


def load_tokens(path: Path) -> list[StructureToken]:
    contents = path.read_text(encoding="utf-8")
    return extract_structure(contents)


def diff_tokens(expected: Iterable[str], actual: Iterable[str]) -> str:
    diff = difflib.unified_diff(
        list(expected),
        list(actual),
        fromfile="template",
        tofile="report",
        lineterm="",
    )
    return "\n".join(diff)


import re

def extract_team_names(report_text: str):
    # Extrait les noms d'équipes et le score depuis le rapport
    # Titre principal : # Rapport d'analyse : USAO U8 VS Bouillon
    m = re.search(r"# Rapport d'analyse : ([^V]+)VS ([^\n]+)", report_text)
    if m:
        team_home = m.group(1).strip()
        team_away = m.group(2).strip()
    else:
        team_home = team_away = None
    # Score : **Score** : 16-3
    m2 = re.search(r"\*\*Score\*\* *: *([0-9]+)[-–]([0-9]+)", report_text)
    if m2:
        score_home, score_away = m2.group(1), m2.group(2)
    else:
        score_home = score_away = None
    return team_home, team_away, score_home, score_away

def normalize_dynamic(line: str, team_home, team_away, team_name=None):
    # Remplace les valeurs réelles par les placeholders du template
    # Pour la section Métriques Offensives, le template peut utiliser [TEAM_NAME] ou [TEAM_HOME]
    # On harmonise les deux pour la validation
    if team_name:
        # Remplace d'abord le nom réel par [TEAM_NAME]
        line = line.replace(team_name, '[TEAM_NAME]')
    if team_home:
        line = line.replace(team_home, '[TEAM_HOME]')
    if team_away:
        line = line.replace(team_away, '[TEAM_AWAY]')
    # Si le template utilise [TEAM_NAME] ou [TEAM_HOME] de façon interchangeable, on harmonise
    line = line.replace('[TEAM_NAME]', '[TEAM_HOME]')
    return line

def validate_report(report_path: Path, template_path: Path = DEFAULT_TEMPLATE) -> tuple[bool, str]:
    template_tokens = load_tokens(template_path)
    report_text = report_path.read_text(encoding="utf-8")
    report_tokens = extract_structure(report_text)

    team_home, team_away, _, _ = extract_team_names(report_text)
    # Pour la section Métriques Offensives, on cherche le nom de l'équipe dans le titre
    team_name = team_home

    expected_lines = [token.to_line() for token in template_tokens]
    actual_lines = [token.to_line() for token in report_tokens]

    # Normalisation dynamique : remplace les noms réels par les placeholders
    actual_lines_norm = []
    for l in actual_lines:
        l_norm = normalize_dynamic(l, team_home, team_away, team_name)
        actual_lines_norm.append(l_norm)

    if expected_lines == actual_lines_norm:
        return True, (
            "Template compliance confirmed (dynamic headings allowed): "
            f"{len(actual_lines)} structural elements (headings + tables)."
        )

    diff = diff_tokens(expected_lines, actual_lines_norm)
    if not diff:
        diff = "Report deviates from template but no diff could be generated."

    return False, diff


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate rapport_analyse_complete.md files before archiving "
            "by comparing headings and table headers to the canonical template."
        )
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Path to the report Markdown file that should be validated.",
    )
    parser.add_argument(
        "--template",
        default=str(DEFAULT_TEMPLATE),
        help="Path to the canonical template (defaults to templates/rapport_analyse_complete.md).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    report_path = Path(args.report)
    template_path = Path(args.template)

    ok, details = validate_report(report_path, template_path)
    if ok:
        print(f"✅ {details}")
        return 0

    print("❌ Template mismatch detected:\n" + details)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
