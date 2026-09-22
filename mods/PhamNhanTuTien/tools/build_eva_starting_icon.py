"""Build EVA's 64px starting-item KTEX from the existing compressed mip chain."""

from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "images/inventoryimages/eva_scythe.tex"
OUTPUT = ROOT / "images/inventoryimages/eva_scythe_starting.tex"
MIP_COUNT_SHIFT = 13
MIP_COUNT_MASK = 31 << MIP_COUNT_SHIFT
MIPMAP = struct.Struct("<HHHI")


def read_ktex(path):
    data = path.read_bytes()
    if len(data) < 8 or data[:4] != b"KTEX":
        raise ValueError(f"not a KTEX file: {path}")
    specifications = struct.unpack_from("<I", data, 4)[0]
    mip_count = (specifications & MIP_COUNT_MASK) >> MIP_COUNT_SHIFT
    metadata_end = 8 + MIPMAP.size * mip_count
    if mip_count < 2 or len(data) < metadata_end:
        raise ValueError("source KTEX has no lower mip chain")
    metadata = [MIPMAP.unpack_from(data, 8 + MIPMAP.size * index)
                for index in range(mip_count)]
    offset = metadata_end
    payloads = []
    for width, height, _, size in metadata:
        end = offset + size
        if width == 0 or height == 0 or end > len(data):
            raise ValueError("invalid or truncated KTEX mipmap")
        payloads.append(data[offset:end])
        offset = end
    if offset != len(data):
        raise ValueError("unexpected trailing KTEX data")
    return specifications, metadata, payloads


def build(source=SOURCE, output=OUTPUT):
    specifications, metadata, payloads = read_ktex(source)
    if metadata[0][:2] != (128, 128) or metadata[1][:2] != (64, 64):
        raise ValueError("expected the EVA scythe 128px-to-64px mip transition")
    mip_count = len(metadata) - 1
    specifications = ((specifications & ~MIP_COUNT_MASK)
                      | (mip_count << MIP_COUNT_SHIFT))
    result = bytearray(b"KTEX")
    result.extend(struct.pack("<I", specifications))
    for record in metadata[1:]:
        result.extend(MIPMAP.pack(*record))
    for payload in payloads[1:]:
        result.extend(payload)
    output.write_bytes(result)

    rebuilt = read_ktex(output)
    if rebuilt != (specifications, metadata[1:], payloads[1:]):
        raise RuntimeError("rebuilt KTEX does not preserve the lower mip chain")
    print(f"Built {output.name}: 64x64, {mip_count} lossless source mips, {len(result)} bytes")


if __name__ == "__main__":
    build()
