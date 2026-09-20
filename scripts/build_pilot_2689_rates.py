import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
SOURCE='Счет №2689 от 21.07.2026'
SUPPLIER='ООО "ЭТМ "КОСТРОМА ПЛЮС"'
def rate(name,pos,unit,cost,code=None,**extra):
    x={'name':name,'sourceInvoice':SOURCE,'invoicePosition':pos,'supplier':SUPPLIER,
       'pricingUnit':unit,'unitCost':cost,'currency':'RUB','validFrom':'2026-07-21'}
    if code: x['supplierCode']=code
    x.update(extra); return x
materials={
 'MT-2689-01':rate('ВВГнг-LS 3×2,5(ож)-0,66 ГОСТ',1,'м',116.05,'3000722'),
 'MT-2689-02':rate('ВВГ-LS 3×1,5 кабель',2,'м',73.33,'330315'),
 'MT-2689-03':rate('КГВВнг 5×0,75 кабель',3,'м',74.76,'315045'),
 'MT-2689-04':rate('КГВВнг(А)-LS 7×0,75 кабель',4,'м',122.15,'3954262'),
 'MT-2689-05':rate('Коробка установочная СЗ блочная для твердых стен Ø68×60',5,'шт',11.97,'1458052'),
 'MT-2689-06':rate('Площадка под стяжку для прямого монтажа черная',6,'шт',3.50,'130342'),
 'MT-2689-07':rate('Стяжка нейлоновая КСС 3×150 ч',7,'шт',0.4846,'459399',
                    sourcePricingUnit='упак',sourceUnitCost=48.46,packageSize=100,
                    conversion='48.46 ₽/упак ÷ 100 шт/упак'),
 'MT-2689-11':rate('ВВГнг-LS 4×1,5(ож)-0,66 ГОСТ',11,'м',102.40,'3000751'),
 'MT-2689-12':rate('Гвоздь усиленный CN EG bullet point 3,05×17 мм',12,'шт',1.45,'621317'),
 'MT-2689-27':rate('Коробка уст. 68×45 с/у г/к IMT35150 SchE',27,'шт',30.44,'452492'),
 'MT-2689-30':rate('Газовый баллон для монтажных пистолетов 165 мм',30,'шт',350.03,'7308061'),
 'MT-2689-36':rate('КГВВнг 3×1,5 кабель',36,'м',97.75,'315314'),
 'MT-2689-40':rate('КГВВнг 3×2,5 кабель',40,'м',146.63,'315316')
}
variants={
 'MT-2689-08':rate('Трубка ТТК-(3:1)-6/2 черная (КВТ)',8,'м',38.94,'5150711'),
 'MT-2689-09':rate('Трубка ТТК (3:1)-9/3 черная',9,'м',68.28,'445447'),
 'MT-2689-33':rate('Гильза медная луженая ГМЛ 2,5-2,6 ГОСТ 23469.3 IEK',33,'шт',12.12,'231251'),
 'MT-2689-34':rate('ГМЛ 4-3 (Техэл) Гильза медная',34,'шт',12.80,'7001005'),
 'MT-2689-35':rate('ГМЛ 6-4 (Техэл) Гильза медная',35,'шт',17.81,'7001006')
}
out={
 'schema_version':'1.0','rateCardId':'PILOT-2689-2026-07-21','currency':'RUB',
 'scope':'VIVUM electrical rough-installation pilot','sourceInvoice':SOURCE,
 'materials':materials,'purchaseVariants':variants,'tools':{},'logistics':{},
 'notes':'Пилотные закупочные ставки. Не являются корпоративным прайсом. ГМЛ/ТТК используются только после выбора конкретного типоразмера.'
}
(DATA/'pilot_2689_cost_rates.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('mapped rates',len(materials),'variants',len(variants))
