import json, os, traceback
import unreal
OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep", "enum_probe.json")
res = {}
e = unreal.QzCvNPCState.static_enum()
res["type"] = str(type(e))
res["methods"] = [m for m in dir(e) if not m.startswith("_")][:80]
out = []
for i in range(30):
    row = {"i": i}
    for fn in ("get_enumerator_name", "get_enumerator_user_friendly_name"):
        try:
            row[fn] = str(getattr(unreal.KismetNodeHelperLibrary, fn)(e, i))
        except Exception as ex:
            row[fn] = "ERR " + str(ex)[:200]
    try:
        row["py"] = str(unreal.QzCvNPCState(i))
    except Exception as ex:
        row["py"] = "ERR " + str(ex)[:80]
    out.append(row)
res["rows"] = out
try:
    res["text_export"] = unreal.KismetSystemLibrary.get_display_name(e)
except Exception as ex:
    res["text_export"] = str(ex)
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
unreal.log("[qz_probe_enum] done")
