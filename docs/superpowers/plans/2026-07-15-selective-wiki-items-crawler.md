# Selective Wiki Items Crawler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a resumable `items` crawl profile that discovers item links only from five approved wiki sections, exports each item's latest detail and normalized recipes, downloads only selected original item icons, and stops after a configurable number of item pages per invocation.

**Architecture:** Keep the existing full-site crawler intact and add a selective discovery path. A standard-library HTML parser extracts visual item links from exact section IDs, a wikitext parser normalizes crafting inputs, and the existing SQLite/JSONL storage gains seed and recipe records plus per-run queue budgets. The HTTP client classifies disconnected sockets as transient so a single closed connection is retried instead of escaping as a fatal raw exception.

**Tech Stack:** Python 3 standard library (`html.parser`, `http.client`, `urllib`, `sqlite3`, `json`, `unittest`), MediaWiki Action API, JSONL.

## Global Constraints

- The approved sources are exactly `Items#Resources-0`, `Items#Craftable_Items-0`, `Items#Food-0`, `Items#By_Crock_Pot_Value-0`, and `Plants#DST-0`.
- Only visual wiki links containing an image inside an approved section become seeds; template, file, category, navigation, and titles ending in ` Filter` are excluded.
- Duplicate links across sections resolve to one page while preserving every source section in the seed record.
- Detail crawling does not recursively enqueue arbitrary links from an item page.
- Each item exports only its latest revision, rendered HTML, wikitext, categories, and link metadata.
- Only the original item icon selected by the source list is downloaded; body galleries and navbox images are not enqueued.
- Recipe output contains infobox crafting inputs and `Recipe` templates whose result matches the current item.
- `--item-budget` defaults to `100` and limits pages processed during one invocation, not the total queue size.
- Output defaults to `data/crawled/dontstarve-items/` for the `items` profile and remains `data/crawled/dontstarve-wiki/` for the full profile.
- Existing full-crawl state and output remain readable and resumable.
- The implementation adds no third-party Python dependency and does not modify Next.js behavior.

---

## File Map

- Create `tools/crawl_wiki/item_seeds.py`: approved source definitions and deterministic HTML seed extraction.
- Create `tools/crawl_wiki/recipes.py`: balanced MediaWiki template parsing and normalized recipe records.
- Modify `tools/crawl_wiki/client.py`: retry disconnected transports and resolve/parse pages by title.
- Modify `tools/crawl_wiki/storage.py`: persist seed metadata, recipes, queue progress, and partial manifests.
- Modify `tools/crawl_wiki/crawler.py`: add selective discovery, page budget, selected-icon enqueueing, and recipe export.
- Modify `tools/crawl_wiki/cli.py`: add `--profile items`, profile-specific output, and `--item-budget`.
- Modify `tools/crawl_wiki/models.py`: report pending page/image counts without breaking existing constructors.
- Create `tests/crawl_wiki/test_item_seeds.py`: exact-section extraction and exclusion coverage.
- Create `tests/crawl_wiki/test_recipes.py`: infobox and matching Recipe template coverage.
- Modify `tests/crawl_wiki/test_client.py`: reproduce `RemoteDisconnected` and title lookup behavior.
- Modify `tests/crawl_wiki/test_crawler.py`: selective local-server integration and resume-by-budget coverage.
- Modify `tests/crawl_wiki/test_cli.py`: profile defaults and argument validation.
- Modify `docs/wiki-crawler.md`: selective operation, output, retry, and resume instructions.

---

### Task 1: Exact-section seed extraction

**Files:**

- Create: `tools/crawl_wiki/item_seeds.py`
- Create: `tests/crawl_wiki/test_item_seeds.py`

**Interfaces:**

- Produces: `ITEM_SOURCE_SECTIONS: Mapping[str, tuple[str, ...]]`
- Produces: `ItemSeed(title, href, icon_title, icon_thumbnail_url, source_sections)`
- Produces: `extract_item_seeds(page_title: str, html: str, base_url: str) -> list[ItemSeed]`
- Produces: `merge_item_seeds(groups: Iterable[Iterable[ItemSeed]]) -> list[ItemSeed]`

