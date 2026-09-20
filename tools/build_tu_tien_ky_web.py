"""Publish the curated Tu Tien Ky inventory, recipes and production graph.

Gameplay facts come from the current mods/PhamNhanTuTien implementation, not source descriptions.
Existing catalog entries supply only labels/icons for vanilla references.
"""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.extract.publish_solo_leveling_assets import decode_ktex

MOD = ROOT / 'mods/PhamNhanTuTien'
import re
VERSION = re.search(r'version\s*=\s*"([^"]+)"', (MOD/'modinfo.lua').read_text(encoding='utf-8')).group(1)
source = json.loads((ROOT/'public/data/items.json').read_text(encoding='utf-8'))['items']
original = {v['prefabId']: v for v in source}
original['collapsed_treasurechest'] = dict(
    id='base_game:collapsed_treasurechest', prefabId='collapsed_treasurechest',
    namespace='base_game', category='structure', name='Rương Sập',
    description='Rương giữ phần vật phẩm còn lại khi tháo kho có nhiều chồng đồ.',
    sprite=None, recipe=None,
)
entries = []
by_code = {}
support = {}
evidence = [{'source': 'Phàm Nhân Tu Tiên '+VERSION, 'locator': 'mods/PhamNhanTuTien/README_VI.md'}]

def sprite(code, source_code=None):
    atlas = MOD / f'images/inventoryimages/{code}.xml'
    if code == 'homesign': atlas = MOD/'images/ttt_portal/icon.xml'
    if atlas.exists():
        tree = ET.parse(atlas).getroot()
        texture = tree.find('Texture').get('filename')
        element = tree.find('Elements/Element')
        out = ROOT/f'public/tu-tien-ky/icons/{code}.png'
        out.parent.mkdir(parents=True, exist_ok=True)
        decode_ktex((atlas.parent/texture).read_bytes()).save(out)
        return {'src':f'/tu-tien-ky/icons/{code}.png', 'uv':{k:float(element.get(k)) for k in ['u1','u2','v1','v2']}}
    return original.get(source_code or code, {}).get('sprite')

def add(code, name, category, description, recipe=None, station=None, effects=(), source_code=None):
    value = dict(id='tu_tien_ky:'+code, prefabId=code, namespace='tu_tien', category=category,
                 name=name, englishName=None, description=description, craftingNote=station,
                 sprite=sprite(code,source_code), recipe=None, wiki=None,
                 details={'recipeStatus':'known' if recipe else 'none',
                          'usage':{'status':'known','recipes':[], 'effects':[{'trigger':'Sử dụng','text':s,'evidence':evidence} for s in effects or [description]]},
                          'dropBy':{'status':'none','sources':[]}}, products=[])
    value['_recipe'] = recipe
    entries.append(value);by_code[code]=value
    return value

def ref(code):
    if code in by_code:v=by_code[code]
    else:
        assert code in original, code
        old=original[code]
        assert old['namespace']=='base_game',code
        v={k:old.get(k) for k in ['id','prefabId','namespace','category','name','englishName','description','craftingNote','sprite','recipe','wiki']}
        # Reference-only records open inside the modal; they are not counted as new mod content.
        support[code]=v
    return {k:v[k] for k in ['id','name','sprite']}

def product(parent, child, amount, condition):
    by_code[parent]['products'].append({'item':ref(child),'quantity':amount,'conditions':condition})
    if child in by_code:
        drops=by_code[child]['details']['dropBy'];drops['status']='known'
        drops['sources'].append({'type':'other','source':ref(parent),'quantity':amount,'chance':None,'conditions':condition,'evidence':evidence})

S1='Máy Khoa Học';S2='Máy Luyện Kim';MAGIC='Shadow Manipulator'
add('ttk_hhlmz','Hoàng Hoa Lê Mộc Trác','structure','Bàn 8 ô để cất và trưng bày món ăn, có khả năng hồi độ tươi.', [('livinglog',3),('boards',5),('ttk_lingshi1',10)],S1,
    ['Chỉ nhận món có tag preparedfood. Hệ số bảo quản −0,2 làm món ăn hồi độ tươi.', 'Có mẫu mặc định và hai mẫu HTJC, WFZ. Nâng cấp một lần bằng mảnh vương miện để chồng đồ không giới hạn.', 'Đập/giải thể trả đồ. Nếu có quá nhiều chồng, dùng rương sập chuẩn để giữ phần đồ còn lại.'])
for i,name in enumerate(['Hạ Phẩm Linh Thạch','Trung Phẩm Linh Thạch','Thượng Phẩm Linh Thạch','Cực Phẩm Linh Thạch'],1):
    recipe=[(f'ttk_lingshi{i-1}',100 if i==2 else 10)] if i>1 else None
    add(f'ttk_lingshi{i}',name,'item','Linh thạch dùng chế tạo, đổi phẩm và vận hành các vật phẩm Phàm Nhân Tu Tiên.',recipe,S1 if recipe else None,
        ['Quái đủ điều kiện rơi 2–5 Hạ Phẩm; boss đủ điều kiện rơi 2–5 Thượng Phẩm. Không thưởng cho thú đồng hành hoặc boss đang chuyển giai đoạn.', 'Đổi phẩm một chiều: 100 Hạ → 1 Trung; 10 Trung → 1 Thượng; 10 Thượng → 1 Cực. Không có công thức tạo Hạ Phẩm từ Vàng/Đá.'])
