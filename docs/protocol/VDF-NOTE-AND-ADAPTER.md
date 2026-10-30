# VDF note and adapter boundary

VDF means Verifiable Delay Function.

A VDF is a cryptographic function designed so that producing its result requires a prescribed sequential evaluation, while checking a valid result can be substantially faster. In the TEP patent trace this property is used by the claim-6 profile: the block hash evaluation and its verification form the delay-function evaluation and verification pair, and verification time is lower than evaluation time.

A VDF is not a civil-time clock. It does not by itself state a date or UTC time. In TEP it contributes sequential evidence to the Proof of History construction. Certified civil time, when used, is supplied by the separate TSA profile.

TEP-PoH is also not defined as a synonym for the VDF. The TEP-PoH model combines recursive ledger state, progressive block count, sequential evaluation, verification and the rule that transmission registrations are bound to the block being evaluated.

## VDF adapter

The VDF adapter is the software boundary between the deterministic TEP ledger and a concrete VDF implementation.

The ledger supplies canonical input bytes and a versioned parameter set. The adapter converts those values into the representation required by the selected VDF suite, performs or resumes evaluation, returns the VDF output and proof, and verifies received output/proof pairs. It also reports the exact suite and parameter identifiers and converts implementation-specific failures into stable protocol errors.

The adapter MUST NOT decide block encoding, record encoding, block count, body ordering, genesis state or ledger finality. Those rules belong to the deterministic ledger layer.

This separation permits the ledger format and its test vectors to remain unchanged if the experimental VDF library is replaced. A new VDF suite or parameter set changes its versioned identifiers and parameter hash; it does not silently reinterpret an existing ledger.

The first implementation stage intentionally contains no VDF engine and no VDF adapter. The deterministic core must pass its conformance vectors before that cryptographic component is added.
