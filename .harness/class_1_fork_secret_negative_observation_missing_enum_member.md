# Class 1 Fork — `NegativeObservationSurface` has no member for workflow-manifest secret arrival; `verify_sole_resolution_path` hardcodes the wrong label regardless of input

**Status:** RATIFIED 2026-07-15 (Q1=A `WORKFLOW_MANIFEST_ENTRY`, Q2=a bundled dispatch fix, Q3=a — all per filer recommendation; roadmap-continue autonomous session). **BUILT** — see `.harness/post-phase-8-forward-register.md` §"B-24". **Correction (out-of-family `just codex-review` round 2, same PR):** the initial close-out claimed "no design-substrate edit owed" because `Spec_Action_Surface_v1.md` never declares this enum — true but incomplete. `Implementation_Plan_Action_Surface_v1.md` §1073-1078 (the PLAN, not the spec) DOES declare `NegativeObservationSurface`'s canonical 4-member signature at U-AS-21, preserved verbatim through v1.2/v1.3/v1.4. A plan delta (`Implementation_Plan_Action_Surface_v1_5.md`) + clearance marker (`.harness/clearance/implementation-plan-action-surface-v1-5-cleared-2026-07-15.md`) were required and are now filed in the same PR before merge.

**Filed at:** 2026-07-14

