# Multi-host deployment gate for v0.4.0-testnet

Baseline: `a97a17833074e9e44820fe8e90c151e8b22f37ad`

## Isolation

Use at least three disposable Ubuntu hosts or VMs. Do not use the production TEP state directory, production node keys, production peer registry or the production UDP/TCP ports. The testnet peer uses TCP 47840 and a dedicated `/var/lib/hashburst-testnet` identity.

## Per-host installation

Create a dedicated unprivileged account named `hashburst-testnet`. Check out the exact baseline plus the multi-host deployment tooling from this branch into `/opt/hashburst-tep-testnet`. Install Python 3, `cryptography` and `chiavdf`. Install `deploy/systemd/hashburst-tep-testnet.service`, enable it and allow TCP 47840 only between the selected testnet hosts or test controller.

Never copy a key or state directory between hosts.

## Gate A: authenticated reachability

From the test controller run:

`python3 tools/testnet_multihost_probe_v040.py http://HOST1:47840 http://HOST2:47840 http://HOST3:47840`

Every endpoint must return a distinct node identity and pass an Ed25519 challenge.

## Gate B: fault injection

1. Record all node identities and the probe output.
2. Stop one peer and verify the remaining peers remain reachable.
3. Restart it and verify the same node identity returns.
4. Stop enough peers to remove federation quorum. No finality test may be declared successful while quorum is absent.
5. Restore the peers and rerun authenticated reachability.
6. Run the repository's complete 100-test conformance suite on the exact code revision used by every host.

## Evidence

Preserve UTC timestamps, host labels, exact Git SHA, package versions, service status, challenge results and test output. Do not collect private key bytes.

Passing these gates establishes authenticated multi-host testnet reachability and identity continuity. The next gate must compose the real ledger, TEP-PoH and finality pipeline over these authenticated testnet peers before v0.9.0-mainnet-rc.
