# Phàm Nhân Full UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the complete Phàm Nhân presentation layer with the approved artifact visual system while preserving all existing Solo/Phàm Nhân gameplay, RPC, container, ownership, and save behavior.

**Architecture:** Keep the original Solo container and screen lifecycle as the behavioral boundary. A shared artifact theme and widget primitive module renders every panel; `TTKUnifiedScreen` coordinates navigation and input without re-parenting native `ContainerWidget` instances. Each screen is completed with a focused RED→GREEN test and a rendered PNG checkpoint before the next screen starts.

**Tech Stack:** Don't Starve Together Lua 5.1 UI APIs, Python 3, Pillow, Lupa Lua 5.1 test harness, Klei TextureConverter, repository artifact renderers.

**Spec:** `docs/superpowers/specs/2026-09-22-pham-nhan-full-ui-redesign.md`

## Global Constraints

- `artifacts/` latest-version images are the visual source of truth; `v3` wins for Bảng Tổng Hợp and `v4` wins for Thần Binh Phổ.
- The 1536×1024 artifact size is reference geometry only, never a fixed runtime canvas.
- Preserve existing prefab, component, netvar, RPC, payload, save, item-rule, probability, ownership, lock, stock, quest, army, level, and achievement behavior.
- Preserve all existing `ttk_` and `hh_` identifiers.
- Each rendered surface has exactly one `SCALEMODE_PROPORTIONAL` root and remains centered with `ANCHOR_MIDDLE`.
- Never re-parent a native `ContainerWidget` into another proportional root.
- Keep the original Solo forge-slot scale baseline of `0.7`; do not restore the broken `1.05` scale.
- Use the licensed Vietnamese serif source and Klei-compatible font channel metadata.
- Do not use a full concept screenshot as an interactive background.
- Preserve unrelated dirty files, including `.superpowers/brainstorm/.last-port` and `mods/PhamNhanTuTien/tests/hud/test_damage_number.lua`.

## Review Focus

- A 1024×768 or narrower viewport must shrink the complete frame without clipping the close button, bottom action button, dialogs, or native slots; Task 2 adds this bound test.
- Font load failure must select a DST fallback without publishing the custom alias or rendering block glyphs; Task 1 adds this lifecycle test.
- Switching tabs during a pending native open must close/cancel only the previous request and must not strand locked items; Task 2 adds this serialization test.
- Closing any container through mouse, controller cancel, or tab change must clear registry/focus/open flags exactly once; Tasks 2 and 10 add these lifecycle tests.
- Empty, delayed, maximum-level, insufficient-resource, and server-rejected states must remain readable and actionable; Tasks 3–10 add state-specific render assertions.

---

### Task 1: Artifact theme, font, and render harness

**Files:**
- Modify: `mods/PhamNhanTuTien/tools/build_forge_font.py`
- Modify: `mods/PhamNhanTuTien/main/ttk_forge_fonts.lua`
- Modify: `mods/PhamNhanTuTien/scripts/widgets/hh_ui/ttk_unified_theme.lua`
- Create: `mods/PhamNhanTuTien/scripts/widgets/hh_ui/ttk_artifact_primitives.lua`
- Modify: `mods/PhamNhanTuTien/tests/ui/test_forge_fonts.lua`
- Create: `mods/PhamNhanTuTien/tests/ui/test_artifact_theme.lua`
- Modify: `mods/PhamNhanTuTien/tools/test_unified_ui.py`
- Create: `artifacts/pham-nhan-ui-runtime/render.py`

**Interfaces:**
- Consumes: licensed `fonts/source/NotoSerif-Medium.ttf`, `images/ttk_forge/frame.xml`, `controls.xml`, `effect_row.xml`.
- Produces: `Theme.GetFont()`, `Theme.GetSurfaceScale(kind)`, and primitive constructors `Frame`, `Label`, `Button`, `Divider`, `SlotSkin`; `render.py --screen NAME --width W --height H --output PATH`.

- [ ] **Step 1: Write failing font and theme tests**

Add assertions that inspect the generated `font.fnt`, exercise successful and failed `LoadFont`, and verify the theme resolves the alias lazily:

