import argparse
from pathlib import Path

from tools.extract.assets import add_base_game_asset_facts
from tools.extract.base_game import (
    derive_dependency_requests,
    enrich_prefab_modules,
    verify_snapshot_archive,
)
from tools.extract.contracts import dump_bundle, load_bundle
from tools.extract.database import write_database
from tools.extract.export_items import export_items
from tools.extract.export_json import export_catalog
from tools.extract.export_mod_markdown import collect_game_text, export_mod_markdown
from tools.extract.mod_static import extract_mod_static
from tools.extract.normalize import normalize
from tools.extract.runtime_import import (
    load_runtime_bundle,
    static_mod_version,
    static_runtime_target_ids,
)
from tools.extract.runtime_runner import run_runtime_probe
from tools.extract.publish_web_assets import publish_web_assets
from tools.extract.source_manifest import ARCHIVES, snapshot_game_sources
from tools.extract.validate import validate_catalog, write_validation_report
from tools.extract.wiki_import import import_wiki
from tools.extract.wiki_translate import build_summary_translation_cache


MOD_ROOT = Path("mod/3721846643")
TU_TIEN_TRANSLATION = Path("mod/3721859355/modmain.lua")
BASE_TRANSLATION_PO = Path("mod/3731181944/viethoa.po")
GAME_SOURCES = Path("data/sources/game")
STATIC_FACTS = Path("data/raw/mod_static.json")
RUNTIME_FACTS = Path("data/raw/runtime.json")
BASE_FACTS = Path("data/raw/base_game.json")
DATABASE = Path("data/generated/wiki.sqlite")
COVERAGE = Path("data/generated/coverage.json")
CATALOG_JSON = Path("public/data/catalog.json")
ASSETS_JSON = Path("public/data/assets.json")
ITEMS_JSON = Path("public/data/items.json")
ITEM_TEXTURES = Path("data/generated/item-textures.json")
ITEM_DETAILS_OVERRIDES = Path("data/manual/tu_tien_item_details.json")
ITEM_DETAILS_REPORT = Path("data/generated/tu-tien-item-details-report.json")
STRUCTURE_ICON_AUDIT = Path("data/generated/structure-icon-audit.json")
EFFECT_OTHER_AUDIT = Path("data/generated/effect-other-audit.json")
WEB_ASSETS = Path("public/assets/game")
MOD_TEXT = Path("docs/mod-text")
WIKI_CRAWL = Path("data/crawled/dontstarve-items")


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
    extract_static.add_argument("--mod-root", type=Path, default=MOD_ROOT)
    extract_static.add_argument(
        "--tu-tien-translation",
        type=Path,
        default=TU_TIEN_TRANSLATION,
    )
    extract_static.add_argument(
        "--base-translation-po",
        type=Path,
        default=BASE_TRANSLATION_PO,
    )
    extract_static.add_argument(
        "--output", type=Path, default=STATIC_FACTS
    )
    run_runtime = sub.add_parser("run-runtime")
    run_runtime.add_argument("--server-bin", type=Path, required=True)
    run_runtime.add_argument("--game-mods-dir", type=Path, required=True)
    run_runtime.add_argument("--workspace", type=Path, default=Path("."))
    run_runtime.add_argument("--timeout", type=float, default=180)
    run_runtime.add_argument("--static", type=Path, default=STATIC_FACTS)
    import_runtime = sub.add_parser("import-runtime")
    import_runtime.add_argument(
        "--input", type=Path, default=RUNTIME_FACTS
    )
    import_runtime.add_argument("--static", type=Path, default=STATIC_FACTS)
    enrich_base = sub.add_parser("enrich-base")
    enrich_base.add_argument(
        "--static", type=Path, default=STATIC_FACTS
    )
    enrich_base.add_argument(
        "--runtime", type=Path, default=RUNTIME_FACTS
    )
    enrich_base.add_argument(
        "--scripts", type=Path, default=GAME_SOURCES / "scripts.zip"
    )
    enrich_base.add_argument(
        "--manifest", type=Path, default=GAME_SOURCES / "manifest.json"
    )
    enrich_base.add_argument(
        "--images", type=Path, default=GAME_SOURCES / "images.zip"
    )
    enrich_base.add_argument(
        "--base-translation-po",
        type=Path,
        default=BASE_TRANSLATION_PO,
    )
    enrich_base.add_argument(
        "--output", type=Path, default=BASE_FACTS
    )
    build_db = sub.add_parser("build-db")
    build_db.add_argument(
        "--static", type=Path, default=STATIC_FACTS
    )
    build_db.add_argument(
        "--runtime", type=Path, default=RUNTIME_FACTS
    )
    build_db.add_argument(
        "--base", type=Path, default=BASE_FACTS
    )
    build_db.add_argument(
        "--output", type=Path, default=DATABASE
    )
    import_wiki_parser = sub.add_parser("import-wiki")
    import_wiki_parser.add_argument("--input", type=Path, default=WIKI_CRAWL)
    import_wiki_parser.add_argument("--database", type=Path, default=DATABASE)
    export = sub.add_parser("export")
    export.add_argument("--database", type=Path, default=DATABASE)
    export.add_argument("--catalog", type=Path, default=CATALOG_JSON)
    export.add_argument("--assets", type=Path, default=ASSETS_JSON)
    export.add_argument("--items", type=Path, default=ITEMS_JSON)
    export.add_argument("--textures", type=Path, default=ITEM_TEXTURES)
    export.add_argument(
        "--detail-overrides", type=Path, default=ITEM_DETAILS_OVERRIDES
    )
    export.add_argument("--detail-report", type=Path, default=ITEM_DETAILS_REPORT)
    export.add_argument(
        "--structure-audit", type=Path, default=STRUCTURE_ICON_AUDIT
    )
    export.add_argument(
        "--effect-other-audit", type=Path, default=EFFECT_OTHER_AUDIT
    )
    translate_wiki = sub.add_parser("translate-wiki")
    translate_wiki.add_argument(
        "--pages", type=Path, default=Path("public/data/wiki/pages")
    )
    translate_wiki.add_argument(
        "--output", type=Path, default=WIKI_CRAWL / "summary_vi.json"
    )
    translate_wiki.add_argument(
        "--manual", type=Path, default=Path("data/manual/wiki_summary_vi.json")
    )
    translate_wiki.add_argument("--workers", type=int, default=4)
    export_markdown = sub.add_parser("export-markdown")
    export_markdown.add_argument("--catalog", type=Path, default=CATALOG_JSON)
    export_markdown.add_argument("--runtime", type=Path, default=RUNTIME_FACTS)
    export_markdown.add_argument("--output", type=Path, default=MOD_TEXT)
    publish_assets = sub.add_parser("publish-assets")
    publish_assets.add_argument("--textures", type=Path, default=ITEM_TEXTURES)
    publish_assets.add_argument("--mod-root", type=Path, default=MOD_ROOT)
    publish_assets.add_argument(
        "--images", type=Path, default=GAME_SOURCES / "images.zip"
    )
    publish_assets.add_argument(
        "--manifest", type=Path, default=GAME_SOURCES / "manifest.json"
    )
    publish_assets.add_argument("--output", type=Path, default=WEB_ASSETS)
    publish_assets.add_argument("--decoder", default="ktech")
    validate = sub.add_parser("validate")
    validate.add_argument("--database", type=Path, default=DATABASE)
    validate.add_argument("--coverage", type=Path, default=COVERAGE)
    validate.add_argument("--manifest", type=Path, default=GAME_SOURCES / "manifest.json")
    validate.add_argument("--scripts", type=Path, default=GAME_SOURCES / "scripts.zip")
    validate.add_argument("--items", type=Path, default=ITEMS_JSON)
    validate.add_argument(
        "--structure-audit", type=Path, default=STRUCTURE_ICON_AUDIT
    )
    validate.add_argument(
        "--effect-other-audit", type=Path, default=EFFECT_OTHER_AUDIT
    )
    all_stages = sub.add_parser("all")
    all_stages.add_argument("--static", type=Path, default=STATIC_FACTS)
    return parser


