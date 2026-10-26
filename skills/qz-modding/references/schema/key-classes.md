# Ключевые классы QZ для модов (из qz_deep_dump)

Поля указаны как в Python API (`snake_case`; в редакторе — CamelCase). Показаны только СОБСТВЕННЫЕ поля класса (унаследованные — у родителя). Полный дамп: `%LOCALAPPDATA%/QZSim/Saved/ModSchema/deep/classes.json`.

## QZTool_UVFlashLight  ←  QzToolComponent < ActorComponent < Object
_QZTool UVFlash Light  **C++ Source:**_
- `angle_parameter_name` (Name) [Read-Write]
- `curve` (CurveFloat) [Read-Write]
- `direction_parameter_name` (Name) [Read-Write]
- `distance_parameter_name` (Name) [Read-Write]
- `enable_parameter_name` (Name) [Read-Write]
- `intensity` (Vector2D) [Read-Write]
- `material_parameter_collection` (MaterialParameterCollection) [Read-Write]
- `origin_parameter_name` (Name) [Read-Write]

## QzBaggageItemDataAsset  ←  QzBaggageSetDataAsset < PrimaryDataAsset < DataAsset
_deprecated: 'QzBaggageItemDataAsset' was renamed to 'QzBaggageSetDataAsset'._

## QzBaggageSetDataAsset  ←  PrimaryDataAsset < DataAsset < Object
_Qz Baggage Set Data Asset  **C++ Source:**_
- `items` (Array[QzBaggageItemData]) [Read-Write]

## QzCharacterAccessoryDataAsset  ←  QzGeneratorParentPrimaryData < PrimaryDataAsset < DataAsset
_Qz Character Accessory Data Asset  **C++ Source:**_
- `accessory_id` (Name) [Read-Write] Optional readable accessory id
- `accessory_tag` (GameplayTag) [Read-Write] Primary accessory tag
- `blocked_tags` (GameplayTagContainer) [Read-Write] Blocking context or character tags
- `break_effect` (NiagaraSystem) [Read-Write]
- `breakable` (bool) [Read-Write]
- `compatible_body_type_tags` (GameplayTagContainer) [Read-Write] Tag-based body type restriction
- `compatible_face_ids` (Array[Name]) [Read-Write] Restriction by specific face ids
- `compatible_face_tags` (GameplayTagContainer) [Read-Write] Tag-based face restriction
- `display_name` (Text) [Read-Write] Debug or editor display name
- `gender_tag` (GameplayTag) [Read-Write] Gender restriction
- `owned_tags` (GameplayTagContainer) [Read-Write] Additional tags owned by the accessory itself
- `required_tags` (GameplayTagContainer) [Read-Write] Required context or character tags
- `selection_weight` (float) [Read-Write] Generator selection weight for the accessory

## QzCharacterAccessoryHeadDataAsset  ←  QzCharacterAccessoryDataAsset < QzGeneratorParentPrimaryData < PrimaryDataAsset
_Qz Character Accessory Head Data Asset  **C++ Source:**_
- `runtime_actor_class` (Class) [Read-Write] Used to remove dependency on legacy SkinDataAssets in the new architecture
- `slot_tag` (GameplayTag) [Read-Write] Accessory slot

## QzCharacterAccessoryOtherDataAsset  ←  QzCharacterAccessoryDataAsset < QzGeneratorParentPrimaryData < PrimaryDataAsset
_Qz Character Accessory Other Data Asset  **C++ Source:**_
- `additional_transform` (Transform) [Read-Write]
- `runtime_actor_class` (Class) [Read-Write]
- `socket_in_head` (bool) [Read-Write]
- `socket_names` (Array[Name]) [Read-Write]
- `spawn_probability` (float) [Read-Write]
- `visible_in_x_ray` (bool) [Read-Write] Include this accessory in the X-ray scene capture.

## QzCharacterDataAsset  ←  QzGeneratorParentPrimaryData < PrimaryDataAsset < DataAsset
_Base character appearance - Defines the shared head and body - Defines the body type key_
- `blocked_bone_zones` (Array[Name]) [Read-Write] Root bones of blocked zones for hit detection.
- `body` (QzCharacterBody) [Read-Write] Shared body mesh for this body archetype
- `body_type` (QzCharacterBodyTypeKey) [Read-Write] Primary body type key
- `compatibility` (QzCharacterCompatibilityRules) [Read-Write] Compatibility rules for this body archetype
- `display_name` (Text) [Read-Write] Debug or editor display name
- `face_meshes` (Array[SkeletalMesh]) [Read-Write]
- `gender_tag` (GameplayTag) [Read-Write] , meta = (Categories = "Generator.NPC.Gender"))
- `height` (int32) [Read-Write] Base character height
- `occupied_zones` (QzBodyOccupiedZones) [Read-Write] Zones pre-occupied by this body (tattoos, markings baked into the mesh).
- `owned_tags` (GameplayTagContainer) [Read-Write] Additional tags owned by this body type
- `selection_weight` (float) [Read-Write] Generator selection weight for this body type

## QzCharacterGlassesDataAsset  ←  QzCharacterAccessoryHeadDataAsset < QzCharacterAccessoryDataAsset < QzGeneratorParentPrimaryData
_Qz Character Glasses Data Asset  **C++ Source:**_
- `automatic_attach` (bool) [Read-Write]
- `glasses_mesh` (SkeletalMesh) [Read-Write] Glasses skeletal mesh
- `index_glass` (int32) [Read-Write]
- `placement` (QzGlassesPlacementSettings) [Read-Write] Glasses placement parameters

## QzCharacterHairDataAsset  ←  QzGeneratorParentPrimaryData < PrimaryDataAsset < DataAsset
_Qz Character Hair Data Asset  **C++ Source:**_
- `allowed_hat_tags` (GameplayTagContainer) [Read-Write] Empty means all hats are allowed for this hair item
- `blocked_hat_tags` (GameplayTagContainer) [Read-Write] Empty means no hats are blocked for this hair item
- `blocked_tags` (GameplayTagContainer) [Read-Write] Blocking context or character tags
- `compatible_body_type_tags` (GameplayTagContainer) [Read-Write] Tag-based body type compatibility
- `compatible_face_ids` (Array[Name]) [Read-Write] Compatibility by specific face ids
- `compatible_face_tags` (GameplayTagContainer) [Read-Write] Tag-based face compatibility
- `display_name` (Text) [Read-Write] Editor or debug display name
- `follicle_texture` (Texture) [Read-Write] Optional follicle or mask texture for hair material logic
- `gender_tag` (GameplayTag) [Read-Write] Can stay empty for universal variants
- `groom_asset` (GroomAsset) [Read-Write]
- `hair_color_tags` (GameplayTagContainer) [Read-Write] Hair color or material profile tags
- `hair_face_params` (QzSoftMaterialParameterStruct) [Read-Write]
- `hair_id` (Name) [Read-Write] Optional readable id
- `hair_tag` (GameplayTag) [Read-Write]
- `materials` (Array[MaterialInterface]) [Read-Write] Groom materials
- `owned_tags` (GameplayTagContainer) [Read-Write] Additional tags owned by this hair item
- `required_tags` (GameplayTagContainer) [Read-Write] Required context or character tags
- `selection_weight` (float) [Read-Write] Generator selection weight
- `slot` (QzCharacterHairSlot) [Read-Write]
- `source_face_mesh` (SkeletalMesh) [Read-Write] Source head mesh used when this hair was originally created

## QzCharacterHatDataAsset  ←  QzCharacterAccessoryHeadDataAsset < QzCharacterAccessoryDataAsset < QzGeneratorParentPrimaryData
_Qz Character Hat Data Asset  **C++ Source:**_
- `allow_removing` (bool) [Read-Write]
- `base_placement` (QzHatGenderPlacementSettings) [Read-Write] Base placement by gender
- `block_bullet_and_hammer_collision` (bool) [Read-Write]
- `compatible_hair_ids` (Array[Name]) [Read-Write] Compatibility by specific HairId values
- `compatible_hair_tags` (GameplayTagContainer) [Read-Write] Tag-based hair compatibility
- `face_overrides` (Array[QzHatFacePlacementOverride]) [Read-Write] Additional override parameters for specific faces or DNA variants
- `hat_extent` (Vector) [Read-Write] Parameter from the current hat BP logic
- `hat_mesh` (StaticMesh) [Read-Write] Hat static mesh
- `hat_offset` (Vector) [Read-Write] Parameter from the current hat BP logic
- `volume_texture` (Texture) [Read-Write] Volume texture for hair interaction

## QzCharacterSkinDataAsset  ←  QzGeneratorParentPrimaryData < PrimaryDataAsset < DataAsset
_Base skin asset for the new generator - Face texture sets - Body texture sets_
- `blocked_tags` (GameplayTagContainer) [Read-Write] Blocking context or character tags
- `body_textures` (Array[QzSkinSurfaceTextureSet]) [Read-Write]
- `compatible_body_type_tags` (GameplayTagContainer) [Read-Write] Tag-based body type compatibility
- `display_name` (Text) [Read-Write] Editor or debug asset name
- `face_textures` (Array[QzSkinSurfaceTextureSet]) [Read-Write]
- `owned_tags` (GameplayTagContainer) [Read-Write] Additional tags owned by this skin profile
- `required_tags` (GameplayTagContainer) [Read-Write] Required context or character tags
- `selection_weight` (float) [Read-Write] Generator selection weight for the entire skin profile
- `skin_tag` (GameplayTag) [Read-Write] Primary skin profile tag
- `skin_tones` (Array[QzSkinTonePreset]) [Read-Write]

## QzCharacterSkinOverlayDataAsset  ←  QzGeneratorParentPrimaryData < PrimaryDataAsset < DataAsset
_Qz Character Skin Overlay Data Asset  **C++ Source:**_
- `blocked_tags` (GameplayTagContainer) [Read-Write]
- `compatible_body_type_tags` (GameplayTagContainer) [Read-Write]
- `display_name` (Text) [Read-Write]
- `gender_tag` (GameplayTag) [Read-Write]
- `overlay_layers` (Array[QzCharacterSkinOverlayLayer]) [Read-Write]
- `required_tags` (GameplayTagContainer) [Read-Write]
- `selection_weight` (float) [Read-Write]