```lua
assert(font_common.alphaChnl == "1")
assert(font_common.redChnl == "0" and font_common.greenChnl == "0" and font_common.blueChnl == "0")
assert(Theme.GetFont() == "ttk_forge_serif")
GLOBAL.TTK_FORGE_SERIF = nil
assert(Theme.GetFont() == BODYTEXTFONT)
assert(Theme.GetSurfaceScale("forge") == .7)
```

- [ ] **Step 2: Run the focused suite and verify RED**

Run: `python mods/PhamNhanTuTien/tools/test_unified_ui.py`

Expected: FAIL on font channel metadata, missing lazy `Theme.GetFont`, missing `.7` forge surface scale, or missing artifact primitive module.

- [ ] **Step 3: Correct the font pipeline and implement primitives**

Set the BMFont common-channel attributes explicitly:

```python
element(root, "common", lineHeight=ascent + descent, base=ascent,
        scaleW=2048, scaleH=2048, pages=1, packed=0,
        alphaChnl=1, redChnl=0, greenChnl=0, blueChnl=0)
```

Expose the alias only after successful native loading and resolve it at widget-construction time:

```lua
function Theme.GetFont()
    return GLOBAL.TTK_FORGE_SERIF or BODYTEXTFONT or UIFONT
end

function Theme.GetSurfaceScale(kind)
    return kind == "forge" and .7 or 1
end
```

Implement focused primitive constructors that always receive a parent, local coordinates, and dimensions; none may call `SetScaleMode`.

- [ ] **Step 4: Build the font and verify GREEN**

Run: `python mods/PhamNhanTuTien/tools/build_forge_font.py`

Run: `python mods/PhamNhanTuTien/tools/test_unified_ui.py`

Expected: font build reports glyph count and SHA-256; all font/theme/UI harness tests PASS.

- [ ] **Step 5: Commit**

```powershell
git add -- mods/PhamNhanTuTien/tools/build_forge_font.py mods/PhamNhanTuTien/main/ttk_forge_fonts.lua mods/PhamNhanTuTien/scripts/widgets/hh_ui/ttk_unified_theme.lua mods/PhamNhanTuTien/scripts/widgets/hh_ui/ttk_artifact_primitives.lua mods/PhamNhanTuTien/tests/ui/test_forge_fonts.lua mods/PhamNhanTuTien/tests/ui/test_artifact_theme.lua mods/PhamNhanTuTien/tools/test_unified_ui.py artifacts/pham-nhan-ui-runtime/render.py mods/PhamNhanTuTien/fonts/ttk_forge_serif.zip
git commit -m "fix(ui): establish artifact theme and Vietnamese font"
```

### Task 2: Responsive six-tab shell and native bridge

**Files:**
- Modify: `mods/PhamNhanTuTien/scripts/screens/ttk_unified_screen.lua`
- Modify: `mods/PhamNhanTuTien/scripts/widgets/hh_ui/ttk_native_panel.lua`
- Modify: `mods/PhamNhanTuTien/scripts/ui/ttk_native_input.lua`
- Modify: `mods/PhamNhanTuTien/main/hh_ui.lua`
- Modify: `mods/PhamNhanTuTien/tests/ui/test_unified_screen.lua`
- Modify: `mods/PhamNhanTuTien/tests/ui/test_unified_controller.lua`

**Interfaces:**
- Consumes: `Theme.GetFont`, artifact primitives from Task 1, existing `Registry`, `Controller`, `NativeBridge`, and `NativeInput` contracts.
- Produces: `TTKUnifiedScreen:TrackNativeContainer(widget, prefab)`, `UntrackNativeContainer(widget)`, and `GetDesignBounds(viewport_width, viewport_height) -> { inside, left, right, top, bottom, scale }`; shell never changes the widget parent.

- [ ] **Step 1: Write failing responsive and no-reparent tests**

```lua
local original_parent = detached_widget:GetParent()
assert(screen:TrackNativeContainer(detached_widget, "hh_ui_container"))
assert(detached_widget:GetParent() == original_parent)
assert(screen.root.scale_mode == SCALEMODE_PROPORTIONAL)
assert(detached_widget.scale[1] == .7)
assert(screen:GetDesignBounds(1024, 768).inside == true)
```

Add a pending-open test that switches tabs and asserts one cancellation, one native close, no duplicate RPC, and cleared registry ownership.

