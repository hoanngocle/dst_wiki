"""Run the umbrella regression test on an isolated local DST server."""
from pathlib import Path
import subprocess
import time
import shutil
import sys
import re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / '.superpowers/dst-runtime-audit'
source = ROOT / 'mods/PhamNhanTuTien'
shutil.copytree(source, runtime / 'mods/PhamNhanTuTien', dirs_exist_ok=True)
cluster_name = 'Cluster_NhatVu_' + str(int(time.time()))
conf_dir = 'nhatvu_' + str(int(time.time()))
cluster = runtime / 'storage' / conf_dir / cluster_name
(cluster / 'Master').mkdir(parents=True, exist_ok=True)
(cluster / 'cluster.ini').write_text('[NETWORK]\ncluster_name = Umbrella test\noffline_cluster = true\nlan_only_cluster = true\ncluster_password = local-test\n[GAMEPLAY]\ngame_mode = survival\nmax_players = 1\npvp = false\npause_when_empty = false\n[SHARD]\nshard_enabled = false\n')
(cluster / 'Master/server.ini').write_text('[NETWORK]\nserver_port = 11996\n[SHARD]\nis_master = true\n')
(cluster / 'Master/modoverrides.lua').write_text('return {["PhamNhanTuTien"]={enabled=true}}')
(cluster / 'Master/worldgenoverride.lua').write_text('return {override_enabled=true,preset="SURVIVAL_TOGETHER",overrides={world_size="small"}}')
test = (source / 'tests/test_nhatvuphuonghoa.lua').read_text(encoding='utf-8')
test = ' '.join(line for line in test.splitlines() if not line.lstrip().startswith('--'))
command = '(function() ' + test + ' end)()\n'
out = runtime / 'nhatvu_test_output.txt'
args = [str(runtime/'bin64/dontstarve_dedicated_server_nullrenderer_x64.exe'),
        '-persistent_storage_root',str(runtime/'storage'),'-conf_dir',conf_dir,
        '-cluster',cluster_name,'-shard','Master','-offline','-console','-skip_update_server_mods']
with out.open('w',encoding='utf-8') as log:
    p = subprocess.Popen(args,cwd=runtime/'bin64',stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    deadline = time.time()+180
    sent = False
    try:
        while p.poll() is None and time.time()<deadline:
            time.sleep(1)
            text = out.read_text(encoding='utf-8',errors='replace')
            if not sent and 'Telling Client our new session identifier:' in text:
                p.stdin.write(command.encode('utf-8')); p.stdin.flush(); sent=True
                print('Sent umbrella tests to isolated server',flush=True)
            results = '\n'.join(line for line in text.splitlines() if 'RemoteCommandInput:' not in line)
            if re.search(r'\]: NHATVU_TEST_PASS\s', results) or 'LUA ERROR' in results or 'NHATVU: prefab must be registered' in results:
                break
    finally:
        if p.poll() is None:
            try:
                p.stdin.write(b'c_shutdown(false)\n');p.stdin.flush();p.wait(timeout=10)
            except (OSError,subprocess.TimeoutExpired):
                p.terminate();p.wait(timeout=10)
text = out.read_text(encoding='utf-8',errors='replace')
print(text[-9000:])
sys.exit(0 if re.search(r'\]: NHATVU_TEST_PASS\s', text) and 'LUA ERROR' not in text else 1)
