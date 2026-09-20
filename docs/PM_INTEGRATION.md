# VIVUM — контракт интеграции с ProjectManagement

## Сущность: Work Package
Минимальные поля:
- object / zone / discipline;
- workType;
- quantity + unit;
- installer / crew;
- supplyPerson;
- engineerPerson;
- readiness checklist;
- readinessAcceptedAt;
- supplyPrepMin;
- engineerPrepMin;
- installerPrepMin;
- technologicalProductiveTime;
- lossTime;
- lossReasons;
- operationTimes;
- status.

## Статусы
DRAFT → SUPPLY_READY → ENGINEERING_READY → INSTALLER_ACCEPTED → IN_PROGRESS → COMPLETED.

Если обязательный пункт готовности не закрыт, переход в IN_PROGRESS запрещён.

## Правило источника истины
ProjectManagement после интеграции хранит рабочий пакет и его статусы. Хронометраж является полевым интерфейсом ввода и не должен создавать параллельную карточку проекта.

## Правило расчёта
Подготовительные минуты и технологический хронометраж передаются раздельными полями. Простои также передаются отдельно. Смешивать эти категории в одно «время работы» запрещено.