"""Refresh the web snapshot from the integrated mod without replacing curated entries."""
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "mods/PhamNhanTuTien"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "mods/mod_steam/.fasttravel-test-runtime"))
from lupa.luajit21 import LuaRuntime
from tools.extract.publish_solo_leveling_assets import decode_ktex


def publish_config():
    source = (MOD / "modinfo.lua").read_text(encoding="utf-8-sig")
    lua = LuaRuntime()
    # Only metadata evaluation; no filesystem, process, import or network APIs.
    env = lua.eval("{pairs=pairs, ipairs=ipairs, tonumber=tonumber, tostring=tostring, string=string, table=table, math=math}")
    lua.eval("function(s,e) local f=assert(loadstring(s)); setfenv(f,e); f() end")(source, env)
    options = []
    for _, row in env.configuration_options.items():
        choices = [{"label": v.description if v.description is not None else str(v.data), "value": v.data, "description": v.hover or ""}
                   for _, v in row.options.items()]
        # Decorative section headings in DST have a single blank choice.
        if len(choices) == 1 and not choices[0]["label"].strip():
            continue
        group = ("Túi đồ" if row.name.startswith("ttk_inv45_") else
                 "Truyền Tống Trận" if row.name.startswith("ttk_portal_") else
                 "Lục Mạch Thần Kiếm" if row.name.startswith("lucmachthankiem_") else
                 "Vĩnh Hằng Thần Hỏa" if row.name.startswith("ttk_vhth_") else
                 "HUD chiến đấu" if row.name.startswith("ttk_hud_") else
                 "Solo tích hợp")
        options.append({"key": row.name, "label": row.label, "description": row.hover or "",
                        "group": group, "default": row.default, "choices": choices})
    assert len({v["key"] for v in options}) == len(options)
    for option in options:
        assert any(type(c["value"]) is type(option["default"]) and c["value"] == option["default"] for c in option["choices"]), option["key"]
    payload = {"version": env.version, "source": "mods/PhamNhanTuTien/modinfo.lua",
               "sourceHash": hashlib.sha256(source.encode()).hexdigest(), "options": options}
    (ROOT / "app/data/pham-nhan-config.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return len(options)


def publish_catalog():
    path = ROOT / "app/data/tu-tien-ky.ts"
    text = path.read_text(encoding="utf-8")
    marker = " satisfies readonly ItemListEntry[];"
    items = json.loads(text.split("export const tuTienKyItems = ", 1)[1].split(marker, 1)[0])
    refs = json.loads(text.split("export const tuTienKyReferences = ", 1)[1].split(marker, 1)[0])
    by_code = {i["prefabId"]: i for i in items}
    vanilla = {i["prefabId"]: i for i in json.loads((ROOT / "public/data/items.json").read_text(encoding="utf-8"))["items"] if i["namespace"] == "base_game"}
    # Preserve the exact ingredient ID used by the integrated recipe.
    if "armor_skeleton" not in vanilla:
        vanilla["armor_skeleton"] = dict(id="base_game:armor_skeleton", prefabId="armor_skeleton", namespace="base_game", category="item", name="Giáp Xương", englishName="Bone Armor", description="Nguyên liệu Giáp Xương trong công thức Tà Sát Hộ Giáp.", craftingNote=None, sprite=None, recipe=None, wiki=None)
    for item in items:
        for effect in (item.get("details") or {}).get("usage", {}).get("effects", []):
            if "Solo là tùy chọn" in effect["text"]:
                effect["text"] = "Solo đã tích hợp trong Phàm Nhân. Cường hóa tăng sát thương vật lý phi kiếm; không nhân phần thưởng cường hóa vào sát thương planar."

    def add(code, name, category, description, materials=(), station=None, source="modinfo.lua"):
        atlas = next((p for p in [MOD/f"images/inventoryimages/{code}.xml", MOD/f"images/map_icons/{code}.xml", MOD/f"images/{code}/icon.xml"] if p.exists()), None)
        sprite = None
        if atlas:
            tree = ET.parse(atlas).getroot()
            element = tree.find("Elements/Element")
            image = ROOT/f"public/tu-tien-ky/icons/{code}.png"
            image.parent.mkdir(parents=True, exist_ok=True)
            decode_ktex((atlas.parent/tree.find("Texture").get("filename")).read_bytes()).save(image)
            sprite = {"src": f"/tu-tien-ky/icons/{code}.png", "uv": {k: float(element.get(k)) for k in ["u1","u2","v1","v2"]}}
        ingredients = []
        for key, amount in materials:
            ingredient = by_code.get(key) or vanilla.get(key)
            if not ingredient:
                raise ValueError(f"Missing ingredient {key} for {code}")
            ingredients.append({**{k: ingredient[k] for k in ["id","name","sprite"]}, "amount": amount})
            if key not in by_code and not any(v["id"] == ingredient["id"] for v in refs):
                refs.append(ingredient)
        entry = {"id": "tu_tien_ky:"+code, "prefabId": code, "namespace": "tu_tien", "category": category,
                 "name": name, "englishName": None, "description": description, "craftingNote": station, "sprite": sprite,
                 "recipe": {"outputCount": 1, "ingredients": ingredients} if ingredients else None, "wiki": None,
                 "details": {"recipeStatus": "known" if ingredients else "unknown", "usage": {"status": "known", "recipes": [],
                 "effects": [{"trigger": "Sử dụng", "text": description, "evidence": [{"source": "Phàm Nhân Tu Tiên 2.0", "locator": "mods/PhamNhanTuTien/"+source}]}]},
                 "dropBy": {"status": "unknown", "sources": []}}}
        if code not in by_code:
            items.append(entry)
            by_code[code] = entry
        else:
            # Keep hand-authored products/relationships from other tasks.
            current = by_code[code]
            for field in ["name", "description", "craftingNote", "sprite", "recipe"]:
                current[field] = entry[field]
            current.setdefault("details", entry["details"])["usage"]["effects"] = entry["details"]["usage"]["effects"]

    add("ttk_fsct", "Luân Hồi Đài", "structure", "Hồn ma ám vào đài để hồi sinh không giới hạn lượt; không cần nạp hoặc chờ hồi.", [("cutstone",10),("goldnugget",6),("reviver",2),("ttk_lingshi3",2)], "Máy Luyện Kim", "main/ttk_fsct.lua")
    add("ttk_chuongthienbinh", "Chưởng Thiên Bình", "item", "Đặt ngoài trời ban đêm để tích linh khí, tối đa 200. Mỗi lần thúc cây tiêu hao 50 linh khí.", [("livinglog",2),("moonglass",6),("bluegem",3),("ttk_lingshi1",30)], "Mũ Cao", "main/ttk_chuongthienbinh.lua")
    add("ttk_ngulongdang", "Ngư Long Đăng", "item", "Đèn chiếu sáng và điều hòa nhiệt độ. Mỗi Hạ Phẩm Linh Thạch nạp 10% linh khí; đầy thì không nhận thêm.", [("goldnugget",3),("log",2),("papyrus",3),("ttk_lingshi2",1)], "Máy Khoa Học", "main/ttk_ngulongdang.lua")
    add("nhatvuphuonghoa", "Nhất Vũ Phương Hoa", "item", "Ô che mưa và chống nóng. Hạ Phẩm Linh Thạch hồi 5% độ bền; phép Giữ Khô tiêu hao 25%, chống ướt trong 4 phút.", [("papyrus",6),("silk",3),("ttk_lingshi2",2),("livinglog",2)], "Máy Luyện Kim", "main/nhatvuphuonghoa.lua")
    add("ttk_zcmj", "Tử Xá Diện Giáp", "item", "830 độ bền, hấp thụ 90% sát thương thường, 10 phòng thủ phẳng, tăng 20% sát thương. Mặc cùng Tà Sát Hộ Giáp: 66% cơ hội tạo kết giới 2 giây, hồi 8 giây. Tự hồi 1% độ bền mỗi 10 giây; Trung Phẩm Linh Thạch sửa 20%.", [("feather_crow",1),("beefalowool",1),("feather_robin",3),("ttk_lingshi3",1)], "Không cần trạm chế tạo", "ARMOR_SET_VI.md")
    add("ttk_xshj", "Tà Sát Hộ Giáp", "item", "830 độ bền, hấp thụ 90% sát thương thường, 10 phòng thủ phẳng và tăng 10% tốc độ. Kết hợp Tử Xá Diện Giáp tạo kết giới. Tự hồi 1% độ bền mỗi 10 giây; Trung Phẩm Linh Thạch sửa 20%; hỏng vẫn giữ để sửa.", [("armor_skeleton",1),("ttk_spider_leg",1),("ttk_pog_tail",6),("ttk_lingshi3",1)], "Không cần trạm chế tạo", "ARMOR_SET_VI.md")
    add("ttk_yunxiao_ymsz", "Vân Mạc Thượng Trang", "item", "840 độ bền, hấp thụ 85%, giữ ấm 240 và phát sáng bán kính 5. Hao 1,25% độ bền mỗi phút mặc; sửa bằng Bộ Kim Chỉ.", [("beefalowool",8),("goldnugget",10),("ttk_lingshi2",2)], "Không cần trạm chế tạo", "ARMOR_SET_VI.md")
    add("ttk_choujiangji", "Máy Quay Thưởng Linh Thạch", "structure", "Mỗi Trung Phẩm Linh Thạch đổi một lượt: hệ thống bốc nhóm thưởng rồi một gói, người chơi nhận toàn bộ nội dung gói. Xem bảng thưởng đầy đủ trong mục Hướng dẫn.", [("cutstone",6),("boards",4),("gears",2),("purplegem",1),("ttk_lingshi1",30)], "Máy Luyện Kim", "CHOUJIANGJI_REWARDS.md")
    add("ttk_spirit_workshop", "Linh Tuyền Cực Phẩm", "structure", "Mỗi 5 ngày máy chủ hoạt động, thu 20 Hạ Phẩm và 2 Trung Phẩm; 20% cơ hội thêm 1 Thượng Phẩm. Không đào cạn, chỉ giữ một đợt chờ thu; lưu/tải giữ tiến độ. Chưa hỗ trợ di dời hoặc đập búa.", [("cutstone",20),("boards",6),("purplegem",2),("ttk_lingshi2",5),("ttk_lingshi3",1)], "Máy Luyện Kim", "SPIRIT_MINES_VI.md")
    for code, name, desc in [("ttk_rock1","Mỏ Linh Thạch Thường","6 lượt công: 3 Đá, 1 Đá Lửa và 3 Hạ Phẩm; 50% thêm 1 Hạ Phẩm."),("ttk_rock2","Mỏ Linh Thạch Hiếm","6 lượt công: 3 Đá, 1 Đá Lửa và 1 Trung Phẩm."),("ttk_rock3","Mỏ Linh Thạch Tuyệt Phẩm","12 lượt công: 3 Đá và 1 Thượng Phẩm.")]:
        add(code,name,"structure",desc+" Mỏ tự nhiên khai thác bằng cuốc, đào hết biến mất. Sinh ngoài mặt đất, bổ sung theo mùa; không có công thức chế tạo.", source="SPIRIT_MINES_VI.md")
    for code,name in [("deluxe_firepit","Bếp Thần Hỏa"),("endo_firepit","Bếp Hàn Hỏa"),("heat_star","Vĩnh Hằng Thần Hỏa"),("ice_star","Vĩnh Hằng Hàn Hỏa")]:
        add(code,name,"structure","Thuộc Vĩnh Hằng Thần Hỏa đã tích hợp. Công thức, nhiên liệu, phạm vi sáng và nhiệt độ phụ thuộc thiết lập mod; xem nhóm Vĩnh Hằng Thần Hỏa tại trang Config.",source="main/ttk_vinhhangthanhoa.lua")
    for skin in json.loads((MOD/"skins_manifest.json").read_text(encoding="utf-8")):
        parent = by_code.get(skin["base"])
        if parent is None or skin["name"] in by_code:
            continue
        add(skin["name"], parent["name"]+" · "+skin["display_name"], "other", "Ngoại hình của "+parent["name"]+". Giữ công dụng của công trình gốc; chọn khi chế tạo hoặc thay bằng Chổi Sạch.", source="skins_manifest.json")
        child = by_code[skin["name"]]
        child["products"] = [{"item": {k: parent[k] for k in ["id","name","sprite"]}, "quantity": "Công trình gốc", "conditions": "Xem công thức và công dụng."}]
        parent.setdefault("products", []).append({"item": {k: child[k] for k in ["id","name","sprite"]}, "quantity": "Skin có sẵn", "conditions": "Ngoại hình, không phải vật phẩm rơi."})
    # Update source revision, retaining historical evidence labels.
    prefix = text.split("export const tuTienKyItems = ",1)[0]
    path.write_text(prefix+"export const tuTienKyItems = "+json.dumps(items,ensure_ascii=False,indent=2)+marker+"\n\nexport const tuTienKyReferences = "+json.dumps(refs,ensure_ascii=False,indent=2)+marker+"\n",encoding="utf-8")
    return len(items)


def publish_guides():
    docs = [
        ("spirit-mines", "Linh Tuyền và mỏ tự nhiên", "SPIRIT_MINES_VI.md"),
        ("garden", "Dụng cụ hái, hồ cá và cây trồng", "GARDEN_EXPANSION_VI.md"),
        ("armor", "Bộ giáp và Vân Mạc Thượng Trang", "ARMOR_SET_VI.md"),
        ("rewards", "Máy Quay Thưởng · Bảng thưởng", "CHOUJIANGJI_REWARDS.md"),
        ("herbs", "Ngọc Lộ, linh thảo và hạt giống", "BATCH19_HERBS_VI.md"),
        ("houses", "Sào huyệt, thú nuôi và Thiên Cơ Ốc", "BATCH19_HOUSES_VI.md"),
        ("structures", "Kho, hoa và công trình", "BATCH19_MISC_VI.md"),
        ("solo", "Solo tích hợp · Thế giới và save", "SOLO_INTEGRATION_VI.md"),
    ]
    guides = [{"id": "utilities", "title": "Tiện ích đã tích hợp", "source": "mods/PhamNhanTuTien/main", "text": "# Tiện ích Phàm Nhân\n\n- Túi đồ mặc định 45 ô; có lựa chọn 15 hoặc 25 ô trong Config.\n- Những vật phẩm có thể xếp chồng được tăng giới hạn lên 120.\n- Nhấn G để sắp xếp túi đồ.\n- Mở quà ở mọi nơi, không cần đứng cạnh Máy Khoa Học.\n- Cỏ không biến thành Grass Gekko.\n- Máy Phóng Băng thông minh giữ lửa trại và các bếp Vĩnh Hằng Thần Hỏa, dùng dung lượng nhiên liệu chuẩn.\n- HUD chiến đấu đã tích hợp; xem Config để tra các lựa chọn thanh máu và số sát thương.\n\nCác tiện ích cố định như stack 120, mở quà và ngăn Grass Gekko không có nút bật/tắt riêng trong Config hiện tại."}]
    for key,title,filename in docs:
        text = (MOD/filename).read_text(encoding="utf-8-sig")
        text = re.split(r"(?m)^## (?:Kiểm tra|Kiểm chứng|Nguồn và kiểm tra|Nguồn|Tài nguyên|Đối chiếu|Kiểm thử)",text)[0]
        text = re.sub(r"(?ms)^### Hình ảnh mới.*?(?=^### |^## |\Z)","",text)
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)","",text)
        guides.append({"id":key,"title":title,"source":"mods/PhamNhanTuTien/"+filename,"text":text.strip()})
    guides.extend(json.loads((ROOT/"app/data/pham-nhan-book.json").read_text(encoding="utf-8")))
    (ROOT/"app/data/pham-nhan-guides.json").write_text(json.dumps(guides,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


if __name__ == "__main__":
    configs = publish_config()
    items = publish_catalog()
    publish_guides()
    print(f"Published {items} entries, {configs} configuration options and 9 guides.")
