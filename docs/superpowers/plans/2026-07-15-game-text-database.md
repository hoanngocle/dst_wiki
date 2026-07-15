# Game-Facing Text Database Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist all non-dialogue Tu Tiên UI and notification text in the generated SQLite database with source provenance.

**Architecture:** Extract game text once into typed source/row data, reuse it for Markdown, and pass it into the existing atomic SQLite writer. The database writer merges collector sources with the normalized catalog sources before inserting `game_text` rows.

**Tech Stack:** Python 3.9 standard library, SQLite, `unittest`.

## Global Constraints

- Do not parse Markdown as a database input.
- Exclude `scripts/speech_*.lua` and non-UTF-8 Lua bytecode.
- Preserve every `STRINGS.*` key, value and original line locator.
- Keep `PRAGMA foreign_key_check` clean and database output deterministic.

---

### Task 1: Collect game text as provenance-aware data

**Files:**
- Modify: `tools/extract/export_mod_markdown.py`
- Modify: `tests/extract/test_export_mod_markdown.py`

**Interfaces:**
- Produces `collect_game_text(mod_roots) -> (sources, rows)` where each row has
  `text_id`, `text_key`, `value_vi`, `source_id`, and `locator`.

- [ ] Write a failing test asserting one `STRINGS` row references a source with
  hash/path and has `locator == "line:1"`.
- [ ] Implement the collector by reusing the existing parser and source-file
  filtering; use stable SHA-256 identifiers.
- [ ] Re-run the focused exporter tests.

### Task 2: Persist the text table during database rebuild

**Files:**
- Modify: `tools/extract/database.py`
- Modify: `tools/extract/cli.py`
- Modify: `tests/extract/test_database.py`

**Interfaces:**
- Extends `write_database(path, catalog, game_text_sources=(), game_text_rows=())`.
- Adds `game_text(text_id, text_key, value_vi, source_id, locator)`.

- [ ] Write a failing database test that supplies one source/row, reads it
  after `write_database`, and checks the FK with `PRAGMA foreign_key_check`.
- [ ] Add schema, source merge validation and deterministic inserts; call the
  collector from `_build_db_stage`.
- [ ] Re-run database and exporter tests.

### Task 3: Rebuild and verify the real SQLite artifact

**Files:**
- Modify: `data/generated/wiki.sqlite`

- [ ] Run `python3 -m tools.extract.cli build-db`.
- [ ] Query the exact `game_text` count, assert no speech locator and run
  `PRAGMA foreign_key_check`.
- [ ] Run all extractor tests and rebuild a second time to compare SQLite
  checksums.
