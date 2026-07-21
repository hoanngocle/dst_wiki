import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Tuple
from urllib.parse import unquote, urlsplit


CATEGORY_CONFIG_ROOT = Path("data/config/wiki-categories")
SCHEMA_VERSION = 1
_KEY_PATTERN = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
_EXCLUSION_REASONS = {
    "non_dst:dont_starve",
    "non_dst:hamlet",
    "non_dst:reign_of_giants",
    "non_dst:shipwrecked",
}


class CategoryConfigError(ValueError):
    pass


@dataclass(frozen=True)
class CategoryConfig:
    key: str
    source_url: str
    category_title: str
    expected_direct_pages: int
    expected_published_pages: int
    allowed_namespaces: Tuple[int, ...]
    excluded_titles: Tuple[Tuple[str, str], ...]
    game: str
    item_type: str
    tags: Tuple[str, ...]

    @property
    def base_url(self) -> str:
        parsed = urlsplit(self.source_url)
        return "{}://{}/".format(parsed.scheme, parsed.netloc)

    @property
    def output_path(self) -> Path:
        return Path("data/crawled/fandom-categories") / self.key


def load_category_config(
    key: str, root: Path = CATEGORY_CONFIG_ROOT
) -> CategoryConfig:
    normalized_key = _require_key(key)
    path = Path(root) / "{}.json".format(normalized_key)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise CategoryConfigError(
            "category config does not exist: {}".format(path)
        ) from error
    except (OSError, json.JSONDecodeError) as error:
        raise CategoryConfigError(
            "category config is not valid JSON: {}".format(path)
        ) from error
    if not isinstance(payload, dict):
        raise CategoryConfigError("category config must contain an object")

    expected_keys = {
        "allowedNamespaces",
        "categoryTitle",
        "excludedTitles",
        "expectedDirectPages",
        "expectedPublishedPages",
        "game",
        "itemType",
        "key",
        "schema_version",
        "sourceUrl",
        "tags",
    }
    if set(payload) != expected_keys:
        raise CategoryConfigError("category config keys are invalid")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise CategoryConfigError("category config schema_version is invalid")
    if payload.get("key") != normalized_key:
        raise CategoryConfigError("category config key does not match its path")

    source_url = _require_string(payload, "sourceUrl")
    category_title = _require_string(payload, "categoryTitle")
    _validate_source(source_url, category_title)
    direct = _require_positive_int(payload, "expectedDirectPages")
    published = _require_positive_int(payload, "expectedPublishedPages")
    if published > direct:
        raise CategoryConfigError(
            "expectedPublishedPages cannot exceed expectedDirectPages"
        )

    namespaces = payload.get("allowedNamespaces")
    if (
        not isinstance(namespaces, list)
        or not namespaces
        or not all(isinstance(value, int) for value in namespaces)
        or len(set(namespaces)) != len(namespaces)
        or any(value != 0 for value in namespaces)
    ):
        raise CategoryConfigError("allowedNamespaces must contain only unique 0")

    raw_exclusions = payload.get("excludedTitles")
    if not isinstance(raw_exclusions, dict):
        raise CategoryConfigError("excludedTitles must be an object")
    exclusions = []
    seen_titles = set()
    for title, reason in raw_exclusions.items():
        if not isinstance(title, str) or not title.strip():
            raise CategoryConfigError("excluded title must be non-empty")
        normalized_title = _normalized_title(title)
        folded = normalized_title.casefold()
        if folded in seen_titles:
            raise CategoryConfigError("excludedTitles contains a duplicate title")
        seen_titles.add(folded)
        if reason not in _EXCLUSION_REASONS:
            raise CategoryConfigError("excluded title reason is unsupported")
        exclusions.append((normalized_title, reason))
    if direct - published != len(exclusions):
        raise CategoryConfigError(
            "expected count difference must equal excludedTitles count"
        )

    game = _require_string(payload, "game")
    if game != "DST":
        raise CategoryConfigError("category game must be DST")
    item_type = _require_string(payload, "itemType")
    if not _KEY_PATTERN.fullmatch(item_type):
        raise CategoryConfigError("itemType must be a lowercase key")
    raw_tags = payload.get("tags")
    if (
        not isinstance(raw_tags, list)
        or not raw_tags
        or not all(isinstance(value, str) and value.strip() for value in raw_tags)
        or len({value.strip().casefold() for value in raw_tags}) != len(raw_tags)
    ):
        raise CategoryConfigError("tags must be unique non-empty strings")

    return CategoryConfig(
        key=normalized_key,
        source_url=source_url,
        category_title=category_title,
        expected_direct_pages=direct,
        expected_published_pages=published,
        allowed_namespaces=tuple(namespaces),
        excluded_titles=tuple(
            sorted(exclusions, key=lambda value: (value[0].casefold(), value[0]))
        ),
        game=game,
        item_type=item_type,
        tags=tuple(value.strip() for value in raw_tags),
    )


def _require_key(value: str) -> str:
    if not isinstance(value, str) or not _KEY_PATTERN.fullmatch(value.strip()):
        raise CategoryConfigError("category key must be a lowercase path key")
    return value.strip()


def _require_string(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise CategoryConfigError("{} must be a non-empty string".format(key))
    return value.strip()


def _require_positive_int(payload: Mapping[str, Any], key: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise CategoryConfigError("{} must be a positive integer".format(key))
    return value


def _validate_source(source_url: str, category_title: str) -> None:
    parsed = urlsplit(source_url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise CategoryConfigError("sourceUrl must use HTTPS")
    if parsed.query or parsed.fragment or not parsed.path.startswith("/wiki/"):
        raise CategoryConfigError("sourceUrl must be a direct wiki page URL")
    if not category_title.startswith("Category:"):
        raise CategoryConfigError("categoryTitle must start with Category:")
    source_title = _normalized_title(unquote(parsed.path[len("/wiki/") :]))
    if source_title != category_title:
        raise CategoryConfigError("sourceUrl title must match categoryTitle")


def _normalized_title(value: str) -> str:
    return " ".join(value.strip().replace("_", " ").split())
