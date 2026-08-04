# Extract DST from Nova Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan.

**Goal:** Make `/Users/nyx/company/dst_wiki` the independent, Vercel-ready public DST site using Next.js and static JSON while preserving Nova's optimized DST content UI, then completely remove the DST domain from `/Users/nyx/company/nova` after a verified cutover.

**Architecture:** `dst_wiki` keeps its local Python/SQLite extraction pipeline, publishes deterministic JSON and assets under `public/`, and renders them with Next.js Server Components plus small client islands for search, filters, dialogs, and Wiki retry. It never calls Nova or a runtime database. Nova cleanup is a separate, gated phase that removes DST routes, code, data, assets, tests, and tables without touching unrelated dirty worktree changes.

**Tech Stack:** Next.js 16 App Router, React 19, TypeScript, Tailwind CSS 4, Radix Dialog/Tabs, Vitest + Testing Library, Python + pytest + SQLite for the local pipeline; Laravel 13, Inertia 3, React 19, Pest 4, Jest, and PostgreSQL for Nova cleanup verification.

## Global Constraints

- Preserve the approved URL contract: `/`, `/characters`, `/guides`, `/guides/[slug]`, and `/guides/canh-gioi-tu-tien`.
- Keep only Nova's optimized DST content UI. Do not port Nova `GameLayout`, header/sidebar, auth, Zustand stores, Inertia, admin editor, or route helpers.
- Production reads committed static JSON/assets only. SQLite remains a local extraction/audit artifact and must not enter the runtime bundle.
- Keep `dst_wiki`'s simple standalone header and replace all internal `/dst...` links with root routes.
- Do not add a compatibility redirect in either repository. After cleanup, Nova `/dst...` and `/admin/dst...` URLs must return 404.
- Do not start Nova deletion until all automated checks, local production build, Vercel Preview checks, and desktop/mobile parity checks pass.
- The Nova worktree contains extensive unrelated user changes. Before every Nova commit, inspect `git status --short`, stage explicit DST paths only, and never reset, restore, or reformat unrelated files.
- Use `apply_patch` for text edits. Binary character portraits may be copied with an explicit file list after source/destination hashes are checked.
- Follow red-green-refactor: write the smallest failing test, run it and observe the expected failure, implement, rerun the focused test, then commit.
- Before changing Next.js framework-facing files, install the locked dependencies and read the relevant versioned guides under `node_modules/next/dist/docs/`, as required by `dst_wiki/AGENTS.md`.
- Before any Laravel change, use Laravel Boost `search-docs`; before deleting shared-looking Nova symbols, use CodeGraph impact analysis.

## Target Contracts

Use these public TypeScript boundaries so UI components never know about Laravel models or database IDs:

```ts
export type DstLocale = 'vi' | 'en';

export type CharacterSource = 'tu_tien' | 'base_game';
export type CharacterCatalogSource = 'all' | CharacterSource;
export type GuideConfidence = 'confirmed' | 'interpreted' | 'unknown';
export type CharacterRange = 'melee' | 'ranged' | 'hybrid' | 'summoner';
export type CharacterComplexity = 'easy' | 'medium' | 'advanced';

export interface CharacterProfileSource {
  code: string; // injected from the key in the source `profiles` object
  namespace: CharacterSource;
  name: { vi: string; en: string };
  title: { vi: string; en: string };
  description: { vi: string; en: string };
  portrait: { path: string; sourceUrl: string };
  stats: Record<string, { value: number | null; display?: string; note?: string }>;
  abilities: Array<{ name: { vi: string; en: string }; effect: { vi: string; en: string } }>;
  startingItems: Array<{
    code: string;
    name: { vi: string; en: string };
    quantity?: number;
    effect: { vi: string; en: string };
  }>;
  artifacts: Array<{
    code: string;
    name: { vi: string; en: string };
    quantity?: number;
    effect: { vi: string; en: string };
  }>;
  sourceVersion: string;
}

export interface PublicCharacterGuideFact {
  label: string;
  description: string;
  confidence: GuideConfidence;
}

export interface CharacterGuideSource {
  code: string; // injected from the key in the source `guides` object
  roles: string[];
  attackPattern: string;
  range: CharacterRange;
  complexity: CharacterComplexity;
  summary: string;
  strengths: string[];
  tradeoffs: string[];
  firstSteps: string[];
  combat: Array<PublicCharacterGuideFact & { evidence?: string[] }>;
  realmMilestones: Array<{
    realm: string;
    unlocks: Array<PublicCharacterGuideFact & { evidence?: string[] }>;
  }>;
  artifacts: Array<PublicCharacterGuideFact & { evidence?: string[] }>;
  sourceVersion: string;
}

export interface DstCharacterDetail {
  id: string; // `${source}:${code}`; never a Nova database ID
  code: string;
  source: CharacterSource;
  name: string;
  nameVi: string;
  nameEn: string;
  title: string | null;
  description: string | null;
  portrait: string | null;
  searchText: string;
  stats: Record<string, { value: number | null; display?: string; note?: string }> | null;
  abilities: Array<{ name: string; effect: string }>;
  startingItems: Array<{ code: string; name: string; quantity?: number; icon: string | null; effect: string }>;
  artifacts: Array<{ code: string; name: string; quantity?: number; icon: string | null; effect: string }>;
  guide: Omit<CharacterGuideSource, 'code'> | null;
  wikiUrl: string | null;
}
```

The parser exports must be:

```ts
parseCharacterProfiles(value: unknown): Map<string, CharacterProfileSource>
parseCharacterGuides(value: unknown): Map<string, CharacterGuideSource>
buildCharacterCatalog(
  items: readonly ItemCatalogEntry[],
  profiles: ReadonlyMap<string, CharacterProfileSource>,
  guides: ReadonlyMap<string, CharacterGuideSource>,
  locale: DstLocale,
): DstCharacterDetail[]
filterCharacters(
  characters: readonly DstCharacterDetail[],
  query: string,
  source: CharacterCatalogSource,
): DstCharacterDetail[]
```

