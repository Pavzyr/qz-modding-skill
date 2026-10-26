"""Turn the raw qz_deep_dump.py output into compact markdown references for the skill.

Run with plain Python (no engine) after qz_deep_dump.py:
  python -I build_schema_refs.py [dump_dir] [out_dir]
Defaults: dump_dir = %LOCALAPPDATA%/QZSim/Saved/ModSchema/deep
          out_dir  = <skill>/references/schema
"""
import json, os, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DUMP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.environ.get("LOCALAPPDATA", ""), "QZSim", "Saved", "ModSchema", "deep")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "references", "schema")
os.makedirs(OUT, exist_ok=True)


def load(name):
    p = os.path.join(DUMP, name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


classes = load("classes.json") or {}
samples = load("samples.json") or {}
bps = load("blueprints.json") or []
das = load("data_assets.json") or []
skel = load("skeletons.json") or {}

# Classes a modder actually touches. Prefix match also pulls in subclasses (e.g. QzSymptomFillingRule_*).
KEY = [
    "QzSymptomDataAsset", "QzSymptomSectionDataAsset", "QzSymptomFillingRule", "QzReactionRule",
    "QzSymptomModifier", "QzModifySymptom", "QzNPCSymptom", "QzSymptom",
    "QzToolDataAsset", "QzManualGrantToolDataAsset", "QzToolComponent", "QZTool_", "QzTool_",
    "QzStaticNPCSkinDataAsset", "QzLevelDataAsset", "QzCompanyDataAsset", "QzCompanyBaseConfig",
    "QzCompanyConfig", "QzCompanyShortInfo", "QzDayDataAsset", "QzNewDayData", "QzDayConfig", "QzDayRules",
    "QzDayModifier", "QzGenRule", "QzQueueDay", "QzNPCProfileDataAsset", "QzProfileDataAsset", "QzStaticProfile",
    "QzProfileAppearanceOverrides", "QzHandbookDataAsset", "QzGeneratorParentPrimaryData",
    "QzCharacterHatDataAsset", "QzCharacterAccessory", "QzCharacterGlassesDataAsset", "QzCharacterHairDataAsset",
    "QzClothingItemDataAsset", "QzCharacterDataAsset", "QzCharacterSkinDataAsset", "QzCharacterSkinOverlayDataAsset",
    "QzBaggageSetDataAsset", "QzBaggageItemDataAsset", "QzInternalContrabandSetDataAsset", "QzMusicDataAsset",
    "LossCondition", "QzLockedSymptomsDataAsset", "QzDynamicRule", "UGC_Metadata", "UGCPackage", "UGCRejectReason",
]
SKIP_CHAIN = ("DelegateBase", "MulticastDelegateBase")


def is_key(n):
    return any(n == k or n.startswith(k) for k in KEY)


def own_props(name):
    c = classes.get(name, {})
    props = dict(c.get("props", {}))
    parent = (c.get("chain") or [None])[0]
    if parent in classes:
        for p in classes[parent].get("props", {}):
            props.pop(p, None)
    return props, parent


# ------------------------------------------------------------- key-classes.md
lines = ["# Ключевые классы QZ для модов (из qz_deep_dump)", "",
         "Поля указаны как в Python API (`snake_case`; в редакторе — CamelCase). Показаны только СОБСТВЕННЫЕ поля класса "
         "(унаследованные — у родителя). Полный дамп: `%LOCALAPPDATA%/QZSim/Saved/ModSchema/deep/classes.json`.", ""]
for n in sorted(classes):
    c = classes[n]
    if not is_key(n) or (c.get("chain") or [""])[0] in SKIP_CHAIN:
        continue
    props, parent = own_props(n)
    lines.append("## %s  ←  %s" % (n, " < ".join(c.get("chain", [])[:3])))
    if c.get("summary"):
        lines.append("_%s_" % c["summary"][:300].replace("\n", " "))
    if c.get("chain", [""])[0] == "EnumBase":
        lines.append("")
        continue
    for p, v in props.items():
        lines.append("- `%s` (%s) %s" % (p, v["type"], v["doc"][:200]))
    lines.append("")
open(os.path.join(OUT, "key-classes.md"), "w", encoding="utf-8").write("\n".join(lines))

# ------------------------------------------------------------- classes-index.txt
with open(os.path.join(OUT, "classes-index.txt"), "w", encoding="utf-8") as f:
    f.write("# All Qz*/QZ*/Sim*/UGC* classes: name <- parent chain | own+inherited editor prop count\n")
    for n in sorted(classes):
        c = classes[n]
        if n.startswith("Modio") or (c.get("chain") or [""])[0] in SKIP_CHAIN:
            continue
        f.write("%s <- %s | %d\n" % (n, " < ".join(c.get("chain", [])[:3]), len(c.get("props", {}))))

# ------------------------------------------------------------- samples.md
by_class = defaultdict(list)
for path, s in samples.items():
    if isinstance(s, dict):
        by_class[s["class"]].append((path, s))


def compact(v, limit=1800):
    t = json.dumps(v, ensure_ascii=False, indent=1)
    return t if len(t) <= limit else t[:limit] + "\n... (обрезано)"


lines = ["# Образцы значений базовых ассетов", "",
         "1–2 ассета на класс; полные значения — `samples.json` в папке дампа.", ""]
for cls in sorted(by_class):
    lines.append("## %s (%d в выборке)" % (cls, len(by_class[cls])))
    for path, s in by_class[cls][:2]:
        lines.append("### `%s`" % path)
        lines.append("```json")
        lines.append(compact(s.get("values", {})))
        if "cdo" in s:
            lines.append("// CDO:")
            lines.append(compact(s["cdo"], 1200))
        lines.append("```")
    lines.append("")
open(os.path.join(OUT, "samples.md"), "w", encoding="utf-8").write("\n".join(lines))

# ------------------------------------------------------------- content-index.md
lines = ["# Индекс контента", "", "## Data-ассеты /Game/Data по классам", ""]
cnt = Counter(a["class"] for a in das)
folders = defaultdict(set)
for a in das:
    folders[a["class"]].add(a["path"].rsplit("/", 1)[0])
for cls, n in cnt.most_common():
    fs = sorted(folders[cls])
    lines.append("- **%s** ×%d — %s%s" % (cls, n, ", ".join(fs[:4]), " …" if len(fs) > 4 else ""))
lines += ["", "## Native-родители Blueprint'ов (/Game, без MetaHumans) — что наследовать в моде", ""]
pc = Counter()
examples = defaultdict(list)
for b in bps:
    par = re.sub(r"^.*[./]", "", (b.get("native_parent") or b.get("parent") or "")).rstrip("'")
    pc[par] += 1
    if len(examples[par]) < 3:
        examples[par].append(b["path"])
for par, n in pc.most_common(80):
    lines.append("- `%s` ×%d — %s" % (par, n, ", ".join(examples[par])))
lines += ["", "## Blueprint'ы инструментов и симптомов", ""]
for b in sorted(bps, key=lambda b: b["path"]):
    if re.search(r"/Blueprints/Tools/|Symptom|/GA_|BP_GA_", b["path"]):
        lines.append("- `%s` ← %s" % (b["path"], re.sub(r"^.*[./]", "", b.get("parent", "")).rstrip("'")))
lines += ["", "## Скелеты, используемые сэмплированными ассетами", ""]
for sk, uses in (skel.get("used_by_sampled_assets") or {}).items():
    lines.append("- `%s` ×%d — напр. %s" % (sk, len(uses), uses[0]))
lines += ["", "## Все Skeleton-ассеты (без /Engine, ControlRig, Anatomy)", ""]
for sk in skel.get("all_skeletons", []):
    if not re.search(r"^/(Engine|ControlRig|AnimToTexture)|Anatomy_Ultimate|Tutorial", sk):
        lines.append("- `%s`" % sk)
open(os.path.join(OUT, "content-index.md"), "w", encoding="utf-8").write("\n".join(lines))

print("written to", os.path.abspath(OUT))
for f in sorted(os.listdir(OUT)):
    print(" ", f, os.path.getsize(os.path.join(OUT, f)))
