"""Reproducible static port of Tu Tien 19.7's nine boss combat graphs.

The encrypted source loader is never executed. Cultivation/world progression and
NPC shops are deliberately not imported; original combat states are retained.
"""
import json
import re
import shutil
from pathlib import Path
import port_ttk_buildings as base

ROOT, SOURCE, DEST = base.ROOT, base.SOURCE, base.DEST
base.source.MAPPING[3] = ord('%')
MAINS = 'baihu jfsn qlch qxdx futu spiderqueen ziyunboss stalke_fuben deerclops_ziyun'.split()
EXTRA = 'baihufx fxs baihu_buff jfsn_fire jfsnmeteor sand_spike shadowmeteor qlch_cloud gongdeshadow ht sword swordfx xjs_curve_fx stmeteor rock_basalt spider spiderqueen_cloud stalke_ziyun shadowmonster aoeent ziyunswordfx vortex_fx mutated_fx'.split()
RENAMES = {'xd_'+n: 'ttk_'+n for n in MAINS}
RENAMES['xd_deerclops_ziyun'] = 'ttk_boss_deerclops_ziyun_aux'
RENAMES.update({'xd_npxsz':'ttk_npxsz','xd_spider_leg':'ttk_spider_leg'})
RENAMES.update({'xd_lc_'+n+'_seed':'ttk_lc_'+n+'_seed' for n in 'hsc dms qfx cyh lmg yhh'.split()})
PRIVATE_FX='bianhua_fx bianhua_fx_big bianhua_fx_explo db_bianhua_fx shadow_merm_spawn_fx splash_yellow statue_transition_2_big'.split()
COLLECTIBLES = set()

def read(p):
    raw = (SOURCE/p).read_bytes()
    try: t = raw.decode('utf8')
    except UnicodeDecodeError:
        t = ''.join(chr(base.source.MAPPING[c]) if c in base.source.MAPPING else '<%02X>'%c for c in raw[::-1])
    t = re.sub(r'--\[\[.*?\]\]', '', t, flags=re.S)
    t = re.sub(r'--[^\r\n]*', '', t)
    # Remaining unmapped bytes are Chinese localization only. Preserve distinct
    # keys (hex spelling), rather than collapsing different source strings.
    t = re.sub(r'"[^"\r\n]*<[A-F0-9]{2}>[^"\r\n]*"', lambda m: '"source_'+''.join(re.findall(r'<([A-F0-9]{2})>',m[0]))+'"', t)
    assert not re.search(r'<[A-F0-9]{2}>', t), p
    t='\n'.join(l.rstrip() for l in t.splitlines() if l.strip())+'\n'
    return prune(str(p).replace('\\','/'),t)

def call_at(t,start):
    """Extract one balanced Lua function call, ignoring quoted parentheses."""
    begin=t.index('(',start); depth=0;quote=None;escape=False
    for i in range(begin,len(t)):
        c=t[i]
        if quote:
            if escape:escape=False
            elif c=='\\':escape=True
            elif c==quote:quote=None
        elif c in '\"\'':quote=c
        elif c=='(':depth+=1
        elif c==')':
            depth-=1
            if depth==0:return t[start:i+1]
    raise ValueError('unbalanced call')

def prune(p,t):
    n=Path(p).stem
    if n=='xd_buffs':
        names=['xd_ignoreplanarentity','xd_slow_buff','xd_spiderqueen_buff1','xd_spiderqueen_buff2','xd_spiderqueen_buff3']
        calls=[call_at(t,t.index('makebuffs("'+s+'"')) for s in names]
        return t[:t.index('local function electric_attach')]+ 'return '+',\n'.join(calls)+'\n'
    if n=='xd_cl':
        t=t[:t.index('local function setanim')]+t[t.index('local function speed_remove_buff'):]
        t=t.replace('return  Prefab("xd_cl", fn, assets, prefabs),','return ')
    if n=='xd_hyf':
        # Combat only uses the source moonbeam effects, never the magic weapon.
        a=t.index('local function spinfn')
        t=t[:t.index('local function')]+t[a:]
        t=t.replace('return  Prefab("xd_hyf", fn, assets, prefabs),','return ')
        t=t.replace('SetOnThrownFn(OnThrown)','SetOnThrownFn(function(projectile, owner) projectile.owner = owner end)',1)
    if n=='xd_ftj':
        t=t[:t.index('local function UseFbAnim')]+t[t.index('local function explodefn'):]
        t=t.replace('return Prefab("xd_ftj", fn, assets),','return ')
    if n=='xd_sudaji_xyj':
        t=t[:t.index('local function setanim')]+t[t.index('local function fxfn'):]
        t=t.replace('return  Prefab("xd_sudaji_xyj", fn, assets, prefabs),','return ')
    if n=='xd_sudaji_fx':
        tail=t[t.rindex('return Prefab'):]
        tail=re.sub(r',?\s*Prefab\("xd_sudaji_puppet"[^\n]*','',tail).rstrip().rstrip(',')+'\n'
        t=t[:t.index('local function CopySkinsFromPlayer')]+tail
    return t

