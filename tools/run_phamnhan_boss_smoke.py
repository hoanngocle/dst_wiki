"""Run the Pham Nhan nine-boss audit in an isolated offline DST cluster."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
SOURCE_RUNTIME = ROOT / ".superpowers/dst-runtime-audit"
RUNTIME = ROOT / ".superpowers/pham-nhan-boss-audit"
CLUSTER = "Cluster_BossAudit"
# Offline LAN clusters are restricted by DST to 10998..11018.
PORT = 11013


def sync_tree(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        target = destination / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or (
            path.stat().st_size,
            path.stat().st_mtime_ns,
        ) != (
            target.stat().st_size,
            target.stat().st_mtime_ns,
        ):
            shutil.copy2(path, target)


def prepare_runtime(reload: bool) -> tuple[Path, Path]:
    sync_tree(SOURCE_RUNTIME / "bin64", RUNTIME / "bin64")
    data = RUNTIME / "data"
    if not data.exists():
        subprocess.run(
            [
                "cmd",
                "/c",
                "mklink",
                "/J",
                str(data),
                str((SOURCE_RUNTIME / "data").resolve()),
            ],
            check=True,
        )

    # This is a disposable copy. Replacing it prevents removed source files from
    # lingering between audit runs while leaving the working mod untouched.
    copied_mod = RUNTIME / "mods/PhamNhanTuTien"
    if copied_mod.resolve().parent != (RUNTIME / "mods").resolve():
        raise SystemExit(f"Refusing to replace unexpected mod-copy path: {copied_mod}")
    if copied_mod.exists():
        shutil.rmtree(copied_mod)
    shutil.copytree(ROOT / "mods/PhamNhanTuTien", copied_mod)

    cluster = RUNTIME / f"storage/audit/{CLUSTER}"
    master = cluster / "Master"
    save = master / "save"
    if reload and not save.exists():
        raise SystemExit("No boss-audit world exists. Run the create phase first.")
    if not reload and save.exists():
        raise SystemExit(
            "The disposable boss-audit world already exists; use --reload or --reset."
        )

    master.mkdir(parents=True, exist_ok=True)
    (cluster / "cluster.ini").write_text(
        "[NETWORK]\n"
        "cluster_name = Pham Nhan nine boss offline audit\n"
        "offline_cluster = true\n"
        "lan_only_cluster = true\n"
        "[GAMEPLAY]\n"
        "game_mode = survival\n"
        "max_players = 1\n"
        "pause_when_empty = false\n"
        "[SHARD]\n"
        "shard_enabled = false\n",
        encoding="utf-8",
    )
    (master / "server.ini").write_text(
        f"[NETWORK]\nserver_port = {PORT}\n[SHARD]\nis_master = true\n",
        encoding="utf-8",
    )
    (master / "modoverrides.lua").write_text(
        'return { ["PhamNhanTuTien"] = { enabled = true } }', encoding="utf-8"
    )
    (master / "worldgenoverride.lua").write_text(
        'return {override_enabled=true,preset="SURVIVAL_TOGETHER",'
        'overrides={world_size="small"}}',
        encoding="utf-8",
    )
    (RUNTIME / "mods/modsettings.lua").write_text(
        'ForceEnableMod("PhamNhanTuTien")\n', encoding="utf-8"
    )
    return master, copied_mod


def reset_world() -> None:
    target = (RUNTIME / f"storage/audit/{CLUSTER}").resolve()
    audit_storage = (RUNTIME / "storage/audit").resolve()
    if target.parent != audit_storage:
        raise SystemExit(f"Refusing to remove unexpected path: {target}")
    if target.exists():
        shutil.rmtree(target)


def run_server(reload: bool, final_reload: bool = False) -> int:
    master, _ = prepare_runtime(reload or final_reload)
    smoke_path = ROOT / "mods/PhamNhanTuTien/tools/boss_smoke.lua"
    script = smoke_path.read_text(encoding="utf-8")
    phase = "final_reload" if final_reload else "reload" if reload else "create"
    expected = f"PHAM_NHAN_BOSS_{phase.upper()}_PASS"
    failure = "PHAM_NHAN_BOSS_FAIL"
    # DST's console silently truncates very long command lines. Assemble the
    # audit source in bounded commands, then compile it with traceback support.
    payload_lines = [
        f'rawset(_G, "PHAM_NHAN_BOSS_SMOKE_PHASE", "{phase}"); '
        'rawset(_G, "PHAM_NHAN_BOSS_SMOKE_SOURCE", "")'
    ]
    for offset in range(0, len(script), 3000):
        chunk = json.dumps(script[offset : offset + 3000], ensure_ascii=False)
        payload_lines.append(
            'rawset(_G,"PHAM_NHAN_BOSS_SMOKE_SOURCE",'
            f'rawget(_G,"PHAM_NHAN_BOSS_SMOKE_SOURCE")..{chunk})'
        )
    payload_lines.append(
        "local __boss_smoke,__boss_compile=loadstring("
        'rawget(_G,"PHAM_NHAN_BOSS_SMOKE_SOURCE"),"@pham_nhan_boss_smoke.lua"); '
        'if not __boss_smoke then print("PHAM_NHAN_BOSS_FAIL",'
        '"compile",tostring(__boss_compile)) else '
        "local __boss_ok,__boss_error=xpcall(__boss_smoke,debug.traceback); "
        'if not __boss_ok then print("PHAM_NHAN_BOSS_FAIL","bootstrap",'
        "tostring(__boss_error)) end end"
    )
    payload = "\n".join(payload_lines) + "\n"

    command = [
        str(RUNTIME / "bin64/dontstarve_dedicated_server_nullrenderer_x64.exe"),
        "-persistent_storage_root",
        str(RUNTIME / "storage"),
        "-conf_dir",
        "audit",
        "-cluster",
        CLUSTER,
        "-shard",
        "Master",
        "-port",
        str(PORT),
        "-offline",
        "-console",
        "-skip_update_server_mods",
    ]
    log_path = RUNTIME / f"{phase}.log"
    success = False
    with log_path.open("w", encoding="utf-8") as output:
        process = subprocess.Popen(
            command,
            cwd=RUNTIME / "bin64",
            stdin=subprocess.PIPE,
            stdout=output,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        print(f"Started disposable boss audit PID {process.pid}; {log_path}", flush=True)
        try:
            deadline = time.monotonic() + 420
            dispatched = False
            while process.poll() is None and time.monotonic() < deadline:
                time.sleep(1)
                log = log_path.read_text(encoding="utf-8", errors="replace")
                filtered = "\n".join(
                    line for line in log.splitlines() if "RemoteCommandInput:" not in line
                )
                if any(
                    marker in filtered
                    for marker in (
                        "LUA ERROR",
                        "MOD ERROR:",
                        "Disabling PhamNhanTuTien",
                        failure,
                        "Server failed to start!",
                        "Unhandled exception",
                    )
                ):
                    break
                if not dispatched and "Telling Client our new session identifier:" in log:
                    assert process.stdin is not None
                    process.stdin.write(payload.encode("utf-8"))
                    process.stdin.flush()
                    dispatched = True
                    print(f"Dispatched {phase} assertions", flush=True)
                if expected in filtered:
                    success = True
                    break
        finally:
            if process.poll() is None:
                try:
                    assert process.stdin is not None
                    process.stdin.write(b"c_shutdown(true)\n")
                    process.stdin.flush()
                    process.wait(timeout=30)
                except (OSError, subprocess.TimeoutExpired):
                    process.terminate()
                    process.wait(timeout=10)

    final = log_path.read_text(encoding="utf-8", errors="replace")
    final_filtered = "\n".join(line for line in final.splitlines() if "RemoteCommandInput:" not in line)
    if any(
        marker in final_filtered
        for marker in ("LUA ERROR", "MOD ERROR:", "Disabling PhamNhanTuTien", failure)
    ):
        success = False
    if success:
        print("\n".join(line for line in final_filtered.splitlines()
                        if "]: PHAM_NHAN_BOSS_" in line and "SUPPORT_TRY" not in line))
    else:
        print(final_filtered[-10000:])
    if not success:
        print(f"Audit did not finish cleanly with marker {expected!r}; world: {master}")
    return 0 if success else 1


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reload", action="store_true", help="Validate the saved create-phase world")
    parser.add_argument("--final-reload", action="store_true", help="Verify all nine stay dead after the final Ziyun kill")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete only the disposable boss-audit cluster before creating it",
    )
    args = parser.parse_args()
    if sum((args.reset, args.reload, args.final_reload)) > 1:
        parser.error("--reset, --reload and --final-reload cannot be combined")
    if args.reset:
        reset_world()
    return run_server(args.reload, args.final_reload)


if __name__ == "__main__":
    raise SystemExit(main())