- [ ] **Step 2: Run the focused suite and verify RED**

Run: `python mods/PhamNhanTuTien/tools/test_unified_ui.py`

Expected: FAIL because `AttachNativeContainer` reparents the widget and uses `.88`, and `TrackNativeContainer`/design bounds do not exist.

- [ ] **Step 3: Replace re-parenting with tracking and rebuild the shell skin**

Keep the native parent and proportional mode established by Solo:

```lua
function TTKUnifiedScreen:TrackNativeContainer(widget, prefab)
    if not self:WantsNativeContainer(prefab) then return false end
    Registry.ResolveNative(self.owner, self, prefab)
    self.native_widget = widget
    widget:SetScale(Theme.GetSurfaceScale(prefab == "hh_forge_container" and "forge" or "native"))
    widget:Show()
    return true
end
```

Draw the artifact frame, title, six tabs, close button, subtab rail, and content viewport with Task 1 primitives. Keep one proportional root and center anchors. Update `main/hh_ui.lua` to call `TrackNativeContainer` without changing widget parent.

- [ ] **Step 4: Verify shell behavior and render the checkpoint**

Run: `python mods/PhamNhanTuTien/tools/test_unified_ui.py`

Run: `python artifacts/pham-nhan-ui-runtime/render.py --screen shell --width 1366 --height 768 --output artifacts/pham-nhan-ui-runtime/shell-1366x768.png`

Expected: tests PASS; PNG contains the full frame, six tabs, title, close button, and no clipped edges.

- [ ] **Step 5: Commit and show `shell-1366x768.png`**

```powershell
git add -- mods/PhamNhanTuTien/scripts/screens/ttk_unified_screen.lua mods/PhamNhanTuTien/scripts/widgets/hh_ui/ttk_native_panel.lua mods/PhamNhanTuTien/scripts/ui/ttk_native_input.lua mods/PhamNhanTuTien/main/hh_ui.lua mods/PhamNhanTuTien/tests/ui/test_unified_screen.lua mods/PhamNhanTuTien/tests/ui/test_unified_controller.lua artifacts/pham-nhan-ui-runtime/shell-1366x768.png
git commit -m "feat(ui): rebuild responsive artifact shell"
```

### Task 3: Bảng Tổng Hợp

**Files:**
- Modify: `mods/PhamNhanTuTien/scripts/widgets/hh_ui/hh_equip_ui.lua`
- Create: `mods/PhamNhanTuTien/tests/ui/test_summary_artifact.lua`
- Modify: `mods/PhamNhanTuTien/tools/test_unified_ui.py`
- Modify: `artifacts/pham-nhan-ui-runtime/render.py`

**Interfaces:**
- Consumes: primitive constructors, unchanged `hh_ui_container`, `Utils:GetClientValue`, `Items`, `Lock.Close`.
- Produces: `Summary:GetSlotLayout(index, tab)`, `GetSlotScale(index)`, `GetVisibleSlots(tab)`, `GetActionRPC(action)`, `SetTab(tab)`, and `RefreshSlots()`.

- [ ] **Step 1: Write failing layout and behavior tests**

Assert 24 recycle slots, three combine inputs, one socket input, exact tab visibility, existing RPC action names, `.7` native scale, and local dialog ownership:

```lua
assert(#summary:GetVisibleSlots("combine") == 27)
assert(#summary:GetVisibleSlots("socket") == 25)
assert(summary.dialog == nil or summary.dialog:GetParent() == summary)
assert(summary:GetActionRPC("reroll") == "UpdateEffectValue")
```

- [ ] **Step 2: Run and verify RED**

Run: `python mods/PhamNhanTuTien/tools/test_unified_ui.py`

Expected: FAIL on missing public layout/visibility contracts or a dialog parent outside the panel.

- [ ] **Step 3: Recompose Summary from artifact primitives**

Use `bang-tong-hop/v3` geometry, preserve the existing slot indices and callback bodies, and make confirmation dialogs children of `Summary`. Do not alter item filters, request payloads, or inventory movement.

- [ ] **Step 4: Verify and render both subtabs**

Run: `python mods/PhamNhanTuTien/tools/test_unified_ui.py`

Run: `python artifacts/pham-nhan-ui-runtime/render.py --screen summary-combine --width 1366 --height 768 --output artifacts/pham-nhan-ui-runtime/summary-combine.png`

