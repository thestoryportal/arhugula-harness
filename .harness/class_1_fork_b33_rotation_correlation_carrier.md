# Class 1 Fork — B-33: `verify_rotation_6_steps` cannot prove a rotation boundary occurred

**Status: RATIFIED 2026-07-21 — the operator selected OPTION A AS RECOMMENDED** (open-dict additive IS carrier + 3-step verifier extension + injected OD-join evidence DTO from the composition root; apply arc per §3).

**Apply-arc progress (updated 2026-07-23).** Leg (i) — the IS carrier — LANDED at IS spec v1.11→v1.12 + IS plan v2.8 (U-IS-20, PR #1083). Leg (ii) — the CP+OD+Runtime SPEC+PLAN surface §2 item 2/4 + §3 sequencing calls for — LANDED at CP spec v1.104→v1.105 (§20.3.1 row 7 amended + NEW §20.3.2), OD spec v1.34→v1.35 (NEW §24.8), Runtime spec v1.104→v1.105 (NEW §13.6), plus the corresponding CP/OD/Runtime plan deltas (v2.41/v2.30/v2.53) and CXA v2.22 (NEW §2.3.10, `R-planned`); clearance markers at `.harness/clearance/*-2026-07-23.md`. Two rounds of out-of-family (Codex) review on leg (ii)'s PR fixed 10 findings total (5 round-1: evidence-semantics disclaimer, window-derived-not-caller-supplied id, required not optional key-identity resolver, U-RT-147 no-production-caller scope narrowing, stale pointer rows; 5 round-2: split `audit_ledger_entries`/`rotation_window_entries` — the two require CONFLICTING input shapes on `verify_rotation_6_steps`'s existing parameter, a real design defect the round-1 draft introduced; `signatures_verified` field making structural OD evidence necessary-but-not-sufficient for `PROBE_VERIFY_AT_READ`; evidence correlation-id echo-check; lone-matching-entry now raises `RotationPairIntegrityBreach` instead of folding into absence). Round-2 also raised a genuine sequencing disagreement — whether this leg must include the real write path to "honestly close" — reconciled via `advisor()` 2026-07-23: the fork's own §3 sequencing stands (write path is leg iii, not this leg), but leg iii's scope is now explicitly registered as TWO dependencies, not one: (a) `execute_key_rotation`'s real ledger-write path + a real `rotation_window_entries` producer, AND (b) the OD §21.2.2 rotation-period signature-verification extension `signatures_verified=True` requires (CP spec v1.105 §2 row 4b / OD spec v1.35 §24.8 row 8a) — without (b), `PROBE_VERIFY_AT_READ` cannot genuinely succeed even once (a) lands. **Leg (iii) — the remaining impl per §3 bullet 2 (the `verify_rotation_6_steps`/OD-accessor/Runtime-adapter CODE + the rotation-absent/torn-window/genuine-rotation-with-OD-join witnesses, all mutation-probed per PD-8, PLUS the two now-explicit dependencies above) — NOT YET STARTED**; this filing's own §3 wait-for-real-caller boundary still holds (no production caller of `execute_key_rotation` is wired at any leg so far, by design). A third out-of-family review round on leg (ii)'s PR fixed 8 more findings (2 P1, 6 P2): a genuine security gap the round-2 parameter split otherwise left open (`rotation_window_entries` needed an explicit subset-membership check against `audit_ledger_entries`, closed via `compute_entry_hash`-identity comparison — NOT via new OD-owned entry references, to avoid a cross-axis-ownership blur); a self-contradictory test witness (round-2's own text claimed a real-OD-accessor pass was reachable when `signatures_verified` gating makes that structurally impossible in this delta — replaced with a stub-provider reachability witness + an absent/tampered-only real-accessor witness); an explicit, disclosed narrowing of the pre-existing "every step after the first failure blocks" ordinal-halt contract (this delta's two new steps sit at earlier enum positions than the unchanged `VERIFY_HASH_CHAIN_LINK`, which must NOT become contingent on them); a resolver-factory wording fix (the factory never raises for an absent `key_identity_resolver` — "required" describes the downstream CP-side gate, not a construction precondition); and 4 clearance-marker/CLAUDE.md staleness fixes where round-1/round-2's spec corrections ("required not optional", "lone entry is a breach") weren't propagated into the once-written marker prose and axis CLAUDE.md pointer rows. **A fourth review round found 6 more (3 P1, 3 P2), fixed per advisor reconciliation 2026-07-23: a wrong hash primitive (round-3's membership check named OD's `compute_entry_hash(AuditPayload)`, corrected to IS's own `harness_is.entry_hash.compute_response_hash(StateLedgerEntry)`); a Pydantic construction-time coherence validator added to `RotationPairEvidence` (rejects `pair_present=True` with a missing period field, or `pair_present=False` with a populated one — illegal states unrepresentable); a stale Runtime spec change-note claim ("valid pair → step passes" through the real OD accessor, corrected to the explicit-incomplete disposition `signatures_verified=False` actually produces); `key_identity_resolver` added to `verify_rotation_6_steps`'s named parameter list (previously described only downstream, never in the signature); and a plan-text correction restating the ALREADY-LANDED §24.7 `verify_rotation_pairs` correlation-id check accurately (`uuid.UUID(...)`-parseable, not strict canonical-form) rather than overclaiming a guarantee PR #938's code doesn't enforce.**

**Two items REGISTERED rather than fixed, per advisor reconciliation (stop-the-arms-race call, 2026-07-23) — genuine residuals for leg iii, not defects in this leg's text:** (1) the IS-window↔OD-pair join is, by the ratified fork §2 item 4's own design, a correlation-id value-equality match with no additional cryptographic binding tying a specific IS entry to a specific OD entry — closing this fully would be an architectural extension of the ratified Option A design (a leg-iii-or-later question, not a leg-ii wording fix); (2) PR #938's landed `verify_rotation_pairs` accepts any `uuid.UUID`-parseable correlation-id string, not strictly canonical form (missing-hyphens or uppercase variants would pass) — a pre-existing gap in already-landed code, out of this spec+plan-only leg's scope to fix. **Four codex review rounds is the stopping point** (round 2's fixes caused round 3's findings; round 3's fixes caused round 4's findings — a self-reinforcing pattern, not residual defect discovery; recognized and stopped per `non-convergent-adversarial-hardening-arms-race`).
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
