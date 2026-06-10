# Spec: Operational Discipline — v1.24 (delta over v1.23)

---

## Change-note (v1.23 → v1.24)

**Scope of revision.** Fidelity-pure citation-correction patch closing v1.23 §"Adjacent observations" finding (f) — `harness-od/` enum-rename arc deferred — via DERIVATIVE-naming retirement at the production code layer. v1.23 §1.2 + v1.3 separated the requirement-level + stability dimensions at the canonical-reading layer but explicitly preserved enum member identifiers (`REQUIRED_STABLE` / `RECOMMENDED_DEVELOPMENT` / `OPT_IN_CONTENT`) + their string values (`"Required (Stable)"` / `"Recommended (Development)"` / `"Opt-In content"`) at `harness-od/src/harness_od/otel_genai_base.py:113-116` as DERIVATIVE naming per v1.16 §1.2 precedent. v1.24 retires the DERIVATIVE naming: enum identifiers + values renamed to canonical OTel vocabulary (`REQUIRED` / `RECOMMENDED` / `OPT_IN`); `CONDITIONALLY_REQUIRED` was already canonical at v1.16 §1.2 and PRESERVED VERBATIM. v1.23 + earlier file bodies PRESERVED VERBATIM per delta-only-spec-file convention.

**Audit lineage.** v1.23 (f) was authored 2026-05-27 (this session, ~70 minutes before v1.24) as a NEW carry with framing "deferred as future operator-discretion routing". Operator-routed 2026-05-27 (immediate same-session sequel post-v1.23 push to `origin/main` at `8316383`). The "future" of v1.23 (f) was 70 minutes. Sub-species classification: 3.same-session-immediate-sequel — distinct from prior sub-species in that the resolution-event lands in the same session as the carry's authoring; the carry exists only as a scope-control device at v1.23 to keep that arc fidelity-pure.

**Empirical verification.**

- Pre-amendment grep at `harness-od/` (worktree HEAD post-v1.23 push):
  - `REQUIRED_STABLE` / `RECOMMENDED_DEVELOPMENT` / `OPT_IN_CONTENT` identifier callsites: 43 unique across 3 files (`harness-od/src/harness_od/otel_genai_base.py`, `harness-od/tests/test_otel_genai_base.py`, `harness-od/src/harness_od/harness_breaker_schema.py`).
  - String-value usages (`"Required (Stable)"` / `"Recommended (Development)"` / `"Opt-In content"`) at `test_otel_genai_base.py:152-155` — 3 sites in the per-tier value-assertion test.
- Pre-amendment grep at non-`harness-od/` Python: ZERO external consumers (no `harness_*` package imports `AttributeTier.REQUIRED_STABLE` etc.).
- Pre-amendment grep at design-substrate/.md: 7+ files cite the DERIVATIVE names (Phase_7_Class_1_Tension_004 + Implementation_Plan_OD_v2_5 + Implementation_Plan_OD_v2_20 + Implementation_Plan_OD_v2_22 + Spec_OD_v1_19 + Spec_OD_v1_23 + class_1_tension_u_od_09_tier_classification_design_gap). All sites PRESERVED VERBATIM per delta-only-spec-file convention + workspace `CLAUDE.md` §4.3 file-resident text immutability discipline; downstream readers apply the v1.24 §1.2 substitution table when interpreting prior-version cites.
- Post-amendment test verification: 26/26 `harness-od/tests/test_otel_genai_base.py` pass + harness-od full suite passes.

**Distinctive lineage finding.** v1.23 (f) closes via a NEW closure event class — **same-session-immediate-sequel** — distinct from all 4 prior species 3 sub-species (3.code-resolution / 3.fork-doc-closure / 3.workflow-grammar / 3.empirical-verification-of-external-authority). Closure event is "carry deliberately authored as scope-control device at version vN; resolution-event lands in the SAME SESSION at version vN+1 as the immediate sequel arc." Distinguished by intent: prior species 3 sub-species operate on resolution-events that occur EXTERNAL to the originating arc (separate commit / fork doc / workflow-doc publication / WebFetch); same-session-immediate-sequel operates on intra-session sequencing. This is a sub-species refinement at column "Sub-species" of workflow v1.9 §7.4.7.2 species 3. Sub-species set at species 3 now FIVE: code-resolution / fork-doc-closure / workflow-grammar / empirical-verification-of-external-authority / same-session-immediate-sequel.

**No fork doc filed.** Per workspace precedent for fidelity-pure citation-correction patches anchored at conclusive empirical state. v1.23 (f) carry-text IS canonical authority anchor for the retirement.

