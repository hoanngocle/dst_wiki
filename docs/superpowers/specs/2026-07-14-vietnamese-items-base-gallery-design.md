# Vietnamese Items and Base Gallery Design

Date: 2026-07-14
Status: Approved for implementation planning

## Goal

Rebrand the existing Frost Atlas demo as a Vietnamese Don't Starve Together reference. Localize the Items search experience and add a routable `/base` gallery placeholder for storing base screenshots later.

## Shared navigation

- Replace `FROST ATLAS` with `Don't Starve Together`.
- Use one shared header across both routes.
- Provide two clear navigation links: `Items` at `/` and `Base` at `/base`.
- Show the current route with the existing cobalt active treatment.
- Remove the entry count from the header.

## Items page

- Preserve the approved bright Frost Atlas layout, spacing, palette, search behavior, keyboard shortcuts, accessibility, and responsive rules.
- Replace the search label with `Tìm kiếm Items.`.
- Localize all visible interface text, live-region messages, filter labels, empty-state text, metadata, and document language to Vietnamese.
- Localize the eight neutral sample entries, including names, descriptions, keywords, and displayed category labels.
- Keep internal category identifiers in English so the existing typed filtering API remains stable.
- Continue matching Vietnamese text without sensitivity to case or diacritics.

## Base page

- Add a real `/base` route that is reachable from the shared header.
- Use a compact introduction with the title `Thư viện Base` and a short Vietnamese description.
- Render six local neutral placeholder images in a gallery inspired by the supplied card-grid reference.
- Each card contains only a 16:9 image and its base name.
- Use three columns on desktop, two on tablet, and one on narrow mobile screens.
- Keep placeholders clearly generic so they are not mistaken for real game screenshots.
- Store gallery metadata in a small typed data array so real screenshots can replace placeholders later without changing the layout.

## Components and data

- Extract a shared server-rendered site header used by `/` and `/base`.
- Keep `app/page.tsx` as a Server Component and retain the existing client-only search island.
- Add the base gallery as a Server Component because it has no interaction yet.
- Use local assets only; do not introduce remote image hosts or a new UI library.

## Verification

- Develop copy, navigation, and gallery behavior test-first.
- Verify Vietnamese search with and without diacritics.
- Verify both routes and active navigation states.
- Verify the gallery renders six image-and-name cards.
- Run the complete Vitest suite, ESLint, production build, and `git diff --check`.
- Inspect `/` and `/base` at desktop and 375px widths for overflow and readable card layout.

## Scope boundaries

Included: Vietnamese UI and sample data, shared Items/Base navigation, `/base` placeholder gallery, local placeholder assets.

Excluded: image upload, persistence, authentication, base detail pages, editing, deletion, sorting, and real game screenshots.
