# Факты о QZ ModKit

Корень: `<kit>` — папка, куда распакован QZ ModKit (~185 ГБ; скрипты находят её сами, переопределение — env `QZ_KIT`). **Версия 0.9.4** (`KIT_VERSION.txt`: «MODIO 9a4ff618fa (NewTech merged into MODIO; mod GameVersion 4)», 2026-10-14).
Патч 0.9.2→0.9.4 применён 2026-10-14 18:07; бэкап и откат: `_patch_backup/0.9.4/` (`rollback/ROLLBACK_PATCH.bat`, 2.77 ГБ).
Бэкап содержит прежний `QZSim.uproject` пользователя (с PythonScriptPlugin/RemoteControl) — патч его заменил.

## Состав
- `Engine/` — UE **5.7.4**, ветка `UE5-QZ`, installed build (без исходников, C++ не собрать). `UnrealEditor.exe`, `UnrealEditor-Cmd.exe`, `UnrealPak.exe`, `Build/BatchFiles/RunUAT.bat`, Python 3.11.
- `QZSim/QZSim.uproject` — EngineAssociation `5.7qz`. Модули игры только бинарниками.
- `QZSim/Content/Data` (15 МБ) — главное для модов; остальное — референс.
- `QZSim/Plugins/ModioUGC` — Create UGC / Package UGC; `QZSim/Mods/` — моды-исходники (сейчас пусто).
- `QZSim/Releases/BaseGameRelease/Windows/AssetRegistry.bin` — база для DLC-кука модов.
- Гайды: `MODDING_GUIDE.md` (EN, 0.9.4 — актуальный), `GUIDE_SKIN_MOD_RU.md` (0.9.4), `MODDING_GUIDE_RU.md` (**устарел: 0.9.2, GameVersion 2** — верить EN).
- `KitTools/qz_dump_schema.py` + `Run_QZ_SchemaDump.bat` — простой дамп (появились до 0.9.4, не от патча); мой расширенный — `scripts/qz_deep_dump.py`.

## Версии
- `DefaultGame.ini [/Script/ModioUGC.ModioUGCSettings] RequiredModGameVersion=4` → мод должен иметь `"GameVersion": 4`.
- Моды из mod.io (13–14.10) имеют GameVersion 3 → игра с апдейтом 0.9.4 их отклонит («Mods need an update»), авторам нужно перепаковать.
- Manual Grant инструментов и тайминг замен инструментов работают в игре только после апдейта игры, вышедшего с китом 0.9.4.
- `[/Script/QZSim.QzGameSettings] bAutoIncludeUGCSymptoms=True, bAutoGrantUGCTools=True`.

