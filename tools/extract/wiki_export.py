"""Build compact wiki overlays and publish per-page detail artifacts."""

import html
import json
import os
import re
import shutil
import sqlite3
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
from urllib.parse import urljoin, urlparse

from tools.extract.wiki_mapping import normalize_identity


JsonObject = Dict[str, Any]
FULL_UV = {"u1": 0.0, "u2": 1.0, "v1": 0.0, "v2": 1.0}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


@dataclass(frozen=True)
class WikiAsset:
    title: str
    source_path: Path
    published_name: str
    public_path: str
    sha256: str
    mime: str
    width: Optional[int]
    height: Optional[int]


@dataclass(frozen=True)
class WikiExport:
    overlays: Dict[str, JsonObject]
    standalone_items: Tuple[JsonObject, ...]
    details: Tuple[JsonObject, ...]
    assets: Tuple[WikiAsset, ...]


def _empty_export() -> WikiExport:
    return WikiExport({}, (), (), ())


def _table_exists(connection: sqlite3.Connection, table: str) -> bool:
    return (
        connection.execute(
            "select 1 from sqlite_master where type='table' and name=?", (table,)
        ).fetchone()
        is not None
    )


def _categories(raw: str) -> List[str]:
    value = json.loads(raw)
    if not isinstance(value, list):
        raise ValueError("wiki page categories_json must contain an array")
    return [
        category[len("Category:") :] if category.startswith("Category:") else category
        for category in value
        if isinstance(category, str)
    ]


