# Don't Starve Wiki Crawler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a resumable, unauthenticated MediaWiki Action API crawler that exports the latest Main, Category, and File pages to indexed JSONL and downloads original images.

**Architecture:** A standard-library Python package separates deterministic parsing, retrying HTTP transport, SQLite/JSONL persistence, crawl orchestration, and CLI validation. SQLite holds resumable queue state while finalized JSONL files are compacted by stable logical keys, indexed by byte offset, and checksummed in a manifest.

**Tech Stack:** Python 3 standard library (`argparse`, `urllib`, `sqlite3`, `html.parser`, `hashlib`, `unittest`), MediaWiki Action API, JSONL.

## Global Constraints

- Base URL defaults to `https://dontstarve.wiki.gg/` and requires no authentication.
- Crawl namespace IDs are exactly `0`, `14`, and `6` unless the user supplies a supported subset.
- Only the latest revision is exported.
- Every page record includes wikitext, rendered HTML, normalized plain text, categories, links, images, redirects, and revision metadata.
- Images use the API's original URL and content-addressed SHA-256 local paths; thumbnails are not accepted.
- Default request delay is `0.5` seconds, timeout is `30` seconds, maximum attempts is `5`, and Action API requests include `maxlag=5`.
- The implementation adds no third-party Python dependency and does not modify existing extraction or Next.js behavior.
- Preserve all pre-existing uncommitted workspace changes.

---

## File Map

- Create `tools/crawl_wiki/__init__.py`: package marker and public version.
- Create `tools/crawl_wiki/models.py`: namespace constants, typed record contracts, crawl summary.
- Create `tools/crawl_wiki/parser.py`: base/page URL normalization, HTML-to-text, API response normalization, image suffix selection.
- Create `tools/crawl_wiki/client.py`: rate-limited/retrying Action API and streamed binary HTTP client.
- Create `tools/crawl_wiki/storage.py`: SQLite state, queue transitions, JSONL append/compaction, index and manifest.
- Create `tools/crawl_wiki/crawler.py`: discovery, page export, image export, finalization orchestration.
- Create `tools/crawl_wiki/cli.py`: validated CLI and exit-code mapping.
- Create `tests/crawl_wiki/test_parser.py`: pure parser/model behavior.
- Create `tests/crawl_wiki/test_client.py`: local-server HTTP retry and streaming behavior.
- Create `tests/crawl_wiki/test_storage.py`: resume, deduplication, offsets, manifest behavior.
- Create `tests/crawl_wiki/test_crawler.py`: local MediaWiki fixture end-to-end crawl.
- Create `tests/crawl_wiki/test_cli.py`: CLI validation and exit codes.
- Create `docs/wiki-crawler.md`: operator instructions and output contract.
- Modify `.gitignore`: exclude generated `data/crawled/` output.

---

### Task 1: Deterministic models and parsing

**Files:**

- Create: `tools/crawl_wiki/__init__.py`
- Create: `tools/crawl_wiki/models.py`
- Create: `tools/crawl_wiki/parser.py`
- Create: `tests/crawl_wiki/__init__.py`
- Create: `tests/crawl_wiki/test_parser.py`

**Interfaces:**

- Produces: `SUPPORTED_NAMESPACES: Mapping[int, str]`
- Produces: `CrawlSummary(pages, images, links, failures)`
- Produces: `normalize_base_url(value: str) -> str`
- Produces: `canonical_page_url(base_url: str, title: str) -> str`
- Produces: `html_to_text(value: str) -> str`
- Produces: `safe_image_extension(url: str, mime: str | None) -> str`
- Produces: `normalize_page(query_page, parsed, base_url, fetched_at, allowed_namespaces) -> tuple[dict, list[dict], set[str]]`

- [ ] **Step 1: Write failing parser tests**

