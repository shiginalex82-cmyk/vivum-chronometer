import argparse, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def money(v):
    return round(float(v)+1e-12,2)
def add_missing(result,kind,key,reason):
    result['missing'].append({'kind':kind,'key':key,'reason':reason}); result['complete']=False
def main():
    ap=argparse.ArgumentParser(description='VIVUM production cost estimate')
    ap.add_argument('request')
    ap.add_argument('--labor',required=True)
    ap.add_argument('--rates',default=str(ROOT/'data/cost_rate_card.template.json'))
    ap.add_argument('--policy',default=str(ROOT/'data/production_cost_policy.template.json'))
    ap.add_argument('--output')
    a=ap.parse_args()
    req=load(a.request); labor=load(a.labor); rates=load(a.rates); policy=load(a.policy)
    result={'productionEstimateId':req['productionEstimateId'],'laborEstimateId':labor.get('estimateId'),
            'currency':rates.get('currency','RUB'),'complete':bool(labor.get('complete')),
            'missing':[],'components':{'labor':money(labor.get('laborCost',0)),'materials':[],
            'equipment':[],'logistics':[],'directCosts':[]},'overhead':None}
    if not labor.get('complete'): add_missing(result,'labor',labor.get('estimateId'),'labor_estimate_incomplete')
    currency_ok=True
    base_currency=rates.get('currency','RUB')
    if labor.get('currency') and labor.get('currency')!=base_currency: add_missing(result,'currency','labor','labor_currency_mismatch'); currency_ok=False
    if policy.get('currency') and policy.get('currency')!=base_currency: add_missing(result,'currency','policy','production_policy_currency_mismatch'); currency_ok=False
    for line in req.get('materials',[]):
        rid=line['resourceId']; responsibility=line.get('costResponsibility','VIVUM'); rate=rates.get('materials',{}).get(rid,{})
        unit_cost=rate.get('unitCost'); pricing_unit=rate.get('pricingUnit'); request_unit=line.get('unit')
        excluded=responsibility!='VIVUM'; cost=0
        if not excluded:
            if unit_cost is None: add_missing(result,'material',rid,'unit_cost_missing')
            elif not pricing_unit: add_missing(result,'material',rid,'pricing_unit_missing')
            elif pricing_unit!=request_unit: add_missing(result,'material',rid,'pricing_unit_mismatch')
            else: cost=float(line['quantity'])*float(unit_cost)
        result['components']['materials'].append({'resourceId':rid,'quantity':line['quantity'],'unit':request_unit,'costResponsibility':responsibility,'excludedFromVivumCost':excluded,'unitCost':unit_cost,'pricingUnit':pricing_unit,'cost':money(cost)})
    for line in req.get('equipment',[]):
        rid=line['toolId']; rate=rates.get('tools',{}).get(rid,{})
        unit_cost=rate.get('unitCost'); expected_basis=rate.get('rateBasis')
        if unit_cost is None:
            add_missing(result,'equipment',rid,'unit_cost_missing'); cost=0
        elif expected_basis and expected_basis!=line['rateBasis']:
            add_missing(result,'equipment',rid,'rate_basis_mismatch'); cost=0
        else: cost=float(line['quantity'])*float(unit_cost)
        result['components']['equipment'].append({'toolId':rid,'quantity':line['quantity'],'rateBasis':line['rateBasis'],'unitCost':unit_cost,'cost':money(cost)})
    for line in req.get('logistics',[]):
        code=line['rateCode']; rate=rates.get('logistics',{}).get(code,{}); unit_cost=rate.get('unitCost'); pricing_unit=rate.get('pricingUnit'); request_unit=line.get('unit')
        if unit_cost is None: add_missing(result,'logistics',code,'unit_cost_missing'); cost=0
        elif not pricing_unit: add_missing(result,'logistics',code,'pricing_unit_missing'); cost=0
        elif pricing_unit!=request_unit: add_missing(result,'logistics',code,'pricing_unit_mismatch'); cost=0
        else: cost=float(line['quantity'])*float(unit_cost)
        result['components']['logistics'].append({'rateCode':code,'quantity':line['quantity'],'unit':request_unit,'pricingUnit':pricing_unit,'unitCost':unit_cost,'cost':money(cost)})
    for line in req.get('directCosts',[]):
        amount=float(line['amount'])
        result['components']['directCosts'].append({'category':line['category'],'name':line['name'],'amount':money(amount)})
    direct=sum([result['components']['labor']]+[x['cost'] for x in result['components']['materials']]+[x['cost'] for x in result['components']['equipment']]+[x['cost'] for x in result['components']['logistics']]+[x['amount'] for x in result['components']['directCosts']])
    result['directProductionCost']=money(direct)
    if req.get('includeOverhead',True):
        oh=policy.get('overhead',{}); method=oh.get('method')
        if method=='PERCENT_DIRECT_COST' and oh.get('percent') is not None:
            amount=direct*float(oh['percent'])/100
        elif method=='FIXED_AMOUNT' and oh.get('amount') is not None:
            amount=float(oh['amount'])
        else:
            add_missing(result,'overhead','policy','overhead_policy_missing'); amount=0
        result['overhead']={'method':method,'amount':money(amount)}
    else:
        amount=0; result['overhead']={'method':'EXCLUDED_BY_REQUEST','amount':0}
    result['currencyCompatible']=currency_ok
    result['knownPartialCost']=money(direct+amount) if currency_ok else None
    result['fullProductionCost']=result['knownPartialCost'] if result['complete'] and currency_ok else None
    text=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output: Path(a.output).write_text(text,encoding='utf-8')
    else: print(text)
if __name__=='__main__':
    main()
