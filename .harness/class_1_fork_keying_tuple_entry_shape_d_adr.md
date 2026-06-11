# Class 1 (halt-execution) — keying-tuple ↔ entry-shape relationship (the unauthored ledger-schema D-ADR; IS C-IS-07 §7.4)

**Filed at:** Post-MVP closure Phase 0 scope-lock (2026-06-10), HEAD `37b7c80`
**Locus:** `design-substrate/Spec_Information_Substrate_v1.md` C-IS-07 §7.4 (line ~489; §7 body authored at v1.1, preserved verbatim through v1.3 HEAD) + `design-substrate/ADR-F2.md` §Consequences (c) (lines ~63-64, the named-but-unauthored "D-ADR on ledger entry schema fields" + "D-ADR on ledger entry idempotency-key composition fields").
**Status:** ✅ RATIFIED-AS-READING-(iii) — operator AskUserQuestion 2026-06-10, re-confirmed 2026-06-11 (the prior-session ratification was captured in-conversation but never applied; re-confirmed against the OPEN fork doc + code at HEAD). Applied at **IS spec v1.4** (NEW §7.5 ratifies reading (iii) + §7.4 deferral→resolution flip + stale F2-12 forward-cite refresh); clearance marker `.harness/clearance/Spec_Information_Substrate-v1_4-cleared-2026-06-11.md`. No behavior/contract change (the landed code already implements reading (iii) — `WriteKey` carries `thread_id`/`step_id`; `StateLedgerEntry` persists only the six fields + the v1.3 sidecar); the one src touch is doc-only — the `state_ledger_write.py` docstring's "§7.4 deferral / left to implementer" framing reconciled to the ratified reading (Codex review finding). The §7.4 portion of `R-CL-P4` is now UNBLOCKED.
**Routing:** IS-axis design-phase — **Class 1/2 fork → `.harness/` resolution, NOT a foundational ADR** per `[[adr-vs-fork-spec-plan-granularity]]` (this is a spec/plan-granularity reconciliation, not an F1–F5/D1–D6 foundational decision). Resolution cascades to an IS spec v1.x §7.4 amendment.
**Precedent:** `[[adr-vs-fork-spec-plan-granularity]]` · `[[stale-carry-text-disposition]]` (the §7.4 F2-12 cite is itself stale — see below) · `[[grounding-reveals-claude-closeable-slice-close-honestly]]`.

## The surface

The idempotent-write **keying tuple** `(thread_id, step_id, idempotency_key)` (C-IS-07 §7.1, Stripe-style) and the C-IS-05 **six-field entry shape** `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` coexist, but their **relationship was deferred** (§7.4 "Deferred to implementation discretion"). The spec leaves **four open readings** for how `thread_id`/`step_id` relate to the persisted entry — none selected:

- **(i)** embedded within `action_id`'s encoded metadata;
- **(ii)** implicit in run-context (not persisted as distinct fields);
- **(iii)** supplied as separate write-arguments, not persisted;
- **(iv)** per-workload-class extension fields.

At HEAD the implementation has *de facto* chosen something (`WriteKey` carries `thread_id`/`step_id` as write-args, not persisted on `StateLedgerEntry` — reading (iii)-ish), but **the spec never committed it**, so the contract↔code relationship is unratified. Committing a reading at Phase 7 = authoring the deferred D-ADR silently = X-AL-3.

## Stale-cite to refresh (bundle with the resolution)

§7.4 names *"F2-12 active engagement ... is the open downstream resolution path."* **F2-12 is CLOSED** (`F2-12_Closure_Declaration.md`, 2026-05-14) — but it closed a **different scope** (D1/D6 replay-trace-emission + cost-dedup; sub-scope (iii) used `idempotency_key` as a *trace-ingestion cost-dedup join key*, NOT the write-keying-tuple↔entry-shape reconciliation). The §7.4 cite is **stale-as-described** (`[[stale-carry-text-disposition]]`): it points at a closed council that resolved an *adjacent* question. **Refresh the §7.4 F2-12 cite in the same amendment** that resolves the reconciliation.

## Decision points

- **DP-1 — which reading (i)-(iv)?** Recommended: **ratify the de-facto reading (iii)** — `thread_id`/`step_id` are write-keying arguments (carried on `WriteKey`), idempotency-bearing but not persisted as distinct `StateLedgerEntry` fields; the persisted dedup discriminator is `idempotency_key`. This matches the landed code (low-risk, code-confirmed) and keeps the F-layer six-field shape inviolate (IS-AL-3). A fork should verify the landed code actually implements (iii) before ratifying.
- **DP-2 — per-workload-class extension (iv) coexistence.** Does (iii) preclude a future per-workload-class subclass adding `thread_id`/`step_id` fields? Recommended: **no** — the C-IS-05 §5 "field-shape extensibility commitment" already permits subclass extension; (iii) is the base contract, (iv) is an admissible per-class extension.
- **DP-3 — the sibling D-ADRs.** ADR-F2 §Consequences (c) also names a "canonicalization library binding" D-ADR (Cat-4 impl-discretion — RFC 8785 JCS per language). Recommended: **out of scope for this fork** (it's a genuine impl-discretion footer, already satisfiable; do not bundle).

## Recommendation

File this as a Class 1/2 fork; resolve by **ratifying reading (iii)** (code-confirmed) + amending IS spec §7.4 to state the chosen reading + **refresh the stale F2-12 cite**. This is a spec-prose reconciliation against landed reality (`[[spec-prose-plan-body-drift-pattern]]`), low blast-radius. Clearance marker owed at the spec-amendment PR.

## Closeout posture

~~Filed, not resolved. No code change is owed (the code already implements a reading); the work is **ratify-and-document** + the cite refresh. The §7.4 portion of `R-CL-P4` is **blocked** on this fork's ratification.~~

**RESOLVED 2026-06-11.** Operator ratified reading (iii) (re-confirmed against the conflicting OPEN fork doc per the memory↔artifact reconcile). Applied as a design-phase bundled-absorption arc: IS spec v1.3 → v1.4 (NEW §7.5 + §7.4 flip + F2-12 cite refresh), pointer bumps (root §2.3 references IS by filename so no bump; `harness-is/CLAUDE.md` §1.2 + `claude-artifact-pointers.md` §2.3 bumped to v1.4), this Status line, and the clearance marker. DP-1 (reading iii) + DP-2 (per-class (iv) coexistence admissible) applied; DP-3 (canonicalization-lib sibling D-ADR) left out of scope as recommended. No behavior/contract change (code already implements (iii)); one doc-only docstring reconciliation at `state_ledger_write.py` (Codex review finding).
