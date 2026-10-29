# Recovery conformance profile v0.2.0-rc1

The RC1 recovery layer uses the same restricted deterministic-CBOR value domain as the encoder. The decoder rejects unsupported CBOR major types, indefinite lengths, non-shortest integer and length encodings, truncation and trailing data. A decoded checkpoint is accepted only if validation succeeds and canonical re-encoding is byte-identical.

The finalized checkpoint file is:

    checkpoint_id || canonical CheckpointCore

Recovery recomputes checkpoint_id and rejects any mismatch.

## Atomic replacement property

The writer creates a temporary file in the destination directory, writes and fsyncs it, verifies it by read-back, atomically replaces the destination and fsyncs the directory.

The unit-test crash model injects failure immediately before os.replace. The required property is that the prior finalized file remains byte-identical and the temporary file is removed.

This test is not represented as a physical power-loss durability proof. Filesystem, storage-controller and platform durability require deployment-specific fault testing.

## Recursive chain test

The conformance suite constructs B1 from the genesis state and B2 from B1. B2 must bind both H1 and block_id_1 through A2 and its header. Counts must be exactly 1 then 2.

No federation finality is inferred by this test.
