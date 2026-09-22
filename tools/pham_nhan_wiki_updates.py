"""Current gameplay records, sourced from the integrated mod's definitions."""
from lupa.luajit21 import LuaRuntime


def refresh_current_content(mod, items, by_code, add):
    lua = LuaRuntime()
    defs = lua.execute((mod/"scripts/ttk_boss_defs.lua").read_text(encoding="utf-8"))
    stats = {"trueDamageNum": "sát thương chuẩn", "health": "máu tối đa", "mana": "mana tối đa", "hunger": "độ no tối đa", "sanity": "tinh thần tối đa", "reduceAttackedDamage": "giảm sát thương nhận vào dạng cố định"}
    effects = {"criticalHitRate": "+10 điểm phần trăm tỷ lệ chí mạng", "immuneHot": "miễn sát thương do quá nóng", "immuneCold": "miễn sát thương do quá lạnh", "immunePoison": "miễn độc theo hệ Solo", "immunitySleep": "miễn bị cưỡng ép ngủ", "immuneFreeze": "miễn đóng băng"}
    for index in range(1, len(defs.order)+1):
        boss = defs.bosses[defs.order[index]]
        description = ("Boss duy nhất: không sinh lại sau cái chết cuối cùng, không có vật phẩm triệu hồi. Rơi 10 Cực Phẩm, 100 Thượng Phẩm; 10 mỗi ngọc đỏ/xanh dương/tím, 5 mỗi ngọc vàng/cam/lục." if boss.unique else "Boss đánh lại được. Cái chết cuối cùng rơi 1 linh vật, 1 vật phẩm triệu hồi tương ứng và 2–5 Thượng Phẩm Linh Thạch.")
        add(boss.prefab, boss.name, "boss", description+" Sinh trên đất liền của thế giới chính; phân thân và chuyển pha không trả thưởng chính. Xem Hướng dẫn để tra chiến lợi phẩm bổ sung.", source="BOSS_DROPS_VI.md")
        if not boss.unique:
            add(boss.food, boss.food_name, "item", f"Ăn tăng {boss.gain:g} {stats[boss.stat]}, tối đa 10 lần mỗi nhân vật. Đủ 10 lần: {effects[boss.effect]}. Mỗi lần ăn hồi cơ bản 50 máu, 75 độ no và 50 tinh thần; từ lần 11 không tăng thêm chỉ số. Rơi từ {boss.name}.", source="BOSSES_VI.md")
            add(boss.summon, boss.summon_name, "item", "Dùng từ túi trên đất liền để triệu hồi "+boss.name+" khi boss cùng loại đã chết. Không dùng trong hang, trên thuyền hoặc Thiên Cơ Ốc; dùng thất bại không mất vật phẩm.", source="BOSSES_VI.md")
            by_code[boss.prefab]["products"] = [{"item": {k: by_code[code][k] for k in ["id","name","sprite"]}, "quantity":"1", "conditions":"Chắc chắn rơi khi boss chính chết ở pha cuối."} for code in [boss.food,boss.summon]]
    for code,name,description in [
        ("ttk_boss_back_xh","Ba Lô Tiên Hà","Túi 18 ô (3 cột × 6 hàng), dùng ô ba lô riêng. Không có giáp, bảo quản hay tăng tốc; không xếp chồng hoặc cất vào túi/rương khác. Thanh Tụ Đan Tiên chắc chắn rơi 1 chiếc."),
        ("ttk_boss_zcmy","Tử Thần Ma Ngọc","Tử Vân Ma Quân chắc chắn rơi 1 viên. Nguyên liệu chế Tử Xá Diện Giáp sau khi học bản vẽ."),
        ("ttk_boss_mgqg","Ma Cốt","Ma Tướng Phù Đồ chắc chắn rơi 1 món. Nguyên liệu chế Tà Sát Hộ Giáp sau khi học bản vẽ."),
        ("ttk_boss_zcyseed","Hạt Tử Chi","Thanh Tụ Đan Tiên rơi chắc chắn 2 hạt. Trồng trực tiếp trên đất: 50% cây xanh, 50% cây tím. Ăn hồi 5 máu, 12 độ no, 2 tinh thần; hạt có hạn sử dụng. Cây lớn chặt được 3 gỗ, 2 hạt và 17% cơ hội 1 Gỗ Sống."),
        ("ttk_zcmj_blueprint","Bản Vẽ Tử Xá Diện Giáp","Chắc chắn rơi từ Tử Vân Ma Quân ở pha cuối. Học để mở công thức Tử Xá Diện Giáp."),
        ("ttk_xshj_blueprint","Bản Vẽ Tà Sát Hộ Giáp","Chắc chắn rơi từ Ma Tướng Phù Đồ. Học để mở công thức Tà Sát Hộ Giáp."),
    ]:
        add(code,name,"item",description,source="BOSS_DROPS_VI.md")
    for code,recipe in [("ttk_zcmj",[("ttk_boss_zcmy",1),("purplegem",2),("yellowgem",2),("ttk_lingshi3",1)]),("ttk_xshj",[("ttk_boss_mgqg",1),("armor_skeleton",1),("orangegem",2),("greengem",2)])]:
        old=by_code[code]
        add(code,old["name"],"item",old["description"],recipe,"Phải học bản vẽ tương ứng; sau đó không cần trạm chế tạo.","ARMOR_SET_VI.md")
    items[:] = [item for item in items if item["prefabId"] != "calliope_mori"]
    add("eva","EVA","character","Nhân vật đã tích hợp trong Phàm Nhân 2.0.3, một ngoại hình mặc định, dùng cho world mới. Hồn Lực và kỹ năng mở theo cấp 10/20/30/50/100. EVA dùng chung cấp nhân vật hh_leveling đã tích hợp trong Phàm Nhân. Tắt mod EVA độc lập khi dùng bản tích hợp.",source="EVA_INTEGRATION_VI.md")
    tool=by_code.get("ttk_yhsyz")
    if tool:
        description="Hái linh thảo bằng dụng cụ còn độ bền: 75% cơ hội nhận hạt; khi có hạt, 75% nhận 1 và 25% nhận 2 hạt cùng loại. Tốn 1 độ bền; vẫn nhận 1 linh thảo. Hái tay: 40% nhận 1 hạt."
        tool["description"]=description
        tool["details"]["usage"]["effects"]=[{"trigger":"Thu hoạch", "text":description,"evidence":[{"source":"Phàm Nhân Tu Tiên 2.0.3","locator":"mods/PhamNhanTuTien/SEED_TREE_VI.md"}]}]
