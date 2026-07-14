import argparse
from pathlib import Path

from tools.extract.contracts import dump_bundle
from tools.extract.mod_static import extract_mod_static
from tools.extract.source_manifest import ARCHIVES, snapshot_game_sources


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dst-extract")
    sub = parser.add_subparsers(dest="command", required=True)
    snapshot = sub.add_parser("snapshot-game")
    snapshot.add_argument("--game-data", type=Path, required=True)
    snapshot.add_argument(
        "--destination",
        type=Path,
        default=Path("data/sources/game"),
    )
    extract_static = sub.add_parser("extract-static")
    extract_static.add_argument("--mod-root", type=Path, default=Path("mod/3721846643"))
    extract_static.add_argument(
        "--tu-tien-translation",
        type=Path,
        default=Path("mod/3721859355/modmain.lua"),
    )
    extract_static.add_argument(
        "--base-translation-po",
        type=Path,
        default=Path("mod/3731181944/viethoa.po"),
    )
    extract_static.add_argument(
        "--output", type=Path, default=Path("data/raw/mod_static.json")
    )
    for name in ("run-runtime", "import-runtime", "enrich-base", "build-db", "export", "validate", "all"):
        sub.add_parser(name)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "snapshot-game":
        manifest = snapshot_game_sources(args.game_data, args.destination)
        for name in ARCHIVES:
            print(f"{args.destination / name} {manifest['files'][name]['sha256']}")
        return 0
    if args.command == "extract-static":
        bundle = extract_mod_static(
            args.mod_root, args.tu_tien_translation, args.base_translation_po
        )
        dump_bundle(args.output, bundle)
        entity_count = len(
            {fact.subject for fact in bundle.facts if fact.kind == "entity"}
        )
        asset_count = sum(fact.kind == "asset" for fact in bundle.facts)
        print(
            f"{args.output} entities={entity_count} assets={asset_count} errors={len(bundle.errors)}"
        )
        return 0
    raise SystemExit(f"stage not wired: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
