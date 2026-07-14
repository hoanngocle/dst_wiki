import argparse
from pathlib import Path

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
    for name in ("extract-static", "run-runtime", "import-runtime", "enrich-base", "build-db", "export", "validate", "all"):
        sub.add_parser(name)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "snapshot-game":
        manifest = snapshot_game_sources(args.game_data, args.destination)
        for name in ARCHIVES:
            print(f"{args.destination / name} {manifest['files'][name]['sha256']}")
        return 0
    raise SystemExit(f"stage not wired: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
