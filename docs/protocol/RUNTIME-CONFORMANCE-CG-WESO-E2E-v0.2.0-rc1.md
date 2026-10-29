# CG-WESO end-to-end runtime conformance record

Status: PASS

Tested commit:

7450dcfd035ca18cf0234437917fb4010caeed4e

Environment:

- WSL Ubuntu
- Python 3.14.4
- chiavdf 1.2.1
- cryptography 50.0.2
- test date: 2026-10-29

Results:

- pip check: no broken requirements
- real CG-WESO end-to-end tests: 2 passed
- complete discovered unittest suite: 42 passed
- observer probe smoke test: passed
- CG-WESO prepare, Ed25519 quorum, finalization and canonical recovery: passed
- insufficient 2-of-4 quorum created no finalized checkpoint: passed
- working tree: clean
- git diff check: passed

Conclusion:

Commit 7450dcfd035ca18cf0234437917fb4010caeed4e is the runtime-conformant RC1 core integration baseline for deterministic ledger construction, CG-WESO PoH evaluation and verification, federation finality, atomic checkpoint persistence and canonical recovery.

This does not yet certify that registrations overlap the physical CG-WESO evaluation interval; that lifecycle property is gated separately.
