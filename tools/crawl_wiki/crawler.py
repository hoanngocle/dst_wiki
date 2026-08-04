import json
import logging
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence
from urllib.parse import unquote, urlsplit

from tools.crawl_wiki.client import ClientError, MediaWikiClient
from tools.crawl_wiki.category_config import CategoryConfig
from tools.crawl_wiki.category_seeds import CategorySeed, normalize_category_members
from tools.crawl_wiki.item_seeds import (
    ITEM_SOURCE_SECTIONS,
    extract_item_seeds,
    merge_item_seeds,
)
from tools.crawl_wiki.models import CrawlSummary, SCHEMA_VERSION
from tools.crawl_wiki.parser import normalize_page
from tools.crawl_wiki.recipes import extract_recipes
from tools.crawl_wiki.storage import CrawlStorage, _utc_now
from tools.crawl_wiki.url_registry import UrlClaim, UrlRegistry, UrlRegistryError
from tools.extract.wiki_structures import normalize_structure_page


LOGGER = logging.getLogger(__name__)


class _InfoboxImageParser(HTMLParser):
    _CONTAINERS = {"aside", "div", "figure", "table"}
    _VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.infobox_depth = 0
        self.candidates: List[str] = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = set(str(attributes.get("class", "")).casefold().split())
        starts_infobox = tag in self._CONTAINERS and any(
            "infobox" in value for value in classes
        )
        if starts_infobox and self.infobox_depth == 0:
            self.infobox_depth = 1
        elif self.infobox_depth and tag not in self._VOID:
            self.infobox_depth += 1
        if self.infobox_depth and tag == "img":
            for key in ("data-image-key", "alt", "title", "data-src", "src"):
                value = attributes.get(key)
                if isinstance(value, str) and value.strip():
                    self.candidates.append(value.strip())
                    break

    def handle_endtag(self, tag):
        del tag
        if self.infobox_depth:
            self.infobox_depth -= 1


def select_primary_infobox_image(
    parsed: Mapping[str, Any], wikitext: Optional[str] = None
) -> Optional[str]:
    images = parsed.get("images")
    if not isinstance(images, list):
        return None
    by_name = {}
    for value in images:
        if not isinstance(value, str) or not value.strip():
            continue
        title = value.strip()
        if not title.startswith("File:"):
            title = "File:" + title
        by_name[title.removeprefix("File:").casefold()] = title

    if isinstance(wikitext, str):
        match = re.search(
            r"(?ims)^\s*\|\s*image\s*=\s*(.*?)(?=^\s*\|\s*[A-Za-z][^=\n]*=|\}\})",
            wikitext,
        )
        if match is not None:
            cleaned = re.sub(r"</?gallery[^>]*>", "", match.group(1), flags=re.I)
            for line in cleaned.splitlines():
                candidate = line.strip().split("|", 1)[0].strip().removeprefix("File:")
                selected = by_name.get(candidate.casefold())
                if selected is not None:
                    return selected

    rendered = parsed.get("text", "")
    if isinstance(rendered, Mapping):
        rendered = rendered.get("*", "")
    if not isinstance(rendered, str) or not rendered:
        return None
    parser = _InfoboxImageParser()
    parser.feed(rendered)
    parser.close()
    for candidate in parser.candidates:
        if "/" in candidate:
            candidate = unquote(urlsplit(candidate).path.rsplit("/", 1)[-1])
        name = candidate.removeprefix("File:").strip()
        matched = by_name.get(name.casefold())
        if matched is not None:
            return matched
    return None


