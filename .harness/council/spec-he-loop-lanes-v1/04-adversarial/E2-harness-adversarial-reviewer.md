# E2 — harness-adversarial-reviewer (Phase-7 pre-implementation mode; decorrelated: did not read 01-/02-/03-)

## Verdict

**LOOP-BACK** — Class 1: 3 · Class 2: 3 · Class 3: 1.

## Class 1

| id | contract | quote | attack | required fix |
|---|---|---|---|---|
| ADV-F1 | C-HE-03 §5 vs C-HE-03 Invariants vs C-HE-20 §2 vs ADR-HE-1 O3/D8 | "`pending` + aged (> 24 h …) → silent reclaim" vs "No path reclaims a reservation on TTL expiry" vs "The TTL MUST NOT trigger reclaim, release, or any state change" | The `pending`-tier rule is a pure elapsed-time transition with no ground truth to check (no PR yet) — exactly a TTL-driven reclaim the same contract and C-HE-20 forbid. ADR-HE-1 O3's acceptance test: "Confirm no path reclaims on TTL expiry; if one does, the value becomes safety-critical." D8 covers only the `open`+stuck tier; §12's O3 row over-reads it onto `pending`. | (a) carve `pending` out of the invariant with a change-note, reconciled against O3's safety-critical test, or (b) remove `pending`-tier auto-reclaim; route aged `pending` through HITL-notify only. |
| ADV-F2 | C-HE-30 vs §0.3 vs §6 S3 vs §8.1 | C-HE-30 has only `### Contract`; §6 marks S3 "Gates lane safety: yes" | The sole contract with zero verification surface — no Invariants/Verification block, no §8 row, no §8.1 row — yet C-HE-13 §1's `lanes-phase0-check` is defined by §8.1 rows; the store audit is an implicit precondition, the exact failure C-HE-13 §1 was written to foreclose. | Add `### Invariants` + `### Verification` (static check that the audit doc exists and enumerates exactly 8 stores with one authority each) and a `phase0` manifest row. |
| ADV-F3 | §10 vs §5 C-HE-17 row | §10: "the Codex-projection tree (`AGENTS.md`/`.agents/`)" out of scope; §5 C-HE-17: "`AGENTS.md`/R1 checklist restatement of #3 (doc)" | `AGENTS.md:56-57` really carries invariant #3 ("Decorrelation flips with authorship … use `just gemini-review` as the out-of-family artifact reviewer"). §5 instructs editing a file §10 forecloses. | Drop `AGENTS.md` from the C-HE-17 row; route the #3 restatement through in-scope `.claude/skills/*` docs and file a companion Codex-projection back-flow item; or narrow §10. |

## Class 2

| id | contract | quote | attack | required fix |
|---|---|---|---|---|
| ADV-F4 | C-HE-09 §2/§3 | "control markers … MAY stay per-lane" / "key on `lane_id`" | If ACTIVATE stays per-lane, the shared-venue reducer never sees it; the "key on `lane_id`" branch is unbuildable — no `lane_id` column exists on any `loop_status.md` row (`loop_log` writes 3 columns, `:82`). | Either ACTIVATE rows also land in the shared venue with a named `lane_id` column (as C-HE-10 adds `cause_signature`), or strike the `lane_id` disjunct and commit to "MUST NOT reset globally-visible HIL rows". |
| ADV-F5 | C-HE-13 §1 vs C-HE-08 §8.1 row | "live step is operator-gated and recorded, not a pytest row" | S3 and S4c both contain items `lanes-phase0-check` cannot observe; a pilot could pass the gate with branch protection never applied — X9's server half reintroduced. | Add a phase0 read-only probe (`gh api …/branches/main/protection` parsed against C-HE-08 §2's required set), or narrow C-HE-13 §1's claim and name the carved-out attested items. |
| ADV-F6 | C-HE-04 §3 | "MUST NOT return with the arc's queue entry absent … Worktree disposal MUST NOT be able to lose a capture silently" | Interleaving: A `_claim_arc` → `append()` succeeds locally → A is SIGKILLed / worktree torn down before `os.replace(taken, path)` `:754`. The re-publish is a postcondition inside the still-running process and cannot fire. `_recover_dead_claims()` later restores the entry; B re-drains and re-appends into B's ledger; A's row (with computed phases/outcomes) is orphaned — a third state the Invariant says does not exist; none of the five interleavings (i–v) is an external kill. | Name the enforcement site (a teardown contract: MUST NOT dispose a worktree until `drain()` returned AND the entry is confirmed present/committed) and add a sixth AC#2(a) interleaving killing between `append()` and the restore; or accept the residual explicitly in §10. |

## Class 3

| ADV-F7 | C-HE-24 header `[R: L0.2′]` vs §12 | no `L0.2′` row in §12 | Add an `L0.2′` row pointing at the HE-3 §6 disposition, or drop the standalone tag. |

## [V] audit

Held: `arc_metrics.py:44-45,516,602-610,624-626,666,746,754,79` · `codex_context_guard.py:774-781` · `ci.yml:536,542` · `permission-guard.sh:427` · `agy_review.py:612` · `main` unprotected (404 protection, 404 rules) · git 2.39.5 · `arc_disjoint_check.py`/`codex_review.py`/`review_wrapper_common.py` absent · `two-lane/SKILL.md:18` (off by one) · forward register: `files:` 0. **Not re-verified:** C-HE-19's `CANCELLED` zero-occurrence claim. **Reported "held" but WRONG (orchestrator re-derived, converging with Codex C3-01):** "`flock`/`fcntl` zero occurrences in `tools/hooks/`" — 7 files match (`capture-failure.sh`, `subagent-validate.sh`, `loop-gc.sh`, `lib.sh`, three tests).

## Verification-as-falsifier audit

C-HE-02 §6 "revert token compare to path-only" — ambiguous: O_EXCL already prevents both winning; the plan must pin down a literal generation-field comparison or the probe is not a falsifier · C-HE-03 §5 — cannot go RED until ADV-F1 is resolved · C-HE-15 §1 — yes · C-HE-24 §2 — yes · C-HE-04 E9 witness — yes for the in-band race, not the kill sub-case (ADV-F6) · C-HE-06 AC#2(c) — yes · C-HE-09 reducer probe — conditional on ADV-F4.

## Rejected candidates

T6 (composes safely with `--match-head-commit` + ground truth) · T4 (clean split) · C-HE-06 §7 · §6 acyclicity (walked; no cycle) · C-HE-17 D6 restatement · C-HE-08 live state · C-HE-13 §5 · cross-namespace collision (none) · CP-AL-1 leakage (none) · C-HE-19 honesty framing · T9 (council territory).

## Disposition

LOOP-BACK to spec authoring; fix F1–F3 with a dated change-note; resolve F4–F6 in the same pass; F7 one-liner.