add('lucmachthankiem','Lục Mạch Thần Kiếm','item','Trang bị triệu hồi tối đa sáu phi kiếm hộ thân, có tự đánh, chỉ định mục tiêu và nâng cấp bằng ngọc.', [('glasscutter',1),('redgem',6)],MAGIC,
    ['Mặc định độ bền vô hạn, đeo ô dây chuyền; nếu không có ô này thì dùng ô thân. Có cấu hình đổi ô, sát thương, tốc độ và độ bền.', 'Bắt đầu với kiếm đỏ; dùng lần lượt Ngọc Xanh Dương, Tím, Cam, Vàng, Xanh Lá. Mỗi cấp mặc định cần 6 viên đúng màu; hệ số sát thương: 0,2 / 0,3 / 0,45 / 0,6 / 0,75 / 1.', 'Một Ngọc Lấp Lánh bật cầu vồng và nhân đôi sát thương gốc + planar một lần: cấp cuối mặc định 34 + 10 planar → 68 + 20 planar. Dùng thêm không nhân tiếp; chỉ sửa 800 độ bền nếu cấu hình hữu hạn.', 'Solo là tùy chọn: cường hóa tăng sát thương vật lý phi kiếm; không nhân bonus Solo vào planar. Vẫn dùng được khi không bật Solo.'])
elemental_swords = [
    ('ttk_votuongkiem','Vô Tướng Kiếm','xd_wxj',[('goldnugget',12),('flint',6)],'Kim: mỗi đòn thêm 10 sát thương planar.'),
    ('ttk_thanhtrucphongvankiem','Thanh Trúc Phong Vân Kiếm','xd_htz_qzj',[('livinglog',6),('twigs',12)],'Mộc: mỗi đòn thứ tư gọi một phi kiếm đuổi mục tiêu, gây 40% sát thương nền vũ khí.'),
    ('ttk_tinhlakiem','Tinh La Kiếm','xd_xlj',[('bluegem',3),('goldnugget',6)],'Thủy: 20% cơ hội làm chậm di chuyển 25% trong 3 giây; làm mới thời gian, không cộng dồn.'),
    ('ttk_phanthienkiem','Phần Thiên Kiếm','xd_ftj',[('redgem',3),('charcoal',6)],'Hỏa: 15% cơ hội nổ bán kính 3, gây 30% sát thương nền vũ khí; không gây cháy.'),
    ('ttk_tienkiem','Tiên Kiếm','xd_sword_red',[('thulecite',6),('rocks',12)],'Thổ: mỗi đòn thứ năm nhận lá chắn hấp thụ 30 sát thương, tồn tại 5 giây; không cộng dồn.'),
    ('ttk_makiem','Ma Kiếm','xd_sword_mo',[('purplegem',3),('nightmarefuel',6)],'Lôi: 20% cơ hội phóng điện sang tối đa hai địch khác, mỗi con nhận 35% sát thương nền vũ khí.'),
]
for code,name,source_code,materials,passive in elemental_swords:
    add(code,name,'item','Kiếm cầm tay thuộc bộ sáu nguyên tố để hợp thành Lục Nguyên Kiếm Đồng.', materials+[('ttk_lingshi2',1)],S2,
        ['Mọi nhân vật đều chế tạo và sử dụng được. 100 sát thương nền, tầm đánh 2.', 'Bắt đầu 300/1.000 lượt, giữ kiếm và sát thương khi cạn; nạp lại bằng vũ khí khác.' if code == 'ttk_tinhlakiem' else '1.000 lượt, chế tạo đầy lượt; nạp bằng vũ khí khác theo bảng Tinh La. Kiếm vỡ khi dùng hết.', passive, 'Sát thương phụ không crit hoặc kích hoạt thêm nội tại. Tỷ lệ sát thương phụ tính theo nền vũ khí sau cường hóa.', 'Dùng một thanh cùng năm kiếm nguyên tố còn lại để chế Lục Nguyên Kiếm Đồng.'],source_code=source_code)
add('ttk_lucnguyenkiemdong','Lục Nguyên Kiếm Đồng','item','Ống bắn hợp thành từ sáu kiếm, gọi phi kiếm nguyên tố khi chí mạng.', [(s[0],1) for s in elemental_swords],S2,
    ['50 sát thương nền, tầm bắn 8; mọi nhân vật dùng được, không cần vật phẩm đạn.', '1.000 lượt bắn; mỗi phát tốn 1 lượt. Một Hạ Phẩm Linh Thạch nạp 100 lượt, tối đa 1.000; đầy từ chối nhận. Hết lượt giữ vũ khí nhưng không bắn được.', 'Phát bắn trúng crit thật của Solo gọi ngẫu nhiên 1–6 kiếm khác nhau. Mỗi kiếm bốc riêng 10–20% sát thương nền trước crit, có tính cường hóa vũ khí.', 'Kiếm xuất phát từ người chơi, tỏa rồi bay vòng cung đuổi mục tiêu; đánh một lần rồi tan. Kiếm phụ không crit tiếp, không gọi loạt mới hoặc hao thêm lượt.', 'Kim thêm 10 sát thương planar. Mộc hồi 2 máu, hồi chiêu riêng 3 giây. Thủy có 20% cơ hội làm chậm di chuyển 25% trong 2 giây.', 'Hỏa nổ bán kính 2 lên địch khác, gây 50% sát thương kiếm khí; không gây cháy. Thổ tạo lá chắn 10 sát thương trong 3 giây, hồi chiêu riêng 3 giây. Lôi nảy sang một địch khác, gây 50% sát thương kiếm khí.', 'Hồi chiêu tính theo người bắn; làm chậm và lá chắn không cộng dồn. Không bật Solo vẫn bắn thường; vũ khí không tự có tỷ lệ crit.'],source_code='xd_jingwei_blowdart')