```python
import unittest

from tools.crawl_wiki.parser import (
    canonical_page_url,
    html_to_text,
    normalize_base_url,
    normalize_page,
    safe_image_extension,
)


class ParserTests(unittest.TestCase):
    def test_normalizes_base_and_unicode_page_urls(self):
        self.assertEqual(normalize_base_url("https://dontstarve.wiki.gg"), "https://dontstarve.wiki.gg/")
        self.assertEqual(
            canonical_page_url("https://dontstarve.wiki.gg/", "Category:Don't Starve Together"),
            "https://dontstarve.wiki.gg/wiki/Category:Don%27t_Starve_Together",
        )

    def test_rejects_non_http_base_urls(self):
        with self.assertRaisesRegex(ValueError, "http"):
            normalize_base_url("file:///tmp/wiki")

    def test_converts_rendered_html_to_normalized_visible_text(self):
        value = "<h2>Stats &amp; notes</h2><script>bad()</script><p>Health: <b>150</b></p>"
        self.assertEqual(html_to_text(value), "Stats & notes\nHealth: 150")

    def test_chooses_safe_extension_from_mime_before_url(self):
        self.assertEqual(safe_image_extension("https://cdn/x.php?name=x.exe", "image/png"), ".png")
        self.assertEqual(safe_image_extension("https://cdn/x.WEBP", None), ".webp")
        self.assertEqual(safe_image_extension("https://cdn/no-suffix", None), ".bin")

    def test_normalizes_page_links_images_redirect_and_content(self):
        query_page = {
            "pageid": 7,
            "ns": 0,
            "title": "Wilson",
            "redirect": True,
            "revisions": [{
                "revid": 11,
                "timestamp": "2026-07-01T10:00:00Z",
                "sha1": "abc",
                "contentmodel": "wikitext",
                "slots": {"main": {"content": "#REDIRECT [[Wilson (DST)]]"}},
            }],
        }
        parsed = {
            "title": "Wilson",
            "displaytitle": "<b>Wilson</b>",
            "text": "<p>Redirect page</p>",
            "links": [
                {"ns": 0, "title": "Wilson (DST)", "exists": True},
                {"ns": 10, "title": "Template:Infobox"},
            ],
            "categories": [{"category": "Characters"}],
            "images": ["Wilson.png", "Wilson.png"],
        }
        page, links, images = normalize_page(
            query_page, parsed, "https://dontstarve.wiki.gg/", "2026-07-15T00:00:00Z", {0, 6, 14}
        )
        self.assertEqual(page["redirect_target"], "Wilson (DST)")
        self.assertEqual(page["categories"], ["Category:Characters"])
        self.assertEqual(page["images"], ["File:Wilson.png"])
        self.assertEqual(page["plain_text"], "Redirect page")
        self.assertEqual([link["in_scope"] for link in links], [True, False])
        self.assertEqual(images, {"File:Wilson.png"})
```

- [ ] **Step 2: Run tests and verify RED**

Run: `python -m unittest tests.crawl_wiki.test_parser -v`

Expected: `ModuleNotFoundError: No module named 'tools.crawl_wiki'`.

- [ ] **Step 3: Implement models and parser**

`models.py` defines immutable namespace names `{0: "Main", 6: "File", 14: "Category"}`, `SCHEMA_VERSION = 1`, and a frozen `CrawlSummary` dataclass with integer fields and `exit_code` returning `1` when failures are non-zero.

`parser.py` MUST implement the interfaces above with these concrete rules:

```python
def normalize_base_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("base URL must use http or https")
    path = parsed.path.rstrip("/") + "/"
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


def canonical_page_url(base_url: str, title: str) -> str:
    slug = urllib.parse.quote(title.replace(" ", "_"), safe="/:()")
    return urllib.parse.urljoin(normalize_base_url(base_url), "wiki/" + slug)


def safe_image_extension(url: str, mime: str | None) -> str:
    mime_extensions = {
        "image/png": ".png", "image/jpeg": ".jpg", "image/gif": ".gif",
        "image/webp": ".webp", "image/svg+xml": ".svg", "image/avif": ".avif",
    }
    if mime and mime.lower().split(";", 1)[0] in mime_extensions:
        return mime_extensions[mime.lower().split(";", 1)[0]]
    suffix = pathlib.PurePosixPath(urllib.parse.urlsplit(url).path).suffix.lower()
    return suffix if suffix in set(mime_extensions.values()) else ".bin"
```

Use an `HTMLParser` subclass that increments a suppression depth for `script`, `style`, `noscript`, and `template`; inserts line boundaries around headings, paragraphs, list items, table rows, and `br`; decodes character references through `HTMLParser(convert_charrefs=True)`; strips each line; collapses internal whitespace; and removes repeated blank lines.

`normalize_page` validates one revision and its main slot content, builds sorted unique category/link/image titles, treats an absent `exists` key as `False`, prefixes category/image names when the API omits the namespace, derives redirect target from the first parsed link only when `query_page["redirect"]` is truthy, and returns page/link/image values matching the design schema.

- [ ] **Step 4: Run parser tests and verify GREEN**

Run: `python -m unittest tests.crawl_wiki.test_parser -v`

