#!/usr/bin/env python3
import argparse,json,secrets,urllib.request
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ap=argparse.ArgumentParser();ap.add_argument("urls",nargs="+");a=ap.parse_args()
seen=set();rows=[]
for u in a.urls:
 with urllib.request.urlopen(u.rstrip("/")+"/health",timeout=5) as r:h=json.load(r)
 nid=bytes.fromhex(h["node_id"]);pk=bytes.fromhex(h["public_key"])
 if nid in seen:raise SystemExit("duplicate node identity")
 seen.add(nid);c=secrets.token_bytes(32);data=json.dumps({"challenge":c.hex()}).encode()
 req=urllib.request.Request(u.rstrip("/")+"/challenge",data=data,headers={"Content-Type":"application/json"},method="POST")
 with urllib.request.urlopen(req,timeout=5) as r:o=json.load(r)
 if o["node_id"]!=nid.hex() or o["public_key"]!=pk.hex() or o["challenge"]!=c.hex():raise SystemExit("challenge binding mismatch")
 Ed25519PublicKey.from_public_bytes(pk).verify(bytes.fromhex(o["signature"]),b"HB-TEP-TESTNET-CHALLENGE-v1\x00"+nid+c)
 rows.append({"url":u,"node_id":nid.hex(),"authenticated":True})
print(json.dumps({"profile":"v0.4.0-testnet","nodes":rows},indent=2))
