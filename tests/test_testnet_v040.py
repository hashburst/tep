import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from hashburst_tep.federation import Validator
from hashburst_tep.federation_v03 import FederationState,Member,ACTIVE
from hashburst_tep.testnet import TestnetNode,Testnet

class TestnetV040Tests(unittest.TestCase):
 def setUp(self):
  vals=tuple(Validator(bytes([i])*32,bytes([i+10])*32) for i in range(1,5))
  self.fed=FederationState(bytes.fromhex("aa"*32),1,tuple(Member(v,ACTIVE) for v in vals))
  self.nodes=[TestnetNode(v.validator_id,self.fed) for v in vals];self.net=Testnet(self.nodes)
 def test_bootstrap_discovery(self):
  self.net.discover_all()
  for n in self.nodes:self.assertEqual(len(n.discovered),3)
 def test_quorum_partition_and_heal(self):
  self.net.partition((3,));bid=bytes.fromhex("11"*32)
  for n in self.net.online():n.finalize(1,bid,3)
  self.assertEqual([n.finalized_count for n in self.net.online()],[1,1,1])
  self.net.partition((2,3))
  with self.assertRaises(ValueError):self.nodes[0].finalize(2,bytes.fromhex("22"*32),2)
  self.net.heal();self.nodes[3].recover_from(self.nodes[0]);self.assertEqual(self.nodes[3].finalized_count,1)
 def test_crash_restart_rejoin_catches_up(self):
  self.net.discover_all();self.nodes[3].online=False;bid=bytes.fromhex("33"*32)
  for n in self.nodes[:3]:n.finalize(1,bid,3)
  self.nodes[3].online=True;self.nodes[3].recover_from(self.nodes[0])
  self.assertEqual(self.nodes[3].finalized_block_id,bid);self.assertEqual(self.nodes[3].finalized_count,1)
 def test_recovery_rejects_wrong_federation(self):
  other=FederationState(bytes.fromhex("bb"*32),1,self.fed.members);peer=TestnetNode(bytes.fromhex("ff"*32),other,1,bytes.fromhex("44"*32))
  with self.assertRaises(ValueError):self.nodes[0].recover_from(peer)

if __name__=="__main__":unittest.main(verbosity=2)
