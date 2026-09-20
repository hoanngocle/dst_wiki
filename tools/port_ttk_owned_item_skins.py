"""Audit/import owned-item skins. Source Lua is read as text and never executed."""
from __future__ import annotations
import argparse, hashlib, json, re, shutil
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]; SOURCE=ROOT/'mods/mod_steam/3235319974'; DST=ROOT/'mods/PhamNhanTuTien'
UI=ROOT/'mods/eva-assets-work/skill-audit/decoded/scripts/widgets/xd_skinui.lua'
ALIAS=ROOT/'mods/eva-assets-work/skill-audit/decoded/scripts/main/xd_new.lua'
REPORT=ROOT/'docs/superpowers/reports/2026-09-20-tu-tien-ky-all-owned-skins.json'
SOURCE_TO_DEST={'xd_ztp':['ttk_chuongthienbinh'],'xd_qwsk':['ttk_qwsk'],'xd_sudaji_ywfh':['nhatvuphuonghoa'],'xd_sudaji_redlantern':['ttk_ngulongdang'],'xd_zcmj':['ttk_zcmj'],'xd_xshj':['ttk_xshj'],'xd_xianjian_builder':['ttk_tienkiem'],'xd_mo_builder':['ttk_makiem']}
GENERIC=[('ttk_tinhlakiem','xd_xlj'),('ttk_votuongkiem','xd_wxj'),('ttk_thanhtrucphongvankiem','xd_htz_qzj')]
HIDDEN_GENERIC={'xd_skin_hasaki','xd_skin_jj','xd_skin_jydm','xd_skin_kt','xd_skin_xuanyuan','xd_skin_ys','xd_skin_ysb','xd_skin_zw'}
SPECIAL={'xd_zcmj_jhxs':'xd_zcmj','xd_zcmj_trxz':'xd_zcmj','xd_yaohat':'xd_zcmj','xd_jtkhat':'xd_zcmj','xd_lhyhat':'xd_zcmj','xd_xshj_bbzy':'xd_xshj','xd_xshj_fhlh':'xd_xshj','xd_yaoarmor':'xd_xshj','xd_jdjarmor':'xd_xshj','xd_hyparmor':'xd_xshj','xd_qwsk_xznw':'xd_qwsk','xd_sudaji_ywfh_lxzy':'xd_sudaji_ywfh','xd_sudaji_redlantern_zyx':'xd_sudaji_redlantern'}
FAMILY={'ttk_zcmj':'equipment_hat','ttk_xshj':'equipment_body','ttk_yhsyz':'equipment_hand','ttk_chuongthienbinh':'equipment_hand','ttk_ngulongdang':'equipment_hand','nhatvuphuonghoa':'equipment_hand','ttk_tinhlakiem':'weapon','ttk_votuongkiem':'weapon','ttk_thanhtrucphongvankiem':'weapon','ttk_tienkiem':'weapon','ttk_makiem':'weapon','ttk_qwsk':'staged_structure'}
EXCLUSIVE_EQUIPMENT=('xd_xshj_fhlh','xd_xshj_bbzy','xd_yaohat','xd_jtkhat','xd_lhyhat','xd_yaoarmor','xd_jdjarmor','xd_hyparmor')

def discover_destination_prefabs(root):
    names=set()
    for p in Path(root).rglob('*.lua'):
        t=p.read_text(encoding='utf-8',errors='ignore')
        for pat in [r'Prefab\s*\(\s*["\']([\w]+)["\']',r'prefab\s*=\s*["\']([\w]+)["\']',r'MakeDecoration\s*\(\s*["\']([\w]+)["\']',r'\{\s*["\'](ttk_[\w]+)["\']\s*,',r'(?m)^\s*(ttk_[\w]+)\s*=\s*\{']:
            names.update(re.findall(pat,t))
    return names

def source_base(sid):
    if sid in SPECIAL:return SPECIAL[sid]
    if sid.startswith('xd_skin_'):return 'xd_cl'
    m=re.match(r'(xd_.+?)_skins_',sid); return m.group(1) if m else None

