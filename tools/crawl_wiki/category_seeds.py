from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set
from urllib.parse import quote, urlsplit

from tools.crawl_wiki.category_config import CategoryConfig


class CategorySeedError(ValueError):
    pass


@dataclass(frozen=True)
class CategorySeed:
    page_id: int
    namespace: int
    title: str
    canonical_url: str
    accepted: bool
    reason: Optional[str]


def normalize_category_members(
    config: CategoryConfig, members: Iterable[Mapping[str, Any]]
) -> List[CategorySeed]:
    exclusions = {
        _normalized_title(title).casefold(): reason
        for title, reason in config.excluded_titles
    }
    seen_page_ids: Dict[int, tuple] = {}
    seeds = []
    seen_exclusions: Set[str] = set()

    for member in members:
        page_id, namespace, title = _member_identity(member)
        identity = (namespace, title)
        previous = seen_page_ids.get(page_id)
        if previous is not None:
            if previous != identity:
                raise CategorySeedError(
                    "category member page ID has conflicting identities"
                )
            continue
        seen_page_ids[page_id] = identity

        normalized_title = _normalized_title(title)
        if namespace not in config.allowed_namespaces:
            accepted = False
            reason = "excluded_namespace:{}".format(namespace)
        else:
            folded = normalized_title.casefold()
            reason = exclusions.get(folded)
            accepted = reason is None
            if reason is not None:
                seen_exclusions.add(folded)
        seeds.append(
            CategorySeed(
                page_id=page_id,
                namespace=namespace,
                title=normalized_title,
                canonical_url=_page_url(config.source_url, normalized_title),
                accepted=accepted,
                reason=reason,
            )
        )

    direct = [
        seed for seed in seeds if seed.namespace in config.allowed_namespaces
    ]
    accepted = [seed for seed in direct if seed.accepted]
    if len(direct) != config.expected_direct_pages:
        raise CategorySeedError(
            "direct category member count mismatch: expected {}, got {}".format(
                config.expected_direct_pages, len(direct)
            )
        )
    missing_exclusions = sorted(set(exclusions) - seen_exclusions)
    if missing_exclusions:
        raise CategorySeedError(
            "configured excluded titles are missing from discovery: {}".format(
                ", ".join(missing_exclusions)
            )
        )
    if len(accepted) != config.expected_published_pages:
        raise CategorySeedError(
            "published category member count mismatch: expected {}, got {}".format(
                config.expected_published_pages, len(accepted)
            )
        )
    return sorted(
        seeds,
        key=lambda seed: (seed.title.casefold(), seed.title, seed.page_id),
    )


def _member_identity(member: Mapping[str, Any]):
    if not isinstance(member, Mapping):
        raise CategorySeedError("category member must be an object")
    page_id = member.get("pageid")
    namespace = member.get("ns")
    title = member.get("title")
    if (
        not isinstance(page_id, int)
        or isinstance(page_id, bool)
        or page_id <= 0
        or not isinstance(namespace, int)
        or isinstance(namespace, bool)
        or not isinstance(title, str)
        or not title.strip()
    ):
        raise CategorySeedError("category member identity is invalid")
    return page_id, namespace, title.strip()


def _normalized_title(value: str) -> str:
    return " ".join(value.strip().replace("_", " ").split())


def _page_url(source_url: str, title: str) -> str:
    parsed = urlsplit(source_url)
    encoded = quote(title.replace(" ", "_"), safe="/:()_-'!,$*+.~")
    return "{}://{}/wiki/{}".format(parsed.scheme, parsed.netloc, encoded)