## QzClothingItemDataAsset  ←  QzGeneratorParentPrimaryData < PrimaryDataAsset < DataAsset
_Clothing item-level layer - Mesh - Shape mesh_
- `allowed_outfit_color_set_tags` (GameplayTagContainer) [Read-Write]
- `blocked_outfit_color_set_tags` (GameplayTagContainer) [Read-Write]
- `blocked_tags` (GameplayTagContainer) [Read-Write] Blocking context or character tags
- `blocked_underlying_item_tags` (GameplayTagContainer) [Read-Write] Specific clothing item tags blocked by this item
- `blocked_underlying_tags` (GameplayTagContainer) [Read-Write] Underlying tags blocked by this item
- `clothes_mesh` (SkeletalMesh) [Read-Write] Primary clothing skeletal mesh
- `clothes_name` (Name) [Read-Write] Readable clothing item id or name
- `clothes_type` (QzClothingSlotType) [Read-Write]
- `clothing_tag` (GameplayTag) [Read-Write]
- `color_override` (QzClothingSlotPaletteStyle) [Read-Write]
- `compatible_body_type_tags` (GameplayTagContainer) [Read-Write] Tag-based body type compatibility
- `compatible_face_ids` (Array[Name]) [Read-Write] Deprecated for clothing. Clothing compatibility must depend on body type, gender and tags
- `compatible_face_tags` (GameplayTagContainer) [Read-Write] Deprecated for clothing. Clothing compatibility must depend on body type, gender and tags
- `default_materials` (Array[QzClothingMaterialSlot]) [Read-Write] Base material slots for the item
- `display_name` (Text) [Read-Write] Editor or debug display name
- `gender_tag` (GameplayTag) [Read-Write] Gender restriction
- `ignored_under_lying_type_clothes` (Array[QzClothingSlotType]) [Read-Write] Underlayer slots blocked by this item
- `override_palette_color` (bool) [Read-Write]
- `owned_tags` (GameplayTagContainer) [Read-Write] Additional tags owned by the clothing item
- `print_channel_sets` (Array[QzClothingPrintChannelSet]) [Read-Write]
- `print_settings` (QzClothesPrintSettings) [Read-Write]
- `prints_parameter_struct` (QzClothingPrintsMaterialParameters) [Read-Write] Parameters for prints, dirt, blood, and leaks
- `required_tags` (GameplayTagContainer) [Read-Write] Required context or character tags
- `selection_weight` (float) [Read-Write] Generator selection weight for this item
- `shape_mesh` (StaticMesh) [Read-Write] Shape mesh used to mask or hide body parts
- `short` (bool) [Read-Write]
- `slot_tag` (GameplayTag) [Read-Write] Additional slot tag
- `supports_blood` (bool) [Read-Write]
- `supports_dirt` (bool) [Read-Write]
- `supports_leak` (bool) [Read-Write]
- `supports_prints` (bool) [Read-Write]
- `texture_override_rules` (Array[QzClothingTextureOverrideRule]) [Read-Write]

## QzCompanyBaseConfig  ←  StructBase < _WrapperBase < object
_Qz Company Base Config  **C++ Source:**_
- `available_flags_mask` (int32) [Read-Write]
- `available_symptoms` (Set[GameplayTag]) [Read-Write]
- `baggage_count_weights` (RuntimeFloatCurve) [Read-Write]
- `baggage_weights` (QzBaggageGenerateWeights) [Read-Write]
- `behavior_weights` (Map[QzBehaviorPattern, float]) [Read-Write]
- `body_shape_weights` (Map[GameplayTag, float]) [Read-Write]
- `chance_documents` (float) [Read-Write]
- `chance_female` (float) [Read-Write]
- `clothes_rule` (QzClothesDayRule) [Read-Write]
- `hidden_contraband_count_weights` (RuntimeFloatCurve) [Read-Write]
- `hidden_contraband_weights` (QzHiddenContrabandGenerateWeights) [Read-Write]
- `ic_count_weights` (RuntimeFloatCurve) [Read-Write]
- `ic_weights` (QzICGenerateWeights) [Read-Write]
- `makeup_spawn_probability` (float) [Read-Write]
- `opened_symptoms` (Set[GameplayTag]) [Read-Write]
- `race_weights` (Map[QzRaceType, float]) [Read-Write]
- `skin_pigmentation_weights` (Map[QzSkinPigmentationType, float]) [Read-Write]
- `standalone_body_tattoo_probability` (float) [Read-Write]
- `standalone_face_tattoo_probability` (float) [Read-Write]
- `symptoms_count_weights` (RuntimeFloatCurve) [Read-Write]
- `symptoms_weights` (QzSymptomsGenerateWeights) [Read-Write]
- `uv_baggage_count_weights` (RuntimeFloatCurve) [Read-Write]
- `voice_weights` (Map[QzVoiceType, float]) [Read-Write]

## QzCompanyConfig  ←  StructBase < _WrapperBase < object
_Qz Company Config  **C++ Source:**_
- `base_day_config` (QzDayConfig) [Read-Write]
- `base_management` (bool) [Read-Write]
- `count_days` (int32) [Read-Write]
- `days` (Map[int32, QzDayConfig]) [Read-Write]
- `endless_mode` (bool) [Read-Write]
- `level` (GameplayTag) [Read-Write]
- `seed` (int32) [Read-Write]
- `supported_blocks` (GameplayTagContainer) [Read-Write]
- `supported_sections` (GameplayTagContainer) [Read-Write]
- `tag` (GameplayTag) [Read-Write]
- `triggers_quests` (Array[QzTagQuestEntry]) [Read-Write]
- `type` (QzCompanyType) [Read-Write]

## QzCompanyConfigContext  ←  StructBase < _WrapperBase < object
_Qz Company Config Context  **C++ Source:**_

## QzCompanyDataAsset  ←  PrimaryDataAsset < DataAsset < Object
_Qz Company Data Asset  **C++ Source:**_
- `base_config` (QzCompanyBaseConfig) [Read-Write]
- `base_management` (bool) [Read-Write]
- `campaign_psevdonim` (Text) [Read-Write] Used by MainMenu widget
- `days` (Array[QzDayDataAsset]) [Read-Write]
- `debug` (bool) [Read-Write]
- `description` (Text) [Read-Write]
- `endless` (bool) [Read-Write]
- `endless_repeat_day` (QzDayDataAsset) [Read-Write]
- `endless_tag` (GameplayTag) [Read-Write]
- `level_tag` (GameplayTag) [Read-Write]
- `logo` (Texture2D) [Read-Write]
- `priority` (int32) [Read-Write]
- `supported_blocks` (GameplayTagContainer) [Read-Write]
- `supported_sections` (GameplayTagContainer) [Read-Write]
- `tag` (GameplayTag) [Read-Write]
- `title` (Text) [Read-Write]
- `triggers_quests` (Array[QzTagQuestEntry]) [Read-Write]

## QzCompanyShortInfo  ←  StructBase < _WrapperBase < object
_Qz Company Short Info  **C++ Source:**_
- `description` (Text) [Read-Write]
- `endless` (bool) [Read-Write]
- `endless_tag` (GameplayTag) [Read-Write]
- `logo` (Texture2D) [Read-Write]
- `name` (Text) [Read-Write]
- `psevdonim` (Text) [Read-Write]
- `tag` (GameplayTag) [Read-Write]

## QzDayConfig  ←  StructBase < _WrapperBase < object
_Qz Day Config  **C++ Source:**_
- `available_flags_mask` (int32) [Read-Write]

## QzDayDataAsset  ←  DataAsset < Object < _ObjectBase
_Qz Day Data Asset  **C++ Source:**_
- `modifiers` (Array[QzDayModifier]) [Read-Write]
- `rand_queue` (QzRandomQueue) [Read-Write]

## QzDayModifier  ←  SInstancedObject < Object < _ObjectBase
_Qz Day Modifier  **C++ Source:**_

## QzDayModifier_Accumulable  ←  QzDayModifier < SInstancedObject < Object
_Qz Day Modifier Accumulable  **C++ Source:**_
- `accumulate` (bool) [Read-Write]

## QzDayModifier_AvailableFlags  ←  QzDayModifier_Accumulable < QzDayModifier < SInstancedObject
_Qz Day Modifier Available Flags  **C++ Source:**_
- `flags_mask` (int32) [Read-Write]

## QzDayModifier_Baggage  ←  QzDayModifier < SInstancedObject < Object
_Qz Day Modifier Baggage  **C++ Source:**_
- `chance_baggage` (float) [Read-Write]
- `chance_contraband` (float) [Read-Write]
- `chance_uv_baggage` (float) [Read-Write]
- `chance_zombie_baggage` (float) [Read-Write]
- `override_chance_baggage` (bool) [Read-Write]
- `override_chance_contraband_baggage` (bool) [Read-Write]
- `override_chance_uv_baggage` (bool) [Read-Write]
- `override_chance_zombie_baggage` (bool) [Read-Write]

## QzDayModifier_Behavior  ←  QzDayModifier_Accumulable < QzDayModifier < SInstancedObject
_Qz Day Modifier Behavior  **C++ Source:**_
- `weights` (Map[QzBehaviorPattern, float]) [Read-Write]

## QzDayModifier_BodyShape  ←  QzDayModifier < SInstancedObject < Object
_Qz Day Modifier Body Shape  **C++ Source:**_
- `weights` (Map[GameplayTag, float]) [Read-Write]

## QzDayModifier_Evacuation  ←  QzDayModifier < SInstancedObject < Object
_Qz Day Modifier Evacuation  **C++ Source:**_
- `evacuation_config` (QzEvacuationScheduleConfig) [Read-Write]
- `military_evacuation_reward` (QzFactionRewardMode) [Read-Write]
- `science_evacuation_reward` (QzFactionRewardMode) [Read-Write]

## QzDayModifier_Gender  ←  QzDayModifier_Accumulable < QzDayModifier < SInstancedObject
_Qz Day Modifier Gender  **C++ Source:**_
- `chance_female` (float) [Read-Write]

## QzDayModifier_HiddenContraband  ←  QzDayModifier_Accumulable < QzDayModifier < SInstancedObject
_Qz Day Modifier Hidden Contraband  **C++ Source:**_
- `chance` (float) [Read-Write]
- `count_weights` (RuntimeFloatCurve) [Read-Write]

## QzDayModifier_InternalContraband  ←  QzDayModifier < SInstancedObject < Object
_Qz Day Modifier Internal Contraband  **C++ Source:**_
- `chance_contraband_ic` (float) [Read-Write]
- `chance_ic` (float) [Read-Write]
- `chance_zombie_ic` (float) [Read-Write]
- `override_chance_contraband_ic` (bool) [Read-Write]
- `override_chance_zombie_ic` (bool) [Read-Write]
- `override_ic` (bool) [Read-Write]

## QzDayModifier_Makeup  ←  QzDayModifier_Accumulable < QzDayModifier < SInstancedObject
_Qz Day Modifier Makeup  **C++ Source:**_
- `spawn_probability` (float) [Read-Write]

