import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ARCHIVES = ("scripts.zip", "images.zip")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_game_sources(game_data: Path, destination: Path) -> dict:
    destination.mkdir(parents=True, exist_ok=True)
    files = {}
    for name in ARCHIVES:
        source = game_data / "databundles" / name
        if not source.is_file():
            raise FileNotFoundError(source)

        target = destination / name
        temporary = destination / (name + ".partial")
        shutil.copyfile(source, temporary)
        source_hash = _sha256(source)
        copied_hash = _sha256(temporary)
        if source.stat().st_size != temporary.stat().st_size or source_hash != copied_hash:
            temporary.unlink(missing_ok=True)
            raise IOError(f"copy verification failed: {name}")

        temporary.replace(target)
        files[name] = {
            "size": target.stat().st_size,
            "sha256": copied_hash,
        }

    manifest = {
        "schema_version": 1,
        "copied_at": datetime.now(timezone.utc).isoformat(),
        "files": files,
    }
    (destination / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest
