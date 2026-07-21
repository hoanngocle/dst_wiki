import json
import tempfile
import unittest
from pathlib import Path

from tests.extract.test_category_mobs import animals_config, page
from tools.extract.category_mobs import normalize_category_mobs
from tools.extract.category_notes import build_note_review, sha256_text
from tools.extract.cli import build_parser


class CategoryNoteTests(unittest.TestCase):
    def test_extract_cli_exposes_category_note_and_normalize_commands(self):
        notes = build_parser().parse_args(
            ["category-notes", "--category", "animals"]
        )
        normalize = build_parser().parse_args(
            ["normalize-category", "--category", "animals"]
        )

        self.assertEqual(notes.command, "category-notes")
        self.assertEqual(notes.category, "animals")
        self.assertEqual(normalize.command, "normalize-category")
        self.assertEqual(normalize.category, "animals")

    def test_note_review_keeps_dst_gameplay_and_drops_patch_trivia(self):
        bunnyman = page(
            208,
            "Bunnyman",
            """
{{Mob Infobox|spawnCode=bunnyman|health={{DST|200}}}}
== Notes ==
* Turns into a Beardlord below 40% Sanity.<ref>gameplay</ref>
* Added in the March 2020 update.
* In Hamlet, it used a different animation.
== Trivia ==
* Its design changed during development.
""",
        )

        review = build_note_review([bunnyman], animals_config())

        source = "Turns into a Beardlord below 40% Sanity."
        self.assertEqual(review["pages"]["208"]["source"], source)
        self.assertEqual(
            review["pages"]["208"]["source_sha256"],
            sha256_text(source),
        )

    def test_normalizer_rejects_unreviewed_source_note(self):
        bunnyman = page(
            208,
            "Bunnyman",
            """
{{Mob Infobox|spawnCode=bunnyman|health={{DST|200}}}}
== Notes ==
* Turns into a Beardlord below 40% Sanity.
""",
        )
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "pages.jsonl").write_text(
                json.dumps(bunnyman) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "reviewed Vietnamese summary"):
                normalize_category_mobs(
                    root,
                    animals_config(),
                    mappings={},
                    summaries={},
                )


if __name__ == "__main__":
    unittest.main()
