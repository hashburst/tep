"""G6 operational recovery primitives: verified backup/restore and hash-chained audit."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import json,os,shutil,tarfile,tempfile,time

CRITICAL=("testnet-ed25519.key","production-genesis.json","finalized-checkpoint.bin","testnet-ledger.jsonl","anti-equivocation-vote-lock.json","enrollment-registry.json","governance-registry.json")
SCHEMA="hb-tep-ops-backup-v1"
def _h(b):return sha256(b).hexdigest()
def _canon(o):return json.dumps(o,sort_keys=True,separators=(",",":")).encode()
def create_backup(state_dir,out_path):
    state=Path(state_dir);out=Path(out_path);rows=[]
    for name in CRITICAL:
        p=state/name
        if p.is_file():
            b=p.read_bytes();rows.append({"path":name,"size":len(b),"sha256":_h(b)})
    if not any(x["path"]=="testnet-ed25519.key" for x in rows):raise ValueError("identity missing")
    manifest={"schema":SCHEMA,"files":rows}
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);(root/"manifest.json").write_bytes(_canon(manifest))
        for x in rows:shutil.copyfile(state/x["path"],root/x["path"])
        with tarfile.open(out,"w:gz",format=tarfile.PAX_FORMAT) as t:
            for p in sorted(root.iterdir()):
                info=t.gettarinfo(str(p),arcname=p.name);info.uid=info.gid=0;info.uname=info.gname="";info.mtime=0
                with p.open("rb") as h:t.addfile(info,h)
    return _h(out.read_bytes()),manifest
def verify_backup(path):
    with tempfile.TemporaryDirectory() as d:
        with tarfile.open(path,"r:gz") as t:
            members=t.getmembers()
            for m in members:
                if not m.isfile() or "/" in m.name or m.name in ("",".",".."):raise ValueError("unsafe backup member")
            t.extractall(d,filter="data")
        root=Path(d);m=json.loads((root/"manifest.json").read_text())
        if m.get("schema")!=SCHEMA:raise ValueError("invalid backup schema")
        expected={"manifest.json"}|{x["path"] for x in m["files"]}
        if {p.name for p in root.iterdir()}!=expected:raise ValueError("unexpected backup content")
        for x in m["files"]:
            p=root/x["path"];b=p.read_bytes()
            if len(b)!=x["size"] or _h(b)!=x["sha256"]:raise ValueError("backup integrity failure")
        return m
def restore_backup(path,target_dir):
    m=verify_backup(path);target=Path(target_dir);target.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix=".hb-restore-",dir=target.parent))
    try:
        with tarfile.open(path,"r:gz") as t:t.extractall(stage,filter="data")
        (stage/"manifest.json").unlink()
        if target.exists():raise ValueError("restore target must be empty/nonexistent")
        os.replace(stage,target)
    finally:
        if stage.exists():shutil.rmtree(stage)
    return m
class AuditLog:
    def __init__(self,path):self.path=Path(path)
    def append(self,event,details):
        prev="0"*64;seq=1
        if self.path.exists() and self.path.stat().st_size:
            last=json.loads(self.path.read_text().splitlines()[-1]);prev=last["entry_hash"];seq=last["seq"]+1
        body={"seq":seq,"ts_ns":time.time_ns(),"event":event,"details":details,"previous_hash":prev}
        body["entry_hash"]=_h(_canon(body))
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open("a") as f:f.write(json.dumps(body,sort_keys=True,separators=(",",":"))+"\n");f.flush();os.fsync(f.fileno())
        return body["entry_hash"]
    def verify(self):
        prev="0"*64;seq=1
        if not self.path.exists():return True
        for line in self.path.read_text().splitlines():
            x=json.loads(line);h=x.pop("entry_hash")
            if x["seq"]!=seq or x["previous_hash"]!=prev or _h(_canon(x))!=h:return False
            prev=h;seq+=1
        return True

# G6 operations protocol revision: 1
