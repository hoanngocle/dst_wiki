import urllib.parse
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


ITEM_SOURCE_SECTIONS: Mapping[str, Tuple[str, ...]] = {
    "Items": (
        "Resources-0",
        "Craftable_Items-0",
        "Food-0",
        "By_Crock_Pot_Value-0",
    ),
    "Plants": ("DST-0",),
}

_IMAGE_SUFFIXES = (
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".avif",
    ".bmp",
    ".tiff",
)
_VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


@dataclass(frozen=True)
class ItemSeed:
    title: str
    href: str
    icon_title: Optional[str]
    icon_thumbnail_url: Optional[str]
    source_sections: Tuple[str, ...]


@dataclass
class _Anchor:
    title: Optional[str]
    href: Optional[str]
    sections: Tuple[str, ...]
    depth: int
    icon_title: Optional[str] = None
    icon_thumbnail_url: Optional[str] = None
    visual: bool = False


class _SeedHTMLParser(HTMLParser):
    def __init__(
        self,
        page_title: str,
        section_ids: Sequence[str],
        base_url: str,
    ) -> None:
        super().__init__(convert_charrefs=True)
        self.page_title = page_title
        self.section_ids = set(section_ids)
        self.base_url = base_url
        self.depth = 0
        self._section_frames: List[Tuple[int, str]] = []
        self._anchor: Optional[_Anchor] = None
        self.seeds: List[ItemSeed] = []

    @staticmethod
    def _attributes(
        attrs: List[Tuple[str, Optional[str]]]
    ) -> Dict[str, str]:
        return {
            key.lower(): value
            for key, value in attrs
            if value is not None
        }

    def handle_starttag(
        self, tag: str, attrs: List[Tuple[str, Optional[str]]]
    ) -> None:
        tag = tag.lower()
        self.depth += 1
        attributes = self._attributes(attrs)
        element_id = attributes.get("id")
        if element_id in self.section_ids:
            self._section_frames.append((self.depth, element_id))

        if tag == "a" and self._section_frames and self._anchor is None:
            sections = tuple(
                "{}#{}".format(self.page_title, section_id)
                for _, section_id in self._section_frames
            )
            self._anchor = _Anchor(
                title=attributes.get("title"),
                href=attributes.get("href"),
                sections=sections,
                depth=self.depth,
            )
        elif tag == "img" and self._anchor is not None:
            self._anchor.visual = True
            alt = attributes.get("alt", "").strip()
            if alt.lower().endswith(_IMAGE_SUFFIXES):
                self._anchor.icon_title = "File:" + alt
            source = attributes.get("src")
            if source:
                self._anchor.icon_thumbnail_url = urllib.parse.urljoin(
                    self.base_url, source
                )
        if tag in _VOID_TAGS:
            self.depth = max(0, self.depth - 1)

    def handle_startendtag(
        self, tag: str, attrs: List[Tuple[str, Optional[str]]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in _VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if (
            tag.lower() == "a"
            and self._anchor is not None
            and self._anchor.depth == self.depth
        ):
            seed = self._to_seed(self._anchor)
            if seed is not None:
                self.seeds.append(seed)
            self._anchor = None

        if self._section_frames and self._section_frames[-1][0] == self.depth:
            self._section_frames.pop()
        self.depth = max(0, self.depth - 1)

    def _to_seed(self, anchor: _Anchor) -> Optional[ItemSeed]:
        if not anchor.visual or not anchor.title or not anchor.href:
            return None
        title = anchor.title.strip()
        href = anchor.href.strip()
        if not title or title.casefold().endswith(" filter"):
            return None
        if ":" in title or not href.startswith("/wiki/"):
            return None
        parsed = urllib.parse.urlsplit(href)
        if not parsed.path.startswith("/wiki/"):
            return None
        normalized_href = parsed.path
        if parsed.query:
            normalized_href += "?" + parsed.query
        return ItemSeed(
            title=title,
            href=normalized_href,
            icon_title=anchor.icon_title,
            icon_thumbnail_url=anchor.icon_thumbnail_url,
            source_sections=tuple(sorted(set(anchor.sections))),
        )


def merge_item_seeds(
    groups: Iterable[Iterable[ItemSeed]],
) -> List[ItemSeed]:
    merged: Dict[str, ItemSeed] = {}
    for group in groups:
        for seed in group:
            current = merged.get(seed.href)
            if current is None:
                merged[seed.href] = seed
                continue
            merged[seed.href] = ItemSeed(
                title=current.title,
                href=current.href,
                icon_title=current.icon_title or seed.icon_title,
                icon_thumbnail_url=(
                    current.icon_thumbnail_url or seed.icon_thumbnail_url
                ),
                source_sections=tuple(
                    sorted(
                        set(current.source_sections) | set(seed.source_sections)
                    )
                ),
            )
    return sorted(
        merged.values(),
        key=lambda seed: (seed.title.casefold(), seed.title, seed.href),
    )


def extract_item_seeds(
    page_title: str, html: str, base_url: str
) -> List[ItemSeed]:
    section_ids = ITEM_SOURCE_SECTIONS.get(page_title)
    if section_ids is None:
        return []
    parser = _SeedHTMLParser(page_title, section_ids, base_url)
    parser.feed(html)
    parser.close()
    return merge_item_seeds([parser.seeds])
