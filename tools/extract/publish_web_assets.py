"""Decode referenced KTEX files and publish browser PNG textures atomically."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any, Dict, List
from zipfile import ZipFile

from tools.extract.base_game import verify_snapshot_archive


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _resolve_decoder(decoder: str) -> str:
    candidate = Path(decoder)
    if candidate.parent != Path(".") or candidate.is_absolute():
        if candidate.is_file():
            return str(candidate)
        raise RuntimeError(f"texture decoder not found: {decoder}")
    resolved = shutil.which(decoder)
    if resolved is None:
        raise RuntimeError(f"texture decoder not found: {decoder}")
    return resolved


def _load_textures(path: Path) -> List[Dict[str, str]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    values = payload.get("textures")
    if not isinstance(values, list):
        raise ValueError("texture manifest must contain a textures array")
    by_hash: Dict[str, Dict[str, str]] = {}
    for value in sorted(
        values,
        key=lambda item: (
            str(item.get("sha256") or "") if isinstance(item, dict) else "",
            str(item.get("source") or "") if isinstance(item, dict) else "",
            str(item.get("texture") or "") if isinstance(item, dict) else "",
        ),
    ):
        if not isinstance(value, dict):
            raise ValueError("texture manifest rows must be objects")
        texture_hash = value.get("sha256")
        source = value.get("source")
        texture = value.get("texture")
        if (
            not isinstance(texture_hash, str)
            or len(texture_hash) != 64
            or source not in ("mod", "base_game")
            or not isinstance(texture, str)
            or not texture
        ):
            raise ValueError("invalid texture manifest row")
        by_hash.setdefault(
            texture_hash,
            {"sha256": texture_hash, "source": source, "texture": texture},
        )
    return [by_hash[key] for key in sorted(by_hash)]


def _decode_texture(
    decoder: str,
    source_path: Path,
    texture_hash: str,
    staging: Path,
) -> None:
    decode_directory = staging / ("decode-" + texture_hash)
    decode_directory.mkdir(parents=True)
    try:
        subprocess.run(
            [decoder, str(source_path), str(decode_directory)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        suffix = f": {detail}" if detail else ""
        raise RuntimeError(f"texture decoder failed for {source_path.name}{suffix}") from exc
    decoded = decode_directory / (source_path.stem + ".png")
    if not decoded.is_file():
        raise RuntimeError(f"texture decoder did not produce {decoded.name}")
    data = decoded.read_bytes()
    if len(data) <= len(PNG_SIGNATURE) or not data.startswith(PNG_SIGNATURE):
        raise RuntimeError(f"texture decoder produced an invalid PNG for {source_path.name}")
    shutil.copyfile(decoded, staging / (texture_hash + ".png"))
    shutil.rmtree(decode_directory)


def _replace_directory(staging: Path, output_dir: Path, temporary_root: Path) -> None:
    previous = temporary_root / "previous"
    had_previous = output_dir.exists()
    if had_previous:
        output_dir.rename(previous)
    try:
        staging.rename(output_dir)
    except BaseException:
        if had_previous and previous.exists() and not output_dir.exists():
            previous.rename(output_dir)
        raise


def publish_web_assets(
    texture_manifest: Path,
    mod_root: Path,
    images_archive: Path,
    source_manifest: Path,
    output_dir: Path,
    decoder: str = "ktech",
) -> List[Path]:
    """Decode every referenced unique texture before replacing the public set."""

    decoder_path = _resolve_decoder(decoder)
    textures = _load_textures(texture_manifest)
    mod_root = Path(mod_root)
    images_archive = Path(images_archive)
    source_manifest = Path(source_manifest)
    output_dir = Path(output_dir)
    base_textures = [item for item in textures if item["source"] == "base_game"]
    if base_textures:
        verify_snapshot_archive(images_archive, source_manifest)

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".game-assets-", dir=str(output_dir.parent)
    ) as tmp:
        temporary_root = Path(tmp)
        staging = temporary_root / "staging"
        staging.mkdir()
        archive = ZipFile(images_archive) if base_textures else None
        try:
            for item in textures:
                texture_hash = item["sha256"]
                texture = item["texture"]
                if item["source"] == "mod":
                    source_path = mod_root / texture
                    if not source_path.is_file():
                        raise FileNotFoundError(source_path)
                    _decode_texture(decoder_path, source_path, texture_hash, staging)
                    continue
                assert archive is not None
                try:
                    texture_bytes = archive.read(texture)
                except KeyError as exc:
                    raise FileNotFoundError(
                        f"{texture} is missing from {images_archive}"
                    ) from exc
                extracted = temporary_root / "base-inputs" / texture_hash / Path(texture).name
                extracted.parent.mkdir(parents=True)
                extracted.write_bytes(texture_bytes)
                _decode_texture(decoder_path, extracted, texture_hash, staging)
        finally:
            if archive is not None:
                archive.close()
        _replace_directory(staging, output_dir, temporary_root)

    return [output_dir / (item["sha256"] + ".png") for item in textures]
