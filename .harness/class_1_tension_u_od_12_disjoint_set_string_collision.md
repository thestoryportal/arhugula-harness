# Class 1 Tension — U-OD-12: acc #2 set-disjointness contradicted by the declared member sets

**Status:** ✅ CLOSED-via-OD-plan-v2.8-D-4 (resolved 2026-05-16; status-line refreshed 2026-05-27) — production landed at `harness-od/src/harness_od/base_rate_set_and_envelope.py` (`DUAL_REGIME_EVENT_CLASSES` documentation + v2.5 unconditional-disjointness test replaced by D-4-variant per OD plan v2.8 §0.2 defect table). **Status-line refresh** per workflow v1.9 §7.4.7.3 empirical-verification discipline — fork-doc body §"RESOLVED" (line 127) declared closure at v2.8 publication; top **Status:** field stale until this refresh. Species 3 (resolved-but-carry-stale-inherited) per workflow v1.9 §7.4.7.2.

_Original filing:_ 🛑 OPEN — filed 2026-05-16 during Phase 7 sub-phase 7b OD axis-stream (L5 batch).
**Unit:** U-OD-12 — Declare 13-entry base-rate-sampled set + per-cell tuning envelope.
**Plan body:** `Implementation_Plan_Operational_Discipline_v2_5.md` §3.4.2 (v2.5 conformance revision; not re-pointed at v2.6 — v2.6 §3 pointer table does not list U-OD-12).
**Spec contract:** `Spec_Operational_Discipline_v1_3.md` C-OD-10 §10.1, §10.2, §10.3 (preserved verbatim from v1.2 §10).
**Fork class:** Class 1 (halt-execution) — acceptance criterion incompatible with the declared signature.

## Defect

U-OD-12 acceptance criterion #2 (v2.5 §3.4.2):

> `BASE_RATE_SAMPLED_EVENT_CLASSES ∩ ALWAYS_SAMPLED_EVENT_CLASSES == ∅` —
> sets are disjoint (event class belongs to exactly one regime).

The two operands are declared as `Set<string>` of event-class strings:

`ALWAYS_SAMPLED_EVENT_CLASSES` (U-OD-11, v2.5 §3.4.1 — **landed** at
`sampling_mode.py`) contains the bare strings:
- `"files.operation"` — §9.2 row "`files.operation` at `kind ∈ {upload, delete}`"
- `"memory.operation"` — §9.2 row "`memory.operation` at `kind ∈ {write, update, delete}`"

`BASE_RATE_SAMPLED_EVENT_CLASSES` (U-OD-12, v2.5 §3.4.2 signature block, lines
478–479) contains the bare strings:
- `"files.operation"` — §10.1 row "`files.operation` at `kind ∈ {list, metadata, reference}`"
- `"memory.operation"` — §10.1 row "`memory.operation` at `kind ∈ {read, list}`"

As declared — `Set<string>` keyed on the bare event-class string — both
`"files.operation"` and `"memory.operation"` are members of **both** sets.
Therefore:

```
BASE_RATE_SAMPLED_EVENT_CLASSES ∩ ALWAYS_SAMPLED_EVENT_CLASSES
  = {"files.operation", "memory.operation"}  ≠  ∅
```

Acc #2 is **directly contradicted by the declared member sets**. The
disjointness test (`test_base_rate_and_always_sampled_disjoint` in U-OD-12's
`Tests:` field) cannot pass against the signatures U-OD-11 and U-OD-12 declare.

## Root cause — the sampling regime is keyed on `(event_class, kind)`, the signature on `event_class`

The spec C-OD-09 §9.2 and C-OD-10 §10.1 do **not** place a whole event class
in one regime. They split `files.operation` and `memory.operation` by the
`kind` attribute:

| Event class | `kind` ∈ | Regime | Source |
|---|---|---|---|
| `files.operation` | `{upload, delete}` (mutation) | always-sampled | C-OD-09 §9.2 |
| `files.operation` | `{list, metadata, reference}` (non-mutation) | base-rate | C-OD-10 §10.1 |
| `memory.operation` | `{write, update, delete}` (mutation) | always-sampled | C-OD-09 §9.2 |
| `memory.operation` | `{read, list}` (non-mutation) | base-rate | C-OD-10 §10.1 |

The spec's disjointness holds over **`(event_class, kind)` pairs**, not over
bare `event_class` strings. The acc #2 claim "event class belongs to exactly
one regime" is **false at the granularity the §9.2 / §10.1 tables actually
specify** — `files.operation` and `memory.operation` belong to *both* regimes,
discriminated by `kind`.

