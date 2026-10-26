"""Read-only: find any Python-callable API that can create/import Blueprint graph nodes. Writes graph_api.json."""
import json, os, re
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep")
res = {}
for n in sorted(dir(unreal)):
    if not re.search(r"Graph|K2|Node|Kismet|Blueprint|Clipboard|EditorUtility|Script", n):
        continue
    c = getattr(unreal, n, None)
    if not isinstance(c, type):
        continue
    ms = []
    for m in dir(c):
        if m.startswith("_"):
            continue
        if re.search(r"node|graph|paste|import|text|clipboard|spawn|pin|link|script|function|create|add", m, re.I):
            try:
                doc = (getattr(c, m).__doc__ or "").strip().splitlines()
            except Exception:
                doc = []
            ms.append(m + " | " + (doc[0][:160] if doc else ""))
    if ms:
        res[n] = ms
plug = {}
try:
    for p in unreal.PluginBlueprintLibrary.get_enabled_plugin_names():
        plug[str(p)] = True
except Exception as e:
    plug["err"] = str(e)
res["_enabled_plugins"] = sorted(plug)
with open(os.path.join(OUT, "graph_api.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
unreal.log("[qz_probe_graphapi] done %d" % len(res))
