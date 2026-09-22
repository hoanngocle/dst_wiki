"""Deterministic 1536x1024 UI review renderer.

The renderer mirrors the in-game fit-to-safe-area contract. Individual screen
layouts are registered incrementally as the Lua panels are rebuilt.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

DESIGN = (1536, 1024)
BG = (10, 12, 20, 255)
PANEL = (19, 23, 36, 250)
SILVER = (195, 205, 224, 255)
PURPLE = (126, 78, 207, 255)
CYAN = (98, 192, 250, 255)


def font(size: int) -> ImageFont.FreeTypeFont:
    source = Path(__file__).parents[2] / "mods/PhamNhanTuTien/fonts/source/NotoSerif-Medium.ttf"
    return ImageFont.truetype(str(source), size)


def theme_preview() -> Image.Image:
    image = Image.new("RGBA", DESIGN, BG)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((64, 54, 1472, 970), 22, fill=PANEL, outline=SILVER, width=3)
    draw.polygon(((768, 28), (794, 54), (768, 80), (742, 54)), fill=PURPLE, outline=SILVER)
    draw.text((768, 118), "PHÀM NHÂN TU TIÊN", font=font(52), fill=SILVER, anchor="mm")
    draw.text((768, 190), "ARTIFACT UI • 1536 × 1024", font=font(28), fill=CYAN, anchor="mm")
    draw.line((136, 246, 1400, 246), fill=CYAN, width=2)
    for index, (name, colour) in enumerate((
        ("NềN", BG), ("PANEL", PANEL), ("BẠC", SILVER), ("TÍM", PURPLE), ("CYAN", CYAN)
    )):
        x = 244 + index * 260
        draw.rounded_rectangle((x - 82, 340, x + 82, 504), 16, fill=colour, outline=SILVER, width=2)
        draw.text((x, 548), name, font=font(24), fill=SILVER, anchor="mm")
    draw.text((768, 726), "Tiếng Việt: Cường hóa • Thần Binh Phổ • Kế Thừa", font=font(34), fill=SILVER, anchor="mm")
    draw.text((768, 812), "Fit-to-safe-area • không crop • không scale lồng nhau", font=font(25), fill=CYAN, anchor="mm")
    return image


def shell_preview() -> Image.Image:
    reference = Path(__file__).parents[1] / "pham-nhan-unified-ui/trang-bi-phac-thao.png"
    return Image.open(reference).convert("RGBA")


def artifact_preview(relative: str):
    def render() -> Image.Image:
        return Image.open(Path(__file__).parents[1] / relative).convert("RGBA")
    return render


def unified_canvas(active: int, title: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = shell_preview().copy()
    draw = ImageDraw.Draw(image)
    draw.rectangle((132, 286, 1404, 900), fill=(12, 14, 23, 255))
    tabs = ("Nhan vat", "Trang bi", "Nhiem vu", "Quan doan", "Cua hang", "Kho")
    for index, label in enumerate(tabs):
        x1 = 142 + index * 203
        fill = (164, 116, 216, 255) if index == active else (25, 22, 32, 255)
        draw.rectangle((x1, 178, x1 + 194, 226), fill=fill, outline=SILVER, width=2)
        draw.text((x1 + 97, 202), label, font=font(24), fill=(18, 16, 24, 255) if index == active else SILVER, anchor="mm")
    draw.text((768, 320), title, font=font(38), fill=SILVER, anchor="mm")
    draw.line((190, 354, 1346, 354), fill=CYAN, width=2)
    return image, draw


def character_preview() -> Image.Image:
    image, draw = unified_canvas(0, "NHAN VAT")
    draw.text((350, 408), "THUOC TINH", font=font(26), fill=CYAN, anchor="mm")
    rows = (("Suc manh", "18", "+1.5 sat thuong"), ("Nhanh nhen", "14", "+1.2% toc do"),
            ("The chat", "22", "+20 mau"), ("Cam quan", "12", "+1% chi mang"),
            ("Tri tue", "16", "+20 mana"))
    for i, (name, value, desc) in enumerate(rows):
        y = 470 + i * 76
        draw.rounded_rectangle((190, y - 28, 620, y + 28), 8, fill=(27, 27, 42, 255), outline=(92, 82, 115, 255), width=2)
        draw.text((214, y), name, font=font(23), fill=SILVER, anchor="lm")
        draw.text((475, y), value, font=font(24), fill=CYAN, anchor="mm")
        draw.text((602, y), desc, font=font(16), fill=(170, 170, 187, 255), anchor="rm")
    draw.line((700, 390, 700, 830), fill=(92, 82, 115, 255), width=2)
    draw.rounded_rectangle((770, 418, 1260, 650), 16, fill=(22, 21, 34, 255), outline=SILVER, width=2)
    draw.text((1015, 462), "CAP 35  •  RANK A", font=font(27), fill=CYAN, anchor="mm")
    draw.text((1015, 522), "EXP 7,850 / 10,000", font=font(23), fill=SILVER, anchor="mm")
    draw.rectangle((835, 554, 1195, 570), fill=(49, 45, 62, 255))
    draw.rectangle((835, 554, 1118, 570), fill=PURPLE)
    draw.text((1015, 610), "Diem tiem nang: 4", font=font(24), fill=(255, 215, 76, 255), anchor="mm")
    draw.rounded_rectangle((812, 700, 1218, 765), 8, fill=(75, 54, 112, 255), outline=SILVER, width=2)
    draw.text((1015, 732), "Thanh tuu • Mua • Dac quyen", font=font(22), fill=SILVER, anchor="mm")
    return image


SCREENS = {
    "theme": theme_preview,
    "shell": shell_preview,
    "summary-combine": artifact_preview("bang-tong-hop/v3/hop-thanh.png"),
    "summary-socket": artifact_preview("bang-tong-hop/v3/kham.png"),
    "forge-cleanse": artifact_preview("than-binh-pho/v4/thanh-tay.png"),
    "forge-stone-change": artifact_preview("than-binh-pho/v4/duc-linh.png"),
    "forge-inherit": artifact_preview("than-binh-pho/v4/ke-thua.png"),
    "strengthen-empty": artifact_preview("lam-phuong-ui/trong.png"),
    "strengthen-ready": artifact_preview("lam-phuong-ui/cuong-hoa.png"),
    "strengthen-protected": artifact_preview("lam-phuong-ui/bao-ve.png"),
    "strengthen-maxed": artifact_preview("lam-phuong-ui/toi-da.png"),
    "character": character_preview,
}


def fit(image: Image.Image, width: int, height: int) -> Image.Image:
    scale = min((width - 32) / image.width, (height - 32) / image.height, 1)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    output = Image.new("RGBA", (width, height), BG)
    output.alpha_composite(resized, ((width - resized.width) // 2, (height - resized.height) // 2))
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--screen", choices=sorted(SCREENS), required=True)
    parser.add_argument("--width", type=int, default=1536)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fit(SCREENS[args.screen](), args.width, args.height).convert("RGB").save(args.output)
    print(args.output.resolve())


if __name__ == "__main__":
    main()
