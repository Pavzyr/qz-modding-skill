# Внешние скиллы/инструменты — что взято и почему (2026-10-14)

## rehan-remade/universal-modder (MIT) — https://github.com/rehan-remade/universal-modder
Набор скиллов «моддить любую игру» (+ CLI `um`, fal MCP, база field notes). Не установлен целиком, потому что:
- маршрут для UE там — UE4SS / pak-override `~mods/*_P.pak` / repak / retoc / FModel. Для QZ это неверный путь: есть официальный
  ModioUGC-пайплайн, игра валидирует моды по uplugin/GameVersion, а pak-override вне него ломается на обновлениях;
- большинство скиллов про другие движки (Terraria, AoE2, Minecraft); генерация ассетов требует платного FAL_KEY;
- `um` требует uv/pipx (не установлены) и ffmpeg (нет в PATH).
Взято в `workflow.md`: журнал MODLOG, intake → recon → vertical slice → verify (игра — оракул) → package → field note,
circuit breaker (3 одинаковых провала → стоп), lint перед публикацией, правила публикации (публикует пользователь, AI-disclosure).
Пригодится позже: скилл `game-automation` (`um win shot/drive` — скриншоты окна игры через gfxcapture, клики) для самостоятельной
проверки модов в игре. Ставить только с согласия пользователя: `uv tool install git+https://github.com/rehan-remade/universal-modder`.
Шаблон field note: `knowledge/TEMPLATE.md` в их репо.

## EpicGames/unreal-engine-skills-for-claude-code-plugin (MIT)
Управление редактором через MCP (сотни инструментов). **Не подходит**: требует плагины движка `ModelContextProtocol` и `AllToolsets`
(+ запуск `ModelContextProtocol.StartServer` в редакторе) — в движке кита их нет (`Engine/Engine/Plugins` проверен).
Наш эквивалент — Python-задания `qz_mod_job.py` через `-ExecutePythonScript`.

## maystudios/claude-skills (MIT) — https://github.com/maystudios/claude-skills
- `unreal-gas` — справочник по Gameplay Ability System (C++). Полезен концептуально: симптомы с логикой в модах — это
  Blueprint GameplayAbility (`BP_GA_*`), инструменты/способности — `SGameplayAbility`. Читать по ссылке при задаче «симптом с логикой».
- `unreal-blueprint-codegen` — генерация графов BP из C++ editor-модуля; у нас нет компилятора/исходников движка → неприменимо.
  Из Python доступно только создание BP-наследника, переменных, функций-заглушек (`BlueprintEditorLibrary`), но не нод графа.
- `unreal-best-practices`, `unreal-pcg-python` — общие, не нужны.