Run: `python artifacts/pham-nhan-ui-runtime/render.py --screen summary-socket --width 1366 --height 768 --output artifacts/pham-nhan-ui-runtime/summary-socket.png`

Expected: tests PASS; both PNGs remain inside the frame and match the v3 composition.

- [ ] **Step 5: Commit and show both Summary PNGs**

```powershell
git add -- mods/PhamNhanTuTien/scripts/widgets/hh_ui/hh_equip_ui.lua mods/PhamNhanTuTien/tests/ui/test_summary_artifact.lua mods/PhamNhanTuTien/tools/test_unified_ui.py artifacts/pham-nhan-ui-runtime/render.py artifacts/pham-nhan-ui-runtime/summary-combine.png artifacts/pham-nhan-ui-runtime/summary-socket.png
git commit -m "feat(ui): rebuild equipment summary from artifacts"
```

### Task 4: Thần Binh Phổ

**Files:**
- Modify: `mods/PhamNhanTuTien/scripts/widgets/hh_ui/hh_forge_ui.lua`
- Modify: `mods/PhamNhanTuTien/scripts/utils/ttk_forge_rules.lua`
- Create: `mods/PhamNhanTuTien/tests/ui/test_forge_artifact.lua`
- Modify: `mods/PhamNhanTuTien/tools/test_unified_ui.py`
- Modify: `artifacts/pham-nhan-ui-runtime/render.py`

**Interfaces:**
- Consumes: unchanged `ttk_forge_rules` decisions and current forge RPC/state events.
- Produces: `ForgeUI:GetModeLayout(mode)`, `ForgeUI.surface_scale = Theme.GetSurfaceScale("forge")`, local confirmation/selection layers, and three artifact-mode renders.

- [ ] **Step 1: Write failing mode, slot, and RPC preservation tests**

```lua
assert(forge:GetModeLayout("cleanse").slots[1].container_slot == 1)
assert(forge:GetModeLayout("stone_change").slots[2].prefab == "hh_essence")
assert(forge:GetModeLayout("equip_inherit").slots[4].prefab == "nightmarefuel")
assert(forge.surface_scale == .7)
assert(forge.dialog == nil or forge.dialog:GetParent() == forge)
```

Exercise empty, server-rejected, insufficient-resource, and selected-effect states without changing the returned rule codes.

- [ ] **Step 2: Run and verify RED**

Run: `python mods/PhamNhanTuTien/tools/test_unified_ui.py`

Expected: FAIL on missing mode-layout contract, wrong surface scale, or non-local overlays.

- [ ] **Step 3: Recompose the three modes from v4 artifacts**

Replace bespoke rectangles with shared primitives, preserve `Submit`, `RequestMode`, item lookup, rule validation, pending revision, and RPC payload code. Keep all transient layers under the forge widget.

- [ ] **Step 4: Verify and render all forge modes**

Run: `python mods/PhamNhanTuTien/tools/test_unified_ui.py`

Run the renderer for `forge-cleanse`, `forge-stone-change`, and `forge-inherit`, writing `forge-cleanse.png`, `forge-stone-change.png`, and `forge-inherit.png`.

Expected: tests PASS; the three PNGs match the v4 column structure and remain within viewport.

- [ ] **Step 5: Commit and show all three Forge PNGs**

```powershell
git add -- mods/PhamNhanTuTien/scripts/widgets/hh_ui/hh_forge_ui.lua mods/PhamNhanTuTien/scripts/utils/ttk_forge_rules.lua mods/PhamNhanTuTien/tests/ui/test_forge_artifact.lua mods/PhamNhanTuTien/tools/test_unified_ui.py artifacts/pham-nhan-ui-runtime/render.py artifacts/pham-nhan-ui-runtime/forge-cleanse.png artifacts/pham-nhan-ui-runtime/forge-stone-change.png artifacts/pham-nhan-ui-runtime/forge-inherit.png
git commit -m "feat(ui): rebuild Than Binh Pho from v4 artifacts"
```

### Task 5: Lâm Phượng Luyện Khí Đài

