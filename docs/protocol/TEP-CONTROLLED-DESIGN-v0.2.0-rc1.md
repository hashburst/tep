# TEP v0.2.0-rc1 Controlled Protocol Design

Status: RC1 DESIGN FREEZE CANDIDATE

This document records project engineering decisions. Patent-derived requirements remain identified in the Patent-to-Protocol Traceability Matrix and the claim trace. The choices below are not represented as patent requirements.

## 1. Cryptographic primitives

Digest and domain-separation hash: SHA3-256 as defined by FIPS 202.

Canonical structured encoding: deterministic CBOR using the core deterministic encoding requirements of RFC 8949 section 4.2.1. TEP protocol objects use definite-length arrays with fixed field positions. Floating-point values, indefinite-length items and duplicate map keys are forbidden.

Signature container: COSE_Sign1 structure from RFC 9052. The RC1 identity signature algorithm remains Ed25519 to match the existing HashBurst identity direction. Private keys remain node-local.

VDF suite 1: repeated squaring in an imaginary-quadratic class group of unknown order with a Wesolowski proof. This is a PROJECT-DESIGN choice, not a patent requirement. The class-group choice avoids an RSA modulus trusted setup. The construction requires independent cryptographic review before mainnet.

## 2. Domain separation

Every digest begins with an ASCII domain label followed by a zero byte.

GENESIS_DOMAIN = "HB-TEP-GENESIS-v1"
POH_INPUT_DOMAIN = "HB-TEP-POH-INPUT-v1"
POH_OUTPUT_DOMAIN = "HB-TEP-POH-OUTPUT-v1"
RECORD_DOMAIN = "HB-TEP-RECORD-v1"
BODY_DOMAIN = "HB-TEP-BODY-v1"
BLOCK_DOMAIN = "HB-TEP-BLOCK-v1"
CHECKPOINT_DOMAIN = "HB-TEP-CHECKPOINT-v1"

No digest from one domain is valid in another domain.

## 3. Genesis B0 and H0

The canonical genesis descriptor is the deterministic-CBOR array

G0 = [
  1,
  network_id,
  protocol_version,
  vdf_suite,
  vdf_params_hash
]

where network_id and vdf_params_hash are 32-byte values.

The genesis PoH state is

H0 = SHA3-256(GENESIS_DOMAIN || 0x00 || CBOR(G0)).

The genesis block has C0 = 0 and no transmission records.

The genesis block identifier is computed by the normal block-id rule. A network is the same TEP ledger network only when its complete genesis descriptor and H0 match.

## 4. Canonical count Cn

C0 = 0.

For every accepted successor block:

Cn = C(n-1) + 1.

Cn is an unsigned 64-bit integer. A node MUST NOT create or accept a successor after Cn reaches 2^64 - 1. A future protocol version is required before exhaustion.

This rule is a PROJECT-DESIGN strengthening of the patent-mandated monotonic property.

## 5. PoH input domain An

The VDF input for block n is derived before its evaluation begins:

An = SHA3-256(
  POH_INPUT_DOMAIN || 0x00 ||
  network_id ||
  uint64be(Cn) ||
  H(n-1) ||
  block_id(n-1) ||
  vdf_params_hash
).

Including both H(n-1) and block_id(n-1) preserves direct recursive PoH dependency and commits the next PoH step to the complete accepted predecessor, including its body commitment.

BDn is deliberately absent from An because the records of BDn arrive while Hn is being evaluated.

## 6. VDF suite 1

The RC1 suite is named CG-WESO-v1.

The challenge An deterministically selects an imaginary-quadratic class group using a negative prime discriminant derived by hash-to-discriminant. The discriminant size is 1024 bits for RC1 interoperability experiments. This parameter is not a mainnet security claim.

The initial group element is the suite-defined fixed generator representation. Evaluation performs N sequential squarings:

y0 = g(An)
yi = yi-1 squared, for i from 1 to N
yn = yN.

The proof is a Wesolowski proof for the relation yN = g^(2^N).

The PoH hash state is

Hn = SHA3-256(
  POH_OUTPUT_DOMAIN || 0x00 ||
  An ||
  EncodeGroupElement(yN)
).

The proof is verified before block acceptance.

RC1 parameter profiles:
- TEST: N = 64.
- CONFORMANCE: N = 4096.
- PILOT: N = 1,000,000.

N is part of the VDF parameter set and therefore part of vdf_params_hash. A production value beyond PILOT is selected only after reproducible benchmarks and cryptographic review. Nodes never infer N from local wall-clock speed.

The required conformance relation remains tv < tH for the selected profile.

## 7. Transmission record rdp

A record core is the deterministic-CBOR array

Rcore = [
  1,
  sender_id,
  recipient_id,
  packet_id,
  sequence,
  prior_block_id,
  iteration_index,
  iteration_state_digest,
  certified_time,
  payload_digest
].

sender_id, recipient_id, packet_id, prior_block_id, iteration_state_digest and payload_digest are 32-byte values. sequence and iteration_index are unsigned 64-bit integers. certified_time is either null or an integer number of milliseconds since the Unix epoch supplied by the selected certified-time profile.

The record identifier is

record_id = SHA3-256(
  RECORD_DOMAIN || 0x00 || CBOR(Rcore)
).

