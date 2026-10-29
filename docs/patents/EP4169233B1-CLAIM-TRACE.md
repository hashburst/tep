# EP4169233B1 claim trace

Status: PRE-NORMATIVE.

Claims 1-7 define the core temporal-ledger path:
- Claim 1: distributed-ledger copy per node; recursive blocks; progressive count; hash from a predetermined sequential operation chain; registration in the block under hash evaluation when the request is issued; recipient ordering by ledger position.
- Claim 2: ordering by the increasing count value in the block header.
- Claim 3: same-block ordering by recorded timestamps.
- Claim 4: same-block ordering by associated hashing-algorithm values.
- Claim 5: predetermined iterations, each dependent on the previous iteration result.
- Claim 6: append after congruence verification; verification is faster than evaluation; evaluation and verification form a verifiable-delay-function pair.
- Claim 7: the hashing algorithm supplies PoH indicating temporal order of ledger-block generation.

Claims 8-12 add dependent profiles:
- Claim 8: certified TSA timestamp acquired at packet generation and included in the registration request.
- Claim 9: transmission information includes at least one of sender identifier, recipient identifier, packet identifier or sequence identifier and is stored in the block.
- Claim 10: confidentiality and/or origin-authentication protection for transmission information.
- Claim 11: registration also carries the hash associated with the last ledger block at transmission time.
- Claim 12: a node removes transmission information for packets for which it is neither sender nor recipient.
- Claim 13: system claim for nodes maintaining ledger copies and executing the method.

## Description symbols

The detailed description names Lx, Bn, source B0, header HB = (Hn, Hn-1, Cn), body BD containing rdp records, evaluation fH with time tH, and verification vH with time tv. Requests received during tH are inserted into BDn and the generated block is added after vH verification.

These description-level symbols inform the protocol model but are not represented as though every detail were independently required by claim 1.
