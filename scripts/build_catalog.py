import json, csv
from pathlib import Path
ROOT=Path(r'C:\Temp\vivum-chronometer')
DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
DOCS=ROOT/'docs'
SCHEMA_VERSION='1.0'

def op(code,pkg,seq,name,driver,scope,tools=None,materials=None,pre=None,qa=None,crew='1',notes=''):
    return {'code':code,'package_code':pkg,'sequence':seq,'name':name,'time_class':'T_tech','quantity_driver':driver,'measurement_scope':scope,'crew_rule':crew,'tool_ids':tools or [],'material_ids':materials or [],'preconditions':pre or [],'qa':qa or [],'notes':notes}
tools=[
 {'id':'TL-LASER','name':'Лазерный уровень / построитель плоскостей','category':'measurement'},
 {'id':'TL-TAPE','name':'Рулетка','category':'measurement'},
 {'id':'TL-MARK','name':'Разметочный инструмент','category':'hand_tool'},
 {'id':'TL-DRILL','name':'Перфоратор / дрель','category':'power_tool'},
 {'id':'TL-CROWN68','name':'Коронка Ø68 для твёрдых стен','category':'consumable_tool'},
 {'id':'TL-HOLLOW68','name':'Инструмент/коронка для отверстий Ø68 в полых стенах','category':'power_tool'},
 {'id':'TL-VAC','name':'Промышленный пылесос','category':'equipment'},
 {'id':'TL-MIX','name':'Ёмкость и инструмент для замешивания состава','category':'hand_tool'},
 {'id':'TL-GUN','name':'Газовый монтажный пистолет','category':'power_tool'},
 {'id':'TL-UNWIND','name':'Устройство/место для размотки бухты кабеля','category':'equipment'},
 {'id':'TL-LABEL','name':'Маркиратор / ручной комплект маркировки','category':'hand_tool'},
 {'id':'TL-STRIP','name':'Инструмент для снятия оболочки и изоляции','category':'hand_tool'},
 {'id':'TL-CRIMP','name':'Ручной или гидравлический пресс с матрицами','category':'power_tool'},
 {'id':'TL-HEAT','name':'Строительный фен либо газовая горелка','category':'power_tool'},
 {'id':'TL-CHASE','name':'Штроборез / резчик','category':'power_tool'},
 {'id':'TL-CHISEL','name':'Перфоратор/зубило для выборки штробы','category':'power_tool'},
 {'id':'TL-HAND','name':'Комплект ручного электромонтажного инструмента','category':'hand_tool'},
 {'id':'TL-ACCESS','name':'Стремянка / подмости по высоте работ','category':'access_equipment'}
]
materials=[
 {'id':'MT-2689-05','name':'Коробка установочная С-3 блочная для твёрдых стен Ø68×60 со стыковочными узлами','source':'Счёт №2689','position':'5','type':'product'},
 {'id':'MT-2689-27','name':'Коробка для полых стен / ГКЛ / ГВЛ Ø68×45 Schneider Electric IMT35150','source':'Счёт №2689','position':'27','type':'product'},
 {'id':'MT-2689-01','name':'ВВГнг-LS 3×2,5(ож)-0,66 ГОСТ','source':'Счёт №2689','position':'1','type':'cable'},
 {'id':'MT-2689-02','name':'ВВГ-LS 3×1,5','source':'Счёт №2689','position':'2','type':'cable'},
 {'id':'MT-2689-03','name':'КГВВнг 5×0,75','source':'Счёт №2689','position':'3','type':'cable'},
 {'id':'MT-2689-04','name':'КГВВнг(А)-LS 7×0,75','source':'Счёт №2689','position':'4','type':'cable'},
 {'id':'MT-2689-11','name':'ВВГнг-LS 4×1,5(ож)-0,66 ГОСТ','source':'Счёт №2689','position':'11','type':'cable'},
 {'id':'MT-2689-36','name':'КГВВнг 3×1,5','source':'Счёт №2689','position':'36','type':'cable'},
 {'id':'MT-2689-40','name':'КГВВнг 3×2,5','source':'Счёт №2689','position':'40','type':'cable'},
 {'id':'MT-2689-06','name':'Площадка под стяжку для прямого монтажа, чёрная','source':'Счёт №2689','position':'6','type':'fastener'},
 {'id':'MT-2689-07','name':'Стяжка нейлоновая КСС 3×150 ч','source':'Счёт №2689','position':'7','type':'fastener'},
 {'id':'MT-2689-12','name':'Гвоздь усиленный CN EG bullet point 3,05×17 мм','source':'Счёт №2689','position':'12','type':'fastener'},
 {'id':'MT-2689-30','name':'Газовый баллон для монтажных пистолетов 165 мм','source':'Счёт №2689','position':'30','type':'consumable'},
 {'id':'MT-ALABASTER','name':'Алебастр / быстротвердеющий гипсовый состав','source':'generic','position':None,'type':'compound'},
 {'id':'MT-GYPSUM','name':'Гипсовая штукатурка / медленный монтажный состав','source':'generic','position':None,'type':'compound'},
 {'id':'MT-JBOX','name':'Коммутационная коробка требуемого типа и размера','source':'project','position':None,'type':'product'},
 {'id':'MT-MARK','name':'Материал для маркировки кабелей','source':'generic','position':None,'type':'consumable'},
 {'id':'MT-GML','name':'Гильза медная ГМЛ требуемого сечения','source':'generic','position':None,'type':'connector'},
 {'id':'MT-TTK','name':'Трубка термоусаживаемая клеевая ТТК','source':'generic','position':None,'type':'insulation'},
 {'id':'MT-WAGO','name':'Согласованная клемма типа WAGO для сети освещения','source':'generic','position':None,'type':'connector'}
]
CABLE_IDS=['MT-2689-01','MT-2689-02','MT-2689-03','MT-2689-04','MT-2689-11','MT-2689-36','MT-2689-40']
packages=[
 {'code':'EL-RI-001','key':'solid','name':'Подрозетники — твёрдые оштукатуренные стены','primary_unit':'подрозетник','secondary_unit':'блок','norm_basis':'primary_unit','start_boundary':'Зона принята; привязки известны; материалы и инструмент у рабочего места.','finish_boundary':'Коробки установлены, выровнены, закреплены, проконтролированы; локальная уборка завершена.','exclusions':['штроба под кабель','прокладка кабеля','завод кабеля после затвердевания','чистовой механизм']},
 {'code':'EL-RI-002','key':'hollow','name':'Подрозетники — полые стены / каркасная система','primary_unit':'подрозетник','secondary_unit':'блок','norm_basis':'primary_unit','start_boundary':'Тип конструкции и привязки подтверждены.','finish_boundary':'Коробки штатно закреплены и проконтролированы.','exclusions':['прокладка кабеля','подключение механизма']},
 {'code':'EL-RI-003','key':'cable1','name':'Кабель по потолку — одиночная линия','primary_unit':'м линии','secondary_unit':'линия','norm_basis':'primary_unit','start_boundary':'Линия идентифицирована; бухта подготовлена; маршрут известен.','finish_boundary':'Линия проложена, закреплена, промаркирована и проверена.','exclusions':['изготовление проходок','коммутация концов','устройство кабельного лотка']},
 {'code':'EL-RI-004','key':'cableBundle','name':'Кабель по потолку — группа линий / пучок','primary_unit':'м общего маршрута','secondary_unit':'линия в пучке','norm_basis':'primary_unit+secondary_parameter','start_boundary':'Состав группы и маркировка всех линий определены.','finish_boundary':'Группа проложена, закреплена; линии идентифицируемы.','exclusions':['коммутация','ответвления вне общего маршрута']},
 {'code':'EL-RI-005','key':'boxInstall','name':'Коммутационная коробка — монтаж + завод и маркировка кабелей','primary_unit':'коробка','secondary_unit':'заведённый кабель','norm_basis':'primary_unit+secondary_parameter','start_boundary':'Место коробки и перечень кабелей заданы.','finish_boundary':'Коробка закреплена; кабели заведены с запасом и промаркированы.','exclusions':['соединение жил']},
 {'code':'EL-RI-006','key':'boxSocket','name':'Коммутация коробки розеточной сети','primary_unit':'коробка','secondary_unit':'гильза/соединение','norm_basis':'primary_unit+secondary_parameter','start_boundary':'Маркировка сверена со схемой.','finish_boundary':'Соединения опрессованы, изолированы ТТК, уложены; коробка закрыта и проверена.','exclusions':['монтаж самой коробки','прокладка кабелей']},
 {'code':'EL-RI-007','key':'boxLight','name':'Коммутация коробки освещения','primary_unit':'коробка','secondary_unit':'соединение','norm_basis':'primary_unit+secondary_parameter','start_boundary':'Маркировка и схема сверены.','finish_boundary':'Соединения выполнены клеммами, уложены; коробка закрыта и проверена.','exclusions':['монтаж самой коробки','прокладка кабелей']},
 {'code':'EL-RI-008','key':'chase','name':'Штробление — вертикальный опуск к подрозетнику','primary_unit':'м штробы','secondary_unit':'опуск','norm_basis':'primary_unit+fixed_per_drop','start_boundary':'Маршрут проверен и размечен; пылеудаление готово.','finish_boundary':'Штроба прорезана, выбрана, очищена и проверена.','exclusions':['отверстие под подрозетник','заделка штробы']},
 {'code':'EL-RI-009','key':'cableToBox','name':'Заведение кабеля в подрозетник после фиксации','primary_unit':'подрозетник','secondary_unit':'кабель','norm_basis':'primary_unit+secondary_parameter','start_boundary':'Монтажный состав набрал достаточную прочность.','finish_boundary':'Подрозетник очищен; кабель идентифицирован, заведён; запас и маркировка сформированы.','exclusions':['магистральная прокладка','подключение чистового механизма']}
]
ops=[]
# EL-RI-001 — solid wall boxes
ops += [
 op('EL-RI-001-01','EL-RI-001',1,'Разметить координаты, оси и высоту блока','block_qty','PER_BLOCK',['TL-LASER','TL-TAPE','TL-MARK']),
 op('EL-RI-001-02','EL-RI-001',2,'Проверить отсутствие конфликта в зоне сверления','block_qty','PER_BLOCK',['TL-LASER'],pre=['актуальная привязка']),
 op('EL-RI-001-03','EL-RI-001',3,'Прокоронить отверстие Ø68','primary_qty','PER_UNIT',['TL-DRILL','TL-CROWN68','TL-VAC']),
 op('EL-RI-001-04','EL-RI-001',4,'Удалить сердцевину и подготовить посадочное место','primary_qty','PER_UNIT',['TL-DRILL','TL-VAC']),
 op('EL-RI-001-05','EL-RI-001',5,'Очистить отверстие от пыли и крошки','primary_qty','PER_UNIT',['TL-VAC']),
 op('EL-RI-001-06','EL-RI-001',6,'Собрать/подготовить блок подрозетников','block_qty','PER_BLOCK',['TL-HAND'],['MT-2689-05']),
 op('EL-RI-001-07','EL-RI-001',7,'Замешать монтажный состав','package_batch','BATCH',['TL-MIX'],['MT-ALABASTER','MT-GYPSUM']),
 op('EL-RI-001-08','EL-RI-001',8,'Установить подрозетник/блок на состав','primary_qty','PER_UNIT',['TL-MIX'],['MT-2689-05','MT-ALABASTER','MT-GYPSUM']),
 op('EL-RI-001-09','EL-RI-001',9,'Выставить горизонталь, глубину и межосевые расстояния','block_qty','PER_BLOCK',['TL-LASER','TL-HAND']),
 op('EL-RI-001-10','EL-RI-001',10,'Удалить излишки состава и очистить коробки','block_qty','PER_BLOCK',['TL-MIX']),
 op('EL-RI-001-11','EL-RI-001',11,'Контроль геометрии и фиксации','block_qty','PER_BLOCK',['TL-LASER'],qa=['координата','высота','горизонталь','глубина','жёсткость фиксации']),
 op('EL-RI-001-12','EL-RI-001',12,'Локальная уборка зоны','package','FIXED_PACKAGE',['TL-VAC'])
]
# EL-RI-002 — hollow wall boxes
ops += [
 op('EL-RI-002-01','EL-RI-002',1,'Разметить координаты, оси и высоту блока','block_qty','PER_BLOCK',['TL-LASER','TL-TAPE','TL-MARK']),
 op('EL-RI-002-02','EL-RI-002',2,'Проверить каркас и свободное пространство за листом','block_qty','PER_BLOCK',['TL-HAND'],pre=['конструкция стены доступна для проверки']),
 op('EL-RI-002-03','EL-RI-002',3,'Вырезать отверстие Ø68','primary_qty','PER_UNIT',['TL-HOLLOW68','TL-VAC']),
 op('EL-RI-002-04','EL-RI-002',4,'Очистить и проверить кромку отверстия','primary_qty','PER_UNIT',['TL-HAND','TL-VAC']),
 op('EL-RI-002-05','EL-RI-002',5,'Подготовить коробку и вводы','primary_qty','PER_UNIT',['TL-HAND'],['MT-2689-27']),
 op('EL-RI-002-06','EL-RI-002',6,'Установить коробку в полую стену','primary_qty','PER_UNIT',['TL-HAND'],['MT-2689-27']),
 op('EL-RI-002-07','EL-RI-002',7,'Затянуть штатные лапки/фиксаторы','primary_qty','PER_UNIT',['TL-HAND']),
 op('EL-RI-002-08','EL-RI-002',8,'Выставить положение блока','block_qty','PER_BLOCK',['TL-LASER','TL-HAND']),
 op('EL-RI-002-09','EL-RI-002',9,'Контроль геометрии и жёсткости','block_qty','PER_BLOCK',['TL-LASER'],qa=['высота','горизонталь','глубина','жёсткость']),
 op('EL-RI-002-10','EL-RI-002',10,'Локальная уборка зоны','package','FIXED_PACKAGE',['TL-VAC'])
]
# EL-RI-003 — single cable line
ops += [
 op('EL-RI-003-01','EL-RI-003',1,'Сверить начало, конец, маркировку и маршрут линии','line_qty','PER_LINE',['TL-TAPE'],pre=['актуальное задание']),
 op('EL-RI-003-02','EL-RI-003',2,'Разметить точки крепления по маршруту','route_length','PER_METER',['TL-TAPE','TL-MARK','TL-LASER']),
 op('EL-RI-003-03','EL-RI-003',3,'Подготовить монтажный пистолет, площадки и расходники','package','FIXED_PACKAGE',['TL-GUN'],['MT-2689-06','MT-2689-12','MT-2689-30']),
 op('EL-RI-003-04','EL-RI-003',4,'Пристрелить площадки крепления','fastener_qty','PER_FASTENER',['TL-GUN'],['MT-2689-06','MT-2689-12','MT-2689-30']),
 op('EL-RI-003-05','EL-RI-003',5,'Установить бухту/катушку на размотку','line_qty','PER_LINE',['TL-UNWIND'],CABLE_IDS),
 op('EL-RI-003-06','EL-RI-003',6,'Размотать и проложить кабель по маршруту','route_length','PER_METER',['TL-UNWIND','TL-ACCESS'],CABLE_IDS,crew='1; допускается 2 по массе/длине/условиям маршрута'),
 op('EL-RI-003-07','EL-RI-003',7,'Закрепить кабель стяжками на площадках','fastener_qty','PER_FASTENER',['TL-HAND','TL-ACCESS'],['MT-2689-07']),
 op('EL-RI-003-08','EL-RI-003',8,'Сформировать технологический запас на концах','line_end_qty','PER_LINE_END',['TL-HAND']),
 op('EL-RI-003-09','EL-RI-003',9,'Промаркировать оба конца линии','line_end_qty','PER_LINE_END',['TL-LABEL'],['MT-MARK']),
 op('EL-RI-003-10','EL-RI-003',10,'Контроль маршрута, крепления и маркировки','line_qty','PER_LINE',['TL-HAND'],qa=['маршрут','шаг крепления','отсутствие повреждений','маркировка']),
 op('EL-RI-003-11','EL-RI-003',11,'Локальная уборка и перенос остатка бухты','package','FIXED_PACKAGE',['TL-HAND'])
]
# EL-RI-004 — cable bundle
ops += [
 op('EL-RI-004-01','EL-RI-004',1,'Сверить состав группы, маркировку и общий маршрут','package','FIXED_PACKAGE',['TL-TAPE'],pre=['состав группы задан инженером']),
 op('EL-RI-004-02','EL-RI-004',2,'Разметить точки крепления общего маршрута','route_length','PER_METER',['TL-TAPE','TL-MARK','TL-LASER']),
 op('EL-RI-004-03','EL-RI-004',3,'Подготовить монтажный пистолет, площадки и расходники','package','FIXED_PACKAGE',['TL-GUN'],['MT-2689-06','MT-2689-12','MT-2689-30']),
 op('EL-RI-004-04','EL-RI-004',4,'Пристрелить площадки крепления','fastener_qty','PER_FASTENER',['TL-GUN'],['MT-2689-06','MT-2689-12','MT-2689-30']),
 op('EL-RI-004-05','EL-RI-004',5,'Подготовить и идентифицировать бухты линий группы','secondary_qty','PER_CABLE',['TL-UNWIND','TL-LABEL'],CABLE_IDS+['MT-MARK']),
 op('EL-RI-004-06','EL-RI-004',6,'Сформировать управляемый пучок для прокладки','secondary_qty','PER_CABLE',['TL-HAND'],CABLE_IDS),
 op('EL-RI-004-07','EL-RI-004',7,'Проложить группу кабелей по общему маршруту','route_length','PER_METER',['TL-UNWIND','TL-ACCESS'],CABLE_IDS,crew='1–2 по числу/массе кабелей и условиям маршрута'),
 op('EL-RI-004-08','EL-RI-004',8,'Закрепить пучок стяжками на площадках','fastener_qty','PER_FASTENER',['TL-HAND','TL-ACCESS'],['MT-2689-07']),
 op('EL-RI-004-09','EL-RI-004',9,'Разделить/сформировать технологические запасы линий на концах','secondary_qty','PER_CABLE',['TL-HAND']),
 op('EL-RI-004-10','EL-RI-004',10,'Промаркировать линии группы на концах','secondary_qty','PER_CABLE',['TL-LABEL'],['MT-MARK']),
 op('EL-RI-004-11','EL-RI-004',11,'Контроль состава, маршрута, крепления и идентификации','package','FIXED_PACKAGE',['TL-HAND'],qa=['состав группы','маршрут','шаг крепления','маркировка','отсутствие повреждений']),
 op('EL-RI-004-12','EL-RI-004',12,'Локальная уборка и перенос остатков материалов','package','FIXED_PACKAGE',['TL-HAND'])
]
# EL-RI-005 — junction box install + cable entry/marking
ops += [
 op('EL-RI-005-01','EL-RI-005',1,'Сверить место, обозначение коробки и перечень кабелей','primary_qty','PER_BOX',['TL-TAPE'],pre=['актуальная схема/задание']),
 op('EL-RI-005-02','EL-RI-005',2,'Разметить положение коробки и крепления','primary_qty','PER_BOX',['TL-LASER','TL-TAPE','TL-MARK']),
 op('EL-RI-005-03','EL-RI-005',3,'Подготовить основание и крепёж','primary_qty','PER_BOX',['TL-DRILL','TL-HAND']),
 op('EL-RI-005-04','EL-RI-005',4,'Закрепить и выровнять коробку','primary_qty','PER_BOX',['TL-DRILL','TL-HAND','TL-LASER'],['MT-JBOX']),
 op('EL-RI-005-05','EL-RI-005',5,'Подготовить кабельные вводы коробки','secondary_qty','PER_CABLE',['TL-HAND'],['MT-JBOX']),
 op('EL-RI-005-06','EL-RI-005',6,'Идентифицировать кабель перед вводом','secondary_qty','PER_CABLE',['TL-LABEL'],['MT-MARK']),
 op('EL-RI-005-07','EL-RI-005',7,'Завести кабель в коробку','secondary_qty','PER_CABLE',['TL-HAND']),
 op('EL-RI-005-08','EL-RI-005',8,'Сформировать запас кабеля в коробке','secondary_qty','PER_CABLE',['TL-HAND']),
 op('EL-RI-005-09','EL-RI-005',9,'Промаркировать заведённый кабель','secondary_qty','PER_CABLE',['TL-LABEL'],['MT-MARK']),
 op('EL-RI-005-10','EL-RI-005',10,'Контроль крепления, вводов, запаса и маркировки','primary_qty','PER_BOX',['TL-HAND'],qa=['жёсткость коробки','кабель не повреждён','запас','маркировка']),
 op('EL-RI-005-11','EL-RI-005',11,'Закрыть/защитить коробку до коммутации','primary_qty','PER_BOX',['TL-HAND'])
]
# EL-RI-006 — socket junction box, GML + TTK
ops += [
 op('EL-RI-006-01','EL-RI-006',1,'Сверить маркировку кабелей со схемой','primary_qty','PER_BOX',['TL-HAND'],pre=['схема коммутации']),
 op('EL-RI-006-02','EL-RI-006',2,'Разложить проводники по группам соединений','primary_qty','PER_BOX',['TL-HAND']),
 op('EL-RI-006-03','EL-RI-006',3,'Снять оболочку и подготовить жилы','secondary_qty','PER_CONNECTION',['TL-STRIP']),
 op('EL-RI-006-04','EL-RI-006',4,'Подобрать ГМЛ по сечению и составу жил','secondary_qty','PER_CONNECTION',['TL-HAND'],['MT-GML']),
 op('EL-RI-006-05','EL-RI-006',5,'Опрессовать соединение','secondary_qty','PER_CONNECTION',['TL-CRIMP'],['MT-GML']),
 op('EL-RI-006-06','EL-RI-006',6,'Установить клеевую ТТК на соединение','secondary_qty','PER_CONNECTION',['TL-HAND'],['MT-TTK']),
 op('EL-RI-006-07','EL-RI-006',7,'Усадить ТТК феном/горелкой','secondary_qty','PER_CONNECTION',['TL-HEAT'],['MT-TTK']),
 op('EL-RI-006-08','EL-RI-006',8,'Проверить качество опрессовки и изоляции','secondary_qty','PER_CONNECTION',['TL-HAND'],qa=['гильза деформирована корректно','нет оголённых участков','ТТК проклеена']),
 op('EL-RI-006-09','EL-RI-006',9,'Уложить соединения и запасы в коробке','primary_qty','PER_BOX',['TL-HAND']),
 op('EL-RI-006-10','EL-RI-006',10,'Закрыть коробку','primary_qty','PER_BOX',['TL-HAND']),
 op('EL-RI-006-11','EL-RI-006',11,'Финальный визуальный контроль и фиксация результата','primary_qty','PER_BOX',['TL-HAND'],qa=['коробка закрыта','маркировка читаема','нет пережатия проводников'])
]
# EL-RI-007 — lighting junction box, WAGO
ops += [
 op('EL-RI-007-01','EL-RI-007',1,'Сверить маркировку кабелей со схемой','primary_qty','PER_BOX',['TL-HAND'],pre=['схема коммутации']),
 op('EL-RI-007-02','EL-RI-007',2,'Разложить проводники по группам соединений','primary_qty','PER_BOX',['TL-HAND']),
 op('EL-RI-007-03','EL-RI-007',3,'Снять оболочку и подготовить жилы','secondary_qty','PER_CONNECTION',['TL-STRIP']),
 op('EL-RI-007-04','EL-RI-007',4,'Подобрать согласованную клемму WAGO','secondary_qty','PER_CONNECTION',['TL-HAND'],['MT-WAGO']),
 op('EL-RI-007-05','EL-RI-007',5,'Выполнить коммутацию в клемме','secondary_qty','PER_CONNECTION',['TL-HAND'],['MT-WAGO']),
 op('EL-RI-007-06','EL-RI-007',6,'Проверить фиксацию проводников в клемме','secondary_qty','PER_CONNECTION',['TL-HAND'],qa=['жила вставлена до упора','нет оголённой меди вне клеммы']),
 op('EL-RI-007-07','EL-RI-007',7,'Уложить соединения и запасы в коробке','primary_qty','PER_BOX',['TL-HAND']),
 op('EL-RI-007-08','EL-RI-007',8,'Закрыть коробку','primary_qty','PER_BOX',['TL-HAND']),
 op('EL-RI-007-09','EL-RI-007',9,'Финальный визуальный контроль','primary_qty','PER_BOX',['TL-HAND'],qa=['коробка закрыта','маркировка читаема','нет пережатия проводников'])
]
# EL-RI-008 — chase for vertical drop
ops += [
 op('EL-RI-008-01','EL-RI-008',1,'Сверить вертикальный опуск и конечную точку','secondary_qty','PER_DROP',['TL-LASER','TL-TAPE'],pre=['актуальная трасса']),
 op('EL-RI-008-02','EL-RI-008',2,'Разметить границы штробы','primary_qty','PER_METER',['TL-LASER','TL-MARK']),
 op('EL-RI-008-03','EL-RI-008',3,'Подготовить пылеудаление и защитить локальную зону','package','FIXED_PACKAGE',['TL-VAC']),
 op('EL-RI-008-04','EL-RI-008',4,'Прорезать границы штробы','primary_qty','PER_METER',['TL-CHASE','TL-VAC']),
 op('EL-RI-008-05','EL-RI-008',5,'Выбрать материал между резами','primary_qty','PER_METER',['TL-CHISEL','TL-VAC']),
 op('EL-RI-008-06','EL-RI-008',6,'Доработать дно и края штробы','primary_qty','PER_METER',['TL-CHISEL']),
 op('EL-RI-008-07','EL-RI-008',7,'Очистить штробу от пыли и крошки','primary_qty','PER_METER',['TL-VAC']),
 op('EL-RI-008-08','EL-RI-008',8,'Контроль глубины, ширины и маршрута','secondary_qty','PER_DROP',['TL-TAPE'],qa=['маршрут','достаточная глубина','нет лишних повреждений']),
 op('EL-RI-008-09','EL-RI-008',9,'Локальная уборка зоны','package','FIXED_PACKAGE',['TL-VAC'])
]
# EL-RI-009 — cable entry into cured socket box
ops += [
 op('EL-RI-009-01','EL-RI-009',1,'Проверить достаточную прочность фиксации подрозетника','primary_qty','PER_UNIT',['TL-HAND'],pre=['монтажный состав затвердел']),
 op('EL-RI-009-02','EL-RI-009',2,'Очистить подрозетник от монтажного состава','primary_qty','PER_UNIT',['TL-HAND','TL-VAC']),
 op('EL-RI-009-03','EL-RI-009',3,'Подготовить штатный ввод под кабель','secondary_qty','PER_CABLE',['TL-HAND']),
 op('EL-RI-009-04','EL-RI-009',4,'Идентифицировать требуемый кабель','secondary_qty','PER_CABLE',['TL-LABEL'],['MT-MARK']),
 op('EL-RI-009-05','EL-RI-009',5,'Завести кабель в подрозетник','secondary_qty','PER_CABLE',['TL-HAND']),
 op('EL-RI-009-06','EL-RI-009',6,'Сформировать технологический запас кабеля','secondary_qty','PER_CABLE',['TL-HAND']),
 op('EL-RI-009-07','EL-RI-009',7,'Уложить запас без повреждения изоляции','secondary_qty','PER_CABLE',['TL-HAND']),
 op('EL-RI-009-08','EL-RI-009',8,'Промаркировать кабель','secondary_qty','PER_CABLE',['TL-LABEL'],['MT-MARK']),
 op('EL-RI-009-09','EL-RI-009',9,'Контроль коробки, кабеля, запаса и маркировки','primary_qty','PER_UNIT',['TL-HAND'],qa=['коробка не расшатана','изоляция не повреждена','запас достаточен','маркировка читаема']),
 op('EL-RI-009-10','EL-RI-009',10,'Локальная уборка','package','FIXED_PACKAGE',['TL-VAC'])
]
norm_rules={
 'schema_version':SCHEMA_VERSION,
 'time_categories':{
   'T_supply_prep':'подготовка снабжения; не входит в технологическую норму',
   'T_engineer_prep':'инженерная подготовка; не входит в технологическую норму',
   'T_installer_prep':'локальная логистика и организация рабочего места до запуска пакета',
   'T_tech':'производительное технологическое время внутри пакета',
   'T_loss':'простои/организационные потери; не увеличивают технологическую норму',
   'T_wait':'технологическая выдержка; календарное время, не человеко-часы'
 },
 'scope_rules':{
   'FIXED_PACKAGE':'учитывается один раз на рабочий пакет',
   'BATCH':'учитывается на одну фактическую партию/замес/подготовку партии',
   'PER_UNIT':'умножается на primary_qty',
   'PER_BLOCK':'умножается на число блоков',
   'PER_METER':'умножается на измеренную длину маршрута/штробы',
   'PER_LINE':'умножается на число линий',
   'PER_LINE_END':'обычно 2 конца на линию; хранить фактическое число концов',
   'PER_FASTENER':'умножается на фактическое число точек крепления',
   'PER_CABLE':'умножается на фактическое число кабелей',
   'PER_BOX':'умножается на число коробок',
   'PER_CONNECTION':'умножается на число соединений',
   'PER_DROP':'умножается на число вертикальных опусков'
 },
 'estimation_formula':'T_est_h = sum(norm_person_min_per_driver * driver_quantity) / 60',
 'labor_cost_formula':'LaborCost = sum(T_role_h * Rate_role)',
 'validation_rule':'Норма публикуется только по валидным наблюдениям; T_loss и T_wait исключаются из T_tech.',
 'crew_rule':'Норма хранится в человеко-минутах. Если 2 человека работают 20 минут, трудоёмкость = 40 чел·мин; календарная длительность хранится отдельно.'
}
def grp(code,name,opcodes):
    return {'code':code,'name':name,'operation_codes':opcodes}
