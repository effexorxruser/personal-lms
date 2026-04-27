# TERMINAL READINESS

## Назначение

Документ фиксирует контракт безопасности текущего lesson-scoped Terminal MVP для curriculum pipeline.

## Scope (что поддерживается сейчас)

- trusted single-user режим (локальный обучающий контур);
- запуск только внутри lesson/task контекста;
- ограниченный набор команд через whitelist;
- short-lived execution с лимитами по времени и выводу.

## Trusted / single-user допущение

Текущий terminal рассчитан на:
- одного пользователя;
- локальную учебную среду;
- отсутствие multi-tenant/isolation требований production-уровня.

## Allowed command grammar

Команды должны соответствовать grammar уровня MVP:
- только разрешенные базовые команды (`help`, `pwd`, `tree`, `python`, `pytest`, `show`);
- аргументы ограничены учебным сценарным контекстом;
- запрещены shell chaining / redirection / произвольные бинарники вне whitelist.

## Sandbox limits

- доступ ограничен рабочей областью учебной задачи;
- path traversal и выход за lesson scope должны блокироваться;
- manual input может быть отключен на уровне task.

## Timeout и output limits

- каждая команда выполняется с timeout;
- вывод ограничен по размеру;
- длинные или зависшие процессы должны прерываться.

## Что безопасно сейчас

- демонстрация базовых Python/Git/pytest команд по preset-ам;
- проверка простых шагов learner-а в рамках lesson;
- сохранение истории запусков для учебного прогресса.

## Что требует future containerized runner

- недоверенные multi-user сценарии;
- расширенный command set (package managers, system utilities);
- сильная изоляция процессов/FS/сети;
- выполнение произвольного пользовательского кода production-grade уровня.

## Readiness вывод

Terminal MVP подходит для block-by-block curriculum generation в trusted single-user контуре.
Для масштабирования на более рискованные сценарии обязателен отдельный containerized runner этап.