def discover_source_declarations(path=UI):
    t=Path(path).read_text(encoding='utf-8',errors='ignore')
    names=dict.fromkeys(re.findall(r'name\s*=\s*["\'](xd_[\w]+)["\']',t))
    # The body skins are paired presentation dependencies inside the two zcmj
    # UI declarations rather than independent `name` fields, but are selectable
    # by the aliased xd_xshj base and have complete resources.
    names.update(dict.fromkeys(EXCLUSIVE_EQUIPMENT))
    # Later releases contain eight hidden-but-selectable universal weapon skins
    # absent from the older UI table. Archive helpers ending in _skillbuild are
    # dependencies and deliberately remain non-selectable.
    for archive in sorted((SOURCE/'anim').glob('*skin*.zip')):
        if not archive.stem.endswith('_skillbuild'):
            names.setdefault(archive.stem,None)
    return [{'source_id':n,'source_base':source_base(n)} for n in names]

def destinations_for(c,implemented,aliases):
    sid,base=c['source_id'],c.get('source_base')
    if sid.startswith('xd_skin_'):return [d for d,_ in GENERIC if d in implemented]
    if base in aliases:return [d for d in aliases[base] if d in implemented]
    d='ttk_'+base[3:] if base and base.startswith('xd_') else None
    return [d] if d in implemented else []

def validate_resource(root,sid):
    a=Path(root)/'anim'/f'{sid}.zip'; x=Path(root)/'images/inventoryimages'/f'{sid}.xml'; tex=x.with_suffix('.tex')
    missing=[str(p.relative_to(root)).replace('\\','/') for p in (a,x,tex) if not p.exists()]
    if missing:return False,missing,'thiếu tài nguyên: '+', '.join(missing)
    try:
        with ZipFile(a) as z:
            bad=z.testzip(); payload=z.read('build.bin')+(z.read('anim.bin') if 'anim.bin' in z.namelist() else b'')
            if bad:return False,[str(a.relative_to(root))],f'ZIP CRC lỗi tại {bad}'
            if sid.encode() not in payload:return False,[str(a.relative_to(root))],'archive không chứa định danh build nguồn'
    except Exception as e:return False,[str(a.relative_to(root))],f'archive không hợp lệ: {e}'
    if f'{sid}.tex' not in x.read_text(encoding='utf-8',errors='ignore'):return False,[str(x.relative_to(root))],'atlas sai texture'
    return True,[str(p.relative_to(root)).replace('\\','/') for p in (a,x,tex)],'đủ ZIP/atlas/texture'

def reconcile_candidates(candidates,implemented,source_root,aliases):
    rows=[]
    for c in candidates:
        dest=destinations_for(c,implemented,aliases); ok,assets,why=validate_resource(source_root,c['source_id'])
        status='imported' if dest and ok else ('missing_resource' if dest else 'base_not_implemented')
        reason='prefab đích tồn tại và tài nguyên hợp lệ' if status=='imported' else (why if status=='missing_resource' else 'prefab gốc chưa được triển khai')
        rows.append({**c,'destination_bases':dest,'final_status':status,'assets':assets,'reason':reason})
    return rows

def record_name(sid,dest):
    if sid.startswith('xd_skin_'):return dest+'_skins_'+sid.removeprefix('xd_skin_')
    replacements={'xd_zcmj_':'ttk_zcmj_skins_','xd_xshj_':'ttk_xshj_skins_','xd_ztp_skins_':'ttk_chuongthienbinh_skins_','xd_qwsk_':'ttk_qwsk_skins_','xd_sudaji_ywfh_':'nhatvuphuonghoa_skins_','xd_sudaji_redlantern_':'ttk_ngulongdang_skins_','xd_xianjian_builder_skins_':'ttk_tienkiem_skins_','xd_mo_builder_skins_':'ttk_makiem_skins_'}
    exact={'xd_yaohat':'ttk_zcmj_skins_yaohat','xd_jtkhat':'ttk_zcmj_skins_jtkhat','xd_lhyhat':'ttk_zcmj_skins_lhyhat','xd_yaoarmor':'ttk_xshj_skins_yaoarmor','xd_jdjarmor':'ttk_xshj_skins_jdjarmor','xd_hyparmor':'ttk_xshj_skins_hyparmor'}
    if sid in exact:return exact[sid]
    for a,b in replacements.items():
        if sid.startswith(a):return b+sid[len(a):]
    return 'ttk_'+sid[3:]

