import unittest

from tools.crawl_wiki.parser import (
    canonical_page_url,
    html_to_text,
    normalize_base_url,
    normalize_page,
    safe_image_extension,
)


class ParserTests(unittest.TestCase):
    def test_normalizes_base_and_unicode_page_urls(self):
        self.assertEqual(
            normalize_base_url("https://dontstarve.wiki.gg"),
            "https://dontstarve.wiki.gg/",
        )
        self.assertEqual(
            canonical_page_url(
                "https://dontstarve.wiki.gg/",
                "Category:Don't Starve Together",
            ),
            "https://dontstarve.wiki.gg/wiki/Category:Don%27t_Starve_Together",
        )

    def test_rejects_non_http_base_urls(self):
        with self.assertRaisesRegex(ValueError, "http"):
            normalize_base_url("file:///tmp/wiki")

    def test_converts_rendered_html_to_normalized_visible_text(self):
        value = (
            "<h2>Stats &amp; notes</h2><script>bad()</script>"
            "<p>Health: <b>150</b></p>"
        )
        self.assertEqual(html_to_text(value), "Stats & notes\nHealth: 150")

    def test_chooses_safe_extension_from_mime_before_url(self):
        self.assertEqual(
            safe_image_extension("https://cdn/x.php?name=x.exe", "image/png"),
            ".png",
        )
        self.assertEqual(
            safe_image_extension("https://cdn/x.WEBP", None), ".webp"
        )
        self.assertEqual(
            safe_image_extension("https://cdn/no-suffix", None), ".bin"
        )

    def test_normalizes_page_links_images_redirect_and_content(self):
        query_page = {
            "pageid": 7,
            "ns": 0,
            "title": "Wilson",
            "redirect": True,
            "revisions": [
                {
                    "revid": 11,
                    "timestamp": "2026-07-01T10:00:00Z",
                    "sha1": "abc",
                    "contentmodel": "wikitext",
                    "slots": {
                        "main": {
                            "content": "#REDIRECT [[Wilson (DST)]]"
                        }
                    },
                }
            ],
        }
        parsed = {
            "title": "Wilson",
            "displaytitle": "<b>Wilson</b>",
            "text": "<p>Redirect page</p>",
            "links": [
                {"ns": 0, "title": "Wilson (DST)", "exists": True},
                {"ns": 10, "title": "Template:Infobox"},
            ],
            "categories": [{"category": "Characters"}],
            "images": ["Wilson.png", "Wilson.png"],
        }

        page, links, images = normalize_page(
            query_page,
            parsed,
            "https://dontstarve.wiki.gg/",
            "2026-07-15T00:00:00Z",
            {0, 6, 14},
        )

        self.assertEqual(page["redirect_target"], "Wilson (DST)")
        self.assertEqual(page["categories"], ["Category:Characters"])
        self.assertEqual(page["images"], ["File:Wilson.png"])
        self.assertEqual(page["plain_text"], "Redirect page")
        self.assertEqual([link["in_scope"] for link in links], [True, False])
        self.assertEqual(images, {"File:Wilson.png"})


if __name__ == "__main__":
    unittest.main()
