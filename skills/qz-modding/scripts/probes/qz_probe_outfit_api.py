"""Read-only (commandlet): BP-callable methods of the NPC / appearance classes that could rebuild clothes at runtime
(QzCvConstructorComponent, QzNPCCharacter, QzTakeOffClothes*, ...). Writes deep/outfit_api.json. (2026-10-20)"""
import json, os, re
import unreal

OUT = os.path.join(unreal.Paths.project_saved_dir(), "ModSchema", "deep", "outfit_api.json")
res = {}
NAMES = [n for n in dir(unreal) if re.search(r"(Constructor|TakeOff|Appearance|Clothes|Clothing|NPCCharacter|NPCManager|Generator|Outfit|Skin)", n)]
for n in NAMES:
    c = getattr(unreal, n)
    if not isinstance(c, type):
        continue
    own = {}
    for m in sorted(vars(c)):
        if m.startswith("_"):
            continue
        a = getattr(c, m, None)
        if callable(a) and not isinstance(a, type):
            doc = (getattr(a, "__doc__", "") or "").strip().splitlines()
            own[m] = " | ".join(x.strip() for x in doc[:6])[:400]
    if issubclass(c, unreal.EnumBase):
        own = {"__enum__": [str(x) for x in list(c.__members__)] if hasattr(c, "__members__") else [k for k in vars(c) if k.isupper()]}
    if own:
        res[n] = own
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("OUTFIT_API_DONE", len(res))
