import hashlib
import html
import json
import math
import os
import re
import shutil
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple
from urllib.parse import urljoin, urlsplit


JsonObject = Dict[str, Any]
FANDOM_BASE_URL = "https://dontstarve.fandom.com"

GUIDE_REVIEWS = {
    "Guides/How to Kill the Giants in DST": {
        "titleVi": "Cách đánh bại các Giant trong DST",
        "summaryVi": "Chuẩn bị trang bị, bẫy và chiến thuật để đối phó các Giant trong Don't Starve Together.",
        "topic": "combat",
        "audience": "advanced",
    },
    "Guides/Maximum Efficiency Day 13 Base DST Guide": {
        "titleVi": "Căn cứ hiệu quả trong 13 ngày đầu",
        "summaryVi": "Lộ trình khám phá, thu thập và dựng căn cứ hiệu quả trong 13 ngày đầu của một thế giới DST.",
        "topic": "base-building",
        "audience": "intermediate",
    },
    "Guides/Slurtle Slime Guide": {
        "titleVi": "Hướng dẫn tạo Slurtle Slime",
        "summaryVi": "Giải thích cách Slurtle và Snurtle tiêu thụ khoáng vật để tạo Slurtle Slime trong DST.",
        "topic": "resources",
        "audience": "intermediate",
    },
    "Guides/Taming a Beefalo": {
        "titleVi": "Thuần hóa Beefalo",
        "summaryVi": "Hướng dẫn tăng obedience, domestication và chọn tendency khi thuần hóa Beefalo.",
        "topic": "domestication",
        "audience": "intermediate",
    },
}


def _slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.casefold()).strip("-")


def _image_key(value: str) -> str:
    return value.removeprefix("File:").replace("_", " ").casefold().strip()


def _read_jsonl(path: Path) -> List[JsonObject]:
    rows = []
    with path.open(encoding="utf-8") as source:
        for line_number, raw in enumerate(source, start=1):
            if not raw.strip():
                continue
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError("{}:{} must contain an object".format(path, line_number))
            rows.append(value)
    return rows


def _write_json_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _heading_plan(source: str) -> List[Tuple[str, str, int]]:
    used: Dict[str, int] = {}
    result = []
    for match in re.finditer(r"(?is)<h([2-4])\b[^>]*>(.*?)</h\1>", source):
        label = html.unescape(re.sub(r"<[^>]+>", "", match.group(2))).strip()
        if not label:
            continue
        base = _slug(label) or "section"
        used[base] = used.get(base, 0) + 1
        anchor = base if used[base] == 1 else "{}-{}".format(base, used[base])
        result.append((anchor, label, int(match.group(1))))
    return result


