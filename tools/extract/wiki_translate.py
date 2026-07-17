"""Build the reproducible Vietnamese summary cache used by Wiki exports."""

import hashlib
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from tools.extract.wiki_export import _summary_source


JsonObject = Dict[str, Any]
Translator = Callable[[str], str]
GOOGLE_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _existing_pages(path: Path) -> Mapping[str, Any]:
    if not path.is_file():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise ValueError(f"invalid Wiki summary translation cache: {path}")
    pages = value.get("pages")
    if not isinstance(pages, dict):
        raise ValueError(f"Wiki summary translation cache pages must be an object: {path}")
    return pages


def _manual_pages(path: Optional[Path]) -> Mapping[str, str]:
    if path is None or not Path(path).is_file():
        return {}
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise ValueError(f"invalid manual Wiki summaries: {path}")
    pages = value.get("pages")
    if not isinstance(pages, dict) or not all(
        isinstance(key, str) and isinstance(summary, str) and summary.strip()
        for key, summary in pages.items()
    ):
        raise ValueError(f"manual Wiki summaries must contain a pages string map: {path}")
    return pages


def google_translate(source: str, attempts: int = 5) -> str:
    query = urlencode(
        {
            "client": "gtx",
            "sl": "en",
            "tl": "vi",
            "dt": "t",
            "q": source,
        }
    )
    request = Request(
        f"{GOOGLE_TRANSLATE_URL}?{query}",
        headers={"User-Agent": "dst-wiki-data-builder/1.0"},
    )
    last_error: Optional[BaseException] = None
    for attempt in range(attempts):
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            segments = payload[0] if isinstance(payload, list) and payload else None
            translated = "".join(
                segment[0]
                for segment in segments or []
                if isinstance(segment, list)
                and segment
                and isinstance(segment[0], str)
            ).strip()
            if not translated:
                raise ValueError("translation response did not contain translated text")
            return translated
        except (
            HTTPError,
            URLError,
            OSError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(min(2 ** attempt, 8))
    raise RuntimeError(f"could not translate summary after {attempts} attempts") from last_error


def _entry(source: str, translated: str) -> JsonObject:
    return {
        "source": source,
        "source_sha256": _sha256(source),
        "vi": " ".join(translated.split()),
    }


def _valid_translation(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    normalized = value.strip().casefold()
    return not normalized.startswith(("dành riêng cho:", "xem thêm:"))


def _write_atomic(path: Path, value: JsonObject) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def build_summary_translation_cache(
    pages_path: Path,
    output: Path,
    translate: Translator = google_translate,
    workers: int = 4,
    manual_path: Optional[Path] = None,
) -> Dict[str, int]:
    """Translate every available Wiki lead and atomically update the cache."""

    pages_path = Path(pages_path)
    output = Path(output)
    if workers < 1:
        raise ValueError("workers must be at least 1")
    previous = _existing_pages(output)
    manual = _manual_pages(manual_path)
    entries: Dict[str, JsonObject] = {}
    pending: Dict[str, str] = {}
    cached = 0

    paths = sorted(
        pages_path.glob("*.json"),
        key=lambda path: (0, int(path.stem)) if path.stem.isdigit() else (1, path.stem),
    )
    for path in paths:
        page = json.loads(path.read_text(encoding="utf-8"))
        page_id = page.get("pageId") if isinstance(page, dict) else None
        html = page.get("html") if isinstance(page, dict) else None
        if not isinstance(page_id, int) or not isinstance(html, str):
            continue
        plain_text = page.get("plainText")
        source = _summary_source(
            html, plain_text if isinstance(plain_text, str) else ""
        )
        if source is None:
            continue
        key = str(page_id)
        source_sha = _sha256(source)
        old = previous.get(key)
        manual_summary = manual.get(key)
        if manual_summary is not None:
            entries[key] = _entry(source, manual_summary)
            cached += 1
        elif (
            isinstance(old, dict)
            and old.get("source_sha256") == source_sha
            and _valid_translation(old.get("vi"))
        ):
            entries[key] = _entry(source, old["vi"])
            cached += 1
        else:
            pending[key] = source

    failures = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(translate, source): (key, source)
            for key, source in pending.items()
        }
        for future in as_completed(futures):
            key, source = futures[future]
            try:
                entries[key] = _entry(source, future.result())
            except BaseException as error:
                failures.append((key, error))
    if failures:
        page_ids = ", ".join(key for key, _ in sorted(failures))
        raise RuntimeError(f"failed to translate Wiki summary pages: {page_ids}") from failures[0][1]

    ordered = {key: entries[key] for key in sorted(entries, key=int)}
    _write_atomic(output, {"schema_version": 1, "pages": ordered})
    return {
        "pages": len(ordered),
        "cached": cached,
        "translated": len(pending),
    }
