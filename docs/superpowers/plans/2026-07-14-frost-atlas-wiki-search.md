# Frost Atlas Wiki Search Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a responsive Frost Atlas game wiki page that filters neutral mock entries instantly by text and category.

**Architecture:** Keep `app/page.tsx` as a synchronous Server Component and pass serializable mock entries into one focused `WikiSearch` Client Component. Put pure normalization and filtering logic in a framework-free module so it can be developed test-first and reused when database data replaces the mock array.

**Tech Stack:** Next.js 16.2.10 App Router, React 19.2.4, TypeScript 5, Tailwind CSS 4, Vitest, React Testing Library, Phosphor Icons.

## Global Constraints

- Use the approved Frost Atlas direction: fixed light theme, cool silver-blue surfaces, deep navy text, and one cobalt accent.
- Keep `DESIGN_VARIANCE: 5`, `MOTION_INTENSITY: 3`, and `VISUAL_DENSITY: 6`.
- Search filters on every keystroke with no submit button and no artificial debounce.
- Search matches name, description, category, and keywords after lowercase and diacritic normalization.
- Categories are All entries, Items, Creatures, Locations, and Quests.
- Use neutral mock data only. Do not imply a real game or real statistics.
- Keep the page responsive below 768px and usable by keyboard and touch.
- Use `@phosphor-icons/react` only for the search and clear icons. Do not add another component or icon library.
- Use zero em-dash or en-dash characters in visible copy.
- Preserve the Server Component boundary at `app/page.tsx`; only the search island gets `'use client'`.
- Respect `prefers-reduced-motion` for result transitions.
- Exclude database work, authentication, detail routes, CMS, pagination, dark mode, and analytics.

---

## File Map

- Modify `package.json`: add the test script and dependencies.
- Modify `package-lock.json`: lock Vitest, Testing Library, and Phosphor versions.
- Create `vitest.config.mts`: configure jsdom, React, and the existing `@/*` alias.
- Create `app/lib/wiki-search.ts`: own shared entry types, normalization, and pure filtering.
- Create `app/lib/wiki-search.test.ts`: verify normalization and filtering behavior.
- Create `app/data/wiki-entries.ts`: provide typed neutral mock entries.
- Create `app/components/wiki-search.tsx`: own interactive query, category, shortcuts, result rendering, and empty state.
- Create `app/components/wiki-search.test.tsx`: verify user-visible search behavior.
- Modify `app/page.tsx`: render the static Frost Atlas shell and pass mock data into the client island.
- Modify `app/layout.tsx`: replace starter metadata and keep Geist fonts at the root.
- Modify `app/globals.css`: define Frost Atlas tokens, body defaults, focus treatment, and reduced-motion fallback.
- Create `app/page.test.tsx`: verify the starter page is replaced by the Frost Atlas shell.

---

### Task 1: Search domain and test foundation

**Files:**
- Modify: `package.json`
- Modify: `package-lock.json`
- Create: `vitest.config.mts`
- Create: `app/lib/wiki-search.test.ts`
- Create: `app/lib/wiki-search.ts`

**Interfaces:**
- Consumes: no application code.
- Produces: `WikiCategory`, `WikiEntry`, `WikiEntryAccent`, `SearchCategory`, `normalizeSearchText(value: string): string`, and `filterWikiEntries(entries: readonly WikiEntry[], query: string, category: SearchCategory): WikiEntry[]`.

- [ ] **Step 1: Install the verified dependencies and add the test script**

Run:

```bash
npm install @phosphor-icons/react
npm install -D vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/dom vite-tsconfig-paths
```

Update `package.json` so the scripts contain:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint",
    "test": "vitest run"
  }
}
```

Expected: npm exits with code 0 and updates both `package.json` and `package-lock.json`.

- [ ] **Step 2: Configure Vitest using the Next.js 16 bundled guide**

Create `vitest.config.mts`:

```ts
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [tsconfigPaths(), react()],
  test: {
    environment: "jsdom",
    globals: true,
  },
});
```

Run:

```bash
npm test
```

Expected: Vitest exits with code 1 and reports that no test files were found. This confirms the runner starts before production search code exists.

- [ ] **Step 3: Write the failing normalization tests**

Create `app/lib/wiki-search.test.ts`:

```ts
import { describe, expect, it } from "vitest";