The actual source envelopes remain `{ "schemaVersion": 1, "profiles": { "<code>": <profile> } }` and `{ "schemaVersion": 1, "guides": { "<code>": <guide> } }`. Profile parsing injects the object key as `code`; guide parsing injects the object key as `code` and assigns source `tu_tien`. Both parsers must reject unsupported schema versions, malformed records, and duplicate identities. Profile parsing also rejects missing required localized text and non-root-relative portrait paths. `buildCharacterCatalog` must order Tu Tiên profiles before base-game profiles, resolve item icons from `items.json`, preserve Vietnamese/English fallback, and omit all source `evidence` fields from the public DTO.

## Source-to-Target Map

| Nova source | `dst_wiki` target | Required adaptation |
|---|---|---|
| `resources/js/components/dst-wiki/dst-{hero,panel,state,field,page-shell}.tsx` | `app/components/dst-*.tsx` | Remove Nova layout/import aliases; keep content visuals and accessibility |
| `resources/js/components/dst-wiki/{wiki-search,item-result,item-detail-modal,wiki-content,game-sprite,recipe-ingredients,mob-sections,structure-sections,tu-tien-item-sections,wiki-article,wiki-structured-sections}.tsx` | `app/components/*.tsx` | Replace Inertia links with `next/link`; static Wiki fetch; no `/dst` paths |
| `resources/js/components/dst/characters/*.tsx` | `app/components/characters/*.tsx` | Receive complete build-time DTOs; no Laravel detail endpoint |
| `resources/js/lib/dst-wiki/*.ts` | `app/lib/*.ts` | Reuse parser/selector logic; static JSON contracts only |
| `resources/js/pages/dst/*.tsx` | Next App Router pages | Replace `Head` with metadata and Inertia props with imports/build-time parsing |
| `database/data/dst-import/character-*.json` | `data/manual/character-*.json` | Copy curated source, validate, and publish through the local pipeline |
| `public/assets/dst/characters/**` | same path in `dst_wiki/public/` | Copy exactly 28 referenced portraits after hash audit |

Import substitutions during the port:

- `@/lib/dst-wiki/*` becomes `@/app/lib/*`.
- `@/components/dst-wiki/*` becomes `@/app/components/*`.
- `@inertiajs/react` `Link` becomes `next/link`; `Head` becomes Next metadata.
- `lucide-react` icons become matching `@phosphor-icons/react` icons.
- Nova's `cn` helper becomes a local `app/lib/cn.ts` helper that filters falsey class names and joins them.
- Any `/dst`, `/dst/characters`, `/dst/guides`, or `/dst/wiki/...` URL becomes `/`, `/characters`, `/guides`, or `/data/wiki/pages/{pageId}.json` respectively.

---

## Task 1: Establish Baselines and Read Next.js 16 Guides

**Files:**

- Read: `/Users/nyx/company/dst_wiki/AGENTS.md`
- Read: `/Users/nyx/company/dst_wiki/package-lock.json`
- Read: matching files under `/Users/nyx/company/dst_wiki/node_modules/next/dist/docs/`
- Modify only if absent: `/Users/nyx/company/dst_wiki/.gitignore`

- [ ] **Step 1: Record both repository baselines**

Run:

```bash
git -C /Users/nyx/company/dst_wiki status --short
git -C /Users/nyx/company/nova status --short
git -C /Users/nyx/company/dst_wiki rev-parse HEAD
git -C /Users/nyx/company/nova rev-parse HEAD
```

Expected: `dst_wiki` is clean at the design/plan commit; Nova is dirty. Save the two HEADs in the execution notes, not in a new repository file.

- [ ] **Step 2: Install the locked standalone dependencies**

Run:

```bash
cd /Users/nyx/company/dst_wiki
npm ci
```

Expected: dependencies install without changing `package-lock.json`.

- [ ] **Step 3: Read the exact bundled Next.js documentation before framework edits**

Run:

```bash
rg --files node_modules/next/dist/docs | rg '(app-router|server-and-client-components|static|generate-static-params|not-found|metadata|public)'
```

Read the matched guides covering App Router layouts/pages, Server versus Client Components, `generateStaticParams`, `notFound`, metadata, and `public` assets. Do not rely on remembered APIs when the bundled Next 16 documentation differs.

- [ ] **Step 4: Run the current standalone baseline**

Run:

```bash
npm test
npm run lint
npx tsc --noEmit
npm run build
python -m pytest tests/extract/test_export_items.py tests/extract/test_publication_quality.py
```

Expected: capture any pre-existing failure separately. Do not repair unrelated failures in this task.

- [ ] **Step 5: Confirm local-only artifacts are ignored**

Run:

```bash
git check-ignore data/generated/wiki.sqlite data/generated public/data/items.json
```

Expected: SQLite/generated working data is ignored; published `public/data/items.json` is not ignored. If the SQLite path is not ignored, add only these patterns to `.gitignore`:

```gitignore
data/generated/
*.sqlite-journal
*.sqlite-wal
*.sqlite-shm
```

- [ ] **Step 6: Commit only if `.gitignore` changed**

```bash
git add .gitignore
git commit -m "chore: keep DST extraction artifacts local"
```

---

## Task 2: Transfer and Validate Curated Character Sources

**Files:**

- Create: `/Users/nyx/company/dst_wiki/data/manual/character-profiles.json`
- Create: `/Users/nyx/company/dst_wiki/data/manual/character-guides.json`
- Create: `/Users/nyx/company/dst_wiki/public/assets/dst/characters/base/*.png`
- Create: `/Users/nyx/company/dst_wiki/public/assets/dst/characters/xd_*.png`
- Modify: `/Users/nyx/company/dst_wiki/app/lib/character-catalog.ts`
- Modify: `/Users/nyx/company/dst_wiki/app/lib/character-catalog.test.ts`
- Modify: `/Users/nyx/company/dst_wiki/tools/extract/export_items.py`
- Modify: `/Users/nyx/company/dst_wiki/tests/extract/test_export_items.py`
- Modify: `/Users/nyx/company/dst_wiki/tools/extract/publication_quality.py`
- Modify: `/Users/nyx/company/dst_wiki/tests/extract/test_publication_quality.py`
- Regenerate: `/Users/nyx/company/dst_wiki/public/data/items.json`

