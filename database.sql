PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS altar_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_path TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    imported_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS altar_sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    section_key TEXT NOT NULL,
    heading TEXT NOT NULL,
    heading_level INTEGER NOT NULL CHECK (heading_level BETWEEN 0 AND 6),
    position INTEGER NOT NULL CHECK (position >= 0),
    body TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES altar_documents(id) ON DELETE CASCADE,
    UNIQUE (document_id, section_key)
);

CREATE INDEX IF NOT EXISTS idx_altar_sections_document_position
    ON altar_sections(document_id, position);

CREATE VIRTUAL TABLE IF NOT EXISTS altar_sections_fts USING fts5(
    heading,
    body,
    content='altar_sections',
    content_rowid='id',
    tokenize='trigram'
);

CREATE TRIGGER IF NOT EXISTS altar_sections_after_insert
AFTER INSERT ON altar_sections
BEGIN
    INSERT INTO altar_sections_fts(rowid, heading, body)
    VALUES (new.id, new.heading, new.body);
END;

CREATE TRIGGER IF NOT EXISTS altar_sections_after_delete
AFTER DELETE ON altar_sections
BEGIN
    INSERT INTO altar_sections_fts(altar_sections_fts, rowid, heading, body)
    VALUES ('delete', old.id, old.heading, old.body);
END;

CREATE TRIGGER IF NOT EXISTS altar_sections_after_update
AFTER UPDATE ON altar_sections
BEGIN
    INSERT INTO altar_sections_fts(altar_sections_fts, rowid, heading, body)
    VALUES ('delete', old.id, old.heading, old.body);
    INSERT INTO altar_sections_fts(rowid, heading, body)
    VALUES (new.id, new.heading, new.body);
END;
