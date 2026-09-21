# Phàm Nhân — Unified Level Progression Design

**Date:** 2026-09-21

**Status:** Proposed for user review

**Target:** `mods/PhamNhanTuTien` (Phàm Nhân Tu Tiên 2.0)

**Primary milestone:** A fresh solo save reaches level 100 in roughly 60–80 hours of balanced play.

## 1. Context and objective

Phàm Nhân currently owns its character progression through `hh_leveling`, while the historical Achievement mod supplied a broader set of gameplay-driven EXP sources. The two level tracks must become one coherent Phàm Nhân progression:

- `hh_leveling` remains the only level, EXP, and ability-point authority.
- Normal survival, production, combat, quests, bosses, and dungeons feed that one EXP bar.
- Achievement completion itself awards Star only and never awards EXP.
- Progression is tuned for solo play: meaningful but not grind-heavy early, increasingly demanding later, and resistant to exploits without punishing legitimate repetition.

The target experience is:

- balanced play: 60–80 hours to level 100, with 72 hours as the tuning baseline;
- optimized grinding: about 40–50 hours;
- mostly survival/production: about 95–120 hours;
- casual or inefficient play: about 100–130 hours.

Level 100 is a balance milestone, not a hard level cap.

## 2. Scope

This design covers:

1. the Phàm Nhân level curve;
2. gameplay actions that award EXP;
3. combat and boss EXP;
4. daily quest EXP;
5. EXP modifiers and their cap;
6. solo kill ownership and removal of party sharing;
7. anti-exploit rules;
8. dungeon rank gates matching the gate's displayed rank;
9. verification of the resulting progression.

## 3. Explicit non-goals and integration boundary

The implementation must not:

- modify `mods/AchievementLevel`;
- redesign Achievement content, Star rewards, or character-specific Achievement behavior;
- add character-specific EXP bonuses;
- migrate Achievement level data or merge old save data;
- redesign the existing AP/stat system;
- add an EXP daily cap or diminishing returns for legitimate repeated play;
- re-integrate Solo Leveling as an external dependency—the integrated Phàm Nhân implementation is the target.

The separate Achievement task owns its own refactor. Its integration contract with this work is:

- Achievement completion grants Star, not EXP;
- it must not attach or maintain a second player level component;
- it may consume the canonical Phàm Nhân level as read-only context if needed.

This design is accepted against a fresh save starting at level 1, EXP 0, and AP 0. No cross-system save migration is required. The existing `hh_leveling` save format should remain readable where practical, but old-save conversion is not an acceptance requirement.

## 4. Canonical level curve

For current level `L`, define `n = L - 1`. EXP required to advance from `L` to `L + 1` is:

```text
EXP(L -> L+1) = round(100 + 10n + 1.5n²)
```

Lua must use deterministic positive-number rounding:

```lua
math.floor(100 + 10 * n + 1.5 * n * n + 0.5)
```

The exact cumulative EXP from level 1 to level 100 is **536,258**.

### 4.1 Milestones

| Reached level | New cumulative EXP | Old Phàm Nhân | Achievement track |
|---:|---:|---:|---:|
| 10 | 1,568 | 2,820 | 475 |
| 20 | 6,778 | 16,720 | 1,189 |
| 30 | 18,538 | 51,620 | 2,293 |
| 40 | 39,848 | 117,520 | 3,987 |
| 50 | 73,708 | 224,420 | 6,471 |
| 60 | 123,118 | 382,320 | 9,945 |
| 70 | 191,078 | 601,220 | 14,609 |
| 80 | 280,588 | 891,120 | 20,663 |
| 90 | 394,648 | 1,262,020 | 28,307 |
| 100 | 536,258 | 1,723,920 | 37,741 |

The new level-100 total is approximately:

- **3.21× lighter** than the old Phàm Nhân curve;
- **14.21× heavier** than the historical Achievement level track.

The Achievement comparison uses its effective threshold behavior (`50 + floor(0.1L²)` and a strict `>` check), hence the aggregate total of about 37,741.

### 4.2 Representative per-level requirements