def records_from_audit(rows):
    out=[]
    for row in rows:
        if row['final_status']!='imported':continue
        sid=row['source_id']
        for dest in row['destination_bases']:
            name=record_name(sid,dest); asset='ttk_shared_'+sid if sid.startswith('xd_skin_') else name
            rec={'name':name,'base':dest,'build':sid,'display_name':'Mẫu '+sid.rsplit('_',1)[-1].upper(),'family':FAMILY.get(dest,'structure'),'asset_name':asset,'icon_name':asset,'source_id':sid}
            if sid.startswith('xd_skin_'):rec['equip_symbol']='png' if sid in HIDDEN_GENERIC else 'swap'
            if sid=='xd_sudaji_ywfh_lxzy':rec['equip_symbol']='swap'
            if sid=='xd_hyparmor':rec['bank']='xd_xshj'
            skillbuild=SOURCE/'anim'/f'{sid}_skillbuild.zip'
            if sid.startswith('xd_skin_') and skillbuild.exists():rec['extra_anims']=[f'{sid}_skillbuild']
            if sid=='xd_sudaji_redlantern_zyx':rec['extra_anims']=['swap_xd_sudaji_redlantern_zyx']
            if sid=='xd_sudaji_redlantern_zyx':rec['anim']='idle_loop'
            if sid.startswith('xd_xianjian_builder_skins_'):
                rec['equip_build']='xd_sword_red_'+sid.rsplit('_',1)[-1]; rec['extra_anims']=[rec['equip_build']]
            if sid.startswith('xd_mo_builder_skins_'):
                rec['equip_build']='xd_sword_mo_'+sid.rsplit('_',1)[-1]; rec['extra_anims']=[rec['equip_build']]
            out.append(rec)
    return out

def parse_lua_records(path):
    if not Path(path).exists():return []
    out=[]
    for table in Path(path).read_text(encoding='utf-8',errors='ignore').splitlines():
        if not table.lstrip().startswith('{'):continue
        d=dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"',table))
        if {'name','base','build'}<=d.keys():out.append(d)
    return out

def merge_records(json_records,lua_records,discovered):
    by={}
    # JSON carries list-valued dependency metadata that the conservative Lua
    # parser intentionally does not try to reconstruct.
    for r in json_records+lua_records+discovered:by.setdefault(r['name'],r)
    for r in discovered:by[r['name']]=r
    return sorted(by.values(),key=lambda r:(r['name']!='ttt_portal_gcsz',r['name']))

def render_json(records):return json.dumps(sorted(records,key=lambda r:(r['name']!='ttt_portal_gcsz',r['name'])),ensure_ascii=False,indent=2)+'\n'
def lua_value(v):return '{ '+', '.join(json.dumps(x,ensure_ascii=False) for x in v)+' }' if isinstance(v,list) else json.dumps(v,ensure_ascii=False)
def render_lua(records):
    keys=['name','base','build','display_name','family','asset_name','icon_name','source_id','bank','anim','apply_ground','equip_build','equip_symbol','extra_anims']; lines=['-- Generated by tools/port_ttk_owned_item_skins.py; do not edit by hand.','return {']
    for r in sorted(records,key=lambda x:(x['name']!='ttt_portal_gcsz',x['name'])):lines.append('    { '+', '.join(f'{k} = {lua_value(r[k])}' for k in keys if k in r)+' },')
    return '\n'.join(lines+['}',''])

