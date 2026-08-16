---
artifact: design-substrate/Spec_Operational_Discipline_v1_42.md
version: v1.42
cleared_at: 2026-08-16T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-operator-ratification
back_reference:
  - .harness/b137-c1-admit-the-envelope-root-2026-08-16.md
  - .harness/forward-register.yaml B-137 (step (3) OPERATOR RATIFICATION 2026-08-16)
merge_commit: <filled at PR merge>
reviewer_chain:
  - "operator AskUserQuestion ratification 2026-08-16 (B-137 step (3) = C1, recorded at PR #1383)"
  - build-time re-measurement of the ratification's carried-forward cost (this arc)
supersedes: Spec_Operational_Discipline_v1_41.md
---

# Clearance — `Spec_Operational_Discipline v1.42`

Additive amendment to C-OD-09 §9.2: the always-sampled exception set gains **row 20,
`workflow.envelope`**, 19 → 20. This is candidate **C1** of `B-137` step (3), ratified by
the operator on 2026-08-16 over a five-option set with each option's measured cost stated.
Bundled-absorption arc per root `CLAUDE.md` §11.4 — the spec delta lands in the same PR as
the `harness-od` substrate change, the count-contract reconciliation across five carriers,
and the test updates.

**The amendment is an ingestion repair, not a new declaration.** Build-time grounding found
that C-OD-25 §25.1 (`Spec_Operational_Discipline_v1_8.md:90`) has declared *"`workflow.envelope`
head=1.0 (always-sampled … the envelope ALWAYS persists)"* since v1.8, and that C-OD-25 is
preserved verbatim through the whole v1.9 → v1.41 chain. §9.2 simply never absorbed it. That
is the same defect shape v1.37 repaired for `fallback.exhausted` (declared at CP `:410`,
dropped at OD ingestion), differing only in that the declaring contract here is intra-axis.
The grounding materially changes how the amendment should be read: it is not the workspace
minting a new floor at Phase 7, it is §9.2 catching up to a floor OD already committed.

**The ratification's carried-forward cost was re-measured and does not hold.** The operator
ratified C1 *with* its stated cost — *"data loss, not delay … a trace containing any ordinary
non-member child becomes never-resolving"* — and required the implementing arc to measure the
ordinary-child population before shipping. Measured at `team-binding × self-hosted-server`
through the real `TailKeepSpanProcessor`: **0 buffered / 0 evicted** sequentially, even at a
buffer cap of 3 where the pre-`B-136` counterfactual read 3 buffered / 97 evicted. `B-136`'s
name-arm repair (PR #1331) is why. **One claim from the first draft is WITHDRAWN**, after out-of-family
review: it read the cap-8 row as *"no configuration loses a span the status quo would have
kept"* because both worlds exported **8** ordinary children. That was cardinality-only.
Compared by trace IDENTITY the sets differ — the base-rate sampler preserves a hash-drawn
spread while C1 admits everything and the buffer's drop-oldest FIFO keeps only the newest
`max_buffered_traces` — so **under buffer pressure C1 displaces traces the previous sampler
would have preserved**. What governs shipping is the threshold: displacement requires
concurrency above the cap, and at the shipped 4096 default the measured displacement set at
concurrency 100 is **empty** while C1 preserves 100 ordinary children against the baseline's
13. Full table at v1.42 §0.3; the displacement is pinned at
`test_c1_displaces_previously_preserved_traces_under_buffer_pressure`.

**The residual that is real, and is stated rather than absorbed:** C1 multiplies *concurrent
in-flight buffer occupancy* by `1/base_rate` (measured peak 9 → 100 at concurrency 100),
moving the eviction threshold at a 0.1-rate cell from roughly 40,960 to roughly 4,096
concurrent envelope-rooted workflows against the shipped `max_buffered_traces` default of
4096. **Beyond that threshold the cost is displacement, not merely reduced headroom** — a real
per-trace loss the status quo would not have incurred. Below it the cost is zero. This is a
*different* residual from the one the ratification carried, and it is registered at `B-185`
rather than repaired.

No ADR revision. No CP delta — the declaring contract is OD's own C-OD-25. No CXA rows — the
amendment moves a row inside a table OD owns, consumed by OD's own substrate; aggregate stays
frozen at 111. No §9.3 language change — this delta ingests a declared floor rather than
ratifying a narrower one, so candidate C is explicitly not taken.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- `B-137`'s C11 half — the *exported-volume* multiplier against the C-OD-11 §11.1 per-cell
  budgets — is untouched by this delta and stays open at `B-182` / `B-183`. v1.37 rider (a)
  applies unchanged: §11.1 enforces downstream of sampling, so membership cannot admit
  throughput past the caps.
- `B-160`'s head=1.0 divergence class grows from four unconditional names to five: its
  close-out scoped the sweep to *"any OTHER **C-OD-3x** namespace"*, and this declaration
  lives at C-OD-25, so the enumeration was structurally unable to see it. The four C-OD-3x
  instances stay open there.
- **One venue row 20 does NOT reach, surfaced by out-of-family Codex against the build PR and
  confirmed by direct measurement before acceptance:** the floor works by inheritance through
  `ParentBased`, which consults the inner sampler only for roots — so under an **unsampled ambient
  OTel parent** the envelope is a child, `ParentBased` short-circuits to the parent's DROP, and the
  whole trace disappears as it did pre-v1.42. Production-reachable (the MCP daemon path hands the
  ambient context to its worker via `asyncio.to_thread` + `copy_context()`). Stated as a bound at
  v1.42 §0.3.1 and registered at `B-186` rather than repaired, because the fix — forcing the
  envelope to be a trace root — trades the floor against distributed-trace continuity and would be
  a silent X-AL-3 extension against a delta declaring ZERO emission-site change. It does not narrow
  the ratified scope: `B-137` reasoned throughout from the envelope being the trace root.
  **Row 20 is written ROOT-CONDITIONAL in the contract itself** (v1.42 §0.2.1 + §0.2.3), joining
  §9.2's existing `subagent.span (root)` in that shape, so the spec does not assert a floor its
  own mechanism cannot deliver. That is a precise statement of reach, NOT `B-137`'s candidate C:
  within a harness-rooted trace the floor is absolute, §9.3 is untouched and all three of its
  invariants bind row 20, and rows 1–19 acquire no qualifier.
- See `.harness/clearance/README.md` for marker discipline.
