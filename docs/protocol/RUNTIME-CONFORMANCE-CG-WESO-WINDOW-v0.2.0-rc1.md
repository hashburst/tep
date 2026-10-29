# CG-WESO registration-window runtime conformance record

Status: PASS

Tested commit:

1457416ba8f86375d8ec602987ec411fec6b47c3

Environment:

- WSL Ubuntu
- Python 3.14.4
- chiavdf 1.2.1
- test date: 2026-10-29

Results:

- registration-window tests: 4 passed
- complete discovered unittest suite: 23 passed
- observer probe smoke test: passed
- live CG-WESO window: count 1, two records, N=4096
- VDF output length: 100 bytes
- Wesolowski proof length: 100 bytes
- verification: true
- final window phase: verified
- working tree: clean
- git diff check: passed

Conclusion:

Commit 1457416ba8f86375d8ec602987ec411fec6b47c3 is the runtime-conformant CG-WESO registration-window baseline for RC1.
