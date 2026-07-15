import pathlib
import re
import urllib.parse
from html.parser import HTMLParser
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set, Tuple

from tools.crawl_wiki.models import (
    SCHEMA_VERSION,
    SUPPORTED_NAMESPACES,
)


_BLOCK_TAGS = {
    "address",
    "article",
    "aside",
    "blockquote",
    "br",
    "dd",
    "div",
    "dl",
    "dt",
    "figcaption",
    "figure",
    "footer",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hr",
    "li",
    "main",
    "nav",
    "ol",
    "p",
    "pre",
    "section",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "tr",
    "ul",
}
_SUPPRESSED_TAGS = {"script", "style", "noscript", "template"}
_WHITESPACE = re.compile(r"[\t\f\v ]+")


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: List[str] = []
        self._suppressed_depth = 0

    def handle_starttag(
        self, tag: str, attrs: List[Tuple[str, Optional[str]]]
    ) -> None:
        del attrs
        tag = tag.lower()
        if tag in _SUPPRESSED_TAGS:
            self._suppressed_depth += 1
            return
        if self._suppressed_depth == 0 and tag in _BLOCK_TAGS:
            self._parts.append("\n")

    def handle_startendtag(
        self, tag: str, attrs: List[Tuple[str, Optional[str]]]
    ) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in _SUPPRESSED_TAGS:
            if self._suppressed_depth:
                self._suppressed_depth -= 1
            return
        if self._suppressed_depth == 0 and tag in _BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._suppressed_depth == 0:
            self._parts.append(data)

    def text(self) -> str:
        lines = []
        for line in "".join(self._parts).splitlines():
            normalized = _WHITESPACE.sub(" ", line).strip()
            if normalized:
                lines.append(normalized)
        return "\n".join(lines)


def normalize_base_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("base URL must use http or https")
    path = parsed.path.rstrip("/") + "/"
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, path, "", "")
    )


def canonical_page_url(base_url: str, title: str) -> str:
    slug = urllib.parse.quote(title.replace(" ", "_"), safe="/:()")
    return urllib.parse.urljoin(normalize_base_url(base_url), "wiki/" + slug)


def html_to_text(value: str) -> str:
    parser = _VisibleTextParser()
    parser.feed(value)
    parser.close()
    return parser.text()


def safe_image_extension(url: str, mime: Optional[str]) -> str:
    mime_extensions = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "image/svg+xml": ".svg",
        "image/avif": ".avif",
        "image/bmp": ".bmp",
        "image/tiff": ".tiff",
    }
    if mime:
        normalized_mime = mime.lower().split(";", 1)[0].strip()
        if normalized_mime in mime_extensions:
            return mime_extensions[normalized_mime]
    suffix = pathlib.PurePosixPath(
        urllib.parse.urlsplit(url).path
    ).suffix.lower()
    return suffix if suffix in set(mime_extensions.values()) else ".bin"


def _required_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("{} must be an object".format(field))
    return value


def _required_string(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError("{} must be a string".format(field))
    return value


def _prefix_title(title: str, prefix: str) -> str:
    return title if title.lower().startswith(prefix.lower() + ":") else prefix + ":" + title


def _sorted_unique_strings(values: Iterable[str]) -> List[str]:
    return sorted(set(values), key=lambda value: (value.casefold(), value))


def normalize_page(
    query_page: Mapping[str, Any],
    parsed: Mapping[str, Any],
    base_url: str,
    fetched_at: str,
    allowed_namespaces: Set[int],
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Set[str]]:
    page_id = query_page.get("pageid")
    namespace = query_page.get("ns")
    if not isinstance(page_id, int) or not isinstance(namespace, int):
        raise ValueError("page ID and namespace must be integers")
    title = _required_string(query_page.get("title"), "page title")

    revisions = query_page.get("revisions")
    if not isinstance(revisions, list) or len(revisions) != 1:
        raise ValueError("page must contain exactly one latest revision")
    revision = _required_mapping(revisions[0], "revision")
    slots = _required_mapping(revision.get("slots"), "revision slots")
    main_slot = _required_mapping(slots.get("main"), "main revision slot")
    wikitext = main_slot.get("content", main_slot.get("*"))
    wikitext = _required_string(wikitext, "revision content")

    rendered_html = parsed.get("text", "")
    if isinstance(rendered_html, Mapping):
        rendered_html = rendered_html.get("*", "")
    rendered_html = _required_string(rendered_html, "parsed HTML")

    raw_links = parsed.get("links", [])
    if not isinstance(raw_links, list):
        raise ValueError("parsed links must be an array")
    links: List[Dict[str, Any]] = []
    for raw_link in raw_links:
        link = _required_mapping(raw_link, "parsed link")
        target_namespace = link.get("ns")
        target_title = link.get("title", link.get("*"))
        if not isinstance(target_namespace, int) or not isinstance(
            target_title, str
        ):
            raise ValueError("parsed link namespace/title is invalid")
        links.append(
            {
                "schema_version": SCHEMA_VERSION,
                "source_page_id": page_id,
                "source_title": title,
                "target_title": target_title,
                "target_namespace": target_namespace,
                "exists": bool(link.get("exists", False)),
                "in_scope": target_namespace in allowed_namespaces,
            }
        )
    links.sort(
        key=lambda item: (
            item["target_namespace"],
            item["target_title"].casefold(),
            item["target_title"],
        )
    )

    raw_categories = parsed.get("categories", [])
    if not isinstance(raw_categories, list):
        raise ValueError("parsed categories must be an array")
    categories = _sorted_unique_strings(
        _prefix_title(
            _required_string(
                _required_mapping(item, "parsed category").get(
                    "category",
                    _required_mapping(item, "parsed category").get("*"),
                ),
                "category title",
            ),
            "Category",
        )
        for item in raw_categories
    )

    raw_images = parsed.get("images", [])
    if not isinstance(raw_images, list):
        raise ValueError("parsed images must be an array")
    image_titles = {
        _prefix_title(_required_string(item, "image title"), "File")
        for item in raw_images
    }

    is_redirect = bool(query_page.get("redirect"))
    redirect_target = links[0]["target_title"] if is_redirect and links else None
    revision_id = revision.get("revid")
    if not isinstance(revision_id, int):
        raise ValueError("revision ID must be an integer")
    timestamp = _required_string(revision.get("timestamp"), "revision timestamp")
    sha1 = _required_string(revision.get("sha1"), "revision sha1")
    content_model = revision.get(
        "contentmodel", main_slot.get("contentmodel", "wikitext")
    )
    content_model = _required_string(content_model, "content model")
    display_title = parsed.get("displaytitle", title)
    display_title = _required_string(display_title, "display title")

    page = {
        "schema_version": SCHEMA_VERSION,
        "page_id": page_id,
        "namespace": namespace,
        "namespace_name": SUPPORTED_NAMESPACES.get(
            namespace, "Namespace {}".format(namespace)
        ),
        "title": title,
        "display_title": display_title,
        "canonical_url": canonical_page_url(base_url, title),
        "redirect_target": redirect_target,
        "revision": {
            "id": revision_id,
            "timestamp": timestamp,
            "sha1": sha1,
        },
        "content_model": content_model,
        "wikitext": wikitext,
        "html": rendered_html,
        "plain_text": html_to_text(rendered_html),
        "categories": categories,
        "links": _sorted_unique_strings(
            item["target_title"] for item in links
        ),
        "images": _sorted_unique_strings(image_titles),
        "fetched_at": fetched_at,
    }
    return page, links, image_titles
