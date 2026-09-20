-- Real soul component with deterministic entity/event/task/network doubles.
local count = 0
local function eq(got, want, label)
    assert(got == want, label .. ': expected ' .. tostring(want) .. ', got ' .. tostring(got))
    count = count + 1
end
Class = function(ctor)
    local c = {}; c.__index = c
    return setmetatable(c, {__call = function(_, ...)
        local self = setmetatable({}, c); ctor(self, ...); return self
    end})
end
TUNING = {EVA_REAP_COUNTER = 666} -- retired setting must have no effect
local function net()
    return {n = 0, set = function(self, n) self.n = n end,
        value = function(self) return self.n end}
end
local function entity(level)
    local inst = {components = {}, tags = {}, events = {}, delayed = {}, periodic = {},
        currentsouls = net(), maxsouls = net(), eva_level = net()}
    if level then inst.components.levelsystem = {level = level} end
    inst.components.health = {IsDead = function() return inst.dead == true end}
    function inst:HasTag(tag) return self.tags[tag] == true end
    function inst:ListenForEvent(name, fn)
        self.events[name] = self.events[name] or {}; table.insert(self.events[name], fn)
    end
    function inst:RemoveEventCallback(name, fn)
        for i, f in ipairs(self.events[name] or {}) do
            if f == fn then table.remove(self.events[name], i); break end
        end
    end
    function inst:PushEvent(name, data)
        for _, fn in ipairs(self.events[name] or {}) do fn(self, data) end
    end
    local function task(fn)
        return {fn = fn, Cancel = function(self) self.cancelled = true end}
    end
    function inst:DoTaskInTime(delay, fn)
        local t = task(fn); table.insert(self.delayed, t); return t
    end
    function inst:DoPeriodicTask(delay, fn)
        eq(delay, 1, 'one second update'); local t = task(fn)
        table.insert(self.periodic, t); return t
    end
    function inst:Flush()
        local tasks = self.delayed; self.delayed = {}
        for _, t in ipairs(tasks) do if not t.cancelled then t.fn(self) end end
    end
    function inst:Tick()
        for _, t in ipairs(self.periodic) do if not t.cancelled then t.fn(self) end end
    end
    return inst
end
local Soul = dofile('scripts/components/eva_souls.lua')
local function make(level, keep_initial)
    local inst = entity(level); local soul = Soul(inst)
    if not keep_initial then soul:DoDelta(-soul.current) end
    inst.components.eva_souls = soul; return inst, soul
end

local a, s = make(nil, true); a:Flush()
eq(s.max, 100, 'no dependency: fixed base capacity')
eq(s.current, 100, 'new character starts with 100 souls')
s:DoDelta(100); eq(s.current, 100, 'gain bounded')
s:DoDelta(-999); eq(s.current, 0, 'spending bounded')
a:Tick(); eq(s.current, 0, 'no dependency: no regeneration')
for _, case in ipairs({{1,100},{2,106},{100,694},{101,700},{150,994},{151,1000},{10000,1000}}) do
    a.components.levelsystem = {level = case[1]}
    a:PushEvent('chasni_levelup'); eq(s.max, case[2], 'level capacity ' .. case[1])
    eq(a.maxsouls:value(), case[2], 'replicated capacity ' .. case[1])
    eq(a.eva_level:value(), case[1], 'replicated level ' .. case[1])
end
eq(s:OnSave().level, 10000, 'EVA saves its own level without capping it to soul capacity')
a.components.levelsystem.level = 10001
eq(s:OnSave().level, 10001, 'save captures latest external level')
eq(a.eva_level:value(), 10001, 'save also syncs level above capacity cap')
a.components.levelsystem.level = 1; a:Tick()
eq(s:OnSave().level, 10001, 'recorded EVA level is not lost to external reset')
a, s = make(100); a:Flush()
s:DoDelta(50); a:Tick()
eq(s.current, 50, 'no regen at level 100')
a.components.levelsystem.level = 101; a:Tick()
eq(s.current, 51, 'regen at level 101; direct level restoration detected')
eq(s.max, 700, 'capacity follows direct level restoration')
s:DoDelta(999); a:Tick(); eq(s.current, 700, 'regen cannot exceed cap')
s:DoDelta(-20); a.dead = true; a:Tick(); eq(s.current, 680, 'no regen while dead')
a.dead = false; a.tags.playerghost = true; a:Tick()
eq(s.current, 680, 'no regen as ghost')
a.tags.playerghost = nil
s.current = 257; a:PushEvent('death'); eq(s.current, 25, 'death keeps floored 10 percent')
eq(a.currentsouls:value(), 25, 'death replicated')
a:PushEvent('death'); eq(s.current, 25, 'duplicate death does not charge again')
local saved = s:OnSave()
local b, loaded = make(nil)
loaded:OnLoad(saved)
b.components.levelsystem = {level = 101}; b.tags.playerghost = true; b:Flush()
eq(loaded.current, 25, 'ghost reload preserves retained souls')
b:PushEvent('death'); eq(loaded.current, 25, 'saved death guard')
b:Tick(); eq(loaded.current, 25, 'ghost reload never regenerates')
b.tags.playerghost = nil; b:PushEvent('ms_respawnedfromghost')
b:Tick(); eq(loaded.current, 26, 'respawn resumes regen')
b:PushEvent('death'); eq(loaded.current, 2, 'next real death charges once again')

