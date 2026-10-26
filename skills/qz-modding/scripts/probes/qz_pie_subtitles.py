"""PIE probe: which subtitle widgets appear while characters speak, with their text/visibility. Writes pie_subtitles.json.
Run: UnrealEditor.exe QZSim.uproject -Installed -ExecCmds="py <abs path>" -unattended -nosplash"""
import json, os, time, traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep", "pie_subtitles.json")
T0 = time.time()
res = {"snaps": [], "seen": {}}
st = {"phase": "boot", "t": time.time(), "h": None, "n": 0}
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)


def text_of(w):
    out = {}
    for n in ("CommonRichTextBlock_47", "Text_Main"):
        try:
            tb = w.get_editor_property(n)
            if tb:
                out[n] = str(tb.get_text())
        except Exception:
            pass
    return out


def snap():
    d = {"t": round(time.time() - T0, 1), "w": []}
    for w in unreal.ObjectIterator(unreal.QzSubtitlesWidget):
        pn = w.get_path_name()
        if "/Engine/Transient" not in pn and "PIE" not in pn and ":" not in pn.split(".")[-1] and "Default__" in pn:
            continue
        try:
            e = {"cls": w.get_class().get_name(), "path": pn[-140:], "vis": str(w.get_visibility()), "in_vp": bool(w.is_in_viewport()),
                 "visible": bool(w.is_visible()), "opacity": w.get_render_opacity(), "text": text_of(w)}
            par = w.get_parent()
            e["parent"] = par.get_name() if par else None
            d["w"].append(e)
            key = e["cls"] + "|" + json.dumps(e["text"], ensure_ascii=False)
            if e["text"] and key not in res["seen"]:
                res["seen"][key] = d["t"]
        except Exception:
            d.setdefault("err", traceback.format_exc()[-300:])
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
            LES.editor_request_begin_play(); st.update(phase="run", t=now)
        elif st["phase"] == "run" and el > 1.0:
            st["t"] = now; st["n"] += 1
            if UES.get_game_world():
                snap()
            if st["n"] > 75:
                finish("done")
    except Exception:
        res["err"] = traceback.format_exc()[-800:]
        finish("exception")


st["h"] = unreal.register_slate_post_tick_callback(tick)