Expected: 5 tests pass.

- [ ] **Step 5: Commit Task 1**

```bash
git add tools/crawl_wiki/__init__.py tools/crawl_wiki/models.py tools/crawl_wiki/parser.py tests/crawl_wiki/__init__.py tests/crawl_wiki/test_parser.py
git commit -m "feat: add wiki crawler record parsing"
```

---

### Task 2: Rate-limited MediaWiki HTTP client

**Files:**

- Create: `tools/crawl_wiki/client.py`
- Create: `tests/crawl_wiki/test_client.py`

**Interfaces:**

- Consumes: `normalize_base_url`
- Produces: `ClientError(message, retryable, status=None, code=None)`
- Produces: `DownloadResult(final_url, byte_size, sha256)`
- Produces: `MediaWikiClient.list_allpages(namespace, continuation=None) -> (list[dict], str | None)`
- Produces: `MediaWikiClient.get_page(page_id) -> dict`
- Produces: `MediaWikiClient.parse_page(page_id) -> dict`
- Produces: `MediaWikiClient.get_image_info(title) -> dict`
- Produces: `MediaWikiClient.download(url, destination: Path) -> DownloadResult`

- [ ] **Step 1: Write failing client integration tests**

Create a local `ThreadingHTTPServer` handler whose `/api.php` route returns `503` once and then JSON, returns a MediaWiki `maxlag` error once for `action=parse`, supports `list=allpages`, `prop=revisions`, and `prop=imageinfo`, and whose `/asset.png` route returns `b"png-bytes"`. Assertions MUST verify:

```python
with WikiServer() as server:
    sleeps = []
    client = MediaWikiClient(server.base_url, delay=0, timeout=2, max_attempts=3, sleep=sleeps.append, jitter=lambda: 0)
    pages, token = client.list_allpages(0)
    self.assertEqual(pages, [{"pageid": 1, "ns": 0, "title": "Wilson"}])
    self.assertEqual(token, "next-token")
    self.assertGreaterEqual(server.request_counts["allpages"], 2)

    parsed = client.parse_page(1)
    self.assertEqual(parsed["title"], "Wilson")
    self.assertTrue(sleeps)

    target = Path(tempdir) / "asset.part"
    result = client.download(server.base_url + "asset.png", target)
    self.assertEqual(target.read_bytes(), b"png-bytes")
    self.assertEqual(result.byte_size, 9)
    self.assertEqual(result.sha256, hashlib.sha256(b"png-bytes").hexdigest())
```

Add a second test where the server always returns HTTP `404`; assert `ClientError.retryable is False` after exactly one request. Add a third test where `download` redirects to an `http://` final URL; assert the client rejects it because original image downloads require a final HTTPS URL, while local test URLs are allowed only through constructor option `require_https_downloads=False`.

- [ ] **Step 2: Run tests and verify RED**

Run: `python -m unittest tests.crawl_wiki.test_client -v`

Expected: import failure for `tools.crawl_wiki.client`.

- [ ] **Step 3: Implement the client**

Use `urllib.request.build_opener()` and inject `opener`, monotonic clock, sleep, and jitter callables. Before each request, wait until `last_request_at + delay`. Add `User-Agent` and `Accept` headers.

All Action API calls pass:

```python
{"format": "json", "formatversion": 2, "maxlag": 5}
```

`list_allpages` passes `action=query`, `list=allpages`, `apnamespace`, `aplimit=max`, and optional `apcontinue`; it returns `query.allpages` plus `continue.apcontinue`.

`get_page` passes `action=query`, `pageids`, `prop=info|revisions`, `rvprop=ids|timestamp|sha1|content|contentmodel`, and `rvslots=main`; it rejects missing pages/revisions.

`parse_page` passes `action=parse`, `pageid`, and `prop=text|links|categories|images|displaytitle|properties`.

`get_image_info` passes `action=query`, `titles`, `prop=imageinfo`, and `iiprop=url|size|mime|sha1`; it returns the first `imageinfo` entry and annotates it with page ID/title.

The request loop retries `URLError`, timeout, HTTP `429`, HTTP `500..599`, and API code `maxlag`. It uses a numeric `Retry-After` when present, otherwise `min(60.0, 2 ** (attempt - 1)) + jitter()`. Other HTTP `4xx`, invalid JSON, schema failures, and non-transient API errors raise non-retryable `ClientError`. Exhaustion raises a retryable `ClientError` containing the attempt count.