observation_groups={
 'EL-RI-001':[grp('EL-RI-001-G01','Разметка',['EL-RI-001-01','EL-RI-001-02']),grp('EL-RI-001-G02','Коронение отверстий',['EL-RI-001-03']),grp('EL-RI-001-G03','Подготовка отверстий',['EL-RI-001-04','EL-RI-001-05']),grp('EL-RI-001-G04','Подготовка состава',['EL-RI-001-07']),grp('EL-RI-001-G05','Установка подрозетников',['EL-RI-001-06','EL-RI-001-08']),grp('EL-RI-001-G06','Выравнивание',['EL-RI-001-09','EL-RI-001-10']),grp('EL-RI-001-G07','Контроль',['EL-RI-001-11']),grp('EL-RI-001-G08','Уборка',['EL-RI-001-12'])],
 'EL-RI-002':[grp('EL-RI-002-G01','Разметка',['EL-RI-002-01','EL-RI-002-02']),grp('EL-RI-002-G02','Вырезание отверстий',['EL-RI-002-03']),grp('EL-RI-002-G03','Подготовка отверстий',['EL-RI-002-04']),grp('EL-RI-002-G04','Установка коробок',['EL-RI-002-05','EL-RI-002-06']),grp('EL-RI-002-G05','Фиксация',['EL-RI-002-07','EL-RI-002-08']),grp('EL-RI-002-G06','Контроль',['EL-RI-002-09']),grp('EL-RI-002-G07','Уборка',['EL-RI-002-10'])],
 'EL-RI-003':[grp('EL-RI-003-G01','Разметка креплений',['EL-RI-003-01','EL-RI-003-02']),grp('EL-RI-003-G02','Пристрелка площадок',['EL-RI-003-03','EL-RI-003-04']),grp('EL-RI-003-G03','Размотка / прокладка',['EL-RI-003-05','EL-RI-003-06']),grp('EL-RI-003-G04','Крепление стяжками',['EL-RI-003-07']),grp('EL-RI-003-G05','Маркировка',['EL-RI-003-08','EL-RI-003-09']),grp('EL-RI-003-G06','Контроль',['EL-RI-003-10']),grp('EL-RI-003-G07','Завершение',['EL-RI-003-11'])],
 'EL-RI-004':[grp('EL-RI-004-G01','Разметка креплений',['EL-RI-004-01','EL-RI-004-02']),grp('EL-RI-004-G02','Пристрелка площадок',['EL-RI-004-03','EL-RI-004-04']),grp('EL-RI-004-G03','Подготовка группы',['EL-RI-004-05','EL-RI-004-06']),grp('EL-RI-004-G04','Прокладка пучка',['EL-RI-004-07']),grp('EL-RI-004-G05','Крепление стяжками',['EL-RI-004-08']),grp('EL-RI-004-G06','Маркировка',['EL-RI-004-09','EL-RI-004-10']),grp('EL-RI-004-G07','Контроль',['EL-RI-004-11']),grp('EL-RI-004-G08','Завершение',['EL-RI-004-12'])],
 'EL-RI-005':[grp('EL-RI-005-G01','Разметка',['EL-RI-005-01','EL-RI-005-02']),grp('EL-RI-005-G02','Крепление коробки',['EL-RI-005-03','EL-RI-005-04']),grp('EL-RI-005-G03','Подготовка вводов',['EL-RI-005-05']),grp('EL-RI-005-G04','Завод кабелей',['EL-RI-005-06','EL-RI-005-07']),grp('EL-RI-005-G05','Формирование запаса',['EL-RI-005-08']),grp('EL-RI-005-G06','Маркировка',['EL-RI-005-09']),grp('EL-RI-005-G07','Контроль',['EL-RI-005-10']),grp('EL-RI-005-G08','Завершение',['EL-RI-005-11'])],
 'EL-RI-006':[grp('EL-RI-006-G01','Сверка маркировки',['EL-RI-006-01','EL-RI-006-02']),grp('EL-RI-006-G02','Разделка проводников',['EL-RI-006-03']),grp('EL-RI-006-G03','Подбор ГМЛ',['EL-RI-006-04']),grp('EL-RI-006-G04','Опрессовка',['EL-RI-006-05']),grp('EL-RI-006-G05','Монтаж ТТК',['EL-RI-006-06']),grp('EL-RI-006-G06','Термоусадка',['EL-RI-006-07']),grp('EL-RI-006-G07','Укладка соединений',['EL-RI-006-08','EL-RI-006-09']),grp('EL-RI-006-G08','Закрытие коробки',['EL-RI-006-10']),grp('EL-RI-006-G09','Контроль',['EL-RI-006-11'])],
 'EL-RI-007':[grp('EL-RI-007-G01','Сверка маркировки',['EL-RI-007-01','EL-RI-007-02']),grp('EL-RI-007-G02','Разделка проводников',['EL-RI-007-03']),grp('EL-RI-007-G03','Подготовка клемм',['EL-RI-007-04']),grp('EL-RI-007-G04','Коммутация WAGO',['EL-RI-007-05','EL-RI-007-06']),grp('EL-RI-007-G05','Укладка соединений',['EL-RI-007-07']),grp('EL-RI-007-G06','Закрытие коробки',['EL-RI-007-08']),grp('EL-RI-007-G07','Контроль',['EL-RI-007-09'])],
 'EL-RI-008':[grp('EL-RI-008-G01','Разметка',['EL-RI-008-01','EL-RI-008-02']),grp('EL-RI-008-G02','Подготовка пылеудаления',['EL-RI-008-03']),grp('EL-RI-008-G03','Резка штробы',['EL-RI-008-04']),grp('EL-RI-008-G04','Выборка',['EL-RI-008-05','EL-RI-008-06']),grp('EL-RI-008-G05','Очистка',['EL-RI-008-07']),grp('EL-RI-008-G06','Контроль',['EL-RI-008-08']),grp('EL-RI-008-G07','Завершение',['EL-RI-008-09'])],
 'EL-RI-009':[grp('EL-RI-009-G01','Проверка фиксации',['EL-RI-009-01']),grp('EL-RI-009-G02','Очистка подрозетника',['EL-RI-009-02']),grp('EL-RI-009-G03','Подготовка вводов',['EL-RI-009-03']),grp('EL-RI-009-G04','Идентификация кабеля',['EL-RI-009-04']),grp('EL-RI-009-G05','Завод кабеля',['EL-RI-009-05']),grp('EL-RI-009-G06','Формирование запаса',['EL-RI-009-06','EL-RI-009-07']),grp('EL-RI-009-G07','Маркировка',['EL-RI-009-08']),grp('EL-RI-009-G08','Контроль',['EL-RI-009-09']),grp('EL-RI-009-G09','Завершение',['EL-RI-009-10'])]
}
for p0 in packages:
    p0['observation_groups']=observation_groups[p0['code']]
    mapped=[c for g in p0['observation_groups'] for c in g['operation_codes']]
    expected=[x['code'] for x in ops if x['package_code']==p0['code']]
    assert len(mapped)==len(set(mapped)), ('duplicate observation mapping',p0['code'])
    assert set(mapped)==set(expected), ('incomplete observation mapping',p0['code'],set(expected)-set(mapped),set(mapped)-set(expected))

