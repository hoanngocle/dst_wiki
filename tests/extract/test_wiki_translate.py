import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from typing import Optional

from tools.extract.wiki_translate import build_summary_translation_cache


class WikiTranslateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.pages = self.root / "pages"
        self.pages.mkdir()
        self.output = self.root / "summary_vi.json"

    def tearDown(self):
        self.temporary.cleanup()

    def _write_page(self, page_id: int, html: str, summary: Optional[str] = None):
        value = {"pageId": page_id, "html": html}
        if summary is not None:
            value["summaryViHtml"] = summary
        (self.pages / f"{page_id}.json").write_text(
            json.dumps(value, ensure_ascii=False), encoding="utf-8"
        )

    def test_translates_leads_and_preserves_matching_vietnamese_cache(self):
        self._write_page(
            10,
            "<p><i>Exclusive to:</i><br><i>Only during the Event:</i> Test Event"
            "<br>A nugget of gold used for crafting.</p>"
            "<h2>Usage</h2>",
        )
        self._write_page(
            11,
            "<p>Nightmare Fuel is a refined item.</p>",
            "<h2>Tóm tắt</h2><p>Nhiên liệu dùng cho ma thuật hắc ám.</p>",
        )
        nightmare_source = "Nightmare Fuel is a refined item."
        self.output.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "pages": {
                        "11": {
                            "source": nightmare_source,
                            "source_sha256": hashlib.sha256(
                                nightmare_source.encode("utf-8")
                            ).hexdigest(),
                            "vi": "Nhiên liệu dùng cho ma thuật hắc ám.",
                        }
                    },
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        translated_sources = []

        def translate(source: str) -> str:
            translated_sources.append(source)
            return "Một cục vàng."

        summary = build_summary_translation_cache(
            self.pages, self.output, translate=translate, workers=1
        )
        value = json.loads(self.output.read_text(encoding="utf-8"))

        self.assertEqual(summary, {"pages": 2, "cached": 1, "translated": 1})
        self.assertEqual(translated_sources, ["A nugget of gold used for crafting."])
        self.assertEqual(value["pages"]["10"]["vi"], "Một cục vàng.")
        self.assertEqual(
            value["pages"]["11"]["vi"],
            "Nhiên liệu dùng cho ma thuật hắc ám.",
        )

    def test_reuses_matching_cache_and_retranslates_changed_source(self):
        old_source = "An old description."
        self._write_page(10, "<p>A new description.</p>")
        self.output.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "pages": {
                        "10": {
                            "source": old_source,
                            "source_sha256": hashlib.sha256(
                                old_source.encode("utf-8")
                            ).hexdigest(),
                            "vi": "Mô tả cũ.",
                        }
                    },
                }
            ),
            encoding="utf-8",
        )

        build_summary_translation_cache(
            self.pages,
            self.output,
            translate=lambda source: "Mô tả mới.",
            workers=1,
        )
        value = json.loads(self.output.read_text(encoding="utf-8"))

        self.assertEqual(value["pages"]["10"]["source"], "A new description.")
        self.assertEqual(value["pages"]["10"]["vi"], "Mô tả mới.")

    def test_retranslates_known_boilerplate_translation(self):
        source = "The Ancient Remains are found within the Sanctum."
        self._write_page(10, f"<p>{source}</p>")
        self.output.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "pages": {
                        "10": {
                            "source": source,
                            "source_sha256": hashlib.sha256(
                                source.encode("utf-8")
                            ).hexdigest(),
                            "vi": "Dành riêng cho: Di tích cổ xưa nằm trong Sanctum.",
                        }
                    },
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        build_summary_translation_cache(
            self.pages,
            self.output,
            translate=lambda value: "Di tích cổ xưa nằm trong Sanctum.",
            workers=1,
        )

        value = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(value["pages"]["10"]["vi"], "Di tích cổ xưa nằm trong Sanctum.")

    def test_uses_manual_summary_for_page_without_article_lead(self):
        (self.pages / "10.json").write_text(
            json.dumps(
                {
                    "pageId": 10,
                    "html": "<h2>Contents</h2><table></table>",
                    "plainText": "Contents 1 Wall 2 Post 3 Lamp",
                }
            ),
            encoding="utf-8",
        )
        manual = self.root / "manual.json"
        manual.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "pages": {"10": "Danh sách công trình của sự kiện."},
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        summary = build_summary_translation_cache(
            self.pages,
            self.output,
            translate=lambda source: self.fail("manual summary must not be translated"),
            workers=1,
            manual_path=manual,
        )
        value = json.loads(self.output.read_text(encoding="utf-8"))

        self.assertEqual(summary, {"pages": 1, "cached": 1, "translated": 0})
        self.assertEqual(value["pages"]["10"]["vi"], "Danh sách công trình của sự kiện.")
