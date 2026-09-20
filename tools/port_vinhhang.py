from pathlib import Path
import json
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'.superpowers/vinhhang-runtime'))
from lupa.lua51 import LuaRuntime
src=ROOT/'mods/VinhHangThanHoa'
dst=ROOT/'mods/PhamNhanTuTien'
prefix='ttk_vhth_'
def quote(v):
    if isinstance(v, bool): return 'true' if v else 'false'
    return json.dumps(v,ensure_ascii=False)

lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((src/'modinfo.lua').read_text(encoding='utf-8'))
options=lua.globals().configuration_options
names={'general':'Thiết lập chung','firepit':'Bếp Thần Hỏa','endoFirepit':'Bếp Hàn Hỏa',
       'heatStar':'Vĩnh Hằng Thần Hỏa','iceStar':'Vĩnh Hằng Hàn Hỏa'}
props={'recipe':'Công thức','recipeCost':'Công thức chung','efficiency':'Hiệu suất nhiên liệu',
       'maxFuel':'Dung lượng nhiên liệu','startFuel':'Nhiên liệu ban đầu','lightRange':'Phạm vi sáng',
       'structureSize':'Kích thước bếp','sanityBoost':'Hồi tinh thần','dropLoot':'Vật phẩm khi tắt',
       'starsSpawnHounds':'Triệu hồi chó săn khi tắt'}
translations={'No Override':'Theo thiết lập chung','No override':'Theo thiết lập chung',
    'Test':'Thử nghiệm','Cheat':'Rất rẻ','Cheap':'Rẻ','Standard':'Tiêu chuẩn',
    'Expensive':'Đắt','Advanced':'Cao cấp','Nothing':'Không có','Less':'Ít',
    'Normal':'Bình thường','More':'Nhiều','No':'Không','Medium':'Vừa','Full':'Tối đa'}
def label(k):
    if k in names: return names[k]
    for suffix,target in [('EndoFirepit','Bếp Hàn Hỏa'),('FirePit','Bếp Thần Hỏa'),
                          ('Firepit','Bếp Thần Hỏa'),('HeatStar','Thần Hỏa'),('IceStar','Hàn Hỏa')]:
        if k.endswith(suffix): return target+': '+props[k[:-len(suffix)]]
    return 'Thần Hỏa: '+props[k]

lines=['\n-- Cấu hình Vĩnh Hằng Thần Hỏa; giữ giá trị của bản nguồn.','local thanhoa_options = {']
for _,o in options.items():
    lines.append('    {name='+quote(prefix+o.name)+', label='+quote(label(o.name))+', options={')
    for _,v in o.options.items():
        text=v.description
        text=translations.get(text,text)
        assert not re.search('[A-Za-z]{3,}',text) or text in translations.values(), text
        lines.append('        {description='+quote(text)+', data='+quote(v.data)+'},')
    lines.append('    }, default='+quote(o.default)+'},')
lines.extend(['}','for index = 1, #thanhoa_options do',
              '    configuration_options[#configuration_options + 1] = thanhoa_options[index]','end',''])

main=(src/'modmain.lua').read_text(encoding='utf-8')
variables=set(re.findall(r'GLOBAL\.([a-z]\w*)\s*=',main))
def namespace(s):
    for key in sorted(variables,key=len,reverse=True):
        s=re.sub(r'\b'+key+r'\b',prefix+key,s)
    return s

for directory in ['anim','images','minimap','scripts']:
    for path in (src/directory).rglob('*'):
        if not path.is_file(): continue
        target=dst/path.relative_to(src)
        assert not target.exists(), f'Không ghi đè tài nguyên đang có: {target}'
        target.parent.mkdir(parents=True,exist_ok=True)
        if path.suffix=='.lua':
            s=namespace(path.read_text(encoding='utf-8'))
            def speech(m):
                t=m.group(1)
                if 'STOP' in t: vi='Dừng tay! Ta chưa muốn tiêu tan!'
                elif 'HOUND' in t: vi='Hãy tiếp nhiên liệu! Chó săn sẽ bảo vệ ta!'
                elif 'Spirit of' in t: vi='Ta là linh hỏa vĩnh hằng!'
                elif 'beg' in t: vi='Xin đừng để linh hỏa của ta lụi tàn...'
                elif 'More' in t: vi='Thêm nữa! Linh hỏa đang mạnh lên!'
                elif 'weak' in t or 'fading' in t: vi='Linh hỏa đang yếu đi... hãy tiếp nhiên liệu!'
                elif 'COLD' in t or 'coldness' in t: vi='Hàn hỏa của ta đang tỏa sáng!'
                else: vi='Linh hỏa đã bừng tỉnh!'
                return 'talker:Say('+quote(vi)+')'
            s=re.sub(r'talker:Say\(\s*"([^"\n]*)"\s*\)',speech,s)
            target.write_text(s,encoding='utf-8')
        else: shutil.copy2(path,target)

