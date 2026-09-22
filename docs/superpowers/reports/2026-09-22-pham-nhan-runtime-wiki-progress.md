# Phàm Nhân Tu Tiên runtime wiki progress

## Baseline

- 2026-09-22: Shared worktree was already dirty. Web-file SHA-256 baselines were captured for `app/pham-nhan-tu-tien/page.tsx`, `app/pham-nhan-tu-tien/page.test.tsx`, `next.config.ts`, and `app/components/site-header.tsx` before this work started.
- 2026-09-22: Next 16.2.10 layouts/pages and server/client component guides read before frontend work. The interactive browser will be a client boundary fed serializable JSON by the server page.
- 2026-09-22: Ruling: no isolated worktree or commits are created because the task explicitly requires preserving a shared dirty workspace and forbids Git mutations beyond inspection. Cost if wrong: changes require careful before-write drift checks.

## Pre-flight interfaces

- Task 1 → Task 2: discovery emits ordered source files and their hashes; registration collection consumes only sources marked resolved.
- Task 2 → Task 3: normalized runtime recipes retain product, amount, conditions, image/atlas and evidence; catalog owns membership rather than recipes.
- Task 3 → Task 4 → Task 5: catalog/enrichment emit the shared Snapshot contract; export only validates/publishes it.
- Task 5 → Task 6: page imports generated JSON only; the browser owns hash navigation and does not import legacy Solo catalog data.

## Progress

- Task 1: discovery implemented and tested (nested local imports, comments/strings, disabled branch, missing-module diagnostic). Real source: 166 loaded modules, 41 registration files, no local unresolved imports.
- Task 2: declarative registration collector implemented and tested. It records final recipe-ID overrides, variants sharing a product, ingredients, output count, builder condition, station and source evidence without executing gameplay callbacks.
- Task 3: catalog implemented with active provider/recipe/source facts, explicit helper/boss exclusions, cooking predicates and two source-backed fusion recipes.
- Task 4–5: deterministic JSON/report builder and `--check` implemented. Ruling: sprite resolver returns no sprite rather than guessing atlas UV coordinates — cost if wrong: UI has placeholders until exact atlas publication is added.
- Task 6: main route now consumes the generated snapshot; legacy guide/config/alias routes and redirect removed. The independent Solo and Linh Giới routes were not modified.
- Task 7: acceptance report records current verification and the unresolved asset/browser acceptance work; this handoff is intentionally not marked complete.
