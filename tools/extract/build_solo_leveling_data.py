"""Publish the local Solo Leveling manual and static Lua definitions, without running Lua.

Run: python -m tools.extract.build_solo_leveling_data
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import zipfile
from pathlib import Path

from tools.extract.lua_strings import decode_lua_string_literal
from tools.extract.solo_leveling_visuals import mod_sprites, enrich_entries

TOKEN = re.compile(r'--\[(=*)\[.*?\]\1\]|--[^\n]*|\[(=*)\[.*?\]\2\]|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[A-Za-z_][\w]*|(?:\d+\.\d*|\.\d+|\d+)|\s+|.', re.S)


def tokens(text: str) -> list[str]:
    return [m.group() for m in TOKEN.finditer(text) if not m.group().isspace() and not m.group().startswith('--')]


def split_fields(parts: list[str]) -> list[list[str]]:
    result, current = [], []
    nesting, blocks = 0, 0
    for token in parts:
        if token in ('{', '(', '['):
            nesting += 1
        elif token in ('}', ')', ']'):
            nesting -= 1
        elif token in ('function', 'if', 'for', 'while', 'repeat'):
            blocks += 1
        elif token in ('end', 'until'):
            blocks -= 1
        if token in (',', ';') and nesting == 0 and blocks == 0:
            if current:
                result.append(current)
            current = []
        else:
            current.append(token)
    if current:
        result.append(current)
    return result


def scalar(parts: list[str], context: dict | None = None):
    if not parts:
        return None
    expression = ''.join(parts)
    if parts[0] == '{' and parts[-1] == '}':
        return parse_table(expression, context)
    if 'function' in parts:
        return None
    if len(parts) == 1 and parts[0][0] in ('"', "'"):
        return decode_lua_string_literal(parts[0])
    if len(parts) == 1 and re.match(r'^\[(=*)\[', parts[0]):
        match = re.match(r'^\[(=*)\[(.*?)\]\1\]$', parts[0], re.S)
        return match[2] if match else None
    if re.fullmatch(r'(?:M\.)?RANK\.[EDCBAS]', expression):
        return expression[-1]
    if context is not None and re.fullmatch(r'TUNING(?:\["[^"]+"\]|\.[A-Za-z_]\w*)+', expression):
        value = context
        for quoted, dotted in re.findall(r'\["([^"]+)"\]|\.([A-Za-z_]\w*)', expression):
            value = value.get(quoted or dotted) if isinstance(value, dict) else None
        return value
    # Only arithmetic/boolean literals are evaluated. No calls, attributes or names.
    translated = ' '.join({'true': 'True', 'false': 'False', 'nil': 'None'}.get(p, p) for p in parts).replace('~ =', '!=').replace('= =', '==').replace('< =', '<=').replace('> =', '>=')
    try:
        tree = ast.parse(translated, mode='eval')
        allowed = (ast.Expression, ast.Constant, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare,
                   ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.USub, ast.UAdd,
                   ast.And, ast.Or, ast.Not, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)
        if all(isinstance(node, allowed) for node in ast.walk(tree)):
            return eval(compile(tree, '<lua literals>', 'eval'), {'__builtins__': {}})
    except (SyntaxError, ValueError, TypeError, ZeroDivisionError, OverflowError):
        pass
    return None


def parse_table(text: str, context: dict | None = None) -> dict:
    result, index = {}, 1
    for field in split_fields(tokens(text)[1:-1]):
        if not field:
            continue
        if field[0] == '[' and len(field) > 3 and field[2:4] == [']', '=']:
            key, value = scalar([field[1]]), scalar(field[4:], context)
        elif len(field) > 1 and field[1] == '=':
            key, value = field[0], scalar(field[2:], context)
        else:
            key, value = str(index), scalar(field, context)
            index += 1
        if key is not None and value is not None:
            result[str(key)] = value
    return result


def balanced(text: str, start: int, opening='{', closing='}') -> str:
    depth = 0
    for token in TOKEN.finditer(text, start):
        if token.group() == opening:
            depth += 1
        elif token.group() == closing:
            depth -= 1
            if depth == 0:
                return text[start:token.end()]
    raise ValueError('Unclosed source block')


def table_at(text: str, pattern: str) -> dict:
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f'Missing source table: {pattern}')
    return parse_table(balanced(text, text.index('{', match.start())))


def tuning_tables(text: str, context: dict, *, top_level_only: bool = False) -> dict:
    """Fold literal assignments and the mod's two explicit EXP remapping loops in order."""
    path_pattern = r'(?:\[\s*["\'][^"\']+["\']\s*\]|\.[A-Za-z_]\w*)+'
    operations = []
    # Conditional configuration branches are alternatives, not sequential overrides.
    # Keep the declared defaults rather than interpreting server-dependent conditions.
    nested_spans = []
    block_start, depth = 0, 0
    if top_level_only:
        for token in TOKEN.finditer(text):
            if token.group() in ('function', 'if', 'for', 'while', 'repeat'):
                if depth == 0:
                    block_start = token.start()
                depth += 1
            elif token.group() in ('end', 'until'):
                depth -= 1
                if depth == 0:
                    nested_spans.append((block_start, token.end()))
    for match in re.finditer(r'TUNING(?P<path>' + path_pattern + r')\s*=\s*', text):
        if any(start <= match.start() < end for start, end in nested_spans):
            continue
        keys = [quoted or dotted for quoted, dotted in re.findall(r'\[\s*["\']([^"\']+)["\']\s*\]|\.([A-Za-z_]\w*)', match['path'])]
        rest = text[match.end():]
        default = re.match(r'TUNING' + path_pattern + r'\s+or\s*', rest)
        start = match.end() + (default.end() if default else 0)
        if text[start:start + 1] == '{':
            value = balanced(text, start)
        else:
            expression = text[start:].split('\n', 1)[0].split('--', 1)[0].strip()
            value = expression
        operations.append((match.start(), 'assign', keys, value))
    loop_pattern = r'for prefab, exp in pairs\(TUNING\["([^"]+)"\]\) do\s*TUNING\["([^"]+)"\]\[prefab\]\s*=\s*(.*?)\bend\b'
    for match in ([] if top_level_only else re.finditer(loop_pattern, text, re.S)):
        operations.append((match.start(), 'remap', [match[1], match[2]], match[3]))
    result = {}
    for _, operation, keys, value in sorted(operations, key=lambda item: item[0]):
        if operation == 'remap':
            source, target = keys
            mapped = {key: scalar([str(exp) if token == 'exp' else token for token in tokens(value)]) for key, exp in context[source].items()}
            if any(v is None for v in mapped.values()):
                raise ValueError('Unsupported EXP remapping expression')
            context[target] = mapped
            result[target] = mapped
        else:
            value = scalar(tokens(value), context)
            if value is None:
                continue
            current = context
            for key in keys[:-1]:
                current = current.setdefault(key, {})
            current[keys[-1]] = value
            result[keys[0]] = context[keys[0]]
    return result


