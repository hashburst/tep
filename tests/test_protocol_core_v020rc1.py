import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from hashburst_tep.encoding import dumps,EncodingError
from hashburst_tep.genesis import Genesis
from hashburst_tep.ledger import poh_input,next_count
from hashburst_tep.records import RecordCore,body_root
from hashburst_tep.checkpoint import Checkpoint,atomic_write

H0="25b00f0b763b0742f15b95a383076b788ebb11f1f4baa47ec27dec8aa1fa228f"
A1="52bc9c692f97801337aad2db178ecff8120d28715a1ac5078c7c6129fc23925f"
RID="73f2544590d67864e4eae71dd21f4a99bb20d131ab478abe80eff19a7a49d361"
BROOT="dd8daa2efa4cb17d0aa6f31cfa2f8d70bfc7e513024514a98a4241b18c455a7b"
GENESIS_CBOR="850158200000000000000000000000000000000000000000000000000000000000000000010158201111111111111111111111111111111111111111111111111111111111111111"
RECORD_CBOR="8a0158203333333333333333333333333333333333333333333333333333333333333333582044444444444444444444444444444444444444444444444444444444444444445820555555555555555555555555555555555555555555555555555555555555555507582022222222222222222222222222222222222222222222222222222222222222220958206666666666666666666666666666666666666666666666666666666666666666f658207777777777777777777777777777777777777777777777777777777777777777"

class Conformance(unittest.TestCase):
 def setUp(self):
  self.net=bytes(32);self.vp=bytes.fromhex("11"*32);self.prev=bytes.fromhex("22"*32)
 def test_tv001_genesis(self):
  g=Genesis(self.net,1,1,self.vp)
  self.assertEqual(g.encode().hex(),GENESIS_CBOR);self.assertEqual(g.h0().hex(),H0)
 def test_tv002_poh_input(self):
  self.assertEqual(poh_input(self.net,1,bytes.fromhex(H0),self.prev,self.vp).hex(),A1)
 def test_tv003_record(self):
  r=RecordCore(bytes.fromhex("33"*32),bytes.fromhex("44"*32),bytes.fromhex("55"*32),7,self.prev,9,bytes.fromhex("66"*32),None,bytes.fromhex("77"*32))
  self.assertEqual(r.encode().hex(),RECORD_CBOR);self.assertEqual(r.record_id().hex(),RID)
 def test_tv004_body(self):self.assertEqual(body_root([bytes.fromhex(RID)]).hex(),BROOT)
 def test_count(self):
  self.assertEqual(next_count(0),1)
  with self.assertRaises(ValueError):next_count(2**64-1)
 def test_encoder_rejects_float_bool_and_map(self):
  for x in (1.0,True,{}):
   with self.assertRaises(EncodingError):dumps(x)
 def test_fixed_identifier_length(self):
  with self.assertRaises(ValueError):Genesis(b"x",1,1,self.vp).h0()
 def test_checkpoint_atomic_write(self):
  cp=Checkpoint(self.net,1,bytes.fromhex(H0),self.prev,self.vp,1,bytes.fromhex("88"*32))
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"checkpoint.cbor";atomic_write(p,cp.encode());self.assertEqual(p.read_bytes(),cp.encode())

if __name__=="__main__":unittest.main(verbosity=2)