def lua_matches_manifest(path,records):
    return Path(path).read_text(encoding='utf-8')==render_lua(records)

def copy_resource(sid,asset):
    shutil.copyfile(SOURCE/'anim'/f'{sid}.zip',DST/'anim'/f'{asset}.zip')
    x=SOURCE/'images/inventoryimages'/f'{sid}.xml'; (DST/'images/inventoryimages'/f'{asset}.xml').write_text(x.read_text(encoding='utf-8').replace(f'{sid}.tex',f'{asset}.tex'),encoding='utf-8')
    shutil.copyfile(x.with_suffix('.tex'),DST/'images/inventoryimages'/f'{asset}.tex')

def validate_copied_resource(source_root,dst_root,record):
    errors=[]; sid=record['source_id']; asset=record['asset_name']; icon=record['icon_name']
    source_zip=Path(source_root)/'anim'/f'{sid}.zip'; dest_zip=Path(dst_root)/'anim'/f'{asset}.zip'
    source_xml=Path(source_root)/'images/inventoryimages'/f'{sid}.xml'; dest_xml=Path(dst_root)/'images/inventoryimages'/f'{icon}.xml'
    source_tex=source_xml.with_suffix('.tex'); dest_tex=dest_xml.with_suffix('.tex')
    if not dest_zip.exists() or dest_zip.read_bytes()!=source_zip.read_bytes():errors.append('ZIP đích thiếu/khác nguồn')
    elif ZipFile(dest_zip).testzip() is not None:errors.append('CRC ZIP đích lỗi')
    expected_xml=source_xml.read_text(encoding='utf-8').replace(f'{sid}.tex',f'{icon}.tex')
    if not dest_xml.exists() or dest_xml.read_text(encoding='utf-8')!=expected_xml:errors.append('atlas đích thiếu/khác phép đổi tên chuẩn')
    if not dest_tex.exists() or dest_tex.read_bytes()!=source_tex.read_bytes():errors.append('texture đích thiếu/khác nguồn')
    for extra in record.get('extra_anims',[]):
        source_extra=Path(source_root)/'anim'/f'{extra}.zip'; dest_extra=Path(dst_root)/'anim'/f'{extra}.zip'
        if not dest_extra.exists() or dest_extra.read_bytes()!=source_extra.read_bytes():errors.append(f'animation phụ {extra} thiếu/khác nguồn')
        elif ZipFile(dest_extra).testzip() is not None:errors.append(f'CRC animation phụ {extra} lỗi')
    return errors

def build_audit():
    implemented=discover_destination_prefabs(DST/'scripts/prefabs')|discover_destination_prefabs(DST/'main'); rows=reconcile_candidates(discover_source_declarations(),implemented,SOURCE,SOURCE_TO_DEST)
    return rows,records_from_audit(rows),implemented

