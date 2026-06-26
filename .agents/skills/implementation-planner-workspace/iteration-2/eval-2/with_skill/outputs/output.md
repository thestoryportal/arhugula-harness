# C-AS-05 §5 — `fetch_secret` Contract: Atomic Unit Decomposition

*Implementation-planning artifact. Decomposes a single specification contract (C-AS-05 §5, `Spec_Action_Surface_v1.md`) into atomic implementation units per the `implementation-planner` discipline. Not a full axis plan — a scoped per-contract decomposition. Status: Proposed.*

---

## Status block

| Field | Value |
|---|---|
| Status | Proposed (pre-P6-CK) |
| Scope | C-AS-05 §5 contract only — `fetch_secret(name, scope) -> SecretRef` |
| Source-set | `Spec_Action_Surface_v1.md` §5 (C-AS-05); cross-referenced: §2 (C-AS-02 sandbox-tier composition), §6 (C-AS-06 allowlist), §8 (C-AS-08 audit-ledger), §15 (C-AS-15 span emission); ADR-F5 v1.1; ADD v1.3; PRD v1.1 R-AS-04 |
| Entry authorization | Operator request — decompose C-AS-05 §5 into implementation units |
| Exit gate | P6-CK clearance (for the host axis plan into which these units integrate) |
| Axis | AS (Action Surface) |

---

## Shape decision

**Shape: dependency-graph-led**, scoped to one contract. C-AS-05 §5 decomposes along its own sub-section topology: §5.1+§5.4 form a foundational types layer; §5.2 splits into two mechanism families (C2 env-var injection / C3 in-sandbox HTTP fetch); a dispatcher unit composes the foundation with the resolved sandbox tier; §5.3 negative-observation invariant lands as a verification unit anchoring the "sole resolution path" property. Section boundaries follow the dependency-graph layers, not a per-tier or per-sub-section mechanical split. Grounded in `Spec_Action_Surface_v1.md` §5 structure (§5.1–§5.4).

---

## §1 Plan summary

C-AS-05 §5 (`Spec_Action_Surface_v1.md`) commits a single capability-aware secret-fetch abstraction — the `fetch_secret(name, scope) -> SecretRef` signature, an opaque `SecretRef` handle type, tier-aware resolution across the four C-AS-01 sandbox tiers, and a negative-observation invariant prohibiting secret content in prompts, logs, and the audit ledger. The contract honors ADR-F5 v1.1 and satisfies PRD R-AS-04 (fetch-abstraction half). This decomposition yields **five atomic units (U-AS-SEC-1 … U-AS-SEC-5)**: one foundational types unit (anchor), two mechanism-family units (process/container env-var injection; microVM/full-VM in-sandbox HTTP fetch), one dispatcher unit composing them by resolved sandbox tier, and one negative-observation-invariant verification unit. The foundational types unit anchors the dependency graph; all four other units depend on it directly or transitively. One open item is surfaced: the `SecretScope` type's structural shape is not committed at C-AS-05 (see §6).

---

## §2 Atomic units

### U-AS-SEC-1: `SecretRef` opaque type + `fetch_secret` signature surface

**Scope.** Author the `SecretRef` opaque handle type and the `fetch_secret(name, scope) -> SecretRef` function signature surface (declaration only — mechanism bodies land in later units). Establish the `SecretRef` opaque-type discipline: no value-returning API surface, sandbox-lifetime-bounded lifetime, release-on-sandbox-termination, no cross-sandbox sharing, fresh-on-restart (no in-process cache across restart boundaries).

**Spec linkage.** C-AS-05 §5.1 (function signature + parameter/return semantics); C-AS-05 §5.4 (`SecretRef` opaque-type discipline — opaque / lifetime-bounded / fresh-on-restart).

**Surfaces affected.** Secret-fetch type-definition module (the `SecretRef` handle type + the `fetch_secret` signature export). `SecretScope` is consumed as an existing/declared type — see §6 Open Items; this unit does not author `SecretScope`.

