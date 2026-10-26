"""PIE probe: the raid level with a given wave config (NoRaid empty waves): does the raid end in victory by itself?
Startup map must be the raid level (-ini:Engine:[/Script/EngineSettings.GameMapsSettings]:EditorStartupMap=...).
Config: Saved/ModSchema/deep/defense_waves_cfg.json {"wave": "/NoRaid/Data/DA_NoRaid_EmptyWavesA", "start": true}"""
import json, os, time, traceback
import unreal
D = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep")
CFG = json.load(open(os.path.join(D, "defense_waves_cfg.json"), encoding="utf-8"))
OUT = os.path.join(D, "pie_defense_waves_%s.json" % CFG.get("tag", "run"))
res = {"cfg": CFG, "events": []}
st = {"phase": "boot", "t": time.time(), "h": None, "n": 0}
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


def tick(dt):
    try:
        now = time.time(); el = now - st["t"]
        if st["phase"] == "boot" and el > 30:
            LES.editor_request_begin_play(); st.update(phase="run", t=now); ev("PIE started in %s" % UES.get_editor_world().get_name())
        elif st["phase"] == "run" and el > 1.0:
            st["t"] = now; st["n"] += 1
            w = UES.get_game_world()
            if not w:
                return
            dm = unreal.QzDefenseManager.get_defense_manager(w)
            if st["n"] == 8:
                try:
                    ev("force_editor_wave_config before: %s" % dm.get_editor_property("force_editor_wave_config"))
                except Exception as e:
                    ev("read force cfg: %s" % e)
                if CFG.get("wave"):
                    try:
                        dm.set_editor_property("force_editor_wave_config", unreal.load_asset(CFG["wave"])); ev("force cfg set")
                    except Exception as e:
                        ev("set force cfg: %s" % e)
                if CFG.get("reinit", True):
                    dm.initialize_all_spawners(); ev("initialize_all_spawners()")
                if CFG.get("start"):
                    dm.start_defense(); ev("start_defense()")
            if st["n"] >= 8 and st["n"] % 4 == 0:
                z = len(unreal.GameplayStatics.get_all_actors_of_class(w, unreal.QzDefenseZombie))
                ws = [x.get_class().get_name() for x in unreal.WidgetLibrary.get_all_widgets_of_class(w, unreal.UserWidget, True)]
                ev("zombies=%d widgets=%s current_cfg=%s" % (z, ws, dm.get_current_wave_config() if dm else None))
            if st["n"] in (20, 30):
                for fw in unreal.WidgetLibrary.get_all_widgets_of_class(w, unreal.UserWidget, False):
                    if fw.get_class().get_name() == "WB_DefenceFinish_C":
                        texts = []
                        for cls in (unreal.TextBlock, unreal.RichTextBlock):
                            for tb in unreal.WidgetLibrary.get_all_widgets_of_class(w, unreal.UserWidget, False) and []:
                                pass
                        tree = unreal.find_object(fw, "WidgetTree")
                        for obj in unreal.ObjectIterator(unreal.TextBlock):
                            if obj.get_outer() == tree or (obj.get_path_name().startswith(fw.get_path_name())):
                                t = str(obj.get_text())
                                if t.strip(): texts.append([obj.get_name(), t, str(obj.get_visibility())])
                        for obj in unreal.ObjectIterator(unreal.RichTextBlock):
                            if obj.get_path_name().startswith(fw.get_path_name()):
                                t = str(obj.get_text())
                                if t.strip(): texts.append([obj.get_name(), t, str(obj.get_visibility())])
                        ev("finish texts: %s" % texts[:40])
                        for obj in unreal.ObjectIterator(unreal.TextBlock):
                            if obj.get_path_name().startswith(fw.get_path_name()) and str(obj.get_text()) in ("Victory", "Defeat"):
                                chain = []; x = obj
                                while x:
                                    item = "%s/%s/%s" % (x.get_name(), x.get_class().get_name(), str(x.get_visibility()).split(".")[-1].split(":")[0])
                                    if isinstance(x, unreal.WidgetSwitcher):
                                        item += "/active=%s" % x.get_active_widget().get_name()
                                    try:
                                        item += "/opacity=%.2f" % x.get_render_opacity()
                                    except Exception:
                                        pass
                                    chain.append(item); x = x.get_parent()
                                ev("chain %s: %s" % (obj.get_text(), chain))
            if st["n"] > 34:
                finish("done")
    except Exception:
        res["err"] = traceback.format_exc()[-1200:]
        finish("exception")


st["h"] = unreal.register_slate_post_tick_callback(tick)