## Запуск и автоматизация (проверено)
- **Saved-папка проекта**: `%LOCALAPPDATA%\QZSim\Saved\` (из-за `-Installed`), логи редактора: `...\Saved\Logs\QZSim.log`. Кэш реестра: `QZSim/Intermediate` (~0.5 ГБ).
- **Commandlet** (`UnrealEditor-Cmd.exe QZSim.uproject -Installed -run=pythonscript -script="<py> <args>" -unattended -nosplash -stdout`):
  быстро (~1–3 мин), годится для чтения схемы/ассетов `/Game`. **UGC-провайдер выключен** («Skipping UGC initialization ... commandlet») →
  моды из `QZSim/Mods` НЕ монтируются, `/<Mod>/` пути «does not map to a root». Шаблонов Create UGC в этом режиме тоже нет.
- **Полный редактор** (`UnrealEditor.exe QZSim.uproject -Installed -ExecutePythonScript="<py> <args>" -unattended -nosplash -log`):
  при старте монтирует `QZSim/Mods/*` («Mounted mod source 'X' ... for editing»), **но только плагины, которые уже были на диске**.
  Добавленный во время сессии плагин через `UGCSubsystem.add_ugc_from_path` — «Added», но не mounted → нужен перезапуск
  (совпадает с гайдом 0.9.4: «mod folder copied by hand needs an editor restart»). Редактор **сам закрывается**, когда скрипт вернулся
  (`Cmd: QUIT_EDITOR`) → всё делать синхронно. ~2.5 мин на запуск. Python включается принудительно, плагин в uproject не нужен.
- uplugin без `EngineVersion` → `LogModioUGC: Warning: uplugin missing engine version` и мод не добавляется.
- **Кит новее игры → крэш игры при старте** [M 2026-10-16]: в ките 0.9.4 у `QzCompanyDataAsset` есть поле `CampaignPsevdonim`, в exe игры
  (ветка modio, release 2.0.0.2544) его нет. Обычный кук пишет свойства БЕЗ имён (unversioned) по схеме класса кита → игра читает
  мусор: `Fatal error … AsyncLoading2.cpp … ObjectSerializationError: /<Mod>/…/DA_X - QzCompanyDataAsset …: Bad name index`, падение
  на главном меню (меню сканирует кампании), игра «не запускается». Скины (QzStaticNPCSkinDataAsset) совпадают — их это не задело.
  Профилактика: перед упаковкой ассета игрового класса сверить имена полей класса в `QZSim-Win64-Shipping.exe` игры и в
  `UnrealEditor-QZSim.dll` кита (строки ASCII/UTF-16); при расхождении — `qz_package.py <Mod> --versioned` (UAT `-VersionCookedContent`,
  свойства с именами — незнакомые игра пропускает) [H: загрузка versioned-пакета игрой ещё не проверена]. Лог падения — в
  `QZSim-backup-*.log` (текущий QZSim.log перезаписывается следующим запуском) и `%LOCALAPPDATA%/QZSim/.sentry-native/*.run/__sentry-event`.
  Лог игры и лог кита — ОДИН файл: любой запуск редактора вытесняет игровой лог → читать лог игры сразу после её запуска.
- **`UUGC_Metadata.io_store_enabled` (bIoStoreEnabled) = false** → в игре мод находится, монтируется и сразу выгружается:
  `LogModioUGC: Error: bUseIoStore values mismatch between UGC (FALSE) and Base Game (TRUE). This UGC will not be mounted.`
  Мастер Create UGC кита оставляет false (флаг ставит, видимо, кнопка Package UGC); наш UAT-кук его не трогает. [M 2026-10-16]
  Лечение: задание `{"op":"set","path":"/<Mod>/UUGC_Metadata","props":{"io_store_enabled":true}}`; qz_validate_mod
  теперь FAIL, если в UUGC_Metadata.uasset нет строки `bIoStoreEnabled` (false не сериализуется).
- Код возврата редактора/commandlet часто 1 из-за ошибок базовой игры в логе («Duplicate appearance registry key ... OutfitColor»,
  ConsoleManager повторы) — не признак провала, смотреть свой отчёт.
- **UAT DLC-кук** (то, что делает Package UGC; строки из ModioUGCEditor.dll + проверено):
  `RunUAT.bat BuildCookRun -project=<uproject> -noP4 -clientconfig=Shipping -serverconfig=Shipping -installed -platform=Win64 -target=QZSim
   -SkipCookingEditorContent -cook -stage -pak -iostore -unattended -utf8output -nocompile -nocompileeditor -skipbuild
   -DLCName=<Mod> -basedonreleaseversion=BaseGameRelease -stagingdirectory=<dir>` → BUILD SUCCESSFUL ~1 мин,
  результат `<dir>/Windows/QZSim/Mods/<Mod>/{<Mod>.uplugin, Content/Paks/Windows/<Mod>QZSim-Windows.{pak,utoc,ucas}}`.
  Кук оставляет `QZSim/Mods/<Mod>/Saved/Cooked` — не отправлять. Config/Tags в staging не попадает — копировать самому (qz_package делает).
  Запускать через PowerShell/`cmd /c` с полным путём (из Git Bash `cmd //c RunUAT.bat` не находит файл).
  Шейдер-архив (`ShaderArchive-*.ushaderbytecode`) появляется, только если в моде есть свои материалы с новыми шейдерами.
- Python API (подтверждено `qz_probe_api.py`): `UGCTemplateSubsystem.create_ugc_from_template/get_templates`,
  `UGCSubsystem.add_ugc_from_path/refresh_ugc/get_rejected_mods/is_ugc_compatible`, `PluginBlueprintLibrary.is_plugin_mounted/get_plugin_base_dir`,
  `BlueprintEditorLibrary.create_blueprint_asset_with_parent/compile_blueprint/add_member_variable` (граф нодов из Python не собрать),
  `EditorAssetSubsystem.*`, `AssetTools.import_asset_tasks`, `MaterialEditingLibrary`, `Exporter.run_asset_export_task`.
  GameplayTag из Python: `t = unreal.GameplayTag(); t.import_text('(TagName="A.B")')`; печать — `GameplayTagLibrary.get_tag_name(t)` (str() даёт `{}`).
- FBX-экспорт: `UE4_Mannequin` — ок (1 МБ). Меш MetaHuman-одежды (`Female_MediumAverage_Bra_01`) — **краш редактора** (MeshMergeUtilities, array OOB) даже без LOD.

## Железо пользователя
RTX 4070 Laptop 8 ГБ, **16 ГБ ОЗУ**, C: свободно ~180 ГБ (минус ~3 ГБ бэкап патча). Не запускать редактор и UAT одновременно.

## Официальные возможности модов (гайд 0.9.4)
| Что | Добавить | Заменить |
|---|---|---|
| Внешность посетителей (`QzGeneratorParentPrimaryData`-наследники) | да, вес спавна на ассете | тот же ключ + `generator_data_source = Mod` |
| Скины персонала `QzStaticNPCSkinDataAsset` (`npc_tag`, `mesh`, `materials: Map[int, Material]`) | — | `NPC.Skin.Doc/Usmon/UsmonWhite/Military/Scientist` |
| Симптомы `QzSymptomDataAsset` | да, во все кампании | тот же `Symptom.*` |
| Инструменты `QzToolDataAsset` (`tag`, `item_data_asset`) | да, авто-выдача с начала дня; или `QzManualGrantToolDataAsset` + Blueprint «Get Game Flow → Add Tools» | тот же `Tool.*`, выдаётся когда кампания выдаёт базовый |
| Карты `QzLevelDataAsset` (`tag`, `level` soft ref, `level_name`) | да | — |
| Профили, кампании (`QzCompanyDataAsset`), багаж, контрабанда, справочник | да | по ключу |

## Где лежат базовые ассеты
- Внешность: `/Game/Data/GeneratorApperance/*` (1720). Ключи `Generator.DataKey.<Cat>.<Sub>.<AssetName>` (`Config/Tags/Generator.ini`).
- Симптомы: `/Game/Data/Symptoms/Items/*` (73 `QzSymptomDataAsset`), секции `Symptoms/Sections` (12).
- Инструменты: `/Game/Data/Tools/DA_*` (12) + акторы `/Game/Blueprints/Tools/<Name>/BP_*, ID_*` (`ID_*` = `SItemDataAsset`).
- Уровни: `/Game/Data/Levels/DA_Level{Chicago,Miami}` (Miami: `level_name=L_BuildDLC_Miami`, `level` пустой).
- Кампании: `/Game/Data/Companies/*` (6 `QzCompanyDataAsset`), дни `QzDayDataAsset`/`QzNewDayData`, правила дней `QzDayRules`.
- Поражение: `/Game/Data/DA_LossGame*` (`LossConditionsDataAsset`, условия `LossConditionMoney/NPCKill/...`).
- UI: `/Game/Data/UI/DA_WidgetRegistry*`, `DA_MenuRegistry`, `DA_DefenseRegistry` (`SWidgetRegistryDataAsset`) — так Jurassic подменял UI.

## Скелеты
- Одежда/тела посетителей: `/Game/MetaHumans/Common/Female/Medium/NormalWeight/Body/metahuman_base_skel` (405 использований в выборке; у мужских — свои пути, проверять у конкретного DA через `inspect`).
- Персонал/манекены: `/Game/Art/Characters/RP_Character/00_rp_master/Mannequin/UE4_Mannequin_Skeleton` (меш `UE4_Mannequin`, слоты `M_UE4Man_Body`, `M_UE4Man_ChestLogo`).
- Руки FP: `.../FlashLightFPPack/.../SK_Mannequin_Arms_Skeleton`. Полный список — `schema/content-index.md`.
- Какой меш у конкретного NPC персонала (доктор и т.д.) — ещё не найдено (TODO в notes).

## Игра (2026-10-15)
- `<Steam>\steamapps\common\Quarantine Zone The Last Check\` (appid 3419520). Ветка `public` (buildid 24591723) —
  без поддержки модов. С 2026-10-15 пользователь на ветке **`modio`** (buildid 25938414): ModioUGC есть, **требует GameVersion ≥ 3**
  (кит 0.9.4 ставит 4 — проходит). Моды: `QZSim\Modio\<папка>\<Name>.uplugin`. В Binaries\Win64 стоит UE4SS (не трогать).
  Проверка поддержки модов: в логе `LogPluginManager: Mounting Project plugin ModioUGC` и `LogModioUGC: Searching for UGC plugins`.

## Язык игры (2026-10-22)
- Язык: `GetCurrentLanguage`/`GetCurrentCulture` (pure). Культуры игры: de, en, es, es-419, fr, it, ja, ko, pl, pt-BR, ru, tr, uk, zh-Hans.
