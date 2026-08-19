# Durable store audit — H_E loop + lanes (C-HE-30)

Repo `07b6bc760` · 2026-08-19 · plan S3 / U-HE-14 · owed before C-HE-03 / C-HE-06 code lands (spec §6: S3 before S4b/S4c).
Witness: `tools/test_store_audit.py` (phase0; `just lanes-verify` row `C-HE-30`).

**Rule.** Exactly one authority per fact. Any fact found with two authorities is resolved by demoting one to a derived copy *before* the corresponding contract is implemented. No runtime path creates a store this page does not list — the witness greps every `QUEUE_DIR` / `.harness` path literal in `tools/arc_metrics.py`, `tools/merge_door.py`, `tools/reservations.py`, `tools/hooks/loop_lib.sh` (the S4 modules re-run the row when they land) and fails on any token absent here.

## The eight stores

| Store | Venue | Authority for |
|---|---|---|
| Queue entries (`QUEUE_DIR/*.json` captures / `QUEUE_DIR/*.taken` claims; `.with_suffix(".taken")` is the claim rename) | `QUEUE_DIR` (default `~/.gstack/projects/arhugula-v2/arc-metrics-queue`; `ARC_METRICS_QUEUE_DIR` override, C-HE-05) | "capture exists and is not yet in committed history" |
| Reservation files (`reservations/<arc_id>/<gen>.json`, immutable full snapshots; head = highest gen) | `QUEUE_DIR` | arc landing state (`pending/open/terminal`), `concurrent_lanes_at_open` sensor, `arc_type` at open, accreted `phases` |
| Merge-door lease (`merge-door/LEASE`) | `QUEUE_DIR`-adjacent | who is landing now; `merge_attempted_at`; `state ∈ {held, blocked}` |
| `.harness/arc-metrics.jsonl` (per-worktree until committed; `LEDGER`, `ARC_METRICS_LEDGER` override) | `REPO` | arc rows (`record_kind=arc`, one per `arc_id`), per-round outcomes, phases (folded at drain); `arc_type_open/close/declared_at` (C-HE-25) |
| `.harness/merge-gate-log.md` + structured sibling `.harness/merge-gate-log.jsonl` | `REPO` | gate verdicts and every finding-class row. The JSONL is the authority for EVERY C-HE-24 record landing there (gate emissions AND the review-wrapper / finding rows, which have no md twin); the md carries only the gate-summary line — a human projection written in the same producer step as the gate emission (`merge_gate_log.emit_gate_row` under one `flock`, JSONL first) and re-emitted from the JSONL at the next gate run when its write failed (`reconcile_orphans`, C-HE-23 §2) — never a second authority |
| `loop_status.md` (HIL/NOTIFY rows at the shared venue `QUEUE_DIR/../loop_status.md`; today `.harness/loop_status.md` under `hook_project_dir()` — control markers per-lane under the same dir) | shared / per-lane | operator-attention state; run-scoped skip-set |
| Finding emission (`codex_context_guard.Finding` projection of the C-HE-24 record) | CI/stdout | derived from the 8-field record — never authored independently |
| Committed history on `MERGED_REF` | git | the only proof that a row is durable |

## Derived families + new-fact carriers (no second authority for an existing fact)