**Signatures introduced or modified.**
- `fetch_secret(name: string, scope: SecretScope) -> SecretRef` per C-AS-05 §5.1.
- `SecretRef` — opaque handle type per C-AS-05 §5.1 and §5.4; exposes no API surface returning the secret value as a string (§5.4 "Opaque").

**Depends on.** (none) — foundational anchor unit.

**Acceptance criterion (functional).** The `SecretRef` type is defined and exports no method or property that yields the resolved secret value as a string. The `fetch_secret` signature is declared with `name: string` and `scope: SecretScope` parameters and a `SecretRef` return type. A test asserting `SecretRef` has no value-getter, and a test asserting `SecretRef` instances are not shareable across two distinct sandbox identities (raise / reject on cross-sandbox use), both pass.

**Notes.** `SecretRef` value access is tier-mechanism-specific (env-var read at process/container; in-sandbox HTTP at microVM/full-VM) — the mechanism resolution is U-AS-SEC-2 / U-AS-SEC-3 scope, not this unit. This unit fixes only that no *generic* value-getter exists on the type.

---

### U-AS-SEC-2: Process / container tier resolution — env-var injection mechanism

**Scope.** Implement the C2-pole resolution mechanism for `tier-1-process` and `tier-2-container`: secret values delivered into the sandboxed process via environment variables at sandbox/container startup (the within-turn-snapshot pattern). `SecretRef` value access at these tiers reads the injected environment variable.

**Spec linkage.** C-AS-05 §5.2 (tier-aware resolution table — `tier-1-process` and `tier-2-container` rows; C2 within-turn-snapshot pole).

**Surfaces affected.** Process/container-tier secret-resolution module (env-var injection at startup; tier-local `SecretRef` value-access mechanism).

**Signatures introduced or modified.** No new public signature — implements the tier-1/tier-2 branch of `SecretRef` value access per C-AS-05 §5.2. Internal env-var injection + read functions at logical level (keyring-backed local secret store at the process/container tiers).

**Depends on.** [U-AS-SEC-1].

**Acceptance criterion (functional).** Given a secret resolved for a `tier-1-process` or `tier-2-container` sandbox, the value is delivered via an environment variable present at process/container startup, and tier-local `SecretRef` access reads that variable. A test confirming the value is captured as a within-turn snapshot (no across-turn re-fetch path is invoked at these tiers) passes.

**Notes.** Long-lived agent-process-with-keyring-handles pattern applies at `tier-2-container` per C-AS-05 §5.2 (ADR-F5 v1.1 §Rationale (b)(i)). The specific keyring-library binding is deferred per the C-AS-05 §"Deferred to implementation discretion" clause — kept at logical surface here.

---

### U-AS-SEC-3: microVM / full-VM tier resolution — in-sandbox HTTP fetch mechanism

**Scope.** Implement the C3-pole resolution mechanism for `tier-3-microvm` and `tier-4-full-vm`: an in-sandbox HTTP client fetches secret values over the network using a sandbox-identity bootstrap token bounded by sandbox lifetime (the across-turn fresh-fetch pattern). `tier-4-full-vm` additionally supports rotation-aware refresh within the sandbox lifetime.

**Spec linkage.** C-AS-05 §5.2 (tier-aware resolution table — `tier-3-microvm` and `tier-4-full-vm` rows; C3 across-turn fresh-fetch pole).

**Surfaces affected.** microVM/full-VM-tier secret-resolution module (in-sandbox HTTP fetch over network; bootstrap-token-bounded resolution; tier-4 rotation-aware refresh).

**Signatures introduced or modified.** No new public signature — implements the tier-3/tier-4 branch of `SecretRef` value access per C-AS-05 §5.2. Internal in-sandbox HTTP fetch + bootstrap-token consumption functions at logical level.

**Depends on.** [U-AS-SEC-1].

