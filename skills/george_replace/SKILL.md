---
name: george_replace
description: Замена модели доктора Джорджи (скин NPC.Skin.Doc) в Quarantine Zone на свою модель из Tripo/AI/Blender (GLB) — от файла пользователя до установленного мода в игре. Используй, когда пользователь даёт .glb и хочет увидеть его вместо Джорджи, обновить свой мод-скин доктора, проверить модель перед игрой. Полностью без GUI: headless Blender + фоновый редактор кита. Подробности и грабли — в qz-modding (references/tripo-to-game.md).
---

# george_replace — своя модель вместо Джорджи

Проверено на ките 0.9.4 (модель Tripo ~49k tris, одна BaseColor-текстура). Отвечать на языке пользователя.
Полный разбор этапов и 40+ ошибок, на которых это построено: `qz-modding/references/tripo-to-game.md` — прочитать перед первым запуском в сессии.

Пути (спросить у пользователя, если неизвестны): кит `$KIT` (папка с `QZSim/QZSim.uproject`), папка для моделей `$ART`,
Blender `$BL` (путь к `blender.exe`), скрипты qz-modding `$QZ=$KIT/.claude/skills/qz-modding/scripts`,
этого скилла `$GR=$KIT/.claude/skills/george_replace`, папка игры `<игра>` (Steam → Quarantine Zone The Last Check).
Мод — `$MOD` (например `MyDocSkin`), префикс `<PFX>`; имена ассетов ниже — `SK_MyChar`, `M_MyChar`, `T_MyChar_*`, `DA_<PFX>_DocSkin`.

## Правила (не нарушать)
- UnrealEditor и игра **закрыты** перед этапами 5–8 (`tasklist`); Blender пользователя не трогать — только `--background --factory-startup`.
- Каждая модель — в **свою папку** `$ART/<vN>/` (копия GLB под новым именем; исходник пользователя не трогать и не перезаписывать).
- Ничего не сохранять в /Game; на «regenerate/save Skeleton» — нет. Бэкап Content+uplugin мода перед реимпортом.
- В папку игры писать с согласия пользователя (запрос «сделай патч/поставь в игру» = согласие на этот прогон).
- Персонаж — только взрослый, не реальный человек. Публикация на mod.io — только пользователь.
- Каждый этап заканчивается **воротами**; не прошли — чинить, а не идти дальше.

## Этапы
**0. Файл.** Если имя `*.crdownload` — загрузка не закончена, ждать файл без этого суффикса.
`mkdir $ART/<vN>`; `cp <glb> $ART/<vN>/<name>_<vN>.glb`;
`python -I $GR/scripts/inspect_glb.py <glb>` → **VERDICT OK**. BLOCKED «no UV / no base colour» = модель выгружена без
текстуры (в Tripo серый вид) → попросить перевыгрузить с текстурой, ничего не делать дальше. tris 15k–120k (норма ~50k: Quad 25000).
Эталон: FBX меша доктора `D2_Zheka` со скелетом `D1_Usmon_Skeleton` в `$ART/D2_Zheka.FBX` (один раз — op `export` в задании, см. tripo-to-game §1).

**1. Конфиг.** Скопировать `$GR/templates/config_fit.template.json` → `$ART/<vN>/auto/config_fit.json`, заменить `<ART>`/`<vN>`/`<model>`;
копия с `"stage": "all"` → `config_all.json`. `material_name` = имя слота меша, уже импортированного в UE (при первом импорте — убрать).

**2. Подгонка.** `$BL --background --factory-startup --python $QZ/blender/auto_fit_skin.py -- config_fit.json`
Ворота: открыть `auto/1_fit_front.png`, `2_fit_side.png` — руки/ноги модели вдоль красного эталона; в отчёте stretch рук 0.9–1.3,
`arm_z_vs_shoulder` ≈ 0; `hair_verts` > 0 если волосы светлые. Разметку волос при сомнении проверить рендером (светлая кожа/одежда не
должны попасть; тёмные/цветные волосы не определяются → `"hair": false` или порог).

**3. Привязка + экспорт.** То же с `config_all.json`. Затем:
- нет Normal/RoughMetal в GLB → `python -I $GR/scripts/flat_maps.py $ART/<vN>/textures T_MyChar 0.7`;
- `$BL --background --factory-startup --python $GR/scripts/pose_check.py -- <fbx> <textures>/T_MyChar_BaseColor.jpg <auto>/check`
  → **VERDICT OK** и глазами `check/pose_grid.png` (6 поз спереди/сбоку; сидение важно — доктор в игре сидит на стуле);
