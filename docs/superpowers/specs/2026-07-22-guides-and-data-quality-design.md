# Guides and Data Quality Design

**Date:** 2026-07-22
**Status:** Approved

## Objective

Add a dedicated DST Guides library at `/guides`, publish each guide at `/guides/[slug]`, expose Guides in the shared header, and introduce a repair-first quality gate that prevents incomplete catalog records from being published.

## Scope

This work is split into two sequential subsystems:

1. Crawl, normalize, and publish direct DST guide pages from `Category:Guides`.
2. Audit all published catalog data, repair recoverable records, and remove only records that remain unusable.

The category currently contains 107 direct members: 105 namespace-zero pages, one Board Thread, and one child category. The crawler must not recurse into `Category:Dedicated Servers`.

## Guide Eligibility

A page is publishable when all of the following are true:

- It is a direct namespace-zero member of `Category:Guides`.
- It is a guide article rather than the `Guides` overview page.
- Its instructions apply to Don't Starve Together.
- It is not exclusive to Shipwrecked, Hamlet, Reign of Giants, the single-player game, or an obsolete event.
- It has a stable canonical URL, usable article content, and at least one valid image suitable for a cover.

Rejected pages remain documented in the category config with a concrete reason. Child categories and non-content namespaces are rejected without recursion.

## Guide Data Contract

The published guide catalog contains lightweight entries for listing and separate detail payloads for reading. Every published guide has:

- a stable unique `id` derived from the canonical page identity;
- a unique URL-safe `slug`;
- the source title and Vietnamese display title;
- a short Vietnamese summary;
- a valid local cover image with dimensions and alternative text;
- normalized topic tags;
- an audience level: beginner, intermediate, or advanced;
- an estimated reading time derived from normalized text length;
- a table of contents generated from normalized section headings;
- cleaned article sections containing safe HTML and local image references;
- canonical source URL, revision identifier, revision timestamp, and content checksum.

The catalog parser rejects duplicate identifiers, duplicate slugs, missing covers, empty summaries, empty article bodies, unsafe markup, and malformed revision metadata.

## Routes and Components

### `/guides`

The index is a Server Component backed by the local guide catalog. It presents:

- the shared site header with `Guide` marked active;
- a compact editorial introduction;
- client-side search across title, summary, and normalized text;
- topic and audience filters;
- a featured guide area using real crawled imagery;
- a responsive two-column guide grid on desktop and one column below 768px;
- intentional empty and no-results states.

### `/guides/[slug]`

Each detail page is statically generated from the local catalog. It presents:

- a breadcrumb to `/guides`;
- title, Vietnamese summary, metadata, and cover image;
- a sticky table of contents beside a constrained reading column;
- semantic article sections with stable heading anchors;
- a collapsible table of contents on mobile;
- source URL, revision, and update time at the end of the article;
- a not-found response for unknown or unpublished slugs.

Guide details use a dedicated reading route and never open in the item side peek.

## Visual Direction

This is an editorial extension of the existing wiki interface. It preserves the current cool gray surfaces, blue accent, sans-serif typography, soft 16px content radius, and pill navigation.

- `DESIGN_VARIANCE: 5`
- `MOTION_INTENSITY: 3`
- `VISUAL_DENSITY: 5`

Motion is limited to hover, active, focus, disclosure, and filter feedback. All navigation remains on one line at desktop. Mobile navigation must remain usable without truncating Guide or hiding the active route.

## Data Quality Pipeline

The quality pipeline runs after Guide publication and covers every published item and guide.

### Audit

The audit records, at minimum:

- duplicate normalized `code`, entity ID, canonical URL, or guide slug;
- missing, empty, corrupt, or invalid JSON fields;
- missing title, summary, article content, essential structured information, or source evidence;
- missing image references, zero-sized images, corrupt files, unsupported formats, and unreachable source images;
- unresolved references and records whose detail payload cannot be parsed;
- exclusive content outside the DST scope.

### Repair

Repair is attempted before deletion:

- merge duplicate records around one canonical `code` or page identity;
- keep the most complete valid fields and newest supported revision;
- re-crawl missing detail and image assets from the canonical DST page;
- rebuild derived summaries, indexes, slugs, checksums, dimensions, and reading time;
- replace invalid image references with a valid crawled image from the same canonical page;
- normalize empty optional fields without weakening required publication rules.

### Removal

A record is removed only when it still fails the publication contract after repair. Each removal is written to a machine-readable report with its identity, source URL, failed rules, repair attempts, and final reason. Deletion never happens silently.

### Publication Invariant

After cleanup, every published record must have:

- a unique canonical identity and unique `code` where the entity schema uses codes;
- a valid locally served image;
- non-empty human-readable content;
- valid detail information appropriate to its type;
- parseable source and revision metadata;
- no known DST-scope violation.

## Error Handling

- Crawl and repair failures do not publish partial output.
- The previous valid artifact remains available until a complete replacement passes validation.
- A failed image download remains pending and blocks publication of that record.
- Invalid guide slugs return the standard not-found page.
- Search and filters operate on already validated local data and do not depend on Fandom availability.

## Testing

The implementation requires:

- Python tests for category eligibility, exclusions, normalization, image validation, duplicate repair, and removal reporting;
- TypeScript parser tests for guide catalog and detail contracts;
- component tests for header navigation, guide search, filters, cards, article layout, mobile table of contents, empty states, and not-found behavior;
- crawler manifest and checksum validation;
- full Python, Vitest, TypeScript, lint, and production build verification;
- a post-cleanup audit proving zero duplicate identities, zero missing required content, and zero invalid or missing images among published records.

## Deliverables

- reviewed `guides` category configuration;
- crawler and normalizer support required by the Guide contract;
- local guide catalog, detail payloads, and images;
- `/guides` and `/guides/[slug]` routes;
- shared header Guide navigation;
- repair-first audit command and machine-readable report;
- updated crawler control documentation;
- verification evidence for the final publication invariants.