**Acceptance criterion (functional).** Given a secret resolved for a `tier-3-microvm` or `tier-4-full-vm` sandbox, the value is fetched by an in-sandbox HTTP client using a sandbox-identity bootstrap token whose validity is bounded by the sandbox lifetime; the fetch is performed fresh (no reliance on a startup snapshot). For `tier-4-full-vm`, a test confirming a rotation-aware refresh occurs within the sandbox lifetime passes.

**Notes.** The specific in-sandbox HTTP client implementation and the specific bootstrap-token issuance protocol (AWS STS / Vault wrapped / GCP Workload Identity / etc.) are deferred per the C-AS-05 §"Deferred to implementation discretion" clause — kept at logical surface here. Acceptance verifies the *contract shape* (in-sandbox, network-fetched, bootstrap-token-bounded, lifetime-scoped), not a specific protocol's behavior.

---

### U-AS-SEC-4: `fetch_secret` tier dispatcher — resolution-mechanism composition

**Scope.** Implement the `fetch_secret` entry-point body: select the resolution mechanism (U-AS-SEC-2 env-var injection vs. U-AS-SEC-3 in-sandbox HTTP fetch) by the resolved sandbox tier, and return a `SecretRef` bound to that mechanism. Both T-perm-2 poles are expressed; the dispatcher is the structural composition with the sandbox-tier surface, not a choice between C2 and C3.

**Spec linkage.** C-AS-05 §5.1 (signature — `fetch_secret` entry point); C-AS-05 §5.2 (tier-aware resolution — "Tier choice picks pole; both poles expressed; closure is structural composition with F4"); C-AS-02 §2 (sandbox-tier composition — provides the resolved tier the dispatcher branches on).

**Surfaces affected.** `fetch_secret` dispatcher module (the function body composing the resolved sandbox tier with the per-tier resolution mechanism).

**Signatures introduced or modified.** `fetch_secret(name: string, scope: SecretScope) -> SecretRef` body per C-AS-05 §5.1 — signature already declared at U-AS-SEC-1; this unit supplies the dispatching body.

**Depends on.** [U-AS-SEC-1, U-AS-SEC-2, U-AS-SEC-3]. (The resolved sandbox tier is produced by the C-AS-02 §2 sandbox-tier composition — same AS axis; treated as an input substrate to the dispatcher.)

**Acceptance criterion (functional).** Given a `(name, scope)` pair and a resolved sandbox tier, `fetch_secret` returns a `SecretRef` bound to the env-var injection mechanism for `tier-1-process` / `tier-2-container`, and bound to the in-sandbox HTTP fetch mechanism for `tier-3-microvm` / `tier-4-full-vm`. A test exercising all four tier values and asserting the correct mechanism is selected for each passes.

**Acceptance criterion (integration).** When invoked within a sandbox whose tier was resolved by the C-AS-02 §2 `sandbox_tier` composition, `fetch_secret` dispatches to the mechanism matching that resolved tier; no tier value reaches an undefined branch.

**Notes.** This unit depends on the C-AS-02 sandbox-tier surface being available as the source of the resolved tier; it does not re-implement tier resolution. Allowlist intersection (C-AS-06 §6.2) and per-call audit-ledger emission (C-AS-08, via C-AS-06 §6.2) compose with `fetch_secret` but are owned by C-AS-06 / C-AS-08 units — out of scope for this contract's decomposition; flagged in §6.

---

### U-AS-SEC-5: Negative-observation invariant — sole-resolution-path verification

**Scope.** Implement and verify the C-AS-05 §5.3 negative-observation invariant: secret values absent from stored prompt-cache prefixes, absent from span attributes / log records / observability content-capture surfaces, absent from audit-ledger entries; and `fetch_secret` is the sole path through which secret content reaches a sandbox. Establish the assertion surface that flags secret content arriving by any non-`fetch_secret` ingress as a contract violation.

**Spec linkage.** C-AS-05 §5.3 (negative-observation invariant — absence in stored prompts / log surfaces / ledger; sole resolution path).