**Files:**
- Modify: `mods/PhamNhanTuTien/scripts/widgets/hh_ui/ttk_strengthen_ui.lua`
- Create: `mods/PhamNhanTuTien/tests/ui/test_strengthen_artifact.lua`
- Modify: `mods/PhamNhanTuTien/tools/test_unified_ui.py`
- Modify: `artifacts/pham-nhan-ui-runtime/render.py`

**Interfaces:**
- Consumes: current strengthen snapshot fields, one-slot container, existing strengthen RPC.
- Produces: `StrengthenUI:ViewState(data, item)` returning `empty`, `ready`, `protected`, or `maxed` for presentation only.

- [ ] **Step 1: Write failing four-state tests**

Assert the exact state classifier, button enablement, cost text, risk message, item identity check, and one-slot mapping for empty, ready, protected +9→+10, and maxed +13 states.

- [ ] **Step 2: Run and verify RED**

Run: `python mods/PhamNhanTuTien/tools/test_unified_ui.py`

Expected: FAIL because `ViewState` and state-specific render contract do not exist.

- [ ] **Step 3: Recompose Strengthen UI from `lam-phuong-ui`**

Use the shared frame and primitives; preserve `Refresh`, pending revision handling, probability clamping, gem counting, risk rules, `Submit`, and RPC payload.

- [ ] **Step 4: Verify and render four states**

Run: `python mods/PhamNhanTuTien/tools/test_unified_ui.py`

Render `strengthen-empty.png`, `strengthen-ready.png`, `strengthen-protected.png`, and `strengthen-maxed.png` at 1366×768.

Expected: tests PASS; each image corresponds to the matching artifact state.

- [ ] **Step 5: Commit and show all four Strengthen PNGs**

```powershell
git add -- mods/PhamNhanTuTien/scripts/widgets/hh_ui/ttk_strengthen_ui.lua mods/PhamNhanTuTien/tests/ui/test_strengthen_artifact.lua mods/PhamNhanTuTien/tools/test_unified_ui.py artifacts/pham-nhan-ui-runtime/render.py artifacts/pham-nhan-ui-runtime/strengthen-empty.png artifacts/pham-nhan-ui-runtime/strengthen-ready.png artifacts/pham-nhan-ui-runtime/strengthen-protected.png artifacts/pham-nhan-ui-runtime/strengthen-maxed.png
git commit -m "feat(ui): rebuild Lam Phuong strengthen screen"
```

### Task 6: Nhân vật

**Files:**
- Modify: `mods/PhamNhanTuTien/scripts/widgets/hh_status_ui.lua`
- Create: `mods/PhamNhanTuTien/tests/ui/test_character_artifact.lua`
- Modify: `mods/PhamNhanTuTien/tools/test_unified_ui.py`
- Modify: `artifacts/pham-nhan-ui-runtime/render.py`

**Interfaces:**
- Consumes: current level/rank/stats/skill data and embedded options passed by the shell.
- Produces: an artifact-themed embedded character panel with unchanged event subscriptions and skill callbacks.

- [ ] **Step 1: Write failing data-binding and layout tests**

Create representative level, rank, stat, and skill snapshots; assert the panel renders their values, has no second proportional root when embedded, and keeps existing skill callback identifiers.

- [ ] **Step 2: Run and verify RED**

Run: `python mods/PhamNhanTuTien/tools/test_unified_ui.py`

Expected: FAIL on the embedded-root or artifact-primitive assertions.

- [ ] **Step 3: Replace character presentation only**

Rebuild headings, stat regions, skill rows, and empty/loading states with shared primitives. Keep all reads, listeners, and click callback bodies unchanged.

- [ ] **Step 4: Verify and render**

Run focused suite, then render `character.png` at 1366×768.

Expected: PASS; complete character panel fits the shell and uses the artifact visual language.

- [ ] **Step 5: Commit and show `character.png`**

```powershell
git add -- mods/PhamNhanTuTien/scripts/widgets/hh_status_ui.lua mods/PhamNhanTuTien/tests/ui/test_character_artifact.lua mods/PhamNhanTuTien/tools/test_unified_ui.py artifacts/pham-nhan-ui-runtime/render.py artifacts/pham-nhan-ui-runtime/character.png
git commit -m "feat(ui): restyle character panel"
```

### Task 7: Nhiệm vụ

