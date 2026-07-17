"""Curated identifiers that look like prefabs but are only string/event labels."""


NON_ENTITY_PREFAB_IDS = frozenset(
    {
        # Death-state label for Tô Đát Kỷ. SpawnPrefab returns nil and the
        # mod has neither a prefab module nor an inventory asset for this id.
        "sudaji_killed",
    }
)


# Real prefabs that exist only as implementation details and are not standalone
# objects a player can obtain, craft, encounter, or inspect as wiki items.
NON_ITEM_PREFAB_IDS = frozenset(
    {
        # Six-slot UI container opened by Long Thái Tử's Long Châu storage spell.
        "xd_cwkj_container",
    }
)
