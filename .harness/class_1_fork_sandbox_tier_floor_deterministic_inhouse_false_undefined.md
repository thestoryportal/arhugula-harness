# Class 1 Fork — `sandbox_tier_floor()` never reads `ToolMetadata.is_deterministic_inhouse`; the field is threaded end-to-end into production but discarded at the one place it's supposed to matter

**Status:** RATIFIED + CLOSED 2026-07-15 — Q1 resolved to **Reading A** (non-forcing, spec-text-only). Resolution process: per this fork's own §2 Q3 recommendation, a dyadic council convening (C10 action-safety/blast-radius + C4 tool-contract-semantics) ran before the operator decision — its decisive finding was that `is_deterministic_inhouse` carries zero verification mechanism today, so Reading B/C's floor bump would be trivially spoofable by the actor it targets while only penalizing honest tool authors who never opted into the field. Both voices converged on Reading A; the council's 4-option synthesis was presented to the operator via `AskUserQuestion`, who selected "Reading A + reserved annotation." Applied at `ADR-D2.md` v1.2 → v1.3 + `Spec_Action_Surface_v1.md` v1.13 → v1.14 (both carry clearance markers) + corrected stale docstrings at `tool_contract.py` / `types.py` / `sandbox_tier_floor.py` + a new mutation-probed witness test (`test_sandbox_tier_floor_read_only_ignores_is_deterministic_inhouse`) pinning the resolved behavior. **No code behavior change** — production code already implemented Reading A; this closes the documentation self-contradiction (at both the ADR and spec layers) and the stale-docstring drift. See `.harness/clearance/adr-d2-v1-3-cleared-2026-07-15.md` + `.harness/clearance/spec-action-surface-v1-14-cleared-2026-07-15.md` for the full resolution record.

**Filed at:** 2026-07-14

