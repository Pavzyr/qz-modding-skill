"""VisitorTalk PIE verification (full editor, -ExecCmds="py <this>"). Changes no assets.
PIE on startup map -> wait for manager -> put player in front of the visitor at inspection, look at him ->
check focus/hint -> inject IA_VT_Talk (Enter) -> check dialog + screenshot -> inject again -> closed -> quit.
Writes <Saved>/ModSchema/deep/vt_verify.json and screenshots in <Saved>/Screenshots."""
import json, os, time, traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep", "vt_verify.json")
T0 = time.time()
res = {"steps": [], "error": None}
st = {"phase": "boot", "t": time.time(), "h": None, "npc": None}
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)


def step(msg, **kw):
    kw["msg"] = msg
    kw["t"] = round(time.time() - T0, 1)
    res["steps"].append(kw)
    unreal.log("[vt_verify] %s %s" % (msg, {k: v for k, v in kw.items() if k not in ("msg", "t")}))
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)


def cls(path):
    try:
        return unreal.EditorAssetLibrary.load_blueprint_class(path)
    except Exception:
        return None


def mgr_state(world):
    c = cls("/VisitorTalk/BP_VT_Manager")
    ms = unreal.GameplayStatics.get_all_actors_of_class(world, c) if c else []
    d = {"managers": len(ms)}
    if ms:
        m = ms[0]
        for v in ("Initialized", "DialogOpen", "FocusedNPC"):
            try:
                x = m.get_editor_property(v)
                d[v] = x.get_name() if isinstance(x, unreal.Object) else x
            except Exception as e:
                d[v] = "err %s" % e
        for w in ("HintUI", "DialogUI"):
            try:
                ui = m.get_editor_property(w)
                d[w] = str(ui.get_visibility()) if ui else None
                d[w + "_text"] = str(ui.get_editor_property("Text_Main").get_text()) if ui else None
            except Exception as e:
                d[w] = "err %s" % e
    try:
        doc = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.QzDocCharacter)[0]
        mc = doc.get_component_by_class(unreal.SkeletalMeshComponent)
        d["doc_mesh"] = mc.get_skeletal_mesh_asset().get_path_name()
        pp = mc.get_post_process_instance()
        d["doc_post_process"] = pp.get_class().get_name() if pp else None
    except Exception as e:
        d["doc"] = "err %s" % e
    return d, (ms[0] if ms else None)


def inject(world):
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    sub = [s for s in unreal.ObjectIterator(unreal.EnhancedInputLocalPlayerSubsystem) if s.get_outer() == pc.get_local_player()][0]
    ia = unreal.load_asset("/VisitorTalk/Input/IA_VT_Talk")
    sub.inject_input_vector_for_action(ia, unreal.Vector(1, 0, 0), [], [])


def shot(name):
    try:
        unreal.AutomationLibrary.take_high_res_screenshot(1600, 900, name)
    except Exception as e:
        step("screenshot failed", err=str(e))


def finish(reason):
    step("finish: " + reason)
    try:
        if LES.is_in_play_in_editor():
            LES.editor_request_end_play()
    except Exception:
        pass
    try:
        unreal.unregister_slate_post_tick_callback(st["h"])
    except Exception:
        pass
    unreal.SystemLibrary.quit_editor()


def tick(dt):
    try:
        now = time.time()
        ph, el = st["phase"], now - st["t"]
        if now - T0 > 420:
            return finish("timeout")
        if ph == "boot" and el > 20:
            LES.editor_request_begin_play(); st.update(phase="wait_pie", t=now)
        elif ph == "wait_pie":
            if UES.get_game_world():
                st.update(phase="wait_mgr", t=now); step("pie started")
            elif el > 90:
                return finish("no PIE")
        elif ph == "wait_mgr":
            w = UES.get_game_world()
            d, m = mgr_state(w)
            if m and d.get("Initialized") is True:
                step("manager ready", **d); st.update(phase="aim", t=now)
            elif el > 60:
                step("manager NOT ready", **d); return finish("no manager")
        elif ph == "aim":
            w = UES.get_game_world()
            npcs = [n for n in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.QzNPCCharacter)
                    if "INSPECTION" in str(n.get_state()) and "IDLE" not in str(n.get_state())]
            if not npcs:
                if el > 60:
                    return finish("no visitor at inspection")
                return
            npc = npcs[0]; st["npc"] = npc
            pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
            pc = unreal.GameplayStatics.get_player_controller(w, 0)
            nl = npc.get_actor_location()
            fwd = npc.get_actor_forward_vector()
            pawn.set_actor_location(unreal.Vector(nl.x + fwd.x * 140, nl.y + fwd.y * 140, nl.z + 10), False, True)
            cam = unreal.GameplayStatics.get_player_camera_manager(w, 0).get_camera_location()
            rot = unreal.MathLibrary.find_look_at_rotation(cam, unreal.Vector(nl.x, nl.y, nl.z + 40))
            pc.set_control_rotation(rot)
            step("aimed at", npc=npc.get_name(), state=str(npc.get_state()))
            st.update(phase="check_hint", t=now)
        elif ph == "check_hint" and el > 1.5:
            w = UES.get_game_world()
            pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
            focus = pawn.get_actor_in_focus()
            d, m = mgr_state(w)
            step("hint check", focus=focus.get_name() if focus else None, **d)
            shot("vt_hint.png")
            inject(w); st.update(phase="check_dialog", t=now)
        elif ph == "check_dialog" and el > 1.0:
            w = UES.get_game_world()
            d, m = mgr_state(w)
            step("after Enter #1", **d)
            shot("vt_dialog.png")
            st.update(phase="close", t=now)
        elif ph == "close" and el > 1.5:
            inject(UES.get_game_world()); st.update(phase="check_closed", t=now)
        elif ph == "check_closed" and el > 1.0:
            d, m = mgr_state(UES.get_game_world())
            step("after Enter #2", **d)
            return finish("done")
    except Exception:
        res["error"] = traceback.format_exc()[-1500:]
        finish("exception")


st["h"] = unreal.register_slate_post_tick_callback(tick)
step("registered")
