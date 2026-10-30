# TEP Sovereignty v0.3.0-rc1

## Purpose

Sovereignty defines policy boundaries for data placement and processing without making possession of application plaintext a condition of federation participation.

Federation answers which validators may attest shared protocol state. Sovereignty answers which authorized domains may store, replicate, process or disclose protected application data.

## Sovereignty domain

A sovereignty domain has a stable identifier, a versioned policy digest and an authority reference. A ledger record may bind a sovereignty-domain identifier and policy version without exposing the protected payload.

## Policy

A sovereignty policy may constrain storage domains, replication domains, processing domains, retention, disclosure and pruning. Enforcement decisions are bound to a policy version so that later policy changes do not silently reinterpret earlier records.

The ledger may retain commitments, ordering evidence and finality information while protected payload material remains within its authorized sovereignty domain.

## Federation separation

A validator may verify record commitments, block commitments, finality votes and policy references without receiving application plaintext.

Federation membership does not by itself grant access to protected sovereign data.

## Auditability

Policy transitions are versioned and committed to finalized federation state. An implementation records the policy identifier and version used for an authorization decision.

## Recovery

Recovery restores finalized policy state before processing new protected data. A node that cannot verify the required sovereignty policy fails closed for the affected operation.
