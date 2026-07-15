# Tu Tiên Game-Facing Text Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate deterministic Markdown reference files for all non-dialogue, game-facing Tu Tiên text and the runtime crafting formulas.

**Architecture:** A focused Python exporter reads the committed normalized catalog plus local runtime/source snapshots. It resolves player-facing names, renders formulas and conditions, and writes three Markdown files atomically under `docs/mod-text/`.

**Tech Stack:** Python 3.9 standard library, `unittest`, existing JSON extraction outputs.

## Global Constraints

- Do not modify any source under `mod/`.
- Exclude `scripts/speech_*.lua` from this export.
- Treat `data/raw/runtime.json` as the sole authority for mod recipe contents.
- Retain prefab IDs and source locators beside translated text.
- Keep output deterministic and UTF-8 encoded.

---

### Task 1: Test the Markdown rendering contract

**Files:**
- Create: `tests/extract/test_export_mod_markdown.py`
- Create: `tools/extract/export_mod_markdown.py`

**Interfaces:**
- Produces `render_recipe_markdown(catalog, runtime)` and
  `extract_strings(paths)`.

- [ ] **Step 1:** Add fixture catalog/runtime data and assertions for a formula
  rendered as `2 × Vàng + 1 × Linh Thạch → 3 × Kiếm Thử`, a health/sanity
  condition, builder fallback, and a nested `STRINGS` table entry.
- [ ] **Step 2:** Run `python3 -m unittest tests.extract.test_export_mod_markdown -v`
  and confirm it fails because the module is absent.
- [ ] **Step 3:** Implement only the renderer/parser required for those
  assertions; preserve source line numbers and sort output deterministically.
- [ ] **Step 4:** Re-run the test and confirm it passes.

### Task 2: Add the public export entry point

**Files:**
- Modify: `tools/extract/export_mod_markdown.py`
- Modify: `tools/extract/cli.py`
- Modify: `tests/extract/test_export_mod_markdown.py`

**Interfaces:**
- Produces `export_mod_markdown(catalog_path, runtime_path, mod_roots, output_dir)`.
- Adds `python3 -m tools.extract.cli export-markdown`.

- [ ] **Step 1:** Add a failing integration test that writes fixture JSON/Lua
  files into a temporary directory, exports the three files, and compares a
  second run byte-for-byte.
- [ ] **Step 2:** Run that test and confirm failure because the export entry
  point is missing.
- [ ] **Step 3:** Implement atomic writes for `README.md`,
  `crafting-recipes.md`, and `game-text.md`; include source/version counts and
  exclude speech paths.
- [ ] **Step 4:** Wire the CLI command with defaults for the existing catalog,
  runtime snapshot, mod roots and `docs/mod-text/`.
- [ ] **Step 5:** Run the focused test module and confirm all cases pass.

### Task 3: Generate and verify the real reference

**Files:**
- Create: `docs/mod-text/README.md`
- Create: `docs/mod-text/crafting-recipes.md`
- Create: `docs/mod-text/game-text.md`

- [ ] **Step 1:** Run `python3 -m tools.extract.cli export-markdown`.
- [ ] **Step 2:** Assert `crafting-recipes.md` has 112 recipe headings,
  `game-text.md` has no `speech_` locator, and every output is UTF-8.
- [ ] **Step 3:** Run `python3 -m unittest tests.extract.test_export_mod_markdown -v`
  and `python3 -m tools.extract.cli export-markdown`, then compare output
  checksums from both runs.
