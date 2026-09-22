local prefabs = {}

table.insert(prefabs, CreatePrefabSkin("eva_purple", {
    base_prefab = "eva",
    build_name_override = "eva_purple",
    type = "base",
    rarity = "Loyal",
    skip_item_gen = true,
    skip_giftable_gen = true,
    skin_tags = {"BASE", "EVA", "CHARACTER"},
    skins = {
        normal_skin = "eva_purple",
        ghost_skin = "ghost_eva_build",
    },
    share_bigportrait_name = "eva",
    assets = {
        Asset("ANIM", "anim/eva_purple.zip"),
        Asset("ANIM", "anim/ghost_eva_build.zip"),
    },
}))

return unpack(prefabs)
