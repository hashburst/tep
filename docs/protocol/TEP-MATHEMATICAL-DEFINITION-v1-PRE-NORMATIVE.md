# Mathematical Definition of the TEP Temporal Ledger

Status: PRE-NORMATIVE

This document gives a mathematical description of the temporal ledger defined from the traced EP4169233B1 patent material. Equations marked Required express properties derived from the traced claims. Equations marked Model give a precise notation for the description. Open parameters are not patent requirements.

## 1. Ledger

For a node x, the ledger after block n is

\[
L_x^{(n)} = \left(B_0,B_1,\ldots,B_n\right).
\]

This notation represents the ordered local copy of the distributed ledger.

For n greater than zero, a block is written as

\[
B_n = \left(HB_n,BD_n\right).
\]

The header model is

\[
HB_n = \left(H_n,H_{n-1},C_n\right).
\]

The body model is

\[
BD_n = \left(r_{n,1},r_{n,2},\ldots,r_{n,k_n}\right).
\]

Here Hn is the block hash state, H(n-1) is the preceding hash state, Cn is the progressive count, and each r(n,j) is a transmission record.

## 2. Progressive order

Required:

\[
C_{n+1} > C_n.
\]

Therefore, for two blocks Ba and Bb,

\[
C_a < C_b
\]

implies that Ba precedes Bb in the count ordering.

Proof. The count is increasing with ledger position. Applying the strict inequality repeatedly from a to b gives C(a) < C(b) whenever a < b.

The stronger rule

\[
C_n=C_0+n
\]

is not established by the traced claims. It remains an implementation choice.

## 3. Recursive hash state

The description is represented by

\[
H_n=f_H\left(H_{n-1},A_n\right),
\]

where An denotes any additional input selected by the protocol.

The essential recursive property is

\[
H_n \leftarrow H_{n-1}.
\]

A change to an accepted preceding state changes the input to the next evaluation. This gives an ordered dependency between consecutive hash states.

The exact contents and encoding of An remain open.

## 4. Sequential evaluation

For the iterative profile, let N be the predetermined number of iterations. Define

\[
y_{n,0}=\operatorname{Init}\left(H_{n-1},A_n\right).
\]

For each integer i with 1 less than or equal to i less than or equal to N,

\[
y_{n,i}=F\left(y_{n,i-1},X_{n,i}\right).
\]

The final state is

\[
H_n=\operatorname{Finalize}\left(y_{n,N}\right).
\]

The required dependency is

\[
y_{n,i-1}\rightarrow y_{n,i}.
\]

Each iteration therefore depends on the result of the preceding iteration. N, Init, F, Finalize and X(n,i) are not fixed in this draft.

## 5. Evaluation interval

Let

\[
s_n
\]

be the start of block evaluation and

\[
e_n
\]

its completion. The evaluation duration is

\[
t_H(n)=e_n-s_n.
\]

For a registration request qj issued at time tau(j), the recording rule is

\[
s_n \leq \tau_j < e_n
\quad\Longrightarrow\quad
r_j \in BD_n.
\]

This equation states the recording-window rule. A request made while block n is being evaluated is recorded in block n.

## 6. Inter-block temporal order

Let record ra belong to block Ba and record rb belong to block Bb. If

\[
a<b,
\]

then their ledger order is

\[
r_a \prec_L r_b.
\]

For the count-ordering profile,

\[
C_a<C_b
\quad\Longrightarrow\quad
r_a \prec_C r_b.
\]

Proof. Each record inherits the position of the block in which it is registered. Strictly increasing block count preserves the same order.

This establishes ledger order. It does not assign a civil-time value to either record.

## 7. Same-block order

If two relevant records belong to the same block,

\[
r_{n,a},r_{n,b}\in BD_n,
\]

block position alone does not distinguish their internal order.

The timestamp profile may define

\[
T(r_{n,a})<T(r_{n,b})
\quad\Longrightarrow\quad
r_{n,a}\prec r_{n,b}.
\]

