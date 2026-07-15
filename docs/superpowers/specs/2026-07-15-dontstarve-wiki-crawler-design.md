# Don't Starve Wiki Crawler Design

## Goal

Build a resumable Python crawler for `https://dontstarve.wiki.gg/` that exports the latest public content from the Main, Category, and File namespaces as streaming JSONL and downloads every original image.

## Scope

The crawler MUST:

- use the public, unauthenticated MediaWiki Action API;
- enumerate namespaces `0` (Main), `14` (Category), and `6` (File), including orphan pages;
- capture only the latest revision of each page;
- store source wikitext, MediaWiki-rendered HTML, and normalized plain text;
- store categories, embedded images, redirects, canonical URLs, and every internal link exposed by the parser;
- record links to namespaces outside the crawl scope without fetching those target pages;
- fetch metadata for File pages and download the original binary, never a thumbnail;
- stream records to JSONL, generate a lookup index and manifest, and resume safely after interruption;
- avoid duplicate page records and duplicate image content across resumed runs;
- continue past isolated permanent failures, record them, and return a non-zero exit status when unresolved failures remain.

Revision history, external pages, Talk/User/Template/Module/Help content, browser-rendered JavaScript, and offline HTML mirroring are out of scope.

## Architecture

The implementation lives in `tools/crawl_wiki/` and uses only the Python standard library. Clear module boundaries keep network behavior, parsing, persistence, orchestration, and the command-line interface independently testable.

- `client.py` owns Action API and binary HTTP requests, MediaWiki continuation, timeouts, `maxlag`, rate limiting, retries, and response validation.
- `models.py` defines namespace constants and the page, link, image, and error record shapes.
- `parser.py` normalizes titles and URLs and converts rendered HTML into plain text while excluding non-content script/style markup.
- `storage.py` owns JSONL append operations, SQLite crawl state, content-addressed image paths, atomic metadata files, and final indexes.
- `crawler.py` enumerates pages, fetches revision and parsed content, schedules images, downloads files, and finalizes the run.
- `cli.py` validates arguments, constructs the crawler, handles interruption, prints a summary, and returns a meaningful exit code.

The existing extraction and Next.js code remains untouched. In particular, the pre-existing uncommitted change in `app/components/item-detail-modal.tsx` is outside this feature.

## MediaWiki Data Flow

1. Call `action=query&list=allpages` independently for namespace IDs `0`, `14`, and `6`, following `continue` until exhaustion. Persist each page ID/title in the SQLite queue as it is discovered.
2. Claim pending pages from the queue. Fetch latest revision metadata and wikitext using `prop=revisions` with `rvprop=ids|timestamp|sha1|content|contentmodel`.
3. Fetch rendered content and relationships using `action=parse` with `prop=text|links|categories|images|displaytitle|properties`.
4. Normalize the response into one `pages.jsonl` record, one `links.jsonl` record per internal edge, and queued image titles.
5. For every File page or embedded image, call `prop=imageinfo` with `iiprop=url|size|mime|sha1` and `iiurlwidth` omitted so the response identifies the original file.
6. Download each original URL to a `.part` file while calculating SHA-256. Atomically rename it to `images/original/<sha256><extension>` only after the response completes. Record one `images.jsonl` entry per wiki File title; repeated binary content reuses the same local path.
7. Generate `index.json` and `manifest.json` from committed SQLite state after queues drain. Retain `state.sqlite` to support later incremental/resume runs.

Enumeration, rather than link reachability, defines completeness. Parsed links still extend the queue when they resolve to one of the three allowed namespaces, which handles pages created during a long discovery pass.

## Output Contract

The default output directory is `data/crawled/dontstarve-wiki/`:

```text
pages.jsonl
images.jsonl
links.jsonl
errors.jsonl
index.json
manifest.json
state.sqlite
images/original/<sha256>.<extension>
```

All JSON is UTF-8, emitted with unescaped Unicode and deterministic key ordering. JSONL files contain one complete object per newline.

### Page record

```json
{
  "schema_version": 1,
  "page_id": 123,
  "namespace": 0,
  "namespace_name": "Main",
  "title": "Wilson",
  "display_title": "Wilson",
  "canonical_url": "https://dontstarve.wiki.gg/wiki/Wilson",
  "redirect_target": null,
  "revision": {
    "id": 456,
    "timestamp": "2026-07-01T10:00:00Z",
    "sha1": "mediawiki-base36-sha1"
  },
  "content_model": "wikitext",
  "wikitext": "...",
  "html": "...",
  "plain_text": "...",
  "categories": ["Category:Playable characters"],
  "links": ["Willow", "File:Wilson.png"],
  "images": ["File:Wilson.png"],
  "fetched_at": "2026-07-15T00:00:00Z"
}
```

Lists are deduplicated and sorted by title so output is reproducible. Redirects retain their own page record and name the canonical target.

### Link record

Each record contains `source_page_id`, `source_title`, `target_title`, `target_namespace`, `exists`, and `in_scope`. Red links and links outside the selected namespaces are retained.

### Image record

Each record contains File page ID/title when available, original URL, MIME type, byte size, width, height, MediaWiki SHA-1, computed SHA-256, local relative path, and fetch timestamp. MIME type and a safe URL/path suffix determine the extension; untrusted title text never forms a filesystem path.

