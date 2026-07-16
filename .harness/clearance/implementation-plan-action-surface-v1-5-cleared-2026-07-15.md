---
artifact: design-substrate/Implementation_Plan_Action_Surface_v1_5.md
version: v1.5
cleared_at: 2026-07-15T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-roadmap-continue
back_reference:
  - .harness/class_1_fork_secret_negative_observation_missing_enum_member.md (Q1=A / Q2=a / Q3=a readings, all filer-recommended)
  - .harness/forward-register.yaml (B-24 entry)
merge_commit: pending (pre-merge at filing time)
reviewer_chain:
  - advisor() pre-implementation grounding (this session) — reviewed the B-24/B-25/B-27 ratification batch before build; confirmed B-24 as Claude-ratifiable (clear, reversible, filer-recommended, convention-following)
  - out-of-family `just codex-review` round 2 — caught that the initial B-24 close-out ("no design-substrate edit owed") checked only `Spec_Action_Surface_v1.md` (which never declares `NegativeObservationSurface`) and missed that `Implementation_Plan_Action_Surface_v1.md` §1073-1078 DOES declare this enum's canonical 4-member signature, preserved verbatim through v1.2/v1.3/v1.4 — extending it to 5 members without a plan delta was a silent design-extension under X-AL-3 even though the spec itself was silent. This v1.5 delta + clearance marker is the correction, landed in the same PR before merge.
  - full test run: `harness-as/tests/test_secret_negative_observation.py` — 8/8 passed
  - ruff format + ruff check clean; pyright 0 errors/0 warnings/0 informations
supersedes: null
superseded_by: null
---

# Clearance — `Implementation Plan Action Surface v1.5`

v1.5 closes the `B-24` fork: `verify_sole_resolution_path` hardcoded the wrong `NegativeObservationSurface` label regardless of input, because the canonical 4-member enum (declared at this plan's U-AS-21 unit body, `Implementation_Plan_Action_Surface_v1.md:1073-1078`) had no member corresponding to the spec's 4th-named non-`fetch_secret` arrival class — "manifest" (`Spec_Action_Surface_v1.md` §5.3's "Sole resolution path" row names "manifest, prompt, log, ledger" verbatim, but only 3 of the 4 map onto an existing enum member).

This delta extends U-AS-21's signature with a 5th member, `NegativeObservationSurface.WORKFLOW_MANIFEST_ENTRY` (named to mirror the CP-axis `WorkflowManifestEntry` carrier, matching the existing 4 members' own concrete-surface-name convention), and adds 1 new AC requiring `verify_sole_resolution_path` to dispatch on the real `secret_arrival_site` rather than hardcode a return value. `harness-as/src/harness_as/secret_negative_observation.py` implements this via a `_ARRIVAL_SITE_SURFACES` mapping keyed on both the spec's short-form vocabulary (`manifest`/`prompt`/`log`/`ledger`) and the longer-form aliases the other 3 validators already use as their own `detected_at` values, defaulting an unrecognized site to `WORKFLOW_MANIFEST_ENTRY`.

**Process correction, same PR.** The first commit of the PR this marker co-publishes with closed B-24 asserting "no design-substrate edit owed," reasoning that `Spec_Action_Surface_v1.md` never declares this enum. That reasoning checked the SPEC but not the PLAN — a distinct design-substrate artifact that, for this unit, is where the enum's canonical signature actually lives (per U-AS-21's own `**Signatures:**` block). Out-of-family `just codex-review` caught the gap on a subsequent round; this v1.5 delta + marker is filed in the same PR before merge, so no merged state ever carried an un-back-flowed enum extension against a plan-declared closed signature.

## Notes

- Phase 7 consumers may rely on this version (v1.5) as canonical for `NegativeObservationSurface`'s 5-member signature.
- `B-24`'s forward-register row (`.harness/forward-register.yaml` + `.harness/post-phase-8-forward-register.md`) close-out text is corrected in the same PR to cite this plan delta instead of the prior "no design-substrate edit owed" claim.
- See `.harness/clearance/README.md` for marker discipline.
