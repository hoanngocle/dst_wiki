# Reusable Category Animals Crawler and Side Peek Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Discover the 34 direct namespace-0 Animals pages, exclude six reviewed Shipwrecked/Hamlet-only pages before detail crawling, crawl and publish the remaining 28 DST Mob pages through a reusable category pipeline, merge them by verified prefab code with a non-destructive cleanup audit, and replace the centered detail modal with an accessible right-side peek.

**Architecture:** Add a configuration-driven `category` profile beside the existing full and items crawlers. Category discovery snapshots remain isolated by key, while a locked human-readable URL registry and shared page cache deduplicate item fetches across parallel categories. An offline Mob normalizer produces DST-only typed data and reviewed note candidates; export merges by exact prefab code while preserving canonical source/runtime facts. The frontend consumes schema-versioned local JSON and renders shared Mob sections inside a right-edge drawer.

**Tech Stack:** Python 3.9 standard library, MediaWiki Action API, SQLite, JSONL, deterministic JSON, React 19.2, Next.js 16.2 App Router, TypeScript 5, Tailwind CSS 4, Vitest 4, Testing Library.

## Global Constraints

- The source is exactly `https://dontstarve.fandom.com/wiki/Category:Animals`.
- Require exactly 34 direct namespace-0 discovery members, then exclude the six
  reviewed non-DST titles before detail/image crawling and publish exactly 28
  DST pages; record but never crawl namespace-14 children.
- The non-DST exclusions are exact and configuration-owned: Shipwrecked-only
  `Blue Whale`, `White Whale`, `Wildbore`; Hamlet-only `Peagawk`, `Pog`,
  `Glowfly`.
- Normalize and render only Don't Starve Together values.
- A public Mob page must have at least one verified prefab code; name similarity never authorizes an automatic merge.
- One prefab code belongs to at most one canonical Mob page.
- Known Animals Wiki fields replace stale Wiki/presentation data, but verified Lua/runtime facts win numeric gameplay and reward conflicts.
- Existing stable catalog IDs and inbound item references remain stable.
- Duplicate, sparse, invalid, and orphaned records are audited and hidden when necessary; this delivery deletes none of them.
- Every meaningful source note requires a short reviewed Vietnamese summary before final export.
- Browser runtime never fetches Fandom; text and images come from generated local artifacts.
- Keep the existing `WikiSearch` client boundary. Per the bundled Next.js 16 guide, imported interactive components do not need a redundant `use client` directive.
- Continue using Tailwind utilities for component styling and `app/globals.css` only for shared keyframes, following the bundled Next.js 16 CSS guide.
- Generated JSON, audits, seed order, variant order, and asset paths are deterministic.
- Missing URLs enter the shared registry as `New`; one worker atomically claims
  them as `Doing`; `Doing` and `Done` skip network fetch. Completed payloads are
  reused from the shared cache and every referencing category remains recorded.

---

## File Map

### Shared URL work registry

- Create `docs/category-crawler-knowledge.md`: reusable category and queue contract.
- Create `data/crawled/fandom-url-registry.json`: human-readable shared URL list.
- Create `tools/crawl_wiki/url_registry.py`: URL normalization, locked state transitions, atomic JSON and shared payload cache.
- Create `tests/crawl_wiki/test_url_registry.py`: New/Doing/Done, overlap, concurrency, failure release and cache tests.

### Category crawl infrastructure

- Create `data/config/wiki-categories/animals.json`: reviewed membership/publication counts and explicit non-DST exclusions.
- Create `tools/crawl_wiki/category_config.py`: strict configuration loader and output-path helpers.
- Create `tools/crawl_wiki/category_seeds.py`: direct-member normalization and inclusion/exclusion records.
- Create `tests/crawl_wiki/test_category_config.py`: configuration validation.
- Create `tests/crawl_wiki/test_category_seeds.py`: page/subcategory decisions and redirect deduplication.
- Modify `tools/crawl_wiki/client.py`: category-members pagination API.
- Modify `tests/crawl_wiki/test_client.py`: API parameter and continuation coverage.
- Modify `tools/crawl_wiki/storage.py`: category seed/checkpoint persistence.
- Modify `tests/crawl_wiki/test_storage.py`: resume and deterministic seed export.
- Modify `tools/crawl_wiki/crawler.py`: reusable budgeted `CategoryCrawler`.
- Modify `tests/crawl_wiki/test_crawler.py`: continuation, non-recursion, resume, and primary-image coverage.
- Modify `tools/crawl_wiki/cli.py`: `--profile category --category <key>` routing.
- Modify `tests/crawl_wiki/test_cli.py`: profile defaults and invalid-option behavior.

### Animals normalization and export

- Create `tools/extract/category_mobs.py`: DST-only Mob page normalization and variant/code contract.
- Create `tools/extract/category_notes.py`: cleaned note candidates, source hashes, and reviewed-summary loading.
- Create `tools/extract/category_merge.py`: code-based merge, duplicate hiding, and cleanup audit rows.
- Create `tools/extract/category_assets.py`: atomic publication of selected category images.
- Create `tests/extract/test_category_mobs.py`: Beefalo/Bunnyman/variant parsing fixtures.
- Create `tests/extract/test_category_notes.py`: DST filtering, hash invalidation, and review gates.
- Create `tests/extract/test_category_merge.py`: precedence, duplicates, variants, and flags.
- Create `tests/extract/test_category_assets.py`: referenced-only atomic asset publication.
- Create `data/manual/category-prefab-mappings/animals.json`: explicit page-to-code exceptions; initially valid and empty.
- Create `data/manual/category-note-summaries/animals.json`: reviewed note summaries keyed by page ID and source hash; populated from the real crawl in Task 7.
- Modify `tools/extract/export_items.py`: consume category artifact, merge Mob records, publish assets, and write category audit.
- Modify `tests/extract/test_export_items.py`: category integration and schema-version coverage.
- Modify `tools/extract/validate.py`: 34-discovered/6-excluded/28-published, code ownership, DST-only, note-review, and audit consistency gates.
- Modify `tests/extract/test_export_validate.py`: new hard-failure cases.
- Modify `tools/extract/cli.py`: category note-review and normalization commands plus export/validate paths.

### Frontend

- Create `app/components/mob-sections.tsx`: shared DST/Tu Tiên Mob renderer.
- Create `app/components/mob-sections.test.tsx`: section, variant, reference, and unknown-state coverage.
- Create `app/components/item-detail-peek.tsx`: accessible right-side drawer shell and existing detail routing.
- Create `app/components/item-detail-peek.test.tsx`: desktop/mobile semantics, focus, close, and scroll reset.
- Modify `app/lib/item-catalog.ts`: schema version 7 and strict expanded Mob parsing.
- Modify `app/lib/item-catalog.test.ts`: valid/invalid contract coverage.
- Modify `app/components/tu-tien-item-sections.tsx`: remove the private legacy Mob renderer.
- Modify `app/components/tu-tien-item-sections.test.tsx`: retain non-Mob Tu Tiên coverage.
- Modify `app/components/wiki-search.tsx`: render `ItemDetailPeek`.
- Modify `app/components/wiki-search.test.tsx`: open and navigate within the side peek.
- Modify `app/globals.css`: right-peek entrance keyframe.
- Delete `app/components/item-detail-modal.tsx`: replaced by the side-peek component.
- Delete `app/components/item-detail-modal.test.tsx`: replaced by the side-peek tests.

