from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import math
import os
import struct
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = Path(os.environ.get("EVA_ARCHIVE", ROOT / "anim/eva.zip"))
ANIM_SHA256 = "13969e77f249aff2a55035cd36e9134a31380b367dc4d4b4c2c2f57c41e8de9d"
EVA_NONE_SHA256 = "3d0affa46060d013be8572168983ab817410a1e2b3304f167c99d652b200cd41"
RIG_MAP = Path(os.environ.get(
    "EVA_RIG_MAP",
    ROOT / "assets/source/eva_approved/rig-map.json",
))
FACE_HASH = 3118343357


class Reader:
    def __init__(self, data):
        self.data, self.pos = data, 0

    def take(self, size):
        value = self.data[self.pos:self.pos + size]
        if len(value) != size:
            raise ValueError("truncated BILD")
        self.pos += size
        return value

    def uint(self):
        return struct.unpack("<I", self.take(4))[0]

    def string(self):
        return self.take(self.uint()).decode("ascii")


def inspect_build(data):
    reader = Reader(data)
    digest = hashlib.sha256()
    digest.update(reader.take(4))
    digest.update(reader.take(4))
    symbol_count, frame_count = reader.uint(), reader.uint()
    digest.update(struct.pack("<II", symbol_count, frame_count))
    name = reader.string()
    digest.update(struct.pack("<I", len(name)) + name.encode("ascii"))
    atlases = [reader.string() for _ in range(reader.uint())]
    symbols = []
    for _ in range(symbol_count):
        symbol_hash, frame_total = reader.uint(), reader.uint()
        frames = [struct.unpack("<IIffffII", reader.take(32))
                  for _ in range(frame_total)]
        symbols.append((symbol_hash, frames))
    vertex_count = reader.uint()
    indices = set()
    vertex_data = reader.take(vertex_count * 24)
    for offset in range(0, len(vertex_data), 24):
        x, y, z, u, v, atlas = struct.unpack_from("<ffffff", vertex_data, offset)
        if not all(math.isfinite(value) for value in (u, v, atlas)):
            raise ValueError("non-finite UV or atlas index")
        if not (0 <= u <= 1 and 0 <= v <= 1) or atlas != int(atlas):
            raise ValueError("invalid UV or non-integral atlas index")
        indices.add(int(atlas))
    for symbol_hash, frames in symbols:
        if symbol_hash == FACE_HASH:
            continue
        digest.update(struct.pack("<II", symbol_hash, len(frames)))
        for frame in frames:
            digest.update(struct.pack("<IIffffI", *frame[:6], frame[7]))
            start = frame[6] * 24
            digest.update(vertex_data[start:start + frame[7] * 24])
    digest.update(reader.take(len(data) - reader.pos))
    return name, atlases, indices, digest.hexdigest(), symbol_count


def inspect_ktex(data):
    if data[:4] != b"KTEX":
        raise ValueError("invalid KTEX")
    specifications = struct.unpack_from("<I", data, 4)[0]
    mip_count = (specifications >> 13) & 31
    compression = (specifications >> 4) & 31
    metadata = [struct.unpack_from("<HHHI", data, 8 + 10 * index)
                for index in range(mip_count)]
    offset = 8 + 10 * mip_count
    payloads = []
    for width, height, pitch, size in metadata:
        expected_size = ((width + 3) // 4) * ((height + 3) // 4) * 16
        if pitch != max(4, width) * 4 or size != expected_size:
            raise ValueError("invalid DXT5 mip metadata")
        payloads.append(data[offset:offset + size])
        offset += size
    if offset != len(data):
        raise ValueError("KTEX mip payload length mismatch")
    return compression, metadata, payloads


class EvaBuildRepackTest(unittest.TestCase):
    def test_archive_uses_two_native_atlases(self):
        with ZipFile(ARCHIVE) as archive:
            self.assertEqual(set(archive.namelist()), {
                "anim.bin", "build.bin", "atlas-0.tex", "atlas-1.tex",
            })
            name, atlases, indices, digest, symbol_count = inspect_build(
                archive.read("build.bin")
            )
            self.assertEqual(name, "eva")
            self.assertIn(symbol_count, {20, 35})
            self.assertEqual(atlases, ["atlas-0.tex", "atlas-1.tex"])
            self.assertLessEqual(indices, {0, 1})
            manifest = json.loads(RIG_MAP.read_text(encoding="utf8"))
            self.assertEqual(
                manifest["build_sha256"],
                hashlib.sha256(archive.read("build.bin")).hexdigest(),
            )
            self.assertEqual(hashlib.sha256(archive.read("anim.bin")).hexdigest(), ANIM_SHA256)
            for atlas in atlases:
                compression, metadata, payloads = inspect_ktex(archive.read(atlas))
                self.assertEqual(compression, 2)
                expected_dimensions = [
                    (max(1, 2048 >> level), max(1, 2048 >> level))
                    for level in range(12)
                ]
                self.assertEqual([record[:2] for record in metadata], expected_dimensions)
                self.assertTrue(any(payloads[0]), atlas)

    def test_eva_none_remains_single_default_skin(self):
        prefab = ROOT / "scripts/prefabs/eva_none.lua"
        self.assertEqual(hashlib.sha256(prefab.read_bytes()).hexdigest(), EVA_NONE_SHA256)
        source = prefab.read_text(encoding="utf-8-sig")
        self.assertEqual(source.count('CreatePrefabSkin("eva_none"'), 1)
        self.assertIn('normal_skin = "eva"', source)
        self.assertIn('build_name_override = "eva"', source)


if __name__ == "__main__":
    unittest.main()
