# job "py" op (read-only, nothing saved): actors of the raid level and what code carriers it offers (skinned characters, accessories...)
lvl = ARGS.get("level", "/Game/Maps/Chekpoint/LightCity_Defense_01")
unreal.EditorLoadingAndSavingUtils.load_map(lvl)
world = unreal.EditorLevelLibrary.get_editor_world()
acts = unreal.EditorLevelLibrary.get_all_level_actors()
cls_count = {}
skinned = []
for a in acts:
    c = a.get_class().get_name()
    cls_count[c] = cls_count.get(c, 0) + 1
    for comp in a.get_components_by_class(unreal.SkeletalMeshComponent):
        try:
            m = comp.get_editor_property("skeletal_mesh_asset")
        except Exception:
            m = None
        abp = comp.get_editor_property("anim_class")
        skinned.append([a.get_name(), c, m.get_path_name() if m else None, abp.get_path_name() if abp else None])
REPORT["classes"] = sorted(cls_count.items(), key=lambda kv: -kv[1])[:80]
REPORT["skinned"] = skinned[:80]
REPORT["world_settings_gamemode"] = str(world.get_world_settings().get_editor_property("default_game_mode")) if world else None
# defence pawn/soldier/intro classes: default skin-related properties
for cn in ("QzDefenseSoldier", "QzDefenseCharacterIntro", "QzDefenseDrone", "QzDefenseAC"):
    c = getattr(unreal, cn, None)
    if c:
        cdo = unreal.get_default_object(c)
        REPORT.setdefault("cdo_props", {})[cn] = [p for p in dir(cdo) if any(k in p.lower() for k in ("skin", "mesh", "npc_tag", "profile", "anim"))][:40]
