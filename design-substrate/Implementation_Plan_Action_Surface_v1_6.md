# Implementation Plan — Action Surface v1.6

## Change-note (v1.5 → v1.6)

**Trigger.** B-25 resolution (`.harness/class_1_fork_sandbox_tier_floor_deterministic_inhouse_false_undefined.md`, ratified + closed 2026-07-15 via a dyadic C10⊥C4 council convening + operator `AskUserQuestion` selecting Reading A) corrected `ADR-D2.md` v1.2→v1.3 and `Spec_Action_Surface_v1.md` v1.13→v1.14 to state explicitly that `is_deterministic_inhouse` does **not** gate C-AS-02 §2.3 row 7 — the field is carried on `ToolMetadata`/`ToolContract` but reserved, non-gating, pending a possible future verification mechanism.

**Out-of-family `just codex-review` caught this fix landing against the spec/ADR pair without a matching plan delta** — the SAME category of gap it caught at the B-24 arc one session earlier (`Implementation_Plan_Action_Surface_v1_5.md`'s own change-note documents that precedent). `Implementation_Plan_Action_Surface_v1_2.md`'s U-AS-06 unit body (§5.2, preserved byte-exact through v1.3/v1.4/v1.5) still describes `is_deterministic_inhouse` as a "§2.3 row-1/2/7 discriminator" at three sites — the **Inputs** line, the **Signatures** block's `ToolMetadata` comment, and **AC #7** — and AC #1's row enumeration still names row 7 "read-only deterministic." Per X-AL-3, a spec/ADR-level reading correction that leaves the canonical plan's unit body stating the superseded reading is exactly the silent-plan-drift the back-flow discipline exists to catch, even though this delta changes zero code and zero tests (production and the test suite already implement Reading A; only the plan's *description* of what the field does was stale).

**Scope of revision.** Single-unit-body documentation correction at the delta-only-plan-chain layer (v1.1–v1.5 plan files preserved byte-exact; v1.6 supplies amendment-overlay):

- **U-AS-06 Inputs line** — "`ToolMetadata` (carries `is_deterministic_inhouse`, `forces_computer_use`, `forces_code_execution` — the §2.3 rows 1–2 / 7 discriminators)" corrected to state `forces_computer_use`/`forces_code_execution` are the rows 1–2 discriminators; `is_deterministic_inhouse` is carried but non-gating/reserved (v1.14, B-25) — it does not key row 7 or any row.
- **U-AS-06 Signatures block** — the `ToolMetadata` record's inline comment ("Pattern B carrier — the §2.3 row-1/2/7 discriminators") corrected to the same reading.
- **U-AS-06 AC #1** — the row enumeration's "read-only deterministic" corrected to "read-only" (matching the spec's own v1.14 row-7 condition-text correction — "any", not "deterministic in-house"). The keying-contract sentence in AC #1 ("rows 7–10 on `blast_radius_tier`") is **unchanged** — it already stated the Reading-A keying correctly at v1.2 and needs no amendment.
- **U-AS-06 AC #7** — "`ToolMetadata` is declared in this unit carrying `is_deterministic_inhouse` / `forces_computer_use` / `forces_code_execution` — the §2.3 row-1/2/7 discriminators" corrected to name only rows 1–2 as discriminators, with `is_deterministic_inhouse` documented as carried-but-non-gating.

**ZERO new atomic unit; ZERO DAG change; ZERO cross-axis cascade; ZERO code change; ZERO test change.** This delta corrects only the plan's prose description of an existing field's effect — `sandbox_tier_floor()`'s implementation, signature, and the U-AS-06 test list are all unchanged (production already implemented Reading A before this delta; B-25's own fork doc confirmed this by direct code read at filing time).

**Spec authority chain.** `Spec_Action_Surface_v1.md` v1.14 §2.3 (C-AS-02; row 7 condition text + keying-paragraph note corrected at the same B-25 resolution this delta absorbs) + `ADR-D2.md` v1.3 §1.5.1 (the upstream authority both the spec and this plan cite).

**Plan shape preserved.** v1.2's 9-cluster axis-led structure preserved verbatim. No new clusters; no new units. Net AC count unchanged (AC #1 and AC #7 text corrected in place, not added/removed). Net unit count: 33 → 33.

**Sections preserved verbatim from v1.5 + v1.4 + v1.3 + v1.2 + v1.1 + v1.** ALL pre-v1.6 content preserved byte-exact at predecessor files. v1.6 supplies canonical-reading amendment-overlay per the delta-only-plan-chain convention applied at v1.5 §1's own precedent (in-unit-body prose correction, not a new unit).

