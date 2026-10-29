# TEP-POH-v1 — PRE-NORMATIVE

Source anchor: EP4169233B1 claims 1, 5, 6 and 7 with recording procedure 300.

TEP Proof of History here means the mechanism disclosed by this patent family. No Solana protocol semantics are imported.

## Claim-derived core

Claim 1: recursively generated ledger blocks have progressive count Cn and hash Hn computed through a predetermined sequential operation chain.

Claim 5: in its dependent profile, evaluation performs a predetermined number N of iterations and every iteration receives the preceding result.

Claim 6: block congruence is checked by a verification algorithm whose execution time is lower than the evaluation time; evaluation and verification form a verifiable delay function.

Claim 7: this hashing/evaluation supplies an unalterable proof of history indicating temporal order of ledger-block generation.

## Description-derived recurrence

Conceptually:

Hn = fH(H(n-1), An)

For the iterative profile:

y(n,0) = Init(H(n-1), An)
y(n,i) = F(y(n,i-1), X(n,i))   for i = 1..N
Hn = Finalize(y(n,N))

The mandatory property is sequential dependency. Init, F, Finalize, N, An, X and proof encoding remain PRE-NORMATIVE parameters.

## Evaluation time

Let:

tH(n) = finish(n) - start(n)

represent evaluation time for fH under the selected computational profile. The description specifies sequential non-parallelizable operations and discusses a minimum evaluation time under a PRAM model.

tH is not, by itself, a civil-time timestamp.

## Registration during evaluation

For every registration request qj occurring while Bn is being evaluated:

start(n) <= tau(j) < finish(n)

the corresponding record is associated with Bn.

Temporal evidence therefore combines recursive ledger position, progressive Cn, sequential delayed evaluation, and request-to-current-block binding.

## Verification

Let Eval produce Hn and a verification proof pi(n). Abstractly:

vH(parameters, H(n-1), An, Hn, pi(n)) = true

with required relation:

tv < tH.

The description states verification may be substantially faster. Exact complexity ratio and proof representation remain UNFROZEN.

## Temporal-order statement

For accepted blocks Ba and Bb with a < b in a congruent verified ledger sequence, their PoH state certifies the temporal order represented by ledger generation/addition order. Transmission records bound to those blocks inherit that ordering evidence.

This does not mean Hn directly encodes civil time. Claim 8 separately defines a certified-TSA-time profile.

## Invariants

1. Cn increases with ledger position.
2. Hn recursively depends on prior ledger state.
3. Evaluation contains predetermined sequential work/delay.
4. Registration requests bind to the block under evaluation under the protocol timing rule.
5. Claim-6/7 blocks append only after successful congruence and PoH verification.
6. UDP nonces, heartbeat timestamps and transport counters are not PoH.
7. Certified timestamps, when used, supplement rather than replace recursive PoH order.

## UNFROZEN

Not yet frozen: block serialization; genesis construction; exact Cn delta; An; concrete VDF and proof encoding; N and parameter governance; competing-block resolution; dissemination/quorum; crash checkpoint representation.

## Solana exclusion

This specification does not inherit Solana slots, ticks, leaders, leader schedules, validator model, Tower BFT, entry format, transaction model or Solana's particular PoH construction.
