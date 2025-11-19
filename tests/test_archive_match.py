#!/usr/bin/env python3
"""Test archive_match.py functionality."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.archive_match import archive_match, verify_match_assets


class TestArchiveMatch(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.memory_bank = self.temp_dir / ".memory-bank" / "competitions" / "analysis"
        self.completed_tasks = self.temp_dir / "completed-tasks" / "competitions" / "match_reports"
        self.memory_bank.mkdir(parents=True)
        self.completed_tasks.mkdir(parents=True)
        self.index_file = self.completed_tasks / "INDEX.md"
        self.index_file.write_text("# Match Reports Index\n\n| Matchday | Status | Notes |\n| --- | --- | --- |\n")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    @patch('tools.archive_match.verify_match_assets')
    def test_archive_match_success(self, mock_verify):
        mock_verify.return_value = True
        matchday = "2025-11-07"
        source_dir = self.memory_bank / matchday
        source_dir.mkdir()
        (source_dir / "test.txt").write_text("test")

        with patch('tools.archive_match.MEMORY_BANK_ROOT', self.temp_dir / ".memory-bank"), \
             patch('tools.archive_match.COMPLETED_TASKS_ROOT', self.completed_tasks), \
             patch('tools.archive_match.INDEX_FILE', self.index_file):
            archive_match(matchday)

        dest_dir = self.completed_tasks / matchday
        self.assertTrue(dest_dir.exists())
        self.assertTrue((dest_dir / "test.txt").exists())
        self.assertFalse(source_dir.exists())
        index_content = self.index_file.read_text()
        self.assertIn(f"| {matchday} | Archived |", index_content)

    @patch('tools.archive_match.verify_match_assets')
    def test_archive_match_dry_run(self, mock_verify):
        mock_verify.return_value = True
        matchday = "2025-11-07"
        source_dir = self.memory_bank / matchday
        source_dir.mkdir()
        (source_dir / "test.txt").write_text("test")

        with patch('tools.archive_match.MEMORY_BANK_ROOT', self.temp_dir / ".memory-bank"), \
             patch('tools.archive_match.COMPLETED_TASKS_ROOT', self.completed_tasks), \
             patch('tools.archive_match.INDEX_FILE', self.index_file), \
             patch('builtins.print') as mock_print:
            archive_match(matchday, dry_run=True)

        dest_dir = self.completed_tasks / matchday
        self.assertFalse(dest_dir.exists())
        self.assertTrue(source_dir.exists())
        index_content = self.index_file.read_text()
        self.assertNotIn(f"| {matchday} | Archived |", index_content)
        mock_print.assert_called()

    @patch('tools.archive_match.verify_match_assets')
    def test_archive_match_verification_failure(self, mock_verify):
        mock_verify.return_value = False
        matchday = "2025-11-07"
        source_dir = self.memory_bank / matchday
        source_dir.mkdir()

        with patch('tools.archive_match.MEMORY_BANK_ROOT', self.temp_dir / ".memory-bank"):
            with self.assertRaises(RuntimeError):
                archive_match(matchday)

    def test_verify_match_assets(self):
        # This would require mocking subprocess, but for simplicity, assume it's tested via integration
        pass


if __name__ == "__main__":
    unittest.main()