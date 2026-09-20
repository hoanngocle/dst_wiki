# EVA

Release: **1.2.0**. The stable folder/display name is `EVA`; `modinfo.lua`
is the version source, with release history in `CHANGELOG.md`.
Versioned archives contain `EVA/`. See the Vietnamese README for migration
from `EVA_v1.0` and the release-version policy.

EVA is an independent Don't Starve Together character using the existing
`eva` prefab ID for save compatibility. The approved silver-haired,
amethyst-eyed, single lavender gown appearance and matching scythe remain in
place.

## Skill panel and input

The bottom-right HUD panel has five collapsible, no-inventory icons: Sinh Chi Hoa,
Tinh Vũ Nguyệt Dực, Trảm Linh, Tử Phong Tụ Linh and Dạ Du. Vietnamese hover text shows costs and ranges;
server-replicated values drive cooldown numbers and Wings state. Sinh Chi Hoa and
Wings execute immediately. Trảm Linh, Tử Phong Tụ Linh and Dạ Du enter the native point reticule and
spends nothing until the world point is confirmed; cancelling is free. The
established G/H/J bindings remain optional shortcuts.

Its hidden spellbook is owner-bound and non-persistent. It is never inserted
into an inventory, cannot be picked up or traded, and is removed with EVA.
Remote clients may target only through their own replicated book reference;
the server checks its owner and delegates to EVA's component.

## Sinh Chi Hoa

Press **G** by default while the gameplay HUD has focus. The shortcut can be
changed to H, J, K or L, or disabled, in the mod configuration. The client
sends only an activation request; the server validates the EVA character,
life state, action state, active duration and cooldown.

An accepted activation lasts 15 seconds and starts its 60-second cooldown
immediately. It costs 10 Hồn Lực per accepted activation and does not require the scythe.

- Every 0.2 seconds, one lavender/silver projectile seeks a current enemy or
  hostile threat within 12 units and deals 80 base damage. The target is
  checked again on impact.
- Every 0.5 seconds, the aura deals 67 base damage to each legal enemy within
  6 units.
- EVA heals 5% of current maximum health exactly at seconds 0, 3, 6, 9 and 12.
- A silver force field snapshots 25% of maximum health on activation. It
  absorbs a finite amount, passes overflow damage to health, and disappears
  when depleted or when the 15-second skill ends.

The aura and projectile call the target's combat component directly with no
weapon. Target armor and health absorption still apply, while scythe effects
and weapon multipliers cannot be triggered by the skill. The shield chains the
existing health delta modifier after inventory armor and health absorption; it
does not set invincibility. Cleanup restores the earlier modifier when EVA
still owns the hook and leaves a later third-party hook in place.

Valid targets must be alive, visible combat entities that EVA can legally
attack and that are hostile, attacking EVA, or EVA's current combat target.
The skill excludes EVA, ghosts, untargetable entities, companions, allied
followers and neutral bystanders. Players are excluded while PvP is off.

## Tinh Vũ Nguyệt Dực

Press **H** by default to toggle EVA's silver wings and violet lightning. An
accepted OFF-to-ON transition costs exactly **100 Hồn Lực**. Staying
airborne, closing the wings, and restoring a saved active state are free; the
wings have no maintenance drain and no cultivation requirement. If the Wings
and Sinh Chi Hoa shortcuts are configured to the same key, Sinh Chi Hoa keeps that key and the
Wings shortcut is suppressed until the bindings are separated.

While open, the wings add 8% movement speed and let EVA walk across ocean
tiles on surface worlds. Walls and normal obstacles still collide, and cave
void falling remains enabled. EVA cannot manually close the wings over open
ocean without a platform; return to land or a boat first. Death, ghost state,
mounting, hopping, swimming, freezing, and removal force safe cleanup.

The replicated active state applies the same ocean pathing and collision limit
changes to local client prediction. The visual retains Tu Tiên's `xd_htz_flc`
animation motion with new silver/lavender feather artwork, moon ornaments and
star highlights in the independent `eva_moon_wings` bank. The original owner
colour-adder synchronization is preserved on hosts, clients and dedicated
servers, including the current colour for late joiners. No Tu Tiên Lua code is imported.

## Huyền Thiên Trảm Linh Kiếm — level-100 Ultimate

Press **J** by default while the gameplay HUD has focus to cast at the world
cursor. The server accepts finite legal points within 12 units. Land and
platforms are valid; an open-ocean center requires active Tinh Vũ Nguyệt Dực. An
accepted cast spends exactly **100 Hồn Lực**, immediately starts a 60-second
cooldown, and does not require the equipped scythe, cultivation or another
buff. Sinh Chi Hoa and Wings retain priority when shortcuts collide.

