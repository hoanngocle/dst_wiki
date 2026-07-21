# Mob and Boss Catalog Normalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish complete, phase-aware DST and Tu Tiên Mob/Boss details and merge `alterguardian_phase3dead` into the canonical Celestial Champion Boss with accurate post-defeat mining rewards.

**Architecture:** Extend canonical extraction with per-prefab classification and shared/direct reward parsing, then normalize Mob/Boss candidates through an explicit grouping manifest into a typed detail contract. Export a deterministic audit beside the public payload, validate cross-record consistency, and render the same Mob/Boss sections for both namespaces.

**Tech Stack:** Python 3 extraction and `unittest`, SQLite provenance, JSON contracts, TypeScript, React 19, Next.js, Vitest, Testing Library, ESLint.

## Global Constraints

- Lua/runtime facts are authoritative for numeric gameplay and rewards; Wiki data enriches descriptions, appearance, and images.
- Group variants only through explicit reviewed group facts, never display-name similarity.
- `base_game:alterguardian_phase3` is the canonical Celestial Champion record.
- `base_game:alterguardian_phase3dead` is hidden from standalone search and removed from Công trình.
- Unknown values remain unknown and must not render as verified `Không`.
- Reward methods are exactly `kill`, `mine_post_defeat`, `harvest`, or `conditional`.
- Raw extraction and provenance remain available.
- Generated output and audit ordering must be deterministic.

---

### Task 1: Explicit Mob/Boss groups and canonical membership

**Files:**
- Create: `data/manual/mob-variant-groups.json`
- Create: `tools/extract/mob_groups.py`
- Create: `tests/extract/test_mob_groups.py`

**Interfaces:**
- Consumes: catalog item dictionaries with `id`, `prefabId`, `category`, and optional `mob`.
- Produces: `load_mob_groups(path: Path) -> list[dict[str, Any]]` and `apply_mob_groups(items, groups) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]` where the second value is one audit row per member.

- [ ] **Step 1: Write failing group tests**

```python
class MobGroupTests(unittest.TestCase):
    def test_merges_members_into_existing_canonical_record(self):
        items = [
            item("base_game:alterguardian_phase1", "boss"),
            item("base_game:alterguardian_phase2", "boss"),
            item("base_game:alterguardian_phase3", "boss"),
            item("base_game:alterguardian_phase3dead", "structure"),
        ]
        groups = [{
            "canonicalId": "base_game:alterguardian_phase3",
            "members": [
                {"id": "base_game:alterguardian_phase1", "role": "phase", "order": 1},
                {"id": "base_game:alterguardian_phase2", "role": "phase", "order": 2},
                {"id": "base_game:alterguardian_phase3", "role": "phase", "order": 3},
                {"id": "base_game:alterguardian_phase3dead", "role": "post_defeat", "order": 4},
            ],
        }]

        public, audit = apply_mob_groups(items, groups)

        self.assertEqual([value["id"] for value in public], ["base_game:alterguardian_phase3"])
        self.assertEqual(
            [value["id"] for value in public[0]["mob"]["variants"]],
            [
                "base_game:alterguardian_phase1",
                "base_game:alterguardian_phase2",
                "base_game:alterguardian_phase3",
                "base_game:alterguardian_phase3dead",
            ],
        )
        self.assertEqual({row["action"] for row in audit}, {"keep", "merge"})

    def test_rejects_member_in_multiple_groups(self):
        with self.assertRaisesRegex(ValueError, "multiple mob groups"):
            apply_mob_groups([item("base_game:shared", "mob")], duplicate_groups())
```

- [ ] **Step 2: Run tests and verify the module is missing**

Run: `python3 -m unittest tests.extract.test_mob_groups -v`

Expected: FAIL with `ModuleNotFoundError: tools.extract.mob_groups`.

- [ ] **Step 3: Add the reviewed Celestial Champion manifest**

```json
{
  "schema_version": 1,
  "groups": [
    {
      "canonicalId": "base_game:alterguardian_phase3",
      "category": "boss",
      "members": [
        {"id": "base_game:alterguardian_phase1", "role": "phase", "order": 1},
        {"id": "base_game:alterguardian_phase2", "role": "phase", "order": 2},
        {"id": "base_game:alterguardian_phase3", "role": "phase", "order": 3},
        {"id": "base_game:alterguardian_phase3dead", "role": "post_defeat", "order": 4}
      ]
    }
  ]
}
```

