import argparse, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def add_missing(result,requirement,reason,resource=None):
    x={'requirementId':requirement,'reason':reason}
    if resource: x['resourceId']=resource
    result['missing'].append(x); result['complete']=False

def selected_resources(req_def, request, result):
    rid=req_def['requirementId']; allowed=req_def['resourceIds']; mode=req_def['mode']
    if mode=='REQUIRED': return allowed
    chosen=request.get('selections',{}).get(rid,[])
    if not chosen:
        add_missing(result,rid,'selection_missing'); return []
    if any(x not in allowed for x in chosen):
        add_missing(result,rid,'selection_not_allowed'); return []
    if mode=='ONE_OF' and len(chosen)!=1:
        add_missing(result,rid,'exactly_one_selection_required'); return []
    if mode=='ONE_OR_MORE_OF' and len(chosen)<1:
        add_missing(result,rid,'one_or_more_selection_required'); return []
    return chosen

def manual_quantity(request,rid,resource):
    for x in request.get('manualQuantities',{}).get(rid,[]):
        if x.get('resourceId')==resource: return x
    return None
def policy_quantity(rule,drivers):
    if not rule or rule.get('status') not in {'WORKING','APPROVED'}:
        return None,None,'consumption_policy_not_approved'
    method=rule.get('method'); unit=rule.get('quantityUnit')
    if method=='MULTIPLIER':
        driver=rule.get('driver'); value=drivers.get(driver); mult=rule.get('quantityPerDriver')
        if value is None: return None,unit,'driver_missing:'+str(driver)
        if mult is None: return None,unit,'policy_value_missing:quantityPerDriver'
        return float(value)*float(mult),unit,None
    if method=='CABLE_LENGTH_WITH_RESERVE':
        route=drivers.get(rule.get('driver','route_length')); ends=drivers.get(rule.get('endDriver','line_end_qty'))
        pct=rule.get('reservePercent'); end_m=rule.get('endReserveM')
        if route is None: return None,unit,'driver_missing:route_length'
        if ends is None: return None,unit,'driver_missing:line_end_qty'
        if pct is None or end_m is None: return None,unit,'policy_value_missing:cable_reserve'
        return float(route)*(1+float(pct)/100)+float(ends)*float(end_m),unit,None
    if method=='RATIO':
        driver=rule.get('driver'); value=drivers.get(driver); per=rule.get('sourceUnitsPerResourceUnit')
        if value is None: return None,unit,'driver_missing:'+str(driver)
        if per is None or float(per)<=0: return None,unit,'policy_value_missing:sourceUnitsPerResourceUnit'
        return float(value)/float(per),unit,None
    if method=='DIRECT_SELECTED_QUANTITIES':
        return None,unit,'manual_quantity_required'
    return None,unit,'unsupported_consumption_method'

def main():
    ap=argparse.ArgumentParser(description='VIVUM strict resource quantity derivation')
    ap.add_argument('request'); ap.add_argument('--policy',default=str(ROOT/'data/consumption_policy.v1.json')); ap.add_argument('--output')
    a=ap.parse_args(); request=load(a.request); policy=load(a.policy)
    requirements=load(ROOT/'data/package_resource_requirements.v2.json')
    package=next((x for x in requirements['packages'] if x['workPackageCode']==request['workPackageCode']),None)
    if not package: raise SystemExit('Unknown workPackageCode')
    result={'resourceBuildId':request['resourceBuildId'],'workPackageCode':request['workPackageCode'],'complete':True,'materials':[],'tools':package['tools'],'missing':[],'policyId':policy.get('policyId')}
    drivers=request.get('drivers',{}); overrides=request.get('costResponsibilityOverrides',{}); rules=policy.get('rules',{})
    for rr in package['materials']:
        rid=rr['requirementId']; selected=selected_resources(rr,request,result)
        responsibility=overrides.get(rid,request['defaultCostResponsibility'])
        for resource in selected:
            manual=manual_quantity(request,rid,resource); qty=None; unit=None; source=None; error=None
            if manual:
                qty=float(manual['quantity']); unit=manual['unit']; source=manual['source']
                if rr.get('quantityUnit') and unit!=rr['quantityUnit']: error='manual_unit_mismatch'
            elif rr.get('multiplier') is not None and rr.get('quantityDriver'):
                d=rr['quantityDriver']; value=drivers.get(d)
                if value is None: error='driver_missing:'+d
                else:
                    qty=float(value)*float(rr['multiplier']); unit=rr.get('quantityUnit'); source='AUTO_DRIVER'
            elif rr.get('consumptionRuleId'):
                qty,unit,error=policy_quantity(rules.get(rr['consumptionRuleId']),drivers); source='APPROVED_POLICY' if not error else None
            else:
                error='quantity_rule_missing'
            if error:
                add_missing(result,rid,error,resource)
                result['materials'].append({'requirementId':rid,'resourceId':resource,'quantity':None,'unit':unit or rr.get('quantityUnit'),'costResponsibility':responsibility,'status':'NOT_DERIVED','reason':error})
            else:
                result['materials'].append({'requirementId':rid,'resourceId':resource,'quantity':qty,'unit':unit,'costResponsibility':responsibility,'status':'DERIVED','source':source})
    text=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output: Path(a.output).write_text(text,encoding='utf-8')
    else: print(text)

if __name__=='__main__': main()
