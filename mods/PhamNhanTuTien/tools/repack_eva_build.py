"""Repack EVA's six-sheet BILD into two native character atlases.

The top DXT5 mip is assembled by copying aligned compressed blocks verbatim.
Only generated lower mips are recompressed. The source archive is accepted
explicitly and pinned so the historical input need not remain in the mod.
"""

from argparse import ArgumentParser
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
import struct

from PIL import Image


SOURCE_SHA256 = "fbfd9993a9ddb778ef88b3cdf06e9c8f865856f6eaaf70d443d5b36509a09e9d"
MIPMAP = struct.Struct("<HHHI")
VERTEX = struct.Struct("<ffffff")
SIZE = 2048

# old index: (source entry, source size, crop box, new index, destination origin)
# Crop bounds are DXT-block aligned and include >=4px padding around used UVs.
PLACEMENTS = {
    0: ("atlas-0.tex", (2048, 2048), (0, 68, 2024, 1204), 0, (0, 0)),
    1: ("atlas-1.tex", (2048, 1024), (16, 300, 2044, 1024), 0, (0, 1140)),
    2: ("eva-eyes.tex", (2048, 1024), (124, 424, 1840, 612), 1, (0, 1028)),
    4: ("eva-dress.tex", (2048, 1024), (32, 468, 1584, 608), 1, (0, 1220)),
    5: ("eva-expression.tex", (2048, 1024), (0, 0, 2048, 1024), 1, (0, 0)),
}


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


def pack_string(value):
    encoded = value.encode("ascii")
    return struct.pack("<I", len(encoded)) + encoded


def read_ktex(data):
    if data[:4] != b"KTEX":
        raise ValueError("invalid KTEX magic")
    specifications = struct.unpack_from("<I", data, 4)[0]
    mip_count = (specifications >> 13) & 31
    metadata = [MIPMAP.unpack_from(data, 8 + MIPMAP.size * index)
                for index in range(mip_count)]
    offset = 8 + MIPMAP.size * mip_count
    payloads = []
    for width, height, _, size in metadata:
        end = offset + size
        if not width or not height or end > len(data):
            raise ValueError("invalid KTEX mip metadata")
        payloads.append(data[offset:end])
        offset = end
    if offset != len(data):
        raise ValueError("unexpected KTEX trailing bytes")
    return specifications, metadata, payloads


