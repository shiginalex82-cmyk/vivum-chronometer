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
