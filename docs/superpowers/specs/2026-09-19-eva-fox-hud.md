# EVA Hồ Ảnh and clickable skill panel

User authorized porting Hồ Ảnh and replacing keyboard-only operation with a Hàn Thiên Tôn style panel. Explicit answers: Hồ Ảnh costs zero Hồn Lực; panel icons occupy no inventory slots. Existing Sol High execution preference persists. Work is within the existing standalone mod, not the original Tu Tiên package.

## User flow

Three permanent, collapsible HUD icons: Sinh, Phong Lôi Xí, Trảm Linh. Sinh activates immediately; Wings toggles immediately; Array enters point targeting and casts only after world confirmation. Hồ Ảnh is direct ground right-click only and has no panel icon. Cancel targeting freely. Show remaining cooldowns and Wings active state, helpful Vietnamese hover labels with costs/ranges. Hide/disable on ghost, menus and chat. Retain existing G/H/J as optional shortcuts; icons are the primary use and require no equipped item, crafting, cultivation, or extra inventory slot. Default position must avoid inventory and status meters.

Hàn's native pattern is a hidden owned spellbook with network entity reference and native AOE reticule; adapt it without importing his framework or copying insecure global ownership overrides. Book belongs only to its EVA, cannot be traded/picked/dropped, recreated on load, removed with owner. Native cast animation being busy must not cause all existing skills to reject their own authorized cast. Server checks owner, selected skill, range, finite values, cooldown, Soul costs; never trusts UI state. Display cooldown from server-replicated state. HUD must work on listen host and remote client, and never be instantiated on dedicated server.

Additional user steering: Hồ Ảnh binds directly to right-click on empty ground, like Hàn's movement skill. Latest user explicitly removed its panel icon; show only the other three skills. Preserve right-click actions on objects, active inventory items/deploying, native AOE targeting cancellation, menus and other characters. Remote client and host use the same server validation/cooldown. No equipment prerequisite.

## Hồ Ảnh

- Standalone component `eva_fox_blink`; `CastAt(x,z)` returns success/reason, `GetCooldownRemaining()`, `Stop(reason)`, save/load remaining cooldown.
- Cost0; range20 hard server bound from activation position; cooldown12 from accepted cast. Invalid casts/cancelled targeting don't start cooldown. Failed destination revalidation must restore all state; accepted cast interrupted afterward retains cooldown.
- Port source normal timeline: fade over0.5s, own dodge protection from0.5; relocate at1.75; restore at2.0 (0.25 after relocation); finish at2.2. Native animation alternatives must exist in EVA banks; do not reference Tu Tiên character-only animation. Engine state interrupts/death/ghost/removal always restore owned visibility/shadow/protection/movement state. Do not globally clear another skill's invincibility or override Physics collision masks.
- Validate terrain, world bounds, finite coords, ground-target blockers and native teleport permissions both before accepting and at relocation. Land/platform valid; open ocean only with active EVA Wings, never cave void. Reject mount/hop/frozen/ghost/busy/invalid health. Respect active Wings pathing/collision ownership.
- At destination show original fox FX and purple fire, tinted silver/lavender; standalone copied source animation banks in uniquely named EVA archive files. No original EVA binary art changed. No image generation is needed for reusing source artwork with runtime tint.
- Native fire source: three266.7 base hits at0,.2,.4 after fire spawn; radius4. First tick heals owner3.3% max health; third applies sleepiness0.8 for3seconds or equivalent grogginess where supported, respecting frozen/pinned/fossilized guards. Apply Life common allegiance/neutral/PvP protections; owner is attacker for Soul credit. Damage passes normal combat/armor without original Tu Tiên cultivation multipliers. Fire visual lifetime1.5s; owner death/ghost/removal cancels remaining damage/heal. Don't ignite terrain/items.
- Clarified to user: sleepiness affects valid enemy targets only, never EVA. User's conditional request to remove self-sleep does not remove enemy control.
- Save/load does not resume an active blink/fire or hide player; only cooldown persists.

## Preserved systems

Sinh15s/CD60/free, Wings+8%/3HồnLực on enable/free upkeep and disable, Array range12/15HồnLực/CD25 and existing damage timeline; original single EVA skin/assets, soul kill counting, absence of legacy Calliope powers. No Tu Tiên runtime dependency.

## Evidence and delivery

Capture95-file baseline and archive before mutation. Behavioral tests of blink and native engine visibility/protection; HUD/hidden book action path and server validation with host/client/dedicated fixtures; all current regression suites. Package byte parity/CRC and unchanged-art hashes. No live game test claim. No Steam writes, git commits or publication.
