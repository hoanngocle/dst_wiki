# Vietnamese Items and Base Gallery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebrand the wiki as Don't Starve Together, localize the complete Items search experience to Vietnamese, and add a responsive `/base` image gallery placeholder.

**Architecture:** Keep `/` and `/base` as synchronous Server Component pages. Share one typed `SiteHeader` Server Component between them, retain `WikiSearch` as the only Client Component, and feed the Base gallery from a small typed local data module with local SVG assets.

**Tech Stack:** Next.js 16.2.10 App Router, React 19.2.4, TypeScript 5, Tailwind CSS 4, Vitest, React Testing Library, Next.js `Link` and `Image`.

## Global Constraints

- Replace `FROST ATLAS` with `Don't Starve Together`.
- The search label must be exactly `Tìm kiếm Items.`.
- Localize all visible Items UI, sample entry names, descriptions, keywords, category labels, metadata, and accessibility announcements.
- Keep internal categories as `item`, `creature`, `location`, and `quest`.
- Keep instant filtering, keyboard shortcuts, focus restoration, diacritic-insensitive matching, reduced motion, and the approved bright navy/cobalt visual system.
- `/base` must be a real route with six local image-and-name cards, responsive at one, two, and three columns.
- Do not add upload, persistence, authentication, base details, editing, deletion, sorting, remote image hosts, or a new UI library.
- Preserve unrelated tracked and untracked workspace changes.

---

## File Map

- Create `app/components/site-header.tsx`: shared brand and Items/Base route navigation.
- Create `app/components/site-header.test.tsx`: header link and active-state tests.
- Modify `app/components/wiki-search.tsx`: Vietnamese interface, category display map, counts, status, and empty state.
- Modify `app/components/wiki-search.test.tsx`: Vietnamese behavior and accessibility assertions.
- Modify `app/data/wiki-entries.ts`: eight translated neutral entries.
- Modify `app/page.tsx`: Vietnamese introduction and shared header.
- Modify `app/page.test.tsx`: rebrand, route navigation, localized shell, and no header count.
- Modify `app/layout.tsx`: Vietnamese metadata and document language.
- Create `app/data/base-entries.ts`: typed names and six local asset paths.
- Create `app/base/page.tsx`: server-rendered gallery route.
- Create `app/base/page.test.tsx`: gallery structure and card count.
- Create `public/base-placeholders/base-01.svg` through `base-06.svg`: neutral local 16:9 gallery artwork.

---

### Task 1: Shared navigation and Vietnamese Items search

**Files:**
- Create: `app/components/site-header.tsx`
- Create: `app/components/site-header.test.tsx`
- Modify: `app/components/wiki-search.tsx`
- Modify: `app/components/wiki-search.test.tsx`
- Modify: `app/data/wiki-entries.ts`
- Modify: `app/page.tsx`
- Modify: `app/page.test.tsx`
- Modify: `app/layout.tsx`

**Interfaces:**
- Produces: `SiteHeader({ active }: { active: "items" | "base" }): React.JSX.Element`.
- Preserves: `WikiSearch({ entries }: { entries: readonly WikiEntry[] }): React.JSX.Element`.
- Consumes: existing `WikiEntry`, `SearchCategory`, and filtering helpers.

- [ ] **Step 1: Write failing shared-header and localized-shell tests**

Create `app/components/site-header.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";

import { SiteHeader } from "./site-header";

it("links the shared navigation to Items and Base", () => {
  render(<SiteHeader active="items" />);
  expect(screen.getByText("Don't Starve Together")).toBeDefined();
  expect(screen.getByRole("link", { name: "Items" }).getAttribute("href")).toBe("/");
  expect(screen.getByRole("link", { name: "Base" }).getAttribute("href")).toBe("/base");
  expect(screen.getByRole("link", { name: "Items" }).getAttribute("aria-current")).toBe("page");
});
```

Replace `app/page.test.tsx` assertions with:

```tsx
it("renders the Vietnamese Don't Starve Together Items shell", () => {
  render(<Home />);
  expect(screen.getByText("Don't Starve Together")).toBeDefined();
  expect(screen.getByRole("heading", { level: 1, name: /Tìm nhanh/i })).toBeDefined();
  expect(screen.getByRole("searchbox", { name: "Tìm kiếm Items." })).toBeDefined();
  expect(screen.getByRole("link", { name: "Base" }).getAttribute("href")).toBe("/base");
  expect(screen.queryByText(/entries$/i)).toBeNull();
});
```

