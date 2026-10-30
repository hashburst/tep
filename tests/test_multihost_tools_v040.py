import os,sys,tempfile,unittest,subprocess,time,json,urllib.request
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
ROOT=Path(__file__).resolve().parents[1]
class MultiHostToolTests(unittest.TestCase):
 def test_peer_identity_persists_and_challenge_verifies(self):
  with tempfile.TemporaryDirectory() as d:
   port=47991
   p=subprocess.Popen([sys.executable,str(ROOT/"tools/testnet_peer_v040.py"),"--port",str(port),"--state",d])
   try:
    for _ in range(40):
     try:
      with urllib.request.urlopen(f"http://127.0.0.1:{port}/health",timeout=.2) as r:h=json.load(r);break
     except Exception:time.sleep(.05)
    else:self.fail("peer did not start")
    c=bytes.fromhex("55"*32);req=urllib.request.Request(f"http://127.0.0.1:{port}/challenge",data=json.dumps({"challenge":c.hex()}).encode(),headers={"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(req,timeout=1) as r:o=json.load(r)
    nid=bytes.fromhex(o["node_id"]);pk=bytes.fromhex(o["public_key"])
    Ed25519PublicKey.from_public_bytes(pk).verify(bytes.fromhex(o["signature"]),b"HB-TEP-TESTNET-CHALLENGE-v1\x00"+nid+c)
    first=o["node_id"]
   finally:p.terminate();p.wait(timeout=3)
   p2=subprocess.Popen([sys.executable,str(ROOT/"tools/testnet_peer_v040.py"),"--port",str(port),"--state",d])
   try:
    for _ in range(40):
     try:
      with urllib.request.urlopen(f"http://127.0.0.1:{port}/health",timeout=.2) as r:h2=json.load(r);break
     except Exception:time.sleep(.05)
    else:self.fail("peer did not restart")
    self.assertEqual(first,h2["node_id"])
   finally:p2.terminate();p2.wait(timeout=3)
if __name__=="__main__":unittest.main(verbosity=2)