- [ ] **Step 4: Implement strict loading and deterministic grouping**

```python
def load_mob_groups(path: Path) -> list[JsonObject]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or not isinstance(payload.get("groups"), list):
        raise ValueError("mob groups must use schema version 1")
    return sorted(payload["groups"], key=lambda value: value["canonicalId"])


def apply_mob_groups(
    items: list[JsonObject], groups: Sequence[JsonObject]
) -> tuple[list[JsonObject], list[JsonObject]]:
    by_id = {str(value["id"]): value for value in items}
    membership: dict[str, str] = {}
    hidden: set[str] = set()
    audit: list[JsonObject] = []
    for group in groups:
        canonical_id = required_id(group, "canonicalId")
        canonical = by_id[canonical_id]
        members = sorted(group["members"], key=lambda value: (value["order"], value["id"]))
        variants = []
        for member in members:
            member_id = required_id(member, "id")
            if member_id in membership:
                raise ValueError(f"{member_id} belongs to multiple mob groups")
            membership[member_id] = canonical_id
            source = by_id[member_id]
            variants.append(variant_reference(source, member))
            action = "keep" if member_id == canonical_id else "merge"
            if action == "merge":
                hidden.add(member_id)
            audit.append(group_audit_row(source, canonical_id, member, action))
        canonical["category"] = group["category"]
        canonical.setdefault("mob", empty_mob_details())["variants"] = variants
    public = [value for value in items if value["id"] not in hidden]
    return sorted(public, key=lambda value: value["id"]), sorted(audit, key=lambda value: value["id"])
```

- [ ] **Step 5: Run tests and commit**

Run: `python3 -m unittest tests.extract.test_mob_groups -v`

Expected: PASS.

```bash
git add data/manual/mob-variant-groups.json tools/extract/mob_groups.py tests/extract/test_mob_groups.py
git commit -m "feat: group mob and boss variants"
```

### Task 2: Per-prefab category classification and complete static rewards

**Files:**
- Modify: `tools/extract/base_game.py`
- Modify: `tests/extract/test_base_game.py`

**Interfaces:**
- Consumes: Lua module source and prefab constructor symbols from the existing `PrefabIndex`.
- Produces: per-prefab entity categories plus acquisition facts for fixed, chance, random, shared-table, and callback-spawned rewards.

- [ ] **Step 1: Add failing multi-prefab classification tests**

```python
def test_classifies_each_prefab_constructor_without_module_cross_contamination(self):
    source = '''
    local function bossfn()
      local inst = CreateEntity()
      inst:AddTag("epic")
      inst:AddComponent("health")
      inst:AddComponent("combat")
      inst:AddComponent("locomotor")
      return inst
    end
    local function deadfn()
      local inst = CreateEntity()
      inst:AddComponent("workable")
      return inst
    end
    return Prefab("guardian", bossfn), Prefab("guardian_dead", deadfn)
    '''
    self.assertEqual(classify_prefabs_in_module(source), {
        "guardian": "boss",
        "guardian_dead": "structure",
    })
```

- [ ] **Step 2: Add failing shared/direct reward tests**

```python
def test_extracts_shared_loot_and_post_defeat_work_rewards(self):
    source = '''
    SetSharedLootTable("guardian_dead", {
      {"hat", 1.00}, {"glass", .66}, {"glass", .66}
    })
    local function onwork(inst, worker, workleft)
      if workleft <= 0 then
        inst.components.lootdropper:DropLoot()
        SpawnPrefab("altar_piece")
      end
    end
    local function deadfn()
      inst:AddComponent("workable")
      inst.components.workable:SetWorkAction(ACTIONS.MINE)
      inst:AddComponent("lootdropper")
      inst.components.lootdropper:SetChanceLootTable("guardian_dead")
      inst.components.workable:SetOnWorkCallback(onwork)
    end
    return Prefab("guardian_dead", deadfn)
    '''
    rewards = extract_prefab_rewards("guardian_dead", source)
    self.assertIn(reward("hat", 1, "mine_post_defeat", "guardian_dead"), rewards)
    self.assertIn(reward("glass", .66, "mine_post_defeat", "guardian_dead", count=2), rewards)
    self.assertIn(reward("altar_piece", 1, "mine_post_defeat", "guardian_dead"), rewards)
```

- [ ] **Step 3: Run the focused tests and verify failure**