- [ ] **Step 1: Write failing TypeScript contract tests**

Add tests proving:

```ts
it('rejects duplicate character identities', () => {
  expect(() => parseCharacterProfiles(payloadWithDuplicate('base:wilson')))
    .toThrow(/duplicate character identity/i);
});

it('builds stable public details without evidence', () => {
  const characters = buildCharacterCatalog(items, profiles, guides, 'vi');
  expect(characters[0].id).toBe('tu_tien:xd_hantianzun');
  expect(JSON.stringify(characters)).not.toContain('evidence');
  expect(characters[0].startingItems[0]).toMatchObject({ code: expect.any(String) });
});

it('falls back to English text when Vietnamese is empty', () => {
  expect(buildCharacterCatalog(items, fallbackProfiles, new Map(), 'vi')[0].name)
    .toBe('Wilson');
});
```

Also test unsupported schema version, malformed records, duplicate guide identity, invalid asset paths, normalized Vietnamese/English search, namespace filtering, and deterministic Tu Tiên-before-base ordering.

- [ ] **Step 2: Run the focused TypeScript test and observe failure**

```bash
npm test -- app/lib/character-catalog.test.ts
```

Expected: failure because the parsers and complete DTO builder do not exist yet.

- [ ] **Step 3: Copy the two curated JSON sources and only their 28 referenced portraits**

Copy from:

```text
/Users/nyx/company/nova/database/data/dst-import/character-profiles.json
/Users/nyx/company/nova/database/data/dst-import/character-guides.json
/Users/nyx/company/nova/public/assets/dst/characters/base/*.png
/Users/nyx/company/nova/public/assets/dst/characters/xd_*.png
```

Before copying, enumerate the portrait paths referenced by the profile JSON, require exactly 28 unique paths, and verify every source exists. After copying, compare SHA-256 values for those exact paths. Do not copy Nova's unrelated `public/assets/game/**` files or the entire guide archive.

- [ ] **Step 4: Implement the character parsers and build-time adapter**

Implement the target contracts above in `app/lib/character-catalog.ts`. Use `${namespace}:${code}` as the map key; normalize search text with lowercase plus Unicode diacritic removal; resolve starting item/artifact names and icons from the parsed item catalog; clone only explicitly public guide fields so `evidence` cannot leak by object spread.

- [ ] **Step 5: Run the focused TypeScript tests**

```bash
npm test -- app/lib/character-catalog.test.ts
```

Expected: all character contract/selector tests pass.

- [ ] **Step 6: Write failing Python exporter and publication-audit tests**

Extend the tests to require:

```python
def test_character_export_keeps_public_profile_and_guide_fields_without_evidence():
    items, _textures, _report = build_item_export(
        character_catalog_fixture(),
        {"schema_version": 1, "assets": []},
        character_profiles=character_profile_fixture(),
        character_guides=character_guide_fixture(),
    )
    character = next(item for item in items["items"] if item["category"] == "character")
    assert character["character"]["title"]["vi"]
    assert character["character"]["guide"]["summary"]
    assert "evidence" not in json.dumps(character)

def test_publication_quality_rejects_missing_character_portrait(tmp_path):
    items_path, guides_root, public_root = publication_fixture(tmp_path)
    audit = audit_publication(items_path, guides_root, public_root)
    assert any(
        issue["code"] == "missing_character_portrait"
        for issue in audit["issues"]
    )
```

Use the existing exporter/publication functions and fixtures; do not introduce a standalone verification script.

- [ ] **Step 7: Run focused Python tests and observe failure**

```bash
python -m pytest tests/extract/test_export_items.py tests/extract/test_publication_quality.py -q
```

- [ ] **Step 8: Extend the existing exporter and publication audit**

Add optional `character_profiles` and `character_guides` arguments to `build_item_export` plus optional `character_profiles_path` and `character_guides_path` arguments to `export_items`, keeping current callers compatible with default `None`. Add the three small fixture builders named in the test snippet to `test_export_items.py`/`test_publication_quality.py`; they must return complete schema-valid dictionaries rather than mocks. Publish the normalized profile/guide fields for characters, validate all referenced portraits/equipment assets, and keep SQLite/catalog provenance fields out of `public/data/items.json`.

- [ ] **Step 9: Regenerate and verify published data**

Run the repository's existing export command from its CLI help, supplying `data/manual/character-profiles.json` and `data/manual/character-guides.json` through the new options. Then run:

```bash
python -m pytest tests/extract/test_export_items.py tests/extract/test_publication_quality.py -q
npm test -- app/lib/character-catalog.test.ts
rg 'evidence|/dst/' public/data/items.json data/manual/character-profiles.json data/manual/character-guides.json
```

Expected: tests pass; `evidence` may exist only in manual source if retained for audit, never in `public/data/items.json`; no public internal `/dst/` URLs.

- [ ] **Step 10: Commit the data contract slice**

```bash
git add data/manual app/lib/character-catalog.ts app/lib/character-catalog.test.ts tools/extract/export_items.py tools/extract/publication_quality.py tests/extract/test_export_items.py tests/extract/test_publication_quality.py public/data/items.json public/assets/dst/characters
git commit -m "feat: publish static DST character dossiers"
```

---

## Task 3: Port the Standalone DST Visual Foundation

**Files:**

- Modify: `/Users/nyx/company/dst_wiki/app/globals.css`
- Modify: `/Users/nyx/company/dst_wiki/app/layout.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/layout.test.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/components/site-header.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/components/site-header.test.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/lib/cn.ts`
- Create: `/Users/nyx/company/dst_wiki/app/components/dst-field.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/dst-hero.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/dst-panel.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/dst-state.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/dst-page-shell.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/dst-ui.test.tsx`

