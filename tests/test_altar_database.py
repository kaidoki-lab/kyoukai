from __future__ import annotations

import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from data_migration import migrate_file, parse_markdown
from schema import AltarRepository


class AltarDatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.db_path = self.root / "test.db"
        self.repository = AltarRepository(self.db_path)
        self.repository.initialize()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_source(self, text: str) -> Path:
        source = self.root / "altar.md"
        source.write_text(text, encoding="utf-8")
        return source

    def test_schema_is_created(self) -> None:
        with closing(sqlite3.connect(self.db_path)) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
                )
            }
        self.assertIn("altar_documents", tables)
        self.assertIn("altar_sections", tables)
        self.assertIn("altar_sections_fts", tables)

    def test_parser_keeps_only_altar_sections_by_default(self) -> None:
        parsed = parse_markdown(
            "# 定義\n\n## 祭壇域\n入口の記録。\n\n## 観測域\n別の記録。"
        )
        self.assertEqual("定義", parsed.title)
        self.assertEqual(["祭壇域"], [section.heading for section in parsed.sections])

    def test_migration_is_searchable_and_idempotent(self) -> None:
        source = self.write_source(
            "# KYOUKAI\n\n## 初見導線\n/ (祭壇域) から観測域へ向かう。\n"
        )
        first_count = migrate_file(self.repository, source, root=self.root)
        second_count = migrate_file(self.repository, source, root=self.root)

        self.assertEqual(1, first_count)
        self.assertEqual(0, second_count)
        results = self.repository.search("祭壇域")
        self.assertEqual(1, len(results))
        self.assertEqual("初見導線", results[0]["heading"])

    def test_changed_document_replaces_stale_sections(self) -> None:
        source = self.write_source(
            "# KYOUKAI\n\n## 旧祭壇域\n古い記録。\n\n## 祭壇域補足\n古い補足。\n"
        )
        migrate_file(self.repository, source, root=self.root)
        source.write_text(
            "# KYOUKAI\n\n## 新祭壇域\n新しい記録。\n",
            encoding="utf-8",
        )
        migrate_file(self.repository, source, root=self.root)

        sections = self.repository.list_sections("altar.md")
        self.assertEqual(1, len(sections))
        self.assertEqual("新祭壇域", sections[0]["heading"])
        self.assertEqual([], self.repository.search("古い"))

    def test_section_can_be_managed_after_migration(self) -> None:
        source = self.write_source("# KYOUKAI\n\n## 祭壇域\n入口の記録。\n")
        migrate_file(self.repository, source, root=self.root)
        section = self.repository.list_sections("altar.md")[0]

        changed = self.repository.update_section(
            int(section["id"]),
            "祭壇域 更新",
            "検索可能な更新記録。",
        )

        self.assertTrue(changed)
        results = self.repository.search("更新記録")
        self.assertEqual(1, len(results))
        self.assertEqual("祭壇域 更新", results[0]["heading"])

    def test_stats_report_document_and_section_counts(self) -> None:
        source = self.write_source("# KYOUKAI\n\n## 祭壇域\n入口の記録。\n")
        migrate_file(self.repository, source, root=self.root)

        self.assertEqual(
            {"documentCount": 1, "sectionCount": 1},
            self.repository.stats(),
        )


if __name__ == "__main__":
    unittest.main()
