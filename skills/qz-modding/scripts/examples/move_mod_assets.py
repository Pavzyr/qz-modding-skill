# job "py" op: move every asset of one mod plugin into another (rename the mod = new mount point). AssetTools.rename_assets
# rewrites all references between the moved assets (BP graphs, widget/variable types, mesh -> post-process AnimBP, company -> day...).
# ARGS: {"src": "/OldModName", "dst": "/NewModName", "skip": ["UUGC_Metadata"]}
AT = unreal.AssetToolsHelpers.get_asset_tools()
AR = unreal.AssetRegistryHelpers.get_asset_registry()
BEL = unreal.BlueprintEditorLibrary
src, dst = ARGS["src"].rstrip("/"), ARGS["dst"].rstrip("/")
skip = set(ARGS.get("skip", ["UUGC_Metadata"]))
R = REPORT.setdefault("move", {"moved": [], "failed": [], "left_refs": {}})
paths = [p.split(".")[0] for p in EAS.list_assets(src, recursive=True, include_folder=False)]
items = []
for p in paths:
    name = p.rsplit("/", 1)[1]
    if name in skip:
        continue
    a = EAS.load_asset(p)            # load everything first: referencers inside the mod get fixed up by the rename
    if a is None:
        R["failed"].append(p); continue
    new_dir = dst + p[len(src):].rsplit("/", 1)[0]
    items.append((p, a, new_dir, name))
ok = AT.rename_assets([unreal.AssetRenameData(a, new_dir, name) for _, a, new_dir, name in items])
R["rename_ok"] = bool(ok)
for p, _, new_dir, name in items:
    np_ = new_dir + "/" + name
    (R["moved"] if EAS.does_asset_exist(np_) else R["failed"]).append(np_)
# compile + save the moved Blueprints, then check that nothing points at the old mount point any more
for p in R["moved"]:
    a = EAS.load_asset(p)
    if isinstance(a, unreal.Blueprint):
        try:
            BEL.compile_blueprint(a)
        except Exception as e:
            R.setdefault("compile_err", {})[p] = str(e)[:120]
    EAS.save_loaded_asset(a, False)
opt = unreal.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True,
                                            include_searchable_names=False, include_soft_management_references=False,
                                            include_hard_management_references=False)
for p in R["moved"]:
    deps = [str(d) for d in (AR.get_dependencies(p, opt) or [])]
    old = [d for d in deps if d.startswith(src + "/")]
    if old:
        R["left_refs"][p] = old
R["old_left"] = [x.split(".")[0] for x in EAS.list_assets(src, recursive=True, include_folder=False)]
