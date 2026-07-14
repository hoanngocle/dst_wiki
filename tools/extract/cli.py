import argparse
from pathlib import Path

from tools.extract.contracts import dump_bundle
from tools.extract.mod_static import extract_mod_static
from tools.extract.runtime_import import load_runtime_bundle
from tools.extract.runtime_runner import run_runtime_probe
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
    run_runtime = sub.add_parser("run-runtime")
    run_runtime.add_argument("--server-bin", type=Path, required=True)
    run_runtime.add_argument("--game-mods-dir", type=Path, required=True)
    run_runtime.add_argument("--workspace", type=Path, default=Path("."))
    run_runtime.add_argument("--timeout", type=float, default=180)
    import_runtime = sub.add_parser("import-runtime")
    import_runtime.add_argument(
        "--input", type=Path, default=Path("data/raw/runtime.json")
    )
    for name in ("enrich-base", "build-db", "export", "validate", "all"):
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
    if args.command == "run-runtime":
        output = run_runtime_probe(
            args.server_bin,
            args.game_mods_dir,
            args.workspace,
            args.timeout,
        )
        print(output)
        return 0
    if args.command == "import-runtime":
        bundle = load_runtime_bundle(args.input)
        print(
            f"{args.input} facts={len(bundle.facts)} errors={len(bundle.errors)}"
        )
        return 0
    raise SystemExit(f"stage not wired: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
