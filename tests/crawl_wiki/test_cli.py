import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools.crawl_wiki.cli import (
    build_parser,
    main,
    resolve_base_url,
    resolve_output,
    run_crawl,
)
from tools.crawl_wiki.models import CrawlSummary


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