class WikiCrawler:
    def __init__(
        self,
        client: MediaWikiClient,
        storage: CrawlStorage,
        namespaces: Sequence[int],
        skip_images: bool = False,
        max_pages: Optional[int] = None,
        clock: Callable[[], str] = _utc_now,
    ) -> None:
        if max_pages is not None and max_pages <= 0:
            raise ValueError("max pages must be positive")
        self.client = client
        self.storage = storage
        self.namespaces = tuple(int(value) for value in namespaces)
        self.skip_images = skip_images
        self.max_pages = max_pages
        self.clock = clock

    def run(self, options: Mapping[str, Any]) -> CrawlSummary:
        self._discover_pages()
        self._process_pages()
        if not self.skip_images:
            self._process_images()
        return self.storage.finalize(options)

    def _discover_pages(self) -> None:
        for namespace in self.namespaces:
            if self.storage.is_discovery_complete(namespace):
                continue
            while True:
                if (
                    self.max_pages is not None
                    and self.storage.page_count() >= self.max_pages
                ):
                    return
                current_token = self.storage.get_discovery_token(namespace)
                pages, next_token = self.client.list_allpages(
                    namespace, current_token
                )
                selected = pages
                if self.max_pages is not None:
                    remaining = self.max_pages - self.storage.page_count()
                    selected = pages[:remaining]
                self.storage.enqueue_pages(selected)
                LOGGER.info(
                    "discovered namespace=%s pages=%s",
                    namespace,
                    len(selected),
                )
                if len(selected) < len(pages):
                    return
                if next_token is None:
                    self.storage.mark_discovery_complete(namespace)
                    break
                self.storage.set_discovery_token(namespace, next_token)
                if (
                    self.max_pages is not None
                    and self.storage.page_count() >= self.max_pages
                ):
                    return

    def _process_pages(self) -> None:
        while True:
            claimed = self.storage.claim_page()
            if claimed is None:
                return
            page_id = int(claimed["page_id"])
            title = str(claimed["title"])
            try:
                query_page = self.client.get_page(page_id)
                parsed = self.client.parse_page(page_id)
                page, links, image_titles = normalize_page(
                    query_page,
                    parsed,
                    self.client.base_url,
                    self.clock(),
                    set(self.namespaces),
                )
                if int(claimed["namespace"]) == 6:
                    image_titles.add(title)
                    page["images"] = sorted(
                        image_titles,
                        key=lambda value: (value.casefold(), value),
                    )
                self.storage.complete_page(
                    page_id, page, links, image_titles
                )
                LOGGER.info("completed page id=%s title=%s", page_id, title)
            except (ClientError, ValueError) as error:
                self.storage.fail_page(
                    page_id,
                    self._error_record("page", str(page_id), error),
                )
                LOGGER.error("failed page id=%s title=%s: %s", page_id, title, error)

    def _process_images(self) -> None:
        while True:
            claimed = self.storage.claim_image()
            if claimed is None:
                return
            title = str(claimed["title"])
            part_path: Optional[Path] = None
            try:
                info = self.client.get_image_info(title)
                url = info.get("url")
                if not isinstance(url, str):
                    raise ValueError("imageinfo URL must be a string")
                mime = info.get("mime")
                if mime is not None and not isinstance(mime, str):
                    raise ValueError("imageinfo MIME type must be a string")
                part_path = self.storage.new_image_part()
                download = self.client.download(url, part_path)
                local_path = self.storage.commit_image_file(
                    part_path,
                    download.sha256,
                    download.final_url,
                    mime,
                )
                part_path = None
                record: Dict[str, Any] = {
                    "schema_version": SCHEMA_VERSION,
                    "page_id": info.get("page_id"),
                    "title": info.get("title", title),
                    "original_url": download.final_url,
                    "mime": mime,
                    "byte_size": download.byte_size,
                    "width": info.get("width"),
                    "height": info.get("height"),
                    "mediawiki_sha1": info.get("sha1"),
                    "sha256": download.sha256,
                    "local_path": local_path,
                    "fetched_at": self.clock(),
                }
                self.storage.complete_image(title, record)
                LOGGER.info("completed image title=%s", title)
            except (ClientError, ValueError) as error:
                if part_path is not None:
                    part_path.unlink(missing_ok=True)
                if isinstance(error, ClientError) and not error.retryable:
                    self.storage.skip_image(title, str(error))
                    LOGGER.warning(
                        "skipped unavailable image title=%s: %s", title, error
                    )
                else:
                    self.storage.fail_image(
                        title, self._error_record("image", title, error)
                    )
                    LOGGER.error("failed image title=%s: %s", title, error)

    def _error_record(
        self, stage: str, subject: str, error: Exception
    ) -> Dict[str, Any]:
        if isinstance(error, ClientError):
            retryable = error.retryable
            status = error.status
            code = error.code
        else:
            retryable = False
            status = None
            code = None
        return {
            "stage": stage,
            "subject": subject,
            "url": self.client.api_url,
            "error_type": type(error).__name__,
            "message": str(error),
            "status": status,
            "code": code,
            "retryable": retryable,
            "timestamp": self.clock(),
        }