### Generated artifacts and documentation

- Create `data/generated/categories/animals.json`: normalized 28-Mob DST category artifact plus the complete discovery/exclusion audit.
- Create `data/generated/category-crawl-audits/animals.json`: merge/cleanup/exclusion audit.
- Create `data/generated/category-note-review/animals.json`: source-hash review queue.
- Create `public/assets/wiki-categories/animals/`: selected content-addressed images.
- Modify `public/data/items.json`: schema version 7 with merged Animals Mob data.
- Modify `docs/wiki-crawler.md`: reusable category commands and resume behavior.
- Modify `docs/data-extraction.md`: category normalization, review, export, and validation runbook.

---

### Task 0: Shared category URL registry and page cache

**Files:**
- Create: `docs/category-crawler-knowledge.md`
- Create: `data/crawled/fandom-url-registry.json`
- Create: `tools/crawl_wiki/url_registry.py`
- Create: `tests/crawl_wiki/test_url_registry.py`

**Interfaces:**
- Produces: `normalize_crawler_url(url, allowed_origin) -> str`.
- Produces: `UrlRegistry(path, cache_root, clock)`.
- Produces: `register(url, category) -> UrlRecord`.
- Produces: `claim(url, category, worker_id) -> UrlClaim` where decisions are `crawl`, `busy`, or `reuse`.
- Produces: `complete(claim, payload) -> UrlRecord` and atomically stored shared payload.
- Produces: `release(claim, error) -> UrlRecord` for handled failures.
- Produces: `requeue(url, expected_worker_id=None) -> UrlRecord` for reviewed recovery.

- [x] **Step 1: Write failing URL normalization and transition tests**

Cover fragment removal, canonical title encoding, external-origin rejection,
missing-to-New registration, `New -> Doing -> Done`, repeated category keys,
and strict worker ownership for complete/release.

- [x] **Step 2: Run registry tests and verify RED**

Run:

```bash
python3 -m unittest tests.crawl_wiki.test_url_registry -v
```

Expected: `tools.crawl_wiki.url_registry` does not exist.

- [x] **Step 3: Implement locked atomic registry and content-addressed cache**

Use `fcntl.flock` on a sidecar lock for every read-modify-write. Sort registry
rows by URL and category keys case-insensitively. Write JSON through a sibling
temporary file, `flush`, `os.fsync`, and `os.replace`. Cache payloads under the
SHA-256 of canonical URL and store their relative artifact path in the row.

`claim` performs register and state decision under one lock: missing or `New`
returns `crawl` after setting `Doing`; `Doing` returns `busy`; `Done` returns
`reuse`. A handled error changes the owner's `Doing` row back to `New`; a crash
does not auto-expire. `requeue` is explicit and auditable.

- [x] **Step 4: Add concurrency and shared-cache reuse tests**

Start two registry instances against one temporary file. Prove only one claim
returns `crawl`, the other returns `busy`, both category keys are retained, and
a third claim after completion returns `reuse` with the exact cached payload.

- [x] **Step 5: Run registry and existing crawler suites**

Run:

```bash
python3 -m unittest tests.crawl_wiki.test_url_registry tests.crawl_wiki.test_storage tests.crawl_wiki.test_crawler tests.crawl_wiki.test_cli -v
```

Expected: PASS.

- [x] **Step 6: Commit Task 0**

```bash
git add docs/category-crawler-knowledge.md data/crawled/fandom-url-registry.json tools/crawl_wiki/url_registry.py tests/crawl_wiki/test_url_registry.py docs/superpowers/specs/2026-07-21-reusable-category-animals-crawler-side-peek-design.md docs/superpowers/plans/2026-07-21-reusable-category-animals-crawler-side-peek.md
git commit -m "feat: coordinate category crawler URLs"
```

---

### Task 1: Strict category configuration and MediaWiki discovery API

**Files:**
- Create: `data/config/wiki-categories/animals.json`
- Create: `tools/crawl_wiki/category_config.py`
- Create: `tools/crawl_wiki/category_seeds.py`
- Create: `tests/crawl_wiki/test_category_config.py`
- Create: `tests/crawl_wiki/test_category_seeds.py`
- Modify: `tools/crawl_wiki/client.py`
- Modify: `tests/crawl_wiki/test_client.py`

**Interfaces:**
- Produces: `CategoryConfig(key, source_url, category_title, expected_direct_pages, expected_published_pages, allowed_namespaces, excluded_titles, game, item_type, tags)`.
- Produces: `load_category_config(key: str, root: Path = CATEGORY_CONFIG_ROOT) -> CategoryConfig`.
- Produces: `CategorySeed(page_id, namespace, title, canonical_url, accepted, reason)`.
- Produces: `normalize_category_members(config, members) -> list[CategorySeed]`.
- Produces: `MediaWikiClient.list_category_members(title, continuation=None) -> tuple[list[dict], str | None]`.
- Produces: `MediaWikiClient.resolve_titles_detailed(titles) -> list[ResolvedTitle]`, preserving requested and canonical identity.

- [x] **Step 1: Write failing configuration and seed-decision tests**

```python
def test_loads_animals_category_with_reviewed_scope():
    config = load_category_config("animals")
    assert config.category_title == "Category:Animals"
    assert config.expected_direct_pages == 34
    assert config.expected_published_pages == 28
    assert config.allowed_namespaces == (0,)
    assert dict(config.excluded_titles) == {
        "Blue Whale": "non_dst:shipwrecked",
        "White Whale": "non_dst:shipwrecked",
        "Wildbore": "non_dst:shipwrecked",
        "Peagawk": "non_dst:hamlet",
        "Pog": "non_dst:hamlet",
        "Glowfly": "non_dst:hamlet",
    }
    assert config.game == "DST"
    assert config.item_type == "mob"
    assert config.tags == ("Animals",)


def test_accepts_pages_and_audits_subcategories_without_recursing():
    config = category_config(expected_direct_pages=2, expected_published_pages=2)
    seeds = normalize_category_members(config, [
        {"pageid": 1, "ns": 0, "title": "Beefalo"},
        {"pageid": 2, "ns": 14, "title": "Category:Birds"},
        {"pageid": 3, "ns": 0, "title": "Bunnyman"},
    ])
    assert [seed.title for seed in seeds if seed.accepted] == ["Beefalo", "Bunnyman"]
    assert [(seed.title, seed.reason) for seed in seeds if not seed.accepted] == [
        ("Category:Birds", "excluded_namespace:14")
    ]


def test_excludes_reviewed_non_dst_pages_before_detail_queueing():
    config = category_config(
        expected_direct_pages=3,
        expected_published_pages=1,
        excluded_titles={
            "Blue Whale": "non_dst:shipwrecked",
            "Peagawk": "non_dst:hamlet",
        },
    )
    seeds = normalize_category_members(config, [
        {"pageid": 1, "ns": 0, "title": "Beefalo"},
        {"pageid": 2, "ns": 0, "title": "Blue Whale"},
        {"pageid": 3, "ns": 0, "title": "Peagawk"},
    ])
    assert [seed.title for seed in seeds if seed.accepted] == ["Beefalo"]
    assert [(seed.title, seed.reason) for seed in seeds if not seed.accepted] == [
        ("Blue Whale", "non_dst:shipwrecked"),
        ("Peagawk", "non_dst:hamlet"),
    ]
```