`download` streams 64 KiB chunks to the provided `.part` destination, computes SHA-256 and byte count, flushes and `os.fsync`s the file, deletes the partial file on failure, and applies the same retry policy. When `require_https_downloads=True`, both requested and final URL schemes must be HTTPS.

- [ ] **Step 4: Run client tests and verify GREEN**

Run: `python -m unittest tests.crawl_wiki.test_client -v`

Expected: all client tests pass with no warnings.

- [ ] **Step 5: Commit Task 2**

```bash
git add tools/crawl_wiki/client.py tests/crawl_wiki/test_client.py
git commit -m "feat: add retrying MediaWiki client"
```

---

### Task 3: Resumable SQLite and JSONL storage

**Files:**

- Create: `tools/crawl_wiki/storage.py`
- Create: `tests/crawl_wiki/test_storage.py`

**Interfaces:**

- Consumes: `SCHEMA_VERSION`, `safe_image_extension`
- Produces: `CrawlStorage(output, base_url, namespaces, fresh=False)` context manager
- Produces: `enqueue_pages`, `claim_page`, `complete_page`, `fail_page`
- Produces: `enqueue_images`, `claim_image`, `commit_image_file`, `complete_image`, `fail_image`
- Produces: `get/set_discovery_token`, `mark_discovery_complete`, `retry_errors`
- Produces: `finalize(options) -> CrawlSummary`

- [ ] **Step 1: Write failing storage tests**

Tests MUST use `tempfile.TemporaryDirectory()` and assert these behaviors:

```python
storage.enqueue_pages([{"pageid": 1, "ns": 0, "title": "Wilson"}])
self.assertEqual(storage.claim_page()["title"], "Wilson")
storage.complete_page(1, page_record, [link_record, link_record], {"File:Wilson.png"})
self.assertIsNone(storage.claim_page())
self.assertEqual(storage.claim_image()["title"], "File:Wilson.png")
```

Close and reopen before completing a claimed second page; assert stale `processing` returns to `pending`. Append a deliberately truncated JSON fragment to `pages.jsonl`, reopen, and assert recovery removes the incomplete tail.

Complete the same page twice through a simulated stale append, finalize, and assert `pages.jsonl` contains exactly one record for the page, `links.jsonl` contains one unique edge, and `index.json` offsets seek to those exact JSON lines.

Write two `.part` files with identical bytes for two File titles, call `commit_image_file` for both, and assert both metadata records use the same `images/original/<sha256>.png` path and only one binary exists.

Finalize and independently calculate SHA-256 for each JSONL file; assert it equals `manifest.json["checksums"]`. Assert an unresolved `fail_page` produces one `errors.jsonl` record and summary/manifest failure count `1`.

- [ ] **Step 2: Run tests and verify RED**

Run: `python -m unittest tests.crawl_wiki.test_storage -v`

Expected: import failure for `tools.crawl_wiki.storage`.

- [ ] **Step 3: Implement storage schema and queue transitions**

Create SQLite tables `metadata`, `page_queue`, `image_queue`, and `errors`. Queue keys are page ID and File title. Each queue stores namespace/title, status, attempts, last error, and record offset. `errors` uses `(stage, subject)` as its primary key.

Opening storage MUST:

1. reject `fresh=True` when `state.sqlite` exists;
2. create output and `images/original` directories;
3. create/migrate schema version 1;
4. verify saved base URL and namespace list match this invocation;
5. reset `processing` rows to `pending`;
6. remove a non-newline-terminated JSONL tail from each output file.

Claims use `BEGIN IMMEDIATE`, select the lexicographically/ID-first pending row, update it to `processing`, increment attempts, commit, and return a dictionary. Enqueues use `INSERT ... ON CONFLICT DO UPDATE` without resetting rows already marked `done`.

Append records through one deterministic encoder:

```python
def encode_json_line(record: Mapping[str, object]) -> bytes:
    return (json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
```

Flush and `os.fsync` before committing a queue row as done. Store current offset. Completion enqueues image titles in the same SQLite transaction that marks the page done.

- [ ] **Step 4: Implement compaction, index, errors, and manifest**

Finalization reads each JSONL file and keeps the last record by these stable keys:

- pages: integer `page_id`;
- images: string `title`;
- links: `(source_page_id, target_namespace, target_title)`.

Rewrite each file atomically in sorted-key order, recording byte offsets while writing. Materialize unresolved SQLite errors into `errors.jsonl` sorted by `(stage, subject)`. Write `index.json` atomically with `pages.by_id`, `pages.by_title`, and `images.by_title` offset maps. Write `manifest.json` last with counts, options, run timestamps, unresolved failures, and SHA-256 of all four JSONL files.

