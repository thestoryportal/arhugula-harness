# Cross-Axis Composition Document (v2.18)

*Delta over v2.17. v2.18 ABSORBS the long-carried CXA-OD-IS-EDGE-DRIFT (`Implementation_Plan_Operational_Discipline_v2_4.md` §6 Filing-footer adjacent finding; halt-doc Item 11 at `.harness/halt-overnight-expansion-2026-05-31.md`) by amending §2.3.4 OD→IS bucket enumeration from the v2.1-baseline 6-row form (`U-IS-NN` placeholders with non-resolving IS-spec anchors) to the operator-ratified C3-15 Path (i-refined) 4-row form at OD plan v2.4 §4.5.1 (canonical IS-plan unit cites + canonical C-IS-10 anchors). Bucket cardinality 6 → 4 (–2 net: U-OD-27's 2 mis-routed rows DELETED as OD-internal; U-OD-30's 2 rows REMAPPED to canonical C-IS-10 anchors; U-OD-20 + U-OD-34 PRESERVED with canonical U-IS-12 / U-IS-17 cites). §2.1 aggregate matrix OD→IS cell 6 → 4; aggregate total 107 → 105. §2.4 per-axis attribution OD outbound 28 → 26 (3 / 3 bucket-coverage preserved; OD remains consumer-most axis). ZERO change to §2.3.1 / §2.3.2 / §2.3.3 / §2.3.5 / §2.3.6 / §2.3.7 / §2.2. Direction is CXA-conforms-to-plan per operator AskUserQuestion 2026-05-31 ratification of probe finding: the C3-15 deletions (sqlite + ring-buffer ARE OD-internal, not cross-axis) are substantively correct + operator-ratified at OD plan v2.4 §0.4.2 Session 3 work; CXA §2.3.4 carrying the pre-C3-15 mis-routed rows is the staleness defect.*

## §0 Change note (v2.17 → v2.18)

### §0.1 Revision context — CXA-OD-IS-EDGE-DRIFT closure (halt-doc Item 11)

Per `.harness/halt-overnight-expansion-2026-05-31.md` §"Halt-2 — Item 11: CXA-OD-IS-EDGE-DRIFT (Class 3) revision":

> CXA v2.1 §2.3.4 (6 OD→IS edges enumerated) vs OD plan v2.4 §4.5.1 (4 edges enumerated post C3-15 Path (i-refined) deletions). [...] Routing target: Design-phase session — open council deliberation, ratify direction, apply via spec-writer skill, file clearance marker, PR.

(Halt-doc cited §2.3.5; corrected at probe — §2.3.5 is OD→AS; §2.3.4 is OD→IS at v2.1 numbering.)

The halt-doc named direction-ratification as the blocking decision. Pre-substantive empirical probe at v2.18 arc this session resolved the tension cleanly without council activation per PR #94 standing-posture amendment 1 (nameable-tension discriminator — probe surfaced no real voice-tension; operator already ratified the direction at C3-15 Path (i-refined) Session 3 work). Per amendment 5 (probe-first discipline at tension resolution), the finding was surfaced as `tension-surfaced + probe-resolved` and operator AskUserQuestion ratified Option (A) CXA-conforms-to-plan 2026-05-31.

### §0.2 Sections revised

§0 (this change note); §2.1 (aggregate 4×4 matrix — OD→IS bucket cell 6 → 4; aggregate total 107 → 105); §2.3.4 (OD→IS per-bucket enumeration — 6 rows → 4 rows per C3-15 Path (i-refined) absorption); §2.4 (per-axis outbound posture summary — OD outbound 28 → 26; aggregate 107 → 105). All other sections preserved verbatim from v2.17 (which preserved verbatim from v2.16 + v2.15 + v2.14 + v2.13 + v2.12 + v2.11 + v2.10 + v2.9 + v2.8 + v2.7 + v2.6).

### §0.3 §2.3.4 row absorption (6 rows → 4 rows; C3-15 Path (i-refined))

The v2.1-baseline §2.3.4 enumeration (preserved verbatim through v2.17) is amended at v2.18 with row-by-row absorption per OD plan v2.4 §0.4.2 deletion + remap record:

**Pre-v2.18 §2.3.4 (CXA v2.1-baseline; 6 rows):**

