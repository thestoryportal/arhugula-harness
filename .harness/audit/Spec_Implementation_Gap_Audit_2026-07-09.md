# Spec-Implementation Gap Audit — 2026-07-09

**Posture:** mode-agnostic / process-substrate (reads `design-substrate/**`, `harness-*/src`, `.harness/**`; edits neither design-substrate nor production code). Same posture as the prior `Remaining_Build_Audit_Report.md` (2026-06-20).

**Against HEAD:** `937eeaef` (clean tree, no open PRs).

**Question posed (checkpoint `20260709-171049`):** conduct a comprehensive spec-implementation gap audit to prove no design/spec feature GAPS remain between the canonical design corpus and the current implementation, or enumerate the ones that do — the way the memory-substrate layer (`C-MEM-*`) was missed by "roadmap complete" and only built afterward.

**Gap definition (scope boundary, deliberate):** a gap = **designed-but-unbuilt** (presence) — a capability committed in the authority chain (ADR / ADD / PRD / spec / plan) with no landed, reachable code. This audit does **not** hunt correctness bugs in built features (that is a different audit). The canonical signature hunted: *a committed capability in ADR/ADD/PRD with no downstream spec contract family, hence no code* (the memory-gap analog).

---

## 1. Method

Two decorrelated layers, plus a re-ground against the live trackers:

1. **Layer 1 — overlay orphan buckets (bottom-up).** `just overlay-query --orphans` deterministically maps spec-contract ↔ code ↔ CXA-seam ↔ substitution. Its `contract_without_code` / `unit_without_code` buckets are exactly the gap classes; each candidate body-read against **both** spec and code (a `contract_without_code` can be a real gap, code-that-exists-but-is-uncited, or an obsolete/definitional prose row — the overlay is advisory, per `overlay.py:474-478`).
2. **Layer 2 — authority-chain→spec coverage (top-down).** The overlay only sees requirements that carry a `C-*`/`U-*` token. A designed feature escapes it only if it never got a token — i.e. it lives only in ADR/ADD/PRD prose. So walk the structured requirement spine top-down: PRD `R-*` families + ADR F1–F5 / D1–D7 commitments → does a spec contract family realize it → does that family have code?
3. **Re-ground** against the live arc-ledger (`tools/arc_ledger.py --check`), forward register (`.harness/post-phase-8-forward-register.md`), and the prior 2026-06-20 audit, so "declared complete" is pressure-tested, not trusted.

