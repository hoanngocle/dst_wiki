# Durable Category Crawler State Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist live Category crawler registry/cache in the Git common directory, repair stale `Done` rows explicitly, and crawl the nine reviewed DST Category sources without duplicate detail fetches.

**Architecture:** A focused `state_paths` module resolves the repository-shared operational root while `UrlRegistry` remains path-injected and gains audit/init/repair/snapshot operations. A separate state CLI manages operational lifecycle; the existing crawler CLI consumes the resolved live paths. Category configs remain reviewable data with exact count/exclusion guards.

**Tech Stack:** Python 3 standard library (`argparse`, `dataclasses`, `fcntl`, `hashlib`, `json`, `pathlib`, `subprocess`, `tempfile`, `unittest`), existing MediaWiki crawler, Git worktrees.

## Global Constraints

- Live state root is `<git-common-dir>/category-crawler/`; no `$HOME`, temporary or external fallback.
- Live statuses remain exactly `New`, `Doing`, `Done`; `Doing` is never auto-requeued.
- A `Done` row is reusable only when its artifact exists, checksum matches and JSON is an object.
- Snapshot files are review artifacts, never the live lock/state source.
- Raw Fandom payloads remain untracked and undeployed.
- Category discovery is namespace 0 only and never recursive.
- Only DST pages are registered; reviewed non-DST and overview pages are excluded before detail fetch.
- Explicit path injection remains supported for tests and operators.

---

### Task 1: Resolve durable Git-common state paths

**Files:**
- Create: `tools/crawl_wiki/state_paths.py`
- Create: `tests/crawl_wiki/test_state_paths.py`

**Interfaces:**
- Produces: `CategoryStatePaths(registry: Path, cache: Path)`.
- Produces: `resolve_category_state_paths(cwd: Path, registry: Optional[Path] = None, cache: Optional[Path] = None, runner: Callable = subprocess.run) -> CategoryStatePaths`.
- Consumed by: crawler CLI and state CLI in later tasks.

- [x] **Step 1: Write failing resolver tests**

```python
class StatePathTests(unittest.TestCase):
    def test_resolves_git_common_directory_for_linked_worktree(self):
        with tempfile.TemporaryDirectory() as tempdir:
            common = Path(tempdir) / ".git"
            common.mkdir()
            completed = subprocess.CompletedProcess(
                ["git"], 0, stdout="{}\n".format(common), stderr=""
            )
            paths = resolve_category_state_paths(
                Path(tempdir), runner=mock.Mock(return_value=completed)
            )
            self.assertEqual(
                paths.registry,
                common / "category-crawler/fandom-url-registry.json",
            )
            self.assertEqual(
                paths.cache,
                common / "category-crawler/shared-pages",
            )

    def test_requires_both_explicit_paths(self):
        with self.assertRaisesRegex(StatePathError, "together"):
            resolve_category_state_paths(Path.cwd(), registry=Path("one.json"))
```

- [x] **Step 2: Run resolver tests and verify RED**

Run: `python3 -m unittest tests.crawl_wiki.test_state_paths -v`

Expected: FAIL because `tools.crawl_wiki.state_paths` does not exist.

- [x] **Step 3: Implement resolver**

```python
@dataclass(frozen=True)
class CategoryStatePaths:
    registry: Path
    cache: Path


def resolve_category_state_paths(cwd, registry=None, cache=None, runner=subprocess.run):
    if (registry is None) != (cache is None):
        raise StatePathError("registry and cache overrides must be provided together")
    if registry is not None:
        return CategoryStatePaths(Path(registry), Path(cache))
    result = runner(
        ["git", "rev-parse", "--git-common-dir"],
        cwd=str(Path(cwd)), check=False, capture_output=True, text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise StatePathError("cannot resolve Git common directory")
    common = Path(result.stdout.strip())
    if not common.is_absolute():
        common = (Path(cwd) / common).resolve()
    if not common.is_dir():
        raise StatePathError("Git common directory does not exist")
    root = common / "category-crawler"
    return CategoryStatePaths(root / "fandom-url-registry.json", root / "shared-pages")
```

- [x] **Step 4: Run resolver tests and verify GREEN**

Run: `python3 -m unittest tests.crawl_wiki.test_state_paths -v`

Expected: all resolver tests pass.

- [x] **Step 5: Commit Task 1**

```bash
git add tools/crawl_wiki/state_paths.py tests/crawl_wiki/test_state_paths.py docs/superpowers/plans/2026-07-21-durable-category-crawler-state.md
git commit -m "feat: resolve shared category crawler state"
```

### Task 2: Audit, initialize, repair and snapshot the registry

**Files:**
- Modify: `tools/crawl_wiki/url_registry.py`
- Modify: `tests/crawl_wiki/test_url_registry.py`