- [ ] **Step 2: Convert the component suite to Vietnamese and verify RED**

Use these exact public labels in `app/components/wiki-search.test.tsx`:

```ts
const searchName = "Tìm kiếm Items.";
// filters: "Tất cả", "Vật phẩm", "Sinh vật", "Địa điểm", "Nhiệm vụ"
// clear actions: "Xoá tìm kiếm", "Xoá bộ lọc"
// result counts: "2 mục", "1 mục"
// group name: "Lọc mục theo danh mục"
```

Add a diacritic regression:

```tsx
it("finds Vietnamese text when the query omits diacritics", () => {
  render(<WikiSearch entries={entries} />);
  fireEvent.change(screen.getByRole("searchbox", { name: searchName }), {
    target: { value: "vu khi" },
  });
  expect(screen.getByText("Lưỡi Kiếm Cổ")).toBeDefined();
});
```

Run:

```bash
npm test -- app/components/site-header.test.tsx app/page.test.tsx app/components/wiki-search.test.tsx
```

Expected: FAIL because `SiteHeader` does not exist and the page/component still render English copy.

- [ ] **Step 3: Implement the shared server header**

Create `app/components/site-header.tsx` with `next/link`, a typed active prop, `aria-current="page"` on the selected link, cobalt selected treatment, and 44px minimum touch targets:

```tsx
import Link from "next/link";

const links = [
  { id: "items", href: "/", label: "Items" },
  { id: "base", href: "/base", label: "Base" },
] as const;

export function SiteHeader({ active }: { active: (typeof links)[number]["id"] }) {
  return (
    <header className="border-b border-[#cbd5e1] bg-[#f8fafc]/90">
      <div className="mx-auto flex min-h-16 max-w-6xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-3 font-semibold tracking-[-0.02em] text-[#14233b]">
          <span aria-hidden="true" className="h-4 w-4 rotate-45 border-2 border-[#2e5fb3]" />
          <span>Don't Starve Together</span>
        </Link>
        <nav aria-label="Điều hướng chính" className="flex items-center gap-1">
          {links.map((link) => {
            const selected = active === link.id;
            return (
              <Link key={link.id} href={link.href} aria-current={selected ? "page" : undefined} className={selected ? "inline-flex min-h-11 items-center rounded-full bg-[#2e5fb3] px-4 text-sm font-semibold text-[#f8fafc]" : "inline-flex min-h-11 items-center rounded-full px-4 text-sm font-semibold text-[#53647a] hover:bg-[#e9eff6] hover:text-[#2e5fb3]"}>
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
```

- [ ] **Step 4: Localize Items data and search UI**

Translate the eight data records in `app/data/wiki-entries.ts`. Keep IDs/categories/accents stable, and use Vietnamese names such as `Lưỡi Kiếm Cổ`, `Đèn Dẫn Lối`, `Kẻ Rình Đầm Lầy`, and `Đài Quan Sát Windrest` with matching neutral Vietnamese descriptions and keywords.

In `app/components/wiki-search.tsx`, add a display map without changing internal category types:

```ts
const categoryLabels: Record<WikiEntry["category"], string> = {
  item: "Vật phẩm",
  creature: "Sinh vật",
  location: "Địa điểm",
  quest: "Nhiệm vụ",
};
```

Use exact Vietnamese labels defined in Step 2. Counts use `${results.length} mục`. Status text must include query and active category so equal-count result changes remain announced.

- [ ] **Step 5: Localize the page shell and metadata**

Use `<SiteHeader active="items" />` in `app/page.tsx`, replace the hero with `Tìm nhanh.` and `Chơi tiếp.`, and use `Tra cứu nhanh vật phẩm, sinh vật, nhiệm vụ và địa điểm.` as supporting copy.

In `app/layout.tsx`, set `<html lang="vi">` and:

```ts
export const metadata: Metadata = {
  title: "Don't Starve Together | Tra cứu Items",
  description: "Tra cứu nhanh vật phẩm, sinh vật, nhiệm vụ và địa điểm trong Don't Starve Together.",
};
```

- [ ] **Step 6: Run Task 1 tests and verify GREEN**

Run:

```bash
npm test -- app/components/site-header.test.tsx app/page.test.tsx app/components/wiki-search.test.tsx app/lib/wiki-search.test.ts
```

Expected: all Task 1 and domain tests pass, including keyboard, focus, live status, and Vietnamese no-diacritic search.

