"""Run combat acceptance in a fresh disposable DST cluster, preserving its log."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / '.superpowers/pham-nhan-combat-runtime'
SEED = ROOT / '.superpowers/dst-runtime-audit'
BINARY = 'dontstarve_dedicated_server_nullrenderer_x64.exe'
CLUSTER = 'Cluster_CombatAudit'
PORT = 11017
PASS = 'PHAM_NHAN_COMBAT_SMOKE_PASS'
FAIL = 'PHAM_NHAN_COMBAT_SMOKE_FAIL'


def validate_seed(seed: Path) -> None:
    if not (seed / 'bin64' / BINARY).is_file():
        raise FileNotFoundError(f'DST dedicated-server binary is missing: {seed / "bin64" / BINARY}')
    if not (seed / 'data/databundles/scripts.zip').is_file():
        raise FileNotFoundError(f'DST runtime data is missing: {seed / "data/databundles/scripts.zip"}')


def console_payload(script: str) -> str:
    # Reuse the bounded-console protocol from the boss audit: a single long
    # console line is silently truncated by DST, and source contains Unicode.
    variable = 'PHAM_NHAN_COMBAT_SMOKE_SOURCE'
    lines = [f'rawset(_G,"{variable}","")']
    for offset in range(0, len(script), 2500):
        chunk = json.dumps(script[offset:offset + 2500], ensure_ascii=False)
        lines.append(f'rawset(_G,"{variable}",rawget(_G,"{variable}")..{chunk})')
    lines.append(
        f'local fn,problem=loadstring(rawget(_G,"{variable}"),"@combat_smoke.lua"); '
        f'if not fn then print("{FAIL}","compile",tostring(problem)) else '
        'local ok,detail=xpcall(fn,debug.traceback); '
        f'if not ok then print("{FAIL}","bootstrap",tostring(detail)) end end'
    )
    return '\n'.join(lines) + '\n'


def filtered_log(text: str) -> str:
    return '\n'.join(line for line in text.splitlines() if 'RemoteCommandInput:' not in line)


def log_result(text: str) -> str | None:
    filtered = filtered_log(text)
    if any(marker in filtered for marker in (
        FAIL, 'LUA ERROR', 'MOD ERROR:', 'Disabling PhamNhanTuTien',
        'Server failed to start!', 'Unhandled exception',
    )):
        return 'fail'
    return 'pass' if PASS in filtered else None


def prepare_runtime() -> Path:
    validate_seed(SEED)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    runtime = (ARTIFACTS / ('run-' + uuid.uuid4().hex[:12])).resolve()
    if runtime.parent != ARTIFACTS.resolve():
        raise RuntimeError(f'Unexpected disposable runtime path: {runtime}')
    runtime.mkdir()
    # Use the established audit's binary sync, read-only game-data junction,
    # complete mod copy and offline cluster configuration. A fresh directory
    # means its replacement/reset branches are never entered.
    spec = importlib.util.spec_from_file_location('pham_nhan_boss_runtime', ROOT / 'tools/run_phamnhan_boss_smoke.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    helper.RUNTIME, helper.CLUSTER, helper.PORT = runtime, CLUSTER, PORT
    helper.SOURCE_RUNTIME = SEED
    helper.prepare_runtime(False)
    return runtime


def stop_server(process: subprocess.Popen, timeout: float = 20) -> None:
    try:
        if process.poll() is None:
            try:
                if process.stdin is not None:
                    process.stdin.write(b'c_shutdown(false)\n')
                    process.stdin.flush()
                process.wait(timeout=timeout)
            except (OSError, subprocess.TimeoutExpired):
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
    finally:
        if process.stdin is not None:
            process.stdin.close()


def run(timeout: float = 420) -> int:
    runtime = prepare_runtime()
    script = (ROOT / 'mods/PhamNhanTuTien/tools/combat_smoke.lua').read_text(encoding='utf-8')
    payload = console_payload(script).encode('utf-8')
    command = [str(runtime / 'bin64' / BINARY),
               '-persistent_storage_root', str(runtime / 'storage'), '-conf_dir', 'audit',
               '-cluster', CLUSTER, '-shard', 'Master', '-port', str(PORT),
               '-offline', '-console', '-skip_update_server_mods']
    log_path = runtime / 'combat.log'
    result = None
    with log_path.open('w', encoding='utf-8') as output:
        process = subprocess.Popen(command, cwd=runtime / 'bin64', stdin=subprocess.PIPE,
                                   stdout=output, stderr=subprocess.STDOUT,
                                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        print(f'Disposable combat server PID {process.pid}; log: {log_path}', flush=True)
        try:
            deadline = time.monotonic() + timeout
            dispatched = False
            while process.poll() is None and time.monotonic() < deadline:
                time.sleep(.5)
                text = log_path.read_text(encoding='utf-8', errors='replace')
                result = log_result(text)
                if result is not None:
                    break
                if not dispatched and 'Telling Client our new session identifier:' in text:
                    process.stdin.write(payload)
                    process.stdin.flush()
                    dispatched = True
                    print('Combat assertions dispatched', flush=True)
        finally:
            stop_server(process)
    final = log_path.read_text(encoding='utf-8', errors='replace')
    result = log_result(final)
    if result == 'pass':
        print('\n'.join(line for line in filtered_log(final).splitlines()
                        if 'PHAM_NHAN_COMBAT_' in line))
        return 0
    print(filtered_log(final)[-12000:])
    print(f'Combat smoke failed, exited or timed out without a clean {PASS}; retained {log_path}')
    return 1


def main() -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--timeout', type=float, default=420, help='Maximum server runtime in seconds')
    args = parser.parse_args()
    try:
        return run(args.timeout)
    except (OSError, RuntimeError) as error:
        print(f'Combat smoke environment/setup failure: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
