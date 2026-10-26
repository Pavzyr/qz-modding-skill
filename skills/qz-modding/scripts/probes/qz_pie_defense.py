"""PIE probe of the raid level: who spawns there at runtime (carrier candidates for NoRaid) and what EndDefense(false) does.
Run: UnrealEditor.exe QZSim.uproject /Game/Maps/Chekpoint/LightCity_Defense_01 -Installed -ExecCmds="py <this>" ; writes Saved/ModSchema/deep/pie_defense.json"""
import json, os, time, traceback
import unreal
OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep", "pie_defense.json")
res = {"events": [], "snaps": []}
st = {"phase": "boot", "t": time.time(), "h": None, "n": 0, "ended": False}
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
T0 = time.time()


def ev(m):
    res["events"].append([round(time.time() - T0, 1), m])


def finish(r):
    res["finish"] = r
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    try:
        if LES.is_in_play_in_editor():
            LES.editor_request_end_play()
    except Exception:
        pass
    unreal.unregister_slate_post_tick_callback(st["h"])
    unreal.SystemLibrary.quit_editor()


def snap(w, tag):
    cls = {}
    sk = []
    for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
        c = a.get_class().get_name(); cls[c] = cls.get(c, 0) + 1
        if len(sk) < 40:
            for comp in a.get_components_by_class(unreal.SkeletalMeshComponent):
                m = comp.get_editor_property("skeletal_mesh_asset")
                pp = None
                try:
                    pp = comp.get_post_process_instance()
                except Exception:
                    pass
                sk.append([c, m.get_path_name() if m else None, str(comp.get_editor_property("anim_class")), str(pp.get_class().get_name()) if pp else None])
    res["snaps"].append({"t": round(time.time() - T0, 1), "tag": tag, "world": w.get_name(), "classes": sorted(cls.items(), key=lambda kv: -kv[1])[:60], "skinned": sk})


def tick(dt):
    try:
        now = time.time(); el = now - st["t"]
        if st["phase"] == "boot" and el > 30:
            ev("editor world: %s" % UES.get_editor_world().get_name())
            # the raid map is the startup map of this run (-ini:Engine:[/Script/EngineSettings.GameMapsSettings]:EditorStartupMap=...);
            # loading it from a script crashes the editor (flush async loading during postload)
            LES.editor_request_begin_play(); st.update(phase="run", t=now); ev("PIE started")
        elif st["phase"] == "run" and el > 1.0:
            st["t"] = now; st["n"] += 1
            w = UES.get_game_world()
            if not w:
                return
            if st["n"] in (10, 40):
                snap(w, "n%d" % st["n"])
            if st["n"] == 45 and not st["ended"]:
                dm = unreal.QzDefenseManager.get_defense_manager(w)
                ev("defense manager: %s" % (dm.get_name() if dm else None))
                if dm:
                    dm.end_defense(False); st["ended"] = True; ev("end_defense(False) called")
            if st["n"] in (50, 60):
                snap(w, "after_end_n%d" % st["n"])
                vp = [x.get_class().get_name() for x in unreal.WidgetLibrary.get_all_widgets_of_class(w, unreal.UserWidget, True)]
                ev("top widgets: %s" % vp[:30])
            if st["n"] > 62:
                finish("done")
    except Exception:
        res["err"] = traceback.format_exc()[-1200:]
        finish("exception")


st["h"] = unreal.register_slate_post_tick_callback(tick)