- [x] **Step 2: Write a failing category-members continuation test**

```python
def test_lists_direct_category_members_with_continuation():
    opener = JsonOpener({
        "query": {"categorymembers": [{"pageid": 1, "ns": 0, "title": "Beefalo"}]},
        "continue": {"cmcontinue": "page|next", "continue": "-||"},
    })
    client = MediaWikiClient("https://dontstarve.fandom.com/", delay=0, opener=opener)
    pages, token = client.list_category_members("Category:Animals")
    assert pages[0]["title"] == "Beefalo"
    assert token == "page|next"
    assert opener.last_query["cmtype"] == ["page|subcat"]


def test_resolves_requested_titles_to_canonical_page_identity():
    client = MediaWikiClient("https://dontstarve.fandom.com/", delay=0, opener=redirect_opener())
    resolved = client.resolve_titles_detailed(["Old Beefalo"])
    assert resolved[0].requested_title == "Old Beefalo"
    assert resolved[0].canonical_title == "Beefalo"
    assert resolved[0].page_id == 56
```

- [x] **Step 3: Run the focused tests and verify RED**

Run:

```bash
python3 -m unittest tests.crawl_wiki.test_category_config tests.crawl_wiki.test_category_seeds tests.crawl_wiki.test_client -v
```

Expected: configuration/seed modules are missing and `MediaWikiClient` has no `list_category_members` method.

- [x] **Step 4: Add the reviewed Animals config and strict loader**

`data/config/wiki-categories/animals.json`:

```json
{
  "schema_version": 1,
  "key": "animals",
  "sourceUrl": "https://dontstarve.fandom.com/wiki/Category:Animals",
  "categoryTitle": "Category:Animals",
  "expectedDirectPages": 34,
  "expectedPublishedPages": 28,
  "allowedNamespaces": [0],
  "excludedTitles": {
    "Blue Whale": "non_dst:shipwrecked",
    "White Whale": "non_dst:shipwrecked",
    "Wildbore": "non_dst:shipwrecked",
    "Peagawk": "non_dst:hamlet",
    "Pog": "non_dst:hamlet",
    "Glowfly": "non_dst:hamlet"
  },
  "game": "DST",
  "itemType": "mob",
  "tags": ["Animals"]
}
```

Implement `CategoryConfig` as a frozen dataclass. Reject an invalid schema,
key/path mismatch, non-HTTPS source, non-category title, duplicate/unsupported
namespaces, non-positive expected counts, an exclusion count inconsistent with
the direct/published difference, unsupported exclusion reasons, duplicate
normalized excluded titles, any game other than `DST`, and empty tags. Derive
`base_url` from the source URL origin and expose:

```python
@property
def output_path(self) -> Path:
    return Path("data/crawled/fandom-categories") / self.key
```

- [x] **Step 5: Implement category membership pagination and deterministic seeds**

Add this client method using the existing `_api` retry path:

```python
def list_category_members(self, title, continuation=None):
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": title,
        "cmtype": "page|subcat",
        "cmlimit": "max",
        "cmprop": "ids|title|type",
    }
    if continuation:
        params["cmcontinue"] = continuation
    response = self._api(params)
    query = response.get("query")
    members = query.get("categorymembers") if isinstance(query, Mapping) else None
    if not isinstance(members, list) or not all(isinstance(value, dict) for value in members):
        raise ClientError("categorymembers response is invalid", retryable=False)
    continued = response.get("continue")
    token = continued.get("cmcontinue") if isinstance(continued, Mapping) else None
    if token is not None and not isinstance(token, str):
        raise ClientError("category continuation token must be a string", retryable=False)
    return members, token
```

`normalize_category_members` sorts by `(title.casefold(), title, page_id)`,
deduplicates direct membership rows by page ID, accepts only configured
namespaces, and emits exclusions for every other namespace.

Add `ResolvedTitle(requested_title, page_id, namespace, canonical_title,
canonical_url)` and `resolve_titles_detailed`. Parse the MediaWiki `normalized`
and `redirects` arrays into an alias chain so every requested title maps to one
canonical page. Keep `resolve_titles` backward-compatible by returning the
canonical page dictionaries from the detailed method.

- [x] **Step 6: Run tests and commit Task 1**

Run:

```bash
python3 -m unittest tests.crawl_wiki.test_category_config tests.crawl_wiki.test_category_seeds tests.crawl_wiki.test_client -v
```

Expected: PASS.

```bash
git add data/config/wiki-categories/animals.json tools/crawl_wiki/category_config.py tools/crawl_wiki/category_seeds.py tools/crawl_wiki/client.py tests/crawl_wiki/test_category_config.py tests/crawl_wiki/test_category_seeds.py tests/crawl_wiki/test_client.py
git commit -m "feat: configure reusable wiki category discovery"
```

---

### Task 2: Resumable category storage, crawler, and CLI

**Files:**
- Modify: `tools/crawl_wiki/storage.py`
- Modify: `tests/crawl_wiki/test_storage.py`
- Modify: `tools/crawl_wiki/crawler.py`
- Modify: `tests/crawl_wiki/test_crawler.py`
- Modify: `tools/crawl_wiki/cli.py`
- Modify: `tests/crawl_wiki/test_cli.py`

**Interfaces:**
- Consumes: `CategoryConfig`, `CategorySeed`, category-members client method.
- Produces: `CrawlStorage.save_category_seeds(seeds)`, category discovery token/complete methods, and deterministic `seeds.jsonl`.
- Produces: `CategoryCrawler(client, storage, config, page_budget=100, skip_images=False)`.
- Produces CLI: `python3 -m tools.crawl_wiki.cli --profile category --category animals`.

- [x] **Step 1: Write failing storage tests for accepted/excluded seeds and resume**

