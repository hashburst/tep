"""Fail-closed interoperability adapter from authenticated TEP v2.2 events."""
from dataclasses import dataclass
from .discovery import DiscoveryError

@dataclass(frozen=True)
class LegacyAuthenticatedEndpoint:
    node_id:str
    peer_id:str
    x25519_public_key:bytes
    host:str
    port:int
    authenticated:bool

class LegacyV22ReachabilityAdapter:
    def __init__(self,registry):
        self.registry=registry
    def resolve_authenticated_event(self,event):
        if not event.authenticated:raise DiscoveryError("legacy event is not authenticated")
        reg=self.registry.by_node_id(event.node_id)
        if reg is None:raise DiscoveryError("legacy node_id is not registered")
        s=reg.binding.statement
        if s.legacy.peer_id!=event.peer_id:raise DiscoveryError("legacy peer_id mismatch")
        if s.legacy.x25519_public_key!=event.x25519_public_key:raise DiscoveryError("legacy X25519 key mismatch")
        # Validate transport coordinates through the RC1 reachability endpoint policy,
        # but do not fabricate an Ed25519 reachability signature absent from v2.2.
        from .discovery import _endpoint
        host,port=_endpoint(event.host,event.port)
        return s.identity.identity_id(),host,port
