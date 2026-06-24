---
artifact: design-substrate/Spec_Control_Plane_v1_55.md
version: v1.55
cleared_at: 2026-06-23T20:00:00-06:00
clearance_type: Phase-7-absorbed-via-operator-ratified-amendment
back_reference:
  - .harness/r-fs-1-b-fanout-output-replay-impl-design.md (✅ GATE RESOLVED + 🟩 STORE-as-authority build-time correction; the materializable impl design)
  - PR #719 (C1⊥C9 dyadic council DESIGN pass — the §25.12-D1 framing narrowed: non-attested keyed sidecar preserves D1 literally)
  - PR #721 (operator RATIFIED A — non-attested branch-index-keyed sidecar; the registered arc's operator gate, AUQ 2026-06-23)
  - PR for the B-FANOUT-OUTPUT-REPLAY PR1 core slice (this branch feat/b-fanout-output-replay)
merge_commit: <filled at merge>
reviewer_chain:
  - C1⊥C9 dyadic council (genuine dedicated-agent voices) + advisor red-team on the operator-gated §25.12-D1 rationale (PR #719) — corrected the "SECOND committed-invariant sacrifice" framing as a Class-3 over-claim (D1 scopes the attested ledger, not a non-attested recovery sidecar)
  - advisor — pre-substantive-work design review (Option-B crash-param pivot, shared-gate / wire-both-or-fail-closed traps) AND the synthesis-bearing crash-resume OPEN-PATH catch (resolution (a) fail-closed in PR1; the relax is PR2); reconciled the per-entry-drain (non-atomic) premise → ledger re-materialization is dedup-safe via IS idempotency
  - out-of-family Codex pre-merge review (3 rounds → convergent keystone) — round 1: orchestrator double-fire + recovered-branch ledger re-materialization; round 2: shielded-completion capture + override provenance + empty-steps material-diff; round 3 surfaced the GENERATOR — the output-only store schema made every non-clean-success disposition invisible (at-most-once fail-open class). Keystone fix (advisor): the store records terminal DISPOSITION (completed-with-output → fold; completed-no-output errored → recover-as-terminal; timed_out → FAIL CLOSED, timeout-replay follow-on) + changed-topology fail-closed + fsync-all-ancestors
  - Operator AskUserQuestion 2026-06-23 — chose A (the non-attested keyed sidecar) over REQUIRE-attestation (PR #721)
  - spec-writer apply pass (this arc, applied by the core agent holding the grounded materializable design + the as-built code)
supersedes: <none>
superseded_by: <none>
---

# Clearance — `Spec_Control_Plane v1.55`

v1.55 is an ADDITIVE delta over CP spec v1.54 documenting the **PR1 core slice** of the R-FS-1 standalone arc `B-FANOUT-OUTPUT-REPLAY` (operator-ratified A — non-attested branch-index-keyed recovery sidecar, #721). It changes **no contract, no enum, and no committed invariant**; §25.12 Point 1 + D1 + D1.b are PRESERVED LITERALLY.

- **§1 — non-attested branch-index-keyed fan-out recovery substrate.** The durable per-branch `EngineOutputStore` sidecar is the SOLE which-branches-completed authority on a fan-out crash-resume (the §25.12 D1.b ledger is BINARY — branch terminals buffer + drain atomically at the barrier — so a mid-fan-out crash leaves it empty). Per-branch-file keyed (N concurrent writers), RESERVE-before-COMMIT (store fsynced before the branch terminal ledger-append), gated to `EVENT_SOURCED_REPLAY` / `WAL_SEGMENT` ∧ store-bound by a SINGLE shared predicate (capture-gate ≡ consume-gate, no skew). The orchestrator (`steps[0]`) output is captured in the same pass (else `_determine_fanout_resume` fails closed when workers completed but the orchestrator output is missing).
- **§2 — crash-resume entry.** `_execute_workflow_body` reconstructs the synthetic `FanOutResumeState`/`PeerFanOutResumeState` from the store and threads it through the EXISTING B-FANOUT-PAUSE recovery path verbatim (skip terminal branches, recover outputs, re-dispatch the rest). Fail-closed on a present-but-unreadable branch or an inconsistent orchestrator. Covers recursive HIERARCHICAL levels (each re-enters `_execute_workflow_body`).
- **§3 — synthesis-bearing fan-outs remain FAIL-CLOSED on crash-resume (PR1 boundary).** Extends B-POSTJOIN's interim `post-join-synthesis-on-resume-unsupported` reject from the pause-resume path to the crash-resume path (a recovered synthesis fan-out would otherwise re-dispatch the synthesis FRESH — a non-reproducible W3-window aggregate). Reproducible synthesis-across-crash-resume (the synthesis self-hash + captured-output replay) is the registered PR2 follow-on slice.
- **§4 — §25.12 D1 PRESERVED LITERALLY.** Supersedes the v1.54 forward-looking "SECOND §25.12-D1 sacrifice" note (council-corrected #719 + operator-ratified #721): the recovery sidecar is non-attested (commits completion-order, reads branch-index, NOT in the §6 hash chain), so the attested ledger's branch-index append order is unchanged on both a no-crash and a resumed run. No second sacrifice.

## Caveats for Phase 7 consumers

- This is the **PR1 core slice** — the arc-ledger stays `registered` until the PR2 follow-on (synthesis self-hash + captured-synthesis-output replay + the §3 fail-closed RELAX) lands, which flips it `registered → built` → `closure_gate.py` G1.1 → R-FS-1 resolves.
- The synthesis-bearing crash-resume path is intentionally FAIL-CLOSED here; do not rely on synthesis-across-crash-resume until PR2.

## Notes

- Phase 7 consumers may rely on v1.55 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
