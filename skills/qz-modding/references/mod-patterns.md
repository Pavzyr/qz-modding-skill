# Как устроены реальные моды (разбор 2026-10-14)

> Уточнения после выгрузки схемы: `SWidgetRegistryDataAsset` и `LossConditionsDataAsset` — нативные классы игры
> (базовые: `/Game/Data/UI/DA_WidgetRegistry*`, `/Game/Data/DA_LossGame*`). Классов `*InspectionRules/RunRules/TabletLayout`
> в игре нет — это Blueprint'ы авторов модов (родителя выяснять при задаче). Для инструментов есть `QzManualGrantToolDataAsset` (0.9.4).
> Логика симптома в модах — поле `rule` (`QzSymptomFillingRule_*`: Animation, Decal, Dog, DoubleLayer, Electroshock, Material,
> OrganMaterial, OrganReplace, Other, TextureMaps, Worms) + свои GameplayAbility-BP. Все моды ниже — GameVersion 3 (устарели для 0.9.4).

Источник: 4 мода из закрытой игры на mod.io, скачаны с mod.io. Разобраны только индексы `.utoc` + `.uplugin` + tags ini (содержимое `.ucas` сжато Oodle, классы/поля ассетов не видны). Роли ассетов выведены **по именам** — это гипотезы, пока не подтверждены в редакторе.

| Мод | Автор | Размер | Файлов | Тип |
|---|---|---|---|---|
| MonstersInDisguiseToolkit (MIDT) | DENDRO STUDIOS | 42 МБ | 60 | 2 инструмента + 3 симптома |
| QZTest_Pipeline (SH, SafeHouse) | QZ Mod Team | 983 МБ | 1437 | тест-кампания + карта + скин доктора + шляпа |
| HalloweenInNeighborhood (HN) | DENDRO STUDIOS | 586 МБ | 3054 | кампания из 3 ночей + карта, зависит от MIDT |
| Jurassic | Castox | 431 МБ | 406 | тотальная конверсия: свой GameMode, UI, динозавры |

Списки файлов чужих модов в репозиторий не входят — получить самому: `python -I scripts/utoc_list.py <мод>.utoc`.

## Общая упаковка (одинакова у всех)
- zip: `<Name>.uplugin`, `Config/Tags/<Name>Tags.ini` (если есть теги), `Content/Paks/Windows/<Name>QZSim-Windows.{pak,utoc,ucas}`. Jurassic завернут в лишнюю папку `Jurassic_Windows/` — работает, но лучше без неё.
- Mount point: `../../../QZSim/Mods/<Name>/Content/` → мод разрабатывается в `QZSim/Mods/<Name>/`.
- В контейнере всегда: `UUGC_Metadata.uasset`, `ShaderArchive-<Name>-PCD3D_SM5/SM6.ushaderbytecode`.
- uplugin: `"Category": "UGC"`, `CanContainContent`, `ExplicitlyLoaded: true`, `EngineVersion "5.7.0-0+UE5-QZ"`, `GameVersion 3`.
- utoc: version 8, flags Compressed+Indexed (без шифрования), компрессия Oodle.

## Рецепт: новый симптом с логикой (MIDT)
```
Symptoms/<Name>/DA_Symptom_<PFX>_<Name>      — QzSymptomDataAsset, тег Symptom.Virus.<PFX>.<Name>
Symptoms/<Name>/BP_GA_<PFX>_<Name>           — Blueprint GameplayAbility: «custom logic» симптома (напр. вставляет клыки в рот, рисует укус на коже)
Symptoms/<Name>/BP_<PFX>_<Name>XRayMarker + SM_..XRay + M_..XRayMarker — отображение на рентгене («worms rule»)
Symptoms/<Name>/T_<PFX>_<Name>_Icon          — иконка в планшете
Symptoms/<Name>/SM_/T_ Albedo/Normal         — меши и текстуры (клыки M/F, укус на двух вариантах головы Head1/Head2)
```
- Своя категория в планшете: `DA_SymptomSection_<PFX>_<Name>` + теги `Symptoms.Section.<PFX>.<Name>` и `UI.Game.Tablet.Symptoms.<PFX>.<Name>`.
- Реакция на инструмент оформлена как «rule» симптома (CrucifixAversion срабатывает по electroshock reaction rule, т.е. и от базового шокера).
- Тестовый профиль посетителя для проверки: `Profiles/DA_Profile_<PFX>_<Name>Test`.

## Рецепт: новый инструмент (MIDT)
```
Tools/<Name>/DA_<PFX>_<Name>Tool   — QzToolDataAsset, тег Tool.<PFX>.<Name>
Tools/<Name>/ID_<PFX>_<Name>       — item definition
Tools/<Name>/BP_<PFX>_<Name>       — актор инструмента, наследник базового (QZTool_UVFlashLight / QzTool_Electroshock)
Tools/<Name>/DA_<PFX>_<Name>Data   — доп. данные инструмента
Tools/<Name>/T_<PFX>_<Name>_Wheel  — иконка в колесе инструментов
Tools/<Name>/SM_/M_/MI_/T_         — модель и материалы
Tools/<Name>/AM_/AS_ + CF_         — анимация реакции посетителя (montage/sequence), кривая (CF_PenLight)
Tools/<Name>/MPC_<PFX>_...         — Material Parameter Collection (тут: отключение UV-эффекта базового фонаря)
```
Ключевая идея: новый инструмент = наследник ближайшего базового инструмента + своя модель + свой эффект через симптом/rule.