local c, high = make(nil)
high:OnLoad({current = 900, maxsouls = 1000})
c.components.levelsystem = {level = 500}; c:Flush()
eq(high.current, 900, 'load order does not truncate high-level save at base cap')
eq(high.max, 1000, 'saved max is recomputed from actual level')
local d, standalone = make(nil)
standalone:OnLoad(high:OnSave()); d:Flush()
eq(standalone.current, 900, 'dependency disabled: saved EVA level preserves souls')
eq(standalone.max, 1000, 'dependency disabled: saved EVA level preserves capacity')
d:Tick(); eq(standalone.current, 901, 'saved EVA level permits regeneration without dependency')
eq(standalone:OnSave().level, 500, 'independent EVA level survives save/load')
local missing, legacy = make(nil)
legacy:OnLoad({current = 900, maxsouls = 1000}); missing:Flush()
eq(legacy.current, 100, 'old save without any level source defaults to level 1')
local late, tracked = make(nil); late:Flush()
late.components.levelsystem = {level = 101}; late:Tick()
eq(tracked:OnSave().level, 101, 'late Achievement level restore captured')
late.components.levelsystem.level = 120; late:PushEvent('chasni_levelup')
eq(tracked:OnSave().level, 120, 'level-up event updates EVA saved level')
late.components.levelsystem = nil; late:Tick()
eq(tracked.max, 814, 'removing external component keeps recorded capacity')
local e, oldsave = make(1)
oldsave:OnLoad({current = 17.8, maxsouls = 666}); e:Flush()
eq(oldsave.current, 17, 'old fractional saves normalized to whole souls')
eq(oldsave.max, 100, 'old config and saved cap ignored')
oldsave:DoDelta(10); e:PushEvent('death'); eq(oldsave.current, 2, 'old save death behavior')
e:PushEvent('ms_respawnedfromghost'); oldsave:DoDelta(-99)
e:PushEvent('death'); eq(oldsave.current, 0, 'empty death stays zero')
high:OnRemoveFromEntity(); local before = high.current; c:Tick()
eq(high.current, before, 'component removal cancels regeneration')
c:PushEvent('death'); eq(high.current, before, 'component removal detaches events')

-- Client HUD consumes replicated maximum, never server-only level components.
local player_init, status_init
GLOBAL = {TheWorld = {ismastersim = false}, net_ushortint = net, net_uint = net}
GLOBAL.require = function() return function()
    return {SetPercent = function(self, value, max) self.value, self.max = value, max end,
        SetPosition = function() end, Hide = function(self) self.visible = false end,
        Show = function(self) self.visible = true end}
end end
AddPlayerPostInit = function(fn) player_init = fn end
AddClassPostConstruct = function(_, fn) status_init = fn end
dofile('scripts/util/eva_widget.lua')
local client = entity(nil); client.prefab = 'eva'
client.components = setmetatable({}, {__index = function() error('client read server component') end})
player_init(client)
local display = {owner = client, AddChild = function(_, child) return child end,
    SetGhostMode = function() end}
status_init(display)
client.currentsouls:set(130); client.maxsouls:set(260); client:PushEvent('soulsdirty')
eq(display.hud_souls.max, 260, 'client max sync')
eq(display.hud_souls.value, 0.5, 'client percentage uses dynamic capacity')
client.maxsouls:set(1000); client:PushEvent('soulsdirty')
eq(display.hud_souls.max, 1000, 'max-only change updates client HUD')
display:SetGhostMode(true); eq(display.hud_souls.visible, false, 'ghost HUD hidden')
display:SetGhostMode(false); eq(display.hud_souls.visible, true, 'human HUD visible')
print('PASS: ' .. count .. ' soul progression assertions')
