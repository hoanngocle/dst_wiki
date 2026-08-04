# Light Mode and Tu Tiên Route Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task with an independent review gate after every task.

**Goal:** Restore the optimized DST Wiki interface to its original light appearance, expose the cultivation content directly at `/tu-tien`, and remove the generic Guide product surface and its export/audit pipeline completely.

**Architecture:** Keep the existing Next.js App Router site and its static JSON item catalog. Preserve the optimized cultivation Server Component, shared shell, table, sprites, accessibility behavior, and responsive layout. Retarget the existing `nova-*` semantic design tokens to the original accessible light palette so the component structure does not churn. Remove the generic guide routes, browser/reader/data modules, generated guide assets, crawler config, exporter, and publication-quality coupling instead of redirecting or leaving compatibility aliases.

**Tech Stack:** Next.js 16 App Router, React 19 Server Components, TypeScript, Tailwind CSS 4, Vitest/Testing Library, Python unittest extraction tools, static JSON, Vercel static deployment.

## Global Constraints

- The public cultivation URL is exactly `/tu-tien`.
- The main navigation has exactly these product tabs: `Vật phẩm`, `Nhân vật`, `Cảnh giới Tu Tiên`; the cultivation tab links directly to `/tu-tien`.
- `/guides`, `/guides/canh-gioi-tu-tien`, and `/guides/[slug]` are deleted and must resolve through Next.js as 404s. Do not add redirects, rewrites, aliases, or compatibility pages.
- Preserve all 15 cultivation stages, pills, ingredients, game sprites, table semantics, focus behavior, reduced-motion behavior, and responsive layout already optimized in the current cultivation page.
- Remove the four generic Guide articles and all product/runtime/export code that exists solely to publish them. Keep `data/manual/character-guides.json`, `--character-guides`, and character dossier `guide` fields because they belong to the character feature rather than the removed Guide library.
- Use the exact original light palette: background `#edf1f5`, foreground `#14233b`, surface `#f8fafc`, muted `#53647a`, line `#cbd5e1`, accent `#2e5fb3`. Derive any additional semantic tokens from these values while maintaining readable contrast.
- Keep the cultivation page a Server Component; do not add client-side fetching, a database, a theme toggle, new dependencies, or a layout redesign.
- All implementation changes follow TDD: add or update a focused test, run it and capture the expected RED failure, implement the minimum change, then rerun GREEN.
- Do not edit `/Users/nyx/company/nova`.

## Task 1: Restore the light shell and publish cultivation at `/tu-tien`

**Files:**

- Modify: `app/components/site-header.test.tsx`
- Modify: `app/layout.test.tsx`
- Create: `app/tu-tien/page.test.tsx`
- Move/delete: `app/guides/canh-gioi-tu-tien/page.test.tsx`
- Modify: `app/components/site-header.tsx`
- Modify: `app/layout.tsx`
- Modify: `app/globals.css`
- Create: `app/tu-tien/page.tsx`
- Move/delete: `app/guides/canh-gioi-tu-tien/page.tsx`

### Step 1: Write the failing navigation, route, and theme tests

- Update `site-header.test.tsx` to expect `Cảnh giới Tu Tiên` with `href="/tu-tien"`, expect it to receive `aria-current="page"` when `active="tu-tien"`, and assert that no `Hướng dẫn` or `/guides` navigation link remains.
- Move the cultivation page test to `app/tu-tien/page.test.tsx`. It must still assert 16 table rows (one header plus 15 stages), the final Hóa Thần-to-Phản Hư row, and static game sprites. It must assert the header link is active and that the old `Trở lại thư viện Guide` link is absent.
- Update `app/layout.test.tsx` to describe the light shell and assert the metadata description no longer advertises generic guides.
- Add a focused source-level light palette assertion in `app/layout.test.tsx` (or a colocated CSS contract test following current Vitest conventions) that verifies all six exact colors from Global Constraints are present in `app/globals.css` and the former dark root/background values are absent.

Run:

```bash
npm test -- --run app/components/site-header.test.tsx app/layout.test.tsx app/tu-tien/page.test.tsx
```

Expected: RED because the header still links to `/guides`, `/tu-tien` does not exist, the back link remains, and the CSS still uses dark tokens.

### Step 2: Implement the direct route and light tokens

- Change `SiteSection` and the header link collection to use `tu-tien` instead of `guides` (and remove the unused `base` member).
- Move the current optimized cultivation Server Component to `app/tu-tien/page.tsx`, use `<SiteHeader active="tu-tien" />`, and remove the guide-library back link/import without changing the stage data or table structure.
- Delete the old cultivation route files so `/guides/canh-gioi-tu-tien` is not generated.
- Retarget the `nova-*` semantic tokens and page background in `app/globals.css` to the exact light palette. Preserve current component class names and accessibility rules; update derived raised/soft/border/accent tokens only as needed for contrast.
- Update root metadata copy to describe items, characters, and cultivation realms, not generic guides.

### Step 3: Verify and commit Task 1

Run:

```bash
npm test -- --run app/components/site-header.test.tsx app/layout.test.tsx app/tu-tien/page.test.tsx app/lib/cultivation-guide.test.ts
npm run lint
npx tsc --noEmit
```

Expected: all focused tests, lint, and type checking pass.

Commit:

```bash
git add app/components/site-header.tsx app/components/site-header.test.tsx app/layout.tsx app/layout.test.tsx app/globals.css app/tu-tien app/guides/canh-gioi-tu-tien
git commit -m "feat: restore light Tu Tien navigation"
```

## Task 2: Delete the generic Guide product and data pipeline

**Files:**