```python
def test_persists_category_seeds_and_resume_token(self):
    storage.save_category_seeds([
        CategorySeed(1, 0, "Beefalo", "https://dontstarve.fandom.com/wiki/Beefalo", True, None),
        CategorySeed(2, 14, "Category:Birds", "https://dontstarve.fandom.com/wiki/Category:Birds", False, "excluded_namespace:14"),
    ])
    storage.set_category_discovery_token("animals", "page|next")
    assert storage.get_category_discovery_token("animals") == "page|next"
    lines = [json.loads(line) for line in (root / "seeds.jsonl").read_text().splitlines()]
    assert [line["title"] for line in lines] == ["Beefalo", "Category:Birds"]
    assert sum(line["accepted"] for line in lines) == 1
```

- [x] **Step 2: Write failing crawler tests for continuation, non-recursion, and budget resume**

```python
def test_category_crawler_discovers_all_members_but_queues_only_pages(self):
    client = CategoryClient([
        ([{"pageid": 1, "ns": 0, "title": "Beefalo"}], "next"),
        ([{"pageid": 2, "ns": 14, "title": "Category:Birds"},
          {"pageid": 3, "ns": 0, "title": "Blue Whale"},
          {"pageid": 4, "ns": 0, "title": "Bunnyman"}], None),
    ])
    config = category_config(
        expected_direct_pages=3,
        expected_published_pages=2,
        excluded_titles={"Blue Whale": "non_dst:shipwrecked"},
    )
    CategoryCrawler(client, storage, config, page_budget=1, skip_images=True).run({})
    assert client.category_calls == [("Category:Animals", None), ("Category:Animals", "next")]
    assert storage.page_count() == 2
    assert storage.pending_page_count() == 1
    assert "Category:Birds" not in client.parsed_titles
    assert "Blue Whale" not in client.parsed_titles
```

- [x] **Step 3: Write failing CLI profile tests**

```python
def test_category_profile_uses_configured_source_and_output():
    args = build_parser().parse_args(["--profile", "category", "--category", "animals"])
    assert resolve_base_url(args) == "https://dontstarve.fandom.com/"
    assert resolve_output(args) == Path("data/crawled/fandom-categories/animals")


def test_category_name_is_required_only_for_category_profile():
    with self.assertRaisesRegex(ValueError, "--category is required"):
        run_crawl(build_parser().parse_args(["--profile", "category"]))
```

- [x] **Step 4: Run focused tests and verify RED**

Run:

```bash
python3 -m unittest tests.crawl_wiki.test_storage tests.crawl_wiki.test_crawler tests.crawl_wiki.test_cli -v
```

Expected: category storage methods, crawler class, and CLI choice are missing.

- [x] **Step 5: Add category checkpoint and seed persistence**

Add a `category_seed_metadata` table with page ID, namespace, title, canonical
URL, accepted flag, and reason. Add these exact metadata keys:

```python
def get_category_discovery_token(self, key):
    return self._metadata(f"category:{key}:discovery:token")

def set_category_discovery_token(self, key, token):
    with self.connection:
        self._set_metadata(f"category:{key}:discovery:token", token)

def is_category_discovery_complete(self, key):
    return self._metadata(f"category:{key}:discovery:complete") == "1"

def mark_category_discovery_complete(self, key):
    with self.connection:
        self.connection.execute("delete from metadata where key=?", (f"category:{key}:discovery:token",))
        self._set_metadata(f"category:{key}:discovery:complete", "1")
```

`save_category_seeds` writes both accepted and excluded rows atomically to the
table and regenerates `seeds.jsonl`. Only accepted rows are passed to
`enqueue_pages`.

- [x] **Step 6: Implement `CategoryCrawler` and primary image selection**

Use `WikiCrawler._process_images` for binary handling. `CategoryCrawler.run`
must call discovery, process at most `page_budget` queued pages, then images and
finalize. Page processing calls `normalize_page`, records links, and selects the
first image referenced inside the rendered infobox; if no infobox image is
found, keep the page with no queued image and let visual status become unknown.

```python
class CategoryCrawler(WikiCrawler):
    def __init__(self, client, storage, config, page_budget=100, skip_images=False, clock=_utc_now):
        if page_budget <= 0:
            raise ValueError("page budget must be positive")
        super().__init__(client, storage, config.allowed_namespaces, skip_images=skip_images, clock=clock)
        self.config = config
        self.page_budget = page_budget

    def run(self, options):
        self._discover_category()
        self._process_category_pages()
        if not self.skip_images:
            self._process_images()
        return self.storage.finalize(options)
```

Discovery follows tokens until exhausted, records disallowed namespaces, and
first enforces the 34-page direct namespace-0 membership guard. It then marks
the exact configured non-DST titles excluded before any detail/image request,
resolves only the remaining requested titles through
`resolve_titles_detailed`, rewrites queued seeds with canonical page
ID/title/URL, deduplicates by resolved page ID, and enforces the 28-page queue
guard. It saves all queued/excluded seeds and marks discovery complete only
after membership, exclusion, and queue-count validation.

- [x] **Step 7: Route the category profile in the CLI**

Extend profile choices to `full|items|category`. Add `--category` and a generic
`--page-budget` defaulting to 100. Make `--base-url` default to `None`, then use:

```python
def resolve_base_url(args):
    if args.base_url is not None:
        return args.base_url
    if args.profile == "category":
        return load_category_config(args.category).base_url
    return DEFAULT_BASE_URL
```

Reject `--category` outside the category profile, require it inside that
profile, reject `--max-pages`/`--item-budget` there, and instantiate
`CategoryCrawler` with output `config.output_path` unless `--output` is given.

- [x] **Step 8: Run tests and commit Task 2**

Run:

```bash
python3 -m unittest tests.crawl_wiki.test_storage tests.crawl_wiki.test_crawler tests.crawl_wiki.test_cli -v
```

Expected: PASS.

```bash
git add tools/crawl_wiki/storage.py tools/crawl_wiki/crawler.py tools/crawl_wiki/cli.py tests/crawl_wiki/test_storage.py tests/crawl_wiki/test_crawler.py tests/crawl_wiki/test_cli.py
git commit -m "feat: crawl configured wiki categories"
```

---

### Task 3: DST-only Mob normalization, variants, and note review data

**Files:**
- Create: `tools/extract/category_mobs.py`
- Create: `tools/extract/category_notes.py`
- Create: `tests/extract/test_category_mobs.py`
- Create: `tests/extract/test_category_notes.py`
- Create: `data/manual/category-prefab-mappings/animals.json`
- Create: `data/manual/category-note-summaries/animals.json`
- Modify: `tools/extract/cli.py`

**Interfaces:**
- Produces: `normalize_category_mobs(crawl_root, config, mappings, summaries) -> dict`.
- Produces: `extract_mob_page(page, config, mappings) -> dict`.
- Produces: `build_category_note_review(crawl_root, config, output) -> dict`.
- Produces: `load_reviewed_note_summaries(path) -> Mapping[int, ReviewedNote]`.
- Produces CLI commands `category-notes` and `normalize-category`.

- [x] **Step 1: Write failing DST-only Beefalo and Bunnyman parser tests**

