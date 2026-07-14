local Exporter = {}

local SENTINEL = "DST_WIKI_EXTRACT_COMPLETE"

local function JsonEscape(value)
    return value:gsub('[%z\1-\31\\"]', function(character)
        if character == '"' then
            return '\\"'
        elseif character == "\\" then
            return "\\\\"
        elseif character == "\b" then
            return "\\b"
        elseif character == "\f" then
            return "\\f"
        elseif character == "\n" then
            return "\\n"
        elseif character == "\r" then
            return "\\r"
        elseif character == "\t" then
            return "\\t"
        end
        return string.format("\\u%04x", string.byte(character))
    end)
end

local function IsArray(value)
    local count = 0
    local highest = 0
    for key in pairs(value) do
        if type(key) ~= "number" or key < 1 or key ~= math.floor(key) then
            return false, 0
        end
        count = count + 1
        highest = math.max(highest, key)
    end
    return count == highest, highest
end

local function JsonEncode(value, seen)
    local value_type = type(value)
    if value == nil then
        return "null"
    elseif value_type == "boolean" then
        return value and "true" or "false"
    elseif value_type == "number" then
        if value ~= value or value == math.huge or value == -math.huge then
            return "null"
        end
        return string.format("%.17g", value)
    elseif value_type == "string" then
        return '"' .. JsonEscape(value) .. '"'
    elseif value_type ~= "table" then
        error("cannot encode JSON value of type " .. value_type)
    end

    seen = seen or {}
    if seen[value] then
        error("cannot encode cyclic table")
    end
    seen[value] = true
    local output = {}
    local array, length = IsArray(value)
    if array then
        for index = 1, length do
            output[index] = JsonEncode(value[index], seen)
        end
        seen[value] = nil
        return "[" .. table.concat(output, ",") .. "]"
    end

    local keys = {}
    for key in pairs(value) do
        if type(key) ~= "string" then
            error("JSON object keys must be strings")
        end
        table.insert(keys, key)
    end
    table.sort(keys)
    for _, key in ipairs(keys) do
        table.insert(output, JsonEncode(key, seen) .. ":" .. JsonEncode(value[key], seen))
    end
    seen[value] = nil
    return "{" .. table.concat(output, ",") .. "}"
end

local function Primitive(value)
    local value_type = type(value)
    if value_type == "number" then
        return value == value and value ~= math.huge and value ~= -math.huge and value or nil
    end
    if value_type == "string" or value_type == "boolean" then
        return value
    end
    return nil
end

local function SanitizeError(value)
    local result = tostring(value)
    result = result:gsub("dst_wiki_probe_[0-9a-f]+", "dst_wiki_probe")
    result = result:gsub("dst_wiki_core_[0-9a-f]+", "dst_wiki_core")
    return result
end

local function TablesEqual(left, right)
    if type(left) ~= type(right) then
        return false
    elseif type(left) ~= "table" then
        return left == right
    end
    for key, value in pairs(left) do
        if not TablesEqual(value, right[key]) then
            return false
        end
    end
    for key in pairs(right) do
        if left[key] == nil then
            return false
        end
    end
    return true
end

local function TechName(level)
    local names = {}
    for name in pairs(TECH or {}) do
        table.insert(names, name)
    end
    table.sort(names)
    for _, name in ipairs(names) do
        if TablesEqual(level, TECH[name]) then
            return name
        end
    end
    local levels = {}
    for key, value in pairs(level or {}) do
        if type(value) == "number" and value ~= 0 then
            table.insert(levels, tostring(key) .. "=" .. tostring(value))
        end
    end
    table.sort(levels)
    return table.concat(levels, ",")
end

local function SortedPrimitiveList(value)
    local result = {}
    if Primitive(value) ~= nil then
        table.insert(result, value)
    elseif type(value) == "table" then
        for _, entry in pairs(value) do
            if Primitive(entry) ~= nil then
                table.insert(result, entry)
            end
        end
    end
    table.sort(result, function(left, right)
        return tostring(left) < tostring(right)
    end)
    return result
end

local function ModVersion()
    if KnownModIndex == nil then
        return "unknown"
    end
    local names = KnownModIndex:GetModsToLoad(true) or {}
    table.sort(names)
    for _, modname in ipairs(names) do
        local info = KnownModIndex:GetModInfo(modname) or {}
        local display_name = tostring(info.name or "")
        if display_name:find("Tu Tiên", 1, true) ~= nil then
            return tostring(info.version or "unknown")
        end
    end
    return "unknown"
end

local function RecipeIngredientRows(source, options)
    local rows = {}
    for index, ingredient in ipairs(source or {}) do
        local ingredient_type = string.lower(tostring(ingredient.type))
        rows[index] = {
            group = options.group,
            type = ingredient_type,
            amount = Primitive(ingredient.amount) or 0,
        }
        if options.has_prefab then
            rows[index].prefab = ingredient_type
        end
    end
    return rows