- [ ] **Step 1: Write failing visual-contract tests**

Port the meaningful assertions from Nova's `resources/js/components/dst-wiki/__tests__/dst-ui.test.tsx`, plus standalone assertions:

```tsx
expect(screen.getByRole('navigation', { name: /điều hướng chính/i })).toBeInTheDocument();
expect(screen.getByRole('link', { name: /vật phẩm/i })).toHaveAttribute('href', '/');
expect(screen.getByRole('link', { name: /nhân vật/i })).toHaveAttribute('href', '/characters');
expect(screen.getByRole('link', { name: /hướng dẫn/i })).toHaveAttribute('href', '/guides');
expect(container.innerHTML).not.toContain('/dst');
```

Test `DstState` danger/status semantics, panel/field labels, the content hero, and the layout's dark root wrapper.

- [ ] **Step 2: Run and observe failure**

```bash
npm test -- app/components/dst-ui.test.tsx app/components/site-header.test.tsx app/layout.test.tsx
```

- [ ] **Step 3: Port only the DST primitives and minimum CSS tokens**

Adapt Nova's five `dst-*` primitives. Copy only CSS variables and component rules actually referenced by DST content into `app/globals.css`; do not copy Nova's global game/sidebar/auth styles. Keep `prefers-reduced-motion`, visible focus rings, readable contrast, and mobile spacing.

- [ ] **Step 4: Keep the standalone header simple**

Render only brand plus Items/Characters/Guides links. It must not import Nova state, auth, Inertia, or sidebar components. Set root metadata in `app/layout.tsx` and wrap the site in the local dark content shell.

- [ ] **Step 5: Run focused tests and lint**

```bash
npm test -- app/components/dst-ui.test.tsx app/components/site-header.test.tsx app/layout.test.tsx
npm run lint -- app/components app/layout.tsx
```

- [ ] **Step 6: Commit the visual foundation**

```bash
git add app/globals.css app/layout.tsx app/layout.test.tsx app/lib/cn.ts app/components/site-header.tsx app/components/site-header.test.tsx app/components/dst-field.tsx app/components/dst-hero.tsx app/components/dst-panel.tsx app/components/dst-state.tsx app/components/dst-page-shell.tsx app/components/dst-ui.test.tsx
git commit -m "feat: port Nova DST visual foundation"
```

---

## Task 4: Port Static Catalog, Search, Item Dialog, and Wiki Content

**Files:**

- Modify: `/Users/nyx/company/dst_wiki/app/lib/item-catalog.ts`
- Modify: `/Users/nyx/company/dst_wiki/app/lib/item-catalog.test.ts`
- Modify: `/Users/nyx/company/dst_wiki/app/lib/wiki-detail.ts`
- Modify: `/Users/nyx/company/dst_wiki/app/lib/wiki-detail.test.ts`
- Modify: `/Users/nyx/company/dst_wiki/app/lib/wiki-search.ts`
- Modify: `/Users/nyx/company/dst_wiki/app/lib/wiki-search.test.ts`
- Modify: `/Users/nyx/company/dst_wiki/app/components/wiki-search.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/components/wiki-search.test.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/components/item-result.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/components/item-result.test.tsx`
- Delete: `/Users/nyx/company/dst_wiki/app/components/item-detail-peek.tsx`
- Delete: `/Users/nyx/company/dst_wiki/app/components/item-detail-peek.test.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/item-detail-modal.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/item-detail-modal.test.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/wiki-content.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/wiki-content.test.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/components/game-sprite.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/components/recipe-ingredients.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/components/mob-sections.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/components/structure-sections.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/components/tu-tien-item-sections.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/components/wiki-article.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/components/wiki-structured-sections.tsx`
- Modify: corresponding existing `*.test.tsx` files for all renderers above
- Modify: `/Users/nyx/company/dst_wiki/app/page.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/page.test.tsx`

- [ ] **Step 1: Write failing parser/selector tests**

Port Nova's catalog, Wiki search, and Wiki detail cases. Require schema version validation, duplicate item identity rejection, deterministic category/source ordering, diacritic-insensitive search, static Wiki URLs, and no `/dst` output:

```ts
expect(buildWikiDetailUrl({ pageId: 105588 })).toBe('/data/wiki/pages/105588.json');
expect(() => parseItemCatalog(duplicatePayload)).toThrow(/duplicate/i);
expect(selectItems(items, { query: 'canh gioi' })[0].searchText).toContain('cảnh giới');
```

- [ ] **Step 2: Write failing component/page tests**

Port meaningful Nova tests for search, results, item detail, Wiki loading/success/failure/retry, recipes, mobs, structures, Tu Tiên sections, and sanitized Wiki rendering. Add page tests for hero counts, filters, empty state, modal opening, and root URLs.

- [ ] **Step 3: Run the focused tests and observe failure**

```bash
npm test -- app/lib/item-catalog.test.ts app/lib/wiki-detail.test.ts app/lib/wiki-search.test.ts app/components app/page.test.tsx
```

- [ ] **Step 4: Port catalog logic without Laravel assumptions**

Adapt Nova selectors into `app/lib`. Keep current static JSON compatibility and reject invalid build input early. Do not add an API route or runtime server action.

- [ ] **Step 5: Port the optimized content components**

Adapt Nova's components using the import substitutions in this plan. `WikiContent` must call `fetch('/data/wiki/pages/{pageId}.json')`, expose loading/error/retry states, abort stale requests on item change/unmount, and render only through the existing parsed/sanitized Wiki contract. The item modal must retain accessible title/description, Escape/overlay close, focus trapping/restoration, and responsive viewport bounds.

- [ ] **Step 6: Build the root catalog page from static data**

`app/page.tsx` parses `public/data/items.json` during build/server rendering and passes serializable catalog data to the client search island. It must not read environment database variables and must not fetch Nova.