def entry(id: str, title: str, lines: list[str], source: str, tables=None) -> dict:
    return {'id': id, 'title': title, 'lines': lines, 'tables': tables or [], 'source': source}


def group(id: str, title: str, description: str, entries: list[dict]) -> dict:
    return {'id': id, 'title': title, 'description': description, 'entries': entries}


LABELS = {
    'rank': 'Rank', 'target': 'Mục tiêu', 'reward_credit': 'Xu Hiệp Hội',
    'duration_days': 'Thời hạn (ngày)', 'duration': 'Hiệu lực (giây)',
    'price': 'Giá', 'stock': 'Số lượt mua', 'amount': 'Số lượng', 'level': 'Level',
    'role': 'Vai trò', 'exp_kind': 'Hoạt động nhận EXP', 'prefab': 'Prefab', 'prefab_id': 'Prefab vật phẩm',
    'min': 'Tối thiểu', 'max': 'Tối đa', 'can_add': 'Có thể ép', 'only_one': 'Mỗi trang bị chỉ ép một lần',
    'check_desc': 'Trang bị áp dụng', 'value_range': 'Khoảng giá trị', 'only_compound': 'Chỉ từ ngẫu luyện / siêu boss',
    'ui_from_desc': 'Nguồn nhận', 'reward_items': 'Vật phẩm thưởng', 'talents': 'Kỹ năng theo cấp',
    'category': 'Nhóm', 'reward_exp': 'EXP thưởng', 'require_rank': 'Rank yêu cầu',
    'requirements': 'Vật phẩm giao nộp', 'options': 'Lựa chọn', 'data': 'Giá trị',
    'prefabs': 'Mục tiêu cụ thể', 'distinct': 'Phải khác loại', 'buff_duration': 'Hiệu lực (giây)',
    'hungervalue': 'Độ No', 'healthvalue': 'Máu', 'sanityvalue': 'Tinh thần',
}


def describe(value) -> str:
    if isinstance(value, dict):
        if 'prefab' in value:
            return f"{value.get('amount', 1)} × {value['prefab']}"
        return '; '.join(f'{LABELS.get(k, k)}: {describe(v)}' if not k.isdigit() else describe(v) for k, v in value.items())
    if isinstance(value, bool):
        return 'Có' if value else 'Không'
    return str(value)


