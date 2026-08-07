---
artifact: design-substrate/Implementation_Plan_Information_Substrate_v2_9.md
version: v2.9
cleared_at: 2026-08-07T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-Class-2-fork-ratification (B-57 spec leg; implementation-planner absorption pass per CLAUDE.md §4.3 + §4.5)
back_reference:
  - .harness/class_2_fork_b57_direct_append_writer_owned_opt_in.md (RATIFIED 2026-08-07 — Reading A; §11 ratification stamp)
  - design-substrate/Spec_Information_Substrate_v1.md v1.13 (C-IS-07 §7.6.1 — the authorizing contract, same PR)
  - .harness/clearance/spec-information-substrate-v1-13-cleared-2026-08-07.md (sibling marker, same PR)
merge_commit: pending (pre-merge at filing time; B-57 spec leg PR)
reviewer_chain:
  - operator ratification (2026-08-07) — Reading A
  - implementation-planner absorption pass (2026-08-07) — per-site classification table re-grounded by direct read at HEAD acfc1afa; reachability sweep re-run; two fork count claims corrected rather than carried
  - out-of-family review to convergence on the landing PR (recorded at the PR thread)
supersedes: implementation-plan-information-substrate-v2-8-cleared-2026-07-22.md
---

# Clearance — Implementation_Plan_Information_Substrate v2.9 (`B-57` spec leg)

v2.8 → v2.9 absorbs **IS spec v1.13 C-IS-07 §7.6.1** into the ONE existing unit that owns the write contract — **U-IS-11**, amended with ACs **#14–#20** (with **#14-bis**) and PD-8-probed witnesses. **ZERO new atomic units, ZERO new nodes, ZERO new edges, ZERO new auxiliary types, ZERO CXA rows, ZERO IS-outbound edges**; ACs #1–#13 (the v2.1 baseline plus the v2.7 B-48 additions) and every other unit body are PRESERVED VERBATIM. The new criteria cover: the per-call-site election with **no writer-side mode** permitted; the **negatively demonstrable** default-preservation property (a non-electing direct append persists the caller's value and still refuses an inversion — if that cannot be shown, the election has silently become a default); the eligibility rule and the event-time `RETAIN` at `as_is_wiring.py:129`; the **sentinel-docstring refresh** at `state_ledger_write.py:79`–`:80` (the OTHER prose carrier of the restriction §7.6.1 replaces — named at the spec's own change-note and therefore owed, not left to rediscovery); per-site table conformance; the two injection-caveat resolutions; the `audit_writer` resample-retry disposition; and the `shadow_git_rollback` `restored_at` decoupling pin.

**What was reviewed.** v2.9 carries the **per-site classification table** IS spec v1.13 §7.6.1 deliberately routes to the plan (*"this contract states the RULE, the plan states the ROSTER"*). Every one of its 14 rows was re-resolved **by direct read at HEAD `acfc1afa`**, and every cited CODE LINE re-read byte-identical to what the fork filing's §3(ii) table recorded; the `emit_sibling_ledger_entry` zero-non-test-caller sweep was re-run independently (19 hits, exactly 3 non-test — definition plus two docstring mentions), confirming the DEFER disposition for `sibling_ledger_entry_composition.py:163`. **Two of the fork filing's own count claims were CORRECTED rather than carried** (recorded at §2.1 and at the filing's §11.3): its *"fourteen rows, twelve SITES"* does not reconcile with a table whose two folded companions are already folded, and its *"≈8 conversions"* under-counts an ELECT cell that enumerates **ten** payload-construction rows. Neither correction changes a disposition, a reading or any zero-cost line — both change the size of the surface the impl leg must convert.

**Caveats for Phase 7 consumers.** **SPEC-LEG ONLY** — no code lands here, and `B-57` remains **OPEN**. The §2.1 table's line numbers **will drift**: AC #17 requires the impl arc to re-resolve every row **by content** at its own HEAD and record any drift rather than silently normalizing it. **Council is probe-resolved with a LIVE trigger (§0.6):** if the impl leg judges either injection-caveat site (`audit_writer` / `cost_attribution_f2_write`) **RETAIN**, that produces an exposed direct caller of exactly the shape `B-112` step (3) tests for, and the C3 ⊥ C11 determination must be re-run before any `_CLOCK_SKEW_TOLERANCE` change is authored. No CP or Runtime plan delta is owed by this arc — the converted sites consume the C-IS-07 §7.1 write contract they already import, adding no unit and declaring no edge.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