## Рецепт: своя кампания на своей карте (HN, SafeHouse)
```
Data/Campaign/DA_Company_<PFX>          — кампания, тег Company.<PFX>.<Name>
Data/Campaign/Days/DAY_<PFX>_Night1..3  — конфиги дней
Data/Campaign/DA_Level_<PFX>            — QzLevelDataAsset, тег Level.<PFX>.<Name>, soft ref на карту
Data/DA_<PFX>_LossConditions            — условия поражения
Blueprints/Rules/BP_<PFX>_InspectionRules, BP_<PFX>_RunRules, BP_<PFX>_TabletLayout — правила проверки/забега и раскладка планшета
Data/Profiles/DA_Profile_<PFX>_*        — профили посетителей кампании
Maps/L_BuildPrototype_<Name>.umap       — главная карта (+ подуровни: Environment/Levels/Level_*_Residential, Assets/.../Level_SHC_House12)
UI/T_<PFX>_CampaignCard                 — картинка кампании в меню выбора
UI/Tablet/T_<PFX>_BaseRoad              — карта/фон в планшете
Blueprints/BP_<PFX>_Bed, BP_<PFX>_SpawnFacing, BP_BlackCat — интерактив уровня
```
- Окружение собрано из маркетплейс-паков (SHC_House12, Woodland, HalloweenPorch, Safe_House) → отсюда 0.5–1 ГБ.
- `EngineCopies/` — копии ассетов из `/Engine` (material functions, VolumetricClouds). Вероятно, нужны, т.к. engine-контент, не вошедший в кук игры, в мод автоматически не попадает. Учитывать при сборке карт.
- Межмодовые зависимости: HN использует симптомы/инструменты MIDT по тегам (mod.io dependency HN → MIDT → MIDC). Ссылки между модами — только через GameplayTags, не через жёсткие ссылки.
- Старые тестовые теги кочуют между модами (`Tool.SH.Crucifix` → `Tool.MIDT.Crucifix`) — при переносе менять тег.

## Рецепт: тотальная конверсия (Jurassic)
- Свои `BP_GameModeJurassic`, `BP_PlayerControllerJurassic`, пауны динозавров (`BP_Trex/Raptor/Pachy_Pawn`, ABP_*), `BPI_DinoCombat`.
- **UI в моде есть**: `WB_JurassicBase`, `WB_Jurassic_Inspection`, `WB_Upgrades_Jurassic`, `WBP_JLoadingScreen1` + `DA_WidgetRegistryJurassic(_2)` — похоже, игра берёт виджеты через WidgetRegistry data asset, и мод подменяет его своим. Это путь к UI-модам (не документирован).
- Свои `DA_Handbook_Jurassic`, `DA_MusicsJurassic`, `DA_YachtConfigJurassic`, `DA_ScannerPhaser` + `BP_ScannerPhaser/BP_ScannerDino`, симптомы `DA_Symptom_Disease_Trexing`, `DA_Symptom_Virus_Dinoitis`, `Enum_RunType_Dino`, кредиты `GM_Credits/DinoCredits`.
- Карты: `L_BuildDLC_Miami2.umap` (видимо, копия базовой Miami), `City_02_Environment1`, `L_Dino_Logic` (логика отдельным подуровнем).
- Папка `JankyFix/` — костыли автора; без `Config/Tags` (свои теги не объявлены — видимо, использует базовые/Company.Custom?).

## Рецепт: косметика посетителя (SafeHouse WitchHat)
`Cosmetics/WitchHat/DA_Hats_SH_WitchHat` + `SM_WitchHat` (static mesh — шляпы статичные, крепятся к сокету) + `M_` + `T_` (Basecolor/Normal/Roughness/Metallic/AO). Тег `Generator.DataKey.Accessory.Hat.DA_Hats_SH_WitchHat`. Через профиль кампании шляпу носят только нужные посетители.

## Рецепт: скин персонала (SafeHouse)
`Data/DA_TestDoctor` — `QzStaticNPCSkinDataAsset` с `NPC.Skin.Doc`, только override материалов (описание мода: «doctor material override»).

## Общие правила для всех рецептов (из kb-digest §5, §11, §12)
- **Duplicate базового DA, а не Create с нуля** — пустой ассет теряет скрытые дефолты/обязательные поля. У клона переписать самоссылки (теги, меш → материалы → BP — на свои копии).
- Новый контент — **новые уникальные теги/имена с префиксом мода рядом с ванилью**; базовые не удалять/не переименовывать.
- Подмена базового ассета тем же путём = замена всего определения во всех кампаниях; после обновления игры переприменять. Крайняя мера.
- Проверять, что контент **реально выбирается** генераторами/UI (профили, теги Generator.DataKey.*, реестры), а не только загружен.
- Полный набор на тип контента (иконка, тексты RU/EN, рентген-маркер для симптома, иконка колеса для инструмента и т.д.).
- Тест — на новой кампании/лаб-сейве; ссылки между модами — только через GameplayTags.