def records(table: dict, prefix: str, source: str) -> list[dict]:
    output = []
    for key, value in table.items():
        if not isinstance(value, dict):
            continue
        title = value.get('title', value.get('name', value.get('date')))
        if title:
            lines = [str(value[k]) for k in ('description', 'desc') if k in value]
            lines += [f'{LABELS[k]}: {describe(value[k])}' for k in LABELS if k in value]
            row = entry(f'{prefix}-{value.get("id", key)}', str(title), lines, source)
            if value.get('rank'):
                row['rank'] = value['rank']
            if value.get('prefab_id') or value.get('prefab'):
                row['visual_prefab'] = value.get('prefab_id', value.get('prefab'))
            if value.get('category'):
                row['category'] = {'player_potion': 'Thuốc thợ săn', 'disciple_potion': 'Thuốc đệ tử', 'weapon': 'Vũ khí', 'qol': 'Vật phẩm tiện ích'}.get(value['category'], value['category'])
            if isinstance(value.get('talents'), dict):
                row['talents'] = list(value['talents'].values())
            output.append(row)
        else:
            output += records(value, f'{prefix}-{key}', source)
    return output


def wiki_entries(text: str) -> list[dict]:
    output, current, table = [], None, None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith('[IMG') or line in ('[ITEM]', '[/ITEM]', '[BOSS]', '[/BOSS]'):
            continue
        if line.startswith('=='):
            title = line.strip('=- ').strip()
            current = entry(f'wiki-{len(output)}', title, [], 'Wiki.txt')
            output.append(current)
        elif line.startswith('[NAME:'):
            current = entry(f'wiki-{len(output)}', line[6:-1], [], 'Wiki.txt')
            output.append(current)
        elif line == '[TABLE]':
            table = {'headers': [], 'rows': []}
            current['tables'].append(table)
        elif line.startswith('[HEADER]'):
            table['headers'] = line[8:-9].split('|')
        elif line.startswith('[ROW]'):
            table['rows'].append(line[5:-6].split('|'))
        elif line == '[/TABLE]':
            table = None
        else:
            if current is None:
                current = entry('wiki-start', 'Wiki', [], 'Wiki.txt')
                output.append(current)
            current['lines'].append(line)
    return output


def shop_sprites(workspace: Path) -> dict:
    """Reuse published inventory/wiki images; explicit aliases preserve real prefabs."""
    catalogue = json.loads((workspace / 'public/data/items.json').read_text(encoding='utf-8'))['items']
    sprites = {item['prefabId']: item['sprite'] for item in catalogue
               if item['namespace'] == 'base_game' and item.get('sprite')}
    by_name = {item.get('englishName'): item['sprite'] for item in catalogue if item.get('sprite')}
    aliases = {
        'armorwood': 'Log Suit', 'footballhat': 'Football Helmet', 'berries': 'Berries',
        'strawhat': 'Straw Hat', 'manure': 'Manure', 'meatballs': 'Meatballs', 'perogies': 'Pierogi',
        'armorruins': 'Thulecite Suit', 'ruinshat': 'Thulecite Crown', 'icestaff': 'Ice Staff',
        'firestaff': 'Fire Staff', 'orangestaff': 'The Lazy Explorer', 'greenstaff': 'Deconstruction Staff',
        'dreadstonehat': 'Dreadstone Helm', 'armorwagpunk': 'W.A.R.B.I.S. Armor',
        'vegstinger': 'Vegetable Stinger',
    }
    for prefab, name in aliases.items():
        if name in by_name:
            sprites[prefab] = by_name[name]
    # This local wiki image is published outside the item catalogue.
    staff_page = workspace / 'public/data/wiki/pages/142914.json'
    if staff_page.is_file():
        for image in json.loads(staff_page.read_text(encoding='utf-8')).get('images', []):
            if image['title'] == "File:Star Caller's Staff.png":
                sprites['yellowstaff'] = {'src': image['src'], 'uv': {'u1': 0, 'u2': 1, 'v1': 0, 'v2': 1}}
    return sprites


def curate_items(rows: list[dict]) -> list[dict]:
    """Keep player-facing entries; hide internal helpers and consolidate aliases."""
    internal = {
        'hh_ui_container', 'hh_forge_container', 'hh_monarch_storage_container',
        'hh_true_damage', 'hh_bramble_damage', 'hh_poison', 'hh_monster_kj',
        'hh_turret', 'hh_turret_ice', 'hh_turret_fire', 'hh_turret_poison',
        'hh_arena_lava_pond', 'hh_arena_lava_pond_rock', 'lava_pond', 'lava_pond_rock',
        # These companions have their own complete progression/talent tab.
        'hh_igris_shadow', 'hh_beru_shadow', 'hh_fruitfly_shadow',
        'hh_treasure_tally_a_blueprint', 'hh_treasure_tally_b_blueprint',
        'hh_treasure_tally_b',
    }
    output = []
    for row in rows:
        prefab = row['id'].removeprefix('item-')
        if prefab in internal or prefab.startswith('hh_daogam6_'):
            continue
        if prefab == 'hh_treasure_tally_a':
            row['lines'] = [line for line in row['lines'] if not line.startswith('Prefab:')]
            row['lines'] += ['Có hai công thức chế tạo thay thế nhau; xem tab Chế tạo & dung hợp.', 'Prefab: hh_treasure_tally']
            row['visual_prefab'] = 'hh_treasure_tally'
        elif prefab == 'hh_daogam6':
            row['title'] = 'Tà Thuật Đen'
            row['lines'].insert(1, 'Các dạng biến đổi: Kiếm, Rìu, Cuốc, Cúp và Xẻng.')
        # Remove name-only flavour duplicates, without discarding useful descriptions.
        row['lines'] = [line for line in row['lines'] if line != row['title']]
        output.append(row)
    return output