| Current level | EXP to next level |
|---:|---:|
| 1 | 100 |
| 10 | 312 |
| 20 | 832 |
| 30 | 1,652 |
| 40 | 2,772 |
| 50 | 4,192 |
| 60 | 5,912 |
| 70 | 7,932 |
| 80 | 10,252 |
| 90 | 12,872 |
| 99 | 15,486 |
| 100 | 15,792 |

## 5. Intended pacing by rank bracket

| Level interval | Rank band | Interval EXP | Target hours | Cumulative hours |
|---|---|---:|---:|---:|
| 1 → 10 | E | 1,568 | 2 | 2 |
| 10 → 20 | D | 5,210 | 4 | 6 |
| 20 → 30 | C | 11,760 | 6 | 12 |
| 30 → 40 | B | 21,310 | 7 | 19 |
| 40 → 50 | A | 33,860 | 8 | 27 |
| 50 → 60 | S | 49,410 | 7 | 34 |
| 60 → 70 | S | 67,960 | 8 | 42 |
| 70 → 80 | S | 89,510 | 9 | 51 |
| 80 → 90 | S | 114,060 | 10 | 61 |
| 90 → 100 | S | 141,610 | 11 | 72 |

The expected lifetime EXP mix for balanced play is:

- survival and production: 30–35%;
- ordinary and elite combat: 20–25%;
- daily quests: 20–25%;
- bosses and dungeons: 20–30%;
- Achievement completion: 0%.

These are tuning bands, not per-session quotas.

## 6. Central EXP award path

All new EXP sources should flow through one Phàm Nhân award service or API rather than calling `hh_leveling:AddExp` independently. The service accepts:

- recipient player;
- source category;
- positive base amount;
- context needed for attribution, anti-exploit checks, and modifiers.

Recommended source categories are:

- `activity`;
- `combat`;
- `boss`;
- `dungeon`;
- `daily_quest`;
- `first_learn`.

The central path must:

1. reject invalid, zero, negative, or ineligible awards;
2. resolve the one eligible solo recipient;
3. apply only modifiers valid for the source category;
4. cap the combined effective multiplier at 1.75;
5. round once, after all modifiers, with `math.floor(value + 0.5)`;
6. award at least 1 EXP when a positive eligible base award survives all reductions;
7. call the canonical `hh_leveling:AddExp` exactly once.

Daily quest rewards are already scaled from the current level requirement and therefore bypass combat/activity multipliers. Achievement completion never enters this path.

## 7. Survival and production EXP

EXP is awarded only after a successful action has completed.

| Activity | Base EXP | Eligibility note |
|---|---:|---|
| Harvest or pick | 1 | Successful world harvest only |
| Finish chopping, mining, or hammering | 4 | On completion, not per work hit |
| Plant regular seed | 2 | Successful planting only |
| Plant special seed or tree | 3 | Successful planting only |
| Tend a plant | 1 | Valid tend interaction only |
| Cook | 4 | Finished product collected/created |
| Craft item | 2 | Successful non-free recipe craft |
| Build structure | 6 | Successful placement/build completion |
| Repair | 5 | Durability actually restored |
| Pond fish | 8 | Fish successfully obtained |
| Ocean fish | 20 | Fish successfully landed |
| Catch creature | 5 | Successful capture |
| Learn recipe first time | 10 | Only if the recipe was previously unknown |
| Eat food | 1–5 | `clamp(round(positive_hunger / 20), 1, 5)` |

Eating EXP uses only the food's positive hunger value. Food with zero or negative hunger grants no eating EXP. Health and sanity values do not increase this award.

Events must be hooked at authoritative completion points so animation retries, prediction, or failed actions cannot duplicate EXP.

## 8. Combat EXP

### 8.1 Ordinary enemy tiers

| Enemy tier | Base EXP |
|---|---:|
| Tiny | 5 |
| Common | 10 |
| Medium | 25 |
| Strong | 40 |
| Elite | 60 |
| Miniboss | 100–200 |

Prefab-specific values may be represented as data overrides, but should conform to these bands unless explicitly justified.

Ordinary mobs retain the existing overlevel reduction so trivial enemies become less efficient as the player outlevels them. Bosses do not receive an overlevel reduction.

### 8.2 Overworld bosses