add('vanhonphien','Cửu Thiên Tinh Thần Phiên','item','Pháp bảo đặt đất thu hồn và gọi Hồn Vệ hỗ trợ chiến đấu.', [('livinglog',6),('nightmarefuel',12),('purplegem',2),('ttk_lingshi2',6)],MAGIC,
    ['Đặt xuống gọi 2 Hồn Vệ nếu hết hồi chiêu 60 giây. Thu hồn trong bán kính 18; mỗi 2 hồn gọi thêm 1 vệ nếu chủ còn sống trong bán kính 16.', 'Có 4 lượt gọi bổ sung, mỗi lượt hồi 60 giây; giữ tối đa 2 hồn chờ. Chuột phải thu lại, giữ hồn và hồi chiêu qua thu/đặt và save/load.', 'Thu Phiên hoặc chủ chết/rời shard sẽ giải tán Hồn Vệ; vệ tồn tại tối đa 60 giây, không khôi phục sau tải save. Không dùng độ bền. Có carrier sát thương Solo tùy chọn; không cần bật Solo.'],source_code='xd_wmz_zhf')
add('thanhiquangtruong','Thần Hi Quang Trượng','item','Trượng tăng tốc 30%, dịch chuyển gần và qua bản đồ.', [('townportaltalisman',3),('yellowgem',1),('ttk_lingshi2',1)],MAGIC,
    ['Có 30 lượt. Dịch chuyển gần tốn 1 lượt, tầm 36; bản đồ tốn 3 lượt, tầm 128 và đích đã khám phá trong cùng shard.', 'Hồi chiêu chung 30 giây, không tốn tinh thần. Đá Sa Mạc nạp 15 lượt, tối đa 30; nạp không xóa hồi chiêu.', 'Đánh thường dùng sát thương gậy đi bộ, không tốn lượt. Hết lượt trượng biến mất, nên nạp trước khi cạn. Mọi nhân vật dùng được.'],source_code='xd_yunxiao_fysz')
add('homesign','Truyền Tống Trận','structure','Mạng lưới cổng dịch chuyển nhanh giữa các điểm đã đặt tên trong cùng shard.', [('boards',5),('goldnugget',5)],S1,
    ['Xây ít nhất hai cổng, viết tên rồi nhấp phải Chọn điểm đến. Có tùy chọn chi phí độ no/tinh thần, đếm ngược, quyền sở hữu và dùng biển chỉ đường.', 'Đưa người chơi, thú đi theo và đồ nặng gần cổng tới điểm đến hợp lệ. Không dịch chuyển khi có nguy hiểm; chưa hỗ trợ đi giữa mặt đất và hang.', 'Tắt mod cổng riêng/Fast Travel cùng thay hành vi bảng hiệu để tránh xung đột. Bản 0.8.3 kiểm tra lại vị trí và quyền điểm đến khi hết đếm ngược.'])
trees=[('yhs','Anh Đào Thụ','purplegem',4,2),('df','Đan Phong','redgem',8,4),
       ('ls','Lam Sam','bluegem',2,1),('yxs','Ngân Hạnh','orangegem',2,1)]
gem_names={'purplegem':'Ngọc Tím','redgem':'Ngọc Đỏ','bluegem':'Ngọc Xanh Dương','orangegem':'Ngọc Cam'}
for suffix,name,gem,cost,count in trees:
    add('ttk_tree_'+suffix,name,'structure',f'Cây che mưa, điều hòa nhiệt và sinh {count} ngọc mỗi khoảng 7 ngày.', [('livinglog',4),(gem,cost),('ttk_lingshi1',1)],S2,
        [f'Sinh {count} {gem_names[gem]} mỗi 3.360 giây + 0–100 giây.', 'Giữ nhiệt độ vùng bán kính 6 ở 19 độ, che mưa. Dùng búa tháo công trình.'])
flowers=[('bh','Bách Hợp','purplegem',2),('bmg','Bạch Mân Côi','yellowgem',2),('pgy','Bồ Công Anh','log',12),
         ('ll','Linh Lan','twigs',15),('md','Mẫu Đơn','redgem',3),('mlh','Mộc Lê Hoa','greengem',1)]
for suffix,name,material,amount in flowers:
    add('ttk_flower_'+suffix,name,'structure','Hoa trang trí dưỡng tinh thần và thu hút bướm.', [('butterfly',2),(material,amount),('ttk_lingshi1',1)],S1,
        ['Aura tinh thần bằng 2 × SANITYAURA_TINY.', 'Mỗi bình minh ngoài mùa đông có 40% cơ hội sinh một bướm; không sinh trong hang. Không có sản phẩm hoa/quả custom riêng.'])
