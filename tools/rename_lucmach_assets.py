"""Rename local sword animation symbols using Klei BILD v6 / ANIM v4 layouts.

Layouts/hash from the installed official Mod Tools buildanimation.py.
Only parsed string/hash fields change; geometry, frames and textures stay intact.
"""
import io
import re
import struct
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

OLD = 'terraprisma'
NEW = 'lucmachthankiem'

def rename(s):
    return s.replace(OLD, NEW)

def hash_name(s):
    h = 0
    for c in s.lower():
        h = (ord(c) + (h << 6) + (h << 16) - h) & 0xffffffff
    return h

class Reader:
    def __init__(self, data):
        self.data, self.pos = data, 0
    def take(self, n):
        assert self.pos + n <= len(self.data)
        value = self.data[self.pos:self.pos+n]; self.pos += n
        return value
    def uint(self):
        return struct.unpack('<I', self.take(4))[0]
    def string(self):
        return self.take(self.uint()).decode('ascii')

def uint(n):
    return struct.pack('<I', n)

def string(s):
    b = s.encode('ascii'); return uint(len(b)) + b

def transform(data, convert=True):
    r = Reader(data)
    magic, version = r.take(4), r.uint()
    fields = []
    # Each field is raw data, a symbol hash, or an owned string.
    def raw(n): fields.append(('raw', r.take(n)))
    def hashed(): fields.append(('hash', r.uint()))
    def text(): fields.append(('text', r.string()))
    if magic == b'BILD':
        assert version == 6
        count = r.uint(); frames = r.uint()
        fields.append(('raw', uint(count)+uint(frames)))
        text()
        atlases = r.uint(); fields.append(('raw', uint(atlases)))
        for _ in range(atlases): text()
        symbols = []
        for _ in range(count):
            h = r.uint(); n = r.uint(); body = r.take(n * 32)
            symbols.append((h, n, body))
        # Hash-sorted symbol table is required by the official compiler.
        fields.append(('symbols', symbols))
        vertices = r.uint()
        fields.append(('raw', uint(vertices) + r.take(vertices * 24)))
    elif magic == b'ANIM':
        assert version == 4
        raw(12)
        animations = r.uint(); fields.append(('raw', uint(animations)))
        for _ in range(animations):
            text(); raw(1); hashed(); raw(4)
            frames = r.uint(); fields.append(('raw', uint(frames)))
            for _ in range(frames):
                raw(16)
                events = r.uint(); fields.append(('raw', uint(events)))
                for _ in range(events): hashed()
                elements = r.uint(); fields.append(('raw', uint(elements)))
                for _ in range(elements):
                    hashed(); raw(4); hashed(); raw(28)
    else:
        raise ValueError(magic)
    names = {}
    for _ in range(r.uint()):
        h, s = r.uint(), r.string()
        assert hash_name(s) == h, (s, h)
        names[h] = s
    assert r.pos == len(data), (r.pos, len(data))
    mapped = {h: hash_name(rename(s)) if convert else h for h, s in names.items()}
    def map_hash(h):
        assert h in names, h
        return mapped[h]
    out = io.BytesIO(); out.write(magic + uint(version))
    for kind, value in fields:
        if kind == 'raw': out.write(value)
        elif kind == 'text': out.write(string(rename(value) if convert else value))
        elif kind == 'hash': out.write(uint(map_hash(value)))
        else:
            for h, n, body in sorted(value, key=lambda row: map_hash(row[0])):
                out.write(uint(map_hash(h)) + uint(n) + body)
    out.write(uint(len(names)))
    for h, s in names.items():
        out.write(uint(map_hash(h)) + string(rename(s) if convert else s))
    return out.getvalue()

def rewrite_archive(path):
    with ZipFile(path) as z:
        entries = [(n, z.read(n)) for n in z.namelist()]
    updated = []
    for name, data in entries:
        if name.endswith('.bin'):
            assert transform(data, False) == data, f'Parser roundtrip failed: {path}/{name}'
            data = transform(data)
            assert transform(data, False) == data
            assert OLD.encode() not in data
        updated.append((name, data))
    with ZipFile(path, 'w', ZIP_DEFLATED) as z:
        for name, data in updated: z.writestr(name, data)

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1] / 'mods/PhamNhanTuTien/anim'
    paths = list(root.glob('*terraprisma*.zip'))
    assert paths, 'No source animations found'
    for path in paths:
        rewrite_archive(path)
        path.rename(path.with_name(rename(path.name)))
    print(f'Renamed and structurally verified {len(paths)} animation archives')