Run: `python3 -m unittest tests.extract.test_base_game.BaseGameTests.test_classifies_each_prefab_constructor_without_module_cross_contamination tests.extract.test_base_game.BaseGameTests.test_extracts_shared_loot_and_post_defeat_work_rewards -v`

Expected: FAIL because `classify_prefabs_in_module` and `extract_prefab_rewards` do not exist.

- [ ] **Step 4: Implement constructor-scoped classification**

```python
def classify_prefabs_in_module(source: str) -> dict[str, str]:
    functions = _named_function_bodies(source)
    result: dict[str, str] = {}
    for call in _iter_calls(source, ("Prefab",)):
        if len(call.arguments) < 2:
            continue
        prefab_id = _literal_string(call.arguments[0])
        constructor = call.arguments[1].strip()
        if prefab_id is None or constructor not in functions:
            continue
        result[prefab_id.lower()] = classify_prefab_module(
            prefab_id.lower(), functions[constructor]
        )
    return result
```

- [ ] **Step 5: Implement shared loot and callback reward resolution**

```python
def extract_prefab_rewards(prefab_id: str, source: str) -> list[dict[str, Any]]:
    shared = _parse_shared_loot_tables(source)
    constructor = _prefab_constructor_source(prefab_id, source)
    method = "mine_post_defeat" if _uses_mine_workable(constructor) else "kill"
    rewards = _parse_lootdropper_calls(constructor, shared, method, prefab_id)
    callbacks = _reachable_reward_callbacks(constructor, source)
    rewards.extend(_parse_spawned_rewards(callbacks, method, prefab_id))
    return _aggregate_rewards(rewards)
```

When materializing acquisition facts, persist `method`, `source_prefab_id`,
`loot_table`, callback name, source expression, and locator inside conditions or
fact evidence; do not discard unresolved expressions.

- [ ] **Step 6: Run the complete base extraction suite and commit**

Run: `python3 -m unittest tests.extract.test_base_game -v`

Expected: PASS.

```bash
git add tools/extract/base_game.py tests/extract/test_base_game.py
git commit -m "feat: extract prefab-scoped mob rewards"
```

### Task 3: Normalize complete Mob/Boss detail sections and audit

**Files:**
- Create: `tools/extract/mob_wiki.py`
- Create: `tools/extract/mob_details.py`
- Create: `tests/extract/test_mob_wiki.py`
- Create: `tests/extract/test_mob_details.py`
- Modify: `tools/extract/export_items.py`
- Modify: `tests/extract/test_export_items.py`

**Interfaces:**
- Consumes: canonical catalog entities, runtime coverage, the local full-Wiki `pages.jsonl`, public item references, and Mob groups.
- Produces: `load_mob_wiki_details(path, items) -> dict[str, dict[str, Any]]`, `build_mob_details(...) -> dict[str, dict[str, Any]]`, and `build_mob_boss_audit(...) -> dict[str, Any]`.

- [ ] **Step 1: Write failing Wiki matching tests**

```python
def test_matches_mob_page_by_spawn_code_before_display_name(self):
    details = load_mob_wiki_details(
        pages_path,
        [{"id": "base_game:alterguardian_phase3", "prefabId": "alterguardian_phase3", "englishName": "Celestial Champion"}],
    )
    self.assertEqual(details["base_game:alterguardian_phase3"]["canonicalUrl"], "https://dontstarve.wiki.gg/wiki/Celestial_Champion")
    self.assertIn("Boss Monster", details["base_game:alterguardian_phase3"]["summary"])
```

- [ ] **Step 2: Write failing detail normalization tests**

```python
def test_builds_phase_aware_stats_appearance_mechanics_and_rewards(self):
    details = build_mob_details(
        items=celestial_items(),
        entities=celestial_entities_with_shared_rewards(),
        wiki_details={},
        runtime_coverage=[],
        groups=celestial_groups(),
    )["base_game:alterguardian_phase3"]

    self.assertEqual(details["appearance"]["status"], "known")
    self.assertEqual(details["appearance"]["sources"], ["Sau khi hoàn thành Celestial Champion phase 2"])
    self.assertEqual([value["role"] for value in details["variants"]], [
        "phase", "phase", "phase", "post_defeat"
    ])
    post_defeat = [value for value in details["loot"] if value["method"] == "mine_post_defeat"]
    self.assertTrue(post_defeat)
    self.assertTrue(all(value["sourceVariant"] == "base_game:alterguardian_phase3dead" for value in post_defeat))


def test_does_not_claim_none_when_drop_extraction_is_unobserved(self):
    details = build_single_mob(runtime_status="unobserved", acquisitions=[])
    self.assertEqual(details["lootStatus"], "unknown")
```

