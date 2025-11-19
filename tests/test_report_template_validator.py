"""Tests for the report template validator utility."""
from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from tools import report_template_validator as rtv

TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "templates" / "rapport_analyse_complete.md"


class ReportTemplateValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.template_text = TEMPLATE_PATH.read_text(encoding="utf-8")

    def test_accepts_matching_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "rapport.md"
            custom_text = self.template_text.replace("_Score_", "2-1")
            report_path.write_text(custom_text, encoding="utf-8")

            ok, details = rtv.validate_report(report_path, TEMPLATE_PATH)

            self.assertTrue(ok)
            self.assertIn("structural elements", details)

    def test_rejects_when_heading_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "rapport.md"
            invalid_text = self.template_text.replace(
                "## Résumé du Match",
                "## Résumé Étendu",
            )
            report_path.write_text(invalid_text, encoding="utf-8")

            ok, diff = rtv.validate_report(report_path, TEMPLATE_PATH)

            self.assertFalse(ok)
            self.assertIn("Résumé du Match", diff)
            self.assertIn("Résumé Étendu", diff)

    def test_rejects_when_table_header_reordered(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "rapport.md"
            invalid_text = self.template_text.replace(
                "| Joueur | Note | Commentaire principal |",
                "| Joueur | Commentaire principal | Note |",
            )
            report_path.write_text(invalid_text, encoding="utf-8")

            ok, diff = rtv.validate_report(report_path, TEMPLATE_PATH)

            self.assertFalse(ok)
            self.assertIn("Joueur", diff)
            self.assertIn("Commentaire principal", diff)


if __name__ == "__main__":
    unittest.main()
