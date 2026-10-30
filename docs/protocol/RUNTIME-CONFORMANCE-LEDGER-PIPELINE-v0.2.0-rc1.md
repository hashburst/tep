# Ledger-pipeline runtime conformance record

Status: PASS

Tested commit:

0e844be8788988f8fff3e1342367ef34e90dd3fa

Environment:

- WSL Ubuntu
- Python 3.14.4
- chiavdf 1.2.1 installed in isolated venv
- test date: 2026-10-29

Results:

- block-pipeline tests: 3 passed
- complete discovered unittest suite: 26 passed
- observer probe smoke test: passed
- working tree: clean
- git diff check: passed

Conclusion:

Commit 0e844be8788988f8fff3e1342367ef34e90dd3fa is the runtime-conformant B0-to-B1 block and checkpoint pipeline baseline for RC1.
