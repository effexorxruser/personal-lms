# Curriculum Architecture

## Назначение документа

Документ фиксирует целевую архитектуру основного 6-месячного курса `personal-lms` как source of truth перед этапами platform hardening и реального curriculum onboarding.

## Что зафиксировано

- Курс строится как **Python backend + AI practical builder path for early monetization**.
- Формат курса: **source-backed**, а не полный авторский учебник с нуля.
- Учебная модель: **execution-driven** (lesson → task → submission → review → done) с обязательными stuck flow и recap.
- Крупные блоки курса должны завершаться **observable artifact**, а не только отметкой "пройдено".

## 6-месячная цель курса

За 6 месяцев learner должен пройти путь от базовой Python/CLI грамотности до сборки небольших backend + AI utility решений, которые можно:

- использовать в собственной работе;
- публиковать в GitHub как проверяемые артефакты;
- упаковывать в портфолио;
- в отдельных случаях предлагать как небольшие платные услуги или micro-MVP.

## Целевой профиль learner

Документ ориентирован на learner, который:

- стартует с ограниченным практическим опытом в backend;
- готов учиться регулярно и выполнять задания;
- хочет не только "изучить Python", но и дойти до полезных рабочих выходов;
- рассматривает ранние прикладные и/или монетизируемые результаты как допустимую цель.

## Формула курса

**Python backend + AI practical builder path for early monetization**.

Это означает:

- backend и automation навыки развиваются совместно;
- AI добавляется как прикладной слой поверх уже работающих сценариев;
- учебный прогресс оценивается по выполненным артефактам.

## High-priority skill areas

Приоритетные зоны навыков:

- Python core и рабочая грамотность в терминале;
- Git/GitHub workflow;
- automation и интеграции с внешними API/сервисами;
- HTTP, data handling, SQLite, базовый backend на FastAPI;
- testing, debugging, logging, базовая надежность;
- AI API integration для extraction/triage/utility задач;
- сборка небольших user-facing решений.

## Главный pipeline курса

Пайплайн фиксируется в следующем порядке:

1. foundation;
2. automation;
3. integrations/data;
4. backend;
5. reliability;
6. AI layer;
7. product assembly.

Переход на следующий этап не должен происходить без проверяемого результата на предыдущем.

## Главная прикладная ветка текущего этапа

Текущая приоритетная прикладная ветка:

- Telegram;
- automation;
- AI utility tools.

Это не единственная возможная ветка в будущем, но именно она является главной практической осью текущего этапа и должна отражаться в checkpoint-логике.

## Принцип observable artifacts

Каждый крупный блок должен приводить к наблюдаемому результату:

- рабочий скрипт/утилита;
- интеграционный мини-сервис;
- backend endpoint + storage сценарий;
- AI utility-функция с проверяемым входом/выходом.

Блок без артефакта считается незавершенным с точки зрения продуктовой цели.

## Notion of checkpoint project

Checkpoint project — обязательный контрольный артефакт на границе крупных этапов.

Требования к checkpoint project:

- объединяет несколько навыков из пройденного pipeline;
- имеет проверяемый definition of done;
- пригоден для портфолио;
- при достаточном качестве может быть упакован как sellable micro-result.

## Что не входит / что отложено

- Полный каталог всех уроков и задач на весь период.
- Точная оценка длительности каждого lesson/task.
- Расширение на multi-track/multi-course архитектуру.

## Влияние на следующие этапы

- Platform hardening должен готовить runtime к этой архитектуре, а не наоборот.
- Authoring model должен обеспечивать упаковку lesson/task/checkpoint под данный pipeline.
- Curriculum onboarding должен проверяться по критерию artifact outcomes, а не по объему текста.
