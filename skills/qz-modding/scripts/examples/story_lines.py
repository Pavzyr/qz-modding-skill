"""Collect every line of a story character from the game's localization (Game.po, en + ru).
  python -I story_lines.py <speaker regex> [out.json]
Keys of the string tables carry the speaker as a suffix/part (e.g. ST_Quests,01_Chapter_0001_Major). Writes
[{key, en, ru}] in key order (= roughly the story order) and prints a summary."""
import json, os, re, sys, collections

KIT = os.environ.get("QZ_KIT") or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5))
LOC = os.path.join(KIT, "QZSim", "Content", "Localization", "Game")
PO_RE = re.compile(r'msgctxt "([^"]+)"\s*\nmsgid "((?:[^"\\]|\\.)*)"\s*\nmsgstr "((?:[^"\\]|\\.)*)"')


def po(path):
    t = open(path, encoding="utf-8").read()
    return {m.group(1): (m.group(2).replace('\\"', '"').replace("\\n", "\n"), m.group(3).replace('\\"', '"').replace("\\n", "\n"))
            for m in PO_RE.finditer(t)}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    pat = re.compile(sys.argv[1] if len(sys.argv) > 1 else "schultz|shultz", re.I)
    en, ru = po(os.path.join(LOC, "en", "Game.po")), po(os.path.join(LOC, "ru", "Game.po"))
    keys = sorted(k for k in en if pat.search(k))
    print("keys:", len(keys), collections.Counter(k.split(",")[0] for k in keys))
    rows = [{"key": k, "en": en[k][0], "ru": ru.get(k, ("", ""))[1]} for k in keys]
    if len(sys.argv) > 2:
        json.dump(rows, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in rows[:15]:
        print(r["key"], "|", r["en"][:80], "|", r["ru"][:80])
    mk = [k for k in en if k.startswith("ST_Miami_Quest,")]
    print("Miami keys:", len(mk), collections.Counter(re.sub(r".*_", "", k) for k in mk).most_common(30))
