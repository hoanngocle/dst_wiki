import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional


class StatePathError(RuntimeError):
    pass


@dataclass(frozen=True)
class CategoryStatePaths:
    registry: Path
    cache: Path


def resolve_category_state_paths(
    cwd: Path,
    registry: Optional[Path] = None,
    cache: Optional[Path] = None,
    runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> CategoryStatePaths:
    if (registry is None) != (cache is None):
        raise StatePathError(
            "registry and cache overrides must be provided together"
        )
    if registry is not None and cache is not None:
        return CategoryStatePaths(Path(registry), Path(cache))

    working_directory = Path(cwd)
    result = runner(
        ["git", "rev-parse", "--git-common-dir"],
        cwd=str(working_directory),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise StatePathError("cannot resolve Git common directory")

    common = Path(result.stdout.strip())
    if not common.is_absolute():
        common = (working_directory / common).resolve()
    if not common.is_dir():
        raise StatePathError("Git common directory does not exist")

    root = common / "category-crawler"
    return CategoryStatePaths(
        registry=root / "fandom-url-registry.json",
        cache=root / "shared-pages",
    )