def _extract_static_stage(
    mod_root: Path = MOD_ROOT,
    tu_tien_translation: Path = TU_TIEN_TRANSLATION,
    base_translation_po: Path = BASE_TRANSLATION_PO,
    output: Path = STATIC_FACTS,
):
    bundle = extract_mod_static(mod_root, tu_tien_translation, base_translation_po)
    dump_bundle(output, bundle)
    entity_count = len({fact.subject for fact in bundle.facts if fact.kind == "entity"})
    asset_count = sum(fact.kind == "asset" for fact in bundle.facts)
    print(f"{output} entities={entity_count} assets={asset_count} errors={len(bundle.errors)}")
    return bundle


def _import_runtime_stage(
    path: Path = RUNTIME_FACTS, static_path: Path = STATIC_FACTS
):
    static_bundle = load_bundle(static_path)
    bundle = load_runtime_bundle(
        path,
        expected_mod_version=static_mod_version(static_bundle),
        expected_targets=static_runtime_target_ids(static_bundle),
    )
    print(f"{path} facts={len(bundle.facts)} errors={len(bundle.errors)}")
    return bundle


def _enrich_base_stage(
    static_path: Path = STATIC_FACTS,
    runtime_path: Path = RUNTIME_FACTS,
    scripts: Path = GAME_SOURCES / "scripts.zip",
    manifest: Path = GAME_SOURCES / "manifest.json",
    images: Path = GAME_SOURCES / "images.zip",
    translation: Path = BASE_TRANSLATION_PO,
    output: Path = BASE_FACTS,
):
    verify_snapshot_archive(scripts, manifest)
    static_bundle = load_bundle(static_path)
    runtime_bundle = load_runtime_bundle(
        runtime_path,
        expected_mod_version=static_mod_version(static_bundle),
        expected_targets=static_runtime_target_ids(static_bundle),
    )
    requests = derive_dependency_requests(static_bundle, runtime_bundle)
    bundle = enrich_prefab_modules(scripts, requests, translation)
    bundle = add_base_game_asset_facts(bundle, images, manifest)
    dump_bundle(output, bundle)
    resolved = len({fact.subject.prefab_id for fact in bundle.facts if fact.kind == "entity"})
    unresolved = sum(error.get("code") == "unresolved_base_game_dependency" for error in bundle.errors)
    closure = sum(
        any(evidence.get("relation") == "recipe_ingredient" for evidence in fact.payload.get("requested_by", []))
        for fact in bundle.facts
        if fact.kind == "entity"
    )
    print(
        f"{output} requests={len(requests)} resolved={resolved} unresolved={unresolved} "
        f"closure={closure} facts={len(bundle.facts)} errors={len(bundle.errors)}"
    )
    return bundle


def _build_db_stage(
    static_path: Path = STATIC_FACTS,
    runtime_path: Path = RUNTIME_FACTS,
    base_path: Path = BASE_FACTS,
    output: Path = DATABASE,
):
    static_bundle = load_bundle(static_path)
    runtime_bundle = load_runtime_bundle(
        runtime_path,
        expected_mod_version=static_mod_version(static_bundle),
        expected_targets=static_runtime_target_ids(static_bundle),
    )
    bundles = [static_bundle, runtime_bundle, load_bundle(base_path)]
    catalog = normalize(bundles)
    game_text_sources, game_text_rows = collect_game_text(
        [MOD_ROOT, TU_TIEN_TRANSLATION.parent]
    )
    write_database(output, catalog, game_text_sources, game_text_rows)
    print(f"{output} entities={len(catalog.entities)} evidence={len(catalog.evidence)} conflicts={len(catalog.conflicts)}")
    return catalog


def _export_stage(
    database: Path = DATABASE,
    catalog: Path = CATALOG_JSON,
    assets: Path = ASSETS_JSON,
    items: Path = ITEMS_JSON,
    textures: Path = ITEM_TEXTURES,
    detail_overrides: Path = ITEM_DETAILS_OVERRIDES,
    detail_report: Path = ITEM_DETAILS_REPORT,
    structure_audit: Path = STRUCTURE_ICON_AUDIT,
    effect_other_audit: Path = EFFECT_OTHER_AUDIT,
) -> None:
    export_catalog(database, catalog, assets)
    export_items(
        database,
        catalog,
        assets,
        items,
        textures,
        detail_overrides_path=detail_overrides,
        detail_report_path=detail_report,
        structure_audit_path=structure_audit,
        effect_other_audit_path=effect_other_audit,
    )
    print(
        f"{catalog} {assets} {items} {textures} {detail_report} "
        f"{structure_audit} {effect_other_audit}"
    )


