# VIVUM — контракт интеграции с ProjectManagement

## 1. Work Package
Минимальные поля:
- `workPackageCode` — стабильный код вида `EL-RI-001`;
- object / zone / discipline;
- workType;
- quantity + unit + secondary quantity;
- installer / crew + `crewSize`;
- supplyPerson / engineerPerson;
- readiness checklist + readinessAcceptedAt;
- supplyPrepMin / engineerPrepMin / installerPrepMin;
- technologicalProductiveTime;
- productivePersonTime;
- lossTime / lossPersonTime / lossReasons;
- operationTimes;
- observationGroupTimes;
- status.

## 2. Measurement Record
Каждый замер получает уникальный `measurementId`. Повторный импорт того же ID не должен создавать дубль.

Замер хранит `appVersion` и `catalogSchemaVersion`, чтобы результаты оставались воспроизводимыми после изменения технологии.

JSON-контракт: `schemas/measurement_record.schema.json`.

## 3. Статусы
`DRAFT → SUPPLY_READY → ENGINEERING_READY → INSTALLER_ACCEPTED → IN_PROGRESS → COMPLETED`.

Если обязательный readiness-пункт не закрыт, переход в `IN_PROGRESS` запрещён.

## 4. Источник истины
После интеграции ProjectManagement хранит рабочий пакет, статусы, замеры и ссылки на нормативные карточки. PWA остаётся полевым интерфейсом ввода и не создаёт параллельный проектный реестр.

## 5. Разделение времени
Подготовительные минуты, технологическое время, человеко-время и простои передаются раздельными полями. Смешивать их в одно «время работы» запрещено.

## 6. Каталог технологии
Стабильный справочник: `data/electrical_catalog.v1.json`.

Массовый хронометраж работает по `observation_groups`; детальная нормативная база — по `operations`. Один крупный этап может включать несколько детальных операций.

## 7. Нормативная карточка
После накопления наблюдений PM/сметный модуль связывает `measurementId` с `NormCard`. Контракт: `schemas/norm_card.schema.json`.
