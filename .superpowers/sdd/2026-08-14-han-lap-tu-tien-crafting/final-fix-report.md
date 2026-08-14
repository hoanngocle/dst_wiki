# Final fix report — Hàn Lập Tu Tiên crafting

Date: 2026-08-14
Reviewed base: `fe1b95bb5d17d61450ff1fc863207d8e2958c9a7`

## Result by finding

### Important 1 — fail-closed runtime catalog parsing

- `app/lib/tu-tien-crafting.ts:27-70` now rejects a non-object/non-array
  catalog payload, malformed entity records, invalid entity keys or recipe
  arrays, non-object recipe records, malformed restrictions, and any present
  `builder_tags` value that is not an array of strings.
- `app/lib/tu-tien-crafting.ts:135-138` rejects a craftable whose entity is
  absent from the runtime catalog instead of silently treating it as a manual
  recipe.
- An entity that is present with `recipes: []` remains a valid manual/alchemy
  path. This is exercised by `manual_beta` at
  `app/lib/tu-tien-crafting.test.ts:99-102,127-145`.
- Fail-closed coverage is at
  `app/lib/tu-tien-crafting.test.ts:248-299`.

### Important 2 — verified use requires concrete evidence

- `app/lib/tu-tien-crafting.ts:99-112` now requires at least one usage recipe
  or usage effect, at least one structure function fact, a documented catalog
  mob mechanic, or a resolved use-as-ingredient relation. A bare `known`
  status no longer qualifies.
- Positive evidence fixtures are explicit at
  `app/lib/tu-tien-crafting.test.ts:43-79,112-145`; the resolved ingredient
  relation remains covered at `app/lib/tu-tien-crafting.test.ts:149-174`.
- Negative `known`-but-empty usage and structure cases are covered at
  `app/lib/tu-tien-crafting.test.ts:216-246`.

### Important 3 — server-side non-empty invariant

- `app/tu-tien-crafting/page.tsx:24-51` defines and invokes the server-side
  invariant immediately after the real selector runs against the full parsed
  item and runtime catalogs.
- The thrown diagnostic contains selected and excluded totals plus counts for
  all stable exclusion reasons: `no_recipe`, `other_character`,
  `no_verified_use`, and `unresolved_ingredient`.
- `app/tu-tien-crafting/page-empty.test.tsx:1-24` injects a complete empty
  selection at the selector boundary and proves importing/rendering the page
  fails with all diagnostic counts. The regular actual-data page path remains
  covered by `app/tu-tien-crafting/page.test.tsx`.

### Important 4 — nested modal navigation preserves focus

- `app/components/item-detail-modal.tsx:240-249` focuses the stable close
  button after the replacement item has rendered, while preserving the
  existing scroll-to-top behavior.
- `app/components/item-detail-modal.test.tsx:259-272` first focuses the nested
  ingredient that will unmount, replaces the item, then asserts
  `document.activeElement` remains inside the newly named dialog.

## TDD RED/GREEN evidence

### RED

Command:

```text
npm test -- app/lib/tu-tien-crafting.test.ts app/tu-tien-crafting/page-empty.test.tsx app/components/item-detail-modal.test.tsx
```

Result: exit 1; 3 test files failed, with 7 expected regression failures:

- `known` with empty evidence selected two invalid items;
- four malformed catalog cases did not throw;
- empty page selection resolved instead of rejecting;
- focus escaped the dialog after nested replacement.

An expanded selector RED run added entity-key, entity-recipes,
recipe-restrictions, and missing-entity cases and failed 9 of 12 tests for the
expected absent validations.

### GREEN

Command:

```text
npm test -- app/lib/tu-tien-crafting.test.ts app/tu-tien-crafting/page-empty.test.tsx app/tu-tien-crafting/page.test.tsx app/components/item-detail-modal.test.tsx
```

Result after the minimal fixes: exit 0; 4 files passed, 31 tests passed.

## Minor rulings

1. No production allowlist, item-name exception, or item-specific selector
   behavior was added for Thân Ngoại Hóa Thân or Thiên Cơ Ốc. The selector
   remains generic and evidence-driven. An item-specific actual-data assertion
   was not added because it would couple the regression suite to examples
   rather than prove a distinct generic rule; the full actual-data page test
   and production build exercise the generic selector.
2. Category, Vietnamese name, then id ordering remains unchanged at
   `app/lib/tu-tien-crafting.ts:151-156`. Task 1 explicitly bound the selector
   to deterministic category/name ordering; introducing condition/path UI
   grouping here would broaden scope and invent a grouping contract.

## Full verification

All commands were run from
`/Users/nyx/company/dst_wiki/.worktrees/han-lap-tu-tien-crafting`.

| Command | Result |
| --- | --- |
| Focused regression suite | exit 0; 4 files, 31 tests |
| `npm test` | exit 0; 25 files, 181 tests |
| `npm run lint` | exit 0 |
| `npx tsc --noEmit` | exit 0 |
| `npm run build` | exit 0; compiled, type checked, generated 7/7 static pages |
| `git diff --check` | exit 0 |

The first sandboxed build attempt failed because Turbopack could not create a
process/bind an internal port (`Operation not permitted`, OS error 1). The same
build command was rerun outside the sandbox and completed successfully. Next.js
also emitted its pre-existing multiple-lockfile/workspace-root warning.

## Self-review

- Re-read the complete binding findings and checked each Important against its
  production branch and a behavior-level regression test.
- Confirmed malformed data cannot be reinterpreted as public/manual access.
- Confirmed `recipes: []` on a present entity remains distinct from a missing
  entity.
- Confirmed evidence checks use data arrays/relations rather than names or
  status labels alone.
- Confirmed the page guard uses the real selector/full catalogs in production
  and the test mocks only that boundary to force the otherwise unavailable
  empty state.
- Confirmed focus restoration uses an already rendered, stable dialog control
  and does not remount or close the dialog.
- Removed an unneeded duplicate-key validation during self-review because it
  was outside the binding findings and not required for the minimal fix.
- No unrelated production behavior, item allowlist, visual redesign, or sort
  contract change is present.

## Commit

Single commit subject: `fix: fail closed on invalid crafting selections`.
The authoritative commit SHA is reported in the completion handoff because a
commit cannot embed its own final SHA in content without changing that SHA.

## Concerns

No code or test concerns. Non-blocking toolchain warnings remain for the
deprecated `vite-tsconfig-paths` setup and Next.js workspace-root inference;
neither was introduced or changed in this fix wave.
