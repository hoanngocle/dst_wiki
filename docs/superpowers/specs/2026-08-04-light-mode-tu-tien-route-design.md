# Light Mode and Tu Tiên Route Design

## Goal

Restore the standalone DST Wiki's original light appearance while simplifying the guide surface to one cultivation page at `/tu-tien`.

## Approved Product Behavior

- The public navigation contains three tabs: `Vật phẩm`, `Nhân vật`, and `Cảnh giới Tu Tiên`.
- `Cảnh giới Tu Tiên` links directly to `/tu-tien` and is marked active on that page.
- `/tu-tien` renders the existing optimized cultivation progression content with all 15 stages, pills, ingredients, images, responsive cards/table treatment, and accessibility behavior preserved.
- `/guides`, `/guides/canh-gioi-tu-tien`, and every former `/guides/[slug]` URL return 404. There are no redirects or compatibility aliases.
- The four DST guide articles are unpublished and removed from the runtime, generated public data, tests, and guide-only asset set.

## Visual Design

- Restore the exact original standalone light palette from commit `6270784`:
  - background `#edf1f5`
  - foreground `#14233b`
  - surface `#f8fafc`
  - muted text `#53647a`
  - line `#cbd5e1`
  - accent `#2e5fb3`
- Preserve the optimized layouts, spacing, responsive behavior, modal behavior, focus states, content visibility optimization, and reduced-motion handling introduced during the Nova UI port.
- Retarget the existing `nova-*` semantic color tokens to accessible light values where components still consume those tokens; do not duplicate or rewrite every component class solely to rename tokens.
- Selection, focus rings, hover states, cards, dialogs, tab controls, tables, and Wiki content must maintain readable contrast in light mode.

## Code and Data Boundaries

- Move the cultivation page from `app/guides/canh-gioi-tu-tien/page.tsx` to `app/tu-tien/page.tsx`, retaining Server Component behavior.
- Delete the generic guide index and dynamic guide route tree.
- Delete generic guide browser/reader/catalog/content modules and tests only after confirming they have no non-guide consumers.
- Remove the four guide records from public/generated guide JSON and publication expectations.
- Delete the four guide cover/content assets under `public/assets/guides/` after reference checks confirm the cultivation page does not use them.
- Keep cultivation data and sprite assets used by `/tu-tien`.

## Testing and Verification

- TDD route/navigation tests must fail before implementation and then prove:
  - the header links `Cảnh giới Tu Tiên` to `/tu-tien`;
  - `/tu-tien` renders all 15 stages;
  - no generic guide static params, catalog records, or guide-only public assets remain;
  - former guide URLs are absent from the static build and return 404 when served.
- Add light-theme assertions for the original palette and navigation/header contrast contracts.
- Run the focused tests first, then the full Vitest suite, publication audit, ESLint, TypeScript, and production build.
- Perform desktop and mobile visual checks for `/`, `/characters`, and `/tu-tien`, including character/item dialogs and horizontal overflow.

## Deployment

- Commit the implementation on the existing extraction branch.
- Push the verified final commit to `master` only after independent review, allowing the existing Vercel Git integration to deploy Production.
- Smoke-test `/`, `/characters`, and `/tu-tien`; confirm former guide routes return 404 without redirect.

## Out of Scope

- No changes to Nova.
- No dark-mode toggle or user-selectable theme.
- No guide redirects, aliases, archive UI, or replacement article system.
- No redesign of the optimized item, character, Wiki, modal, or cultivation layouts.
