"""Authenticated dynamic reachability state for canonical TEP identities."""
from dataclasses import dataclass
import ipaddress
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from .encoding import dumps

REACH_DOMAIN=b"HB-TEP-REACHABILITY-v1\x00"

class DiscoveryError(ValueError):pass

def _endpoint(host,port):
    if not isinstance(host,str) or not host:raise DiscoveryError("host required")
    try:ipaddress.ip_address(host)
    except ValueError:raise DiscoveryError("RC1 reachability host must be an IP literal")
    if not isinstance(port,int) or isinstance(port,bool) or not 1<=port<=65535:raise DiscoveryError("invalid port")
    return host,port

@dataclass(frozen=True)
class ReachabilityStatement:
    network_id:bytes
    identity_id:bytes
    sequence:int
    host:str
    port:int
    def values(self):
        if not isinstance(self.network_id,bytes) or len(self.network_id)!=32:raise DiscoveryError("network_id must be 32 bytes")
        if not isinstance(self.identity_id,bytes) or len(self.identity_id)!=32:raise DiscoveryError("identity_id must be 32 bytes")
        if not isinstance(self.sequence,int) or isinstance(self.sequence,bool) or not 0<=self.sequence<2**64:raise DiscoveryError("sequence must be uint64")
        host,port=_endpoint(self.host,self.port)
        return [1,self.network_id,self.identity_id,self.sequence,host.encode("ascii"),port]
    def message(self):return REACH_DOMAIN+dumps(self.values())

@dataclass(frozen=True)
class SignedReachability:
    statement:ReachabilityStatement
    signature:bytes

@dataclass(frozen=True)
class ReachabilityEntry:
    sequence:int
    host:str
    port:int

class ReachabilityTable:
    def __init__(self,registry):
        self.registry=registry;self.network_id=registry.network_id;self._entries={}
    def update(self,signed):
        s=signed.statement
        if s.network_id!=self.network_id:raise DiscoveryError("wrong network")
        reg=self.registry.by_identity(s.identity_id)
        if reg is None:raise DiscoveryError("identity not registered")
        s.values()
        try:Ed25519PublicKey.from_public_bytes(reg.binding.statement.identity.signing_public_key).verify(signed.signature,s.message())
        except Exception as exc:raise DiscoveryError("invalid reachability signature") from exc
        old=self._entries.get(s.identity_id)
        if old is not None and s.sequence<=old.sequence:raise DiscoveryError("stale or replayed reachability")
        e=ReachabilityEntry(s.sequence,s.host,s.port);self._entries[s.identity_id]=e;return e
    def resolve_identity(self,identity_id):return self._entries.get(identity_id)
    def resolve_address(self,address):
        reg=self.registry.by_address(address);return None if reg is None else self._entries.get(reg.binding.statement.identity.identity_id())
    def resolve_node_id(self,node_id):
        reg=self.registry.by_node_id(node_id);return None if reg is None else self._entries.get(reg.binding.statement.identity.identity_id())
    def resolve_peer_id(self,peer_id):
        reg=self.registry.by_peer_id(peer_id);return None if reg is None else self._entries.get(reg.binding.statement.identity.identity_id())
