# Identity registry runtime conformance record

Status: PASS

Tested commit:

089b2bac16b715e7be8a80789ca07b08f267f286

Results:

- stateful identity registry tests: 5 passed
- complete discovered unittest suite: 60 passed
- observer probe smoke test: passed
- pip dependency check: passed
- working tree and diff check: clean

The tested registry enforces unique identity_id, TEP address, node_id and peer_id indexes, signed bootstrap, sequence-controlled authorized rotation, replay rejection and no state mutation after rejected rotation.

Durable persistence was not part of this tested commit and is gated separately.
