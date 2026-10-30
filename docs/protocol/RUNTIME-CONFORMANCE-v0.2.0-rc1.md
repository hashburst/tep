# Runtime Conformance Record

Status: PASS

Tested commit:

3a8531f514d01e85890ed03de787321bef8eca17

Environment:

- WSL Ubuntu
- Python 3.14.4
- test date: 2026-10-29

Commands:

    PYTHONPATH=src python3 -m unittest -v tests/test_protocol_core_v020rc1.py
    PYTHONPATH=src python3 -m unittest discover -s tests -v
    git diff --check

Results:

- deterministic protocol core: 8 tests passed
- observer probe smoke test: passed
- complete discovered unittest suite: passed
- git diff check: passed
- no tracked source modification was produced by the tests

Python generated __pycache__ directories during execution. They were untracked runtime artifacts. The repository now ignores Python bytecode and cache directories.

Conclusion:

Commit 3a8531f514d01e85890ed03de787321bef8eca17 is the runtime-conformant deterministic protocol-core baseline for the next RC1 implementation stage.
