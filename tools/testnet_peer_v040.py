"""Minimal authenticated testnet peer service for multi-host v0.4.0 gates.

This service intentionally exposes only health, identity and signed challenge
endpoints. It never loads production TEP state.
"""
import argparse,base64,json,os
from hashlib import sha3_256
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PrivateFormat,PublicFormat,NoEncryption

def _load_or_create(state):
 p=Path(state);p.mkdir(parents=True,exist_ok=True);k=p/"testnet-ed25519.key"
 if k.exists(): raw=k.read_bytes()
 else:
  raw=Ed25519PrivateKey.generate().private_bytes(Encoding.Raw,PrivateFormat.Raw,NoEncryption());k.write_bytes(raw);os.chmod(k,0o600)
 sk=Ed25519PrivateKey.from_private_bytes(raw);pk=sk.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
 return sk,pk,sha3_256(b"HB-TEP-TESTNET-NODE-v1\x00"+pk).digest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--listen",default="127.0.0.1");ap.add_argument("--port",type=int,default=47840);ap.add_argument("--state",required=True);a=ap.parse_args()
 sk,pk,nid=_load_or_create(a.state)
 class H(BaseHTTPRequestHandler):
  def _send(self,obj,status=200):
   b=json.dumps(obj,separators=(",",":")).encode();self.send_response(status);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
  def do_GET(self):
   if self.path=="/health":return self._send({"ok":True,"profile":"v0.4.0-testnet","node_id":nid.hex(),"public_key":pk.hex()})
   return self._send({"error":"not found"},404)
  def do_POST(self):
   if self.path!="/challenge":return self._send({"error":"not found"},404)
   try:
    n=int(self.headers.get("Content-Length","0"));o=json.loads(self.rfile.read(n));challenge=bytes.fromhex(o["challenge"])
    if len(challenge)!=32:raise ValueError()
   except Exception:return self._send({"error":"invalid challenge"},400)
   msg=b"HB-TEP-TESTNET-CHALLENGE-v1\x00"+nid+challenge
   return self._send({"node_id":nid.hex(),"public_key":pk.hex(),"challenge":challenge.hex(),"signature":sk.sign(msg).hex()})
  def log_message(self,fmt,*args):pass
 ThreadingHTTPServer((a.listen,a.port),H).serve_forever()
if __name__=="__main__":main()
