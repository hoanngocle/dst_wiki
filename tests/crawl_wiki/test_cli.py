import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools.crawl_wiki.cli import build_parser, main
from tools.crawl_wiki.models import CrawlSummary


class CliTests(unittest.TestCase):
    def test_parser_has_safe_full_crawl_defaults(self):
        args = build_parser().parse_args([])
        self.assertEqual(args.base_url, "https://dontstarve.wiki.gg/")
        self.assertEqual(args.output, Path("data/crawled/dontstarve-wiki"))
        self.assertEqual(args.namespaces, (0, 14, 6))
        self.assertEqual(args.delay, 0.5)
        self.assertEqual(args.timeout, 30.0)
        self.assertEqual(args.max_attempts, 5)

    def test_invalid_arguments_exit_before_run(self):
        invalid = [
            ["--namespaces", "0,10"],
            ["--delay", "-1"],
            ["--timeout", "0"],
            ["--max-attempts", "0"],
            ["--max-pages", "0"],
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
