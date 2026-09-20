import json,re
from pathlib import Path
r=Path(r'C:\Temp\vivum-chronometer')
html=(r/'index.html').read_text(encoding='utf-8')
cat=json.loads((r/'data/electrical_catalog.v1.json').read_text(encoding='utf-8'))
for p in cat['packages']:
    pat=rf"{re.escape(p['key'])}:\{{code:'{p['code']}',name:.*?stages:\[(.*?)\],supply:"
    m=re.search(pat,html,re.S)
    if not m: raise RuntimeError('stages not found '+p['code'])
    stages=re.findall(r"'([^']*)'",m.group(1))
    groups=[g['name'] for g in p['observation_groups']]
    if stages!=groups: raise RuntimeError(f"stage mismatch {p['code']}\napp={stages}\ncat={groups}")
print('APP_STAGE_MAPPING_OK',len(cat['packages']))
for f in ['measurement_record.schema.json','norm_card.schema.json']:
    json.loads((r/'schemas'/f).read_text(encoding='utf-8'))
print('SCHEMAS_JSON_OK')
estimate_schema=json.loads((r/'schemas'/'estimate_request.schema.json').read_text(encoding='utf-8'))
assert estimate_schema['title']=='VIVUM Labor Estimate Request'
norms=json.loads((r/'data'/'norm_cards.template.json').read_text(encoding='utf-8'))
assert len(norms['cards'])==len(cat['operations'])
assert {c['operationCode'] for c in norms['cards']}=={o['code'] for o in cat['operations']}
rates=json.loads((r/'data'/'rate_card.template.json').read_text(encoding='utf-8'))
assert {'installer','engineer','supply'}<=set(rates['roles'])
print('ESTIMATOR_TEMPLATES_OK',len(norms['cards']))
driver_rules=json.loads((r/'data'/'driver_rules.v1.json').read_text(encoding='utf-8'))
used_drivers={o['quantity_driver'] for o in cat['operations']}
missing_drivers=used_drivers-set(driver_rules['drivers'])
assert not missing_drivers, ('missing driver rules',missing_drivers)
print('DRIVER_RULES_OK',len(used_drivers))
resources=json.loads((r/'data'/'package_resource_requirements.v1.json').read_text(encoding='utf-8'))
assert len(resources['packages'])==len(cat['packages'])
tids={x['id'] for x in cat['tools']}; mids={x['id'] for x in cat['materials']}
for p0 in resources['packages']:
    assert set(p0['toolIds'])<=tids and set(p0['materialIds'])<=mids
print('RESOURCE_MATRIX_OK',len(resources['packages']))
