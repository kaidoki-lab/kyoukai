from __future__ import annotations

import argparse
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from schema import AltarRepository, AltarSection


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "kyoukai.db"
DEFAULT_SOURCES = (
    BASE_DIR / "central-os" / "graph" / "room-flows.md",
    BASE_DIR / "central-os" / "graph" / "sns-flow.md",
    BASE_DIR / "central-os" / "graph" / "monetization-flow.md",
    BASE_DIR / "central-os" / "schema" / "rooms-schema.md",
    BASE_DIR / "central-os" / "connection" / "route-lock-rules.md",
)
ALTAR_MARKERS = ("祭壇域", "/ (祭壇域)", "`/`")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


@dataclass(frozen=True)
class ParsedMarkdown:
    title: str
    sections: tuple[AltarSection, ...]


def parse_markdown(text: str, include_all: bool = False) -> ParsedMarkdown:
    title = "Untitled"
    raw_sections: list[tuple[str, int, list[str]]] = []
    heading = "Document"
    level = 0
    body: list[str] = []

    def flush() -> None:
        nonlocal body
        content = "\n".join(body).strip()
        if content or heading != "Document":
            raw_sections.append((heading, level, body))
        body = []

    for line in text.splitlines():
        match = HEADING_PATTERN.match(line)
        if match:
            flush()
            level = len(match.group(1))
            heading = match.group(2).strip()
            if title == "Untitled" and level == 1:
                title = heading
        else:
            body.append(line)
    flush()

    sections: list[AltarSection] = []
    for position, (section_heading, section_level, section_lines) in enumerate(raw_sections):
        section_body = "\n".join(section_lines).strip()
        searchable = f"{section_heading}\n{section_body}"
        if not include_all and not any(marker in searchable for marker in ALTAR_MARKERS):
            continue
        key_seed = f"{position}:{section_level}:{section_heading}"
        section_key = hashlib.sha256(key_seed.encode("utf-8")).hexdigest()[:20]
        sections.append(
            AltarSection(
                section_key=section_key,
                heading=section_heading,
                heading_level=section_level,
                position=position,
                body=section_body,
            )
        )
    return ParsedMarkdown(title=title, sections=tuple(sections))


def migrate_file(
    repository: AltarRepository,
    source: Path,
    root: Path = BASE_DIR,
    include_all: bool = False,
) -> int:
    text = source.read_text(encoding="utf-8-sig")
    parsed = parse_markdown(text, include_all=include_all)
    source_path = source.resolve().relative_to(root.resolve()).as_posix()
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return repository.replace_document(
        source_path=source_path,
        title=parsed.title,
        content_hash=content_hash,
        sections=parsed.sections,
    )


def migrate(
    db_path: Path,
    sources: tuple[Path, ...] = DEFAULT_SOURCES,
    include_all: bool = False,
) -> dict[str, int]:
    repository = AltarRepository(db_path)
    repository.initialize()
    results: dict[str, int] = {}
    for source in sources:
        if not source.is_file():
            raise FileNotFoundError(f"Markdown source not found: {source}")
        relative_source = source.resolve().relative_to(BASE_DIR.resolve()).as_posix()
        results[relative_source] = migrate_file(
            repository,
            source,
            include_all=include_all,
        )
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Migrate altar-related Markdown sections into the KYOUKAI database."
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument(
        "--source",
        action="append",
        type=Path,
        help="Markdown source path. Repeat to migrate multiple files.",
    )
    parser.add_argument(
        "--all-sections",
        action="store_true",
        help="Import every section from each source instead of altar-related sections only.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    sources = tuple(path.resolve() for path in args.source) if args.source else DEFAULT_SOURCES
    results = migrate(args.db.resolve(), sources=sources, include_all=args.all_sections)
    imported = sum(results.values())
    for source, count in results.items():
        print(f"{source}: {count} sections imported")
    print(f"Total: {imported} sections imported")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
