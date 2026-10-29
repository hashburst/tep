# Federation finality runtime conformance record

Status: PASS

Tested commit:

4599ac6995243698dddadb9bde82346e043bf536

Environment:

- WSL Ubuntu
- Python 3.14.4
- chiavdf 1.2.1
- cryptography 50.0.2
- test date: 2026-10-29

Results:

- pip check: no broken requirements
- federation tests: 6 passed
- complete discovered unittest suite: 36 passed
- observer probe smoke test: passed
- valid QC for another block accepted by isolated QC verification but rejected by local block finalizer: passed
- tampered block binding: rejected
- duplicate votes: rejected
- insufficient quorum: rejected
- duplicate validator identity and public key: rejected
- working tree: clean
- git diff check: passed

Conclusion:

Commit 4599ac6995243698dddadb9bde82346e043bf536 is the runtime-conformant RC1 federation-finality baseline.
