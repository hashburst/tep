"""Federation lifecycle and sovereignty primitives for TEP v0.3.0-rc1."""
from dataclasses import dataclass
from hashlib import sha3_256
from .encoding import dumps
from .federation import Validator,ValidatorSet
from .domains import FEDERATION_STATE_DOMAIN,MEMBERSHIP_PROPOSAL_DOMAIN,SOVEREIGNTY_POLICY_DOMAIN

CANDIDATE=0
ACTIVE=1
SUSPENDED=2
RETIRED=3
REVOKED=4

def _b32(n,v):
    if not isinstance(v,bytes) or len(v)!=32: raise ValueError(f"{n} must be 32 bytes")
def _u64(n,v):
    if not isinstance(v,int) or isinstance(v,bool) or not 0<=v<2**64: raise ValueError(f"{n} must be uint64")

@dataclass(frozen=True)
class Member:
    validator:Validator
    state:int
    def values(self):
        self.validator.values()
        if self.state not in (CANDIDATE,ACTIVE,SUSPENDED,RETIRED,REVOKED): raise ValueError("invalid membership state")
        return [self.validator.values(),self.state]

@dataclass(frozen=True)
class FederationState:
    federation_id:bytes
    version:int
    members:tuple
    def ordered(self):
        _b32("federation_id",self.federation_id);_u64("version",self.version)
        out=tuple(sorted(self.members,key=lambda m:m.validator.validator_id))
        ids=[m.validator.validator_id for m in out]
        if not out or len(ids)!=len(set(ids)): raise ValueError("invalid federation members")
        for m in out:m.values()
        return out
    def active_validator_set(self):
        vals=tuple(m.validator for m in self.ordered() if m.state==ACTIVE)
        return ValidatorSet(self.version,vals)
    def digest(self):
        return sha3_256(FEDERATION_STATE_DOMAIN+dumps([1,self.federation_id,self.version,[m.values() for m in self.ordered()]])).digest()

@dataclass(frozen=True)
class MembershipProposal:
    federation_id:bytes
    base_version:int
    validator:Validator
    new_state:int
    def values(self):
        _b32("federation_id",self.federation_id);_u64("base_version",self.base_version);self.validator.values()
        if self.new_state not in (ACTIVE,SUSPENDED,RETIRED,REVOKED): raise ValueError("invalid proposed state")
        return [1,self.federation_id,self.base_version,self.validator.values(),self.new_state]
    def digest(self): return sha3_256(MEMBERSHIP_PROPOSAL_DOMAIN+dumps(self.values())).digest()

def apply_membership(state,proposal):
    if proposal.federation_id!=state.federation_id or proposal.base_version!=state.version: raise ValueError("membership proposal does not match current federation state")
    proposal.values()
    members={m.validator.validator_id:m for m in state.ordered()}
    old=members.get(proposal.validator.validator_id)
    if old is None:
        if proposal.new_state!=ACTIVE: raise ValueError("new validator may only enter ACTIVE")
    else:
        if old.state==REVOKED: raise ValueError("revoked validator identity is terminal")
        allowed={ACTIVE:{SUSPENDED,RETIRED,REVOKED},SUSPENDED:{ACTIVE,RETIRED,REVOKED},CANDIDATE:{ACTIVE,REVOKED}}
        if proposal.new_state not in allowed.get(old.state,set()): raise ValueError("invalid membership transition")
        if old.validator.public_key!=proposal.validator.public_key: raise ValueError("membership transition cannot replace validator key")
    members[proposal.validator.validator_id]=Member(proposal.validator,proposal.new_state)
    return FederationState(state.federation_id,state.version+1,tuple(members.values()))

@dataclass(frozen=True)
class SovereigntyPolicy:
    domain_id:bytes
    version:int
    storage_domains:tuple
    processing_domains:tuple
    disclosure_domains:tuple
    def values(self):
        _b32("domain_id",self.domain_id);_u64("version",self.version)
        groups=[]
        for name,values in (("storage",self.storage_domains),("processing",self.processing_domains),("disclosure",self.disclosure_domains)):
            vals=tuple(sorted(values))
            if len(vals)!=len(set(vals)): raise ValueError(f"duplicate {name} domain")
            for v in vals:_b32(name,v)
            groups.append(list(vals))
        return [1,self.domain_id,self.version,*groups]
    def digest(self): return sha3_256(SOVEREIGNTY_POLICY_DOMAIN+dumps(self.values())).digest()
    def permits_storage(self,domain_id): _b32("storage_domain",domain_id);return domain_id in self.storage_domains
    def permits_processing(self,domain_id): _b32("processing_domain",domain_id);return domain_id in self.processing_domains
    def permits_disclosure(self,domain_id): _b32("disclosure_domain",domain_id);return domain_id in self.disclosure_domains