## QzDayModifier_Quests  ←  QzDayModifier < SInstancedObject < Object
_Qz Day Modifier Quests  **C++ Source:**_
- `main_quest_class` (Class) [Read-Write]
- `override_triggers_quests` (Array[QzTagQuestEntry]) [Read-Write]
- `prohibit_triggers_quests` (Array[QzTagQuestEntry]) [Read-Write]
- `quest_catalog` (QzQuestCatalogDataV2) [Read-Write]

## QzDayModifier_SetSymptomsCountWeights  ←  QzDayModifier_Accumulable < QzDayModifier < SInstancedObject
_Qz Day Modifier Set Symptoms Count Weights  **C++ Source:**_
- `symptoms_count_weights` (RuntimeFloatCurve) [Read-Write]

## QzDayModifier_Skin  ←  QzDayModifier_Accumulable < QzDayModifier < SInstancedObject
_Qz Day Modifier Skin  **C++ Source:**_
- `weights` (Map[QzSkinPigmentationType, float]) [Read-Write]

## QzDayModifier_SkinDirt  ←  QzDayModifier < SInstancedObject < Object
_Qz Day Modifier Skin Dirt  **C++ Source:**_
- `body_weights` (Map[QzSkinDirtType, int32]) [Read-Write]
- `face_weights` (Map[QzSkinDirtType, int32]) [Read-Write]

## QzDayModifier_StandaloneUVTattoo  ←  QzDayModifier_Accumulable < QzDayModifier < SInstancedObject
_Qz Day Modifier Standalone UVTattoo  **C++ Source:**_
- `body_spawn_probability` (float) [Read-Write]
- `face_spawn_probability` (float) [Read-Write]

## QzDayRules  ←  DataAsset < Object < _ObjectBase
_Qz Day Rules  **C++ Source:**_
- `days_data` (Array[QzNewDayData]) [Read-Write]
- `default_money` (int32) [Read-Write]
- `endless_mode` (bool) [Read-Write]
- `infinity_days_data` (Array[QzNewDayData]) [Read-Write]
- `infinity_mode_type` (QzInfinityModeType) [Read-Write]
- `interval_day_from_side_quests` (Vector2D) [Read-Write]
- `last_day` (int32) [Read-Write]
- `loop_type` (QzGameLoopType) [Read-Write]
- `max_days_in_infinity_mode` (int32) [Read-Write]
- `max_side_quests_in_day` (int32) [Read-Write]
- `min_day_for_spawn_special` (int32) [Read-Write]
- `profile_data_assets` (Array[QzProfileDataAsset]) [Read-Write]
- `profile_quest_chains` (Array[QzProfileQuestChain]) [Read-Write]
- `research_points_data_asset` (QzResearchPointsDataAsset) [Read-Write]
- `triggers_quests` (Array[QzTagQuestEntry]) [Read-Write]

## QzDynamicRule  ←  Object < _ObjectBase < _WrapperBase
_Qz Dynamic Rule  **C++ Source:**_

## QzDynamicRuleWidget  ←  CommonUserWidget < UserWidget < Widget
_Qz Dynamic Rule Widget  **C++ Source:**_
- `accessible_behavior` (SlateAccessibleBehavior) [Read-Write] Whether or not the widget is accessible, and how to describe it. If set to custom, additional customization options will appear.
- `accessible_summary_behavior` (SlateAccessibleBehavior) [Read-Write] How to describe this widget when it's being presented through a summary of a parent widget. If set to custom, additional customization options will appear.
- `accessible_summary_text` (Text) [Read-Write] When AccessibleSummaryBehavior is set to Custom, this is the text that will be used to describe the widget.
- `accessible_text` (Text) [Read-Write] When AccessibleBehavior is set to Custom, this is the text that will be used to describe the widget.
- `can_children_be_accessible` (bool) [Read-Write] Whether or not children of this widget can appear as distinct accessible widgets.
- `clipping` (WidgetClipping) [Read-Write] Controls how the clipping behavior of this widget.  Normally content that overflows the
- `color_and_opacity` (LinearColor) [Read-Write] The color and opacity of this widget.  Tints all child widgets.
- `consume_pointer_input` (bool) [Read-Write] Set this to true if you don't want any pointer (mouse and touch) input to bubble past this widget
- `cursor` (MouseCursor) [Read-Write] The cursor to show when the mouse is over the widget
- `description_text` (CommonRichTextBlock) [Read-Write]
- `desired_focus_widget` (WidgetChild) [Read-Write]
- `display_in_action_bar` (bool) [Read-Write] True to generally display this widget's actions in the action bar, assuming it has actions.
- `flow_direction_preference` (FlowDirectionPreference) [Read-Write] Allows you to set a new flow direction
- `foreground_color` (SlateColor) [Read-Write] The foreground color of the widget, this is inherited by sub widgets.  Any color property
- `is_enabled` (bool) [Read-Write] Sets whether this widget can be modified interactively by the user
- `is_focusable` (bool) [Read-Write] Setting this flag to true, allows this widget to accept focus when clicked, or when navigated to.
- `is_volatile` (bool) [Read-Write] If true prevents the widget or its child's geometry or layout information from being cached.  If this widget
- `navigation` (WidgetNavigation) [Read-Write] The navigation object for this widget is optionally created if the user has configured custom
- `on_visibility_changed` (OnVisibilityChangedEvent) [Read-Write] Called when the visibility has changed
- `override_accessible_defaults` (bool) [Read-Write] Override all of the default accessibility behavior and text for this widget.
- `override_cursor` (bool) [Read-Write]
- `padding` (Margin) [Read-Write] The padding area around the content.
- `pixel_snapping` (WidgetPixelSnapping) [Read-Write] If the widget will draw snapped to the nearest pixel.  Improves clarity but might cause visibile stepping in animation
- `preview_background` (Texture2D) [Read-Write] A preview background that you can use when designing the UI to get a sense of scale on the screen.  Use
- `priority` (int32) [Read-Write]
- `render_opacity` (float) [Read-Write] The opacity of the widget
- `render_transform` (WidgetTransform) [Read-Write] The render transform of the widget allows for arbitrary 2D transforms to be applied to the widget.
- `render_transform_pivot` (Vector2D) [Read-Write] The render transform pivot controls the location about which transforms are applied.
- `slot` (PanelSlot) [Read-Write] The parent slot of the UWidget.  Allows us to easily inline edit the layout controlling this widget.
- `stop_action` (bool) [Read-Write]
- `tick_frequency` (WidgetTickFrequency) [Read-Write] This widget is allowed to tick. If this is unchecked tick will never be called, animations will not play correctly, and latent actions will not execute.
- `title_text` (CommonRichTextBlock) [Read-Write]
- `tool_tip_text` (Text) [Read-Write] Tooltip text to show when the user hovers over the widget with the mouse
- `tool_tip_widget` (Widget) [Read-Only] Tooltip widget to show when the user hovers over the widget with the mouse
- `visibility` (SlateVisibility) [Read-Write] The visibility of the widget

## QzDynamicRule_Age  ←  QzDynamicRule < Object < _ObjectBase
_Qz Dynamic Rule Age  **C++ Source:**_
- `age_range` (IntPoint) [Read-Write]
- `use_random` (bool) [Read-Write]

## QzDynamicRule_City  ←  QzDynamicRule < Object < _ObjectBase
_Qz Dynamic Rule City  **C++ Source:**_
- `city` (str) [Read-Write]

## QzDynamicRule_HasContraband  ←  QzDynamicRule < Object < _ObjectBase
_Qz Dynamic Rule Has Contraband  **C++ Source:**_
- `contraband_tag` (GameplayTag) [Read-Write]
- `inverse` (bool) [Read-Write]

## QzDynamicRule_HasDoc  ←  QzDynamicRule < Object < _ObjectBase
_Qz Dynamic Rule Has Doc  **C++ Source:**_
- `inverse` (bool) [Read-Write]

## QzDynamicRule_HasSymptoms  ←  QzDynamicRule < Object < _ObjectBase
_Qz Dynamic Rule Has Symptoms  **C++ Source:**_
- `inverse` (bool) [Read-Write]

## QzDynamicRule_Street  ←  QzDynamicRule < Object < _ObjectBase
_Qz Dynamic Rule Street  **C++ Source:**_
- `street` (str) [Read-Write]

## QzDynamicRulesBoardWidget  ←  CommonUserWidget < UserWidget < Widget
_Qz Dynamic Rules Board Widget  **C++ Source:**_
- `accessible_behavior` (SlateAccessibleBehavior) [Read-Write] Whether or not the widget is accessible, and how to describe it. If set to custom, additional customization options will appear.
- `accessible_summary_behavior` (SlateAccessibleBehavior) [Read-Write] How to describe this widget when it's being presented through a summary of a parent widget. If set to custom, additional customization options will appear.
- `accessible_summary_text` (Text) [Read-Write] When AccessibleSummaryBehavior is set to Custom, this is the text that will be used to describe the widget.
- `accessible_text` (Text) [Read-Write] When AccessibleBehavior is set to Custom, this is the text that will be used to describe the widget.
- `can_children_be_accessible` (bool) [Read-Write] Whether or not children of this widget can appear as distinct accessible widgets.
- `clipping` (WidgetClipping) [Read-Write] Controls how the clipping behavior of this widget.  Normally content that overflows the
- `color_and_opacity` (LinearColor) [Read-Write] The color and opacity of this widget.  Tints all child widgets.
- `consume_pointer_input` (bool) [Read-Write] Set this to true if you don't want any pointer (mouse and touch) input to bubble past this widget
- `cursor` (MouseCursor) [Read-Write] The cursor to show when the mouse is over the widget
- `desired_focus_widget` (WidgetChild) [Read-Write]
- `display_in_action_bar` (bool) [Read-Write] True to generally display this widget's actions in the action bar, assuming it has actions.
- `flow_direction_preference` (FlowDirectionPreference) [Read-Write] Allows you to set a new flow direction
- `foreground_color` (SlateColor) [Read-Write] The foreground color of the widget, this is inherited by sub widgets.  Any color property
- `grid_panel` (UniformGridPanel) [Read-Write]
- `is_enabled` (bool) [Read-Write] Sets whether this widget can be modified interactively by the user
- `is_focusable` (bool) [Read-Write] Setting this flag to true, allows this widget to accept focus when clicked, or when navigated to.
- `is_volatile` (bool) [Read-Write] If true prevents the widget or its child's geometry or layout information from being cached.  If this widget
- `navigation` (WidgetNavigation) [Read-Write] The navigation object for this widget is optionally created if the user has configured custom
- `on_visibility_changed` (OnVisibilityChangedEvent) [Read-Write] Called when the visibility has changed
- `override_accessible_defaults` (bool) [Read-Write] Override all of the default accessibility behavior and text for this widget.
- `override_cursor` (bool) [Read-Write]
- `padding` (Margin) [Read-Write] The padding area around the content.
- `pixel_snapping` (WidgetPixelSnapping) [Read-Write] If the widget will draw snapped to the nearest pixel.  Improves clarity but might cause visibile stepping in animation
- `preview_background` (Texture2D) [Read-Write] A preview background that you can use when designing the UI to get a sense of scale on the screen.  Use
- `priority` (int32) [Read-Write]
- `render_opacity` (float) [Read-Write] The opacity of the widget
- `render_transform` (WidgetTransform) [Read-Write] The render transform of the widget allows for arbitrary 2D transforms to be applied to the widget.
- `render_transform_pivot` (Vector2D) [Read-Write] The render transform pivot controls the location about which transforms are applied.
- `slot` (PanelSlot) [Read-Write] The parent slot of the UWidget.  Allows us to easily inline edit the layout controlling this widget.
- `stop_action` (bool) [Read-Write]
- `tick_frequency` (WidgetTickFrequency) [Read-Write] This widget is allowed to tick. If this is unchecked tick will never be called, animations will not play correctly, and latent actions will not execute.
- `tool_tip_text` (Text) [Read-Write] Tooltip text to show when the user hovers over the widget with the mouse
- `tool_tip_widget` (Widget) [Read-Only] Tooltip widget to show when the user hovers over the widget with the mouse
- `visibility` (SlateVisibility) [Read-Write] The visibility of the widget

