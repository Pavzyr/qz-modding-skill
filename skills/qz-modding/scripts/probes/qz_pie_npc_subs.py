"""PIE probe: what checkpoint visitors say (3D subtitles WBP_NPCSubtitle in Qz3DSubtitleComponent) and when.
Every 0.5 s records changes: per visitor -> state, subtitle component visible, widget visible, CommonRichTextBlock_47 text.
Writes Saved/ModSchema/deep/pie_npc_subs.json. Run with -ExecCmds="py <abs path>" (full editor)."""
import json, os, time, traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep", "pie_npc_subs.json")
T0 = time.time()
res = {"changes": [], "info": {}}
st = {"phase": "boot", "t": time.time(), "h": None, "n": 0, "last": {}}
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)


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


def look(world):
    cur = {}
    for npc in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.QzNPCCharacter):
        d = {"state": str(npc.get_state()).split(".")[-1].split(":")[0]}
        comps = npc.get_components_by_class(unreal.Qz3DSubtitleComponent)
        if comps:
            c = comps[0]
            d["comp_vis"] = bool(c.is_visible())
            w = c.get_user_widget_object()
            if w:
                d["w_cls"] = w.get_class().get_name()
                d["w_vis"] = bool(w.is_visible())
                try:
                    d["text"] = str(w.get_editor_property("CommonRichTextBlock_47").get_text())[:200]
                except Exception as e:
                    d["text"] = "err %s" % e
        dl = npc.get_components_by_class(unreal.QzDialogueComponent)
        if dl:
            d["playing"] = bool(dl[0].is_playing())
            snd = dl[0].get_editor_property("sound")
            d["sound"] = snd.get_name() if snd else None
        cur[npc.get_name()] = d
    return cur


def tick(dt):
    try:
        now = time.time(); el = now - st["t"]
        if st["phase"] == "boot" and el > 20:
            LES.editor_request_begin_play(); st.update(phase="run", t=now)
        elif st["phase"] == "run" and el > 0.5:
            st["t"] = now; st["n"] += 1
            w = UES.get_game_world()
            if not w:
                return
            cur = look(w)
            for k, d in cur.items():
                if st["last"].get(k) != d:
                    res["changes"].append([round(now - T0, 1), k, d])
            st["last"] = cur
            if st["n"] % 20 == 0:
                json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            if st["n"] > 640:
                finish("done")
    except Exception:
        res["err"] = traceback.format_exc()[-800:]
        finish("exception")


st["h"] = unreal.register_slate_post_tick_callback(tick)