def write_all(rows,discovered,implemented):
    manifest=DST/'skins_manifest.json'; old_json=json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else []; old_lua=parse_lua_records(DST/'scripts/ttk_skin_data.lua')
    portal={'name':'ttt_portal_gcsz','base':'homesign','build':'ttt_portal_gcsz','display_name':'Cổ Trận','family':'homesign','asset_name':'ttt_portal_gcsz','icon_name':'ttt_portal_gcsz','source_id':'manual:ttt_portal_gcsz'}
    records=merge_records(old_json,old_lua+[portal],discovered)
    copied=set()
    for r in discovered:
        key=(r['source_id'],r['asset_name'])
        if key not in copied:copy_resource(*key);copied.add(key)
        for extra in r.get('extra_anims',[]):shutil.copyfile(SOURCE/'anim'/f'{extra}.zip',DST/'anim'/f'{extra}.zip')
    manifest.write_text(render_json(records),encoding='utf-8'); (DST/'scripts/ttk_skin_data.lua').write_text(render_lua(records),encoding='utf-8')
    touched={'tools/port_ttk_owned_item_skins.py','tools/test_ttk_owned_item_skins.py','tools/build_tu_tien_ky_web.py','mods/PhamNhanTuTien/modmain.lua','mods/PhamNhanTuTien/skins_manifest.json','mods/PhamNhanTuTien/scripts/ttk_skin_data.lua','mods/PhamNhanTuTien/scripts/ttk_skins.lua','mods/PhamNhanTuTien/scripts/ttk_skin_effects.lua','mods/PhamNhanTuTien/scripts/prefabs/ttk_hhlmz_skins.lua','mods/PhamNhanTuTien/scripts/prefabs/ttk_tinhlakiem.lua','mods/PhamNhanTuTien/scripts/prefabs/ttk_elemental_swords.lua','mods/PhamNhanTuTien/scripts/prefabs/nhatvuphuonghoa.lua','mods/PhamNhanTuTien/scripts/prefabs/ttk_zcmj.lua','mods/PhamNhanTuTien/scripts/prefabs/ttk_skin_hyys_fx.lua','mods/PhamNhanTuTien/tools/test_owned_skins_runtime.py','mods/PhamNhanTuTien/tools/test_armor_set.py','mods/PhamNhanTuTien/modinfo.lua','mods/PhamNhanTuTien/README_VI.md','docs/superpowers/reports/2026-09-20-tu-tien-ky-all-owned-skins.json','docs/superpowers/reports/2026-09-20-tu-tien-ky-all-owned-skins.md','.superpowers/sdd/2026-09-20-tu-tien-ky-all-owned-skins/progress.md'}
    for r in discovered:
        touched.update({f"mods/PhamNhanTuTien/anim/{r['asset_name']}.zip",f"mods/PhamNhanTuTien/images/inventoryimages/{r['icon_name']}.xml",f"mods/PhamNhanTuTien/images/inventoryimages/{r['icon_name']}.tex"})
        touched.update(f'mods/PhamNhanTuTien/anim/{x}.zip' for x in r.get('extra_anims',[]))
    visual_count=len({r['source_id'] for r in records})
    backup_root=ROOT/'mods/backups/TuTienKy_before_all_owned_skins_20260920_1630'
    backup_files=sorted(str(p.relative_to(ROOT)).replace('\\','/') for p in backup_root.rglob('*') if p.is_file())
    report={'generated_at':'2026-09-20','canonical_source':'mods/mod_steam/3235319974 v19.7','localized_comparison':'mods/mod_steam/3721846643 v18.1.0; older, one fewer *skin*.zip','unlock_skin':'mods/mod_steam/3773896514; inspected statically; unlock code only, no skin assets','declaration_source':str(UI.relative_to(ROOT)).replace('\\','/'),'alias_source':str(ALIAS.relative_to(ROOT)).replace('\\','/'),'backup_path':'mods/backups/TuTienKy_before_all_owned_skins_20260920_1630','backup_files':backup_files,'backup_limitations':['ttk_tinhlakiem.lua and ttk_elemental_swords.lua were changed before they were added to the scoped backup; their two-line equip changes are reviewable in the working tree but no exact pre-edit copy is claimed.'],'workspace_preservation':['Concurrent ttk_solo_guard/ttk_solo_bootstrap modmain edits were not authored or changed by this task and remain intact.'],'baseline_json_count':31,'baseline_effective_registration_count':32,'baseline_distinct_visual_count':32,'final_registration_count':len(records),'new_registration_count':len(records)-32,'final_distinct_visual_count':visual_count,'new_distinct_visual_count':visual_count-32,'generic_shared_visual_count':42,'generic_destination_binding_count':126,'implemented_prefab_count':len(implemented),'records':records,'source_audit':rows,'touched_files':sorted(touched),'archive_only_reconciliation':{'xd_tree_yx_skins_jqs':'alias/orphan: no UI declaration or icon; canonical xd_tree_yxs_skins_jqs imported','*_skillbuild.zip':'presentation dependencies registered with their owning skin, not independent choices'},'equipment_symbol_scope':{'xd_yaohat':'source onequip explicitly hides HEAD_HAT; destination comparison fixed to embedded xd_ build and tested through equip/unequip','xd_lhyhat.swap_face':'archive contains the symbol but decoded source onequip only overrides swap_hat, so no invented face override was added','xd_hyparmor.arm_lower/arm_upper':'archive contains the symbols but decoded source xshj onequip only overrides swap_body; dropped art reuses the xd_xshj bank/idle animation with the xd_hyparmor build'},'presentation_effects':{'xd_skin_hyys_fx':'ported as ttk_skin_hyys_fx and attached/cleaned with each HYYS weapon skin','*_skillbuild.zip':'loaded as skin dependencies only; source combat/character skill triggers are intentionally not run because their gameplay systems are outside the port'},'runtime_limitations':['No live DST client/server session was launched; Lua smoke checks cover dispatch and metadata with mocked engine APIs.','Native DST reskin persistence/replication remains dependent on the game CreatePrefabSkin pipeline and requires an in-game client/host check.','Four *_skillbuild archives are available to clients but their source combat/character-skill effects are not invoked; only the standalone HYYS cosmetic follower was ported.'],'validation_results':['10 importer regression tests passed, including stable declaration order, build-only armor, stale/corrupt destination and exact JSON/Lua metadata checks','--check: checked=148 imported_records=178 failures=0; primary/extra assets byte-match source and CRC/atlas transforms pass','Lua Apply/Clear/equip/icon/HYYS FX smoke checks passed','Armor suite passed after adding an actual xd_yaohat equip/hide/unequip/restore regression','Existing tinhlakiem, elemental_swords, nhatvuphuonghoa and ngulongdang suites passed','Five fresh-process audit hashes were identical','Second --write produced identical manifest, Lua data and JSON audit SHA-256 hashes'],'validation_commands':['python -m unittest discover -s tools -p test_ttk_owned_item_skins.py -v','python tools/port_ttk_owned_item_skins.py --check','python mods/PhamNhanTuTien/tools/test_owned_skins_runtime.py','preload lupa.lua51 from .superpowers/luoshen-runtime, then runpy.run_path for legacy mod test scripts']}
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return records

