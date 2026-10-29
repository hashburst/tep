#!/usr/bin/env python3
import json,tempfile,subprocess,sys
from pathlib import Path
with tempfile.TemporaryDirectory() as td:
 p=Path(td);(p/'tep').mkdir();(p/'tep'/'hb_tep.py').write_text('x',encoding='utf-8');r=subprocess.run([sys.executable,'tools/tep_observer_probe_v1.py','--root',str(p)],capture_output=True,text=True,check=True);d=json.loads(r.stdout);assert d['read_only'] is True;assert all(v is False for v in d['privacy'].values());assert d['roots'][0]['modules'][0]['name']=='hb_tep.py'
print('observer probe smoke test: PASS')
