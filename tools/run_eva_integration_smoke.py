"""Offline DST smoke, isolated from real saves and the Steam mod folders."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / '.superpowers/eva-vietnamese/fresh-server'


def main():
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    parser = argparse.ArgumentParser()
    parser.add_argument('--reload', action='store_true')
    parser.add_argument('--initialize-existing', action='store_true',
                        help='Create smoke fixtures in an already generated disposable world')
    parser.add_argument('--migration', action='store_true', help='Use a separate legacy migration cluster')
    parser.add_argument('--legacy-start', action='store_true', help='Generate fixtures with the original two mods')
    args = parser.parse_args()
    global RUNTIME
    if args.migration:
        RUNTIME = RUNTIME.with_name('server-migration')
    if args.legacy_start and (not args.migration or args.reload):
        parser.error('--legacy-start requires --migration and cannot use --reload')
    source = ROOT / '.superpowers/dst-runtime-audit'
    RUNTIME.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source / 'bin64', RUNTIME / 'bin64', dirs_exist_ok=True)
    if not (RUNTIME / 'data').exists():
        subprocess.run(['cmd', '/c', 'mklink', '/J', str(RUNTIME / 'data'), str((source / 'data').resolve())], check=True)
    if args.legacy_start:
        baseline = json.loads((ROOT / '.superpowers/ttk-solo-integration/baseline.json').read_text(encoding='utf-8'))
        with zipfile.ZipFile(baseline['backup']) as archive:
            archive.extractall(RUNTIME / 'mods')
        shutil.copytree(ROOT / 'mods/mod_steam/3780347550', RUNTIME / 'mods/SoloLeveling', dirs_exist_ok=True)
    else:
        shutil.copytree(ROOT / 'mods/PhamNhanTuTien', RUNTIME / 'mods/PhamNhanTuTien', dirs_exist_ok=True)
    cluster = RUNTIME / 'storage/audit/Cluster_SoloIntegration'
    master = cluster / 'Master'
    if not args.reload and not args.initialize_existing and (master / 'save').exists():
        raise SystemExit('A world already exists; use --reload or a new disposable runtime path.')
    master.mkdir(parents=True, exist_ok=True)
    (cluster / 'cluster.ini').write_text('[NETWORK]\ncluster_name = TTK Solo integration audit\noffline_cluster = true\nlan_only_cluster = true\n[GAMEPLAY]\ngame_mode = survival\nmax_players = 1\npause_when_empty = false\n[SHARD]\nshard_enabled = false\n')
    port = 12194 if args.migration else 12205
    (master / 'server.ini').write_text(f'[NETWORK]\nserver_port = {port}\n[SHARD]\nis_master = true\n')
    solo_override = ', ["SoloLeveling"] = { enabled = true }' if args.legacy_start else ''
    (master / 'modoverrides.lua').write_text('return { ["PhamNhanTuTien"] = { enabled = true }' + solo_override + ' }')
    (master / 'worldgenoverride.lua').write_text('return {override_enabled=true,preset="SURVIVAL_TOGETHER",overrides={world_size="small"}}')
    (RUNTIME / 'mods/modsettings.lua').write_text('ForceEnableMod("PhamNhanTuTien")\n' + ('ForceEnableMod("SoloLeveling")\n' if args.legacy_start else ''))
    command = [str(RUNTIME / 'bin64/dontstarve_dedicated_server_nullrenderer_x64.exe'),
               '-persistent_storage_root', str(RUNTIME / 'storage'), '-conf_dir', 'audit',
               '-cluster', 'Cluster_SoloIntegration', '-shard', 'Master', '-port', str(port),
               '-offline', '-console', '-skip_update_server_mods']
    log_path = RUNTIME / ('legacy_create.log' if args.legacy_start else 'reload.log' if args.reload else 'create.log')
    expected = 'EVA_SMOKE_PASS'
    success = False
    with log_path.open('w', encoding='utf-8') as log:
        process = subprocess.Popen(command, cwd=RUNTIME / 'bin64', stdin=subprocess.PIPE,
                                   stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        print(f'Started disposable DST server PID {process.pid}; {log_path}', flush=True)
        try:
            deadline = time.monotonic() + 300
            sent = False
            while process.poll() is None and time.monotonic() < deadline:
                time.sleep(1)
                text = log_path.read_text(encoding='utf-8', errors='replace')
                lines = '\n'.join(line for line in text.splitlines() if 'RemoteCommandInput:' not in line)
                if any(marker in lines for marker in ('LUA ERROR', 'MOD ERROR:', 'EVA_SMOKE_FAIL',
                                                      'Server failed to start!', 'Unhandled exception')):
                    break
                if not sent and 'Telling Client our new session identifier:' in text:
                    script = (ROOT / 'mods/PhamNhanTuTien/tools/eva_integration_smoke.lua').read_text(encoding='utf-8')
                    script = 'assert(loadstring(' + json.dumps(script, ensure_ascii=False) + '))()'
                    if args.reload:
                        script = 'rawset(_G,"TTK_SOLO_RELOAD",true); ' + script
                    process.stdin.write((script + '\n').encode('utf-8'))
                    process.stdin.flush()
                    sent = True
                    print('Runtime assertions dispatched', flush=True)
                if expected in lines:
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
    print(final[-10000:])
    raise SystemExit(0 if success else 1)


if __name__ == '__main__':
    main()
