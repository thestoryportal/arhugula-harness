# Class 3 Drift — `Spec_Harness_Runtime_v1.md` §4 `HarnessContext` field-set post-v2.12

**Class:** 3 (informational drift)
**Filed:** 2026-05-20 at CP plan v2.12 close
**Trigger:** CP plan v2.12 §0.5 adds `ledger_reader: LedgerReader` to
`HarnessContext` to resolve `[[fork-u-cp-56-resumption-underspec]]`. The
runtime spec §4 (C-RT-04) field enumeration does not list `ledger_reader`
by name.

## Drift

`Spec_Harness_Runtime_v1.md` v1.1 §4 C-RT-04 enumerates 27 `HarnessContext`
fields (mirrored at `harness-runtime/tests/test_types.py:102`'s
`test_harness_context_declares_all_c_rt_04_fields` invariant). Post-v2.12,
`HarnessContext` declares 28 fields — `ledger_reader` is the new one.

The runtime-side test was updated to expect the new field with a one-line
comment ("v2.12 — read-view counterpart of ledger_writer"). The spec text
itself was not amended.

## Disposition — same pattern as Lane 6 §11 drift

Non-blocking; informational only. No revision-pass triggered.

**Defense:** `ledger_reader` is a *composition* over the same IS substrate
as `ledger_writer` — both wrap the same `JsonlLedgerHandle`, providing
read vs. write access surfaces over a single substrate primitive. C-RT-04
§4 specifies substrate primitives (the path resolver, the ledger writer,
the index, etc.); the runtime is authorized to compose access-view
adapters over those primitives without extending the contract surface.

Analogy: HTTP servers don't get a new "spec field" each time someone adds
a `GET` variant alongside an existing `POST` endpoint over the same
resource. The resource is the substrate primitive; verbs are access-view
adapters.

The CP-side defense at plan v2.12 §0.2 — "CP spec v1.4 §6.1 (verbatim
from v1.2) declares the manifest schema with explicit extension
authorization: `// ... additional per-workload fields`" — applies
symmetrically to the runtime side: C-RT-04 §4's substrate enumeration is
the canonical surface, and the read-view adapter is a derived composition.

## Asymmetry with Lane 6 §11 drift

Lane 6 filed `class_3_drift_runtime_spec_section_11_post_lane_6.md`
declaring "no spec bump at Lane 6 — §11 risk surface already anticipated
the thin-adapter outcome." v2.12 mirrors that exact pattern at §4: the
spec already anticipates substrate composition; adding an access-view
adapter materializes a substrate-composition that the spec already
authorizes implicitly.

## Routing

Class 3 informational; logged here for visibility. Routes to a future
`Spec_Harness_Runtime_v1.md` revision pass when the runtime spec next
bumps (any reason). Suggested §4 amendment at that pass:

- Append a "Reader/writer composition" subsection to §4 explicitly
  authorizing access-view adapters (read-view, append-only-view, etc.)
  over substrate primitives.
- Update the C-RT-04 §4 field-enumeration to include `ledger_reader`
  alongside `ledger_writer` (and any other paired access-views).
- Update the test_types.py invariant docstring to cite the amended spec.

## Provenance

- v2.12 commit: (current uncommitted; will be the v2.12 landing commit).
- Advisor flag: 2026-05-20 advisor call at v2.12 pre-commit review.
- Parent fork: `.harness/class_1_tension_u_cp_56_resumption_underspec.md`
  (CLOSED at v2.12).
- Pattern reference: `.harness/class_3_drift_runtime_spec_section_11_post_lane_6.md`
  (Lane 6 §11 drift; same pattern, same disposition).