| Boss stage | Base EXP band |
|---|---:|
| Early | 500–750 |
| Midgame | 1,000–1,500 |
| Endgame | 2,000–2,500 |
| Treasure or exceptional special boss | 3,500 |

### 8.3 Dungeon enemies and bosses

| Dungeon target | Base EXP |
|---|---:|
| Ordinary dungeon mob | 15–30 |
| Strong dungeon mob | 40–60 |
| Vanilla dungeon boss | 750–1,500 |
| Igris | 3,000 |
| Sharkboi | 4,500 |
| Beru | 6,000 |

The dungeon modifier described below applies after these base values.

## 9. Solo kill attribution and removal of sharing

There is exactly one recipient for a kill:

- if the player kills the target, that player receives 100% of the eligible EXP;
- if a player-owned shadow or other supported owned combat follower kills the target, its owner receives 100%;
- otherwise, no player EXP is awarded.

The implementation must remove nearby-player scans, party/dungeon-recipient lists, and division by recipient count from the EXP award path. A nearby player who did not own the credited killer receives nothing.

Targets or killers marked `noxp`, invalid ownership chains, and player-owned allies/summons used as victims are ineligible. Ownership resolution must stop safely on invalid or cyclic references.

## 10. EXP modifiers

Applicable modifiers multiply the base award, then the combined result is capped at **1.75×**.

| Modifier | Value | Applies to |
|---|---:|---|
| Rank S combat bonus | 1.25× | Combat kill EXP only |
| Existing player EXP buff | 1.25× | Eligible activity/combat awards according to its current semantics |
| Existing dungeon EXP buff | 1.35× | Eligible dungeon awards |

The existing Rank S kill multiplier of 2.0 must become 1.25.

The application order is:

1. base amount;
2. ordinary-mob overlevel reduction, if applicable;
3. Rank S combat bonus, if applicable;
4. player EXP buff, if applicable;
5. dungeon EXP buff, if applicable;
6. clamp the total effective multiplier relative to base to 1.75;
7. round once and award.

Quest scaling is not a multiplier and daily quest rewards bypass this stack. No character-specific modifier is introduced.

## 11. Daily quest EXP

Let `goal` be the current value returned by the canonical level curve for the player's next level. On successful quest completion:

```text
Easy   = max(20, round(goal × 0.06))
Medium = max(35, round(goal × 0.10))
Hard   = max(50, round(goal × 0.15))
```

Daily quest definitions should specify difficulty, not a permanently fixed EXP reward. Completion computes the reward from the player's current `goal` at completion time. The computed amount is awarded once, with no other EXP multiplier.

If a quest definition must retain a legacy reward field for compatibility, it must not override the formula in the fresh-save target path.

## 12. Dungeon rank gates

Dungeon entry requirements must match the rank shown by the gate:

| Wave count | Required rank |
|---:|---|
| 2 | E |
| 3 | D |
| 4 | C |
| 5 | B |
| 6 | A |
| 7–10 | S |

The existing rank progression remains:

- D at level 10;
- C at level 20;
- B at level 30;
- A at level 40;
- S at level 50.

Entry validation must use the same shared mapping as display logic, or a single authoritative helper consumed by both, so the UI and server gate cannot drift. Rejected entry must clearly report the required rank. Existing non-rank requirements and cooldowns remain in force.

## 13. Anti-exploit rules

“Anti-farm” in this design means preventing duplicate or fake rewards, not slowing legitimate play.

The system must not add:

- a daily EXP cap;
- time-based diminishing returns;
- reduced rewards merely because a valid activity is repeated.

The following grant no EXP:

- failed or cancelled actions;
- work hits before the chop/mine/hammer job is complete;
- free or zero-cost recipes;
- learning a recipe already known;
- repeatedly dropping and picking up the same item;
- repeated handling of one death event;
- killing player-owned allies, shadows, or summons;
- entities explicitly marked `noxp`;
- client-side predicted actions that were not authoritatively completed.

Each authoritative completion/death event must be idempotent from the EXP system's perspective.

## 14. Data and control flow