- [ ] **Step 1: Write failing exact-section tests**

```python
def test_extracts_only_visual_links_inside_approved_section():
    html = '''
    <a href="/wiki/Outside" title="Outside"><img alt="Outside.png"></a>
    <article id="Resources-0">
      <a href="/wiki/Cut_Grass" title="Cut Grass"><img alt="Cut Grass.png" src="/images/thumb/Cut_Grass.png/40px-Cut_Grass.png"></a>
      <a href="/wiki/Tools_Filter" title="Tools Filter"><img alt="Tools Filter.png"></a>
      <a href="/wiki/Text_Only" title="Text Only">Text only</a>
    </article>
    '''
    seeds = extract_item_seeds("Items", html, "https://dontstarve.wiki.gg/")
    assert [seed.title for seed in seeds] == ["Cut Grass"]
    assert seeds[0].icon_title == "File:Cut Grass.png"
    assert seeds[0].source_sections == ("Items#Resources-0",)

def test_merges_duplicate_links_and_preserves_sections():
    merged = merge_item_seeds([
        [ItemSeed("Berry", "/wiki/Berry", "File:Berry.png", "/thumb-a", ("Items#Food-0",))],
        [ItemSeed("Berry", "/wiki/Berry", "File:Berry.png", "/thumb-b", ("Items#By_Crock_Pot_Value-0",))],
    ])
    assert len(merged) == 1
    assert merged[0].source_sections == (
        "Items#By_Crock_Pot_Value-0",
        "Items#Food-0",
    )
```

- [ ] **Step 2: Run tests and verify RED**

Run: `python3 -m unittest tests.crawl_wiki.test_item_seeds -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'tools.crawl_wiki.item_seeds'`.

- [ ] **Step 3: Implement the minimal parser**

Use `HTMLParser(convert_charrefs=True)` with an element stack. Enter capture mode only while an element whose `id` is approved for the current page is open. Track each `/wiki/` anchor, mark it visual when a nested `img` occurs, derive `File:<alt>` only when the alt text has a known image suffix, normalize the thumbnail with `urljoin`, and emit the anchor on close. Reject titles containing a namespace colon, titles ending in ` Filter`, missing titles, fragment-only links, and links without a nested image. Sort by `(title.casefold(), title, href)` and merge by canonical href.

- [ ] **Step 4: Run tests and verify GREEN**

Run: `python3 -m unittest tests.crawl_wiki.test_item_seeds -v`

Expected: 2 tests pass.

- [ ] **Step 5: Commit Task 1**

```bash
git add tools/crawl_wiki/item_seeds.py tests/crawl_wiki/test_item_seeds.py
git commit -m "feat: extract selective wiki item seeds"
```

---

### Task 2: Recipe normalization

**Files:**

- Create: `tools/crawl_wiki/recipes.py`
- Create: `tests/crawl_wiki/test_recipes.py`

**Interfaces:**

- Produces: `extract_recipes(page_id: int, title: str, wikitext: str) -> list[dict[str, object]]`

- [ ] **Step 1: Write failing recipe tests**

```python
def test_extracts_infobox_ingredients_as_product_recipe():
    text = """{{Object Infobox
    |ingredient1 = Rotten Egg|multiplier1 = 1
    |ingredient2 = Charcoal|multiplier2 = 2
    |tab = Science|tier = 2}}
    """
    records = extract_recipes(7, "Gunpowder", text)
    assert records == [{
        "schema_version": 1,
        "page_id": 7,
        "result": "Gunpowder",
        "source": "Object Infobox",
        "variant": "base",
        "ingredients": [
            {"title": "Rotten Egg", "count": 1.0},
            {"title": "Charcoal", "count": 2.0},
        ],
        "station": None,
        "tab": "Science",
        "tier": "2",
        "dlc": None,
        "character": None,
        "note": None,
    }]

def test_keeps_only_recipe_templates_that_create_current_page():
    text = """
    {{Recipe|item1=Meats|item2=Filler|count2=3|tool=Crock Pot|result=Meatballs}}
    {{Recipe|item1=Meatballs|item2=Twigs|result=Wet Goop}}
    """
    records = extract_recipes(9, "Meatballs", text)
    assert len(records) == 1
    assert records[0]["ingredients"] == [
        {"title": "Meats", "count": 1.0},
        {"title": "Filler", "count": 3.0},
    ]
    assert records[0]["station"] == "Crock Pot"
```