def ns_name(n):
    if n.endswith('.lua'): return ns_name(n[:-4])+'.lua'
    if n.startswith('SGxd_'): return 'SG'+ns_name(n[2:])
    return RENAMES.get(n, 'ttk_boss_'+n[3:] if n.startswith('xd_') else n)

def namespace(t):
    # Art bank/build/animation names are embedded inside the original archives.
    keep = []
    def protect(m):
        keep.append(m[0]); return '__BOSS_ART_%d__' % (len(keep)-1)
    t = re.sub(r'[^\n]*(?:AnimState:|SoundEmitter:|Asset\(|resolvefilepath\(|build\s*=|bank\s*=|anim\s*=|sound\s*=)[^\n]*', protect, t)
    t = re.sub(r'\b(?:SG)?xd_\w+', lambda m: ('SG'+ns_name(m[0][2:])) if m[0].startswith('SG') else ns_name(m[0]), t)
    t = re.sub(r'\b(?:'+'|'.join(sorted(PRIVATE_FX,key=len,reverse=True))+r')\b',lambda m:'ttk_boss_'+m[0],t)
    for i,v in enumerate(keep): t=t.replace('__BOSS_ART_%d__'%i,v)
    return t

def prepare(path,t):
    name=Path(path).stem
    # Unique armor bosses award one crafting material each.
    if name=='xd_futu':
        t=re.sub(r'^\s*"xd_mgqg",[^\n]*\n', '', t, count=1, flags=re.M)
    if name=='xd_ziyunboss':
        t=re.sub(r"^\s*\{'xd_zcmy',[^\n]*\n", '', t, count=1, flags=re.M)
    # These three old collectibles are replaced by the registry's one edible
    # core + one summon soul. Never add a second pair to the source loot table.
    retired = {'xd_baihu': 'xd_baihu_skin', 'xd_jfsn': 'xd_fs', 'xd_qlch': 'xd_qlr'}
    if name in retired:
        t = re.sub(r'^\s*\{\s*[\"\x27]' + retired[name] + r'[\"\x27]\s*,[^\n]*\n', '', t, flags=re.M)
    if name=='xd_jcbird':
        # These default crow animations are immediately replaced by the two
        # mutated bird constructors; neither constructor loads the crow bank.
        t=t.replace('inst.AnimState:SetBuild("crow_build")','')
        t=t.replace('inst.AnimState:SetBank("crow")','')
        t=t.replace('inst.AnimState:PlayAnimation("idle", true)','',1)
        t=t.replace('inst.AnimState:SetBank("mutated_crow")','inst.AnimState:SetBank("mutated_crow")\n    inst.AnimState:PlayAnimation("idle", true)')
    if name=='xd_gongdeshadow':
        # The original mod globally preloaded this weapon. Our standalone
        # shadow prefab must declare its own symbol build dependency.
        t=t.replace('Asset("ANIM", "anim/lavaarena_shadow_lunge.zip"),',
                    'Asset("ANIM", "anim/lavaarena_shadow_lunge.zip"),\n    Asset("ANIM", "anim/xd_tssyq.zip"),')
    if name in ['xd_'+n for n in MAINS]:
        t=re.sub(r'inst\.components\.health\.OnSave\s*=\s*(?:function\([^\n]*?\)\s*end|empty)',
                 '-- Normal health persistence: registry encounters survive save/load.',t)
    if name=='xd_baihu':
        t=re.sub(r'"source_[A-F0-9]+"','"Uy thế của Bạch Hổ đang trỗi dậy."',t)
    if name=='xd_qxdx':
        t=re.sub(r"('xd_back_xh'\s*,\s*)0\.1\b", r'\g<1>1.0', t)
        a=t.index('local seed_list ='); b=t.index('local function OnEntityWake',a)
        t=t[:a]+'''local fixed_seed_loot = {
    "xd_zcyseed", "xd_zcyseed",
    "xd_lc_hsc_seed", "xd_lc_dms_seed", "xd_lc_qfx_seed",
    "xd_lc_cyh_seed", "xd_lc_lmg_seed", "xd_lc_yhh_seed",
}
local function OnDeath(inst)
    if inst._ttk_fixed_seeds_dropped then return end
    inst._ttk_fixed_seeds_dropped = true
    for _, prefab in ipairs(fixed_seed_loot) do
        for _ = 1, (prefab == "xd_zcyseed" and 1 or 3) do
            inst.components.lootdropper:SpawnLootPrefab(prefab)
        end
    end
end
'''+t[b:]
        t=t.replace('"source_1786ED17DAE32BFD1C"','"Hình thái: Thanh Tụ"').replace('"source_2B579DF1F8382BFD1C"','"Hình thái: Đan Tiên"')
        # Shop and donation NPC is outside the combat port. Its art is retained.
        a=t.index('local function onuse('); b=t.index('local TEXTURE',a)
        t=t[:a]+t[b:]
        t=re.sub(r'\s*Prefab\("xd_qxdx_npc"[^\n]+\n','\n',t)
        t=re.sub(r'\s*Prefab\("xd_qxdx_spawner"[^\n]+','',t).rstrip().rstrip(',')+'\n'
    # Registry replaces all source map spawners; leave no callable respawners.
    t=re.sub(r'^[ \t]*Prefab\("xd_\w+_spawner",\s*spawnerfn[^\n]*\n', '', t, flags=re.M)
    t=t.rstrip().rstrip(',')+'\n'
    if name=='xd_deerclops_ziyun':
        t=t.replace('return owner ~= nil and FindEntity(inst, 12,','return FindEntity(inst, 12,').replace('return owner:IsValid() and XD_CanAttackTrget(inst,guy)','return (owner == nil or owner:IsValid()) and XD_CanAttackTrget(inst,guy)')
    if name=='xd_ziyunboss':
        t=t.replace('inst.components.health.OnSave = function(...) end','-- Use normal health persistence for the standalone encounter.')
        t=t.replace('inst:AddComponent("leader")','inst:AddComponent("leader")\n    -- Sword/phase helpers are transient and rebuilt from saved encounter phase.\n    inst.components.leader.OnSave = function() return {} end')
    if name=='SGxd_ziyunboss':
        t=t.replace('inst.components.health:SetCurrentHealth(1)','inst.components.health:SetCurrentHealth(1)\n            inst._ttk_boss_phase_transition = nil')
    if name=='SGxd_swhs':
        # This shared graph also has an unused Wukong cultivation state. HT's
        # brain never dispatches it, and its source-only global is not imported.
        a=t.index('    State{\n        name = "xd_wukong_skill"')
        b=t.index('    State{',a+12)
        t=t[:a]+t[b:]
    if name=='SGxd_qxdx':
        a=t.index('            inst.components.xd_sword_controller:DeSummon()',t.index('name = "goaway"'))
        b=t.index('            inst:Remove()',a)+len('            inst:Remove()')
        t=t[:a]+'''            -- Encounter reset must retain the registry's original entity.
            inst:ChangeMode(1)
            inst.components.health:SetPercent(1)
            inst.components.combat:SetTarget(nil)
            inst.sg:GoToState("idle")'''+t[b:]
    # All boss-specific support entities are classified during creation, before
    # AddPrefabPostInit runs. Only the nine explicit public constructors opt out.
    t=namespace(t)
    if name=='xd_gongdeshadow':
        # This list contains animation builds, not prefab identifiers.
        t=re.sub(r'(local mychars = \{[^\n]+)',lambda m:m[0].replace('ttk_boss_','xd_'),t)
    # Factory parameters sometimes double as prefab ids and embedded art names.
    t=re.sub(r'(AnimState:(?:SetBank|SetBuild|AddOverrideBuild))\(([^()\n]+)\)',r'\1(Boss.Art(\2))',t)
    t=re.sub(r'Asset\("ANIM",\s*([^\n]+?)\)',r'Asset("ANIM", Boss.ArtPath(\1))',t)
    if name=='xd_deerclops_ziyun':
        t=t.rstrip()+',\nPrefab("ttk_deerclops_ziyun", mutatedfn, mutated_assets, mutated_prefabs)\n'
    if path.startswith('scripts/brains/'):
        t='require "behaviours/follow"\nrequire "behaviours/leash"\nrequire "behaviours/doaction"\nrequire "behaviours/runaway"\nrequire "behaviours/chaseandattack"\nrequire "behaviours/wander"\nrequire "behaviours/faceentity"\n'+t
    globals_=sorted(set(re.findall(r'(?<![.:\w])(?:XD|Xd)_\w+\s*\(',t)))
    globals_=[re.sub(r'\s*\($','',n) for n in globals_]
    header='-- Statically ported Tu Tien 19.7 combat; see tools/port_phamnhan_boss_combat.py.\nlocal Boss = require("ttk_boss_util")\nlocal TUNING = Boss.TUNING\nlocal STRINGS = Boss.STRINGS\n'
    if path.startswith('scripts/prefabs/'):header+='local Prefab = Boss.Prefab\n'
    header+=''.join('local %s = Boss.%s\n'%(n,n) for n in globals_)
    return header+t

