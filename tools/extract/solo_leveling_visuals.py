"""Resolve actual local inventory/portrait atlas elements for the Solo wiki."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from tools.extract.assets import parse_atlas


def mod_sprites(root: Path) -> tuple[dict, dict]:
    elements, textures = {}, {}
    for path in sorted((root / 'images').rglob('*.xml')):
        relative = path.relative_to(root).as_posix()
        # Ground animations, minimap markers and UI backgrounds are not item icons.
        if any(part in relative for part in ('/minimap/', '/fx/', '_ground', 'background', '/de_tu_skill_icon/')):
            continue
        atlas = parse_atlas(path)
        texture = path.parent / atlas.texture
        if not texture.is_file():
            continue
        source = '/solo-leveling/icons/' + hashlib.sha256(texture.read_bytes()).hexdigest() + '.png'
        textures[source] = texture
        for name, uv in atlas.elements.items():
            key = name.removesuffix('.tex')
            sprite = {'src': source, 'uv': dict(zip(('u1', 'u2', 'v1', 'v2'), uv))}
            elements.setdefault(key, sprite)
    sprites = dict(elements)
    # Standard inventory element naming is also used by potions and QoL items.
    for key, sprite in elements.items():
        if key.endswith('_inventory'):
            sprites[key.removesuffix('_inventory')] = sprite
    aliases = {
        'hh_effect_tally': 'giay_thuoc_tinh_inventory',
        'hh_remove_stone': 'luc_bao_thach_inventory',
        'hh_essence': 'linh_thach_inventory',
        'wb_enhancegem': 'da_cuong_hoa_inventory',
        'hh_effect_stone': 'dyc_gem_purple',
        'nn_magicpaper': 'bua_ma_thuat_inventory',
        'wb_strengthen_strengthen_protectpaper': 'bua_bao_ve_inventory',
        'hh_cat_box': 'tui_meo_inventory', 'hh_duck_box': 'tui_vit_inventory',
        'hh_treasure_tally_a': 'tam_bao_quyen_truc_inventory',
        'hh_treasure_tally_b': 'tam_bao_quyen_truc_inventory',
        'hh_treasure_tally': 'tam_bao_quyen_truc_inventory',
        'hh_van_nang_trao': 'nn_tools', 'hh_daogam6': 'hh_daogam6_sword',
        'hh_lo_ren': 'lo_ren',
        'nn_liquidluck': 'phuc_lac_duoc_1_inventory',
        'nn_liquidluck_2': 'phuc_lac_duoc_2_inventory',
        'nn_liquidluck_3': 'phuc_lac_duoc_3_inventory',
        'hh_igris_shadow': 'igris_icon', 'hh_beru_shadow': 'beru_icon',
        'hh_fruitfly_shadow': 'fruitfly_icon', 'hh_macanh_shadow': 'mac_anh_icon',
        'hh_hacanh_shadow': 'hac_anh_icon', 'hh_monarch_storage_container': 'kho_quan_vuong_icon',
    }
    for prefab, element in aliases.items():
        if element in elements:
            sprites[prefab] = elements[element]
    return sprites, textures


def enrich_entries(groups: list[dict], sprites: dict, names: dict):
    by_title = {name.casefold(): prefab for prefab, name in names.items()}
    for group in groups:
        for row in group['entries']:
            if group['id'] in ('guild', 'exams'):
                rank = next((line for line in row['lines'] if line.startswith('Rank: ')), None)
                if rank:
                    row['category'] = rank.replace(':', '')
            if group['id'] == 'effects':
                row['category'] = 'Đá thuộc tính' if row['id'].startswith('enchant-') else 'Mẫu mô tả hiệu ứng'
            if group['id'] == 'config':
                row['category'] = 'Tùy chọn mod' if row['id'].startswith('setting-') else 'Thông số trò chơi'
            row.setdefault('category', group['title'])
            prefab = row.get('visual_prefab')
            if not prefab:
                match = re.search(r'(?:Prefab sản phẩm|Prefab vật phẩm|Prefab):\s*([a-z_0-9]+)', '\n'.join(row['lines']))
                prefab = match[1] if match else by_title.get(row['title'].casefold())
            if group['id'] == 'shadows':
                prefab = row['id'].removeprefix('shadows-')
            row['sprite'] = sprites.get(prefab)
            if row.get('recipe'):
                row['sprite'] = sprites.get(row['recipe']['prefab'])
                for ingredient in row['recipe']['ingredients']:
                    ingredient['sprite'] = sprites.get(ingredient['prefab'])
            targets = next((line.split(': ', 1)[1] for line in row['lines'] if line.startswith('Mục tiêu hợp lệ: ')), '')
            related = []
            for target in targets.split(', '):
                if target in sprites and len(related) < 6:
                    related.append({'prefab': target, 'name': names.get(target, target), 'sprite': sprites[target]})
            if related:
                row['related'] = related