- [ ] **Step 3: Run tests and verify failure**

Run: `python3 -m unittest tests.extract.test_mob_wiki tests.extract.test_mob_details -v`

Expected: FAIL with missing `tools.extract.mob_wiki` and `tools.extract.mob_details` modules.

- [ ] **Step 4: Implement deterministic local Wiki matching**

```python
def load_mob_wiki_details(
    pages_path: Path, items: Sequence[JsonObject]
) -> dict[str, JsonObject]:
    wanted_titles = {
        _identity(str(item.get("englishName") or item["name"])): str(item["id"])
        for item in items
    }
    wanted_prefabs = {str(item["prefabId"]): str(item["id"]) for item in items}
    title_matches: dict[str, JsonObject] = {}
    spawn_matches: dict[str, JsonObject] = {}
    with pages_path.open(encoding="utf-8") as handle:
        for line in handle:
            page = json.loads(line)
            if page.get("namespace") != 0:
                continue
            title_id = wanted_titles.get(_identity(str(page.get("title") or "")))
            if title_id is not None:
                title_matches[title_id] = page
            wikitext = str(page.get("wikitext") or "")
            for prefab_id in extract_spawn_codes(wikitext):
                item_id = wanted_prefabs.get(prefab_id)
                if item_id is not None:
                    spawn_matches[item_id] = page
    output: dict[str, JsonObject] = {}
    for item in items:
        item_id = str(item["id"])
        page = spawn_matches.get(item_id) or title_matches.get(item_id)
        if page is not None:
            output[item_id] = normalize_mob_page(page)
    return dict(sorted(output.items()))
```

`normalize_mob_page` must retain canonical URL, page ID, title, first summary
paragraph, categories, spawn sources, mechanics text, image candidates, and
evidence locators. Matching ambiguity returns no match plus an audit reason;
it never selects the first fuzzy result.

- [ ] **Step 5: Implement typed section builders**

```python
def build_mob_details(
    items: Sequence[JsonObject],
    entities: Sequence[JsonObject],
    wiki_details: Mapping[str, JsonObject],
    runtime_coverage: Sequence[JsonObject],
    groups: Sequence[JsonObject],
) -> dict[str, JsonObject]:
    item_by_id = {str(value["id"]): value for value in items}
    entity_by_id = {str(value["key"]): value for value in entities}
    membership = build_group_membership(groups)
    output: dict[str, JsonObject] = {}
    for canonical_id, member_ids in canonical_members(items, membership):
        output[canonical_id] = {
            "appearance": build_appearance(canonical_id, member_ids, entity_by_id, wiki_details),
            "variants": build_variants(member_ids, item_by_id, groups),
            "stats": build_stats(member_ids, entity_by_id),
            "mechanics": build_mechanics(member_ids, entity_by_id, wiki_details),
            "lootStatus": loot_status(member_ids, entity_by_id, runtime_coverage),
            "loot": build_rewards(member_ids, entity_by_id, item_by_id),
        }
    return dict(sorted(output.items()))
```

- [ ] **Step 6: Replace the old Tu Tiên-only `_mob_details` export path**

Build Mob/Boss details after Wiki merge and before structure/effect audits. Apply
Mob groups before building structure details so merged post-defeat members are
absent from the structure audit. Attach `mob` to both `mob` and `boss`
categories, and preserve `mob: null` for all other categories.

- [ ] **Step 7: Generate deterministic Mob/Boss audit rows**

```python
def build_mob_boss_audit(
    candidates: Sequence[JsonObject],
    public_items: Sequence[JsonObject],
    groups: Sequence[JsonObject],
) -> JsonObject:
    rows = audit_rows(candidates, public_items, groups)
    return {
        "schema_version": 1,
        "summary": summarize_actions(rows),
        "rows": sorted(rows, key=lambda value: value["id"]),
    }
```

- [ ] **Step 8: Run focused export tests and commit**

Run: `python3 -m unittest tests.extract.test_mob_wiki tests.extract.test_mob_details tests.extract.test_export_items -v`

Expected: PASS.