import { normalizeSearchText } from "./wiki-search";

describe("normalizeSearchText", () => {
  it("normalizes case and surrounding whitespace", () => {
    expect(normalizeSearchText("  Ancient Blade  ")).toBe("ancient blade");
  });

  it("removes combining diacritics", () => {
    expect(normalizeSearchText("Café Ruins")).toBe("cafe ruins");
  });
});
```

- [ ] **Step 4: Run the tests and verify RED**

Run:

```bash
npm test -- app/lib/wiki-search.test.ts
```

Expected: FAIL because `./wiki-search` does not exist.

- [ ] **Step 5: Add the minimal types and normalization implementation**

Create `app/lib/wiki-search.ts`:

```ts
export const wikiCategories = ["item", "creature", "location", "quest"] as const;

export type WikiCategory = (typeof wikiCategories)[number];
export type SearchCategory = "all" | WikiCategory;
export type WikiEntryAccent = "ice" | "moss" | "sand" | "slate";

export type WikiEntry = {
  id: string;
  name: string;
  category: WikiCategory;
  description: string;
  keywords: readonly string[];
  accent: WikiEntryAccent;
};

export function normalizeSearchText(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase();
}
```

- [ ] **Step 6: Run the normalization tests and verify GREEN**

Run:

```bash
npm test -- app/lib/wiki-search.test.ts
```

Expected: 2 tests pass.

- [ ] **Step 7: Add failing filter tests**

Append to `app/lib/wiki-search.test.ts`:

```ts
import type { WikiEntry } from "./wiki-search";
import { filterWikiEntries } from "./wiki-search";

const entries: readonly WikiEntry[] = [
  {
    id: "ancient-blade",
    name: "Ancient Blade",
    category: "item",
    description: "A relic weapon from the northern ruins.",
    keywords: ["sword", "rare"],
    accent: "ice",
  },
  {
    id: "mire-stalker",
    name: "Mire Stalker",
    category: "creature",
    description: "A territorial beast near flooded paths.",
    keywords: ["swamp", "beast"],
    accent: "moss",
  },
];

describe("filterWikiEntries", () => {
  it("preserves all entries for an empty query and all categories", () => {
    expect(filterWikiEntries(entries, "", "all")).toEqual(entries);
  });

  it.each(["blade", "relic", "item", "sword"])(
    "matches the searchable field %s",
    (query) => {
      expect(filterWikiEntries(entries, query, "all").map((entry) => entry.id)).toEqual([
        "ancient-blade",
      ]);
    },
  );

  it("combines category and text filters", () => {
    expect(filterWikiEntries(entries, "mire", "creature").map((entry) => entry.id)).toEqual([
      "mire-stalker",
    ]);
    expect(filterWikiEntries(entries, "mire", "item")).toEqual([]);
  });
});
```

- [ ] **Step 8: Run the filter tests and verify RED**

Run:

```bash
npm test -- app/lib/wiki-search.test.ts
```

Expected: FAIL because `filterWikiEntries` is not exported.

- [ ] **Step 9: Add the minimal filter implementation**

Append to `app/lib/wiki-search.ts`:

```ts
export function filterWikiEntries(
  entries: readonly WikiEntry[],
  query: string,
  category: SearchCategory,
): WikiEntry[] {
  const normalizedQuery = normalizeSearchText(query);

  return entries.filter((entry) => {
    const matchesCategory = category === "all" || entry.category === category;
    if (!matchesCategory) return false;
    if (!normalizedQuery) return true;

    const searchableText = normalizeSearchText(
      [entry.name, entry.description, entry.category, ...entry.keywords].join(" "),
    );

    return searchableText.includes(normalizedQuery);
  });
}
```

- [ ] **Step 10: Run the complete domain tests and verify GREEN**

Run:

```bash
npm test -- app/lib/wiki-search.test.ts
```

Expected: all normalization and filtering tests pass with no warnings.

- [ ] **Step 11: Commit the search domain**

```bash
git add package.json package-lock.json vitest.config.mts app/lib/wiki-search.ts app/lib/wiki-search.test.ts
git commit -m "test: add wiki search domain"
```

---

### Task 2: Interactive search island and mock data

**Files:**
- Create: `app/data/wiki-entries.ts`
- Create: `app/components/wiki-search.test.tsx`
- Create: `app/components/wiki-search.tsx`

**Interfaces:**
- Consumes: `WikiEntry`, `SearchCategory`, `filterWikiEntries`, and `normalizeSearchText` from `app/lib/wiki-search.ts`.
- Produces: `WikiSearch({ entries }: { entries: readonly WikiEntry[] }): React.JSX.Element` for `app/page.tsx`.

- [ ] **Step 1: Write the failing default and text-filter tests**

Create `app/components/wiki-search.test.tsx`:

```tsx
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { WikiEntry } from "@/app/lib/wiki-search";
import { WikiSearch } from "./wiki-search";