def copy_blocks(source, source_size, crop, destination, dest_xy):
    left, top, right, bottom = crop
    dest_x, dest_y = dest_xy
    if any(value % 4 for value in (*crop, dest_x, dest_y)):
        raise ValueError("DXT placement is not block aligned")
    width, height = right - left, bottom - top
    source_width, source_height = source_size
    expected_source_size = source_width // 4 * (source_height // 4) * 16
    if len(source) != expected_source_size:
        raise ValueError("unexpected source DXT5 payload length")
    if (right > source_width or bottom > source_height
            or dest_x + width > SIZE or dest_y + height > SIZE):
        raise ValueError("DXT placement is out of bounds")
    source_stride = source_width // 4 * 16
    dest_stride = SIZE // 4 * 16
    row_size = width // 4 * 16
    for block_y in range(height // 4):
        source_start = (top // 4 + block_y) * source_stride + left // 4 * 16
        dest_start = (dest_y // 4 + block_y) * dest_stride + dest_x // 4 * 16
        source_row = source[source_start:source_start + row_size]
        if len(source_row) != row_size:
            raise ValueError("truncated source DXT5 block row")
        destination[dest_start:dest_start + row_size] = source_row
    if len(destination) != SIZE * SIZE:
        raise RuntimeError("copy changed destination DXT5 payload length")


def assert_copied_blocks(source, source_size, crop, destination, dest_xy):
    left, top, right, bottom = crop
    dest_x, dest_y = dest_xy
    source_width, _ = source_size
    source_stride = source_width // 4 * 16
    dest_stride = SIZE // 4 * 16
    row_size = (right - left) // 4 * 16
    for block_y in range((bottom - top) // 4):
        source_start = (top // 4 + block_y) * source_stride + left // 4 * 16
        dest_start = (dest_y // 4 + block_y) * dest_stride + dest_x // 4 * 16
        if source[source_start:source_start + row_size] != destination[dest_start:dest_start + row_size]:
            raise RuntimeError("top-level DXT5 blocks changed during packing")


def encode_dxt5(image):
    stream = BytesIO()
    image.save(stream, format="DDS", pixel_format="DXT5")
    data = stream.getvalue()
    if data[84:88] != b"DXT5":
        raise RuntimeError("Pillow did not emit DXT5")
    return data[128:]


def make_ktex(top_payload, source_specifications):
    payloads = [bytes(top_payload)]
    image = Image.frombytes("RGBA", (SIZE, SIZE), payloads[0], "bcn", (3,))
    width = height = SIZE
    while width > 1 or height > 1:
        width, height = max(1, width // 2), max(1, height // 2)
        # The source RGB channels are already premultiplied. Resize all four
        # channels independently so Pillow cannot premultiply them again.
        image = Image.merge("RGBA", tuple(
            channel.resize((width, height), Image.Resampling.LANCZOS)
            for channel in image.split()))
        payloads.append(encode_dxt5(image))
    mip_count = len(payloads)
    specifications = ((source_specifications & ~(31 << 13))
                      | (mip_count << 13))
    metadata = []
    width = height = SIZE
    for payload in payloads:
        metadata.append((width, height, max(4, width) * 4, len(payload)))
        width, height = max(1, width // 2), max(1, height // 2)
    result = bytearray(b"KTEX" + struct.pack("<I", specifications))
    for record in metadata:
        result.extend(MIPMAP.pack(*record))
    for payload in payloads:
        result.extend(payload)
    return bytes(result)


def transform_build(data):
    reader = Reader(data)
    magic, version = reader.take(4), reader.uint()
    if magic != b"BILD" or version != 6:
        raise ValueError("expected BILD version 6")
    symbol_count, frame_count = reader.uint(), reader.uint()
    build_name = reader.string()
    old_atlases = [reader.string() for _ in range(reader.uint())]
    expected = ["atlas-0.tex", "atlas-1.tex", "eva-eyes.tex",
                "eva-dress-back.tex", "eva-dress.tex", "eva-expression.tex"]
    if old_atlases != expected:
        raise ValueError(f"unexpected EVA atlas list: {old_atlases}")
    symbols_start = reader.pos
    for _ in range(symbol_count):
        reader.take(4)
        reader.take(reader.uint() * 32)
    symbols = data[symbols_start:reader.pos]
    vertex_count = reader.uint()
    vertices = []
    for _ in range(vertex_count):
        x, y, z, u, v, atlas_value = VERTEX.unpack(reader.take(VERTEX.size))
        old_index = int(atlas_value)
        if atlas_value != old_index or old_index not in PLACEMENTS:
            raise ValueError(f"unsupported EVA atlas index: {atlas_value}")
        _, (old_width, old_height), (left, top, _, _), new_index, (dest_x, dest_y) = PLACEMENTS[old_index]
        new_u = (u * old_width - left + dest_x) / SIZE
        new_v = (v * old_height - top + dest_y) / SIZE
        if not (0 <= new_u <= 1 and 0 <= new_v <= 1):
            raise ValueError("remapped EVA UV is out of bounds")
        vertices.append(VERTEX.pack(x, y, z, new_u, new_v, float(new_index)))
    tail = reader.take(len(data) - reader.pos)
    result = bytearray(magic + struct.pack("<III", version, symbol_count, frame_count))
    result.extend(pack_string(build_name))
    result.extend(struct.pack("<I", 2))
    result.extend(pack_string("atlas-0.tex"))
    result.extend(pack_string("atlas-1.tex"))
    result.extend(symbols)
    result.extend(struct.pack("<I", vertex_count))
    result.extend(b"".join(vertices))
    result.extend(tail)
    return bytes(result)


def repack(source_path, output_path):
    source_bytes = source_path.read_bytes()
    actual_hash = sha256(source_bytes).hexdigest()
    if actual_hash != SOURCE_SHA256:
        raise ValueError(f"source EVA archive hash mismatch: {actual_hash}")
    with ZipFile(BytesIO(source_bytes)) as source:
        entries = {name: source.read(name) for name in source.namelist()}
    source_specifications = None
    tops = [bytearray(SIZE * SIZE) for _ in range(2)]
    for old_index, (entry, expected_size, crop, new_index, destination) in PLACEMENTS.items():
        specifications, metadata, payloads = read_ktex(entries[entry])
        if (specifications >> 4) & 31 != 2 or metadata[0][:2] != expected_size:
            raise ValueError(f"unexpected source KTEX: {entry}")
        if source_specifications is None:
            source_specifications = specifications
        copy_blocks(payloads[0], expected_size, crop, tops[new_index], destination)
        assert_copied_blocks(payloads[0], expected_size, crop,
                             tops[new_index], destination)

    packed = [make_ktex(top, source_specifications) for top in tops]
    build = transform_build(entries["build.bin"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output_path, "w", ZIP_DEFLATED, compresslevel=9) as output:
        for name, data in (("anim.bin", entries["anim.bin"]),
                           ("atlas-0.tex", packed[0]),
                           ("atlas-1.tex", packed[1]),
                           ("build.bin", build)):
            info = ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            output.writestr(info, data, compresslevel=9)
    print(f"Built {output_path}: two 2048x2048 DXT5 atlases")


def main():
    parser = ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.source.resolve() == args.output.resolve():
        parser.error("--source and --output must differ")
    repack(args.source, args.output)


if __name__ == "__main__":
    main()
