import argparse, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def money(v):
    return round(float(v)+1e-12,2)
def missing(result,component,reason):
    result['missing'].append({'component':component,'reason':reason}); result['complete']=False
def pct_amount(base,p):
    return float(base)*float(p)/100
def main():
    ap=argparse.ArgumentParser(description='VIVUM commercial price layer')
    ap.add_argument('--production',required=True)
    ap.add_argument('--policy',default=str(ROOT/'data/commercial_policy.template.json'))
    ap.add_argument('--output')
    a=ap.parse_args(); prod=load(a.production); pol=load(a.policy)
    raw_cost=prod.get('fullProductionCost')
    cost=float(raw_cost) if raw_cost is not None else float(prod.get('knownPartialCost',0))
    result={'productionEstimateId':prod.get('productionEstimateId'),'currency':pol.get('currency','RUB'),
            'complete':bool(prod.get('complete')),'missing':[],
            'fullProductionCost':money(cost) if prod.get('complete') else None,
            'knownPartialProductionCost':money(cost) if not prod.get('complete') else None}
    currency_ok=not prod.get('currency') or prod.get('currency')==pol.get('currency','RUB')
    if not currency_ok:
        missing(result,'currency','production_and_commercial_policy_currency_mismatch')
    if not prod.get('complete') or not currency_ok:
        missing(result,'production','production_cost_incomplete')
        result.update({'risk':None,'profit':None,'contractAdjustments':[],'priceBeforeTax':None,'tax':None,'knownPartialPrice':None,'clientPrice':None})
        text=json.dumps(result,ensure_ascii=False,indent=2)
        if a.output: Path(a.output).write_text(text,encoding='utf-8')
        else: print(text)
        return
    risk=pol.get('risk',{}); method=risk.get('method')
    if method=='NONE': risk_amount=0
    elif method=='PERCENT_FULL_COST' and risk.get('percent') is not None: risk_amount=pct_amount(cost,risk['percent'])
    elif method=='FIXED_AMOUNT' and risk.get('amount') is not None: risk_amount=float(risk['amount'])
    else: missing(result,'risk','risk_policy_missing'); risk_amount=0
    result['risk']={'method':method,'amount':money(risk_amount)}
    base=cost+risk_amount
    profit=pol.get('profit',{}); method=profit.get('method')
    if method=='NONE': profit_amount=0; pre_tax=base
    elif method=='MARKUP_PERCENT' and profit.get('percent') is not None:
        profit_amount=pct_amount(base,profit['percent']); pre_tax=base+profit_amount
    elif method=='TARGET_MARGIN_PERCENT' and profit.get('percent') is not None and 0 <= float(profit['percent']) < 100:
        pre_tax=base/(1-float(profit['percent'])/100); profit_amount=pre_tax-base
    elif method=='FIXED_AMOUNT' and profit.get('amount') is not None:
        profit_amount=float(profit['amount']); pre_tax=base+profit_amount
    else:
        missing(result,'profit','profit_policy_missing_or_invalid'); profit_amount=0; pre_tax=base
    result['profit']={'method':method,'amount':money(profit_amount)}
    adjustments=[]
    for adj in pol.get('contractAdjustments',[]):
        m=adj.get('method'); name=adj.get('name','Корректировка'); amount=0
        if m=='ADD_FIXED' and adj.get('amount') is not None: amount=float(adj['amount'])
        elif m=='DISCOUNT_FIXED' and adj.get('amount') is not None: amount=-float(adj['amount'])
        elif m=='ADD_PERCENT' and adj.get('percent') is not None: amount=pct_amount(pre_tax,adj['percent'])
        elif m=='DISCOUNT_PERCENT' and adj.get('percent') is not None: amount=-pct_amount(pre_tax,adj['percent'])
        else: missing(result,'contractAdjustment',name); amount=0
        pre_tax+=amount; adjustments.append({'name':name,'method':m,'amount':money(amount)})
    result['contractAdjustments']=adjustments
    result['priceBeforeTax']=money(pre_tax)
    tax=pol.get('tax',{}); method=tax.get('method')
    if method=='NONE': tax_amount=0
    elif method=='PERCENT_PRICE_BEFORE_TAX' and tax.get('percent') is not None: tax_amount=pct_amount(pre_tax,tax['percent'])
    elif method=='FIXED_AMOUNT' and tax.get('amount') is not None: tax_amount=float(tax['amount'])
    else: missing(result,'tax','tax_policy_missing'); tax_amount=0
    result['tax']={'method':method,'amount':money(tax_amount)}
    result['knownPartialPrice']=money(pre_tax+tax_amount)
    if not result['complete']:
        result['priceBeforeTax']=None
        result['clientPrice']=None
    else:
        result['clientPrice']=result['knownPartialPrice']
    text=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output: Path(a.output).write_text(text,encoding='utf-8')
    else: print(text)
if __name__=='__main__':
    main()