**Surfaces affected.** Secret-redaction / sole-resolution-path verification surface (assertion hooks at the prompt-cache-prefix boundary, the span-emission boundary, and the audit-ledger boundary; the "sole resolution path" guard).

**Signatures introduced or modified.** No new public signature — adds invariant-verification / assertion logic. Logical assertion surfaces at the prompt-prefix, span-emission, and ledger-write boundaries.

**Depends on.** [U-AS-SEC-1, U-AS-SEC-4]. Acceptance verification additionally exercises the C-AS-15 span-emission surface and the C-AS-08 audit-ledger surface (cross-contract verification edges — those surfaces are owned by their own units; this unit verifies the *absence* property against them).

**Acceptance criterion (functional).** A test that resolves a secret via `fetch_secret` and then inspects (a) the static prompt-cache prefix, (b) emitted span attributes / log records, and (c) audit-ledger entries confirms the secret value appears in none of them. A test that attempts to introduce secret content by a non-`fetch_secret` path (manifest / prompt / log / ledger) is flagged as a contract violation by the sole-resolution-path guard.

**Acceptance criterion (integration).** When a tool resolves a secret and subsequently emits spans (C-AS-15) and writes an audit-ledger entry (C-AS-08), no secret value is present in either surface; the structure-not-content fingerprint per C-AS-08 is the only secret-related ledger content.

**Notes.** §5.3's first three properties (absence in prompts / logs / ledger) are acceptance-shaped constraints; the "sole resolution path" property is the genuinely product-shaped surface (an active guard) and is why §5.3 warrants its own unit rather than dispersing as acceptance criteria on U-AS-SEC-4. The C-AS-15 and C-AS-08 dependencies are verification-time edges, not product dependencies.

---

## §3 Dependency graph

Per-unit direct dependencies:

```
U-AS-SEC-1  Depends on: (none)                        — foundational anchor
U-AS-SEC-2  Depends on: [U-AS-SEC-1]
U-AS-SEC-3  Depends on: [U-AS-SEC-1]
U-AS-SEC-4  Depends on: [U-AS-SEC-1, U-AS-SEC-2, U-AS-SEC-3]
U-AS-SEC-5  Depends on: [U-AS-SEC-1, U-AS-SEC-4]
```

Topologically sorted order: **U-AS-SEC-1 → U-AS-SEC-2 → U-AS-SEC-3 → U-AS-SEC-4 → U-AS-SEC-5**
(U-AS-SEC-2 and U-AS-SEC-3 are mutually independent — either order; both must precede U-AS-SEC-4.)

Acyclic: yes — a single linear chain with one parallel pair (SEC-2 ‖ SEC-3). No cycle.

Cross-contract / cross-axis edges (within AS axis — no cross-axis-to-other-axis edges):
- U-AS-SEC-4 consumes the resolved sandbox tier produced by **C-AS-02 §2** `sandbox_tier` composition (same AS axis; an input-substrate edge, not a unit dependency within this decomposition).
- U-AS-SEC-5 verification edges touch **C-AS-15** (span emission) and **C-AS-08** (audit-ledger) — same AS axis; verification-time, not product, edges.

Note: this decomposition covers C-AS-05 §5 only. The C-AS-06 allowlist-intersection gate and the C-AS-08 per-call audit-ledger emission compose with `fetch_secret` at runtime but are owned by C-AS-06 / C-AS-08 units in the full AS plan; they appear here only as §6 carry-forward flags.

---

## §4 Coverage matrix

Rows = C-AS-05 §5 sub-sections (contract surfaces). Columns = units. Cell marked where the unit cites that sub-section at `Spec linkage`.

```
                          | U-AS-SEC-1 | U-AS-SEC-2 | U-AS-SEC-3 | U-AS-SEC-4 | U-AS-SEC-5 |
C-AS-05 §5.1 (signature)  |     X      |            |            |     X      |            |
C-AS-05 §5.2 (tier res.)  |            |     X      |     X      |     X      |            |
C-AS-05 §5.3 (neg. inv.)  |            |            |            |            |     X      |
C-AS-05 §5.4 (SecretRef)  |     X      |            |            |            |            |
```

