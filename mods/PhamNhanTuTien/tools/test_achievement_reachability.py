"""Execute installed achievement adapters and native action/plant/cook code in Lua 5.1."""
from pathlib import Path
from zipfile import ZipFile
import unittest
from lupa.lua51 import LuaRuntime

MOD = Path(__file__).resolve().parents[1]
GAME = Path("C:/Program Files (x86)/Steam/steamapps/common/Don't Starve Together/data/databundles/scripts.zip")


class ActivityReachability(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute("package.path = ... .. package.path", (MOD / "scripts/?.lua").as_posix() + ";")
        self.lua.execute('''
            GLOBAL=_G; env={}; modname="test"; hooks={}; prefab_hooks={}; AllPlayers={}
            TheWorld={ismastersim=true,state={season="autumn",cycles=0,elapseddaysinseason=0,isnight=false,isday=true},
                Map={GetTileAtPoint=function(_,x) return x == 1 and 10 or 0 end}}
            WORLD_TILES={FARMING_SOIL=10}; TUNING={BASE_COOK_TIME=10}
            function Class(ctor) local c={}; c.__index=c
                return setmetatable(c,{__call=function(_,...) local s=setmetatable({},c); ctor(s,...); return s end}) end
            function AddReplicableComponent() end
            function AddPlayerPostInit(fn) player_init=fn end
            function AddComponentPostInit(name,fn) hooks[name]=fn end
            function AddPrefabPostInit(name,fn) prefab_hooks[name]=fn end
            function AddModRPCHandler() end
            function modimport() end
            function net_string() return {set=function() end} end
            function GetTime() return 0 end
            function FunctionOrValue(v,...) if type(v)=="function" then return v(...) end return v end
            package.loaded["achievement/ttk_perk_effects"]={Install=function() end,Apply=function() end}
            package.loaded.cooking={CalculateRecipe=function() return "meatballs",1 end,
                GetRecipe=function() return {perishtime=100} end}
            function entity(prefab)
                local e={prefab=prefab,components={},events={},watch={},tasks={},tags={},valid=true,Transform={SetPosition=function() end}}
                function e:IsValid() return self.valid end
                function e:HasTag(t) return self.tags[t] == true end
                function e:AddTag(t) self.tags[t]=true end
                function e:RemoveTag(t) self.tags[t]=nil end
                function e:Remove() self.valid=false end
                function e:OnUsedAsItem() end
                function e:GetPosition() return {Get=function() return 1,0,0 end} end
                function e:ListenForEvent(n,fn) self.events[n]=self.events[n] or {}; table.insert(self.events[n],fn) end
                function e:PushEvent(n,d) for _,fn in ipairs(self.events[n] or {}) do fn(self,d) end end
                function e:WatchWorldState(n,fn) self.watch[n]=self.watch[n] or {}; table.insert(self.watch[n],fn) end
                function e:DoTaskInTime(t,fn,...)
                    local args={...}; local task={cancel=false,time=t}
                    function task:Cancel() self.cancel=true end
                    task.run=function() if not task.cancel then fn(self,unpack(args)) end end
                    table.insert(self.tasks,task); return task
                end
                function e:flush()
                    local tasks=self.tasks; self.tasks={}
                    for _,t in ipairs(tasks) do if t.time==0 then t.run() else table.insert(self.tasks,t) end end
                end
                return e
            end
            function SpawnPrefab(p) return entity(p) end
            function TheWorld:PushEvent() end
            local Progress=require("components/ttk_achievement_progress")
            function player(id,setup,defer)
                local p=entity("wilson"); p.userid=id; p.player_classified={}; p.tags.player=true
                p.components.health={IsDead=function() return p.dead == true end}
                p.components.temperature={current=20,overheattemp=70,IsFreezing=function(s) return s.current<0 end,
                    IsOverheating=function(s) return s.current>s.overheattemp end}
                p.components.inventory={itemslots={},equipslots={},GetOverflowContainer=function(s) return s.overflow end}
                p.components.ttk_achievement_progress=Progress(p)
                if setup then setup(p) end
                table.insert(AllPlayers,p); player_init(p); if not defer then p:flush() end; return p
            end
            function progress(p,id) local s=p.components.ttk_achievement_progress.core.achievements[id]; return s and s.progress or 0 end
            function world(n,v)
                TheWorld.state[n]=v
                for _,p in ipairs(AllPlayers) do for _,fn in ipairs(p.watch[n] or {}) do fn(p,v) end end
            end
            function temp(p,v) p.components.temperature.current=v; p:PushEvent("temperaturedelta",{new=999}) end
            function item(p,prefab,size)
                local i=entity(prefab); i.components.inventoryitem={inst=i,GetGrandOwner=function() return i.owner end}; i.owner=p
                i.components.stackable={inst=i,size=size,StackSize=function(s) return s.size end,Get=function() end,Put=function() end}
                hooks.inventoryitem(i.components.inventoryitem); hooks.stackable(i.components.stackable); return i
            end
        ''')
        with ZipFile(GAME) as archive:
            for name, var in (("bufferedaction", "NativeAction"), ("components/farmplantable", "Plantable"), ("components/stewer", "Stewer")):
                self.lua.execute(var + " = (function() " + archive.read("scripts/" + name + ".lua").decode() + " end)()")
        self.lua.execute((MOD / "main/ttk_achievement.lua").read_text(encoding="utf-8"))

    def test_pick_regrowth_fish_identity_and_two_actors(self):
        self.lua.execute('''
            a=player("a"); b=player("b"); bush=entity("grass"); d={object=bush}
            a:PushEvent("picksomething",d); a:PushEvent("picksomething",d)
            assert(progress(a,"labor_pick_grass")==1,"missing committed pick route")
            a:PushEvent("picksomething",{object=bush}); b:PushEvent("picksomething",{object=bush})
            assert(progress(a,"labor_pick_grass")==2 and progress(b,"labor_pick_grass")==1)
            f=entity("fish"); a:PushEvent("fishingcatch",{fish=f}); a:PushEvent("fishingcollect",{})
            a:PushEvent("fishingcollect",{fish=entity("oceanfish_small_1_inv")})
            assert(progress(a,"labor_fish_pond")==0)
            a:PushEvent("fishingcollect",{fish=f}); a:PushEvent("fishingcollect",{fish=f})
            a:PushEvent("fishingcollect",{fish=entity("eel")})
            assert(progress(a,"labor_fish_pond")==2 and progress(b,"labor_fish_pond")==0)
        ''')

    def test_native_plant_success_failure_and_explicit_map(self):
        self.lua.execute('''
            a=player("a"); b=player("b"); soil=entity("farm_soil"); soil.tags.soil=true
            function plant(seed,doer,target)
                local i=entity(seed); local c=Plantable(i); c.plant="farm_plant_carrot"; if hooks.farmplantable then hooks.farmplantable(c) end
                return c:Plant(target,doer)
            end
            assert(plant("carrot_seeds",a,entity("ground"))==false)
            assert(progress(a,"farming_plant_carrot")==0)
            assert(plant("carrot_seeds",a,soil)); assert(progress(a,"farming_plant_carrot")==1,"missing plant receipt")
            plant("invented_seeds",a,soil); plant("seeds",b,soil)
            assert(progress(a,"farming_plant_carrot")==1 and progress(b,"labor_plant_seeds")==1)
            for _,crop in ipairs({"pumpkin","eggplant","dragonfruit","asparagus","tomato","potato","garlic","onion","pepper","pomegranate"}) do
                plant(crop.."_seeds",a,soil); assert(progress(a,"farming_plant_"..crop)==1,crop)
            end
        ''')

    def test_native_success_callbacks_reject_failed_canceled_and_nonfarm(self):
        self.lua.execute('''
            a=player("a"); b=player("b"); farm=entity("farm_plant_carrot"); farm.tags.farm_plant=true
            function action(id,target,x,success,doer,inv)
                local act=setmetatable({doer=doer or a,target=target,invobject=inv,onsuccess={},onfail={},
                    action={id=id,fn=function() return success end}}, {__index=BufferedAction})
                function act:IsValid() return true end
                function act:GetActionPoint() return {Get=function() return x or 0,0,0 end} end
                a:PushEvent("performaction",{action=act}); a:PushEvent("performaction",{action=act}); return act
            end
            action("POUR_WATER",farm,0,false):Do()
            action("POUR_WATER",farm,0,true):Fail()
            action("POUR_WATER",entity("campfire"),1,true):Do()
            action("POUR_WATER_GROUNDTILE",nil,0,true):Do()
            action("POUR_WATER",farm,0,true,b):Do()
            assert(progress(a,"farming_water_plants")==0)
            action("POUR_WATER",farm,0,true):Do()
            action("POUR_WATER_GROUNDTILE",nil,1,true):Do()
            assert(progress(a,"farming_water_plants")==2,"missing farm success receipt")
            local manure=entity("poop"); manure.components.fertilizer={nutrients={1,1,1}}
            function manure:OnUsedAsItem() end
            action("DEPLOY",nil,0,true,a,manure):Do()
            action("DEPLOY_TILEARRIVE",nil,0,true,a,manure):Do()
            action("DEPLOY_TILEARRIVE",nil,1,false,a,manure):Do()
            action("DEPLOY_TILEARRIVE",nil,1,true,a,manure):Fail()
            action("DEPLOY_TILEARRIVE",nil,1,true,b,manure):Do()
            action("DEPLOY_TILEARRIVE",nil,1,true,a,entity("sapling")):Do()
            action("DEPLOY",nil,1,true,a,entity("sapling")):Do()
            action("FERTILIZE",entity("campfire"),1,true,a,manure):Do()
            assert(progress(a,"farming_fertilize_plants")==0)
            action("DEPLOY",nil,1,true,a,manure):Do()
            action("FERTILIZE",farm,0,true,a,manure):Do()
            assert(progress(a,"farming_fertilize_plants")==2)
            -- Native tile_deploy fertilizer uses this action ID on farming soil.
            action("DEPLOY_TILEARRIVE",nil,1,true,a,manure):Do()
            assert(progress(a,"farming_fertilize_plants")==3,"native tile fertilizer must credit its committing actor once")
            assert(progress(b,"farming_fertilize_plants")==0)
            a:PushEvent("tilling"); assert(progress(a,"farming_till_soil")==1)
        ''')

    def test_inventory_observes_partial_amount_overflow_and_transfers(self):
        self.lua.execute('''
            a=player("a"); b=player("b"); i=item(a,"ttk_lingshi4",4)
            a.components.inventory.itemslots[1]=i; a:PushEvent("itemget",{item=i}); a:flush()
            assert(progress(a,"collection_lingshi4")==4,"ownership must observe four, not jump to target")
            i.components.stackable.size=8; i:PushEvent("stacksizechange"); a:flush()
            assert(progress(a,"collection_lingshi4")==8)
            a.components.inventory.itemslots={}; i.owner=b; b.components.inventory.itemslots[1]=i
            a:PushEvent("itemlose",{prev_item=i}); b:PushEvent("itemget",{item=i}); a:flush(); b:flush()
            assert(progress(a,"collection_lingshi4")==8 and progress(b,"collection_lingshi4")==8)
            a.components.inventory.itemslots[1]=item(a,"ttk_lingshi4",3); a:PushEvent("itemget",{item=a.components.inventory.itemslots[1]}); a:flush()
            assert(progress(a,"collection_lingshi4")==8,"transfers must not accumulate ownership")
            a.components.inventory.overflow={slots={item(a,"ttk_lingshi4",90)}}
            a:PushEvent("equip"); a:flush(); assert(progress(a,"collection_lingshi4")==93)
            a.components.inventory.opencontainers={slots={item(a,"ttk_lingshi4",1000)}}
            a:PushEvent("itemlose"); a:flush(); assert(progress(a,"collection_lingshi4")==93)
            a.components.inventory.overflow.slots[1].components.stackable.size=97
            a.components.inventory.overflow.slots[1]:PushEvent("stacksizechange"); a:flush()
            assert(progress(a,"collection_lingshi4")==100)
        ''')

    def test_dropped_and_removed_items_do_not_retain_former_players(self):
        self.lua.execute('''
            kept_items={}; former_players=setmetatable({}, {__mode="v"})
            for index,event in ipairs({"ondropped","onremove"}) do
                local owner=player("owner_"..event)
                local held=item(owner,"ttk_lingshi4",4)
                kept_items[index]=held; former_players[index]=owner
                owner.components.inventory.itemslots[1]=held
                held:PushEvent("onputininventory"); owner:flush()
                assert(progress(owner,"collection_lingshi4")==4)
                held.owner=nil; owner.components.inventory.itemslots={}
                held:PushEvent(event)
                assert(owner._ttk_ownership_pending,"item lifecycle must still queue former-owner observation")
                owner:flush()
                assert(not owner._ttk_ownership_pending)
                assert(progress(owner,"collection_lingshi4")==4,"loss must preserve observed high-water progress")
            end
            AllPlayers={}
            collectgarbage("collect"); collectgarbage("collect")
            assert(former_players[1]==nil,"a surviving dropped item must not retain its former player")
            assert(former_players[2]==nil,"a referenced removed item must not retain its former player")
        ''')

    def test_native_cook_commit_chef_save_load_and_callback_preservation(self):
        self.lua.execute('''
            a=player("a"); b=player("b"); callbacks=0
            function pot(saved)
                local p=entity("cookpot")
                p.components.container={slots={},Close=function() end,DestroyContents=function() end}
                local s=Stewer(p); p.components.stewer=s
                if hooks.stewer then hooks.stewer(s) end
                s.ondonecooking=function() callbacks=callbacks+1 end
                if prefab_hooks.cookpot then prefab_hooks.cookpot(p) end
                if saved then s:OnLoad(saved) end
                return p,s
            end
            p,s=pot(); s:StartCooking(a)
            local saved=s:OnSave(); p,s=pot(saved)
            s.task.run()
            assert(progress(a,"labor_cook_meals")==0,"ondonecooking precedes done; award must defer")
            p:flush(); assert(progress(a,"labor_cook_meals")==1,"missing committed chef receipt")
            assert(callbacks==1 and progress(b,"labor_cook_meals")==0)
            s.ondonecooking(p); p:flush(); assert(progress(a,"labor_cook_meals")==1)
            saved=s:OnSave(); q,t=pot(saved); t.ondonecooking(q); q:flush()
            assert(progress(a,"labor_cook_meals")==1,"completed load must not award again")
            s.product=nil; s.done=nil; s.targettime=nil; s:StartCooking(b)
            s.task.run(); p:flush(); assert(progress(b,"labor_cook_meals")==1)
        ''')

    def test_all_survival_keys_in_solo_authoritative_state(self):
        self.lua.execute('''
            a=player("solo")
            for _,season in ipairs({"winter","spring","summer","autumn"}) do world("season",season); a:flush() end
            for _,season in ipairs({"autumn","winter","spring","summer"}) do assert(progress(a,"survive_"..season)==1,"season "..season) end
            for i=1,100 do world("cycles",i); world("cycles",i) end
            assert(progress(a,"survive_hundred_days")==100 and progress(a,"survive_rescue_friend")==30)
            world("isnight",true); world("isnight",false)
            assert(progress(a,"survive_night")==0)
            world("isday",true); assert(progress(a,"survive_night")==1)
            temp(a,75); assert(progress(a,"survive_heat")==0); temp(a,20)
            temp(a,-5); assert(progress(a,"survive_cold")==0); temp(a,20)
            assert(progress(a,"survive_heat")==1 and progress(a,"survive_cold")==1)
            a.dead=true; a:PushEvent("death"); a:PushEvent("ms_respawnedfromghost")
            assert(progress(a,"survive_revive")==0)
            a.dead=false; a:PushEvent("ms_respawnedfromghost"); assert(progress(a,"survive_revive")==1)
        ''')

    def test_death_reload_and_client_cannot_fabricate_receipts(self):
        self.lua.execute('''
            a=player("solo"); temp(a,80); world("isnight",true)
            a.dead=true; a:PushEvent("death"); temp(a,20); world("isday",true); world("cycles",1); world("season","winter")
            for _,id in ipairs({"heat","night","hundred_days","autumn"}) do assert(progress(a,"survive_"..id)==0,id) end
            a.dead=false; a:PushEvent("ms_respawnedfromghost"); world("cycles",2)
            assert(progress(a,"survive_hundred_days")==1)
            TheWorld.ismastersim=false; b=player("client")
            assert(b._ttk_achievement_installed==nil)
            a:PushEvent("picksomething",{object=entity("grass")}); a:PushEvent("fishingcollect",{fish=entity("fish")})
            temp(a,-10); temp(a,20); world("cycles",3)
            assert(progress(a,"labor_pick_grass")==0 and progress(a,"labor_fish_pond")==0 and progress(a,"survive_cold")==0)
        ''')

    def test_reload_baselines_inventory_day_night_temperature_and_ghost(self):
        self.lua.execute('''
            TheWorld.state.cycles=50; TheWorld.state.isnight=true; TheWorld.state.isday=false
            a=player("loaded",function(p)
                p.components.inventory.itemslots[1]=item(p,"ttk_lingshi3",17)
                p.components.inventory.overflow={slots={item(p,"ttk_lingshi3",23)}}
                p.components.temperature.current=80
            end)
            assert(progress(a,"collection_lingshi3")==40,"post-load ownership must count actual contents")
            assert(progress(a,"survive_hundred_days")==0 and progress(a,"survive_autumn")==0)
            world("cycles",50); world("isday",true); temp(a,20)
            assert(progress(a,"survive_hundred_days")==0 and progress(a,"survive_night")==0 and progress(a,"survive_heat")==0)
            world("cycles",51); world("isnight",false); world("isday",false); world("isnight",true); world("isday",true)
            temp(a,80); temp(a,20)
            assert(progress(a,"survive_hundred_days")==1 and progress(a,"survive_night")==1 and progress(a,"survive_heat")==1)
            b=player("ghost",function(p) p.tags.playerghost=true; p.dead=true end)
            b.tags.playerghost=nil; b.dead=false; b:PushEvent("ms_respawnedfromghost")
            assert(progress(b,"survive_revive")==1,"loaded ghost must use real respawn receipt")
            b:PushEvent("ms_respawnedfromghost"); assert(progress(b,"survive_revive")==1)
        ''')

    def test_every_new_component_route_is_master_only(self):
        self.lua.execute('''
            a=player("a"); TheWorld.ismastersim=false
            local seed=entity("carrot_seeds"); local c=Plantable(seed); c.plant="farm_plant_carrot"
            local old=c.Plant; hooks.farmplantable(c); assert(c.Plant==old)
            local soil=entity("soil"); soil.tags.soil=true; c:Plant(soil,a)
            assert(progress(a,"farming_plant_carrot")==0)
            local p=entity("cookpot"); local s=Stewer(p); old=s.StartCooking
            hooks.stewer(s); assert(s.StartCooking==old)
            assert(progress(a,"labor_cook_meals")==0)
            local i=item(a,"ttk_lingshi4",100); a.components.inventory.itemslots[1]=i
            a:PushEvent("itemget",{item=i}); a:flush(); assert(progress(a,"collection_lingshi4")==0)
            a:PushEvent("tilling"); assert(progress(a,"farming_till_soil")==0)
        ''')

    def test_late_ghost_load_and_overflow_loss_receipts(self):
        self.lua.execute('''
            a=player("loaded",nil,true); a.tags.playerghost=true; a.dead=true; a:flush()
            a.tags.playerghost=nil; a.dead=false; a:PushEvent("ms_respawnedfromghost")
            assert(progress(a,"survive_revive")==1,"ghost restoration occurs after player postinit")
            local bag=item(a,"backpack",1); bag.components.container={inst=bag,slots={}}
            a.components.inventory.overflow=bag.components.container
            if hooks.container then hooks.container(bag.components.container) end
            -- An overflow receipt schedules observation of the committed slots.
            bag.components.container.slots[1]=item(a,"ttk_lingshi4",9)
            bag:PushEvent("itemget",{item=bag.components.container.slots[1]}); a:flush()
            assert(progress(a,"collection_lingshi4")==9,"overflow receipt must observe its owner's inventory")
            bag.components.container.slots={}; bag:PushEvent("itemlose")
            assert(a._ttk_ownership_pending,"overflow loss must schedule recomputation")
            a:flush(); assert(progress(a,"collection_lingshi4")==9)
        ''')

    def test_cook_save_and_harvest_before_deferred_receipt(self):
        self.lua.execute('''
            a=player("chef"); b=player("harvester")
            local p=entity("cookpot"); p.components.container={slots={},Close=function() end,DestroyContents=function() end}
            local s=Stewer(p); p.components.stewer=s; hooks.stewer(s)
            s:StartCooking(a); local first=s.task
            s:StartCooking(b); assert(s.task==first,"native rejects a second start")
            first.run(); local saved=s:OnSave()
            assert(progress(a,"labor_cook_meals")==1 and saved.ttk_achievement_cook_awarded)
            p:flush(); assert(progress(a,"labor_cook_meals")==1 and progress(b,"labor_cook_meals")==0)
            s.product=nil; s.done=nil; s.targettime=nil; s:StartCooking(a); s:StopCooking(); p:flush()
            assert(progress(a,"labor_cook_meals")==1,"canceled cooking must not count")
            s:StartCooking(a); s.task.run()
            -- Native Harvest gives the item to the harvester, who is not the chef.
            b.components.inventory.GiveItem=function() end
            s:Harvest(b); p:flush()
            assert(progress(a,"labor_cook_meals")==2 and progress(b,"labor_cook_meals")==0)
        ''')


class GuildDungeonReachability(unittest.TestCase):
    def setUp(self):
        ActivityReachability.setUp(self)
        self.lua.execute('''
            TheWorld.ismastershard=true; TheWorld.components={}
            function TheWorld:HasTag(tag) return tag == "forest" and not self.cave end
            TUNING.TOTAL_DAY_TIME=480
            local basic_entity=entity
            function entity(prefab)
                local e=basic_entity(prefab)
                e.Transform.GetWorldPosition=function() return 0,0,0 end
                e.DoPeriodicTask=e.DoTaskInTime
                e.entity={SetParent=function() end}
                return e
            end
            function SpawnPrefab(prefab)
                if prefab=="minotaurchest" then return nil end
                local e=entity(prefab)
                e.components.inventoryitem={owner=nil}
                e.SetDungeonProduct=function() return true end
                return e
            end
            TheNet={Announce=function() end}
            exit_gate=entity("dungeon_exit")
            TheSim={FindFirstEntityWithTag=function(_,tag) if tag=="dungeon_exit" then return exit_gate end end}
            function inventory(p)
                local inv=p.components.inventory; inv.inst=p; inv.maxslots=40
                function inv:GetItemInSlot(slot) return self.itemslots[slot] end
                function inv:CanTakeItemInSlot() return true end
                function inv:CanAcceptCount(_,count) return count end
                function inv:GiveItem(item)
                    if self.fail then return nil end
                    for slot=1,self.maxslots do if not self.itemslots[slot] then
                        self.itemslots[slot]=item; item.components.inventoryitem.owner=p; return item
                    end end
                end
                function inv:RemoveItem(item)
                    for slot,v in pairs(self.itemslots) do if v==item then self.itemslots[slot]=nil end end
                    item.components.inventoryitem.owner=nil; return item
                end
                function inv:FindItems() local r={} for _,v in pairs(self.itemslots) do table.insert(r,v) end return r end
                return inv
            end
            function rank(p)
                local r=require("components/hh_rank")(p); p.components.hh_rank=r; inventory(p); return r
            end
            function manager()
                local w=entity("forest"); w.ismastersim=true; w.ismastershard=true; w.tags.forest=true
                local m=require("components/dungeon_manager")(w)
                m.state="READY"; m.run_epoch=1; m.active_gate=entity("dungeon_gate"); m.active_gate.tags.dungeon_gate=true
                TheWorld.components.dungeon_manager=m; return m
            end
            function counts(p,event)
                local result={n=0}
                p:ListenForEvent(event,function(_,data) result.n=result.n+1; result.data=data end)
                return result
            end
        ''')

    def test_entry_reentry_clear_snapshot_and_duplicate_final_death(self):
        self.lua.execute('''
            local m=manager(); local a=player("a"); local b=player("b"); local nearby=player("nearby")
            local entries=counts(a,"hh_dungeon_entered"); local clears=counts(a,"hh_dungeon_completed")
            assert(m:EnterDungeon(a)); assert(not m:EnterDungeon(a)); assert(m:EnterDungeon(b))
            m.players_in_dungeon[a]=nil; a:RemoveTag("in_solo_dungeon"); assert(m:EnterDungeon(a))
            assert(entries.n==1,"entry must emit once per actor per run")
            assert(progress(a,"dungeon_guild_enter_dungeon")==1 and progress(nearby,"dungeon_guild_enter_dungeon")==0)
            local stale=entity("hh_igris_dungeon"); stale.hh_dungeon_run_epoch=0
            m:OnMonsterDeath(stale); assert(not m.is_cleared)
            m.current_wave=m.max_waves
            local boss=entity("hh_beru_dungeon"); boss.hh_dungeon_run_epoch=1; m.monsters={boss}
            -- Removing B during A's receipt must not change the committed snapshot.
            a:ListenForEvent("hh_dungeon_completed",function() assert(m.is_cleared); m.players_in_dungeon[b]=nil end)
            m:OnMonsterDeath(boss); m:OnMonsterDeath(boss)
            assert(clears.n==1,"duplicate death must not replay final clear")
            assert(progress(a,"dungeon_guild_clear_dungeon")==1 and progress(b,"dungeon_guild_clear_dungeon")==1)
            assert(progress(nearby,"dungeon_guild_clear_dungeon")==0)
            m.run_epoch=2; m.is_cleared=false; m.state="READY"; m.current_wave=0; m.players_in_dungeon={}
            assert(m:EnterDungeon(a)); assert(entries.n==2)
        ''')

    def test_dungeon_kills_require_current_member_and_owned_run(self):
        self.lua.execute('''
            local m=manager(); local a=player("member"); local b=player("nearby"); assert(m:EnterDungeon(a))
            local function kill(p,prefab,epoch,owner)
                local v=entity(prefab); v.components.health={IsDead=function() return true end}
                v.hh_dungeon_manager=owner; v.hh_dungeon_run_epoch=epoch
                p:PushEvent("killed",{victim=v}); p:PushEvent("killed",{victim=v})
            end
            kill(b,"hh_igris_dungeon",1,m); kill(a,"hh_igris_dungeon",0,m); kill(a,"hh_igris_dungeon",1,{})
            assert(progress(a,"dungeon_guild_defeat_igris")==0 and progress(b,"dungeon_guild_defeat_igris")==0)
            kill(a,"hh_igris_dungeon",1,m); kill(a,"hh_beru_dungeon",1,m)
            assert(progress(a,"dungeon_guild_defeat_igris")==1 and progress(a,"dungeon_guild_defeat_beru")==1)
        ''')

    def test_coin_add_spend_load_and_dungeon_purchase_commit(self):
        self.lua.execute('''
            local a=player("a"); local b=player("b"); local inv=inventory(a)
            local wallet=require("components/hh_dungeon_coin")(a); a.components.hh_dungeon_coin=wallet
            wallet:OnLoad({coins=100000}); wallet:Spend(10); wallet:Add(0)
            assert(progress(a,"dungeon_guild_earn_dungeon_coin")==0)
            wallet:Add(40,"reward"); assert(progress(a,"dungeon_guild_earn_dungeon_coin")==40)
            local shop=require("components/hh_dungeon_shop")(TheWorld); shop:EnsureCycle()
            local id=shop.active[1]; local before=shop.stock[id]; local coins=wallet.coins
            local receipts=counts(a,"hh_dungeon_shop_purchased")
            a.tags.playerghost=true; assert(not shop:Purchase(a,id)); a.tags.playerghost=nil
            a.tags.hh_dungeon_transition=true; assert(not shop:Purchase(a,id)); a.tags.hh_dungeon_transition=nil
            assert(not shop:Purchase(a,"invalid")); inv.fail=true; assert(not shop:Purchase(a,id)); inv.fail=false
            local spend=wallet.Spend; wallet.Spend=function() return false end
            assert(not shop:Purchase(a,id)); wallet.Spend=spend
            assert(next(inv.itemslots)==nil and receipts.n==0 and shop.stock[id]==before and wallet.coins==coins)
            a:ListenForEvent("hh_dungeon_shop_purchased",function() assert(shop.stock[id]==before-1 and wallet.coins<coins) end)
            assert(shop:Purchase(a,id)); assert(receipts.n==1)
            assert(progress(a,"dungeon_guild_buy_dungeon_item")==1 and progress(a,"gacha_shop_shop_purchase")==1)
            assert(progress(b,"gacha_shop_shop_purchase")==0 and progress(a,"dungeon_guild_earn_dungeon_coin")==40)
        ''')

    def test_guild_quest_and_exam_commit_not_auto_promotion(self):
        self.lua.execute('''
            local a=player("a"); local r=rank(a)
            local q=require("components/hh_guild_quest")(a); a.components.hh_guild_quest=q
            q:EnsureOffers(); local id=q.offers[1]; assert(id)
            assert(not q:StartQuest(-99)); q:CompleteQuest()
            assert(progress(a,"dungeon_guild_accept_guild_quest")==0 and progress(a,"dungeon_guild_complete_guild_quest")==0)
            assert(q:StartQuest(id)); assert(progress(a,"dungeon_guild_accept_guild_quest")==1)
            q:AddProgress(q.target); q:CompleteQuest(); assert(progress(a,"dungeon_guild_complete_guild_quest")==1)
            assert(not r:ClaimExam()); r.rank=6; a.components.hh_leveling={level=70}; assert(r:ReconcileLevelPromotion())
            assert(r.rank==7 and progress(a,"dungeon_guild_pass_rank_exam")==0)
            a.components.hh_leveling.level=100; assert(r:ReconcileLevelPromotion()); assert(r.rank==8)
            assert(progress(a,"dungeon_guild_pass_rank_exam")==0)
            r.rank=1; r.exam_id=1; r.exam_status=3; assert(r:ClaimExam())
            assert(progress(a,"dungeon_guild_pass_rank_exam")==1)
        ''')

    def test_guild_staff_validation_and_shop_credit_rollback(self):
        self.lua.execute('''
            local a=player("a"); local r=rank(a); local ui=false
            a.hh_guild_ui_open={set=function(_,v) ui=v end}
            assert(not r:OpenInterface(nil)); assert(not ui and progress(a,"dungeon_guild_meet_guild")==0)
            local staff=entity("guild_staff"); staff.tags.hh_guild_employee=true
            staff.BeginGuildInteraction=function() end
            staff.valid=false; assert(not r:OpenInterface(staff)); staff.valid=true
            staff.tags.hh_guild_employee=nil; assert(not r:OpenInterface(staff)); staff.tags.hh_guild_employee=true
            a.tags.playerghost=true; assert(not r:OpenInterface(staff)); a.tags.playerghost=nil
            TheWorld.state.phase="night"; assert(not r:OpenInterface(staff)); TheWorld.state.phase="day"
            assert(r:OpenInterface(staff)); assert(ui and progress(a,"dungeon_guild_meet_guild")==1)
            local shop=require("components/hh_guild_shop")(a); a.components.hh_guild_shop=shop; r.credit=100000; r.rank=8
            local id=shop.active_products[1]; local before=shop.stock[id]; local inv=a.components.inventory
            local receipts=counts(a,"hh_guild_shop_purchased")
            inv.fail=true; assert(not shop:Purchase(id,1)); inv.fail=false
            local spend=r.SpendCredit; r.SpendCredit=function() return false end
            assert(not shop:Purchase(id,1)); r.SpendCredit=spend
            assert(next(inv.itemslots)==nil,"failed credit debit must roll delivery back")
            assert(receipts.n==0 and shop.stock[id]==before and r.credit==100000)
            -- The delivery transaction must also rollback a debit callback exception.
            r.SpendCredit=function(s) s.credit=s.credit-1; error("failed debit sync") end
            assert(not shop:Purchase(id,1)); r.SpendCredit=spend
            assert(next(inv.itemslots)==nil and receipts.n==0 and shop.stock[id]==before and r.credit==100000)
            a:ListenForEvent("hh_guild_shop_purchased",function() assert(shop.stock[id]==before-1 and r.credit<100000) end)
            assert(shop:Purchase(id,1)); assert(receipts.n==1)
            for _,id in ipairs({"dungeon_guild_spend_guild_credit","dungeon_guild_visit_guild_shop","gacha_shop_shop_discount"}) do
                assert(progress(a,id)==1,id)
            end
        ''')

    def test_component_methods_reject_non_surface_and_client_transactions(self):
        self.lua.execute('''
            local a=player("a"); local r=rank(a); r.rank=8; r.credit=100000
            local guild=require("components/hh_guild_shop")(a); local id=guild.active_products[1]
            local dungeon=require("components/hh_dungeon_shop")(TheWorld); dungeon:EnsureCycle()
            local wallet=require("components/hh_dungeon_coin")(a); a.components.hh_dungeon_coin=wallet; wallet.coins=100000
            local m=manager(); local w=m.inst
            for _,mode in ipairs({"client","cave","secondary"}) do
                TheWorld.ismastersim=mode~="client"; TheWorld.ismastershard=mode~="secondary"; TheWorld.cave=mode=="cave"
                w.ismastersim=TheWorld.ismastersim; w.ismastershard=TheWorld.ismastershard; w.tags.forest=not TheWorld.cave
                assert(not m:EnterDungeon(a)); assert(not guild:Purchase(id,1)); assert(not dungeon:Purchase(a,dungeon.active[1]))
                r.rank=1; r.exam_id=1; r.exam_status=3; assert(not r:ClaimExam())
                local q=require("components/hh_guild_quest")(a); a.components.hh_guild_quest=q
                q:EnsureOffers(); local quest=q.offers[1]; assert(q:StartQuest(quest)); q:AddProgress(q.target)
                assert(progress(a,"dungeon_guild_accept_guild_quest")==0 and progress(a,"dungeon_guild_complete_guild_quest")==0)
            end
            assert(next(a.components.inventory.itemslots)==nil and r.credit==100000 and wallet.coins==100000)
            assert(progress(a,"dungeon_guild_enter_dungeon")==0 and progress(a,"dungeon_guild_pass_rank_exam")==0)
        ''')

    def test_existing_dungeon_open_validation_and_surface_only_routes(self):
        # Execute the existing server validator/handler verbatim, without loading client UI.
        source=(MOD / "main/hh_dungeon_shop.lua").read_text(encoding="utf-8")
        block=source[source.index("local function CanOpen(player)"):source.index('AddModRPCHandler("hh_rpc", "hh_dungeon_shop_buy"')]
        self.lua.execute('function AddModRPCHandler(_,_,fn) open_shop=fn end')
        self.lua.execute(block)
        self.lua.execute('''
            local a=player("a"); local b=player("b")
            TheWorld.components.hh_dungeon_shop=require("components/hh_dungeon_shop")(TheWorld)
            a.tags.playerghost=true; open_shop(a); a.tags.playerghost=nil
            a.tags.hh_dungeon_transition=true; open_shop(a); a.tags.hh_dungeon_transition=nil
            TheWorld.cave=true; open_shop(a); TheWorld.cave=false
            assert(progress(a,"gacha_shop_shop_visit")==0)
            open_shop(a); assert(progress(a,"gacha_shop_shop_visit")==1 and progress(b,"gacha_shop_shop_visit")==0)
            TheWorld.ismastershard=false
            local wallet=require("components/hh_dungeon_coin")(b); wallet:Add(100,"reward"); open_shop(b)
            assert(progress(b,"dungeon_guild_earn_dungeon_coin")==0 and progress(b,"gacha_shop_shop_visit")==0)
            TheWorld.ismastershard=true; TheWorld.ismastersim=false; wallet:Add(100,"reward")
            assert(progress(b,"dungeon_guild_earn_dungeon_coin")==0)
        ''')


if __name__ == "__main__":
    unittest.main()