| # | Source OD unit | IS target | Contract anchor |
|---|---|---|---|
| Row 1 | U-OD-20 | U-IS-NN (idempotency-key join unit) | C-IS-10 §10.2 |
| Row 2 | U-OD-27 | U-IS-NN (sqlite substrate unit) | C-IS-13 §13.2 |
| Row 3 | U-OD-27 | U-IS-NN (ring-buffer eviction unit) | C-IS-08 §8.4 |
| Row 4 | U-OD-30 | U-IS-NN (Tier-5 audit ledger durability) | C-IS-14 §14.2 |
| Row 5 | U-OD-30 | U-IS-NN (hash-chain integrity unit) | C-IS-13 §13.5 |
| Row 6 | U-OD-34 | U-IS-17 (terminal aggregate exporter) | IS substrate seam exports |

**v2.18 §2.3.4 (post C3-15 Path (i-refined); 4 rows):**

| # | Source OD unit | IS target | Contract anchor | U-OD-34 manifest entry |
|---|---|---|---|---|
| Row 1 | U-OD-20 | U-IS-12 (idempotency-key join carrier) | C-IS-10 §10.2 | export #6 |
| Row 2 | U-OD-30 | U-IS-11 (JSONL write contract carrier) | C-IS-10 §10.5 | export #8 |
| Row 3 | U-OD-30 | U-IS-10 (hash-chain verification carrier) | C-IS-10 §10.3 | export #8 |
| Row 4 | U-OD-34 | U-IS-17 (terminal aggregate exporter) | IS substrate seam exports | (terminal aggregate reference) |

**Row delta absorption (per OD plan v2.4 §0.4.2 + §4.5.1 record):**

```
DELETED: U-OD-27 → U-IS-NN (sqlite substrate) — C-IS-13 §13.2     [mis-routed OD-internal — formalization at halt-doc Item 12 OD plan v2.27 sibling PR]
DELETED: U-OD-27 → U-IS-NN (ring-buffer eviction) — C-IS-08 §8.4   [mis-routed OD-internal — formalization at halt-doc Item 12 OD plan v2.27 sibling PR]
REMAP:   U-OD-30 → U-IS-11 (was C-IS-14 §14.2 → now C-IS-10 §10.5)
REMAP:   U-OD-30 → U-IS-10 (was C-IS-13 §13.5 → now C-IS-10 §10.3)
PRESERVED: U-OD-20 → U-IS-12 (was U-IS-NN → now canonical U-IS-12; anchor unchanged)
PRESERVED: U-OD-34 → U-IS-17 (terminal aggregate; unchanged)
```

The 2 deleted U-OD-27 rows are NOT cross-axis edges per the C3-15 rationale: sqlite substrate residence + ring-buffer eviction are OD-axis internal (sqlite is the OD-side durable substrate, not an IS-axis primitive). Their formalization as OD-internal (NOT cross-axis) routes to halt-doc Item 12 follow-on at OD plan v2.27 (sibling PR per `[[advisor-44th-application-dont-bundle-distinct-structural-shapes]]`).

### §0.4 §2.1 aggregate matrix amendment

Pre-v2.18 §2.1 matrix at OD→IS cell: **6 canonical** (v2.1 baseline preserved verbatim through v2.17).
v2.18 §2.1 matrix at OD→IS cell: **4 canonical (−2)**.

Aggregate cross-axis edge count: **107 → 105** (–2 net).

| Source ↓ / Target → | IS | AS | CP | OD |
|---|---|---|---|---|
| **IS** | *(self)* | 0 | 0 | 0 |
| **AS** | 13 | *(self)* | 0 | 0 |
| **CP** | **43** *(v2.17)* | **19** *(v2.15)* | *(self)* | 0 |
| **OD** | **4** *(v2.18)* | 10 | **8** *(v2.9)* | *(self)* |

*(Cells in **bold** with version annotation reflect post-baseline absorption events; other cells preserved verbatim from v2.1 baseline.)*

**Aggregate cross-axis edge count: 105 edges across 6 non-empty buckets.**

### §0.5 §2.4 per-axis attribution amendment

