# Class 1 Tension — U-OD-28 collector-placement enum: three-way plan/§1.2/§20.1 mismatch (FF-2)

| Field | Value |
|---|---|
| Unit | U-OD-28 — Declare per-cell OTLP collector placement matrix + BatchSpanProcessor universality |
| Sub-phase | 7b — OD axis-stream (Level 6) |
| Fork class | Class 1 (halt-execution — plan signature un-materializable; acceptance criterion cites a non-existent verbatim surface; plan-vs-spec divergence) |
| Filed | 2026-05-16 (surfaced at OD-7b batch-2 execution; this is the **FF-2 carried fork** — `Implementation_Plan_Operational_Discipline_v2_5.md` §0.6 FF-2, unresolved at v2.6/v2.7/v2.8) |
| Actor | phase-7-implementation (OD-7b batch 2) |
| Disposition | **OPEN** — U-OD-28 halted, not landed. Skipped; batch-2 landed the other 4 units. Transitively blocks U-OD-29, U-OD-30, U-OD-31, U-OD-34 (terminal exporter). |

## Defect

U-OD-28 (`Implementation_Plan_Operational_Discipline_v2_1.md` §3.7.2, never revised through v2.8) declares:

```
enum CollectorPlacement {            // 7 members
  IN_PROCESS_LOOPBACK                          // cell-1
  EXTERNAL_OTLP_LOCALHOST                      // cell-2
  EXTERNAL_OTLP_VENDOR_INGESTION               // cell-3
  EXTERNAL_OTLP_TEAM_SELF_HOSTED_ENDPOINT      // cells 4, 5
  EXTERNAL_OTLP_TEAM_MANAGED_CLOUD             // cell-6
  EXTERNAL_PER_TENANT_OTLP_SELF_HOSTED         // cell-7
  EXTERNAL_PER_TENANT_OTLP_MANAGED_CLOUD       // cell-8
}
```

acc #1: *"`CollectorPlacement` enumerates exactly **7** values per §20.1 verbatim."*

This is a **three-way mismatch**:

1. **vs spec §20.1.** C-OD-20 §20.1 is an **8-row prose per-cell placement matrix** — `| Cell | Collector placement | Backing |`. The "Collector placement" cells are prose descriptions with alt-route disjunctions (cell-2 "in-process permitted as alt-route; cell-committed backend's collector preferred"; cell-4 "in-process + sqlite OR Langfuse self-hosted single-node OTLP"; cell-5 "Sidecar OR collector-as-DaemonSet ... collector-as-sidecar at non-K8s"). **§20.1 declares no enum.** acc #1's "7 values per §20.1 verbatim" cites a surface that does not exist — un-materializable as written (same defect shape as U-OD-08 D-2).

2. **vs spec §1.2.** C-OD-01 §1.2's per-cell entry schema commits the collector-placement field as `enum ∈ {in-process, sidecar, vendor-pipeline, sidecar with per-tenant routing, per-tenant collector instance, vendor-managed collector}` — a **6-value architectural-class** enum, sourced "C-OD-20 + ADR-F4 v1.1 §Consequences (b)(iv)". The plan's 7-value enum is keyed on a *deployment-topology* taxonomy (loopback / localhost / vendor-ingestion / team-endpoint / managed-cloud / per-tenant) — it transcribes **neither** §1.2's 6 values nor their vocabulary. The plan enum is a plan-introduced taxonomy with no spec basis (X-AL-3 — no silent H_T design extension).

3. **Spec-internal gap.** Even §1.2's 6-value enum does not cleanly cover §20.1's prose. §20.1 cell-2 and cell-4 commit a non-in-process placement of "the cell-committed single-node backend's own collector endpoint" (Langfuse self-hosted OTLP endpoint, etc.) — this is **not** one of the 6 §1.2 values (`in-process` / `sidecar` / `vendor-pipeline` / `sidecar+per-tenant-routing` / `per-tenant-collector-instance` / `vendor-managed-collector`). §20.1's "collector-as-DaemonSet" (cell-5) is arguably a deployment-form within the `sidecar` architectural class, but the cell-2/cell-4 "backend's own collector" case has no §1.2 home. The spec is **not internally clean** at this surface: §1.2 declares a 6-value enum and sources it to C-OD-20, but C-OD-20 §20.1's prose does not decompose into those 6 values.