The associated-hash profile may instead define an order from hash states attached to the records during sequential evaluation. The exact representation of that marker remains open.

## 8. Evaluation and verification

Write the evaluation operation as

\[
\operatorname{Eval}_{f_H}
\left(H_{n-1},A_n;\theta\right)
=
\left(H_n,\pi_n\right),
\]

where theta denotes public evaluation parameters and pi(n) denotes verification data.

Write verification as

\[
\operatorname{Verify}_{v_H}
\left(
H_{n-1},
A_n,
H_n,
\pi_n;
\theta
\right)
\in
\{0,1\}.
\]

A valid result satisfies

\[
\operatorname{Verify}_{v_H}(\cdots)=1.
\]

For the VDF profile, the required timing relation is

\[
t_v<t_H.
\]

Here tv is verification time and tH is evaluation time under the selected measurement profile.

This relation states that verification is faster than evaluation. It does not define a particular VDF construction.

## 9. Block acceptance

A pre-normative acceptance predicate is

\[
\operatorname{Accept}(B_n,L_x^{(n-1)})
=
P_{link}
\land
P_{count}
\land
P_{verify}
\land
P_{records}.
\]

The terms mean:

\[
P_{link}
=
\operatorname{Congruent}
\left(B_n,L_x^{(n-1)}\right),
\]

\[
P_{count}
=
\left(C_n>C_{n-1}\right),
\]

\[
P_{verify}
=
\operatorname{Verify}_{v_H}(\cdots),
\]

and

\[
P_{records}
=
\operatorname{RecordRulesValid}(BD_n).
\]

The logical form is a protocol model. The exact congruence and record-validation algorithms remain open.

## 10. Transmission record

A general record can be represented as

\[
r_{n,j}
=
\left(
I_s,
I_r,
I_p,
I_q,
T,
H_{prior},
M,
P
\right),
\]

where the fields represent sender identity, recipient identity, packet identity, sequence identity, optional certified time, optional prior-ledger hash, optional intra-block ordering marker and optional protection data.

The patent profiles do not require every field to be present in every record. Canonical field selection remains open.

## 11. Proof of History statement

Let Ba and Bb be accepted blocks in the same congruent verified ledger sequence. If

\[
a<b,
\]

then

\[
B_a\prec_{PoH}B_b.
\]

For records bound to these blocks,

\[
r_a\in BD_a,
\qquad
r_b\in BD_b,
\qquad
a<b,
\]

the inherited order is

\[
r_a\prec_{PoH}r_b.
\]

The result follows from the recursive block sequence, progressive ordering, sequential evaluation and recording-window binding.

This is an order statement. It is not an equation for civil time.

## 12. Certified time

When the certified-time profile is used, a record may contain

\[
T_j=\operatorname{TSA}(dp_j).
\]

The TSA value supplies certified civil-time information for that packet. It supplements the ledger order and does not replace the recursive PoH relation.

## 13. Properties established by the model

Sequential dependency:

\[
y_{n,i}
\text{ cannot be defined by this recurrence before }
y_{n,i-1}.
\]

Ledger dependency:

\[
H_n
\text{ depends on }
H_{n-1}.
\]

Recording locality:

\[
\tau_j\in[s_n,e_n)
\Longrightarrow
r_j\in BD_n.
\]

Count monotonicity:

\[
a<b
\Longrightarrow
C_a<C_b.
\]

Fast verification requirement:

\[
t_v<t_H.
\]

These properties follow from the stated model and traced claim conditions. They are not claims of cryptographic security beyond those conditions.

## 14. Open definitions

The following values remain open: B0, H0, canonical byte encoding, the exact increment of Cn, An, the concrete VDF, proof encoding, N, parameter governance, competing-block resolution, quorum, dissemination and crash-recovery state.

They must be decided in the Protocol Decision Register before this document can become normative.