class SelectiveItemsCrawler(WikiCrawler):
    def __init__(
        self,
        client: MediaWikiClient,
        storage: CrawlStorage,
        item_budget: int = 100,
        skip_images: bool = False,
        clock: Callable[[], str] = _utc_now,
    ) -> None:
        if item_budget <= 0:
            raise ValueError("item budget must be positive")
        super().__init__(
            client,
            storage,
            (0,),
            skip_images=skip_images,
            clock=clock,
        )
        self.item_budget = item_budget

    def run(self, options: Mapping[str, Any]) -> CrawlSummary:
        self._discover_items()
        self._process_selected_pages()
        if not self.skip_images:
            self._enqueue_saved_structure_images()
            self._process_images()
        return self.storage.finalize(options)

    def _enqueue_saved_structure_images(self) -> int:
        """Reconcile normalized structure visuals for fresh and resumed crawls."""

        path = self.storage.output / "pages.jsonl"
        if not path.is_file():
            return 0
        titles = set()
        with path.open(encoding="utf-8") as source:
            for line_number, raw in enumerate(source, start=1):
                if not raw.strip():
                    continue
                try:
                    page = json.loads(raw)
                except json.JSONDecodeError as error:
                    raise ValueError(
                        "invalid saved page at {}:{}".format(path, line_number)
                    ) from error
                if not isinstance(page, dict):
                    raise ValueError(
                        "saved page at {}:{} must be an object".format(
                            path, line_number
                        )
                    )
                details = normalize_structure_page(page)
                candidates = (
                    details.get("visual_candidates")
                    if isinstance(details, dict)
                    else None
                )
                if not isinstance(candidates, list):
                    continue
                titles.update(
                    candidate["title"]
                    for candidate in candidates
                    if isinstance(candidate, dict)
                    and isinstance(candidate.get("title"), str)
                )
        return self.storage.enqueue_images(titles)

    def _discover_items(self) -> None:
        if self.storage.is_item_discovery_complete():
            return
        groups = []
        for page_title in ITEM_SOURCE_SECTIONS:
            parsed = self.client.parse_page_by_title(page_title)
            rendered_html = parsed.get("text", "")
            if isinstance(rendered_html, Mapping):
                rendered_html = rendered_html.get("*", "")
            if not isinstance(rendered_html, str):
                raise ClientError(
                    "source page HTML must be a string", retryable=False
                )
            groups.append(
                extract_item_seeds(
                    page_title, rendered_html, self.client.base_url
                )
            )
        seeds = merge_item_seeds(groups)
        if not seeds:
            raise ClientError(
                "approved item sections produced no item links",
                retryable=False,
            )
        self.storage.save_seeds(seeds)
        resolved = self.client.resolve_titles(
            [seed.title for seed in seeds]
        )
        main_pages = [page for page in resolved if page.get("ns") == 0]
        self.storage.enqueue_pages(main_pages)
        self.storage.mark_item_discovery_complete()
        LOGGER.info(
            "discovered selective item seeds=%s resolved_pages=%s",
            len(seeds),
            len(main_pages),
        )

    def _process_selected_pages(self) -> None:
        for _ in range(self.item_budget):
            claimed = self.storage.claim_page()
            if claimed is None:
                return
            page_id = int(claimed["page_id"])
            title = str(claimed["title"])
            try:
                query_page = self.client.get_page(page_id)
                parsed = self.client.parse_page(page_id)
                page, links, _ = normalize_page(
                    query_page,
                    parsed,
                    self.client.base_url,
                    self.clock(),
                    {0},
                )
                seed = self.storage.seed_for_title(title)
                selected_images = set()
                if seed is not None and isinstance(
                    seed.get("icon_title"), str
                ):
                    selected_images.add(seed["icon_title"])
                recipes = extract_recipes(
                    page_id, title, str(page["wikitext"])
                )
                self.storage.complete_page(
                    page_id,
                    page,
                    links,
                    selected_images,
                    recipe_records=recipes,
                )
                LOGGER.info(
                    "completed selected item id=%s title=%s recipes=%s",
                    page_id,
                    title,
                    len(recipes),
                )
            except (ClientError, ValueError) as error:
                self.storage.fail_page(
                    page_id,
                    self._error_record("page", str(page_id), error),
                )
                LOGGER.error(
                    "failed selected item id=%s title=%s: %s",
                    page_id,
                    title,
                    error,
                )