**Production-code co-publication.** Enum rename across 3 `harness-od/` files for byte-exact alignment with v1.23 §1.2 canonical reading. Identifier mapping: `REQUIRED_STABLE` → `REQUIRED`; `RECOMMENDED_DEVELOPMENT` → `RECOMMENDED`; `OPT_IN_CONTENT` → `OPT_IN`. String-value mapping: `"Required (Stable)"` → `"Required"`; `"Recommended (Development)"` → `"Recommended"`; `"Opt-In content"` → `"Opt-In"`. `CONDITIONALLY_REQUIRED` identifier + `"Conditionally Required"` value PRESERVED VERBATIM (already canonical at v1.16 §1.2). Test assertions at `test_otel_genai_base.py:152-155` per-tier value-set refreshed in lockstep. Comment + docstring cites at v1.23 co-publication refreshed where they reference the DERIVATIVE names. ZERO behavior change at the AttributeTier consumers — emission gating + cardinality-safe-attribute discipline + redaction discipline operate on tier IDENTITY, not on identifier-string or value-string lookup.

**Co-publication this session.** Workspace `CLAUDE.md` §2.3 OD spec row bumped to v1.24 with closure narrative. ZERO cross-axis cascade verified via grep (no non-`harness-od/` Python consumer of the renamed identifiers; no test outside `harness-od/tests/` asserts on the string values).

---

## §1 Finding-closure-disposition refresh

### §1.1 v1.23 §"Adjacent observations" finding (f) — CLOSED

**Carry-text at v1.23.** *"NEW at v1.23 — `harness-od/` enum-rename arc deferred. Production code at `harness-od/src/harness_od/otel_genai_base.py:102–104` carries enum member names (`REQUIRED_STABLE` / `RECOMMENDED_DEVELOPMENT` / `OPT_IN_CONTENT`) that conflate the requirement-level + stability dimensions per v1.2-lineage label naming. Per v1.16 §1.2 precedent (DERIVATIVE-naming preservation), enum identifiers are PRESERVED at this arc; rename pass is a separate ~3-file ~49-site arc owed at future operator-discretion routing. Class 3 informational. The DERIVATIVE-naming framing is documented at this v1.23 arc (production comments refreshed to cite canonical names alongside derivative names)."*

**Disposition at v1.24.** **CLOSED-by-DERIVATIVE-naming-retirement-at-production-code-layer** 2026-05-27. Operator-routed same-session immediately post-v1.23 push to `origin/main` (`8316383`). Identifier rename + string-value rename + test-assertion refresh landed across 3 `harness-od/` files; 26/26 tests pass; ZERO behavior change at consumers; ZERO cross-axis cascade. Sub-species: 3.same-session-immediate-sequel.

### §1.2 Identifier + value mapping table (v1.24 canonical)

The v1.24 canonical reading retires the v1.2-lineage DERIVATIVE naming at the production-code layer. The substitution table below applies to all `harness-od/` Python sites + (in DERIVATIVE-name-citation mode) to all prior-version design-substrate/ cite sites:

| Pre-v1.24 identifier | Pre-v1.24 string value | v1.24 identifier | v1.24 string value |
|---|---|---|---|
| `REQUIRED_STABLE` | `"Required (Stable)"` | `REQUIRED` | `"Required"` |
| `CONDITIONALLY_REQUIRED` | `"Conditionally Required"` | `CONDITIONALLY_REQUIRED` | `"Conditionally Required"` |
| `RECOMMENDED_DEVELOPMENT` | `"Recommended (Development)"` | `RECOMMENDED` | `"Recommended"` |
| `OPT_IN_CONTENT` | `"Opt-In content"` | `OPT_IN` | `"Opt-In"` |

Tier classification per-attribute at §C-OD-04 §4.3 base-layer table (v1.16 §1.3 PRESERVED VERBATIM at v1.23): UNCHANGED. Tier assignment IDENTITY unchanged; only the identifier + string-value labels are refined to drop the conflated stability suffix per v1.23 §1.2 dimensional split.

### §1.3 Disposition summary

| v1.23 carry | Closure event | Closure commit | Status at v1.24 |
|---|---|---|---|
| §"Adjacent observations" (f) | DERIVATIVE-naming retirement at production code layer + 3-file 46-site rename + 26/26 tests pass | this session (filing commit on `worktree-od-spec-v1-24-enum-rename-pass`) | **CLOSED** |

