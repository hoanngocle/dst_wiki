<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

## Shared project naming — effective 2026-09-20

- The current mod is **Phàm Nhân Tu Tiên**, abbreviated **Phàm Nhân**, version **2.0**. Use **Phàm Nhân** in conversation and new task titles; use the full name in formal mod metadata and documentation headings.
- This is the renamed continuation of **Tu Tiên Ký**, not a separate mod. Solo Leveling has already been fully integrated. Work on the integrated implementation in `mods/PhamNhanTuTien`; do not repeat the integration or describe Solo as an optional external dependency for the current mod.
- Keep `mods/PhamNhanTuTien`, existing `ttk_`/`hh_` prefab/component/save/RPC identifiers, and existing routes unless a separate migration is explicitly requested. A display-name change must not break saves, tooling, or links.
- Retain original names when identifying historical releases, source mods, provenance, and archived evidence. In particular, the original **Tu Tiên** source mod and the name **Solo Leveling** remain valid when discussing those sources.
- These naming rules apply to all tasks working in this repository. Preserve unrelated task work and use the new name on future updates.

- The user explicitly renamed the working mod folder from `mods/TuTienKy` to `mods/PhamNhanTuTien`. Use the new folder for all ongoing work; old paths in archived reports refer to the historical location.