Every C-AS-05 §5 sub-section row carries at least one mark — contract fully covered. Every unit column carries at least one mark — no trace-omission. The C-AS-05 §"Deferred to implementation discretion" clause is intentionally uncovered (deferred items are not unit scope per the decomposition discipline) — see §6.

---

## §5 Cross-cutting integration units

None. C-AS-05 §5 is a single contract; its five units form one linear-with-one-parallel-pair chain and do not require an N:1 cross-cutting consolidation. Composition with C-AS-06 / C-AS-08 / C-AS-15 / C-AS-02 is handled by dependency / verification edges (§3), not by a consolidated cross-cutting unit — those contracts' units live elsewhere in the full AS plan.

---

## §6 Open items

1. **`SecretScope` structural shape not committed at C-AS-05 [MODERATE].** C-AS-05 §5.1 types the `scope` parameter as `SecretScope` and gives its *semantic* (a credential-dimension session key per ADR-F5 v1.1 §Context, orthogonal to ADR-F1's routing-dimension session key), but C-AS-05 commits no structural shape (fields) for `SecretScope`; §"Deferred to implementation discretion" defers only the *serialization format*, not the field shape. C-AS-06 §6.1 reuses `SecretScope` in `SecretAllowlistEntry` without defining it either. U-AS-SEC-1 declares the `fetch_secret` signature against `SecretScope` as a *named, externally-defined* type and does not author its shape — authoring a `SecretScope` schema inside any unit would be a spec extension. **Action for operator:** decide whether C-AS-05 (or an upstream AS contract / ADR-F5) must commit the `SecretScope` field shape before execution, or whether the field shape is a legitimate implementation-discretion item. This decomposition does not apply a spec fix or file a tension record (out of scope for this task); it surfaces the gap for operator routing per `CLAUDE.md` §4.3.

2. **Keyring-library binding deferred [HIGH].** C-AS-05 §"Deferred to implementation discretion" defers the specific keyring-library binding per language ecosystem. Unit bodies (U-AS-SEC-2) stay at logical surface ("keyring-backed local secret store"). The workspace stack commitment (`CLAUDE.md` §3.1 — `python-keyring`) is honored at execution time, not bound in the plan; this is consistent, not a conflict — noted so the executor does not read the logical phrasing as an unresolved choice.

3. **In-sandbox HTTP client + bootstrap-token protocol deferred [HIGH].** C-AS-05 §"Deferred to implementation discretion" defers the in-sandbox HTTP client implementation and the bootstrap-token issuance protocol (AWS STS / Vault wrapped / GCP Workload Identity / etc.). U-AS-SEC-3 acceptance verifies the contract shape (in-sandbox, network-fetched, bootstrap-token-bounded, lifetime-scoped), not a specific protocol — intentional; no action required unless a prod-tech binding is later needed.

4. **Composition carry-forwards (not C-AS-05 scope) [HIGH].** The C-AS-06 §6.2 allowlist-intersection gate (`fetch_secret` succeeds only if `(name, scope) ∈ tool.contract.required_secrets ∩ operator-policy override`) and the C-AS-08 per-call audit-ledger emission both compose with `fetch_secret` at runtime. They are owned by C-AS-06 / C-AS-08 units in the full AS plan and are deliberately out of scope for this single-contract decomposition. Flagged so the full-plan author wires the dependency edges (C-AS-06 unit → U-AS-SEC-4; C-AS-08 emission → U-AS-SEC-4 successful-call path).

---

*End of C-AS-05 §5 decomposition. Five atomic units (U-AS-SEC-1 … U-AS-SEC-5); dependency graph acyclic; coverage matrix complete over §5.1–§5.4; four open items surfaced for operator routing. Status: Proposed — clears at host-axis-plan P6-CK. Unit IDs are decomposition-local placeholders; the full-AS-plan author assigns canonical U-AS-NN IDs at plan integration.*
