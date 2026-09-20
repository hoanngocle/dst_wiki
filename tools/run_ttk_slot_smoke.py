"""Run the slot machine in a separate DST world; never touch a player's save."""
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / '.superpowers/choujiangji-audit'
source = ROOT / '.superpowers/dst-runtime-audit'
shutil.copytree(source / 'bin64', runtime / 'bin64', dirs_exist_ok=True)
shutil.copytree(ROOT / 'mods/PhamNhanTuTien', runtime / 'mods/PhamNhanTuTien', dirs_exist_ok=True)
cluster = runtime / 'storage/audit/Cluster_Slot'
master = cluster / 'Master'
master.mkdir(parents=True, exist_ok=True)
(cluster / 'cluster.ini').write_text('[NETWORK]\ncluster_name = Slot audit\noffline_cluster = true\nlan_only_cluster = true\n[GAMEPLAY]\ngame_mode = survival\nmax_players = 1\npause_when_empty = false\n[SHARD]\nshard_enabled = false\n')
(master / 'server.ini').write_text('[NETWORK]\nserver_port = 11997\n[SHARD]\nis_master = true\n')
(master / 'modoverrides.lua').write_text('return { ["PhamNhanTuTien"] = { enabled = true } }')
(master / 'worldgenoverride.lua').write_text('return {override_enabled=true,preset="SURVIVAL_TOGETHER",overrides={world_size="small"}}')
(runtime / 'mods/modsettings.lua').write_text('ForceEnableMod("PhamNhanTuTien")\n')
args = [str(runtime / 'bin64/dontstarve_dedicated_server_nullrenderer_x64.exe'),
        '-persistent_storage_root', str(runtime / 'storage'), '-conf_dir', 'audit',
        '-cluster', 'Cluster_Slot', '-shard', 'Master', '-offline', '-console', '-skip_update_server_mods']
out = runtime / 'slot_smoke.log'
success = False
with out.open('w', encoding='utf-8') as log:
    process = subprocess.Popen(args, cwd=runtime / 'bin64', stdin=subprocess.PIPE,
                               stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        deadline = time.time() + 220
        sent = False
        while process.poll() is None and time.time() < deadline:
            time.sleep(1)
            text = out.read_text(encoding='utf-8', errors='replace')
            lines = '\n'.join(line for line in text.splitlines() if 'RemoteCommandInput:' not in line)
            if not sent and 'Telling Client our new session identifier:' in text:
                script = (ROOT / 'mods/PhamNhanTuTien/tools/choujiangji_smoke.lua').read_text(encoding='utf-8')
                # One console command; source comments must not swallow the rest.
                script = ' '.join(line for line in script.splitlines() if not line.lstrip().startswith('--'))
                process.stdin.write((script + '\n').encode()); process.stdin.flush()
                sent = True
                print('Slot smoke dispatched', flush=True)
            if 'TTK_SLOT_SMOKE_FAIL' in lines or 'LUA ERROR' in lines:
                break
            if 'TTK_SLOT_SMOKE_PASS' in lines:
                success = True
                break
    finally:
        if process.poll() is None:
            try:
                process.stdin.write(b'c_shutdown(false)\n'); process.stdin.flush(); process.wait(timeout=15)
            except (OSError, subprocess.TimeoutExpired):
                process.terminate(); process.wait(timeout=10)
print(out.read_text(encoding='utf-8', errors='replace')[-9000:])
raise SystemExit(0 if success else 1)