add('ttk_gj','Cam Tỉnh','structure','Giếng nước dùng nạp bình tưới.', [('rocks',12),('rope',1),('log',11),('ttk_lingshi1',1)],S1,
    ['Dùng thao tác lấy nước chuẩn của bình tưới. Không cần bình nước riêng hoặc linh lực của Tu Tiên gốc.', 'Không tạo ra chai nước/vật phẩm mới. Dùng búa tháo công trình.'])
add('ttk_huapen','Chậu Hoa Uẩn Linh','structure','Trồng rau, có 2 lượt linh lực và nạp lại bằng Hạ Phẩm Linh Thạch.', [('livinglog',1),('cutstone',2),('ttk_lingshi1',3)],S1,
    ['Gieo một hạt rau vào mỗi chậu. Khi còn linh lực, bỏ stress cuối vụ và cho phép cây đạt khổng lồ; cây vẫn cần thời gian, ánh sáng. Hạt thường vẫn có thể ra cỏ dại.', 'Mỗi lần cây bị thu hoạch/đào/cháy mất tốn 1 lượt; chuyển mầm vô danh không tốn lượt. Khi hết, dùng 1 Hạ Phẩm Linh Thạch lên chậu/cây, chọn Uẩn linh để nạp lại 2 lượt.', 'Cây, hạt, nông sản khổng lồ và sản phẩm thối dùng loại tương ứng của DST. Chậu có cây không thể đập; chậu trống đập ra 1 Đá Cắt + 1 Hạ Phẩm.'])
houses=[('pflnw','Chuồng Bò Lai','beefalo','Bò Lai',[('cutstone',5),('goldnugget',3),('horn',2),('ttk_lingshi1',10)],'Đủ đàn 3 kỳ ngày: 8 lông bò, 50% thêm 1 sừng.',1800),('ftys','Chuồng Dê Điện','lightninggoat','Dê Điện',[('lightninggoathorn',2),('rocks',10),('rope',10),('ttk_lingshi1',10)],'Mỗi kỳ ngày đủ đàn: 1 sữa dê, 25% thêm 1 sừng.',1400),('klxw','Chuồng Voi Koala','koalefant','Voi Koala',[('cutstone',5),('trunk_summer',1),('trunk_winter',1),('ttk_lingshi1',10)],'Đủ đàn 3 kỳ ngày: 1 vòi hè hoặc đông ngẫu nhiên.',1800)]
for suffix,name,animal,animalname,recipe,production,hp in houses:
    add('ttk_'+suffix,name,'structure','Nuôi tối đa hai thú, có sản phẩm định kỳ và thao tác Thu hoạch.',recipe,S1,[production,'Thú ra ban ngày, về chuồng ban đêm; tái tạo đàn khoảng 480 giây. Đủ đàn tính cả thú trong/ngoài chuồng; kho cần chỗ trống.', 'Dùng Thu hoạch lấy đồ trong kho. Đập chuồng thả đàn kể cả ban đêm; nếu chưa có chỗ ra, giữ chuồng và thú còn lại.'])
    add('ttk_'+animal,animalname,'mob',f'Thú của {name}, {hp} máu; tự về chuồng ban đêm.',effects=['Thú chết rơi 1 Thịt. Có brain và stategraph riêng, không cần Tu Tiên gốc.', 'Là thú đồng hành: không phát linh thạch khi chết. Không mặc định có mọi khả năng thuần hóa/cưỡi của thú vanilla.'],source_code='xd_'+animal)
add('ttk_gjx','Công Cụ Hạp','structure','Kho 36 ô, tự nhặt công cụ vô chủ quanh công trình.', [('goldnugget',3),('boards',2),('ttk_lingshi1',7)],S1,
    ['Mỗi khoảng 10 giây quét bán kính 8, nhận công cụ/ô và dụng cụ hợp lệ. Bỏ qua đồ đang cầm và đồ có thông tin chủ sở hữu.', 'Hỗ trợ nâng cấp sức chứa một lần bằng mảnh vương miện; đập trả đồ, quá tải dùng rương sập chuẩn.'])
add('ttk_dbg','Đa Bảo Các','structure','Kệ chứa 36 ô và trưng bày tám món đầu tiên.', [('boards',6),('goldnugget',2),('marble',2),('ttk_lingshi1',1)],S1,
    ['Hiển thị tám ô đầu, cập nhật khi cất/lấy và tải save.', 'Hỗ trợ nâng cấp sức chứa một lần bằng mảnh vương miện. Đập trả đồ; quá tải dùng rương sập. Mẫu LLT có linh thú thoáng hiện; mẫu YBG giữ cơ chế trưng bày.'])
add('ttk_dc','Cửu U Xích Linh Đăng','structure','Đèn dùng linh thạch, tự sáng ban đêm; tên cũ Đăng Thải.', [('twigs',10),('rope',3),('goldnugget',3),('ttk_lingshi1',1)],S1,
    ['Bán kính sáng tăng từ 2,5 lên 3,5. Cho Hạ Phẩm Linh Thạch vào ô đèn; mỗi viên cho 3.360 giây phát sáng.', 'Dừng tiêu hao khi ban ngày hoặc hết nhiên liệu. Lưu thời gian còn lại qua save/load; đập trả linh thạch còn trong ô.'])

