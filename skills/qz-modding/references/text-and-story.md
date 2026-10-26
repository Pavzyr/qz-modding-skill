# Тексты, реплики, интро, кампании — как устроено и как мод это меняет

Исследовано 2026-10-16 (пример — `scripts/examples/nointro_*`). [M] — проверено, [H] — гипотеза до проверки в игре.

## Где лежат тексты [M]
- Все реплики/интерфейс — **String Tables** `/Game/Tables/ST_*` (ST_Quests 115 строк сюжета Чикаго, ST_Miami_Quest 432, ST_Tutorial,
  ST_Onboarding, ST_HUD, ST_Menu, ST_Intro …). Namespace таблицы = её имя (`StringTableLibrary.get_table_namespace` → `ST_Quests`).
- Переводы: `QZSim/Content/Localization/Game/<culture>/Game.{po,locres}` (14 культур, native `en`). Поиск фразы: по `ru/Game.po`
  (`msgctxt "ST_Quests,<key>"`) — скрипт `scratch po_search` / `qz_locres.py dump`. Python с `-I` игнорирует PYTHONIOENCODING —
  для кириллицы в консоли `sys.stdout.reconfigure(encoding="utf-8")`.
- Реплики **озвучены**: `Sounds/Tutorial/S_Chapter_0001` + русская `L10N/ru/Sounds/Tutorial/S_Chapter_0001` → смена текста меняет
  субтитр, голос остаётся оригинальный.
- Пример: «Как спалось, юнец? Ты у нас новенький…» = `ST_Quests,01_Chapter_0001_Major` (EN «Sleep well, grunt?…»), квест
  `/Game/Blueprints/Quests/Act1/Day1/SM_MQ1_TheNewGuy` (Logic Driver state machine), source hash `f423dd21`.
- В Python кита: `unreal.TextLibrary.text_from_string_table(table, key)` (таблицу сначала `load_asset`); `KismetTextLibrary`/
  `KismetInternationalizationLibrary` называются `TextLibrary`/`InternationalizationLibrary`. В редакторе/commandlet `set_current_culture("ru")`
  НЕ подгружает игровую локализацию — русский текст так не проверить.

## Замена текста модом [H → проверить в игре]
- Мод несёт свою локализацию: в uplugin `"LocalizationTargets": [{"Name": "<Mod>", "LoadingPolicy": "Always"}]` и файлы
  `Content/Localization/<Mod>/<culture>/<Mod>.locres` + `<Mod>.locmeta`. UAT DLC-кук **кладёт их в .pak** [M] (`UnrealPak -List`;
  в utoc их нет — там только uasset). Записи: тот же namespace/key, **source hash из игрового Game.locres** (иначе движок игнорирует).
- Инструмент: `scripts/qz_locres.py` (`dump`, `build overrides.json`). Пишет locres v1 (Compact — без хэшей ключей), locmeta v2
  (как у игры: + uint32 0 в конце). Формат игры: locres v3 (CityHash64_UTF16), magic `0e147475674a03fc4a15909dc3377f1b`.
- Перекроет ли запись мода игровую при монтировании UGC — **не проверено** (исходников движка в ките нет). План Б — pak `_P` с
  целиком заменённым `Content/Localization/Game/<culture>/Game.locres` (неофициально, ломается с обновлениями игры).

## Интро (вертолёт, Чикаго) [M по данным, H в игре]
- Кампания `/Game/Data/Companies/Chicago/DA_CompanyChicago` (`QzCompanyDataAsset`, тег `Company.Main.Chicago`, `LevelTag Level.Chicago`,
  27 дней `Days/DAY_Chicago01..27` — `QzDayDataAsset` с instanced `modifiers`).
- Интро включает модификатор дня **`QzDayModifier_Intro`** `Config=(bIntro=True, IntroLevelName="IntroLevel")` в DAY_Chicago01
  (+ GameFlow условие `QzGameFlowCondition_HasIntro`). Старые конфиги `DaysConfigs/CampaignShortV2` (QzNewDayData, поле bIntro) —
  параллельная/старая система.
- Класс модификатора не экспортирован в Python, но элементы массива `modifiers` видны (`get_class().get_name()`), и массив можно
  переписать без него → интро нет [M: в ассете].
- В DLL зашиты теги `Company.Main.Chicago`, `.Endless`, `Company.Main.Miami` («The story campaign tag exists») → кампания мода под
  другим тегом может не получить сюжетно-специфичную логику [H]. Мод-кампании поддерживаются («Campaign %s skipped: its mod is not
  mounted»). Гайд кита: кампании — «Add new: Yes; Replace: key-based content only».
- Пример `NoIntroExample` (задание `scripts/examples/nointro_job.json` + `nointro_build.py`): копия кампании
  `DA_Company_NIE_Chicago` (тег `Company.NIE.Chicago`, title «Chicago - No Intro», pseudonym «Чикаго (без заставки)», day0 → копия
  дня без Intro, дни 2–27 оригинальные). Замена строк — `scripts/qz_locres.py`.

## Крэш первой версии мода [M]
Копия кампании (обычный кук) → игра падала на меню: «Bad name index» — класс кампании в ките новее, чем в игре
(поле CampaignPsevdonim). Пересборка `--versioned`; проверка в игре — следующий шаг. См. kit-facts «Кит новее игры».
