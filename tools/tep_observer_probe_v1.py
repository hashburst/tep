#!/usr/bin/env python3
import argparse,hashlib,json,platform,re,socket,subprocess,sys
from pathlib import Path
SCHEMA='hashburst-tep-observer-conformance-v1'
ROOTS=('/opt/hashburst-tep','/opt/node-installer-v220-blockchainapi')
MODULES=('__init__.py','hb_tep.py','hb_tep_app.py','hb_tep_client.py','hb_tep_ha_service.py','hb_tep_master_service.py','hb_tep_relay.py','hb_tep_runtime.py','hb_tep_runtime_ha.py','hb_tep_runtime_v220.py','hb_tep_services.py','hb_tep_wire.py')
DENY=('.key','.pem','.env','.db','.sqlite','.log','peers.json','anti-replay','identity')
def run(c):
 try:
  p=subprocess.run(c,text=True,capture_output=True,timeout=8,check=False,env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LC_ALL':'C'}); return p.stdout.strip()
 except Exception:return ''
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def modules(root):
 out=[]; d=root/'tep'
 if not d.is_dir():return out
 for n in MODULES:
  p=d/n
  if p.is_file() and not any(x in str(p).lower() for x in DENY):
   out.append({'name':n,'path':str(p),'size':p.stat().st_size,'sha256':digest(p)})
 return out
def processes():
 out=[]
 for line in run(['ps','-eo','pid=,user=,args=']).splitlines():
  if re.search(r'(^|[ /])tep[./ ]|hb_tep',line,re.I):
   x=line.strip().split(None,2)
   if len(x)==3:out.append({'pid':x[0],'user':x[1],'args':x[2]})
 return out
def listeners():
 return [x for x in run(['ss','-lntupH']).splitlines() if any((':'+p) in x for p in ('47777','47778','47780','47781'))]
def units():
 names=[]
 for line in run(['systemctl','list-units','--type=service','--all','--no-legend','--no-pager']).splitlines():
  if re.search(r'hashburst|tep',line,re.I) and line.split():
   n=line.split()[0]
   if n.endswith('.service') and re.fullmatch(r'[A-Za-z0-9_.@-]+',n):names.append(n)
 out=[]
 for n in sorted(set(names)):
  s=run(['systemctl','show',n,'--no-pager','--property=Id,LoadState,ActiveState,SubState,FragmentPath,ExecStart'])
  out.append({'unit':n,'properties':s.splitlines()})
 return out
def main():
 a=argparse.ArgumentParser();a.add_argument('--root',action='append',default=[]);a.add_argument('--output');q=a.parse_args();roots=[Path(x).resolve() for x in (q.root or ROOTS)]
 d={'schema':SCHEMA,'probe_version':'1.0.0','read_only':True,'privacy':{'private_keys_read':False,'env_files_read':False,'databases_read':False,'peer_state_read':False,'process_environ_read':False},'host':{'hostname':socket.gethostname(),'platform':platform.platform(),'python':sys.version.split()[0]},'roots':[{'root':str(r),'exists':r.exists(),'modules':modules(r)} for r in roots],'processes':processes(),'listeners':listeners(),'systemd':units()}
 raw=json.dumps(d,sort_keys=True,indent=2)+'\n'
 if q.output:Path(q.output).write_text(raw,encoding='utf-8')
 else:sys.stdout.write(raw)
if __name__=='__main__':main()