```python
def test_normalizes_only_dst_values_from_multi_game_infobox(self):
    mob = extract_mob_page(beefalo_page(), animals_config(), prefab_mappings())
    assert mob["identity"]["primaryCode"] == "beefalo"
    assert mob["classification"] == {"type": "mob", "tags": ["Animals"], "game": "DST"}
    assert fact(mob, "stats", "max_health")["value"] == 1000
    assert fact(mob, "combat", "attack_damage")["value"] == 34
    assert fact(mob, "movement", "run_speed")["value"] == 7
    assert all("Shipwrecked" not in json.dumps(value) for value in walk_values(mob))


def test_keeps_dst_loot_row_and_bunnyman_transformation_trait(self):
    mob = extract_mob_page(bunnyman_page(), animals_config(), prefab_mappings())
    assert fact(mob, "effects", "sanity_aura")["value"] == "25/min"
    assert mob["traits"]["status"] == "known"
    assert any("Beardlord" in value["text"] for value in mob["traits"]["values"])
    assert all(drop["game"] == "DST" for drop in mob["loot"]["values"])
```

- [x] **Step 2: Write failing variant and unknown-state tests**

```python
def test_groups_verified_prefab_variants_on_one_page():
    mob = extract_mob_page(koalefant_page(), animals_config(), prefab_mappings())
    assert mob["identity"]["prefabCodes"] == ["koalefant_summer", "koalefant_winter"]
    assert [value["code"] for value in mob["variants"]] == [
        "koalefant_summer", "koalefant_winter"
    ]


def test_marks_ambiguous_unlabelled_multi_game_value_unknown():
    mob = extract_mob_page(ambiguous_page(), animals_config(), prefab_mappings())
    assert mob["combat"]["status"] == "unknown"
    assert mob["combat"]["reason"] == "ambiguous_game_version"
```

- [x] **Step 3: Write failing note cleaning, hash, and review-gate tests**

```python
def test_note_review_keeps_dst_gameplay_and_drops_patch_trivia():
    review = build_note_review([note_page()], animals_config())
    assert review["pages"]["208"]["source"] == "Turns into a Beardlord below 40% Sanity."
    assert review["pages"]["208"]["source_sha256"] == sha256_text(
        "Turns into a Beardlord below 40% Sanity."
    )


def test_normalizer_rejects_unreviewed_source_note():
    with self.assertRaisesRegex(ValueError, "reviewed Vietnamese summary"):
        normalize_category_mobs(crawl_root, animals_config(), mappings={}, summaries={})
```

- [x] **Step 4: Run tests and verify RED**

Run:

```bash
python3 -m unittest tests.extract.test_category_mobs tests.extract.test_category_notes -v
```

Expected: category Mob and Notes modules are missing.

- [x] **Step 5: Implement strict section and variant builders**

Use one shared section shape everywhere:

```python
def section(status, values=(), reason=None, evidence=()):
    return {
        "status": status,
        "values": list(values),
        "reason": reason,
        "evidence": list(evidence),
    }
```

Implement explicit field aliases for health, sanity aura, damage, attack period,
attack range, walking speed, and running speed. Parse version-labelled cells
before shared cells. Reject DS, RoG, Shipwrecked, and Hamlet-only candidates.
Build `traits`, `loot`, and `spawnsFrom` from DST-labelled infobox/table/template
content. Every value carries source page/revision plus a wikitext or HTML
locator. Aggregate loot only when item, variant, chance, quantity, method, and
condition all match.

Prefab discovery uses exact spawn-code templates and the reviewed mapping file.
The mapping format starts valid and empty:

```json
{"schema_version": 1, "pages": {}}
```

Missing or ambiguous page codes remain errors for the real-data gate rather
than triggering title matching.

- [x] **Step 6: Implement note candidates and reviewed-summary loading**

Extract `Notes`, gameplay callouts, and note-like infobox rows. Strip citations,
navigation, update history, duplicates, and non-DST-exclusive sentences. Store
source text and SHA-256 in `data/generated/category-note-review/<key>.json`.

The reviewed manual file uses this exact contract:

```json
{"schema_version": 1, "pages": {}}
```

Each populated page entry must contain `source_sha256`, non-empty `vi`, and
`reviewed: true`. A hash mismatch is treated as unreviewed. Proven note absence
produces section status `none`; an extraction gap produces `unknown`.

- [x] **Step 7: Add offline CLI commands**

Add:

```text
python3 -m tools.extract.cli category-notes --category animals
python3 -m tools.extract.cli normalize-category --category animals
```

`category-notes` reads the completed crawl and atomically writes the review
queue. `normalize-category` reads config, raw crawl, mappings, reviewed note
summaries, and atomically writes `data/generated/categories/animals.json` only
when it contains 28 valid canonical DST Mob records. The artifact also contains
a `discovery` object with all 34 direct namespace-0 members, the exact six
non-DST exclusions, all accepted canonical pages, and every excluded
subcategory seed, so merge/audit can emit explicit `excluded` rows.

- [x] **Step 8: Run tests and commit Task 3**

Run:

```bash
python3 -m unittest tests.extract.test_category_mobs tests.extract.test_category_notes -v
```

Expected: PASS.

```bash
git add tools/extract/category_mobs.py tools/extract/category_notes.py tools/extract/cli.py tests/extract/test_category_mobs.py tests/extract/test_category_notes.py data/manual/category-prefab-mappings/animals.json data/manual/category-note-summaries/animals.json
git commit -m "feat: normalize DST category mobs"
```

---

### Task 4: Code-based catalog merge, assets, cleanup audit, and validation

**Files:**
- Create: `tools/extract/category_merge.py`
- Create: `tools/extract/category_assets.py`
- Create: `tests/extract/test_category_merge.py`
- Create: `tests/extract/test_category_assets.py`
- Modify: `tools/extract/export_items.py`
- Modify: `tests/extract/test_export_items.py`
- Modify: `tools/extract/validate.py`
- Modify: `tests/extract/test_export_validate.py`
- Modify: `tools/extract/cli.py`

**Interfaces:**
- Produces: `merge_category_mobs(items, artifact, entities) -> CategoryMergeResult`.
- Produces: `CategoryMergeResult(items, audit)`.
- Produces: `publish_category_assets(artifact, crawl_root, output) -> list[dict]`.
- Extends `export_items(...)` with category artifact/audit/asset paths.
- Extends `validate_catalog(...)` with category audit consistency checks.

- [x] **Step 1: Write failing merge precedence and duplicate tests**

```python
def test_merges_by_code_without_changing_canonical_id():
    result = merge_category_mobs(existing_beefalo_items(), animals_artifact(), entities())
    beefalo = item(result.items, "base_game:beefalo")
    assert beefalo["id"] == "base_game:beefalo"
    assert beefalo["mob"]["classification"]["tags"] == ["Animals"]
    assert audit(result, "base_game:beefalo")["action"] == "merged"


def test_known_wiki_value_replaces_stale_presentation_but_not_runtime_fact():
    result = merge_category_mobs(items_with_runtime_damage(34), wiki_damage(40), entities())
    assert mob_fact(result.items, "beefalo", "attack_damage")["value"] == 34
    assert mob_fact(result.items, "beefalo", "attack_damage")["evidence"][0]["source"].startswith("runtime:")


def test_hides_duplicate_code_and_flags_empty_orphan():
    result = merge_category_mobs(duplicate_and_orphan_items(), animals_artifact(), entities())
    assert public_ids(result.items).count("base_game:beefalo") == 1
    assert audit_action(result, "base_game:beefalo_copy") == "duplicate_hidden"
    assert "empty_details" in audit_flags(result, "base_game:unknown_mob")
```

