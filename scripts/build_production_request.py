import argparse, json, sys
from pathlib import Path

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def main():
    ap=argparse.ArgumentParser(description='VIVUM strict Production Cost Request builder')
    ap.add_argument('--resource',action='append',required=True,help='Resource Quantity Build result; repeat for multiple packages')
    ap.add_argument('--production-id',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--no-overhead',action='store_true')
    a=ap.parse_args(); builds=[load(x) for x in a.resource]
    incomplete=[{'resourceBuildId':x.get('resourceBuildId'),'missing':x.get('missing',[])} for x in builds if not x.get('complete')]
    if incomplete:
        diag={'complete':False,'productionEstimateId':a.production_id,'reason':'resource_quantity_build_incomplete','sources':incomplete}
        Path(a.output).write_text(json.dumps(diag,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(diag,ensure_ascii=False)); return 2
    agg={}
    for b in builds:
        for m in b.get('materials',[]):
            if m.get('status')!='DERIVED' or m.get('quantity') is None: continue
            key=(m['resourceId'],m['unit'],m['costResponsibility'])
            agg[key]=agg.get(key,0.0)+float(m['quantity'])
    materials=[{'resourceId':k[0],'quantity':v,'unit':k[1],'costResponsibility':k[2]} for k,v in sorted(agg.items())]
    out={'productionEstimateId':a.production_id,
         'sourceResourceBuildIds':[x['resourceBuildId'] for x in builds],
         'materials':materials,'equipment':[],'logistics':[],'directCosts':[],
         'includeOverhead':not a.no_overhead}
    Path(a.output).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print('PRODUCTION_REQUEST_OK',len(builds),len(materials)); return 0

if __name__=='__main__': sys.exit(main())
