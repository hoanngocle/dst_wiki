# EVA cleanup plan

> For agentic workers: use superpowers:executing-plans after approval. This is housekeeping only; do not resume visual redesign.

**Goal:** Keep the current EVA implementation and necessary editable sources inside `mods/PhamNhanTuTien`, removing redundant experimental material from the working repository.

**Architecture:** Preserve runtime bytes. Retain a small in-mod source/test/tool set whose dependencies resolve without the old artifact directories. The user explicitly overrode the backup proposal: delete redundant experiments permanently, without retaining a backup.

**Tech Stack:** PowerShell, Git, Python, Lua assets.

**Spec:** User request on 2026-09-22 to remove excess tests and old assets and consolidate into the Pham Nhan mod.

## Constraints and review focus

- Current runtime files and Steam installation must remain byte-identical.
- Scope only EVA work from this conversation, not unrelated mod or website tasks.
- Preserve source files referenced by the current rig-map until dependencies are explicitly migrated.
- Do not remove original reference mods or historical user assets outside the three named experiment trees.
- Six inaccessible temporary directories require explicit handling, not ignored backup errors or recursive deletion through another shell.
- No new character art, gameplay change, commit or push is included in this cleanup approval.

## One cleanup task

- [ ] Inventory `artifacts/eva-approved-sprite`, `artifacts/eva-eyes-study`, and `artifacts/eva-luoshen-rebuild-preview`, including inaccessible entries and tracked files. Current readable inventory: 1,115 files, approximately 702.6 MiB.
- [ ] Preserve current package manifest and installation notes under `mods/PhamNhanTuTien/docs/eva/`. Retain useful current verification scripts under the mod tools/tests folders; remove obsolete face-transplant and rejected preview scripts only with their dependency references accounted for.
- [ ] Keep `assets/source/eva_approved` files required by the current provenance map. Migrate necessary renderer/build dependencies and replace old artifact paths in retained tools before removing external trees. Do not copy all old candidates into the mod.
- [x] User explicitly authorized permanent deletion instead of backup. The newly created empty backup directory was removed. Elevated inventory confirmed 1,115 files and no reparse points in the three experiment roots, including the six temporary directories inaccessible in the sandbox.
- [ ] Resolve each removal target to an absolute path and assert it is beneath one of the three exact experiment roots. Use native PowerShell file operations only. Never remove the repository/artifacts root itself.
- [ ] Run approved-rig, repack, fox, starting-icon, tooltip and inventory checks, and a reference scan for removed paths. Compare runtime hashes against the deployed package manifest. Report removed size/count, retained layout, recovery location and any skipped inaccessible files.

## Approval

Approved by the user; subsequent instruction: "Không, thừa thì xóa luôn đi chứ". Retain essential editable sources and useful regression checks; permanently delete redundant experiments. Runtime redesign remains paused.

## Completed 2026-09-22

- Permanently removed all three experimental trees: 1,115 files, 736,664,008 bytes (702.5 MiB), plus three obsolete face-transplant scripts/tests and three superseded planning documents. No backup retained; untracked deleted experiments cannot be recovered through Git.
- Preserved current editable sources in `assets/source/eva_approved`, renderer/helpers in `tools/eva`, and installation metadata/test guide in `docs/eva`. Retained build and registration tools now use in-mod source/output paths, not removed artifact directories.
- After deletion, root verified all seven runtime-file hashes unchanged in both workspace and Steam. Fresh tests: approved rig 6, repack 2, fox 1, starting icon 4, concept registration 10 all pass; skill-panel and inventory checks also pass. Retained Python tools contain no references to the three removed experiment directories.
- No commit/push or Steam mutation performed for cleanup. Historical provenance may describe former artifact locations; these are not runtime dependencies.