end

local function RecipeRows(prefab_ids)
    print("DST wiki runtime recipe scan begin")
    local rows = {}
    local names = {}
    for recipe_name, recipe in pairs(AllRecipes or {}) do
        local product = string.lower(tostring(recipe.product or recipe_name))
        if product:sub(1, 3) == "xd_" then
            prefab_ids[product] = true
            table.insert(names, recipe_name)
        end
    end
    table.sort(names)
    print("DST wiki runtime recipe scan matched " .. tostring(#names))
    for _, recipe_name in ipairs(names) do
        local recipe = AllRecipes[recipe_name]
        print("DST wiki runtime recipe begin " .. tostring(recipe_name))
        local ingredients = RecipeIngredientRows(recipe.ingredients, {
            group = "item",
            has_prefab = true,
        })
        local character_ingredients = RecipeIngredientRows(
            recipe.character_ingredients,
            { group = "character" }
        )
        local tech_ingredients = RecipeIngredientRows(
            recipe.tech_ingredients,
            { group = "tech" }
        )
        local builder_tags = {}
        for _, tag in ipairs({ recipe.builder_tag, recipe.no_builder_tag }) do
            if Primitive(tag) ~= nil then
                table.insert(builder_tags, tag)
            end
        end
        table.sort(builder_tags, function(left, right)
            return tostring(left) < tostring(right)
        end)
        print("DST wiki runtime recipe tech begin " .. tostring(recipe_name))
        local tech = TechName(recipe.level)
        print("DST wiki runtime recipe tech end " .. tostring(recipe_name))
        table.insert(rows, {
            product = string.lower(tostring(recipe.product or recipe_name)),
            ingredients = ingredients,
            character_ingredients = character_ingredients,
            tech_ingredients = tech_ingredients,
            tech = tech,
            filters = SortedPrimitiveList(recipe.filter),
            builder_tags = builder_tags,
            output_count = Primitive(recipe.numtogive) or 1,
        })
    end
    table.sort(rows, function(left, right)
        return left.product < right.product
    end)
    print("DST wiki runtime recipe scan end")
    return rows
end

local function AddStat(stats, key, value, unit)
    value = Primitive(value)
    if value ~= nil then
        table.insert(stats, { key = key, value = value, unit = unit })
    end
end

local function AddLoot(output, prefab, chance, count, conditions)
    if type(prefab) == "string" and prefab ~= "" then
        table.insert(output, {
            prefab = string.lower(prefab),
            chance = Primitive(chance) or 1,
            count = Primitive(count) or 1,
            conditions = conditions or {},
        })
    end
end

local function SortAcquisition(rows)
    table.sort(rows, function(left, right)
        if left.prefab ~= right.prefab then
            return left.prefab < right.prefab
        elseif left.chance ~= right.chance then
            return left.chance < right.chance
        end
        return left.count < right.count
    end)
end

local function InspectInstance(instance, prefab)
    local stats = {}
    local loot = {}
    local harvest = {}
    local relations = {}
    local components = instance.components or {}

    local weapon = components.weapon
    if weapon ~= nil then
        AddStat(stats, "damage", weapon.damage, "hp")
        AddStat(stats, "attack_range", weapon.attackrange, "tiles")
    end
    local armor = components.armor
    if armor ~= nil then
        AddStat(stats, "armor_durability", armor.maxcondition, "hp")
        AddStat(stats, "damage_absorption", armor.absorb_percent, "ratio")
    end
    local finiteuses = components.finiteuses
    if finiteuses ~= nil then
        AddStat(stats, "uses", finiteuses.total, "uses")
    end
    local edible = components.edible
    if edible ~= nil then
        AddStat(stats, "health", edible.healthvalue, "hp")
        AddStat(stats, "hunger", edible.hungervalue, "hunger")
        AddStat(stats, "sanity", edible.sanityvalue, "sanity")
        AddStat(stats, "food_type", edible.foodtype, "category")
    end
    local perishable = components.perishable
    if perishable ~= nil then
        AddStat(stats, "perish_time", perishable.perishtime, "seconds")
        if type(perishable.onperishreplacement) == "string" then
            table.insert(relations, {
                relation = "transforms_to",
                target_prefab_id = string.lower(perishable.onperishreplacement),
            })
        end
    end
    local lootdropper = components.lootdropper
    if lootdropper ~= nil then
        for _, dropped in ipairs(lootdropper.loot or {}) do
            AddLoot(loot, dropped, 1, 1)
        end
        for _, dropped in ipairs(lootdropper.chanceloot or {}) do
            AddLoot(loot, dropped.prefab, dropped.chance, 1)
        end
        local shared = lootdropper.chanceloottable ~= nil
            and LootTables ~= nil
            and LootTables[lootdropper.chanceloottable]
            or nil
        for _, dropped in ipairs(shared or {}) do
            AddLoot(loot, dropped[1] or dropped.prefab, dropped[2] or dropped.chance, 1, {
                loot_table = lootdropper.chanceloottable,
            })
        end
        local total_weight = Primitive(lootdropper.totalrandomweight)
        for _, dropped in ipairs(lootdropper.randomloot or {}) do
            local chance = total_weight ~= nil and total_weight > 0
                and (Primitive(dropped.weight) or 0) / total_weight
                or 0
            AddLoot(loot, dropped.prefab, chance, lootdropper.numrandomloot or 1, {
                random_weight = Primitive(dropped.weight),
            })
        end
    end
    local pickable = components.pickable
    if pickable ~= nil and type(pickable.product) == "string" then
        AddLoot(harvest, pickable.product, 1, pickable.numtoharvest or 1, {
            regrowth_seconds = Primitive(pickable.baseregentime or pickable.regentime),
        })
    end
    local tradable = components.tradable
    if tradable ~= nil then
        AddStat(stats, "trade_gold_value", tradable.goldvalue, "value")
        AddStat(stats, "rock_tribute", tradable.rocktribute, "value")
        for _, target in ipairs(tradable.tradefor or {}) do
            if type(target) == "string" then
                table.insert(relations, {
                    relation = "trades_for",
                    target_prefab_id = string.lower(target),
                })
            end
        end
    end
    local stackable = components.stackable
    if stackable ~= nil then
        AddStat(stats, "stack_size", stackable.maxsize, "items")
    end
    local container = components.container
    if container ~= nil then
        AddStat(stats, "container_slots", container.numslots, "slots")
    end

    table.sort(stats, function(left, right)
        return left.key < right.key
    end)
    SortAcquisition(loot)
    SortAcquisition(harvest)
    table.sort(relations, function(left, right)
        local left_key = tostring(left.relation) .. ":" .. tostring(left.target_prefab_id)
        local right_key = tostring(right.relation) .. ":" .. tostring(right.target_prefab_id)
        return left_key < right_key
    end)

    local entity_type = "prefab"
    if components.inventoryitem ~= nil then
        entity_type = "inventory_item"
    elseif components.locomotor ~= nil or components.combat ~= nil then
        entity_type = "creature"
    elseif components.workable ~= nil or instance:HasTag("structure") then
        entity_type = "structure"
    end
    return {
        prefab = prefab,
        entity_type = entity_type,
        stats = stats,
        loot = loot,
        harvest = harvest,
        relations = relations,
    }
end

local function SpawnAndInspect(prefab)
    local instance = SpawnPrefab(prefab)
    if instance == nil then
        error("SpawnPrefab returned nil")
    end
    local ok, result = pcall(InspectInstance, instance, prefab)
    pcall(function()
        if instance:IsValid() then
            instance:Remove()
        end
    end)
    if not ok then
        error(result)
    end
    return result
end

function Exporter.Run()
    print("DST wiki runtime exporter begin")
    local prefab_ids = {}
    for name in pairs((STRINGS and STRINGS.NAMES) or {}) do
        if type(name) == "string" and name:sub(1, 3) == "XD_" then
            prefab_ids[string.lower(name)] = true
        end
    end
    print("DST wiki runtime names collected")
    local recipes = RecipeRows(prefab_ids)
    print("DST wiki runtime recipes collected")
    local ids = {}
    for prefab in pairs(prefab_ids) do
        table.insert(ids, prefab)
    end
    table.sort(ids)

    local prefabs = {}
    local errors = {}
    for _, prefab in ipairs(ids) do
        print("DST wiki runtime inspecting " .. prefab)
        local ok, result = pcall(SpawnAndInspect, prefab)
        if ok then
            table.insert(prefabs, result)
        else
            table.insert(errors, {
                code = "prefab_inspection_failed",
                prefab = prefab,
                detail = SanitizeError(result),
            })
        end
    end
    local payload = {
        schema_version = 1,
        mod_version = ModVersion(),
        recipes = recipes,
        prefabs = prefabs,
        errors = errors,
    }
    local ok, encoded = pcall(JsonEncode, payload)
    if not ok then
        print("DST wiki runtime JSON encoding failed: " .. tostring(encoded))
        return
    end
    TheSim:SetPersistentString("runtime.json", encoded, false, function(success)
        if success then
            print(SENTINEL)
        else
            print("DST wiki runtime save failed")
        end
    end)
end

return Exporter
