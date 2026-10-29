# TEP ledger and Proof of History RC1 core freeze

Status: FROZEN FOR v0.2.0-rc1 EXCEPT DEMONSTRATED DEFECTS

Runtime-conformant baseline:

49a608f3ba3e68ac596616497ab06184e7223ccc

Observed environment:

- WSL Ubuntu
- Python 3.14.4
- chiavdf 1.2.1
- cryptography 50.0.2
- test date: 2026-10-29

Final gate results:

- real CG-WESO concurrent registration: 1 passed
- isolated real CG-WESO concurrent test runtime: approximately 7.054 seconds at 1,000,000 iterations
- complete discovered unittest suite: 46 passed
- observer probe smoke test: passed
- pip dependency check: passed
- working tree: clean
- git diff check: passed

The real concurrency test demonstrated a registration after the CG-WESO evaluation worker entered RUNNING and before that evaluation completed. The candidate contained the registered record and the Wesolowski result verified.

The local monotonic timing observations are diagnostics only and are not ledger data, certified timestamps or PoH values.

Frozen RC1 core scope:

- deterministic CBOR protocol core;
- deterministic genesis and recursive block linkage;
- TEP PoH challenge construction;
- CG-WESO-v1 adapter and verification;
- registration-window semantics including real concurrent evaluation;
- schema-2 ledger record binding;
- canonical block assembly;
- federation quorum certificate gate;
- atomic finalized checkpoint persistence;
- canonical checkpoint recovery;
- end-to-end CG-WESO finalization path.

Changes to this frozen core require a demonstrated defect, explicit protocol-decision update and regression gate.
