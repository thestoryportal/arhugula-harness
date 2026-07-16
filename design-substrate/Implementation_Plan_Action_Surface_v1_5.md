# Implementation Plan — Action Surface v1.5

## Change-note (v1.4 → v1.5)

**Trigger.** Class 1 fork resolution per `.harness/class_1_fork_secret_negative_observation_missing_enum_member.md` (ratified 2026-07-15 per the fork's Q1=A/Q2=a/Q3=a filer-recommended readings — roadmap-continue autonomous session, B-24). `verify_sole_resolution_path` hardcoded the wrong `NegativeObservationSurface` label regardless of input — `surface` was unconditionally `STATIC_PROMPT_CACHE_PREFIX` no matter what `secret_arrival_site` actually was. Root cause: the canonical U-AS-21 `NegativeObservationSurface` enum (this file, §1073-1078) declares exactly 4 members, mapping cleanly onto 3 of the spec's 4 named non-`fetch_secret` arrival classes (prompt / log / ledger) — but has **no member for `manifest`**, the 4th class C-AS-05 §5.3's "Sole resolution path" row names verbatim ("a secret arriving by any other path (manifest, prompt, log, ledger) is a contract violation"). A correct dispatch implementation had nothing to return for the manifest case; the pre-fix code's unconditional wrong label was a symptom of this gap, not an independent bug.

**Out-of-family `just codex-review` caught this fix landing against `harness-as/src/harness_as/secret_negative_observation.py` without a matching plan delta** — the fifth enum value was added to the code-level `StrEnum` while this file's U-AS-21 signature (§1073-1078, preserved verbatim through v1.2/v1.3/v1.4) still declared only 4 members. The B-24 close-out record initially read "no design-substrate edit owed" because `Spec_Action_Surface_v1.md` (the spec) never declares this enum at all — true, but incomplete: the **plan** (this file), not the spec, is where `NegativeObservationSurface`'s canonical signature lives, and per X-AL-3 a closed-enum extension against a plan-declared signature is exactly the kind of silent design-extension the back-flow discipline exists to catch even when the spec itself is silent. This v1.5 delta is the correction.

**Scope of revision.** Single-unit-body canonical-reading amendment at delta-only-plan-chain layer (v1.1 + v1.2 + v1.3 + v1.4 plan files preserved byte-exact; v1.5 supplies amendment-overlay):

- **U-AS-21 signature extension** — `NegativeObservationSurface` enum gains a 5th member, `WORKFLOW_MANIFEST_ENTRY`, mapping the spec's 4th-named non-`fetch_secret` arrival class ("manifest") to a real enum value. Name mirrors the CP-axis carrier type `WorkflowManifestEntry` (`harness-cp/src/harness_cp/workflow_manifest_entry.py`), matching the existing 4 members' own naming convention (each named after the concrete surface/carrier, not the abstract property). ZERO new atomic unit; ZERO DAG topology change; ZERO cluster reorganization — mirrors the v1.4 U-AS-03 carrier-extension pattern (in-unit-body signature amendment, not a new unit).
- **`verify_sole_resolution_path` dispatch fix** — the function body gains a real `secret_arrival_site` → `NegativeObservationSurface` dispatch (a `_ARRIVAL_SITE_SURFACES` mapping keyed on BOTH the spec's own short-form vocabulary — `"manifest"` / `"prompt"` / `"log"` / `"ledger"` — AND the longer-form aliases matching the other 3 validators' own `detected_at` values), replacing the unconditional `STATIC_PROMPT_CACHE_PREFIX` hardcode. Unrecognized sites default to `WORKFLOW_MANIFEST_ENTRY` (the one arrival path with no dedicated detector function of its own, so an unlabeled site is most likely one of theirs).

**Spec authority chain.** `Spec_Action_Surface_v1.md` §5.3 (v1.13 HEAD; "Sole resolution path" row naming 4 arrival classes verbatim — "manifest, prompt, log, ledger") — the spec's own text is unamended by this delta (it never declared the enum in the first place); only this plan's code-level signature changes.

**Plan shape preserved.** v1.2's 9-cluster axis-led structure preserved verbatim. No new clusters; no new units. Net AC count: +1 (U-AS-21 gains 1 new AC covering the 5th member + real dispatch). Net unit count: 33 → 33.

**ZERO cross-axis cascade.** `NegativeObservationSurface` is AS-axis-local (defined + consumed entirely within `harness-as/`); confirmed via full-repo grep at fork-doc filing — zero production callers today, zero cross-axis consumers.

**Sections preserved verbatim from v1.4 + v1.3 + v1.2 + v1.1 + v1.** ALL pre-v1.5 content preserved byte-exact at predecessor files. v1.5 supplies canonical-reading amendment-overlay per the delta-only-plan-chain convention applied at v1.4 §1's own precedent (in-unit-body carrier-extension, not a new unit).

**Status posture.** Proposed (v1.4) → Proposed (v1.5) → **BUILT 2026-07-15** (implementation landed same-session at `harness-as/src/harness_as/secret_negative_observation.py` + `harness-as/tests/test_secret_negative_observation.py`; 9/9 tests pass, ruff clean, pyright 0/0/0).

**Downstream absorption owed (post-v1.5).**
- `harness-as/CLAUDE.md` §1.2 plan version pointer (v1.4 → v1.5).
- Clearance marker: `.harness/clearance/implementation-plan-action-surface-v1-5-cleared-2026-07-15.md`.
- `.harness/forward-register.yaml` B-24 close-out text corrected to cite this plan delta (was: "no design-substrate edit owed" — corrected by out-of-family Codex review).

---

## §1 — U-AS-21 signature extension (canonical-reading amendment)

**v1 unit body PRESERVED VERBATIM** except for the enum member list + `verify_sole_resolution_path`'s dispatch discipline note:

| Surface | v1 status | v1.5 amendment |
|---|---|---|
| `NegativeObservationSurface` enum (`STATIC_PROMPT_CACHE_PREFIX` / `SPAN_ATTRIBUTES` / `LOG_RECORDS` / `AUDIT_LEDGER_ENTRY`) | landed at U-AS-21 (4 members) | PRESERVED VERBATIM — all 4 members unchanged |
| `NegativeObservationSurface.WORKFLOW_MANIFEST_ENTRY` (5th member) | NOT LANDED | **NEW at v1.5** — maps the spec's 4th-named non-`fetch_secret` arrival class ("manifest") |
| `NegativeObservationViolation` record | landed | PRESERVED VERBATIM |
| `validate_no_secret_in_static_prefix` / `_span_attributes` / `_audit_ledger_entry` | landed | PRESERVED VERBATIM |
| `verify_sole_resolution_path(secret_arrival_site) -> Optional<NegativeObservationViolation>` signature | landed | PRESERVED VERBATIM (signature unchanged — only the body's internal dispatch logic changes, from a hardcoded return to a real `secret_arrival_site → surface` mapping) |

**NEW AC at U-AS-21 (appended to v1 unit body):**

- **AC #5** — `verify_sole_resolution_path`'s `surface` field on a non-`fetch_secret`-arrival violation reflects the REAL arrival site, not a hardcoded constant. At minimum, the 4 spec-named short-form labels (`"manifest"` / `"prompt"` / `"log"` / `"ledger"`) each dispatch to their corresponding `NegativeObservationSurface` member (`WORKFLOW_MANIFEST_ENTRY` / `STATIC_PROMPT_CACHE_PREFIX` / `LOG_RECORDS` / `AUDIT_LEDGER_ENTRY` respectively); an unrecognized site defaults to `WORKFLOW_MANIFEST_ENTRY` (implementer-discretion default, since manifest has no dedicated detector function of its own to fall back to).

**NEW test names (appended to the v1 test list):**

- `test_verify_sole_resolution_path_dispatches_known_sites_to_matching_surfaces`
- `test_verify_sole_resolution_path_dispatches_spec_short_form_labels`
- `test_verify_sole_resolution_path_unrecognized_site_defaults_to_manifest` (added at the merge-gate test-witness lens's request — pins the default-fallback branch, which the first two tests left unwitnessed since neither ever calls with a site absent from `_ARRIVAL_SITE_SURFACES`)

**Implementer-discretion at unrecognized-site default.** The plan does not mandate a specific fallback for a `secret_arrival_site` string outside the spec's 4 named short-form labels and the existing validators' own long-form `detected_at` aliases. `WORKFLOW_MANIFEST_ENTRY` is the recommended default (matches the landed implementation) since it is the one arrival path with no dedicated validator function producing its own canonical `detected_at` string elsewhere in this unit's surface — an unlabeled call is most plausibly one of theirs. A future caller needing stricter behavior (reject-unknown rather than default-to-manifest) MAY narrow this at a follow-on amendment once a real production caller exists; zero production callers exist at v1.5 filing time, so this is implementer-discretion, not a contract gap.

---

## §2 — Coverage matrix delta (v1.4 → v1.5)

No coverage delta. AS contract C-AS-05 §5.3 retains its v1 unit coverage verbatim — U-AS-21 already covers C-AS-05 at v1 baseline. The v1.5 amendment extends the existing unit body in-scope; no new coverage row.

---

## §3 — DAG verification (v1.4 → v1.5)

DAG unchanged. v1.5 amendment is in-unit-body (U-AS-21 only); no new units; no new edges. U-AS-21's existing dependency edges (`[U-AS-17, U-AS-20]`) preserved verbatim.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Action_Surface_v1_5.md` |
| Version | v1.5 |
| Filing event | Class 1 fork resolution per `.harness/class_1_fork_secret_negative_observation_missing_enum_member.md`, ratified + built 2026-07-15 (roadmap-continue autonomous session, B-24; out-of-family `just codex-review` caught the missing plan delta on a prior commit of the same PR — corrected here) |
| Predecessor | `Implementation_Plan_Action_Surface_v1_4.md` (v1.4 substantive baseline); v1.3/v1.2/v1.1/v1 preserved byte-exact at predecessor files |
| Spec authority | `Spec_Action_Surface_v1.md` v1.13 §5.3 (C-AS-05; unamended — the spec never declared this enum) |
| New units | 0 |
| Amended unit bodies | U-AS-21 (signature extension: +`WORKFLOW_MANIFEST_ENTRY` member; +1 AC covering real dispatch) |
| Net AC delta | +1 AC at U-AS-21 |
| DAG verification | Unchanged (no new units; no graph delta) |
| Coverage verification | Unchanged (C-AS-05 already covered at v1 baseline; v1.5 extends in-unit-body) |
| Cross-axis cascade | ZERO — AS-axis-internal; zero production callers confirmed by full-repo grep |
| Date | 2026-07-15 |