pkg_codes={p['code'] for p in packages}; tool_ids={x['id'] for x in tools}; mat_ids={x['id'] for x in materials}
assert len(pkg_codes)==len(packages)==9
assert len({x['code'] for x in ops})==len(ops)
for x in ops:
    assert x['package_code'] in pkg_codes, x['code']
    missing_t=set(x['tool_ids'])-tool_ids; missing_m=set(x['material_ids'])-mat_ids
    assert not missing_t, (x['code'],missing_t)
    assert not missing_m, (x['code'],missing_m)

for p in packages:
    p['operation_codes']=[x['code'] for x in sorted(ops,key=lambda q:(q['package_code'],q['sequence'])) if x['package_code']==p['code']]

catalog={'schema_version':SCHEMA_VERSION,'discipline':'electrical','phase':'rough_installation_pilot','packages':packages,'operations':ops,'tools':tools,'materials':materials,'norm_rules':norm_rules}
(DATA/'electrical_catalog.v1.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
(DATA/'norm_rules.v1.json').write_text(json.dumps(norm_rules,ensure_ascii=False,indent=2),encoding='utf-8')
with (DATA/'electrical_operations.v1.csv').open('w',newline='',encoding='utf-8-sig') as f:
    fields=['code','package_code','sequence','name','time_class','quantity_driver','measurement_scope','crew_rule','tool_ids','material_ids','preconditions','qa','notes']
    w=csv.DictWriter(f,fieldnames=fields,delimiter=';'); w.writeheader()
    for x in ops:
        row=x.copy()
        for k in ['tool_ids','material_ids','preconditions','qa']:
            row[k]=' | '.join(row[k])
        w.writerow(row)
with (DATA/'electrical_work_packages.v1.csv').open('w',newline='',encoding='utf-8-sig') as f:
    fields=['code','key','name','primary_unit','secondary_unit','norm_basis','start_boundary','finish_boundary','exclusions','operation_codes','observation_groups']
    w=csv.DictWriter(f,fieldnames=fields,delimiter=';'); w.writeheader()
    for p in packages:
        row=p.copy(); row['exclusions']=' | '.join(row['exclusions']); row['operation_codes']=' | '.join(row['operation_codes']); row['observation_groups']=' | '.join(g['code']+': '+g['name'] for g in row['observation_groups']); w.writerow(row)
lines=['# VIVUM — Каталог операций черновой электрики v1.0','',f'Пакетов: {len(packages)}. Операций: {len(ops)}.','', 'Время операции хранится как человеко-минуты. Подготовка снабжения, инженера и локальная логистика до старта пакета учитываются отдельно.','']
for p in packages:
    lines += [f"## {p['code']} — {p['name']}",f"База нормы: **{p['primary_unit']}**; дополнительный драйвер: **{p['secondary_unit']}**.",f"Старт: {p['start_boundary']}",f"Финиш: {p['finish_boundary']}",'', '| Код | Операция | Драйвер | Масштаб | Основной инструмент |', '|---|---|---|---|---|']
    for x in sorted([q for q in ops if q['package_code']==p['code']],key=lambda q:q['sequence']):
        tool=', '.join(next(t['name'] for t in tools if t['id']==tid) for tid in x['tool_ids']) or '—'
        lines.append(f"| {x['code']} | {x['name']} | {x['quantity_driver']} | {x['measurement_scope']} | {tool} |")
    lines += ['', 'Не входит: '+('; '.join(p['exclusions']) if p['exclusions'] else '—'), '']
(DOCS/'OPERATION_CATALOG.md').write_text('\n'.join(lines),encoding='utf-8')
print('packages',len(packages),'operations',len(ops),'tools',len(tools),'materials',len(materials))
