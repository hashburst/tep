"""Minimal authenticated testnet peer service for multi-host v0.4.0 gates."""
import argparse,json,os
from hashlib import sha3_256
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PrivateFormat,PublicFormat,NoEncryption

NODE_DOMAIN=b"HB-TEP-TESTNET-NODE-v1\x00"
CHALLENGE_DOMAIN=b"HB-TEP-TESTNET-CHALLENGE-v1\x00"
LEDGER_DOMAIN=b"HB-TEP-TESTNET-LEDGER-v1\x00"
LEDGER_ACK_DOMAIN=b"HB-TEP-TESTNET-LEDGER-ACK-v1\x00"
FINALITY_VOTE_DOMAIN=b"HB-TEP-FINALITY-VOTE-v1\x00"
FINALITY_QC_DOMAIN=b"HB-TEP-FINALITY-QC-v1\x00"
VALIDATOR_SET_DOMAIN=b"HB-TEP-VALIDATOR-SET-v1\x00"
CHECKPOINT_DOMAIN=b"HB-TEP-CHECKPOINT-v1\x00"
ENROLLMENT_CHALLENGE_DOMAIN=b"HB-TEP-ENROLLMENT-CHALLENGE-v1\x00"\nVALIDATOR_GOVERNANCE_VOTE_DOMAIN=b"HB-TEP-VALIDATOR-GOVERNANCE-VOTE-v1\\x00"

def _cbor(v):
 if isinstance(v,int):
  if v<24:return bytes([v])
  if v<256:return b"\x18"+bytes([v])
  if v<65536:return b"\x19"+v.to_bytes(2,"big")
  if v<2**32:return b"\x1a"+v.to_bytes(4,"big")
  return b"\x1b"+v.to_bytes(8,"big")
 if isinstance(v,bytes):
  n=len(v);h=_cbor(n);return bytes([h[0]|0x40])+h[1:]+v
 if isinstance(v,(list,tuple)):
  n=len(v);h=_cbor(n);return bytes([h[0]|0x80])+h[1:]+b"".join(_cbor(x) for x in v)
 raise ValueError("unsupported canonical value")

def _finality_message(version,vs_digest,network_id,count,block_id):
 return FINALITY_VOTE_DOMAIN+_cbor([1,version,vs_digest,network_id,count,block_id])
def _vs_digest(version,validators):
 vals=sorted(validators,key=lambda x:x[0])
 return sha3_256(VALIDATOR_SET_DOMAIN+_cbor([1,version,[[i,k] for i,k in vals]])).digest()
def _qc_digest(version,vs_digest,network_id,count,block_id,votes):
 votes=sorted(votes,key=lambda x:x[0])
 return sha3_256(FINALITY_QC_DOMAIN+_cbor([1,version,vs_digest,network_id,count,block_id,[[i,s] for i,s in votes]])).digest()
def _checkpoint_bytes(network_id,count,h,block_id,vdf_params_hash,version,qcd):
 return _cbor([1,network_id,count,h,block_id,vdf_params_hash,version,qcd])
def _persist_checkpoint(state,payload):
 p=Path(state)/"finalized-checkpoint.bin";tmp=p.with_suffix(".tmp")
 with tmp.open("wb") as f:f.write(payload);f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
 return sha3_256(CHECKPOINT_DOMAIN+payload).digest()

def _load_or_create(state):
 p=Path(state);p.mkdir(parents=True,exist_ok=True);k=p/"testnet-ed25519.key"
 if k.exists(): raw=k.read_bytes()
 else:
  raw=Ed25519PrivateKey.generate().private_bytes(Encoding.Raw,PrivateFormat.Raw,NoEncryption());k.write_bytes(raw);os.chmod(k,0o600)
 sk=Ed25519PrivateKey.from_private_bytes(raw);pk=sk.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
 return sk,pk,sha3_256(NODE_DOMAIN+pk).digest()

def _ledger_path(state): return Path(state)/"testnet-ledger.jsonl"
def _ledger_rows(state):
 p=_ledger_path(state)
 if not p.exists(): return []
 rows=[]
 for line in p.read_text().splitlines():
  if line.strip(): rows.append(json.loads(line))
 return rows
def _entry_id(index,previous,payload):
 return sha3_256(LEDGER_DOMAIN+index.to_bytes(8,"big")+previous+payload).digest()