**Files:**
- Modify: `mods/PhamNhanTuTien/scripts/widgets/hh_ui/ttk_quest_panel.lua`
- Modify: `mods/PhamNhanTuTien/scripts/widgets/hh_guild_ui.lua`
- Create: `mods/PhamNhanTuTien/tests/ui/test_quests_artifact.lua`
- Modify: `mods/PhamNhanTuTien/tools/test_unified_ui.py`
- Modify: `artifacts/pham-nhan-ui-runtime/render.py`

**Interfaces:**
- Consumes: existing daily/rank/Guild Quest widgets, focus modes, timers, and remote-guild callbacks.
- Produces: artifact-styled `daily`, `guild`, and `promotion` views under one embedded panel.

- [ ] **Step 1: Write failing quest-mode tests**

Assert all three subtabs, remote Guild action availability, daily/rank/Guild empty states, timer text, and embedded mode with no nested proportional root.

- [ ] **Step 2: Run and verify RED**

Run: `python mods/PhamNhanTuTien/tools/test_unified_ui.py`

Expected: FAIL on missing theme primitives or nested root behavior.

- [ ] **Step 3: Restyle quest and guild widgets**

Keep `SetQuestFocus`, data listeners, timer calculation, and remote action callbacks. Replace only frames, tabs, cards, typography, spacing, and state colours.

- [ ] **Step 4: Verify and render**

Run focused suite; render `quests-daily.png`, `quests-guild.png`, and `quests-promotion.png`.

Expected: PASS; each view remains inside the shell and exposes its original actions.

- [ ] **Step 5: Commit and show the three Quest PNGs**

```powershell
git add -- mods/PhamNhanTuTien/scripts/widgets/hh_ui/ttk_quest_panel.lua mods/PhamNhanTuTien/scripts/widgets/hh_guild_ui.lua mods/PhamNhanTuTien/tests/ui/test_quests_artifact.lua mods/PhamNhanTuTien/tools/test_unified_ui.py artifacts/pham-nhan-ui-runtime/render.py artifacts/pham-nhan-ui-runtime/quests-daily.png artifacts/pham-nhan-ui-runtime/quests-guild.png artifacts/pham-nhan-ui-runtime/quests-promotion.png
git commit -m "feat(ui): restyle quest and guild panels"
```

### Task 8: Quân đoàn

**Files:**
- Modify: `mods/PhamNhanTuTien/scripts/screens/hh_shadow_upgrade_screen.lua`
- Create: `mods/PhamNhanTuTien/tests/ui/test_army_artifact.lua`
- Modify: `mods/PhamNhanTuTien/tools/test_unified_ui.py`
- Modify: `artifacts/pham-nhan-ui-runtime/render.py`

**Interfaces:**
- Consumes: current shadow selection, level, EXP, talent, stats, animation widget, and summon/upgrade callbacks.
- Produces: embedded artifact-styled army panel that does not own or alter shadow progression.

- [ ] **Step 1: Write failing army binding tests**

Assert five shadow selectors, lock state, selected shadow, level/EXP/talents/stat display, embedded mode without nested proportional scaling, and unchanged action callback names.

- [ ] **Step 2: Run and verify RED**

Run: `python mods/PhamNhanTuTien/tools/test_unified_ui.py`

Expected: FAIL on embedded-root or shared-theme assertions.

- [ ] **Step 3: Restyle the army screen**

Preserve netvar reads, animation setup, stat formulas, talent gating, summon, and upgrade actions. Recompose only the presentation.

- [ ] **Step 4: Verify and render**

Run focused suite; render `army.png` at 1366×768 with representative Igris level 10 data.

Expected: PASS; selector, model region, talent list, stats, and description fit the artifact frame.

- [ ] **Step 5: Commit and show `army.png`**

```powershell
git add -- mods/PhamNhanTuTien/scripts/screens/hh_shadow_upgrade_screen.lua mods/PhamNhanTuTien/tests/ui/test_army_artifact.lua mods/PhamNhanTuTien/tools/test_unified_ui.py artifacts/pham-nhan-ui-runtime/render.py artifacts/pham-nhan-ui-runtime/army.png
git commit -m "feat(ui): restyle army panel"
```

### Task 9: Cửa hàng

