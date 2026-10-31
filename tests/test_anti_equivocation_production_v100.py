import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from hashburst_tep.anti_equivocation import PersistentVoteLock,VoteLockKey

class AntiEquivocationProductionTests(unittest.TestCase):
 def setUp(self):self.key=VoteLockKey(b"F"*32,7,42,b"V"*32);self.a=b"A"*32;self.b=b"B"*32
 def test_first_vote_locks_and_same_vote_is_idempotent(self):
  with tempfile.TemporaryDirectory() as d:
   r=PersistentVoteLock(Path(d)/"lock.json");self.assertEqual(r.authorize(self.key,self.a),"LOCKED");self.assertEqual(r.authorize(self.key,self.a),"IDEMPOTENT")
 def test_conflicting_vote_rejected_permanently_after_restart(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"lock.json";r=PersistentVoteLock(p);r.authorize(self.key,self.a)
   with self.assertRaisesRegex(ValueError,"equivocation"):r.authorize(self.key,self.b)
   r2=PersistentVoteLock(p);self.assertEqual(r2.locked_digest(self.key),self.a)
   with self.assertRaisesRegex(ValueError,"equivocation"):r2.authorize(self.key,self.b)
   self.assertEqual(r2.authorize(self.key,self.a),"IDEMPOTENT")
 def test_lock_scope_includes_count_version_validator_and_federation(self):
  with tempfile.TemporaryDirectory() as d:
   r=PersistentVoteLock(Path(d)/"lock.json");r.authorize(self.key,self.a)
   for k in (VoteLockKey(b"G"*32,7,42,b"V"*32),VoteLockKey(b"F"*32,8,42,b"V"*32),VoteLockKey(b"F"*32,7,43,b"V"*32),VoteLockKey(b"F"*32,7,42,b"W"*32)):
    self.assertEqual(r.authorize(k,self.b),"LOCKED")
 def test_corrupt_schema_fail_closed(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"lock.json";p.write_text('{"schema":"wrong","locks":{}}')
   with self.assertRaises(ValueError):PersistentVoteLock(p)
if __name__=="__main__":unittest.main(verbosity=2)
