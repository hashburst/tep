"""Production validator governance state machine for TEP v1.0 G2."""
from dataclasses import dataclass
from hashlib import sha3_256
import json,os,tempfile
from .encoding import dumps
from .federation import Validator,ValidatorSet
from .domains import VALIDATOR_GOVERNANCE_PROPOSAL_DOMAIN,VALIDATOR_GOVERNANCE_VOTE_DOMAIN,VALIDATOR_GOVERNANCE_STATE_DOMAIN

ENROLLED=0
CANDIDATE=1
PENDING_ACTIVATION=2
ACTIVE=3
SUSPENDED=4
REVOKED=5
_STATES=(ENROLLED,CANDIDATE,PENDING_ACTIVATION,ACTIVE,SUSPENDED,REVOKED)
_ALLOWED={ENROLLED:{CANDIDATE,REVOKED},CANDIDATE:{PENDING_ACTIVATION,REVOKED},PENDING_ACTIVATION:{ACTIVE,REVOKED},ACTIVE:{SUSPENDED,REVOKED},SUSPENDED:{PENDING_ACTIVATION,REVOKED},REVOKED:set()}

def _b32(n,v):
    if not isinstance(v,bytes) or len(v)!=32:raise ValueError(f"{n} must be 32 bytes")
def _u64(n,v):
    if not isinstance(v,int) or isinstance(v,bool) or not 0<=v<2**64:raise ValueError(f"{n} must be uint64")

@dataclass(frozen=True)
class GovernanceMember:
    validator_id:bytes
    public_key:bytes
    state:int
    def values(self):
        _b32("validator_id",self.validator_id);_b32("public_key",self.public_key)
        if self.state not in _STATES:raise ValueError("invalid governance state")
        return [self.validator_id,self.public_key,self.state]

@dataclass(frozen=True)
class GovernanceState:
    federation_id:bytes
    version:int
    members:tuple
    def ordered(self):
        _b32("federation_id",self.federation_id);_u64("version",self.version)
        out=tuple(sorted(self.members,key=lambda x:x.validator_id))
        ids=[x.validator_id for x in out]
        if not out or len(ids)!=len(set(ids)):raise ValueError("invalid governance members")
        for x in out:x.values()
        return out
    def active_validator_set(self):
        vals=tuple(Validator(x.validator_id,x.public_key) for x in self.ordered() if x.state==ACTIVE)
        return ValidatorSet(self.version,vals)
    def digest(self):
        return sha3_256(VALIDATOR_GOVERNANCE_STATE_DOMAIN+dumps([1,self.federation_id,self.version,[x.values() for x in self.ordered()]])).digest()

@dataclass(frozen=True)
class GovernanceProposal:
    federation_id:bytes
    base_version:int
    validator_id:bytes
    old_public_key:bytes
    new_public_key:bytes
    from_state:int
    to_state:int
    nonce:bytes
    def values(self):
        _b32("federation_id",self.federation_id);_u64("base_version",self.base_version);_b32("validator_id",self.validator_id)
        _b32("old_public_key",self.old_public_key);_b32("new_public_key",self.new_public_key);_b32("nonce",self.nonce)
        if self.from_state not in _STATES or self.to_state not in _STATES:raise ValueError("invalid governance state")
        return [1,self.federation_id,self.base_version,self.validator_id,self.old_public_key,self.new_public_key,self.from_state,self.to_state,self.nonce]
    def digest(self):return sha3_256(VALIDATOR_GOVERNANCE_PROPOSAL_DOMAIN+dumps(self.values())).digest()
    def vote_message(self,authorizing_set):
        return VALIDATOR_GOVERNANCE_VOTE_DOMAIN+dumps([1,authorizing_set.version,authorizing_set.digest(),self.digest()])

@dataclass(frozen=True)
class GovernanceVote:
    validator_id:bytes
    signature:bytes

def verify_authorization(proposal,votes,authorizing_set):
    try:
        msg=proposal.vote_message(authorizing_set);members={v.validator_id:v.public_key for v in authorizing_set.ordered()}
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        seen=set();valid=0
        for vote in votes:
            _b32("validator_id",vote.validator_id)
            if vote.validator_id in seen or vote.validator_id not in members:return False
            seen.add(vote.validator_id);Ed25519PublicKey.from_public_bytes(members[vote.validator_id]).verify(vote.signature,msg);valid+=1
        return valid>=authorizing_set.threshold()
    except Exception:return False

def apply_governance(state,proposal,votes,authorizing_set):
    if proposal.federation_id!=state.federation_id or proposal.base_version!=state.version:raise ValueError("stale governance proposal")
    proposal.values()
    current=state.active_validator_set()
    if authorizing_set.version!=current.version or authorizing_set.digest()!=current.digest():raise ValueError("stale authorizing validator set")
    if not verify_authorization(proposal,votes,authorizing_set):raise ValueError("insufficient previous-set quorum")
    members={m.validator_id:m for m in state.ordered()};old=members.get(proposal.validator_id)
    if old is None:raise ValueError("validator must be enrolled before governance")
    if old.state!=proposal.from_state or old.public_key!=proposal.old_public_key:raise ValueError("proposal does not match current member")
    if proposal.to_state not in _ALLOWED[old.state]:raise ValueError("invalid governance transition")
    if proposal.new_public_key!=old.public_key:
        if not (old.state==SUSPENDED and proposal.to_state==PENDING_ACTIVATION):raise ValueError("key rotation requires SUSPENDED to PENDING_ACTIVATION")
        if any(m.public_key==proposal.new_public_key and m.validator_id!=old.validator_id for m in state.ordered()):raise ValueError("duplicate rotated key")
    members[old.validator_id]=GovernanceMember(old.validator_id,proposal.new_public_key,proposal.to_state)
    return GovernanceState(state.federation_id,state.version+1,tuple(members.values()))

class PersistentGovernanceRegistry:
    def __init__(self,path):
        self.path=os.fspath(path);self.state=None;self.used_proposals=set()
        if os.path.exists(self.path):
            raw=json.load(open(self.path,"r",encoding="utf-8"));self.used_proposals=set(raw["used_proposals"])
            self.state=GovernanceState(bytes.fromhex(raw["federation_id"]),raw["version"],tuple(GovernanceMember(bytes.fromhex(x["validator_id"]),bytes.fromhex(x["public_key"]),x["state"]) for x in raw["members"]))
    def initialize(self,state):
        if self.state is not None:raise ValueError("governance registry already initialized")
        state.digest();self.state=state;self._save()
    def _save(self):
        directory=os.path.dirname(self.path) or ".";os.makedirs(directory,exist_ok=True)
        obj={"federation_id":self.state.federation_id.hex(),"version":self.state.version,"members":[{"validator_id":m.validator_id.hex(),"public_key":m.public_key.hex(),"state":m.state} for m in self.state.ordered()],"used_proposals":sorted(self.used_proposals)}
        fd,tmp=tempfile.mkstemp(prefix=".governance-",dir=directory,text=True)
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as h:json.dump(obj,h,sort_keys=True,separators=(",",":"));h.flush();os.fsync(h.fileno())
            os.replace(tmp,self.path);dfd=os.open(directory,os.O_RDONLY)
            try:os.fsync(dfd)
            finally:os.close(dfd)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
    def apply(self,proposal,votes,authorizing_set):
        pid=proposal.digest().hex()
        if pid in self.used_proposals:raise ValueError("governance proposal replay")
        new_state=apply_governance(self.state,proposal,votes,authorizing_set)
        self.state=new_state;self.used_proposals.add(pid);self._save();return new_state
