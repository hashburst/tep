"""Stateful TEP identity registry and address resolution."""
from dataclasses import dataclass
from .identity_binding import SignedBinding,AuthorizedRotation,verify_signed_binding,verify_rotation

class RegistryError(ValueError):pass

@dataclass(frozen=True)
class RegistryEntry:
    binding:SignedBinding
    address:bytes

class IdentityRegistry:
    def __init__(self,network_id):
        if not isinstance(network_id,bytes) or len(network_id)!=32:raise RegistryError("network_id must be 32 bytes")
        self.network_id=network_id;self._by_identity={};self._by_address={};self._by_node={};self._by_peer={}
    def _keys(self,b):
        s=b.statement
        if s.network_id!=self.network_id:raise RegistryError("wrong network")
        if not verify_signed_binding(b):raise RegistryError("invalid binding signature")
        iid=s.identity.identity_id();addr=s.identity.ledger_address(self.network_id)
        return iid,addr,s.legacy.node_id,s.legacy.peer_id
    def _check_unique(self,keys,allow_identity=None):
        iid,addr,node,peer=keys
        for table,key,label in ((self._by_identity,iid,"identity"),(self._by_address,addr,"address"),(self._by_node,node,"node_id"),(self._by_peer,peer,"peer_id")):
            hit=table.get(key)
            if hit is not None and hit!=allow_identity:raise RegistryError(f"{label} already registered")
    def bootstrap(self,binding):
        keys=self._keys(binding);self._check_unique(keys)
        self._insert(binding,keys);return self._by_identity[keys[0]]
    def rotate(self,rotation):
        nb=rotation.next_binding;newkeys=self._keys(nb);oldid=rotation.continuity.previous_identity_id
        old=self._by_identity.get(oldid)
        if old is None:raise RegistryError("previous identity not registered")
        oldseq=old.binding.statement.sequence
        if not verify_rotation(rotation,old.binding.statement.identity,oldseq):raise RegistryError("invalid rotation")
        self._check_unique(newkeys,allow_identity=oldid)
        self._remove(oldid);self._insert(nb,newkeys);return self._by_identity[newkeys[0]]
    def _insert(self,binding,keys):
        iid,addr,node,peer=keys;e=RegistryEntry(binding,addr)
        self._by_identity[iid]=e;self._by_address[addr]=iid;self._by_node[node]=iid;self._by_peer[peer]=iid
    def _remove(self,iid):
        e=self._by_identity.pop(iid);s=e.binding.statement
        self._by_address.pop(e.address,None);self._by_node.pop(s.legacy.node_id,None);self._by_peer.pop(s.legacy.peer_id,None)
    def by_identity(self,iid):return self._by_identity.get(iid)
    def by_address(self,address):
        iid=self._by_address.get(address);return None if iid is None else self._by_identity[iid]
    def by_node_id(self,node_id):
        iid=self._by_node.get(node_id);return None if iid is None else self._by_identity[iid]
    def by_peer_id(self,peer_id):
        iid=self._by_peer.get(peer_id);return None if iid is None else self._by_identity[iid]
