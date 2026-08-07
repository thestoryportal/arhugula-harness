---
artifact: design-substrate/Spec_Information_Substrate_v1.md
version: v1.13
cleared_at: 2026-08-07T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-Class-2-fork-ratification (B-57 spec leg; spec-writer apply pass per CLAUDE.md §4.3 + §4.5)
back_reference:
  - .harness/class_2_fork_b57_direct_append_writer_owned_opt_in.md (FILED 2026-08-07 PR #1253; RATIFIED 2026-08-07 — Reading A; ratification stamp at that filing's §11)
  - .harness/forward-register.yaml — B-57 (remedy owner; registered_finding → open at this PR) + B-112 (cause-and-evidence record, PR #1241)
merge_commit: pending (pre-merge at filing time; B-57 spec leg PR)
reviewer_chain:
  - operator ratification (2026-08-07) — Reading A (per-call-site opt-in); Reading B (HOLD) declined
  - spec-writer apply pass (2026-08-07) — grounding pass at HEAD acfc1afa before authoring; all fourteen fork §3(ii) classification rows and every state_ledger_write.py cite re-resolved by direct read; the emit_sibling_ledger_entry reachability sweep re-run independently
  - out-of-family review to convergence on the landing PR (recorded at the PR thread)
supersedes: spec-information-substrate-v1-12-cleared-2026-07-22.md
---

# Clearance — Spec_Information_Substrate_v1 v1.13 (`B-57` spec leg — per-call-site writer-owned election on DIRECT append surfaces)

v1.12 → v1.13 extends the EXISTING **C-IS-07 §7.6** with a NEW **§7.6.1**: a DIRECT-append call site MAY **elect** writer-owned timestamp sampling by supplying the EXISTING `WRITER_OWNED_TIMESTAMP` sentinel as its write payload's `timestamp`, whereupon the persisted `timestamp` is sampled by the writer inside the write serialization point — the same authority and the same by-construction monotonicity §7.6 already commits for the buffered/branch-drain surface. **The election is PER CALL SITE — never a default, never a mode on the writer**: any direct producer that supplies another value retains caller-supplied semantics byte-verbatim, and no surface discriminator, mode flag, path gate or configuration key is added. §7.6.1 also pins the **eligibility rule** (elect only where the timestamp means *when the entry was appended*; where it means *when the event happened*, caller-supplied semantics are REQUIRED and an out-of-order refusal is the honest outcome), a **demonstrable-negatively** default-preservation property, and an explicit does-NOT-authorize list. **NO new contract number is minted** — a spec leg cannot mint one, and none is needed.

**What was reviewed, and what was preserved.** The §7.6 `"Surfaces that do NOT change"` and `Registered residual (surfaced, NOT absorbed)` paragraphs are **PRESERVED VERBATIM**; ONE added status paragraph records that the residual's demanded back-flow has now been **performed and DISCHARGED** in this narrow per-call-site form, so a later reader cannot mistake the preserved text for a live prohibition (the §7.5-over-§7.4 precedent). The §7.1 row-7 `"Timestamp authority"` cell gains a **cross-reference-only** clause naming §7.6.1 — zero new semantics, authored solely so the summary row does not become stale-as-described. Everything else is byte-unchanged: §1–§4, §5 and §5.1–§5.6, §6 hash-chain construction and canonicalization, §7.2–§7.5, §7.7, §8, §9, §10 seam exports, and the `[carry-forwards]` / `[traceability]` / `[coherence pass]` sections. **ZERO hash / canonicalization / migration / `snapshot_hash` impact** (no field added, no shape changed, no recipe touched — only which instant a consenting call site records), **ZERO CXA rows** (no new package edge, no new typed seam — determined, not assumed), **ZERO new plan units**.

**Caveats for Phase 7 consumers.** This is a **SPEC-ONLY** leg: no code lands here. The per-site ELECT / RETAIN / DEFER roster is deliberately **NOT** in the contract — it lives at `Implementation_Plan_Information_Substrate_v2_9.md` §2.1 (U-IS-11) and is re-grounded at the impl arc, because a code-inventory pinned in a cleared contract would guarantee stale-carry. `B-57` remains **OPEN** after this leg: the 10 ELECT conversions, the two injection-caveat resolutions, the `audit_writer` resample-retry disposition, the `shadow_git_rollback` `restored_at` decoupling pin and the two-process contention witness are the separate impl leg. **Council is probe-resolved, with a LIVE trigger** — if the impl leg judges either injection-caveat site RETAIN, the C3 ⊥ C11 determination must be re-run before any `_CLOCK_SKEW_TOLERANCE` change is authored (recorded at the plan's §0.6).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
