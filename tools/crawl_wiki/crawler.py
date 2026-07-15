import logging
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence

from tools.crawl_wiki.client import ClientError, MediaWikiClient
from tools.crawl_wiki.item_seeds import (
    ITEM_SOURCE_SECTIONS,
    extract_item_seeds,
    merge_item_seeds,
)
from tools.crawl_wiki.models import CrawlSummary, SCHEMA_VERSION
from tools.crawl_wiki.parser import normalize_page
from tools.crawl_wiki.recipes import extract_recipes
from tools.crawl_wiki.storage import CrawlStorage, _utc_now


LOGGER = logging.getLogger(__name__)


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
            self._process_images()
        return self.storage.finalize(options)

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
