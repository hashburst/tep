"""Restricted canonical COSE_Sign1 profile for normative TEP RC1 records.

RFC 9052 COSE_Sign1 shape is used with an embedded payload. The project codec
intentionally has no CBOR maps or negative integers, so the protected header is
the fixed canonical CBOR encoding of {1: -8} (alg: EdDSA).
"""
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey,Ed25519PublicKey
from .encoding import dumps,loads

COSE_SIGN1_CONTEXT=b"Signature1"
COSE_EDDSA_PROTECTED=b"\xa1\x01\x27"  # canonical CBOR map {1: -8}
EMPTY_MAP=b"\xa0"

class CoseError(ValueError):pass

def _sig_structure(protected,payload):
    return dumps([COSE_SIGN1_CONTEXT,protected,b"",payload])

def sign1_ed25519(payload,private_key):
    if not isinstance(payload,bytes):raise CoseError("payload must be bytes")
    if not isinstance(private_key,Ed25519PrivateKey):raise CoseError("Ed25519 private key required")
    sig=private_key.sign(_sig_structure(COSE_EDDSA_PROTECTED,payload))
    # Outer COSE array uses the fixed empty unprotected map encoded separately,
    # because the frozen project codec deliberately does not admit maps.
    return (b"\x84"+dumps(COSE_EDDSA_PROTECTED)+EMPTY_MAP+dumps(payload)+dumps(sig))

def _read_item(data,pos):
    # Decode one item using canonical project decoder by finding its exact end.
    # Only byte strings are needed for protected, payload and signature.
    if pos>=len(data):raise CoseError("truncated COSE_Sign1")
    first=data[pos];major=first>>5;ai=first&31
    if major!=2:raise CoseError("COSE_Sign1 byte string expected")
    pos+=1
    if ai<24:n=ai
    elif ai==24:
        if pos>=len(data):raise CoseError("truncated COSE_Sign1")
        n=data[pos];pos+=1
        if n<24:raise CoseError("non-canonical COSE length")
    elif ai==25:
        if pos+2>len(data):raise CoseError("truncated COSE_Sign1")
        n=int.from_bytes(data[pos:pos+2],"big");pos+=2
        if n<256:raise CoseError("non-canonical COSE length")
    elif ai==26:
        if pos+4>len(data):raise CoseError("truncated COSE_Sign1")
        n=int.from_bytes(data[pos:pos+4],"big");pos+=4
        if n<65536:raise CoseError("non-canonical COSE length")
    else:raise CoseError("unsupported COSE length")
    end=pos+n
    if end>len(data):raise CoseError("truncated COSE_Sign1")
    return data[pos:end],end

def parse_sign1(encoded):
    if not isinstance(encoded,bytes) or not encoded.startswith(b"\x84"):raise CoseError("COSE_Sign1 array required")
    protected,p=_read_item(encoded,1)
    if encoded[p:p+1]!=EMPTY_MAP:raise CoseError("unprotected header must be empty map")
    p+=1;payload,p=_read_item(encoded,p);signature,p=_read_item(encoded,p)
    if p!=len(encoded):raise CoseError("trailing COSE_Sign1 data")
    if protected!=COSE_EDDSA_PROTECTED:raise CoseError("protected alg must be EdDSA")
    if len(signature)!=64:raise CoseError("Ed25519 signature must be 64 bytes")
    return protected,payload,signature

def verify_sign1_ed25519(encoded,public_key,expected_payload=None):
    try:
        protected,payload,sig=parse_sign1(encoded)
        if expected_payload is not None and payload!=expected_payload:return False
        Ed25519PublicKey.from_public_bytes(public_key).verify(sig,_sig_structure(protected,payload))
        return True
    except Exception:return False
