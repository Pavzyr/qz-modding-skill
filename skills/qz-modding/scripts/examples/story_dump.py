"""Dump a campaign's string table in quest order: python -I story_dump.py ST_Miami_Quest [ru|en] > out.txt
Keys look like SQM_<quest>_<Speaker>_<n> (order of speakers inside a quest is not stored in the key)."""
import os, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from story_lines import po, LOC

sys.stdout.reconfigure(encoding="utf-8")
table = sys.argv[1] if len(sys.argv) > 1 else "ST_Miami_Quest"
lang = sys.argv[2] if len(sys.argv) > 2 else "en"
en, ru = po(os.path.join(LOC, "en", "Game.po")), po(os.path.join(LOC, "ru", "Game.po"))
src = en if lang == "en" else {k: (v[1], v[1]) for k, v in ru.items()}
keys = [k for k in en if k.startswith(table + ",")]


def sortkey(k):
    name = k.split(",", 1)[1]
    nums = [int(x) for x in re.findall(r"\d+", name)]
    return (nums[0] if nums else 999, name.split("_")[2] if name.count("_") >= 2 else "", nums[1:] if len(nums) > 1 else [])


groups = collections.OrderedDict()
for k in sorted(keys, key=sortkey):
    name = k.split(",", 1)[1]
    m = re.match(r"([A-Za-z]+_\d+)_(.*)", name)
    g = m.group(1) if m else "misc"
    groups.setdefault(g, []).append((m.group(2) if m else name, src[k][0].replace("\n", " ")))
for g, rows in groups.items():
    print("=== %s" % g)
    for who, t in rows:
        print("  %s: %s" % (who, t))