class CategoryCrawler(WikiCrawler):
    def __init__(
        self,
        client: MediaWikiClient,
        storage: CrawlStorage,
        config: CategoryConfig,
        url_registry: UrlRegistry,
        page_budget: int = 100,
        skip_images: bool = False,
        worker_id: str = "category-worker",
        clock: Callable[[], str] = _utc_now,
    ) -> None:
        if page_budget <= 0:
            raise ValueError("page budget must be positive")
        if not worker_id.strip():
            raise ValueError("worker ID must not be empty")
        super().__init__(
            client,
            storage,
            config.allowed_namespaces,
            skip_images=skip_images,
            clock=clock,
        )
        self.config = config
        self.url_registry = url_registry
        self.page_budget = page_budget
        self.worker_id = worker_id.strip()

    def run(self, options: Mapping[str, Any]) -> CrawlSummary:
        self._discover_category()
        self.storage.resume_waiting_pages()
        self._process_category_pages()
        if not self.skip_images:
            self._process_images()
        return self.storage.finalize(options)

    def _discover_category(self) -> None:
        key = self.config.key
        if self.storage.is_category_discovery_complete(key):
            return

        if not self.storage.is_category_member_discovery_complete(key):
            while True:
                token = self.storage.get_category_discovery_token(key)
                members, next_token = self.client.list_category_members(
                    self.config.category_title, token
                )
                self.storage.save_category_members(members)
                if next_token is None:
                    self.storage.mark_category_member_discovery_complete(key)
                    break
                self.storage.set_category_discovery_token(key, next_token)

        discovered = normalize_category_members(
            self.config, self.storage.category_members()
        )
        accepted = [seed for seed in discovered if seed.accepted]
        resolved = self.client.resolve_titles_detailed(
            [seed.title for seed in accepted]
        )
        by_requested = {value.requested_title: value for value in resolved}
        canonical = []
        seen_page_ids = set()
        for seed in accepted:
            value = by_requested.get(seed.title)
            if value is None:
                raise ValueError(
                    "accepted category title did not resolve: {}".format(
                        seed.title
                    )
                )
            if value.namespace not in self.config.allowed_namespaces:
                raise ValueError(
                    "accepted category title resolved outside allowed namespace"
                )
            if value.page_id in seen_page_ids:
                raise ValueError(
                    "multiple category titles resolve to one canonical page"
                )
            seen_page_ids.add(value.page_id)
            canonical.append(
                CategorySeed(
                    page_id=value.page_id,
                    namespace=value.namespace,
                    title=value.canonical_title,
                    canonical_url=value.canonical_url,
                    accepted=True,
                    reason=None,
                )
            )
        if len(canonical) != self.config.expected_published_pages:
            raise ValueError(
                "resolved category page count mismatch: expected {}, got {}".format(
                    self.config.expected_published_pages, len(canonical)
                )
            )

        excluded = [seed for seed in discovered if not seed.accepted]
        all_seeds = excluded + canonical
        self.storage.save_category_seeds(all_seeds)
        for seed in canonical:
            self.url_registry.register(seed.canonical_url, key)
        self.storage.enqueue_pages(
            [
                {
                    "pageid": seed.page_id,
                    "ns": seed.namespace,
                    "title": seed.title,
                }
                for seed in canonical
            ]
        )
        self.storage.mark_category_discovery_complete(key)
        LOGGER.info(
            "discovered category=%s direct=%s queued=%s excluded=%s",
            key,
            self.config.expected_direct_pages,
            len(canonical),
            len(excluded),
        )

    def _process_category_pages(self) -> None:
        for _ in range(self.page_budget):
            claimed = self.storage.claim_page()
            if claimed is None:
                return
            page_id = int(claimed["page_id"])
            title = str(claimed["title"])
            seed = self.storage.category_seed_for_page(page_id)
            if seed is None or not seed["accepted"]:
                raise ValueError(
                    "queued category page has no accepted seed: {}".format(
                        page_id
                    )
                )
            registry_claim: Optional[UrlClaim] = None
            try:
                registry_claim = self.url_registry.claim(
                    seed["canonical_url"],
                    self.config.key,
                    self.worker_id,
                )
                if registry_claim.decision == "busy":
                    self.storage.defer_page(page_id, "url_registry:Doing")
                    continue
                if registry_claim.decision == "reuse":
                    shared = self.url_registry.load_payload(
                        registry_claim.record
                    )
                else:
                    query_page = self.client.get_page(page_id)
                    parsed = self.client.parse_page(page_id)
                    page, links, _ = normalize_page(
                        query_page,
                        parsed,
                        self.client.base_url,
                        self.clock(),
                        set(self.config.allowed_namespaces),
                    )
                    primary_image = select_primary_infobox_image(
                        parsed, page.get("wikitext")
                    )
                    shared = {
                        "schemaVersion": 1,
                        "page": page,
                        "links": links,
                        "imageTitles": (
                            [primary_image] if primary_image is not None else []
                        ),
                    }
                    self.url_registry.complete(registry_claim, shared)
                self._materialize_shared_page(page_id, shared)
                LOGGER.info(
                    "completed category page id=%s title=%s source=%s",
                    page_id,
                    title,
                    registry_claim.decision,
                )
            except (ClientError, UrlRegistryError, ValueError) as error:
                if registry_claim is not None and registry_claim.decision == "crawl":
                    try:
                        self.url_registry.release(registry_claim, str(error))
                    except UrlRegistryError:
                        LOGGER.exception(
                            "failed to release URL claim for page id=%s",
                            page_id,
                        )
                self.storage.fail_page(
                    page_id,
                    self._error_record("page", str(page_id), error),
                )
                LOGGER.error(
                    "failed category page id=%s title=%s: %s",
                    page_id,
                    title,
                    error,
                )

    def _materialize_shared_page(
        self, page_id: int, payload: Mapping[str, Any]
    ) -> None:
        page = payload.get("page")
        links = payload.get("links")
        image_titles = payload.get("imageTitles")
        if not isinstance(page, Mapping) or page.get("page_id") != page_id:
            raise ValueError("shared category page identity is invalid")
        if not isinstance(links, list) or not all(
            isinstance(value, Mapping) for value in links
        ):
            raise ValueError("shared category links are invalid")
        if not isinstance(image_titles, list) or not all(
            isinstance(value, str) for value in image_titles
        ):
            raise ValueError("shared category image titles are invalid")
        self.storage.complete_page(
            page_id,
            page,
            links,
            set(image_titles),
        )