## QzDynamicRulesEndDay  ←  EnumBase < _WrapperBase < object
_EQz Dynamic Rules End Day  **C++ Source:**_

## QzDynamicRulesReplaceVar  ←  EnumBase < _WrapperBase < object
_EQz Dynamic Rules Replace Var  **C++ Source:**_

## QzDynamicRulesRewardType  ←  EnumBase < _WrapperBase < object
_EQz Dynamic Rules Reward Type  **C++ Source:**_

## QzDynamicRulesSubsystem  ←  QzWorldSubsystemBase < WorldSubsystem < Subsystem
_Qz Dynamic Rules Subsystem  **C++ Source:**_
- `on_dynamic_quest_completed` (OnDynamicQuestCompleted) [Read-Write]
- `on_dynamic_quest_failed` (OnDynamicQuestCompleted) [Read-Write]
- `on_dynamic_rules_ready` (OnDynamicRulesReady) [Read-Write]

## QzGenRule  ←  SInstancedObject < Object < _ObjectBase
_Qz Gen Rule  **C++ Source:**_

## QzGenRule_AddBaggage  ←  QzGenRule < SInstancedObject < Object
_Qz Gen Rule Add Baggage  **C++ Source:**_
- `categories` (Set[GameplayTag]) [Read-Write]
- `custom_count` (int32) [Read-Write]
- `mode` (QzCountMode) [Read-Write]

## QzGenRule_AddCustomSymptoms  ←  QzGenRule < SInstancedObject < Object
_Qz Gen Rule Add Custom Symptoms  **C++ Source:**_
- `zombie_baggage_symptom` (GameplayTag) [Read-Write]

## QzGenRule_AddSymptoms  ←  QzGenRule < SInstancedObject < Object
_Qz Gen Rule Add Symptoms  **C++ Source:**_
- `categories` (Set[QzSymptomCategory]) [Read-Write]
- `custom_count` (int32) [Read-Write]
- `mode` (QzCountMode) [Read-Write]
- `uv` (bool) [Read-Write]

## QzGenRule_AddTransformationSymptoms  ←  QzGenRule < SInstancedObject < Object
_Qz Gen Rule Add Transformation Symptoms  **C++ Source:**_
- `categories` (Set[QzSymptomCategory]) [Read-Write]
- `uv` (bool) [Read-Write]

## QzGenRule_HiddenContraband  ←  QzGenRule < SInstancedObject < Object
_Qz Gen Rule Hidden Contraband  **C++ Source:**_
- `categories` (Set[GameplayTag]) [Read-Write]
- `custom_count` (int32) [Read-Write]
- `mode` (QzCountMode) [Read-Write]

## QzGenRule_Inline  ←  Object < _ObjectBase < _WrapperBase
_Qz Gen Rule Inline  **C++ Source:**_
- `rules` (Array[QzGeneratorRule]) [Read-Write]

## QzGenRule_InternalContraband  ←  QzGenRule < SInstancedObject < Object
_Qz Gen Rule Internal Contraband  **C++ Source:**_
- `categories` (Set[GameplayTag]) [Read-Write]
- `custom_count` (int32) [Read-Write]
- `mode` (QzCountMode) [Read-Write]

## QzGenRule_OccupyZones  ←  QzGenRule < SInstancedObject < Object
_Qz Gen Rule Occupy Zones  **C++ Source:**_
- `zone_type` (QzOccupyZoneType) [Read-Write]

## QzGeneratorParentPrimaryData  ←  PrimaryDataAsset < DataAsset < Object
_Qz Generator Parent Primary Data  **C++ Source:**_
- `allowed_campaign_tags` (GameplayTagContainer) [Read-Write] Empty means that this asset can be selected in any campaign.
- `generator_data_source` (QzGeneratorDataAssetSource) [Read-Write]
- `generator_layer` (QzGeneratorDataAssetLayer) [Read-Write]
- `key_tag_data` (GameplayTag) [Read-Only]
- `tag_pipeline_section` (Name) [Read-Write]
- `use_only_custom_profile` (bool) [Read-Write]

## QzHandbookDataAsset  ←  PrimaryDataAsset < DataAsset < Object
_Qz Handbook Data Asset  **C++ Source:**_
- `handbook_content` (Array[HandbookTabContent]) [Read-Write]
- `support_levels` (GameplayTagContainer) [Read-Write]

## QzInternalContrabandSetDataAsset  ←  PrimaryDataAsset < DataAsset < Object
_Qz Internal Contraband Set Data Asset  **C++ Source:**_
- `items` (Array[QzInternalContrabandItemData]) [Read-Write]

## QzLevelDataAsset  ←  PrimaryDataAsset < DataAsset < Object
_Qz Level Data Asset  **C++ Source:**_
- `level` (World) [Read-Write] Full soft reference to the level. Preferred over LevelName: it carries the package path,
- `level_name` (Name) [Read-Write]
- `tag` (GameplayTag) [Read-Write]

## QzLockedSymptomsDataAsset  ←  PrimaryDataAsset < DataAsset < Object
_Qz Locked Symptoms Data Asset  **C++ Source:**_
- `all_symptoms` (Set[GameplayTag]) [Read-Write]
- `symptoms` (Map[GameplayTag, QzLockedSymptoms]) [Read-Write]

## QzManualGrantToolDataAsset  ←  QzToolDataAsset < PrimaryDataAsset < DataAsset
_Mod tool that is NOT given to the player at the start of the day. Hand it out yourself from your own Blueprint with Get Game Flow > Add Tools (the tool is then saved and stays on the following days).  **C++ Source:**_

## QzModifySymptom_Temperature  ←  QzSymptomModifier < Object < _ObjectBase
_Qz Modify Symptom Temperature  **C++ Source:**_
- `celsius` (Texture2D) [Read-Write]
- `fahrenheit` (Texture2D) [Read-Write]

## QzMusicDataAsset  ←  DataAsset < Object < _ObjectBase
_Qz Music Data Asset  **C++ Source:**_
- `looping_music_types` (Map[QzMusicTypes, Vector2D]) [Read-Write]
- `music_array` (Map[QzMusicTypes, QzMusicArrayStruct]) [Read-Write]
- `music_play_frequency` (Map[QzMusicTypes, Vector2D]) [Read-Write]
- `music_priority` (Map[QzMusicTypes, int32]) [Read-Write]

## QzNPCProfileDataAsset  ←  PrimaryDataAsset < DataAsset < Object
_Qz NPCProfile Data Asset  **C++ Source:**_
- `additional_animation` (QzMovementAdditionalAnimation) [Read-Write]
- `age` (int32) [Read-Write]
- `allowed_actions` (GameplayTagQuery) [Read-Write]
- `animation_layer` (QzNPCAnimationLayerData) [Read-Write]
- `animation_set_tag_override` (GameplayTag) [Read-Write]
- `apartments` (int32) [Read-Write] Apartment number override. Zero keeps random generation.
- `appearance` (QzProfileAppearanceOverrides) [Read-Write]
- `attack_on_accessory_confiscation` (bool) [Read-Write]
- `baggage_color` (LinearColor) [Read-Write]
- `baggage_color_override` (bool) [Read-Write]
- `baggage_container_type` (QzBaggageContainerType) [Read-Write]
- `baggage_list` (Array[GameplayTag]) [Read-Write]
- `baggage_mode` (QzBaggageProfileMode) [Read-Write]
- `baggage_range` (IntPoint) [Read-Write]
- `baggage_type_name` (Name) [Read-Write]
- `baggage_type_override` (bool) [Read-Write]
- `baggage_weights` (QzBaggageGenerateWeights) [Read-Write]
- `bio` (Text) [Read-Write]
- `body_tag` (GameplayTag) [Read-Write]
- `city` (int32) [Read-Write]
- `company_support` (bool) [Read-Write]
- `custom_logic_list` (Array[QzNPCCustomLogic]) [Read-Write]
- `endless_support` (bool) [Read-Write]
- `first_name` (Text) [Read-Write]
- `gender` (QzGender) [Read-Write]
- `has_document` (bool) [Read-Write]
- `healing_symptoms` (Set[GameplayTag]) [Read-Write]
- `hidden_contraband_list` (Array[GameplayTag]) [Read-Write]
- `hidden_contraband_list_locations` (Map[int32, QzHiddenContrabandLocation]) [Read-Write] Key is an index in HiddenContrabandList. Missing entries use any compatible free location.
- `hidden_contraband_mode` (QzHiddenContrabandProfileMode) [Read-Write]
- `hidden_contraband_range` (IntPoint) [Read-Write]
- `hidden_contraband_weights` (QzHiddenContrabandGenerateWeights) [Read-Write]
- `house` (int32) [Read-Write] House number override. Zero keeps random generation.
- `ic_list` (Array[GameplayTag]) [Read-Write]
- `ic_mode` (QzICProfileMode) [Read-Write]
- `ic_range` (IntPoint) [Read-Write]
- `ic_weights` (QzICGenerateWeights) [Read-Write]
- `ignored_company_tags` (GameplayTagContainer) [Read-Write]
- `ignored_symptoms` (Set[GameplayTag]) [Read-Write]
- `last_name` (Text) [Read-Write]
- `max_health` (float) [Read-Write]
- `military_damage` (int32) [Read-Write]
- `name_key` (Name) [Read-Write]
- `override_address` (bool) [Read-Write]
- `override_bio` (bool) [Read-Write]
- `photo_mask` (int32) [Read-Write]
- `player_knockback_strength` (float) [Read-Write]
- `profession` (GameplayTag) [Read-Write]
- `quest_tag_npc` (GameplayTag) [Read-Write]
- `random_age` (bool) [Read-Write]
- `random_gender` (bool) [Read-Write]
- `random_has_document` (bool) [Read-Write]
- `random_name` (bool) [Read-Write]
- `role` (QzNpcRole) [Read-Write]
- `source_profile` (QzSourceProfile) [Read-Write]
- `street` (int32) [Read-Write]
- `supported_company_tags` (GameplayTagContainer) [Read-Write]
- `symptoms_list` (Array[GameplayTag]) [Read-Write]
- `symptoms_list_locations` (Map[int32, Name]) [Read-Write] Key is a zero-based index in SymptomsList. Value overrides the automatically generated location.
- `symptoms_mode` (QzSymptomsProfileMode) [Read-Write]
- `symptoms_range` (IntPoint) [Read-Write]
- `symptoms_weights` (QzSymptomsGenerateWeights) [Read-Write]
- `voice` (GameplayTag) [Read-Write]
- `wanted_npc` (bool) [Read-Write] Only in Miami
- `zombie_transformation_symptoms` (Array[GameplayTag]) [Read-Write]

