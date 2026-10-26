# Job "py" op for NoIntroExample: day 1 copy without QzDayModifier_Intro; campaign copy with own tag, title, day 1 swapped.
import unreal

DAY = "/NoIntroExample/Data/DAY_NIE_Chicago01"
CMP = "/NoIntroExample/Data/DA_Company_NIE_Chicago"
day = EAS.load_asset(DAY)
mods = list(day.get_editor_property("modifiers"))
before = [m.get_class().get_name() for m in mods if m]
keep = [m for m in mods if m and m.get_class().get_name() != "QzDayModifier_Intro"]
day.set_editor_property("modifiers", keep)
EAS.save_loaded_asset(day, False)
after = [m.get_class().get_name() for m in EAS.load_asset(DAY).get_editor_property("modifiers")]

c = EAS.load_asset(CMP)
days = list(c.get_editor_property("days"))
days[0] = EAS.load_asset(DAY)
c.set_editor_property("days", days)
c.set_editor_property("tag", tag("Company.NIE.Chicago"))
c.set_editor_property("title", unreal.Text("Chicago - No Intro"))
c.set_editor_property("campaign_psevdonim", unreal.Text("Чикаго (без заставки)"))
c.set_editor_property("description", unreal.Text("Original Chicago campaign without the helicopter intro. / Оригинальная кампания Чикаго без вертолётной заставки."))
EAS.save_loaded_asset(c, False)
c = EAS.load_asset(CMP)
REPORT["nointro"] = {"day_modifiers_before": before, "day_modifiers_after": after,
                 "company_tag": str(unreal.GameplayTagLibrary.get_tag_name(c.get_editor_property("tag"))),
                 "day0": c.get_editor_property("days")[0].get_path_name(), "day1": c.get_editor_property("days")[1].get_path_name(),
                 "n_days": len(c.get_editor_property("days")), "level_tag": str(unreal.GameplayTagLibrary.get_tag_name(c.get_editor_property("level_tag"))),
                 "title": str(c.get_editor_property("title")), "psevdonim": str(c.get_editor_property("campaign_psevdonim"))}
log("nointro done %s" % REPORT["nointro"])