# Eleven-item structure/garden batch. Related products and FX are first-class
# records so the web mirrors every prefab that the transferred content creates.
add('ttk_luoshen_huazhong','Hạt Lạc Thần Hoa','item','Hạt giống độc lập để trồng Lạc Thần Hoa.', [('petals',60),('plantmeat',3),('ttk_lingshi2',1)],S2,
    ['Đặt xuống đất để tạo Lạc Thần Hoa ở giai đoạn mầm. Đây là đường tạo độc lập thay cho điều kiện nhân vật Lạc Thần của mod nguồn.'])
add('ttk_luoshen_hua','Lạc Thần Hoa','structure','Hoa năm giai đoạn, nuôi bằng linh thạch rồi tạo Lạc Thần Hoa Nhân.',effects=[
    'Dùng 1 Hạ Phẩm Linh Thạch để tiến một giai đoạn. Giai đoạn 3 sưởi vùng bán kính 15 ở 25 độ và có aura tinh thần; giai đoạn 4 nhận đất/nông sản để lớn tiếp.',
    'Giai đoạn 5 có kho 3 × 3 và tạo 1 Lạc Thần Hoa Ấn mỗi ngày. Đào cây trả 10 Cành Cây và 8 Cánh Hoa; giai đoạn, chu kỳ và đồ trong kho được lưu.'])
add('ttk_luoshen_huayin','Lạc Thần Hoa Nhân','item','Sản vật ăn được của Lạc Thần Hoa trưởng thành.',effects=[
    'Ăn hồi 10 máu, 5 no và 10 tinh thần. Có tốc độ hỏng PERISH_FAST; có thể cắm bình hoa và dùng như đồ chơi cho mèo.'])
add('ttk_luoshen_qingshu','Lạc Thần Thanh Sơ','item','Món chay nấu từ Lạc Thần Hoa Nhân.',station='Nồi Hầm',effects=[
    'Nấu khi hỗn hợp có Lạc Thần Hoa Nhân và không có thịt. Ăn hồi 200 máu, 42,5 no và 80 tinh thần; hỏng sau 15 ngày.'])
add('ttk_luoxiang_pengrou','Lạc Hương Phanh Nhục','item','Món thịt nấu từ Lạc Thần Hoa Nhân.',station='Nồi Hầm',effects=[
    'Nấu khi hỗn hợp có Lạc Thần Hoa Nhân và có thịt. Ăn hồi 10 máu, 75 no và 62,5 tinh thần.', 'Trong 480 giây sau khi ăn, mỗi lần đánh trúng mục tiêu còn sống hồi 2 máu.'])
add('ttk_lbx','Linh Bảo Sương','structure','Kho 20 ô có thể nhân bản một món đang cất.', [('cutstone',10),('boards',5),('ttk_lingshi1',20)],S1,
    ['Khi có ít nhất 12 ô đang dùng và còn chỗ, mỗi 15 ngày chọn ngẫu nhiên một món hợp lệ trong kho để nhân bản; chồng bản sao tối đa 20.', 'Chỉ xây tối đa ba chiếc trong mỗi shard. Bộ đếm giảm khi công trình bị tháo; đập trả toàn bộ đồ.'])
add('ttk_lgzbh','Lưu Quang Châu Bảo Hạp','structure','Kho 20 ô dành cho đá quý, linh thạch và Trân Châu Nứt.', [('goldnugget',10),('marble',4),('ttk_lingshi1',4)],S1,
    ['Chỉ nhận đồ có tag gem, linh thạch Phàm Nhân Tu Tiên và Trân Châu Nứt. Có hiệu ứng lấp lánh.', 'Nâng cấp sức chứa chồng một lần bằng mảnh vương miện; đập trả đồ và giữ phần quá tải trong rương sập.'])
add('ttk_mg','Mật Quán','structure','Kho 20 ô bảo quản mật, ong và kẹo.', [('butterfly',10),('rocks',5),('rope',2),('ttk_lingshi1',10)],S1,
    ['Chỉ nhận Băng Gạc, Ong, Sáp Ong, Sữa Ong Chúa, Đường Gia Vị, Mật Ong, Tổ Ong và Kẹo Dẻo.', 'Hệ số hỏng −0,2 giúp thực phẩm bên trong hồi độ tươi. Nâng cấp sức chứa chồng một lần bằng mảnh vương miện.'])
add('ttk_sj_kls','Khô Lâu Sơn','structure','Điểm nhập sơn dùng mở bản đồ và dịch chuyển đến nơi đã khám phá.', [('cutstone',6),('boneshard',3),('purplegem',1),('ttk_lingshi2',1)],MAGIC,
    ['Nhấp phải Nhập sơn, trả 25 tinh thần rồi có 20 giây mở bản đồ để chọn vị trí hợp lệ trong cùng shard.', 'Máy chủ kiểm tra người dùng còn ở gần đúng Khô Lâu Sơn, đích đã khám phá và có thể đứng trước khi dịch chuyển. Mọi nhân vật đều dùng được.'])
add('ttk_lbjlt','Linh Bảo Tế Luyện Đài','structure','Tế luyện pháp bảo Phàm Nhân Tu Tiên tối đa chín cấp.', [('flint',3),('cutstone',6),('ttk_lingshi2',1)],MAGIC,
    ['Đặt Lục Mạch Thần Kiếm, Cửu Thiên Tinh Thần Phiên hoặc Lục Nguyên Kiếm Đồng vào ô rồi bấm Tế luyện. Tỉ lệ thành công 100%; chi phí Thượng Phẩm Linh Thạch theo cấp 0–8 là 1, 1, 1, 3, 6, 12, 33, 99, 300.', 'Mỗi cấp tăng 5% sát thương, tối đa 45%. Cấp tế luyện được lưu cùng pháp bảo và vẫn hoạt động khi không bật Solo. Với Kiếm Đồng, tăng sát thương phát chính và sát thương nền dùng tính kiếm phụ; không nhân tế luyện lần thứ hai.'])