- Delete: `app/components/guide-browser.tsx`
- Delete: `app/components/guide-browser.test.tsx`
- Delete: `app/components/guide-reader.tsx`
- Delete: `app/components/guide-reader.test.tsx`
- Delete: `app/guides/page.tsx`
- Delete: `app/guides/page.test.tsx`
- Delete: `app/guides/loading.tsx`
- Delete: `app/guides/[slug]/page.tsx`
- Delete: `app/guides/[slug]/page.test.tsx`
- Delete: `app/guides/[slug]/loading.tsx`
- Delete: `app/lib/guide-catalog.ts`
- Delete: `app/lib/guide-catalog.test.ts`
- Delete: `app/lib/guide-content.ts`
- Delete: `app/lib/guide-content.test.ts`
- Delete: `public/data/guides/index.json`
- Delete: `public/data/guides/pages/*.json`
- Delete: `public/assets/guides/*`
- Delete: `tools/extract/guides.py`
- Delete: `tests/extract/test_guides.py`
- Delete: `data/config/wiki-categories/guides.json`
- Modify: `tests/crawl_wiki/test_category_config.py`
- Modify: `tools/extract/cli.py`
- Modify: `tools/extract/publication_quality.py`
- Modify: `tests/extract/test_publication_quality.py`
- Modify: `data/generated/publication-quality-report.json` only if the verified audit command intentionally regenerates this tracked report.

### Step 1: Write the failing absence and publication-contract tests

- Change the CLI parser test in `tests/extract/test_publication_quality.py` to call `publication-quality` without `--guides` and assert no `guides` attribute is required.
- Update publication fixtures and calls to the new intended signature `audit_publication(items_path, public_root)` and `run_publication_quality(items_path, public_root, category_root, report_path, apply=...)`.
- Assert the resulting audit/report does not expose a top-level `guides` count.
- Remove the guide-asset audit test because that entire published artifact no longer exists; keep and adapt all item, character, wiki, leak, and repair tests.
- Remove the reviewed `guides` crawler-config test; add/adjust a registry-level assertion, if supported by the current config loader, that `guides` is no longer an available reviewed category.

Run:

```bash
python -m unittest tests.extract.test_publication_quality tests.crawl_wiki.test_category_config
```

Expected: RED because the CLI and publication-quality functions still require a guide root and the guides category still exists.

### Step 2: Remove routes, modules, assets, and exporter coupling

- Delete every generic Guide UI/data file listed above. The `app/guides` directory must disappear; do not replace it with a redirect or `notFound()` page.
- Delete `tools/extract/guides.py`, its dedicated tests, and `data/config/wiki-categories/guides.json`.
- Remove `export_guides`, `GUIDES_CRAWL`, `GUIDES_DATA`, `GUIDES_ASSETS`, the `export-guides` subcommand, its handler, and the `--guides` publication-quality option from `tools/extract/cli.py`.
- Remove `GUIDE_ASSET_SOURCE`, `_audit_guides`, the guide-root parameter, guide publication path enumeration, guide issue checks, and guide counts from `tools/extract/publication_quality.py`. Keep the item/wiki/character audit and repair behavior unchanged.
- Update all affected publication-quality tests and command invocations to the guide-free API.
- Do not delete or rename cultivation code (`app/lib/cultivation-guide.ts`), character dossier guide data (`data/manual/character-guides.json`), or character-publishing arguments.

### Step 3: Prove the removed routes and files cannot ship

Run:

```bash
test ! -e app/guides
test ! -e public/data/guides
test ! -e public/assets/guides
test ! -e tools/extract/guides.py
test ! -e data/config/wiki-categories/guides.json
rg -n '(/guides|export-guides|GUIDES_(CRAWL|DATA|ASSETS)|_audit_guides|public/data/guides|public/assets/guides)' app tools tests package.json public data/config || true
python -m unittest tests.extract.test_publication_quality tests.crawl_wiki.test_category_config
npm test -- --run
npm run build
```

Expected: no generic guide paths or exporter/auditor symbols remain in active code/config, Python and Vitest pass, and the Next.js build route list contains `/`, `/characters`, `/characters/[slug]`, item routes already present in the application, and `/tu-tien` but no `/guides` route.

Commit:

```bash
git add -A app public/data public/assets tools/extract tests data/config data/generated/publication-quality-report.json
git commit -m "refactor: remove generic guide system"
```

## Task 3: Full verification, visual review, and deployment

**Files:**

- Modify only files required by verified regressions found in this task.

### Step 1: Run the complete automated verification matrix

Run:

```bash
npm test -- --run
python -m unittest discover -s tests -p 'test_*.py'
python -m tools.extract.cli publication-quality
npm run lint
npx tsc --noEmit
npm run build
```

Expected: every command passes; publication quality reports zero post-repair hard failures without a guides count; the build emits `/tu-tien` and no `/guides` routes.

### Step 2: Perform desktop and mobile browser checks

- Start the production build locally and inspect `/`, `/characters`, and `/tu-tien` at desktop and mobile widths.
- Verify the exact light shell is visible, text and controls remain readable, the direct cultivation tab is active on `/tu-tien`, the 15-stage table remains usable, and focus outlines are visible.
- Open `/guides`, `/guides/canh-gioi-tu-tien`, and one former generic guide slug and verify each returns the application 404 with no redirect.
- Check browser console output for new runtime errors.

### Step 3: Final independent review and deploy

- Generate a whole-branch review package from the plan merge base to `HEAD` and dispatch an independent final reviewer. Fix and re-review any Critical or Important findings before deployment.
- Push the reviewed branch head directly to GitHub `master` using the repository's approved account-specific SSH remote:

```bash
git push git@github-hoancn1:hoanngocle/dst_wiki.git HEAD:master
```

- Confirm the Vercel Git deployment becomes Ready, then smoke-test the production aliases for `/tu-tien` and the removed `/guides` URLs.

