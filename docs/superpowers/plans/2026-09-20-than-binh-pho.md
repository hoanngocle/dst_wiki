# Thần Binh Phổ Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans to implement task by task.

**Goal:** Implement the approved EVA silver/amethyst Thần Binh Phổ UI in Phàm Nhân Tu Tiên, with three readable tabs and restricted ingredient slots.

**Architecture:** Keep the native five-slot personal container and existing save/prefab/RPC identifiers. A shared rules module controls server-authoritative tab filtering, while the client widget lays out real inventory slots over a generated decorative frame. Bùa Tẩy remains the existing virtual currency.

**Tech Stack:** DST Lua 5.1, native inventory widgets and networking, generated PNG compiled with Klei TextureConverter, Python/Lupa regression checks.

**Spec:** User-approved Thanh Tẩy / Đúc Linh / Kế Thừa concepts in this conversation; title Thần Binh Phổ, EVA charcoal/ivory/amethyst palette, upper result preview, lower inputs, right-hand instructions, faded fixed-item icons when empty.

## Constraints and review focus

- Preserve unrelated workspace changes and all existing prefab/save identifiers.
- No physical Bùa Tẩy item or altered game economy; use hh_items.ad_cleanStone.
- Wrong items must be rejected on server and client; hidden slots must not accept items.
- Switching tabs must return inputs safely, including full inventories.
- Preview must never pretend to be a real output slot; inheritance destination must be clearly marked as an input.
- Rare Đúc Linh output must survive filtering and cannot be rerolled as a common stone.
- UI must survive empty slots, attribute changes, closing/reopening, and delayed server mode acknowledgments.

## Tasks

- [x] Backend: write behavior tests, add ttk_forge_rules, replicated mode, guarded RPC/actions, safe item return. Slots: cleanse 1 equipment; stone_change 2 stone/3 essence; inherit 2 source/3 destination/4 essence/5 nightmarefuel.
- [x] Artwork: generate a textless silver/feather/amethyst frame from approved concept, copy source to workspace, compile native texture and atlas, preserve provenance.
- [x] Client: replace hh_forge_ui with three tabs and live native slots, ghost icons, currency/quantity labels, attribute selection, result preview and action readiness. Update main/hh_ui attachment hook.
- [x] Copy: rename building/container and relevant guide strings to Thần Binh Phổ / Đúc Linh; document verified hh_essence acquisition.
- [x] Verify: behavior tests, Lua compilation, widget rendering for all tabs, native dedicated-server smoke, independent review and focused fixes. Report client visual validation limits honestly.