Five purple EVA scythes mark a fixed radius-5 pentagon. From second 1.3,
legal enemies inside that polygon are rooted, while leaving or becoming
invalid releases only this array's root source. A large center scythe strikes
once for 734 base damage at second 1.8 in radius 6. Its native purple beam
finishes the 1.1-second warning before dealing 200 base damage every 0.5
seconds from 2.9 through 7.9, for 11 pulses. Damage uses the selected center,
credits EVA as attacker, respects normal armor, and follows Sinh Chi Hoa's ally,
follower, PvP, visibility and neutral-target protections.

Death, ghost state, removal and expiry cancel owned tasks, release owned roots
and remove the transient visuals. Cooldown survives save/load; an active
array does not resume and never refunds or charges Hồn Lực again on load.

## Tử Phong Tụ Linh

Click its panel icon and confirm a finite point within 12 units. An accepted
cast costs exactly **3 Hồn Lực**, lasts 7 seconds, affects a radius of 8 and
starts a 10-second cooldown. Cancelling the reticule, choosing an invalid point,
or failing to create the effect costs nothing.

Every 0.5 seconds the vortex harvests ready pickables, chops or mines valid
workables, and digs only stumps. Loose ground items move toward the selected
center without entering EVA's inventory. It excludes held items, containers,
traders and structures, and it does not uproot planted pickables or protected
plant infrastructure. The skill does not claim to extinguish fires.

## Dạ Du

Click its panel icon and confirm a point within 12 units. The server selects the
nearest valid enemy within 2 units of that point. If no valid target exists, the
cast costs nothing. The enemy must also be within 12 units of EVA and able to
receive the mark. An accepted cast costs exactly **5 Hồn Lực**, launches a
mark-only scythe projectile and starts a 15-second cooldown.

On impact the target takes 10% more damage for 5 seconds. The projectile itself
deals no direct damage. Reapplying the mark refreshes its duration without
stacking the multiplier, including marks from different EVA players. A target
that becomes invalid after the projectile launches does not refund the cast.

## Melee sword wave

Every two successful weapon melee hits release one free purple sword wave for
50 base damage. Melee attacks made with tools count; unarmed attacks, work
actions, misses, ranged attacks, generated skill hits and the wave's own damage
do not. A partial one-hit count resets on death and is not restored from a save.

## Hồ Ảnh

Right-click empty ground to cast Hồ Ảnh. Existing object, container,
equipped-item, deployment, mount and active-reticule actions keep priority;
empty deck points remain valid. The server accepts only finite, legal
destinations within 20 units. The skill costs no Hồn Lực and starts its
12-second cooldown only after acceptance; invalid points are free.

The cast fades EVA over 0.5 seconds, relocates at 1.75 seconds, restores at
2.0 and completes at 2.2. Its purple fire deals three 266.7-base-damage
pulses at 0/0.2/0.4 seconds, heals 3.3% maximum health on the first pulse and
applies guarded sleepiness on the third. It shares Sinh Chi Hoa's ally, follower, PvP
and neutral protections. Interruption or load restores presentation, movement
and only the protection owned by Hồ Ảnh.

## Hồn Lực and scythe

Hồn Lực retains its saved counter and HUD (the original internal save field
is still named Soul for compatibility). EVA gains +1 Hồn Lực for a
normal valid kill, +10 for a ghost and +30 for an epic enemy. EVA stores its own
attained level in the soul component save data. Achievement & Level's player level
(`levelsystem.level`) raises that recorded level on level-up, initial load or delayed
restoration; disabling/resetting the external mod does not lower EVA's saved level.
EVA has no separate XP counter. A new character without that mod starts at level 1.

Capacity is fixed at `min(1000, 100 + 6 * (EVA level - 1))`; the old maximum setting
is removed and ignored. New characters start with 100/100 souls; existing saves keep their current amount.
The cap reaches 1000 at level 151 (994 at level 150). From level 101, living EVA
regenerates 1 Hồn Lực per second, up to capacity. Ghosts/dead characters do not
regenerate. A death retains `floor(current / 10)` Hồn Lực; loading a ghost save
does not apply the penalty again. Current souls, attained level and the death guard
are saved; both current and maximum souls are replicated to the HUD.

Kills from Sinh Chi Hoa count. Hồn Lực has no combat multiplier,
critical chance or passive decay. Opening Tinh Vũ Nguyệt Dực costs 100 and casting Tử Phong Tụ
Linh costs 3, Dạ Du costs 5, Huyền Thiên Trảm Linh Kiếm costs 100,
Sinh Chi Hoa costs 10, and Hồ Ảnh is free.

