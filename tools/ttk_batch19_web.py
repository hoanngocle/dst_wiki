"""Curated batch-18 records and native output references for Tu Tien Ky."""
import json


def populate(root, original, add, product, by_code):
    # These vanilla farm seeds exist in DST but were omitted from the old wiki index.
    for code, name in {
        "asparagus_seeds": "Hạt Măng Tây", "garlic_seeds": "Hạt Tỏi",
        "pepper_seeds": "Hạt Ớt", "pumpkin_seeds": "Hạt Bí Ngô",
        "tomato_seeds": "Hạt Cà Chua",
    }.items():
        original.setdefault(code, dict(id="base_game:" + code, prefabId=code,
            namespace="base_game", category="item", name=name,
            description="Hạt cây trồng gốc DST; dùng trồng rau hoặc chuyển hóa thành hạt linh thảo.",
            sprite=None, recipe=None))
    rows = []
    for group in ["misc", "herbs", "houses"]:
        path = root / f"tools/ttk_batch19_{group}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        rows.extend(data if isinstance(data, list) else data["records"])
    rows = [row for row in rows if row.get("category") != "skin"]
    for row in rows:
        category = row.get("category", "item")
        category = {"creature": "mob", "room": "structure", "room_piece": "other"}.get(category, category)
        add(row["id"], row["name"], category, row["description"],
            row.get("recipe"), row.get("station"), row.get("effects", []), row.get("source"))
    for row in rows:
        for edge in row.get("products", []):
            product(row["id"], edge["id"], str(edge["quantity"]), edge["conditions"])

    dishes = json.loads((root / "tools/ttk_batch19_spiced_refs.json").read_text(encoding="utf-8"))
    for dish in dishes:
        code = dish["prefabId"]
        original[code] = dict(
            id="base_game:" + code, prefabId=code, namespace="base_game", category="item",
            name=dish["name"], description="Món ăn gốc DST đã nêm gia vị; giữ tác dụng của món ăn và gia vị tương ứng.",
            sprite=original.get(dish["base"], {}).get("sprite"), recipe=None,
            craftingNote="Nêm món ăn với gia vị tại Vân Yên Hương Liệu Trạm.",
        )
        product("ttk_qwsk", code, "1–2", "Một loại được chọn ngẫu nhiên mỗi ngày trong danh sách món đã nêm gia vị gốc DST.")
        if dish["base"] != "wetgoop":
            product("ttk_yunxiao_portable_spicer", code, "1 mỗi cặp", "1 phần " + dish["name"].split(" · ")[0] + " + 1 gia vị " + dish["name"].split(" · ")[-1] + "; xử lý tối đa 120 cặp/mẻ.")
