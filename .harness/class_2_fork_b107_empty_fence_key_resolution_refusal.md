# Class 2 Fork — B-107: no channel REFUSES an operator resolution addressed to an EMPTY effect-fence key

**Status: FILED 2026-08-01, awaiting operator ratification.** Doc-only filing per the workspace
codex-context-guard rule (fork FILINGS ship doc-only FIRST; no `design-substrate/**` edit rides this
PR). Chain mirrors `B-97`(a)'s and `B-65`'s: **filing (this PR) → operator ratification → spec
leg(s) → impl leg.**

**Register row.** `B-107` at `.harness/forward-register.yaml:3461` (`status:
design_substrate_gated`, `pr: '#pending'`) + prose at `.harness/post-phase-8-forward-register.md`
`### B-107`. The row's `close_out` carries the **2026-08-01 grounding pass absorbed at PR #1177**;
this filing is the fork the row's status transit declared **OWED but not yet filed**. The row's
`pr:` pointer and any status change ride the **ratification** leg, not this PR.

**Grounding HEAD.** `abf2593f`. Every `§`/line cite below was re-resolved by direct read at this
HEAD; **no anchor moved from the row's `c1afb225` grounding**, and the two cite-shape observations
that surfaced are recorded at §10 rather than silently normalized.

**What this filing does NOT do.** It does not re-litigate the row's established facts (the corrected
seven-site consult map; the `any()` position-dependence; the four terminal/consumption sites; the
`{"": ABORT}` over-application harm; the absence of any contract term supporting a build-now
refusal; the b80 empirical pin; the amended closure criterion; the not-free `_any_fence_abort`
slice). It **re-verifies** them (§10) and composes them into the operator's decision.

---

## §1 The question, and what carries it

An **empty captured `idempotency_key`** is reachable on the durable effect-fence carriers, and **no
channel refuses an operator resolution addressed to it.** The adjudicated rule is already settled —
`Spec_Control_Plane_v1_113.md` §1.2 publishes it verbatim: the key-ABSENT source shapes are
*"position-only …, which the resume path cannot address"* (`:95`). What is **not** settled is
**which seam enforces that rule**, and the answer is a design-substrate change in every shape that
closes it.

**Two failure modes, not one.**

1. **SILENT DROP.** A resolution addressed to `""` is either threaded as an
   `EffectFenceResolutionDirective(idempotency_key="")` that **no runtime dispatcher can ever
   match** (the LINEAR consult), or never consulted at all (the truthiness-guarded per-branch and
   orchestrator delivery consults). Different mechanism, identical outcome: a silent INERT re-pause
   with no diagnostic.
2. **OVER-APPLICATION — the worse of the two.** A `{"": ABORT}` map entry reaches the **level-local
   `_any_fence_abort` scans**, which iterate `_recovered_effect_fence_paused.values()` with **no
   empty-key filter** (`workflow_driver.py:7841` / `:11710`), and the run-level ABORT guard at
   `:8238` / `:12576` then **suppresses a KEYED sibling's valid directive**. That is precisely the
   cross-location misattribution `Spec_Control_Plane_v1_107.md` §1.1(a) forbids (`:30`, *"never a
   cross-location misattribution of a `SKIP_AS_FIRED`/`RE_FIRE`/`ABORT`/`ABORT_BRANCH` judgment
   intended for a different location"*). `[HIGH]`

**Why it is a fork rather than an impl task — the three legs, re-verified at this HEAD.** `[HIGH]`

- **No membership term supports a build-now refusal.** `Spec_Control_Plane_v1_107.md` §1.1's
  unaddressed-set membership **INCLUDES** `""`: the test is `not in resolutions` over an enumeration
  that keeps `""` by design (`workflow_driver.py:2965`–`:2967`), and
  `Spec_Control_Plane_v1_112.md` §2.1 states it outright at `:111` — *"the authoritative effect-fence
  walk **includes** the empty key, the uniform-fallback computation **counts** it, and only the abort
  walk filters it."*
- **The "cannot address" language is PUBLICATION, not a rule source.**
  `Spec_Control_Plane_v1_112.md` §2.4 disqualifies §2 in its own words at `:149` — *"§2 publishes;
  it does not decide … MUST NOT become a second place where classification semantics are stated."*
  So `v1.113` §1.2's *"cannot address"* row records a rule; it cannot **be** the rule that a refusal
  enforces.
- **The Runtime refusal battery is closed and has no matching class.** `Spec_Harness_Runtime_v1.md`
  §30's failure-mode taxonomy is a table of **12 data rows** (`:3421`–`:3432`, recounted
  programmatically), none of which names an empty-fence-key condition. A refusal needs a **new fail
  class**, which is a spec change by construction.