class _GuideSanitizer(HTMLParser):
    ALLOWED = {
        "a", "b", "blockquote", "br", "code", "dd", "dl", "dt", "em",
        "figcaption", "figure", "h2", "h3", "h4", "hr", "i", "img", "li",
        "ol", "p", "pre", "strong", "table", "tbody", "td", "th", "thead",
        "tr", "ul",
    }
    VOID = {"br", "hr", "img"}
    DROP_TAGS = {"script", "style", "svg", "template"}
    DROP_CLASS_PARTS = {
        "editsection", "metadata", "navbox", "notice", "portable-infobox", "toc",
    }

    def __init__(
        self,
        image_paths: Mapping[str, str],
        headings: Iterable[Tuple[str, str, int]],
    ) -> None:
        super().__init__(convert_charrefs=True)
        self.image_paths = image_paths
        self.headings = iter(headings)
        self.output: List[str] = []
        self.drop_depth = 0
        self.open_allowed: List[str] = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = str(attributes.get("class", "")).casefold()
        identifier = str(attributes.get("id", "")).casefold()
        starts_drop = tag in self.DROP_TAGS or any(
            part in classes or part in identifier for part in self.DROP_CLASS_PARTS
        )
        if self.drop_depth:
            if tag not in self.VOID:
                self.drop_depth += 1
            return
        if starts_drop:
            self.drop_depth = 1
            return
        if tag not in self.ALLOWED:
            return
        safe: List[Tuple[str, str]] = []
        if tag in {"h2", "h3", "h4"}:
            try:
                anchor, _label, _level = next(self.headings)
            except StopIteration:
                anchor = "section"
            safe.append(("id", anchor))
        elif tag == "a":
            href = str(attributes.get("href", "")).strip()
            if href.startswith("/"):
                href = urljoin(FANDOM_BASE_URL, href)
            scheme = urlsplit(href).scheme
            if href.startswith("#") or scheme in {"http", "https"}:
                safe.append(("href", href))
                if scheme in {"http", "https"}:
                    safe.extend((("rel", "noreferrer"), ("target", "_blank")))
        elif tag == "img":
            raw_name = next(
                (
                    str(attributes[key])
                    for key in ("data-image-name", "data-image-key", "alt")
                    if attributes.get(key)
                ),
                "",
            )
            local = self.image_paths.get(_image_key(raw_name))
            if local is None:
                return
            safe.extend(
                (
                    ("src", local),
                    ("alt", str(attributes.get("alt") or raw_name.removesuffix(".png"))),
                    ("loading", "lazy"),
                )
            )
            for dimension in ("width", "height"):
                value = str(attributes.get(dimension, ""))
                if value.isdigit():
                    safe.append((dimension, value))
        elif tag in {"td", "th"}:
            for name in ("colspan", "rowspan"):
                value = str(attributes.get(name, ""))
                if value.isdigit():
                    safe.append((name, value))
        rendered = "".join(
            ' {}="{}"'.format(name, html.escape(value, quote=True))
            for name, value in safe
        )
        self.output.append("<{}{}>".format(tag, rendered))
        if tag not in self.VOID:
            self.open_allowed.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if self.drop_depth:
            self.drop_depth -= 1
            return
        if tag in self.ALLOWED and tag not in self.VOID and tag in self.open_allowed:
            while self.open_allowed:
                current = self.open_allowed.pop()
                self.output.append("</{}>".format(current))
                if current == tag:
                    break

    def handle_data(self, data):
        if not self.drop_depth:
            self.output.append(html.escape(data))

    def result(self) -> str:
        while self.open_allowed:
            self.output.append("</{}>".format(self.open_allowed.pop()))
        return "".join(self.output).strip()


def _sections(safe_html: str, toc: List[JsonObject]) -> List[JsonObject]:
    starts = list(re.finditer(r'<h([2-4]) id="([^"]+)">', safe_html))
    sections = []
    if starts and safe_html[: starts[0].start()].strip():
        sections.append(
            {"id": "overview", "heading": "Tổng quan", "level": 1, "html": safe_html[: starts[0].start()].strip()}
        )
    if not starts:
        return [{"id": "overview", "heading": "Tổng quan", "level": 1, "html": safe_html}]
    toc_by_id = {row["id"]: row for row in toc}
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(safe_html)
        anchor = match.group(2)
        row = toc_by_id[anchor]
        sections.append(
            {"id": anchor, "heading": row["label"], "level": row["level"], "html": safe_html[match.start():end].strip()}
        )
    return [section for section in sections if re.sub(r"<[^>]+>", "", section["html"]).strip()]


def _review_for(page: Mapping[str, Any], lead: str) -> JsonObject:
    title = str(page["title"])
    reviewed = GUIDE_REVIEWS.get(title)
    if reviewed is not None:
        return dict(reviewed)
    short = re.sub(r"\s+", " ", lead).strip()[:180].rstrip(" ,.;:")
    return {
        "titleVi": title.removeprefix("Guides/"),
        "summaryVi": "Hướng dẫn DST: {}.".format(short or title.removeprefix("Guides/")),
        "topic": "general",
        "audience": "intermediate",
    }