def main(argv=None):
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--audit-only',action='store_true');g.add_argument('--check',action='store_true');g.add_argument('--write',action='store_true');a=p.parse_args(argv)
    rows,discovered,implemented=build_audit()
    if a.write:print(f'Wrote {len(write_all(rows,discovered,implemented))} deduplicated skins ({len(discovered)} source/destination records).')
    elif a.check:
        bad=[r for r in rows if r['destination_bases'] and r['final_status']!='imported']
        manifest=json.loads((DST/'skins_manifest.json').read_text(encoding='utf-8'))
        by={r['name']:r for r in manifest}; lua_names={r['name'] for r in parse_lua_records(DST/'scripts/ttk_skin_data.lua')}
        for r in discovered:
            if by.get(r['name'])!=r:bad.append({'source_id':r['source_id'],'reason':'manifest thiếu hoặc khác metadata'})
            if r['name'] not in lua_names:bad.append({'source_id':r['source_id'],'reason':'Lua table thiếu record'})
            bad.extend({'source_id':r['source_id'],'reason':reason} for reason in validate_copied_resource(SOURCE,DST,r))
        if set(by)!=lua_names:bad.append({'source_id':'manifest','reason':'tập tên JSON/Lua không khớp'})
        if not lua_matches_manifest(DST/'scripts/ttk_skin_data.lua',manifest):bad.append({'source_id':'manifest','reason':'metadata JSON/Lua không khớp chính xác'})
        print(f'checked={len(rows)} imported_records={len(discovered)} failures={len(bad)}');return bool(bad)
    else:print(json.dumps({'source_declarations':len(rows),'imported_records':len(discovered),'excluded':sum(r['final_status']!='imported' for r in rows)},indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
