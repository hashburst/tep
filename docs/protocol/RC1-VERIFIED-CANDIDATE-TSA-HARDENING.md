# RC1 verified candidate and TSA profile hardening

Status: release hardening.

A raw WindowCandidate is an evaluation result, not authority to assemble a block. EvaluationWindow.verify now returns a distinct VerifiedWindowCandidate only after adapter verification and exact registration-set verification. Canonical block assembly accepts only VerifiedWindowCandidate and requires the supplied ledger records to match its verified record identifiers in exact order.

This makes the verified boundary structural rather than a caller convention.

TSA is an optional block-window profile and remains separate from TEP Proof of History.

For one evaluation window:

- non-TSA profile: every record has certified_time = null;
- TSA profile: every record has a uint64 certified_time;
- mixed timed and untimed records in the same window are rejected before VDF evaluation.

In TSA profile, records are ordered by certified_time and then record_id. In non-TSA profile, records are ordered canonically by record_id.

A certified_time is external timestamp evidence. It is not the PoH value, VDF iteration counter, or civil-time interpretation of Hn.
