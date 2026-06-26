# Adversarial Review — C-AS-01 §1 Four-Tier Sandbox-Isolation Tier-Set

**Artifact under review.** `design-substrate/Spec_Action_Surface_v1.md`, §1 C-AS-01 (lines 125–165).
**Scope.** Critical pass over the four-tier sandbox-isolation contract ahead of implementation. Adjacent §2 C-AS-02 (the `max()` composition formula, lines 169–241) is in-scope only where it composes against C-AS-01 surfaces.
**Verdict.** The contract is **buildable but should not be built against as-is.** It carries one structural naming defect that the contract itself hardens into an invariant (F1), one broken within-contract citation (F2), and a return-type that escapes its own declared enum (F4). These should be resolved before a unit lands against C-AS-01. The remaining findings are specification-grade clarity defects that will produce divergent implementations if left unaddressed.

---

## Findings

### F1 — [HIGH] Tier-3 / Tier-4 identifiers misname their own mechanism classes

`tier-3-microvm` (line 145) enumerates Docker, Podman, gVisor, and Kata — all **container-class** mechanisms. `tier-4-full-vm` (line 146) enumerates Firecracker, which is a **hardware-virt microVM**, not a full VM. The identifiers say the opposite of what each tier contains.

- The label `tier-3-microvm` is *partially* defensible: gVisor is a user-space kernel and Kata is microVM-backed, so "microvm" is not pure fiction. But the tier's own "Mechanism class" column reads "**container** isolation" / "Shared-kernel container," and the §9 deployment matrix (lines 574–576) consistently labels tier-3 `container`. The identifier and the mechanism-class column contradict each other inside the same contract.
- `tier-4-full-vm` containing Firecracker is straightforwardly wrong. Firecracker is the canonical microVM. Line 146's own label says "Tier 4 VM isolation" with mechanism "Hardware-virt microVM (Firecracker) OR full VM."
- This is not cosmetic. §1.2 (line 152) declares the identifiers **stable across tech swap** and names `sandbox.tier` a **structural attribute**. C-AS-14 line 1117 wires `sandbox.tier ∈ {tier-1-process, tier-2-container, tier-3-microvm, tier-4-full-vm}` into the OTel telemetry schema. The misnaming is therefore load-bearing across the observability surface and the §1.2 invariant *forecloses* the cheap fix.

**Impact.** Every operator and implementer reading `sandbox.tier=tier-3-microvm` in a telemetry stream will believe a microVM is in use when a Docker container is. For a security-isolation contract this is a correctness-of-meaning defect, not a style nit.

**Recommended resolution.** Rename to mechanism-honest identifiers (`tier-3-container` / `tier-4-microvm`, or decouple identifier from mechanism entirely) *before* the §1.2 stability invariant is treated as binding. If the names are genuinely locked by an upstream ADR-F4 commitment, that is a Class 1 fork — surface it; do not absorb the misnaming silently into implementation.

### F2 — [HIGH] Dangling within-contract citation: `§1.5.2` does not exist in C-AS-01

Line 143 (tier-1 capability column) and line 221 (C-AS-02 §2.3 lookup) both cite "**§1.5.2 policy override**." C-AS-01 contains only §1.1, §1.2, §1.3. There is no §1.4 and no §1.5, let alone §1.5.2.

- Line 221 partially self-corrects — it reads "per §1.5.2 **per C-AS-12**" — so the intended target is plausibly **C-AS-12 §12.2** (operator-policy override, lines 789–804) or **ADR-D2 v1.1 §1.5.2** (cited at line 604, 733).
- Line 143 has no such disambiguation. It cites a bare `§1.5.2` that resolves to nothing within the contract.

**Impact.** An implementer building the tier-1 capability rule cannot resolve the operator-tunability scope from C-AS-01 alone. Citation byte-exact discipline (CLAUDE.md I-1; Workflow §7.4.2) is violated.

**Recommended resolution.** Rewrite both references to the correct cross-contract anchor — `C-AS-12 §12.2` and/or `ADR-D2 v1.1 §1.5.2` — explicitly.

### F3 — [MODERATE] §1.3 "two rules force tier resolution" is an incomplete enumeration

