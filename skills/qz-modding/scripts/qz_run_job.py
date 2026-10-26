"""Run a mod job end to end from the outside (plain Python, no engine needed to start it).

  python -I qz_run_job.py <job.json> [--keep-log]

1. If the job has a create_mod op and QZSim/Mods/<mod>/<mod>.uplugin does not exist yet, writes the plugin
   skeleton FIRST (the editor only mounts mods it finds at startup — "Mounted mod source ... for editing").
2. Launches the full editor hidden-ish: UnrealEditor.exe QZSim.uproject -Installed
   -ExecutePythonScript="qz_mod_job.py <job>" -unattended -nosplash  (editor closes itself when the script ends;
   ~2-4 min on this PC; commandlet mode does NOT work: the UGC provider is disabled there).
3. Prints <job>.report.json and the [qz_mod_job] log lines.
"""
import json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))          # .../QZ_ModKit
PROJECT = os.path.join(KIT, "QZSim", "QZSim.uproject")
EDITOR = os.path.join(KIT, "Engine", "Engine", "Binaries", "Win64", "UnrealEditor.exe")
MODS = os.path.join(KIT, "QZSim", "Mods")
LOG = os.path.join(os.environ.get("LOCALAPPDATA", ""), "QZSim", "Saved", "Logs", "QZSim.log")


def required_game_version():
    try:
        for line in open(os.path.join(KIT, "QZSim", "Config", "DefaultGame.ini"), encoding="utf-8-sig"):
            if line.strip().startswith("RequiredModGameVersion="):
                return int(line.split("=", 1)[1])
    except Exception:
        pass
    return 4


def scaffold(mod, op):
    root = os.path.join(MODS, mod)
    up = os.path.join(root, mod + ".uplugin")
    for sub in ("Content", os.path.join("Config", "Tags"), "Resources"):
        os.makedirs(os.path.join(root, sub), exist_ok=True)
    if not os.path.exists(up):
        d = {"FileVersion": 3, "Version": 1, "VersionName": op.get("version_name", "1.0"),
             "FriendlyName": op.get("friendly_name", mod), "Description": op.get("description", ""),
             "Category": "UGC", "CreatedBy": op.get("author", ""), "CreatedByURL": "", "DocsURL": "",
             "MarketplaceURL": "", "SupportURL": "", "CanContainContent": True, "IsBetaVersion": False,
             "IsExperimentalVersion": False, "Installed": False, "ExplicitlyLoaded": True,
             "EngineVersion": op.get("engine_version", "5.7.0-0+UE5-QZ"),
             "GameVersion": int(op.get("game_version", required_game_version()))}
        with open(up, "w", encoding="utf-8", newline="\n") as f:      # UTF-8 without BOM
            json.dump(d, f, indent="\t", ensure_ascii=False)
        print("scaffolded", up)
    icon_src = os.path.join(KIT, "QZSim", "Plugins", "ModioUGC", "Templates", "BaseTemplate", "Resources", "Icon128.png")
    icon_dst = os.path.join(root, "Resources", "Icon128.png")
    if os.path.exists(icon_src) and not os.path.exists(icon_dst):
        open(icon_dst, "wb").write(open(icon_src, "rb").read())
    tags = op.get("tags")            # optional: {"Tag.Name": "DevComment", ...}
    if tags:
        ini = os.path.join(root, "Config", "Tags", mod + "Tags.ini")
        with open(ini, "w", encoding="utf-8", newline="\n") as f:
            f.write("[/Script/GameplayTags.GameplayTagsList]\n")
            for t, c in tags.items():
                f.write('GameplayTagList=(Tag="%s",DevComment="%s")\n' % (t, c.replace('"', "'")))
        print("tags ->", ini)


def main():
    job_path = os.path.abspath(sys.argv[1])
    job = json.load(open(job_path, encoding="utf-8"))
    for op in job["ops"]:
        if op.get("op") == "create_mod":
            scaffold(job["mod"], op)
    rp = os.path.splitext(job_path)[0] + ".report.json"
    if os.path.exists(rp):
        os.remove(rp)
    script = os.path.join(HERE, "qz_mod_job.py").replace("\\", "/")
    cmd = [EDITOR, PROJECT, "-Installed", '-ExecutePythonScript=%s %s' % (script, job_path.replace("\\", "/")),
           "-unattended", "-nosplash", "-log"]
    t0 = time.time()
    print("launching editor ...")
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("editor exited after %.0fs" % (time.time() - t0))
    try:
        for line in open(LOG, encoding="utf-8", errors="replace"):
            if "[qz_mod_job]" in line or "Mounted mod source" in line or "LogPython: Error" in line:
                print("  " + line.rstrip()[:300])
    except Exception:
        pass
    if not os.path.exists(rp):
        print("NO REPORT — script did not run; check", LOG)
        sys.exit(2)
    r = json.load(open(rp, encoding="utf-8"))
    print("OK:", r["ok"])
    print("ASSETS:", r.get("mod_assets"))
    for e in r["errors"]:
        print("ERROR:", e.get("op"), e.get("error"))
    sys.exit(1 if r["errors"] else 0)


if __name__ == "__main__":
    main()
