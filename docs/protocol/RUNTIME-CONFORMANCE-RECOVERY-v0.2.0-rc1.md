# Recovery runtime conformance record

Status: PASS

Tested commit:

a91fbaa7c43c100bf6037a5a3fd4d95350111030

Environment:

- WSL Ubuntu
- Python 3.14.4
- chiavdf 1.2.1 in isolated venv
- test date: 2026-10-29

Results:

- recovery tests: 4 passed
- complete discovered unittest suite: 30 passed
- observer probe smoke test: passed
- canonical checkpoint round-trip: passed
- corrupt and truncated checkpoint rejection: passed
- injected pre-rename failure preserved previous finalized bytes: passed
- B0 to B1 to B2 recursive linkage: passed
- working tree: clean
- git diff check: passed

The injected rename failure is an atomic-replacement unit test, not a physical power-loss durability certification.

Conclusion:

Commit a91fbaa7c43c100bf6037a5a3fd4d95350111030 is the runtime-conformant canonical recovery and recursive-ledger baseline for RC1.