- [x] **Step 2: Write failing asset and validation tests**

```python
def test_publishes_only_referenced_images_atomically(self):
    published = publish_category_assets(artifact_with_image("abc.png"), crawl_root, output)
    assert [value["publicPath"] for value in published] == [
        "/assets/wiki-categories/animals/" + "a" * 64 + ".png"
    ]
    assert not (output / "unused.png").exists()


def test_category_validation_rejects_duplicate_code_and_unreviewed_note(self):
    errors = category_export_errors(items_payload(), broken_category_audit())
    assert "duplicate_prefab_code" in error_codes(errors)
    assert "unreviewed_category_note" in error_codes(errors)


def test_category_validation_rejects_non_dst_detail_fetch_and_count_drift(self):
    errors = category_export_errors(
        items_payload(),
        category_audit(
            direct_pages=34,
            excluded_non_dst=reviewed_six_non_dst_titles(),
            fetched_titles=["Beefalo", "Blue Whale"],
            published_pages=28,
        ),
    )
    assert "excluded_title_fetched" in error_codes(errors)

    drift = category_export_errors(
        items_payload(),
        category_audit(direct_pages=34, excluded_non_dst=[], published_pages=34),
    )
    assert "non_dst_exclusion_mismatch" in error_codes(drift)
    assert "published_category_count_mismatch" in error_codes(drift)
```

- [x] **Step 3: Run tests and verify RED**

Run:

```bash
python3 -m unittest tests.extract.test_category_merge tests.extract.test_category_assets tests.extract.test_export_items tests.extract.test_export_validate -v
```

Expected: merge/asset modules and category validation are absent.

- [x] **Step 4: Implement merge actions and audit rows**

Index all existing base-game Mob records by normalized prefab code. For each
canonical category page, match every `prefabCodes` value. Preserve the chosen
existing canonical ID, redirect references from hidden duplicates, merge
variants, and emit one audit row per created/matched/flagged/excluded record.

Use actions exactly `created`, `merged`, `kept`, `flagged`,
`duplicate_hidden`, and `excluded`. Use flags exactly `missing_code`,
`empty_details`, `invalid_schema`, `missing_visual`, `orphan_record`, and
`duplicate_code`. Sort rows by `(recordId, action)`.

- [x] **Step 5: Integrate category artifacts into export and bump schema**

After base items and old Mob details are built, load
`data/generated/categories/animals.json`, merge it before structure/effect
audits, publish selected images into a staging directory, then atomically
replace `public/assets/wiki-categories/animals`. Write the audit to
`data/generated/category-crawl-audits/animals.json`.

Change the public payload header from schema version 6 to 7. Always serialize
`mob: null` for non-Mob/Boss records and the expanded Mob contract for Mob/Boss
records.

- [x] **Step 6: Add hard validation gates**

Validation must reject direct namespace-0 discovery total not equal to 34, a
non-DST exclusion set other than the exact reviewed six titles/reasons, queued
or published category total not equal to 28, any excluded title with fetched
detail/image data, any published category page with no code, code ownership
conflicts, category-child publication, non-DST evidence/value labels, invalid
known-empty sections, unresolved known loot references, source note without
matching reviewed hash, audit/public disagreement, and absent source/revision
attribution.

Append `category_export_errors` to coverage JSON and add
`category_export_errors` to `hard_failures` when non-empty. Keep cleanup-only
flags as warnings so they can be deleted in a later reviewed task.

- [x] **Step 7: Run tests and commit Task 4**

Run:

```bash
python3 -m unittest tests.extract.test_category_merge tests.extract.test_category_assets tests.extract.test_export_items tests.extract.test_export_validate -v
```

Expected: PASS.

```bash
git add tools/extract/category_merge.py tools/extract/category_assets.py tools/extract/export_items.py tools/extract/validate.py tools/extract/cli.py tests/extract/test_category_merge.py tests/extract/test_category_assets.py tests/extract/test_export_items.py tests/extract/test_export_validate.py
git commit -m "feat: merge audited category mob data"
```

---

### Task 5: Strict frontend Mob contract and shared renderer

**Files:**
- Create: `app/components/mob-sections.tsx`
- Create: `app/components/mob-sections.test.tsx`
- Modify: `app/lib/item-catalog.ts`
- Modify: `app/lib/item-catalog.test.ts`
- Modify: `app/components/tu-tien-item-sections.tsx`
- Modify: `app/components/tu-tien-item-sections.test.tsx`
- Modify: `app/components/item-detail-modal.tsx`

**Interfaces:**
- Consumes: public item payload schema version 7.
- Produces: strict `MobDetails` section/status types.
- Produces: `MobSections({ item, itemsById, onSelectItem, titleId })` for both namespaces and Mob/Boss categories.

- [x] **Step 1: Write failing expanded parser tests**

```typescript
it("accepts the expanded DST Animals Mob contract", () => {
  const payload = payloadWithAnimalMob();
  const mob = parseItemPayload(payload)[0].mob;
  expect(mob?.identity.prefabCodes).toEqual(["koalefant_summer", "koalefant_winter"]);
  expect(mob?.combat.values[0]).toMatchObject({ key: "attack_damage", value: 50 });
  expect(mob?.notes.values[0]).toMatchObject({ status: "reviewed" });
});

it("rejects known empty sections, duplicate codes, and non-DST classification", () => {
  expect(() => parseItemPayload(payloadWithKnownEmptyCombat())).toThrow(/known combat/i);
  expect(() => parseItemPayload(payloadWithDuplicatePrefabCodes())).toThrow(/prefabCodes/i);
  expect(() => parseItemPayload(payloadWithGame("Shipwrecked"))).toThrow(/DST/i);
});
```

- [x] **Step 2: Write failing Mob renderer tests**

```tsx
it("renders ordered Animals sections and navigable loot", () => {
  render(<MobSections item={bunnyman} itemsById={itemsById} onSelectItem={onSelectItem} titleId="mob" />);
  expect(screen.getByRole("heading", { name: "Stats" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Effects" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Combat" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Movement" })).toBeInTheDocument();
  expect(screen.getByText(/Beardlord/)).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Carrot" }));
  expect(onSelectItem).toHaveBeenCalledWith(itemsById.get("base_game:carrot"));
});

it("renders one variant selector and concise unknown state", () => {
  render(<MobSections item={koalefant} itemsById={itemsById} onSelectItem={vi.fn()} titleId="mob" />);
  expect(screen.getByRole("tab", { name: "Winter Koalefant" })).toBeInTheDocument();
  expect(screen.getByText("Chưa xác minh")).toBeInTheDocument();
});
```