- [ ] **Step 7: Run focused tests and static URL scan**

```bash
npm test -- app/lib/item-catalog.test.ts app/lib/wiki-detail.test.ts app/lib/wiki-search.test.ts app/components app/page.test.tsx
rg '/dst|@inertiajs|route\(' app
```

Expected: tests pass and the scan has no runtime Nova route/dependency references.

- [ ] **Step 8: Commit the catalog slice**

```bash
git add app/lib app/components app/page.tsx app/page.test.tsx
git commit -m "feat: port static DST catalog experience"
```

---

## Task 5: Port the Character Gallery and Accessible Dossier

**Files:**

- Modify: `/Users/nyx/company/dst_wiki/package.json`
- Modify: `/Users/nyx/company/dst_wiki/package-lock.json`
- Create: `/Users/nyx/company/dst_wiki/app/components/ui/dialog.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/ui/tabs.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/characters/character-card.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/characters/character-gallery.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/characters/character-dossier-modal.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/characters/character-overview.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/characters/character-combat.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/characters/character-realms.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/characters/character-artifacts.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/characters/__tests__/character-card.test.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/characters/__tests__/character-gallery.test.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/characters/__tests__/character-dossier-modal.test.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/components/characters/__tests__/character-sections.test.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/characters/page.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/characters/page.test.tsx`

- [ ] **Step 1: Add only the accessibility primitives the port needs**

Run:

```bash
npm install @radix-ui/react-dialog@^1.1.14 @radix-ui/react-tabs@^1.1.19
```

Use local wrappers adapted from Nova, but replace Lucide icons with Phosphor icons. Do not add Nova's entire UI library.

- [ ] **Step 2: Write failing gallery and dossier tests**

Port Nova's character tests and adapt them to complete static DTOs. Cover:

- 28 cards from curated profiles;
- Tu Tiên/base filters and Vietnamese/English search;
- opening a card immediately renders overview, combat, realms, and artifacts without an HTTP detail request;
- accessible dialog name, Escape close, tab keyboard behavior, focus restoration;
- missing guide shows a deliberate profile-only state;
- item/artifact icons use resolved static paths;
- rendered HTML contains no evidence and no `/dst` URL.

- [ ] **Step 3: Run and observe failure**

```bash
npm test -- app/components/characters app/characters/page.test.tsx
```

- [ ] **Step 4: Port the components as a single client island**

`app/characters/page.tsx` imports/parses `items.json`, profile JSON, and guide JSON at build time, calls `buildCharacterCatalog(items, profiles, guides, 'vi')`, and passes `DstCharacterDetail[]` to `CharacterGallery`. Clicking a card sets the selected DTO locally; it must never call Nova's `/dst/items/{code}` endpoint.

- [ ] **Step 5: Run focused tests and dependency scan**

```bash
npm test -- app/lib/character-catalog.test.ts app/components/characters app/characters/page.test.tsx
rg '@inertiajs|lucide-react|/dst/items|/dst/characters' app package.json
```

- [ ] **Step 6: Commit the character experience**

```bash
git add package.json package-lock.json app/components/ui app/components/characters app/characters/page.tsx app/characters/page.test.tsx
git commit -m "feat: port static DST character dossiers"
```

---

## Task 6: Port Guides and the Tu Tiên Cultivation Route

**Files:**

- Modify: `/Users/nyx/company/dst_wiki/app/lib/guide-catalog.ts`
- Modify: `/Users/nyx/company/dst_wiki/app/lib/guide-catalog.test.ts`
- Create: `/Users/nyx/company/dst_wiki/app/lib/guide-content.ts`
- Modify: `/Users/nyx/company/dst_wiki/app/lib/guide-content.test.ts`
- Create: `/Users/nyx/company/dst_wiki/app/lib/cultivation-guide.ts`
- Create: `/Users/nyx/company/dst_wiki/app/lib/cultivation-guide.test.ts`
- Modify: `/Users/nyx/company/dst_wiki/app/components/guide-browser.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/components/guide-browser.test.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/components/guide-reader.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/components/guide-reader.test.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/guides/page.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/guides/page.test.tsx`
- Modify: `/Users/nyx/company/dst_wiki/app/guides/[slug]/page.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/guides/[slug]/page.test.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/guides/canh-gioi-tu-tien/page.tsx`
- Create: `/Users/nyx/company/dst_wiki/app/guides/canh-gioi-tu-tien/page.test.tsx`

- [ ] **Step 1: Write failing guide contract tests**

Require `parseGuideIndex` to reject duplicate slugs and invalid detail/cover paths. Add a build-time detail registry with this exact API:

```ts
export function guideSlugs(): string[];
export function findGuide(slug: string): GuideDetail | undefined;
```

The registry explicitly imports the four currently published JSON pages, parses each through the shared contract, and returns slugs in index order. This remains static and makes future additions an explicit data-review change.

- [ ] **Step 2: Write failing page/component tests**

Cover guide filtering, root links, reader sections/assets, cultivation rows, `generateStaticParams()` returning the four published slugs, route metadata, and `notFound()` for an unpublished slug. Ensure the special `canh-gioi-tu-tien` segment is not treated as a generic guide JSON slug.

- [ ] **Step 3: Run and observe failure**

```bash
npm test -- app/lib/guide-catalog.test.ts app/lib/guide-content.test.ts app/lib/cultivation-guide.test.ts app/components/guide-browser.test.tsx app/components/guide-reader.test.tsx app/guides
```

- [ ] **Step 4: Port guide selectors and presentation**

Adapt Nova's `guide-catalog.ts`, `cultivation-guide.ts`, browser, reader, listing page, guide page, and cultivation page. Use `generateStaticParams()` from `guideSlugs()`, `notFound()` from `next/navigation`, and metadata derived only from validated static data.

- [ ] **Step 5: Audit only production-referenced guide assets**