```bash
git add tools/extract/mob_wiki.py tools/extract/mob_details.py tests/extract/test_mob_wiki.py tests/extract/test_mob_details.py tools/extract/export_items.py tests/extract/test_export_items.py
git commit -m "feat: normalize mob and boss details"
```

### Task 4: Validate Mob/Boss grouping, rewards, and audit consistency

**Files:**
- Modify: `tools/extract/cli.py`
- Modify: `tools/extract/validate.py`
- Modify: `tests/extract/test_export_validate.py`

**Interfaces:**
- Consumes: `public/data/items.json`, `data/generated/mob-boss-audit.json`, and `data/manual/mob-variant-groups.json`.
- Produces: hard-failure validation codes for contradictory group/detail/audit state.

- [ ] **Step 1: Write failing validator tests**

```python
def test_validation_rejects_hidden_member_still_published(self):
    errors = mob_boss_errors(items_with_dead_structure(), celestial_audit(), celestial_groups())
    self.assertIn({
        "code": "merged_mob_member_is_public",
        "id": "base_game:alterguardian_phase3dead",
    }, errors)


def test_validation_rejects_known_empty_loot_and_missing_reward_reference(self):
    errors = mob_boss_errors(items_with_invalid_mob_details(), audit(), groups())
    self.assertTrue(any(value["code"] == "known_mob_loot_is_empty" for value in errors))
    self.assertTrue(any(value["code"] == "missing_mob_reward_reference" for value in errors))
```

- [ ] **Step 2: Run tests and verify failure**

Run: `python3 -m unittest tests.extract.test_export_validate -v`

Expected: FAIL because Mob/Boss audit validation is absent.

- [ ] **Step 3: Implement strict validation and CLI paths**

Add default paths:

```python
MOB_BOSS_AUDIT = Path("data/generated/mob-boss-audit.json")
MOB_GROUPS = Path("data/manual/mob-variant-groups.json")
```

Validate group uniqueness, hidden-member absence, canonical category, detail
shape/status, reward method/quantity/chance/source/reference, audit coverage,
and audit/public action consistency. Wire both paths through `export` and
`validate` CLI subcommands.

- [ ] **Step 4: Run validation tests and commit**

Run: `python3 -m unittest tests.extract.test_export_validate -v`

Expected: PASS.

```bash
git add tools/extract/cli.py tools/extract/validate.py tests/extract/test_export_validate.py
git commit -m "test: validate mob and boss normalization"
```

### Task 5: Shared DST and Tu Tiên Mob/Boss modal

**Files:**
- Create: `app/components/mob-sections.tsx`
- Create: `app/components/mob-sections.test.tsx`
- Modify: `app/lib/item-catalog.ts`
- Modify: `app/lib/item-catalog.test.ts`
- Modify: `app/components/item-detail-modal.tsx`
- Modify: `app/components/tu-tien-item-sections.tsx`
- Modify: `app/components/tu-tien-item-sections.test.tsx`

**Interfaces:**
- Consumes: versioned Mob/Boss detail JSON with appearance, variants, stats, mechanics, loot status, and rewards.
- Produces: `MobSections` shared by base DST and Tu Tiên Mob/Boss records.

- [ ] **Step 1: Write failing parser tests for the expanded contract**

```typescript
expect(parsed.mob?.variants[3]).toMatchObject({
  id: "base_game:alterguardian_phase3dead",
  role: "post_defeat",
});
expect(parsed.mob?.loot[0]).toMatchObject({
  method: "mine_post_defeat",
  sourceVariant: "base_game:alterguardian_phase3dead",
  minimum: 1,
  maximum: 1,
});
```

- [ ] **Step 2: Write failing shared renderer tests**

```tsx
it("renders base-game boss phases and post-defeat mining rewards", () => {
  render(<MobSections item={celestialChampion} itemsById={itemsById} onSelectItem={vi.fn()} titleId="boss" />);
  expect(screen.getByText("Giai đoạn hậu chiến")).toBeInTheDocument();
  expect(screen.getByText("Khai thác xác bằng cuốc")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Enlightened Crown" })).toBeInTheDocument();
});
```

- [ ] **Step 3: Run Vitest and verify failures**

Run: `npm test -- app/lib/item-catalog.test.ts app/components/mob-sections.test.tsx`

Expected: FAIL because the expanded parser and `MobSections` do not exist.

- [ ] **Step 4: Expand strict TypeScript types and parsing**

