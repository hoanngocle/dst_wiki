# EVA Huyền Thiên Trảm Linh Kiếm Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans for this coupled feature. User requests GPT-5.6 Sol High implementation after planning; parent handles independent engine review and final package.

**Goal:** Add a standalone point-targeted five-scythe array to EVA for15 Hồn Lực and25-second cooldown.

**Architecture:** A server character component validates cast/cooldown and owns one transient array controller. A geometry/target helper defines pentagon containment and center-relative selection. Unique prefabs render five scythes/perimeter, central scythe and beam. Client keyboard sends only coordinates; server owns costs, roots and damage.

**Tech Stack:** DST Lua5.1, installed engine scripts/assets, Python/Lupa behavior tests, ZIP.

**Spec:** `docs/superpowers/specs/2026-09-19-eva-scythe-array.md`

## Global Constraints

- Cost15 on successful cast only; cooldown25 from accepted cast; no buff/equipment/level prerequisite. Preserve current Wings and Life behavior and approved assets.
- No internet dependencies, Steam writes, publication or git commits. Make immutable baseline backup and real CSV/JSON hash manifest before edits. Avoid literal PowerShell escape separators.
- New tests outside distributable mod; preserve/update existing restricted modinfo count/default and character integration fixtures only where necessary. Modinfo has no ipairs/tostring/stdlib globals.
- All RPC coordinates checked for numeric/finite/bounds/range/valid terrain on server. Network clients never supply damage, radius, duration or cost.
- Root source owned by controller; cleanup must not remove another spell/mod's root sources. Native rooted API inspected before implementation. Never globally override target speed/brain or remove foreign components.
- Original binary character/weapon/wings assets byte-identical. Reuse approved weapon build for scythe FX; verify bank/animation references from archive/source. No need for new painted artwork.

## Review Focus

- Array on distant center finds targets by center, not owner; root pentagon excludes corners outside polygon though damage uses radius6.
- Terminal beam pulse and expiry share timestamp: explicit sequencing prevents lost final hit or lingering roots.
- Two EVA arrays overlap: releasing one must leave the other active.
- Save/reload and owner removal cancel active geometry but retain cooldown without refund/extra fee.
- Bad cursor, NaN/Infinity/string RPC, insufficient Soul, cooldown and key collision leave state unchanged.

## Task1 — Sol High implementation

Create mod `scripts/components/eva_scythe_array.lua`, `scripts/util/eva_scythe_array_common.lua`, `scripts/util/eva_scythe_array_input.lua`, `scripts/prefabs/eva_scythe_array_fx.lua` (controller may reside with prefabs/helper as appropriate). Modify `modmain.lua`, `modinfo.lua`, character master initialization, strings and READMEs. Tests under `mods/eva-assets-work/scythe-array/`.

- [x] Backup current91-file mod + distribution and hash manifest.
- [x] Read source reference and actual rooted/combat/map/input APIs; confirm scythe/beam/perimeter animation names.
- [x] Write meaningful failing tests for cost/cooldown, finite coordinate validation, geometry and cleanup.
- [x] Implement server `CastAt(x,z)` / cooldown save-load, input J at cursor with feedback, existing key priority and RPC throttle.
- [x] Implement pentagon radius5, root scan1.3 thenevery0.3, independent root-source cleanup; no global locomotor hacks.
- [x] Implement large scythe at1.3,367hit at1.8 radius6; beamvisual1.8,11 pulses100 at2.9..7.9. Explicit final pulse thenrelease/cleanup.
- [x] Implement client-safe unique FX using approved scythe and native purple beam/perimeter, dedicatedserver safe and no item loot/collision spawned by decorative scythes.
- [x] Wire prefabs/component/config; update Hồn Lực documentation and descriptions; leave Life/Wings logic intact.
- [x] Run new suite plus restricted modinfo and all prior suites; inspect art hashes and share exact changed files/results for review.

## Task2 — Independent review and delivery

- [x] Parent verifies native rooted cleanup and engine timing/coordinate validation; separate Sol High reviewer examines final runtime integration.
- [x] Resolve concrete findings and rerun affected checks, then final regression suite. Independent review found no remaining actionable issues.
- [x] Package `mods/dist/EVA_v1.0.zip` with `EVA_v1.0/` root; check CRC, exact content parity and original appearance hashes. Verified95 files; artwork unchanged.
- [x] Save verification evidence; deliver ZIP with G/Life, H/Wings, J/Array,15-cost/25s cooldown instructions and live-test limitation. Evidence in `mods/eva-assets-work/scythe-array/verification.json`, `regression-results.json` and `parent-review.md`.
