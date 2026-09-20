# Phàm Nhân Tu Tiên — Thần Binh Phổ

Implemented the approved charcoal/silver/amethyst EVA UI in `mods/PhamNhanTuTien`.

## Visual correction after user review

The first pass simplified the concept too far and used an Arial substitute in previews. Replaced the forge-only runtime font with bundled OFL Cormorant Garamond SemiBold, including all Vietnamese NFC glyphs. Native `TheSim:LoadFont` and `TextWidget` accepted it; the preview renderer now uses the exact shipped `font.tex` glyphs and `font.fnt` metrics. Native and preview sample bounds agree within 0.001 pixels. Client screenshot verification remains unperformed.

Generated a new four-control sprite sheet with built-in image_gen from the approved reference: chamfered dark/lavender tabs, feather-wrapped purple primary button and silver inventory frames. Replaced flat rectangle controls, enlarged preview framing, added ornamental separators and proper checkmarks. Fixed slot restrictions and crafting logic are unchanged.

Current previews are under `artifacts/than-binh-pho/v2/`. Sources/prompts: `mods/solo-assets-work/than-binh-pho/controls-provenance.json`; font build/source/license/validation are in the same work directory. Lua widget interaction checks, syntax, installed sprite names and Vietnamese glyph coverage pass after the correction.

### Attribute-row correction

### Current font: Noto Serif Medium (v4)

The user authorized a readable Vietnamese font closest to the concept. Replaced Cormorant Garamond with Noto Serif Medium (weight 500, width 95), bundled under the same `ttk_forge_serif` alias with its SIL OFL license. The atlas includes 429 glyphs and verifies complete precomposed Vietnamese coverage. Explicit UI arrows avoid missing-glyph boxes. Font source and build validation are in `mods/solo-assets-work/than-binh-pho/font-source/noto/` and `font-build/validation.json`.

Current previews are `artifacts/than-binh-pho/v4/`: all three tabs and `dong-thuoc-tinh.png`. They render the actual Lua layout and installed bitmap font/texture, with mock state; they are not client screenshots. Visually checked all three tabs for text fit; widget checks PASS after replacement. Earlier native font measurements refer to the previous Cormorant build; native client verification of Noto remains outstanding.

Font coverage follow-up: all three tabs share the Noto label/button helpers, including disabled buttons, status messages and counts. Slot hints and attribute hover descriptions now explicitly use the same font. Added both pagination chevrons to the bundled atlas (431 glyphs total). Rebuilt font and all three previews; widget checks PASS.

### Previous attribute-row preview (v3)

Latest previews: `artifacts/than-binh-pho/v3/`. Replaced the reused tab background with a dedicated image_gen asset derived from the user's cropped reference: muted purple fill, single thin notched border, large rounded lavender checkbox and gold trash marker. Text stays dynamic and left-aligned. The trash marker indicates selection only; deletion still requires the Thanh Tẩy action. Larger rows show three entries per page; a regression verifies that choosing the fourth attribute on page two submits the correct original index. Source/prompt: `mods/solo-assets-work/than-binh-pho/effect-row-provenance.json`.

- Three tabs: Thanh Tẩy, Đúc Linh, Kế Thừa. Native inventory slots retain drag/drop and item tooltips. Upper box is explicitly a preview; receiving gear B has a labelled input below.
- Fixed ingredient slots display current inventory artwork at 28% alpha when empty. Client and server restrict every slot by the replicated active tab.
- Bùa Tẩy remains the existing virtual `ad_cleanStone` balance. Its illustrated currency tile is not a physical drop target.
- Tab changes return ingredients to inventory, with safe nearby drops if both inventory and cursor are full. Current and legacy container saves retain their contents.
- Actions validate ownership, distance, current tab, ingredients and snapshot revision. Item identity uses network IDs across peers. Pending UI actions wait for an authoritative snapshot.
- Inheritance rejects incompatible attributes before consuming the donor. Existing ingredient costs and effect-stone reward probabilities are preserved.
- Display names changed without changing prefabs, RPC identifiers, save keys or routes.

## Artwork and previews

Production frame generated with built-in image_gen, compiled with Klei TextureConverter; source and prompt provenance are in `mods/solo-assets-work/than-binh-pho/`. Initial checkerboard output was replaced through image_gen with an opaque charcoal surround before installation.

Installed atlas: `mods/PhamNhanTuTien/images/ttk_forge/frame.xml` and `frame.tex`.

Actual Lua layout and installed texture previews: `artifacts/than-binh-pho/thanh-tay.png`, `duc-linh.png`, `ke-thua.png`. These use a substitute font and mock item/state data; they are not client screenshots. Native client visual/input QA remains unperformed. Existing shift-transfer rejection is retained; drag items into the labelled slots.

## Verification

- `tools/test_ttk_forge_backend.py`: PASS, including strict filters, item preservation, costs, output, access validation, compatibility rejection, replay/missing-revision rejection, cooldown acknowledgment and Lua syntax.
- `mods/solo-assets-work/than-binh-pho/test_ui.py`: PASS; tests actual widget logic, deferred tab acknowledgment, faded/hidden ghosts, insufficient materials, rare-stone rejection, stale selection reset, network IDs different from local GUIDs, and action remaining disabled beyond four seconds without acknowledgment.
- `mods/solo-assets-work/than-binh-pho/native-smoke.log`: `TTK_FORGE_PASS` at 00:00:54. Real dedicated-server prefab/network setup, full-inventory overflow, reroll output/cost, new/legacy saves, inheritance donor/recipient/cost and virtual cleanse verified.
- Independent review: no remaining blocking findings after network identity and revision fixes.
- CodeGraph 1.6.0 index refreshed; impact for `UpdateForgeState` identifies player actions/RPC and container events (8 nodes, 10 edges). Static call graph is supplementary to runtime checks.

## Verified hh_essence acquisition

- Craft 1 Linh Thạch from 1 Giấy Thuộc Tính (`hh_effect_tally`) + 2 Lục Bảo Thạch (`hh_remove_stone`), TECH.NONE: `main/hh_recipe.lua`.
- Put attribute stones in Túi Mèo (`hh_cat_box`) and press Đổi: common/no-effect stone yields 1; non-common stone yields 5. `main/hh_ui.lua` and `scripts/enums/hh_prefabs.lua`.
- Dungeon boss reward chest includes 4 when max_waves <= 5, otherwise 5: `scripts/components/dungeon_manager.lua`.
- Guild rank B/A quest rewards include 60/80 respectively: `scripts/guild/hh_rank_exam_defs.lua`.
- `hh_essence` is distinct from `ttk_lingshi1` (Hạ Phẩm Linh Thạch). Only `hh_essence` fits Thần Binh Phổ's Linh Thạch slots.
