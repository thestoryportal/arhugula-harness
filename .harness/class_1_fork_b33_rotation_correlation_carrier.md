# Class 1 Fork — B-33: `verify_rotation_6_steps` cannot prove a rotation boundary occurred

**Status: RATIFIED 2026-07-21 — the operator selected OPTION A AS RECOMMENDED** (open-dict additive IS carrier + 3-step verifier extension + injected OD-join evidence DTO from the composition root; apply arc per §3).
Registered pre-B-36; GROUNDED 2026-07-18 (the wait-for-real-caller boundary held:
`execute_key_rotation` — the sole `verify_rotation_6_steps` caller — still has only test
consumers, and rotation at MTC is explicitly deferred pending B-33 by both the B-51/B-52/B-54
and B-48 filings). **Unblocked 2026-07-16 by B-36/ADR-D8** (`AwsKmsSigningBackend` — a real
backend now exists to build the rotation-correlation carrier against). The register close_out
prescribes exactly this filing: "File a Class 1 fork for an IS rotation-correlation carrier
(mirrors OD §24.7); extend once B-36's backend lands."

## §1 The defect

`verify_rotation_6_steps` verifies a key-rotation window with a generic hash-chain continuity
check — which PASSES on a ledger where NO rotation boundary occurred at all. The verifier
cannot distinguish "rotation executed correctly across the boundary" from "no rotation
happened": nothing in the IS chain CARRIES the rotation event's identity, so the 6-step walk
proves continuity, not rotation. (The OD side already has the correlation surface: OD v1.31
§24.7 ports `audit.rotation_correlation_id` into the `audit_namespace_attrs` open-dict for the
two-row dual-signature rotation runtime path — but the IS state-ledger rows the walk traverses
carry no counterpart, so the walk cannot join against it.)

## §2 The prescribed shape (Class 1 — an IS-spec surface is missing)

An **IS rotation-correlation carrier** mirroring the OD §24.7 precedent: the rotation window's
IS entries carry a correlation identifier the verifier REQUIRES and JOINS on —
`verify_rotation_6_steps` then fails closed when the claimed window carries no correlation
(no rotation to prove) or an inconsistent one (a torn/mixed window), and proves genuine
rotation by joining the IS-side carrier against the OD-side `audit.rotation_correlation_id`
pair. Design questions the spec delta must answer (mirroring §24.7's own choices):

1. **Carrier home**: an open-dict sidecar field on the rotation window's `EntryPayload`s
   (the §24.7-style additive convention; drop-when-absent byte-compat for every non-rotation
   entry) vs a first-class C-IS-05 field (heavier; needs canonicalize-contribution rules).
   §24.7's precedent argues for the open-dict/additive shape.
2. **Verifier contract**: `verify_rotation_6_steps` gains a REQUIRED correlation argument;
   its 6 steps extend with (a) presence — every window entry carries the id; (b) uniqueness —
   one id per window; (c) OD join — the id matches the dual-signature audit pair's
   `audit.rotation_correlation_id`. Absence at any step = typed failure (never a pass).
3. **Rotation-boundary attestation**: the boundary entry (old-key-last / new-key-first) is
   identified by the carrier + the key-period transition, verified against the B-36 backend's
   key identities (`AwsKmsSigningBackend` `key_arns` mapping — physical-key distinctness at
   the boundary, the same canonical-material comparison the cutover-record checks use).
4. **OD-join mechanism (codex round-2 [P1] on this filing)**: a required correlation STRING
   does not prove a dual-signature OD pair exists, and `harness-cp` cannot import the OD
   ledger type without reversing the axis-import direction. The join is therefore an
   **INJECTED verifier / typed evidence DTO supplied by the runtime composition root** (the
   §20.3.1 injected-verifier precedent from the B-54 arc): the root reads the OD pair, builds
   the evidence carrier (correlation id + both key periods + pair presence), and
   `verify_rotation_6_steps` validates the IS-side carrier AGAINST that evidence — never a
   caller-supplied id trusted on its own.

## §3 Scope + sequencing

- IS spec delta (C-IS-05/C-IS-07 additive carrier convention + the verifier contract section)
  + U-IS plan widening; clearance markers per X-AL-3.
- Impl: carrier population at `execute_key_rotation`'s writes + `verify_rotation_6_steps`
  extension + witnesses (rotation-absent window fails; torn window fails; genuine
  rotation with OD join passes; PD-8 per check).
- MTC rotation remains DEFERRED until this lands (`sign_rotation_pair` PROHIBITED at MTC per
  the B-51/B-52/B-54 ratification, gate item 6 — this filing is that gate's exit path).
- Still no production caller for `execute_key_rotation`: the apply arc builds the carrier +
  verifier honestly against test consumers; CLI/production wiring is a separate follow-on
  (out of this filing's scope, consistent with the grounded wait-for-real-caller boundary).

## §4 The operator ratification (ONE decision)

- **(A) RECOMMENDED — ratify the §2 shape: open-dict additive IS carrier + 3-step verifier
  extension + OD §24.7 join; apply arc proceeds as §3.**
- (B) first-class C-IS-05 field variant (heavier; only if the operator wants the correlation
  hash-covered by the chain itself rather than carried additively).
- (C) hold — keep MTC rotation deferred with B-33 as the standing blocker (status quo; the
  register row remains the queryable record).
