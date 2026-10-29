"""Minimal deterministic CBOR encoder for frozen TEP protocol objects.

Supported values are non-negative integers, bytes, fixed arrays and null.
Maps, text, floats, tags and indefinite lengths are intentionally rejected.
"""
class EncodingError(ValueError): pass

def _head(major,n):
    if not isinstance(n,int) or n<0: raise EncodingError("non-negative integer required")
    if n<24:return bytes([(major<<5)|n])
    if n<256:return bytes([(major<<5)|24,n])
    if n<65536:return bytes([(major<<5)|25])+n.to_bytes(2,"big")
    if n<2**32:return bytes([(major<<5)|26])+n.to_bytes(4,"big")
    if n<2**64:return bytes([(major<<5)|27])+n.to_bytes(8,"big")
    raise EncodingError("integer exceeds uint64")

def dumps(value):
    if value is None:return b"\xf6"
    if isinstance(value,bool):raise EncodingError("boolean not allowed")
    if isinstance(value,int):return _head(0,value)
    if isinstance(value,bytes):return _head(2,len(value))+value
    if isinstance(value,(list,tuple)):return _head(4,len(value))+b"".join(dumps(v) for v in value)
    raise EncodingError("unsupported protocol value")

def uint64be(value):
    if not isinstance(value,int) or isinstance(value,bool) or not 0<=value<2**64: raise EncodingError("uint64 required")
    return value.to_bytes(8,"big")