**Status posture.** BUILT 2026-07-15 — this delta documents a code/test state that was already correct at filing time; only the plan's prose was stale.

**Downstream absorption owed (post-v1.6).**
- `harness-as/CLAUDE.md` §1.2 plan version pointer (v1.5 → v1.6).
- Clearance marker: `.harness/clearance/implementation-plan-action-surface-v1-6-cleared-2026-07-15.md`.
- `.harness/forward-register.yaml` B-25 close-out text amended to cite this plan delta alongside the ADR-D2/spec clearance markers (out-of-family Codex review round 1 caught the initial B-25 close-out only touching the ADR/spec pair, not the plan).

---

## §1 — U-AS-06 unit-body correction (canonical-reading amendment, no signature/AC-count change)

**v1.2 unit body PRESERVED VERBATIM** except for the four sites named above:

| Surface | v1.2 status (preserved through v1.5) | v1.6 amendment |
|---|---|---|
| **Inputs** line | `ToolMetadata` described as carrying "the §2.3 rows 1–2 / 7 discriminators" | Corrected — rows 1–2 only; `is_deterministic_inhouse` carried, non-gating, reserved |
| **Signatures** block `ToolMetadata` comment | `// Pattern B carrier — the §2.3 row-1/2/7 discriminators` | Corrected to the same reading |
| **AC #1** row enumeration | "...read-only deterministic, local-mutation..." | "...read-only, local-mutation..." (matches spec v1.14 row-7 condition text) |
| **AC #1** keying-contract sentence | "rows 7–10 on `blast_radius_tier`" | **PRESERVED VERBATIM** — already correct at v1.2, no amendment needed |
| **AC #7** | "`is_deterministic_inhouse` / `forces_computer_use` / `forces_code_execution` — the §2.3 row-1/2/7 discriminators" | Corrected — `forces_computer_use`/`forces_code_execution` are the row-1/2 discriminators; `is_deterministic_inhouse` is carried but non-gating |
| `sandbox_tier_floor` function signature, all other ACs, test list | landed, unchanged | PRESERVED VERBATIM — no code or test change |

**No new AC, no removed AC, no new test.** This is a documentation-only correction of existing AC #1 and AC #7 text; the underlying acceptance behavior (what `sandbox_tier_floor()` must do) is unchanged — it was already Reading A at v1.2, v1.5, and today. The 17 existing test names plus the 1 test added at the B-25 code PR (`test_sandbox_tier_floor_read_only_ignores_is_deterministic_inhouse`, landed in the same PR as this plan delta) already satisfy the corrected AC text without modification.

---

## §2 — Coverage matrix delta (v1.5 → v1.6)

No coverage delta. AS contract C-AS-02 §2.3 retains its v1.2 unit coverage verbatim — U-AS-06 already covers C-AS-02 at v1.2 baseline. The v1.6 amendment corrects the existing unit body's description in-scope; no new coverage row.

---

## §3 — DAG verification (v1.5 → v1.6)

DAG unchanged. v1.6 amendment is in-unit-body (U-AS-06 only, prose-only); no new units; no new edges. U-AS-06's existing dependency edges (`[U-AS-01, U-AS-04, U-AS-05]`) preserved verbatim.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Action_Surface_v1_6.md` |
| Version | v1.6 |
| Filing event | B-25 resolution per `.harness/class_1_fork_sandbox_tier_floor_deterministic_inhouse_false_undefined.md`, ratified + closed 2026-07-15 (dyadic C10⊥C4 council + operator `AskUserQuestion`); out-of-family `just codex-review` caught the missing plan delta on the initial commit of the same PR — corrected here |
| Predecessor | `Implementation_Plan_Action_Surface_v1_5.md` (v1.5 substantive baseline); v1.4/v1.3/v1.2/v1.1/v1 preserved byte-exact at predecessor files |
| Spec authority | `Spec_Action_Surface_v1.md` v1.14 §2.3 (C-AS-02); `ADR-D2.md` v1.3 §1.5.1 |
| New units | 0 |
| Amended unit bodies | U-AS-06 (prose correction only: Inputs line, Signatures comment, AC #1 row-7 label, AC #7 discriminator description) |
| Net AC delta | 0 — AC #1 and AC #7 text corrected in place, not added/removed |
| DAG verification | Unchanged (no new units; no graph delta) |
| Coverage verification | Unchanged (C-AS-02 already covered at v1.2 baseline; v1.6 corrects in-unit-body prose) |
| Cross-axis cascade | ZERO — AS-axis-internal; no code or test change |
| Date | 2026-07-15 |
