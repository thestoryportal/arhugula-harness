# Consolidated reconcile — C7 observability

## Dispositions

| G | disposition | wording / evidence |
|---|---|---|
| G11 | RECONCILE | Accept (a)–(f). Add: (1) "`finding_id` is not stable across `head_sha` for the same defect — acceptable for every cited consumer (same-`head_sha` `unique_catch`, `(pr, head_sha, verdict)` join, within-`head_sha` disposition lineage); cross-`head_sha` same-defect tracking is out of scope for v1 (forward item: content hash over `location`+`finding_type`)." (2) "`producer`, `reviewer_identity`, `deterministic_check_id` MUST NOT contain `:` (the `finding_id`/`code` delimiter); the emitter validates at write time." |
| G12 | ACCEPT with corrected premise | At HEAD `arc_type` is already populated: 6/18 `inventing`, 12/18 null, 0 `applying`; `concurrent_lanes` 0/18. Honest first-months AC#10 claim: exactly two joint cells populated — `(N=1, inventing)` n=6, `(N=1, null)` n=12; every N≥2 cell and every `applying` cell starts at 0 → descriptive counts only, no effect estimate. |
| G13 | RECONCILE | `NOTIFY` sound. The trailing-column shape (C-HE-10's `cause_signature` 5th column AND G13's `lane_id`) is NOT safe against `_loop_pending_hil_rows()` — see defect. `delivered_generation` MUST NOT be a new mutable file: make it an append-only row kind `COALESCE-DELIVERED` on `loop_status.md` (`| ts | COALESCE-DELIVERED | <cause_signature> | <generation-id> |`); a group is "delivered" iff such a row exists at/after the group's `first_seen`. |
| G14 | ACCEPT + one addition | Accretion-at-drain composes with G6 (accrete during `open`, fold at drain-time `append()`). Add to N6: "a `phases.verify` span whose round terminated `REVIEWER_UNAVAILABLE` MUST be excluded from the denominator (or bucketed as `phases.verify_unavailable_s`)." |
| G15 | RECONCILE | Kill reducer IS computable from `merge-gate-log.jsonl` alone (`round_n` in envelope; same-`head_sha` rows in one file). But the OC parenthetical is WRONG: P(X<3 | n=30, p=0.10) = 0.0424+0.1413+0.2277 ≈ **0.411**, not 0.18. Corrected table (n=30, kill if <3): p=0 → 1.000; .05 → .812; .10 → .411; .15 → .151; .20 → .044; .25 → .011. (≈0.18–0.20 at p=0.10 is what kill-if-<2/30 gives.) Pick and print the number that reproduces. |

## Defects the proposed folds introduce

| G | failure | sev | fix |
|---|---|---|---|
| G13 | Verified by `awk` repro: `_loop_pending_hil_rows()` (`loop_lib.sh:175-186`) rejoins `s=$4; for(i=5;i<NF;i++) s=s"|"$i` — written to restore escaped-pipe splits, not to skip a legitimate trailing column. Any column appended AFTER `detail` (C-HE-10's `cause_signature`, G13's `lane_id`) is glued onto the rendered detail with a stray `|` (repro output: `detail=[R-410 — blocked until R-300 decides | merge-door-lease-acquire:transient-retry:lease_contended ]`). `loop_skip_set()` unaffected (never reads past `$4`). | 2 (verified) | Name the fix in the fold: (a) fix column order with `detail` LAST and structured columns BEFORE it, or (b) bounded rejoin with a named trailing-column constant. C-HE-10 already specifies the broken shape. |
| G15 | Stated OC number does not reproduce (above). | 2 | Replace with the corrected table; choose (a) accept ≈0.41 at p=0.10, (b) kill-if-<2/30 (≈0.18), or (c) C8's SPRT. |
| G11 | no defect found after checking `finding_id` non-persistence vs every cited consumer and `disposition_actor≠producer` enforceability once the `:` charset gap is closed. | — | — |
| G12 | no defect found after recomputing the live ledger population and confirming the join point (sibling-`open` count at the `pending→open` flip under G1's versioned files) is a benign best-effort snapshot. | — | — |
| G14 | no defect found after tracing G6's ordering against G1's CAS. | — | — |

## Verified at HEAD

`arc_metrics.py:45` sole path constant · `:765-775` `read_ledger()` bare `json.loads`, no kind filtering (tolerant) · `:810-832` `dict.get()` access, additive-safe · no other reader of `arc-metrics.jsonl` repo-wide (non-test) · `.harness/merge-gate-log.jsonl` absent (new file, no reader to break) · ledger 18 rows: `arc_type` `Counter({None:12,'inventing':6})`, `concurrent_lanes` 0/18 · `loop_lib.sh:77-85`, `:134-157` (`k=$3` only), `:165-186` (rejoin loop; repro'd) · spec `:494` 8-field core untouched by the 12-field envelope · spec `:479-482` C-HE-10 trailing column already specified.

## Reconciled-to-zero?

NO — two mechanical items: G13 (reducer/column fix + `COALESCE-DELIVERED` venue) and G15 (OC table + threshold choice). Neither Class 1.