**Files:**
- Modify: `mods/PhamNhanTuTien/scripts/screens/hh_dungeon_shop_screen.lua`
- Modify: `mods/PhamNhanTuTien/scripts/dungeon_shop/hh_dungeon_shop_manual_layout.lua`
- Create: `mods/PhamNhanTuTien/tests/ui/test_shop_artifact.lua`
- Modify: `mods/PhamNhanTuTien/tools/test_unified_ui.py`
- Modify: `artifacts/pham-nhan-ui-runtime/render.py`

**Interfaces:**
- Consumes: current authoritative sync request, categories, cycle, stock, coin balance, product defs, and buy RPC.
- Produces: artifact-styled embedded shop with the same refresh and purchase behavior.

- [ ] **Step 1: Write failing shop tests**

Assert one sync request per activation, fresh sync after hide/show, ten card positions, category selection, insufficient-coin state, sold-out state, and no nested proportional root in embedded mode.

- [ ] **Step 2: Run and verify RED**

Run: `python mods/PhamNhanTuTien/tools/test_unified_ui.py`

Expected: FAIL on artifact layout or embedded scaling assertions.

- [ ] **Step 3: Restyle shop panel and cards**

Keep product lookup, cycle calculation, stock, balance, notice, and buy callback bodies. Replace only layout tables, textures, typography, focus, and disabled states.

- [ ] **Step 4: Verify and render**

Run focused suite; render `shop.png` at 1366×768 with representative stocked products and zero coins.

Expected: PASS; title, categories, ten products, balance, prices, stock, and disabled purchase states remain readable.

- [ ] **Step 5: Commit and show `shop.png`**

```powershell
git add -- mods/PhamNhanTuTien/scripts/screens/hh_dungeon_shop_screen.lua mods/PhamNhanTuTien/scripts/dungeon_shop/hh_dungeon_shop_manual_layout.lua mods/PhamNhanTuTien/tests/ui/test_shop_artifact.lua mods/PhamNhanTuTien/tools/test_unified_ui.py artifacts/pham-nhan-ui-runtime/render.py artifacts/pham-nhan-ui-runtime/shop.png
git commit -m "feat(ui): restyle dungeon shop panel"
```

### Task 10: Kho 120 ô

**Files:**
- Modify: `mods/PhamNhanTuTien/scripts/widgets/hh_ui/ttk_native_panel.lua`
- Modify: `mods/PhamNhanTuTien/main/hh_ui.lua`
- Modify: `mods/PhamNhanTuTien/main/ttk_solo_source.lua`
- Create: `mods/PhamNhanTuTien/scripts/widgets/hh_ui/ttk_storage_ui.lua`
- Create: `mods/PhamNhanTuTien/tests/ui/test_storage_artifact.lua`
- Modify: `mods/PhamNhanTuTien/tools/test_unified_ui.py`
- Modify: `artifacts/pham-nhan-ui-runtime/render.py`

**Interfaces:**
- Consumes: existing `hh_monarch_storage_container`, 120 native slots, lock state, ownership/open/close RPC, deposit/withdraw behavior, and save-backed container replica.
- Produces: `TTKStorageUI:AttachContainerWidget(native)`, `RefreshSlots()`, paged or scrollable presentation of all 120 native slots without copying item state.

- [ ] **Step 1: Write failing storage tests**

Assert all 120 native slot identities remain attached to the original container widget, each slot appears on exactly one page, locked styling does not unlock the slot, open/close RPC fires once, owner rejection is visible, and closing clears `HHMonarchStorageOpen`.

- [ ] **Step 2: Run and verify RED**

Run: `python mods/PhamNhanTuTien/tools/test_unified_ui.py`

Expected: FAIL because the full storage presentation module does not exist.

- [ ] **Step 3: Implement the full storage presentation**

Lay out native slots in deterministic pages while retaining the original native widget and replica as the sole item owner. Add page controls, lock overlay, ownership/status text, and artifact frame. Do not create shadow item records or a second inventory model.

- [ ] **Step 4: Verify and render**

Run focused suite; render `storage-page-1.png` and `storage-locked.png` at 1366×768.

Expected: PASS; page one and locked state fit the shell, and test coverage proves all 120 slots are reachable exactly once.

- [ ] **Step 5: Commit and show both Storage PNGs**

