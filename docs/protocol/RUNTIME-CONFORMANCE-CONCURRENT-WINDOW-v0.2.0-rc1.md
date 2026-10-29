# Concurrent VDF window runtime conformance record

Status: PASS

Tested commit:

4646c8f112fbebfe09a8d3b505780dc9925013b7

Environment:

- WSL Ubuntu
- Python 3.14.4
- chiavdf 1.2.1
- cryptography 50.0.2
- test date: 2026-10-29

Results:

- pip check: no broken requirements
- concurrent-window tests: 3 passed
- complete discovered unittest suite: 45 passed
- observer probe smoke test: passed
- registration while controlled evaluate() remained active: passed
- registration after evaluation: rejected
- failed evaluation: abandoned
- working tree: clean
- git diff check: passed

Conclusion:

Commit 4646c8f112fbebfe09a8d3b505780dc9925013b7 is the runtime-conformant concurrent-window lifecycle baseline.

The controlled adapter proves synchronization semantics without a timing race. Physical overlap with a real CG-WESO evaluation is gated separately.
