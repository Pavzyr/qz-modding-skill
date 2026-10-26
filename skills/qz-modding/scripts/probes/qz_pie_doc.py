"""PIE probe: doctor actor - which mesh is applied (mod skin?), is the mesh's post-process AnimBP instantiated? Writes pie_doc.json."""
import json, os, time, traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep", "pie_doc.json")
T0 = time.time()
res = {"snaps": []}
st = {"phase": "boot", "t": time.time(), "h": None}
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)


def snap(tag):
    w = UES.get_game_world()
    d = {"tag": tag, "t": round(time.time() - T0, 1), "docs": []}
    try:
        cls = unreal.QzDocCharacter
        for a in unreal.GameplayStatics.get_all_actors_of_class(w, cls):
            e = {"actor": a.get_name(), "class": a.get_class().get_name()}
            try:
                e["mod_skin_tag"] = str(a.get_editor_property("mod_skin_tag"))
            except Exception as ex:
                e["mod_skin_tag"] = "err %s" % ex
            comps = []
            for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
                ce = {"name": c.get_name()}
                try:
                    m = c.get_skeletal_mesh_asset()
                    ce["mesh"] = m.get_path_name() if m else None
                except Exception as ex:
                    ce["mesh"] = "err %s" % ex
                for fn in ("get_post_process_instance", "get_anim_instance"):
                    try:
                        inst = getattr(c, fn)()
                        ce[fn] = inst.get_class().get_path_name() if inst else None
                    except Exception as ex:
                        ce[fn] = "err %s" % ex
                comps.append(ce)
            e["meshes"] = comps
            d["docs"].append(e)
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
        elif st["phase"] == "late" and el > 15:
            snap("pie+25s"); finish("done")
    except Exception:
        res["err"] = traceback.format_exc()[-800:]
        finish("exception")


st["h"] = unreal.register_slate_post_tick_callback(tick)
