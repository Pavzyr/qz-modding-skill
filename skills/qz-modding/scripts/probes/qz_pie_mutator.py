"""PIE probe (full editor, -ExecCmds="py <this>"): is a mod's UGCMutator subclass discovered / registered / instantiated?
Writes <Saved>/ModSchema/deep/pie_mutator.json. Changes no assets."""
import json, os, time, traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep", "pie_mutator.json")
T0 = time.time()
res = {"steps": []}
st = {"phase": "boot", "t": time.time(), "h": None}
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
MUT = "/ZZMutatorProbe/BP_ZZ_Mutator"


def snap(tag, world):
    d = {"tag": tag, "t": round(time.time() - T0, 1)}
    try:
        cls = st.get("cls") or unreal.EditorAssetLibrary.load_blueprint_class(MUT)
        st["cls"] = cls
        d["class"] = str(cls)
        gi = unreal.GameplayStatics.get_game_instance(world) if world else None
        d["game_instance"] = str(gi)
        subs = list(unreal.ObjectIterator(unreal.UGCMutatorSubsystem))
        d["all_subsystems"] = [x.get_path_name() for x in subs]
        sub = None
        for x in subs:
            if gi and x.get_outer() == gi:
                sub = x
        d["subsystem"] = str(sub)
        if sub:
            for use_cache in (True, False):
                try:
                    d["class_list_%s" % use_cache] = [str(c.get_name()) for c in (sub.get_mutator_class_list(use_cache) or [])]
                except Exception as e:
                    d["class_list_%s" % use_cache] = "err %s" % e
            try:
                d["is_registered"] = sub.is_registered(cls)
            except Exception as e:
                d["is_registered"] = "err %s" % e
        d["instances"] = [o.get_path_name() for o in unreal.ObjectIterator(unreal.UGCMutator)][:20]
    except Exception:
        d["err"] = traceback.format_exc()[-600:]
    res["steps"].append(d)
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    unreal.log("[qz_pie_mutator] %s" % d)


def finish(r):
    res["steps"].append({"finish": r})
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
            snap("editor", UES.get_editor_world())
            LES.editor_request_begin_play(); st.update(phase="wait", t=now)
        elif st["phase"] == "wait":
            w = UES.get_game_world()
            if w and el > 15:
                snap("pie+15s", w); st.update(phase="late", t=now)
            elif el > 90:
                finish("no pie")
        elif st["phase"] == "late" and el > 15:
            snap("pie+30s", UES.get_game_world())
            finish("done")
    except Exception:
        res["steps"].append({"err": traceback.format_exc()[-800:]})
        finish("exception")


st["h"] = unreal.register_slate_post_tick_callback(tick)
