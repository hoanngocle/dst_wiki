# Phàm Nhân Tu Tiên runtime wiki — acceptance handoff

## Generated evidence

- Source traversal: 166 loaded modules; 41 registration files; 0 unresolved local imports.
- Snapshot: 199 items; 40 recipes (36 crafting, 2 cooking, 2 fusion); 30 affixes; 13 guides; 3 config entries.
- Membership audit: 199 candidates, 199 included and 17 explicit helper/creature exclusions.
- Required recipe samples are covered by extractor tests: two Tầm Bảo Quyển Trục variants, Đá Cường Hoá ×8, Hắc Nguyệt Hồ with marble, EVA builder condition, Lạc Thần cooking predicates, and both Phúc Lạc Dược fusion variants.

## Commands observed

- `python -m unittest discover -s tests/extract -p test_pham_nhan_*.py` — 9 tests passed (using local Python 3.13 executable because the `python` app alias changed during the task).
- `tools/build_pham_nhan_items.py` followed by `--check` — passed.
- `npx next typegen` — passed.
- `npx tsc --noEmit` — passed after regenerating stale route types for intentionally deleted routes.
- `npm run lint` — exited without lint diagnostics.
- `npm run build` — compiled successfully, then Next failed at a sandbox child-process `spawn EPERM` during its TypeScript stage; this is not a clean build acceptance.
- Vitest could not load its config under the sandbox: Vite fails spawning a child process with `EPERM`.

## Not accepted yet

Asset publication is incomplete: all 199 items report missing sprite descriptors. The extractor intentionally avoids assigning an arbitrary first atlas element, so this is an honest blocker rather than a visual fallback. Browser visual/HTTP smoke, lint/build and complete behavior coverage remain pending parent review after atlas decoding is implemented.
