"""G7 production federation admission policy."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha3_256
from .enrollment import EnrollmentCertificate,verify_certificate
from .governance import GovernanceState,ACTIVE
@dataclass(frozen=True)
class FederationAdmission:
    network_id:bytes
    genesis_id:bytes
    governance:GovernanceState
    controller_public_key:bytes
    now:int
    def admit(self,node_id:bytes,public_key:bytes,certificate:EnrollmentCertificate|None,presented_genesis_id:bytes)->bool:
        if len(node_id)!=32 or len(public_key)!=32 or len(presented_genesis_id)!=32:raise ValueError("invalid federation identity")
        if presented_genesis_id!=self.genesis_id:raise ValueError("foreign genesis rejected")
        if certificate is None:raise ValueError("non-enrolled node rejected")
        verify_certificate(certificate,self.controller_public_key,self.now)
        if certificate.network_id!=self.network_id or certificate.node_id!=node_id or certificate.node_public_key!=public_key:raise ValueError("enrollment identity mismatch")
        member=next((m for m in self.governance.members if m.validator_id==node_id),None)
        if member is None or member.state!=ACTIVE or member.public_key!=public_key:raise ValueError("unauthorized validator rejected")
        return True
    def admission_digest(self)->bytes:
        return sha3_256(b"HB-TEP-FEDERATION-ADMISSION-v1\x00"+self.network_id+self.genesis_id+self.governance.digest()).digest()