## Why this is FF-2, not a new discovery

`Implementation_Plan_Operational_Discipline_v2_5.md` §0.6 records **FF-2** verbatim: U-OD-28's "verbatim" divergence was caught by the §4A verbatim audit, but — unlike the 9 determinately-conformed units — its **conformance target was undetermined**; v2.5 did not conform it and "did not guess the target". v2.6, v2.7, v2.8 each revised an explicit unit list; U-OD-28 is in none. FF-2 has been carried unresolved to execution-time. The OD-7b worklist's 5-defect table and deferred-cluster enumeration treated U-OD-28 as *cascade-blocked by U-OD-02 only* — it missed that U-OD-28 carries its own independent FF-2 Class 1 fork. Landing the v2.1 7-value enum + the "verbatim per §20.1" AC would be silent absorption of a known design-phase defect against an invalid contract (`CLAUDE.md` §4.3 worst failure mode).

## Resolution

**HALT U-OD-28. Not landed. Skipped — OD-7b batch 2 landed U-OD-03/10/22/32.**

### Downstream impact

U-OD-28's dependents: U-OD-29 (`Depends on: [U-OD-28, …]`), U-OD-30 (`[U-OD-01, U-OD-02, U-OD-28, …]`), U-OD-31 (`[…, U-OD-30]` — transitive), U-OD-34 (terminal aggregate exporter — `[…, U-OD-28, U-OD-30, …]`). **OD-7b cannot fully close** — the terminal exporter U-OD-34 is blocked until FF-2 resolves. OD-7b lands at **29/35**; the remaining 5 (U-OD-28/29/30/31/34) are all FF-2-blocked.

## Recommended resolution (operator decision required)

This is a genuine spec-internal defect, not a determinate plan conformance. It needs a spec fix before the plan can be revised. Three paths:

- **Option A — spec fix at §20.1 + plan conform (recommended).** Give C-OD-20 §20.1 an explicit `CollectorPlacement` enum declaration conformed to the §1.2 vocabulary, resolving the cell-2/cell-4 "backend's own collector" gap (either by adding a `self_hosted_backend_collector` value — §1.2 grows 6 → 7 — or by ruling cell-2/cell-4's non-in-process route folds into an existing class). Then revise plan U-OD-28: `CollectorPlacement` conformed to the §20.1/§1.2 enum; the per-cell map becomes `Map<CellID, Set<CollectorPlacement>>` for the alt-route cells 2/4/5 (the U-OD-02 D-1 set-valued pattern); acc #1 → "N values per §1.2/§20.1 verbatim". `spec-writer` + `implementation-planner` revision passes; operator ratifies the cell-2/cell-4 gap call.
- **Option B — spec revision adopting the plan's taxonomy.** If the operator judges the plan's 7-value deployment-topology taxonomy canonical, re-specify §1.2 + §20.1 (and possibly ADR-F4 §Consequences (b)(iv)) to that taxonomy. Higher cost — touches §1.2, §20.1, and an ADR.
- **Option C — re-scope acc #1 only.** Strike acc #1's "verbatim per §20.1" claim; keep the plan's 7-value enum as a plan-layer operationalization. **Not recommended** — it leaves the plan enum diverging from §1.2's committed 6-value enum, an unresolved X-AL-3 plan-vs-spec conflict.

Option A is the faithful resolution: §1.2 is the senior surface (it commits the enum); §20.1 needs the enum declaration §1.2 already references; the cell-2/cell-4 gap is the one genuine design call. Until the operator decides, U-OD-28 and its 4 dependents stay unlanded.
