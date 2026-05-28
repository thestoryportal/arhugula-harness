# Class 1 Tension — U-OD-29 `SandboxTier`: 0-indexed in-unit enum vs AS-owned cross-axis enum (FF-3)

**Status:** ✅ CLOSED-via-OD-plan-v2.10 (resolved 2026-05-16; verified workspace-wide audit 2026-05-20; status-line refreshed 2026-05-27) — in-unit `SandboxTier` struck; AS enum imported. Species 3 stale-carry per workflow v1.9 §7.4.7.2.

| Field | Value |
|---|---|
| Unit | U-OD-29 — Verify per-sandbox-tier OTLP reachability + F4 capability-floor composition |
| Sub-phase | 7b — OD axis-stream (Level 7) |
| Fork class | Class 1 (halt-execution — plan-internal contradiction; plan-vs-AS-axis divergence) |
| Filed | 2026-05-16 (surfaced at OD-7b final-batch sequencing; this is the **FF-3 carried fork** — `Implementation_Plan_Operational_Discipline_v2_5.md` §0.6 FF-3, "open; ADR-D2 §1.2 verification required", unresolved through v2.9) |
| Actor | phase-7-implementation (OD-7b — pre-dispatch check) |
| Disposition | **✅ RESOLVED 2026-05-16** — operator ratified "resolve now"; plan v2.10 filed (U-OD-29 §3.7.3 conformed: in-unit `SandboxTier` struck, consumed from the AS-owned enum, reachability re-keyed to OD spec §20.3). U-OD-29 lands against v2.10 → OD-7b 35/35. |

## Defect

U-OD-29 (`Implementation_Plan_Operational_Discipline_v2_1.md` §3.7.3, preserved verbatim through v2.9) declares **in-unit**:

```
enum SandboxTier { TIER_0, TIER_1, TIER_2, TIER_3 }   // per D2 v1.1 §1.2
```

acc #1: *"`SandboxTier` enumerates exactly 4 values per D2 v1.1 §1.2."* The `Inputs` field reads "sandbox tiers 0–3" throughout. This is **0-indexed**, 4-value.

Three problems:

1. **vs the AS-axis-owned, landed `SandboxTier`.** The AS axis owns `SandboxTier` and landed it (AS axis-stream complete, 33/33) at `harness-as/src/harness_as/sandbox_tier.py` as `TIER_1_PROCESS / TIER_2_CONTAINER / TIER_3_MICROVM / TIER_4_FULL_VM` — **1-indexed**. The plan's `TIER_0..TIER_3` diverges from the canonical enum.

2. **vs the v2.6 R5 materializability audit.** `Implementation_Plan_Operational_Discipline_v2_6.md` (R5 audit table) classifies `SandboxTier` for U-OD-29 as **"AS axis (cross-axis AS edge — clean); AS-owned enum; declared cross-axis AS edge"** — i.e. U-OD-29 must **not** declare `SandboxTier` in-unit; it consumes the AS-owned enum across the axis boundary. The v2.1 body's in-unit `enum SandboxTier` declaration **contradicts the R5 audit's own classification**. The plan is internally inconsistent: the v2.1 unit body declares the enum; the v2.6 audit reclassified it as a cross-axis import and did not strike the v2.1 declaration.

