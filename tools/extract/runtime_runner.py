import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import List

from tools.extract.runtime_import import load_runtime_bundle, read_runtime_json_bytes


SENTINEL = "DST_WIKI_EXTRACT_COMPLETE"


class RuntimeProbeError(RuntimeError):
    pass


def assert_within_workspace(workspace: Path, candidate: Path) -> None:
    workspace = Path(workspace).resolve()
    candidate = Path(candidate).resolve()
    try:
        candidate.relative_to(workspace)
    except ValueError as exc:
        raise ValueError(f"path is outside workspace: {candidate}") from exc


def _probe_ports(run_id: str):
    base = 20000 + (int(run_id[:8], 16) % 39995)
    return base, base + 1, base + 2


def _write_cluster_config(
    persistent_root: Path,
    cluster_name: str,
    core_mod: str,
    probe_mod: str,
    run_id: str,
) -> None:
    cluster = persistent_root / "DoNotStarveTogether" / cluster_name
    shard = cluster / "Master"
    shard.mkdir(parents=True)
    cluster.joinpath("cluster.ini").write_text(
        "[GAMEPLAY]\n"
        "game_mode = survival\n"
        "max_players = 1\n"
        "pause_when_empty = false\n"
        "pvp = false\n"
        "[NETWORK]\n"
        "cluster_name = DST Wiki Runtime Probe\n"
        "cluster_intention = cooperative\n"
        "lan_only_cluster = true\n"
        "offline_cluster = true\n"
        "[MISC]\n"
        "console_enabled = true\n"
        "[SHARD]\n"
        "shard_enabled = false\n",
        encoding="utf-8",
    )
    server_port, master_port, auth_port = _probe_ports(run_id)
    shard.joinpath("server.ini").write_text(
        "[NETWORK]\n"
        f"server_port = {server_port}\n"
        "[SHARD]\n"
        "is_master = true\n"
        "[STEAM]\n"
        f"master_server_port = {master_port}\n"
        f"authentication_port = {auth_port}\n",
        encoding="utf-8",
    )
    shard.joinpath("modoverrides.lua").write_text(
        "return {\n"
        f'    ["{core_mod}"] = {{ enabled = true }},\n'
        f'    ["{probe_mod}"] = {{ enabled = true }},\n'
        "}\n",
        encoding="utf-8",
    )


def _terminate_started_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def _log_tail(path: Path, limit: int = 8000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return text[-limit:]


def _wait_for_sentinel(
    process: subprocess.Popen, log_path: Path, timeout_seconds: float
) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if SENTINEL in _log_tail(log_path):
            return
        return_code = process.poll()
        if return_code is not None:
            raise RuntimeProbeError(
                f"dedicated server exited with code {return_code} before sentinel\n"
                f"{_log_tail(log_path)}"
            )
        time.sleep(0.1)
    raise RuntimeProbeError(
        f"runtime probe timed out after {timeout_seconds} seconds\n{_log_tail(log_path)}"
    )


def _find_runtime_json(persistent_root: Path) -> Path:
    candidates = sorted(
        path
        for path in persistent_root.rglob("runtime.json")
        if path.is_file()
    )
    if len(candidates) != 1:
        raise RuntimeProbeError(
            f"expected exactly one runtime.json under {persistent_root}, found {len(candidates)}"
        )
    load_runtime_bundle(candidates[0])
    return candidates[0]


def run_runtime_probe(
    server_bin: Path,
    game_mods_dir: Path,
    workspace: Path,
    timeout_seconds: float,
) -> Path:
    """Run the exporter in an isolated cluster and return the validated raw output."""

    workspace = Path(workspace).resolve()
    server_bin = Path(server_bin).resolve()
    game_mods_dir = Path(game_mods_dir).resolve()
    if not server_bin.is_file():
        raise FileNotFoundError(f"dedicated server not found: {server_bin}")
    if not game_mods_dir.is_dir():
        raise FileNotFoundError(f"game mods directory not found: {game_mods_dir}")
    core_source = workspace / "mod/3721846643"
    probe_source = workspace / "tools/runtime_mod"
    if not core_source.is_dir() or not probe_source.is_dir():
        raise FileNotFoundError("runtime probe requires mod/3721846643 and tools/runtime_mod")

    run_id = uuid.uuid4().hex
    core_name = f"dst_wiki_core_{run_id}"
    probe_name = f"dst_wiki_probe_{run_id}"
    persistent_root = workspace / "data/runtime" / f"probe-{run_id}"
    assert_within_workspace(workspace, persistent_root)
    persistent_root.mkdir(parents=True)
    cluster_name = f"DSTWikiProbe-{run_id}"
    _write_cluster_config(
        persistent_root, cluster_name, core_name, probe_name, run_id
    )
    log_path = persistent_root / "server.log"
    copied: List[Path] = []
    process = None
    temporary = None
    try:
        for source, name in ((core_source, core_name), (probe_source, probe_name)):
            target = game_mods_dir / name
            if target.exists():
                raise RuntimeProbeError(f"refusing to replace existing game mod: {target}")
            copied.append(target)
            shutil.copytree(source, target, symlinks=False)

        command = [
            str(server_bin),
            "-persistent_storage_root",
            str(persistent_root),
            "-conf_dir",
            "DoNotStarveTogether",
            "-cluster",
            cluster_name,
            "-shard",
            "Master",
            "-offline",
            "-lan",
            "-skip_update_server_mods",
        ]
        with log_path.open("wb") as log_handle:
            process = subprocess.Popen(
                command,
                cwd=server_bin.parent,
                stdin=subprocess.DEVNULL,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
            )
            try:
                _wait_for_sentinel(process, log_path, timeout_seconds)
            finally:
                _terminate_started_process(process)

        runtime_path = _find_runtime_json(persistent_root)
        destination = workspace / "data/raw/runtime.json"
        assert_within_workspace(workspace, destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(f".{destination.name}.{run_id}.tmp")
        temporary.write_bytes(read_runtime_json_bytes(runtime_path))
        load_runtime_bundle(temporary)
        temporary.replace(destination)
        return destination
    finally:
        if process is not None:
            _terminate_started_process(process)
        if temporary is not None and temporary.is_file():
            temporary.unlink()
        for target in reversed(copied):
            if (
                target.parent == game_mods_dir
                and target.name in {core_name, probe_name}
                and target.is_dir()
            ):
                shutil.rmtree(target)
