import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import ANY, patch

from tools.crawl_wiki.cli import (
    build_parser,
    main,
    resolve_base_url,
    resolve_output,
    run_crawl,
)
from tools.crawl_wiki.models import CrawlSummary
from tools.crawl_wiki.state_paths import CategoryStatePaths
from tools.crawl_wiki.url_registry import RegistryAudit


class CliTests(unittest.TestCase):
    def test_parser_has_safe_full_crawl_defaults(self):
        args = build_parser().parse_args([])
        self.assertEqual(args.base_url, "https://dontstarve.wiki.gg/")
        self.assertIsNone(args.output)
        self.assertEqual(
            resolve_output(args), Path("data/crawled/dontstarve-wiki")
        )
        self.assertEqual(args.namespaces, (0, 14, 6))
        self.assertEqual(args.delay, 0.5)
        self.assertEqual(args.timeout, 30.0)
        self.assertEqual(args.max_attempts, 5)

    def test_items_profile_defaults_to_selective_output_and_budget(self):
        args = build_parser().parse_args(["--profile", "items"])

        self.assertEqual(args.profile, "items")
        self.assertEqual(args.item_budget, 100)
        self.assertEqual(
            resolve_output(args), Path("data/crawled/dontstarve-items")
        )

    def test_category_profile_uses_configured_source_and_output(self):
        args = build_parser().parse_args(
            ["--profile", "category", "--category", "animals"]
        )

        self.assertEqual(
            resolve_base_url(args),
            "https://dontstarve.fandom.com/",
        )
        self.assertEqual(
            resolve_output(args),
            Path("data/crawled/fandom-categories/animals"),
        )
        self.assertEqual(args.page_budget, 100)
        self.assertIsNone(args.url_registry)
        self.assertIsNone(args.shared_page_cache)

    def test_category_crawl_uses_git_common_state_and_audits_it(self):
        args = build_parser().parse_args(
            ["--profile", "category", "--category", "animals"]
        )
        summary = CrawlSummary(34, 0, 34, 0)
        paths = CategoryStatePaths(Path("live.json"), Path("shared-pages"))
        with patch(
            "tools.crawl_wiki.cli.resolve_category_state_paths",
            return_value=paths,
        ) as resolve, patch("tools.crawl_wiki.cli.UrlRegistry") as registry, patch(
            "tools.crawl_wiki.cli.CrawlStorage"
        ) as storage, patch("tools.crawl_wiki.cli.MediaWikiClient"), patch(
            "tools.crawl_wiki.cli.CategoryCrawler"
        ) as crawler:
            registry.return_value.audit.return_value = ()
            crawler.return_value.run.return_value = summary

            result = run_crawl(args)

        self.assertEqual(result, summary)
        resolve.assert_called_once_with(ANY, registry=None, cache=None)
        registry.assert_called_once_with(
            Path("live.json"),
            Path("shared-pages"),
            "https://dontstarve.fandom.com",
        )
        registry.return_value.audit.assert_called_once_with()
        crawler.assert_called_once()
        storage.assert_called_once()

    def test_category_crawl_rejects_invalid_done_before_opening_storage(self):
        args = build_parser().parse_args(
            ["--profile", "category", "--category", "animals"]
        )
        invalid = RegistryAudit(
            "https://dontstarve.fandom.com/wiki/Beefalo",
            "Done",
            "missing",
        )
        with patch(
            "tools.crawl_wiki.cli.resolve_category_state_paths",
            return_value=CategoryStatePaths(Path("live.json"), Path("cache")),
        ), patch("tools.crawl_wiki.cli.UrlRegistry") as registry, patch(
            "tools.crawl_wiki.cli.CrawlStorage"
        ) as storage:
            registry.return_value.audit.return_value = (invalid,)

            with self.assertRaisesRegex(
                RuntimeError,
                "invalid Done",
            ):
                run_crawl(args)

        storage.assert_not_called()

    def test_registry_overrides_are_paired_and_category_only(self):
        category_args = build_parser().parse_args(
            [
                "--profile",
                "category",
                "--category",
                "animals",
                "--url-registry",
                "registry.json",
            ]
        )
        with self.assertRaisesRegex(RuntimeError, "together"):
            run_crawl(category_args)

        full_args = build_parser().parse_args(
            [
                "--url-registry",
                "registry.json",
                "--shared-page-cache",
                "cache",
            ]
        )
        with patch(
            "tools.crawl_wiki.cli.CrawlStorage",
            side_effect=AssertionError("storage must not open"),
        ), self.assertRaisesRegex(ValueError, "category profile"):
            run_crawl(full_args)

    def test_category_name_is_required_only_for_category_profile(self):
        args = build_parser().parse_args(["--profile", "category"])

        with self.assertRaisesRegex(ValueError, "--category is required"):
            run_crawl(args)

    def test_rejects_explicit_item_budget_for_full_profile(self):
        args = build_parser().parse_args(
            ["--profile", "full", "--item-budget", "5"]
        )

        with self.assertRaisesRegex(ValueError, "items profile"):
            run_crawl(args)

    def test_invalid_arguments_exit_before_run(self):
        invalid = [
            ["--namespaces", "0,10"],
            ["--delay", "-1"],
            ["--timeout", "0"],
            ["--max-attempts", "0"],
            ["--max-pages", "0"],
            ["--item-budget", "0"],
            ["--base-url", "file:///tmp/wiki"],
        ]
        for argv in invalid:
            with self.subTest(argv=argv), patch(
                "tools.crawl_wiki.cli.run_crawl"
            ) as run_crawl, redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    main(argv)
                self.assertEqual(raised.exception.code, 2)
                run_crawl.assert_not_called()

    def test_maps_summary_to_exit_code_and_prints_counts(self):
        stdout = io.StringIO()
        with patch(
            "tools.crawl_wiki.cli.run_crawl",
            return_value=CrawlSummary(3, 1, 7, 0),
        ), redirect_stdout(stdout):
            self.assertEqual(main(["--output", "/tmp/wiki-output"]), 0)
        self.assertIn("pages=3 images=1 links=7 failures=0", stdout.getvalue())

        with patch(
            "tools.crawl_wiki.cli.run_crawl",
            return_value=CrawlSummary(2, 0, 4, 1),
        ), redirect_stdout(io.StringIO()):
            self.assertEqual(main([]), 1)

    def test_maps_interrupt_and_fatal_setup_error(self):
        with patch(
            "tools.crawl_wiki.cli.run_crawl", side_effect=KeyboardInterrupt
        ), redirect_stderr(io.StringIO()):
            self.assertEqual(main([]), 130)

        stderr = io.StringIO()
        with patch(
            "tools.crawl_wiki.cli.run_crawl", side_effect=OSError("disk full")
        ), redirect_stderr(stderr):
            self.assertEqual(main([]), 2)
        self.assertIn("disk full", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