3. **vs OD spec §20.3 + the citation.** OD spec C-OD-20 §20.3 ("Per-sandbox-tier OTLP reachability") keys its reachability table on **1-indexed** tiers — `Tier-1 process / Tier-2 container / Tier-3 microVM / Tier-4 full-VM` (matching ADR-F4's "four-tier sandbox-isolation tier-set — process / container / microVM / full-VM"). The plan's acc #1 cites "D2 v1.1 §1.2"; per the ADR-D2 section index, §1.2 is the **sandbox provider-class enumeration**, not the tier set — the citation target is wrong (the tier set is ADR-F4's, transcribed at C-AS-01 §1.1).

The `OtlpReachabilityClass` 4-class scheme (`TRIVIAL_IN_PROCESS` tier-0 / `UNIX_DOMAIN_SOCKET_OR_LOOPBACK_TCP` tier-1 / `SANDBOX_PERMITTED_EGRESS_LOOPBACK` tier-2 / `SANDBOX_PERMITTED_EGRESS_PRIVATE_NET_ONLY` tier-3) was designed against the 0-indexed scheme, which had a `tier-0` = "in-process, no sandbox". The 1-indexed AS canonical enum has **no such tier** — `TIER_1_PROCESS` is already process-isolation. So the reachability semantics do not re-key 1:1 onto the AS tiers; they need re-derivation against OD spec §20.3's actual table.

## Why this is FF-3, not a new discovery

`Implementation_Plan_Operational_Discipline_v2_5.md` §0.6 records **FF-3** verbatim: U-OD-29's `SandboxTier` `TIER_0..TIER_3` "per D2 v1.1 §1.2" — "the divergence target is an ADR (ADR-D2 §1.2), not a spec-§ verbatim claim … the operator (or a follow-on pass) must verify ADR-D2 §1.2 directly … U-OD-29 is not revised at v2.5." v2.6/v2.7/v2.8/v2.9 each revised an explicit unit list; U-OD-29 is in none. FF-3 has been carried unresolved to execution-time. The OD-7b worklist treated U-OD-29 as cascade-blocked-by-U-OD-28-only — it missed FF-3 as an independent fork (the same miss pattern as FF-2 / U-OD-28).

ADR-D2 §1.2 verification (the FF-3 action): ADR-D2 §1.2 is the *sandbox provider-class enumeration*; the *tier set* is ADR-F4 v1.1's "four-tier sandbox-isolation tier-set (process / container / microVM / full-VM)" — 4 tiers, named not numbered. The AS axis operationalized it 1-indexed (`TIER_1_PROCESS..TIER_4_FULL_VM`). The plan's 0-indexed `TIER_0..3` is ADR-unsanctioned.

## Resolution

**HALT U-OD-29. Not landed. Skipped from the OD-7b final batch.** U-OD-29 is a leaf — no OD unit depends on it (U-OD-31 deps `[U-OD-13,14,15,16,22,24,25,30]`; U-OD-34 deps do not include U-OD-29). OD-7b lands **34/35**; U-OD-29 alone remains.

## Recommended resolution

The fix **direction** is determinate (conform to the senior artifacts — the AS-owned `SandboxTier` enum + OD spec §20.3); the one genuine question is the **7b/7c boundary**:

- The v2.1 body declares `SandboxTier` in-unit; the v2.6 audit reclassified it as a **cross-axis AS import**. Cross-axis edges resolve at sub-phase **7c**, not 7b (`phase-7-implementation` SKILL.md §5 — cross-axis substrate is read-only via the terminal exporter manifest at 7c). If `SandboxTier` is a genuine cross-axis AS import, U-OD-29's reachability-verification surface is **partly a 7c concern** — U-OD-29 cannot import the AS enum at 7b.

Two resolution shapes for operator decision:

- **Option A — plan micro-revision (v2.10) + land at 7b.** Revise U-OD-29: strike the in-unit `enum SandboxTier`; declare `SandboxTier` as a cross-axis AS dependency (consumed from the AS-landed `harness_as.sandbox_tier.SandboxTier`, `TIER_1_PROCESS..TIER_4_FULL_VM`); re-author `OtlpReachabilityClass` + `PER_SANDBOX_TIER_REACHABILITY` + acc against OD spec §20.3's 1-indexed reachability table; fix the acc #1 citation (ADR-F4 four-tier set / C-AS-01 §1.1, not ADR-D2 §1.2). If the AS enum is treated as a `harness-core`-style shared import (as U-OD-22 treated `WorkloadClass`), U-OD-29 lands at 7b. `implementation-planner` revision pass; determinate conform — operator ratifies.
- **Option B — defer U-OD-29 to 7c.** If `SandboxTier` is a strict cross-axis edge (resolved only via the AS terminal exporter manifest at 7c), U-OD-29's reachability verification lands at 7c alongside the cross-axis composition. OD-7b closes at 34/35 by design; U-OD-29 is a 7c unit.

Option A is recommended if the AS `SandboxTier` enum is importable now (the AS axis is complete and its modules are in the `uv` workspace — `harness-od` units have already imported `harness-core` types cross-package this session). Until the operator decides, U-OD-29 stays unlanded.

---

## ✅ RESOLVED — plan v2.10 (2026-05-16)

Operator ratified FF-3 "resolve now". `design-substrate/Implementation_Plan_Operational_Discipline_v2_10.md` §3.7.3: in-unit `enum SandboxTier {TIER_0..3}` struck; `SandboxTier` consumed cross-axis from the AS-owned enum (`TIER_1_PROCESS..TIER_4_FULL_VM`); `OtlpReachabilityClass` + per-tier reachability map re-keyed to OD spec C-OD-20 §20.3's 1-indexed tiers; acc #1 citation corrected (ADR-F4 four-tier set / C-AS-01 §1.1, not D2 §1.2). U-OD-29 lands against v2.10 at 7b — OD-7b closes 35/35.

---

## Audit reconciliation (2026-05-20)

**Verified status:** RESOLVED

**Resolving artifact / evidence:** Already labeled RESOLVED 2026-05-16 (OD plan v2.10 — in-unit SandboxTier struck; AS enum imported). Audit confirms.

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
