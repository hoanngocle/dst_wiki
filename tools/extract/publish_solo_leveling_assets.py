"""Decode referenced Klei KTEX icons with the installed Pillow BCn decoder.

Run with the bundled Python runtime (Pillow required), after build_solo_leveling_data.
The original mod files are never changed.
"""
from __future__ import annotations

import json
import struct
from pathlib import Path

from PIL import Image
from tools.extract.solo_leveling_visuals import mod_sprites


def decode_ktex(data: bytes) -> Image.Image:
    if len(data) < 18 or data[:4] != b'KTEX':
        raise ValueError('Invalid KTEX header')
    specifications = struct.unpack_from('<I', data, 4)[0]
    format_id, mipmaps = (specifications >> 4) & 31, (specifications >> 13) & 31
    start = 8 + 10 * mipmaps
    if not mipmaps or len(data) < start:
        raise ValueError('Invalid KTEX mipmap metadata')
    width, height, _, size = struct.unpack_from('<HHHI', data, 8)
    if not width or not height or width * height > 16_777_216:
        raise ValueError('Invalid KTEX dimensions')
    block_size = 8 if format_id == 0 else 16
    expected = ((width + 3) // 4) * ((height + 3) // 4) * block_size
    if format_id in (3, 4):
        expected = width * height * (3 if format_id == 3 else 4)
    if format_id not in (0, 1, 2, 3, 4) or size != expected or len(data) < start + size:
        raise ValueError('Unsupported or truncated KTEX payload')
    payload = data[start:start + size]
    if format_id <= 2:
        image = Image.frombytes('RGBA', (width, height), payload, 'bcn', (format_id + 1, ('DXT1', 'DXT3', 'DXT5')[format_id]))
    else:
        image = Image.frombytes('RGB' if format_id == 3 else 'RGBA', (width, height), payload).convert('RGBA')
    # Klei stores bottom-up, premultiplied pixels; the web atlas renderer uses top-down PNGs.
    image = Image.frombytes('RGBa', image.size, image.tobytes()).convert('RGBA')
    return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)


def main():
    workspace = Path(__file__).resolve().parents[2]
    data = json.loads((workspace / 'data/generated/solo-leveling.json').read_text(encoding='utf-8'))
    _, textures = mod_sprites(workspace / 'solo_leveling')
    def sources(value):
        if isinstance(value, dict):
            if str(value.get('src', '')).startswith('/solo-leveling/icons/'):
                yield value['src']
            for child in value.values():
                yield from sources(child)
        elif isinstance(value, list):
            for child in value:
                yield from sources(child)
    used = sorted(set(sources(data['groups'])))
    output = workspace / 'public/solo-leveling/icons'
    output.mkdir(parents=True, exist_ok=True)
    for source in used:
        image = decode_ktex(textures[source].read_bytes())
        image.save(workspace / 'public' / source.lstrip('/'), optimize=True)
    print(json.dumps({'published_icon_atlases': len(used)}))


if __name__ == '__main__':
    main()
