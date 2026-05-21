# Class 3 Tension — CXA v2.4 introduces first axis-level back-edge (IS<AS<CP<OD partial-order no longer total)

**Class:** 3 — informational; non-blocking; documented.
**Filed:** 2026-05-20 at CXA v2.4 landing (`ee5ae21`).
**Status:** OPEN-FLAGGED — surfaced for operator visibility; absorbed at next CP/OD plan revision change-notes.

---

## Finding

Per `Cross_Axis_Composition_Document_v2_4.md` §0.4 + §2.2: the U-CP-28 → U-OD-00 edge added at v2.4 (per U-RT-59 Fork 2 Path D landing) is **the first cross-axis edge in the project's history that runs against the prior axis-level partial-order invariant** (IS < AS < CP < OD).

Pre-v2.4 CXA documents (v1 through v2.3) treated IS < AS < CP < OD as a **total partial-order** at axis granularity:
- IS: 0 outbound (pure substrate)
- AS: outbound only to IS
- CP: outbound only to IS + AS
- OD: outbound only to IS + AS + CP

CXA v2.3 §2.4 posture summary recorded "OD outbound (downstream): 0 — OD terminates the axis-level dependency graph"; CXA v2.3 §2.2 declared "Axis-level acyclicity (IS < AS < CP < OD) holds."

CXA v2.4's new CP → OD edge introduces a **back-direction dependency at axis granularity** — CP now consumes OD (via the typed seam at the converter contract). Per-unit acyclicity within CP and within OD is unaffected (the new edge is U-CP-28 → U-OD-00; U-CP-28 is a CP cluster-5 unit; U-OD-00 is an OD pre-cluster L0 carrier; the edge is unidirectional and adds no per-unit cycle). Per-axis Kahn ordering within each axis is preserved.

## Why it matters

The IS < AS < CP < OD axis-level partial-order has been treated as a **load-bearing architectural invariant** in three places:

| Site | What it commits |
|---|---|
| `harness-od/CLAUDE.md` §2.2 | "OD outbound (downstream): 0 — OD terminates the axis-level dependency graph" |
| `harness-cp/CLAUDE.md` §2.3 | "CP → OD (outbound) \| 0 \| OD pulls from CP via U-CP-54 + U-CP-55 manifest" |
| `Cross_Axis_Composition_Document_v2_3.md` §2.2 | "Axis-level acyclicity (IS < AS < CP < OD) holds" |

CXA v2.4 §2.2 amends the third site explicitly. The first two are **owed amendments** at the next CP/OD plan revision change-notes (Form A citation-precision deltas — no decomposition change, just outbound-count update + back-edge acknowledgement).

## Why the back-edge is justified

Per `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` §10 (Path D ratification): the alternative homes for the `cp_audit_to_od_audit` converter — `harness-od/` (foreclosed by OD's 0-outbound-edges invariant) and `harness-cp/` (would create a new CP→OD outbound at the package-import level, which is what this Class 3 documents) — both impose costs. The operator's Q5 ratification homed the converter at `harness-cxa/` precisely to avoid forcing the back-edge into either consumer-axis package's outbound profile.

**The contract-level back-edge still exists** at v1.7 §13.5.1 (the CP-side contract references OD `AuditLedgerEntry` as the converter output type). This is what CXA v2.4 §2.3.7 enumerates: the typed-seam edge classification reflects the contract-level dependency, regardless of where the physical import lives. The `harness-cxa/` home keeps the package-import surface of `harness-cp/` and `harness-od/` clean; the CXA enumeration honestly records the contract-level back-edge.

## Routing per `Project_Workflow_v1_8.md` §2.7.6

**Class 3 (informational).** Non-blocking; documented. No design extension (X-AL-3 holds — the back-edge follows from the Fork 2 Path D ratification, not from authoring-time invention).

**Owed amendments at next plan revisions (Form A — citation precision only):**

| Plan | Site | Amendment |
|---|---|---|
| `harness-cp/CLAUDE.md` | §2.3 "Cross-axis edge inventory" table | Add row: CP → OD (outbound) \| 1 \| `Cross_Axis_Composition_Document_v2_4.md` §2.3.7 (genuine-typed-seam; import at `harness-cxa/`). Strike the existing "CP → OD (outbound) \| 0 \|" row. |
| `harness-od/CLAUDE.md` | §2.2 "Cross-axis edge inventory" + axis posture | Acknowledge the new CP→OD inbound at U-OD-00. The "0 outbound (downstream)" invariant is unaffected — OD still has 0 outbound; the new edge is OD-INBOUND from CP. |
| Workspace `CLAUDE.md` | §2.1.4 (CXA "92 canonical cross-axis relationships ... 22 genuine typed seams") | Update to "93 canonical cross-axis relationships ... 23 genuine typed seams" + cite CXA v2.4. |
| Workspace `CLAUDE.md` | §2.4 CP-plan v2.10 → v2.14 pointer + OD-plan v2.11 → v2.12 pointer | Owed when CP plan + OD plan absorb the §13.5.1 contract reference. |

These amendments are NOT in Path D scope (Path D = CXA v2.4 + CP spec v1.7 §13.5.1 only); they are owed downstream absorption work at the next CP plan / OD plan / workspace CLAUDE.md revision passes per `[[design-substrate-divergence]]` in-CLI discipline.

## Filing footer

| Field | Value |
|---|---|
| Filed at | CXA v2.4 landing commit `ee5ae21` (2026-05-20) |
| Filed by | spec-writer arc — U-RT-59 Fork 2 Path D landing closure |
| Class | 3 (informational) |
| Surface | Cross-axis architectural-invariant shift |
| Related | `[[u_rt_59_fork_2_cp_to_od_audit_discovery]]` §10 Path D routing + §0.3 precedent note; `Cross_Axis_Composition_Document_v2_4.md` §0.4 + §2.2 |
| Re-entry trigger | Next CP plan revision pass + next OD plan revision pass + next workspace `CLAUDE.md` revision pass — Form A citation-precision deltas absorbing the back-edge |
| Resolution | Will close when all three pointer-amendment sites absorb the back-edge acknowledgement |

---

*This Class 3 record exists so the back-edge is operator-visible at filing, not discovered later as a surprise in CXA v2.4 fine print. The architectural shift is real but follows necessarily from Fork 2 Path D ratification; the alternative homes for the converter both imposed worse costs.*