The C-HE-30 clearance-fold note adds these families under the invariant "none a new authority for an **existing** fact". Audited row by row, they are of three kinds — a **derived** copy/history of a store above (recomputable from it), a **part of** one of the eight stores (a sidecar file that carries some of that store's own fields), or the **sole carrier of a NEW coordination fact** this spec introduces (exclusive-create registries, counters, allocators, live mode state — no other store holds the fact, so the file *is* its one authority). All three satisfy the invariant; the third is recorded honestly as an authority rather than mislabelled "derived". The eight-store count is the authority set for the facts HE-1 §5 enumerates; new-fact carriers are durable stores in their own right, enumerated here (C-HE-30 Invariant 1; spec v1.3 X3 says so in the count sentence) and distinct from the eight.

| Family | Path | Relation | Derived from / sole carrier of |
|---|---|---|---|
| Reservation generations | `QUEUE_DIR/reservations/<arc_id>/<gen>.json`, `.<gen>.<pid>.tmp` | part of store 2 (the reservation files ARE the store) | the highest generation is the authoritative current reservation (store 2's own row); generations below head are its immutable history by construction (GC prunes below head) — there is no separate file they derive from |
| Reservation sequence allocator | `QUEUE_DIR/reservations/.seq/<n>` | sole carrier (new fact) | "the highest `seq` number ever allocated" (`alloc_seq`: exclusive create of the next `n` BEFORE the generation that carries it is written — a crash between the two leaves an allocation no snapshot records, so it is not recomputable from the generations) |
| Lease transition marker | `QUEUE_DIR/merge-door/transition.<lease_token>` (one per token, ever; payload `{pid, host, target_action ∈ {release, reclaim, unblock}, created_at}` + `fresh_lease` (the replacement token + payload) on `reclaim`) | sole carrier (new fact) | "a transition of this token is in flight, by whom, toward what — and, for a reclaim, the fresh lease to publish" (C-HE-06 §6) — the marker winner is the only party allowed to move `LEASE`, and a third party completes a dead creator's declared `target_action` (publishing `fresh_lease` on reclaim) from this payload alone; not reconstructible from `LEASE` once it has moved |
| Lease per-token sidecars | `QUEUE_DIR/merge-door/LEASE.<token>.<suffix>` for suffix ∈ {`attempted`, `blocked`, `refresh`} | part of store 3 (the lease) | the immutable `LEASE` file keeps its base values; `merge_attempted_at`, `state: blocked` + reason, and refresh-continuation state live in these sidecars and `read_lease` merges them into the one lease view — live recovery state, never recomputable, so they ARE the lease store's fields, not history |
| Lease transition history | `QUEUE_DIR/merge-door/released.<token>`, `reclaimed.<token>` | derived | the lease (the renamed-aside `LEASE` payload itself = audit history of completed transitions; GC 30 d) |
| Door attempt rate-window | `QUEUE_DIR/merge-door/attempts/<lane_id>/<ts>` | sole carrier (new fact) | "how many landing attempts each lane made in the window" (C-HE-06 rate limit) — exclusive-create per attempt; nothing else records attempts |
| Attestation-tier counter | `QUEUE_DIR/merge-door/tier-clean-cycles/<token>` | sole carrier (new fact) | "how many consecutive clean cycles since the last miss" (C-HE-06 §10 tiering) — one file per clean cycle, written by `land()` |
| Lane index registry | `QUEUE_DIR/lanes/<k>` | sole carrier (new fact) | "which lane indices are taken" (C-HE-11) — exclusive create at lane-init, released at teardown |
| HIL coalescing delivery claims | `QUEUE_DIR/hil-deliveries/<gen-id>` | sole carrier (new fact) | "this HIL generation was delivered once" (`loop_hil_deliver`, exclusive create); the `COALESCE-DELIVERED` row in `loop_status.md` is the audit twin, not the claim |
| Loop control markers (per-lane) | `.harness/.loop-active` (loop on), `.harness/.loop-iter` (Stop-continue counter), `.harness/.loop-halt` (stand-down signal) | sole carrier (new fact) | "is this lane's loop on / how many auto-continues remain / was a stand-down signalled" (`loop_activate` / the Stop hook) — control state, not HIL state; the `loop_status.md` reduction never reads them |
| Mechanized-check runtime state (C-HE-31 §4d; lands with Arc 4, not yet on main) | `.harness/mechanized-checks-state.json` | sole carrier (new fact) | "each mechanized check's live `kind` (advisory/blocking) + its rolling demotion window". A **promotion** is recorded ONLY here (no row is emitted), so the file is not reconstructible from C-HE-24 rows; a **demotion** additionally emits a `record_kind=gate_demotion` + `NOTIFY` row — an audit trail, not a second authority. §8.1 carries only the policy + each check's initial `kind` |
| Mutation-probe run log — **DERIVED** | `.harness/mutation-probe-log.jsonl` | derived | `tools/mutation_probe.py` exits (one digest-bound row per run; `just mutation-probe-coverage-check` reads it; the `# mutation-probe:` annotations in the test files stay the authority for *which* probes exist) |
| Structured gate sibling | `.harness/merge-gate-log.jsonl` | part of store 5 (the authority half) | listed above with its markdown twin — JSONL-first, same step; the md line is the gate-summary projection |

*Grounding note (U-HE-14 → spec v1.3 X3).* The v1.2 C-HE-30 clearance-fold parenthetical read "all derived from the authorities above, none a new authority for an existing fact". Audited row by row, its first clause did not hold for the rows marked *sole carrier (new fact)* — each holds a coordination fact with no other carrier (a transition in flight, attempt counts, clean-cycle counts, lane indices, delivery claims, control markers, promotion state) — while its operative invariant (no **existing** fact gains a second carrier; the authority set for existing facts stays the eight above) holds for every row. Rather than certify against an imprecise sentence, change-note **X3** (spec v1.3, same PR) re-words that parenthetical to say exactly this; C-HE-30's contract table, Invariants and Verification are unchanged. The S4 units that create these files re-run this row.

## Transient writer-exclusion + staging artifacts (NOT stores)

Short-lived files that carry no fact beyond "a writer is in flight" — never read for state, never an authority, safe to remove when stale.

| Artifact | Path | Lifetime |
|---|---|---|
| Ledger writer claim (C-HE-02 §1+§2 CAS; `append` and `relabel` exclude through it) | `QUEUE_DIR/.ledger-claim-<key>` (`QUEUE_DIR/.ledger-claim-*`; `QUEUE_DIR`-adjacent, never under `REPO`) | one write; reclaimed when dead |
| Gate emission lock | `.harness/merge-gate-log.jsonl.emit.lock` (`flock`; emissions + reconcile serialized) | one emission |
| Lens scratch (binding input) | `.harness/tmp/` (`LENS_SCRATCH`; a lens's fenced JSON must RESOLVE under it) | one gate round |
| Atomic-write stagers | `.<name>.<pid>.tmp` next to the target (`LEDGER`, queue entries; `arc_metrics.py` only — `loop_status.md` is appended in place under the mutex below) | one `os.replace` |
| Status-ledger mutex | `.harness/.loop-status.lock` (fd 8; lib.sh worktree-mutex pattern) | one append |

## Referenced pre-existing workspace stores (not created or extended by this spec)

`tools/hooks/loop_lib.sh` *reads* `.harness/forward-register.yaml` and `.harness/post-phase-8-forward-register.md` to scope the `R-` / `B-` filter — their authorities are `tools/forward_register.py` / the post-Phase-8 register protocol (CLAUDE.md §12), unchanged here. Listed so the witness names every `.harness` literal the module spells.

## Two-authority checks performed

- "Is arc X landed?" — reservation state (`merged`) is authoritative for the *state machine*; `gh pr view` is ground truth the reservation is reconciled *from*; the arc row's `merged_at` is a capture. No conflict: reservation ← gh; row ← reservation at drain.
- "Who may append arc X?" — the `open` reservation's holder (`lane_id`), not the queue claim's pid/host (claim = seconds-scale liveness only; the named D2 exception transfers the holder in the same recovery step). The `.ledger-claim-*` file answers only "is a ledger write in flight" — never "who owns the arc".
- "Is the door held?" — `LEASE` presence + `state`; `merge_attempted_at` folds into the lease (no third store). "Is a transition of token T in flight, and toward what?" — `transition.<T>` alone (C-HE-06 §6); `LEASE` answers only who holds now.
- "Which HIL items are pending?" — the shared `loop_status.md` reduction; per-lane `.loop-active` / `.loop-iter` / `.loop-halt` are control markers, not HIL state.
- "What was the gate verdict on #N@head?" — the JSONL row is the authority (written first, under the emit lock); the md line is its projection — an md line missing after a failed write is re-emitted FROM the JSONL (`reconcile_orphans`), never the reverse; `just merge-gate-log-check` reduces the md against the JSONL (ts,count,round) multiset and a residual disagreement is a producer defect, not a second authority.
- "Which mutation probes are live?" — the `# mutation-probe:` annotations name the probes; the log rows only say when each last ran and against which digests (a pin is live only while both digests match HEAD).
