"""Canonical durable persistence for the TEP identity registry."""
import os
from pathlib import Path
from .encoding import dumps,loads
from .identity import PeerIdentity,LegacyBinding
from .identity_binding import BindingStatement,SignedBinding
from .registry import IdentityRegistry,RegistryError

SCHEMA=1

def _entry_values(e):
    s=e.binding.statement
    return [s.sequence,s.identity.signing_public_key,s.identity.transport_public_key,
            s.legacy.node_id.encode("utf-8"),s.legacy.peer_id.encode("utf-8"),e.binding.signature]

def registry_bytes(registry):
    entries=sorted(registry._by_identity.values(),key=lambda e:e.binding.statement.identity.identity_id())
    return dumps([SCHEMA,registry.network_id,[_entry_values(e) for e in entries]])

def load_registry_bytes(data):
    try:v=loads(data)
    except Exception as exc:raise RegistryError("invalid canonical registry encoding") from exc
    if not isinstance(v,list) or len(v)!=3 or v[0]!=SCHEMA:raise RegistryError("invalid registry schema")
    network=v[1];rows=v[2]
    if not isinstance(network,bytes) or len(network)!=32 or not isinstance(rows,list):raise RegistryError("invalid registry document")
    r=IdentityRegistry(network)
    for row in rows:
        if not isinstance(row,list) or len(row)!=6:raise RegistryError("invalid registry entry")
        seq,spk,tpk,nodeb,peerb,sig=row
        if not isinstance(nodeb,bytes) or not isinstance(peerb,bytes) or not isinstance(sig,bytes):raise RegistryError("invalid registry entry types")
        try:node=nodeb.decode("utf-8");peer=peerb.decode("utf-8")
        except UnicodeDecodeError as exc:raise RegistryError("invalid registry UTF-8") from exc
        i=PeerIdentity(spk,tpk);l=LegacyBinding(i.identity_id(),node,peer,tpk);s=BindingStatement(network,seq,i,l)
        r.bootstrap(SignedBinding(s,sig))
    if registry_bytes(r)!=data:raise RegistryError("registry is not canonical")
    return r

def save_registry_atomic(path,registry,before_replace=None):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+".tmp")
    data=registry_bytes(registry)
    try:
        with open(tmp,"wb") as f:
            f.write(data);f.flush();os.fsync(f.fileno())
        if before_replace is not None:before_replace()
        os.replace(tmp,p)
        try:
            fd=os.open(str(p.parent),os.O_RDONLY)
            try:os.fsync(fd)
            finally:os.close(fd)
        except OSError:pass
    except Exception:
        try:tmp.unlink()
        except FileNotFoundError:pass
        raise
    return data

def load_registry(path):
    return load_registry_bytes(Path(path).read_bytes())
