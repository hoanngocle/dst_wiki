import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from tools.crawl_wiki.state_paths import (
    StatePathError,
    resolve_category_state_paths,
)
from tools.crawl_wiki.url_registry import UrlRegistry, UrlRegistryError


FANDOM_ORIGIN = "https://dontstarve.fandom.com"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dontstarve-category-crawler-state",
        description="Manage repository-shared Fandom Category crawler state.",
    )
    parser.add_argument("--url-registry", type=Path)
    parser.add_argument("--shared-page-cache", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)

    initialize = commands.add_parser("init")
    initialize.add_argument("--snapshot", type=Path, required=True)

    commands.add_parser("audit")

    repair = commands.add_parser("repair")
    repair.add_argument("--snapshot", type=Path, required=True)

    snapshot = commands.add_parser("snapshot")
    snapshot.add_argument("--snapshot", type=Path, required=True)
    return parser


def run(args: argparse.Namespace) -> int:
    paths = resolve_category_state_paths(
        Path.cwd(),
        registry=args.url_registry,
        cache=args.shared_page_cache,
    )
    registry = UrlRegistry(paths.registry, paths.cache, FANDOM_ORIGIN)

    if args.command == "init":
        initialized = registry.initialize_from_snapshot(args.snapshot)
        exported = registry.export_snapshot(args.snapshot)
        print("initialized={} snapshot={}".format(initialized, exported))
        return 0

    if not registry.path.exists():
        raise UrlRegistryError(
            "live URL registry does not exist; run the init command first"
        )

    if args.command == "audit":
        audits = registry.audit()
        invalid = tuple(item for item in audits if item.issue is not None)
        counts = {
            status: sum(item.status == status for item in audits)
            for status in ("New", "Doing", "Done")
        }
        print(
            "urls={} valid={} invalid={} New={} Doing={} Done={}".format(
                len(audits),
                len(audits) - len(invalid),
                len(invalid),
                counts["New"],
                counts["Doing"],
                counts["Done"],
            )
        )
        for item in invalid:
            print("{} {} {}".format(item.status, item.issue, item.url))
        return 1 if invalid else 0

    if args.command == "repair":
        repaired = registry.repair_invalid_done()
        exported = registry.export_snapshot(args.snapshot)
        print("repaired={} snapshot={}".format(len(repaired), exported))
        return 0

    exported = registry.export_snapshot(args.snapshot)
    print("snapshot={}".format(exported))
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run(args)
    except (OSError, StatePathError, UrlRegistryError, ValueError) as error:
        print("category crawler state error: {}".format(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
