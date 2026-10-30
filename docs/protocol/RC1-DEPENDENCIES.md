# RC1 Python test dependencies

The complete v0.2.0-rc1 conformance suite currently requires:

- Python 3.14.4 in the recorded WSL environment
- chiavdf 1.2.1
- cryptography 50.0.2

Install the pinned test dependencies into an isolated virtual environment with:

    python -m pip install -r requirements-rc1.txt

The requirement file pins direct project dependencies used by the current RC1 suite. It is not a transitive lock file and does not claim reproducible hashes for indirect packages.

The production packaging decision remains separate from this test-environment pin.