§1.3 (line 158) states "**Two rules** force tier resolution" and tables exactly two forcing conditions (code-execution beta → tier-4; computer-use → tier-4). But the §2.3 `sandbox_tier_floor` lookup (lines 217–218) introduces two further forcing conditions:

- STDIO MCP transport → `max(tier-3-microvm, blast_radius_floor)` — a tier-3 floor regardless of declared blast-radius (corroborated at C-AS-10 line 644).
- Remote MCP, trust level 0 → `REFUSE` — a hard rejection at registration.

These are forcing conditions in the same sense as the two §1.3 rows. Either §1.3 is *not* the canonical forcing-rule surface (in which case "Two rules force…" overclaims and should say "two of the forcing conditions, see C-AS-02 §2.3 for the full set"), or §1.3 *is* canonical and is under-specified by two rows.

**Impact.** An implementer treating §1.3 as the complete forced-tier surface will omit the STDIO and refuse-remote floors. Ambiguity about which section owns the forcing-rule surface produces divergent implementations.

**Recommended resolution.** Make §1.3 either complete or explicitly partial with a forward pointer to C-AS-02 §2.3.

### F4 — [MODERATE] `REFUSE` is a return value that escapes the declared `SandboxTier` enum

C-AS-02 §2.1 (line 187) declares `SandboxTier ∈ {tier-1-process, tier-2-container, tier-3-microvm, tier-4-full-vm}` "per C-AS-01 §1.1." The §2.2 composition formula returns `SandboxTier`. But the §2.3 lookup table (line 218) maps "Remote MCP, trust level 0" to `REFUSE` — a sentinel that is *not* a member of `SandboxTier`.

`max(tier-1, ..., REFUSE, ...)` is not a well-typed expression: `REFUSE` has no position in the tier ordering. The contract calls `REFUSE` a "sentinel; harness rejects connection at MCP server registration," which implies the refusal is evaluated at registration time — a *different* point in the lifecycle than the per-call `sandbox_tier(...)` resolution. The signature and the table disagree about both type and evaluation site.

**Impact.** Direct implementation hazard. A Pydantic-typed `SandboxTier` (the committed stack uses Pydantic v2) will not admit `REFUSE`; the implementer must either widen the type unsoundly or invent an unspecified separate path.

**Recommended resolution.** Split refusal out of the tier-floor return type. Model it as a distinct `RegistrationDecision` (admit / refuse) evaluated at MCP-server registration, with the tier `max()` operating only over the 4-value enum for admitted servers. C-AS-01 §1.1 should note that the tier-set is closed at 4 and refusal is not a tier.

### F5 — [MODERATE] §1.2 tier-monotonicity claim is false for capability coverage

§1.2 line 154: "higher tiers structurally accommodate lower-tier operations (tier monotonicity per §1.1 escape-risk descending)."

This holds for **isolation strength** but not for **capability coverage**. The tier-4 cell is "ephemeral; **network-egress-restricted**" (lines 146, 163, 215). A tier-1 `read-only` operation whose semantics include an outbound HTTP fetch does *not* run unchanged inside a network-egress-restricted tier-4 sandbox — egress restriction removes a capability the lower tier had. Monotonicity of the *isolation lattice* is real; monotonicity of *operation accommodation* is not, and the contract asserts the latter.

**Impact.** An implementer relying on the stated monotonicity to "just promote any tool to a higher tier safely" will break network-dependent read-only tools when they land in egress-restricted tier-4.

**Recommended resolution.** Restate the invariant precisely: tiers are monotone in isolation strength; they are *not* monotone in capability surface. Network-egress restriction at tier-4 is a capability *subtraction* and must be called out as an exception to naive promotion.

### F6 — [MODERATE] Tier-3 escape-risk is heterogeneous; the tier-3/tier-4 boundary collapses on the Kata branch

The tier-3 row (line 145) lists escape risk as "**Docker medium / gVisor low / Kata very low**" — three different containment grades under a single tier identifier. Tier-4 (line 146) is "very low (hardware boundary)."

On the Kata branch, tier-3 escape risk is "very low" — equal to tier-4. The property that is supposed to *discriminate* tier-3 from tier-4 (containment grade) is not actually discriminating. The tier ID is simultaneously encoding two non-aligned things: a mechanism class *and* a containment grade, and the join between them is inconsistent (a "very low" containment mechanism sits in the tier whose nominal grade is weaker than tier-4).