# Related forms are searchable records as well as links from their parent item.
add('vanhonphien_ground','Cửu Thiên Tinh Thần Phiên · Đã dựng','structure','Dạng đặt đất thu hồn và điều khiển Hồn Vệ.',effects=['Chuột phải thu lại Phiên. Số hồn và hồi chiêu giữ nguyên; thu Phiên giải tán Hồn Vệ của nó.'],source_code='xd_wmz_zhf')
add('vanhonphien_soul','Hồn Vệ','mob','Thực thể triệu hồi từ Phiên, tồn tại 60 giây.',effects=['Hỗ trợ mục tiêu của chủ và kẻ đang đánh chủ/vệ; mỗi chuỗi bắn 2 đạn, chu kỳ 2 giây, nền 20 vật lý mỗi đạn và lan bán kính 3. Cường hóa sát thương Phiên bằng Solo tăng sát thương đạn và lan; giữ mức cường hóa qua đặt/thu và tải save.', 'Không đánh chủ/thú của chủ; tắt PvP thì không đánh người chơi khác và đồng hành của họ. Biến mất khi chủ chết/rời shard hoặc thu Phiên.'],source_code='xd_wmz_zhf_soul')
for suffix,label in [('red','Đỏ'),('blue','Xanh Dương'),('purple','Tím'),('orange','Cam'),('yellow','Vàng'),('green','Xanh Lá')]:
    add('lucmachthankiem_'+suffix,'Phi Kiếm '+label,'effect','Phi kiếm được triệu hồi khi trang bị Lục Mạch Thần Kiếm ở cấp ngọc tương ứng.',effects=['Không chế tạo hoặc nhặt riêng. Nhận sát thương từ trang bị chính, cùng hiệu ứng cầu vồng và cường hóa tùy chọn.'])
for code,name,parent in [('lucmachthankiem_ember_vfx','Tàn Sáng Phi Kiếm','lucmachthankiem'),('lucmachthankiem_sparkle_vfx','Tinh Quang Phi Kiếm','lucmachthankiem'),('thanhiquangtruongfx','Hạt Sáng Thần Hi','thanhiquangtruong'),('vanhonphien_soulfx','Hồn Bay Về Phiên','vanhonphien_ground'),('vanhonphien_soulfx_in','Hiệu Ứng Nhập Hồn','vanhonphien_ground'),('vanhonphien_projectile','Đạn Hồn Vệ','vanhonphien_soul'),('vanhonphien_hit_fx','Hiệu Ứng Đạn Trúng','vanhonphien_projectile'),('vanhonphien_vortexspawner','Bộ Tạo Xoáy Phiên','vanhonphien_ground'),('vanhonphien_vortexfx','Xoáy Tinh Thần Phiên','vanhonphien_ground')]:
    add(code,name,'effect','Thực thể phụ trợ tự tạo trong quá trình sử dụng '+by_code[parent]['name']+'.',effects=['Không chế tạo/nhặt riêng; được xử lý cùng cơ chế của vật phẩm chủ.'])
    product(parent,code,'Tự tạo','Xuất hiện trong khi vật phẩm hoạt động.')
for code,name,parent in [('ttk_hyf_fullfx','Linh Khí Linh Bảo Sương','ttk_lbx'),('ttk_hyf_frontfx','Quầng Sáng Linh Bảo Sương','ttk_lbx'),('ttk_hyf_frontfx_small','Quầng Sáng Nhỏ','ttk_lbx'),('ttk_lgzbh_fx','Tinh Quang Châu Bảo Hạp','ttk_lgzbh'),('ttk_lbjlt_fx','Linh Quang Tế Luyện','ttk_lbjlt')]:
    add(code,name,'effect','Hiệu ứng phụ trợ của '+by_code[parent]['name']+'.',effects=['Không chế tạo hoặc nhặt riêng; tự xuất hiện khi công trình hoạt động.'])
    product(parent,code,'Tự tạo','Xuất hiện khi công trình kích hoạt hiệu ứng tương ứng.')
add('ttk_luoxiang_pengrou_buff','Dư Vị Lạc Hương','effect','Buff hồi máu của Lạc Hương Phanh Nhục.',effects=['Tồn tại 480 giây; mỗi lần người ăn đánh trúng mục tiêu còn sống sẽ hồi 2 máu. Không chế tạo hoặc nhặt riêng.'])
product('ttk_luoxiang_pengrou','ttk_luoxiang_pengrou_buff','1 hiệu ứng','Kích hoạt khi ăn; ăn lại làm mới thời gian.')
add('ttk_skin_spirit','Linh Thú · Skin LLT','effect','Linh thú trang trí của mẫu LLT Đa Bảo Các, thoáng hiện rồi tan biến.',effects=['Đi quanh vị trí xuất hiện trong khoảng 8 giây rồi mờ dần; không tấn công, không rơi chiến lợi phẩm.'])
from ttk_batch19_web import populate as populate_batch19
populate_batch19(ROOT, original, add, product, by_code)

