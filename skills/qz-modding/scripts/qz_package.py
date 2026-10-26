"""Package a mod headlessly (equivalent of mod.io → Package UGC) and produce an upload-ready zip.

  python -I qz_package.py <ModName> [--out <dir>] [--keep-staging] [--versioned]

Steps:
 1. qz_validate_mod.py on the source plugin (aborts on FAIL).
 2. RunUAT BuildCookRun as a DLC cook based on Releases/BaseGameRelease (verified 2026-10-14: ~1 min for a small mod):
    -platform=Win64 -clientconfig=Shipping -cook -stage -pak -iostore -SkipCookingEditorContent
    -DLCName=<Mod> -basedonreleaseversion=BaseGameRelease -stagingdirectory=<out>/staging
 3. Takes <staging>/Windows/QZSim/Mods/<Mod>/ (uplugin + Content/Paks/Windows/*), adds Config/ (tags) from source
    if UAT did not stage it, removes the cook leftovers QZSim/Mods/<Mod>/Saved.
 4. Validates the result and zips it as <out>/<Mod>_Windows.zip with the same layout as mods on mod.io:
      <Mod>.uplugin, Config/Tags/*.ini, Content/Paks/Windows/<Mod>QZSim-Windows.{pak,utoc,ucas}
Default out: $QZ_MODS_OUT/<Mod>/Builds/ when the env variable is set, else <kit>/ModBuilds/<Mod>/
Local test: unzip into <game>\\QZSim\\Modio\\<Mod>\\ (not at the same time as a mod.io subscription of it).
"""
import os, shutil, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
UAT = os.path.join(KIT, "Engine", "Engine", "Build", "BatchFiles", "RunUAT.bat")
PROJECT = os.path.join(KIT, "QZSim", "QZSim.uproject")


def run_validate(path):
    r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "qz_validate_mod.py"), path])
    return r.returncode == 0


def main():
    mod = sys.argv[1]
    out = (os.path.join(os.environ["QZ_MODS_OUT"], mod, "Builds") if os.environ.get("QZ_MODS_OUT")
           else os.path.join(KIT, "ModBuilds", mod))
    if "--out" in sys.argv:
        out = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    src = os.path.join(KIT, "QZSim", "Mods", mod)
    print("== validate source")
    if not run_validate(src):
        sys.exit("source validation failed")
    staging = os.path.join(out, "staging")
    shutil.rmtree(staging, ignore_errors=True)
    os.makedirs(staging, exist_ok=True)
    args = ["BuildCookRun", "-project=" + PROJECT, "-noP4", "-clientconfig=Shipping", "-serverconfig=Shipping",
            "-installed", "-platform=Win64", "-target=QZSim", "-SkipCookingEditorContent", "-cook", "-stage",
            "-pak", "-iostore", "-unattended", "-utf8output", "-nocompile", "-nocompileeditor", "-skipbuild",
            "-DLCName=" + mod, "-basedonreleaseversion=BaseGameRelease", "-stagingdirectory=" + staging]
    if "--versioned" in sys.argv:
        # tagged (named) properties instead of unversioned ones: needed when a game class in the kit has fields the
        # player's game build does not have (kit newer than game) - otherwise "ObjectSerializationError ... Bad name index"
        args.append("-VersionCookedContent")
    log = os.path.join(out, "uat.log")
    print("== UAT cook (log: %s)" % log)
    with open(log, "w", encoding="utf-8", errors="replace") as f:
        r = subprocess.run(["cmd", "/c", UAT] + args, stdout=f, stderr=subprocess.STDOUT)
    tail = open(log, encoding="utf-8", errors="replace").read()[-600:]
    if r.returncode != 0 or "BUILD SUCCESSFUL" not in tail:
        print(tail)
        sys.exit("UAT failed (exit %s)" % r.returncode)
    staged = os.path.join(staging, "Windows", "QZSim", "Mods", mod)
    if not os.path.isdir(staged):
        sys.exit("staged mod not found at " + staged)
    final = os.path.join(out, mod)
    shutil.rmtree(final, ignore_errors=True)
    shutil.copytree(staged, final)
    cfg = os.path.join(src, "Config")
    if os.path.isdir(cfg) and not os.path.isdir(os.path.join(final, "Config")):
        shutil.copytree(cfg, os.path.join(final, "Config"))
        print("copied Config/ from source")
    for d in ("Saved", "Intermediate"):
        shutil.rmtree(os.path.join(final, d), ignore_errors=True)
    # cook leftovers inside the source plugin
    shutil.rmtree(os.path.join(src, "Saved"), ignore_errors=True)
    print("== validate package")
    if not run_validate(final):
        sys.exit("package validation failed")
    zp = os.path.join(out, "%s_Windows.zip" % mod)
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for r_, _, fs in os.walk(final):
            for f in fs:
                p = os.path.join(r_, f)
                z.write(p, os.path.relpath(p, final))
    if "--keep-staging" not in sys.argv:
        shutil.rmtree(staging, ignore_errors=True)
    print("== done:", zp, "%.1f MB" % (os.path.getsize(zp) / 1e6))
    for n in zipfile.ZipFile(zp).namelist():
        print("   ", n)


if __name__ == "__main__":
    main()
