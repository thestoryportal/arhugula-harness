# Implementation Plan — Operational Discipline (v2.27)

*Delta over v2.26. v2.27 AUTHORS NEW §4.6 "OD-internal cross-cluster dependency" section per halt-doc Item 12 (OD-INTERNAL-FORMALIZATION) operator AskUserQuestion 2026-05-31 Option (B) carve-out + C3-15 examples. The section formalizes the distinction between OD-axis-internal cross-cluster composition (within-axis; NOT cross-axis edge) and genuine cross-axis composition (declared at §4.5). Canonical examples drawn from the 2 deleted U-OD-27 rows at the v2.4 §0.4.2 C3-15 Path (i-refined) absorption record: U-OD-27 → sqlite substrate + U-OD-27 → ring-buffer eviction. Discriminator provided for future cases. Sibling to PR #110 (CXA v2.18) closing halt-doc Item 11. §4.5 + §4.5.1 / §4.5.2 / §4.5.3 cross-axis enumeration PRESERVED VERBATIM. ZERO new contract; ZERO new atomic unit; ZERO acceptance criterion change at any existing unit; ZERO cross-axis cascade. NEW §4.6 is documentation-formalization scope — establishes a discriminator dimension (OD-internal vs cross-axis) that existed implicitly at the C3-15 deletion rationale but was not section-formalized prior to v2.27.*

## §0 Change note (v2.26 → v2.27)

### §0.1 Revision context — halt-doc Item 12 closure

Per `.harness/halt-overnight-expansion-2026-05-31.md` §"Halt-3 — Item 12: OD-INTERNAL-FORMALIZATION (Class 3)":

