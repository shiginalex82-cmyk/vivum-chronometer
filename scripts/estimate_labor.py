import argparse, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def main():
    ap=argparse.ArgumentParser(description='VIVUM labor estimate from approved norms')
    ap.add_argument('request')
    ap.add_argument('--norms',default=str(ROOT/'data/norm_cards.template.json'))
    ap.add_argument('--rates',default=str(ROOT/'data/rate_card.template.json'))
    ap.add_argument('--output')
    a=ap.parse_args()
    catalog=load(ROOT/'data/electrical_catalog.v1.json')
    req=load(a.request); norms=load(a.norms); rates=load(a.rates)
    packages={p['code']:p for p in catalog['packages']}
    operations={o['code']:o for o in catalog['operations']}
    cards={c['operationCode']:c for c in norms['cards']}
    role_rates={k:v.get('hourlyCost') for k,v in rates['roles'].items()}
    accepted={'WORKING','APPROVED'}
    result={'estimateId':req['estimateId'],'project':req.get('project',''),'currency':rates.get('currency','RUB'),'packages':[],'missing':[],'complete':True,'laborPersonMin':0.0,'laborCost':0.0}
    for item in req['packages']:
        code=item['workPackageCode']; p=packages.get(code)
        if not p:
            result['missing'].append({'package':code,'reason':'unknown_package'}); result['complete']=False; continue
        po={'workPackageCode':code,'name':p['name'],'operations':[],'prep':[],'laborPersonMin':0.0,'laborCost':0.0,'complete':True}
        drivers=item.get('drivers',{})
        for oc in p['operation_codes']:
            o=operations[oc]; card=cards.get(oc); scope=o['measurement_scope']; driver=o['quantity_driver']
            qty=1.0 if scope=='FIXED_PACKAGE' else drivers.get(driver)
            missing=[]
            if qty is None: missing.append('driver:'+driver)
            if not card or card.get('recommendedPersonMin') is None or card.get('status') not in accepted: missing.append('approved_norm')
            rate=role_rates.get(o.get('role_id','installer'))
            if rate is None: missing.append('rate:'+o.get('role_id','installer'))
            if missing:
                result['missing'].append({'package':code,'operation':oc,'missing':missing}); po['complete']=False; result['complete']=False
                po['operations'].append({'operationCode':oc,'name':o['name'],'quantity':qty,'status':'NOT_CALCULATED','missing':missing}); continue
            person_min=float(card['recommendedPersonMin'])*float(qty)
            cost=person_min/60*float(rate)
            po['operations'].append({'operationCode':oc,'name':o['name'],'driver':driver,'quantity':qty,'normPersonMin':card['recommendedPersonMin'],'personMin':person_min,'role':o.get('role_id','installer'),'hourlyCost':rate,'cost':cost,'normStatus':card['status']})
            po['laborPersonMin']+=person_min; po['laborCost']+=cost
        for role,person_min in item.get('prepPersonMin',{}).items():
            rate=role_rates.get(role)
            if rate is None:
                result['missing'].append({'package':code,'prepRole':role,'missing':['rate:'+role]}); po['complete']=False; result['complete']=False
                po['prep'].append({'role':role,'personMin':person_min,'status':'NOT_CALCULATED'}); continue
            cost=float(person_min)/60*float(rate)
            po['prep'].append({'role':role,'personMin':person_min,'hourlyCost':rate,'cost':cost})
            po['laborPersonMin']+=float(person_min); po['laborCost']+=cost
        result['laborPersonMin']+=po['laborPersonMin']; result['laborCost']+=po['laborCost']; result['packages'].append(po)
    result['laborHours']=result['laborPersonMin']/60
    text=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output: Path(a.output).write_text(text,encoding='utf-8')
    else: print(text)

if __name__=='__main__':
    main()
