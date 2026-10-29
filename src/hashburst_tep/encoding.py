"""Minimal deterministic CBOR codec for frozen TEP protocol objects.

Supported values are non-negative integers, bytes, fixed arrays and null.
Maps, text, floats, tags and indefinite lengths are intentionally rejected.
Decoding additionally requires canonical shortest-form lengths.
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

def _argument(data,pos,ai):
    if ai<24:return ai,pos
    widths={24:1,25:2,26:4,27:8}
    if ai not in widths:raise EncodingError("indefinite or reserved additional information")
    w=widths[ai]
    if pos+w>len(data):raise EncodingError("truncated CBOR")
    n=int.from_bytes(data[pos:pos+w],"big")
    minimum={24:24,25:256,26:65536,27:2**32}[ai]
    if n<minimum:raise EncodingError("non-canonical CBOR integer/length")
    return n,pos+w

def _load_one(data,pos):
    if pos>=len(data):raise EncodingError("truncated CBOR")
    first=data[pos];pos+=1;major=first>>5;ai=first&31
    if major==7 and ai==22:return None,pos
    if major not in (0,2,4):raise EncodingError("unsupported CBOR type")
    n,pos=_argument(data,pos,ai)
    if major==0:return n,pos
    if major==2:
        end=pos+n
        if end>len(data):raise EncodingError("truncated byte string")
        return data[pos:end],end
    out=[]
    for _ in range(n):
        v,pos=_load_one(data,pos);out.append(v)
    return out,pos

def loads(data):
    if not isinstance(data,bytes):raise EncodingError("bytes required")
    value,pos=_load_one(data,0)
    if pos!=len(data):raise EncodingError("trailing CBOR data")
    if dumps(value)!=data:raise EncodingError("non-canonical CBOR")
    return value

def uint64be(value):
    if not isinstance(value,int) or isinstance(value,bool) or not 0<=value<2**64: raise EncodingError("uint64 required")
    return value.to_bytes(8,"big")
