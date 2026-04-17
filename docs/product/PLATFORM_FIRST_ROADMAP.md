# Platform First Roadmap

## Назначение документа

Документ фиксирует обязательный порядок этапов развития `personal-lms` перед массовым curriculum onboarding.

## Что зафиксировано

Массовая загрузка реального курса не начинается до закрытия platform hardening и authoring readiness.

## Порядок этапов

1. documentation freeze;
2. platform hardening;
3. authoring readiness;
4. first real curriculum pass;
5. curriculum hardening;
6. later expansion.

Нарушение этого порядка повышает риск закрепления слабой runtime/UX базы и ухудшает качество обучения.

## Состав platform hardening

Этап platform hardening обязан включать минимум:

- stuck flow;
- weekly recap;
- minimal terminal-like execution surface;
- lesson-scoped AI helper;
- UX hardening длинных страниц;
- authoring-ready model для блоков/уроков/задач/checkpoints.

## Почему platform before scale

Причина фиксации:

- без устойчивого runtime learner теряет continuity;
- без стабильного UX длинные учебные страницы ухудшают execution;
- без authoring-ready структуры реальный curriculum будет загружаться хаотично;
- исправление базовых платформенных разрывов после массовой загрузки обходится дороже.

## Что входит в authoring readiness

- согласованная структура block/module/lesson/task/checkpoint;
- правила обязательных полей и definition of done;
- предсказуемый ingestion-процесс content in files;
- корректная привязка runtime state в БД.

## Что не входит / что отложено

- Массовое добавление новых тематических веток до стабилизации основы.
- Переход к multi-course/multi-tenant модели.
- Расширенная продуктовая экспансия до первого устойчивого curriculum pass.

## Влияние на следующие этапы

- Любой implementation pass после freeze обязан ссылаться на данный порядок.
- First real curriculum pass выполняется ограниченно и как проверка модели.
- Расширение масштаба допускается только после curriculum hardening.
