import argparse, csv, json, re, statistics
from pathlib import Path
def num(v):
    if v is None or str(v).strip()=='': return None
    try: return float(str(v).strip().replace(',','.'))
    except ValueError: return None
def quantile(values,q):
    a=sorted(values); n=len(a)
    if not n: return None
    if n==1: return a[0]
    pos=(n-1)*q; lo=int(pos); hi=min(lo+1,n-1); f=pos-lo
    return a[lo]*(1-f)+a[hi]*f
def parse_groups(text,crew):
    out={}
    for part in (text or '').split('|'):
        m=re.match(r'\s*([^:]+):\s*([0-9.,]+)с\s*$',part)
        if m:
            sec=num(m.group(2)) or 0; out[m.group(1).strip()]=sec*crew/60
    return out
def main():
    ap=argparse.ArgumentParser(description='VIVUM package benchmark analyzer; never auto-publishes norms')
    ap.add_argument('csv_file'); ap.add_argument('--output',required=True)
    a=ap.parse_args(); rows=[]; rejected=[]
    with open(a.csv_file,'r',encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f,delimiter=';'):
            mid=(r.get('ID замера') or '').strip(); code=(r.get('Код пакета') or '').strip()
            crew=num(r.get('Размер бригады, чел.')); qty=num(r.get('Объём 1'))
            work_pm=num(r.get('Работа чел·мин')); loss_pm=num(r.get('Простой чел·мин')) or 0
            reasons=[]
            if not mid: reasons.append('measurement_id_missing')
            if not code: reasons.append('package_code_missing')
            if not crew or crew<1: reasons.append('crew_size_invalid')
            if not qty or qty<=0: reasons.append('primary_quantity_invalid')
            if work_pm is None or work_pm<=0: reasons.append('productive_person_min_invalid')
            if reasons: rejected.append({'measurementId':mid,'packageCode':code,'reasons':reasons}); continue
            rows.append({'measurementId':mid,'packageCode':code,'crewSize':crew,'primaryQty':qty,
                         'productivePersonMin':work_pm,'lossPersonMin':loss_pm,
                         'personMinPerPrimary':work_pm/qty,'lossRatio':loss_pm/(work_pm+loss_pm) if work_pm+loss_pm else 0,
                         'groups':parse_groups(r.get('Группы наблюдения',''),crew)})
    by={}
    for r in rows: by.setdefault(r['packageCode'],[]).append(r)
    summaries=[]
    for code,items in sorted(by.items()):
        vals=[x['personMinPerPrimary'] for x in items]; losses=[x['lossRatio'] for x in items]
        summaries.append({'workPackageCode':code,'sampleSize':len(items),'status':'CANDIDATE_REVIEW_REQUIRED',
                          'medianPersonMinPerPrimary':statistics.median(vals),'p25':quantile(vals,.25),'p75':quantile(vals,.75),
                          'min':min(vals),'max':max(vals),'medianLossRatio':statistics.median(losses),
                          'sourceMeasurementIds':[x['measurementId'] for x in items],
                          'normPublicationAllowed':False})
    group_by={}
    for r in rows:
        for g,pm in r['groups'].items(): group_by.setdefault((r['packageCode'],g),[]).append(pm/r['primaryQty'])
    groups=[{'workPackageCode':k[0],'observationGroupCode':k[1],'sampleSize':len(v),
             'medianPersonMinPerPrimary':statistics.median(v),'status':'BENCHMARK_ONLY','normPublicationAllowed':False}
            for k,v in sorted(group_by.items())]
    result={'schema_version':'1.0','analysisType':'PACKAGE_BENCHMARK_NOT_NORM','validStructuralRecords':len(rows),
            'rejectedStructuralRecords':rejected,'packageBenchmarks':summaries,'groupBenchmarks':groups}
    Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('valid',len(rows),'rejected',len(rejected),'packages',len(summaries),'groups',len(groups))
if __name__=='__main__': main()