def _append(state,index,previous,payload):
 rows=_ledger_rows(state); expected_index=len(rows)+1
 expected_prev=bytes.fromhex(rows[-1]["entry_id"]) if rows else bytes(32)
 if index!=expected_index or previous!=expected_prev: raise ValueError("ledger continuity mismatch")
 eid=_entry_id(index,previous,payload)
 row={"index":index,"previous_entry_id":previous.hex(),"payload":payload.hex(),"entry_id":eid.hex()}
 p=_ledger_path(state);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("a") as f:
  f.write(json.dumps(row,separators=(",",":"))+"\n");f.flush();os.fsync(f.fileno())
 return row

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--listen",default="127.0.0.1");ap.add_argument("--port",type=int,default=47840);ap.add_argument("--state",required=True);a=ap.parse_args()
 sk,pk,nid=_load_or_create(a.state)
 class H(BaseHTTPRequestHandler):
  def _send(self,obj,status=200):
   b=json.dumps(obj,separators=(",",":")).encode();self.send_response(status);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
  def do_GET(self):
   if self.path=="/health":return self._send({"ok":True,"profile":"v0.4.0-testnet","node_id":nid.hex(),"public_key":pk.hex()})
   if self.path=="/finality/head":
    p=Path(a.state)/"finalized-checkpoint.bin"
    if not p.exists():return self._send({"node_id":nid.hex(),"finalized":False})
    payload=p.read_bytes();cid=sha3_256(CHECKPOINT_DOMAIN+payload).digest()
    return self._send({"node_id":nid.hex(),"finalized":True,"checkpoint_id":cid.hex()})
   if self.path=="/ledger/head":
    rows=_ledger_rows(a.state);head=rows[-1] if rows else None
    return self._send({"node_id":nid.hex(),"height":len(rows),"head":head})
   return self._send({"error":"not found"},404)
  def do_POST(self):
   try:
    n=int(self.headers.get("Content-Length","0"));o=json.loads(self.rfile.read(n))
   except Exception:return self._send({"error":"invalid json"},400)
   if self.path=="/challenge":
    try:
     challenge=bytes.fromhex(o["challenge"])
     if len(challenge)!=32:raise ValueError()
    except Exception:return self._send({"error":"invalid challenge"},400)
    msg=CHALLENGE_DOMAIN+nid+challenge
    return self._send({"node_id":nid.hex(),"public_key":pk.hex(),"challenge":challenge.hex(),"signature":sk.sign(msg).hex()})
   if self.path=="/enrollment/challenge":
    try:
     net=bytes.fromhex(o["network_id"]);challenge=bytes.fromhex(o["challenge"])
     if len(net)!=32 or len(challenge)!=32:raise ValueError()
     msg=ENROLLMENT_CHALLENGE_DOMAIN+_cbor([1,net,nid,challenge])
     return self._send({"node_id":nid.hex(),"public_key":pk.hex(),"network_id":net.hex(),"challenge":challenge.hex(),"signature":sk.sign(msg).hex()})
    except Exception:return self._send({"error":"invalid enrollment challenge"},400)
   if self.path=="/governance/vote":
    try:
     set_version=int(o["validator_set_version"]);set_digest=bytes.fromhex(o["validator_set_digest"]);proposal_digest=bytes.fromhex(o["proposal_digest"])
     if set_version<0 or len(set_digest)!=32 or len(proposal_digest)!=32:raise ValueError()
     from hashburst_tep.encoding import dumps
     from hashburst_tep.domains import VALIDATOR_GOVERNANCE_VOTE_DOMAIN
     msg=VALIDATOR_GOVERNANCE_VOTE_DOMAIN+dumps([1,set_version,set_digest,proposal_digest])
     return self._send({"node_id":nid.hex(),"validator_id":nid.hex(),"public_key":pk.hex(),"signature":sk.sign(msg).hex()})
    except Exception:return self._send({"error":"invalid governance vote request"},400)
   if self.path=="/finality/vote":
    try:
     version=int(o["validator_set_version"]);vsd=bytes.fromhex(o["validator_set_digest"]);net=bytes.fromhex(o["network_id"]);count=int(o["count"]);bid=bytes.fromhex(o["block_id"])
     if any(len(x)!=32 for x in (vsd,net,bid)) or version<0 or count<0:raise ValueError()
     msg=_finality_message(version,vsd,net,count,bid)
     return self._send({"node_id":nid.hex(),"public_key":pk.hex(),"validator_id":nid.hex(),"signature":sk.sign(msg).hex()})
    except Exception:return self._send({"error":"invalid finality vote request"},400)
   if self.path=="/finality/catchup":
    try:
     version=int(o["validator_set_version"]);net=bytes.fromhex(o["network_id"]);count=int(o["count"]);bid=bytes.fromhex(o["block_id"]);h=bytes.fromhex(o["h"]);vph=bytes.fromhex(o["vdf_params_hash"])
     validators=[(bytes.fromhex(x["validator_id"]),bytes.fromhex(x["public_key"])) for x in o["validators"]]
     votes=[(bytes.fromhex(x["validator_id"]),bytes.fromhex(x["signature"])) for x in o["votes"]]
     if len(validators)!=4 or len({i for i,k in validators})!=4 or len({k for i,k in validators})!=4:raise ValueError("invalid validator set")
     vsd=_vs_digest(version,validators);msg=_finality_message(version,vsd,net,count,bid);members=dict(validators);seen=set()
     from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
     for vid,sig in votes:
      if vid in seen or vid not in members:raise ValueError("invalid vote")
      seen.add(vid);Ed25519PublicKey.from_public_bytes(members[vid]).verify(sig,msg)
     threshold=(2*len(validators))//3+1
     if len(seen)<threshold:raise ValueError("insufficient quorum")
     qcd=_qc_digest(version,vsd,net,count,bid,votes);payload=_checkpoint_bytes(net,count,h,bid,vph,version,qcd);cid=_persist_checkpoint(a.state,payload)
     expected=o.get("checkpoint_id")
     if expected and cid.hex()!=expected:raise ValueError("checkpoint mismatch")
     return self._send({"node_id":nid.hex(),"checkpoint_id":cid.hex(),"qc_digest":qcd.hex(),"votes":len(seen),"threshold":threshold,"caught_up":True})
    except ValueError as e:return self._send({"error":str(e)},409)
    except Exception:return self._send({"error":"invalid finality catchup"},400)
   if self.path=="/finality/commit":
    try:
     version=int(o["validator_set_version"]);net=bytes.fromhex(o["network_id"]);count=int(o["count"]);bid=bytes.fromhex(o["block_id"]);h=bytes.fromhex(o["h"]);vph=bytes.fromhex(o["vdf_params_hash"])
     validators=[(bytes.fromhex(x["validator_id"]),bytes.fromhex(x["public_key"])) for x in o["validators"]]
     votes=[(bytes.fromhex(x["validator_id"]),bytes.fromhex(x["signature"])) for x in o["votes"]]
     if len(validators)!=4 or len({i for i,k in validators})!=4 or len({k for i,k in validators})!=4:raise ValueError("invalid validator set")
     if any(len(x)!=32 for x in (net,bid,h,vph)) or any(len(i)!=32 or len(k)!=32 for i,k in validators):raise ValueError("invalid field")
     vsd=_vs_digest(version,validators);msg=_finality_message(version,vsd,net,count,bid);members=dict(validators);seen=set()
     from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
     valid=0
     for vid,sig in votes:
      if vid in seen or vid not in members:raise ValueError("invalid vote")
      seen.add(vid);Ed25519PublicKey.from_public_bytes(members[vid]).verify(sig,msg);valid+=1
     threshold=(2*len(validators))//3+1
     if valid<threshold:raise ValueError("insufficient quorum")
     qcd=_qc_digest(version,vsd,net,count,bid,votes);payload=_checkpoint_bytes(net,count,h,bid,vph,version,qcd);cid=_persist_checkpoint(a.state,payload)
     return self._send({"node_id":nid.hex(),"checkpoint_id":cid.hex(),"qc_digest":qcd.hex(),"votes":valid,"threshold":threshold})
    except ValueError as e:return self._send({"error":str(e)},409)
    except Exception:return self._send({"error":"invalid finality commit"},400)
   if self.path=="/ledger/append":
    try:
     index=int(o["index"]);previous=bytes.fromhex(o["previous_entry_id"]);payload=bytes.fromhex(o["payload"])
     if len(previous)!=32 or not payload or len(payload)>65536:raise ValueError()
     row=_append(a.state,index,previous,payload);eid=bytes.fromhex(row["entry_id"])
     sig=sk.sign(LEDGER_ACK_DOMAIN+nid+eid)
     return self._send({"node_id":nid.hex(),"public_key":pk.hex(),"entry":row,"signature":sig.hex()})
    except ValueError as e:return self._send({"error":str(e)},409)
    except Exception:return self._send({"error":"invalid ledger append"},400)
   return self._send({"error":"not found"},404)
  def log_message(self,fmt,*args):pass
 ThreadingHTTPServer((a.listen,a.port),H).serve_forever()
if __name__=="__main__":main()