**Filer:** roadmap-continue no-parking sweep (post-#996 session; B-25 grounding)

**Surfaced by:** `.harness/harness-preflight-code-review-2026-07-12.md` Medium findings table; direct read of `harness-as/src/harness_as/sandbox_tier_floor.py` against `design-substrate/Spec_Action_Surface_v1.md` §2.3 + its own v1.10→v1.11 change-note.

**Classification:** Class 1 — not a local code bug fixable in place: the spec's own §2.3 table only defines row 7 for the `True` case, its "Row→argument keying" paragraph contradicts the change-note that introduced the field into `ToolMetadata`, and a real production default (`False`) reaches this code path today via every non-opted-in MCP server. Resolving `False`'s floor requires a spec-table amendment (new row or corrected keying language), not a local patch — a candidate floor value is a genuine design decision, not a mechanical fix.

---

## §1 — The gap

### §1.1 — The resolver never consults the field; both `True` and `False` currently resolve identically

`ToolMetadata` (`harness-as/src/harness_as/sandbox_tier_floor.py:46-56`):

```python
class ToolMetadata(BaseModel):
    """Tool-classification discriminators for the §2.3 lookup (Pattern B carrier).

    Carries the §2.3 row-1 / row-2 / row-7 discriminators.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    is_deterministic_inhouse: bool
    forces_computer_use: bool
    forces_code_execution: bool
```

The resolver (`sandbox_tier_floor.py:115-155`) body:

```python
def sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_server):
    if tool.forces_computer_use:
        return _resolved(SandboxTier.TIER_4_FULL_VM)
    if tool.forces_code_execution:
        return _resolved(SandboxTier.TIER_4_FULL_VM)
    floor = blast_radius_floor(blast_radius_tier)
    if mcp_transport is MCPTransport.STDIO:
        return _resolved(_tier_max(SandboxTier.TIER_3_MICROVM, floor))
    if mcp_server is not None:
        match mcp_server.trust_level:
            case MCPServerTrustLevel.L0_REFUSE_REMOTE: return REFUSE
            case MCPServerTrustLevel.L2_SANDBOX_ALL: return _resolved(_tier_max(SandboxTier.TIER_4_FULL_VM, floor))
            case MCPServerTrustLevel.L1_SIGNED_PINNED | MCPServerTrustLevel.L3_ALLOW_WITH_AUDIT: return _resolved(floor)
    return _resolved(floor)
```

`tool.is_deterministic_inhouse` is read **nowhere** in this body (confirmed by direct read + grep within the file). There is no "`True` branch does X, `False` branch is undefined" split in the code — both values currently fall through to the identical final `return _resolved(floor)` for a read-only tool. `harness-as/tests/test_sandbox_tier_floor.py:120-128` tests `is_deterministic_inhouse=True` + `READ_ONLY` → `TIER_1_PROCESS`, but there is no (and currently cannot be a meaningfully different) test for `is_deterministic_inhouse=False` producing a distinct tier.

### §1.2 — The field is a real, production-threaded default — not a dormant stub

Unlike a typical "declared but never wired" field, `is_deterministic_inhouse` is threaded end-to-end into production dispatch, with `False` as the **default for every tool/server that doesn't explicitly opt in**:

- `harness-as/src/harness_as/tool_contract.py:96-99` — `ToolContract.is_deterministic_inhouse: bool = False`, with a docstring claiming it *"keys the C-AS-02 §2.3 row-7 read-only-deterministic-in-house lookup (→ TIER_1_PROCESS, bounded below by the deployment-surface default + blast-radius floor)"* — a docstring that is currently **wrong**, since the lookup doesn't key on it at all.
- `harness-runtime/src/harness_runtime/config/sandbox_defaults.py:245` — the production per-tool resolver (`resolve_per_tool_sandbox_defaults`, runtime spec §14.9.11) explicitly threads `contract.is_deterministic_inhouse` into the `ToolMetadata` it constructs and passes to `sandbox_tier_floor(...)`, expecting the value to matter.
- `harness-runtime/src/harness_runtime/types.py:683-684` + `harness-runtime/src/harness_runtime/bootstrap/factories/mcp_client_host_factory.py:182` — an operator-declarable per-MCP-server default (`MCPClientConfig.default_is_deterministic_inhouse: bool = False`) exists, meaning `False` is the live, common-case value for every MCP server that doesn't set the opt-in flag — this is the majority case in production, not a corner case.

So this is not "an unused field nobody set" — it is "a field that IS set (mostly to its default `False`) at every real dispatch site, and is silently discarded at the one function that's documented to consume it."

### §1.3 — The spec itself is internally inconsistent about whether this field gates anything

`design-substrate/Spec_Action_Surface_v1.md` §2.3 (v1.13 HEAD) row 7, verbatim:

> `Read-only, deterministic in-house tool` → `tier-1-process` (operator-tunable at solo-developer × non-compliance cells per §1.5.2 per C-AS-12)

There is **no row** for "Read-only, NOT deterministic in-house." The same §2.3's "Row→argument keying" paragraph (line 480, present since v1.2) states: *"rows 7-10 are keyed on the `blast_radius_tier` argument"* — i.e., by this paragraph's literal claim, `is_deterministic_inhouse` is **not a keying input for row 7 at all**; "deterministic in-house" in row 7's condition text would be purely descriptive, with no gating effect, and both `True` and `False` should resolve to the same blast-radius-keyed floor (which is exactly what the code does today).

But the v1.10→v1.11 change-note (the same amendment that added `is_deterministic_inhouse` to `ToolContract`) frames the field very differently: *"the `ToolMetadata` forcing discriminators (`forces_computer_use` / `forces_code_execution` / `is_deterministic_inhouse` …) that key the §2.3 rows 1-2 … + row 7 (`is_deterministic_inhouse` read-only → `tier-1-process`) … row 7's `tier-1-process` is bounded below by the deployment-surface default + the per-tool `blast_radius_tier` floor"* — grouping `is_deterministic_inhouse` alongside `forces_computer_use`/`forces_code_execution` as a **forcing discriminator that keys row 7**, and describing the tier-1 floor as conditional on the field ("bounded below by ... when the flag is present"), implying the `False` case is NOT simply the unconditional blast-radius floor.

**These two spec passages disagree, and neither was amended when the other was written.** The "Row→argument keying" paragraph (present since v1.2, "PRESERVED VERBATIM" through every subsequent change-note) says row 7 doesn't key on `tool` at all; the v1.11 change-note that introduced the field's threading treats it as a row-7-keying forcing discriminator. The current code implements the "Row→argument keying" reading (ignores the field); the current `ToolContract` docstring + the runtime production threading assume the v1.11 change-note's reading (the field should matter). This is exactly the kind of drift the fork-doc mechanism exists to surface rather than silently resolve in either code or spec.

### §1.4 — Why this is a real (not cosmetic) risk

`False` (the production default for every non-opted-in MCP server) is currently treated identically to `True` (an operator's explicit "I've verified this tool is deterministic and locally-authored" assertion) for sandbox-tier purposes. If the intended design is that non-verified tools should receive a stricter floor than verified-deterministic ones (which the row-7 condition text's very existence, and the v1.11 change-note's "forcing discriminator" framing, both suggest), then every unverified read-only MCP tool today is silently receiving the SAME minimal `TIER_1_PROCESS` floor as an explicitly-verified one — a blast-radius under-provisioning gap for the common case, not the rare one.

### §1.5 — Addendum (2026-07-15): the self-contradiction is at the ADR layer too, not just spec-vs-change-note

Grounding pass (roadmap-continue autonomous session, B-24/B-25/B-27 ratification batch) checked whether a higher-authority source — `ADR-D2 v1.2` §1.5.1, the very "composition authority" this fork's own filing footer cites for `sandbox_tier_floor` — settles the tension in favor of one reading, per the canonical authority chain (`CLAUDE.md` §1.3: ADR → ADD → PRD → spec → plan; ADR wins on conflict).

It does not settle the tension. It reveals the **same contradiction exists inside ADR-D2 itself**, one layer earlier than this fork originally traced it:

`ADR-D2.md` §1.5.1's `where:` block (verbatim, line 176):

```
(read-only, *, deterministic in-house)    → Tier 1 (operator-tunable
                                                    at solo-developer)
```

This row's condition tuple has **three** elements — `read-only`, a wildcard, and `deterministic in-house` — unlike the surrounding rows 8-10 (`local-mutation, *`; `external-reversible, *`; `external-irreversible, *`), which have only two. The third element is doing real work in the row's own text: it names `is_deterministic_inhouse` as part of row 7's match condition.

But the very next paragraph — ADR-D2's own "Row→argument keying" prose (line 183) — states: *"rows 7–10 ... are keyed on the **`blast_radius_tier`** argument"*, with no carve-out for row 7's extra `deterministic in-house` qualifier. Read literally, this paragraph says row 7 does NOT key on `tool.is_deterministic_inhouse` at all — directly contradicting the `where:`-block row it is describing one paragraph above.

**This is not new information resolving the fork — it is the fork's own tension, now confirmed to originate at the ADR (not merely propagate from a later spec change-note as originally framed in §1.3).** The AS spec's v1.10→v1.11 change-note (§1.3 above) did not introduce a NEW misreading; it picked the `where:`-block's own literal row-7 text (which the change-note's author was presumably reading directly) over the keying paragraph's blanket claim — a defensible reading of the ADR as internally inconsistent, not an error. No clearance marker exists for ADR-D2 v1.2 disambiguating this (confirmed via `.harness/clearance/` — none filed; ADR-D2 v1.2 predates the 2026-05-29 marker-convention start date, so implicit clearance applies to the *version as authored*, contradiction included, per `CLAUDE.md` §4.5 retroactive scope — the implicit clearance does not itself resolve which of the two internally-conflicting passages is authoritative).

**Net effect on Q1/Q3:** the meta-question "does row 7 key on `tool` at all" now leans evidentially toward YES (readings B/C) — the `where:`-block condition tuple is the more specific, more clearly load-bearing text (an explicit third match element vs. a blanket summary paragraph that arguably just forgot to carve out row 7's own extra qualifier). But this is still an evidential lean on a genuinely ambiguous primary source, not a resolution — and even granting "row 7 keys on `tool`," the SPECIFIC floor value for `is_deterministic_inhouse=False` (Q1: A/no-change vs. B/one-tier-bump vs. C/forcing-Tier-4) remains undecided by either the ADR or the spec. That value is a live production sandbox-posture decision affecting every non-opted-in MCP server today (§1.4) — a blast-radius tradeoff with no reversible "try it and see" path once shipped to a non-coding operator who cannot independently audit which tools that decision silently re-tiers. **Resolution (2026-07-15, follow-on session).** This fork was NOT resolved unilaterally at filing time — it was registered as an explicit operator-gated tail per the standing no-unilateral-blast-radius-change discipline. It was subsequently resolved via the process this addendum itself anticipated (§2 Q3's council recommendation): a dyadic C10⊥C4 council convening ran three empirical probes and found `is_deterministic_inhouse` carries zero verification today, converging both voices on Reading A despite this addendum's own evidential lean toward B/C. The operator selected Reading A from the council's 4-option synthesis via `AskUserQuestion`. See the fork's top-of-file Status line + `.harness/clearance/adr-d2-v1-3-cleared-2026-07-15.md` for the full record — the evidential lean recorded in this paragraph is preserved as an accurate point-in-time record of what was known before the council's probes, not retroactively corrected.

---

## §2 — Proposed readings

**Q1 — What should `sandbox_tier_floor()` do when `is_deterministic_inhouse=False`?**

- **(A) Reconcile toward "non-forcing" (status quo, spec-text fix only)** — treat the "Row→argument keying" paragraph as canonical: `is_deterministic_inhouse` does NOT gate anything at row 7; row 7's condition text is corrected to just "Read-only, any" (dropping "deterministic in-house" as descriptive-only); the v1.11 change-note's "forcing discriminator" framing is acknowledged as an inaccurate description at the time it was written, corrected via a doc-hygiene note. **No code change** — `sandbox_tier_floor()` already implements this reading. Lowest blast radius; but does not resolve why the field exists at all if it never gates anything (arguably should be removed/deprecated from `ToolContract` + the runtime threading, a larger footprint than it first appears).
- **(B) Compound-condition, one-tier bump** — row 7 requires BOTH `blast_radius_tier == READ_ONLY` AND `is_deterministic_inhouse == True`; when `False`, bump the floor one tier above the blast-radius default (`TIER_2_CONTAINER` for a read-only-but-unverified tool). Mirrors the general C10 blast-radius-conservatism-toward-untrusted-inputs principle; requires a new explicit branch in `sandbox_tier_floor()` keyed on `(blast_radius_tier == READ_ONLY, tool.is_deterministic_inhouse)` + a new §2.3 table row + fixing the "Row→argument keying" paragraph to acknowledge row 7 is ALSO keyed on `tool`.
- **(C) Compound-condition, forcing-tier bump** — treat "not deterministic in-house" (i.e., a stochastic/LLM-mediated or externally-authored tool) as risk-equivalent to the existing rows 1-2 forcing conditions, and force `TIER_4_FULL_VM` regardless of blast-radius tier when `is_deterministic_inhouse == False`. Highest blast-radius-conservatism reading; would materially change sandbox behavior for every currently-non-opted-in MCP server in production (most of them, per §1.2) — the largest behavior-change candidate, and the one most likely to need an operator migration/communication plan if adopted.

**Filer recommendation:** Reading (B) is the filer's best-guess middle ground given the row-7 condition text's own wording ("deterministic in-house" reads as a genuine qualifier, not decoration) and the v1.11 change-note's explicit forcing-discriminator framing — but this is squarely the kind of blast-radius-vs-tool-contract-semantics tradeoff the register's own note flags as council-eligible (see Q3), not something the filer should decide unilaterally.

**Q2 — Scope of the amendment.**

- (a) Spec-table amendment (row 7 split or corrected keying language, per whichever Q1 reading) + `sandbox_tier_floor()` code change (if Q1=B or C) + updated `ToolContract`/`MCPClientConfig` docstrings (all readings, since the current `tool_contract.py:96-99` docstring is wrong regardless of which reading is chosen) + new/updated tests distinguishing `True` vs `False` outcomes.
- (b) Spec-only (Q1=A) — corrects the row-7 text + keying-paragraph consistency; no code change since current code already implements this reading; still needs the stale `ToolContract` docstring fixed as a companion code change.

**Q3 — Council eligibility.** Per the register's own note: *"⚖️ conditional — C10 blast-radius ⊥ C4 tool-contract semantics — nameable once the candidate floor value is proposed."* Now that Q1 proposes 3 concrete candidate values (A: no change / B: one-tier bump / C: forcing tier-4), the tension is nameable: **C10 (action-safety / blast-radius conservatism)** would favor B or C (don't trust unverified tools with the minimal floor); **C4 (tool-contract semantics / capability-introspection)** would favor A (the field's meaning should be decided by what `ToolContract`'s author actually asserts, and a `False` default shouldn't silently escalate isolation for every tool that simply didn't bother setting the flag — that penalizes contract authors who haven't opted in to a NEWER field, not ones who declared something risky). **Recommend a dyadic council convening (C10 + C4) before Q1 is ratified**, per workspace `CLAUDE.md` §10.9 nameable-tension discriminator + §13.4 worked-example precedent (the resolver Reading A-vs-B decision).

**Q4 — Cross-axis cascade.**

- (α) Q1=A → `design-substrate/Spec_Action_Surface_v1.md` §2.3 text-only correction + AS/CP-runtime docstring fixes. No `sandbox_tier_floor` signature change, no cross-axis touch (the function is AS-axis-owned, consumed read-only by the runtime resolver at `harness-runtime/src/harness_runtime/config/sandbox_defaults.py:245` — its call signature is unchanged under this reading).
- (β) Q1=B or C → AS spec §2.3 table amendment (new row / keying-paragraph correction) + `sandbox_tier_floor()` code change (AS-axis-internal, signature unchanged — only the function body branches differently) + no new cross-axis edge (the runtime resolver already threads `is_deterministic_inhouse` into `ToolMetadata` and calls `sandbox_tier_floor`; a body-only behavior change requires no new consumer wiring). Both readings are AS-axis-internal; zero CP / OD / IS / CXA / ADR / ADD / PRD touch.

---

## §3 — Filing footer

| Field | Value |
|---|---|
| Artifact | `class_1_fork_sandbox_tier_floor_deterministic_inhouse_false_undefined.md` |
| Status | PROPOSING |
| Filed at | 2026-07-14 |
| Authority anchors | `design-substrate/Spec_Action_Surface_v1.md` §2.3 (v1.13 HEAD; row 7 + "Row→argument keying" paragraph); v1.10→v1.11 change-note (introduces `is_deterministic_inhouse` threading into `ToolContract`, frames it as a row-7 forcing discriminator — in tension with the keying paragraph); ADR-D2 v1.2 §1.5.1 (`sandbox_tier_floor` composition authority) |
| Empirical anchors | `harness-as/src/harness_as/sandbox_tier_floor.py:46-56` (`ToolMetadata`), `:115-155` (resolver body, confirmed no read of `is_deterministic_inhouse`); `harness-as/tests/test_sandbox_tier_floor.py:120-128` (only `True` case tested); `harness-as/src/harness_as/tool_contract.py:96-99` (production default + stale docstring), `:191` (threading into registration); `harness-runtime/src/harness_runtime/config/sandbox_defaults.py:245` (production per-tool resolver threading); `harness-runtime/src/harness_runtime/types.py:683-684` + `harness-runtime/src/harness_runtime/bootstrap/factories/mcp_client_host_factory.py:182` (per-server operator default, `False` is the live common case) |
| Council eligibility | ⚖️ Recommended — C10 (blast-radius conservatism) vs C4 (tool-contract semantics), nameable per Q3 now that 3 candidate readings are proposed |
| Resolution path | Per workspace `CLAUDE.md` §4.3 Class 1 → route to Phase 5 spec revision-pass (AS spec §2.3) once Q1/Q3 are resolved (council convening recommended before operator AskUserQuestion, per `CLAUDE.md` §13.4); apply arc lands spec + code + test changes at a follow-on PR with a clearance marker |
| Cross-axis cascade | ZERO under every reading — AS-axis-internal; `sandbox_tier_floor`'s call signature is unchanged under all 3 Q1 readings |
| Registered at | `.harness/forward-register.yaml` id `B-25` / `.harness/post-phase-8-forward-register.md` §"B-25" |
