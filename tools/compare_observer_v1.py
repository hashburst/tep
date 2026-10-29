#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
SCHEMA='hashburst-tep-observer-conformance-result-v1'
def sums(p):
 out={}
 for line in p.read_text(encoding='utf-8').splitlines():
  m=re.fullmatch(r'([0-9a-f]{64})  tep/(.+)',line.strip())
  if m:out[m.group(2)]=m.group(1)
 return out
def main():
 a=argparse.ArgumentParser();a.add_argument('report');a.add_argument('--baseline',default='legacy/node-installer-v2.2.0/SHA256SUMS');q=a.parse_args();r=json.loads(Path(q.report).read_text(encoding='utf-8'));base=sums(Path(q.baseline));obs={}
 for root in r.get('roots',[]):
  for m in root.get('modules',[]):obs.setdefault(m['name'],[]).append({'root':root['root'],'sha256':m['sha256'],'size':m['size']})
 rows=[]
 for name,want in sorted(base.items()):
  got=obs.get(name,[]);status='IDENTICAL' if any(x['sha256']==want for x in got) else ('DIFFERENT' if got else 'NOT OBSERVABLE');rows.append({'component':'tep/'+name,'legacy_sha256':want,'observed':got,'status':status})
 d={'schema':SCHEMA,'observer_schema':r.get('schema'),'classification_rule':'IDENTICAL is exact SHA-256; DIFFERENT is observed but non-identical; NOT OBSERVABLE is absent; COMPATIBLE requires separate behavioral interoperability testing and is never inferred here.','components':rows};print(json.dumps(d,sort_keys=True,indent=2))
if __name__=='__main__':main()
