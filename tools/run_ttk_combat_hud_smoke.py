"""Boot a copied Phàm Nhân mod on a disposable, offline DST dedicated server."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / '.superpowers/pham-nhan-hud-smoke'
SOURCE_RUNTIME = ROOT / '.superpowers/dst-runtime-audit'


def sync_copy(source, destination):
    destination.mkdir(parents=True, exist_ok=True)
    for path in source.rglob('*'):
        if not path.is_file():
            continue
        target = destination / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or (path.stat().st_size, path.stat().st_mtime_ns) != (target.stat().st_size, target.stat().st_mtime_ns):
            shutil.copy2(path, target)


def main():
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sync_copy(SOURCE_RUNTIME / 'bin64', RUNTIME / 'bin64')
    if not (RUNTIME / 'data').exists():
        # Only creates a directory junction to existing read-only game assets.
        subprocess.run(['cmd', '/c', 'mklink', '/J', str(RUNTIME / 'data'), str((SOURCE_RUNTIME / 'data').resolve())], check=True)
    sync_copy(ROOT / 'mods/PhamNhanTuTien', RUNTIME / 'mods/PhamNhanTuTien')
    cluster = RUNTIME / 'storage/audit/Cluster_HUD'
    master = cluster / 'Master'
    master.mkdir(parents=True, exist_ok=True)
    (cluster / 'cluster.ini').write_text('[NETWORK]\ncluster_name = Pham Nhan HUD offline audit\noffline_cluster = true\nlan_only_cluster = true\n[GAMEPLAY]\ngame_mode = survival\nmax_players = 1\npause_when_empty = false\n[SHARD]\nshard_enabled = false\n')
    (master / 'server.ini').write_text('[NETWORK]\nserver_port = 12203\n[SHARD]\nis_master = true\n')
    (master / 'modoverrides.lua').write_text('return { ["PhamNhanTuTien"] = { enabled = true } }')
    (master / 'worldgenoverride.lua').write_text('return {override_enabled=true,preset="SURVIVAL_TOGETHER",overrides={world_size="small"}}')
    (RUNTIME / 'mods/modsettings.lua').write_text('ForceEnableMod("PhamNhanTuTien")\n')
    script = (ROOT / '.superpowers/pham-nhan-hud-smoke.lua').read_text(encoding='utf-8')
    command = [str(RUNTIME / 'bin64/dontstarve_dedicated_server_nullrenderer_x64.exe'),
        '-persistent_storage_root', str(RUNTIME / 'storage'), '-conf_dir', 'audit',
        '-cluster', 'Cluster_HUD', '-shard', 'Master', '-port', '12203',
        '-offline', '-console', '-skip_update_server_mods']
    log_path = RUNTIME / 'smoke.log'
    success = False
    with log_path.open('w', encoding='utf-8') as output:
        process = subprocess.Popen(command, cwd=RUNTIME / 'bin64', stdin=subprocess.PIPE,
            stdout=output, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        print(f'Disposable server PID {process.pid}; {log_path}', flush=True)
        try:
            deadline, dispatched = time.monotonic() + 300, False
            while process.poll() is None and time.monotonic() < deadline:
                time.sleep(1)
                log = log_path.read_text(encoding='utf-8', errors='replace')
                lines = '\n'.join(line for line in log.splitlines() if 'RemoteCommandInput:' not in line)
                if any(marker in lines for marker in ('LUA ERROR', 'MOD ERROR:', 'PHAM_NHAN_HUD_FAIL', 'Server failed to start!', 'Unhandled exception')):
                    break
                if not dispatched and 'Telling Client our new session identifier:' in log:
                    payload = 'assert(loadstring(' + json.dumps(script, ensure_ascii=False) + '))()\n'
                    process.stdin.write(payload.encode('utf-8'))
                    process.stdin.flush()
                    dispatched = True
                    print('Runtime HUD assertions dispatched', flush=True)
                if 'PHAM_NHAN_HUD_PASS' in lines:
                    success = True
                    break
        finally:
            if process.poll() is None:
                try:
                    process.stdin.write(b'c_shutdown(true)\n')
                    process.stdin.flush()
                    process.wait(timeout=20)
                except (OSError, subprocess.TimeoutExpired):
                    process.terminate()
                    process.wait(timeout=10)
    final = log_path.read_text(encoding='utf-8', errors='replace')
    if 'LUA ERROR' in final:
        success = False
    print(final[-14000:])
    return not success


if __name__ == '__main__':
    raise SystemExit(main())
