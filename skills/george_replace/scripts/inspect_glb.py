"""Gate 0: is a Tripo GLB usable for the doctor (Georgie) skin replacement? Plain Python, read-only.
  python -I inspect_glb.py <model.glb>
Prints parts/tris/UV/textures/doubleSided and a verdict. Exit code 0 = OK, 1 = blocker."""
import json, struct, sys, os, hashlib

p = sys.argv[1]
d = open(p, "rb").read()
if d[:4] != b"glTF":
    sys.exit("not a GLB: " + p)
jl = struct.unpack_from("<I", d, 12)[0]
js = json.loads(d[20:20 + jl])
acc = js["accessors"]
prims = [pr for m in js.get("meshes", []) for pr in m["primitives"]]
tris = sum(acc[pr["indices"]]["count"] for pr in prims if "indices" in pr) // 3
attrs = sorted({a for pr in prims for a in pr["attributes"]})
mats = js.get("materials", [])
imgs = [(i.get("name"), i.get("mimeType")) for i in js.get("images", [])]
m0 = mats[0] if mats else {}
roles = {"BaseColor": "baseColorTexture" in m0.get("pbrMetallicRoughness", {}),
         "RoughMetal": "metallicRoughnessTexture" in m0.get("pbrMetallicRoughness", {}),
         "Normal": "normalTexture" in m0}
print("file", os.path.basename(p), "size %.1f MB" % (len(d) / 1e6), "sha1", hashlib.sha1(d).hexdigest()[:12])
print("parts", len(prims), "tris", tris, "attrs", attrs, "materials", len(mats), "doubleSided", m0.get("doubleSided", False))
print("images", imgs, "texture roles", roles, "skins", len(js.get("skins", [])))
block, warn = [], []
if "TEXCOORD_0" not in attrs:
    block.append("no UV (TEXCOORD_0) - model exported without texturing; re-export from Tripo WITH texture")
if not roles["BaseColor"]:
    block.append("no base colour texture - re-export from Tripo with texture")
if len(mats) > 1:
    warn.append("%d materials - pipeline expects 1 (only the first is used)" % len(mats))
if tris > 120000:
    block.append("%d tris - too heavy; regenerate with Quad 25000 (~50k tris)" % tris)
elif tris < 15000:
    warn.append("%d tris - fingers will be mush; Quad 25000 recommended" % tris)
if not roles["Normal"] or not roles["RoughMetal"]:
    warn.append("no Normal/RoughMetal map -> use flat_maps.py (flat normal, matte)")
if js.get("skins"):
    warn.append("GLB has its own skeleton - ignored (we bind to the game skeleton)")
for w in warn:
    print("WARN ", w)
for b in block:
    print("BLOCK", b)
print("VERDICT:", "BLOCKED" if block else "OK")
sys.exit(1 if block else 0)
