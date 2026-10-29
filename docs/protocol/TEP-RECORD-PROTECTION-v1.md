# TEP normative record protection v0.2.0-rc1

Status: RC1 security hardening implementing PDR-015.

Normative schema-v2 records require COSE_Sign1 with Ed25519/EdDSA. Arbitrary protection bytes and null protection are rejected.

RC1 COSE profile:

- COSE_Sign1 four-element array;
- protected header is canonical CBOR {1: -8}, selecting EdDSA;
- unprotected header is the empty map;
- payload is embedded and MUST equal the exact canonical WindowRecordCore encoding;
- external_aad is the empty byte string;
- signature is Ed25519 over the RFC 9052 Sig_structure for context Signature1.

The frozen TEP deterministic protocol codec remains unchanged. It intentionally does not admit maps or negative integers. The two fixed COSE header maps are therefore encoded and parsed by the restricted COSE adapter rather than widening the core ledger codec.

Legacy/import records are a separate explicit profile. They may use null protection only when ledger_record(..., legacy_import=True) is requested. This exception MUST NOT be used for normative RC1-originated records.

This hardening does not alter record_id: record_id continues to commit to the canonical record core and not to the protection envelope.
