# Solo Combat HUD — approved delivery plan

User approved the in-chat integration plan and explicitly selected GPT-5.6 Sol to implement it. Final delivery directory confirmed: `C:\Users\hoanc\company\dst_wiki\mods\SoloCombatHUD`. The user will copy the mod into the game and perform gameplay testing. No automatic installation, Workshop publication, or source-mod replacement is authorized or needed.

## Accepted behavior

- One independent personal mod replaces Simple Health Bar DST (local source 1207269058) and Epic Healthbar (1185229307).
- Retain overhead mob health bars, Epic boss visuals and supported phase information, and exclude a boss from overhead display while its Epic bar is displayed.
- One authoritative damage popup path: normal white, crit gold/orange and 20% larger, true damage cyan. Crit and true portions remain separate.
- Display resolved HP loss without changing combat. Blocked/dodged hits must not generate positive damage; nested damage paths and simultaneous attackers must not duplicate or misclassify events.
- Solo (3780347550) may have combat text OFF; the integration still receives crit/true metadata. Preserve EXP, quest and level-up notifications.
- Optional Solo integration must not make the standalone HUD crash when Solo is absent.
- Bound visibility, popup count and update work; preserve distinct damage types when aggregating. Claim no unmeasured FPS improvement.
- Disable both original healthbar mods when installing the integrated mod. Keep original source directories untouched.

## Implementation and verification sequence

1. Sol creates isolated modules/assets and retains source attribution. Integrate Epic's original boss implementation; reuse SHB assets and recreate the useful overhead behavior without its unrelated global overrides.
2. Sol implements a per-hit Solo bridge, resolved-damage collection and one popup transport/render path. Handle reentrancy, death, immunity, nearby observers, followers and dedicated clients.
3. Sol adds focused executable Lua tests, whole-package Lua syntax checking, asset/dependency checks and Vietnamese installation/playtest instructions.
4. Parent requests independent code review, returns material findings to Sol, and reruns relevant checks after fixes.
5. Deliver the ready-to-copy folder, explain required toggles and report exactly what was tested. Actual game rendering/performance remains for in-game verification.

## Decisions and evidence

- Source versions observed: Simple Health Bar DST 2.16; Epic Healthbar 102.
- Epic already has its own attacked-event popup path; it must be disabled when the unified path is enabled.
- Solo true damage uses `DoHHDelta`/`SetVal`, so a `DoDelta`-only listener misses it.
- Solo's `HH_CAN_SHOW_TEXT_FX` gate is shared with some informational notifications; hiding combat words must not blindly hide every call.
- Implementation choice: retain Epic proxy/widget/phase data and atlases, replace the obfuscated SHB runtime with scoped overhead handling. Cost: SHB's unrelated options are not automatically inherited; document supported settings explicitly.
- Runtime checks use Lua 5.1 through locally installed Lupa; mocks cannot establish real rendering, network timing or FPS.

## Status

- [x] User approved scope, implementation model and final path.
- [x] Implementation delegated to Sol 5.6.
- [x] Implementation and focused verification complete.
- [x] Independent review and required fixes complete.
- [x] Final package verified and ready for user copying.

## Review ledger

- Initial focused tests: resolver, Solo bridge, server wrapper pass under Lua 5.1 (28 assertions reported). Initial syntax check passed for 18 Lua files, 2 atlas references; all 256 original-source Lua hashes unchanged.
- First independent review returned material findings: real mod load order puts Solo crit classification outside the HUD transaction; silent follower critical branches missing; informational messages still blocked with Solo OFF; victim removal during lethal SetVal loses popup position; overhead widgets retained while hidden/removed; duplicated/clobbered Epic settings; nil-containing method return tuples; arbitrary numeric caps; boss selection/disabled HUD and visibility bounds.
- All findings returned to original Sol implementer; initial mock tests alone are not sufficient acceptance evidence.
- Execution adjustment: child runtime test command was waiting on elevation. Parent now runs Lua verification centrally so implementation does not block on child approval routing.
- Subsequent review fixed host registry, required-module environment, missing namespaced Epic persistence module, viewport eligibility before capacity allocation, and suppression only for the locally displayed boss. Widget callbacks belong to their widget entity and are cleaned on destruction.
- Final central verification: 4/4 Lua 5.1 test files pass; all 21 delivered Lua files compile; 2 atlas texture references and local asset checks pass; all 27 literal runtime require references resolve against package or installed DST scripts; all 256 original-source Lua hashes unchanged.
- Final scoped independent review: clean after checking Epic active/shown/transition condition. No real DST session, rendering, live multiplayer, or FPS measurement was performed. User will perform documented gameplay tests.