def build_data(root: Path) -> dict:
    def read(path):
        return (root / path).read_text(encoding='utf-8-sig')
    tuning = read('main/hh_tunning.lua')
    ui = table_at(tuning, r'TUNING\["HH_UI_TEXT"\]\s*=')
    format_config = table_at(tuning, r'TUNING\["HH_FORMAT_CONFIG"\]\s*=')
    groups = []
    help_text = read('scripts/widgets/hh_help_ui.lua')
    help_start = re.search(r'function [^\n]+:CreateSoloLevelingUi\(\)', help_text).end()
    help_block = re.search(r'local _text_list\s*=\s*\{', help_text[help_start:])
    solo_help = balanced(help_text, help_text.index('{', help_start + help_block.start()))
    guide = []
    current = None
    for literal in re.findall(r'\["str"\]\s*=\s*("(?:\\.|[^"\\])*")', solo_help):
        line = decode_lua_string_literal(literal).strip()
        if not line:
            continue
        if line.startswith('---'):
            current = entry(f'guide-{len(guide)}', line.strip('-[] '), [], 'scripts/widgets/hh_help_ui.lua')
            guide.append(current)
        elif current:
            if not line.startswith('•') and current['lines']:
                current['lines'][-1] += ' ' + line
            else:
                current['lines'].append(line)
    for key, value in ui['MOD_INFO'].items():
        if isinstance(value, str):
            titles = {'mod_role_1': 'Giới thiệu', 'mod_role_2': 'Lối chơi', 'monster': 'Hệ thống quái vật',
                      'conflict': 'Tương thích & lỗi đã biết', 'respect': 'Mod khuyến nghị', 'qq_str': 'Tác giả & cộng đồng'}
            guide.append(entry(f'info-{key}', titles.get(key, key), value.splitlines(), 'main/hh_tunning.lua'))
        elif isinstance(value, dict):
            guide += records(value, f'updates-{key}', 'main/hh_tunning.lua')
    for key, value in ui['UI_ITEMS'].items():
        titles = {'ui_role_1': 'Đạo cụ: đục lỗ, tháo, đặt lại & thanh tẩy', 'ui_role_2': 'Châu báu thường',
                  'ui_role_3': 'Châu báu theo mục tiêu & follower', 'ui_role_4': 'Châu báu hiếm & siêu hiếm',
                  'ui_role_5': 'Cách nhận đạo cụ & châu báu', 'ui_role_6': 'Cách dùng Quạt Lông Vũ', 'ui_role_7': 'Quạt Lông Vũ: châu báu hiếm'}
        guide.append(entry(f'gem-guide-{key}', titles[key], value.splitlines(), 'main/hh_tunning.lua'))
    guide += records(ui['UPDATE_VISION'], 'enhancement-guide', 'main/hh_tunning.lua')
    groups.append(group('guide', 'Hướng dẫn', 'Hầm ngục, kỹ năng, trích xuất, hiệp hội, cường hoá và khảm nạm.', guide))
    groups.append(group('wiki', 'Wiki', 'Toàn bộ văn bản và bảng trong Wiki.txt, giữ nguyên thông tin của tài liệu gốc.', wiki_entries(read('Wiki.txt'))))

    names = {}
    items = table_at(read('main/hh_string.lua'), r'local items\s*=')
    for key, value in items.items():
        if isinstance(value, dict) and '1' in value:
            names[key] = value['1']
    names.update({'marble': 'Đá cẩm thạch', 'cutstone': 'Đá cắt', 'cutgrass': 'Cỏ', 'twigs': 'Cành cây',
                  'rocks': 'Đá', 'goldnugget': 'Vàng', 'nightmarefuel': 'Nhiên liệu ác mộng', 'opalpreciousgem': 'Iridescent Gem',
                  'purplegem': 'Ngọc tím', 'orangegem': 'Ngọc cam', 'yellowgem': 'Ngọc Vàng', 'vegstinger': 'Vegetable Stinger',
                  'stinger': 'Nọc ong', 'silk': 'Tơ nhện', 'spidergland': 'Tuyến nhện', 'coontail': 'Đuôi mèo', 'goose_feather': 'Lông ngỗng',
                  'wb_enhancegem': 'Đá Cường Hoá', 'nn_liquidluck': 'Phúc Lạc Dược', 'nn_magicpaper': 'Bùa Ma Thuật',
                  'wb_strengthen_strengthen_protectpaper': 'Bùa Bảo Vệ', 'hh_cat_box': 'Túi Mèo', 'hh_duck_box': 'Túi Vịt'})
    names['hh_lo_ren'] = 'Lò Rèn'
    recipes = []
    source = read('main/hh_recipe.lua')
    for match in re.finditer(r'\bAddRecipe(?:2)?\s*\(', source):
        call = balanced(source, source.index('(', match.start()), '(', ')')
        fields = split_fields(tokens(call)[1:-1])
        id = scalar(fields[0])
        if not id:
            raise ValueError('Non-literal recipe identifier')
        ingredients = re.findall(r'Ingredient\(\s*"([^"]+)"\s*,\s*(\d+)', call)
        tech = re.search(r'TECH\["([^"]+)"\]', call)[1]
        product_match = re.search(r'\["product"\]\s*=\s*"([^"]+)"', call)
        product = product_match[1] if product_match else id
        num = re.search(r'\["numtogive"\]\s*=\s*(\d+)', call)
        amount = int(num[1]) if num else 1
        lines = [f'{count} × {names.get(prefab, prefab)} ({prefab})' for prefab, count in ingredients]
        lines += [f'Nhận được: {amount} × {names.get(id, id)}',
                  'Chế tạo tại: ' + {'NONE': 'Không cần máy', 'MAGIC_THREE': 'Máy Ma Thuật cấp 2 (Shadow Manipulator)',
                                    'hh_lo_ren_ONE': 'Lò Rèn', 'SCIENCE_TWO': 'Máy Khoa Học cấp 2 (Alchemy Engine)'}[tech],
                  f'Prefab sản phẩm: {product}']
        row = entry(f'recipe-{id}', names.get(id, id), lines, 'main/hh_recipe.lua')
        row['recipe'] = {'prefab': product, 'amount': amount, 'station': lines[-2].removeprefix('Chế tạo tại: '),
                         'ingredients': [{'prefab': p, 'name': names.get(p, p), 'amount': int(n)} for p, n in ingredients]}
        row['category'] = row['recipe']['station']
        recipes.append(row)
    recipes += [entry('fusion-2', 'Dung hợp Phúc Lạc Dược II', ['3 × Phúc Lạc Dược I', '1 × Pure Brilliance', 'Dung hợp tại Máy Ma Thuật cấp 2.'], 'Wiki.txt'),
                entry('fusion-3', 'Dung hợp Phúc Lạc Dược III', ['3 × Phúc Lạc Dược II', '2 × Pure Brilliance', 'Dung hợp tại Máy Ma Thuật cấp 2.'], 'Wiki.txt'),
                entry('recipe-differences', 'Đối chiếu tài liệu & công thức hiện tại', ['Hắc Nguyệt Hồ: mã công thức dùng 10 Đá cẩm thạch (marble); Wiki.txt ghi 10 Thạch anh.',
                    'Tầm Bảo Quyển Trục có hai công thức riêng: 40 Nọc ong HOẶC 40 Tơ nhện + 20 Tuyến nhện.',
                    'Phúc Lạc Dược II có hiệu lực 90 giây trong mã mod; Wiki.txt ghi 60 giây ở mục vật phẩm và 90 giây ở mục cường hoá.'], 'main/hh_recipe.lua; scripts/prefabs/wb_strengthen_food.lua; Wiki.txt')]
    groups.append(group('crafting', 'Chế tạo & dung hợp', 'Nguyên liệu, số lượng sản phẩm và máy chế tạo, đối chiếu với mã mod hiện tại.', recipes))
    for level, ingredient, brilliance in ((2, 'nn_liquidluck', 1), (3, 'nn_liquidluck_2', 2)):
        row = next(r for r in recipes if r['id'] == f'fusion-{level}')
        row['recipe'] = {'prefab': f'nn_liquidluck_{level}', 'amount': 1, 'station': 'Máy Ma Thuật cấp 2 (Shadow Manipulator)',
                         'ingredients': [{'prefab': ingredient, 'name': f'Phúc Lạc Dược {"I" if level == 2 else "II"}', 'amount': 3},
                                         {'prefab': 'purebrilliance', 'name': 'Pure Brilliance', 'amount': brilliance}]}
        row['category'] = 'Dung hợp'

    quest_source = 'scripts/quests/hh_daily_quest_defs.lua'
    quest_text = read(quest_source)
    quests = table_at(quest_text, r'local Q\s*=')
    quest_groups = table_at(quest_text, r'local GROUPS\s*=')
    daily = [entry('daily-rules', 'Cách làm nhiệm vụ ngày', [
        'Nhấn B mở Bảng Trạng Thái và đọc nhiệm vụ đang được giao. Nhiệm vụ xuất hiện từ ngày 10 của thế giới.',
        'Thực hiện đúng hành động khi nhiệm vụ đang hoạt động; tiến độ đã làm trước khi nhận không được tính.',
        'Thời hạn hoàn thành là 2 ngày trong game. Hoàn thành sẽ tự nhận EXP và tăng số nhiệm vụ đã hoàn thành; đợi 2 ngày để nhận nhiệm vụ tiếp theo.',
        'Thất bại: giảm Máu, Độ No và Tinh thần hiện tại còn một nửa (sàn 1, không hồi thêm nếu vốn thấp hơn 1), phong ấn EXP 1 ngày và khóa ngẫu nhiên một ô trang bị 1 ngày. Đợi 2 ngày kể từ thất bại để nhận nhiệm vụ mới.',
        'Hoàn thành 5 nhiệm vụ mở Mặc Ảnh; 10 nhiệm vụ mở Hắc Ảnh. Khi đang phong ấn EXP, thưởng EXP không được cộng.',
    ], 'scripts/components/hh_daily_quest.lua; main/hh_tunning.lua')]
    tracker_tips = {'finishedwork': 'Phải chặt hạ cây / đào vỡ đá hoàn toàn; từng nhát làm việc chưa được tính.',
                    'pick': 'Thu hoạch trực tiếp đúng bụi/cây; nhặt vật phẩm đã rơi dưới đất không thay thế hành động thu hoạch.',
                    'kill': 'Bạn phải trực tiếp kết liễu đúng loại quái. Quái do đệ tử hoặc người khác giết không được tính.',
                    'distance': 'Chạy bộ bằng chân. Cưỡi thú, đứng trên thuyền, dịch chuyển và di chuyển khi là ma không được tính.',
                    'work': 'Mỗi hành động CHOP, MINE hoặc HAMMER được tính một lần.',
                    'maintain': 'Giữ liên tục ngưỡng yêu cầu. Tụt dưới ngưỡng khiến nhiệm vụ thất bại ngay.'}
    for q in quests.values():
        lines = [q['description'], f"{q['reward']} EXP", f"Mục tiêu: {q['target']}",
                 'Độ khó: ' + {'easy': 'Dễ', 'medium': 'Vừa', 'hard': 'Khó'}[q['difficulty']]]
        if q['tracker'] in tracker_tips:
            lines.append(tracker_tips[q['tracker']])
        if q.get('unique_field'):
            lines.append('Chỉ tính các loại khác nhau; lặp lại cùng công thức, món ăn hoặc khu vực không tăng tiến độ.')
        if q.get('group'):
            lines.append('Mục tiêu hợp lệ: ' + ', '.join(quest_groups[q['group']] ))
        if q.get('cave_only'):
            lines.append('Chỉ được giao trong hang động.')
        if q.get('night_only'):
            lines.append('Chỉ tính chạy bộ vào ban đêm.')
        if q.get('allowed_seasons'):
            lines.append('Được giao vào mùa xuân, hè và thu; không giao trong 3 ngày cuối mùa thu.')
        if q.get('min_completed_quests'):
            lines.append(f"Chỉ được giao sau khi đã hoàn thành {q['min_completed_quests']} nhiệm vụ ngày.")
        if q.get('source_prefab'):
            lines.append(f"Phải học từ: {q['source_prefab']}.")
        if q.get('event') == 'healthdelta':
            lines.append('Chỉ cộng lượng máu thực sự hồi phục; mất máu không được tính.')
        if q.get('event') == 'attacked':
            lines.append('Phải chịu đòn có sát thương lớn hơn 0.')
        row = entry(f"daily-{q['id']}", q['title'], lines, quest_source)
        row['category'] = {'easy': 'Dễ', 'medium': 'Vừa', 'hard': 'Khó'}[q['difficulty']]
        daily.append(row)
    groups.append(group('daily', 'Daily Quest', '60 nhiệm vụ ngày: yêu cầu, EXP, điều kiện nhận và cách tính tiến độ của từng nhiệm vụ.', daily))

    catalogue = [entry(f'item-{key}', value['1'], list(dict.fromkeys(str(v) for k, v in value.items() if k != '1')) + [f'Prefab: {key}'], 'main/hh_string.lua')
                 for key, value in items.items() if isinstance(value, dict) and '1' in value]
    catalogue += records(table_at(read('scripts/prefabs/wb_strengthen_food.lua'), r'local B__u_G\s*='), 'luck-potion', 'scripts/prefabs/wb_strengthen_food.lua')
    catalogue = curate_items(catalogue)
    groups.append(group('items', 'Vật phẩm & sinh vật', 'Vật phẩm sử dụng, vũ khí, công trình và sinh vật cần biết khi chơi. Các dạng biến đổi được gộp; bỏ mục nội bộ và mục trùng.', catalogue))
    effects = [entry(f'effect-{key}', key, [value], 'main/hh_tunning.lua') for key, value in format_config['EQUIP_EFFECT'].items() if value]
    enchant_text = read('scripts/enums/hh_enchant.lua')
    enchant = table_at(enchant_text, r'local af\s*=')
    for key, value in enchant.items():
        if not isinstance(value, dict) or 'name' not in value:
            continue
        # Descriptions refer to the localized format table rather than string literals.
        block = re.search(r'\["' + re.escape(key) + r'"\]\s*=\s*\{', enchant_text)
        raw = balanced(enchant_text, enchant_text.index('{', block.start())) if block else ''
        desc_ref = re.search(r'\["desc"\]\s*=\s*b\["([^"]+)"\]', raw)
        desc = format_config['EQUIP_EFFECT'].get(desc_ref[1], '') if desc_ref else value.get('desc', '')
        vr = value.get('value_range', {})
        if desc and vr:
            desc = desc.replace('%s', f"{vr.get('min', '?')}–{vr.get('max', '?')}").replace('%%', '%')
        lines = [desc] if desc else []
        lines += [f'{LABELS[k]}: {describe(value[k])}' for k in ('value_range', 'check_desc', 'only_one', 'can_add', 'only_compound', 'ui_from_desc') if k in value]
        effects.append(entry(f'enchant-{key}', value['name'], lines, 'scripts/enums/hh_enchant.lua'))
    groups.append(group('effects', 'Thuộc tính & hiệu ứng', 'Danh sách hiệu ứng, đá thuộc tính, phạm vi giá trị và giới hạn trang bị.', effects))

    sprites = shop_sprites(root.parent)
    local_sprites, _ = mod_sprites(root)
    sprites.update(local_sprites)
    guild_settings = table_at(read('main/hh_guild_main.lua'), r'TUNING\.HH_GUILD\s*=')
    for id, title, path, pattern in [
        ('guild', 'Nhiệm vụ Hiệp Hội', 'scripts/guild/hh_guild_quest_defs.lua', r'local Q\s*='),
        ('exams', 'Rank Up', 'scripts/guild/hh_rank_exam_defs.lua', r'local EXAMS\s*='),
        ('dungeon-shop', 'Cửa hàng Hầm Ngục', 'scripts/dungeon_shop/hh_dungeon_shop_defs.lua', r'local PRODUCTS\s*='),
        ('guild-shop', 'Cửa hàng Hiệp Hội', 'scripts/guild/hh_guild_shop_defs.lua', r'local PRODUCTS\s*='),
        ('shadows', 'Đệ tử & quân đoàn', 'scripts/enums/hh_shadow_progression_defs.lua', r'M.DEFS\s*='),
    ]:
        rows = records(table_at(read(path), pattern), id, path)
        if id == 'guild-shop':
            for row, product in zip(rows, table_at(read(path), pattern).values()):
                row['shop'] = {key: product[key] for key in ('rank', 'prefab', 'price', 'stock', 'amount')}
                row['shop']['sprite'] = sprites.get(product['prefab'])
                row['shop']['currency'] = 'Xu Hiệp Hội'
                row['category'] = 'Rank ' + product['rank']
        if id == 'dungeon-shop':
            for row, product in zip(rows, table_at(read(path), pattern).values()):
                prefab = product.get('prefab_id', product.get('prefab'))
                row['shop'] = {'prefab': prefab, 'price': product['price'], 'stock': product['stock'], 'amount': product.get('amount', 1),
                               'currency': 'Xu Hầm Ngục', 'sprite': sprites.get(prefab)}
        if id in ('guild', 'exams'):
            definition = table_at(read(path), pattern)
            targets = table_at(read('scripts/guild/hh_guild_quest_defs.lua'), r'local GROUPS\s*=')
            for row, record in zip(rows, definition.values()):
                if record.get('group') in targets:
                    row['lines'].append('Mục tiêu hợp lệ: ' + ', '.join(targets[record['group']]))
                if record.get('tracker') == 'delivery':
                    row['lines'].append('Mang đủ nguyên liệu tới Nhân Viên Hiệp Hội để giao nộp, sau đó tự nhận thưởng.')
        description = 'Toàn bộ danh mục được khai báo trong mod.'
        if id == 'guild-shop':
            description = ('Giá tính bằng Xu Hiệp Hội. Mỗi lượt mua nhận số vật phẩm ghi trên thẻ. '
                           'Mỗi chu kỳ cửa hàng chọn ngẫu nhiên 6 sản phẩm cho mỗi Rank; danh mục dưới đây gồm toàn bộ 90 sản phẩm có thể xuất hiện. '
                           f'Giới hạn lượt mua được làm mới mỗi {guild_settings["SHOP_RESET_DAYS"]} ngày theo cấu hình mod hiện tại.')
        elif id == 'dungeon-shop':
            description = ('Giá tính bằng Xu Hầm Ngục. Danh mục gồm toàn bộ thuốc thợ săn, thuốc đệ tử, vũ khí và vật phẩm tiện ích có thể xuất hiện. '
                           'Số lượt bán được khai báo cho mỗi sản phẩm; hàng đang mở trong game có thể đã được thợ săn khác mua.')
        groups.append(group(id, title, description, rows))
    groups[-4]['entries'].insert(0, entry('rank-levels', 'Cấp độ yêu cầu & tỷ lệ trích xuất',
        ['Rank E: khởi đầu · trích xuất 15%', 'Rank D: Level 10 · trích xuất 20%', 'Rank C: Level 20 · trích xuất 25%',
         'Rank B: Level 30 · trích xuất 35%', 'Rank A: Level 40 · trích xuất 40%', 'Rank S: Level 50 · trích xuất 100%',
         'Đạt cấp độ chưa tự tăng Rank: phải nhận và hoàn thành bài thi tương ứng tại Hiệp Hội.'], 'scripts/guild/hh_rank_defs.lua; main/hh_tunning.lua'))

    # Publish literal gameplay tuning tables, including drop chances and mana costs.
    configs = []
    context = {}
    for path in ('main/hh_tunning.lua', 'main/hh_config.lua', 'main/hh_guild_main.lua'):
        text = read(path)
        for key, parsed in tuning_tables(text, context, top_level_only=path == 'main/hh_config.lua').items():
            if key in ('HH_UI_TEXT', 'HH_FORMAT_CONFIG', 'HH_COLOR_CONFIG', 'HH_ICON_CONFIG'):
                continue
            if parsed is not None:
                lines = [f'{k}: {describe(v)}' for k, v in parsed.items()] if isinstance(parsed, dict) else [describe(parsed)]
                configs.append(entry(f'config-{key}', key, lines, path))
    guide.append(entry('weapon-mana', 'Mana khi dùng vũ khí', ['Đòn bắn thường của Trượng Ma Vực và Trượng Hỏa Ngục tiêu thụ 5 mana.',
        'Kỹ năng chuột phải của Kiếm Quỷ Vương, Trượng Ma Vực và Hắc Thiên Kiếm tốn thêm 20 mana; không đủ mana sẽ không thi triển.'],
        'scripts/enums/hh_equip.lua; main/hh_skill_cost.lua'))
    guide.append(entry('world-rank', 'Thế giới mạnh lên theo Rank', ['Khi có thợ săn đạt Rank B, hệ số máu quái tăng lên 1,20 và sát thương 1,10.',
        'Khi có thợ săn đạt Rank S, hệ số máu quái tăng lên 1,50 và sát thương 1,25.', 'Đây là giai đoạn sức mạnh chung của thế giới.'], 'scripts/components/hh_world.lua; main/hh_world_rank.lua'))
    settings = table_at(read('modinfo.lua'), r'configuration_options\s*=')
    hotkeys = table_at(read('modinfo.lua'), r'local a\s*=')
    teleport_options = table_at(read('modinfo.lua'), r'local teleport_hotkey_options\s*=')
    for key, value in settings.items():
        if isinstance(value, dict) and value.get('name'):
            if value['name'] == 'key_config':
                value['options'] = hotkeys
            elif 'teleport' in value['name']:
                value['options'] = teleport_options
            configs.append(entry(f'setting-{key}', value.get('label', value['name']),
                [value.get('hover', ''), 'Mặc định: ' + describe(value.get('default', 'Không khai báo')),
                 'Các lựa chọn: ' + describe(value.get('options', {}))], 'modinfo.lua'))
    groups.append(group('config', 'Thông số & cấu hình', 'Thông số được khai báo tĩnh: chỉ số, mana, quái, rơi đồ và tùy chọn mod. Giá trị thực tế phụ thuộc cấu hình server.', configs))
    enrich_entries(groups, sprites, names)
    files = []
    for path in sorted(root.rglob('*')):
        if path.is_file():
            files.append({'path': path.relative_to(root).as_posix(), 'size': path.stat().st_size,
                          'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'text': path.suffix in ('.lua', '.txt', '.xml')})
    version = re.search(r'version\s*=\s*"([^"]+)"', read('modinfo.lua'))[1]
    return {'meta': {'name': 'Solo Leveling', 'version': version, 'author': 'Saikuno', 'files': len(files)}, 'groups': groups, 'files': files}


def main():
    workspace = Path(__file__).resolve().parents[2]
    root = workspace / 'solo_leveling'
    data = build_data(root)
    target = workspace / 'data/generated/solo-leveling.json'
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    public = workspace / 'public/solo-leveling'
    public.mkdir(exist_ok=True)
    (public / 'Wiki.txt').write_bytes((root / 'Wiki.txt').read_bytes())
    # The exhaustive source reader is a separate lazy-loaded payload.
    texts = {f['path']: (root / f['path']).read_text(encoding='utf-8-sig') for f in data['files'] if f['text']}
    (public / 'sources.json').write_text(json.dumps(texts, ensure_ascii=False), encoding='utf-8')
    with zipfile.ZipFile(public / 'solo-leveling-sources.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in texts:
            archive.write(root / path, path)
    print(json.dumps({'groups': {g['id']: len(g['entries']) for g in data['groups']}, 'files': len(data['files'])}))


if __name__ == '__main__':
    main()
