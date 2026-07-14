# Frost Atlas Wiki Search Design

Date: 2026-07-14
Status: Approved for implementation planning

## Product goal

Build a polished demo for a game wiki search page. The page places one search input near the top, displays neutral mock game data below it, and filters results instantly while the user types. The demo should establish the visual and interaction foundation for a database-backed version without coupling the UI to a future schema or API.

## Design direction

Reading this as: a search-first game knowledge product for players who want fast answers, using a bright, structured visual language with a restrained game identity.

Selected direction: **Frost Atlas**.

- `DESIGN_VARIANCE: 5` - offset enough to feel designed, but predictable enough for fast scanning.
- `MOTION_INTENSITY: 3` - tactile hover, focus, and result transitions only.
- `VISUAL_DENSITY: 6` - compact result rows with comfortable spacing.
- Theme: fixed light theme for this demo, following the explicitly selected bright direction.
- Palette: cool silver-blue surfaces, deep navy text, and one cobalt accent.
- Shape system: 10px controls, 6px thumbnails, and pill-only category filters.
- Typography: Geist Sans and Geist Mono through `next/font`.

The taste skill is applied to visual hierarchy, color consistency, shape consistency, readable copy, responsive behavior, and accessibility. Its landing-page patterns are not applied because this page is a product search interface.

## Page structure

1. A compact top bar contains the Frost Atlas mark and total entry count.
2. A short headline introduces the page without competing with search.
3. A large search input is the main interaction.
4. Category filters support discovery: All entries, Items, Creatures, Locations, and Quests.
5. A result count and result list appear below the controls.
6. Results use horizontal rows rather than a card grid so the page scales cleanly as data grows.

The desktop content container is centered with a maximum readable width. Below 768px, all content collapses to one column, category filters scroll horizontally, and result metadata is reduced to the essentials.

## Component architecture

### Server shell

`app/page.tsx` remains a Server Component. It owns the static page shell and passes mock entries into the interactive search island.

### Client search island

`app/components/wiki-search.tsx` is a Client Component responsible for:

- Query state.
- Active category state.
- Keyboard shortcuts.
- Derived filtered results.
- Accessible result announcements.

The client island is split into small local components:

- `SearchInput`
- `CategoryFilters`
- `ResultList`
- `ResultRow`
- `EmptyState`
- `HighlightedText`

The components remain in one focused file for the initial demo. They can be extracted when the real data model or detail routes create independent reuse.

### Mock data

`app/data/wiki-entries.ts` exports typed neutral sample data across four categories. Each entry contains:

- `id`
- `name`
- `category`
- `description`
- `keywords`
- `accent`

The `accent` field selects from a controlled set of cool neutral thumbnail treatments. No fake statistics or unsupported game claims are used.

## Search behavior

Search filters immediately on each keystroke without a submit button or artificial debounce. The initial dataset is small enough that synchronous filtering is the simplest and fastest implementation.

Filtering rules:

1. Trim the query.
2. Convert query and searchable fields to lowercase.
3. Normalize diacritics for forgiving matching.
4. Match against name, description, category, and keywords.
5. Apply the active category after text matching.
6. Preserve the original data order.

The result count updates immediately. Matching text in result names and descriptions is highlighted with React elements, never raw HTML injection.

Keyboard behavior:

- `/` focuses search when the user is not typing in another editable control.
- `Cmd + K` or `Ctrl + K` focuses search.
- `Escape` clears the current query and keeps focus in the input.

## UI states

### Default

The page shows all entries and the All entries filter is active.

### Filtering

The list and result count update immediately. A subtle opacity and transform transition communicates that the result set changed. Reduced-motion preferences disable the transform.

### No results

An inline empty state explains that no entries match and provides one clear action to clear the query and category filter.

### Future loading and error states

The mock-data demo has no asynchronous loading or network failure. The list boundary is designed so a database integration can later replace it with row-shaped skeletons or an inline loading error without changing the page layout.

## Responsive behavior

### Desktop and tablet

- The brand and entry count remain on one line.
- Headline and short description share an aligned two-column intro.
- Search spans the content width.
- Result rows show thumbnail, name, description, and category.

### Mobile below 768px

- The entry count is hidden while the brand remains visible.
- Intro content stacks vertically.
- Search remains full width.
- Category filters use horizontal overflow.
- Result rows show thumbnail, name, category, and a shortened description.
- Page padding reduces to 16px.

## Accessibility

- The search field has a visible label and accessible description.
- Category filters use real buttons with `aria-pressed`.
- Result changes are announced through a polite live region.
- Focus states remain visible and meet contrast requirements.
- Body text, input text, placeholders, and controls target WCAG AA contrast.
- Controls are usable by keyboard and touch.
- Motion respects `prefers-reduced-motion`.

## Visual implementation notes

- Use Tailwind CSS v4 already present in the project.
- Use CSS custom properties for the Frost Atlas color tokens.
- Use `@phosphor-icons/react` for the search and clear icons. Verify and install the dependency before importing it.
- Do not introduce a second component library or design system.
- Do not use gradients for page backgrounds, glow effects, glassmorphism, or generic equal card grids.
- Use thin dividers and negative space for result grouping.
- Result rows are informational in this demo. Detail navigation is excluded until a real detail route exists.

## Metadata and copy

Update the root metadata to describe Frost Atlas rather than the default Next.js starter. Visible copy uses a single clear product register and avoids game-specific lore that could imply real source data.

## Verification

Implementation verification covers:

- ESLint.
- Next.js production build.
- Filtering by name, description, category, and keyword.
- Category and query filters working together.
- Keyboard focus and clear behavior.
- Empty-state reset behavior.
- Desktop and mobile visual inspection.
- Reduced-motion behavior.
- Copy audit for clarity and consistency.

## Scope boundaries

Included:

- One responsive search page.
- Neutral mock data.
- Instant client-side filtering.
- Category filters.
- Default, filtering, and empty states.

Excluded:

- Database schema and API integration.
- Authentication.
- Wiki entry detail pages.
- Content management.
- Pagination or virtualization.
- Dark mode for this initial bright-direction demo.
- Analytics and production search ranking.
