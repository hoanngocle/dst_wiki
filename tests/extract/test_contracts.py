import tempfile
import unittest
from pathlib import Path

from tools.extract.contracts import EntityKey, Fact, FactBundle, SourceRef, dump_bundle, load_bundle


class ContractTests(unittest.TestCase):
    def test_bundle_round_trip_is_deterministic(self):
        source = SourceRef("mod-static", "mod_static", "mod/3721846643/scripts/main/strings.lua", "18.0.10", "abc")
        fact = Fact("name", EntityKey("tu_tien", "xd_lingshi1"), {"lang": "vi", "value": "Hạ Phẩm Linh Thạch"}, source, 1.0)
        bundle = FactBundle(1, [source], [fact], [])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "facts.json"
            dump_bundle(path, bundle)
            first = path.read_bytes()
            self.assertEqual(load_bundle(path), bundle)
            dump_bundle(path, bundle)
            self.assertEqual(path.read_bytes(), first)


if __name__ == "__main__":
    unittest.main()
