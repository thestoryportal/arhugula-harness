# Cross-Axis Composition Document (v2.23)

*Delta over v2.22. v2.23 is a **CLASSIFICATION-ONLY** delta for the RATIFIED **B-69 durable-pause-state read accessor arc** (council record `.harness/council-b69-pause-state-accessor-2026-07-30.md`; operator ratified OPTION A′ 2026-07-30). It registers **NO new edge and adds NO §2.3 row**: the plan-canonical §2.1 aggregate (**107** = 37 genuine + 48 convention + 22 phase-2-runtime) is **frozen verbatim**, and the §2.3.8 R-PM-1 family (2 edges), the §2.3.9 B-54 edge (1 edge) and the §2.3.10 B-33 edge (1 edge) are each **frozen verbatim** — the reported total remains **111**. What v2.23 DOES is discharge the classification obligation CP spec v1.112 §2.4 and Runtime spec v1.107 §14.14.9.3 both name as owed: an explicit, re-verified determination of how the NEW CP-published projection-returning surface consumed by `harness-runtime` relates to this document's enumeration, **stated rather than carried forward unexamined** — the discipline `Spec_Control_Plane_v1_106.md` §3 applied to itself. ZERO change to §2.1 / §2.2 / §2.3.1–§2.3.10 / §2.4 / §3 (all preserved verbatim). 2026-07-30.*

## §0 Change note (v2.22 → v2.23)

### §0.1 Revision context — the surface under classification

The `B-69` arc introduces one new cross-package consumption: `harness-runtime`'s NEW §14.14.9 durable-pause-state read accessor (`Spec_Harness_Runtime_v1.md` v1.107) consumes a NEW **public projection-returning surface** published by `harness-cp` (`Spec_Control_Plane_v1_112.md` §2) — an ordered sequence of typed location projections over the resume tree, carrying the authoritative four-variant classification (HITL-addressable / effect-fence-addressable / uniform-fallback-only / transitively-paused) plus tree position.

The surface exists for a **safety** reason, not a convenience one: the gate-owning-vs-container distinction (CP §1.2 property 5), the never-keyable pre-dispatch identity (CP §1.1(b)), and the effect-fence-abort suppression (CP property 8) are a safety classification whose semantics were corrected three times in six weeks. Re-deriving them Runtime-side would give the classification **two authorities that can drift** — so CP publishes and Runtime consumes, with the checkable acceptance criterion *"Runtime's accessor contains no recursion over `PauseSnapshot` and reads no nested resume-carrier field."*

### §0.2 The determination — explicit, and made rather than deferred

**Three findings, each verified at this filing rather than assumed.**

**(1) The consumption is NOT a member of this document's enumerated relationship space.** `[HIGH]` §2.1's aggregate is a **4×4 matrix over the four design axes — IS / AS / CP / OD**. `harness-runtime` is not one of those four; it is the composition root that imports across them. Every forward-capability row this document has added since v2.20 (§2.3.8's two R-PM-1 edges, §2.3.9's B-54 edge, §2.3.10's B-33 edge) is an **axis→axis** edge in which `harness-runtime` appears strictly as the **MEDIATOR** (the "Mediation" column), never as a consumer or producer endpoint. A `harness-runtime` → `harness-cp` consumption therefore has **no endpoint pair to occupy** in either the plan-canonical matrix or the forward-capability tables.

**(2) It introduces NO new crossing point.** `[HIGH]` The surface is consumed at the SAME already-established `harness-runtime` → `harness-cp` boundary that **three sibling public CP computations** are already consumed across — the HITL uniform-fallback-eligible run-id computation, the effect-fence uniform-fallback-eligible-key computation, and the effect-fence tree-wide-abort-presence computation — all three wired at the same runtime consumption site. B-69 adds a fourth member to an existing family, not a new family.

**(3) But the PAYLOAD widens materially, and this document says so rather than assuming it away.** `[HIGH]` The three existing siblings each return a **single scalar**. The B-69 surface returns a **structured, ordered sequence of typed discriminated-union projections**. That is a real change in what crosses the boundary — in shape, in size, and in the number of contract terms the two sides must agree on. **"No new crossing point" must not be allowed to carry weight it cannot.** The widening is recorded here explicitly so that a future arc reading this determination sees the payload change, not merely the absence of a row.

### §0.3 Ruling

> **NO new §2.3 row is added. The §2.1 aggregate is FROZEN. The reported total remains 111.**
>
> **The B-69 CP→Runtime projection consumption is classified as `harness-runtime` composition-root consumption of a CP-published public computation — the SAME relationship class as the three existing sibling scalar computations, and outside the IS/AS/CP/OD relationship space §2.1 enumerates.** It is therefore covered by existing structure rather than registered as a new edge.
>
> **Two riders bind this ruling, so it cannot be cited as more than it is:**
>
> **(a)** The determination is about **enumeration membership**, not about significance. The touch is real; the payload widening (three scalars → one structured sequence) is real; neither is denied by the absence of a row.
>
> **(b)** The ruling is **conditional on the direction holding**. If the impl leg finds it cannot compose the accessor without `harness-cp` importing `harness-od`, or without a genuine NEW axis→axis typed seam, that is a **fresh Class 1/2 fork question for the impl leg to raise** — NOT something this classification resolves in advance. The `harness-cp` MUST NOT import `harness-od` constraint (§2.3.3's OD→CP canonical direction) is **preserved unchanged** by this arc, which touches no OD-consuming CP code path.

### §0.4 Why this delta exists at all, given it registers nothing

A version that adds no row may look like a no-op. It is not, for the same reason `Spec_Control_Plane_v1_111.md` (a prose-only miscount fix) earned its own version: **the determination is the deliverable.** CP spec v1.106 §3 established the standing discipline that a CXA classification is *"re-verified at this correction pass, not carried forward unexamined"*; CP v1.112 §2.4 and Runtime v1.107 §14.14.9 both cite an owed CXA classification by name. An arc that widened a cross-package payload and left the classification implicit would be exactly the silent carry that discipline exists to prevent. **A no-row determination that was made is a different artifact from a determination that was skipped** — and only a filed version makes the difference legible.

### §0.5 Aggregate clause (UNCHANGED from v2.22, restated for the byte-exact record)

**107 plan-canonical (FROZEN) + 2 R-PM-1 forward-capability (§2.3.8, `R-live`) + 1 B-54 audit-verification forward-capability (§2.3.9, `R-live` since 2026-07-20/PR #1067) + 1 B-33 rotation-pair-evidence forward-capability (§2.3.10, `R-planned` — flips `R-live` at the impl arc) = 111 total cross-axis relationships.**

**No term of this clause changes at v2.23.** B-69 contributes zero.

### §0.6 What is frozen verbatim (NOT touched by v2.23)

§2.1 aggregate 4×4 matrix (107) + the 37/48/22 sub-split; §2.2 axis-level dependency graph; §2.3.1–§2.3.7 per-bucket rows; §2.3.8 (2 R-PM-1 edges); §2.3.9 (1 B-54 edge, `R-live`); §2.3.10 (1 B-33 edge, `R-planned`); §2.4; §3. **No cell of any existing table is edited, and no status flag is flipped by this delta.**

---

*All prior sections preserved verbatim per the delta convention. Clearance marker owed at `.harness/clearance/cross-axis-composition-v2-23-cleared-2026-07-30.md`.*