**Interfaces:**
- Consumes: existing `UrlRecord`, `_read`, `_write`, `_atomic_json` and explicit registry/cache paths.
- Produces: `RegistryAudit(url: str, status: str, issue: Optional[str])`.
- Produces: `audit() -> Tuple[RegistryAudit, ...]`.
- Produces: `initialize_from_snapshot(snapshot: Path) -> int`.
- Produces: `repair_invalid_done() -> Tuple[UrlRecord, ...]`.
- Produces: `export_snapshot(target: Path) -> int`.

- [x] **Step 1: Add failing registry lifecycle tests**

```python
def test_audit_and_repair_missing_done_artifact(self):
    with tempfile.TemporaryDirectory() as tempdir:
        registry = self.make_registry(Path(tempdir))
        claim = registry.claim(URL, "animals", "worker")
        completed = registry.complete(claim, {"page": {"title": "Beefalo"}})
        (registry.path.parent / completed.artifact_path).unlink()
        audit = registry.audit()
        self.assertEqual(audit[0].issue, "missing")
        repaired = registry.repair_invalid_done()
        self.assertEqual(repaired[0].status, "New")
        self.assertEqual(repaired[0].categories, ("animals",))
        self.assertEqual(repaired[0].attempts, 1)

def test_initialize_snapshot_imports_rows_as_new(self):
    snapshot = make_done_snapshot(root / "snapshot.json")
    count = registry.initialize_from_snapshot(snapshot)
    imported = json.loads(registry.path.read_text())["items"][0]
    self.assertEqual(count, 1)
    self.assertEqual(imported["status"], "New")
    self.assertIsNone(imported["artifactPath"])
```

Also cover checksum mismatch, invalid JSON/object, refusal to initialize over an existing live registry, `Doing` preservation during repair, and stable snapshot export.

- [x] **Step 2: Run registry tests and verify RED**

Run: `python3 -m unittest tests.crawl_wiki.test_url_registry -v`

Expected: FAIL because lifecycle methods do not exist.

- [x] **Step 3: Implement audit and lifecycle operations**

```python
@dataclass(frozen=True)
class RegistryAudit:
    url: str
    status: str
    issue: Optional[str]


def audit(self):
    with self._locked():
        payload = self._read()
        return tuple(self._audit_row(row) for row in payload["items"])


def repair_invalid_done(self):
    with self._locked():
        payload = self._read()
        repaired = []
        for row in payload["items"]:
            audit = self._audit_row(row)
            if row["status"] == "Done" and audit.issue is not None:
                row.update({
                    "status": "New", "workerId": None,
                    "claimedAt": None, "completedAt": None,
                    "artifactPath": None, "artifactSha256": None,
                    "updatedAt": self.clock(),
                    "lastError": "requeued invalid Done: {}".format(audit.issue),
                })
                repaired.append(self._to_record(row))
        self._write(payload)
        return tuple(repaired)
```

Initialization must validate the snapshot schema/rows, preserve URL/categories/attempts/createdAt, set every imported row to `New`, clear owner/timestamps/artifact metadata and never overwrite an existing live registry. Snapshot export must copy the live payload atomically without rewriting statuses.

- [x] **Step 4: Run registry tests and verify GREEN**

Run: `python3 -m unittest tests.crawl_wiki.test_url_registry -v`

Expected: all registry tests pass.

- [x] **Step 5: Commit Task 2**

```bash
git add tools/crawl_wiki/url_registry.py tests/crawl_wiki/test_url_registry.py docs/superpowers/plans/2026-07-21-durable-category-crawler-state.md
git commit -m "feat: audit category crawler registry state"
```

### Task 3: Add the state CLI and integrate durable paths into crawling

**Files:**
- Create: `tools/crawl_wiki/state_cli.py`
- Create: `tests/crawl_wiki/test_state_cli.py`
- Modify: `tools/crawl_wiki/cli.py`
- Modify: `tests/crawl_wiki/test_cli.py`

**Interfaces:**
- Consumes: `resolve_category_state_paths`, `UrlRegistry` lifecycle methods.
- Produces commands: `init`, `audit`, `repair`, `snapshot`.
- Existing category crawler defaults to common live paths; explicit `--url-registry` and `--shared-page-cache` remain paired overrides.

- [x] **Step 1: Write failing CLI tests**

