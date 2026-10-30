# Final RC1 gate attempt 5803852

Status: FAILED DUE TO STALE API AND PROFILE TESTS

Candidate commit: 580385238a0955bd7ee2f73b0a8b96d78e5f21e1

The focused release-hardening gate passed 4/4. The focused COSE, block pipeline, orchestrator and CG-WESO E2E gate passed 15/15. pip check passed and observer smoke passed.

The complete suite executed 80 tests and reported four errors:

1. poh/__init__.py accidentally stopped exporting the existing PoH state-machine API.
2. the historical window lifecycle fixture mixed TSA and non-TSA records, which is intentionally rejected by the frozen RC1 TSA profile.
3. and 4. two recovery paths still invoked the pre-hardening assemble_verified_block API with raw challenge and VDF result.

No weakening of the verified-candidate or TSA-profile boundaries is permitted. The correction restores the existing public state-machine exports and migrates the affected tests to the hardened RC1 API/profile.