`commit_image_file(part_path, sha256, url, mime)` computes the safe extension, reuses an existing destination, otherwise atomically replaces it, and returns a path relative to the output directory.

- [ ] **Step 5: Run storage tests and verify GREEN**

Run: `python -m unittest tests.crawl_wiki.test_storage -v`

Expected: all storage tests pass.

- [ ] **Step 6: Commit Task 3**

```bash
git add tools/crawl_wiki/storage.py tests/crawl_wiki/test_storage.py
git commit -m "feat: add resumable crawler storage"
```

---

### Task 4: Discovery, page crawl, image crawl, and end-to-end resume

**Files:**

- Create: `tools/crawl_wiki/crawler.py`
- Create: `tests/crawl_wiki/test_crawler.py`

**Interfaces:**

- Consumes: `MediaWikiClient`, `CrawlStorage`, `normalize_page`, `safe_image_extension`
- Produces: `WikiCrawler(client, storage, namespaces, skip_images=False, max_pages=None, clock=utc_now)`
- Produces: `WikiCrawler.run(options: Mapping[str, object]) -> CrawlSummary`

- [ ] **Step 1: Write failing end-to-end fixture test**

Create a local MediaWiki HTTP fixture with two `allpages` continuation responses: Main contains `Wilson`, Category contains an orphan `Category:Characters`, and File contains `File:Wilson.png`. The fixture returns latest revisions, parse payloads containing a red link and an out-of-scope Template link, imageinfo pointing to the local binary, and one duplicate reference to the same image.

Run the crawler against the fixture with `delay=0`, `require_https_downloads=False`, and a temporary output directory. Assert:

```python
self.assertEqual(summary.pages, 3)
self.assertEqual(summary.images, 1)
self.assertEqual(summary.failures, 0)
self.assertEqual({row["title"] for row in pages}, {"Wilson", "Category:Characters", "File:Wilson.png"})
self.assertEqual(pages_by_title["Wilson"]["wikitext"], "'''Wilson''' is a character.")
self.assertIn("Wilson is a character.", pages_by_title["Wilson"]["plain_text"])
self.assertTrue(any(link["target_title"] == "Template:Infobox" and not link["in_scope"] for link in links))
self.assertTrue(any(link["target_title"] == "Missing page" and not link["exists"] for link in links))
self.assertEqual(len(list((output / "images/original").iterdir())), 1)
```

Add a resume test: configure the fixture to return a permanent parse failure for the second page on the first run, assert unrelated work completes and exit summary has one failure, then clear the failure, call `storage.retry_errors()`, rerun, and assert all three logical page records exist exactly once and the unresolved error count is zero.

- [ ] **Step 2: Run test and verify RED**

Run: `python -m unittest tests.crawl_wiki.test_crawler -v`

Expected: import failure for `tools.crawl_wiki.crawler`.

- [ ] **Step 3: Implement discovery and page processing**

Discovery loops namespace IDs in the configured order. For each namespace, resume from `storage.get_discovery_token(namespace)`, call `client.list_allpages`, enqueue returned pages, save continuation after every response, and mark complete when continuation is absent. `max_pages` caps newly enqueued page IDs globally without marking an incomplete namespace as fully discovered.

Page processing repeatedly claims one page. For each claim:

1. call `get_page(page_id)` and `parse_page(page_id)`;
2. normalize the page and relationships with one `fetched_at` timestamp;
3. add the File page's own title to the image queue when namespace is 6;
4. append/commit page and link records and image titles;
5. on `ClientError`, record stage `page`, retryability, status/code, attempts, and continue to the next queue item.

The loop MUST not immediately reclaim failed rows. Only `--retry-errors` resets them.

- [ ] **Step 4: Implement image processing and finalization**

Unless `skip_images` is set, repeatedly claim an image title, fetch imageinfo, create a unique `.part` path under the output directory, download it, commit the content-addressed file, build the image metadata record, and complete the queue item. Remove orphan `.part` files after errors.

Always call `storage.finalize(options)` after queues drain, including when item failures occurred. Let `KeyboardInterrupt` propagate so the CLI can return 130, but close storage through its context manager. Fatal storage/schema exceptions propagate and do not finalize potentially corrupt output.

- [ ] **Step 5: Run end-to-end tests and verify GREEN**

Run: `python -m unittest tests.crawl_wiki.test_crawler -v`