- [ ] **Step 2: Run tests and verify RED**

Run: `python3 -m unittest tests.crawl_wiki.test_recipes -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'tools.crawl_wiki.recipes'`.

- [ ] **Step 3: Implement balanced template parsing**

Scan `{{...}}` using brace depth so nested `Pic` templates do not truncate an outer template. Split template fields only on top-level `|` and split keys on the first top-level `=`. Normalize wiki links to their display/target text, strip simple nested formatting, convert numeric counts to `float`, default missing counts to `1.0`, and sort ingredients by numeric suffix. Emit one infobox record per ingredient suffix variant and one `Recipe` record only when normalized `result` equals normalized current title. Deduplicate records by canonical JSON serialization.

- [ ] **Step 4: Run tests and verify GREEN**

Run: `python3 -m unittest tests.crawl_wiki.test_recipes -v`

Expected: 2 tests pass.

- [ ] **Step 5: Commit Task 2**

```bash
git add tools/crawl_wiki/recipes.py tests/crawl_wiki/test_recipes.py
git commit -m "feat: normalize wiki item recipes"
```

---

### Task 3: Retry closed connections and add title APIs

**Files:**

- Modify: `tools/crawl_wiki/client.py`
- Modify: `tests/crawl_wiki/test_client.py`

**Interfaces:**

- Produces: `MediaWikiClient.parse_page_by_title(title: str) -> dict`
- Produces: `MediaWikiClient.resolve_titles(titles: Sequence[str]) -> list[dict]`

- [ ] **Step 1: Write a failing `RemoteDisconnected` regression test**

```python
def test_retries_remote_disconnected_api_request():
    opener = DisconnectOnceOpener({
        "query": {"allpages": [{"pageid": 1, "ns": 0, "title": "Wilson"}]}
    })
    client = MediaWikiClient(
        "https://dontstarve.wiki.gg/", delay=0, max_attempts=2,
        opener=opener, sleep=lambda value: None, jitter=lambda: 0,
    )
    pages, _ = client.list_allpages(0)
    assert pages[0]["title"] == "Wilson"
    assert opener.attempts == 2
```

The fake opener raises `http.client.RemoteDisconnected("Remote end closed connection without response")` on its first call and returns a context-managed byte response on its second call.

- [ ] **Step 2: Run the regression test and verify RED**

Run: `python3 -m unittest tests.crawl_wiki.test_client.ClientTests.test_retries_remote_disconnected_api_request -v`

Expected: ERROR with the uncaught `http.client.RemoteDisconnected` message.

- [ ] **Step 3: Implement transient connection classification**

Import `http.client` and catch `(urllib.error.URLError, TimeoutError, socket.timeout, ConnectionError, http.client.RemoteDisconnected)` in Action API requests. Convert the raw transport exception to retryable `ClientError`, apply existing backoff, and preserve the final attempt behavior. Add `parse_page_by_title` using `action=parse&page=<title>` and `resolve_titles` using batches of at most 50 titles with `action=query`, `titles` joined by `|`, `prop=info`, and `redirects=1`; reject malformed responses.

- [ ] **Step 4: Run client tests and verify GREEN**

Run: `python3 -m unittest tests.crawl_wiki.test_client -v`

Expected: all client tests pass.

- [ ] **Step 5: Commit Task 3**

