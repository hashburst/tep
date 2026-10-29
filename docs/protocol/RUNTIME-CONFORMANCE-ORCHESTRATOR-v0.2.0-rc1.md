# End-to-end orchestration runtime conformance record

Status: PASS

Tested commit:

d9b1928937e4dc8334e29741ba09fcd74ce31e19

Environment:

- WSL Ubuntu
- Python 3.14.4
- chiavdf 1.2.1
- cryptography 50.0.2
- test date: 2026-10-29

Results:

- pip check: no broken requirements
- orchestrator tests: 4 passed
- complete discovered unittest suite: 40 passed
- observer probe smoke test: passed
- end-to-end prepare, synthetic vote, QC, finalize and recovery: passed
- insufficient quorum persistence prevention: passed
- signature replay from another prepared block: rejected
- duplicate record IDs before VDF: rejected
- working tree: clean
- git diff check: passed

Conclusion:

Commit d9b1928937e4dc8334e29741ba09fcd74ce31e19 is the runtime-conformant isolated end-to-end orchestration baseline. Its orchestration tests use DeterministicTestVDF; CG-WESO end-to-end integration is gated separately.
