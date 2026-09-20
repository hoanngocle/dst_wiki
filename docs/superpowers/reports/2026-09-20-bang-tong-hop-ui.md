# Phàm Nhân Tu Tiên — Bảng Tổng Hợp

Latest revision: the right side now has two mutually exclusive tabs, **Hợp Thành** and **Khảm**. Recycling remains visible on the left. Native slots 25–27 are shown only in Hợp Thành, slot 28 only in Khảm; switching tabs preserves inventory and sends no gameplay RPC. Confirmation blocks tab changes and dismissal restores only the active tab's slots. Expanded each tab's layout into the available right panel. Tab visibility, inventory preservation and modal restoration checks PASS. Current previews are `artifacts/bang-tong-hop/v3/hop-thanh.png` and `kham.png`; these remain Lua/asset previews, not client captures.

Rebuilt the existing summary panel using the installed EVA silver/amethyst assets and Noto Serif font. Preserved the 28 native inventory slots and their server filters: recycling 1–24, attribute gear 25, attribute material 26, removal material 27, socketing gear 28. Each slot is repositioned by the widget; the shared container adapter accepts per-slot scales while preserving the existing scale for other panels.

The UI separates recycling, attributes and socketing. “Đưa từ túi” describes MoveEquips correctly; “Đổi trị số” discloses the virtual Bùa May cost. Eight paginated gemstone/tool entries show names and counts. Bùa May is shown alongside reroll, and Bùa Tẩy remains at Thần Binh Phổ. Existing RPC actions and backend mechanics are unchanged.

Operations show a confirmation before sending their existing RPC. Inventory slots hide during confirmation to avoid underlying drag/drop. Confirmation checks relevant slot identities and prevents repeated submission; backend validation remains authoritative. Rarity is indicated with gold text, and unsupported star glyphs are omitted from button labels (full names remain in hover text).

Validation: widget tests pass for pagination ID mapping, confirm/cancel, equipment replacement, recycling slot changes, native slot layout and empty lists. Actual item definitions and constructor load under Lua 5.1; both modified production files pass Lua syntax checks. Thần Binh Phổ widget regression checks pass.

Preview: `artifacts/bang-tong-hop/v2/tong-quan.png` and `xac-nhan.png`, rendered from production Lua and installed font/textures with illustrative inventory data. This is not a client screenshot; live client visual/input QA is still pending. Prior widget source is preserved in `mods/solo-assets-work/bang-tong-hop/hh_equip_ui.before.lua`.