The canonical ledger record is

rdp = [Rcore, record_id, protection].

protection is a deterministic COSE_Sign1 object or null. RC1 normative authenticated records require an Ed25519 COSE_Sign1 signature over record_id and the protocol context. Null protection is accepted only by explicitly declared legacy/import profiles.

## 8. Same-block temporal marker

During VDF evaluation, the evaluator exposes an iteration index i and a digest of the current sequential state:

iteration_state_digest =
SHA3-256(
  POH_OUTPUT_DOMAIN || 0x00 ||
  An ||
  uint64be(i) ||
  EncodeGroupElement(yi)
).

A registration request accepted during the evaluation window is assigned the latest fully completed iteration i.

For two records in the same block, the primary RC1 order is:
1. lower iteration_index;
2. lower certified_time when both certified times are present and iteration_index is equal;
3. bytewise lower record_id as deterministic tie-breaker.

The record-id tie-breaker is deterministic ordering, not evidence that one transmission occurred earlier than the other.

## 9. Body commitment and block identifier

After VDF evaluation closes, records are sorted by the rule above.

The body commitment is

body_root = SHA3-256(
  BODY_DOMAIN || 0x00 || CBOR([record_id_1, ..., record_id_k])
).

The canonical header is

Header_n = [
  1,
  Cn,
  H(n-1),
  block_id(n-1),
  Hn,
  vdf_suite,
  vdf_params_hash,
  body_root
].

The canonical block core is

BlockCore_n = [Header_n, [rdp_1, ..., rdp_k]].

The block identifier is

block_id_n = SHA3-256(
  BLOCK_DOMAIN || 0x00 || CBOR(BlockCore_n)
).

The VDF proof is stored beside the block core and is not included in block_id. This permits proof representation upgrades without changing the ledger object, provided the proof verifies the same frozen VDF relation.

The next An includes block_id_n. Therefore alteration of BDn changes block_id_n and invalidates the next accepted PoH transition.

## 10. Competing blocks

RC1 does not use longest-chain or work-weight selection.

For a given accepted predecessor and Cn, a candidate is eligible only if its VDF input, parameters and proof are valid. If multiple eligible candidates exist, deterministic selection uses the lexicographically smallest block_id.

This rule is a deterministic convergence rule for RC1. It is not represented as a patent requirement and is not a Byzantine-consensus proof.

A block becomes final for RC1 after a federation quorum certificate defined by the deployment profile. Public permissionless consensus is outside v0.2.0-rc1.

## 11. Dissemination and quorum

The ledger layer is transported over TEP. TEP-v2.2-COMPAT remains available as the carrier compatibility profile.

RC1 federation profile requires a configured validator set with monotonically versioned membership. A quorum certificate requires at least floor(2m/3) + 1 distinct authorized validator signatures for a set of m validators.

This is a PROJECT-DESIGN rule for the RC1 federation profile. It is not derived from EP4169233B1.

## 12. Privacy pruning

Nodes may prune record payload metadata for records for which they are neither sender nor recipient only after block finality.

The node retains:
- record_id;
- body_root;
- block header;
- block_id;
- PoH output and verification material required by the active proof-retention policy;
- pruning marker.

Pruning MUST NOT change block_id, body_root or the accepted PoH chain.

## 13. Checkpoint

A checkpoint is written only for a finalized block.

CheckpointCore = [
  1,
  network_id,
  Cn,
  Hn,
  block_id_n,
  vdf_params_hash,
  validator_set_version,
  quorum_certificate_digest
].

checkpoint_id = SHA3-256(
  CHECKPOINT_DOMAIN || 0x00 || CBOR(CheckpointCore)
).

The checkpoint file is written to a new temporary path, flushed, synchronized, verified by read-back, and atomically renamed into place. The previous valid checkpoint is retained until the next checkpoint is verified.

## 14. Crash recovery

On startup a node:

1. loads the newest structurally valid checkpoint;
2. verifies its checkpoint_id and referenced finalized block;
3. verifies the retained ledger forward from that checkpoint;
4. discards any unfinalized block candidate whose predecessor, parameters or proof state cannot be reconstructed;
5. resumes from the last accepted finalized block;
6. never reuses an incomplete VDF result as an accepted Hn.

An in-progress VDF may be checkpointed only as an optimization. Such a checkpoint is never ledger-final state. If its integrity or exact sequential position cannot be proven, evaluation restarts from the accepted predecessor.

## 15. Migration from TEP v2.2

The existing v2.2 runtime remains unchanged during RC1 introduction.

Migration is additive:
- preserve existing node identity and peer state;
- retain UDP v2.2 compatibility;
- add ledger/PoH services behind explicit capability negotiation;
- a v2.2-only peer continues to exchange legacy APP/heartbeat traffic;
- a v0.2.0-rc1 peer activates ledger/PoH messages only after mutual capability confirmation;
- no transport nonce, heartbeat counter or legacy timestamp is imported as Hn, Cn or PoH evidence;
- genesis and ledger state are new versioned state, stored separately from existing TEP identity state.

Rollback disables the new ledger/PoH service and returns to the unchanged v2.2 transport runtime without replacing persistent node keys.
