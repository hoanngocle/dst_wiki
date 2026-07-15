import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence, Tuple

from tools.crawl_wiki.client import (
    DEFAULT_USER_AGENT,
    ClientError,
    MediaWikiClient,
)
from tools.crawl_wiki.crawler import SelectiveItemsCrawler, WikiCrawler
from tools.crawl_wiki.models import CrawlSummary, SUPPORTED_NAMESPACES
from tools.crawl_wiki.parser import normalize_base_url
from tools.crawl_wiki.storage import CrawlStorage, StorageError


DEFAULT_BASE_URL = "https://dontstarve.wiki.gg/"
DEFAULT_FULL_OUTPUT = Path("data/crawled/dontstarve-wiki")
DEFAULT_ITEMS_OUTPUT = Path("data/crawled/dontstarve-items")
DEFAULT_NAMESPACES = (0, 14, 6)


def _base_url(value: str) -> str:
    try:
        return normalize_base_url(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error))


def _non_negative_float(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("value must be a number")
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be non-negative")
    return parsed


def _positive_float(value: str) -> float:
    parsed = _non_negative_float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("value must be an integer")
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def _namespaces(value: str) -> Tuple[int, ...]:
    try:
        parsed = tuple(int(part.strip()) for part in value.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError("namespaces must be comma-separated integers")
    if not parsed or len(set(parsed)) != len(parsed):
        raise argparse.ArgumentTypeError("namespaces must be unique and non-empty")
    unsupported = [value for value in parsed if value not in SUPPORTED_NAMESPACES]
    if unsupported:
        raise argparse.ArgumentTypeError(
            "unsupported namespace IDs: {} (allowed: 0,6,14)".format(
                ",".join(str(item) for item in unsupported)
            )
        )
    return parsed


class _ItemBudgetAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        del parser, option_string
        setattr(namespace, self.dest, values)
        setattr(namespace, "item_budget_explicit", True)


def resolve_output(args: argparse.Namespace) -> Path:
    if args.output is not None:
        return args.output
    if args.profile == "items":
        return DEFAULT_ITEMS_OUTPUT
    return DEFAULT_FULL_OUTPUT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dontstarve-wiki-crawler",
        description=(
            "Export either the full wiki or approved item-list sections as "
            "resumable JSONL plus selected original images."
        ),
    )
    parser.set_defaults(item_budget_explicit=False)
    parser.add_argument(
        "--profile", choices=("full", "items"), default="full"
    )
    parser.add_argument("--base-url", type=_base_url, default=DEFAULT_BASE_URL)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--namespaces", type=_namespaces, default=DEFAULT_NAMESPACES
    )
    parser.add_argument("--delay", type=_non_negative_float, default=0.5)
    parser.add_argument("--timeout", type=_positive_float, default=30.0)
    parser.add_argument("--max-attempts", type=_positive_int, default=5)
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    parser.add_argument("--max-pages", type=_positive_int)
    parser.add_argument(
        "--item-budget",
        type=_positive_int,
        default=100,
        action=_ItemBudgetAction,
        help="maximum selected item detail pages processed this invocation",
    )
    parser.add_argument("--skip-images", action="store_true")
    parser.add_argument("--fresh", action="store_true")
    parser.add_argument("--retry-errors", action="store_true")
    parser.add_argument(
        "--log-level",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        default="INFO",
    )
    return parser


def run_crawl(args: argparse.Namespace) -> CrawlSummary:
    if args.profile == "full" and args.item_budget_explicit:
        raise ValueError("--item-budget is only valid for the items profile")
    if args.profile == "items" and args.max_pages is not None:
        raise ValueError("--max-pages is only valid for the full profile")
    output = resolve_output(args)
    namespaces = (0,) if args.profile == "items" else args.namespaces
    options = {
        "profile": args.profile,
        "base_url": args.base_url,
        "namespaces": list(namespaces),
        "delay": args.delay,
        "timeout": args.timeout,
        "max_attempts": args.max_attempts,
        "user_agent": args.user_agent,
        "max_pages": args.max_pages,
        "item_budget": args.item_budget if args.profile == "items" else None,
        "skip_images": args.skip_images,
    }
    with CrawlStorage(
        output,
        args.base_url,
        namespaces,
        fresh=args.fresh,
        profile=args.profile,
    ) as storage:
        if args.retry_errors:
            storage.retry_errors()
        client = MediaWikiClient(
            args.base_url,
            delay=args.delay,
            timeout=args.timeout,
            max_attempts=args.max_attempts,
            user_agent=args.user_agent,
        )
        if args.profile == "items":
            crawler = SelectiveItemsCrawler(
                client,
                storage,
                item_budget=args.item_budget,
                skip_images=args.skip_images,
            )
        else:
            crawler = WikiCrawler(
                client,
                storage,
                namespaces,
                skip_images=args.skip_images,
                max_pages=args.max_pages,
            )
        return crawler.run(options)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        summary = run_crawl(args)
    except KeyboardInterrupt:
        print("crawl interrupted; checkpoint preserved", file=sys.stderr)
        return 130
    except (ClientError, StorageError, OSError, ValueError) as error:
        print("crawler setup/fatal error: {}".format(error), file=sys.stderr)
        return 2
    print(
        "pages={} images={} links={} failures={} pending_pages={} "
        "pending_images={} output={}".format(
            summary.pages,
            summary.images,
            summary.links,
            summary.failures,
            summary.pending_pages,
            summary.pending_images,
            resolve_output(args).resolve(),
        )
    )
    return summary.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