- `python -I $QZ/fbx_tree.py <fbx> $ART/D2_Zheka.FBX` → LimbNode 119 = 119, расхождений 0.
Если пользователь сам правил веса и экспортировал — сверить и почистить `$QZ/blender/clean_user_export.py` (см. tripo-to-game §4).

**4. (по желанию) Пользователь смотрит в Blender**: `$QZ/blender/check_in_blender.py` (FBX/BASECOLOR в начале файла).

**5. UE.** Первый раз: мод создаётся заданием с `create_mod` + `import` (меш на `D1_Usmon_Skeleton`, текстуры), `create_asset` для
data-ассета скина (дубликат скина доктора из игры, `npc_tag NPC.Skin.Doc`) — см. qz-modding `mod-patterns.md`.
Повторно (реимпорт): бэкап `cp -r $KIT/QZSim/Mods/$MOD/{Content,$MOD.uplugin} <папка бэкапов>/$MOD_before_<vN>_<дата>/`.
Задание из `$GR/templates/ue_job.template.json` (путь к `reimport_keep_settings.py` — абсолютный) → `python -I $QZ/qz_run_job.py <job.json>` (2.5–4 мин).
Ворота (отчёт `reimport.after` + `inspect`): скелет `D1_Usmon_Skeleton`, слот → `/$MOD/M_MyChar`, `M_MyChar.two_sided True`,
Normal: sRGB false + flip green; RoughMetal sRGB false; `DA_<PFX>_DocSkin`: npc_tag NPC.Skin.Doc, mesh SK_MyChar, materials {0: M_MyChar};
bounds z ≈ 94 см.

**6. PIE.** `$KIT/Engine/Engine/Binaries/Win64/UnrealEditor.exe $KIT/QZSim/QZSim.uproject -Installed -ExecCmds="py $QZ/probes/qz_pie_doc.py" -unattended -nosplash`
(~3 мин) → `%LOCALAPPDATA%/QZSim/Saved/ModSchema/deep/pie_doc.json`: `BP_Doc_C_0` → `/$MOD/SK_MyChar`, anim `ABP_Doc_C`;
в `QZSim.log` 0 строк `missing bones that SkeletalMesh`.

**7. Сборка.** uplugin: `Version`+1, `VersionName` (1.1 → 1.2…), должны быть `EngineVersion 5.7.0-0+UE5-QZ`, `GameVersion 4`,
`ExplicitlyLoaded true` (UTF-8 без BOM). `python -I $QZ/qz_validate_mod.py $MOD` → `python -I $QZ/qz_package.py $MOD`
→ RESULT OK; `python -I $QZ/utoc_list.py <...>.utoc` — есть меш, physics, DA, M_, текстуры + ubulk, metadata, ShaderArchive.

**8. Установка.** Игра закрыта → `rm -rf "<игра>/QZSim/Modio/$MOD"` → копия сборки (`$QZ_MODS_OUT/$MOD/Builds/$MOD/` или
`$KIT/ModBuilds/$MOD/$MOD/`) туда. Пользователь перезапускает игру. Не видно модель → `%LOCALAPPDATA%\QZSim\Saved\Logs\QZSim.log`:
`Added UGC plugin '$MOD'`, нет `bUseIoStore values mismatch` / `below required` / `missing engine version`.

**9. Запись.** Строка в `qz-modding/references/notes.md` (дата, vN, ворота, что нового); новые грабли — в tripo-to-game.md.

## Откат
`<папка бэкапов>/$MOD_before_<vN>_*` → обратно в `QZSim/Mods/$MOD/`, пересобрать (этап 7–8). Удалить мод из игры — папка `QZSim\Modio\$MOD`.

## Если ворота не проходят (быстрый указатель)
| Симптом | Куда смотреть |
|---|---|
| BLOCKED no UV / нет текстуры | перевыгрузить из Tripo с текстурой |
| руки/ноги не в эталоне | поза не T? A-поза → проверить fit-рендеры, отчёт arms |
| иглы/лоскуты в pose_grid | `pose_check.json` по позам; `auto_fit_skin.py`: маски конечностей, волосы, юбка ниже паха, цепочка ног |
| текстура «лоскутами» в игре | текстуры не из того же GLB → этап 3 заново |
| модель в 100× / «Failed to merge bones» | масштаб/имя `root` → fbx_tree, tripo-to-game §3 |
| в игре прежний Джорджи | лог игры: bUseIoStore / uplugin поля / игра не перезапущена |
| дыры в модели | `M_MyChar.two_sided` |