const entries: readonly WikiEntry[] = [
  {
    id: "ancient-blade",
    name: "Ancient Blade",
    category: "item",
    description: "A relic weapon from the northern ruins.",
    keywords: ["sword"],
    accent: "ice",
  },
  {
    id: "mire-stalker",
    name: "Mire Stalker",
    category: "creature",
    description: "A beast near flooded paths.",
    keywords: ["swamp"],
    accent: "moss",
  },
];

describe("WikiSearch", () => {
  it("shows every entry before the user filters", () => {
    render(<WikiSearch entries={entries} />);
    expect(screen.getByText("Ancient Blade")).toBeDefined();
    expect(screen.getByText("Mire Stalker")).toBeDefined();
    expect(screen.getByText("2 entries")).toBeDefined();
  });

  it("filters immediately as the user types", () => {
    render(<WikiSearch entries={entries} />);
    fireEvent.change(screen.getByRole("searchbox", { name: "Search the atlas" }), {
      target: { value: "mire" },
    });
    expect(screen.queryByText("Ancient Blade")).toBeNull();
    expect(screen.getByText("Mire Stalker")).toBeDefined();
    expect(screen.getByText("1 entry")).toBeDefined();
  });
});
```

- [ ] **Step 2: Complete the failing component behavior suite**

Insert these tests before the final `});` in `app/components/wiki-search.test.tsx`:

```tsx
it("filters by category", () => {
  render(<WikiSearch entries={entries} />);
  fireEvent.click(screen.getByRole("button", { name: "Items" }));
  expect(screen.getByText("Ancient Blade")).toBeDefined();
  expect(screen.queryByText("Mire Stalker")).toBeNull();
});