```bash
git add tools/crawl_wiki/client.py tests/crawl_wiki/test_client.py
git commit -m "fix: retry disconnected wiki requests"
```

---

### Task 4: Selective storage and budgeted orchestration

**Files:**

- Modify: `tools/crawl_wiki/models.py`
- Modify: `tools/crawl_wiki/storage.py`
- Modify: `tools/crawl_wiki/crawler.py`
- Modify: `tests/crawl_wiki/test_storage.py`
- Modify: `tests/crawl_wiki/test_crawler.py`

**Interfaces:**

- Produces: `CrawlStorage.save_seeds(seeds: Iterable[ItemSeed]) -> None`
- Produces: `CrawlStorage.seed_for_title(title: str) -> dict | None`
- Produces: `CrawlStorage.complete_page(..., recipe_records=()) -> None`
- Produces: `SelectiveItemsCrawler(client, storage, item_budget, clock).run(options) -> CrawlSummary`

- [ ] **Step 1: Write failing storage and integration tests**

Storage assertions:

```python
storage.save_seeds([ItemSeed("Cut Grass", "/wiki/Cut_Grass", "File:Cut Grass.png", "https://cdn/thumb.png", ("Items#Resources-0",))])
assert storage.seed_for_title("Cut Grass")["icon_title"] == "File:Cut Grass.png"
```

Local-server integration assertions:

```python
first = SelectiveItemsCrawler(client, storage, item_budget=1, clock=clock).run({"profile": "items"})
assert first.pages == 1
assert first.pending_pages == 1
assert read_titles(output / "pages.jsonl") == ["Cut Grass"]
assert read_titles(output / "images.jsonl") == ["File:Cut Grass.png"]

second = SelectiveItemsCrawler(client, reopened_storage, item_budget=1, clock=clock).run({"profile": "items"})
assert second.pages == 2
assert second.pending_pages == 0
assert len(read_records(output / "recipes.jsonl")) == 1
```

The fixture source sections contain two visual item links, duplicated across two sections; detail pages include large unrelated `images` arrays. Assert only the two selected icon titles are downloaded.

- [ ] **Step 2: Run tests and verify RED**

Run: `python3 -m unittest tests.crawl_wiki.test_storage tests.crawl_wiki.test_crawler -v`

Expected: FAIL because seed storage, pending summary fields, recipe records, and `SelectiveItemsCrawler` do not exist.

- [ ] **Step 3: Implement seed/recipe storage and partial manifests**

Add `seed_metadata(title PRIMARY KEY, href, icon_title, icon_thumbnail_url, source_sections)` and atomically regenerate `seeds.jsonl` from this table. Add `recipes.jsonl` to compaction with a deterministic identity derived from page ID plus canonical recipe JSON. Extend `complete_page` with default-empty recipe records. Add `pending_page_count()` and `pending_image_count()`. Extend `CrawlSummary` with defaulted pending counts so existing callers remain valid. Write manifest `status: "partial"` while queues remain and `status: "complete"` only when both pending counts are zero.

- [ ] **Step 4: Implement selective orchestration**

`SelectiveItemsCrawler` parses only `Items` and `Plants`, merges seeds, resolves their titles in batches, stores seed metadata, and enqueues namespace-0 pages. It claims at most `item_budget` pages per run. For each page it calls the existing latest-revision and parse APIs, normalizes the detail, exports recipes, and passes only the seed's `icon_title` to `complete_page`; it never passes the page's full parsed image set. After page processing, it drains the selected image queue and finalizes the partial snapshot.

- [ ] **Step 5: Run storage/crawler tests and verify GREEN**

Run: `python3 -m unittest tests.crawl_wiki.test_storage tests.crawl_wiki.test_crawler -v`

Expected: all storage and crawler tests pass.

- [ ] **Step 6: Commit Task 4**

```bash
git add tools/crawl_wiki/models.py tools/crawl_wiki/storage.py tools/crawl_wiki/crawler.py tests/crawl_wiki/test_storage.py tests/crawl_wiki/test_crawler.py
git commit -m "feat: crawl selected wiki items in resumable batches"
```

