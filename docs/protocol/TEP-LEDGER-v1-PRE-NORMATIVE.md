# TEP-LEDGER-v1 — PRE-NORMATIVE

Source anchor: granted EP4169233B1 and recording procedure 300.

For node x, model its ledger copy as:

Lx(n) = (B0, B1, ..., Bn)

For n greater than zero, the description supports:

Bn = (HBn, BDn)
HBn = (Hn, H(n-1), Cn)
BDn = (rdp(n,1), ..., rdp(n,k))

Claim 1 independently requires a progressive count and a hash produced through a predetermined sequential operation chain. Claim 2 supplies the header/count ordering profile.

## Count

Required ordering property:

C(n+1) > Cn

A contiguous increment of exactly one is a candidate implementation, not yet a frozen patent requirement.

## Recursive hash state

Description-level model:

Hn = fH(H(n-1), An)

where An represents zero or more additional inputs permitted by the description. Contents and canonical encoding of An remain UNFROZEN.

## Recording window

Let start(n) and finish(n) delimit evaluation for Bn. A registration request q(dp) occurring during that evaluation window maps to a record in Bn:

start(n) <= tau(q) < finish(n)  =>  q(dp) -> rdp in BDn.

This is the central claim-1 timing rule. The description calls the evaluation interval tH and states that one or more requests received during tH are inserted into BDn.

## Record model

A PRE-NORMATIVE transmission record is abstractly:

rdp = (tx_info, certified_time?, prior_ledger_hash?, intra_block_hash_marker?, protection?)

Claim 9 defines the available identity/packet/sequence information. Claim 8 adds certified time. Claim 11 adds the last-ledger-block hash at transmission time. Claim 10 adds confidentiality/origin protection. Question marks mean profile-dependent until specification freeze.

## Ordering

Primary order: if a record is in Ba and another in Bb with a < b, ledger position orders them.

Claim 2: order by increasing Cn.

Within the same relevant block, claim 3 provides timestamp ordering and claim 4 provides associated-hash ordering.

## Verification and append

For the claim-6/7 profile, a block is appended only after congruence with prior ledger state and successful VDF verification. Abstractly:

Accept(Bn, Lx(n-1)) =
  Congruent(Bn, Lx(n-1))
  AND VerifyPoH(Bn)
  AND CounterOrderValid(Cn)
  AND RecordRulesValid(BDn).

The proof representation and exact verification interface remain UNFROZEN.

## Boundary

Lx is the TEP/shared transmission ledger described by this specification. It is not automatically the public HashBurst/HVM blockchain. rdp is a transmission record, not automatically a cryptocurrency transaction. Hn is ledger state, not the deployed UDP nonce or heartbeat counter.