**Impact.** Routing decisions that key on tier (e.g., "external-irreversible needs tier-4") are unsound if a tier-3 Kata deployment already delivers tier-4-grade containment, and conversely a tier-3 Docker deployment delivers materially weaker containment than the tier ID implies. The escape-risk column cannot be used as a contract guarantee.

**Recommended resolution.** Decide what the tier ordinal *means* — mechanism class or containment grade — and make the other a separate, queryable attribute. If Kata genuinely belongs at tier-4-grade containment, either move it or document explicitly that within-tier escape risk is mechanism-dependent and the tier ordinal is *not* a containment-grade guarantee.

### F7 — [LOW] Tier-1 escape-risk row carries an unbound conditional

Line 143: tier-1 escape risk is "**High if no language sandbox**." This is a conditional embedded in an enum row with nothing binding the conditional. Whether a language sandbox is present is left implicit; the contract gives no field, no policy, and no resolution rule for the "if."

**Impact.** Minor, but a specification-grade enum row should not carry an unresolved conditional. Two implementers will reasonably disagree on tier-1's actual escape risk.

**Recommended resolution.** Either bind the conditional (e.g., a `language_sandbox_present` flag on the tier-1 deployment binding, or a sub-row) or state the worst case unconditionally ("High") and note language-sandbox mitigation as a separate hardening attribute.

### F8 — [LOW] §1.3 "Deferred to implementation discretion" sits in tension with the §1.2 stability invariant

§1.3's closing note (line 165) defers "specific container-runtime selection within `tier-3-microvm` (Docker / Podman / containerd)" to implementation discretion. This is fine *as a deferral*, but it lands in a contract that just (§1.2) declared the tier identifier a stable structural attribute. The deferral and the invariant should be explicitly reconciled: the *tier* is stable, the *tech within tier* (`sandbox.tech`, line 1118) is swap-friendly. The contract states this elsewhere but not at the point of deferral, so §1.3 reads as if it is deferring something the contract just locked.

**Recommended resolution.** One clause at line 165: "deferral is at the `sandbox.tech` discriminator, not the `sandbox.tier` identifier; tier stability per §1.2 is unaffected."

---

## Cross-cutting observation — governance gap

§1.2's "Cardinality bound" (line 153) governs *adding* a fifth tier (Class-2 ADR-F4 revision) but is silent on *renaming* an existing tier. Given F1, a rename is the most likely near-term change to this contract, and there is no stated governance path for it. The cardinality bound should be extended to cover identifier renames — and, until then, F1's rename should be routed as an explicit ADR-F4 back-flow rather than absorbed.

## Summary table

| ID | Severity | One-line | Blocks build? |
|---|---|---|---|
| F1 | HIGH | tier-3/tier-4 identifiers misname their mechanism class; §1.2 hardens the error | Yes — resolve or route as ADR fork first |
| F2 | HIGH | `§1.5.2` cited at lines 143/221 does not exist in C-AS-01 | Yes — broken citation |
| F3 | MODERATE | §1.3 "two rules" omits STDIO + refuse-remote forcing conditions | Yes — under-specified surface |
| F4 | MODERATE | `REFUSE` escapes the declared `SandboxTier` enum / wrong eval site | Yes — direct typing hazard |
| F5 | MODERATE | §1.2 monotonicity claim false for capability coverage (egress restriction) | No — but will mislead |
| F6 | MODERATE | tier-3 escape-risk heterogeneous; tier-3/tier-4 boundary collapses on Kata | No — but unsound routing guarantees |
| F7 | LOW | tier-1 escape-risk row carries an unbound conditional | No |
| F8 | LOW | §1.3 deferral not reconciled with §1.2 stability invariant | No |

**Bottom line.** F1, F2, F3, and F4 should be cleared before any atomic unit is implemented against C-AS-01. F1 in particular may be a Class 1 back-flow (ADR-F4 revision) rather than an in-spec edit — do not absorb the tier-name inversion silently into implementation, since it propagates into the C-AS-14 telemetry schema and every downstream contract that reads `sandbox.tier`.