def write(p,t):
    p=DEST/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='utf8',newline='\n')

def discover():
    source={}
    for p in (SOURCE/'scripts').rglob('*.lua'):
        if p.parent.name not in ['prefabs','brains','stategraphs','components']:continue
        try:source[p.relative_to(SOURCE).as_posix()]=read(p.relative_to(SOURCE))
        except AssertionError:pass
    providers={}
    for p,t in source.items():
        if not p.startswith('scripts/prefabs/'):continue
        for n in re.findall(r'\b(?:Prefab|swordfx|[Mm]ake\w*|name\s*=)\s*\(?\s*["\'](xd_\w+)["\']',t): providers[n]=p
    for p,t in source.items():
        if p.startswith('scripts/prefabs/'):providers[Path(p).stem]=p
    for n in re.findall(r'name\s*=\s*["\'](xd_\w+)["\']',source['scripts/prefabs/xd_fxs.lua']): providers[n]='scripts/prefabs/xd_fxs.lua'
    queue=['scripts/prefabs/xd_'+n+'.lua' for n in MAINS+EXTRA]
    selected={}; missing=set()
    while queue:
        p=queue.pop()
        if p in selected:continue
        if p not in source:missing.add(p);continue
        t=source[p]
        # Remove optional NPC subtree before discovering dependencies.
        if Path(p).stem=='xd_qxdx':
            a=t.index('local function onuse(');b=t.index('local TEXTURE',a);t=t[:a]+t[b:]
        selected[p]=t
        for n in re.findall(r'require\s*\(?["\']([^"\']+)',t):
            dep='scripts/'+n+'.lua'
            if dep in source:queue.append(dep)
        for kind,n in re.findall(r':(SetStateGraph|AddComponent)\(["\']((?:SG)?xd_\w+)',t):queue.append('scripts/'+('stategraphs' if kind=='SetStateGraph' else 'components')+'/'+n+'.lua')
        for n in re.findall(r'["\'](SGxd_\w+)["\']',t):queue.append('scripts/stategraphs/'+n+'.lua')
        deps=re.findall(r'(?:SpawnPrefab|SpawnAt)\(\s*["\'](xd_\w+)["\']',t)
        deps+=re.findall(r'AddDebuff\([^\n]*?["\'](xd_\w+)["\']\s*[,)]',t)
        deps+=re.findall(r'childname\s*=\s*["\'](xd_\w+)',t)
        if Path(p).stem=='xd_sword_controller':deps+=['xd_sword_red']
        for n in deps:
            if n=='xd_sword_':continue # Expanded red/green/blue by sword controller.
            if n in providers:
                queue.append(providers[n])
            else:missing.add(n)
    return selected,missing

