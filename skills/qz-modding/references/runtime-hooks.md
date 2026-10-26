# Рантайм-логика в модах QZ: взаимодействие, ввод, NPC, точки входа (исследование 2026-10-14, кит 0.9.4)

Источник: выгрузки `%LOCALAPPDATA%\QZSim\Saved\ModSchema\deep\` (npc_probe2.json, sig_probe.json, widget_probe*.json,
pie_probe*.json, misc_probe.json) + PIE-прогоны. Уровни: [S] статически, [M] измерено в PIE, [H] гипотеза.

## 1. Главное ограничение: логику Blueprint нельзя собрать скриптом [S]
- Python кита умеет: создавать BP (`create_blueprint_asset_with_parent`), переменные (`add_member_variable`, типы через
  `get_basic_type_by_name/get_array_type/get_object_reference_type`), значения CDO после compile, `remove_graph`, `reparent_blueprint`,
  `compile_blueprint`. **Узлы графа создавать/связывать нельзя** (нет API: проверены BlueprintEditorLibrary, все *Graph*/K2*/Node*;
  KismetEditorUtilities, KismetNodeHelperLibrary, KismetSystemLibrary в Python отсутствуют).
- Рабочий путь (выбран пользователем): я генерирую **текст узлов для вставки** (формат копирования узлов UE: `Begin Object Class=/Script/BlueprintGraph.K2Node_...`),
  пользователь в редакторе открывает BP → кликает в граф → Ctrl+V → Compile → Save. Всё остальное (ассеты, переменные, виджеты, DA) — скриптом.
- **Экспорт узлов в текст работает** [M]: `unreal.AssetExportTask(object=<EdGraphNode>, filename=*.copy|*.t3d, automated=True)` +
  `unreal.Exporter.run_asset_export_task` → ровно формат Ctrl+C/Ctrl+V узлов. Узлы BP перечисляются `unreal.ObjectIterator(unreal.EdGraphNode)`
  по префиксу `<bp path>:`. Графы базовых BP в ките есть (не вырезаны). → Библиотека настоящих узлов игры для сборки текста вставки
  (probes/qz_probe_nodeexport.py, scripts/qz_node_harvest.py). Импорта текста в граф из Python нет — вставляет человек.
- BP_HatBase имеет свои BeginPlay и Tick → в наследнике переопределять BeginPlay только с узлом Parent: BeginPlay.
- Нативных «показать текст по кнопке» способностей нет (проверены все классы с Text-полями).

## 2. Виджеты (UMG) скриптом — можно, через копию [M в commandlet, в памяти]
- `WidgetBlueprintFactory` новый WBP создаёт **без корня**; `WidgetTree.RootWidget` и `RootWidgetClass` защищены (protected) — задать нельзя.
- `unreal.find_object(wbp, "WidgetTree")` даёт дерево; `unreal.new_object(unreal.CanvasPanel, tree, "Имя")` создаёт виджеты;
  `add_child_to_canvas / add_child_to_vertical_box / set_content`, `slot.set_anchors/set_alignment/set_position/set_auto_size`, `TextBlock.set_text`.
- Обход: **duplicate_asset игрового WBP с корнем** (напр. `/Game/UI/Quests/WBP_QuestInteractText`: SizeBox_0 → Text_Main) →
  `remove_graph(find_event_graph)` → `reparent_blueprint(dup, unreal.UserWidget)` → `root.set_content(свой CanvasPanel)` → свои Border/VerticalBox/TextBlock → compile. Работает.
- Список виджетов WBP: перебор `unreal.ObjectIterator(unreal.Widget)` по префиксу пути `<wbp>:WidgetTree.`.
- `GetWidgetFromName` в UE 5.7 **не BP-функция** (только C++-экспорт) [S, DLL]. Виджеты, созданные `new_object`, **не становятся переменными**
  класса WBP (bIsVariable protected) [M]; переменными остаются только виджеты исходного WBP (у WBP_QuestInteractText: `Text_Main`, `SizeBox_0`).
  → из графа обращаться к унаследованным переменным-виджетам (их можно перецепить в своё дерево) или к самому UserWidget.
- Флаги/параметры UFUNCTION читаются из DLL: `scripts/ufunc_flags.py <dll> Func` (pure/static/const, имена параметров) [M].

## 3. Система взаимодействия игры (S-фреймворк) [S]
- Игрок: `BP_CharacterBase_C` (← SCharacter). Компоненты: SContextMonitorComponent, SAbilitySystemComponent, SContextActionsComponent,
  SInventoryComponent, SEquipmentManagerComponent, SWheelComponent, SPlayerControlsComponent… Набор способностей `AS_Player`.
- `SCharacter.get_actor_in_focus()` → актор под прицелом (BP-callable).
- Интерактивный актор = `SFocusComponent` (`max_distance`, `ability_set`, required/blocking_tags, `set_enable`) +
  `SContextActionsComponent` (`fragments: Array[SContextFragment]`, `title_fragment`, `set_override_text_fragment(class, text)`; функции добавления фрагмента нет)
  + часто `SHighlightComponent`. При фокусе `ability_set` фокус-компонента выдаётся игроку; способности в нём привязаны к `input_tag`.
- Примеры: доктор `BP_Doc` focus.ability_set=`AS_Doc` (GA_DocLoveInteract на `Player.Input.Interact`, фрагмент QzContextFragment_LoveInteract);
  шляпы `BP_HatBase` → `AS_ClothesClick`; предметы на NPC `BP_BaggageAttachment` → `AS_Attachment` (focus 2000); квестовые `BP_QuestInteractable` → `AS_QuestActorInteract`.
- `SAbilitySet.abilities: Array[SGameplayAbilityInfo{gameplay_ability_class, input_tag, level}]`.
- `SAbilitySystemComponent`: `add_ability(SGameplayAbilityInfo, source_object)`, `add_ability_set(set, actor, source)` (static),
  `get_ability_system_component(actor)` (static), `give_ability(class, level, input_id)`, `remove_ability_set_for_actor`.
- SGameplayAbility (BP-callable): `get_avatar_actor_from_actor_info`, `get_current_source_object`, `end_ability`.
- Подсказки HUD: виджеты `/Game/UI/HUD/Components/Context/WBP_ActionsContainer/WBP_SimpleAction/WBP_Title` (SContextActionsWidgetBase).
- Теги ввода игрока (`/Game/Data/Player/DA_PlayerInput`, IMC_Player): Player.Input.Jump/Sprint/FirstAction/**Interact**/PC/Wheel/Flashlight/
  Crouch/HideTool/Save/**Enter**/SecondAction(Zoom)/Tablet/NextNPC/Skip/Pause/NextTool/PrevTool/Tool1..5/TabletSymptoms/TabletTabInspect/… (+17).
  Пользователь: **E (Interact) в модах не трогать** — использовать свободную клавишу (2026-10-14).
- Раскладка клавиш [S, probes/qz_probe_input.py; у IMC данные в `default_key_mappings.mappings`, поле `mappings` пустое]:
  IMC_Player: E=IA_Interact, F=Flashlight/XRay layer/GlowStick, Q=Tools(колесо), Tab=Tablet, LeftAlt=Next NPC, X=SkipDialog, Esc=Pause,
  F3=Save, R=Reload, G=ToolPistol, 0–6=Tool0..6, I/C/U/H/B=вкладки планшета, Space=Jump, LShift=Sprint, LCtrl=Crouch,
  **J=IA_Enter (тег Player.Input.Enter — ни один AbilitySet его не использует, фактически свободен)**,
  **Enter = IA_UI_EnterDistribution + IA_UI_Apply** (в IMC_Player); в IMC_UI/Mathiascope/BlockScreen/Defence Enter=IA_UI_Confirm/IA_Accept.
  По реестру виджетов Enter нужен только на экранах отчёта конца дня (UI.Game.Report.Cage/Economy/Evacuation/PassInfected — «Далее»)
  и в настройках (Apply) → во время осмотра Enter свободен. Своё действие на Enter делать с `consume_input=False`, чтобы не ломать эти экраны.
- Наборы способностей и их теги: инструменты — FirstAction/HideTool/SecondAction; AS_Player — Crouch/Flashlight/Jump/NextNPC/NextTool/Pause/
  PrevTool/Save/SecondAction/Skip/Sprint/Tablet/TabletTab*/Tool0..6/Wheel; AS_TrolleyDriving — Interact/Jump; остальные взаимодействия — Interact.

## 4. Посетитель КПП [S/M]
- Класс `BP_TestCivilian` ← `QzNPCCharacter`. Компоненты: FocusComponent (SFocusComponent, max 300, **ability_set = null** на КПП),
  SContextActions (фрагменты QzContextFragment_NPCToCage, QzContextFragment_NPCToInspection + Title), DialogueComponent (QzDialogueComponent),
  SubtitleComponent (Qz3DSubtitleComponent), AbilitySystemComponent, SHighlight, HealthComponent…; CDO: quarantine_cage_set=AS_QuarantineCage,
  quarantine_inspection_set=AS_QuarantineInspection (выдаются в карантине, на Interact).
- BP-callable: `get_state()` (EQzCvNPCState), `is_inspecting()`, `is_alive()`, `get_npc_data_bp()` → QzNPCData{profile: QzStaticProfile{document: QzDocument
  {first_name:int32, last_name:int32 (индексы!), override_first_name/override_last_name: Text}}}, `contains_symptom(tag)`, `get_mark_symptoms()`,
  `bp_add_focus_component / bp_remove_focus_component / bp_activate_focus_component(bool)`, `bp_on_npc_inited(is_zombie)` (событие), `get_photo()`.
  Имя посетителя напрямую текстом не лежит (first/last_name — индексы в таблицу имён).
- EQzCvNPCState (точные C++-имена, из UnrealEditor-QZSim.dll): None, Idle, IdleInspection, Inspection, Queue, Dialogue, MoveToInspection,
  MoveToZone, MoveToBaggage, MoveToBackpack, MoveToLaboratory, MoveFromLaboratory, MoveToLabMutation, MoveToEvacuation, MoveToTruck,
  ReturnToZone, InBlock, InCage, InLaboratory, InLiquidation, InQuarantine, EventAttack, EventAttackAnotherNPC, EventAttackMilitary,
  GiveGrenade, Rebellion, ThrowTrash, Finish. (Python показывает их как UPPER_SNAKE — для BP-узлов брать эти.)
  Способ: искать `EQzCvNPCState::` в `QZSim/Binaries/Win64/UnrealEditor-QZSim.dll` (utf-16/ascii) — годится для любых enum.
- [M PIE] в пуле 8 NPC; у стоящего на осмотре state=Inspection, у следующего IdleInspection, остальные None; `is_inspecting()` при этом False.
  К посетителю на осмотре игра цепляет `BP_QuestRoleDialogueActor` (Billboard+QzDialogueComponent; 8 таких в мире).

## 5. Точки входа для кода мода (как мод запускает свою логику) [S/M]
- Мод **не может ставить акторы на базовые уровни** (гайд). Возможные «носители» кода:
  - `runtime_actor_class` у аксессуаров: QzCharacterHatDataAsset (BP_HatBase), QzCharacterGlassesDataAsset (BP_GlassesBase),
    QzCharacterAccessoryOtherDataAsset (BP_Attachment_*). Генератор спавнит этот актор на NPC.
  - **OTHER_ACCESSORY случайным посетителям НЕ выдаётся** [M]: мод-копия DA_Accessory_Camera с use_only_custom_profile=False,
    spawn_probability=1, source=MOD → в PIE 0 камер (все 13 базовых OTHER — только для профилей).
  - **Шляпы/очки выдаются случайным** [M]: в PIE первый посетитель был в очках (BP_GlassesBase_C). Случайный пул
    (use_only_custom_profile=False): 20 шляп `DA_Hats_Hat01_Bowler … Hat20_Cloche` + 2 очков `DA_Glasses_MenSunglasses_Shape_01/02`
    (/Game/Data/GeneratorApperance/Hats|Glasses), все weight 1.0, без ограничений по кампании/полу.
  - Инструменты: акторы инструментов **не существуют с начала дня** [M] (QzToolBase в мире 0; на игроке только BP_MultiFlashlight, BP_Tablet) —
    как точка запуска не годятся.
  - Симптом (BP_GA_* по rule) — только у заражённых, меняет геймплей.
  - `custom_logic_list` (QzNPCCustomLogic) — только из профилей.
- Выбранная схема (VisitorTalk): заменить 22 случайные шляпы/очки копиями с тем же ключом + source=MOD, у которых runtime_actor_class —
  наследник BP_HatBase/BP_GlassesBase; в его BeginPlay (с вызовом Parent) — «если менеджера нет, заспавнить». Менеджер живёт на уровне.
- Дубликат DA **сохраняет key_tag_data оригинала** (read-only) → дубликат с source=MOD = ЗАМЕНА базового. Для нового (не замены)
  ключ = `Generator.DataKey.<Section>.<ИмяАссета>` и его надо объявить в Config/Tags (как у SafeHouse WitchHat); как заставить DA
  пересчитать ключ после duplicate — не выяснено (create_asset вместо duplicate — проверить).

- **Мутаторы ModioUGC** [M, PIE, мод ZZMutatorProbe]: в GameInstance есть `UGCMutatorSubsystem`; BP-наследник `UGCMutator` из мода
  **обнаруживается** (`get_mutator_class_list` → BP_ZZ_Mutator_C; без кэша список растёт дублями), но **не регистрируется и не создаётся**
  (`is_registered=False`, экземпляров нет). По докам mod.io экземпляр создаёт только `RegisterMutator()`, события зовёт код игры;
  в UnrealEditor-QZSim.dll и ассетах /Game ссылок на мутаторы нет (меню `WBP_MutatorMenu` есть только в плагине). → путь закрыт, пока игра его не подключит.
- Игра сканирует у модов 36 типов (DefaultGame.ini PrimaryAssetTypesToScan): Symptom, SymptomDoubleLayer, SymptomSection, Tool, Company, Level, Map,
  NPCProfileDataAsset, NPCAnimations, VoiceReactions, StaticNPCSkin, Character, CharacterHat/Glasses/OtherAccessory/Hair/HairColor/Face/Eyes/Eyelashes/
  SkinTone/SkinTextureSet/SkinOverlay/AgeVisual, ClothingItem, ClothingOutfitColorSet, BaggageSet, BaggageBackpackSet, HiddenContrabandSet,
  InternalContrabandSet, LaboratoryMutation, LockedSymptoms, Handbook, BodyOrgans, Blueprint, PrimaryAssetLabel.

- Добавить свои акторы в базовую карту — **штатных** путей нет [S]; подмена /Game-ассетов самодельным pak/utoc (mount point
  ../../../QZSim/Content/) **НЕ проверена [H]**: контейнеры модов не подписаны (SignatureHash=0), монтируются с Order (Jurassic Order=3),
  игра на ветке public монтирует любые pak из QZSim\Content\Paks\ (лог 05:24) — подмена может сработать. Не писать «нельзя» без пробы.
  Факты: GameFeatures-плагин выключен (есть только ModularGameplay/
  ModularGameplayActors) → External Data Layers невозможны; `L_BuildDLC_Miami` — обычный уровень (не World Partition; внешние акторы только у
  QuarantineLevelInstance); контент мода монтируется в `/<Мод>/`, а не `/Game` → карту/её ассеты по пути не подменить. В DLL игры нет соглашения
  «спавнить актор мода» (как ModActor у UE4SS BPModLoader или InitCave у DRG); интеграция модов в игре: ScanUGCPrimaryAssets, IsAssetFromUGC,
  bAutoGrantUGCTools, bAutoIncludeUGCSymptoms, ApplyModSkin(Override). → код мода попадает в мир только через объекты, которые игра сама
  создаёт из данных мода: акторы аксессуаров (runtime_actor_class), инструменты (при взятии в руки), симптомы (rule/GA у заражённых),
  скины персонала (меш → возможно Post Process AnimBP — не проверено), свои кампании/карты (Company/Level).
- Карты /Game/Maps: L_BuildDLC_Miami, L_BuildPrototype, Final_level, QuarantineLevelInstance, Menu/, PreMenu/, QuestSubLevels/, Checkpoint_Miami/, Chekpoint/.

- **Носитель «доктор» — РАБОТАЕТ** [M, PIE, мод ZZDocProbe, 2026-10-15]: копия меша доктора
  `/Game/Art/Characters/PA_Collection/Assets/Characters/Mesh/Zheka/LowPoly/D2_Zheka` (1,9 МБ, скелет `.../Usmon/LowPoly/D1_Usmon_Skeleton`,
  материалы MI_D2_LP_Suit_VDay, MI_D2_LP_MASK) в мод + `post_process_anim_blueprint` = свой AnimBP (Python-свойство меша, задаётся) +
  `QzStaticNPCSkinDataAsset{npc_tag=NPC.Skin.Doc, mesh=копия}` → у `BP_Doc_C_0` меш = копия мода, `get_post_process_instance()` = наш класс,
  основной AnimBP остаётся `ABP_Doc_C`. Доктор есть на КПП каждый день → 100% точка запуска кода мода. Post-process граф ОБЯЗАН пропускать позу
  (Input Pose → Output Pose), иначе доктор в T-позе. Usmon (BP_Usmon) — отдельный тег NPC.Skin.Usmon. Конфликт с другими модами на скин доктора.
- **Инструменты как носитель не годятся** [S + PIE]: инвентарь (SInventoryComponent, 5 слотов) хранит SItemDataAsset; актор предмета
  (`SWearableItemFragment.ActorClass` — сериализуется, но Python его НЕ видит/не пишет) спавнится EquipItem/EquipActor — при взятии в руки.
  В PIE с прямым запуском карты инструменты вообще не выдаются (все слоты None) — выдача идёт через кампанию/день.
- T3D-экспорт любого ассета показывает и скрытые от Python поля: `scripts/probes/qz_export_t3d.py` (env QZ_EXPORT="путь1;путь2").

## 6. Автоматизация PIE [M]
- Полный редактор с `-ExecCmds="py <script>"` (НЕ -ExecutePythonScript — тот закрывает редактор сразу после скрипта):
  скрипт регистрирует `unreal.register_slate_post_tick_callback`, через 20 с `LevelEditorSubsystem.editor_request_begin_play()`,
  мир PIE: `UnrealEditorSubsystem.get_game_world()`, опрос `GameplayStatics.get_all_actors_of_class(world, unreal.QzNPCCharacter)`,
  `get_attached_actors()`, в конце `editor_request_end_play()` + `SystemLibrary.quit_editor()`. Стартовая карта `L_BuildDLC_Miami` —
  день стартует сам, посетители спавнятся (~8 c). Весь прогон 3–5 мин. Скрипт: `scripts/probes/qz_pie_probe.py` (остальные пробы там же).
- Моды из QZSim/Mods монтируются в PIE автоматически (если плагин был на диске до старта редактора).

## 7. Прочее
- Карты: GameDefaultMap `/Game/Maps/Menu/PSOLevel`, EditorStartupMap `/Game/Maps/L_BuildDLC_Miami`; DA_LevelChicago (L_BuildPrototype), DA_LevelMiami.
- Commandlet-пробы (read-only) ~20–30 с; создавать ассеты в `/Game/...` в commandlet можно только в памяти без сохранения (так проверялись WBP/BP).
- `get_editor_property` на protected-свойствах падает («is protected»); Blueprint.Status тоже недоступен — ошибки компиляции искать в логе.

- В Python кита нет `SubsystemBlueprintLibrary`: подсистемы GameInstance/LocalPlayer искать `unreal.ObjectIterator(<Класс>)` по `get_outer()`.

## 8. Сердечки над Джорджи (взаимодействие с доктором) [M, 2026-10-16]
Цепочка (T3D/граф-дамп, commandlet):
1. `BP_Doc` (← `QzDocCharacter`) — нативный `FocusComponent` (`SFocusComponent`), в BP переопределён `AbilitySet = /Game/Blueprints/KPP/Prototyping/Military/Ability/AS_Doc`.
   Когда игрок смотрит на доктора, набор способностей фокуса доступен игроку.
2. `SContextActions` (`SContextActionsComponent`): `TitleFragment` = `SContextFragment_Title` «Doc» (NSLOCTEXT), `Fragments(0)` =
   `QzContextFragment_LoveInteract` с `Text = LOCTABLE(ST_Settings, SETTINGS_TITLE_INTERACT)` и `InputTag = Player.Input.Interact` — подсказка [E].
3. `AS_Doc` (`SAbilitySet`): `Abilities(0) = (GA_DocLoveInteract_C, InputTag = Player.Input.Interact)` → E активирует способность.
4. `GA_DocLoveInteract` — Blueprint с ПУСТЫМ графом (только отключённые K2_ActivateAbility/K2_OnEndAbility); логика в C++ родителе
   **`QzLoveInteract`** (← SGameplayAbility). Параметры CDO: `Emitter = /Game/Art/VFX/CatLoveFX/NS_CatsLove`, `BoneName = "head"`,
   `EmitterOffset = (0,0,20)`, `EmitterScale = (1,1,3)`, `BlockAbilitiesWithTag = Player.State.Tool.XRay`, InstancedPerActor, без cooldown/cost.
5. `NS_CatsLove` — эффект кошки (его же зовёт `A_Cat_Action_Pet_sit_Montage`), материал `M_HeartFX` с текстурой граффити `T_GraffitiHeart`.
Есть ещё нативный `QzContextFragment_LoveInteractAbility` (не используется доктором). Кость `head` есть и у скинов на D1_Usmon_Skeleton.
Мод: AS_Doc/GA_DocLoveInteract — /Game, не заменить; но `QzLoveInteract` можно наследовать в моде (свой Emitter/кость/масштаб), а
подменить `FocusComponent.AbilitySet` у доктора в рантайме может код мода через носитель-доктор (post-process AnimBP скина) [H].

Грабли проб: Git Bash превращает значение env, начинающееся с `/` (`QZ_GRAPH=/Game/...`), в путь Windows (`C:/Program Files/Git/Game/...`)
→ скрипт молча ничего не находит. Добавлять `;` в конец или `MSYS_NO_PATHCONV=1`. Граф-дамп: `scripts/probes/qz_graph_dump.py`
(env `QZ_GRAPH`, работает в commandlet, пишет `Saved/ModSchema/graphs/*.txt`).

## 9. Субтитры и реплики персонажей [M, 2026-10-16]
- Реплики сюжетных персонажей (Major, Georgie, Dr.Schultz, Guard…) показывает HUD: `WBP_HUDGame` → встроенный
  `WBP_MainTutorialMessage` (← C++ `QzSubtitlesWidget`). C++ сам вызывает BP-событие `InitializeWidget(FQzSubtitlesData Data)`
  (`text, duration, priority(EQzSubtitlesPriority NONE/NPC/TUTORIAL/MEDIA), speaker_role(EQzSpeakerRole), speaker_name`);
  BP форматирует «<Role>Имя: </>текст» в `CommonRichTextBlock_47`. Субтитры посетителей — `WBP_NPCSubtitle` в 3D-компоненте
  (`Qz3DSubtitleComponent` у BP_TestCivilian). Катсцены — `QzSequencerSubtitlesWidget`.
- PIE (Miami): в мире ОДИН живой экземпляр `...WBP_HUDGame_C_0.WidgetTree_0.WBP_MainTutorialMessage_422`; в покое HIDDEN,
  на время реплики HIT_TEST_INVISIBLE (`is_visible()` = True) с текстом, напр. `<Georgie>Georgie: </>Dr. Schultz, please!…`.
  Остальные экземпляры класса — шаблоны (дизайн-текст «<Warning>buihuihu…»). Проба: `scripts/probes/qz_pie_subtitles.py`.
- Рассылка идёт через свой плагин сообщений `SimMessageSystem` (`SGameplayMessageSubsystem`, структуры `QzSubtitlesMessageAdd/
  Remove`, `QzDialogueNowPlayingMessageV2{voice}`), но подсистема НЕ экспортирована в Python/BP (нет async-узла «Listen for
  Gameplay Messages») → мод перехватывает виджет: `GetAllWidgetsOfClass(WBP_MainTutorialMessage_C, TopLevelOnly=false)` →
  `IsVisible` + `CommonRichTextBlock_47.GetText` (опрос таймером), оригинал `SetRenderOpacity(0)` (логику игры не ломает).
- Виджеты, созданные Python-скриптом в дереве WBP, становятся BP-переменными, только если класс по умолчанию bIsVariable=true [M]:
  ДА — RichTextBlock, CommonRichTextBlock, Image, Button, EditableText(Box), MultiLineEditableTextBox; НЕТ — TextBlock,
  CommonTextBlock, Border, CommonBorder, панели (Canvas/VBox/HBox/Overlay/SizeBox/ScrollBox), Spacer. `bIsVariable` защищён (Python не
  пишет). Стиль строки субтитров копируется свойствами CommonRichTextBlock (`text_style_set`, `style`, …) с `CommonRichTextBlock_47`.
- Свободные клавиши: T (не занята в IMC_Player), J (IA_Enter без способностей). Носитель «солдаты»: `NPC.Skin.Military`, меш
  `/Game/Art/Characters/PA_Collection/Assets/Characters/Mesh/Mirbek/Low_Poly/D4_Mirbek`, BP_MilitaryCharacter стоит на L_BuildPrototype
  (Чикаго) и L_BuildDLC_Miami.
- [M 2026-10-16] Вставка (Ctrl+V) сгенерированного `AnimGraphNode_LinkedInputPose` в AnimGraph молча не срабатывает (у реального узла
  есть `Inputs(...)`/`ShowPinForProperties(...)`). «Input Pose» для post-process AnimBP — руками: ПКМ → Input Pose → связь в Output Pose.
- [M 2026-10-16] Вставленный `K2Node_SpawnActorFromClass` с «разобранным» SpawnTransform (скрытый SpawnTransform + пины
  SpawnTransform_Location/Rotation/Scale без SubPins/ParentPin-связей) → после вставки пин SpawnTransform пустой: ошибка компиляции
  «'Spawn Transform' pin is invalid… must have an input wired» + предупреждения «Spawn Transform Scale … no longer exists».
  Лечение руками: Refresh Node, к Spawn Transform подключить Make Transform. Генераторы (`scripts/examples/visitortalk_graphs.py`, `graph_helpers.py`) должны
  давать видимый SpawnTransform + узел KismetMathLibrary::MakeTransform.
- [M 2026-10-16] **Класс узла в тексте вставки должен быть с правильным модулем**, иначе редактор молча выкидывает узел и все его
  связи: `/Script/UMGEditor.K2Node_CreateWidget`, `/Script/InputBlueprintNodes.K2Node_EnhancedInputAction` (НЕ BlueprintGraph).
  `qz_paste_check.py` теперь сверяет классы узлов с реальными. Диагностика вставки без пользователя: job `scripts/examples/graph_dump_op.py`
  (мод монтируется только в полном редакторе) → сравнение узлов/связей сохранённого графа с текстом вставки; цепочку исполнения
  проходить от события по exec-пинам. `ke * <CustomEvent>` в PIE вызывает событие BP по имени (переменные BP-инстанса из Python не
  пишутся без флага Instance Editable).
- [M 2026-10-16] Значение пина функции, отличное от её значения по умолчанию, при вставке СБРАСЫВАЕТСЯ, если в тексте нет
  `AutogeneratedDefaultValue=<дефолт функции>` (было: GetAllWidgetsOfClass.TopLevelOnly "false" → после вставки true → пустой список,
  т.к. субтитры вложены в HUD). Реальные узлы пишут оба поля: `DefaultValue="false",AutogeneratedDefaultValue="true"`.

## 10. Данные посетителя и прочие факты BP [M, 2026-10-17/18]
- Профиль посетителя: `GetNPCDataBP` → QzNPCData.Profile (QzStaticProfile: Gender EQzGender, Role EQzNpcRole, BehaviorType
  EQzBehaviorPattern, Document QzDocument{Age, FirstName/LastName — индексы, BioFactIndex → ST_Bios "000N_Bio"}).
- Состав QzNPCData: Profile (Gender/Role/Race/BehaviorType/Body/Voice/Profession, Document: имя/фамилия/город — ИНДЕКСЫ или Override*-тексты у
  сюжетных, Age, BioFactIndex, Street/House/Apartments; Flags, HiddenContraband, Baggage, Wanted), DynamicData (Health.Temp/HeartRate,
  Symptoms[{Symptom.TagName, Location=сокет}], MarkedSymptoms, Accessories, NewRole…, PhotoRaw — самое большое поле), SavedAppearance,
  Skin (пути MetaHuman-ассетов). Умолчания структуры: у QzStaticProfile Gender=Female, Role=None, Race=Default, Behavior=Calm; у QzDocument
  индексы -1, Age 0. Таблица умолчаний — `unreal.QzNPCData()` в Python.
- Индексы → текст: `/Game/Data/Generator/Documents/DA_FirstNames|DA_LastNames` (male/female Array[Text]), `DA_Cities` (cities[].name),
  `/Game/Data/Generator/DA_BioFacts` (male/female[].text, empty_bio_fact_text). В редакторе только en (смена культуры не грузит ru).
  Python-имена enum без «E»: `unreal.QzGender`, `unreal.QzCvNPCState`.
- Значения enum'ов QzNPCData (дамп 2026-10-18, `scripts/examples/npc_enums_dump.py`): Gender MALE/FEMALE/OTHER; NpcRole NORMAL/ILL/VIRUS/
  QUARANTINE_NORMAL/QUARANTINE_ZOMBIE/UV_VIRUS(/MAX/NONE); BehaviorPattern CALM/FEAR/ANGRY/SAD/ZOMBIE; RaceType ASIAN/BLACK/WHITE/MULATTO/OTHER;
  NPCBodyShape NORMAL/OVERWEIGHT; SkinPigmentation EMPTY/FACE_TATTOO/BODY_TATTOO/FACE_VITILIGO/BODY_VITILIGO; BaggageContainer BACKPACK/BAG;
  SourceProfile NONE/STREAMER/TWITCH/QUEST/UNIQUE; NPCEvent NONE/ATTACK; ProfileFlags DOCUMENT/BAGGAGE_NORMAL/BAGGAGE_CONTRABAND/
  BAGGAGE_ZOMBIE/IC_NORMAL/IC_CONTRABAND/IC_ZOMBIE/HAS_BACKPACK/HAS_VIRTUAL_BAGGAGE; HiddenContrabandLocation UNDER_HAT/LEFT_FIST/RIGHT_FIST;
  NPCKillReason SHOOT/ZOMBIE/QUARANTINE/LABORATORY/LIQUIDATION/HAMMER/NPC/…/ELECTROSHOCK; OrganType BRAIN/LIVER/HEART/PANCREAS/SA/STOMACH/
  LUNGS/GUTS/DIAPHRAGM/INTESTINE/FRONTALE/STERNUM/…; VoiceType M_VOICE1..6/F_VOICE1..6; AgeVisual OLD/VERY_OLD; HairColor BLACK/BLOND/BROWN/
  LIGHT_BROWN/RED/WHITE. Полное дерево полей — classes.json (QzNPCData → profile/dynamic_data/saved_appearance/skin/…).
- Python: `BlueprintEditorLibrary.set_blueprint_variable_instance_editable(bp, var, True)` — чтобы задавать BP-переменные экземпляру из проб.
- Образец макроса (ForEachLoop…) из библиотеки несёт типы того BP, откуда взят (BP_PhysicalFlask) → «Array of X is not
  compatible with Array of Y», каскад оборванных связей. Переписывать тип пинов Array/Array Element под свой класс.
  Вызов CustomEvent как функции (K2Node_CallFunction MemberName=<событие>), когда событие вставляется в том же тексте, → пины узла
  вызова теряются («In use pin <Unnamed> no longer exists on node …»). Вместо вызова — флаг + обработка в таймере.
- `UserWidget.GetWidgetFromName` в этой сборке НЕ доступен из Blueprint (вставленный узел молча пропадает, «Cast… Object
  is undetermined»; нет ни в одном из 429 BP игры, нет в списке методов виджета). Доступ к не-переменной панели (ScrollBox) —
  через ребёнка-переменную: `Text_Main.GetParent()` → Cast To ScrollBox → ScrollToEnd.
- UE4SS v3.0.1 Beta (2024-02) НЕ работает с UE 5.7: «Failed to find EngineVersion / GUObjectArray … Fatal Error:
  PS scan timed out». Нужна новая сборка под 5.7 или свои AOB-сигнатуры.