---

### Task 5: CLI and operator documentation

**Files:**

- Modify: `tools/crawl_wiki/cli.py`
- Modify: `tests/crawl_wiki/test_cli.py`
- Modify: `docs/wiki-crawler.md`

**Interfaces:**

- CLI: `--profile full|items`
- CLI: `--item-budget <positive integer>`

- [ ] **Step 1: Write failing CLI tests**

```python
def test_items_profile_defaults_to_selective_output_and_budget():
    args = build_parser().parse_args(["--profile", "items"])
    assert args.profile == "items"
    assert args.item_budget == 100
    assert resolve_output(args) == Path("data/crawled/dontstarve-items")

def test_rejects_item_budget_for_full_profile():
    with self.assertRaisesRegex(ValueError, "items profile"):
        run_crawl(build_parser().parse_args(["--profile", "full", "--item-budget", "5"]))
```

- [ ] **Step 2: Run CLI tests and verify RED**

Run: `python3 -m unittest tests.crawl_wiki.test_cli -v`

Expected: FAIL because the profile, budget, and output resolver do not exist.

- [ ] **Step 3: Implement CLI routing and docs**

Add profile-specific output resolution, validate incompatible full-only/selective-only options before opening storage, store `profile` in crawl metadata, and route `items` to `SelectiveItemsCrawler`. Print cumulative pages/images, remaining pages/images, failures, and resolved output. Document:

```bash
python3 -m tools.crawl_wiki.cli --profile items --item-budget 100
```

Explain that rerunning the identical command processes the next batch, `--retry-errors` requeues failed entries, source/detail data is latest-revision only, and the old full output is retained as a separate cache.

- [ ] **Step 4: Run CLI tests and verify GREEN**

Run: `python3 -m unittest tests.crawl_wiki.test_cli -v`

Expected: all CLI tests pass.

- [ ] **Step 5: Commit Task 5**

```bash
git add tools/crawl_wiki/cli.py tests/crawl_wiki/test_cli.py docs/wiki-crawler.md
git commit -m "docs: add selective item crawl workflow"
```

---

### Task 6: Full verification and live smoke batch

**Files:**

- Verify only; no production file is created in the repository.

**Interfaces:**

- Consumes the completed CLI and output contract from Tasks 1–5.

- [ ] **Step 1: Run the complete Python suite**

Run: `python3 -m unittest discover -s tests -p 'test_*.py' -v`

Expected: exit `0`, no failures or errors.

- [ ] **Step 2: Run a live one-item smoke batch**

Run:

```bash
python3 -m tools.crawl_wiki.cli \
  --profile items \
  --item-budget 1 \
  --output /tmp/dontstarve-items-smoke \
  --delay 0.5 \
  --fresh
```

Expected: exit `0`, cumulative pages `1`, one or zero selected original icons depending on source metadata, pending pages greater than zero, and `manifest.json` status `partial`.

- [ ] **Step 3: Verify resume with a second one-item batch**

Run the same command without `--fresh`.

Expected: cumulative pages `2`, no duplicate page IDs in `pages.jsonl`, and pending pages decreases by one.

- [ ] **Step 4: Inspect output contract**

Run:

```bash
python3 -m json.tool /tmp/dontstarve-items-smoke/manifest.json
python3 -m json.tool /tmp/dontstarve-items-smoke/index.json
wc -l /tmp/dontstarve-items-smoke/seeds.jsonl /tmp/dontstarve-items-smoke/pages.jsonl /tmp/dontstarve-items-smoke/recipes.jsonl /tmp/dontstarve-items-smoke/images.jsonl
```

Expected: valid JSON manifests/indexes, stable seed count, two page rows, and no unexpected bulk image download.

- [ ] **Step 5: Commit any verification-only corrections**

If smoke verification exposed a defect, repeat RED → GREEN for that defect and commit only the correction. If no correction is needed, do not create an empty commit.

