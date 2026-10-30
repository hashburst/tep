"""Deterministic in-process multi-node testnet harness for TEP v0.4.0-testnet.

The harness exercises protocol transitions and fault handling without opening
network sockets or using production identities.
"""
from dataclasses import dataclass,field
from .federation_v03 import FederationState,RecoveryCursor,partition_has_quorum

@dataclass
class TestnetNode:
    node_id:bytes
    federation:FederationState
    finalized_count:int=0
    finalized_block_id:bytes=bytes(32)
    online:bool=True
    discovered:set=field(default_factory=set)
    def discover(self,other):
        if self.online and other.online and other.node_id!=self.node_id:self.discovered.add(other.node_id)
    def finalize(self,count,block_id,reachable_active):
        if not self.online:raise ValueError("offline node cannot finalize")
        if not partition_has_quorum(len(self.federation.active_validator_set().validators),reachable_active):
            raise ValueError("partition has no quorum")
        if count<=self.finalized_count:raise ValueError("finality must advance")
        self.finalized_count=count;self.finalized_block_id=block_id
    def cursor(self):return RecoveryCursor(self.federation.federation_id,self.federation.version,self.finalized_count,self.finalized_block_id)
    def recover_from(self,peer):
        if not self.online or not peer.online:raise ValueError("recovery requires online authenticated peers")
        if peer.federation.federation_id!=self.federation.federation_id:raise ValueError("federation mismatch")
        if peer.finalized_count<self.finalized_count:raise ValueError("peer is behind local finalized state")
        self.federation=peer.federation;self.finalized_count=peer.finalized_count;self.finalized_block_id=peer.finalized_block_id

class Testnet:
    def __init__(self,nodes):self.nodes=list(nodes)
    def discover_all(self):
        for a in self.nodes:
            for b in self.nodes:a.discover(b)
    def online(self):return [n for n in self.nodes if n.online]
    def partition(self,offline_indexes):
        for i,n in enumerate(self.nodes):n.online=i not in set(offline_indexes)
    def heal(self):
        for n in self.nodes:n.online=True
        self.discover_all()
