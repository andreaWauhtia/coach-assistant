"""Unit tests for match_memory_guard utility."""
from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from tools import match_memory_guard as mmg


class MatchMemoryGuardTests(unittest.TestCase):
    def test_guard_reports_missing_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)

            ok, missing, match_dir = mmg.guard(
                matchday="2025-11-07",
                base_dir=base_dir,
                check_assets=True,
            )

            self.assertFalse(ok)
            self.assertEqual(match_dir, base_dir / "2025-11-07")
            self.assertIn("match_2025-11-07.json", missing)
            self.assertIn("2025-11-07.md", missing)
            self.assertTrue(
                any(entry.startswith("raw/") for entry in missing),
                msg="raw directory should be reported when empty",
            )

    def test_guard_passes_when_assets_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            match_dir = base_dir / "2025-11-14"
            mmg.ensure_structure(match_dir)

            (match_dir / "match_2025-11-14.json").write_text("{}", encoding="utf-8")
            (match_dir / "2025-11-14.md").write_text("notes", encoding="utf-8")
            raw_image = match_dir / "raw" / "timeline-1.jpg"
            raw_image.write_text("binary", encoding="utf-8")

            ok, missing, _ = mmg.guard(
                matchday="2025-11-14",
                base_dir=base_dir,
                check_assets=True,
            )

            self.assertTrue(ok)
            self.assertEqual(list(missing), [])


if __name__ == "__main__":
    unittest.main()