Walk cover/detail paths from `public/data/guides/index.json` and the four page JSON files, require every referenced path under `public/assets/guides/` to exist, and compare with Nova only when a referenced asset is missing. Do not copy Nova's 18 MB `public/assets/guides/archive/**` wholesale.

- [ ] **Step 6: Run focused tests and build-time route scan**

```bash
npm test -- app/lib/guide-catalog.test.ts app/lib/guide-content.test.ts app/lib/cultivation-guide.test.ts app/components/guide-browser.test.tsx app/components/guide-reader.test.tsx app/guides
rg '/dst|@inertiajs|route\(' app/guides app/components/guide-browser.tsx app/components/guide-reader.tsx app/lib/guide-catalog.ts app/lib/guide-content.ts
```

- [ ] **Step 7: Commit guides**

```bash
git add app/lib/guide-catalog.ts app/lib/guide-catalog.test.ts app/lib/guide-content.ts app/lib/guide-content.test.ts app/lib/cultivation-guide.ts app/lib/cultivation-guide.test.ts app/components/guide-browser.tsx app/components/guide-browser.test.tsx app/components/guide-reader.tsx app/components/guide-reader.test.tsx app/guides public/assets/guides
git commit -m "feat: port static DST guides"
```

---

## Task 7: Prove Standalone Vercel Readiness and UI Parity

**Files:**

- Modify: `/Users/nyx/company/dst_wiki/tools/extract/publication_quality.py`
- Modify: `/Users/nyx/company/dst_wiki/tests/extract/test_publication_quality.py`
- Modify if needed: `/Users/nyx/company/dst_wiki/next.config.ts`
- No Nova files may change in this task

- [ ] **Step 1: Add failing publication invariants**

Extend the existing audit tests to fail when:

- a guide detail/cover path is missing;
- a character portrait/equipment path is missing;
- a Wiki `pageId` does not map to `public/data/wiki/pages/{pageId}.json` when required;
- published JSON contains an internal `/dst` path;
- published JSON contains a local SQLite path, Nova absolute path, or `evidence` key.

- [ ] **Step 2: Run and observe the expected failure**

```bash
python -m pytest tests/extract/test_publication_quality.py -q
```

- [ ] **Step 3: Implement the checks in the existing audit**

Keep optional Wiki images non-fatal when the current contract marks them optional. Do not create placeholder images and do not add a second audit script.

- [ ] **Step 4: Run the complete standalone automated gate**

```bash
python -m pytest tests/extract tests/crawl_wiki -q
npm test
npm run lint
npx tsc --noEmit
npm run build
rg '@inertiajs|laravel|/dst(?:/|\b)|DATABASE_URL|DB_CONNECTION|\.sqlite' app public/data next.config.* package.json
```

Expected: every command passes; the scan has no runtime dependency or internal `/dst` URL. Asset folder names such as `/assets/dst/characters` are allowed and must be reviewed separately from route URLs.

- [ ] **Step 5: Run local production smoke tests**

Start `npm run start` from the completed build and check desktop/mobile widths for:

- `/`: search, source/category filters, counts, empty state, item modal, Wiki loading/error/retry;
- `/characters`: search/filter, card/dossier, tabs, Escape/focus behavior;
- `/guides`: listing/filter and all four guide links;
- every `/guides/[slug]` route;
- `/guides/canh-gioi-tu-tien`;
- direct requests for representative item, character, guide, and Wiki assets;
- reduced-motion and no horizontal viewport overflow.

- [ ] **Step 6: Commit any gate fixes**

```bash
git add tools/extract/publication_quality.py tests/extract/test_publication_quality.py next.config.ts app public/data public/assets package.json package-lock.json
git commit -m "test: enforce standalone DST publication quality"
```

Stage only files that actually changed.

- [ ] **Step 7: Deploy and verify Vercel Preview — hard stop before Nova cleanup**

Deploy `/Users/nyx/company/dst_wiki` to a Vercel Preview using the repository's existing Vercel integration or project settings. Do not introduce runtime database environment variables. Repeat the route/asset and desktop/mobile smoke list against the Preview URL.

Record the Preview URL and successful checks in the task conversation. If deployment permission/project linkage is unavailable, stop and ask the user to deploy or authorize it. **Do not proceed to Task 8 until this step is explicitly confirmed successful.**

---

## Task 8: Remove DST Routes, Backend, and Frontend from Nova

**Files:**

- Create: `/Users/nyx/company/nova/tests/Feature/DstRemovalTest.php`
- Modify: `/Users/nyx/company/nova/routes/web.php`
- Modify: `/Users/nyx/company/nova/resources/js/lib/inertia-layouts.tsx`
- Modify: `/Users/nyx/company/nova/resources/js/lib/__tests__/inertia-layouts.test.tsx`
- Modify: `/Users/nyx/company/nova/resources/js/components/game/common/header.tsx`
- Modify: related header tests under `/Users/nyx/company/nova/resources/js/components/game/common/__tests__/`
- Modify: `/Users/nyx/company/nova/resources/js/components/game/common/sidebar.tsx`
- Modify: related sidebar tests under `/Users/nyx/company/nova/resources/js/components/game/common/__tests__/`
- Modify: `/Users/nyx/company/nova/resources/js/pages/dashboard.tsx`
- Modify: dashboard tests beside/under `/Users/nyx/company/nova/resources/js/pages/`
- Modify: `/Users/nyx/company/nova/resources/js/lib/i18n.tsx`
- Modify: `/Users/nyx/company/nova/package.json`
- Delete: all DST-only backend/frontend/test files listed below

Delete these DST-only groups after CodeGraph confirms no non-DST consumers:

```text
app/Console/Commands/DstIntegrityReport.php
app/Console/Commands/ImportDstCharacterProfiles.php
app/Console/Commands/ImportDstGuides.php
app/Console/Commands/ImportDstWiki.php
app/Domain/Dst/**
app/Http/Controllers/Admin/Dst/**
app/Http/Controllers/Dst/**
app/Http/Requests/Admin/Dst/**
app/Http/Resources/Dst/**
app/Models/DstAsset.php
app/Models/DstGuide.php
app/Models/DstItem.php
app/Models/DstItemTranslation.php
app/Models/DstWikiPage.php
app/Policies/DstItemPolicy.php
app/Services/Dst/**
config/dst-guides.php
database/factories/Dst*.php
database/seeders/DstPlaywrightSeeder.php
resources/js/components/dst-wiki/**
resources/js/components/dst/**
resources/js/lib/dst-wiki/**
resources/js/lib/dst/**
resources/js/pages/dst/**
resources/js/pages/admin/dst/**
resources/js/types/dst-character.ts
resources/js/types/admin/dst-character-guide.ts
tests/Feature/Dst/**
tests/Feature/Admin/Dst/**
tests/Unit/Domain/Dst/**
tests/Playwright/dst-characters.spec.ts
tests/Playwright/dst.global-teardown.ts
tests/Playwright/start-dst-server.mjs
tests/Playwright/support/dst-test-environment.mjs
tests/Playwright/support/dst-test-environment.test.mjs
playwright.dst.config.ts
```

- [ ] **Step 1: Recheck Nova's dirty worktree and exact DST ownership**

Run `git status --short` and save the result in the execution notes. Use CodeGraph `impact` for `WikiCatalogService`, `CharacterCatalogService`, `DstItem`, `DstPageShell`, and `resolveDefaultLayout`. Open only the surfaced shared consumers. If any non-DST consumer exists, keep/refactor that shared symbol instead of deleting it.

- [ ] **Step 2: Search Laravel 13 testing/routing documentation**

Use Boost `search-docs` with `['route testing assert not found', 'route collection named routes', 'database schema has table']`. Follow the installed Laravel 13/Pest guidance.

- [ ] **Step 3: Generate and write the failing removal test**

Run:

```bash
php artisan make:test --pest DstRemovalTest --no-interaction
```

Test both route registration and behavior:

```php
it('does not register DST routes', function (): void {
    expect(Route::has('dst.index'))->toBeFalse()
        ->and(Route::has('dst.characters.index'))->toBeFalse()
        ->and(Route::has('dst.guides.index'))->toBeFalse()
        ->and(Route::has('admin.dst.items.edit'))->toBeFalse();
});

it('returns not found for removed DST URLs', function (string $url): void {
    $this->get($url)->assertNotFound();
})->with(['/dst', '/dst/characters', '/dst/guides', '/admin/dst/items/example/edit']);
```

Use the exact current route names discovered from `routes/web.php`; do not weaken the test to status-code ranges.

- [ ] **Step 4: Run and observe failure**

```bash
php artisan test tests/Feature/DstRemovalTest.php
```

- [ ] **Step 5: Remove route groups and shared navigation hooks**

Remove public/auth/admin DST routes, DST imports, header title logic, sidebar submenu, dashboard shortcut, layout resolver branch, and now-unused English/Vietnamese DST navigation keys. Preserve shared Game/Library behavior and translations.

- [ ] **Step 6: Delete DST-only code and adapt shared tests**

Delete the explicit groups above. Remove DST-specific cases from layout/header/sidebar/dashboard/global-layout tests while retaining assertions for Game, Library, auth, and default layout behavior. Remove `test:e2e:dst` and `test:e2e:dst:safety` scripts from `package.json`; do not remove shared Playwright dependencies used elsewhere.

- [ ] **Step 7: Run focused Nova tests**

```bash
php artisan test tests/Feature/DstRemovalTest.php
yarn test --runInBand resources/js/lib/__tests__/inertia-layouts.test.tsx resources/js/components/game/common resources/js/pages/dashboard
yarn eslint resources/js tests/frontend
yarn types
```

If a command's repository script uses a different exact test path, use the narrow existing script while preserving the same test scope.

- [ ] **Step 8: Inspect staged scope and commit**

Run:

```bash
git status --short
git diff --cached --name-status
```

Stage only the explicit DST deletions, route/shared-navigation edits, their tests, and `package.json`/lockfile if it changed. Confirm no Library, Spirit, Game asset, or unrelated migration change is staged.

```bash
git commit -m "refactor: remove DST application domain from Nova"
```

---

## Task 9: Remove Nova DST Data, Assets, and Database Tables

**Files:**

- Create via Artisan: `/Users/nyx/company/nova/database/migrations/*_drop_dst_tables.php`
- Delete: `/Users/nyx/company/nova/database/data/dst-import/character-profiles.json`
- Delete: `/Users/nyx/company/nova/database/data/dst-import/character-guides.json`
- Delete: `/Users/nyx/company/nova/public/assets/dst/**`
- Delete only after reference audit: DST-owned files under `/Users/nyx/company/nova/public/assets/guides/**`
- Delete historical migrations:
  - `/Users/nyx/company/nova/database/migrations/2026_07_23_000001_create_dst_core_tables.php`
  - `/Users/nyx/company/nova/database/migrations/2026_07_27_153351_create_dst_wiki_source_tables.php`
  - `/Users/nyx/company/nova/database/migrations/2026_07_27_154542_make_dst_wiki_image_titles_case_sensitive.php`
  - `/Users/nyx/company/nova/database/migrations/2026_07_27_154756_add_public_payload_to_dst_wiki_pages.php`
- Modify: `/Users/nyx/company/nova/tests/Feature/DstRemovalTest.php`

- [ ] **Step 1: Add a failing schema-removal assertion**

Append to `DstRemovalTest.php`:

```php
it('has no DST database tables', function (): void {
    foreach ([
        'dst_assets',
        'dst_items',
        'dst_guides',
        'dst_wiki_pages',
        'dst_import_manifests',
    ] as $table) {
        expect(Schema::hasTable($table))->toBeFalse();
    }
});
```

Use the complete table list from Step 3 in the final test, not only this abbreviated red-test sample.