## QzNPCSymptom  ←  StructBase < _WrapperBase < object
_Qz NPCSymptom  **C++ Source:**_
- `count_worms` (int32) [Read-Write]
- `index` (int32) [Read-Write]
- `location` (Name) [Read-Write]
- `organs` (Array[GameplayTag]) [Read-Write]
- `symptom` (GameplayTag) [Read-Write]
- `texture_map_zone` (QzTextureMapZoneStruct) [Read-Write]
- `uv` (bool) [Read-Write]
- `virtual` (bool) [Read-Write]

## QzNPCSymptomOrganDependence  ←  StructBase < _WrapperBase < object
_Qz NPCSymptom Organ Dependence  **C++ Source:**_
- `organs` (Set[GameplayTag]) [Read-Write]

## QzNewDayData  ←  DataAsset < Object < _ObjectBase
_Qz New Day Data  **C++ Source:**_
- `achievement_type` (QzAchievementType) [Read-Write]
- `activate_defence` (bool) [Read-Write]
- `all_baggage_items` (DataTable) [Read-Write]
- `available_radio_sounds` (Set[GameplayTag]) [Read-Write] Voice
- `available_symptoms` (Set[QzSymptom]) [Read-Write]
- `baggage_data` (QzBaggageSet) [Read-Write]
- `behavior_set` (Array[QzBehaviorType]) [Read-Write]
- `bio_limit` (IntPoint) [Read-Write]
- `body_skin_dirt_weight` (Map[QzSkinDirtType, int32]) [Read-Write]
- `chance_baggage` (float) [Read-Write] BAGGAGE
- `chance_contraband` (float) [Read-Write]
- `chance_doc` (float) [Read-Write]
- `chance_female` (float) [Read-Write] GENDER
- `chance_infected_baggage` (float) [Read-Write]
- `chance_organs_baggage` (int32) [Read-Write] ORGANS CONTRABAND
- `chance_organs_contraband` (int32) [Read-Write]
- `chance_organs_infected` (int32) [Read-Write]
- `clothes_rule` (QzClothesDayRule) [Read-Write] CLOTHES
- `count_quests` (IntPoint) [Read-Write] Dynamic Quests
- `count_uv_baggage_items` (IntPoint) [Read-Write]
- `currency_baggage` (QzCurrencyBaggage) [Read-Write]
- `currency_symptoms` (QzCurrencySymptoms) [Read-Write]
- `daily_data` (QzDailyData) [Read-Write]
- `default_behavior` (QzBehaviorPattern) [Read-Write]
- `defence_generator_data` (QzDefenseTransitionInfo) [Read-Write]
- `ending` (bool) [Read-Write]
- `environment` (QzEnvironment) [Read-Write]
- `evacuation_config` (QzEvacuationScheduleConfig) [Read-Write]
- `face_skin_dirt_probability` (Map[QzSkinDirtType, int32]) [Read-Write]
- `first_context_guide_tag` (GameplayTag) [Read-Write] GLOBAL
- `founded_symptoms` (Set[QzSymptom]) [Read-Write]
- `free_resources` (Map[GameplayTag, int32]) [Read-Write] BASE
- `full_random_range` (IntPoint) [Read-Write]
- `full_random_roles` (Map[QzNpcRole, float]) [Read-Write]
- `health_data` (QzHealthDataAsset) [Read-Write]
- `ill_range` (IntPoint) [Read-Write]
- `intro` (bool) [Read-Write] INTRO
- `intro_environment` (QzEnvironment) [Read-Write]
- `intro_level_name` (Name) [Read-Write]
- `intro_tag` (Name) [Read-Write]
- `main_quest_class` (Class) [Read-Write]
- `military_evacuation_reward` (QzFactionRewardMode) [Read-Write]
- `normal_range` (IntPoint) [Read-Write] ROLE
- `open_features_in_start_day` (GameplayTagContainer) [Read-Write]
- `organs_contraband_total_points_amount` (IntPoint) [Read-Write]
- `override_profiles` (Map[int32, QzProfileDataAsset]) [Read-Write]
- `override_symptoms` (Map[QzSymptom, QzSymptomCategory]) [Read-Write]
- `override_symptoms_prices` (Map[QzSymptom, float]) [Read-Write]
- `override_triggers_quests` (Array[QzTagQuestEntry]) [Read-Write] Quests
- `override_weather` (bool) [Read-Write]
- `prices_baggage` (QzPricesBaggage) [Read-Write]
- `profiles` (Array[QzProfileDataAsset]) [Read-Write]
- `prohibit_triggers_quests` (Array[QzTagQuestEntry]) [Read-Write]
- `quarantine_normal_range` (IntPoint) [Read-Write]
- `quarantine_zombie_range` (IntPoint) [Read-Write]
- `quest_catalog` (QzQuestCatalogDataV2) [Read-Write]
- `quests` (Array[QzDynamicQuestDataAsset]) [Read-Write]
- `queue_type` (QzGenerationQueueType) [Read-Write] QUEUE
- `science_evacuation_reward` (QzFactionRewardMode) [Read-Write]
- `shoot_activities_data_asset` (QzDailyShootActivitiesDataAsset) [Read-Write] ACTIVITIES
- `skin_pigmentation_weight` (Map[QzSkinPigmentationType, float]) [Read-Write] SKIN
- `symptoms_data` (QzSymptomsDataAsset) [Read-Write] SYMPTOMS
- `today_evacuation` (bool) [Read-Write] Evacuation
- `uv_virus_range` (IntPoint) [Read-Write]
- `virus_range` (IntPoint) [Read-Write]
- `weight_uv_all` (float) [Read-Write]
- `weight_uv_baggage` (float) [Read-Write]
- `weight_uv_symptoms` (float) [Read-Write]

## QzProfileAppearanceOverrides  ←  StructBase < _WrapperBase < object
_Qz Profile Appearance Overrides  **C++ Source:**_
- `age_visual` (QzProfileAgeVisualAppearance) [Read-Write]
- `beard` (QzProfileHairAppearance) [Read-Write]
- `body` (QzProfileBodyAppearance) [Read-Write]
- `body_skin_texture` (QzProfileSkinTextureAppearance) [Read-Write]
- `clothing` (QzProfileClothingAppearance) [Read-Write]
- `disable_age_visual` (bool) [Read-Write]
- `disable_beard` (bool) [Read-Write]
- `disable_body_skin_texture` (bool) [Read-Write]
- `disable_eyelashes` (bool) [Read-Write]
- `disable_eyes` (bool) [Read-Write]
- `disable_face` (bool) [Read-Write]
- `disable_face_skin_texture` (bool) [Read-Write]
- `disable_glasses` (bool) [Read-Write]
- `disable_hair` (bool) [Read-Write]
- `disable_hair_color` (bool) [Read-Write]
- `disable_hat` (bool) [Read-Write]
- `disable_mustache` (bool) [Read-Write]
- `disable_other_accessories` (bool) [Read-Write]
- `disable_outfit_color` (bool) [Read-Write]
- `disable_skin_overlays` (bool) [Read-Write]
- `disable_skin_tone` (bool) [Read-Write]
- `eyelashes` (QzProfileEyelashesAppearance) [Read-Write]
- `eyes` (QzProfileEyeAppearance) [Read-Write]
- `face` (QzProfileFaceAppearance) [Read-Write]
- `face_skin_texture` (QzProfileSkinTextureAppearance) [Read-Write]
- `glasses` (QzProfileGlassesAppearance) [Read-Write]
- `hair` (QzProfileHairAppearance) [Read-Write]
- `hair_color` (QzProfileHairColorAppearance) [Read-Write]
- `hat` (QzProfileHatAppearance) [Read-Write]
- `mustache` (QzProfileHairAppearance) [Read-Write]
- `other_accessories` (Array[QzProfileOtherAccessoryAppearance]) [Read-Write]
- `outfit_color` (QzProfileOutfitColorAppearance) [Read-Write]
- `skin_overlays` (Array[QzProfileSkinOverlayAppearance]) [Read-Write]
- `skin_tone` (QzProfileSkinToneAppearance) [Read-Write]

## QzProfileDataAsset  ←  DataAsset < Object < _ObjectBase
_Qz Profile Data Asset  **C++ Source:**_
- `profile` (QzStaticProfile) [Read-Write]
- `random_behavior` (bool) [Read-Write]
- `random_body_shape` (bool) [Read-Write]
- `random_gender` (bool) [Read-Write]
- `random_pigmentation` (bool) [Read-Write]
- `random_race` (bool) [Read-Write]
- `skin` (QzCvOverrideSkin) [Read-Write]

## QzQueueDay  ←  StructBase < _WrapperBase < object
_Qz Queue Day  **C++ Source:**_
- `ill` (int32) [Read-Write]
- `normal` (int32) [Read-Write]
- `q_normal` (int32) [Read-Write]
- `q_zombie` (int32) [Read-Write]
- `uv_virus` (int32) [Read-Write]
- `zombie` (int32) [Read-Write]

## QzReactionRule  ←  Object < _ObjectBase < _WrapperBase
_Qz Reaction Rule  **C++ Source:**_
- `category` (QzReactionCategory) [Read-Write]
- `female_sounds` (Array[QzReactionSound]) [Read-Write]
- `interval` (Vector2D) [Read-Write]
- `male_sounds` (Array[QzReactionSound]) [Read-Write]
- `probability` (float) [Read-Write]
- `type` (GameplayTag) [Read-Write]

