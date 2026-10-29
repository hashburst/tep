import os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from hashburst_tep.block import assemble_verified_block
from hashburst_tep.checkpoint import Checkpoint,atomic_write,decode_checkpoint
from hashburst_tep.encoding import EncodingError,loads
from hashburst_tep.genesis import Genesis
from hashburst_tep.ledger import poh_input
from hashburst_tep.poh import EvaluationWindow
from hashburst_tep.recovery import persist_finalized,load_finalized
from hashburst_tep.vdf import DeterministicTestVDF

class RecoveryTests(unittest.TestCase):
 def setUp(self):
  self.net=bytes(32);self.vp=bytes.fromhex("11"*32);self.g=Genesis(self.net,1,1,self.vp);self.genesis_id=bytes.fromhex("22"*32)
 def _block(self,count,previous_h,previous_id):
  a=poh_input(self.net,count,previous_h,previous_id,self.vp);w=EvaluationWindow(DeterministicTestVDF());w.start(a,count,8);c=w.evaluate_and_close();self.assertTrue(w.verify(c))
  return assemble_verified_block(count=count,previous_h=previous_h,previous_block_id=previous_id,challenge=a,result=c.result,vdf_suite=1,vdf_params_hash=self.vp,records=[])
 def test_checkpoint_roundtrip_and_integrity(self):
  b=self._block(1,self.g.h0(),self.genesis_id);cp=Checkpoint(self.net,1,b.h,b.block_id,self.vp,1,bytes.fromhex("88"*32))
  self.assertEqual(decode_checkpoint(cp.encode()),cp)
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"f.chk";persist_finalized(p,cp);self.assertEqual(load_finalized(p).checkpoint,cp)
   raw=bytearray(p.read_bytes());raw[-1]^=1;p.write_bytes(raw)
   with self.assertRaises(ValueError):load_finalized(p)
 def test_truncated_and_noncanonical_rejected(self):
  with self.assertRaises((ValueError,EncodingError)):decode_checkpoint(b"\x88\x01")
  with self.assertRaises(EncodingError):loads(b"\x18\x01")
 def test_failed_replace_preserves_previous_finalized_bytes(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"f.chk";old=b"previous-finalized-state";atomic_write(p,old)
   with patch("hashburst_tep.checkpoint.os.replace",side_effect=OSError("injected pre-rename failure")):
    with self.assertRaises(OSError):atomic_write(p,b"new-state")
   self.assertEqual(p.read_bytes(),old)
   self.assertEqual(list(Path(d).glob("f.chk.*")),[])
 def test_b0_b1_b2_recursive_link(self):
  b1=self._block(1,self.g.h0(),self.genesis_id);b2=self._block(2,b1.h,b1.block_id)
  self.assertEqual(b2.header[1],2);self.assertEqual(b2.header[2],b1.h);self.assertEqual(b2.header[3],b1.block_id);self.assertNotEqual(b2.h,b1.h);self.assertNotEqual(b2.block_id,b1.block_id)

if __name__=="__main__":unittest.main(verbosity=2)
