# Identity gate attempt 6b19770

Tested commit:

6b19770e1dd8d7218fba9724b4105e85056e02ab

Observed result:

- identity tests: 3 passed, 1 failed
- complete discovered suite: 49 passed, 1 failed
- observer probe smoke test: passed
- working tree: clean
- git diff check: passed

Failure:

The test expected the v2.2 compatibility wire field for node_id `hashburst-node-long-name` to equal `hashburst-node-lo`. That expected value is 17 bytes.

The canonical v2.2 implementation and the RC1 compatibility implementation both define the field as the first 16 bytes of ASCII node_id, zero padded only when shorter. The correct value is therefore `hashburst-node-l`, exactly 16 bytes.

Classification:

TEST DEFECT. No defect was demonstrated in `src/hashburst_tep/identity.py`.

Corrective action:

- change only the test expectation to the canonical 16-byte value;
- add an explicit length assertion;
- do not change identity derivation, address derivation or legacy wire semantics.

This failed attempt is retained as regression evidence.
