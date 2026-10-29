# TEP identity registry and address resolution v0.2.0-rc1

Status: RC1 state-machine layer.

IdentityRegistry applies the previously verified signed-binding rules as registry state.

It maintains unique indexes for:

- canonical identity_id;
- network-scoped TEP ledger address;
- v2.2 node_id;
- v2.2 peer_id.

Bootstrap accepts only a valid signed binding for the registry network. Duplicate identity, address, node_id or peer_id is rejected.

Rotation accepts only AuthorizedRotation whose previous identity is currently registered and whose sequence is exactly the next value under the signed-rotation verifier. On success the old indexes are removed and the new binding becomes authoritative.

Failed bootstrap or rotation does not mutate registry state.

Dynamic IP and UDP port are intentionally absent. They belong to authenticated discovery/reachability state, not canonical identity resolution.

This first registry gate is an in-memory deterministic state machine. Durable canonical serialization and atomic persistence are a separate gate and must pass before the registry is considered restart-safe.
