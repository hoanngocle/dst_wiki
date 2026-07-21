import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.crawl_wiki.state_paths import (
    CategoryStatePaths,
    StatePathError,
    resolve_category_state_paths,
)


class StatePathTests(unittest.TestCase):
    def test_resolves_absolute_git_common_directory(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            common = root / ".git"
            common.mkdir()
            completed = subprocess.CompletedProcess(
                ["git"], 0, stdout="{}\n".format(common), stderr=""
            )
            runner = mock.Mock(return_value=completed)

            paths = resolve_category_state_paths(root, runner=runner)

            self.assertEqual(
                paths.registry,
                common / "category-crawler/fandom-url-registry.json",
            )
            self.assertEqual(
                paths.cache,
                common / "category-crawler/shared-pages",
            )
            runner.assert_called_once_with(
                ["git", "rev-parse", "--git-common-dir"],
                cwd=str(root),
                check=False,
                capture_output=True,
                text=True,
            )

    def test_resolves_relative_git_common_directory_for_linked_worktree(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            worktree = root / "worktree"
            worktree.mkdir()
            common = root / "repo.git"
            common.mkdir()
            relative = Path("..") / common.name
            completed = subprocess.CompletedProcess(
                ["git"], 0, stdout="{}\n".format(relative), stderr=""
            )

            paths = resolve_category_state_paths(
                worktree,
                runner=mock.Mock(return_value=completed),
            )

            self.assertEqual(
                paths.registry,
                common.resolve() / "category-crawler/fandom-url-registry.json",
            )

    def test_returns_both_explicit_paths_without_running_git(self):
        runner = mock.Mock()

        paths = resolve_category_state_paths(
            Path("/unused"),
            registry=Path("state/registry.json"),
            cache=Path("state/cache"),
            runner=runner,
        )

        self.assertEqual(
            paths,
            CategoryStatePaths(Path("state/registry.json"), Path("state/cache")),
        )
        runner.assert_not_called()

    def test_requires_both_explicit_paths(self):
        with self.assertRaisesRegex(StatePathError, "together"):
            resolve_category_state_paths(
                Path.cwd(),
                registry=Path("state/registry.json"),
            )

    def test_rejects_failed_git_resolution(self):
        completed = subprocess.CompletedProcess(
            ["git"], 128, stdout="", stderr="not a repository"
        )
        with self.assertRaisesRegex(StatePathError, "cannot resolve"):
            resolve_category_state_paths(
                Path.cwd(),
                runner=mock.Mock(return_value=completed),
            )

    def test_rejects_missing_git_common_directory(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            completed = subprocess.CompletedProcess(
                ["git"],
                0,
                stdout="{}\n".format(root / "missing"),
                stderr="",
            )
            with self.assertRaisesRegex(StatePathError, "does not exist"):
                resolve_category_state_paths(
                    root,
                    runner=mock.Mock(return_value=completed),
                )


if __name__ == "__main__":
    unittest.main()
