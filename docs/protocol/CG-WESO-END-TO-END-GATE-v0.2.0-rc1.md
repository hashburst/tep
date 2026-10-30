# CG-WESO end-to-end integration gate v0.2.0-rc1

This gate exercises the complete RC1 ledger path with the real CG-WESO-v1 adapter backed by chiavdf rather than DeterministicTestVDF.

Profile:

- VDF suite: CG-WESO-v1
- chiavdf: 1.2.1
- discriminant bits: 1024 for RC1 interoperability experiments
- iterations: 4096
- federation: four synthetic Ed25519 validators
- quorum threshold: three
- no production private keys or production state

The test constructs a schema-2 ledger record, derives the PoH challenge from genesis state, performs CG-WESO evaluation and verification through LedgerOrchestrator.prepare(), assembles the block, signs the exact finality message with synthetic validator keys, verifies the QC, atomically persists the finalized checkpoint and recovers it canonically.

A second test supplies only two of four signatures and requires finalization to fail without creating the checkpoint.

Passing this gate demonstrates integration of the already-tested components. It is not an independent cryptographic audit of chiavdf, not a mainnet security certification, and not a physical power-loss durability test.
