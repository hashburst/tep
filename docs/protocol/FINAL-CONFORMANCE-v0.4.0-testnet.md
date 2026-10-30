# Final Conformance v0.4.0-testnet

## Candidate

The v0.4.0-testnet repository candidate extends the merged v0.3.0-rc1 baseline with a deterministic four-validator multi-node harness and controlled fault injection.

## Automated evidence

Workflow: `TEP v0.4.0 testnet conformance`

Final pre-record candidate head: `52c9945616e833c3734d202000f08464f07bae4e`

Verified workflow run: `40997525008`

Result:

- 100 tests executed
- 100 tests passed
- no failures or errors
- v0.2 protocol and cryptographic regression tests included
- v0.3 Federation and Sovereignty tests included
- v0.4 multi-node bootstrap, partition, healing, crash, recovery and rejoin tests included

## Boundary

This milestone establishes the repository testnet baseline. It does not claim that a public multi-host network has already been deployed. Real transport sockets, TEP Proof of History and ledger execution are validated by their existing protocol suites and are not fabricated inside the fault-injection harness.

A public multi-host deployment remains an operational testnet step before v0.9.0-mainnet-rc.

This file is documentation only. The final head must pass the same complete workflow after this record is added.