def _import_wiki_stage(
    input_path: Path = WIKI_CRAWL,
    database: Path = DATABASE,
):
    summary = import_wiki(database, input_path)
    print(
        f"{database} wiki_pages={summary.pages} recipes={summary.recipes} "
        f"ingredients={summary.ingredients} images={summary.images} "
        f"mapped={summary.mapped} unmatched={summary.unmatched}"
    )
    return summary


def _export_markdown_stage(
    catalog: Path = CATALOG_JSON,
    runtime: Path = RUNTIME_FACTS,
    output: Path = MOD_TEXT,
) -> None:
    export_mod_markdown(
        catalog,
        runtime,
        [MOD_ROOT, TU_TIEN_TRANSLATION.parent],
        output,
    )
    print(output)


def _validate_stage(
    database: Path = DATABASE,
    coverage: Path = COVERAGE,
    manifest: Path = GAME_SOURCES / "manifest.json",
    scripts: Path = GAME_SOURCES / "scripts.zip",
    items: Path = ITEMS_JSON,
    structure_audit: Path = STRUCTURE_ICON_AUDIT,
    effect_other_audit: Path = EFFECT_OTHER_AUDIT,
):
    report = validate_catalog(
        database, manifest, scripts, items, structure_audit, effect_other_audit
    )
    write_validation_report(coverage, report)
    print(
        f"{coverage} tu_tien={report['entity_counts'].get('tu_tien', 0)} "
        f"base_game={report['entity_counts'].get('base_game', 0)} "
        f"hard_failures={len(report['hard_failures'])} warnings={len(report['warnings'])}"
    )
    return report


def run_all(static_path: Path = STATIC_FACTS):
    """Run the offline pipeline only; runtime capture is intentionally excluded."""

    _extract_static_stage(output=static_path)
    _import_runtime_stage(static_path=static_path)
    _enrich_base_stage(static_path=static_path)
    _build_db_stage(static_path=static_path)
    _import_wiki_stage()
    _export_stage()
    return _validate_stage()


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "snapshot-game":
        manifest = snapshot_game_sources(args.game_data, args.destination)
        for name in ARCHIVES:
            print(f"{args.destination / name} {manifest['files'][name]['sha256']}")
        return 0
    if args.command == "extract-static":
        _extract_static_stage(
            args.mod_root, args.tu_tien_translation, args.base_translation_po, args.output
        )
        return 0
    if args.command == "run-runtime":
        output = run_runtime_probe(
            args.server_bin,
            args.game_mods_dir,
            args.workspace,
            args.timeout,
            args.static,
        )
        print(output)
        return 0
    if args.command == "import-runtime":
        _import_runtime_stage(args.input, args.static)
        return 0
    if args.command == "enrich-base":
        _enrich_base_stage(
            args.static,
            args.runtime,
            args.scripts,
            args.manifest,
            args.images,
            args.base_translation_po,
            args.output,
        )
        return 0
    if args.command == "build-db":
        _build_db_stage(args.static, args.runtime, args.base, args.output)
        return 0
    if args.command == "import-wiki":
        _import_wiki_stage(args.input, args.database)
        return 0
    if args.command == "export":
        _export_stage(
            args.database,
            args.catalog,
            args.assets,
            args.items,
            args.textures,
            args.detail_overrides,
            args.detail_report,
            args.structure_audit,
            args.effect_other_audit,
        )
        return 0
    if args.command == "translate-wiki":
        summary = build_summary_translation_cache(
            args.pages,
            args.output,
            workers=args.workers,
            manual_path=args.manual,
        )
        print(
            f"{args.output} pages={summary['pages']} cached={summary['cached']} "
            f"translated={summary['translated']}"
        )
        return 0
    if args.command == "export-markdown":
        _export_markdown_stage(args.catalog, args.runtime, args.output)
        return 0
    if args.command == "publish-assets":
        published = publish_web_assets(
            args.textures,
            args.mod_root,
            args.images,
            args.manifest,
            args.output,
            args.decoder,
        )
        print(f"{args.output} textures={len(published)}")
        return 0
    if args.command == "validate":
        report = _validate_stage(
            args.database,
            args.coverage,
            args.manifest,
            args.scripts,
            args.items,
            args.structure_audit,
            args.effect_other_audit,
        )
        return 1 if report["hard_failures"] else 0
    if args.command == "all":
        report = run_all(args.static)
        return 1 if report["hard_failures"] else 0
    raise SystemExit(f"stage not wired: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
