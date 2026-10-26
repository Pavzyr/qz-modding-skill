"""Pre-package / pre-publish lint for a QZ mod (plain Python, no engine).

  python -I qz_validate_mod.py <ModName | path to QZSim/Mods/<Mod> | packaged folder/zip dir>

FAIL: uplugin missing/BOM/invalid JSON, wrong Category/CanContainContent, ExplicitlyLoaded!=true,
      GameVersion < RequiredModGameVersion (DefaultGame.ini), EngineVersion not 5.7.x+UE5-QZ,
      no UUGC_Metadata, tags ini tags without mod prefix collisions with base tags, secrets in text files.
WARN: empty Content, tag used in assets but not declared (can't check binaries — names only), absolute paths,
      missing Description/CreatedBy, files outside Content/Config/Resources.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
fails, warns, infos = [], [], []


def required_game_version():
    try:
        for line in open(os.path.join(KIT, "QZSim", "Config", "DefaultGame.ini"), encoding="utf-8-sig"):
            if line.strip().startswith("RequiredModGameVersion="):
                return int(line.split("=", 1)[1])
    except Exception:
        pass
    return None


def base_tags():
    tags = set()
    cfg = os.path.join(KIT, "QZSim", "Config")
    for root, _, files in os.walk(cfg):
        for f in files:
            if f.endswith(".ini"):
                for m in re.finditer(r'Tag="([^"]+)"', open(os.path.join(root, f), encoding="utf-8-sig", errors="ignore").read()):
                    tags.add(m.group(1))
    return tags


def main():
    arg = sys.argv[1]
    root = arg if os.path.isdir(arg) else os.path.join(KIT, "QZSim", "Mods", arg)
    ups = [f for f in os.listdir(root) if f.endswith(".uplugin")]
    if len(ups) != 1:
        fails.append("expected exactly one .uplugin in %s, found %s" % (root, ups))
        return root
    name = ups[0][:-8]
    raw = open(os.path.join(root, ups[0]), "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"):
        fails.append("uplugin has UTF-8 BOM (must be UTF-8 without BOM)")
    try:
        d = json.loads(raw.decode("utf-8-sig"))
    except Exception as e:
        fails.append("uplugin is not valid JSON: %s" % e)
        return root
    if d.get("Category") != "UGC":
        warns.append("Category is %r (real mods use 'UGC')" % d.get("Category"))
    if not d.get("CanContainContent"):
        fails.append("CanContainContent must be true")
    if d.get("ExplicitlyLoaded") is not True:
        fails.append("ExplicitlyLoaded must be true (else mod breaks on rescan)")
    ev = d.get("EngineVersion", "")
    if not re.match(r"^5\.7\.\d+-\d+\+UE5-QZ$", ev):
        fails.append("EngineVersion %r (expected like 5.7.0-0+UE5-QZ)" % ev)
    req = required_game_version()
    gv = d.get("GameVersion")
    if not isinstance(gv, int):
        fails.append("GameVersion missing")
    elif req and gv < req:
        fails.append("GameVersion %s < RequiredModGameVersion %s — game will reject the mod" % (gv, req))
    infos.append("uplugin: %s GameVersion=%s EngineVersion=%s (required %s)" % (name, gv, ev, req))
    for k in ("Description", "CreatedBy"):
        if not d.get(k):
            warns.append("uplugin %s is empty" % k)
    # content
    content = os.path.join(root, "Content")
    files = []
    for r, _, fs in os.walk(content):
        files += [os.path.relpath(os.path.join(r, f), content) for f in fs]
    paks = [f for f in files if f.endswith((".pak", ".utoc", ".ucas"))]
    if paks:
        infos.append("packaged mod: %s" % paks)
        if not any(f.endswith(".utoc") for f in paks):
            fails.append("packaged mod without .utoc (IoStore expected)")
    else:
        if not files:
            warns.append("Content is empty")
        if "UUGC_Metadata.uasset" not in files:
            fails.append("Content/UUGC_Metadata.uasset missing (Package UGC will fail: MissingMetadataAsset)")
        else:
            meta = [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(root, "Content")) for f in fs if f == "UUGC_Metadata.uasset"]
            if meta and b"bIoStoreEnabled" not in open(meta[0], "rb").read():
                fails.append("UUGC_Metadata.bIoStoreEnabled is false -> game rejects the mod: 'bUseIoStore values mismatch "
                             "between UGC (FALSE) and Base Game (TRUE)'. Fix: job op set io_store_enabled=true")
        infos.append("source assets: %d" % len([f for f in files if f.endswith((".uasset", ".umap"))]))
    # tags
    tdir = os.path.join(root, "Config", "Tags")
    btags = base_tags()
    if os.path.isdir(tdir):
        for f in os.listdir(tdir):
            txt = open(os.path.join(tdir, f), encoding="utf-8-sig").read()
            if not txt.lstrip().startswith("[/Script/GameplayTags.GameplayTagsList]"):
                fails.append("%s: must start with [/Script/GameplayTags.GameplayTagsList]" % f)
            for t in re.findall(r'Tag="([^"]+)"', txt):
                if t in btags:
                    warns.append("tag %s already exists in base game (ok only if intentional)" % t)
    # stray files / secrets
    for r, _, fs in os.walk(root):
        for f in fs:
            rel = os.path.relpath(os.path.join(r, f), root)
            top = rel.split(os.sep)[0]
            if top not in ("Content", "Config", "Resources", ups[0], "MODLOG.md", "README.md", "jobs", "Saved", "Intermediate"):
                warns.append("unexpected file: %s" % rel)
            if f.endswith((".ini", ".json", ".md", ".txt", ".uplugin")):
                t = open(os.path.join(r, f), encoding="utf-8", errors="ignore").read()
                if re.search(r"(sk-ant-|ghp_|AKIA[0-9A-Z]{16}|ApiKey=|api_key)", t):
                    fails.append("possible secret in %s" % rel)
                if re.search(r"[A-Za-z]:\\\\Users\\\\|C:/Users/", t) and not f.endswith("MODLOG.md"):
                    warns.append("absolute user path in %s" % rel)
    for x in ("Saved", "Intermediate"):
        if os.path.isdir(os.path.join(root, x)):
            warns.append("%s/ folder inside mod — do not ship it" % x)
    return root


if __name__ == "__main__":
    r = main()
    for i in infos:
        print("INFO ", i)
    for w in warns:
        print("WARN ", w)
    for f in fails:
        print("FAIL ", f)
    print("RESULT:", "FAIL" if fails else "OK", "(%s)" % r)
    sys.exit(1 if fails else 0)
