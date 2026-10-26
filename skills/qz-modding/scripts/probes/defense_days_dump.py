# job "py" op (read-only): which day assets start a raid (activate_defence) and where the raid happens
AR = unreal.AssetRegistryHelpers.get_asset_registry()
days = []
flt = unreal.ARFilter(class_paths=[unreal.TopLevelAssetPath("/Script/QZSim", "QzNewDayData")], recursive_classes=True)
for ad in AR.get_assets(flt):
    a = ad.get_asset()
    try:
        act = a.get_editor_property("activate_defence")
        dg = a.get_editor_property("defence_generator_data")
        lvl = dg.get_editor_property("level")
        days.append({"day": str(ad.package_name), "activate_defence": act, "convoy": dg.get_editor_property("convoy"),
                     "level": str(lvl) if lvl else None, "spawner": str(dg.get_editor_property("zombie_spawner_soft"))[:120],
                     "quests": len(dg.get_editor_property("defense_quests"))})
    except Exception as e:
        days.append({"day": str(ad.package_name), "err": str(e)[:150]})
REPORT["days"] = days
mgrs = []
for c in ("QzDefenseManager", "QzGameFlowDefense", "QzGameModeDefense"):
    flt2 = unreal.ARFilter(class_paths=[unreal.TopLevelAssetPath("/Script/Engine", "Blueprint")], recursive_classes=True)
REPORT["note"] = "see days"
