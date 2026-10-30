# CG-WESO-v1 runtime conformance record

Status: PASS

Tested commit:

f74b0464b9537b4f85b4409c7b1365a7cabfe900

Environment:

- WSL Ubuntu
- Python 3.14.4
- chiavdf 1.2.1 CPython 3.14 manylinux wheel
- test date: 2026-10-29

Results:

- CG-WESO tests: 5 passed
- complete discovered unittest suite: 19 passed
- observer probe smoke test: passed
- corrupted output: rejected
- corrupted proof: rejected
- wrong iteration count: rejected
- working tree: clean
- git diff check: passed

Measured CONFORMANCE profile at N=4096:

- evaluation_seconds: 0.06717580000986345
- verification_seconds: 0.03847969998605549
- verification_ok: true
- verification_faster: true
- measured evaluation/verification ratio: approximately 1.746

The timing result describes this test environment and run. It is not a universal performance guarantee and is not a mainnet parameter justification.

Conclusion:

Commit f74b0464b9537b4f85b4409c7b1365a7cabfe900 is the runtime-conformant CG-WESO-v1 evaluate/verify baseline for RC1 experimentation.
