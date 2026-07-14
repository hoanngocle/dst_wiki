local exporter = require("exporter")
local started = false

local function RunOnce(world)
    if started or world == nil or not world.ismastersim then
        return
    end
    started = true
    exporter.Run()
end

AddPrefabPostInit("world", function(inst)
    RunOnce(inst)
end)

AddSimPostInit(function()
    if TheWorld ~= nil and TheWorld.ismastersim then
        TheWorld:DoTaskInTime(0, function()
            RunOnce(TheWorld)
        end)
    end
end)
