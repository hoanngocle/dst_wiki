"""One-time, fail-closed source import after a recorded TuTienKy backup."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'mods/mod_steam/3780347550'
DEST = ROOT / 'mods/PhamNhanTuTien'
BASE = ROOT / '.superpowers/ttk-solo-integration/baseline.json'


def main():
    baseline = json.loads(BASE.read_text(encoding='utf-8'))
    assert Path(baseline['backup']).is_file(), 'Backup required'
    assert not (DEST / 'SOLO_SOURCE_MANIFEST.json').exists(), 'Integration already applied'
    mapping = {
        'modmain.lua': 'main/ttk_solo_source.lua',
        'modworldgenmain.lua': 'main/ttk_solo_worldgen.lua',
        'modinfo.lua': 'provenance/solo/modinfo.lua',
        # Workshop's binary manifest describes the standalone package only.
        'mod.manifest': 'provenance/solo/mod.manifest',
    }
    records = []
    for relative, digest in sorted(baseline['source'].items()):
        src = SOURCE / relative
        target = mapping.get(relative, relative)
        assert hashlib.sha256(src.read_bytes()).hexdigest() == digest, relative
        assert not (DEST / target).exists(), f'Refusing overwrite: {target}'
        records.append({'source': relative, 'destination': target, 'sha256': digest})
    for record in records:
        target = DEST / record['destination']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE / record['source'], target)

    info = (DEST / 'modinfo.lua').read_text(encoding='utf-8-sig')
    info = info.replace('Solo là tùy chọn.', 'Tích hợp đầy đủ Solo Leveling: chỉ số, kỹ năng, nhiệm vụ, quân đoàn và hầm ngục.')
    info = info.replace('version = "0.9.0"', 'version = "0.10.0"')
    info = info.replace('author = "Bản chuyển thể độc lập từ tài nguyên Tu Tiên"',
                        'author = "Tu Tiên Ký; Solo Leveling: Saikuno"')
    solo_info = (SOURCE / 'modinfo.lua').read_text(encoding='utf-8-sig')
    solo_config = solo_info[solo_info.index('local a = {'):]
    solo_config = solo_config.replace('configuration_options = {', 'local configuration_options = {', 1)
    info += '\n-- Solo Leveling 2.2.7 configuration (original keys and defaults).\n'
    info += 'local function SoloOptions()\n' + solo_config + '\nreturn configuration_options\nend\n'
    info += '''local solo_options = SoloOptions()
for i = 1, #solo_options do
    local option = solo_options[i]
    option.label = "Solo: " .. option.label
    configuration_options[#configuration_options + 1] = option
end
'''
    (DEST / 'modinfo.lua').write_text(info, encoding='utf-8')
    entry = (DEST / 'modmain.lua').read_text(encoding='utf-8-sig')
    entry = 'require("ttk_solo_guard").Check(GLOBAL, modname)\n' + entry
    entry += '\n-- Solo is included and always loaded by this single mod.\nmodimport("main/ttk_solo_bootstrap.lua")\n'
    (DEST / 'modmain.lua').write_text(entry, encoding='utf-8')
    (DEST / 'SOLO_SOURCE_MANIFEST.json').write_text(json.dumps({
        'source': 'Solo Leveling', 'version': '2.2.7', 'author': 'Saikuno',
        'workshop_id': '3780347550', 'files': records,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Imported {len(records)} source files; original source bytes preserved.')


if __name__ == '__main__':
    main()
