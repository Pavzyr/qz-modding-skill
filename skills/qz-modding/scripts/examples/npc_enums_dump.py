# job "py" op (read-only): enumerator lists of the enums used in QzNPCData -> REPORT["enums"]
NAMES = ["QzGender", "QzNpcRole", "QzBehaviorPattern", "QzRaceType", "QzNPCBodyShape", "QzSkinPigmentationType", "QzBaggageContainerType",
         "QzSourceProfile", "QzVoiceType", "QzNPCEvent", "QzProfileFlags", "QzHiddenContrabandLocation", "QzNPCKillReason", "QzOrganType",
         "QzAnimationFlag", "QzCvNPCState", "QzCharacterAgeVisualCategory", "QzHairColorType"]
REPORT["enums"] = {}
for n in NAMES:
    e = getattr(unreal, n, None)
    try:
        REPORT["enums"][n] = [str(m.name) for m in sorted(list(e), key=lambda m: m.value)] if e else None
    except Exception as ex:
        REPORT["enums"][n] = "err %s" % ex