it("clears query and category from the empty state", () => {
  render(<WikiSearch entries={entries} />);
  fireEvent.click(screen.getByRole("button", { name: "Items" }));
  fireEvent.change(screen.getByRole("searchbox", { name: "Search the atlas" }), {
    target: { value: "mire" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Clear filters" }));
  expect(screen.getByRole("searchbox", { name: "Search the atlas" })).toHaveProperty("value", "");
  expect(screen.getByRole("button", { name: "All entries" }).getAttribute("aria-pressed")).toBe("true");
});

it("highlights matching text", () => {
  render(<WikiSearch entries={entries} />);
  fireEvent.change(screen.getByRole("searchbox", { name: "Search the atlas" }), {
    target: { value: "blade" },
  });
  expect(screen.getByText("Blade").tagName).toBe("MARK");
});

it("focuses search when slash is pressed outside an editable control", () => {
  render(<WikiSearch entries={entries} />);
  fireEvent.keyDown(window, { key: "/" });
  expect(document.activeElement).toBe(screen.getByRole("searchbox", { name: "Search the atlas" }));
});

it("focuses search when Control K is pressed", () => {
  render(<WikiSearch entries={entries} />);
  fireEvent.keyDown(window, { key: "k", ctrlKey: true });
  expect(document.activeElement).toBe(screen.getByRole("searchbox", { name: "Search the atlas" }));
});

it("clears the query with Escape", () => {
  render(<WikiSearch entries={entries} />);
  const search = screen.getByRole("searchbox", { name: "Search the atlas" });
  fireEvent.change(search, { target: { value: "mire" } });
  fireEvent.keyDown(search, { key: "Escape" });
  expect(search).toHaveProperty("value", "");
});
```

- [ ] **Step 3: Run the complete component suite and verify RED**

Run:

```bash
npm test -- app/components/wiki-search.test.tsx
```

Expected: FAIL because `app/components/wiki-search.tsx` does not exist.

- [ ] **Step 4: Add neutral mock entries**

Create `app/data/wiki-entries.ts` with two entries in each category:

```ts
import type { WikiEntry } from "@/app/lib/wiki-search";

export const wikiEntries: readonly WikiEntry[] = [
  { id: "ancient-blade", name: "Ancient Blade", category: "item", description: "A relic weapon recovered from the northern ruins.", keywords: ["sword", "rare", "relic"], accent: "ice" },
  { id: "wayfinder-lantern", name: "Wayfinder Lantern", category: "item", description: "A travel tool that glows near hidden passages.", keywords: ["tool", "light", "exploration"], accent: "sand" },
  { id: "mire-stalker", name: "Mire Stalker", category: "creature", description: "A territorial creature found beside flooded paths.", keywords: ["swamp", "beast", "hostile"], accent: "moss" },
  { id: "glasswing-moth", name: "Glasswing Moth", category: "creature", description: "A passive night creature drawn to cold light.", keywords: ["flying", "passive", "night"], accent: "ice" },
  { id: "hollow-crossing", name: "The Hollow Crossing", category: "location", description: "A forgotten route beneath the old city.", keywords: ["underground", "ruins", "route"], accent: "slate" },
  { id: "windrest-observatory", name: "Windrest Observatory", category: "location", description: "A mountain station built to chart distant storms.", keywords: ["mountain", "tower", "weather"], accent: "ice" },
  { id: "borrowed-map", name: "The Borrowed Map", category: "quest", description: "Return a marked survey map before the next expedition.", keywords: ["exploration", "delivery", "survey"], accent: "sand" },
  { id: "quiet-bell", name: "The Quiet Bell", category: "quest", description: "Discover why the village signal no longer sounds.", keywords: ["mystery", "village", "investigation"], accent: "slate" },
];
```

- [ ] **Step 5: Add the minimal interactive component that satisfies the suite**

Create `app/components/wiki-search.tsx` with `'use client'`, `useMemo`, `useRef`, `useState`, and `useEffect`. The implementation must:

```tsx
"use client";

import { MagnifyingGlass, X } from "@phosphor-icons/react";
import { useEffect, useMemo, useRef, useState } from "react";

import {
  filterWikiEntries,
  normalizeSearchText,
  type SearchCategory,
  type WikiEntry,
} from "@/app/lib/wiki-search";

const filters: readonly { value: SearchCategory; label: string }[] = [
  { value: "all", label: "All entries" },
  { value: "item", label: "Items" },
  { value: "creature", label: "Creatures" },
  { value: "location", label: "Locations" },
  { value: "quest", label: "Quests" },
];

const accentClasses: Record<WikiEntry["accent"], string> = {
  ice: "bg-[#d6e2ef] text-[#315d91]",
  moss: "bg-[#dce5da] text-[#436247]",
  sand: "bg-[#e8dfd1] text-[#795f3d]",
  slate: "bg-[#d9dee6] text-[#46566d]",
};

function HighlightedText({ text, query }: { text: string; query: string }) {
  const normalizedQuery = normalizeSearchText(query);
  if (!normalizedQuery) return text;

  const normalizedText = normalizeSearchText(text);
  const matchIndex = normalizedText.indexOf(normalizedQuery);
  if (matchIndex < 0) return text;

  const matchEnd = matchIndex + normalizedQuery.length;
  return (
    <>
      {text.slice(0, matchIndex)}
      <mark className="rounded-sm bg-[#dce7f7] px-0.5 text-inherit">
        {text.slice(matchIndex, matchEnd)}
      </mark>
      {text.slice(matchEnd)}
    </>
  );
}

export function WikiSearch({ entries }: { entries: readonly WikiEntry[] }) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<SearchCategory>("all");
  const inputRef = useRef<HTMLInputElement>(null);
  const results = useMemo(
    () => filterWikiEntries(entries, query, category),
    [entries, query, category],
  );

  useEffect(() => {
    function handleShortcut(event: KeyboardEvent) {
      const target = event.target as HTMLElement | null;
      const isEditable =
        target?.isContentEditable ||
        target?.tagName === "INPUT" ||
        target?.tagName === "TEXTAREA" ||
        target?.tagName === "SELECT";

      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        inputRef.current?.focus();
      } else if (event.key === "/" && !isEditable) {
        event.preventDefault();
        inputRef.current?.focus();
      }
    }

    window.addEventListener("keydown", handleShortcut);
    return () => window.removeEventListener("keydown", handleShortcut);
  }, []);

  function resetFilters() {
    setQuery("");
    setCategory("all");
    inputRef.current?.focus();
  }

  const countLabel = `${results.length} ${results.length === 1 ? "entry" : "entries"}`;

  return (
    <section aria-labelledby="atlas-results" className="mt-8">
      <div className="relative">
        <label htmlFor="atlas-search" className="mb-2 block text-sm font-medium text-[#263b58]">
          Search the atlas
        </label>
        <div className="relative">
          <MagnifyingGlass aria-hidden="true" size={20} weight="regular" className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-[#2e5fb3]" />
          <input
            ref={inputRef}
            id="atlas-search"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Escape") setQuery("");
            }}
            placeholder="Search items, creatures, locations..."
            aria-describedby="atlas-search-help"
            className="h-14 w-full rounded-[10px] border border-[#a8b8cc] bg-[#f8fafc] pl-12 pr-28 text-base text-[#14233b] shadow-[0_10px_28px_rgba(34,61,96,0.08)] outline-none transition focus:border-[#2e5fb3] focus:ring-4 focus:ring-[#2e5fb3]/15"
          />
          {query ? (
            <button type="button" onClick={() => setQuery("")} aria-label="Clear search" className="absolute right-3 top-1/2 inline-flex -translate-y-1/2 items-center gap-1 rounded-md px-2 py-1 text-sm text-[#53647a] hover:bg-[#e9eff6] active:scale-[0.98]">
              <X aria-hidden="true" size={16} /> Clear
            </button>
          ) : (
            <kbd className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 rounded-md border border-[#c7d1de] bg-[#eef3f8] px-2 py-1 font-mono text-xs text-[#637287]">⌘ K</kbd>
          )}
        </div>
        <p id="atlas-search-help" className="sr-only">Search by name, description, category, or keyword.</p>
      </div>

      <div className="mt-3 flex gap-2 overflow-x-auto pb-2" aria-label="Filter entries by category">
        {filters.map((filter) => (
          <button key={filter.value} type="button" aria-pressed={category === filter.value} onClick={() => setCategory(filter.value)} className="shrink-0 rounded-full border border-[#cbd5e1] px-3 py-1.5 text-sm font-medium text-[#5c6b80] transition hover:border-[#2e5fb3] hover:text-[#2e5fb3] active:scale-[0.98] aria-pressed:border-[#2e5fb3] aria-pressed:bg-[#2e5fb3] aria-pressed:text-white">
            {filter.label}
          </button>
        ))}
      </div>

      <div className="mt-7 flex items-end justify-between gap-4">
        <h2 id="atlas-results" className="text-lg font-semibold tracking-tight text-[#14233b]">Explore the atlas</h2>
        <p aria-live="polite" className="text-sm text-[#67758a]">{countLabel}</p>
      </div>

      {results.length ? (
        <ul className="mt-3 border-t border-[#cbd5e1]">
          {results.map((entry) => (
            <li key={entry.id} className="grid grid-cols-[48px_minmax(0,1fr)_auto] items-center gap-3 border-b border-[#cbd5e1] py-4 motion-safe:animate-[atlas-result-in_180ms_ease-out] md:grid-cols-[48px_minmax(0,1fr)_auto] md:gap-4">
              <div aria-hidden="true" className={`flex h-11 w-12 items-center justify-center rounded-md font-mono text-xs font-semibold uppercase ${accentClasses[entry.accent]}`}>{entry.category.slice(0, 2)}</div>
              <div className="min-w-0">
                <h3 className="font-semibold text-[#172943]"><HighlightedText text={entry.name} query={query} /></h3>
                <p className="mt-1 line-clamp-2 text-sm leading-6 text-[#67758a]"><HighlightedText text={entry.description} query={query} /></p>
              </div>
              <span className="hidden rounded-full bg-[#dce6f4] px-2.5 py-1 text-xs font-medium capitalize text-[#2e5fb3] sm:inline-flex">{entry.category}</span>
            </li>
          ))}
        </ul>
      ) : (
        <div className="mt-3 border-y border-[#cbd5e1] py-14 text-center">
          <h3 className="text-lg font-semibold text-[#14233b]">No entries found</h3>
          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[#67758a]">Try another search or clear the current filters.</p>
          <button type="button" onClick={resetFilters} className="mt-5 rounded-[10px] bg-[#2e5fb3] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#264f96] active:scale-[0.98]">Clear filters</button>
        </div>
      )}
    </section>
  );
}
```

- [ ] **Step 6: Run the complete component tests and verify GREEN**

Run:

```bash
npm test -- app/components/wiki-search.test.tsx
```

Expected: all 8 tests pass. If a test fails, change production behavior rather than weakening the assertion.

- [ ] **Step 7: Commit the interactive search island**

```bash
git add app/data/wiki-entries.ts app/components/wiki-search.tsx app/components/wiki-search.test.tsx
git commit -m "feat: add interactive wiki search"
```

---

### Task 3: Frost Atlas page shell and visual system

**Files:**
- Create: `app/page.test.tsx`
- Modify: `app/page.tsx`
- Modify: `app/layout.tsx`
- Modify: `app/globals.css`

**Interfaces:**
- Consumes: `wikiEntries` from `app/data/wiki-entries.ts` and `WikiSearch` from `app/components/wiki-search.tsx`.
- Produces: the complete `/` route and static metadata for Frost Atlas.

- [ ] **Step 1: Write the failing page-shell test**

Create `app/page.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";

import Home from "./page";

it("renders the Frost Atlas search shell", () => {
  render(<Home />);
  expect(screen.getByText("FROST ATLAS")).toBeDefined();
  expect(screen.getByRole("heading", { level: 1, name: /Find answers/i })).toBeDefined();
  expect(screen.getByRole("searchbox", { name: "Search the atlas" })).toBeDefined();
});
```

- [ ] **Step 2: Run the page test and verify RED**

Run:

```bash
npm test -- app/page.test.tsx
```

Expected: FAIL because the starter page does not render Frost Atlas.

- [ ] **Step 3: Replace the starter page with the Server Component shell**

Replace `app/page.tsx`:

```tsx
import { WikiSearch } from "@/app/components/wiki-search";
import { wikiEntries } from "@/app/data/wiki-entries";

export default function Home() {
  return (
    <main className="min-h-[100dvh] bg-[#edf1f5] text-[#14233b]">
      <header className="border-b border-[#cbd5e1] bg-[#f8fafc]/90">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3 font-semibold tracking-[0.08em]">
            <span aria-hidden="true" className="h-4 w-4 rotate-45 border-2 border-[#2e5fb3]" />
            <span>FROST ATLAS</span>
          </div>
          <span className="hidden font-mono text-xs text-[#67758a] sm:block">{wikiEntries.length} entries</span>
        </div>
      </header>

      <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 sm:py-16 lg:px-8">
        <div className="grid items-end gap-5 md:grid-cols-[minmax(0,1fr)_280px] md:gap-10">
          <h1 className="max-w-2xl text-4xl font-semibold leading-[1.02] tracking-[-0.045em] text-[#14233b] sm:text-5xl lg:text-6xl">
            Find answers.<br />Keep playing.
          </h1>
          <p className="max-w-[34ch] text-base leading-7 text-[#67758a] md:justify-self-end">
            A fast reference for items, creatures, quests and locations.
          </p>
        </div>
        <WikiSearch entries={wikiEntries} />
      </div>
    </main>
  );
}
```

- [ ] **Step 4: Replace starter metadata while preserving the documented font setup**

Update `app/layout.tsx` metadata and body language:

```tsx
export const metadata: Metadata = {
  title: "Frost Atlas | Game Wiki Search",
  description: "Search a clear, fast reference for game items, creatures, quests and locations.",
};
```

Keep Geist and Geist Mono from `next/font/google`. Set `<html lang="en">` and keep the CSS variables on the root element.

- [ ] **Step 5: Define the global Frost Atlas tokens and defaults**

Replace the starter color rules in `app/globals.css` while preserving `@import "tailwindcss"`:

```css
@import "tailwindcss";

:root {
  --background: #edf1f5;
  --foreground: #14233b;
  --surface: #f8fafc;
  --muted: #67758a;
  --line: #cbd5e1;
  --accent: #2e5fb3;
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --font-sans: var(--font-geist-sans);
  --font-mono: var(--font-geist-mono);
}

* {
  box-sizing: border-box;
}

html {
  min-width: 320px;
  background: var(--background);
}

body {
  min-height: 100%;
  margin: 0;
  background: var(--background);
  color: var(--foreground);
  font-family: var(--font-geist-sans), Arial, Helvetica, sans-serif;
}

button,
input {
  font: inherit;
}

::selection {
  color: #f8fafc;
  background: var(--accent);
}

@keyframes atlas-result-in {
  from {
    opacity: 0.65;
    transform: translateY(2px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
  }
}
```

- [ ] **Step 6: Run the page and component tests and verify GREEN**

Run:

```bash
npm test
```

Expected: all domain, component, and page tests pass.

- [ ] **Step 7: Run static verification**

Run:

```bash
npm run lint
npm run build
```

Expected: both commands exit with code 0 and produce no warnings that require action.

- [ ] **Step 8: Commit the Frost Atlas page**

```bash
git add app/page.tsx app/page.test.tsx app/layout.tsx app/globals.css
git commit -m "feat: build Frost Atlas wiki page"
```

---

### Task 4: Browser verification and final polish

**Files:**
- Modify only files identified by a failing verification check.

**Interfaces:**
- Consumes: the complete `/` route from Tasks 1 through 3.
- Produces: a visually verified responsive demo with a clean final test run.

- [ ] **Step 1: Start the app and inspect desktop behavior**

Run:

```bash
npm run dev
```

Open `http://localhost:3000` at approximately 1440px width. Verify:

- Search, filters, result count, and list are visible without horizontal overflow.
- Search matches name, description, category, and keyword.
- Search and category filters work together.
- Clear search and Clear filters return to the default state.
- `/`, `Cmd + K`, `Ctrl + K`, and `Escape` work as specified.
- Focus rings remain visible.

- [ ] **Step 2: Inspect mobile behavior**

At 375px width, verify:

- The intro stacks into one column.
- Search remains full width.
- Category buttons scroll horizontally without clipping page content.
- Rows remain readable and category pills hide as specified.
- Touch targets remain at least 40px tall.

- [ ] **Step 3: Run the taste-skill pre-flight subset relevant to product UI**

Verify mechanically:

```bash
rg -n '—|–|#[0]{6}|purple|violet|linear-gradient|radial-gradient' app || true
```

Expected: no em-dash or en-dash visible copy, no pure black, no purple defaults, and no gradients.

Manually confirm:

- One cobalt accent is used consistently.
- Controls follow the approved radius rules.
- Input, placeholder, buttons, and focus rings have readable contrast.
- No fake links, disabled-looking controls, decorative status dots, or duplicate actions appear.
- All visible copy reads naturally and describes neutral mock data.

- [ ] **Step 4: Run final verification from a clean command invocation**

Run:

```bash
npm test
npm run lint
npm run build
git diff --check
```

Expected: tests pass, lint passes, production build succeeds, and `git diff --check` prints nothing.

- [ ] **Step 5: Commit only if polish changed files**

```bash
git add app package.json package-lock.json vitest.config.mts
git commit -m "fix: polish Frost Atlas search experience"
```

If Step 1 through Step 3 required no file changes, skip this commit and keep the verified commits from earlier tasks.