def main():
    selected,missing=discover()
    print('Selected',len(selected),'files; unresolved dynamic/library effects:',sorted(missing))
    outputs=[];assets=set()
    for p,t in sorted(selected.items()):
        output='/'.join(ns_name(s) for s in p.split('/'))
        output=output.replace('SGxd_','SGttk_boss_')
        result=prepare(p,read(p));write(output,result);outputs.append(output)
        # Explicit paths plus all source art literals, including dynamic FX builds.
        for a in re.findall(r'["\']((?:anim|images|fx|sound)/[^"\']+\.(?:zip|tex|xml|fsb|fev))["\']',t):
            if (SOURCE/a).exists():assets.add(a)
        for n in re.findall(r'["\'](xd\w+)["\']',t):
            if (SOURCE/('anim/'+n+'.zip')).exists():assets.add('anim/'+n+'.zip')
        for bank in re.findall(r'["\'](xd_\w+)/xd_\w+/',t):
            for ext in ['fsb','fev']:
                if (SOURCE/('sound/'+bank+'.'+ext)).exists():assets.add('sound/'+bank+'.'+ext)
    # Ziyun's resurrect/cast states share the original player staff graph.
    # These are animation-bank dependencies, not prefab dependencies.
    assets.add('anim/player_xd_staff.zip')
    assets.update({'images/xd_back_xh_ui.xml', 'images/xd_back_xh_ui.tex'})
    for a in list(assets):
        if a.endswith('.xml'):
            tex=str(Path(a).with_suffix('.tex')).replace('\\','/')
            if (SOURCE/tex).exists():assets.add(tex)
    # Source rewards remain collectibles unless an equivalent item is integrated.
    reward_rows=[]
    names={'back_xh':'Ba Lô Tiên Hà','zcmy':'Tử Thần Ma Ngọc','mgqg':'Ma Cốt','zcyseed':'Hạt Tử Chi'}
    for n,label in names.items():
        source='xd_'+n
        build=source if (SOURCE/('anim/'+source+'.zip')).exists() else ('feather_robin' if n=='fs' else 'meat')
        animation='raw' if build=='meat' else 'idle'
        reward_rows.append('{"ttk_boss_%s","%s","%s","%s","%s"}'%(n,source,build,animation,label))
        if (SOURCE/('anim/'+build+'.zip')).exists():assets.add('anim/'+build+'.zip')
        for ext in ['xml','tex']: assets.add('images/inventoryimages/'+source+'.'+ext)
    for n in 'cyfxd lmsqd dmhsd qxdhd yfsxd pshsd qjqsd xynyd hsphd xttyd'.split():
        source='xd_dy_'+n+'_5'
        for ext in ['xml','tex']:assets.add('images/inventoryimages/'+source+'.'+ext)
    assets.add('anim/xd_danyao_new.zip')
    write('scripts/ttk_boss_collectible_defs.lua','-- Preserved source drops; intentionally no cultivation or equipment powers.\nreturn {\n'+',\n'.join(reward_rows)+'\n}\n')
    outputs.append('scripts/ttk_boss_collectible_defs.lua')
    for a in sorted(assets):
        out=DEST/a;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(SOURCE/a,out)
    write('scripts/main/ttk_boss_moster_shengti_set.lua',namespace(read('scripts/main/xd_moster_shengti_set.lua')))
    outputs.append('scripts/main/ttk_boss_moster_shengti_set.lua')
    manifest={'lua':outputs,'assets':sorted(assets),'source':'3235319974 / Tu Tien 19.7','unresolved':sorted(missing),'dynamic_prefabs':['ttk_boss_sword_red','ttk_boss_sword_green','ttk_boss_sword_blue']}
    write('scripts/ttk_boss_combat_manifest.json',json.dumps(manifest,indent=2))
    prefabs=[Path(p).stem for p in outputs if '/prefabs/' in p]+['ttk_boss_collectibles']
    preload=''.join('table.insert(Assets, Asset("%s", "%s"))\n'%
                    ('ANIM' if a.endswith('.zip') else 'SOUNDPACKAGE' if a.endswith('.fev') else 'SOUND',a)
                    for a in sorted(assets) if a.endswith(('.zip','.fev','.fsb')))
    write('main/ttk_boss_combat.lua','-- Source combat registration; imported before boss lifecycle hooks.\n'+
          '-- Shared source effects previously relied on global animation/sound assets.\n'+preload+
          'for _, name in ipairs({\n'+''.join('    "%s",\n'%n for n in prefabs)+'}) do table.insert(PrefabFiles, name) end\n'+
          'for _, row in ipairs(require("ttk_boss_collectible_defs")) do\n    STRINGS.NAMES[string.upper(row[1])] = row[5]\n    STRINGS.CHARACTERS.GENERIC.DESCRIBE[string.upper(row[1])] = "Chiến lợi phẩm cổ. Chưa có công dụng trong Phàm Nhân."\nend\n')
    print('Wrote',len(outputs),'Lua files and',len(assets),'assets')

if __name__=='__main__':main()