**Filer:** roadmap-continue no-parking sweep (post-#996 session; B-24 grounding)

**Surfaced by:** `.harness/harness-preflight-code-review-2026-07-12.md` Medium findings table; direct read of `harness-as/src/harness_as/secret_negative_observation.py` against `design-substrate/Spec_Action_Surface_v1.md` §5.3.

**Classification:** Class 1 (the code-level enum realizing a spec-named property set is structurally incomplete — one of the spec's own 4 named arrival paths has no corresponding enum member, so no correct fix is possible without a new design-substrate-adjacent enum member).

---

## §1 — The gap

### §1.1 — The spec names 4 non-`fetch_secret` arrival paths; the code enum covers 3 surfaces

`design-substrate/Spec_Action_Surface_v1.md` §5.3 "Negative-observation invariant" (verbatim, lines 644-651):

| Property | Contract |
|---|---|
| Absence in stored prompts | Secret values MUST NOT enter the static prompt cache prefix |
| Absence in log surfaces | Secret values MUST NOT enter span attributes, log records, or any observability content-attribute capture surface |
| Absence in ledger | Secret values MUST NOT enter audit-ledger entries |
| **Sole resolution path** | `fetch_secret` is the **only** path through which secrets reach a sandbox; secret content arriving by any other path (**manifest**, prompt, log, ledger) is a contract violation |

The spec itself never declares a `NegativeObservationSurface` enum — it is a code-level realization authored at U-AS-21 (`Implementation_Plan_Action_Surface_v1.md` §2 U-AS-21). `harness-as/src/harness_as/secret_negative_observation.py:36-42`:

```python
class NegativeObservationSurface(StrEnum):
    """A surface a secret value must never appear on (C-AS-05 §5.3)."""

    STATIC_PROMPT_CACHE_PREFIX = "STATIC_PROMPT_CACHE_PREFIX"
    SPAN_ATTRIBUTES = "SPAN_ATTRIBUTES"
    LOG_RECORDS = "LOG_RECORDS"
    AUDIT_LEDGER_ENTRY = "AUDIT_LEDGER_ENTRY"
```

Three of the spec's four named "other path" arrival classes map cleanly onto an existing member (prompt → `STATIC_PROMPT_CACHE_PREFIX`; log → `LOG_RECORDS`/`SPAN_ATTRIBUTES`; ledger → `AUDIT_LEDGER_ENTRY`). **`manifest` has zero corresponding member.** A secret arriving inline via a workflow manifest field (e.g. a `StepOverride`/`step_payload` value) rather than resolved at runtime via `fetch_secret` is exactly the scenario the spec names — and there is no enum value a correct implementation could return for it.

### §1.2 — The current function hardcodes the wrong label regardless of input, masking the gap

`harness-as/src/harness_as/secret_negative_observation.py:119-133`:

```python
def verify_sole_resolution_path(
    secret_arrival_site: str,
) -> NegativeObservationViolation | None:
    """Verify a secret reached the sandbox only via `fetch_secret` (§5.3).

    `fetch_secret` is the **sole** resolution path; a secret arriving by any
    other path (manifest, prompt, log, ledger) is a contract violation.
    """
    if secret_arrival_site == "fetch_secret":
        return None
    return NegativeObservationViolation(
        surface=NegativeObservationSurface.STATIC_PROMPT_CACHE_PREFIX,
        detected_at=secret_arrival_site,
        invariant="fetch_secret is the sole secret-resolution path",
    )
```

`surface` is unconditionally `STATIC_PROMPT_CACHE_PREFIX` no matter what `secret_arrival_site` actually is — `detected_at` correctly carries the real site string, but `surface` never reflects it. This means (a) a genuine `"manifest"` violation is currently mislabeled as a prompt-cache violation rather than surfaced as an unrepresentable case, and (b) even a bug-fixed dispatch that correctly matched `secret_arrival_site` against `"prompt"`/`"log"`/`"ledger"` would still have nothing to return for `"manifest"` — the missing enum member is the root gap; the hardcoded label is a symptom that currently hides it (a `"manifest"` call site produces a violation record, just with the wrong `surface`, rather than an error or an unhandled case).

### §1.3 — Zero production callers; the gap is latent, not reachable today

Full-repo grep confirms the only call sites are `harness-as/src/harness_as/__init__.py:230,471` (re-export only) and `harness-as/tests/test_secret_negative_observation.py:42-49`. The test (`test_verify_sole_resolution_path_rejects_manifest_arrival`) passes the literal string `"workflow_manifest"` and only asserts the return `is not None` — it never checks `.surface`, so the mislabel is untested and latent. No production code path currently calls `verify_sole_resolution_path` with a real secret-arrival-site string; the function exists as a landed contract surface (per U-AS-21 acceptance) awaiting a real caller.

---

## §2 — Proposed readings

**Q1 — The missing enum member's name.**

- **(A) `WORKFLOW_MANIFEST_ENTRY`** — matches the CP-axis carrier type name `WorkflowManifestEntry` (`harness-cp/src/harness_cp/workflow_manifest_entry.py`) that the secret would actually be found embedded in. **RECOMMENDED** — the existing 4 members are each named after the concrete surface/carrier (not the abstract property), and this follows that convention precisely.
- **(B) `WORKFLOW_MANIFEST`** — matches the test's own literal string (`"workflow_manifest"`) and the spec's own parenthetical word ("manifest") more directly; slightly less precise about which manifest sub-structure (a `WorkflowManifestEntry`, a `StepOverride`, a `step_payload` field) actually carries the leaked value.
- (C) A more granular split — separate members for `StepOverride`-carried vs. top-level `WorkflowManifestEntry`-carried secrets, if the eventual real caller needs to distinguish them. Deferred as unnecessary until a real caller exists (YAGNI at this stage — no current consumer needs the distinction).

**Q2 — Should `verify_sole_resolution_path`'s dispatch also be fixed in the same arc, or is this fork scoped to the enum member alone?**

- (a) **Enum member + dispatch fix together** — add the new member AND replace the hardcoded `surface=NegativeObservationSurface.STATIC_PROMPT_CACHE_PREFIX` with a real string→enum dispatch (e.g. a small mapping dict keyed on `secret_arrival_site`), since fixing one without the other leaves the function still wrong for every non-`fetch_secret` input. **RECOMMENDED** — the enum-member gap and the dispatch bug are two views of the same defect; landing only the enum member without fixing the dispatch would still produce mislabeled violations for `"manifest"` (now merely mislabeled as one of 4 wrong surfaces instead of the current 1).
- (b) Enum member only, dispatch fix deferred — if the operator wants the design-substrate-adjacent enum addition ratified separately from the (arguably Class-3, since it's a pure code bug not a design gap) dispatch fix.

**Q3 — Is this genuinely design-substrate-gated, or could the enum member be added as a Phase-7 code-only fix?**

- (a) **Design-substrate-gated (as registered)** — `NegativeObservationSurface` is enumerated at code (not spec) level, but the spec's §5.3 "Sole resolution path" property is the authority the enum realizes; per X-AL-3, any enumeration purporting to fully realize a spec-named property set should not silently gain a new member without an explicit back-flow record (this fork) even though the spec itself doesn't need a version bump — the fork exists to make the addition auditable and ratified rather than silent, and to let the operator confirm the naming choice (Q1) before it's load-bearing anywhere.
- (b) Not design-substrate-gated — since the spec never declared this enum, adding a member is a pure code fix with no spec version bump owed, and this could be handled as a Class 3 informational item rather than Class 1. **Not recommended by the filer** — the register's own classification (`design_substrate_gated`) and the X-AL-3 "no silent H_T design extension" framing favor treating any new closed-enum member realizing a spec-named property as needing explicit operator sign-off, even absent a spec-file edit.

**Q4 — Cross-axis cascade.**

`NegativeObservationSurface` is AS-axis-local (defined + consumed entirely within `harness-as/`). Zero production callers today means zero cascade to any consumer. No CP / OD / IS / CXA / ADR / ADD / PRD touch under any reading.

---

## §3 — Filing footer

| Field | Value |
|---|---|
| Artifact | `class_1_fork_secret_negative_observation_missing_enum_member.md` |
| Status | PROPOSING |
| Filed at | 2026-07-14 |
| Authority anchors | `design-substrate/Spec_Action_Surface_v1.md` §5.3 (v1.13 HEAD; Negative-observation invariant, "Sole resolution path" row naming 4 arrival classes verbatim); `Implementation_Plan_Action_Surface_v1.md` §2 U-AS-21 (code-level enum authorship) |
| Empirical anchors | `harness-as/src/harness_as/secret_negative_observation.py:36-42` (enum, 4 members); `:119-133` (`verify_sole_resolution_path`, hardcoded `surface=`); `harness-as/tests/test_secret_negative_observation.py:42-49` (only call sites; untested `.surface` field); `harness-as/src/harness_as/__init__.py:230,471` (re-export only) |
| Zero production callers | Confirmed via full-repo grep — latent, not reachable in production today |
| Resolution path | Per workspace `CLAUDE.md` §4.3 Class 1 → operator ratifies Q1 (member name) + Q2 (bundled dispatch fix or not); apply arc lands the enum member + (if Q2=a) the dispatch fix + updated test assertion at a follow-on PR |
| Cross-axis cascade | ZERO under every reading — AS-axis-internal, zero production callers |
| Registered at | `.harness/forward-register.yaml` id `B-24` / `.harness/post-phase-8-forward-register.md` §"B-24" |