Pre-v2.18 §2.4 OD row: **28 outbound** (v2.1 baseline preserved verbatim through v2.17; 6 IS + 10 AS + 12 CP). The cost-attribution audit-write seam at §2.3.7 row 8 (NEW at v2.9) is attributed to OD outbound per namespace-ownership convention at v2.9 §0.3, pushing the §2.4 effective OD-attributed total to 29 at the v2.9 framing while the §2.1 OD-row sum remained 6+10+12=28; this divergence-of-+1 was preserved through v2.17 per the established attribution convention.

v2.18 §2.4 OD row: **26 outbound** post-C3-15 conforming + cost-attribution attribution preserved (4 IS + 10 AS + 12 CP = 26 at §2.1 OD-row sum + 1 cost-attribution-attributed-to-OD seam at §2.3.7 row 8 surfaces as 27 at the v2.9 attribution framing). The §2.4 row text at v2.18 reads **26** at the §2.1-conformed OD-row sum reading; the **27** v2.9-attribution-framing reading is preserved as the attribution-divergence-convention overlay (unchanged at v2.18).

Updated §2.4 table at v2.18:

| Axis | Outbound cross-axis edges | Outbound buckets | Posture |
|---|---|---|---|
| IS | 0 | 0 / 3 | Pure foundational substrate; exports via U-IS-17 manifest; no outbound `Depends on` declarations |
| AS | 13 | 1 / 3 | Consumes IS substrate only; exports to CP / OD via U-AS-33 manifest |
| CP | 69 *(v2.17; was 63 at v2.15; was 62 at v2.6)* | 2 / 3 | Consumes IS + AS substrate; exports to OD via U-CP-54 (namespace) + U-CP-55 (F2-12 ACTIVE inheritance) |
| OD | **26** *(v2.18; was 28 at v2.1 baseline pre-C3-15; v2.9 attribution-divergence-convention overlay reads 27 with cost-attribution-attributed-to-OD)* | 3 / 3 | Consumer-most axis; consumes IS + AS + CP substrate; one inverted exporter (U-OD-09 → CP) |
| **Aggregate** | **105** *(v2.18; v2.17 was 107)* | — | — |

The attribution-divergence convention from v2.9 (cost.* attributed-to-OD despite living at CP→OD bucket at §2.1 layer) is preserved unchanged at v2.18; only the underlying §2.1 OD-row sum changes from 28 → 26 per the C3-15 absorption.

### §0.6 Status posture

| Status | Per-bucket | Per-axis |
|---|---|---|
| CXA-OD-IS-EDGE-DRIFT | **CLOSED-AT-v2.18** per operator AskUserQuestion 2026-05-31 Option (A) CXA-conforms-to-plan; §2.3.4 6 → 4 rows + §2.1 aggregate 107 → 105 + §2.4 OD outbound 28 → 26 | OD-axis cross-axis edge enumeration now CXA-side-and-plan-side-conformed at HEAD. C3-15 Path (i-refined) reconciliation arc closed. |

### §0.7 Forward-cite acknowledgement

Halt-doc Item 12 (OD-INTERNAL-FORMALIZATION) routes to **sibling PR at OD plan v2.27** authoring NEW §4.6 (or similar) "OD-internal cross-cluster dependency" section per operator AskUserQuestion 2026-05-31 Option (B) carve-out + C3-15 examples. The 2 deleted U-OD-27 rows at v2.18 §0.3 row-delta record (sqlite substrate + ring-buffer eviction) become canonical examples at the v2.27 carve-out section. Per `[[advisor-44th-application-dont-bundle-distinct-structural-shapes]]` — refresh-vs-new-authoring shapes are distinct; sibling PRs not bundled.

### §0.8 Adjacent defects surfaced (not patched per FM-2 no-extension discipline)

(i) **Workspace CLAUDE.md §1.1 OD-axis posture line refresh owed.** The workspace `CLAUDE.md` §1.1 OD row tracks "8 inbound edges from CP at U-OD-00 per CXA v2.17 §2.3.7" + "10 → AS" + "12 → CP" + "6 → IS at CXA v2.1 baseline / 4 at OD plan v2.6 per C3-15" with the explicit divergence cite. v2.18 closes the divergence (CXA now also at 4). Workspace `CLAUDE.md` §1.1 OD row should refresh from divergence-acknowledged to CXA-and-plan-conformed at v2.18 publication. Not patched at this PR per FM-2; surfaces at §0.9 downstream absorption owed.

