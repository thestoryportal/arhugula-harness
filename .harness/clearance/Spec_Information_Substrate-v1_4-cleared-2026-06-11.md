---
artifact: design-substrate/Spec_Information_Substrate_v1.md
version: v1.4
cleared_at: 2026-06-11T00:30:00-06:00
clearance_type: spec-writer-apply-pass
back_reference:
  - .harness/class_1_fork_keying_tuple_entry_shape_d_adr.md (the fork this delta ratifies — reading (iii))
  - Project_Roadmap_v1.md §5.15 R-CL-P4 (spec-completion deferrals; keying-tuple D-ADR §7.4 sub-part)
  - .harness/post-mvp-full-closure-plan-v1.md (Phase P4 — keying-tuple ↔ entry-shape reconciliation)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - operator AskUserQuestion 2026-06-10 (reading (iii) ratified) + re-confirmation 2026-06-11 (memory↔artifact reconcile against the OPEN fork doc)
  - advisor() decision-fork pass (reconciled the memory "ratified" claim vs the OPEN fork docs; confirmed surface-the-gate, asymmetric fork treatment)
  - empirical code-grounding (WriteKey carries thread_id/step_id; StateLedgerEntry persists only the six fields + the v1.3 sidecar — reading (iii) code-confirmed)
  - out-of-family Codex review (pending — this arc)
  - design-phase bundled-absorption posture (workspace CLAUDE.md §11.4)
supersedes:
superseded_by:
---

# Clearance — `Spec_Information_Substrate v1.4`

v1.4 resolves the C-IS-07 §7.4 "Deferred to implementation discretion" deferral of the relationship between the §7.1 idempotent-write keying tuple `(thread_id, step_id, idempotency_key)` and the C-IS-05 six-field entry shape. The deferral named four open readings (i)–(iv) and never selected one; at HEAD the implementation had *de facto* chosen reading (iii) but the spec never committed it (the contract↔code relationship was unratified). Per operator ratification (R-CL-P4; fork `class_1_fork_keying_tuple_entry_shape_d_adr.md`), v1.4 ratifies **reading (iii)**: `thread_id`/`step_id` are write-arguments carried on the write-time `WriteKey` structure, **not** persisted as distinct `StateLedgerEntry` fields; `idempotency_key` is the sole persisted entry-level dedup discriminator.

This is **code-confirmed** at HEAD: `harness-is/src/harness_is/state_ledger_write.py` `WriteKey` carries `thread_id`/`step_id`; `harness-is/src/harness_is/state_ledger_entry_schema.py` `StateLedgerEntry` persists `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` + the v1.3 `procedural_tier_snapshot_ref` D-derivative sidecar — none of which is `thread_id`/`step_id`. The C-IS-05 §5 six-field shape is **inviolate** (IS-AL-3); reading (iii) adds no entry field. The §5 "Field-shape extensibility commitment" reading (iv) per-workload-class extension remains admissible and composes with (iii).

This is a **design-phase bundled-absorption arc** (`CLAUDE.md` §11.4): the design-substrate spec delta lands with its governance-pointer cascade (`harness-is/CLAUDE.md` §1.2 + `.harness/claude-artifact-pointers.md` §2.3 bumped v1.3 → v1.4; root `CLAUDE.md` §2.3 references IS by filename `_v1.md`, which is unchanged, so no bump there), the fork-doc status flip (OPEN → RATIFIED), and this marker. **NO behavior/contract change** — the landed implementation already implements reading (iii); ZERO new contract / ZERO new C-IS-NN field; the six-field shape and read/write contracts are untouched. The one `harness-is/src` touch is **doc-only**: the `state_ledger_write.py` module docstring (which described the relationship as a "§7.4 deferral / left to the implementer") is reconciled to the now-ratified reading (iii) framing, so an implementer reading the code does not see the old unresolved contract (Codex out-of-family review finding, this arc). This delta is a spec-prose reconciliation against landed reality (`[[spec-prose-plan-body-drift-pattern]]`).

A second amendment refreshes a **stale forward-cite**: the v1.1–v1.3 §7.4 deferral named *"F2-12 active engagement … the open downstream resolution path."* F2-12 is CLOSED (`F2-12_Closure_Declaration.md`, 2026-05-14) on an **adjacent** scope (D1/D6 replay-trace-emission + cost-dedup, where `idempotency_key` is a trace-ingestion cost-dedup join key) — it never owned this write-keying-tuple ↔ entry-shape reconciliation (`[[stale-carry-text-disposition]]`). The §7.4 multi-seam T-perm-2 table and the §[carry-forwards] [CF-1] F2-12 line are preserved verbatim as point-in-time-accurate historical record; only the live deferral clause is flipped to a §7.5 pointer.

Verification: `overlay-check` clean (ZERO new contract; the only src touch is a docstring, no behavior change); the reading (iii) statement matches HEAD code (re-grounded this arc — `WriteKey`/`StateLedgerEntry`); no cross-spec drift (the keying tuple was never a persisted cross-axis join key — `idempotency_key` is, and it is unchanged at §5/§6/§7.1–§7.3/§10); the sibling-spec F2-12 hits are the legit D1/D6 replay/cost-dedup scope or archives, not this defect.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- v1.3 + v1.2 + v1.1 + v1 bodies are PRESERVED VERBATIM (delta-only convention); v1.4 records only the §7.4→§7.5 reconciliation + the F2-12 cite refresh.
- The companion R-CL-P4 IS-fork (`class_1_fork_prompts_management_surface_active_prompt_version.md`, prompts/`active_prompt_version` third hash component) was ratified at FULL prompts-management scope and is a **separate, larger design-authoring arc** (systems-architect/council) — NOT in this clearance.
- See `.harness/clearance/README.md` for marker discipline.
