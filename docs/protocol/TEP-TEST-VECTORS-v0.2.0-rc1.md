# TEP v0.2.0-rc1 Deterministic Test Vectors

Status: DESIGN VECTOR SET 1

These vectors cover deterministic encoding and SHA3-256 domain separation. They do not constitute a VDF security test.

## Vector conventions

network_id = 32 zero bytes

vdf_params_hash = 32 bytes of 0x11

previous block identifier = 32 bytes of 0x22

All integers use deterministic CBOR integer encoding. Hash function is SHA3-256.

## TV-001 Genesis

Genesis object:

[1, network_id, 1, 1, vdf_params_hash]

Deterministic CBOR:

850158200000000000000000000000000000000000000000000000000000000000000000010158201111111111111111111111111111111111111111111111111111111111111111

H0:

25b00f0b763b0742f15b95a383076b788ebb11f1f4baa47ec27dec8aa1fa228f

A conforming implementation MUST reproduce both values exactly.

## TV-002 First PoH input

Inputs:

Cn = 1

H(n-1) = H0 from TV-001

block_id(n-1) = 32 bytes of 0x22

The resulting An is:

52bc9c692f97801337aad2db178ecff8120d28715a1ac5078c7c6129fc23925f

## TV-003 Record identifier

Record core values:

version = 1

sender_id = 32 bytes of 0x33

recipient_id = 32 bytes of 0x44

packet_id = 32 bytes of 0x55

sequence = 7

prior_block_id = 32 bytes of 0x22

iteration_index = 9

iteration_state_digest = 32 bytes of 0x66

certified_time = null

payload_digest = 32 bytes of 0x77

Deterministic CBOR:

8a0158203333333333333333333333333333333333333333333333333333333333333333582044444444444444444444444444444444444444444444444444444444444444445820555555555555555555555555555555555555555555555555555555555555555507582022222222222222222222222222222222222222222222222222222222222222220958206666666666666666666666666666666666666666666666666666666666666666f658207777777777777777777777777777777777777777777777777777777777777777

record_id:

73f2544590d67864e4eae71dd21f4a99bb20d131ab478abe80eff19a7a49d361

## TV-004 Single-record body commitment

CBOR array containing only the record_id from TV-003:

81582073f2544590d67864e4eae71dd21f4a99bb20d131ab478abe80eff19a7a49d361

body_root:

dd8daa2efa4cb17d0aa6f31cfa2f8d70bfc7e513024514a98a4241b18c455a7b

## Negative tests

A conforming decoder MUST reject or fail validation for:
- non-deterministic alternate encoding of a protocol object;
- a floating-point value in a protocol structure;
- wrong byte-string length for fixed identifiers;
- Cn not equal to C(n-1)+1;
- record_id not matching its record core;
- body_root not matching the ordered record-id array;
- a normative record without valid protection;
- a VDF proof that does not verify;
- a block whose An does not bind H(n-1) and block_id(n-1);
- reuse of transport nonce or heartbeat counter as PoH state.
