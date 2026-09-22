from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.extract.pham_nhan.export import build_snapshot, write_snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the source-backed Phàm Nhân item snapshot.")
    parser.add_argument("--mod-root", type=Path, default=Path("mods/PhamNhanTuTien"))
    parser.add_argument("--output", type=Path, default=Path("data/generated/pham-nhan-items.json"))
    parser.add_argument("--report", type=Path, default=Path("data/generated/pham-nhan-items-report.json"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    snapshot, report, _ = build_snapshot(args.mod_root)
    return 0 if write_snapshot(snapshot, report, args.output, args.report, args.check) else 1


if __name__ == "__main__":
    raise SystemExit(main())
