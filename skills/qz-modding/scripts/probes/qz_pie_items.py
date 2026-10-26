"""PIE probe: after day start, which item actors exist, what is in the player's inventory/wheel (are mod tools granted? spawned?).
Writes <Saved>/ModSchema/deep/pie_items.json."""
import json, os, time, traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep", "pie_items.json")
T0 = time.time()
res = {"snaps": []}
st = {"phase": "boot", "t": time.time(), "h": None}
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)


def snap(tag):
    w = UES.get_game_world()
    d = {"tag": tag, "t": round(time.time() - T0, 1)}
    try:
        d["items_in_world"] = sorted("%s parent=%s hidden=%s" % (a.get_class().get_name(),
                                     a.get_attach_parent_actor().get_class().get_name() if a.get_attach_parent_actor() else None, a.is_hidden())
                                     for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.SItem))
        pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
        inv = pawn.get_component_by_class(unreal.SInventoryComponent)
        n = inv.get_size()
        d["inventory_size"] = n
        items = []
        for i in range(n):
            try:
                it = inv.get_item(i)
                items.append(it.get_path_name() if it else None)
            except Exception as e:
                items.append("err %s" % e)
        d["inventory"] = items
        wheel = pawn.get_component_by_class(unreal.SWheelComponent)
        d["wheel_items"] = [x.get_path_name() for x in wheel.get_editor_property("items")]
    except Exception:
        d["err"] = traceback.format_exc()[-800:]
    res["snaps"].append(d)
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def finish(r):
    res["finish"] = r
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    try:
        if LES.is_in_play_in_editor():
            LES.editor_request_end_play()
    except Exception:
        pass
    unreal.unregister_slate_post_tick_callback(st["h"])
    unreal.SystemLibrary.quit_editor()


def tick(dt):
    try:
        now = time.time(); el = now - st["t"]
        if st["phase"] == "boot" and el > 20:
            LES.editor_request_begin_play(); st.update(phase="wait", t=now)
        elif st["phase"] == "wait":
            if UES.get_game_world() and el > 10:
                snap("pie+10s"); st.update(phase="late", t=now)
            elif el > 90:
                finish("no pie")
        elif st["phase"] == "late" and el > 30:
            snap("pie+40s"); finish("done")
    except Exception:
        res["err"] = traceback.format_exc()[-800:]
        finish("exception")


st["h"] = unreal.register_slate_post_tick_callback(tick)