**The empirical pin.** Disposition (a) — filtering `""` out of the uniform-fallback candidate set —
**flips a deliberately-pinned test**:
`test_map_addressed_keyed_abort_activates_alongside_an_unrelated_keyless_pause`
(`harness-cp/tests/test_workflow_driver_effect_fence_tree_wide_abort_b80.py:222`–`:257`), whose
`:254` assert reads `... is False`. Its docstring (`:223`–`:231`) states the pinned rule explicitly:
*"a co-existing keyless pause STILL occupies a slot in `compute_effect_fence_uniform_fallback_
eligible_key`'s own (unfiltered, pre-existing B-70) unaddressed-count."* Filtering the keyless
candidate leaves the KEYED location **solely** eligible, the uniform `ABORT` reaches it, and the
assert becomes `True`. **It is the executable pin of the rule (a) would move** — which is why (a) is
a spec amendment, not an impl tweak.

---

## §2 Current behaviour at HEAD `abf2593f`

| Surface | State |
|---|---|
| **The resolver** | `_resolve_effect_fence_gated` (`workflow_driver.py:2973`). Returns a resolution when `is_mapped or idempotency_key == eligible_key` (`:3000`–`:3001`); else `None`. **Neither branch excludes `""`** — a `{"": …}` map entry makes `is_mapped` **True**, and an `eligible_key == ""` makes the scalar branch fire |
| **MAP channel** | `ResumeContext.effect_fence_resolutions` is `dict[str, EffectFenceResolution]` with **UNCONSTRAINED keys**. A caller acting outside the projection can hand-build `{"": …}` directly or through `AccessorDerivedResumeContext` |
| **SCALAR channel** | `compute_effect_fence_uniform_fallback_eligible_key` (`:2935`–`:2970`) does **not** filter empty keys — unlike its sibling `compute_effect_fence_tree_wide_abort_present`, whose candidate comprehension at `:3053` **does** (`if k`) |
| **Resolver consult sites** | **EXACTLY SEVEN**, recounted programmatically (11 textual occurrences − 1 `def` at `:2973` − 3 in comments at `:7809`/`:11674`/`:12538`). See the map at §3(i) |
| **Terminal consumption sites** | **EXACTLY TWO**, by a programmatic sweep of the non-test tree: `runtime_tool_dispatcher.py:1042` and `managed_agents_dispatch.py:300`, both performing the identical `step_context.effect_fence_resolution.idempotency_key == idempotency_key` match. Neither can ever match `""` (the key composed at `runtime_tool_dispatcher.py:989` is never empty) |
| **Reachability, per carrier** | **BRANCH** — `""` reached **DELIBERATELY** at crash reconstruction (`:4074`, `idempotency_key=""`) and defensively through the ordinary fan-out coercion (`:9625`/`:9752`/`:14024`/`:14149`): a **PRODUCTION** shape. **LINEAR** — defensively (`:5456`). **ORCHESTRATOR's OWN carrier** — **not reached at all** (its construction guard chain ends in a truthiness test at `:12376`–`:12381`), so its exposure is **type-level only** |
| **Level-local abort scans** | `_any_fence_abort` at `:7838`–`:7842` (PARALLELIZATION) and `:11707`–`:11711` (ORCHESTRATOR_WORKERS / HIERARCHICAL_DELEGATION per CP spec v1.111 §2.2) — `any(... for _k in _recovered_effect_fence_paused.values())`, **UNFILTERED** |
| **Suppression consumers** | `:8238` and `:12576` — `if _any_fence_abort and _branch_resolution is not EffectFenceResolution.ABORT: _branch_resolution = None`. This is the site the `{"": ABORT}` over-application harms |
| **Carrier-order construction** | `_recovered_effect_fence_paused` is a dict comprehension over `…effect_fence_paused_branches` (`:7791`–`:7795`, `:11655`–`:11659`), and that tuple is `tuple(sorted(keyed dispositions)) + crash_pause_reconstruct_fence_paused` (`:10280`; the ORCHESTRATOR_WORKERS twin at `:14639`) — the crash-reconstruction `""` entries are appended **LAST** |
| **Non-bypassable chokepoint** | `execute_workflow` (`:3061`–`:3076`), which already receives `pause_snapshot_input`, `resume_context` **and** all three root-computed signals as parameters. `execute_workflow` is a **public export** of `harness_cp.workflow_driver`'s `__all__` (verified) |
| **The three root signals' computation site** | `mcp_server.py:378`–`:403` — the ONE site holding the **un-narrowed depth-0 root** together with `_resume_context` |
| **Contract publication of the rule** | `Spec_Control_Plane_v1_113.md` §1.2 `:95` — key-ABSENT shapes are *"position-only …, which the resume path cannot address"* |

---

## §3 Three grounding findings that shape the readings

### (i) The CORRECTED SEVEN-SITE MAP — and a cite-shape note the row's map leaves implicit `[HIGH]`

Exactly seven `_resolve_effect_fence_gated` call sites exist at this HEAD. The register's map cites
**the guard line** for the guarded sites and **the call line** for the ungated ones; both resolve,
but the mixed shape is worth stating so a later session does not read a guard cite as a call cite:

| # | Call line | Guard | Reached with `""`? |
|---|---|---|---|
| 1 | `:3056` | `if k` filter at `:3053` | **NO** — pre-filtered |
| 2 | `:4926` | none | **YES** — LINEAR consult, ungated |
| 3 | `:7839` | none | **YES** — PARALLELIZATION level-local `_any_fence_abort` scan; `:7841` iterates `.values()` unfiltered |
| 4 | `:8213` | `if (_branch_fence_key and _ef_resume_ctx is not None)` at `:8216` | **NO** — truthiness-guarded |
| 5 | `:11708` | none | **YES** — ORCHESTRATOR_WORKERS level-local scan; `:11710` unfiltered |
| 6 | `:12113` | `if (_orch_fence_resume.idempotency_key and …)` at `:12118` | **NO** — the ORCHESTRATOR's OWN carrier short-circuits |
| 7 | `:12551` | `if (_branch_fence_key and _ef_resume_ctx is not None)` at `:12554` | **NO** — truthiness-guarded |

**The consequence that reshapes disposition (c).** A refusal placed **inside the resolver** reaches
sites #2, #3 and #5 — so it **does** reach the BRANCH/WORKER carrier's empty keys. It does **not**
reach the ORCHESTRATOR's own carrier (site #6 is that carrier's ONLY consult, and it is guarded),
and it does **not** reach the per-branch **delivery** consults #4/#7 — which is exactly where the
silent-drop half lives, because those sites never call the resolver with `""` at all. **A
resolver-internal refusal therefore closes neither failure mode completely.**

### (ii) The `any()` is POSITION-DEPENDENT — an independent reason the resolver-internal shape is unsound `[HIGH]`

`_recovered_effect_fence_paused` is built in **carrier order** (a dict comprehension preserves
insertion order), and the carrier tuple appends the crash-reconstruction `""` entries **LAST**
(`:10280` / `:14639`). A keyed sibling resolving `ABORT` therefore **short-circuits the `any()`
before the `""` entry is ever evaluated**. A resolver-internal refusal would consequently fire — or
not fire — depending on **sibling resolution order** rather than on the presence of the empty key.
**A refusal whose firing depends on iteration order is not a refusal.**

### (iii) The tree-wide filter's OWN stated premise is FALSIFIED by the corrected map — which is the strongest ground for the bounded slice `[HIGH]`

`compute_effect_fence_tree_wide_abort_present` already filters empty candidates at `:3053`, and its
docstring justifies that filter at `:3040`–`:3050`:

> *"a `""` `idempotency_key` … is **NEVER actually key-bound-resolvable at the real per-branch
> consult sites** (`if (_branch_fence_key and _ef_resume_ctx is not None)` at both fan-out dispatch
> sites) — they treat it as unresolvable and re-pause INERT rather than ever consulting the uniform
> fallback for it. Passing `""` through here unfiltered could let a uniform ABORT default falsely
> activate the tree-wide signal from an entry no real consumer would ever resolve to ABORT,
> **spuriously suppressing unrelated valid HITL delivery elsewhere in the tree**."*

That rationale is **true of the per-branch DELIVERY consults (#4/#7) and FALSE of the level-local
`_any_fence_abort` scans (#3/#5)**, which the same paragraph does not consider. The harm the
docstring names — *spuriously suppressing unrelated valid delivery* — is **exactly the `{"":
ABORT}` over-application at `:8238`/`:12576`**, occurring through the sibling scan the filter was
never applied to. This matters for Reading C: the level-local empty-key filter is best characterized
as **correcting a stated premise that is false as written**, not as inventing a fresh narrowing.

---

## §4 The readings

Four readings, composed from the row's disposition space. **(a)/(b)/(c)/(d)** below are the row's
own disposition labels.

### Reading A — (a)+(d) + a RESOLVER-BOUNDARY removal: take the empty key out of the addressable set, and enforce it where no caller route can reach around *(RECOMMENDED)*

**THREE parts, and the third is load-bearing** *(added at out-of-family review round 1, which
falsified a two-part draft with two `[P1]`s — see §10.1; both were confirmed empirically before
acceptance)*. The classification legs (a) and (d) state the rule; the resolver-boundary leg
**enforces** it.

**(a) SCALAR channel — the classification.** Amend `Spec_Control_Plane_v1_107.md` §1.1's
unaddressed-set membership so an **empty** captured key is **excluded**, and filter `""` out of
`compute_effect_fence_uniform_fallback_eligible_key`'s candidate set exactly as
`compute_effect_fence_tree_wide_abort_present` already does at `:3053`. An empty-key location is then
**unaddressed by the contract** and the helper can never nominate it as `eligible_key`.

**(d) MAP channel — the operator-facing refusal.** Constrain
`ResumeContext.effect_fence_resolutions`' key domain (a minimum-length-1 key type) so an
operator-authored `{"": …}` is **refused on the ordinary construction path** — the fail-loud half of
§5.3.

**(e) THE ENFORCEMENT POINT — `_resolve_effect_fence_gated` treats an empty `idempotency_key` as
unresolvable** (`if not idempotency_key: return None`, ahead of both the `is_mapped` and the
`== eligible_key` branches at `:3000`–`:3001`). This is the **one private site every consult
transits** — all seven sites of §3(i) call it, it is `_`-prefixed and called nowhere outside
`workflow_driver.py`, and **no caller route can supply around it**.

> **Why (a)+(d) alone are NOT enough — both bypasses verified at this HEAD.** `[HIGH]`
>
> - **(d) does not make `{"": …}` unrepresentable.** `ResumeContext`'s `model_config` is
>   `ConfigDict(extra="forbid", frozen=True)` (`pause_resume_protocol_types.py:1048`), but the field
>   is a plain `dict[str, EffectFenceResolution] | None` (`:1079`) — `frozen=True` blocks field
>   **reassignment**, not **nested mutation**. **Empirically reproduced at this HEAD:** constructing
>   `ResumeContext(effect_fence_resolutions={"ok": ABORT})` and then executing
>   `c.effect_fence_resolutions[""] = ABORT` **is ACCEPTED** (field reassignment on the same object
>   raises `ValidationError`; the item assignment does not). A key-domain annotation validates at
>   construction only, so a post-construction mutation reaches the consults unvalidated.
> - **(a)'s filter is bypassable through a public parameter.**
>   `effect_fence_uniform_fallback_eligible_key: str | None = None` is a **public keyword argument**
>   on the exported `execute_workflow` (`:3074`). A direct caller supplies `""` for it **without
>   ever calling the filtered helper**, and `_resolve_effect_fence_gated`'s
>   `idempotency_key == eligible_key` branch then honours the scalar. The helper is one producer of
>   that signal; the parameter is a second.
>
> **(e) neutralizes both:** an empty `idempotency_key` returns `None` before either branch is
> consulted, whatever the map holds and whatever a caller passed for eligibility.

- **A property of the removal shape that a refusal does NOT have.** `[HIGH]` (e) is **immune to
  §3(ii)'s position-dependence**. Returning `None` for `""` is order-independent — every `""` entry
  yields `None` regardless of where it sits in carrier order — whereas a *refusal* placed at the
  same site fires or not depending on which sibling the `any()` short-circuits on. The
  position-dependence finding is an argument against a resolver-internal **refusal**, not against a
  resolver-internal **removal**.
- **Spec deltas owed.** A **CP** spec leg amending §1.1's membership term (the classification rule
  itself — which `v1.112` §2.4 confirms only §1 may state), the `ResumeContext` field-domain
  constraint, **and** the resolver-boundary removal stated as a contract term rather than left to
  impl discretion (it is the enforcement the other two rely on). **No Runtime §30 delta; no new fail
  class; the 12-row battery stays closed.**
- **Blast radius.** `[HIGH]` **(d) collides with a PRESERVED-VERBATIM guarantee.**
  `Spec_Control_Plane_v1_112.md` §0.4 lists the four `ResumeContext` response fields —
  `effect_fence_resolutions` among them — as **"PRESERVED VERBATIM"** (`:38`), so a key-domain
  change owes its own byte-compat argument. `Spec_Control_Plane_v1_114.md` §0.5 finding (v) records
  (`:61`) that this is the **SAME obstacle** as `B-101`'s disposition (a), and that **the two rows
  stay SEPARATE — no merge is proposed**. That makes a **joint discharge worth pricing**: one
  byte-compat argument could discharge the obstacle for both rows. It must be **determined at the
  spec leg, not assumed** — and the rows still do not merge.
- **Effect on the b80 pinned test.** **FLIPS `:254` from `is False` to `is True`** (§1). The test is
  the executable pin of the membership rule (a) amends, so the flip is the *expected consequence of
  a ratified spec change*, and the spec leg must say so — an unexplained pinned-test flip is the
  failure mode this bullet exists to prevent.
- **Liveness — grounded, not assumed.** Filtering is **NEUTRAL** in the lone-empty-key case (the run
  already re-pauses INERT today) and **STRICTLY MORE LIVE** in the mixed case (one empty + one
  keyed), where today `unaddressed` has 2 members so **neither** may take the uniform fallback,
  whereas filtering leaves the KEYED location solely eligible. This is precisely what the b80
  docstring pins, read from the other side.
- **Does it close the OVER-application harm?** **YES — via (e).** `_resolve_effect_fence_gated(ctx,
  "", …)` returns `None` at **every** site, so the level-local `any()` can never count a `""` entry
  and `:8238`/`:12576` can never suppress a keyed sibling on an empty key's behalf. `[HIGH]`
  *(Corrected at round 1: an earlier draft attributed this closure to (a)+(d) alone, which the two
  verified bypasses above falsify.)*
- **Fail-loud vs INERT.** **Split, and the split is the point.** `[HIGH]` **FAIL-LOUD** on the MAP
  channel: (d) refuses an operator-authored `{"": …}` at construction — the earliest seam at which
  the operator is still holding the mistake, and operator-actionable because the operator authored
  it. **INERT** on the position-only crash-reconstruction location: the operator never authored that
  key and cannot remove it, so a refusal there would be *"a refusal the operator cannot act on … a
  livelock with good manners"* — the bar `Spec_Harness_Runtime_v1.md` §30 term 4 sets at `:3398`.
  Under the closure criterion, INERT here is clause **(i) removal from the addressable set**, not
  clause **(a) silent drop**.
- **The residual (d) leaves, and why closing it is REQUIRED rather than optional** *(round 1 [P1];
  the disposition corrected at round 2 [P1])*. `[HIGH]` Because the map is a plain mutable `dict`,
  an operator who **mutates after construction** gets (e)'s silent removal rather than (d)'s
  refusal — i.e. clause **(a) silent drop** survives on that one route. **Two shapes, and they are
  NOT equally available:**
  - **(6-i) — REQUIRED FOR CLOSURE.** Give the field a **validated immutable mapping**, so the
    invariant cannot be mutated around. **The constraint must be validate-and-COPY, not wrap:** a
    read-only view over a mapping the caller still holds a reference to reintroduces the same route
    through the caller's own alias. Cost: the amendment narrows the field on **two** axes (key
    domain + container mutability) — but it is **ONE amendment site and ONE byte-compat argument**,
    not two, and it is behaviour-visible to any caller that mutates the map after constructing it.
  - **(6-ii) — accept the residual, and A is then a PARTIAL close.** `[HIGH]` *(Recommended in this
    filing's round-1 draft; **withdrawn at round 2 [P1]**, which correctly caught the internal
    contradiction: the criterion says **"Partial is non-closure"**, so a disposition that knowingly
    leaves clause (a) alive on a reachable route **cannot close `B-107`.** (6-ii) is still a
    legitimate operator choice — but only as **harm reduction with the row held OPEN**, never as a
    closure.)*

  **Recommended: (6-i).** `[MODERATE]` The row closes or it does not; ratifying (6-ii) as a closure
  would be the filing contradicting its own criterion.
- **Orchestrator scope.** Type-level only (§2) — site #6 is that carrier's only consult and it is
  truthiness-guarded, so it never reaches (e) at all; (d) covers its ordinary construction path and
  (e) covers it vacuously. Its witnesses must be **constructed-snapshot detect-then-refuse** tests
  per the `B-100` precedent (CP plan v2.48 **AC #A11**,
  `Implementation_Plan_Control_Plane_v2_48.md:53`; Runtime plan v2.57 **AC #16(a)**,
  `Implementation_Plan_Harness_Runtime_v2_57.md:78`), never an e2e run.
- **What it does NOT do.** It produces no **runtime diagnostic** for an empty-key location. The
  operator learns nothing beyond the ordinary INERT re-pause — which is the adjudicated correct
  state, but it is silence, and §6 owns that trade rather than hiding it.

### Reading B — (c): refuse at the seam

Raise, rather than silently skip or thread, when a resolution is addressed to an empty key. **The
only option that converts DROP into REFUSE.** It needs a **NEW Runtime §30 fail class** plus a
detect-then-refuse invariant, and its **seam placement must be RE-DERIVED against the corrected
map** — the row's earlier *"cheapest sound placement is an ADMISSION-TIME check"* was chosen against
a map now known false.

**Seam-placement re-derivation — stated honestly, sound and unsound alike:**

| Candidate placement | Sound? | Why |
|---|---|---|
| **Inside `_resolve_effect_fence_gated`** | **NO — twice over** | Reaches #2/#3/#5 but **misses** the ORCHESTRATOR's own carrier (#6, its only consult, guarded) and the per-branch DELIVERY consults (#4/#7 — where the silent drop lives, because they never call with `""`). And per §3(ii) its firing at #3/#5 is **iteration-order-dependent** |
| **Admission at `api.py:823`** (`_enforce_pause_state_staleness_precondition`) | **NO — bypassable** | `execute_workflow` is a **public `__all__` export** of `harness_cp.workflow_driver` (verified), so a direct caller reaches the consults without transiting `api.resume()` |
| **Depth-0 `mcp_server.py:378`–`:403`** | **NO — bypassable** | It is the ONE site holding the **un-narrowed** root, which is why the three tree-wide signals are computed there — but it is bypassed by a direct `execute_workflow` caller **exactly as `api.py` is**. It is merely where those signals *happen* to be computed today |
| **`execute_workflow` DRIVER ENTRY (`:3061`–`:3076`)** | **YES for a PER-LOCATION check** | The only **non-bypassable** chokepoint: `api.resume()` via `mcp_server`, a direct public caller, and the recursive child re-entry (`child_workflow_runner.py:261`) **all** transit it, and it already receives `pause_snapshot_input`, `resume_context` and the three root signals as parameters |
| **`execute_workflow` DRIVER ENTRY, INPUT-KEYED** *(the shape §6 requires of B anyway)* | **YES — and it needs NO root discriminator** | *(Established at round 2 [P1], which corrected an earlier row of this table.)* Once the refusal keys on **operator INPUT** rather than on a location, the check reads only `resume_context` and `effect_fence_uniform_fallback_eligible_key` — **both parameters of every invocation** (`:3072`, `:3074`) — and refuses an empty map key, or a non-`None` scalar with `eligible_key == ""`, **at root and recursive entries alike, before any `any()` runs**. No tree walk, so the per-level narrowing of `pause_snapshot_input` is irrelevant; **`sub_agent_descent` is not needed**, and §3(ii)'s order-dependence **does not apply** |
| ~~`execute_workflow` OUTER entry, for a LOCATION-keyed TREE-WIDE check~~ | **moot under the input-keyed shape** | Retained so the reasoning is not re-derived: a *location*-keyed check would walk `pause_snapshot_input`, which **is** narrowed per recursion level, so only the outer invocation sees the whole tree — and discriminating outer from re-entry would then be real design work (`sub_agent_descent` is the in-house discriminator, named as *"the 'am I the depth-0 root' discriminator"* at `workflow_driver.py:11033` and used at `:4990`/`:11046`/`:15141`, but it is a default-`False` keyword a direct caller can supply). **The input-keyed shape avoids all of this**, which is why it is the one B should take |
| **Six per-consult guards** (all seven sites bar the pre-filtered #1) | **NO by the row's own binding rule** | Complete only *by enumeration*, and the row binds scope **by rule**: *every* site reading a fence key off a resume carrier or off `resume_context` is in scope "whether or not it is named". Four successive review rounds each found one more site; a seventh is not ruled out. It also does not fix §3(ii) unless placed **before** the `any()` |

**The REMOVAL variant of this seam is NOT a competitor to Reading A — it IS Reading A's enforcement
leg** *(recast at round 1; an earlier draft of this filing offered it here as a dismissed
alternative, which was wrong)*. A resolver-internal `if not idempotency_key: return None` is Reading
A's part **(e)**. Alone it is genuinely insufficient — it leaves
`compute_effect_fence_uniform_fallback_eligible_key` still **returning** `""` as the eligible key, so
the empty key is *inert at today's consumers* rather than *removed from the classification*, which
fails the criterion's *"removed by construction from the addressable/**eligible** set"* on the
eligible half and is exactly the shape the row's binding rule warns against (a disposition validated
against a site list rather than against the rule). **That is why A pairs it with (a)'s membership
amendment and (d)'s construction-time refusal, rather than shipping it alone.**

- **Spec deltas owed.** A **Runtime** spec leg: a NEW §30 fail class (the 12-row battery has no
  matching member) + the detect-then-refuse invariant + the placement as a contract term; plus **CP**
  coordination if the check reads CP-owned classification. Larger than A's, on two axes rather than
  one.
- **Blast radius.** `[MODERATE]` A new pre-bootstrap refusal on a resume path changes the failure
  mode of every resume that carries an empty-key location — **including the crash-reconstruction
  shape, which is PRODUCTION-reachable on the BRANCH carrier** (`:4074`). A refusal there converts
  today's silent INERT re-pause into a hard refusal for a state the operator did not create.
- **Effect on the b80 pinned test.** **NONE** — B does not touch the membership rule the test pins.
  This is B's cleanest advantage over A, and it is a real one: A moves a **deliberately pinned**
  rule, B leaves it standing.
- **Fail-loud vs INERT — the question that fixes B's shape.** `[HIGH]` §30 term 4's bar (`:3398`):
  *"a refusal the operator cannot act on is a livelock with good manners."* For an
  **operator-authored** `{"": …}` the refusal passes the bar (re-read, recompose without it). For
  the **crash-reconstruction** empty key it does **not**: the operator never authored it and has
  nothing to recompose. **So B MUST key on the operator's INPUT, not on the LOCATION** — and, per
  round 2, that is also what makes B's placement simple (no root discriminator, no tree walk, no
  order-dependence).
- **What round 2 established in B's favour, recorded because it narrows the margin.** `[HIGH]` An
  input-keyed driver-entry check runs **after** construction, so it catches a `{"": …}` entry that a
  **pre-entry** mutation introduced — the route round 1 found. B therefore needs **no
  `ResumeContext` shape change, no PRESERVED-VERBATIM byte-compat argument, and no `B-101`
  joint-discharge coupling**, and it does not move a pinned rule.
- **But B has a mutation window of its own, and it is a THIRD mandatory term** *(round 3 `[P1]`; an
  earlier draft called B "immune to mutation", which over-claimed and is **struck**)*. `[HIGH]` The
  driver entry validates the **same mutable `dict` object** that `_resolve_effect_fence_gated` reads
  later in the run. A caller that retains its reference and mutates **after the entry check** — the
  ordinary TOCTOU shape — puts `{"": ABORT}` back in front of the consults with the check already
  passed. **B is therefore a closure only if it additionally SNAPSHOTS OR FREEZES the resolution map
  at entry, or performs its check at the actual point of consumption.** Note where that lands: the
  first option is (6-i)'s immutable copy under another name, and the second is Reading A's part (e)
  under another name. **Neither reading escapes the need to bind the invariant at consumption.**
- **What B still does NOT do.** It refuses rather than removes, so the **classification is
  untouched**: `compute_effect_fence_uniform_fallback_eligible_key` keeps counting `""` in the
  unaddressed set, and `Spec_Control_Plane_v1_112.md` §2.1's *"the walk includes the empty key"*
  stays literally true while the resume path refuses to address it. **Two consequences:** the
  mixed-case liveness gain A brings (§4 Reading A) is **absent** under B, and the contract carries a
  rule the code enforces only by refusing at the door. Under the criterion both clause (i) and
  clause (ii) close the row — but (i) is the stronger property.
- **Orchestrator scope.** Site #6 is that carrier's only consult and it is guarded, so a
  resolver-internal placement misses it **entirely**; only the driver-entry placement covers it.
  Witnesses remain **constructed-snapshot** (production-unreachable carrier).

### Reading C — the bounded first slice: the `_any_fence_abort` empty-key filter alone

Add the two-line `if _k` filter at `:7841` / `:11710`. **Fixes the OVER-application harm** — the
worst case the amended criterion had to be widened to cover — and nothing else.

- **Spec delta owed.** `[HIGH]` **It is NOT free impl discretion.** `Spec_Control_Plane_v1_111.md`
  §2.1(b) (`:54`) requires the tree-wide signal be combined with the level-local `_any_fence_abort`
  computation as *"a strict widening of when suppression fires, never a narrowing"* — and filtering
  empty keys **out** of the level-local scan **narrows** the combined predicate. A stated
  reconciliation is owed, plausibly a `v1.111` §2 amendment. §3(iii) is the argument that makes that
  reconciliation cheap and honest: the sibling filter at `:3053` already exists, and its **stated
  rationale is false as written** for the level-local scans — so the amendment records a **premise
  correction**, not a fresh narrowing.
- **Blast radius.** Smallest of the four. Two lines plus one spec paragraph.
- **Effect on the b80 pinned test.** **NONE.**
- **Fail-loud vs INERT.** INERT throughout; **no refusal is introduced.**
- **Orchestrator scope.** Untouched (that carrier has no level-local scan of its own; #6 is its only
  consult).
- **What it does NOT do — and this is dispositive against C as a *closure*.** It leaves the
  **drop-silently half** entirely open on **both** channels. The criterion says **"Partial is
  non-closure."** C is a **harm-reduction leg**, not a close.
- **Independence.** It is the one piece that does **not** depend on the fork's outcome, so it **could
  ship first**. But note the subsumption at §6: **under Reading A it becomes behaviourally
  redundant**, so shipping it first buys interim safety at the cost of a `v1.111` reconciliation that
  A would then make moot.

### Reading D — defer, with the amended criterion standing

No spec text. The row stays `design_substrate_gated`, the amended closure criterion stands as the
bar any future arc must clear, and the binding rule (re-derive the site set programmatically before
selecting a disposition) stands with it.

- **Honest case for it.** The ORCHESTRATOR carrier is production-unreachable; the LINEAR carrier's
  empty key is defensive-only; and the adjudicated rule (an empty fence key is position-only) is
  already **published** at `v1.113` §1.2 — so the *semantics* are settled even though no seam
  enforces them. `[MODERATE]`
- **Honest case against.** The **BRANCH** carrier's empty key is a **PRODUCTION** shape reached
  deliberately at crash reconstruction (`:4074`), and the over-application harm is a **live
  cross-location misattribution** of exactly the class `v1.107` §1.1(a) forbids. Deferring leaves a
  forbidden outcome reachable in production, with the criterion recording it rather than closing it.
- **Effect on the b80 pinned test.** None. **Fail-loud vs INERT.** Status quo (INERT, silent).

---

## §5 The four decisions, per reading

### §5.1 Decision (1) — which channel is closed, and how

| | SCALAR channel | MAP channel | Over-application (`:8238`/`:12576`) | New §30 fail class | Flips b80 `:254` | `ResumeContext` type change |
|---|---|---|---|---|---|---|
| **A — (a)+(d)+(e)** | **removed from the classification (a)**, enforced at the resolver **(e)** | **refused at construction (d)**, enforced at the resolver **(e)** | **closed by (e)** | **no** | **yes** | **yes** (collides with §0.4 PRESERVED VERBATIM) |
| B — (c) | closed by refusal *(driver entry)* | closed by refusal | closed **only if** the check precedes the `any()` | **yes** | no | no |
| C — slice | open | open | **closed** | no | no | no |
| D — defer | open | open | open | no | no | no |

**Why full closure needs all THREE of A's parts** `[HIGH]` *(re-derived at round 1, replacing a
two-part claim two `[P1]`s falsified)*:

- **(a) alone** leaves `{"": ABORT}` in the map → `is_mapped` `True` → the over-application survives.
- **(a)+(C's slice)** leaves `{"": ABORT}` **HONOURED** at the LINEAR consult #2 as an
  `EffectFenceResolutionDirective(idempotency_key="")` that no dispatcher can match — a **forbidden
  outcome** under criterion clause (b), even though it affects nothing else.
- **(a)+(d) without (e)** is bypassed on **both** channels: the map through post-construction
  mutation of the plain `dict` (`pause_resume_protocol_types.py:1048`/`:1079` — reproduced
  empirically, §4), the scalar through the public `effect_fence_uniform_fallback_eligible_key`
  keyword on the exported `execute_workflow` (`:3074`).
- **(e) alone** makes the empty key inert at today's consumers without removing it from the
  classification or refusing the operator's input — clause (i)'s *eligible*-set half stays open, and
  the operator's `{"": …}` is silently dropped (clause (a)).

This re-derives, and sharpens, the row's *"TWO OF THEM ARE NEEDED FOR FULL CLOSURE (one per
channel)"*: two **classification** dispositions, plus **one enforcement point** the row's disposition
space did not name.

### §5.2 Decision (2) — seam placement

Settled by §4's re-derivation. **What is settled regardless of reading:** *any placement that leaves
a direct `execute_workflow` caller unfenced is NOT a candidate.* That rules out `api.py:823` and
`mcp_server.py:378`–`:403` for **every** reading, and it is the reason the row's earlier
admission-time recommendation is withdrawn.

**Round 1's two `[P1]`s sharpen this into a general principle: the enforcement must sit at
CONSUMPTION, not at composition.** `[HIGH]` A construction-time type constraint is bypassed by
post-construction mutation; a computed-signal filter is bypassed by a public parameter carrying the
same signal. Both findings point the same way. **Reading A adopts the principle at
`_resolve_effect_fence_gated` (part (e))** — private, transited by all seven consults,
order-independent. **Reading B adopts it at the driver entry, input-keyed** — which, per round 2,
needs **no root discriminator, no tree walk, and inherits no order-dependence**. Both placements are
sound. **The difference between the readings is therefore no longer *where* but *what*: a removal
that also fixes the classification, versus a refusal that leaves the classification as-is.**

### §5.3 Decision (3) — fail-loud vs INERT

The bar is `Spec_Harness_Runtime_v1.md` §30 term 4 (`:3398`). Applied per **origin of the empty
key**, which is the discriminator the row's council note anticipated but did not resolve:

| Origin | Operator can act? | Correct posture |
|---|---|---|
| **Operator-authored** `{"": …}` map entry | **YES** — re-read the pause state, recompose without the key | **FAIL LOUD** (A: at construction, per (d), with the mutation residual named at §4; B: at the driver entry) |
| **Crash-reconstruction** `""` on the BRANCH carrier (`:4074`) | **NO** — the operator never authored it and cannot remove it | **INERT re-pause**, with the location **removed from the addressable/eligible set** so nothing is delivered to it and nothing it produces alters another location |

**This split is the filing's central substantive claim** `[HIGH]`, and it is what moves the
recommendation: a refusal that fires on the *location* (B's natural shape) fails term 4 for the
production-reachable carrier; a refusal that fires on the *operator's input* (A's (d)) passes it —
and (d) delivers that refusal without a new fail class and without a bypassable seam.

### §5.4 Decision (4) — orchestrator scope + the witness grid

The ORCHESTRATOR's OWN carrier is **PRODUCTION-UNREACHABLE** (its construction guard chain ends in a
truthiness test, `:12376`–`:12381`), so **its witnesses MUST be constructed-snapshot
detect-then-refuse tests** per the `B-100` precedent (CP plan v2.48 AC #A11; Runtime plan v2.57 AC
#16(a)) — **never an e2e run**.

**Witness grid — 2 CHANNELS × 4 CARRIER-SITES = EIGHT cells.** A plain 2 × 3 carrier grid
**under-specifies** it: the BRANCH carrier has **two independent topology sites**, each with its own
`_any_fence_abort` scan and its own suppression consumer — **PARALLELIZATION** (`:7839` / `:8238`)
and **ORCHESTRATOR_WORKERS** (`:11708` / `:12576`; HIERARCHICAL_DELEGATION reuses it per
`Spec_Control_Plane_v1_111.md` §2.2) — so a grid keyed on carrier alone can be satisfied by
exercising one while the other retains the cross-location suppression.

| | LINEAR | PARALLELIZATION branch | ORCHESTRATOR_WORKERS worker | ORCHESTRATOR's OWN carrier |
|---|---|---|---|---|
| **MAP** (`{"": …}`) | cell 1 | cell 3 — **alongside a keyed sibling** | cell 5 — **alongside a keyed sibling** | cell 7 — **constructed-snapshot** |
| **SCALAR** (uniform + `eligible_key == ""`) | cell 2 | cell 4 — **alongside a keyed sibling** | cell 6 — **alongside a keyed sibling** | cell 8 — **constructed-snapshot** |

Each **branch** cell must exercise an empty-key location **alongside a keyed sibling** — that is the
only shape that witnesses the over-application half — and, per §3(ii), must be run with the keyed
sibling resolving `ABORT` **both before and after** the `""` entry in carrier order, or the
position-dependence goes unwitnessed. **A mutation probe is owed** per Workflow v1.18 PD-8: revert
the chosen fix, confirm the corresponding cell **FAILS**, restore.

---

## §6 Recommendation — **Reading A ((a)+(d)+(e))**, with C's slice **subsumed**, not shipped separately `[MODERATE]`

**In one line: take the empty key out of the addressable set as a matter of CP contract, refuse an
operator who addresses one, and enforce both at the resolver every consult transits — so the only
refusal raised is the one the operator can act on, no fail class is minted, and the over-application
dies at the point of consumption rather than at a composition boundary a caller can walk around.**

Grounded rationale:

1. **It satisfies every clause of the amended criterion — under (6-i), and only under (6-i) — and it
   is a HYBRID, not a pure clause-(i) reading** *(the hybrid framing corrected at round 3 `[P2]`; an
   earlier draft claimed clause (i) on both channels, which is false of the map channel)*. `[HIGH]`
   **SCALAR channel — clause (i)**, removal from the eligible set via (a). **MAP channel — clause
   (ii)**, a refusal at construction via (d), made total by (6-i)'s immutable copy. Clause (b)
   (never HONOURED as an address) closed at the LINEAR consult by (e); clause (c) (never alters
   another location's decision) closed at `:8238`/`:12576` by (e); clause (a) (never silently
   dropped) closed on the map channel by (d)+(6-i), without which that route stays open and **A is a
   partial close, not a close** (§4, round 2 `[P1]`).
2. **Its refusal passes §30 term 4's bar** (§5.3) — (d) refuses exactly the input the operator
   authored, at the earliest seam at which the operator still holds the mistake, while leaving the
   position-only crash-reconstruction location INERT, the adjudicated correct state rather than a
   livelock with good manners. `[HIGH]` **This is NOT a margin over B** *(corrected at round 3
   `[P2]`; an earlier draft added "and B's natural refusal does not", which is stale once B is fixed
   as input-keyed — B's refusal passes term 4 by this filing's own test)*. It is recorded because it
   is the constraint that fixes **both** readings' refusal shape.
3. **It costs the closed §30 battery nothing.** Twelve fail classes stay twelve. B mints a
   thirteenth into a table the `B-69` leg deliberately closed at one new class.
4. **Its enforcement point is sound — and so, per round 2, is B's.** `[MODERATE]` `api.py` and
   `mcp_server.py` are bypassable by a direct `execute_workflow` caller, and the six per-consult
   guards are bounded by an enumeration the row's binding rule forbids relying on — but **B's
   input-keyed driver-entry check is sound with no discriminator and no order-dependence** (§4,
   round 2 [P1]). *(An earlier draft of this item claimed B's placement needed a grounded
   outer/inner discriminator; that was true only of a location-keyed check, and is **withdrawn**.)*
   **This item is therefore NOT a margin for A.** It is recorded because round 1 established the
   principle both readings now obey: a composition-time constraint is not an enforcement point.
5. **It is strictly MORE live, not less** (§4 Reading A) — neutral in the lone-empty-key case,
   strictly more live in the mixed case. The liveness cost an earlier draft of the row asserted was
   falsified at that row's review round 4 and is not re-asserted here.
6. **C's slice is subsumed by it.** `[HIGH]` Under A, `_resolve_effect_fence_gated(ctx, "", …)`
   returns `None` at every site by (e), so the level-local `any()` can never count a `""` entry and
   the filter becomes **behaviourally redundant**. *(Note this subsumption is (e)'s, not (a)+(d)'s —
   round 1's bypasses mean the two-part draft would NOT have subsumed C.)* Shipping C first
   therefore buys interim safety at the price of a `v1.111` §2.1(b) reconciliation that A makes
   moot — **a real trade, and the operator's to make** (§8 row C).

**THE MARGIN IS THIN, AND THE DISCRIMINATOR IS NAMEABLE** *(stated at round 2, which materially
re-priced B)*. `[MODERATE]` After round 2, A and B **both** close the criterion and **both** enforce
at consumption. What separates them is a single question the operator can answer directly:

> **Fix the SCALAR CLASSIFICATION, or stop the harm at the door?**
>
> **A fixes the scalar classification** — the CP contract and the code agree that an empty key is
> not a member of the unaddressed/eligible set, so the mixed case becomes **more live** and the
> membership rule lives in exactly one place (`v1.112` §2.4's own discipline). Its map channel is a
> refusal, not a removal, so A is a **hybrid** (clause (i) scalar + clause (ii) map). It pays with a
> **moved pinned rule** (b80 `:254`), a **`ResumeContext` narrowing against a PRESERVED-VERBATIM
> guarantee** (key domain **and** immutability), and a **`B-101` coupling**.
>
> **B stops the harm at the door** — an input-keyed refusal at the driver entry, clause (ii) on both
> channels, with **no type change, no pinned-rule move, no byte-compat argument and no `B-101`
> coupling**. It pays with a **thirteenth fail class** in a battery the `B-69` leg deliberately
> closed, leaves the classification saying one thing while the door says another (no liveness gain),
> and — per round 3 — must **snapshot or freeze the map at entry**, which is (6-i) or (e) by another
> name.

**A is recommended on the strength of items 1, 3 and 5** — the scalar classification fixed at its
one authority, the §30 battery left closed, and the mixed-case liveness gain. **An operator who
weighs the smaller blast radius (no pinned-rule move, no PRESERVED-VERBATIM narrowing) above those
should take B, and this filing does not argue that choice is wrong.** `[MODERATE]`

**The costs A carries, stated rather than discounted:**

- **The b80 pinned-test flip** (`:254`, `is False` → `is True`). It is the *expected consequence* of
  a ratified membership amendment, and the spec leg must state it as a decision.
- **The PRESERVED-VERBATIM collision** on `ResumeContext.effect_fence_resolutions`
  (`Spec_Control_Plane_v1_112.md` §0.4 `:38`). (d) owes its own byte-compat argument. This is
  **`B-101`(a)'s obstacle** (`v1.114` §0.5 finding (v), `:61`) — a **joint discharge is worth
  pricing**, and must be **determined at the spec leg, not assumed**. The rows stay separate.
- **No runtime diagnostic** for the crash-reconstruction empty key. A tells the operator nothing
  beyond the INERT re-pause. That is correct-but-silent, and it is the one thing B buys.
- **(6-i) is mandatory, not optional** (§4) — the field is narrowed on two axes, and any caller that
  mutates the map after constructing it changes behaviour.

**Runner-up: Reading B (an INPUT-KEYED refusal at the `execute_workflow` driver entry).** `[HIGH]`
**Rounds 1 and 2 both strengthened B relative to A, and this filing records that rather than burying
it:** B validates after construction, so it catches the pre-entry mutation round 1 found; and round 2
established that its input-keyed form needs **no root discriminator, no tree walk, and inherits no
order-dependence**. It is a **fully defensible ratification**. **Why still runner-up:** it refuses
rather than removes on the scalar channel too, so the classification stays as-is — `""` keeps its
slot in the unaddressed count (no mixed-case liveness gain), and `v1.112` §2.1's *"the walk includes
the empty key"* stays true alongside a door that refuses it — and it mints a **thirteenth** fail
class into a battery the `B-69` leg deliberately closed at one.

**If B is ratified, FOUR terms are mandatory:** the refusal **MUST** key on operator input (not on a
location — §30 term 4); the placement **MUST** be the driver entry, applied at **root and
recursive** invocations alike; the entry **MUST** snapshot or freeze the resolution map (or move the
check to the point of consumption) to close the post-check mutation window round 3 found; and the
leg **MUST** state that the CP classification is deliberately unchanged, so a later session does not
read the untouched membership rule as an omission.

**Reading C is not recommended as a closure** — the criterion's *"Partial is non-closure"* is
explicit — **but it is a defensible interim** if the operator wants the over-application harm gone
before the spec legs land. **Reading D is not recommended**, but is not unreasonable if the
operator's judgment is that a defensive-only LINEAR key plus a type-level-only orchestrator exposure
does not justify two spec legs — in which case the honest form is the criterion standing on the
record, which it already does.

### §6.1 The threat-model boundary — stated honestly, and against interest `[HIGH]`

*(Added at round 4, which pressed a `[P1]` arguing that a `{"": ABORT}` reaching the consults via
`model_construct` is a surviving clause-(a) silent drop and therefore makes A harm reduction rather
than closure. **The scope half is ACCEPTED and applied above; the prescription — add a
consumption-time refusal — is DECLINED, on three grounds recorded here rather than absorbed.**)*

**No disposition in this filing defends against an instance that declines to honour its own declared
type contract.** Pydantic's `model_construct` skips validation **by design**, for every model in
this workspace. A criterion under which a type constraint only "closes" if it also survives
`model_construct` is a **universal solvent**: it would equally unmake `RuntimeConfig.tenant_id`'s
validator, `PauseSnapshot`'s schema, and every detect-then-refuse guard in the tree — none of which
has ever been held to that bar. **A finding that proves that much is not a finding about this
disposition.**

**What the criterion actually scopes.** It closes *"on EVERY channel and EVERY carrier"* — the MAP
channel, the SCALAR channel, and the three effect-fence carriers. A forged instance is **neither**.
The in-house precedent is `B-97`(a) §3(iii), which made exactly this move against its own interest:
*"An adversary who can write the journal directory does not need to relocate a record — they can
author one … There is no authentication to defeat."* That filing booked the threat as **out of
scope and said so**, rather than claiming a defence it did not have. This one does the same.

**What IS therefore claimed, precisely:** under **A with (6-i)**, `{"": …}` cannot be constructed,
cannot be mutated in, and — if forged anyway — **cannot be honoured, and cannot alter another
location's decision**. **What is NOT claimed:** that a forged context receives a diagnostic. The
spec leg should state this boundary as a contract term, so a later arc reads it as a **ruling**
rather than an omission. **Reading B carries the identical boundary** — a forged context reaching an
entry check that reads the same forged field is refused only if the check re-derives what the type
already declared — so this is **not a discriminator between the readings.**

---

## §7 Council position — **PROBE-RESOLVED for every reading; NO convening is owed** `[MODERATE]`

The row's `council:` field is **CONDITIONAL**: a dyadic **C9 (reliability — a silent INERT re-pause
is an undiagnosable livelock) ⊥ C11 (operator loop — actionability)** is owed *"at the arc that
opens (c)"*, with **probe-first** applying: *"if a direct read of the §30 refusal battery settles
whether an empty-key refusal is operator-actionable, record it as probe-resolved rather than
convening."*

**The probe was run at this filing** (a direct read of §30, `:3398` term 4 plus the 12-row battery at
`:3421`–`:3432`) **and it SETTLES the question, by splitting it on the key's ORIGIN** (§5.3): a
refusal on operator-authored input is actionable and passes term 4; a refusal on the
crash-reconstruction location is not and fails it. **Recorded as `surfaced + probe-resolved`.**

**The convening is NOT owed under B either** *(corrected at round 3 `[P2]`; an earlier draft of this
section kept a B-specific convening on the books)*. `[HIGH]` That draft's stated question for the
voices — *should the refusal fire on the location or only on operator input?* — is **no longer live
under B**, because §4/§6 now make input-keying a **mandatory term** of B on the strength of the same
probe. Keeping the gate would have blocked the ratification leg on a question already answered,
which is exactly what the probe-first discipline (`CLAUDE.md` §10.9 amendment 5) exists to prevent.
**No convening is owed under A, B, C or D.**

**The one residual the probe leaves, recorded so it is not mistaken for an open council question.**
`[MODERATE]` Under **every** reading, a crash-reconstruction empty-key location re-pauses **INERT
with no diagnostic** — the operator is told nothing about a location they cannot address anyway.
C9's diagnosability instinct is not wrong to notice it; term 4 is simply the ruling that a signal
the operator cannot act on is not worth raising **on the resume path**. If a later arc wants that
visibility, its natural home is an **operator-only inspection surface** (the `B-97`(a) §5.3.1(iii)
precedent), which is a **different row**, not this one. It is **out of `B-107`'s scope by the
criterion's own terms** — a location with nothing addressed to it is neither dropped, nor honoured,
nor altering another decision.

---

## §8 The ratification ask — ONE decision

> **B-107 — which seam closes the empty-fence-key gap: a hybrid that removes the empty key from the
> scalar classification and refuses it on the map, an input-keyed refusal at the resume seam, the
> bounded over-application slice alone, or defer?**

| Option | Channels closed | Spec legs owed | New §30 fail class | b80 `:254` | `ResumeContext` type | Council |
|---|---|---|---|---|---|---|
| **(A) RECOMMENDED — a HYBRID: (a) scalar REMOVAL + (d) map REFUSAL + (e) resolver-boundary enforcement, with (6-i) mandatory** | **SCALAR by removal (clause i)**; **MAP by construction-time refusal (clause ii)**; over-application closed by **(e)**. Boundary at §6.1 | **ONE CP leg** — §1.1 membership amendment + the key-domain constraint **+ the validated immutable mapping (6-i)** (with a **`B-101`(a) joint-discharge determination**) + **the resolver-boundary removal (e) as a contract term** | **none** | **FLIPS** to `is True` — stated as a ratified consequence | **narrowed on TWO axes** — min-length-1 keys **and** an immutable validate-and-copy mapping; owes ONE byte-compat argument against §0.4 covering both, and is behaviour-visible to any caller that mutates the map | **probe-resolved**, no convening |
| (B) RUNNER-UP — (c) INPUT-KEYED refusal at the DRIVER ENTRY | both, by refusal (clause (ii)); classification **unchanged** | **ONE Runtime leg** (+ CP coordination) — new fail class + detect-then-refuse invariant + the input-keyed driver-entry placement + **an entry-time snapshot/freeze of the map** + a stated *"classification deliberately unchanged"* determination | **yes (13th)** | unchanged | unchanged | **probe-resolved**, no convening |
| (C) the bounded slice alone | **neither** — over-application only | ONE CP leg — the `v1.111` §2.1(b) reconciliation (§3(iii)'s premise correction) | none | unchanged | unchanged | not owed |
| (D) defer | none | none | none | unchanged | unchanged | not owed |

**What ratifying (A) commits to, in one line:** the empty key leaves the **scalar classification**
by amendment, an operator who **addresses** one is **refused at construction**, the map field
becomes an **immutable validated copy**, and `_resolve_effect_fence_gated` **treats an empty key as
unresolvable** — with the forged-instance boundary at **§6.1** stated as a ruling.

**Sub-decisions a ratification of (A) also ratifies**, each argued at §4–§6 and any one overridable
in the answer without changing the reading:

1. **The b80 flip is accepted as a ratified consequence** of the membership amendment (§1, §4).
2. **The `B-101`(a) joint discharge is DETERMINED at the spec leg, not assumed** — and the rows stay
   **SEPARATE** (`v1.114` §0.5(v)).
3. **C's slice is NOT shipped separately** — it is behaviourally subsumed by A (§6 item 6). *(Choose
   otherwise and the interim leg owes the `v1.111` §2.1(b) reconciliation that A would moot.)*
4. **INERT stays the posture for the crash-reconstruction location**; the only refusal raised is the
   type-boundary one on operator-authored input (§5.3).
5. **The witness grid is EIGHT cells** (2 channels × 4 carrier-sites), branch cells exercised
   **alongside a keyed sibling** and in **both carrier orders**; the two orchestrator cells
   **constructed-snapshot** (§5.4).
6. **(6-i) — the field takes a VALIDATED IMMUTABLE MAPPING** (validate-and-**copy**, not a view over
   caller-held state), closing the post-construction-mutation route. *(§4. **This is required for A
   to be a closure at all**: choosing (6-ii) instead leaves clause (a) alive on that route, so A
   becomes harm reduction and **`B-107` stays OPEN** — a legitimate choice, but not a close. Round 2
   [P1] withdrew the round-1 recommendation of (6-ii) for exactly this reason.)*
7. **The enforcement point (e) is a CONTRACT TERM, not impl discretion.** *(§5.2. Left to the impl
   leg it would be a convention the next arc can quietly move — and it is the term (a) and (d) both
   rely on.)*
8. **The §6.1 threat-model boundary is stated as a RULING** — no disposition defends against a
   context forged past its own declared type contract; what is guaranteed for such an instance is
   that it is **inert**, not that it is diagnosed. *(§6.1. The boundary is identical under B, so it
   is not a reason to prefer one reading over the other.)*

*(The ask is put to the operator by the orchestrating session via `AskUserQuestion` per `CLAUDE.md`
§14.2 — this filing does not run it.)*

---

## §9 Sequencing, and what each leg owes

**Leg 1 — this filing (doc-only PR).** No `design-substrate/**` edit; **no register flip**; no
`roadmap_status.md` touch. The `B-107` row's `pr:` pointer and any status change ride the
ratification leg. *(Scoping decision by standing instruction, not a guard requirement —
`.harness/forward-register.yaml` is not a `DESIGN_IMPL_MIX` surface.)*

**Leg 2 — operator ratification.** `AskUserQuestion` on §8. Outcome recorded as a `## §11
RATIFICATION` section appended to **this file** (the `B-92`/`B-97`(a) precedent), plus the register
row's `close_out`. Leg 2's **first action** is the register-row update (this filing's PR pointer +
the ratified disposition). **Leg 2 is a SINGLE ask under every reading** — no council convening is
owed (§7, probe-resolved), so there is no gate 2 and leg 3 opens directly on the answer.

**Leg 3 — spec leg(s).** Under the recommended Reading A, **ONE CP leg**, owing:

1. **`Spec_Control_Plane_v1_107.md` §1.1's membership term amended** so an empty captured key is
   **excluded** from the unaddressed effect-fence-pause set — the classification rule itself, which
   `v1.112` §2.4 (`:149`) confirms only §1 may state.
2. **The `ResumeContext.effect_fence_resolutions` key-domain constraint**, with its **byte-compat
   argument against `Spec_Control_Plane_v1_112.md` §0.4's PRESERVED-VERBATIM guarantee** (`:38`)
   stated explicitly, and the **`B-101`(a) joint-discharge question DETERMINED** (`v1.114` §0.5(v),
   `:61`) — the rows stay separate either way. **Plus §8 sub-decision 6: the validated immutable
   mapping (validate-and-copy), which is what makes clause (a) closed rather than merely reduced.**
2-bis. **The RESOLVER-BOUNDARY removal (e) stated as a CONTRACT TERM** — an empty `idempotency_key`
   is unresolvable at every consult, ahead of both the map-hit and the eligibility branch. **This is
   the leg's enforcement point** and the reason (a) and (d) hold against a direct caller; leaving it
   to impl discretion would reduce the closure to a convention (round 1 [P1] ×2).
2-ter. **A determination on the SECOND authority for the eligibility signal.**
   `effect_fence_uniform_fallback_eligible_key` reaches the resolver from **two** producers — the
   filtered helper and the public `execute_workflow` keyword (`:3074`). The leg must state that the
   parameter is caller-supplied and NOT a second classification authority, with (e) as the guarantee
   that a caller-supplied `""` is inert. *(An arc that amends only the helper leaves the parameter
   as an unstated second authority — the drift shape `v1.112` §2.4 exists to prevent.)*
3. **The b80 pinned-test flip stated as a DECISION**, with the amended rule's new pinned behaviour
   named, so the impl leg's test change reads as ratified rather than as drift.
4. **A stated determination that NO §30 delta is owed** — the 12-row battery and the cause
   vocabulary are unchanged under A. State it as a decision, not an omission (the `B-97`(a)
   precedent for a not-owed vocabulary change).
5. **A stated determination on the subclass surface**: whether the key-domain constraint binds
   `AccessorDerivedResumeContext` and any other `ResumeContext` subclass by inheritance —
   **determined, not assumed**, given `v1.114` §1.1's base-typed-carrier findings.
6. **Plan delta** — a CP plan unit (a new `U-CP-*` or an amended AC on the existing effect-fence
   unit), carrying the **eight-cell witness grid** + the mutation probe (§5.4).
7. **CXA** — expected classification-only, no new §2.3 row (CP-internal computation + a CP-owned
   type). To be **determined, not assumed**.
8. **Clearance markers** per `CLAUDE.md` §4.5, and a pre-merge adversarial-review pass per §10.9.

**Under Reading B**, leg 3 is instead a **Runtime** leg owing: the new §30 fail class + its taxonomy
row; the detect-then-refuse invariant; the **input-keyed driver-entry** placement as a contract term,
applied at **root and recursive** invocations alike; **an entry-time snapshot/freeze of the
resolution map** (or an equivalent consumption-point check) closing the post-check mutation window
round 3 found; the term-4 actionability argument binding the refusal to operator **input** rather
than to a location; a stated determination that the **CP classification is deliberately unchanged**
(so the untouched membership rule reads as a decision); plus CP-side coordination if the check reads
CP-owned classification. *(It owes **no** ruling on `sub_agent_descent` — round 2 established the
input-keyed shape needs no root discriminator.)*

**Under Reading C**, leg 3 is a narrow CP leg carrying only the `v1.111` §2.1(b) reconciliation
(framed per §3(iii) as a **premise correction**), and **the row does NOT close** — the criterion's
*"Partial is non-closure"* holds.

**Leg 4 — impl leg.** Under Reading A: the empty-key guard at the top of
`_resolve_effect_fence_gated` (`:2973`, ahead of `:3000`–`:3001`) — **the enforcement point**; the
`if k` filter in `compute_effect_fence_uniform_fallback_eligible_key`'s candidate comprehension
(`:2965`–`:2967`, mirroring `:3053`); the key-domain constraint on the `ResumeContext` field
(`pause_resume_protocol_types.py:1079`); the b80 test's pinned assert updated to the ratified rule;
and the eight-cell witness grid + mutation probe. **Three witnesses beyond the grid, each pinning
one verified bypass** *(the first re-specified at round 3 `[P2]`, which caught it contradicting
(6-i))*:

- **(6-i)'s witness** — `c.effect_fence_resolutions[""] = ABORT` on a constructed context **RAISES**
  (the mapping is immutable), and constructing with a `""` key raises `ValidationError`. *(An
  earlier draft asserted the assignment "reaches the consults and is inert", which is exactly what
  (6-i) makes impossible.)*
- **(e)'s witness — DEFENCE-IN-DEPTH, explicitly OUTSIDE the closure criterion** *(scope stated at
  round 4 `[P1]`, partially declined — see §6.1)*. A context carrying `{"": ABORT}` built by a route
  that **bypasses validation** (`model_construct`, or a replay of bytes serialized before the
  constraint) reaches the consults and is **inert**: no directive threaded, and a keyed sibling's
  `ABORT_BRANCH`/`SKIP_AS_FIRED` directive **survives** at `:8238`/`:12576`. **This witness asserts
  a defence-in-depth property, NOT a criterion clause** — a forged instance is not a channel or a
  carrier (§6.1). It is the witness that fails if (e) is later dropped as "redundant", which is why
  it is owed.
- **(a)'s second-authority witness** — a direct `execute_workflow(...,
  effect_fence_uniform_fallback_eligible_key="")` call threads **no** directive at an empty-key
  location.

**The row's BINDING RULE applies to every leg, and is restated here so it is not lost:** *every site
that reads a fence key off a resume carrier or off `resume_context`, on any path, is in this row's
scope whether or not it is named* — the seven-site map and the two terminal consumption sites are the
**inventory as of this HEAD**, not the definition. **The leg that opens B-107 MUST re-derive the site
set programmatically** from the carriers and from `resume_context`'s two fence surfaces before
finalizing; a disposition validated against this filing's list alone is unsound by construction.

---

## §10 Cite re-verification at HEAD `abf2593f`, and review record

**Every cite carried from the register row's `c1afb225` grounding re-resolved at this HEAD. NO
anchor moved.** Two observations that are cite-*shape* notes rather than staleness:

| Cite | As carried by the row | At HEAD `abf2593f` |
|---|---|---|
| The seven-site map's entries `:8216` / `:12118` / `:12554` | presented alongside call lines `:3056`/`:4926`/`:7839`/`:11708` | **Resolve — but they are GUARD lines, not call lines.** The calls are at `:8213`/`:12113`/`:12551`. Recorded at §3(i) so a later session does not read a guard cite as a call cite |
| *"CP spec v1.112 §2.1 states it outright"* (the walk-includes-the-empty-key sentence) | attributed to `v1.112` §2.1 | **VERIFIED CORRECT** — the sentence is at `Spec_Control_Plane_v1_112.md:111`, which falls inside §2.1 (`:97`–`:134`). It is **restated** at `Spec_Control_Plane_v1_113.md:85` and at `Spec_Harness_Runtime_v1.md:3503`; the `v1.112` attribution is the right one |

**Cites verified unmoved (direct read at this HEAD):**

- `Spec_Control_Plane_v1_107.md` §1.1 membership `:22`; §1.1(a) cross-location-misattribution `:30`.
- `Spec_Control_Plane_v1_111.md` §2.1(b) *"a strict widening … never a narrowing"* `:54`.
- `Spec_Control_Plane_v1_112.md` §2.1 empty-key sentence `:111`; §2.4 *"§2 publishes; it does not
  decide"* `:149`; §0.4 `ResumeContext` response fields **PRESERVED VERBATIM** `:38`.
- `Spec_Control_Plane_v1_113.md` §1.2 *"position-only …, which the resume path cannot address"* `:95`.
- `Spec_Control_Plane_v1_114.md` §0.5 finding (v) — `B-107`(d) and `B-101`(a) share the obstacle,
  rows stay **SEPARATE** — `:61` (§0.5 spans `:51`–`:64`).
- `Spec_Harness_Runtime_v1.md` §30 term 4 *"a refusal the operator cannot act on is a livelock with
  good manners"* `:3398`; the failure-mode taxonomy `:3419`–`:3432`.
- `Implementation_Plan_Control_Plane_v2_48.md` AC #A11 `:53`;
  `Implementation_Plan_Harness_Runtime_v2_57.md` AC #16(a) `:78` — both naming `B-107` as the
  **registered** limit their ACs cannot close (`v2_48:36`, `v2_57:39`).
- `workflow_driver.py` — `:2935`–`:2970`, `:2973`, `:3000`–`:3001`, `:3040`–`:3050`, `:3053`,
  `:3061`–`:3076`, `:4074`, `:4926`, `:5456`, `:7791`–`:7795`, `:7838`–`:7842`, `:8213`–`:8216`,
  `:8238`, `:9625`, `:9752`, `:10280`, `:11655`–`:11659`, `:11707`–`:11711`, `:12113`–`:12118`,
  `:12376`–`:12381`, `:12551`–`:12554`, `:12576`, `:14024`, `:14149`, `:14639`; `sub_agent_descent`
  as the depth-0 discriminator at `:11033` (used at `:4990`/`:11046`/`:15141`).
- `runtime_tool_dispatcher.py:989`/`:1042`; `managed_agents_dispatch.py:300`; `api.py:823`;
  `mcp_server.py:378`–`:403`; `child_workflow_runner.py:261`.
- `test_workflow_driver_effect_fence_tree_wide_abort_b80.py:222`–`:257`, the `:254` `is False`
  assert.
- `pause_resume_protocol_types.py:1048` (`ConfigDict(extra="forbid", frozen=True)`) / `:1079`
  (`effect_fence_resolutions: dict[str, EffectFenceResolution] | None`).

**Empirical probe run at this filing** *(round 1 [P1] #1, verified rather than accepted on
reasoning)*: with `ResumeContext` rebuilt against `harness_cp.hitl_placement.HITLResult`, a
constructed `ResumeContext(effect_fence_resolutions={"ok": ABORT})` **ACCEPTS**
`c.effect_fence_resolutions[""] = ABORT` (the field's runtime type is a plain `dict`), while
reassigning the field itself raises `ValidationError`. **`frozen=True` does not freeze the nested
mapping** — the basis for §4's (e) and for §8 sub-decision 6.

**Programmatic recounts (not eyeballed):**

| Quantity | Count | Method |
|---|---|---|
| `_resolve_effect_fence_gated` **call sites** | **7** | 11 textual occurrences − 1 `def` (`:2973`) − 3 in comments (`:7809`/`:11674`/`:12538`) |
| Terminal `effect_fence_resolution.idempotency_key ==` match sites (non-test tree) | **2** | tree-wide grep over all six `harness-*/src` packages |
| `Spec_Harness_Runtime_v1.md` §30 fail-class **data** rows | **12** | table rows `:3419`–`:3432` minus header + separator |
| Effect-fence pause **carriers** | **3** | LINEAR / BRANCH / ORCHESTRATOR (per `v1.113` §1.2's row) |
| Witness grid cells | **8** | 2 channels × 4 carrier-sites (§5.4) |
| Readings put to the operator | **4** | §4 / §8 |

### §10.1 Out-of-family review — `just codex-review-uncommitted`

**Round 1 — 2 findings, both `[P1]`; both ACCEPTED, neither disputed, both VERIFIED EMPIRICALLY
before acceptance.** Both struck the **recommended** reading's mechanism:

| # | Finding | Disposition |
|---|---|---|
| [P1] | **(d) does not make `{"": …}` unrepresentable** — `frozen=True` (`pause_resume_protocol_types.py:1048`) blocks field reassignment, not nested mutation of the plain `dict` at `:1079`, and `resume()` accepts an already-constructed model without revalidation. A key-domain annotation validates at construction only | **ACCEPTED, empirically reproduced** (§10's probe: the item assignment succeeds; the field reassignment raises). Reading A gains part **(e)**, the resolver-boundary removal; the *"unrepresentable"* / *"non-bypassable by construction"* claims are **struck and replaced** with *"refused on the ordinary construction path"*; the surviving route is named as the §4 residual and carried to §8 sub-decision **6** |
| [P1] | **(a)'s helper filter is bypassed by a public parameter** — `effect_fence_uniform_fallback_eligible_key` is a keyword on the exported `execute_workflow` (`:3074`), so a direct caller supplies `""` without transiting the filtered helper, and `_resolve_effect_fence_gated`'s `== eligible_key` branch honours the scalar | **ACCEPTED, verified in the signature.** Neutralized by **(e)**; NEW spec-leg item **2-ter** requires the leg to state that the parameter is caller-supplied and **not a second classification authority** |

**What round 1 did NOT move.** The **recommendation is unchanged (Reading A)** — flip count **0**,
far below the `[[reviewer-oscillation-register-and-hold]]` cap of 3. Applying the PD-9
discriminators (Workflow v1.19 §7.5) on the record, since both findings struck the recommended
reading:

1. **INVALIDATE or NARROW the premise?** — **Narrow.** A's premise is *take the empty key out of the
   addressable set so nothing is delivered to it*. Both findings say the **siting** of that removal
   was wrong (composition-time, two bypasses), not that the removal is wrong. Same premise, corrected
   enforcement point → **apply, run one more round, then re-assess.**
2. **Is the finding stream about the decision surface or the obligation list?** — **Decision
   surface**, this round: (e) is a new part of the recommended disposition, not an additive
   downstream obligation. That is the signal the surface has **not** yet stabilised, which is why no
   exit is declared here.
3. **Did the findings favour a different reading?** — They favour the **principle** B embodies
   (enforce at consumption), and §6 records that B's relative position **strengthened**. They do not
   favour B's *refusal*, which still fails §30 term 4 for the production-reachable carrier and still
   inherits §3(ii)'s order-dependence. A adopts the principle without the refusal.

**Round 2 — 2 findings, both `[P1]`; both ACCEPTED, neither disputed.** One withdrew a round-1
sub-decision recommendation; the other materially **re-priced the runner-up**:

| # | Finding | Disposition |
|---|---|---|
| [P1] | **Do not ratify the mutation residual as a closure** — recommending (6-ii) while the criterion says *"Partial is non-closure"* lets `B-107` close with a known violating route | **ACCEPTED.** The (6-ii) recommendation is **WITHDRAWN**; **(6-i) — a validated immutable mapping — is now REQUIRED for A to close**, sharpened to **validate-and-COPY** (a view over caller-held state reintroduces the route through the caller's alias). (6-ii) survives only as *harm reduction with the row held OPEN*. §4, §6 item 1, §8 sub-decision 6, §9 leg-3 item 2 all updated |
| [P1] | **Re-evaluate B without the root discriminator** — once B keys on operator input (which §6 already requires), the check reads only `resume_context` and `effect_fence_uniform_fallback_eligible_key`, both parameters of **every** invocation, so it works at root and recursive entries alike with no tree walk; `sub_agent_descent` and §3(ii)'s order-dependence are **not** B's problems, and stating them biased the ratification | **ACCEPTED, verified in the signature** (`:3072`, `:3074`). §4's seam table row **replaced**; §5.2, §6 item 4 and the runner-up paragraph **corrected in place**; §9's B-leg drops the discriminator obligation. **NEW at §6: the margin is stated as THIN, with the decisive question named — *fix the classification, or stop the harm?*** |

**Recommendation-flip count after round 2: still ZERO** (Reading A throughout). One **sub-decision**
moved — (6-ii) → (6-i) — on a verified internal contradiction, not on reviewer preference. Well below
the `[[reviewer-oscillation-register-and-hold]]` cap of 3.

**PD-9 discriminators re-applied at round 2** (both findings again struck the recommended reading):

1. **INVALIDATE or NARROW?** — **Narrow, both.** Finding 1 corrected A's *closure condition* (which
   sub-decision is required), not its premise. Finding 2 corrected the *comparison* against B, not
   A's soundness. → **apply, run one more round, then re-assess.**
2. **Decision surface or obligation list?** — **Still the decision surface** (a required
   sub-decision moved; the runner-up's cost model changed). No exit is declared at round 2.
3. **Do the findings favour a different reading?** — Finding 2 **materially narrows A's margin**, and
   §6 now says so in the operator's own terms rather than absorbing it. It does **not** reverse the
   recommendation: A closes on clause (i) with the battery intact; B closes on clause (ii) with a
   thirteenth fail class and the classification untouched. Per
   `[[over-correction-away-from-mostly-right-baseline]]`, a narrowing that leaves the premise intact
   is not grounds to flip.

**Round 3 — 5 findings (1 × `[P1]`, 4 × `[P2]`); all 5 ACCEPTED, none disputed.** Four corrected
claims *about* the two readings; one found a real hazard in the runner-up:

| # | Finding | Disposition |
|---|---|---|
| [P1] | **B has a post-check mutation window** — the entry check validates the same mutable `dict` the resolver reads later, so a caller retaining its reference can re-introduce `{"": ABORT}` after the check passes | **ACCEPTED.** The *"immune to mutation"* claim is **STRUCK**. B gains a **fourth mandatory term**: snapshot/freeze the map at entry, or check at the point of consumption. Recorded with the observation that both options are (6-i) or (e) under another name — **neither reading escapes binding the invariant at consumption** |
| [P2] | **The mutation witness contradicts (6-i)** — under a validated immutable mapping the assignment must RAISE, so a witness demanding it "reach the consults and be inert" is unsatisfiable | **ACCEPTED.** Leg-4 witnesses split into **three**: (6-i)'s (the assignment raises), (e)'s (a validation-bypassing construction — `model_construct` — reaches the consults inert), and (a)'s second-authority witness |
| [P2] | **The term-4 claim against B is stale** — once B is input-keyed, its refusal passes term 4 by this filing's own §5.3 test; treating term 4 as an A-only advantage misprices the runner-up | **ACCEPTED.** §6 item 2's comparative clause **STRUCK**; term 4 is now recorded as the constraint that fixes **both** readings' refusal shape, not as a margin |
| [P2] | **A's map channel is a REFUSAL, not a removal** — calling both channels clause (i) conflicts with §5.1's own table and overstates the "clause (i) over clause (ii)" rationale | **ACCEPTED.** A is restated as a **HYBRID** — clause (i) on the SCALAR channel, clause (ii) on the MAP channel — at §6 item 1 and in the margin box, and the recommendation's rationale is re-grounded on the **scalar** classification rather than on a blanket clause-(i) claim |
| [P2] | **B's council gate is inconsistent with the probe** — the location-vs-input question is settled by §4/§6 making input-keying mandatory, so requiring a convening blocks the ratification leg on an answered question | **ACCEPTED.** §7 retitled: **probe-resolved for every reading, no convening owed**; §8's B row and §9's leg 2 updated (single ask, no gate 2). The one residual — no diagnostic for the crash-reconstruction location, common to **all** readings — is recorded at §7 as **out of `B-107`'s scope** with an operator-only inspection surface named as its natural (different-row) home |

**Recommendation-flip count after round 3: still ZERO.** The margin has been restated **three
times** and narrowed each time; the recommendation has not moved, and the two reasons carrying it
have been the same since round 0 (the scalar classification fixed at its one authority; the §30
battery left closed).

**PD-9 discriminators re-applied at round 3:**

1. **INVALIDATE or NARROW?** — The `[P1]` struck the **runner-up**, not the recommendation; the four
   `[P2]`s corrected **descriptions** of both readings. **No finding touched Reading A's soundness.**
2. **Decision surface or obligation list?** — **Mixed, trending to obligations.** One new mandatory
   term for B, one witness re-specification, three corrections to comparative text. The *set of
   readings* and the *recommendation* were untouched for the first time.
3. **Is this an arms race?** — Not yet: severity fell (2×`[P1]` → 2×`[P1]` → 1×`[P1]`, and that one
   against the runner-up), and every round has produced at least one **verified fact about HEAD**
   rather than a preference. **One more round, then exit if severity holds or falls.**

**Round 4 — 2 findings (1 × `[P1]`, 1 × `[P2]`); 1 ACCEPTED, 1 PARTIALLY ACCEPTED with the
divergence stated.** Severity fell for the third consecutive round:

| # | Finding | Disposition |
|---|---|---|
| [P1] | **Refuse validation-bypassed empty keys before calling A closed** — the round-3 `model_construct` witness expects `{"": ABORT}` to reach the consults and be inert, which is a surviving clause-(a) silent drop; either refuse at consumption or keep the row open under A | **PARTIALLY ACCEPTED — the SCOPE, not the prescription.** *Accepted:* the round-3 witness wrongly presented a validation-bypassing construction as a route whose handling is part of the closure; it is **re-scoped to defence-in-depth, explicitly outside the criterion**. *Declined:* adding a consumption-time refusal, on three grounds now recorded at **NEW §6.1** — (1) `model_construct` bypasses **every** declared contract in this tree, so the proposed bar is a universal solvent no disposition here has been held to; (2) the criterion scopes *channels and carriers*, and a forged instance is neither; (3) the in-house precedent is `B-97`(a) §3(iii), which booked an author-your-own-record adversary as out of scope **against its own interest**. The boundary is stated as a **ruling** the spec leg must carry, and it is noted that **B carries the identical boundary**, so it discriminates nothing |
| [P2] | **§8's A row misstates the ratified contract** — it said "removal by construction on both channels" and summarized the type change as min-length keys only, while §4–§6 make A a hybrid requiring the immutable mapping | **ACCEPTED.** §8's A row rewritten to name the hybrid (scalar removal / map refusal / resolver enforcement), the **two-axis** field narrowing with (6-i) called out as mandatory, and a plain-language *"what ratifying A commits to"* line added above the sub-decision list. NEW sub-decision **8** carries the §6.1 ruling |

### **SOUNDNESS EXIT — declared after round 4. This filing is CLOSED to further review rounds.**

**PD-9 non-convergence discriminators, applied on the record** (Workflow v1.19 §7.5):

1. **Did any round INVALIDATE the recommended reading's premise, or NARROW it?** — **Narrow, every
   time.** A's premise — *take the empty key out of the addressable set and enforce it at
   consumption* — survived all four rounds intact. Round 1 corrected its **enforcement siting**
   (adding (e)); round 2 corrected its **closure condition** ((6-ii) → (6-i)); round 3 corrected its
   **clause classification** (hybrid, not pure clause (i)); round 4 corrected the **scope of one
   witness**. Same premise, four sharpenings.
2. **Has the recommendation flipped?** — **ZERO times.** Reading A throughout, carried by the same
   two reasons from round 0: the scalar classification fixed at its one authority, and the §30
   battery left closed. Far below the `[[reviewer-oscillation-register-and-hold]]` cap of **3**, and
   the count is recorded here so a later session need not re-derive it.
3. **Decision surface, or obligation list?** — **Obligations, at round 4.** Both findings were about
   *how the disposition is described and scoped*, not about which disposition is right. That is the
   signal the decision surface has stabilised.
4. **Would the round-4 `[P1]`'s prescription invalidate the carrier's premise?** — **It would
   invalidate every type-level contract in the workspace**, which is the
   `[[non-convergent-adversarial-hardening-arms-race]]` shape: a bar that no shipped disposition has
   met, applied to one. **STOP** is the correct response, with the boundary stated (§6.1) rather
   than chased.

**The arc of severity is decisively downward** — 2×`[P1]` → 2×`[P1]` → 1×`[P1]` (against the
**runner-up**) → 1 partially-declined `[P1]` (a scope question) — and every surviving item is a
**spec-leg obligation this filing names**, not an unresolved question inside it. The
`[[over-correction-away-from-mostly-right-baseline]]` discipline cuts in the recommendation's favour:
the round-0 baseline named the right reading and the right two reasons; four rounds corrected its
mechanism and its self-description without moving either.

**Findings that WOULD reopen this filing:** a defect in Reading A's premise (removal at the
classification + enforcement at consumption); a defect in the (6-i) requirement or in §6.1's
boundary; a demonstration that B's four mandatory terms are unsatisfiable; or a cite that fails to
resolve at HEAD.

**Reversals and withdrawals are recorded in-body rather than silently applied**, per this filing's
own discipline: the *"unrepresentable / non-bypassable by construction"* claim (round 1), the (6-ii)
recommendation (round 2), the B-specific council gate, the term-4 comparative claim and the
blanket-clause-(i) framing (round 3), and the closure-scoped `model_construct` witness (round 4).
Each move followed a **verified factual correction**, not reviewer preference.

*(The exit criterion is **soundness, not reviewer silence**, per
`[[deferred-mechanism-spec-leg-exit-on-soundness]]`.)*