Carry removed from v1.24 §"Adjacent observations" carry-set. v1.23 file body PRESERVED VERBATIM per delta-only-spec-file convention; v1.24 §1 is the canonical-reading amendment for the disposition layer.

---

## §2 Cross-artifact cite-cascade disposition (v1.24 NEW)

| Artifact | Site | Disposition at v1.24 |
|---|---|---|
| `harness-od/src/harness_od/otel_genai_base.py` | `AttributeTier` enum (lines 113–116) + BASE_LAYER_ATTRIBUTES references + docstring cites of derivative names | **CO-PUBLISHED this arc** — identifier rename + string-value rename + docstring refresh |
| `harness-od/tests/test_otel_genai_base.py` | 43-site enum-name reference set + per-tier value-set assertion (lines 152–155) | **CO-PUBLISHED this arc** — rename + value-assertion refresh |
| `harness-od/src/harness_od/harness_breaker_schema.py` | Enum-name cite | **CO-PUBLISHED this arc** — rename |
| `.harness/archive/root-historical/Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md` | Pre-v1.24 derivative-name cites | NO change owed — file-resident text immutability per workspace `CLAUDE.md` §4.3; readers apply v1.24 §1.2 substitution table |
| `design-substrate/Implementation_Plan_Operational_Discipline_v2_5.md` | Pre-v1.24 derivative-name cites | NO change owed — delta-only-spec-file convention; readers apply v1.24 §1.2 substitution table |
| `design-substrate/Implementation_Plan_Operational_Discipline_v2_20.md` | Pre-v1.24 derivative-name cites | NO change owed — delta-only-spec-file convention; readers apply v1.24 §1.2 substitution table |
| `design-substrate/Implementation_Plan_Operational_Discipline_v2_22.md` | Pre-v1.24 derivative-name cites | NO change owed — delta-only-spec-file convention; readers apply v1.24 §1.2 substitution table |
| `design-substrate/Spec_Operational_Discipline_v1_19.md` | Pre-v1.24 derivative-name cites | NO change owed — delta-only-spec-file convention; readers apply v1.24 §1.2 substitution table |
| `design-substrate/Spec_Operational_Discipline_v1_23.md` | Pre-v1.24 derivative-name cites at §1 + §"Adjacent observations" (f) | NO change owed — v1.23 PRESERVED VERBATIM; v1.24 (f) closure references these cites by-version |
| `.harness/class_1_tension_u_od_09_tier_classification_design_gap.md` | Pre-v1.24 derivative-name cites | NO change owed — fork-doc convention preserves authoring-time text |
| Workspace `CLAUDE.md` §2.3 OD spec row narrative | v1.23 row narrative | **CO-PUBLISHED this arc** — bumped to v1.24 with closure narrative |

---

## §3 Sections preserved verbatim at v1.24

Per delta-only-spec-file convention + FM-2 no-extension discipline + fidelity-pure citation-correction scope, the v1.24 amendment touches ONLY the NEW §1 finding-closure-disposition refresh + §2 cross-artifact cite-cascade disposition + §"Adjacent observations" refresh. The following sections are PRESERVED VERBATIM from their authoring versions:

- **§C-OD-04 §4.1 / §4.2 / §4.3 / §4.3.1 / §4.4 / §4.5** (v1.23 §1.2 + §1.3 amendments preserved; tier classification per-attribute UNCHANGED; only the production-code identifier + string-value vocabulary is refined at v1.24 §1.2)
- **§C-OD-05 through §C-OD-33** (all v1.2-v1.23 lineage content)
- **All v1.3–v1.23 substantive amendments**

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **v1.23 finding (f) — CLOSED-by-DERIVATIVE-naming-retirement at v1.24 §1.1–§1.2.** Removed from "Adjacent observations" carry.

(b) **v1.23 finding (b) — §8.4.2 anticipated cases empirical-verification.** Carried verbatim from v1.16 → v1.17 → v1.18 → v1.19 → v1.20 → v1.21 → v1.22 → v1.23 → v1.24. Sweep verification 2026-05-27: production grep for the 3 anticipated cases returns ZERO production hits at HEAD; deferred-monitor status preserved. v1.24 does NOT touch this carry.

(c) **v1.23 finding (c) — v1.15 §15.2 vs §15.4 split informational.** Carried verbatim. AS spec v1.7 unchanged since v1.17; carry remains genuine. v1.24 does NOT touch this carry.