> The C3-15 Path (i-refined) deletion record (rows 2+3 of v2.3 §4.5.1) identifies sqlite substrate residence + ring-buffer eviction as OD-internal concerns falsely declared as OD→IS cross-axis edges at v2.3. The OD plan does not currently have an explicit "OD-internal cross-cluster dependency" section that would canonicalize these compositions outside §4.5.* cross-axis enumeration. [...] Routing target: Design-phase session — author formalization section via spec-writer (or implementation-planner if it's a plan-side definition), adversarial review, clearance marker, PR.

Operator AskUserQuestion 2026-05-31 ratified Option (B) — carve-out + C3-15 examples (bounded scope; addresses the recurrence concern without enumerating the full OD DAG). Sibling PR #110 closes halt-doc Item 11 (CXA v2.18 OD→IS bucket refresh). Per `[[advisor-44th-application-dont-bundle-distinct-structural-shapes]]` — refresh-vs-new-authoring shapes are distinct; sibling PRs not bundled.

### §0.2 Sections revised

§0 (this change note); NEW §4.6 "OD-internal cross-cluster dependency" (authored at v2.27 — section did not exist at v2.26 or prior). All other sections preserved verbatim from v2.26 (which preserved verbatim from v2.25 + v2.24 + ... + v2.6 chain).

### §0.3 Scope discipline

Per Option (B) ratification: section authoring is **carve-out + C3-15 examples**, NOT full OD DAG within-axis enumeration. The OD plan's internal DAG is already encoded at §4.6 (DAG traversal) at the v2.1 baseline and preserved through v2.26; v2.27's NEW §4.6 (here authored as §4.6.1 sub-section to avoid renumbering conflict — see §0.4) does NOT duplicate the DAG encoding. Section is a definitional + discriminator + 2-example surface; ~50 lines of plan body.

### §0.4 Section numbering

The v2.1-baseline OD plan §4.6 already houses "DAG topology + traversal" content. To avoid renumbering disruption at the §4.x chain (preserved verbatim through v2.26), v2.27 authors NEW content at **§4.6.OD-INTERNAL** as a sub-section under the existing §4 structure. Discoverable via filing footer + this change-note. Alternative renumbering (§4.7 vs sub-section under §4.5) ratified at operator AskUserQuestion 2026-05-31 by AC clause defaulting to sub-section-under-§4.6 (lower disruption to delta-only-chain preservation).

Section authority note: NEW §4.6.OD-INTERNAL is a peer-level documentation surface to §4.5 (Cross-axis edge enumeration) at the discriminator-dimension layer (within-axis vs cross-axis), even though it lives at §4.6 sub-section per the numbering discipline above.

---

## §1 NEW §4.6.OD-INTERNAL — "OD-internal cross-cluster dependency"

(Authored at v2.27; canonical body below; reference from §4 §4.6 should treat this as a sub-section sibling to the existing DAG-traversal content per §0.4 numbering discipline.)

### §1.1 §4.6.OD-INTERNAL.1 — Definitional carve-out

An **OD-internal cross-cluster dependency** is a within-OD-axis composition where a unit at one OD cluster depends on a unit at a different OD cluster, BUT the composition does NOT cross an axis boundary (the dependency target is also at OD axis).

**OD-internal cross-cluster dependencies are NOT cross-axis edges** and MUST NOT be declared at §4.5.* (cross-axis edge enumeration). Declaring an OD-internal composition as a cross-axis edge is the **C3-15 mis-routing failure mode** — it inflates the cross-axis edge count, surfaces non-resolving IS-spec / AS-spec / CP-spec contract anchors (the target is OD-internal; no foreign-axis contract exists), and propagates a structurally false claim about axis boundaries.

Per workspace CLAUDE.md §1.1 axis-boundary discipline: cross-axis edges are declarations of dependency that traverse the IS / AS / CP / OD axis boundaries. Within-axis compositions — including within-OD-axis cross-cluster dependencies — are encoded at the per-axis DAG (OD plan §4.6 DAG traversal) and the per-cluster acceptance criteria at §3.

### §1.2 §4.6.OD-INTERNAL.2 — Canonical examples (C3-15 deletion record)

The C3-15 Path (i-refined) absorption at OD plan v2.4 §0.4.2 deleted 2 rows from v2.3 §4.5.1 that were OD-internal mis-routed as OD→IS cross-axis. These deletions are canonical examples of OD-internal cross-cluster dependencies:

| Example | OD-internal composition | Why NOT cross-axis | Within-axis cluster pair |
|---|---|---|---|
| Example 1: sqlite substrate residence | U-OD-27 (collector substrate cluster) depends on the OD-side sqlite substrate (NOT an IS-axis primitive) | sqlite is the OD-side durable substrate per OD spec C-OD-27 §27.1 (post-batch-33 4-OD-B SqliteWritePath cluster landing); the substrate's residence is at OD-axis (`harness-od/src/harness_od/sqlite_span_store.py`); IS-axis has no canonical sqlite primitive at IS spec v1.2 or v1.3 | OD Cluster 7 → OD Cluster 4 (within-axis) |
| Example 2: ring-buffer eviction | U-OD-27 (collector substrate cluster) depends on the OD-side ring-buffer eviction discipline (NOT an IS-axis primitive) | Ring-buffer eviction is the OD-side telemetry-buffer lifecycle per OD spec C-OD-27 §27.4 (eviction-on-overflow + eviction-on-flush); IS-axis C-IS-08 §8.4 references shadow-Git checkpoint discipline, NOT ring-buffer eviction (the IS-side citation at v2.3 was a structurally wrong anchor) | OD Cluster 7 → OD Cluster 4 (within-axis) |

Both examples were declared as OD→IS cross-axis edges at the v2.3 §4.5.1 enumeration. The C3-15 audit identified the mis-routing; the v2.4 §0.4.2 absorption deleted the rows. v2.27 §4.6.OD-INTERNAL.2 formalizes the deletion rationale as canonical examples to prevent recurrence.

### §1.3 §4.6.OD-INTERNAL.3 — Discriminator for future cases

When a candidate dependency declaration surfaces during OD plan revision or U-OD-NN authoring, apply this discriminator BEFORE adding the row to §4.5.* cross-axis enumeration:

1. **Identify the dependency target's axis residence.** Where does the target carrier physically live? `harness-is/`, `harness-as/`, `harness-cp/`, `harness-od/`, or `harness-core/`?
   - If the target lives at `harness-od/`: candidate is OD-internal → declare at OD plan §3 (per-cluster ACs) or §4.6 (DAG traversal); do NOT declare at §4.5.
   - If the target lives at `harness-{is,as,cp}/`: candidate is genuinely cross-axis → declare at §4.5.{1,2,3} per axis-direction; verify the contract anchor resolves at the target axis's spec.

2. **Verify the contract anchor resolves at the target axis's spec.** Run a grep / cite-check against the target axis's spec file. A non-resolving anchor (e.g., the v2.3 `C-IS-13 §13.2` cite that didn't exist at IS spec v1.2) is a strong signal of mis-routing.

3. **If contract anchor resolves but the target carrier lives at OD axis:** the dependency is genuinely cross-axis at the anchor layer but OD-internal at the carrier layer. This is a hybrid case (rare). Surface as a Class 1 fork for architectural clarification per workspace CLAUDE.md §4.3 back-flow routing — do NOT silently absorb into either §4.5 or §4.6.OD-INTERNAL until the architectural shape is ratified.

4. **If all three checks pass at the cross-axis reading:** the dependency is genuinely cross-axis. Add the row to §4.5.{1,2,3} with canonical IS-plan / AS-plan / CP-plan unit cite + canonical spec contract anchor.

### §1.4 §4.6.OD-INTERNAL.4 — Relation to existing §4 structure

| Section | Content | Relation to §4.6.OD-INTERNAL |
|---|---|---|
| §3 (Atomic-unit decomposition) | Per-unit ACs + signatures + tests | OD-internal compositions surface implicitly at the unit body; §4.6.OD-INTERNAL provides the explicit discriminator |
| §4.5 (Cross-axis edge enumeration) | OD → IS / AS / CP edges declared at §4.5.1 / §4.5.2 / §4.5.3 | OD-internal compositions are EXCLUDED from §4.5.* by definition (§4.6.OD-INTERNAL.1 carve-out) |
| §4.6 (DAG topology + traversal) | OD-internal cluster-to-cluster dependencies encoded at the within-axis DAG | §4.6.OD-INTERNAL is the documentation-formalization peer; the DAG-traversal content remains canonical for actual within-axis topology |
| §5 (Coverage matrix) | Per-OD-contract coverage at unit landings | OD-internal compositions are NOT separate contract-coverage rows; they compose at the unit body to satisfy the per-OD-contract coverage |

### §1.5 §4.6.OD-INTERNAL.5 — Status posture

Section is **documentation-formalization scope** at v2.27 authoring. ZERO new contract; ZERO new atomic unit; ZERO acceptance criterion change at any existing unit; ZERO cross-axis edge added or removed; ZERO impact on per-OD-contract coverage matrix; ZERO production code change. The 2 canonical examples (sqlite substrate + ring-buffer eviction) are deleted-rows-as-examples from the C3-15 absorption record; they were NEVER cross-axis edges in operational state, only at the v2.3 stale enumeration that v2.4 §0.4.2 corrected.

---

## §2 Adjacent observations (NOT patched per FM-2 single-focus arc scope)

(i) **`harness-od/CLAUDE.md` discriminator refresh owed.** The per-axis `harness-od/CLAUDE.md` §2.3 (OD-internal cross-cluster dependencies — NOT cross-axis) sub-section may benefit from cross-referencing §4.6.OD-INTERNAL.3 discriminator at next per-axis CLAUDE.md hygiene arc. NOT patched at this PR per FM-2.

(ii) **Sibling-axis discriminator extension candidate.** The discriminator at §4.6.OD-INTERNAL.3 generalizes to other axes — within-IS-axis, within-AS-axis, within-CP-axis cross-cluster dependencies face the same mis-routing risk. Per-axis plan revisions at IS / AS / CP may benefit from sibling §4.6.{IS,AS,CP}-INTERNAL sub-sections at future plan revision arcs. NOT patched at this PR per FM-2; routes to future plan revision discretion.

(iii) **C3-15 sub-species candidate at workflow doc.** The C3-15 mis-routing failure mode (OD-internal declared as cross-axis) may be a sub-species candidate at workflow v1.13 §7.4.7.2 species catalogue (`cross-axis-edge-mis-routed-as-within-axis-composition` — distinct closure-event-class from prior species). Cardinality 1 at v2.27 publication; awaits second instance before workflow-doc promotion per existing catalogue discipline.

---

## §3 Sections preserved verbatim

§1 (Spec inventory), §2 (Cluster topology), §3 (Atomic-unit decomposition — all sub-sections; preserved through v2.26 delta chain), §4.1 through §4.5 (cross-axis edge enumeration + existing structural sections), §4.6 DAG-traversal content (preserved; §4.6.OD-INTERNAL is NEW sibling sub-section per §0.4), §5 (Coverage matrix), §6 (Filing footer of base v2.6 file).

---

## §4 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_27.md` |
| Filing event | NEW §4.6.OD-INTERNAL sub-section authored per halt-doc Item 12 (OD-INTERNAL-FORMALIZATION) closure. Carve-out + C3-15 examples + discriminator for future cases. Operator AskUserQuestion 2026-05-31 Option (B) ratification. Sibling to PR #110 (CXA v2.18 halt-doc Item 11 closure). 2026-05-31 |
| Authored at | Design-phase posture session 2026-05-31 (operator-declared per workspace CLAUDE.md §11.3) |
| Authoring authority | Operator AskUserQuestion 2026-05-31 Option (B) carve-out + C3-15 examples ratification + sibling-PR convention per `[[advisor-44th-application-dont-bundle-distinct-structural-shapes]]` |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_26.md` (preserved verbatim except NEW §4.6.OD-INTERNAL sub-section authored at this delta) |
| Successor | TBD per next OD plan arc |
| Sibling PR | CXA v2.18 (PR #110) — halt-doc Item 11 CXA-OD-IS-EDGE-DRIFT |
| Clearance marker | `.harness/clearance/Implementation_Plan_Operational_Discipline-v2_27-cleared-2026-05-31.md` |
