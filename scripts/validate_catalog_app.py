import json,re
from pathlib import Path
r=Path(__file__).resolve().parents[1]
def load(rel):
    return json.loads((r/rel).read_text(encoding='utf-8-sig'))
html=(r/'index.html').read_text(encoding='utf-8')
cat=load('data/electrical_catalog.v1.json')
for p in cat['packages']:
    pat=rf"{re.escape(p['key'])}:\{{code:'{p['code']}',name:.*?stages:\[(.*?)\],supply:"
    m=re.search(pat,html,re.S)
    if not m: raise RuntimeError('stages not found '+p['code'])
    stages=re.findall(r"'([^']*)'",m.group(1))
    groups=[g['name'] for g in p['observation_groups']]
    if stages!=groups: raise RuntimeError(f"stage mismatch {p['code']}\napp={stages}\ncat={groups}")
print('APP_STAGE_MAPPING_OK',len(cat['packages']))
for f in ['measurement_record.schema.json','norm_card.schema.json','estimate_request.schema.json','production_cost_request.schema.json','production_cost_policy.schema.json','commercial_policy.schema.json','resource_requirements.schema.json','cost_rate_card.schema.json','resource_quantity_request.schema.json','resource_quantity_result.schema.json','consumption_policy.schema.json','future_electrical_connection_model.schema.json']:
    load('schemas/'+f)
print('SCHEMAS_JSON_OK')
norms=load('data/norm_cards.template.json')
assert len(norms['cards'])==len(cat['operations'])
assert {c['operationCode'] for c in norms['cards']}=={o['code'] for o in cat['operations']}
rates=load('data/rate_card.template.json')
assert {'installer','engineer','supply'}<=set(rates['roles'])
print('ESTIMATOR_TEMPLATES_OK',len(norms['cards']))
driver_rules=load('data/driver_rules.v1.json')
used_drivers={o['quantity_driver'] for o in cat['operations']}
missing_drivers=used_drivers-set(driver_rules['drivers'])
assert not missing_drivers, ('missing driver rules',missing_drivers)
print('DRIVER_RULES_OK',len(used_drivers))
tids={x['id'] for x in cat['tools']}; mids={x['id'] for x in cat['materials']}
resources=load('data/package_resource_requirements.v1.json')
assert len(resources['packages'])==len(cat['packages'])
for p0 in resources['packages']:
    assert set(p0['toolIds'])<=tids and set(p0['materialIds'])<=mids
print('RESOURCE_MATRIX_V1_OK',len(resources['packages']))
resources2=load('data/package_resource_requirements.v2.json')
assert len(resources2['packages'])==len(cat['packages'])
allowed_modes={'REQUIRED','ONE_OF','ONE_OR_MORE_OF','REQUIRED_CAPABILITY','CONDITIONAL'}
for p0 in resources2['packages']:
    for x in p0['tools']:
        assert x['resourceId'] in tids and x['mode'] in allowed_modes
    for x in p0['materials']:
        assert set(x['resourceIds'])<=mids and x['mode'] in allowed_modes
print('RESOURCE_MATRIX_V2_OK',len(resources2['packages']))
cost_rates=load('data/cost_rate_card.template.json')
assert set(cost_rates['materials'])==mids
assert set(cost_rates['tools'])==tids
assert set(cost_rates['logistics'])=={'SITE_DELIVERY_TRIP','VEHICLE_HOUR','EXTERNAL_DELIVERY'}
load('data/production_cost_policy.template.json')
load('data/commercial_policy.template.json')
print('COST_TEMPLATES_OK',len(cost_rates['materials']),len(cost_rates['tools']))

commercial=load('data/commercial_policy.template.json')
assert commercial['risk']['method'] in {None,'NONE','PERCENT_FULL_COST','FIXED_AMOUNT'}
assert commercial['profit']['method'] in {None,'NONE','MARKUP_PERCENT','TARGET_MARGIN_PERCENT','FIXED_AMOUNT'}
assert commercial['tax']['method'] in {None,'NONE','PERCENT_PRICE_BEFORE_TAX','FIXED_AMOUNT'}
el1=next(x for x in resources2['packages'] if x['workPackageCode']=='EL-RI-001')
assert any(x['mode']=='ONE_OF' and 'MT-COMPOUND-OTHER' in x['resourceIds'] for x in el1['materials'])
el3=next(x for x in resources2['packages'] if x['workPackageCode']=='EL-RI-003')
assert any(x['mode']=='ONE_OF' and len(x['resourceIds'])==7 for x in el3['materials'])
print('COMMERCIAL_AND_ALTERNATIVES_OK')

pilot=load('data/pilot_2689_cost_rates.json')
assert pilot['currency']=='RUB' and pilot['sourceInvoice']=='Счет №2689 от 21.07.2026'
assert set(pilot['materials'])<=mids
assert all(float(x['unitCost'])>0 for x in pilot['materials'].values())
assert pilot['materials']['MT-2689-07']['pricingUnit']=='шт'
assert abs(pilot['materials']['MT-2689-07']['unitCost']*100-48.46)<1e-9
assert len(pilot['purchaseVariants'])==5
print('PILOT_2689_RATES_OK',len(pilot['materials']),len(pilot['purchaseVariants']))

consumption=load('data/consumption_policy.template.json')
rule_ids=set(consumption['rules'])
for p0 in resources2['packages']:
    for x in p0['materials']:
        if x.get('consumptionRuleId'): assert x['consumptionRuleId'] in rule_ids
        if x.get('multiplier') is not None: assert x.get('quantityUnit')
print('CONSUMPTION_CONTRACT_OK',len(rule_ids))

cons=load('data/consumption_policy.v1.json')
gas=cons['rules']['CR-GAS-SHOTS-PER-CYLINDER']
assert gas['status']=='APPROVED' and gas['sourceUnitsPerResourceUnit']==1000
print('GAS_CONSUMPTION_RULE_OK',gas['sourceUnitsPerResourceUnit'])

# Future Revit connection contract: GML is project-derived; TTK derives from selected GML.
el6=next(x for x in resources2['packages'] if x['workPackageCode']=='EL-RI-006')
gml=next(x for x in el6['materials'] if x['requirementId']=='EL-RI-006-M01')
ttk=next(x for x in el6['materials'] if x['requirementId']=='EL-RI-006-M02')
assert gml.get('derivationMode')=='FUTURE_REVIT_CONNECTION_MODEL' and gml['consumptionStatus']=='PROJECT_MODEL_REQUIRED'
assert ttk.get('derivationMode')=='DERIVED_FROM_REQUIREMENT' and ttk.get('dependsOnRequirementId')=='EL-RI-006-M01'
assert ttk.get('consumptionRuleId')=='CR-TTK-FROM-GML' and ttk['consumptionStatus']=='UPSTREAM_RESOURCE_REQUIRED'
cp=load('data/consumption_policy.v1.json'); tr=cp['rules']['CR-TTK-FROM-GML']
assert tr['status']=='DRAFT' and tr['method']=='DERIVED_FROM_UPSTREAM_RESOURCE' and tr['reserveBeforeMm'] is None and tr['reserveAfterMm'] is None
print('FUTURE_GML_TTK_CONTRACT_OK')
