"""Editor probe (nothing saved): silhouettes of clothing meshes. Spawns each mesh far from the level, a SceneCapture2D
(show-only, base colour) per view, waits a few frames so the capture is really rendered, exports PNGs, quits.
Run: UnrealEditor.exe QZSim.uproject -Installed -ExecCmds="py <this file>" ; config: Saved/ModSchema/deep/cloth_shots_cfg.json"""
import json, os, time, traceback
import unreal
CFG = json.load(open(os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep", "cloth_shots_cfg.json"), encoding="utf-8"))
st = {"phase": "boot", "t": time.time(), "h": None, "i": 0, "frames": 0, "cams": [], "actor": None, "log": []}
world = None
VIEWS = (("front", 0, 1, -90), ("back", 0, -1, 90), ("side", 1, 0, 180))


def finish(r):
    st["log"].append(r)
    json.dump(st["log"], open(os.path.join(CFG["dir"], "shots_log.json"), "w"), indent=1)
    unreal.unregister_slate_post_tick_callback(st["h"])
    unreal.SystemLibrary.quit_editor()


def spawn(i):
    global world
    p = CFG["paths"][i]
    mesh = unreal.EditorAssetLibrary.load_asset(p)
    base = unreal.Vector(0, 300000 + i * 5000, 60000)
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkeletalMeshActor, base, unreal.Rotator(0, 0, 0))
    comp = a.get_editor_property("skeletal_mesh_component")
    comp.set_editor_property("skeletal_mesh_asset", mesh)
    b = mesh.get_bounds(); c = base + b.origin; r = max(b.box_extent.x, b.box_extent.y, b.box_extent.z)
    cams = []
    for name, dx, dy, yaw in VIEWS:
        cam = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(c.x + dx * r * 4, c.y + dy * r * 4, c.z), unreal.Rotator(0, 0, yaw))
        cc = cam.get_editor_property("capture_component2d")
        rt = unreal.RenderingLibrary.create_render_target2d(world, 400, 400, unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(0, 0, 0, 1))
        cc.set_editor_property("texture_target", rt)
        cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_BASE_COLOR)
        cc.set_editor_property("fov_angle", 30.0)
        cc.set_editor_property("primitive_render_mode", unreal.SceneCapturePrimitiveRenderMode.PRM_USE_SHOW_ONLY_LIST)
        cc.show_only_actor_components(a, False)
        cc.set_editor_property("capture_every_frame", True)
        cams.append((name, cam, cc, rt))
    st["actor"], st["cams"] = a, cams
    st["log"].append("spawned " + p)


def tick(dt):
    global world
    try:
        now = time.time()
        if st["phase"] == "boot" and now - st["t"] > 15:
            world = unreal.EditorLevelLibrary.get_editor_world()
            spawn(0); st.update(phase="wait", frames=0)
        elif st["phase"] == "wait":
            st["frames"] += 1
            if st["frames"] > 40:
                i = st["i"]
                for name, cam, cc, rt in st["cams"]:
                    unreal.RenderingLibrary.export_render_target(world, rt, CFG["dir"], "%02d_%s_%s.png" % (i, CFG["paths"][i].split("/")[-1], name))
                    cam.destroy_actor()
                st["actor"].destroy_actor()
                st["i"] += 1
                if st["i"] >= len(CFG["paths"]):
                    finish("done")
                else:
                    spawn(st["i"]); st["frames"] = 0
        if now - st["t"] > 400:
            finish("timeout")
    except Exception:
        st["log"].append(traceback.format_exc()[-800:]); finish("exception")


st["h"] = unreal.register_slate_post_tick_callback(tick)
