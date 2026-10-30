# Record protection gate attempt 3625146

Status: FAILED DUE TO STALE TEST FIXTURES

Candidate commit: 362514638dfe943cb109968e01dfca3642726bb5

The focused PDR-015 gate passed:

- COSE_Sign1 record-protection tests: 6/6 PASS.
- updated block-pipeline tests: 3/3 PASS.
- pip dependency check: PASS.
- observer smoke test during the full run: PASS.
- working tree and diff check: clean.

The complete suite executed 81 tests and reported six errors. All six arose before the tested E2E operation because two pre-hardening test fixtures still called ledger_record with the literal byte string synthetic-protection.

Affected fixtures:

- tests/test_orchestrator_v020rc1.py
- tests/test_cg_weso_end_to_end_v020rc1.py

The normative implementation correctly rejected those bytes as not being COSE_Sign1. The implementation MUST NOT be weakened to preserve stale fixture behavior.

Correction: migrate the two test fixtures to generate valid Ed25519 COSE_Sign1 protection for their synthetic record cores, then repeat the complete gate.
