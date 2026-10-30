# Concurrent VDF registration window v0.2.0-rc1

Purpose: demonstrate that a TEP registration can be accepted while the concrete VDF evaluation call is actually active, rather than merely while a sequential state machine is labelled RUNNING.

ConcurrentEvaluationWindow starts a dedicated evaluation worker. The worker records an internal monotonic diagnostic start value, changes the phase to RUNNING and signals the started event immediately before invoking the adapter evaluation. Registrations are accepted only while that worker remains RUNNING. On successful evaluation the worker closes the window; on failure it marks the window ABANDONED.

The monotonic diagnostic timestamps are not ledger fields, are not certified time and are not TEP Proof of History values.

A controlled test adapter holds the evaluation call open with synchronization events. The test registers a record only after the adapter has entered evaluate() and before it is released, proving overlap without timing races.

A second test proves registration after evaluation is rejected. A third proves failed evaluation is abandoned and cannot produce a completed registration window.

This is the concurrency/lifecycle gate required before representing the implementation as matching the patent-traced registration-during-evaluation boundary. A separate real CG-WESO timing integration remains required.
