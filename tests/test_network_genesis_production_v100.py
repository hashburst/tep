import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from hashburst_tep.federation import Validator,ValidatorSet
from hashburst_tep.network_genesis import *

class GenesisProductionTests(unittest.TestCase):
 def genesis(self,network=b"N"*32,chain=b"C"*32,iterations=4096):
  vs=ValidatorSet(1,tuple(Validator(bytes([i])*32,bytes([i+10])*32) for i in range(1,5)))
  return ProductionGenesis(network,chain,1,vs,ConsensusParameters(2,3,30),VDFParameters(b"CG-WESO-v1",1024,iterations))
 def test_deterministic_genesis_binds_all_consensus_inputs(self):
  a=self.genesis();b=self.genesis();self.assertEqual(a.encode(),b.encode());self.assertEqual(a.genesis_id(),b.genesis_id())
  for x in (self.genesis(network=b"X"*32),self.genesis(chain=b"Y"*32),self.genesis(iterations=8192)):
   self.assertNotEqual(a.genesis_id(),x.genesis_id())
 def test_registry_is_immutable_and_idempotent(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"genesis.json";r=PersistentGenesisRegistry(p);g=self.genesis();self.assertEqual(r.bind(g),"BOUND");self.assertEqual(r.bind(g),"IDEMPOTENT")
   with self.assertRaisesRegex(ValueError,"mutation"):r.bind(self.genesis(iterations=8192))
 def test_restart_and_foreign_network_rejection(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"genesis.json";g=self.genesis();PersistentGenesisRegistry(p).bind(g);r=PersistentGenesisRegistry(p);self.assertTrue(r.require(g.network_id,g.chain_id,g.genesis_id()))
   with self.assertRaisesRegex(ValueError,"foreign"):r.require(b"X"*32,g.chain_id,g.genesis_id())
   with self.assertRaisesRegex(ValueError,"foreign"):r.require(g.network_id,g.chain_id,b"Z"*32)
 def test_validator_set_and_vdf_changes_change_genesis(self):
  g=self.genesis();vs=ValidatorSet(1,tuple(Validator(bytes([i])*32,bytes([i+20])*32) for i in range(1,5)));x=ProductionGenesis(g.network_id,g.chain_id,1,vs,g.consensus,g.vdf);self.assertNotEqual(g.genesis_id(),x.genesis_id())
if __name__=="__main__":unittest.main(verbosity=2)
