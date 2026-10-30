# TEP v0.4.0-testnet

## Objective

The testnet milestone validates the complete controlled multi-node protocol path before any mainnet release candidate.

The required path is:

bootstrap -> identity -> federation membership -> discovery -> authenticated transport compatibility -> TEP Proof of History -> ledger propagation -> distributed voting -> quorum certificate and finality -> fault -> restart -> recovery -> rejoin

## Test environment

The repository first provides a deterministic in-process multi-node harness. It uses isolated test identities and does not open production sockets, import production private keys or enable mainnet.

The harness is a protocol fault-injection layer, not a substitute for the later public multi-host deployment gate.

## Fault gates

The automated testnet gate covers:

- four-validator bootstrap and discovery
- quorum continuation with one validator unavailable
- finality stop when a four-validator federation is split two and two
- partition healing
- crash and restart
- catch-up from a finalized peer
- rejection of recovery from another federation
- all v0.2 and v0.3 regression tests

## Exit condition

v0.4.0-testnet is considered repository-ready when the complete suite is green on the final candidate head. Public multi-host deployment remains a separate operational step and must use testnet identities and endpoints only.