- [ ] **Step 7: Commit Task 1 only**

```bash
git add app/components/site-header.tsx app/components/site-header.test.tsx app/components/wiki-search.tsx app/components/wiki-search.test.tsx app/data/wiki-entries.ts app/page.tsx app/page.test.tsx app/layout.tsx
git commit -m "feat: localize Don't Starve Together items"
```

---

### Task 2: Base gallery route and local placeholder artwork

**Files:**
- Create: `app/data/base-entries.ts`
- Create: `app/base/page.tsx`
- Create: `app/base/page.test.tsx`
- Create: `public/base-placeholders/base-01.svg`
- Create: `public/base-placeholders/base-02.svg`
- Create: `public/base-placeholders/base-03.svg`
- Create: `public/base-placeholders/base-04.svg`
- Create: `public/base-placeholders/base-05.svg`
- Create: `public/base-placeholders/base-06.svg`

**Interfaces:**
- Consumes: `SiteHeader({ active: "base" })` from Task 1.
- Produces: `BaseEntry = { id: string; name: string; image: string }` and `baseEntries: readonly BaseEntry[]`.

- [ ] **Step 1: Write the failing Base page test**

Create `app/base/page.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";

import BasePage from "./page";

it("renders six named base image cards", () => {
  render(<BasePage />);
  expect(screen.getByRole("heading", { level: 1, name: "Thư viện Base" })).toBeDefined();
  expect(screen.getByRole("link", { name: "Base" }).getAttribute("aria-current")).toBe("page");
  expect(screen.getAllByRole("img")).toHaveLength(6);
  expect(screen.getAllByRole("listitem")).toHaveLength(6);
  expect(screen.getByText("Base Khởi Đầu")).toBeDefined();
});
```

Run:

```bash
npm test -- app/base/page.test.tsx
```

Expected: FAIL because the `/base` page does not exist.

- [ ] **Step 2: Add typed gallery data**

Create `app/data/base-entries.ts`:

```ts
export type BaseEntry = {
  id: string;
  name: string;
  image: string;
};

export const baseEntries: readonly BaseEntry[] = [
  { id: "starter", name: "Base Khởi Đầu", image: "/base-placeholders/base-01.svg" },
  { id: "meadow", name: "Base Ven Đồng Cỏ", image: "/base-placeholders/base-02.svg" },
  { id: "forest", name: "Base Rìa Rừng", image: "/base-placeholders/base-03.svg" },
  { id: "winter", name: "Base Mùa Đông", image: "/base-placeholders/base-04.svg" },
  { id: "coast", name: "Base Ven Biển", image: "/base-placeholders/base-05.svg" },
  { id: "mega", name: "Mega Base", image: "/base-placeholders/base-06.svg" },
];
```

- [ ] **Step 3: Create six local neutral SVG images**

Each SVG uses `viewBox="0 0 960 540"`, an opaque cool neutral background, thin cobalt/slate map lines, simple circles/rectangles representing a top-down layout, and a small `BASE 01` through `BASE 06` label. Do not use gradients, embedded fonts, external resources, or game characters.

- [ ] **Step 4: Implement the Server Component gallery**

Create `app/base/page.tsx` using `Image` from `next/image`, `<SiteHeader active="base" />`, and `baseEntries`. Use a `grid gap-5 sm:grid-cols-2 lg:grid-cols-3`, an `aspect-video` image wrapper, `fill`, `sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"`, `object-cover`, and a plain title row under each image. Cards remain non-clickable until detail routes exist.

- [ ] **Step 5: Run Task 2 tests and verify GREEN**

Run:

```bash
npm test -- app/base/page.test.tsx app/components/site-header.test.tsx
```

Expected: both Base gallery and shared-header tests pass.

- [ ] **Step 6: Run complete static verification**

Run:

```bash
npm test
npm run lint
npm run build
git diff --check
```

Expected: 0 test failures, lint exit 0, production build exit 0 with static `/` and `/base` routes, and no whitespace errors.

- [ ] **Step 7: Inspect desktop and mobile**

At 1440px and 375px, inspect `/` and `/base`. Confirm no page overflow, the header links remain usable, the Items search retains all interaction behavior, and the Base gallery resolves to three and one columns respectively with readable titles.

- [ ] **Step 8: Commit Task 2 only**

```bash
git add app/base/page.tsx app/base/page.test.tsx app/data/base-entries.ts public/base-placeholders
git commit -m "feat: add base gallery placeholder"
```
