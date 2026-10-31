#!/usr/bin/env python3
import hashlib,json,urllib.request,urllib.error
def get(path):
 return json.load(urllib.request.urlopen("http://127.0.0.1:47840"+path,timeout=3))
def post(path,obj):
 r=urllib.request.Request("http://127.0.0.1:47840"+path,data=json.dumps(obj).encode(),headers={"Content-Type":"application/json"})
 return json.load(urllib.request.urlopen(r,timeout=3))
s=get("/operations/snapshot")
assert s["schema"]=="hb-tep-ops-snapshot-v1"
assert all(x["path"]!="testnet-ed25519.key" for x in s["files"])
for x in s["files"]:
 b=bytes.fromhex(x["content_hex"]);assert len(b)==x["size"] and hashlib.sha256(b).hexdigest()==x["sha256"]
out=post("/operations/restore-sandbox",s);assert out["restored"]
bad=json.loads(json.dumps(s))
if bad["files"]:
 x=bad["files"][0];raw=bytearray.fromhex(x["content_hex"]);raw[0]^=1;x["content_hex"]=raw.hex()
try:post("/operations/restore-sandbox",bad);raise AssertionError("corrupt snapshot accepted")
except urllib.error.HTTPError as e:assert e.code==409
json.dump(s,open("snapshot.json","w"))
print("G6_DR_RESTORE_OK sandbox_restore=1 corrupt_rejected=1 private_key_exported=0")
