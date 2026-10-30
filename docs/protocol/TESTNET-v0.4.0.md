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

## Coverage matrix

| Protocol stage | v0.4 multi-node harness | Existing integrated conformance |
| --- | --- | --- |
| bootstrap and peer discovery | exercised across four nodes | v0.2 registry and discovery suites |
| canonical identity | isolated test validator identities | v0.2 identity, binding and registry suites |
| federation membership and quorum | exercised | v0.3 federation suite |
| authenticated transport compatibility | not represented as a socket in the harness | v0.2 legacy v2.2 adapter and discovery suites |
| TEP Proof of History | not simulated by the harness | v0.2 deterministic, concurrent and real CG-WESO suites |
| ledger block construction | not reimplemented by the harness | v0.2 block pipeline and orchestrator suites |
| quorum and finality | exercised at federation fault level | v0.2 signed QC and finalizer suite |
| partition and healing | exercised | v0.3 quorum guards |
| crash, restart and rejoin | exercised at finalized-state level | v0.2 atomic recovery and registry persistence suites |

The harness deliberately does not fabricate transport, Proof of History or ledger execution. Those stages remain covered by their real protocol conformance tests. A later multi-host testnet deployment must compose those components over actual testnet endpoints before a mainnet release candidate.
