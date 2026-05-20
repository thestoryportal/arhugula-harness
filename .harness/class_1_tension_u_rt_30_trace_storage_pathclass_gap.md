# Class 1 Tension — U-RT-30 trace-storage `PathClass` gap

**Status:** RESOLVED 2026-05-20 — Path B applied (runtime C-RT-07 amended to acknowledge sqlite trace-storage as OD-internal, not via IS PATH_CLASS_REGISTRY).

**Resolution commit:** `<TBD>` on `main` — `Spec_Harness_Runtime_v1.md` §7 C-RT-07 invariants updated to remove the `PathResolver / PATH_CLASS_REGISTRY` claim. AC #2 of U-RT-30 (sqlite path resolves via IS registry) remains STRUCK per the partial-land; this is now the formalized closure rather than a pending decision.

The Track A in-memory store satisfies the spec floor (`closure_invariant = FRESH_ON_RESTART_OPTIONAL_PERSISTENCE_BETWEEN_RESTARTS`). Future on-disk persistence resolves via OD-internal path semantics (NOT a new IS PathClass member). The X-AL-3 architectural-extension concern that motivated the fork is honored.

---

## Original tension (preserved for provenance)


**Filed at:** 2026-05-19 (L6 stage 4 OD observability execution)

**Filing unit:** U-RT-30 (ring-buffer + sqlite rotation wiring)

**Pattern:** `halt-route-split-AC` (workspace memory) — strike the unmaterializable AC + partial-land the remainder + file Class 1 for the struck surface.

---

## 1. The gap

`Spec_Harness_Runtime_v1.md` v1.1 §7 C-RT-07 commits:

> sqlite file path resolves via `PathResolver` to a deployment-surface-appropriate
> location (per OD C-OD-20 §20.1 placement matrix + IS C-IS-01 §1
> PATH_CLASS_REGISTRY).

But `harness-is/src/harness_is/path_class_registry.py` declares exactly 4
values for `PathClass`:

- `SKILLS`
- `PROMPTS`
- `ROUTING_MANIFEST`
- `STATE_LEDGER`

None of these is the canonical home for the OD sqlite trace-storage path
(C-OD-19 §19.2). IS-AL-1 (`harness-is/CLAUDE.md` §4.2) names the 4 classes
as **distinct, not aliases** — re-using any of them for trace storage
violates the anti-leakage rule.

OD spec C-OD-19 §19.2 commits sqlite ring-buffer storage but does not say
"via IS PATH_CLASS_REGISTRY". C-RT-07's reference to the IS registry is
runtime-side composition — it asserts the registry as the *resolution
surface*, but the IS registry does not carry the corresponding typed class.

## 2. Why this is Class 1 (not in-CLI Class 3)

Adding a 5th `PathClass` value is an **architectural extension** under
X-AL-3 (no silent H_T design extension at Phase 7 execution). Precedent
check:

- `PathClass.ROUTING_MANIFEST` was added at U-IS-01 land time (commit
  `397530d`), as part of the initial registry shipping. It was NOT a
  Phase-7 in-CLI extension.
- The U-CP-04 fix (`ea75923`) swapped which existing class to use
  (PROMPTS → ROUTING_MANIFEST) — that is a Class 3 surface (incorrect
  reference, not new design).

Adding a new `PathClass` value is the first time this would be done in-CLI
during Phase 7. Per X-AL-3, this requires architectural ratification before
the IS spec amendment is applied. The amendment-locus is also undecided:

1. **IS-side:** add `PathClass.TRACE_STORAGE` (or similar) to C-IS-01 §1.
2. **Runtime-side:** revise C-RT-07 to acknowledge that the sqlite path
   resolves via a runtime-defined path outside the IS registry (since the
   sqlite store is a Phase-2 runtime concern per OD plan v2.6 §0.7 + §0.9
   "OD-internal").
3. **OD-side:** revise C-OD-19 §19.2 to commit a typed sqlite path class
   that bridges to IS C-IS-01 §1 (less likely — OD plan §0.9 already
   formalized sqlite as OD-internal).

## 3. Resolution paths

| Path | Amendment locus | Cascade |
|---|---|---|
| A | IS C-IS-01 §1 — add `PathClass.TRACE_STORAGE` (or analogous) + residence contract citing OD §19.1 / §19.2 + visibility surface + stability invariants | IS spec + `path_class_registry.py` + `PATH_CLASS_REGISTRY`; U-RT-30 re-lands AC #2 against the new class |
| B | Runtime C-RT-07 — revise the "via PATH_CLASS_REGISTRY" clause to acknowledge sqlite path is runtime-defined (per OD plan §0.9 "OD-internal" framing) | Runtime spec + U-RT-30 lands a runtime-resolved sqlite path; IS registry unchanged |
| C | OD C-OD-19 §19.2 — bridge OD sqlite commitment to a typed IS class via OD plan amendment | OD spec + IS spec; deeper cascade |

Path B is the smallest-blast-radius (no IS spec amendment; no new path
class; OD plan §0.9 already frames sqlite as OD-internal). Path A is the
cleanest cross-axis composition (sqlite typed at IS, consumed at OD/runtime
via registry). Path C duplicates Path A through OD.

**Operator decision needed** before any of A/B/C is applied.

## 4. U-RT-30 partial-landing posture

Per `halt-route-split-AC-pattern`:

- **AC #1 (rotation under load tested)** — LANDED at U-RT-30.
  Verifiable against the OD `evict_oldest_per_ring_buffer_policy` pure
  function + the in-memory `SpanRow` buffer from U-RT-29's supervisor
  scaffold. No sqlite dependency.
- **AC #2 (sqlite path resolves via IS registry)** — STRUCK at U-RT-30.
  Routed to this Class 1 record. Re-lands at the follow-on unit when
  Path A/B/C is selected and applied.
- **AC #3 (backpressure observable)** — LANDED at U-RT-30.
  Verifiable via the ring-buffer state machine — when the policy would
  evict but the buffer is empty, raises `RingBufferError`; when the
  policy fires eviction, the `EvictionAction` records the eviction count
  + bytes (observable surface).

## 5. Filing footer

| Field | Value |
|---|---|
| Tension class | Class 1 — architectural extension (X-AL-3 surface) |
| Status | OPEN — operator-decision pending |
| Filed at | 2026-05-19 (U-RT-30 risk-gate execution) |
| Routing options | A (IS amendment) / B (runtime amendment) / C (OD amendment) |
| Affected ACs | U-RT-30 AC #2 (struck; re-lands at follow-on unit) |
| Affected units | U-RT-30 (this unit); future follow-on for sqlite-path wiring |
| Successor | Follow-on unit to land struck AC against the selected resolution path |
