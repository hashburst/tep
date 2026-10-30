# Final Runtime Conformance v0.3.0-rc1

## Candidate

The v0.3.0-rc1 candidate extends the immutable v0.2.0-rc1 baseline with Federation membership, partition and equivocation guards, recovery/rejoin state and versioned Sovereignty policy.

## Automated gate

GitHub Actions workflow: `TEP v0.3.0 RC1 conformance`

Verified run: `40996891578`

Verified candidate head before this documentation-only record: `ca122b63fb4a42219b95d92b18f1a3a41bbe34b4`

Result:

- 96 tests executed
- 96 tests passed
- no failures or errors
- v0.2.0-rc1 protocol vectors and regression tests included
- v0.3.0-rc1 Federation and Sovereignty tests included

## Release conditions

The release candidate does not enable mainnet or production application. It does not migrate private keys or modify the immutable legacy import.

This conformance record is documentation only. The final PR head must pass the same complete workflow after this file is added before merge.
