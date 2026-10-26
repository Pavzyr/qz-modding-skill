# qz-modding — Claude Code skills for Quarantine Zone: The Last Check

Two [Claude Code](https://claude.com/claude-code) skills that let Claude build, inspect and package mods for
**Quarantine Zone: The Last Check** with the official **QZ ModKit** (UE 5.7, mod.io UGC) — mostly without opening the editor GUI.

| Skill | What it does |
|---|---|
| `qz-modding` | Main skill: kit facts, game class schema, patterns from real mods, headless job runner (create mod, import, duplicate, data assets, Blueprint children), packaging to the mod.io layout, validation, `.utoc` listing, `.locres` text editing, Blueprint node paste generation, PIE probes, Blender helpers, example mods. |
| `george_replace` | Step-by-step pipeline: your own GLB model (Tripo / AI / Blender) → fitted to the game skeleton in headless Blender → reimported → packaged → installed as the doctor (Georgie, `NPC.Skin.Doc`) skin. Every step has a check gate. |

Example mods in `skills/qz-modding/scripts/examples/`: **NoRaid**, **NoJacketsAuto**, **VisitorTalk** (Blueprint logic + UI),
**NoIntroExample** (campaign copy without the intro).

## Requirements
- Windows, QZ ModKit **0.9.4** (`KIT_VERSION.txt`; mod `GameVersion` 4). Other versions: re-check `references/kit-facts.md`.
- Python 3.10+ on PATH (stdlib only; `numpy` for `scripts/vtf_to_png.py`). Blender scripts use Blender's bundled Python.
- Blender 4.x/5.x — optional, only for model work.
- Claude Code.

## Install
1. Copy the folders from `skills/` into `<kit>/.claude/skills/` (`<kit>` = folder containing `QZSim/QZSim.uproject`):
   ```
   <kit>/.claude/skills/qz-modding/
   <kit>/.claude/skills/george_replace/
   ```
2. Start Claude Code in `<kit>` and ask, e.g. *"make a mod that disables raids"* or *"replace the doctor with this .glb"*.
3. Optional environment variables:
   - `QZ_KIT` — kit path, if the scripts cannot find it from their own location;
   - `QZ_MODS_OUT` — where `qz_package.py` writes builds (`$QZ_MODS_OUT/<Mod>/Builds/`); default `<kit>/ModBuilds/<Mod>/`.
4. Generate the local schema references once (they are built from your kit and are not shipped):
   run `scripts/qz_deep_dump.py` (commandlet, see `references/kit-facts.md`), then `python -I scripts/build_schema_refs.py`
   → `references/schema/samples.md` and `content-index.md`.

## Notes
- Mods are always created in `QZSim/Mods/<Mod>/`, never in `/Game`. Close the editor and the game before running jobs.
- The skill never publishes anything; you upload to mod.io yourself.
- Skins: adult characters only, no real people; follow mod.io and game rules.
- The skill keeps a local journal in `references/notes.md` — it starts empty.
- Skill texts are in Russian; Claude answers in your language.

## License
MIT — see `LICENSE`. Third-party notices — `THIRD_PARTY.md`. Not affiliated with the game's developers.

---

## По-русски
Два скилла для Claude Code: **qz-modding** (основной: факты кита, схема классов игры, рецепты, сборка мода заданиями без GUI,
упаковка в раскладку mod.io, проверка, тексты, вставка узлов Blueprint, Blender-скрипты, примеры модов) и **george_replace**
(своя GLB-модель вместо доктора Джорджи — от файла до установленного мода, с проверками на каждом этапе).

Установка: скопировать папки из `skills/` в `<кит>/.claude/skills/`, запустить Claude Code в папке кита.
Нужно: QZ ModKit 0.9.4, Python 3, Blender (по желанию). Переменные: `QZ_KIT` (путь к киту), `QZ_MODS_OUT` (куда класть сборки).
Справочники `samples.md` и `content-index.md` генерируются у себя: `qz_deep_dump.py` → `build_schema_refs.py`.
Публикует моды только сам пользователь. Скины — только взрослые персонажи, без реальных людей.