```powershell
git add -- mods/PhamNhanTuTien/scripts/widgets/hh_ui/ttk_native_panel.lua mods/PhamNhanTuTien/main/hh_ui.lua mods/PhamNhanTuTien/main/ttk_solo_source.lua mods/PhamNhanTuTien/scripts/widgets/hh_ui/ttk_storage_ui.lua mods/PhamNhanTuTien/tests/ui/test_storage_artifact.lua mods/PhamNhanTuTien/tools/test_unified_ui.py artifacts/pham-nhan-ui-runtime/render.py artifacts/pham-nhan-ui-runtime/storage-page-1.png artifacts/pham-nhan-ui-runtime/storage-locked.png
git commit -m "feat(ui): present full monarch storage in unified shell"
```

### Task 11: Full regression, multi-resolution renders, and installed-mod sync

**Files:**
- Modify: `mods/PhamNhanTuTien/tools/test_unified_ui.py`
- Create: `mods/PhamNhanTuTien/tools/test_full_ui_acceptance.py`
- Modify: `artifacts/pham-nhan-ui-runtime/render.py`
- Create: `artifacts/pham-nhan-ui-runtime/manifest.json`
- Create: `docs/superpowers/reports/2026-09-22-pham-nhan-full-ui.md`

**Interfaces:**
- Consumes: every panel and render target from Tasks 1–10.
- Produces: one acceptance command, deterministic render manifest, final report, and a byte-for-byte sync set for the installed mod.

- [ ] **Step 1: Write the failing acceptance test**

The test enumerates every required screen/state and three resolutions, validates image dimensions/non-empty alpha bounds, checks no required widget exceeds viewport bounds, verifies font metadata, and checks registered asset paths:

```python
REQUIRED = {
    "shell", "character", "summary-combine", "summary-socket",
    "forge-cleanse", "forge-stone-change", "forge-inherit",
    "strengthen-empty", "strengthen-ready", "strengthen-protected", "strengthen-maxed",
    "quests-daily", "quests-guild", "quests-promotion", "army", "shop",
    "storage-page-1", "storage-locked",
}
RESOLUTIONS = {(1920, 1080), (1366, 768), (1024, 768)}
```

- [ ] **Step 2: Run and verify RED**

Run: `python mods/PhamNhanTuTien/tools/test_full_ui_acceptance.py`

Expected: FAIL until every required render and manifest entry exists.

- [ ] **Step 3: Complete deterministic batch rendering and manifest generation**

Add `--all` support to the renderer. Record screen, resolution, output path, SHA-256, alpha/content bounds, and artifact source in `manifest.json`. Write the report with test commands, render inventory, limitations, and installed-sync file list.

- [ ] **Step 4: Run focused and full mod verification**

Run: `python mods/PhamNhanTuTien/tools/test_unified_ui.py`

Run: `python mods/PhamNhanTuTien/tools/test_full_ui_acceptance.py`

Run: `python -m unittest discover -s mods/PhamNhanTuTien/tools -p "test_*.py" -v`

Run: `python tools/test_ttk_solo_integration.py`

Expected: every command exits 0; unrelated pre-existing failures, if any, are named in the report and not concealed.

- [ ] **Step 5: Render all screens at all three resolutions**

Run: `python artifacts/pham-nhan-ui-runtime/render.py --all`

Expected: 54 PNGs (18 states × 3 resolutions) plus deterministic `manifest.json`; 1024×768 bounds remain inside the viewport.

- [ ] **Step 6: Synchronize the verified UI files to the installed mod**

Copy only the manifest-listed changed runtime files from `mods/PhamNhanTuTien` to `C:/Program Files (x86)/Steam/steamapps/common/Don't Starve Together/mods/PhamNhanTuTien`, preserving relative paths. Re-run `python mods/PhamNhanTuTien/tools/test_full_ui_acceptance.py --installed` and compare SHA-256 for every synced file.

- [ ] **Step 7: Commit**

```powershell
git add -- mods/PhamNhanTuTien/tools/test_unified_ui.py mods/PhamNhanTuTien/tools/test_full_ui_acceptance.py artifacts/pham-nhan-ui-runtime docs/superpowers/reports/2026-09-22-pham-nhan-full-ui.md
git commit -m "test(ui): verify full artifact redesign"
```