## QzStaticNPCSkinDataAsset  ←  PrimaryDataAsset < DataAsset < Object
_Skin override for hand-placed (static) NPCs such as the checkpoint staff. The base game ships no assets of this type - they come from mods (UGC) _
- `materials` (Map[int32, MaterialInterface]) [Read-Write] Material overrides per mesh slot index
- `mesh` (SkeletalMesh) [Read-Write] Optional full mesh replacement; keep null to only swap materials
- `npc_tag` (GameplayTag) [Read-Write] Which placed NPC this skin applies to (e.g. NPC.Skin.Doc)

## QzStaticProfile  ←  StructBase < _WrapperBase < object
_Qz Static Profile  **C++ Source:**_
- `baggage` (Array[QzBaggageProfile]) [Read-Write]
- `baggage_color` (LinearColor) [Read-Write]
- `baggage_container_type` (QzBaggageContainerType) [Read-Write]
- `baggage_type` (QzBaggageTypeData) [Read-Write]
- `behavior_type` (QzBehaviorPattern) [Read-Write]
- `blocked_animation_flags` (Set[QzAnimationFlag]) [Read-Write]
- `body` (GameplayTag) [Read-Write]
- `body_shape` (QzNPCBodyShape) [Read-Write]
- `character` (bool) [Read-Write]
- `character_name` (Name) [Read-Write]
- `document` (QzDocument) [Read-Write]
- `dynamic_quest_id` (int32) [Read-Write]
- `event` (QzNPCEvent) [Read-Write]
- `flags` (Set[QzProfileFlags]) [Read-Write]
- `for_quest` (bool) [Read-Write]
- `gender` (QzGender) [Read-Write]
- `heal_all_symptoms` (bool) [Read-Write]
- `healing_set` (Set[GameplayTag]) [Read-Write]
- `hidden_contraband` (Array[QzHiddenContrabandProfile]) [Read-Write]
- `max_health` (float) [Read-Write]
- `organs_contraband` (Array[QzOrgansContrabandProfile]) [Read-Write]
- `photo_mask` (int32) [Read-Write]
- `play_custom_replicas` (bool) [Read-Write]
- `player_knockback_strength` (float) [Read-Write]
- `profession` (GameplayTag) [Read-Write]
- `quest_tag_npc` (GameplayTag) [Read-Write]
- `race` (QzRaceType) [Read-Write]
- `role` (QzNpcRole) [Read-Write]
- `skin_pigmentation` (QzSkinPigmentationType) [Read-Write]
- `stethoscope_socket` (Name) [Read-Write]
- `stethoscope_sockets` (Array[Name]) [Read-Write]
- `twitch_id` (int32) [Read-Write]
- `type` (QzSourceProfile) [Read-Write]
- `voice` (GameplayTag) [Read-Write]
- `voice_old` (QzVoiceType) [Read-Write]
- `wanted` (bool) [Read-Write]

## QzSymptom  ←  StructBase < _WrapperBase < object
_Qz Symptom  **C++ Source:**_
- `color_name_category` (LinearColor) [Read-Write]
- `custom_category` (QzSymptomCategoryCustom) [Read-Write]
- `label_category` (QzSymptomCategory) [Read-Write]
- `name_category` (Text) [Read-Write]

## QzSymptomAnimationHint  ←  StructBase < _WrapperBase < object
_Qz Symptom Animation Hint  **C++ Source:**_
- `female` (QzSymptomAnimationMontagePair) [Read-Write]
- `interval` (Vector2D) [Read-Write]
- `male` (QzSymptomAnimationMontagePair) [Read-Write]

## QzSymptomAnimationMontagePair  ←  StructBase < _WrapperBase < object
_Qz Symptom Animation Montage Pair  **C++ Source:**_
- `body_montage` (AnimMontage) [Read-Write]
- `face_montage` (AnimMontage) [Read-Write]

## QzSymptomCategory  ←  EnumBase < _WrapperBase < object
_EQz Symptom Category  **C++ Source:**_

## QzSymptomCategoryCustom  ←  EnumBase < _WrapperBase < object
_EQz Symptom Category Custom  **C++ Source:**_

## QzSymptomDataAsset  ←  PrimaryDataAsset < DataAsset < Object
_Qz Symptom Data Asset  **C++ Source:**_
- `blocking_animation_flags` (Set[QzAnimationFlag]) [Read-Write]
- `can_spawn` (bool) [Read-Write]
- `category` (QzSymptomCategory) [Read-Only]
- `custom_category` (QzSymptomCategoryCustom) [Read-Write]
- `flags_mask` (int64) [Read-Write]
- `info` (QzSymptomsListInfo) [Read-Write]
- `laboratory_symptom_settings` (QzSymptomInLaboratory) [Read-Write]
- `levels` (GameplayTagContainer) [Read-Write]
- `required_animation_flags` (Set[QzAnimationFlag]) [Read-Write]
- `rule` (QzSymptomFillingRule) [Read-Write]
- `section` (GameplayTag) [Read-Write]
- `sorted_index` (int32) [Read-Write]
- `tag` (GameplayTag) [Read-Write]
- `unique` (bool) [Read-Write]
- `uv_map_zones` (Set[QzUVMapZone]) [Read-Write]
- `virtual` (bool) [Read-Write]

## QzSymptomDoubleLayersDataAsset  ←  PrimaryDataAsset < DataAsset < Object
_Qz Symptom Double Layers Data Asset  **C++ Source:**_
- `covers` (Map[GameplayTag, QzCoverSymptom]) [Read-Write]
- `hidden_symptoms` (Map[GameplayTag, QzUVHiddenSymptom]) [Read-Write]

## QzSymptomFillingRule  ←  Object < _ObjectBase < _WrapperBase
_Qz Symptom Filling Rule  **C++ Source:**_
- `priority` (int32) [Read-Write]

## QzSymptomFillingRule_Animation  ←  QzSymptomFillingRule < Object < _ObjectBase
_Qz Symptom Filling Rule Animation  **C++ Source:**_
- `animation_layer` (QzNPCAnimationLayerData) [Read-Write]

## QzSymptomFillingRule_Decal  ←  QzSymptomFillingRule < Object < _ObjectBase
_Qz Symptom Filling Rule Decal  **C++ Source:**_
- `decals` (QzHealthDecalOnSkin) [Read-Write]
- `sockets` (Set[QzSocketName]) [Read-Write]

## QzSymptomFillingRule_Dog  ←  QzSymptomFillingRule < Object < _ObjectBase
_Qz Symptom Filling Rule Dog  **C++ Source:**_
- `reaction_config` (QzDogReactionConfig) [Read-Write]

## QzSymptomFillingRule_DoubleLayer  ←  QzSymptomFillingRule < Object < _ObjectBase
_Qz Symptom Filling Rule Double Layer  **C++ Source:**_
- `cover_symptoms_uv` (Set[GameplayTag]) [Read-Write]
- `hidden_symptoms_uv` (Set[GameplayTag]) [Read-Write]

## QzSymptomFillingRule_Electroshock  ←  QzSymptomFillingRule < Object < _ObjectBase
_Qz Symptom Filling Rule Electroshock  **C++ Source:**_
- `reaction_config` (QzElectroshockReactionConfig) [Read-Write]

## QzSymptomFillingRule_Material  ←  QzSymptomFillingRule < Object < _ObjectBase
_Qz Symptom Filling Rule Material  **C++ Source:**_
- `parameters` (QzSymptomsParametersStruct) [Read-Write]

## QzSymptomFillingRule_OrganMaterial  ←  QzSymptomFillingRule < Object < _ObjectBase
_Qz Symptom Filling Rule Organ Material  **C++ Source:**_
- `material` (QzOrganMaterial) [Read-Write]

## QzSymptomFillingRule_OrganReplace  ←  QzSymptomFillingRule < Object < _ObjectBase
_Qz Symptom Filling Rule Organ Replace  **C++ Source:**_
- `material_data` (QzSoftMaterialParameterStruct) [Read-Write]
- `organ_dependence` (Map[GameplayTag, QzNPCSymptomOrganDependence]) [Read-Write]
- `organs_replacement` (Map[GameplayTag, QzSymptomReplaceOrgan]) [Read-Write]

## QzSymptomFillingRule_Other  ←  QzSymptomFillingRule < Object < _ObjectBase
_Qz Symptom Filling Rule Other  **C++ Source:**_

## QzSymptomFillingRule_TextureMaps  ←  QzSymptomFillingRule < Object < _ObjectBase
_Qz Symptom Filling Rule Texture Maps  **C++ Source:**_
- `female_texture_map_zones` (Set[QzFemaleTextureMapZone]) [Read-Write]
- `male_texture_map_zones` (Set[QzMaleTextureMapZone]) [Read-Write]
- `placement_texture_map` (QzTextureMapArrayStruct) [Read-Write]
- `texture_map_zone_on_face` (bool) [Read-Write]

## QzSymptomFillingRule_Worms  ←  QzSymptomFillingRule < Object < _ObjectBase
_Qz Symptom Filling Rule Worms  **C++ Source:**_
- `count_worms` (IntPoint) [Read-Write]

## QzSymptomInLaboratory  ←  StructBase < _WrapperBase < object
_Qz Symptom in Laboratory  **C++ Source:**_
- `laboratory_organ_ratio_female` (QzOrganSymptom) [Read-Write]
- `laboratory_organ_ratio_male` (QzOrganSymptom) [Read-Write]
- `symptom_bunches` (GameplayTagContainer) [Read-Write]
- `symptom_weight` (float) [Read-Write]

## QzSymptomModifier  ←  Object < _ObjectBase < _WrapperBase
_Qz Symptom Modifier  **C++ Source:**_

## QzSymptomPlacement  ←  EnumBase < _WrapperBase < object
_EQz Symptom Placement  **C++ Source:**_

## QzSymptomReplaceOrgan  ←  StructBase < _WrapperBase < object
_Qz Symptom Replace Organ  **C++ Source:**_
- `meshes_for_body` (Map[GameplayTag, SkeletalMesh]) [Read-Write]

## QzSymptomRuleType  ←  EnumBase < _WrapperBase < object
_EQz Symptom Rule Type  **C++ Source:**_

## QzSymptomSectionDataAsset  ←  PrimaryDataAsset < DataAsset < Object
_Qz Symptom Section Data Asset  **C++ Source:**_
- `info` (QzTextCategory) [Read-Write]
- `miami_priority` (int32) [Read-Write]
- `priority` (int32) [Read-Write]
- `tag` (GameplayTag) [Read-Write]