def export_guides(crawl_root: Path, output_root: Path, asset_root: Path) -> JsonObject:
    pages = _read_jsonl(crawl_root / "pages.jsonl")
    image_rows = _read_jsonl(crawl_root / "images.jsonl")
    images = {_image_key(str(row.get("title", ""))): row for row in image_rows}
    seen_slugs = set()
    index_rows = []
    details = []
    asset_root.mkdir(parents=True, exist_ok=True)

    for page in sorted(pages, key=lambda value: str(value.get("title", "")).casefold()):
        title = str(page.get("title", "")).strip()
        slug = _slug(title.removeprefix("Guides/"))
        if not slug:
            raise ValueError("guide has no usable slug: {}".format(title))
        if slug in seen_slugs:
            raise ValueError("duplicate guide slug: {}".format(slug))
        seen_slugs.add(slug)
        page_image_keys = {_image_key(str(value)) for value in page.get("images", [])}
        available = [images[key] for key in page_image_keys if key in images]
        if not available:
            raise ValueError("guide has no usable local cover: {}".format(title))
        cover_row = sorted(available, key=lambda row: str(row.get("title", "")).casefold())[0]
        source_path = crawl_root / str(cover_row["local_path"])
        if not source_path.is_file():
            raise ValueError("guide cover file is missing: {}".format(source_path))
        extension = source_path.suffix.casefold() or ".bin"
        image_name = str(cover_row["title"]).removeprefix("File:")
        published_name = _slug(Path(image_name).stem) + extension
        destination = asset_root / published_name
        temporary = destination.with_name(destination.name + ".tmp")
        shutil.copyfile(source_path, temporary)
        os.replace(temporary, destination)
        public_cover = "/assets/guides/{}".format(published_name)
        image_paths = {_image_key(str(cover_row["title"])): public_cover}
        source_html = str(page.get("html", ""))
        headings = _heading_plan(source_html)
        sanitizer = _GuideSanitizer(image_paths, headings)
        sanitizer.feed(source_html)
        sanitizer.close()
        safe_html = sanitizer.result()
        plain = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", safe_html))).strip()
        if len(plain) < 40:
            raise ValueError("guide has no usable article content: {}".format(title))
        toc = [
            {"id": anchor, "label": label, "level": level}
            for anchor, label, level in headings
        ]
        sections = _sections(safe_html, toc)
        if not sections:
            raise ValueError("guide has no usable article sections: {}".format(title))
        review = _review_for(page, plain)
        word_source = str(page.get("plain_text") or plain)
        reading_minutes = max(1, math.ceil(len(word_source.split()) / 220))
        revision = page.get("revision")
        if not isinstance(revision, Mapping):
            raise ValueError("guide revision is missing: {}".format(title))
        cover = {
            "src": public_cover,
            "alt": review["titleVi"],
            "width": int(cover_row.get("width") or 1),
            "height": int(cover_row.get("height") or 1),
            "sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        }
        common = {
            "id": "guide:{}".format(slug),
            "slug": slug,
            "title": title.removeprefix("Guides/"),
            "titleVi": review["titleVi"],
            "summaryVi": review["summaryVi"],
            "sourceUrl": str(page.get("canonical_url", "")),
            "cover": cover,
            "topic": review["topic"],
            "audience": review["audience"],
            "readingMinutes": reading_minutes,
        }
        index_rows.append(common)
        details.append(
            dict(
                common,
                schemaVersion=1,
                revision={
                    "id": int(revision.get("id") or 0),
                    "timestamp": str(revision.get("timestamp") or ""),
                    "sha1": str(revision.get("sha1") or ""),
                },
                toc=toc,
                sections=sections,
            )
        )

    output_root.mkdir(parents=True, exist_ok=True)
    for detail in details:
        _write_json_atomic(output_root / "pages" / (detail["slug"] + ".json"), detail)
    _write_json_atomic(
        output_root / "index.json",
        {"schemaVersion": 1, "count": len(index_rows), "guides": index_rows},
    )
    return {"guides": len(index_rows), "assets": len(index_rows)}