- [ ] **Step 2: Run the focused test and observe failure when DST tables exist**

```bash
php artisan test tests/Feature/DstRemovalTest.php
```

- [ ] **Step 3: Create the cleanup migration**

Run:

```bash
php artisan make:migration drop_dst_tables --no-interaction
```

Implement `up(): void` with `Schema::dropIfExists()` in this exact dependency-safe order:

```text
dst_import_manifests
dst_guides
dst_wiki_structure_details
dst_wiki_recipe_ingredients
dst_wiki_recipes
dst_wiki_entity_mappings
dst_wiki_images
dst_wiki_pages
dst_wiki_import_runs
dst_extraction_errors
dst_conflicts
dst_evidence
dst_catalog_assets
dst_entity_relations
dst_runtime_coverage
dst_catalog_effects
dst_catalog_stats
dst_acquisition_sources
dst_catalog_recipe_ingredients
dst_catalog_recipes
dst_catalog_entities
dst_game_texts
dst_sources
dst_item_translations
dst_items
dst_assets
```

Implement `down(): void` as an intentional no-op with a PHPDoc explaining that DST removal is irreversible and restoring the feature requires reverting the removal commits plus restoring data. The migration must reference only `Schema`, never deleted models/services.

- [ ] **Step 4: Delete historical migrations after the cleanup migration exists**

Deleting the four historical DST migrations makes fresh installs skip creating DST tables; deployed databases still execute the new cleanup migration. Test both cases: a database initialized from current migrations and a test database with representative DST tables created before running the cleanup migration.

- [ ] **Step 5: Verify transferred sources/assets before deleting Nova copies**

For the two curated JSON files and all 28 portrait paths, compare the Nova source hash to the committed `dst_wiki` copy. Verify the standalone publication audit and Vercel Preview already passed. Then delete Nova's `database/data/dst-import/**` DST files and `public/assets/dst/**`.

- [ ] **Step 6: Delete only DST-owned guide assets after a reference audit**

Build the set of paths referenced by Nova's remaining non-DST code/data and the set already published in `dst_wiki`. Delete a Nova guide asset only when it is DST-owned, unreferenced by remaining Nova domains, and either present in `dst_wiki` or intentionally excluded as unpublished archive material. Do not delete `public/assets/game/**` or any Library/Game asset, even if it was staged during earlier work.

- [ ] **Step 7: Run migration and removal tests**

```bash
php artisan migrate --no-interaction
php artisan test tests/Feature/DstRemovalTest.php
vendor/bin/pint --dirty
```

Expected: all DST routes are 404 and every table in the complete list is absent.

- [ ] **Step 8: Commit the database/data cleanup with explicit staging**

Inspect `git status --short` and stage only the new cleanup migration, four historical migration deletions, DST manual data deletions, DST assets, audited guide asset deletions, and `DstRemovalTest.php`.

```bash
git commit -m "chore: remove DST data and database schema"
```

---

## Task 10: Final Cross-Repository Verification

**Files:**

- No new files expected
- Modify only regressions directly caused by Tasks 2–9, with a focused test first

- [ ] **Step 1: Verify `dst_wiki` from a clean dependency/build state**

```bash
cd /Users/nyx/company/dst_wiki
npm ci
python -m pytest tests/extract tests/crawl_wiki -q
npm test
npm run lint
npx tsc --noEmit
npm run build
```

- [ ] **Step 2: Verify Nova after DST removal**

```bash
cd /Users/nyx/company/nova
php artisan test tests/Feature/DstRemovalTest.php
yarn test --runInBand resources/js/lib/__tests__/inertia-layouts.test.tsx resources/js/components/game/common resources/js/pages/dashboard
yarn eslint resources/js tests/frontend
yarn types
vendor/bin/pint --dirty
yarn build
```

Ask the user whether to run Nova's entire Pest/Jest suites after the affected suites pass, as required by the repository guidance.

- [ ] **Step 3: Run final source and route scans**

In `dst_wiki`, distinguish permitted asset namespace `/assets/dst/**` from forbidden route paths. In Nova, run:

```bash
rg -n '(/dst\b|admin\.dst|dst\.|Dst[A-Z]|dst_)' routes app resources/js config database tests package.json playwright*.ts
```

Review every remaining match. Accept only the cleanup migration, the removal regression test, historical commit text outside runtime scope, or clearly unrelated prose. There must be no registered route, UI link, service/model, data file, asset reference, seed path, or Playwright DST harness.

- [ ] **Step 4: Recheck Vercel Preview after final standalone commits**

Verify the exact final `dst_wiki` commit on Preview, repeating representative route, JSON, and asset requests. Confirm `dst_wiki` remains independent if Nova is unavailable.

- [ ] **Step 5: Review commit and worktree scope**

```bash
git -C /Users/nyx/company/dst_wiki log --oneline --decorate -10
git -C /Users/nyx/company/dst_wiki status --short
git -C /Users/nyx/company/nova log --oneline --decorate -10
git -C /Users/nyx/company/nova status --short
```

Expected: `dst_wiki` has only intentional commits and a clean worktree. Nova may remain dirty because of the user's unrelated work, but no unrelated path was staged or committed by this extraction.

## Completion Checklist

- [ ] `dst_wiki` serves all five approved route families with Nova-quality DST content UI and its own simple header.
- [ ] Item, character, guide, cultivation, and Wiki detail flows pass automated and desktop/mobile checks.
- [ ] Published JSON/assets pass schema, duplicate, evidence-leak, asset-reference, and internal-route audits.
- [ ] Next production build and Vercel Preview require no runtime database or Nova access.
- [ ] Nova has no DST routes, navigation, frontend/backend domain code, data, assets, seed/import harness, or DST database tables.
- [ ] Nova `/dst...` and `/admin/dst...` return 404 without redirect.
- [ ] Affected Game, Library, layout, header/sidebar, and dashboard tests still pass.
- [ ] Unrelated Nova worktree changes remain untouched.
