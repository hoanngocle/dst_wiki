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
            action("DEPLOY",nil,1,true,a,entity("sapling")):Do()
            action("FERTILIZE",entity("campfire"),1,true,a,manure):Do()
            assert(progress(a,"farming_fertilize_plants")==0)
            action("DEPLOY",nil,1,true,a,manure):Do()
            action("FERTILIZE",farm,0,true,a,manure):Do()
            assert(progress(a,"farming_fertilize_plants")==2)
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


if __name__ == "__main__":
    unittest.main()
