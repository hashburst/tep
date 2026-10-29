# Federation gate attempt record

Status: TEST DEFECT IDENTIFIED, NOT RUNTIME-CONFORMANT YET

Tested commit:

ed6b5289b7696a37680257bd56ea36c9a0592dc5

Environment:

- WSL Ubuntu
- Python 3.14.4
- chiavdf 1.2.1
- cryptography 50.0.2
- test date: 2026-10-29

Initial dependency attempt was blocked because cryptography was absent from the isolated VDF environment. After installing cryptography 50.0.2, Ed25519 import passed.

Federation results after dependency installation:

- 4 tests passed
- 1 test failed
- complete suite executed 35 tests with one failure
- working tree remained clean
- git diff check passed

The failing assertion constructed a quorum certificate for a different block_id and signed that different block_id correctly, then expected internal QC verification to reject it. That expectation was incorrect: a self-consistent QC for another block is cryptographically valid in isolation.

The corrected conformance test now distinguishes:

1. tampering with block_id after signatures are produced, which verify_qc MUST reject;
2. a valid QC for another block, which verify_qc MAY accept internally but finalize_verified_block MUST reject against the local AcceptedBlock.

No federation runtime-conformance claim is made for ed6b5289b7696a37680257bd56ea36c9a0592dc5.
