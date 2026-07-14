import argparse
from pathlib import Path

from tools.extract.base_game import (
    derive_dependency_requests,
    enrich_dependencies,
    verify_snapshot_archive,
)
from tools.extract.contracts import dump_bundle, load_bundle
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
    enrich_base = sub.add_parser("enrich-base")
    enrich_base.add_argument(
        "--static", type=Path, default=Path("data/raw/mod_static.json")
    )
    enrich_base.add_argument(
        "--runtime", type=Path, default=Path("data/raw/runtime.json")
    )
    enrich_base.add_argument(
        "--scripts", type=Path, default=Path("data/sources/game/scripts.zip")
    )
    enrich_base.add_argument(
        "--manifest", type=Path, default=Path("data/sources/game/manifest.json")
    )
    enrich_base.add_argument(
        "--base-translation-po",
        type=Path,
        default=Path("mod/3731181944/viethoa.po"),
    )
    enrich_base.add_argument(
        "--output", type=Path, default=Path("data/raw/base_game.json")
    )
    for name in ("build-db", "export", "validate", "all"):
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
    if args.command == "enrich-base":
        verify_snapshot_archive(args.scripts, args.manifest)
        static_bundle = load_bundle(args.static)
        runtime_bundle = load_runtime_bundle(args.runtime)
        requests = derive_dependency_requests(static_bundle, runtime_bundle)
        bundle = enrich_dependencies(
            args.scripts, requests, args.base_translation_po
        )
        dump_bundle(args.output, bundle)
        resolved = len(
            {fact.subject.prefab_id for fact in bundle.facts if fact.kind == "entity"}
        )
        unresolved = sum(
            error.get("code") == "unresolved_base_game_dependency"
            for error in bundle.errors
        )
        closure = sum(
            any(
                evidence.get("relation") == "recipe_ingredient"
                for evidence in fact.payload.get("requested_by", [])
            )
            for fact in bundle.facts
            if fact.kind == "entity"
        )
        print(
            f"{args.output} requests={len(requests)} resolved={resolved} "
            f"unresolved={unresolved} closure={closure} facts={len(bundle.facts)} "
            f"errors={len(bundle.errors)}"
        )
        return 0
    raise SystemExit(f"stage not wired: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
