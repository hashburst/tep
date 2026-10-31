import tempfile,unittest
from pathlib import Path
from hashburst_tep.operations import *
class OpsTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.r=Path(self.t.name);self.s=self.r/"state";self.s.mkdir()
  (self.s/"testnet-ed25519.key").write_bytes(b"K"*32);(self.s/"production-genesis.json").write_text('{"g":1}');(self.s/"anti-equivocation-vote-lock.json").write_text('{"schema":"hb-vote-lock-v1","locks":{}}')
 def tearDown(self):self.t.cleanup()
 def test_backup_restore_identity_and_state(self):
  b=self.r/"b.tgz";_,m=create_backup(self.s,b);verify_backup(b);restore_backup(b,self.r/"restored")
  for x in m["files"]:self.assertEqual((self.s/x["path"]).read_bytes(),(self.r/"restored"/x["path"]).read_bytes())
 def test_corrupt_backup_rejected(self):
  b=self.r/"b.tgz";create_backup(self.s,b);z=bytearray(b.read_bytes());z[len(z)//2]^=1;b.write_bytes(z)
  with self.assertRaises(Exception):verify_backup(b)
 def test_restore_refuses_overwrite(self):
  b=self.r/"b.tgz";create_backup(self.s,b)
  with self.assertRaises(ValueError):restore_backup(b,self.s)
 def test_audit_chain_detects_tamper(self):
  p=self.r/"audit.jsonl";a=AuditLog(p);a.append("backup",{"ok":1});a.append("restore",{"ok":1});self.assertTrue(a.verify());p.write_text(p.read_text().replace('"ok":1','"ok":0',1));self.assertFalse(a.verify())
if __name__=="__main__":unittest.main()