## QzSymptomSocketData  ←  TableRowBase < StructBase < _WrapperBase
_Qz Symptom Socket Data  **C++ Source:**_
- `body_region_name` (Name) [Read-Write]
- `clothes_types` (QzClothesTypes) [Read-Write]
- `cost_multiplier` (float) [Read-Write]
- `head` (bool) [Read-Write]
- `short_clothes` (bool) [Read-Write]
- `socket_name` (Name) [Read-Write]
- `weight` (float) [Read-Write]
- `zone` (QzPlacementZone) [Read-Write]

## QzSymptomStaticInfo  ←  StructBase < _WrapperBase < object
_Qz Symptom Static Info  **C++ Source:**_
- `anim_symptom` (AnimSequenceBase) [Read-Write]
- `female_texture_map_zones` (Set[QzFemaleTextureMapZone]) [Read-Write]
- `male_texture_map_zones` (Set[QzMaleTextureMapZone]) [Read-Write]
- `placement_type` (QzPlacementType) [Read-Only]
- `sockets` (Set[QzSocketName]) [Read-Write]
- `texture_map_zone_on_face` (bool) [Read-Write]

## QzSymptomZoneData  ←  StructBase < _WrapperBase < object
_Qz Symptom Zone Data  **C++ Source:**_
- `body_region_name` (Name) [Read-Write]
- `clothes_types` (QzClothesTypes) [Read-Write]
- `cost_multiplier` (float) [Read-Write]
- `head` (bool) [Read-Write]
- `multiple_symptoms_spawn` (bool) [Read-Write]
- `short` (bool) [Read-Write]

## QzSymptomsArray  ←  StructBase < _WrapperBase < object
_Qz Symptoms Array  **C++ Source:**_
- `symptoms_tags` (Array[GameplayTag]) [Read-Write]

## QzSymptomsDataAsset  ←  DataAsset < Object < _ObjectBase
_Qz Symptoms Data Asset  **C++ Source:**_
- `female_zone` (Map[QzFemaleTextureMapZone, QzSymptomZoneData]) [Read-Write]
- `info` (Map[QzSymptom, QzSymptomStaticInfo]) [Read-Write]
- `male_zone` (Map[QzMaleTextureMapZone, QzSymptomZoneData]) [Read-Write]
- `socket_zone` (Map[QzSocketName, QzSymptomZoneData]) [Read-Write]
- `unavailable_symptoms_to_add` (Set[QzSymptom]) [Read-Write]

## QzSymptomsGenerateWeights  ←  StructBase < _WrapperBase < object
_Qz Symptoms Generate Weights  **C++ Source:**_
- `categories` (Map[QzSymptomCategory, float]) [Read-Write]
- `items` (Map[GameplayTag, float]) [Read-Write]
- `sections` (Map[GameplayTag, float]) [Read-Write]

## QzSymptomsInfoDataAsset  ←  DataAsset < Object < _ObjectBase
_Qz Symptoms Info Data Asset  **C++ Source:**_
- `category_name` (Array[QzTextCategory]) [Read-Write]
- `inspection_category_name` (Array[QzSymptom]) [Read-Write]
- `label_disease` (Texture2D) [Read-Write]
- `label_mixed` (Texture2D) [Read-Write]
- `label_virus` (Texture2D) [Read-Write]
- `sound_texture` (Texture2D) [Read-Write]
- `unknown_texture` (Texture2D) [Read-Write]

## QzSymptomsListInfo  ←  StructBase < _WrapperBase < object
_Qz Symptoms List Info  **C++ Source:**_
- `custom_symptom` (bool) [Read-Write]
- `days_to_open` (int32) [Read-Only]
- `description_symptom` (QzDescriptionSymptom) [Read-Write]
- `feature_tag_for_custom_symptom` (GameplayTag) [Read-Write]
- `modifiers` (Array[QzSymptomModifier]) [Read-Write]
- `name_symptom` (Text) [Read-Write]
- `sound_symptom` (bool) [Read-Write]
- `texture_symptom` (Texture2D) [Read-Write]
- `tutorial_tag` (GameplayTag) [Read-Write]

## QzSymptomsParametersStruct  ←  StructBase < _WrapperBase < object
_Qz Symptoms Parameters Struct  **C++ Source:**_
- `body_parameters` (QzBodyParametersStruct) [Read-Write]
- `face_parameters` (Array[QzFaceParametersStruct]) [Read-Write]

## QzSymptomsProfileMode  ←  EnumBase < _WrapperBase < object
_EQz Symptoms Profile Mode  **C++ Source:**_

## QzSymptomsStatics  ←  BlueprintFunctionLibrary < Object < _ObjectBase
_Qz Symptoms Statics  **C++ Source:**_

## QzSymptomsSubsystem  ←  QzWorldSubsystemBase < WorldSubsystem < Subsystem
_Qz Symptoms Subsystem  **C++ Source:**_

## QzSymptomsUVDataAsset  ←  DataAsset < Object < _ObjectBase
_Qz Symptoms UVData Asset  **C++ Source:**_
- `smokes_for_ill_range` (IntPoint) [Read-Write]
- `uv_collection` (MaterialParameterCollection) [Read-Write]
- `uv_smoke` (NiagaraSystem) [Read-Write]
- `uv_smoke_niagara_params_struct` (QzNiagaraParamsStruct) [Read-Write]

## QzToolComponent  ←  ActorComponent < Object < _ObjectBase
_Qz Tool Component  **C++ Source:**_
- `activated_sound` (SoundBase) [Read-Write]
- `asset_user_data` (Array[AssetUserData]) [Read-Write] Array of user data stored with the component
- `asset_user_data_editor_only` (Array[AssetUserData]) [Read-Write] Array of user data stored with the component
- `audio_fade_in_time` (float) [Read-Write]
- `audio_fade_out_time` (float) [Read-Write]
- `auto_activate` (bool) [Read-Write] Whether the component is activated at creation or must be explicitly activated.
- `can_ever_affect_navigation` (bool) [Read-Write] Whether this component can potentially influence navigation
- `collision_trace_channel` (CollisionChannel) [Read-Write]
- `component_tags` (Array[Name]) [Read-Write] Array of tags that can be used for grouping and categorizing. Can also be accessed from scripting.
- `deactivated_sound` (SoundBase) [Read-Write]
- `draw_debug` (bool) [Read-Write]
- `editable_when_inherited` (bool) [Read-Write] True if this component can be modified when it was inherited from a parent actor class
- `is_editor_only` (bool) [Read-Write] If true, the component will be excluded from non-editor builds
- `mode_tag` (GameplayTag) [Read-Write]
- `on_component_activated` (ActorComponentActivatedSignature) [Read-Write] Called when the component has been activated, with parameter indicating if it was from a reset
- `on_component_deactivated` (ActorComponentDeactivateSignature) [Read-Write] Called when the component has been deactivated
- `on_skin_change` (OnSkinChange) [Read-Write]
- `on_tool_activated` (OnToolActivated) [Read-Write]
- `on_tool_deactivated` (OnToolDeactivated) [Read-Write]
- `on_tool_upgrade` (OnToolUpgrade) [Read-Write]
- `primary_component_tick` (ActorComponentTickFunction) [Read-Write] Main tick function for the Component
- `replicate_using_registered_sub_object_list` (bool) [Read-Write] When true the replication system will only replicate the registered subobjects list
- `replicates` (bool) [Read-Write] Is this component currently replicating? Should the network code consider it for replication? Owning Actor must be replicating first!
- `return_physical_material` (bool) [Read-Write]
- `skin_type` (QzToolSkinType) [Read-Write]
- `tag` (GameplayTag) [Read-Write]
- `tool_type` (QzToolType) [Read-Write]
- `trace_complex` (bool) [Read-Write]
- `trace_distance` (float) [Read-Write]
- `trace_radius` (float) [Read-Write]
- `value_visual` (str) [Read-Write]

## QzToolDataAsset  ←  PrimaryDataAsset < DataAsset < Object
_Qz Tool Data Asset  **C++ Source:**_
- `item_data_asset` (SItemDataAsset) [Read-Write]
- `tag` (GameplayTag) [Read-Write]

## QzTool_ActionAbility  ←  SGameplayAbility < GameplayAbility < Object
_Qz Tool Action Ability  **C++ Source:**_
- `ability_tags` (GameplayTagContainer) [Read-Write]
- `ability_triggers` (Array[AbilityTriggerData]) [Read-Write] Triggers to determine if this ability should execute in response to an event
- `action_index` (uint8) [Read-Write]
- `activate_ability_on_granted` (bool) [Read-Write]
- `activation_blocked_tags` (GameplayTagContainer) [Read-Write] This ability is blocked if the activating actor/component has any of these tags
- `activation_owned_tags` (GameplayTagContainer) [Read-Write] Tags to apply to activating owner while this ability is active. These are replicated if ReplicateActivationOwnedTags is enabled in AbilitySystemGlobals.
- `activation_required_tags` (GameplayTagContainer) [Read-Write] This ability can only be activated if the activating actor/component has all of these tags
- `block_abilities_with_tag` (GameplayTagContainer) [Read-Write] Abilities with these tags are blocked while this ability is active
- `cancel_abilities_with_tag` (GameplayTagContainer) [Read-Write] Abilities with these tags are cancelled when this ability is executed
- `current_activation_info` (GameplayAbilityActivationInfo) [Read-Write] This is information specific to this instance of the ability. E.g, whether it is predicting, authoring, confirmed, etc.
- `current_event_data` (GameplayEventData) [Read-Write] Information specific to this instance of the ability, if it was activated by an event
- `instancing_policy` (GameplayAbilityInstancingPolicy) [Read-Write] How the ability is instanced when executed. This limits what an ability can do in its implementation.
- `mark_pending_kill_on_ability_end` (bool) [Read-Write]
- `net_execution_policy` (GameplayAbilityNetExecutionPolicy) [Read-Write] How does an ability execute on the network. Does a client "ask and predict", "ask and wait", "don't ask (just do it)".
- `net_security_policy` (GameplayAbilityNetSecurityPolicy) [Read-Write] What protections does this ability have? Should the client be allowed to request changes to the execution of the ability?
- `release_event` (bool) [Read-Write]
- `replicate_input_directly` (bool) [Read-Write] If true, this ability will always replicate input press/release events to the server.
- `replication_policy` (GameplayAbilityReplicationPolicy) [Read-Write] How an ability replicates state/events to everyone on the network. Replication is not required for NetExecutionPolicy.
- `retrigger_instanced_ability` (bool) [Read-Write] if true, and trying to activate an already active instanced ability, end it and re-trigger it.
- `server_respects_remote_ability_cancellation` (bool) [Read-Write] If this is set, the server-side version of the ability can be canceled by the client-side version. The client-side version can always be canceled by the server.
- `source_blocked_tags` (GameplayTagContainer) [Read-Write] This ability is blocked if the source actor/component has any of these tags
- `source_required_tags` (GameplayTagContainer) [Read-Write] This ability can only be activated if the source actor/component has all of these tags
- `target_blocked_tags` (GameplayTagContainer) [Read-Write] This ability is blocked if the target actor/component has any of these tags
- `target_required_tags` (GameplayTagContainer) [Read-Write] This ability can only be activated if the target actor/component has all of these tags
- `tickable` (bool) [Read-Write]