(d) **v1.23 finding (d) — discipline-validation observation (informational, Class 3).** Carried verbatim with strengthening at v1.24 §"Change-note" — v1.24 closure validates the empirical-verification-of-external-authority sub-species (sibling at v1.23) AND establishes the same-session-immediate-sequel sub-species. The discipline empirically validates across two consecutive arcs.

(e) **v1.23 finding (e) — sub-species 3.workflow-grammar catalogued.** Carried verbatim. v1.24 adds a second sibling sub-species 3.same-session-immediate-sequel at §"Change-note" Distinctive lineage finding. The sub-species set at species 3 now FIVE (code-resolution / fork-doc-closure / workflow-grammar / empirical-verification-of-external-authority / same-session-immediate-sequel); future workflow-doc revision MAY consolidate at §7.4.7.2 "Sub-species" column extension per v1.23 finding (g) candidate.

(f) **v1.23 finding (g) — workflow v1.9 §7.4.7.2 sub-species column extension candidate.** Carried verbatim with cardinality refresh: 4 sub-species at v1.23 authoring → 5 sub-species at v1.24 (NEW same-session-immediate-sequel sub-species). The candidate strengthens at v1.24 — five sub-species in three consecutive arcs (v1.22 → v1.23 → v1.24) is empirical evidence the column extension is warranted. v1.24 does NOT patch the upstream artifact per FM-2.

(g) **NEW at v1.24 — same-session-immediate-sequel sub-species catalogued.** v1.23 (f) → v1.24 closure landed in ~70 minutes within the same session. The carry existed only as a scope-control device at v1.23 (FM-2 single-focus arc discipline). Pattern catalogued: when a fidelity-pure arc surfaces an adjacent defect, deferring it to a same-session sequel is a legitimate scope-control mechanism distinct from cross-session deferral. The sequel arc inherits the originating arc's discipline + empirical-verification context. Class 3 informational; NOT patched per FM-2 single-focus arc scope.

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.24 (Fidelity-pure citation-correction patch closing v1.23 §"Adjacent observations" finding (f) `harness-od/` enum-rename arc — via DERIVATIVE-naming retirement at production code layer; identifier rename `REQUIRED_STABLE` → `REQUIRED` + `RECOMMENDED_DEVELOPMENT` → `RECOMMENDED` + `OPT_IN_CONTENT` → `OPT_IN`; string-value rename in lockstep; `CONDITIONALLY_REQUIRED` PRESERVED VERBATIM as already canonical at v1.16; v1.23 + earlier files PRESERVED VERBATIM per delta-only-spec-file convention) |
| Trigger | Operator-routed same-session immediately post-v1.23 push to `origin/main` (`8316383`); v1.23 (f) carry existed for ~70 minutes before closure |
| Supersedes | v1.23 §"Adjacent observations" (f) carry framing — superseded at v1.24 §1 closure. v1.16 §1.2 DERIVATIVE-naming preservation framing — superseded at v1.24 §1.2 substitution table at the production-code layer (the v1.16 §1.2 spec-side mapping table remains the canonical-reading authority for prior-version derivative-name cites). |
| Scope of revision | NARROW: NEW §1 + §2 + §3 + §"Adjacent observations" refresh. ZERO contract / signature / AC / behavior change at runtime. Co-publication: production code identifier + string-value rename across 3 `harness-od/` files; workspace CLAUDE.md OD spec row bump. |
| Cross-axis cascade | ZERO. Verified via grep — no non-`harness-od/` Python consumer of the renamed identifiers; design-substrate/.md cites are PRESERVED VERBATIM per delta-only-spec-file convention. |
| Authority anchor | OD spec v1.23 §1.2 + §1.3 dimensional split (canonical-reading authority); OTel 1.41.0 archived text `gen-ai-spans.md` (the canonical vocabulary mirrored at v1.24); v1.23 (f) carry-text retirement |
| Predecessor | v1.23 (Fidelity-pure citation-correction patch closing v1.22 (e) `gen_ai.provider.name` stability tier divergence via §4.3 dimensional split + NEW §4.3.1 stability classification) |
| Successor | v1.25 (next operator-discretion arc — candidates: v1.24 (b) §8.4.2 anticipated cases; (c) v1.15 §15.2 vs §15.4 split; (f)/(g) sub-species column extension at workflow-doc) |
| Audit lineage | v1.23 (f) carry deliberately authored at v1.23 as scope-control device; resolved at v1.24 same-session immediate sequel (~70 minutes carry lifetime). Pattern catalogued: same-session-immediate-sequel sub-species at workflow v1.9 §7.4.7.2 species 3. |