- [x] **Step 3: Run Vitest and verify RED**

Run:

```bash
npm test -- app/lib/item-catalog.test.ts app/components/mob-sections.test.tsx app/components/tu-tien-item-sections.test.tsx
```

Expected: schema version 7 and `MobSections` are missing.

- [x] **Step 4: Define and strictly parse the expanded types**

Use these core types:

```typescript
export type MobSection<T> = {
  status: ItemDetailStatus;
  values: readonly T[];
  reason: string | null;
  evidence: readonly ItemEvidence[];
};

export type MobVariant = {
  code: string;
  label: string;
  order: number;
  sprite: SpriteDescriptor | null;
};

export type MobLoot = {
  item: ItemReference;
  quantity: string;
  chance: string | null;
  conditions: string | null;
  method: "kill" | "harvest" | "conditional" | "mine_post_defeat";
  sourceVariant: string | null;
  game: "DST";
};

export type MobSpawnSource = {
  source: ItemReference;
  conditions: string | null;
  sourceVariant: string | null;
};

export type MobTrait = { text: string; sourceVariant: string | null };
export type MobNote = {
  source: string;
  summaryVi: string;
  sourceSha256: string;
  status: "reviewed";
};

export type MobDetails = {
  identity: {
    primaryCode: string;
    prefabCodes: readonly string[];
    sourcePageId: number;
    sourceUrl: string;
    revisionId: number;
  };
  classification: { type: "mob" | "boss"; tags: readonly string[]; game: "DST" };
  variants: readonly MobVariant[];
  stats: MobSection<MobStat>;
  effects: MobSection<MobStat>;
  combat: MobSection<MobStat>;
  movement: MobSection<MobStat>;
  traits: MobSection<MobTrait>;
  loot: MobSection<MobLoot>;
  spawnsFrom: MobSection<MobSpawnSource>;
  notes: MobSection<MobNote>;
};
```

Require unique non-empty prefab codes, primary-code membership, positive page
and revision IDs, HTTPS source URL, exact DST classification, sorted unique
variant order, non-empty `known` values, empty `none` values, valid item
references, and reviewed notes.

- [x] **Step 5: Implement the shared Mob renderer and remove the private renderer**

Move Mob rendering out of `tu-tien-item-sections.tsx`. Render sections in this
order: Summary remains owned by the detail shell, then Stats, Effects, Combat,
Movement, Traits, Loot, Spawns from, Notes, Code, and source attribution.
Hide `none`; show `Chưa xác minh` for `unknown`; use a tablist only for multiple
variants. Keep `ReferenceButton` behavior for local item navigation.

In `item-detail-modal.tsx`, route both `mob` and `boss` categories through
`MobSections` before namespace-specific routing. This is an intermediate step;
Task 6 moves the shell to the new side-peek file.

- [x] **Step 6: Run frontend checks and commit Task 5**

Run:

```bash
npm test -- app/lib/item-catalog.test.ts app/components/mob-sections.test.tsx app/components/tu-tien-item-sections.test.tsx
npx tsc --noEmit
```

Expected: PASS and TypeScript exit 0.

```bash
git add app/lib/item-catalog.ts app/lib/item-catalog.test.ts app/components/mob-sections.tsx app/components/mob-sections.test.tsx app/components/tu-tien-item-sections.tsx app/components/tu-tien-item-sections.test.tsx app/components/item-detail-modal.tsx
git commit -m "feat: render shared structured mob details"
```

---

### Task 6: Replace the centered modal with an accessible right-side peek

**Files:**
- Create: `app/components/item-detail-peek.tsx`
- Create: `app/components/item-detail-peek.test.tsx`
- Modify: `app/components/wiki-search.tsx`
- Modify: `app/components/wiki-search.test.tsx`
- Modify: `app/globals.css`
- Delete: `app/components/item-detail-modal.tsx`
- Delete: `app/components/item-detail-modal.test.tsx`

**Interfaces:**
- Produces: `ItemDetailPeek({ item, itemsById, onSelectItem, onClose })`.
- Preserves: `WikiSearch` owns `selectedItem`; related-item selection replaces content without closing.

- [x] **Step 1: Write failing side-peek semantics and focus tests**

```tsx
it("renders a right-edge full-height dialog and restores focus", () => {
  const origin = document.createElement("button");
  document.body.append(origin);
  origin.focus();
  const { unmount } = render(<ItemDetailPeek {...props(beefalo)} />);
  const dialog = screen.getByRole("dialog", { name: "Beefalo" });
  expect(dialog).toHaveAttribute("data-placement", "right");
  expect(dialog.className).toContain("h-dvh");
  expect(screen.getByRole("button", { name: "Đóng chi tiết" })).toHaveFocus();
  unmount();
  expect(origin).toHaveFocus();
});

it("closes through Escape and overlay but not panel clicks", () => {
  render(<ItemDetailPeek {...props(beefalo)} />);
  fireEvent.click(screen.getByRole("dialog", { name: "Beefalo" }));
  expect(onClose).not.toHaveBeenCalled();
  fireEvent.keyDown(document, { key: "Escape" });
  expect(onClose).toHaveBeenCalledTimes(1);
});
```

- [x] **Step 2: Write failing content replacement and scroll-reset tests**

```tsx
it("keeps the peek open and scrolls its body to top when item changes", () => {
  const { rerender } = render(<ItemDetailPeek {...props(beefalo)} />);
  const body = screen.getByTestId("item-detail-peek-body");
  body.scrollTo = vi.fn();
  rerender(<ItemDetailPeek {...props(bunnyman)} />);
  expect(screen.getByRole("dialog", { name: "Bunnyman" })).toBeInTheDocument();
  expect(body.scrollTo).toHaveBeenCalledWith({ top: 0, behavior: "auto" });
});
```

- [x] **Step 3: Run frontend tests and verify RED**

Run:

```bash
npm test -- app/components/item-detail-peek.test.tsx app/components/wiki-search.test.tsx
```

Expected: `ItemDetailPeek` does not exist and WikiSearch still renders the modal.

- [x] **Step 4: Move the detail shell and implement drawer layout**

Move existing summary/crafting/wiki routing into `item-detail-peek.tsx`. Keep
the focus trap, body scroll lock, Escape handling, overlay click, and focus
restoration. Use this shell shape:

