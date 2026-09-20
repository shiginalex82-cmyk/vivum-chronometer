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
## 8. Package Benchmark
Массовые замеры агрегируются в отдельную сущность benchmark и не обновляют `NormCard` автоматически.

Минимальные поля:
- workPackageCode;
- sampleSize;
- medianPersonMinPerPrimary;
- P25 / P75 / min / max;
- medianLossRatio;
- sourceMeasurementIds;
- status;
- normPublicationAllowed.

По умолчанию `normPublicationAllowed=false` до инженерной проверки.

## 9. Resource Requirement
PM должен хранить семантику `REQUIRED / ONE_OF / ONE_OR_MORE_OF / CONDITIONAL`, а не только плоский список материалов.

Контракт: `data/package_resource_requirements.v2.json` + `schemas/resource_requirements.schema.json`.
## 10. Labor Estimate
Расчёт трудовой себестоимости хранит ссылки на версии каталога, нормативов и ставок ролей.
Неполный расчёт имеет `complete=false` и не может быть использован как готовая смета.

## 11. Production Cost Estimate
Отдельная сущность поверх Labor Estimate:
- labor cost;
- materials;
- equipment/tool allocation;
- logistics;
- other direct costs;
- allocated overhead;
- knownPartialCost;
- fullProductionCost;
- complete/missing.

Если `complete=false`, `fullProductionCost=null`.

## 12. Commercial Price Estimate
Отдельная сущность поверх полного Production Cost:
- risk reserve;
- profit method/value;
- contract adjustments;
- tax;
- clientPrice;
- commercial policy version.

Если Production Cost неполон, Commercial Price не рассчитывается. PM не должен позволять коммерческому слою изменять NormCard, Measurement или Production Cost задним числом.

## 13. Cost integrity guards
Для материальной строки PM хранит `unit` и `costResponsibility = VIVUM / CUSTOMER / EXTERNAL`.
PM не должен включать стоимость ресурсов `CUSTOMER/EXTERNAL` в себестоимость VIVUM без отдельного изменения ответственности.

Перед публикацией Production/Commercial Estimate проверяются:
- совпадение валют всех связанных версий;
- совпадение единицы количества с единицей тарифа;
- полнота обязательных ставок/политик;
- отсутствие использования `knownPartialCost` как готовой сметы.

## 14. Resource Quantity Build
Между `ResourceRequirement` и `ProductionCostEstimate` вводится отдельный расчёт количества ресурсов.

Минимальные поля:
- resourceBuildId;
- workPackageCode;
- drivers;
- выбранные альтернативы ресурсов;
- версия Consumption Policy;
- material resourceId / quantity / unit / costResponsibility;
- source количества;
- complete / missing.

PM не должен автоматически считать расход только потому, что ресурс присутствует в readiness-чек-листе. Неутверждённый consumption rule блокирует полный ресурсный расчёт.

Production Cost Request может собираться автоматически только из `Resource Quantity Build` с `complete=true`; его `sourceResourceBuildIds` сохраняются для аудита.

## 15. Future Electrical Connection Model
Электрическое проектирование сейчас отложено. PM не должен требовать ручного ввода количества/типоразмера ГМЛ как постоянный источник истины.

Будущий источник: `Revit/SHIGIN electrical topology`.

Минимальная цепочка:
`junction box → cable/core refs → connection groups → selected GML → derived TTK`.

Для `EL-RI-006`:
- `EL-RI-006-M01` имеет `FUTURE_REVIT_CONNECTION_MODEL`;
- `EL-RI-006-M02` имеет `DERIVED_FROM_REQUIREMENT` и зависит от `EL-RI-006-M01`;
- до появления проектных данных Production Cost остаётся неполным по этим ресурсам.

Контракт: `schemas/future_electrical_connection_model.schema.json`.
