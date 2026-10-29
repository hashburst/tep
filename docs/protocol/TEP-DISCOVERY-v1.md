# TEP Discovery and Reachability v1

Status: RC1 authenticated reachability state.

Canonical identity and TEP ledger address are stable protocol identifiers. IP address and UDP port are mutable transport coordinates and MUST NOT be used as identity.

A reachability statement is:

    [1, network_id, identity_id, sequence, ip_literal_ascii, port]

It is signed by the Ed25519 signing key of the identity currently admitted in IdentityRegistry. The signature domain is:

    HB-TEP-REACHABILITY-v1 || 0x00

The receiver MUST reject:

- an identity absent from the verified registry;
- a wrong network;
- an invalid signature;
- a sequence less than or equal to the last accepted reachability sequence;
- an invalid endpoint.

RC1 deliberately limits the host field to IPv4 or IPv6 literals. DNS-name policy is not silently introduced.

Reachability may be resolved from canonical identity_id, TEP address, legacy node_id or legacy peer_id, but all paths terminate at the same registered canonical identity.

Compatibility boundary with production v2.2:

Production v2.2 already permits endpoint refresh after an authenticated packet/heartbeat and treats peer identity separately from IP/port. This RC1 object formalizes that separation. It does not replace or alter the frozen 36-byte v2.2 UDP carrier and does not claim that the v2.2 heartbeat counter is TEP Proof of History.

Wire adaptation to authenticated v2.2 heartbeat processing is a separate interoperability gate.
