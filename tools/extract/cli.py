import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dst-extract")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("snapshot-game", "extract-static", "run-runtime", "import-runtime", "enrich-base", "build-db", "export", "validate", "all"):
        sub.add_parser(name)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    raise SystemExit(f"stage not wired: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
