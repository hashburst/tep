import sys,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from hashburst_tep.vdf.adapter import VDFResult
from hashburst_tep.vdf.cg_weso import CGWesoV1

try:
 import chiavdf
except ImportError:
 chiavdf=None

@unittest.skipUnless(chiavdf is not None,"optional chiavdf package not installed")
class CGWesoTests(unittest.TestCase):
 def setUp(self):self.a=CGWesoV1();self.c=bytes.fromhex("a5"*32)
 def test_evaluate_verify(self):
  r=self.a.evaluate(self.c,64);self.assertEqual(len(r.output),100);self.assertEqual(len(r.proof),100);self.assertTrue(self.a.verify(self.c,r))
 def test_corrupt_output_rejected(self):
  r=self.a.evaluate(self.c,64);bad=VDFResult(bytes([r.output[0]^1])+r.output[1:],r.proof,r.iterations);self.assertFalse(self.a.verify(self.c,bad))
 def test_corrupt_proof_rejected(self):
  r=self.a.evaluate(self.c,64);bad=VDFResult(r.output,bytes([r.proof[0]^1])+r.proof[1:],r.iterations);self.assertFalse(self.a.verify(self.c,bad))
 def test_wrong_iterations_rejected(self):
  r=self.a.evaluate(self.c,64);self.assertFalse(self.a.verify(self.c,VDFResult(r.output,r.proof,65)))
 def test_verify_faster_than_evaluate_conformance(self):
  t0=time.perf_counter();r=self.a.evaluate(self.c,4096);te=time.perf_counter()-t0
  t0=time.perf_counter();ok=self.a.verify(self.c,r);tv=time.perf_counter()-t0
  self.assertTrue(ok);self.assertLess(tv,te,f"verification {tv:.6f}s must be faster than evaluation {te:.6f}s")

if __name__=="__main__":unittest.main(verbosity=2)