## QzTool_Dog  ←  QzToolComponent < ActorComponent < Object
_Qz Tool Dog  **C++ Source:**_

## QzTool_Electroshock  ←  QzToolComponent < ActorComponent < Object
_Qz Tool Electroshock  **C++ Source:**_
- `electroshock_data` (QzElectroshockDataAsset) [Read-Write]
- `on_charge_changed` (QzElectroshockChargeChanged) [Read-Write]
- `on_charge_started` (QzElectroshockChargeStarted) [Read-Write]
- `on_cooldown_changed` (QzElectroshockCooldownChanged) [Read-Write]
- `on_cooldown_finished` (QzElectroshockCooldownFinished) [Read-Write]
- `on_cooldown_started` (QzElectroshockCooldownStarted) [Read-Write]
- `on_equal_zone_charge_changed` (QzElectroshockEqualZoneChargeChanged) [Read-Write]
- `on_hit` (QzElectroshockHit) [Read-Write]
- `on_shock_applied` (QzElectroshockApplied) [Read-Write]

## QzTool_FlashLight  ←  QzToolComponent < ActorComponent < Object
_Qz Tool Flash Light  **C++ Source:**_

## QzTool_HeartRateMonitor  ←  QzToolComponent < ActorComponent < Object
_Qz Tool Heart Rate Monitor  **C++ Source:**_
- `max_distance` (float) [Read-Write]

## QzTool_MedicalHammer  ←  QzToolComponent < ActorComponent < Object
_Qz Tool Medical Hammer  **C++ Source:**_
- `absent_reflex_force` (float) [Read-Write]
- `check_distance` (float) [Read-Write]
- `crossed_reflex_force` (float) [Read-Write]
- `eye_radius` (float) [Read-Write]
- `hammer_bones_correct` (Array[QzHammerHitZone]) [Read-Write]
- `hammer_hit_count_to_react` (Array[QzMedHammerHitStruct]) [Read-Write]
- `hammer_hit_force` (float) [Read-Write]
- `hit_duration` (float) [Read-Write]
- `hitting` (bool) [Read-Write]
- `medical_hammer_asset` (QzMedicalHammerAsset) [Read-Write]
- `npc_hit_sound` (SoundBase) [Read-Write]
- `swing_hit_sound` (SoundBase) [Read-Write]
- `zombie_hit_multiplier` (float) [Read-Write]

## QzTool_MultiTool  ←  QzToolComponent < ActorComponent < Object
_Qz Tool Multi Tool  **C++ Source:**_
- `on_multi_tool_activate` (OnMultiToolActivateEvent) [Read-Write]
- `on_multi_tool_deactivate` (OnMultiToolDeactivateEvent) [Read-Write]
- `on_multi_tool_update` (OnMultiToolUpdateEvent) [Read-Write]
- `pulse_thresholds` (Array[int32]) [Read-Write]
- `result_sounds` (Array[SoundBase]) [Read-Write]
- `temp_thresholds` (Array[int32]) [Read-Write]
- `time_delay` (float) [Read-Write]

## QzTool_Scanner  ←  QzToolComponent < ActorComponent < Object
_Qz Tool Scanner  **C++ Source:**_
- `direction_parameter_name` (Name) [Read-Write]
- `enable_parameter_name` (Name) [Read-Write]
- `height` (float) [Read-Write]
- `height_parameter_name` (Name) [Read-Write]
- `inspection_light_component_tag` (Name) [Read-Write]
- `material_parameter_collection` (MaterialParameterCollection) [Read-Write]
- `on_scanner_params_change` (OnScannerParamsChange) [Read-Write]
- `origin_parameter_name` (Name) [Read-Write]
- `radius` (float) [Read-Write]
- `radius_parameter_name` (Name) [Read-Write]
- `upgrade_dirt_name` (Name) [Read-Write]

## QzTool_Spectrometer  ←  QzToolComponent < ActorComponent < Object
_Qz Tool Spectrometer  **C++ Source:**_

## QzTool_Stethoscope  ←  QzToolComponent < ActorComponent < Object
_Qz Tool Stethoscope  **C++ Source:**_
- `audio_component` (AudioComponent) [Read-Write]
- `breath_colors` (Map[GameplayTag, LinearColor]) [Read-Write]
- `cat_audio_component` (AudioComponent) [Read-Write]
- `default_color` (LinearColor) [Read-Write]
- `default_upgrade_color` (LinearColor) [Read-Write]
- `disease_breath_symptom` (GameplayTag) [Read-Write]
- `lungs_enable` (Name) [Read-Write]
- `max_distance_to_socket` (float) [Read-Write]
- `min_distance_to_show_colors` (float) [Read-Write]
- `min_distance_to_socket` (float) [Read-Write]
- `mixed_amplitude` (float) [Read-Write]
- `mixed_breath_symptom` (GameplayTag) [Read-Write]
- `normal_amplitude` (float) [Read-Write]
- `on_stethoscope_color_change` (QzStethoscopeColorChange) [Read-Write]
- `on_stethoscope_update` (QzStethoscopeUpdate) [Read-Write]
- `parameter_collection` (MaterialParameterCollection) [Read-Write]
- `parameter_name` (Name) [Read-Write]
- `sound_mix` (SoundMix) [Read-Write]
- `speed` (float) [Read-Write]
- `virus_amplitude` (float) [Read-Write]
- `virus_breath_symptom` (GameplayTag) [Read-Write]

## QzTool_Syringe  ←  QzToolComponent < ActorComponent < Object
_Qz Tool Syringe  **C++ Source:**_
- `inject_montage` (AnimMontage) [Read-Write]
- `inject_sound` (SoundBase) [Read-Write]
- `injecting` (bool) [Read-Write]
- `not_sound` (SoundBase) [Read-Write]
- `on_change_blood` (OnSyringeChangeBlood) [Read-Write]
- `on_syringe_complete` (OnSyringeComplete) [Read-Write]
- `on_update_result` (OnUpdateResult) [Read-Write]
- `zombie_sound` (SoundBase) [Read-Write]

## QzTool_Thermometer  ←  QzToolComponent < ActorComponent < Object
_Qz Tool Thermometer  **C++ Source:**_
- `temperature_curve` (CurveLinearColor) [Read-Write]
- `time_delay` (float) [Read-Write]

## QzTool_UVGlowStick  ←  QzToolComponent < ActorComponent < Object
_Qz Tool UVGlow Stick  **C++ Source:**_

## QzTool_UVStick  ←  QzToolComponent < ActorComponent < Object
_Qz Tool UVStick  **C++ Source:**_

## QzTool_WantedNotebook  ←  QzToolComponent < ActorComponent < Object
_Collects the runtime portraits produced by Wanted photo points and exposes them as pages that can be rendered by the notebook tool Blueprint. _
- `auto_discover_photo_points` (bool) [Read-Write]
- `current_page_index` (int32) [Read-Write]
- `on_wanted_page_changed` (OnWantedNotebookPageChanged) [Read-Write]
- `on_wanted_photo_textures_changed` (OnWantedNotebookPhotoTexturesChanged) [Read-Write] Sends all Wanted portrait textures when the notebook is equipped or the captured photos change.
- `on_wanted_photos_changed` (OnWantedNotebookPhotosChanged) [Read-Write]
- `photo_sources` (Array[QzWantedNPCPhotoPoint]) [Read-Write] Explicit sources are combined with auto-discovered photo points.
- `photos_per_page` (int32) [Read-Write]
- `wanted_photos` (Array[QzWantedNPCPhoto]) [Read-Write]

## QzTool_XRay  ←  QzToolComponent < ActorComponent < Object
_Qz Tool XRay  **C++ Source:**_
- `eye_radius` (float) [Read-Write]
- `input_action` (InputAction) [Read-Write]
- `on_no_signal` (OnNoSignal) [Read-Write]
- `on_npc_on_scan` (OnNPCOnScan) [Read-Write]
- `on_organs_contraband_is_allowed` (OnOrgansContrabandIsAllowed) [Read-Write]
- `tablet_in_x_ray_mode_material` (MaterialInstance) [Read-Write]
- `tablet_material_index` (int32) [Read-Write]
- `x_ray_staff_effect` (NiagaraSystem) [Read-Write]
- `x_ray_staff_effect_component` (NiagaraComponent) [Read-Write]
- `zoom_config` (QzZoomConfig) [Read-Write]

## UGCPackage  ←  StructBase < _WrapperBase < object
_Structure containing data associated with this package  **C++ Source:**_
- `author` (str) [Read-Write] Author of the UGC package. Can be empty.
- `content_path` (str) [Read-Write] Path to the Content directory within the package path (e.g., "/RedSpaceship/Content").
- `description` (str) [Read-Write] Description of the UGC package. Can be empty.
- `engine_version` (str) [Read-Write] Engine version the UGC package was built for. Can be empty.
- `friendly_name` (str) [Read-Write] Friendly name of the UGC package (e.g., "RedSpaceship").
- `mount_state` (UGCPackageMountState) [Read-Write] Mount state of the UGC package.
- `mounted_pak_file_paths` (Array[str]) [Read-Write] Mounted pak file paths for the UGC package. Used to keep track of mounted pak files for the package, such as to
- `package_path` (str) [Read-Write] Path to the UGC package itself (e.g., "/RedSpaceship").

## UGCPackageMountState  ←  EnumBase < _WrapperBase < object
_EUGCPackage Mount State  **C++ Source:**_

## UGCPackageWrapper  ←  Object < _ObjectBase < _WrapperBase
_Blueprint accessible wrapper around a UGC Package Needed if the consumer wants a UObject-based UGC Package, for example in UMG when using a list view _
- `underlying` (UGCPackage) [Read-Write] UGC Package

## UGCRejectReason  ←  EnumBase < _WrapperBase < object
_QZ: reasons a UGC plugin can be rejected during validation, surfaced to UI/telemetry  **C++ Source:**_

## UGC_Metadata  ←  PrimaryDataAsset < DataAsset < Object
_Metadata asset to be included in every UGC plugin  **C++ Source:**_
- `io_store_enabled` (bool) [Read-Write] * Whether IoStore was enabled during the cooking process
- `primary_asset_types_to_scan` (Array[PrimaryAssetTypeInfo]) [Read-Write] * List of asset types to scan at startup
- `unreal_version` (str) [Read-Write] * The version of Unreal Engine this UGC was used to cooked with
