# job "py" op: NoRaid - a copy of the Chicago campaign whose raid days start a raid with EMPTY waves (instant victory, the
# day's upgrade unlocks kept). Two empty wave configs for the PIE test: A = no waves at all, B = one wave with 0 zombies.
DAYS = (2, 7, 11, 16, 19)
R = REPORT.setdefault("noraid", {})


def empty_config(path, variant):
    cfg = EAS.load_asset(path)
    sp = cfg.get_editor_property("spawners")
    new = {}
    for k in sp.keys():
        info = sp[k]
        if variant == "A":
            info.set_editor_property("zombies_elements", [])
        else:
            el = unreal.QzDefenseWaveElementInfo()
            zi = list(info.get_editor_property("zombies_elements")[0].get_editor_property("zombies_in_wave"))[:1]
            for z in zi:
                z.set_editor_property("zombie_count", unreal.IntPoint(0, 0))
            el.set_editor_property("zombies_in_wave", zi)
            info.set_editor_property("zombies_elements", [el])
        info.set_editor_property("zombie_count_waves", [])
        new[k] = info
    cfg.set_editor_property("spawners", new)
    EAS.save_loaded_asset(cfg, False)
    R["config_" + variant] = str(EAS.load_asset(path).get_editor_property("spawners"))[:600]


empty_config("/NoRaid/Data/DA_NoRaid_EmptyWavesA", "A")
empty_config("/NoRaid/Data/DA_NoRaid_EmptyWavesB", "B")
use = EAS.load_asset(ARGS.get("use", "/NoRaid/Data/DA_NoRaid_EmptyWavesA"))
c = EAS.load_asset("/NoRaid/Data/DA_Company_NoRaid_Chicago")
days = list(c.get_editor_property("days"))
for n in DAYS:
    day = EAS.load_asset("/NoRaid/Data/DAY_NoRaid_Chicago%02d" % n)
    for m in day.get_editor_property("modifiers"):
        if m and m.get_class().get_name() == "QzDayModifier_Defense":
            data = m.get_editor_property("data")
            data.set_editor_property("zombie_spawner_soft", use)
            m.set_editor_property("data", data)
            R["day%02d" % n] = str(m.get_editor_property("data"))[:300]
    EAS.save_loaded_asset(day, False)
    days[n - 1] = day
c.set_editor_property("days", days)
c.set_editor_property("tag", tag("Company.NoRaid.Chicago"))
c.set_editor_property("title", unreal.Text("Chicago - No Raids"))
c.set_editor_property("campaign_psevdonim", unreal.Text("Чикаго (без рейдов)"))
c.set_editor_property("description", unreal.Text(
    "The Chicago campaign where every drone raid ends in victory as soon as it starts: no zombies come. The upgrades a raid unlocks are kept. "
    "/ Кампания Чикаго, в которой каждый рейд с дроном сразу заканчивается победой: зомби не приходят. Улучшения, которые открывает рейд, сохраняются."))
EAS.save_loaded_asset(c, False)
c = EAS.load_asset("/NoRaid/Data/DA_Company_NoRaid_Chicago")
R["company"] = {"tag": str(unreal.GameplayTagLibrary.get_tag_name(c.get_editor_property("tag"))), "title": str(c.get_editor_property("title")),
                "days": [d.get_path_name().split("/")[-1] for d in c.get_editor_property("days")]}