The EVA scythe is a normal melee weapon with configurable base damage,
durability and recipe. EVA's Soul Strike, Hồn Lực criticals, kill healing,
immortality/sleep recovery, special sanity relationships and specialty item
recipes are not EVA abilities. The old hat, kazoo and wine prefabs, animations,
textures and kazoo sounds have been removed; existing save items of these types
are no longer supported. The crafting tab now uses the EVA portrait.

## Installation

1. Extract `EVA_v1.2.0.zip` into the game's `mods` directory so that
   `mods/EVA/modinfo.lua` exists.
2. Enable EVA. Disable other EVA/EVA packages that register the same
   internal prefab IDs.
3. Install the same package on the server and participating clients.

EVA works standalone and does not import Tu Tiên or require Solo Leveling.

With the locally audited Solo Leveling 2.2.7, EVA skill damage preserves Solo's
attack bonuses, critical hits and other on-hit effects, while excluding its
melee splash proc. Ordinary weapon melee attacks retain Solo splash. The EVA
damage helper temporarily uses Solo's synchronous splash guard, restores its
prior value on nested hits/errors, and leaves the original combat arguments
and attacker attribution intact. It takes the normal combat path without Solo.
EVA cooldowns remain fixed as documented; no INT cooldown scaling is included.

## Verification and limits

Automated Lua 5.1 checks cover activation and cooldown, the five heal ticks,
projectile cadence and impact validation, aura targeting, shield partial/full/
overflow/depletion/expiry behavior, third-party health-hook chaining, cleanup,
save/load and RPC/input rejection. Wing checks cover exact Hồn Lực charging,
free persistence restore, collision/path-cap ownership, drowning/void
separation, cave safety, ghost cleanup, prediction timing, key conflicts and
original wing motion and attachment geometry. Array checks cover polygon geometry, finite and
terrain coordinate validation, cost/cooldown persistence, center-relative
damage, overlapping root ownership, exact 734/200 timing, terminal cleanup,
input guards and key priority. Panel checks cover remote owner binding,
no-slot native targeting for all three point skills, reselection and cancel behavior,
dedicated-server action rebuilding, replicated cooldowns, impostor-book rejection
and the five-icon layout. Fox checks cover finite/range/
terrain validation, exact fade/relocation/fire timing, interruption cleanup,
save/load and right-click priority. The package also receives syntax, archive CRC,
byte-parity and unchanged-art checks before delivery.

No in-game or multiplayer test has been performed. A host and remote client
should still smoke-test the five icons and G/H/J shortcuts while idle and
while chat is focused; cancel and reselect each point reticule; use Hồ Ảnh on empty
land/deck/ocean, ordinary objects and out-of-range points; hostile/allied
targets; shield overflow; Life's 15-second expiry and
60-second cooldown; the array's 100-Hồn-Lực cost, 60-second cooldown, polygon
rooting, 11 beam pulses and overlapping-source cleanup; save/reload on land and
water; remote-client water walking; wing closing from land/boat/open ocean;
Hồn Lực awards; and the absence of retired EVA powers.

Original EVA mod author: ZeroRyuk. Original Workshop ID: 2336991112.
Tinh Vũ Nguyệt Dực retains Phong Lôi Xí's original animation motion with new
silver/lavender moon-and-star wing sprites and a separate EVA animation bank.
Wing animation and Hồ Ảnh FX source: Tu Tiên Ký workshop package
3721846643. Hồ Ảnh uses standalone EVA-prefixed copies derived from
`xd_sudaji_mxrg` and its related effects; no Tu Tiên runtime is loaded.

## Skill progression

EVA's saved level unlocks Fox blink and the passive melee wave at level 1,
Sinh Chi Hoa at 10, Harvest at 20, Wings at 30, Dạ Du at 50 and the Ultimate
scythe array at 100. There is no level-70 unlock and no Death Flower skill.
Locked panel icons display their required level; clients use the replicated EVA
level, while every server activation route enforces the saved-level requirement.
The Ultimate's 734 strike plus eleven 200 pulses total 2934 base damage if all hit.
Existing Solo damage/blocking behavior is unchanged.

## Sinh Chi Hoa artwork

Sinh Chi Hoa now uses a custom silver/lavender flower icon, rotating flower
projectiles, a translucent ground flower and brief flower flashes on impact
and each heal tick. The shield is pale silver/violet. EVA-prefixed animation
copies retain the motion of Tu Tiên Ký's Life flower; their textures and full
quad meshes use the new flower artwork, without loading the source mod's Lua.
Damage, healing, shield capacity, targeting, unlock level and cooldown are unchanged.
Asset previews are rendered from the compiled files, not captured in-game.