### Manifest and index

`manifest.json` contains schema version, base URL, selected namespaces, run start/end timestamps, crawler options, counts by record type/status, unresolved error count, and SHA-256 checksums of the finalized JSONL files.

`index.json` maps canonical title and page ID to the byte offset of the latest record in `pages.jsonl`, and File title to the latest metadata offset in `images.jsonl`. Consumers can seek directly without loading the JSONL payloads.

## Resume and Consistency

SQLite is the source of operational truth. It tracks discovery continuation tokens, page/image queue states (`pending`, `processing`, `done`, `failed`), attempts, revision IDs, JSONL byte offsets, and error details.

Queue claims and transitions are transactional. On startup, stale `processing` rows return to `pending`. A JSONL record is flushed before its `done` transaction is committed. Startup truncates an incomplete trailing JSONL line and reconciles uncommitted appended records using stable page/image keys. Consequently, interruption may cause a retry but cannot leave duplicate logical entries in the generated index.

The normal mode resumes in an existing compatible output directory. `--fresh` succeeds only when the target does not contain an existing crawl, preventing accidental destructive replacement. `--retry-errors` resets terminal failures to pending.

## HTTP Behavior and Safety

- Set a descriptive, configurable User-Agent; default to `dst-wiki-crawler/1.0 (https://dontstarve.wiki.gg/)`.
- Include `format=json`, `formatversion=2`, and `maxlag=5` in Action API requests.
- Run sequentially with a default minimum interval of `0.5` seconds between requests.
- Use a default timeout of `30` seconds and at most `5` attempts.
- Retry timeouts, connection failures, HTTP `429`, HTTP `5xx`, MediaWiki `maxlag`, and explicitly transient API errors.
- Respect `Retry-After`; otherwise use exponential backoff with bounded jitter.
- Treat malformed JSON, missing required response fields, HTTP `4xx` other than `429`, and unsupported content as permanent per-item failures.
- Limit redirects and reject downloaded image URLs whose final scheme is not HTTPS.
- Stream binary downloads and never buffer a whole image in memory.

## Command-Line Interface

Primary command:

```bash
python -m tools.crawl_wiki.cli \
  --base-url https://dontstarve.wiki.gg/ \
  --output data/crawled/dontstarve-wiki
```

Supported options:

- `--namespaces 0,14,6`
- `--delay 0.5`
- `--timeout 30`
- `--max-attempts 5`
- `--user-agent <value>`
- `--max-pages <count>` for deterministic smoke runs
- `--skip-images`
- `--fresh`
- `--retry-errors`
- `--log-level DEBUG|INFO|WARNING|ERROR`

Invalid numeric values, unsupported namespace IDs, non-HTTP(S) base URLs, and incompatible existing state fail before network access. Exit code `0` means all scheduled work completed; `1` means unresolved item failures; `2` means invalid invocation or fatal setup failure; `130` means interrupted by the user.

## Error Reporting

`errors.jsonl` records stage, stable subject key, URL/action, attempt count, error type, message, HTTP/API status when available, retryability, and timestamp. A repeated failure for the same stage/subject updates operational state; finalization emits only the latest unresolved error, avoiding duplicate error records across resumes.

Logs contain titles and stages but not page bodies or binary response content. A single page or image failure never stops unrelated queue work. Fatal state/schema corruption stops immediately to prevent further output damage.

## Testing Strategy

Implementation follows red-green-refactor TDD.

- Pure unit tests cover URL/title normalization, namespace handling, HTML-to-text behavior, deterministic record encoding, safe image suffixes, checksum paths, and CLI validation.
- Storage tests use temporary directories to cover atomic metadata writes, trailing-line recovery, queue transitions, index offsets, idempotent upserts, resume, and manifest checksums.
- Client and crawler integration tests use a local `http.server` fixture that behaves like Action API and serves binary images. Scenarios include API continuation, orphan discovery, redirect pages, red/out-of-scope links, revision and parse responses, duplicate image bytes, `429`/`503`/`maxlag` retry, permanent errors, interrupted download, and resumed completion.
- A live smoke test crawls at most three pages into a temporary directory when network access is available. It is validation evidence, not part of the deterministic automated suite.
- Final verification runs the crawler test suite, the repository's existing Python tests, lint/build checks relevant to changed files, and the local end-to-end fixture crawl.

## Acceptance Criteria

The feature is complete when:

1. A clean invocation can discover and export all pages in namespaces `0`, `14`, and `6` without authentication.
2. Page records contain latest revision metadata, wikitext, rendered HTML, normalized text, categories, links, images, and redirects.
3. Every available File original is content-addressed locally and described in `images.jsonl`.
4. Internal relationships, including red and out-of-scope links, appear in `links.jsonl`.
5. Interrupting and resuming a fixture crawl yields the same logical page/image/link records as an uninterrupted crawl, with no duplicate logical keys; operational timestamps may differ.
6. Manifest counts/checksums and index offsets validate against the generated files.
7. Transient failures retry; permanent failures are recorded without aborting unrelated work; unresolved failures determine exit status.
8. All new deterministic tests and all previously passing repository tests pass.