add('ttk_yhsyz', 'Nguyệt Hoa Nhiếp Dược Chi', 'item',
    'Cầm để hái linh thảo trưởng thành an toàn, tăng khả năng nhận hạt.',
    [('twigs',12),('petals',6),('orangegem',2),('ttk_lingshi2',1)], S1,
    ['100 lượt dùng; mỗi lần hái linh thảo trưởng thành tốn một lượt, hết lượt dụng cụ biến mất.',
     'Tỷ lệ trả hạt tăng từ 40% lên 75%; tránh tác hại khi hái sáu linh thảo TTK.',
     'Mọi nhân vật dùng được. Trang bị trên tay rồi dùng thao tác hái thông thường.'], source_code='xd_yhsyz')
add('ttk_hyc', 'Hoán Nguyệt Trì', 'structure',
    'Hồ nuôi cá ao và cá biển sống, có ánh sáng ban đêm.',
    [('moonglass',10),('yellowgem',3),('marble',15),('ttk_lingshi1',1)], S1,
    ['Ba vị trí nuôi độc lập, mỗi lần đưa vào nhận một cá.',
     'Sau 3.360 giây mỗi cá cho bốn cá cùng loại; thu hoạch rồi thả cá mới.',
     'Lưu/tải giữ tiến độ. Đập hồ trả cá giống chưa đủ ngày và sản lượng đã trưởng thành.',
     'Phát sáng ban đêm, bán kính 3,5, không cần nhiên liệu.'], source_code='xd_hyc')
add('ttk_tree_xhs', 'Hạnh Hoa Thụ', 'structure',
    'Cây cảnh che chở, điều hòa nhiệt độ và kết Ngọc Vàng.',
    [('livinglog',4),('yellowgem',2),('ttk_lingshi1',1)], S2,
    ['Giữ nhiệt độ 19°C trong bán kính 6 và có khả năng che chở.',
     'Tạo một Ngọc Vàng mỗi khoảng 3.360 giây cộng độ trễ ngẫu nhiên 0–100 giây.'], source_code='xd_tree_xhs')
product('ttk_tree_xhs','yellowgem','1','Mỗi khoảng bảy ngày + 0–100 giây.')
add('ttk_hmsw', 'Hoán Miêu Thụ Ốc', 'structure',
    'Nhà Catcoon tích quà ngẫu nhiên khi đủ thú và còn chỗ chứa.',
    [('cutstone',3),('log',10),('coontail',3),('ttk_lingshi1',10)], S1,
    ['Tối đa một Catcoon, phục hồi sau 480 giây.',
     'Mỗi ngày đủ thú tạo tối đa 2–3 món quà cùng loại được chọn ngẫu nhiên, tùy chỗ trống.',
     'Dùng Nhận quà để lấy đồ tích trong nhà; giữ danh sách quà và Catcoon qua lưu/tải.'], source_code='xd_hmsw')

for skin in json.loads((MOD/'skins_manifest.json').read_text(encoding='utf-8')):
    base=by_code.get(skin['base'])
    # The curated web catalog is intentionally narrower than the runtime mod.
    # Keep regeneration safe until a base item has its own documented entry.
    if base is None:
        continue
    entry=add(skin['name'],base['name']+' · '+skin['display_name'],'other','Skin có sẵn của '+base['name']+'.',effects=['Chọn khi chế tạo hoặc đổi bằng Chổi Sạch; giữ nguyên cơ chế, sản vật và công thức của công trình gốc.'])
    entry['sprite']=sprite(skin.get('icon_name',skin['name']))
    product(skin['base'],skin['name'],'Skin có sẵn','Chọn ngoại hình, không phải vật phẩm rơi.')
    product(skin['name'],skin['base'],'Công trình gốc','Xem tác dụng, công thức và sản vật.')
product('ttk_dbg_skins_llt','ttk_skin_spirit','1 linh thú','Mỗi khoảng 110–120 giây khi có người xem; các kệ LLT gần nhau giãn nhịp hiệu ứng.')
product('ttk_tianjiwu_skins_byj','ttk_tianjiwu_baihufx','1 linh thú','Linh thú trang trí đi kèm ngoại hình Bạch Ngọc Kinh của Thiên Cơ Ốc.')