```python
def test_category_crawl_uses_git_common_state_by_default(self):
    args = build_parser().parse_args(["--profile", "category", "--category", "animals"])
    with patch("tools.crawl_wiki.cli.resolve_category_state_paths") as resolve:
        resolve.return_value = CategoryStatePaths(Path("live.json"), Path("cache"))
        with patch("tools.crawl_wiki.cli.UrlRegistry") as registry:
            run_category_with_mocked_client_and_storage(args)
        registry.assert_called_once_with(Path("live.json"), Path("cache"), ORIGIN)

def test_state_cli_repairs_and_snapshots(self):
    with patch("tools.crawl_wiki.state_cli.UrlRegistry") as registry:
        registry.return_value.repair_invalid_done.return_value = (record(),)
        self.assertEqual(main(["repair", "--snapshot", str(snapshot)]), 0)
        registry.return_value.export_snapshot.assert_called_once_with(snapshot)
```

Also assert one-path-only overrides fail, audit returns nonzero for invalid rows, and fatal errors map to exit code 2.

- [x] **Step 2: Run CLI tests and verify RED**

Run: `python3 -m unittest tests.crawl_wiki.test_state_cli tests.crawl_wiki.test_cli -v`

Expected: FAIL because state CLI and resolver integration do not exist.

- [x] **Step 3: Implement state CLI and crawler integration**

`state_cli.py` must parse exactly one command, resolve live paths, construct
`UrlRegistry`, print deterministic counts and export the tracked snapshot after
`init` or `repair`. `audit` is read-only. `snapshot` only exports.

In `cli.py`, change registry/cache option defaults to `None`, resolve the paired
override only for `category` profile, and pass resolved paths to `UrlRegistry`.
Reject registry/cache flags for non-category profiles. Before discovery or any
network detail fetch, category crawling must call `audit()` and hard-fail when
any `Done` row is invalid; it must never auto-repair live state.

- [x] **Step 4: Run CLI tests and verify GREEN**

Run: `python3 -m unittest tests.crawl_wiki.test_state_cli tests.crawl_wiki.test_cli -v`

Expected: all state/crawler CLI tests pass.

- [x] **Step 5: Commit Task 3**

```bash
git add tools/crawl_wiki/state_cli.py tools/crawl_wiki/cli.py tests/crawl_wiki/test_state_cli.py tests/crawl_wiki/test_cli.py docs/superpowers/plans/2026-07-21-durable-category-crawler-state.md
git commit -m "feat: operate durable category crawler state"
```

### Task 4: Add reviewed batch configs and overview exclusions

**Files:**
- Modify: `tools/crawl_wiki/category_config.py`
- Modify: `tests/crawl_wiki/test_category_config.py`
- Create: `data/config/wiki-categories/armour_filter.json`
- Create: `data/config/wiki-categories/beefalo_foods.json`
- Create: `data/config/wiki-categories/boss_dropped_items.json`
- Create: `data/config/wiki-categories/backpacks.json`
- Create: `data/config/wiki-categories/clothing_filter.json`
- Create: `data/config/wiki-categories/cave_creatures.json`
- Create: `data/config/wiki-categories/celestial_filter.json`
- Create: `data/config/wiki-categories/celestial_tab.json`
- Create: `data/config/wiki-categories/containers.json`
- Modify: `docs/category-crawler-control.md`

**Interfaces:**
- Consumes: schema-version-1 Category config loader and exact live discovery counts.
- Produces: nine configs with exact `expectedDirectPages`, `expectedPublishedPages`, tags and reviewed exclusions.

- [x] **Step 1: Write failing config tests**

```python
def test_loads_reviewed_batch_configs(self):
    expected = {
        "armour_filter": (19, 19), "beefalo_foods": (5, 5),
        "boss_dropped_items": (75, 63), "backpacks": (10, 6),
        "clothing_filter": (10, 10), "cave_creatures": (32, 29),
        "celestial_filter": (6, 6), "celestial_tab": (6, 6),
        "containers": (28, 15),
    }
    for key, counts in expected.items():
        config = load_category_config(key)
        self.assertEqual(
            (config.expected_direct_pages, config.expected_published_pages),
            counts,
        )
    self.assertEqual(
        dict(load_category_config("cave_creatures").excluded_titles)["Mobs"],
        "non_item:overview",
    )
```

- [x] **Step 2: Run config tests and verify RED**

Run: `python3 -m unittest tests.crawl_wiki.test_category_config -v`

Expected: FAIL because configs and `non_item:overview` support do not exist.

- [x] **Step 3: Implement the minimal enum/config data change**

Add only `"non_item:overview"` to `_EXCLUSION_REASONS`. Create configs from the
reviewed table in `docs/category-crawler-control.md`; counts must be:

```text
armour_filter 19/19, beefalo_foods 5/5, boss_dropped_items 75/63,
backpacks 10/6, clothing_filter 10/10, cave_creatures 32/29,
celestial_filter 6/6, celestial_tab 6/6, containers 28/15.
```

