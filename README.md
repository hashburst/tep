# HashBurst TEP

Canonical repository for the HashBurst TEP protocol family and runtime.

## Status

The current protocol baseline is **v0.2.0-rc1**.

This release candidate defines the foundational TEP ledger, TEP Proof of History, deterministic encoding, record protection, checkpoint and recovery mechanisms, peer identity, addressing, registry, reachability, discovery and compatibility with the deployed TEP v2.2 transport implementation.

The annotated tag `v0.2.0-rc1` identifies the verified release-candidate baseline. Subsequent protocol development is performed from `main` without modifying that tag.

## Protocol domains

- TEP logical identity and addressing
- TEP distributed ledger
- TEP Proof of History
- deterministic record and block encoding
- peer registry and discovery
- secure transport compatibility
- routing and forwarding
- Federation
- high availability and revocation
- Sovereignty

## TEP Proof of History

TEP Proof of History is the mechanism defined for the TEP protocol and derived from the applicable patent requirements and protocol specification.

It is distinct from Solana Proof of History. Civil time and optional TSA timestamps are separate from the sequential TEP Proof of History mechanism.

The v0.2.0-rc1 implementation uses the `CG-WESO-v1` VDF profile for the release-candidate protocol and retains the corresponding conformance tests and test vectors in this repository.

## TEP Ledger

The TEP Ledger is separate from the public HashBurst blockchain. It records protocol state and ordered transmission information according to the TEP protocol specification.

The v0.2.0-rc1 ledger implementation includes deterministic genesis, sequential block construction, verified evaluation-window candidates, block commitments, checkpoints and verify-forward recovery.

## Identity and discovery

The canonical identity layer provides peer identity, signed identity binding and rotation, durable registry persistence and authenticated reachability.

Compatibility with the deployed TEP v2.2 implementation is provided through the legacy adapter. Legacy wire identifiers and transport metadata do not replace canonical TEP identity.

## Federation

v0.2.0-rc1 contains the foundational finality data structures and tests. Federation governance, validator lifecycle and multi-node finality are developed in the v0.3.0 release-candidate line.

## Repository structure

- `docs/architecture/`: architecture and protocol boundaries
- `docs/protocol/`: protocol definitions, decisions, conformance records and test vectors
- `legacy/`: immutable imported TEP v2.2 implementation and provenance
- `src/hashburst_tep/`: current protocol implementation
- `tests/`: protocol, interoperability and release-conformance tests
- `tools/`: observer and verification utilities

## Legacy implementation

The imported TEP v2.2 implementation is retained under `legacy/node-installer-v2.2.0/` with provenance and hashes. It is preserved as historical implementation evidence and as an interoperability reference. Files under `legacy/` are not modified by current protocol development.

## Release integrity

Release-candidate protocol changes are validated by the repository test suite and conformance gates before merge. Published release tags are immutable; corrections and extensions are issued under a new version.