```tsx
<div className="fixed inset-0 z-50 bg-[#0f1d30]/55 backdrop-blur-[2px]" onClick={overlayClose}>
  <section
    ref={dialogRef}
    role="dialog"
    aria-modal="true"
    aria-labelledby={titleId}
    data-placement="right"
    className="ml-auto h-dvh w-full overflow-hidden border-l border-[#c8d3df] bg-[#edf1f5] shadow-[-28px_0_80px_rgba(15,29,48,0.28)] motion-safe:animate-[atlas-peek-in_180ms_ease-out] sm:max-w-[560px] sm:rounded-l-3xl"
  >
    <div className="flex h-full flex-col">
      <header className="shrink-0 border-b border-[#d5dde6] bg-[#f8fafc]">...</header>
      <div ref={bodyRef} data-testid="item-detail-peek-body" className="min-h-0 flex-1 overflow-y-auto overscroll-contain">...</div>
    </div>
  </section>
</div>
```

Use `useEffect(..., [item.id])` to scroll the body to top. The header displays
Mob and Animals chips from the typed Mob contract. The panel is full width on
mobile and max 560px on `sm` and above.

- [x] **Step 5: Add the shared keyframe and route WikiSearch**

Add:

```css
@keyframes atlas-peek-in {
  from { opacity: 0.72; transform: translateX(28px); }
  to { opacity: 1; transform: translateX(0); }
}
```

Replace the `ItemDetailModal` import/render with `ItemDetailPeek`. Delete the
old component and test after all imports move. Do not add another client
boundary; `wiki-search.tsx` already begins with `"use client"`.

- [x] **Step 6: Run checks and commit Task 6**

Run:

```bash
npm test -- app/components/item-detail-peek.test.tsx app/components/wiki-search.test.tsx app/components/mob-sections.test.tsx
npx tsc --noEmit
npm run lint
```

Expected: tests pass, TypeScript exits 0, and ESLint exits 0.

```bash
git add app/components/item-detail-peek.tsx app/components/item-detail-peek.test.tsx app/components/wiki-search.tsx app/components/wiki-search.test.tsx app/globals.css app/components/item-detail-modal.tsx app/components/item-detail-modal.test.tsx
git commit -m "feat: open item details in a right side peek"
```

---

### Task 7: Discover 34 pages, crawl the 28 DST pages, review Notes, regenerate, and verify

**Files:**
- Modify: `data/manual/category-prefab-mappings/animals.json`
- Modify: `data/manual/category-note-summaries/animals.json`
- Create: `data/generated/categories/animals.json`
- Create: `data/generated/category-crawl-audits/animals.json`
- Create: `data/generated/category-note-review/animals.json`
- Create: `public/assets/wiki-categories/animals/`
- Modify: `public/data/items.json`
- Modify: `docs/wiki-crawler.md`
- Modify: `docs/data-extraction.md`

**Interfaces:**
- Consumes: completed category infrastructure and normalizer.
- Produces: reviewed real Animals artifacts and documented repeatable commands.

- [ ] **Step 1: Run all focused tests before network work**

Run:

```bash
python3 -m unittest tests.crawl_wiki.test_category_config tests.crawl_wiki.test_category_seeds tests.crawl_wiki.test_client tests.crawl_wiki.test_storage tests.crawl_wiki.test_crawler tests.crawl_wiki.test_cli -v
python3 -m unittest tests.extract.test_category_mobs tests.extract.test_category_notes tests.extract.test_category_merge tests.extract.test_category_assets tests.extract.test_export_items tests.extract.test_export_validate -v
npm test -- app/lib/item-catalog.test.ts app/components/mob-sections.test.tsx app/components/item-detail-peek.test.tsx app/components/wiki-search.test.tsx
```

Expected: PASS.

- [ ] **Step 2: Crawl Animals to completion**

Run repeatedly until no pending pages/images remain:

```bash
python3 -m tools.crawl_wiki.cli --profile category --category animals --page-budget 100
```

Expected final summary: `pages=28`, `failures=0`, `pending_pages=0`, and
`pending_images=0`. Verify the manifest status is `complete`, the direct
namespace-0 discovery count is 34, exactly six direct seeds are excluded with
their reviewed `non_dst:*` reasons, exactly 28 seeds are queued, and all five
category children are excluded by namespace. Confirm no page detail or image
request exists for `Blue Whale`, `White Whale`, `Wildbore`, `Peagawk`, `Pog`,
or `Glowfly`. If membership or exclusion drift occurs, stop and update neither
the config nor generated output without a separate review.

- [ ] **Step 3: Generate and complete the note review queue**

Run:

```bash
python3 -m tools.extract.cli category-notes --category animals
```

For every row in `data/generated/category-note-review/animals.json` with source
text, read the source plus locator, write a one- or two-idea Vietnamese summary
under the matching page ID in
`data/manual/category-note-summaries/animals.json`, copy the exact
`source_sha256`, and set `reviewed` to `true`. Re-run the command; expected
review summary is `unreviewed=0`.

- [ ] **Step 4: Resolve only explicit prefab mapping gaps**

Run normalization once:

```bash
python3 -m tools.extract.cli normalize-category --category animals
```

If the command reports pages without verified spawn codes, inspect each raw
page and the canonical game catalog, then add only exact page-ID mappings to
`data/manual/category-prefab-mappings/animals.json`. Never use display-name
similarity. Re-run until the command reports `pages=28`, `codes_unresolved=0`,
and `code_conflicts=0`.

- [ ] **Step 5: Export, validate, and inspect cleanup recommendations**

Run:

```bash
python3 -m tools.extract.cli export
python3 -m tools.extract.cli validate
```

Expected: validation exits 0 and `category_export_errors` is empty. Inspect all
audit rows whose action is `flagged` or `duplicate_hidden`; confirm they remain
non-public but present in the audit and no files/records were deleted.

- [ ] **Step 6: Document the reusable runbook**

Add the exact category commands, separate output/checkpoint paths, continuation
behavior, 34-page discovery guard, explicit non-DST exclusion review, 28-page
queue/publication guard, note review, mapping review, export, retry, and
validation lifecycle to `docs/wiki-crawler.md` and `docs/data-extraction.md`.
Include a future-category example that adds a config key without copying the
crawler.

- [ ] **Step 7: Run the complete verification suite**

Run:

```bash
python3 -m unittest discover -s tests -v
npm test
npx tsc --noEmit
npm run lint
npm run build
python3 -m tools.extract.cli validate
git diff --check
```

Expected: all Python/Vitest tests pass, TypeScript exits 0, ESLint exits 0,
Next.js production build succeeds, catalog validation exits 0, and diff check
prints no errors.

- [ ] **Step 8: Commit Task 7**

```bash
git add data/manual/category-prefab-mappings/animals.json data/manual/category-note-summaries/animals.json data/generated/categories/animals.json data/generated/category-crawl-audits/animals.json data/generated/category-note-review/animals.json public/assets/wiki-categories/animals public/data/items.json docs/wiki-crawler.md docs/data-extraction.md
git commit -m "data: publish reviewed DST animals category"
```

Record the final audit summary in the handoff: 34 direct namespace-0 pages
discovered, six reviewed non-DST pages excluded before detail crawl, five
subcategory children excluded, 28 DST canonical pages published, prefab-code
count, multi-variant page count, created/merged/kept/flagged/hidden counts,
reviewed note count, and test/build/validation results.
