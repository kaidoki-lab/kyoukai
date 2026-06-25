from __future__ import annotations

import re
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator


BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR / "database.sql"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class AltarSection:
    section_key: str
    heading: str
    heading_level: int
    position: int
    body: str


class AltarRepository:
    def __init__(self, db_path: Path | str, schema_path: Path | str = SCHEMA_PATH) -> None:
        self.db_path = Path(db_path)
        self.schema_path = Path(schema_path)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def session(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        schema = self.schema_path.read_text(encoding="utf-8")
        with self.session() as connection:
            connection.executescript(schema)

    def replace_document(
        self,
        source_path: str,
        title: str,
        content_hash: str,
        sections: Iterable[AltarSection],
    ) -> int:
        imported_at = utc_now()
        section_list = list(sections)
        with self.session() as connection:
            existing = connection.execute(
                "SELECT id, content_hash FROM altar_documents WHERE source_path = ?",
                (source_path,),
            ).fetchone()
            if existing is not None and existing["content_hash"] == content_hash:
                return 0

            connection.execute(
                """
                INSERT INTO altar_documents (source_path, title, content_hash, imported_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(source_path) DO UPDATE SET
                    title = excluded.title,
                    content_hash = excluded.content_hash,
                    imported_at = excluded.imported_at
                """,
                (source_path, title, content_hash, imported_at),
            )
            document_id = connection.execute(
                "SELECT id FROM altar_documents WHERE source_path = ?",
                (source_path,),
            ).fetchone()["id"]
            connection.execute(
                "DELETE FROM altar_sections WHERE document_id = ?",
                (document_id,),
            )
            connection.executemany(
                """
                INSERT INTO altar_sections (
                    document_id,
                    section_key,
                    heading,
                    heading_level,
                    position,
                    body,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        document_id,
                        section.section_key,
                        section.heading,
                        section.heading_level,
                        section.position,
                        section.body,
                        imported_at,
                        imported_at,
                    )
                    for section in section_list
                ],
            )
        return len(section_list)

    def search(self, query: str, limit: int = 20) -> list[dict[str, object]]:
        terms = re.findall(r"[\w\u3000-\u9fff]+", query, flags=re.UNICODE)
        if not terms:
            return []
        fts_query = " AND ".join(f'"{term}"' for term in terms)
        with self.session() as connection:
            rows = connection.execute(
                """
                SELECT
                    section.id,
                    document.source_path,
                    document.title AS document_title,
                    section.section_key,
                    section.heading,
                    section.heading_level,
                    section.position,
                    section.body,
                    bm25(altar_sections_fts) AS rank
                FROM altar_sections_fts
                JOIN altar_sections AS section
                    ON section.id = altar_sections_fts.rowid
                JOIN altar_documents AS document
                    ON document.id = section.document_id
                WHERE altar_sections_fts MATCH ?
                ORDER BY rank, document.source_path, section.position
                LIMIT ?
                """,
                (fts_query, max(1, min(limit, 100))),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_sections(self, source_path: str | None = None) -> list[dict[str, object]]:
        sql = """
            SELECT
                section.id,
                document.source_path,
                document.title AS document_title,
                section.section_key,
                section.heading,
                section.heading_level,
                section.position,
                section.body,
                section.updated_at
            FROM altar_sections AS section
            JOIN altar_documents AS document ON document.id = section.document_id
        """
        params: tuple[object, ...] = ()
        if source_path is not None:
            sql += " WHERE document.source_path = ?"
            params = (source_path,)
        sql += " ORDER BY document.source_path, section.position"
        with self.session() as connection:
            rows = connection.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def update_section(self, section_id: int, heading: str, body: str) -> bool:
        with self.session() as connection:
            cursor = connection.execute(
                """
                UPDATE altar_sections
                SET heading = ?, body = ?, updated_at = ?
                WHERE id = ?
                """,
                (heading.strip(), body.strip(), utc_now(), section_id),
            )
        return cursor.rowcount == 1

    def stats(self) -> dict[str, int]:
        with self.session() as connection:
            document_count = connection.execute(
                "SELECT COUNT(*) FROM altar_documents"
            ).fetchone()[0]
            section_count = connection.execute(
                "SELECT COUNT(*) FROM altar_sections"
            ).fetchone()[0]
        return {
            "documentCount": int(document_count),
            "sectionCount": int(section_count),
        }
