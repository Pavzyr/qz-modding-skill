# job "py" op (read-only): what identifies the unique/quest visitors - character_name, quest tag, document names, bio override,
# replica flags - for every profile data asset under the given folders -> REPORT["profiles"]
FOLDERS = ARGS.get("folders", ["/Game/Data/Profiles/Custom", "/Game/Data/Profiles/Quests"])
out = {}
for folder in FOLDERS:
    for path in EAS.list_assets(folder, recursive=True, include_folder=False):
        try:
            a = EAS.load_asset(path.split(".")[0])
        except Exception:
            continue
        if not a:
            continue
        rec = {"class": a.get_class().get_name()}
        def g(n):
            try:
                v = a.get_editor_property(n)
                return str(v) if not isinstance(v, (int, float, bool)) else v
            except Exception:
                return None
        for n in ("name_key", "first_name", "last_name", "bio", "override_bio", "age", "gender", "quest_tag_npc", "profession",
                  "body_tag", "custom_logic_list", "has_document", "city", "override_address"):
            rec[n] = g(n)
        out[path.split(".")[0]] = rec
REPORT["profiles"] = out
