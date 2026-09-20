import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
def load(name):
    return json.loads((DATA/name).read_text(encoding='utf-8-sig'))
def save(name,obj):
    (DATA/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
cat=load('electrical_catalog.v1.json')
material_rates={m['id']:{'name':m['name'],'pricingUnit':None,'unitCost':None,'source':None,'validFrom':None} for m in cat['materials']}
tool_rates={t['id']:{'name':t['name'],'rateBasis':None,'unitCost':None,'source':None,'validFrom':None} for t in cat['tools']}
logistics={
 'SITE_DELIVERY_TRIP':{'name':'Доставка на объект, рейс','pricingUnit':'рейс','unitCost':None},
 'VEHICLE_HOUR':{'name':'Транспорт на объекте/между складами','pricingUnit':'маш·ч','unitCost':None},
 'EXTERNAL_DELIVERY':{'name':'Внешняя доставка/курьер','pricingUnit':'услуга','unitCost':None}
}
save('cost_rate_card.template.json',{
 'schema_version':'1.0','currency':'RUB','materials':material_rates,'tools':tool_rates,'logistics':logistics
})
save('production_cost_policy.template.json',{
 'schema_version':'1.0','currency':'RUB',
 'overhead':{'method':None,'percent':None,'amount':None,'base':'DIRECT_PRODUCTION_COST','source':None},
 'notes':'Пустой шаблон. Процент задаётся числом 15 для 15%. Автоподстановки запрещены.'
})
save('commercial_policy.template.json',{
 'schema_version':'1.0','currency':'RUB',
 'risk':{'method':None,'percent':None,'amount':None,'base':'FULL_PRODUCTION_COST'},
 'profit':{'method':None,'percent':None,'amount':None,'base':'COST_PLUS_RISK'},
 'tax':{'method':None,'percent':None,'amount':None,'base':'PRICE_BEFORE_TAX'},
 'contractAdjustments':[],
 'notes':'Для прибыли различаются MARKUP_PERCENT и TARGET_MARGIN_PERCENT. Значения 15 означают 15%.'
})
print('cost templates',len(material_rates),len(tool_rates),len(logistics))
