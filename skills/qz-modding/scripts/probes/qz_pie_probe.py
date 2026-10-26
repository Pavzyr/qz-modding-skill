"""PIE experiment (full editor, launched with -ExecCmds="py <this>"):
start Play-In-Editor on the startup map, sample visitor NPCs every few seconds, record their attached actors/state,
then stop PIE and quit the editor. Writes <Saved>/ModSchema/deep/pie_probe2.json. Changes no assets."""
import json, os, time, traceback
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep", "pie_probe2.json")
T0 = time.time()
MAX_PIE_SECONDS = float(os.environ.get("QZ_PIE_SECONDS", "150"))
res = {"events": [], "samples": [], "error": None}
state = {"phase": "wait_editor", "t": time.time(), "pie_t": None, "last_sample": 0, "handle": None}
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)


def ev(msg):
    res["events"].append("%.1fs %s" % (time.time() - T0, msg))
    unreal.log("[qz_pie_probe] " + msg)


def save():
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)


def sample(world):
    npcs = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.QzNPCCharacter)
    rows = []
    for n in npcs:
        try:
            att = [a.get_class().get_name() for a in n.get_attached_actors()]
        except Exception as e:
            att = ["err %s" % e]
        try:
            st = str(n.get_state())
        except Exception:
            st = "?"
        try:
            insp = n.is_inspecting()
        except Exception:
            insp = "?"
        rows.append({"name": n.get_name(), "class": n.get_class().get_name(), "state": st, "inspecting": insp, "attached": att})
    cams = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.QzNPCAttachment)
    extra = {}
    try:
        pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
        extra["player"] = pawn.get_class().get_name() if pawn else None
        extra["player_attached"] = [a.get_class().get_name() for a in pawn.get_attached_actors()] if pawn else []
        extra["player_components"] = sorted({c.get_class().get_name() for c in pawn.get_components_by_class(unreal.ActorComponent)}) if pawn else []
        try:
            extra["focus"] = str(pawn.get_actor_in_focus())
        except Exception as e:
            extra["focus"] = "err %s" % e
        tools = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.QzToolBase)
        extra["tool_actors"] = sorted("%s owner=%s hidden=%s" % (t.get_class().get_name(), t.get_owner().get_name() if t.get_owner() else None, t.is_hidden()) for t in tools)
        qr = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.load_class(None, "/Game/Blueprints/Quests/StoryActors/BP_QuestRoleDialogueActor.BP_QuestRoleDialogueActor_C"))
        extra["quest_role_dialogue"] = ["%s parent=%s comps=%s" % (q.get_name(), q.get_attach_parent_actor().get_name() if q.get_attach_parent_actor() else None,
                                        sorted({c.get_class().get_name() for c in q.get_components_by_class(unreal.ActorComponent)})) for q in qr]
        allc = {}
        for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor):
            n = a.get_class().get_name()
            allc[n] = allc.get(n, 0) + 1
        extra["actor_classes"] = allc if not res.get("_ac") else None
        res["_ac"] = True
    except Exception:
        extra["err"] = traceback.format_exc()[-600:]
    res["samples"].append({"t": round(time.time() - state["pie_t"], 1), "npc_count": len(npcs), "attachments_total": len(cams),
                           "attachment_classes": sorted({c.get_class().get_name() for c in cams}), "extra": extra, "npcs": rows[:40]})
    save()


def finish(reason):
    ev("finish: " + reason)
    try:
        if LES.is_in_play_in_editor():
            LES.editor_request_end_play()
    except Exception:
        pass
    save()
    try:
        unreal.unregister_slate_post_tick_callback(state["handle"])
    except Exception:
        pass
    unreal.SystemLibrary.quit_editor()


def tick(dt):
    try:
        now = time.time()
        if now - T0 > MAX_PIE_SECONDS + 240:
            return finish("global timeout")
        ph = state["phase"]
        if ph == "wait_editor":
            if now - state["t"] > 20:
                world = UES.get_editor_world()
                ev("editor world: %s" % (world.get_path_name() if world else None))
                LES.editor_request_begin_play()
                ev("requested PIE")
                state["phase"] = "wait_pie"; state["t"] = now
        elif ph == "wait_pie":
            gw = UES.get_game_world()
            if gw:
                ev("PIE world: %s" % gw.get_path_name())
                state["phase"] = "run"; state["pie_t"] = now
            elif now - state["t"] > 90:
                return finish("PIE did not start")
        elif ph == "run":
            gw = UES.get_game_world()
            if not gw:
                return finish("PIE world gone")
            if now - state["last_sample"] > 10:
                state["last_sample"] = now
                sample(gw)
            if now - state["pie_t"] > MAX_PIE_SECONDS:
                return finish("done sampling")
    except Exception:
        res["error"] = traceback.format_exc()[-1500:]
        finish("exception")


state["handle"] = unreal.register_slate_post_tick_callback(tick)
ev("registered tick")
save()
