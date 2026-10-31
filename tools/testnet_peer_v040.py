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