(ii) **`harness-od/CLAUDE.md` §2.2 cross-axis edge inventory + §1.1 OD posture line.** Same refresh shape as (i) at per-axis CLAUDE.md scope. NOT patched per FM-2.

### §0.9 Downstream absorption owed (post-v2.18)

(a) Workspace `CLAUDE.md` §1.1 OD-axis row refresh from "6 → IS at CXA v2.1 baseline / 4 at OD plan v2.6 per C3-15" → "4 → IS at CXA v2.18 (post-C3-15 reconciliation)" + aggregate 107 → 105.

(b) Workspace `CLAUDE.md` §2.4 CXA row bump v2.17 → v2.18 with change-note absorption.

(c) `harness-od/CLAUDE.md` §2.2 cross-axis edge inventory row "OD → IS | 6" refresh to "4" + CXA cite v2.17 → v2.18.

(d) `harness-od/CLAUDE.md` §1.1 OD posture line "27 outbound edges per §2.4 axis-attribution" refresh to "26 outbound" + version cite bump.

(e) Workspace `CLAUDE.md` aggregate "107 canonical cross-axis relationships" → "105".

(f) **Sibling PR**: OD plan v2.27 authoring NEW §4.6 "OD-internal cross-cluster dependency" section per halt-doc Item 12 + operator AskUserQuestion 2026-05-31 Option (B). Closes halt-doc Item 12.

### §0.10 Clearance marker

Per workspace `CLAUDE.md` §4.5: clearance marker filed at `.harness/clearance/Cross_Axis_Composition_Document-v2_18-cleared-2026-05-31.md`.

---

## §1 — Cross-arc note (halt-doc Item 11 closure)

This v2.18 amendment is the design-phase posture session arc closing halt-doc Item 11 (CXA-OD-IS-EDGE-DRIFT) per the operator-ratified routing at halt-doc §"Routing target: Design-phase session — open council deliberation, ratify direction, apply via spec-writer skill, file clearance marker, PR." Council deliberation was discriminated-out at probe per PR #94 amendment 1 (nameable-tension discriminator — no real voice-tension; C3-15 ratification already operator-decided). Direction ratified via single operator AskUserQuestion. Apply pass authored at this PR. Clearance marker at §0.10.

Sibling PR for halt-doc Item 12 (OD-INTERNAL-FORMALIZATION) is the OD plan v2.27 carve-out + C3-15 examples per operator AskUserQuestion 2026-05-31 Option (B). Authored at separate PR per `[[advisor-44th-application-dont-bundle-distinct-structural-shapes]]` discipline (refresh-vs-new-authoring shape distinction).

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Cross_Axis_Composition_Document_v2_18.md` |
| Filing event | Narrow-scope absorption of long-carried CXA-OD-IS-EDGE-DRIFT halt-doc Item 11 (closure of OD plan v2.4 §6 Filing-footer adjacent finding from Session 3 close). §2.3.4 6 → 4 rows per operator-ratified C3-15 Path (i-refined) at OD plan v2.4 §0.4.2; §2.1 aggregate 107 → 105; §2.4 OD outbound 28 → 26. Direction ratified via operator AskUserQuestion 2026-05-31 Option (A) CXA-conforms-to-plan. 2026-05-31 |
| Authored at | Design-phase posture session 2026-05-31 (operator-declared per workspace CLAUDE.md §11.3) |
| Authoring authority | Operator AskUserQuestion 2026-05-31 ratification of probe finding (PR #94 amendment 5 probe-first discipline) + sibling-PR convention per `[[advisor-44th-application-dont-bundle-distinct-structural-shapes]]` |
| Predecessor | `Cross_Axis_Composition_Document_v2_17.md` (preserved verbatim except §2.1 OD→IS cell + §2.3.4 + §2.4 OD row + aggregate-total amendment sites) |
| Successor | TBD per next CXA arc |
| Sibling PR | OD plan v2.27 — halt-doc Item 12 OD-INTERNAL-FORMALIZATION |
| Clearance marker | `.harness/clearance/Cross_Axis_Composition_Document-v2_18-cleared-2026-05-31.md` |
