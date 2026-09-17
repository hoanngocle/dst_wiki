import struct
import unittest

from tools.extract.publish_solo_leveling_assets import decode_ktex


def texture(format_id, width, height, payload):
    specification = (format_id << 4) | (1 << 13)
    return b'KTEX' + struct.pack('<IHHHI', specification, width, height, width * 4, len(payload)) + payload


class SoloTextureTests(unittest.TestCase):
    def test_rgba_is_flipped_and_unpremultiplied(self):
        image = decode_ktex(texture(4, 1, 2, bytes([64, 0, 0, 128, 0, 255, 0, 255])))
        self.assertEqual(image.getpixel((0, 0)), (0, 255, 0, 255))
        self.assertEqual(image.getpixel((0, 1)), (127, 0, 0, 128))

    def test_dxt5_block_uses_correct_decoder(self):
        # Fully opaque block selecting RGB565 red as color zero for every pixel.
        payload = bytes([255, 255]) + bytes(6) + struct.pack('<HHI', 0xf800, 0, 0)
        image = decode_ktex(texture(2, 4, 4, payload))
        self.assertEqual(image.getpixel((2, 1)), (255, 0, 0, 255))

    def test_corrupt_or_unknown_payloads_are_rejected(self):
        for data in (b'KTEX', texture(4, 3, 3, bytes(4)), texture(9, 4, 4, bytes(16)), texture(2, 4, 4, bytes(16))[:-1]):
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    decode_ktex(data)


if __name__ == '__main__':
    unittest.main()
