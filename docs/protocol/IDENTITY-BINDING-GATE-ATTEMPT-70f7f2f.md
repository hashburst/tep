# Identity-binding gate attempt 70f7f2f

Tested commit:

70f7f2f62df0fe7101db85edde5bf9b6802f9fa3

Observed result:

- identity-binding tests: 4 errors
- complete discovered suite: 50 passed and 4 errors
- observer probe smoke test: passed
- working tree: clean
- git diff check: passed

All four errors occurred before signature verification. BindingStatement attempted to pass the Python string node_id and peer_id values from LegacyBinding.values() into the frozen deterministic protocol encoder. That encoder intentionally supports unsigned integers, bytes, arrays and null, and rejects strings.

Classification:

NEW IDENTITY-BINDING SERIALIZATION DEFECT. The frozen protocol encoder is not defective and must not be widened for this feature.

Corrective action:

The identity-binding layer now defines a dedicated canonical compatibility representation:

    [1, identity_id, utf8(node_id), utf8(peer_id), x25519_public_key]

node_id and peer_id are encoded as UTF-8 byte strings before deterministic CBOR serialization. Limits are enforced on encoded byte length. The existing LegacyBinding object and the frozen encoding module are unchanged.

A regression test explicitly exercises non-ASCII UTF-8 identifiers and verifies the signed binding.