# Explicit production edges and the reverse acquisition links.
for suffix,_,gem,_,count in trees:product('ttk_tree_'+suffix,gem,str(count),'Mỗi khoảng 3.360 giây + 0–100 giây.')
for s,_,_,_ in flowers:product('ttk_flower_'+s,'butterfly','1','40% mỗi bình minh ngoài mùa đông; không sinh trong hang.')
product('ttk_luoshen_huazhong','ttk_luoshen_hua','1 cây','Trồng hạt xuống đất.')
product('ttk_luoshen_hua','ttk_luoshen_huayin','1/ngày','Khi cây đạt giai đoạn 5 và hết chu kỳ hái lại.')
product('ttk_luoshen_huayin','ttk_luoshen_qingshu','1 món','Nấu trong Nồi Hầm với hỗn hợp không có thịt.')
product('ttk_luoshen_huayin','ttk_luoxiang_pengrou','1 món','Nấu trong Nồi Hầm với hỗn hợp có thịt.')
product('ttk_luoshen_hua','twigs','10','Đào Lạc Thần Hoa.')
product('ttk_luoshen_hua','petals','8','Đào Lạc Thần Hoa.')
product('ttk_lbjlt','lucmachthankiem','Tế luyện','Mỗi cấp tăng 5% sát thương, tối đa chín cấp.')
product('ttk_lbjlt','vanhonphien','Tế luyện','Mỗi cấp tăng 5% sát thương, tối đa chín cấp.')
product('ttk_lbjlt','ttk_lucnguyenkiemdong','Tế luyện','Mỗi cấp tăng 5% sát thương phát chính và nền kiếm phụ, tối đa chín cấp; lưu trên vũ khí.')
by_code['ttk_lucnguyenkiemdong']['details']['usage']['effects'].append({
    'trigger': 'Tế luyện',
    'text': 'Mỗi cấp tăng 5% sát thương phát chính và nền kiếm phụ, tối đa chín cấp; lưu trên vũ khí.',
    'evidence': evidence,
})
for a,b,n,c in [('ttk_huapen','cutstone','1','Đập chậu trống.'),('ttk_huapen','ttk_lingshi1','1','Đập chậu trống.'),('vanhonphien','vanhonphien_ground','1','Đặt pháp bảo xuống đất.'),('vanhonphien_ground','vanhonphien','1','Thu lại pháp bảo.'),('vanhonphien_ground','vanhonphien_soul','2 ban đầu; +1/2 hồn','Hồi chiêu và điều kiện chủ đứng gần như mô tả.')]:product(a,b,n,c)
for suffix in ['red','blue','purple','orange','yellow','green']:product('lucmachthankiem','lucmachthankiem_'+suffix,'1 theo cấp','Trang bị chính triệu hồi 1–6 kiếm tùy cấp ngọc.')
for suffix,_,animal,_,_,_,_ in houses:
    product('ttk_'+suffix,'ttk_'+animal,'Tối đa 2','Tái tạo đàn, ra ban ngày và về nhà ban đêm.')
    product('ttk_'+animal,'meat','1','Khi thú chết.')
for a,b,n,c in [('pflnw','beefalowool','8','Mỗi 3 kỳ ngày đủ đàn; cần chỗ trong kho.'),('pflnw','horn','1','50% mỗi 3 kỳ ngày đủ đàn.'),('ftys','goatmilk','1','Mỗi kỳ ngày đủ đàn.'),('ftys','lightninggoathorn','1','25% mỗi kỳ ngày đủ đàn.'),('klxw','trunk_summer','1','50% mỗi 3 kỳ ngày đủ đàn; chọn một loại vòi.'),('klxw','trunk_winter','1','50% mỗi 3 kỳ ngày đủ đàn; chọn một loại vòi.')]:product('ttk_'+a,b,n,c)
for code in ['ttk_hhlmz','ttk_gjx','ttk_dbg','ttk_lgzbh','ttk_mg']:
    product(code,'alterguardianhatshard','1','Hoàn trả khi tháo công trình đã nâng cấp sức chứa.')
    product(code,'collapsed_treasurechest','Khi quá tải','Giữ phần đồ dư khi tháo kho nâng cấp quá nhiều chồng.')

# Preserve EVA's pre-existing web entry without implying it is bundled in TuTienKy.
add('calliope_mori','EVA','character','Nhân vật EVA đã có trên web, thuộc mod riêng chuyển thể Calliope Mori; không nằm trong gói Phàm Nhân Tu Tiên.',effects=['Mục nhân vật cũ được giữ để tra cứu; không thuộc đợt rà soát nội dung Phàm Nhân Tu Tiên.'])

for item in entries:
    recipe=item.pop('_recipe')
    if recipe:
        ingredients=[dict(ref(c),amount=n) for c,n in recipe]
        item['recipe']={'outputCount':1,'ingredients':ingredients}
        for c,n in recipe:
            if c in by_code:
                by_code[c]['details']['usage']['recipes'].append({'result':ref(item['prefabId']),'resultAmount':1,'subjectAmount':n,'ingredients':ingredients,'craftingNote':item['craftingNote']})
for tier,condition in [(1,'Quái thường đủ điều kiện, không phải thú đồng hành.'),(3,'Boss đủ điều kiện; bỏ giai đoạn chuyển phase.')]:
    by_code[f'ttk_lingshi{tier}']['details']['dropBy']={'status':'known','sources':[{'type':'drop','source':None,'quantity':'2–5','chance':'Mỗi lần chết hợp lệ','conditions':condition,'evidence':evidence}]}
for item in entries:
    for prod in item['products']:
        assert prod['item']['id'] in {e['id'] for e in entries+list(support.values())}
out=ROOT/'app/data/tu-tien-ky.ts'
out.write_text('import type { ItemListEntry } from "@/app/lib/item-catalog";\n\n// Generated by tools/build_tu_tien_ky_web.py from the curated mod records.\nexport const tuTienKyVersion = "'+VERSION+'";\nexport const tuTienKyItems = '+json.dumps(entries,ensure_ascii=False,indent=2)+' satisfies readonly ItemListEntry[];\n\nexport const tuTienKyReferences = '+json.dumps(list(support.values()),ensure_ascii=False,indent=2)+' satisfies readonly ItemListEntry[];\n',encoding='utf-8')
print(f'Published {len(entries)} entries, {len(support)} supporting references and local inventory icons.')
