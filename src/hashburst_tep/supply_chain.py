"""TEP production supply-chain manifest and Ed25519 verification."""
from dataclasses import dataclass
from hashlib import sha256
import json
DOMAIN=b"HB-TEP-SUPPLY-CHAIN-v1\x00"
def _hex32(n,v):
    if not isinstance(v,str) or len(v)!=64:
        raise ValueError(f"{n} must be 32-byte hex")
    try: bytes.fromhex(v)
    except Exception: raise ValueError(f"{n} must be hex")
    return v.lower()
@dataclass(frozen=True)
class ReleaseManifest:
    version:str
    source_commit:str
    artifact_name:str
    artifact_sha256:str
    sbom_sha256:str
    provenance_sha256:str
    def object(self):
        if not self.version or not self.artifact_name:raise ValueError("missing release identity")
        return {"schema":"hb-tep-release-v1","version":self.version,"source_commit":_hex32("source_commit",self.source_commit),"artifact_name":self.artifact_name,"artifact_sha256":_hex32("artifact_sha256",self.artifact_sha256),"sbom_sha256":_hex32("sbom_sha256",self.sbom_sha256),"provenance_sha256":_hex32("provenance_sha256",self.provenance_sha256)}
    def canonical(self):return json.dumps(self.object(),sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()
    def signing_message(self):return DOMAIN+self.canonical()
def sha256_file(path):
    h=sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()
def sign_manifest(manifest,private_key_raw):
    if len(private_key_raw)!=32:raise ValueError("release signing key must be 32 bytes")
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    return Ed25519PrivateKey.from_private_bytes(private_key_raw).sign(manifest.signing_message())
def verify_manifest(manifest,signature,public_key_raw,artifact,sbom,provenance):
    if len(signature)!=64 or len(public_key_raw)!=32:return False
    try:
        if sha256_file(artifact)!=manifest.artifact_sha256 or sha256_file(sbom)!=manifest.sbom_sha256 or sha256_file(provenance)!=manifest.provenance_sha256:return False
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        Ed25519PublicKey.from_public_bytes(public_key_raw).verify(signature,manifest.signing_message());return True
    except Exception:return False