This audit **extends** the 2026-06-20 `Remaining_Build_Audit_Report.md` rather than reinventing it. The prior audit's denominator (108 head `C-*` + 195 head `U-*` + 11 ADRs + CXA seams) and its 5-dimension coverage matrix (`Closure_Gate_v1.md §3`: built / activated / tested / reviewed / documented) remain valid. This audit's job is the **delta**: the two design additions that postdate 2026-06-20 and were therefore never covered — the **memory substrate** (fork filed 2026-07-01; built as U-MEM-01..25) and **external-CLI (OAuth) routing** (ported at PR #914, 2026-07-09).

---

## 2. Layer 1 — overlay orphans (bottom-up): CLEAN

`just overlay-query --orphans` at HEAD:

| Bucket | Count | Disposition |
|---|---|---|
| `cxa_seam_missing_endpoint` (HARD) | 0 | clean |
| `contract_without_code` | 2 | C-IS-11, C-MEM-01 — triaged below, **neither a feature gap** |
| `unit_without_code` | 2 | U-MEM-17, U-RT-00 — triaged below, **neither a feature gap** |
| `code_without_cite` | 2 | `automatic_memory.py`, `external_cli_provider.py` — cite-hygiene (see F-B, F-C) |
| `substitution_without_carrier` | 41 | all `SUBSTANTIVE_RETIRED` / `AUTHORING_ONLY` — retired-by-design, expected |

**Per-candidate triage (all four resolved, none a designed-but-unbuilt gap):**

| ID | What it is | Verdict |
|---|---|---|
| **C-IS-11** | Cited as "IS C-IS-11 §11.1" in the Runtime spec body (`Spec_Harness_Runtime_v1.md:3846,3850`) and CP specs, but **never defined** in the IS spec (confirmed: 0 `## C-IS-11` definitions). The Runtime spec's own change-note (`:2431`) states *"prior v1 cited C-IS-11/14/15 which don't exist."* | **Phantom contract ID.** Not a feature gap — a **live cite-hygiene defect in a cleared head** (finding **F-B**). |
| **C-MEM-01** | "Memory plane boundary" — a definitional five-axis responsibility map + two invariants ("provider-owned memory is never canonical", "derived indexes are never canonical"). | **Definitional/boundary contract.** No code carrier by design; its invariants are enforced by C-MEM-02+ (which have code). Not a gap. |
| **U-MEM-17** | "Refactor Anthropic native memory adapter onto canonical store" (contract C-MEM-15). | **Implemented** — `lifecycle/native_memory_adapter.py` (docstring = the unit's exact title; `resolve_native_memory()`/`resolve_capture()` + operation-ledger wiring = its acceptance criteria) + `lifecycle/memory_migration.py`. Cited via contract **C-MEM-15**, not the U-token. Not a gap — cite-convention artifact (the overlay's documented `overlay.py:489` case). |
| **U-RT-00** | `Spec_Harness_Runtime_v1.md:6022`: *"(this spec entirely — U-RT-00 IS the spec authoring unit)"*. | **Meta-unit**, not implementable code. Not a gap. |

**Memory-layer completeness (the exemplar gap — pressure-tested):** C-MEM-02 through C-MEM-16 all have code carriers; only the definitional C-MEM-01 does not. R-MEM-01..15 (PRD v1.2) all map to U-MEM units (plan §R-MEM traceability table). The whole-layer gap that "roadmap complete" once missed is **now built**. Reachability confirmed (cite-presence proves a file exists, not that it runs): the *automatic* memory substrate is wired into the bootstrap — `materialize_automatic_memory_runtime` is imported and invoked at `bootstrap/stage_5_loop_init.py:287` and threaded as `memory_runtime=` at `:329` (exercised by `test_automatic_memory_runtime.py`). It is not present-but-inert.

---

## 3. Layer 2 — authority-chain→spec coverage (top-down)

**PRD `R-*` requirement spine (unique IDs):** R-AS ×7, R-CP ×12, R-IS ×4, R-OD ×8 (PRD v1.1) + R-MEM ×15 (PRD v1.2) = 46.

- **R-AS / R-CP / R-IS / R-OD (original four axes):** covered by the 2026-06-20 audit (108 contracts, built+tested green) and re-confirmed by the live arc-ledger: **`frozen 11/11, standalone 69 closed / 0 gated / 4 resolved / 0 forward`**. `0 forward` = no registered-but-unbuilt arc remains. R-FS-1 (full-spec build) is genuinely RESOLVED, not just label-RESOLVED.
- **R-MEM (PRD v1.2):** realized by C-MEM-* → U-MEM-01..25, all built (§2 above).
- **ADR commitments:** F1–F5 / D1–D6 cleared and built (prior audit). **ADR-D7** (newest, 2026-07-01) commits: memory substrate (→ C-MEM, built), CLI profiles (→ C-MEM-16, built), provider adapters (→ C-MEM-13/14/15, built), and **composition with the existing external-CLI route** — for which ADR-D7 §Decision affirmatively places routing authority on the generic C-RT-02/C-RT-05 contracts (a cleared placement, examined in §3; not a gap).

**The one surface examined closely: external-CLI (OAuth) provider routing — a CLEARED PLACEMENT, not a gap.** The newest subsystem (ported at PR #914, never covered by the 2026-06-20 audit) is substantial and built: `lifecycle/external_cli_provider.py` = **766 lines**, plus `lifecycle/providers.py`, `lifecycle/llm_dispatch.py`, `cli_profile_loading.py`, `types.py`. It has **no dedicated per-axis spec contract family**:

- `Spec_Control_Plane_v1_85.md` head: **0** external-CLI/OAuth mentions.
- `Spec_Harness_Runtime_v1.md` head: **0** external-CLI/OAuth mentions; C-RT-05's body does not name external-CLI as a provider class.
- No contract references any external-CLI code symbol (`ExternalCli`, `construct_external_cli_adapter`, `prefer_oauth`, provider-kind enum).
- No PRD `R-*` family covers external-CLI routing (PRD v1.2 added only R-MEM).

At first pass this reads like the memory-gap analog (lives in ADR prose + code, skipped the contract/unit layer). **It is not**, and the discriminator is decisive: *is external-CLI routing a deferred capability, or a cleared placement?* **ADR-D7 §Decision (line 88) is an affirmative placement in a cleared foundational ADR** (D7, cleared 2026-07-09): *"Existing external CLI routing **remains the provider-construction authority**."* ADR-D7 did not defer a contract family — it **decided** routing lives under the generic runtime provider-construction contracts (C-RT-02 RuntimeConfig, amended by `class_1_fork_provider_construction_allowlist_semantic.md` for the `external_cli_providers` config fields + `*_optional` degradation; C-RT-05 provider lifecycle). No capability was deferred, so FULL-SPEC's "no defer" rule does not bite — FULL-SPEC builds missing *capabilities*, it does not manufacture documentation obligations a cleared ADR deliberately chose not to impose.

This is the **inverse** of the memory gap on the only axis this audit measures. The memory gap mattered because the capability was **unbuilt/unreachable**; external-CLI is **built, tested, running**. They share a doc-structure surface (no dedicated contracts) and are *opposite* on presence. Treating "every subsystem must have its own contract family" as a hard rule against already-built, ADR-placed, tested code would re-specify ~1k lines of working code — foreclosed by §1.2 (not a re-litigation surface for cleared decisions) and §3 (simplicity). Per `[[grounding-reveals-claude-closeable-slice-close-honestly]]` (ratified → confirm-don't-rescue; over-excavation is the tell) and `[[cleared-spec-resolves-it-before-first-principles-fix]]` (a cleared artifact often resolves the concern by a different mechanism than a first-principles fix), external-CLI routing is **confirmed, not rescued**. The only legitimate residue is that `external_cli_provider.py` carries no cite to its authority — a one-line docstring cite to ADR-D7 / C-RT-05, folded into F-C. **Not a build arc; not an operator fork.**

---

## 4. Findings

No designed-but-unbuilt gaps. Two cite-hygiene items (both Class 3 informational; neither changes behavior, neither re-opens a cleared decision):

| # | Finding | Class | Signature | Remediation |
|---|---|---|---|---|
| **F-B** | **`C-IS-11` live phantom cite in a cleared head.** `Spec_Harness_Runtime_v1.md` body (`:3846`, `:3850`) cites "IS C-IS-11 §11.1" for `WriteResult`/append semantics, while its own change-note (`:2431`) says C-IS-11 doesn't exist; also cited in CP specs. C-IS-11 is confirmed **not defined** in the IS spec (0 definitions). The co-cited **C-IS-10 §10.5** *is* real (a substrate seam export); the real write/`WriteResult` contract is **C-IS-07 §7.1** (idempotent-write contract). | 3 (informational / cite-hygiene) | forward/phantom cite in a cleared head | In the next Runtime-spec delta: **strike the phantom "+ C-IS-11 §11.1"** at `:3846`/`:3850` (C-IS-10 §10.5 already carries the seam cite; add C-IS-07 §7.1 if a write-semantics cite is wanted). Also sweep the CP specs for the same phantom. Clearance marker. Distinct from prior RB-DOC-03 (superseded-version phantoms; this is a live head). |
| **F-C** | **Two `code_without_cite` orphans** (soft; overlay drift gate GREEN — not HARD seam violations). (a) `automatic_memory.py` — real "Automatic local memory substrate wiring", wired into bootstrap (§2), 0 C-*/U-* cites. (b) `external_cli_provider.py` — 766-line routing surface, authority is ADR-D7 §Decision + C-RT-05 (the cleared placement of §3), but the file cites neither. | 3 (cite-hygiene) | code without cite | (a) add a `C-MEM-*` docstring cite (candidate C-MEM-11 retrieval / C-MEM-12 packet assembly — pick the contract the wiring realizes). (b) add a one-line docstring cite to **ADR-D7 §Decision / C-RT-05** (makes the authority chain navigable; clears the orphan without inventing a contract family). |

**Downgraded (recorded so the reasoning is auditable):** an earlier draft flagged "external-CLI routing has no dedicated contract family" as a substantive FULL-SPEC finding. That was **over-excavation** and is withdrawn: ADR-D7 §Decision (line 88) is an affirmative, cleared placement of routing under the generic provider-construction contracts, not a deferred capability (§3). The only residue is the uncited file, captured as F-C(b). Surfacing it as an operator fork would spend a scarce decision signal on a non-fork and re-open a cleared ADR — the failure mode, not diligence.

---

## 5. Pre-registered residuals (tracked, NOT missed)

These are already documented in the forward register / prior audit — enumerated here for completeness so the audit is not read as "everything is closed":

- **Gap D / R-100 AC#2** (`post-phase-8-forward-register.md:155`): the `api.run` bootstrap pings ≥1 provider regardless of step kind, so a tool-only workflow still requires a live provider. A registered **Class 1 fork candidate** with a nameable **C9⊥C11** tension (fail-fast reliability ⊥ tool-only-workflow ergonomics), operator-gated by design, dyadic-council-eligible.
- **R-CL quality/closure track** (prior register RB-GOV-01..06): R-CL-Q1..Q4 / D1 / C1 — 6 phases deliberately gated behind R-FS-1. R-FS-1 is now resolved, so these are now **openable** (R-CL-Q1 is the checkpoint's noted gated item).
- **Doc/governance residuals** (prior register RB-DOC-*, RB-EXP-01, RB-CXA-02/03): READMEs, curated `__all__` exports, cxa-vs-runtime seam-count reconciliation. Doc-hygiene, not feature gaps.
- **Bounded-residual / dormant activations** (RB-SUB-01/02, RB-ACT-01/02/03): built + proven, production-dormant until deployed. Not gaps.

---

## 6. Conclusion

**No designed-but-unbuilt gaps found. The design corpus and implementation are coherent.** The overlay-visible spec→code layer is clean (0 HARD seam orphans; all 4 contract/unit orphans are phantom/definitional/uncited-but-built). The live arc-ledger confirms R-FS-1 is genuinely resolved (`0 forward`, not merely label-RESOLVED). The memory substrate — the exemplar gap this audit was commissioned to guard against — is fully built **and reachable** (automatic-memory wired at bootstrap stage 5). The newest un-audited subsystem, external-CLI routing, is built, tested, running, and its authority is a cleared ADR-D7 placement — coherent, not a gap.

What the audit surfaces is **two cite-hygiene items**, both Class 3, neither behavior-changing:

- **F-B** — strike the phantom `C-IS-11 §11.1` cite from the Runtime spec head body (and sweep the CP specs); the real seam (C-IS-10 §10.5) is already co-cited, the real write contract is C-IS-07 §7.1.
- **F-C** — add authority docstring cites to the two `code_without_cite` files (`automatic_memory.py` → a C-MEM contract; `external_cli_provider.py` → ADR-D7 §Decision / C-RT-05).

An audit that resists inventing work is the stronger result. **No operator decision is owed** — F-B and F-C are mechanical doc-hygiene, fixable in a single design-phase pass (spec-writer posture) with a clearance marker: F-B in the next Runtime/CP spec delta; F-C as one-line docstring cites in the two runtime files. No new contracts, no re-litigation of cleared decisions.

**Scope honesty:** this audit's "no gaps" for the pre-2026-06-20 surface rests on the prior audit + the live arc-ledger (it did not re-derive all 108 contracts from scratch); it independently pressure-tested the two post-2026-06-20 additions (memory, external-CLI) and the overlay orphan set at HEAD. The gap definition is presence (designed-but-unbuilt), not correctness of built features — a correctness audit is a separate exercise.

---

*Filed 2026-07-09. Extends `.harness/audit/Remaining_Build_Audit_Report.md` (2026-06-20). Instruments: `just overlay-query --orphans`, `tools/arc_ledger.py --check`, cross-spec `rg`. Coverage-matrix template: `Closure_Gate_v1.md §3` (5 dimensions).*
