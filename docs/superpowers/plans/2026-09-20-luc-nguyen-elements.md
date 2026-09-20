# Lục Nguyên: six craftable swords and elemental impacts

User approved execution after the in-chat design and two balance corrections. This extends the existing weapon, not the original character cultivation systems.

## Approved behavior

All six swords are independent held weapons available to every character. Preserve existing Tinh La behavior except its new passive and recipe. New swords use 100 base damage and range 2, with durability/repair behavior aligned with existing Tinh La unless asset or integration evidence requires a documented adjustment.

Held passives: Kim adds 10 planar per hit; Mộc summons a homing sword for 40% base damage every fourth hit; Thủy has 20% chance to slow movement 25% for 3 seconds; Hỏa has 15% chance of a radius-3 burst for 30% base damage; Thổ grants a nonstacking 30-damage shield for 5 seconds every fifth hit; Lôi has 20% chance to chain to up to two other enemies for 35% base damage each. Secondary damage does not trigger further procs or crits.

The gun retains its existing critical-triggered distinct 1–6 sword volley. Each sword independently rolls 10–20% enhanced weapon base damage. On impact: Kim adds 10 planar; Mộc heals 2 with a per-owner 3-second cooldown; Thủy has 20% chance to slow movement 25% for 2 seconds; Hỏa bursts within radius 2 for 50% of sword damage against other enemies only; Thổ grants a nonstacking 10-damage shield for 3 seconds with a per-owner 3-second cooldown; Lôi chains to one other enemy for 50% sword damage. No fire, recursive attacks, or offensive multiplier duplication. Slow refreshes without stacking; a weaker shield does not downgrade a stronger active shield.

Each sword costs one Trung Phẩm Linh Thạch plus: Kim 12 gold/6 flint; Mộc 6 living logs/12 twigs; Thủy 3 blue gems/6 gold; Hỏa 3 red gems/6 charcoal; Thổ 6 thulecite/12 rocks; Lôi 3 purple gems/6 nightmare fuel. All use SCIENCE_TWO. Gun consumes one of each sword and replaces its former recipe.

## Execution

- [x] Sol High: implement gameplay, namespaced sword assets, recipes, deterministic regression tests.
- [x] Parent: update exporter, item descriptions, README and attribution to match final behavior.
- [x] Parent/reviewer: inspect proc isolation, planar/defense routing, hostile filtering, modifier cleanup, shield consumption, recipes and assets.
- [x] Run feature/regression and registration checks, regenerate catalog, and run offline dedicated smoke where available.

## Constraints and verification

Use the current checkout because required mod files are untracked. Preserve unrelated live work, do not mass-add or commit, do not edit Workshop source or deploy. Parent and implementer own separate files. Keep client visual verification explicitly separate from headless evidence.

## Progress

Implementation dispatched to GPT-5.6 Sol High. Parent is preparing documentation/catalog changes and integration verification.

Completed: feature/regression tests, registration audit, catalog checks, independent final review and full-mod offline dedicated smoke all passed. See `../reports/2026-09-20-luc-nguyen-elements.md`. Graphical client QA remains unverified.

Ruling: the five new held swords start at 1,000 uses and break on depletion using standard DST finiteuses behavior; Tinh La keeps its existing 300/1,000 start, persistence and donor repair. This avoids altering the independently maintained existing weapon and keeps new swords simple. The unspecified new-sword lifetime is documented for later balance changes.

Ruling: the final user correction to Hàn khí applies to ranged sword impacts (2 seconds), while held Tinh La retains the separately approved 3-second passive. Both descriptions explicitly distinguish these values.

Ruling: secondary Hỏa/Lôi effects exclude players, including PvP players. The requested feature targets monsters; adding PvP splash was not requested. Primary attacks keep the game's existing rules.

Review identified two corrections before completion: scope shield absorption to the actual combat health delta (not synchronous follow-up health costs), and persist Mộc/Thổ hit cadence across world saves.
