"""Build the Vietnamese Noto Serif atlas with Klei's TextureConverter."""
from pathlib import Path
import hashlib
import json
import subprocess
import unicodedata
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageDraw, ImageFont

MOD = Path(__file__).resolve().parents[1]
BUILD = MOD.parents[1] / 'artifacts/forge-font-build'
CONVERTER = Path("C:/Program Files (x86)/Steam/steamapps/common/Don't Starve Mod Tools/mod_tools/tools/bin/TextureConverter.exe")


def build():
    BUILD.mkdir(parents=True, exist_ok=True)
    source = MOD / 'fonts/source/NotoSerif-Medium.ttf'
    font = ImageFont.truetype(str(source), 72)
    chars = set(chr(c) for c in range(32, 127))
    chars.update(chr(c) for c in range(160, 384))
    chars.update('ĐđƠơƯư–—‘’“”…•→×')
    for base in 'aăâeêioôơuưyAĂÂEÊIOÔƠUƯY':
        for tone in ['', '\u0300', '\u0301', '\u0303', '\u0309', '\u0323']:
            chars.update(unicodedata.normalize('NFC', base + tone))
    chars = sorted(chars, key=ord)
    atlas = Image.new('RGBA', (2048, 2048), (255, 255, 255, 0))
    draw = ImageDraw.Draw(atlas)
    root = ET.Element('font')
    def element(parent, tag, **attrs):
        return ET.SubElement(parent, tag, {k: str(v) for k, v in attrs.items()})
    element(root, 'info', face='Noto Serif Medium', size=72, bold=0, italic=0,
            charset='', unicode=1, stretchH=100, smooth=1, aa=1,
            padding='2,2,2,2', spacing='2,2', outline=0)
    ascent, descent = font.getmetrics()
    element(root, 'common', lineHeight=ascent+descent, base=ascent,
            scaleW=2048, scaleH=2048, pages=1, packed=0,
            alphaChnl=0, redChnl=4, greenChnl=4, blueChnl=4)
    element(element(root, 'pages'), 'page', id=0, file='font.png')
    records = element(root, 'chars', count=len(chars))
    x = y = row = 0
    for char in chars:
        left, top, right, bottom = font.getbbox(char, anchor='ls')
        width, height = right-left+4, bottom-top+4
        if x+width > 2048:
            x, y, row = 0, y+row+2, 0
        assert y+height <= 2048, 'Font atlas overflow'
        draw.text((x+2-left, y+2-top), char, font=font, anchor='ls', fill='white')
        element(records, 'char', id=ord(char), x=x, y=y, width=width, height=height,
                xoffset=left-2, yoffset=ascent+top-2,
                xadvance=round(font.getlength(char)), page=0, chnl=15)
        x += width+2
        row = max(row, height)
    kernings = element(root, 'kernings', count=0)
    for first in chars:
        for second in chars:
            amount = round(font.getlength(first+second)-font.getlength(first)-font.getlength(second))
            if amount:
                element(kernings, 'kerning', first=ord(first), second=ord(second), amount=amount)
    kernings.set('count', str(len(kernings)))
    atlas.save(BUILD / 'font.png')
    ET.indent(root)
    (BUILD / 'font.fnt').write_bytes(b'<?xml version="1.0"?>\n'+ET.tostring(root, encoding='utf-8'))
    subprocess.run([str(CONVERTER), '-i', str(BUILD/'font.png'), '-o', str(BUILD/'font.tex'),
                    '-f', 'bc3', '-p', 'opengl', '--mipmap'], check=True)
    output = MOD / 'fonts/ttk_forge_serif.zip'
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        for name in ('font.fnt', 'font.tex'):
            archive.write(BUILD/name, name)
    report = dict(glyphs=len(chars), kernings=len(kernings), line_height=ascent+descent,
                  source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  zip_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    (BUILD/'build.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    build()