The plan signature models the regime sets as `Set<string>` of event-class
strings (kind-narrowing demoted to source-comments — v2.5 §3.4.1 line ~421,
§3.4.2 lines 478–479). At that granularity acc #2 is un-satisfiable. This is
the same defect class as `U-OD-08` (plan event-set diverging from the spec set
the AC claims verbatim) — here the AC asserts a disjointness the chosen string
granularity cannot honor.

## Spec position

C-OD-09 §9.2 + C-OD-10 §10.1 are internally consistent — at `(event_class,
kind)` granularity the regime assignment is a well-defined function (no pair is
in both). The defect is at the **plan layer**: U-OD-11 / U-OD-12 model the
regime sets as `Set<string>` keyed on bare `event_class`, collapsing the `kind`
discriminator the spec relies on. The spec does not under-specify; the plan
under-models the key.

## Recommended fix (for the OD-plan implementation-planner revision pass)

**Option A — key the regime sets on `(event_class, kind)` (preferred).**
Replace `Set<string>` with a set of `(event_class, kind)` pairs (or a richer
`SampledEventClass` record carrying `event_class` + an optional `kind`
predicate). The four mutation/non-mutation rows of `files.operation` /
`memory.operation` then occupy distinct members, and acc #2 disjointness holds
verbatim. This is a plan-layer signature change to **both** U-OD-11 (landed)
and U-OD-12 — U-OD-11 would need a follow-up revision (its
`ALWAYS_SAMPLED_EVENT_CLASSES` is already landed as `frozenset[str]`).

**Option B — strike / re-scope acc #2.** Re-word acc #2 to disjointness "over
event classes that are not `kind`-discriminated", explicitly carving out
`files.operation` / `memory.operation` as dual-regime classes routed by `kind`
at the `sampling_decision` call site. Plan-layer AC revision; no signature
change; no spec change.

Both are plan-internal conform-to-spec; neither needs a spec change. Option A is
the cleaner model (it makes the regime sets a faithful image of the §9.2/§10.1
tables) but touches a landed unit; Option B is lower-blast-radius.

## Note — U-OD-11 already landed

U-OD-11 (`sampling_mode.py`) is landed with `ALWAYS_SAMPLED_EVENT_CLASSES` as
`frozenset[str]` containing bare `"files.operation"` / `"memory.operation"`.
U-OD-11's own acc #3 (cardinality 18, member set byte-exact per §9.2) is
satisfied — the §9.2 table has 18 rows and U-OD-11 conformed to it. U-OD-11
does **not** assert cross-set disjointness, so U-OD-11 itself is not in
defect. Acc #2 is **U-OD-12's** criterion and the contradiction surfaces only
when U-OD-12 composes its set against the landed U-OD-11 set. If the revision
pass selects Option A, U-OD-11 needs a co-revision.

## Routing

Phase 6 OD-plan revision-pass at `design-substrate/` (per `harness-od/CLAUDE.md`
§5.1 — "OD plan v2.6 atomic unit signature defect"). Joins the deferred cluster.
U-OD-12 skipped for this batch.

## Dependent-blocking note

U-OD-12 `Depends on: [U-OD-01, U-OD-11]` and is in turn cited by U-OD-22 (L6),
U-OD-32 / U-OD-33 (L8/L7) — none in the L4/L5 batch. No batch unit is blocked.
U-OD-17 and U-OD-27 (this batch) do not consume U-OD-12.

## Disposition

🛑 HALTED. Skipped. Deferred cluster grows to 9 units (was 8 after U-OD-21):
U-OD-02, U-OD-03, U-OD-08, U-OD-09, U-OD-10, U-OD-12, U-OD-21, U-OD-28, U-OD-30.

---

## ✅ RESOLVED — OD plan v2.8 (2026-05-16)

Resolved by the `implementation-planner` OD-plan v2.8 revision pass (`design-substrate/Implementation_Plan_Operational_Discipline_v2_8.md`), operator-ratified 2026-05-16. See v2.8 §0.2 defect table. The unit is unblocked; lands when OD-7b resumes.

---

## Audit reconciliation (2026-05-20)

**Verified status:** RESOLVED

**Resolving artifact / evidence:** OD plan v2.8 §0.2 defect table (ACC #2 defect addressed in revision pass; unit unblocked).

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