Expected: all end-to-end and resume tests pass.

- [ ] **Step 6: Commit Task 4**

```bash
git add tools/crawl_wiki/crawler.py tests/crawl_wiki/test_crawler.py
git commit -m "feat: crawl wiki pages and original images"
```

---

### Task 5: CLI, operator documentation, and full verification

**Files:**

- Create: `tools/crawl_wiki/cli.py`
- Create: `tests/crawl_wiki/test_cli.py`
- Create: `docs/wiki-crawler.md`
- Modify: `.gitignore`

**Interfaces:**

- Consumes: all crawler interfaces.
- Produces: `build_parser() -> argparse.ArgumentParser`
- Produces: `main(argv: Sequence[str] | None = None) -> int`

- [ ] **Step 1: Write failing CLI tests**

Tests patch only the top-level `run_crawl(args)` seam, not client behavior. Assert parser defaults are base URL `https://dontstarve.wiki.gg/`, output `data/crawled/dontstarve-wiki`, namespaces `(0, 14, 6)`, delay `0.5`, timeout `30`, and attempts `5`.

Assert these invalid invocations raise argparse exit code `2` before `run_crawl` is called:

```text
--namespaces 0,10
--delay -1
--timeout 0
--max-attempts 0
--max-pages 0
--base-url file:///tmp/wiki
```

Assert summary failures map to exit code `1`, clean summary to `0`, `KeyboardInterrupt` to `130`, and fatal `OSError` to `2` with a concise stderr message.

- [ ] **Step 2: Run CLI tests and verify RED**

Run: `python -m unittest tests.crawl_wiki.test_cli -v`

Expected: import failure for `tools.crawl_wiki.cli`.

- [ ] **Step 3: Implement CLI**

Use `argparse` type functions to validate positive/ non-negative numerics, comma-separated supported namespaces, and normalized base URL. `run_crawl` constructs client/storage/crawler and honors `--fresh`, `--retry-errors`, `--skip-images`, and `--max-pages`. Print one final line:

```text
pages=<n> images=<n> links=<n> failures=<n> output=<absolute-path>
```

Configure logging without page bodies. Add the module guard `raise SystemExit(main())`.

- [ ] **Step 4: Document operation and ignore generated output**

Append `/data/crawled/` to `.gitignore` under the local extraction section. Write `docs/wiki-crawler.md` with prerequisites, default/full command, a three-page smoke command, resume behavior, retry-errors workflow, output file descriptions, exit codes, respectful rate guidance, disk-space warning for all originals, and example JSONL consumption using a streaming Python loop.

- [ ] **Step 5: Run focused crawler suite**

Run: `python -m unittest discover -s tests/crawl_wiki -p 'test_*.py' -v`

Expected: all crawler tests pass with zero errors/failures.

- [ ] **Step 6: Run all Python regression tests**

Run: `python -m unittest discover -s tests -p 'test_*.py' -v`

Expected: all repository Python tests pass with zero errors/failures.

- [ ] **Step 7: Run repository lint and frontend tests**

Run: `npm test`

Expected: Vitest exits 0.

Run: `npm run lint`

Expected: ESLint exits 0 with no new crawler-related issues.

- [ ] **Step 8: Run deterministic local end-to-end crawl**

Run: `python -m unittest tests.crawl_wiki.test_crawler -v`

Expected: fixture crawl, failure isolation, and resumed crawl tests all pass.

- [ ] **Step 9: Run optional live smoke crawl**

Run:

```bash
python -m tools.crawl_wiki.cli \
  --output /tmp/dontstarve-wiki-smoke \
  --max-pages 3 \
  --skip-images \
  --delay 0.5 \
  --fresh
```

Expected when network access is available: exit `0`, `pages=3`, `failures=0`, and a manifest whose page count is 3. If the environment blocks network access, record the exact transport error; deterministic local integration remains the correctness gate.

- [ ] **Step 10: Commit Task 5**

```bash
git add .gitignore tools/crawl_wiki/cli.py tests/crawl_wiki/test_cli.py docs/wiki-crawler.md
git commit -m "feat: ship resumable wiki crawler CLI"
```

---

## Plan Self-Review Results

- Spec coverage: every requirement in the approved design maps to Tasks 1–5.
- Placeholder scan: the plan contains no deferred implementation markers.
- Type consistency: `CrawlSummary`, client methods, storage queue methods, and `WikiCrawler.run` names are consistent across producers and consumers.
- Scope: one independently testable subsystem; no Next.js or existing extraction changes are required.