Use the exact exclusion titles/reasons already recorded in the control MD.

- [x] **Step 4: Run config and seed tests and verify GREEN**

Run: `python3 -m unittest tests.crawl_wiki.test_category_config tests.crawl_wiki.test_category_seeds -v`

Expected: all tests pass.

- [x] **Step 5: Commit Task 4**

```bash
git add tools/crawl_wiki/category_config.py tests/crawl_wiki/test_category_config.py data/config/wiki-categories docs/category-crawler-control.md docs/superpowers/plans/2026-07-21-durable-category-crawler-state.md
git commit -m "data: configure reviewed DST category batch"
```

### Task 5: Initialize live state and crawl the reviewed batch

**Files:**
- Modify: `data/crawled/fandom-url-registry.json` through snapshot export.
- Modify: `docs/category-crawler-control.md` with final statuses/counts.
- Local only: `<git-common-dir>/category-crawler/` and `data/crawled/fandom-categories/<key>/`.

**Interfaces:**
- Consumes: Tasks 1-4, MediaWiki API, exact category configs.
- Produces: durable live registry/cache, nine isolated crawl checkpoints and a tracked registry/control snapshot.

- [x] **Step 1: Initialize and audit live state**

Run:

```bash
python3 -m tools.crawl_wiki.state_cli init --snapshot data/crawled/fandom-url-registry.json
python3 -m tools.crawl_wiki.state_cli audit
```

Expected: 29 imported rows are `New`; audit reports zero invalid rows.

- [x] **Step 2: Crawl categories sequentially**

Run once per key in this order:

```bash
python3 -m tools.crawl_wiki.cli --profile category --category armour_filter
python3 -m tools.crawl_wiki.cli --profile category --category beefalo_foods
python3 -m tools.crawl_wiki.cli --profile category --category clothing_filter
python3 -m tools.crawl_wiki.cli --profile category --category celestial_filter
python3 -m tools.crawl_wiki.cli --profile category --category celestial_tab
python3 -m tools.crawl_wiki.cli --profile category --category backpacks
python3 -m tools.crawl_wiki.cli --profile category --category containers
python3 -m tools.crawl_wiki.cli --profile category --category boss_dropped_items
python3 -m tools.crawl_wiki.cli --profile category --category cave_creatures
```

Expected: each category reaches zero pending detail pages; duplicate URLs use valid `Done` payloads rather than network fetches. Category children and excluded titles never enter the registry.

- [x] **Step 3: Audit and export the live snapshot**

Run:

```bash
python3 -m tools.crawl_wiki.state_cli audit
python3 -m tools.crawl_wiki.state_cli snapshot --snapshot data/crawled/fandom-url-registry.json
```

Expected: zero invalid rows; 170 total URLs (`29 Animals + 141 new`), all crawled batch candidates `Done`.

- [x] **Step 4: Reconcile control MD from the exported snapshot**

Update queue/status summaries and shared URL rows so `New/Doing/Done` exactly match the exported JSON. Remove the temporary cache blocker only after audit proves every `Done` artifact valid.

- [ ] **Step 5: Commit Task 5**

```bash
git add data/crawled/fandom-url-registry.json docs/category-crawler-control.md docs/superpowers/plans/2026-07-21-durable-category-crawler-state.md
git commit -m "data: crawl reviewed DST category batch"
```

### Task 6: Full verification and handoff

**Files:**
- Modify: `docs/category-crawler-knowledge.md`
- Modify: `docs/wiki-crawler.md`
- Modify: `docs/superpowers/plans/2026-07-21-durable-category-crawler-state.md`

**Interfaces:**
- Consumes: completed implementation and live batch outputs.
- Produces: verified operational documentation and clean branch.

- [ ] **Step 1: Document common-state lifecycle commands**

Document `init`, `audit`, `repair`, `snapshot`, paired override behavior and the rule that raw common-state payloads are never committed.

- [ ] **Step 2: Run all Python and frontend tests**

Run:

```bash
python3 -m unittest discover -s tests -v
npm test
```

Expected: 0 failures.

- [ ] **Step 3: Run static and production checks**

Run:

```bash
npx tsc --noEmit
npm run lint
npm run build
git diff --check
```

Expected: every command exits 0.

- [ ] **Step 4: Verify live/snapshot invariants**

Run state audit and compare URL/status/category tuples between live registry and tracked snapshot. Expected: exact equality, zero invalid `Done` rows, no `Doing` rows, no excluded title in registry.

- [ ] **Step 5: Commit documentation and verification markers**

```bash
git add docs/category-crawler-knowledge.md docs/wiki-crawler.md docs/superpowers/plans/2026-07-21-durable-category-crawler-state.md
git commit -m "docs: document durable category crawler workflow"
```
