# Adversarial Review — Spec_Control_Plane_v1.32 (R-FS-1 arc #3 / B1-spec-1)

## Summary

- **Mode:** Phase-7 pre-implementation / design-substrate-amendment pre-merge gate review (per skill Standing Posture A).
- **Artifact reviewed:** `design-substrate/Spec_Control_Plane_v1_32.md` (NEW delta — C-CP-25 WorkflowDriver in-place extension §25.10–§25.18). Companions read: 3 fork docs + council DELIVERABLE + the §25-collision fork + `harness-cp/CLAUDE.md` diff + B1 design (arc #2) + scoping (arc #1).
- **Date:** 2026-06-13.
- **Reviewer:** harness-adversarial-reviewer (genuine dedicated-agent invocation).

### Severity scale used (disambiguated per SKILL.md line 14)

This report uses the **§4.1 review-severity** scale, but to avoid the §4.1↔§2.7.6 inversion hazard (where the two taxonomies swap Class 1 and Class 3), **every finding below is labelled in plain words**, not bare "Class N":

- **BLOCKS-MERGE** = a defect that must be resolved before merge (§4.1 Class 3 severe / phase-reopening, OR a §2.7.6 Class-1 halt).
- **FIX-IN-ARC** = a substantive defect resolvable inside this arc before merge (§4.1 Class 2 / §2.7.6 Class 2 — same in both scales).
- **INFORMATIONAL** = minor / non-blocking documentation nit (§4.1 Class 1 drift / §2.7.6 Class 3 informational).

### Verdict

**CLEAR — merge-eligible, with 2 INFORMATIONAL nits.** No BLOCKS-MERGE finding. No FIX-IN-ARC finding. The spec is a faithful, byte-grounded absorption of the cleared B1 design (arc #2) and the three resolved forks; its cite discipline is unusually strong (every load-bearing cite verified byte-exact at HEAD, including the ones the task prompt flagged as highest-risk).

- Finding count by severity: **BLOCKS-MERGE: 0 · FIX-IN-ARC: 0 · INFORMATIONAL: 2.**
- Highest-severity finding: F-INFO-01 (clearance-marker footer claims an artifact that cannot exist pre-merge).
- Disposition recommendation: **Clearance with the 2 informational nits filed/softened at merge.**

---

## BLOCKS-MERGE findings (severe — would halt merge)

**None.**

---

## FIX-IN-ARC findings (moderate — in-arc revision before merge)

**None.**

The two candidate findings I pursued hardest (the §25.14 role-discard cite, and the C10 fork's no-compensation completeness argument) both survived grounding as clean. See "Findings considered and rejected" F-REJ-04 and F-REJ-05 — these were the strongest real candidates and are recorded there rather than manufactured into the body.

---

## INFORMATIONAL findings (minor — non-blocking)

### F-INFO-01 — §-filing-footer claims a clearance marker that cannot exist pre-merge
- **Location:** `Spec_Control_Plane_v1_32.md:208` (Co-published row): *"…+ clearance marker `.harness/clearance/Spec_Control_Plane-v1_32-cleared-2026-06-13.md` + …"*
- **Defect:** The named marker is **absent** at HEAD (verified: `ls .harness/clearance/` — latest is `Spec_Control_Plane-v1_31-cleared-2026-06-11.md`). Per `.harness/clearance/README.md` convention (CLAUDE.md §4.5), a clearance marker's frontmatter pins the **merge commit + reviewer chain** — so by construction it cannot be authored pre-merge. The footer's "co-published" phrasing forward-describes an artifact that the merge step (not this pre-merge state) produces.
- **Discriminator:** (a) misses — it does not affect the spec's substantive contract content; it is a footer-accuracy nit. → INFORMATIONAL (§4.1 Class 1 drift).
- **Evidence:** footer line 208 vs `ls .harness/clearance/` output (no `v1_32` entry).
- **Resolution path (shape only):** either file the marker as part of the merge step (the convention's intent), or soften the footer wording to future-tense ("clearance marker filed at merge"). Not a blocker — this is the normal pre-merge state of a delta that footnotes its own merge artifacts.
- **Decision-vocab:** *decided.*

### F-INFO-02 — §25.14 cites `llm_dispatch.py` bare; the file lives under `harness-runtime/`, not the CP package the surrounding prose implies
- **Location:** `Spec_Control_Plane_v1_32.md:97` (§25.14): *"`AgentRole` is discarded at dispatch today (`llm_dispatch.py`; per the PR #509 record + §29 adjacent-observation (b))."*
- **Defect:** The bare `llm_dispatch.py` resolves to `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py` (verified to exist) — it is **not** in `harness-cp/`. A reader who assumes the CP package (the spec's home axis) would mis-locate it. The underlying claim is **correct and grounded** (verified: `_MVP_DEFAULT_AGENT_ROLE = AgentRole("default")` at line 281; the discriminator-fields-"DISCARDED at this boundary" comment block ~484–489; corroborated independently by CP spec v1.31 §29 change-note "the runtime LLM dispatch keys routing on `_MVP_DEFAULT_AGENT_ROLE` and discards the role discriminator… `grep 'per_role_bindings['` → empty"). The cite is bare-but-resolvable, not a phantom.
- **Discriminator:** (a) misses — the claim is true and resolves; only the path qualifier is implicit. → INFORMATIONAL (§4.1 Class 1 drift).
- **Evidence:** `find harness-cp harness-runtime -name "llm_dispatch*.py"` → only `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py`; line 281 + comment ~484–489.
- **Resolution path (shape only):** add the package-qualified path (`harness-runtime/.../lifecycle/llm_dispatch.py`) at the B1-spec-2 / B1-impl absorption, where the seam is materialized. Note: the cleared B1 design (arc #2 §4) pins it more precisely as `llm_dispatch.py:489`; v1.32 correctly did NOT carry the `:489` line number forward (line 489 is the `agent_role=_MVP_DEFAULT_AGENT_ROLE` envelope line, not the discard-comment line, so dropping it avoids a brittle line-cite) — so v1.32 is actually *more* cite-careful than its own cleared input here.
- **Decision-vocab:** *decided.*

---

## Mandatory-check results (the workspace's biggest defect classes)

### Check 1 — Byte-exact cite verification (CLAUDE.md §10.4 / I-1). PASS.

Every load-bearing cite verified by reading the source at HEAD (not trusting the spec's word):

| Cite in v1.32 | Source verified | Result |
|---|---|---|
| §25.1 deferral "Extension contract (C-CP-25.b or C-CP-26) authored when the first multi-worker workflow unit demands materialization" | `Spec_Control_Plane_v1_6.md:207` | **byte-exact** ✓ |
| §25 header = "C-CP-25 — Workflow execution driver" (identity) | `Spec_Control_Plane_v1_6.md:185` | byte-exact ✓ |
| §25.4 Drain protocol "NO mid-step interruption" | `v1_6.md:355` (§25.4 header) + line 43 (4-site pattern incl. "NO mid-step interruption") | ✓ |
| §25.9 = additive-subsection precedent ("the same in-place-extension shape v1.5 used to add §25.9") | `v1_6.md:414` (§25.9 header) + `v1_5.md` change-note "v1.5 amendment is purely additive at §25.9" | ✓ — precedent is real |
| `RunStatus.PARTIAL` "reserved for future multi-step error modes" (§25.2) | `v1_6.md:238` enum body | **byte-exact** ✓ |
| `_IN_SCOPE_TOPOLOGY = frozenset({SINGLE_THREADED_LINEAR})` at `workflow_driver.py:83` | code line 83 (consumed at 711) | **byte-exact line** ✓ |
| `CascadePolicy` `topology_pattern.py:55-67` domain `"pause"\|"proceed"\|"cascade-cancel"` | code: `class CascadePolicy` @55, values @65–67 | **byte-exact** ✓ |
| C-CP-10 §10.1 / §10.2 / §10.3 (topology taxonomy / cascade_policy field / admissibility) | `v1_2.md:834 / 847+857 / 865` | ✓ all 3 subsection headers resolve |
| C-CP-12 §12.2 sub-agent gate-level descent | `v1_2.md:1004` (§12.2 "Sub-agent gate-level composition formula") | ✓ |
| C-CP-19 §19.1 multiplicative `max()` gate-level | `v1_2.md:1618` (§19.1) + formula `max()` @1009–1012 | ✓ |
| C-CP-16 4-response palette | `v1_2.md:1398` (§16) + closed `approve/edit/reject/respond` @141 | ✓ |
| C-AS-02 `sandbox_tier_floor` + ADR-F4 four-tier | AS spec v1.2 §line 134 (5-arg signature) + `ADR-F4.md:1` ("four-tier sandbox tier-set with `max()`-composed…") | ✓ |
| ADR-F2 §Decision six-field `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` | `ADR-F2.md:28` | ✓ |
| ADR-F2 §Consequences "single-threaded-write boundary" (D1 prescribed resolution) | `ADR-F2.md:55` | **byte-exact** ✓ |
| `procedural_tier_snapshot_ref` D-derivative sidecar precedent | IS spec C-IS-05 §5.1 (v1.3 change-note) | ✓ — exact template the Route-Y sidecar mirrors |
| C-IS-07 §7.5 "`idempotency_key` is the sole persisted entry-level dedup discriminator" | IS spec v1.4 §7.5 (line 23/74) | **byte-exact** ✓ — load-bearing for §25.16 |
| `EntryPayload` `extra="forbid"` (branch causality can't ride existing fields) | `state_ledger_write.py:71,86` | ✓ |
| `_CP_TO_RT_STATUS` (PARTIAL not yet projected; PAUSED→'paused' precedent) | `harness-runtime/.../api.py:862-868` | ✓ — PARTIAL absent → deferral correct |
| C-RT-35 `api.resume` | runtime spec §30 (resolves in-context; see F-REJ-03 re double-use) | ✓ |

**No phantom cite. No mis-numbered cite.** The one bare cite (F-INFO-02) resolves; it is imprecise, not phantom.

### Check 2 — Phantom-cite check on the Route-Y forward-reference (§25.13). PASS.

§25.13 is **explicitly and repeatedly marked as a FORWARD-COORDINATION REFERENCE** (header line 87: "FORWARD-COORDINATION REFERENCE"; blockquote line 91: "FORWARD-COORDINATION REFERENCE (not a byte-resolvable cite)… Its IS section number is assigned at B1-spec-1b; this §25.13 names the seam and the field shape the CP driver composes, not a resolved IS section"). It does **NOT** read as a resolvable cite to a non-existent IS section — it names the producer/consumer roles and the field shape `{parent_action_id, branch_index, terminal_status}` without pinning an IS `§5.x`. This is the correct treatment; not a Class-2 finding. The forward-phantom grep (`grep §25.10-18` across sibling plans/CXA) returned **empty** — nothing forward-references the new subsections either.

### Check 3 — §25/§28 identity-correction soundness. PASS (correction is correct + history-preserving).

- v1.32's claim that §25/C-CP-25 = WorkflowDriver and §28/C-CP-28 = ValidatorFramework is verified against: the §25 body header (`v1_6.md:185` "Workflow execution driver"); the §25-collision fork (`.harness/class_1_fork_cp_spec_section_25_contract_id_collision.md` §7 Reading A, operator-ratified 2026-05-24, §8 + §9 FULLY-CLOSED/applied at v1.13); and code (`workflow_driver.py` = WorkflowDriver vs `validator_framework_types.py` = ValidatorFramework). **Correct.**
- v1.32 correctly does NOT rewrite the historical v1.29–31 change-notes (delta-only preservation). The corrected labels appear only in v1.32's own `§-preserved-verbatim` table (line 175–185) + the §-adjacent (a) observation (line 193), with the forward-only framing explicit ("the historical change-notes are preserved verbatim"). **History-preserving — confirmed.**
- The `harness-cp/CLAUDE.md` diff applies the same forward-correction in the §1.2 parenthetical (C-CP-25 ValidatorFramework→WorkflowDriver; C-CP-28 validator-hook→ValidatorFramework). Consistent.

### Check 4 — Stale-carry-text / cross-spec drift grep. PASS (drift correctly scoped, not absorbed).

- Delta-only preservation honored: `§-preserved-verbatim` table (line 173–187) + footer (line 210) assert v1.31 body + §25.1–§25.9 + §26–§29 PRESERVED VERBATIM; §25.10–§25.18 purely additive. The change-note's "honored-then-lifted" framing of the §25.1 deferral (not contradicted) is the correct delta-only shape.
- The sibling `C-CP-25 ValidatorFramework` mislabel survives in ~10 sibling artifacts (`Spec_Control_Plane_v1_10/11/14/31.md`, CP/runtime plans v2.18/v2.19, CXA v2.6, runtime spec). v1.32 §-adjacent (a) **correctly flags this as a Q1 cite-hygiene fold-in** and does NOT attempt to fix it here (narrow-scope / FM-2 discipline). This is the right disposition — fixing it in-arc would be scope-creep; flagging it is the obligation, and v1.32 meets it.

### Check 5 — X-AL-3 / no-silent-design-extension. PASS.

- **Zero closed-enum extension.** `RunStatus.PARTIAL` is an **existing** reserved value (code `workflow_driver_types.py:57`; spec §25.2 "reserved for future multi-step error modes") — `proceed→PARTIAL` activates a reserved value, NOT a silent enum extension. Verified the enum currently carries SUCCESS/DRAINED/FAILED/PARTIAL/PAUSED (5 values) at HEAD. The `TopologyPattern` enum stays closed-at-6; §25.17 explicitly keeps `TopologyPatternNotYetMaterializedError` for any future non-enumerated topology, naming enum-extension as a "Class-2 D4 revision."
- **Zero ADR-F2 / six-field / §6 hash-chain change** — verified: D1 (§25.12) composes ADR-F2 §Consequences's own single-threaded-write boundary; the Route-Y sidecar follows the `procedural_tier_snapshot_ref` D-derivative template that itself preserved the §5 six-field shape (IS spec v1.3 change-note). The six-field shape (`ADR-F2.md:28`) is untouched.
- **Runtime `RunStatus.PARTIAL` projection correctly DEFERRED to B1-spec-2** (§25.15.1 table note + §25.18). Verified `_CP_TO_RT_STATUS` (api.py:862-868) has **no PARTIAL entry** today (a PARTIAL reaching api.py:905 would KeyError) — so the spec is right that the projection (`_CP_TO_RT_STATUS` += `PARTIAL→'partial'` + the C-RT-09 `Literal` widen) does not exist yet, and it correctly defers it rather than asserting it exists. The deferral is to a coordinated **build** arc (B1-spec-2), not a defer-and-close — consistent with the FULL-SPEC directive.

### Check 6 — Halt-route-split-AC / scope. PASS.

The arc is correctly scoped to the **CP spec only**. The IS sidecar is split to B1-spec-1b (§25.13 + §25.18) and the runtime materialization to B1-spec-2 (§25.18) — both are coordinated **forward build arcs** enumerated in the design §8 cascade, not silent absorptions and not defer-and-close. The materializable atom (the CP-side WorkflowDriver contract extension) is landed; the cross-axis/runtime atoms are routed forward with named arc IDs. This is the correct halt-route-split shape: land what this axis owns, route the cross-axis carriers as their own coordinated PRs.

### Check 7 — Cascade-cancel resolution soundness (under FULL-SPEC). PASS.

The Fork-A resolution (dispatch-boundary-bounded; no new primitive; 8 obligations at §25.15.2) is internally consistent and complete:

- The 8 obligations are mutually coherent and each composes a **verified-committed** primitive: DRAIN §25.4 (✓ v1.6 §25.4), C-AS-02 + ADR-F4 (✓), C-CP-19 §19.1 (✓), C-CP-16 (✓), Route-Y sidecar (the `procedural_tier_snapshot_ref` precedent, ✓), branch-scoped idempotency (C-IS-07 §7.5 dedup-on-idempotency_key, ✓).
- **"Carry open" is correctly NOT used.** The no-compensation/saga decision is grounded as a *complete* semantic, not a deferral: (a) irreversible-effect rollback is incoherent (impossible ≠ deferred — valid); and (b) **GROUNDED, not taken on the spec's word** — the AS spec blast-radius taxonomy itself defines `external-reversible` = "External effects rollbackable (e.g., HTTP write to durable record **with rollback API**)" (`Spec_Action_Surface_v1.md:452`) vs `external-irreversible` = "not rollbackable (email send, payment)" (line 453). The reversible-effect rollback is therefore a **tool-contract-owned** surface that already exists in the committed AS contract, plus C3/shadow-Git rollback (`Spec_Information_Substrate_v1.md:626`). So under FULL-SPEC there is **no buildable-but-deferred capability** here: compensation-for-reversible already lives in the committed `external-reversible` tool-contract semantics; compensation-for-irreversible is genuinely out-of-domain. The "composes committed primitives → not a meaningful-architecture gate" §13.4 discriminator is correctly applied.
- One honest sub-nuance (non-blocking, pre-existing): the IS spec defers "specific rollback API surface" to implementation discretion (`Spec_Information_Substrate_v1.md:636`). That is a **pre-existing deferral in a cleared spec**, not introduced or owned by v1.32; it does not undercut the cascade-cancel completeness argument (the *contract* distinction reversible/irreversible is committed; only the concrete shadow-Git rollback API shape is impl-discretion).

---

## Findings considered and rejected (transparency)

- **F-REJ-01 — A8 framing contamination (X-AL-3, highest-value attack).** Checked whether v1.32 silently picks a persona/stack/deployment value or extends a closed enum/ADR. It does not: I-6 hand-roll (asyncio, no langgraph/crewai/temporal) is explicit (§change-note + §25.11); CP-AL-1 (never the H_E `Agent` tool) is explicit (§25.11); all extensions compose committed primitives. **Handled cleanly.**
- **F-REJ-02 — RunStatus enum silent extension.** Checked `proceed→PARTIAL`. PARTIAL is a pre-existing reserved value at both code (line 57) and spec §25.2; activating a reserved value is not extension. **Not a finding.**
- **F-REJ-03 — C-RT-30 double-use collision.** The runtime spec uses `C-RT-30` for BOTH §14.19 `WorkflowManifestLoader` (v1.35) AND §30 `resume()` (v1.45) — flagged as a "Class-3 doc-hygiene finding (pre-existing)" in the runtime spec's own v1.46 change-note. v1.32's "C-RT-35 `api.resume`" resolves unambiguously in-context to the §30 `resume()` meaning. This is the **runtime spec's** own R-CL-Q1 doc-hygiene issue, NOT a v1.32 defect — v1.32 is a downstream consumer citing the correct contract. **Not a v1.32 finding** (surfaced here for traceability).
- **F-REJ-04 — runtime cite at v1.45 while head is v1.47.** v1.32 cites "runtime spec v1.45" for the `'paused'`/`RunStatus.PAUSED` precedent (§25.18, §-adjacent (c)), but the runtime spec head is **v1.47** (verified). This is **NOT stale** per the workspace's own delta-baseline §-cite convention (root CLAUDE.md §2: "a §-cite names the version of last substantive definition… often older than the head… intentional and resolve byte-exact"). The `'paused'` Literal + `pause_snapshot` field were last substantively defined at **v1.45** (verified: v1.45 change-note line 49 "ADD `'paused'` to the `status` `Literal`… minor-bump"); v1.46/v1.47 did not re-table them. Citing v1.45 as the *authoring event* of the precedent is byte-correct. **Not a finding.**
- **F-REJ-05 — §25.14 role-discard claim (strongest body candidate).** Pursued whether "`AgentRole` is discarded at dispatch" is grounded or a convenient assertion that hollows the D2 decision. **Grounded** at `llm_dispatch.py` (line 281 `_MVP_DEFAULT_AGENT_ROLE`; ~484–489 "DISCARDED at this boundary") and independently corroborated by CP spec v1.31 §29 change-note. Downgraded to the F-INFO-02 path-precision nit only. **Not a FIX-IN-ARC finding.**
- **F-REJ-06 — no-compensation completeness (the claim I took on the artifact's word; re-grounded per advisor).** Grep-verified prong (b): per-step rollback for reversible effects is a committed AS-contract surface (`external-reversible` w/ rollback API, `Spec_Action_Surface_v1.md:452`) + C3 shadow-Git (`Spec_Information_Substrate_v1.md:626`). Under FULL-SPEC, nothing buildable is deferred. **Clean rejection** (see Check 7).
- **F-REJ-07 — A4 fabricated citations.** Spot-read every §-cite the task flagged; all resolve (Check 1 table). **No fabrication.**
- **F-REJ-08 — Spec-prose-vs-design drift (FM: plan/spec-body drift).** Compared v1.32's D1/D1.a/D1.b/D2/D3 against the cleared B1 design (arc #2 §2/§4/§5). Byte-faithful absorption — same decisions, same recommended dispositions, same operator-open lever (B1↔B4 sequencing, default-if-silent D2) surfaced identically. **No drift; faithful absorption, not silent extension.**
- **F-REJ-09 — Verification-shape grep-vs-e2e.** §25.18 B1-impl-N enumerates per-strategy deterministic-append regression + persisted-branch-causality + cascade-cancel idempotency + **live e2e where a provider step is involved**. The verification shape matches the contract demand (e2e for the provider-touching transit path). **Handled.**
- **F-REJ-10 — A5 missing uncertainty signals.** A spec amendment is a decided-contract artifact, not a deliberation; the open-vs-decided surface is carried via the explicit fork records + the one operator-open sequencing lever (§25.14). Confidence-tag absence is appropriate for a settled-contract delta. **Not a finding.**

---

## Disposition

**Clearance with 2 informational nits** (per §4.1.1 — only minor/Class-1-drift findings present; no Class-2/Class-3 / no BLOCKS-MERGE / no FIX-IN-ARC).

- F-INFO-01 (clearance-marker footer) resolves naturally at the merge step (file the marker) or by a one-word footer softening — non-blocking by construction.
- F-INFO-02 (bare `llm_dispatch.py` path) resolves at B1-spec-2 / B1-impl when the seam is materialized — non-blocking.

No §2.7.6 fork is triggered (no Class-1 halt, no Class-2 operator-decision; the one operator-open lever — B1↔B4 sequencing — is already correctly surfaced by the artifact with a default-if-silent recommendation per the standing autonomous directive, not a defect the reviewer introduces).

This is one of the cleaner design-substrate amendments reviewed: the cite discipline is empirically airtight on exactly the surfaces the workspace most often drifts on (cross-spec §-cites, code-line cites, closed-enum extension, ADR-foundational-change avoidance, defer-vs-build under FULL-SPEC).

---

*Filed by harness-adversarial-reviewer (genuine dedicated-agent invocation) at R-FS-1 arc #3 B1-spec-1 pre-merge gate, 2026-06-13. Read-only review; no artifact edited. All cites verified by reading source at HEAD.*