def _file_identity(value: str) -> str:
    value = html.unescape(value).replace("_", " ").strip()
    value = re.sub(r"^(?:File|Image):", "", value, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", value).casefold()


def _extract_filename(value: str) -> Optional[str]:
    match = re.search(
        r"(?:File:)?([^|\[\]{}\n]+?\.(?:png|jpe?g|gif|webp))",
        value,
        flags=re.IGNORECASE,
    )
    return match.group(1).strip() if match else None


def _page_image_identities(wikitext: str) -> Tuple[str, ...]:
    preferred = []
    for match in re.finditer(
        r"\|\s*(?:icon|image)\d*\s*=\s*([^\n]+)",
        wikitext,
        flags=re.IGNORECASE,
    ):
        filename = _extract_filename(match.group(1))
        if filename:
            preferred.append(_file_identity(filename))
    referenced = [
        _file_identity(match.group(1))
        for match in re.finditer(
            r"\[\[(?:File|Image):([^|\]]+)",
            wikitext,
            flags=re.IGNORECASE,
        )
    ]
    return tuple(dict.fromkeys(preferred + referenced))


class _Sanitizer(HTMLParser):
    allowed_tags = {
        "a", "aside", "b", "blockquote", "br", "code", "dd", "div", "dl",
        "dt", "em", "figcaption", "figure", "h1", "h2", "h3", "h4", "h5",
        "h6", "hr", "i", "img", "li", "ol", "p", "pre", "section", "small",
        "span", "strong", "sub", "sup", "table", "tbody", "td", "th", "thead",
        "tr", "u", "ul",
    }
    void_tags = {"br", "hr", "img"}
    blocked_tags = {"embed", "iframe", "object", "script", "style", "template"}
    blocked_classes = {"catlinks", "mw-editsection", "navbox", "navbox-styles", "noexcerpt", "printfooter"}
    allowed_attributes = {
        "alt", "class", "colspan", "height", "href", "id", "rowspan", "src",
        "title", "width",
    }

    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.parts: List[str] = []
        self.suppressed_stack: List[str] = []

    def handle_starttag(self, tag: str, attrs: Sequence[Tuple[str, Optional[str]]]):
        tag = tag.casefold()
        if self.suppressed_stack:
            if tag not in self.void_tags:
                self.suppressed_stack.append(tag)
            return
        class_value = next(
            (value for name, value in attrs if name.casefold() == "class" and value),
            "",
        )
        class_tokens = set(class_value.split())
        if tag in self.blocked_tags or class_tokens & self.blocked_classes:
            if tag not in self.void_tags:
                self.suppressed_stack.append(tag)
            return
        if tag not in self.allowed_tags:
            return
        safe_attrs = []
        for name, value in attrs:
            name = name.casefold()
            if name not in self.allowed_attributes or value is None or name.startswith("on"):
                continue
            if name in {"href", "src"}:
                resolved = urljoin(self.base_url, value)
                parsed = urlparse(resolved)
                if parsed.scheme not in {"http", "https"}:
                    continue
                value = resolved
            safe_attrs.append(f' {name}="{html.escape(value, quote=True)}"')
        self.parts.append("<" + tag + "".join(safe_attrs) + ">")

    def handle_endtag(self, tag: str):
        tag = tag.casefold()
        if self.suppressed_stack:
            if tag == self.suppressed_stack[-1]:
                self.suppressed_stack.pop()
            return
        if tag in self.allowed_tags and tag not in self.void_tags:
            self.parts.append(f"</{tag}>")

    def handle_data(self, data: str):
        if not self.suppressed_stack:
            self.parts.append(html.escape(data))


def sanitize_html(value: str, base_url: str) -> str:
    sanitizer = _Sanitizer(base_url)
    sanitizer.feed(value)
    sanitizer.close()
    return "".join(sanitizer.parts)


def _summary(value: str, limit: int = 360) -> Optional[str]:
    normalized = re.sub(r"\s+", " ", value).strip()
    if not normalized:
        return None
    if len(normalized) <= limit:
        return normalized
    shortened = normalized[: limit + 1].rsplit(" ", 1)[0].rstrip(" ,.;:")
    return shortened + "…"


def _category(categories: Sequence[str]) -> str:
    normalized = {normalize_identity(category) for category in categories}
    if normalized & {
        "items", "food", "resources", "plants", "craftable items", "tools",
        "weapons", "armor", "clothing",
    }:
        return "item"
    if normalized & {"bosses", "boss mobs"}:
        return "boss"
    if normalized & {"mobs", "creatures", "animals"}:
        return "mob"
    if normalized & {"structures", "craftable structures"}:
        return "structure"
    if normalized & {"characters", "playable characters"}:
        return "character"
    return "other"


def _sprite(asset: Optional[WikiAsset]) -> Optional[JsonObject]:
    if asset is None:
        return None
    return {"src": asset.public_path, "uv": dict(FULL_UV)}


def _metadata(page: Mapping[str, Any], related: Sequence[Mapping[str, Any]]) -> JsonObject:
    return {
        "pageId": page["page_id"],
        "title": page["title"],
        "canonicalUrl": page["canonical_url"],
        "categories": list(page["categories"]),
        "mappingState": "mapped" if page["selected"] else "unmatched",
        "detailUrl": f"/data/wiki/pages/{page['page_id']}.json",
        "relatedPages": [
            {
                "pageId": value["page_id"],
                "title": value["title"],
                "canonicalUrl": value["canonical_url"],
                "detailUrl": f"/data/wiki/pages/{value['page_id']}.json",
            }
            for value in related
        ],
    }


def _item(
    item_id: str,
    prefab_id: str,
    page: Mapping[str, Any],
    related: Sequence[Mapping[str, Any]],
    recipe: Optional[JsonObject],
) -> JsonObject:
    return {
        "id": item_id,
        "prefabId": prefab_id,
        "namespace": "base_game",
        "category": _category(page["categories"]),
        "name": page["title"],
        "englishName": page["title"],
        "description": _summary(page["plain_text"]),
        "craftingNote": None,
        "sprite": _sprite(page["primary_asset"]),
        "recipe": recipe,
        "wiki": _metadata(page, related),
    }


def _compact_recipe(
    recipes: Sequence[JsonObject],
    pages_by_name: Mapping[str, Sequence[Mapping[str, Any]]],
) -> Optional[JsonObject]:
    if not recipes:
        return None
    recipe = recipes[0]
    ingredients = []
    for ingredient in recipe["ingredients"]:
        amount = ingredient["amount"]
        if amount <= 0:
            continue
        candidates = pages_by_name.get(normalize_identity(ingredient["title"]), ())
        ingredient_page = candidates[0] if len(candidates) == 1 else None
        if ingredient_page is None:
            slug = normalize_identity(ingredient["title"]).replace(" ", "-") or "unknown"
            ingredient_id = f"wiki-ingredient:{slug}"
            ingredient_sprite = None
        elif ingredient_page["selected"]:
            ingredient_id = (
                f"{ingredient_page['entity_namespace']}:"
                f"{ingredient_page['entity_prefab_id']}"
            )
            ingredient_sprite = _sprite(ingredient_page["primary_asset"])
        else:
            ingredient_id = f"wiki:{ingredient_page['page_id']}"
            ingredient_sprite = _sprite(ingredient_page["primary_asset"])
        normalized_amount = int(amount) if float(amount).is_integer() else float(amount)
        ingredients.append(
            {
                "id": ingredient_id,
                "name": ingredient["title"],
                "amount": normalized_amount,
                "sprite": ingredient_sprite,
            }
        )
    return {"outputCount": 1, "ingredients": ingredients}


def load_wiki_export(database_path: Path, crawl_root: Path) -> WikiExport:
    database_path = Path(database_path)
    crawl_root = Path(crawl_root)
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        if not _table_exists(connection, "wiki_pages"):
            return _empty_export()
        page_rows = connection.execute(
            "select p.*,m.entity_namespace,m.entity_prefab_id,m.method,"
            "m.confidence,m.selected from wiki_pages p join wiki_entity_mappings m "
            "on m.page_id=p.page_id order by p.page_id"
        ).fetchall()
        image_rows = connection.execute(
            "select * from wiki_images order by title"
        ).fetchall()
        recipe_rows = connection.execute(
            "select * from wiki_recipes order by page_id,recipe_id"
        ).fetchall()
        ingredient_rows = connection.execute(
            "select * from wiki_recipe_ingredients order by recipe_id,position"
        ).fetchall()

    images_by_identity: Dict[str, WikiAsset] = {}
    for row in image_rows:
        suffix = Path(row["local_path"]).suffix.casefold()
        if suffix not in IMAGE_SUFFIXES:
            suffix = ".img"
        published_name = row["sha256"] + suffix
        asset = WikiAsset(
            title=row["title"],
            source_path=crawl_root / row["local_path"],
            published_name=published_name,
            public_path=f"/assets/wiki/{published_name}",
            sha256=row["sha256"],
            mime=row["mime"],
            width=row["width"],
            height=row["height"],
        )
        images_by_identity[_file_identity(row["title"])] = asset

    pages = []
    pages_by_id = {}
    referenced_assets: Dict[str, WikiAsset] = {}
    for row in page_rows:
        value = dict(row)
        value["categories"] = _categories(row["categories_json"])
        identities = _page_image_identities(row["wikitext"])
        page_assets = tuple(
            images_by_identity[identity]
            for identity in identities
            if identity in images_by_identity
        )
        for asset in page_assets:
            referenced_assets[asset.published_name] = asset
        value["assets"] = page_assets
        value["primary_asset"] = page_assets[0] if page_assets else None
        pages.append(value)
        pages_by_id[value["page_id"]] = value

    ingredients_by_recipe: Dict[str, List[JsonObject]] = {}
    for row in ingredient_rows:
        ingredients_by_recipe.setdefault(row["recipe_id"], []).append(
            {
                "position": row["position"],
                "title": row["ingredient_title"],
                "amount": row["amount"],
                "amountText": row["amount_text"],
            }
        )
    recipes_by_page: Dict[int, List[JsonObject]] = {}
    for row in recipe_rows:
        recipe = {
            "recipeId": row["recipe_id"],
            "result": row["result_title"],
            "source": row["source_template"],
            "station": row["station"],
            "tab": row["tab"],
            "tier": row["tier"],
            "character": row["character"],
            "dlc": row["dlc"],
            "variant": row["variant"],
            "note": row["note"],
            "ingredients": ingredients_by_recipe.get(row["recipe_id"], []),
        }
        recipes_by_page.setdefault(row["page_id"], []).append(recipe)

    pages_by_name: Dict[str, List[Mapping[str, Any]]] = {}
    for page in pages:
        pages_by_name.setdefault(normalize_identity(page["title"]), []).append(page)

    groups: Dict[str, List[Mapping[str, Any]]] = {}
    unmatched = []
    for page in pages:
        if page["selected"]:
            key = f"{page['entity_namespace']}:{page['entity_prefab_id']}"
            groups.setdefault(key, []).append(page)
        else:
            unmatched.append(page)

    overlays = {}
    fallbacks = []
    for key, candidates in sorted(groups.items()):
        ordered = sorted(
            candidates,
            key=lambda page: (
                -float(page["confidence"]),
                int(page["title"].casefold().endswith("/dst")),
                page["page_id"],
            ),
        )
        primary = ordered[0]
        recipe = _compact_recipe(recipes_by_page.get(primary["page_id"], []), pages_by_name)
        prefab_id = key.split(":", 1)[1]
        item = _item(key, prefab_id, primary, ordered[1:], recipe)
        overlays[key] = item
        fallbacks.append(item)
    for page in unmatched:
        recipe = _compact_recipe(recipes_by_page.get(page["page_id"], []), pages_by_name)
        fallbacks.append(
            _item(
                f"wiki:{page['page_id']}",
                f"wiki-{page['page_id']}",
                page,
                (),
                recipe,
            )
        )

    details = []
    for page in pages:
        details.append(
            {
                "schema_version": 1,
                "pageId": page["page_id"],
                "title": page["title"],
                "displayTitle": page["display_title"],
                "canonicalUrl": page["canonical_url"],
                "revision": {
                    "id": page["revision_id"],
                    "timestamp": page["revision_timestamp"],
                    "sha1": page["revision_sha1"],
                },
                "html": sanitize_html(page["html"], page["canonical_url"]),
                "wikitext": page["wikitext"],
                "plainText": page["plain_text"],
                "categories": list(page["categories"]),
                "redirectTarget": page["redirect_target"],
                "images": [
                    {
                        "title": asset.title,
                        "src": asset.public_path,
                        "mime": asset.mime,
                        "width": asset.width,
                        "height": asset.height,
                    }
                    for asset in page["assets"]
                ],
                "recipes": recipes_by_page.get(page["page_id"], []),
            }
        )
    return WikiExport(
        overlays=dict(sorted(overlays.items())),
        standalone_items=tuple(sorted(fallbacks, key=lambda item: item["id"])),
        details=tuple(sorted(details, key=lambda detail: detail["pageId"])),
        assets=tuple(referenced_assets[key] for key in sorted(referenced_assets)),
    )


def _overlay_item(existing: JsonObject, overlay: JsonObject) -> JsonObject:
    result = dict(existing)
    result["wiki"] = overlay["wiki"]
    for field in ("englishName", "description", "sprite", "recipe"):
        if result.get(field) is None and overlay.get(field) is not None:
            result[field] = overlay[field]
    return result


def merge_wiki_items(items: List[JsonObject], wiki: WikiExport) -> List[JsonObject]:
    merged = []
    seen = set()
    for item in items:
        item_id = item["id"]
        if item_id in seen:
            raise ValueError(f"duplicate item id: {item_id}")
        overlay = wiki.overlays.get(item_id)
        merged.append(_overlay_item(item, overlay) if overlay else item)
        seen.add(item_id)
    for item in wiki.standalone_items:
        if item["id"] in seen:
            continue
        published = item
        if item["id"] in wiki.overlays:
            page_id = item["wiki"]["pageId"]
            published = dict(item)
            published["id"] = f"wiki:{page_id}"
            published["prefabId"] = f"wiki-{page_id}"
        if published["id"] in seen:
            raise ValueError(f"duplicate item id: {published['id']}")
        merged.append(published)
        seen.add(published["id"])
    return sorted(merged, key=lambda item: item["id"])


def _write_json(path: Path, value: JsonObject) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _replace_tree(output: Path, writer) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name("." + output.name + ".tmp")
    backup = output.with_name("." + output.name + ".backup")
    for path in (temporary, backup):
        if path.exists():
            shutil.rmtree(path)
    temporary.mkdir()
    try:
        writer(temporary)
        if output.exists():
            os.replace(output, backup)
        os.replace(temporary, output)
        if backup.exists():
            shutil.rmtree(backup)
    except BaseException:
        if temporary.exists():
            shutil.rmtree(temporary)
        if backup.exists() and not output.exists():
            os.replace(backup, output)
        raise


def export_wiki_artifacts(
    wiki: WikiExport,
    details_path: Path,
    assets_path: Path,
) -> None:
    def write_details(root: Path) -> None:
        for detail in wiki.details:
            _write_json(root / f"{detail['pageId']}.json", detail)

    def write_assets(root: Path) -> None:
        for asset in wiki.assets:
            if not asset.source_path.is_file():
                raise ValueError(f"wiki source image is missing: {asset.source_path}")
            shutil.copyfile(asset.source_path, root / asset.published_name)

    _replace_tree(Path(details_path), write_details)
    _replace_tree(Path(assets_path), write_assets)
