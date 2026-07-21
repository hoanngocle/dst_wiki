import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

from tools.crawl_wiki.category_config import CategoryConfig


_HEADING = re.compile(r"(?m)^(={2,6})\s*([^=\n]+?)\s*\1\s*$")
_REFERENCE = re.compile(r"<ref\b[^>]*>.*?</ref\s*>|<ref\b[^>]*/\s*>", re.I | re.S)
_HTML = re.compile(r"<[^>]+>")
_PATCH_TRIVIA = re.compile(
    r"\b(?:added|introduced|removed|changed)\b.*\b(?:update|version|patch)\b|"
    r"\b(?:update|version|patch)\b.*\b(?:added|introduced|removed|changed)\b",
    re.I,
)
_NON_DST = re.compile(
    r"\b(?:Shipwrecked|Hamlet|Reign of Giants)\b|\bDon't Starve\b(?!\s+Together)",
    re.I,
)


@dataclass(frozen=True)
class ReviewedNote:
    source_sha256: str
    vi: str
    reviewed: bool


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_note_review(
    pages: Iterable[Mapping[str, Any]], config: CategoryConfig
) -> Dict[str, Any]:
    entries = {}
    for page in sorted(pages, key=lambda value: int(value.get("page_id", 0))):
        page_id = page.get("page_id")
        wikitext = page.get("wikitext")
        if not isinstance(page_id, int) or not isinstance(wikitext, str):
            raise ValueError("category note page identity is invalid")
        note = _notes_source(wikitext)
        if note is None:
            continue
        source, locator = note
        entries[str(page_id)] = {
            "source": source,
            "source_sha256": sha256_text(source),
            "locator": locator,
            "reviewed": False,
        }
    return {
        "schema_version": 1,
        "category": config.key,
        "game": "DST",
        "pages": entries,
    }


def build_category_note_review(
    crawl_root: Path,
    config: CategoryConfig,
    output: Path,
) -> Dict[str, Any]:
    pages = _read_jsonl(Path(crawl_root) / "pages.jsonl")
    review = build_note_review(pages, config)
    _write_atomic(Path(output), review)
    return review


def load_reviewed_note_summaries(path: Path) -> Mapping[int, ReviewedNote]:
    path = Path(path)
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("invalid category note summary file: {}".format(path)) from error
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("category note summary schema is invalid")
    pages = payload.get("pages")
    if not isinstance(pages, dict):
        raise ValueError("category note summary pages must be an object")
    result = {}
    for raw_page_id, value in pages.items():
        try:
            page_id = int(raw_page_id)
        except (TypeError, ValueError) as error:
            raise ValueError("category note summary page ID is invalid") from error
        if (
            page_id <= 0
            or not isinstance(value, dict)
            or not isinstance(value.get("source_sha256"), str)
            or len(value["source_sha256"]) != 64
            or not isinstance(value.get("vi"), str)
            or not value["vi"].strip()
            or value.get("reviewed") is not True
        ):
            raise ValueError("category note summary entry is invalid")
        result[page_id] = ReviewedNote(
            source_sha256=value["source_sha256"],
            vi=" ".join(value["vi"].split()),
            reviewed=True,
        )
    return result


def _notes_source(wikitext: str) -> Optional[tuple[str, str]]:
    matches = list(_HEADING.finditer(wikitext))
    retained = []
    selected_headings = []
    for index, match in enumerate(matches):
        heading = _clean_note_line(match.group(2))
        if heading.casefold() not in {"notes", "tips"}:
            continue
        selected_headings.append(heading)
        level = len(match.group(1))
        end = len(wikitext)
        for following in matches[index + 1 :]:
            if len(following.group(1)) <= level:
                end = following.start()
                break
        for raw_line in wikitext[match.end() : end].splitlines():
            cleaned = _clean_note_line(raw_line)
            if (
                cleaned
                and not _PATCH_TRIVIA.search(cleaned)
                and not _NON_DST.search(cleaned)
            ):
                retained.append(cleaned)
    source = " ".join(dict.fromkeys(retained)).strip()
    if not source:
        return None
    headings = ",".join(dict.fromkeys(selected_headings))
    return source, "headings:{}".format(headings)


def _clean_note_line(value: str) -> str:
    value = _REFERENCE.sub("", value)
    value = re.sub(r"\{\{[^{}]*\}\}", "", value)
    value = re.sub(r"\[\[[^\]|]+\|([^\]]+)\]\]", r"\1", value)
    value = re.sub(r"\[\[([^\]]+)\]\]", r"\1", value)
    value = _HTML.sub("", value)
    value = re.sub(r"^[*#:;\s]+", "", value)
    value = value.replace("'''", "").replace("''", "")
    return " ".join(value.split())


def _read_jsonl(path: Path):
    if not path.is_file():
        raise ValueError("category crawl pages are missing: {}".format(path))
    records = []
    with path.open(encoding="utf-8") as source:
        for line_number, raw in enumerate(source, start=1):
            if not raw.strip():
                continue
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as error:
                raise ValueError(
                    "invalid category page at {}:{}".format(path, line_number)
                ) from error
            if not isinstance(value, dict):
                raise ValueError("category page must be an object")
            records.append(value)
    return records


def _write_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(".{}.tmp".format(path.name))
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(str(temporary), str(path))
