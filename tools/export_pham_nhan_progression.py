"""Export integrated Lua catalogs. Requires lupa (Lua 5.1); no game runtime.

Run: python tools/export_pham_nhan_progression.py [--check]
Only the named data modules are evaluated, in a Lua environment without IO,
package loading, process access or Python interop. JSON has no timestamps.
"""
import argparse
import json
from pathlib import Path


def build_data(root: Path) -> dict:
    from lupa.lua51 import LuaRuntime, lua_type

    lua = LuaRuntime(unpack_returned_tuples=True, register_eval=False, register_builtins=False)
    evaluate = lua.eval("function(s,e) local f=assert(loadstring(s)); setfenv(f,e); return f() end")
    scripts = root / "mods/PhamNhanTuTien/scripts"
    sources = []

    def load(relative):
        sources.append("mods/PhamNhanTuTien/scripts/" + relative + ".lua")
        env = lua.eval("{assert=assert,error=error,type=type,pairs=pairs,ipairs=ipairs,tonumber=tonumber,tostring=tostring,math=math,string=string,table=table}")
        return evaluate((scripts / (relative + ".lua")).read_text(encoding="utf-8-sig"), env)

    def plain(value):
        if lua_type(value) != "table":
            return value
        keys = list(value.keys())
        if keys and set(keys) == set(range(1, len(keys) + 1)):
            return [plain(value[index]) for index in range(1, len(keys) + 1)]
        return {str(key): plain(value[key]) for key in sorted(keys, key=str)}

    achievements = plain(load("achievement/ttk_achievement_catalog").All())
    perks_catalog = load("achievement/ttk_perk_catalog")
    perks = plain(perks_catalog.All())
    for perk in perks:
        prices = [perks_catalog.PriceForLevel(level) for level in range(1, perk.get("max_level", 0) + 1)]
        perk["levelPrices"] = prices
        perk["maxCost"] = sum(prices) if prices else perk["price"]

    catalog = load("achievement/ttk_seasonal_catalog")
    rewards = load("achievement/ttk_seasonal_rewards")
    tasks = plain(catalog.All())
    seasons = []
    for season in ("spring", "summer", "autumn", "winter"):
        draw = plain(catalog.Draw(season, lua.eval("function(first,last) return first end")))
        kinds = [catalog.ById(slot["task_id"]).kind for slot in draw]
        milestones = []
        for completed in range(1, len(draw) + 1):
            bundle = rewards.GetBundle(season, completed)
            if bundle is not None:
                milestones.append({"completed": completed, "items": plain(bundle)})
        seasons.append({"id": season, "tasks": [row for row in tasks if row["season"] == season],
                        "draw": {kind: kinds.count(kind) for kind in ("once", "repeat")}, "milestones": milestones})

    alchemy = load("alchemy/ttk_alchemy_defs")
    ranks = load("guild/hh_rank_defs")
    return {
        "sources": sources,
        "achievements": achievements,
        "groups": sorted({row["group"] for row in achievements}),
        "perks": perks,
        "seasons": seasons,
        "furnace": plain(alchemy.furnace),
        "cultivation": plain(alchemy.cultivation),
        "buffs": [plain(alchemy.buffs[key]) for key in sorted(alchemy.buffs.keys())],
        "fasting": plain(alchemy.fasting),
        "ranks": [{"name": ranks.NAMES[index], "level": ranks.GetRequiredLevel(index)}
                  for index in range(1, len(ranks.NAMES) + 1)],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if the checked-in export is stale")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = root / "data/generated/pham-nhan-progression.json"
    serialized = json.dumps(build_data(root), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != serialized:
            raise SystemExit("Progression export is stale; run the exporter without --check")
        print("Progression export matches the canonical Lua catalogs")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(serialized, encoding="utf-8", newline="\n")
        print(output)


if __name__ == "__main__":
    main()