```text
authoritative gameplay event
        |
        v
source adapter (activity / kill / quest / dungeon)
        |
        v
central Phàm Nhân EXP award service
  - validates event and recipient
  - resolves solo ownership
  - looks up base reward
  - applies allowed modifiers and 1.75x cap
  - rounds once
        |
        v
hh_leveling:AddExp(amount)
        |
        v
level-up loop + existing AP/stat behavior
```

Configuration values should live in the existing Phàm Nhân tuning/config layer rather than being duplicated across event hooks. Event adapters should be small and should not own curve mathematics.

## 15. Expected implementation surface

The implementation plan should inspect and, where required, update only Phàm Nhân-owned files such as:

- `mods/PhamNhanTuTien/scripts/components/hh_leveling.lua`;
- `mods/PhamNhanTuTien/main/hh_tunning.lua`;
- `mods/PhamNhanTuTien/main/hh_api.lua`;
- `mods/PhamNhanTuTien/scripts/components/hh_daily_quest.lua`;
- `mods/PhamNhanTuTien/scripts/quests/hh_daily_quest_defs.lua`;
- Phàm Nhân event-hook files for harvesting, work, planting, tending, cooking, crafting, building, repairing, fishing, catching, eating, and recipe learning;
- `mods/PhamNhanTuTien/scripts/components/dungeon_manager.lua`;
- `mods/PhamNhanTuTien/scripts/prefabs/dungeon_gate.lua`;
- Phàm Nhân tests and progression simulation tools.

This list is a discovery boundary, not permission to rewrite every file. The implementation plan must name the exact symbols and smallest necessary edits after CodeGraph inspection.

## 16. Verification and acceptance criteria

### 16.1 Curve tests

- Formula tests cover representative levels and deterministic rounding.
- Cumulative EXP from level 1 to 100 equals exactly 536,258.
- Milestone totals match the table in section 4.1.
- Multi-level awards preserve remainder EXP and existing AP grants.

### 16.2 Source tests

- Every activity in section 7 awards the specified base amount exactly once on success.
- Failed, cancelled, predicted-only, or duplicate events award zero.
- Eating handles negative, zero, small, and large hunger values correctly.
- Recipe learning distinguishes first-time learning from already-known recipes.

### 16.3 Combat tests

- Direct player kills award 100% to the killer.
- Owned-shadow kills award 100% to the owner.
- Nearby unrelated players receive zero.
- Player-owned allies/summons and `noxp` targets yield zero.
- Ordinary-mob overlevel reduction remains active; bosses bypass it.
- Igris, Sharkboi, and Beru use 3,000, 4,500, and 6,000 base EXP respectively.

### 16.4 Modifier tests

- Rank S contributes 1.25× to combat EXP, not 2.0×.
- Player and dungeon buffs retain their intended 1.25× and 1.35× values.
- Any valid combination is capped at 1.75× relative to base.
- Rounding occurs once after the final capped multiplier.
- Daily quests do not receive these multipliers.

### 16.5 Quest tests

- Easy, Medium, and Hard rewards use 6%, 10%, and 15% of the current next-level requirement with minimums 20, 35, and 50.
- Reward is evaluated at completion and granted exactly once.

### 16.6 Dungeon tests

- Wave counts 2–10 enforce E, D, C, B, A, then S exactly as displayed.
- Gate display and server validation read the same mapping.
- Rejection explains the required rank.
- Existing cooldown and other entry checks continue to work.

### 16.7 Progression simulation

A deterministic simulation must report:

- the old Phàm Nhân curve;
- the historical Achievement curve;
- the new unified curve;
- cumulative milestone totals;
- estimated time-to-100 for balanced, optimized, survival-heavy, and casual profiles;
- source-category contribution percentages.

The balanced profile passes when it lands within 60–80 hours and roughly matches the source-mix bands in section 5. Other profiles should remain within their stated target ranges without relying on daily caps or diminishing returns.

## 17. Completion definition

This design is complete when a fresh solo Phàm Nhân save has one authoritative level bar, earns EXP from the approved gameplay sources, cannot duplicate rewards through obvious event exploits, receives no EXP from Achievement completion, obeys rank-correct dungeon gates, and meets the level-100 pacing targets under the verified simulation profiles.