main=re.sub(r'-- [^\n]* dialog\n.*?(?=-- [^\n]* config options)', '', main, flags=re.S)
main=namespace(main)
main=re.sub(r'GetModConfigData\("(.*?)"\)',lambda m:'GetModConfigData('+quote(m[1] if m[1].startswith(prefix) else prefix+m[1])+')',main)
main=main.replace('PrefabFiles = {','local fire_prefabs = {',1).replace('Assets = {','local fire_assets = {',1)
idx=main.index('AddMinimapAtlas(')
main=main[:idx]+'''for _, name in ipairs(fire_prefabs) do table.insert(PrefabFiles, name) end
for _, asset in ipairs(fire_assets) do table.insert(Assets, asset) end

'''+main[idx:]
for alias in ['STRINGS','RECIPETABS','Recipe','Ingredient','TECH']:
    main=main.replace('\n'+alias+' = GLOBAL.', '\nlocal '+alias+' = GLOBAL.')
# The source's cheapest recipe uses a nonexistent vanilla item id.
main=main.replace('Ingredient("stone", 15)','Ingredient("rocks", 15)')
main+='''
-- Tên và lời mô tả hiển thị bằng tiếng Việt.
local fire_names = {
    DELUXE_FIREPIT = {"Bếp Thần Hỏa", "Bếp lửa bền bỉ, không bị máy phóng băng dập tắt."},
    ENDO_FIREPIT = {"Bếp Hàn Hỏa", "Ngọn lửa lạnh giúp xua tan cái nóng."},
    HEAT_STAR = {"Vĩnh Hằng Thần Hỏa", "Linh hỏa tỏa sáng và sưởi ấm một vùng rộng lớn."},
    ICE_STAR = {"Vĩnh Hằng Hàn Hỏa", "Linh hỏa lạnh soi sáng và làm mát xung quanh."},
}
for key, info in pairs(fire_names) do
    STRINGS.NAMES[key] = info[1]
    STRINGS.RECIPE_DESC[key] = info[2]
    for _, character in pairs(STRINGS.CHARACTERS) do
        if character.DESCRIBE then
            character.DESCRIBE[key] = {
                OUT = "Linh hỏa đã tắt. Cần thêm nhiên liệu.",
                EMBERS = "Chỉ còn chút ánh lửa le lói.",
                LOW = "Linh hỏa đang cháy nhẹ.",
                NORMAL = "Linh hỏa tỏa sáng ổn định.",
                HIGH = "Linh hỏa đang bừng sáng!",
            }
        end
    end
end
'''
(dst/'main/ttk_vinhhangthanhoa.lua').write_text(main,encoding='utf-8')
p=dst/'modinfo.lua'; s=p.read_text(encoding='utf-8-sig')
s=s.replace('version = "0.6.3"','version = "0.7.0"',1)
s=s.replace('Truyền Tống Trận;', 'Truyền Tống Trận, Vĩnh Hằng Thần Hỏa;',1)
p.write_text(s+'\n'.join(lines),encoding='utf-8')
p=dst/'modmain.lua'; s=p.read_text(encoding='utf-8-sig')
p.write_text(s+'\n-- Vĩnh Hằng Thần Hỏa luôn được nạp cùng Tu Tiên Ký.\nmodimport("main/ttk_vinhhangthanhoa.lua")\n',encoding='utf-8')
print('Đã tích hợp Vĩnh Hằng Thần Hỏa vào Tu Tiên Ký 0.7.0.')