```typescript
export type MobRewardMethod = "kill" | "mine_post_defeat" | "harvest" | "conditional";

export type MobVariant = {
  id: string;
  prefabId: string;
  name: string;
  role: "phase" | "variant" | "summon" | "post_defeat";
  order: number;
  sprite: SpriteDescriptor | null;
};

export type MobLoot = {
  item: ItemReference;
  minimum: number;
  maximum: number;
  chance: string | null;
  method: MobRewardMethod;
  sourceVariant: string;
  lootTable: string | null;
  conditions: string | null;
  evidence: readonly ItemEvidence[];
};
```

Add strict parsers for appearance, variants, mechanics, and the reward fields.
`parseMobRewardMethod` accepts only the four global-constraint values. Reject a
known empty loot section and reject `minimum > maximum`.

- [ ] **Step 5: Move the renderer and route both categories through it**

In `ItemDetailModal`, render `MobSections` whenever category is `mob` or `boss`
before namespace-specific item sections. Remove the old Mob renderer from
`tu-tien-item-sections.tsx` so the same markup and status handling applies to
both namespaces.

- [ ] **Step 6: Run frontend checks and commit**

Run: `npm test -- app/lib/item-catalog.test.ts app/components/mob-sections.test.tsx app/components/tu-tien-item-sections.test.tsx`

Expected: PASS.

Run: `npx tsc --noEmit`

Expected: exit 0.

```bash
git add app/components/mob-sections.tsx app/components/mob-sections.test.tsx app/lib/item-catalog.ts app/lib/item-catalog.test.ts app/components/item-detail-modal.tsx app/components/tu-tien-item-sections.tsx app/components/tu-tien-item-sections.test.tsx
git commit -m "feat: render shared mob and boss details"
```

### Task 6: Regenerate, audit, and verify the complete catalog

**Files:**
- Modify: `public/data/items.json`
- Modify: `public/data/textures.json`
- Create: `data/generated/mob-boss-audit.json`
- Modify: `data/generated/coverage.json`
- Modify only if produced by the normal pipeline: `data/raw/base_game.json`, `public/data/catalog.json`

**Interfaces:**
- Consumes: all extraction sources and implementation from Tasks 1–5.
- Produces: final deterministic public and audit artifacts.

- [ ] **Step 1: Run the extraction/export pipeline**

Run:

```bash
python3 -m tools.extract.cli enrich-base
python3 -m tools.extract.cli build-db
python3 -m tools.extract.cli export
shasum -a 256 public/data/items.json data/generated/mob-boss-audit.json
python3 -m tools.extract.cli export
shasum -a 256 public/data/items.json data/generated/mob-boss-audit.json
```

Expected: both runs exit 0 and write byte-identical `items.json` and `mob-boss-audit.json` hashes.

- [ ] **Step 2: Verify Celestial Champion and coverage invariants**

Run:

```bash
jq '[.items[] | select(.id=="base_game:alterguardian_phase3dead")] | length' public/data/items.json
jq '.items[] | select(.id=="base_game:alterguardian_phase3") | {category,mob}' public/data/items.json
```

Expected: first command prints `0`; second prints category `boss`, four ordered
variants, and at least one `mine_post_defeat` reward sourced from
`base_game:alterguardian_phase3dead`.

- [ ] **Step 3: Run hard validation**

Run: `python3 -m tools.extract.cli validate`

Expected: `hard_failures=0`. Optional coverage warnings may remain only when
they identify truly unavailable enrichment and must not contradict known
source facts.

- [ ] **Step 4: Run all regression suites**

Run: `python3 -m unittest discover -s tests/extract -v`

Expected: PASS.

Run: `npm test`

Expected: PASS.

Run: `npx tsc --noEmit`

Expected: exit 0.

Run: `npm run lint`

Expected: exit 0.

- [ ] **Step 5: Commit generated artifacts**

```bash
git add public/data/items.json public/data/textures.json data/generated/mob-boss-audit.json data/generated/coverage.json data/raw/base_game.json public/data/catalog.json
git commit -m "data: publish normalized mob and boss catalog"
```

- [ ] **Step 6: Review final diff and report exact results**

Report Mob/Boss totals by namespace, known/unknown appearance and loot counts,
merged/excluded audit counts, missing-image counts, Celestial Champion reward
count, validation warnings, and all verification commands. Do not push or merge
without an explicit user request.
