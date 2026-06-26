# Implementation Plan Fragment — C-AS-05 §5 `fetch_secret` Contract Decomposition

*Partial implementation plan. Scope: the single specification contract **C-AS-05 §5** (`fetch_secret(name, scope) -> SecretRef` signature) from `design-substrate/Spec_Action_Surface_v1.md` (Spec_Action_Surface_v1, v1.1, AS axis). Decomposed under the implementation-planner role discipline: atomic-decomposition + spec-traceability + dependency-graph discipline. Status: Proposed.*

---

## 1. Mode and scope declaration

**Sub-mode.** Initial authoring mode — decomposition of a single contract into atomic units; no prior plan filed for this fragment. Output is a plan fragment, not a full axis plan: the requested scope is C-AS-05 §5 alone.

**Plan shape.** Component-led within the fragment. The contract decomposes around one component identity — the secret-fetch abstraction — so units cluster by the surface each touches (opaque type, signature, per-tier resolution mechanism, negative-observation enforcement). This is declared here per skill §6; the shape is not imposed, it is read from the contract's internal §5.1–§5.4 structure.

**Contract under decomposition.** C-AS-05 §5 — four sub-sections:
- §5.1 Function signature — `fetch_secret(name: string, scope: SecretScope) -> SecretRef`
- §5.2 Tier-aware resolution — per-tier (4 tiers) resolution mechanism, expressing the T-perm-2 C2/C3 poles
- §5.3 Negative-observation invariant — four absence properties (prompt cache, log surfaces, ledger, sole-resolution-path)
- §5.4 `SecretRef` opaque-type discipline — opacity, lifetime-bounding, fresh-on-restart

**Scope boundary.** C-AS-06 (`required_secrets` allowlist), C-AS-07 (`secret.fail.class` taxonomy), C-AS-08 (structure-not-content audit composition) are sibling AS contracts that *compose with* C-AS-05 but are **not** decomposed here — they are out of the requested scope. Where a C-AS-05 unit's acceptance genuinely requires a sibling contract's product, the dependency is named as an **external dependency** (cross-contract, flagged), not silently absorbed. This fragment does not claim coverage of C-AS-06/07/08.

---

## 2. Decomposition rationale

C-AS-05 §5 is a moderately complex contract: a signature + an opaque type + a 4-row tier-resolution table + a 4-property negative-observation invariant. Per skill §3 atomicity criteria, it does not collapse to a single unit — the four sub-sections touch distinct surfaces with a natural dependency ordering, and the two tier-resolution poles (C2 env-var-snapshot at process/container tiers; C3 in-sandbox-HTTP at microVM/full-VM tiers) are genuinely different implementation surfaces. Equally it must not over-decompose — `name`/`scope` parameter handling is not its own unit; it folds into the signature unit.

Resulting decomposition: **5 atomic units** (U-AS05-1 … U-AS05-5).

- §5.1 + §5.4 (signature + `SecretRef` opaque type) → 2 units. The opaque type anchors the signature's return value, so it is a foundational unit and the signature depends on it.
- §5.2 (tier-aware resolution) → 2 units, split on the T-perm-2 pole boundary the spec itself draws: C2 poles (tier-1-process / tier-2-container, env-var injection) and C3 poles (tier-3-microvm / tier-4-full-vm, in-sandbox HTTP client). The spec explicitly tables these as distinct mechanisms; they are distinct implementation surfaces and distinct test surfaces.
- §5.3 (negative-observation invariant) → 1 unit — the absence-enforcement test surface, which composes against all prior units.

---

## 3. Atomic units

### U-AS05-1 — `SecretRef` opaque-handle type

**Spec trace.** C-AS-05 §5.1 (`SecretRef` return-type row of the signature table); C-AS-05 §5.4 (`SecretRef` opaque-type discipline — opacity, lifetime-bounding, fresh-on-restart).

**Surface.** One type definition. Defines the `SecretRef` opaque handle in the AS-axis secrets module. The type carries the resolved-secret reference; per §5.4 it exposes **no API surface that returns the secret value as a string**. Access to the underlying value is tier-mechanism-specific and is implemented by U-AS05-3 / U-AS05-4, not here. This unit establishes the type, its construction surface (consumed by `fetch_secret`), and its lifetime contract: lifetime bounded by sandbox lifetime, release on sandbox termination, no cross-sandbox sharing, no in-process cache across restart boundaries (fresh-on-restart per ADR-F5 v1.1 §Consequences (b)).

**Files affected (logical).** The AS-axis secrets-module type-definition file.

**Signatures.** `SecretRef` opaque handle type — definition only; no value-returning accessor per §5.4 opacity property. (Specification-level type; planner names it, does not redesign.)

**Depends on:** (none) — foundational unit.

**Acceptance criterion.**
- Functional: `SecretRef` type exists; instantiable via its construction surface; exposes no method/attribute that returns the secret value as a plain string (verified by type-surface inspection / a test asserting no string-returning value accessor exists). Lifetime-release surface exists and is callable on sandbox termination.

---

### U-AS05-2 — `fetch_secret(name, scope) -> SecretRef` signature and `SecretScope` parameter handling

**Spec trace.** C-AS-05 §5.1 (function signature; `name` / `scope` parameter-type rows).

**Surface.** One function family. Defines the `fetch_secret` entry-point signature `fetch_secret(name: string, scope: SecretScope) -> SecretRef`, with `name` as a structure-not-content string identifier and `scope` as a `SecretScope` credential-dimension session key (orthogonal to ADR-F1's routing-dimension session key per §5.1). This unit establishes the callable abstraction and its dispatch seam to tier-specific resolution (the seam is *consumed by* U-AS05-3 / U-AS05-4; this unit defines the dispatch point, not the per-tier mechanisms). Returns a `SecretRef` constructed via U-AS05-1's construction surface.

**Files affected (logical).** The AS-axis secrets-module `fetch_secret` definition file; the `SecretScope` type-definition file (if `SecretScope` is not already defined by an upstream substrate unit — see note below).

**Signatures.** `fetch_secret(name: string, scope: SecretScope) -> SecretRef`; `SecretScope` credential-dimension session-key type.

**Depends on:** [U-AS05-1].

**External dependency note.** `SecretScope` is referenced by C-AS-05 §5.1 and C-AS-06 §6.1 as a shared scope-dimension type. If a foundational `SecretScope` type unit exists elsewhere in the AS-axis plan (or harness-core shared types), this unit depends on it rather than defining it. C-AS-05 §5 itself does not commit `SecretScope`'s internal structure (§5.4 explicitly defers `SecretScope` *serialization format* to implementation discretion). Per skill §2: the planner does not invent the `SecretScope` schema — if its definition site is not determinable from C-AS-05 §5 alone, this is a **finding** (see §5 Findings), not a silently-authored type.

**Acceptance criterion.**
- Functional: `fetch_secret` is callable with a `string` name and a `SecretScope` scope and returns a `SecretRef`. Dispatch seam to per-tier resolution is present and selectable by sandbox tier.
- Integration (with U-AS05-1): the returned `SecretRef` is a well-formed instance of the U-AS05-1 type.

---

### U-AS05-3 — Tier-aware resolution: C2 within-turn-snapshot poles (`tier-1-process`, `tier-2-container`)

**Spec trace.** C-AS-05 §5.2 (tier-aware resolution table, rows `tier-1-process` and `tier-2-container`); C-AS-05 §5.4 (opacity property — env-var-read access mechanism).

**Surface.** One resolution-mechanism family. Implements secret resolution for the two C2-pole sandbox tiers per the §5.2 table: `tier-1-process` — direct read into the sandboxed process via environment variables at sandbox startup; `tier-2-container` — container-environment variable injection at container startup (long-lived agent-process-with-keyring-handles pattern per ADR-F5 v1.1 §Rationale (b)(i)). Both express the T-perm-2 C2 pole (within-turn snapshot). This unit wires the env-var injection path that backs `SecretRef` value-access at these two tiers — the access mechanism §5.4 names as "env-var read at process / container tiers."

**Files affected (logical).** The AS-axis secrets-module tier-resolution file (C2-pole resolution path).

**Signatures.** Per-tier resolution mechanism for `tier-1-process` / `tier-2-container`; env-var-backed `SecretRef` value-access path. (No new public signature beyond the U-AS05-2 dispatch seam; this is the seam's tier-1/tier-2 implementation.)

**Depends on:** [U-AS05-1, U-AS05-2].

**External dependency note.** The sandbox tier enum (`tier-1-process` … `tier-4-full-vm`) is committed by C-AS-01 (tier-set enum, 4 values), not by C-AS-05 §5. This unit depends on the tier enum's definition site — flagged as a **cross-contract dependency** on C-AS-01's tier-enum unit. Specific keyring-library binding (`python-keyring` etc.) is **deferred to implementation discretion** per C-AS-05 §5.4 — not committed here, not a plan-level decision.

**Acceptance criterion.**
- Functional: for a sandbox at `tier-1-process` or `tier-2-container`, `fetch_secret` resolves a secret via the environment-variable injection path and the resulting `SecretRef` permits tier-specific value access via the env-var read mechanism. Verified with a process-tier and a container-tier fixture (the tiers' fixtures are the declared-dependency surface; no unrelated unit required).
- Integration: resolution is a within-turn snapshot (C2 pole) — value is captured at sandbox startup, not re-fetched mid-turn.

---

### U-AS05-4 — Tier-aware resolution: C3 across-turn fresh-fetch poles (`tier-3-microvm`, `tier-4-full-vm`)

**Spec trace.** C-AS-05 §5.2 (tier-aware resolution table, rows `tier-3-microvm` and `tier-4-full-vm`); C-AS-05 §5.4 (opacity property — in-sandbox-HTTP access mechanism; fresh-on-restart property).

**Surface.** One resolution-mechanism family. Implements secret resolution for the two C3-pole sandbox tiers per the §5.2 table: `tier-3-microvm` — in-sandbox HTTP client over network using a sandbox-identity bootstrap token bounded by sandbox lifetime; `tier-4-full-vm` — same, plus rotation-aware refresh within sandbox lifetime. Both express the T-perm-2 C3 pole (across-turn fresh-fetch). This unit wires the in-sandbox HTTP client path that backs `SecretRef` value-access at these two tiers — the access mechanism §5.4 names as "in-sandbox HTTP at microVM / full-VM tiers."

**Files affected (logical).** The AS-axis secrets-module tier-resolution file (C3-pole resolution path).

**Signatures.** Per-tier resolution mechanism for `tier-3-microvm` / `tier-4-full-vm`; in-sandbox-HTTP-backed `SecretRef` value-access path; rotation-aware refresh hook (tier-4). (No new public signature beyond the U-AS05-2 dispatch seam; this is the seam's tier-3/tier-4 implementation.)

**Depends on:** [U-AS05-1, U-AS05-2].

**External dependency note.** Cross-contract dependency on C-AS-01's tier-enum unit (as in U-AS05-3). Specific in-sandbox HTTP client implementation, the bootstrap-token issuance protocol per prod-tech (AWS STS / Vault wrapped / GCP Workload Identity / etc.), and the `SecretScope` serialization format are all **deferred to implementation discretion** per C-AS-05 §5.4 — not committed at plan level.

**Acceptance criterion.**
- Functional: for a sandbox at `tier-3-microvm` or `tier-4-full-vm`, `fetch_secret` resolves a secret via an in-sandbox HTTP client authenticated by a sandbox-identity bootstrap token, and the resulting `SecretRef` permits tier-specific value access via the in-sandbox HTTP mechanism. Tier-4 additionally exercises a rotation-aware refresh within sandbox lifetime. Verified with a microVM-tier and a full-VM-tier fixture.
- Integration: resolution is across-turn fresh-fetch (C3 pole) — bootstrap token lifetime is bounded by sandbox lifetime; no in-process secret cache survives a restart boundary (fresh-on-restart per §5.4 / ADR-F5 v1.1 §Consequences (b)).

---

### U-AS05-5 — Negative-observation invariant enforcement and sole-resolution-path test surface

**Spec trace.** C-AS-05 §5.3 (negative-observation invariant — all four properties: absence in stored prompts, absence in log surfaces, absence in ledger, sole resolution path); C-AS-05 §5.4 (opacity property — no string-returning value accessor).

**Surface.** One bounded enforcement-and-test surface. Establishes the verification surface for C-AS-05 §5's negative-observation invariant — the contract that secret values MUST NOT enter (a) the static prompt-cache prefix, (b) span attributes / log records / observability content-attribute capture surfaces, (c) audit-ledger entries, and that (d) `fetch_secret` is the **sole** path through which secrets reach a sandbox. This unit authors the assertions that hold the invariant across the units above: it verifies the opaque-type discipline gives no string-returning accessor, and that no secret value appears on the prompt / log / ledger surfaces after a `fetch_secret` call at each tier.

**Files affected (logical).** The AS-axis secrets-module negative-observation test file; any redaction-assertion hook at the secrets-module boundary required to enforce "absence in log surfaces."

**Signatures.** No new public signature — this is an invariant-enforcement and test unit. (Per skill §3.4, it is a coherent, independently revertible change.)

**Depends on:** [U-AS05-1, U-AS05-2, U-AS05-3, U-AS05-4].

**External dependency note.** §5.3's "absence in ledger" property states that the *structure-not-content fingerprint per C-AS-08 is the audit-ledger composition* — i.e. C-AS-05 §5.3 asserts secret values are absent from the ledger, while C-AS-08 owns what *is* written. This unit verifies the **absence** half (no secret value in any ledger entry); it does **not** implement C-AS-08's `outputs_hash` audit composition, which is out of scope for this fragment. If verifying "absence in ledger" requires an actual ledger-write path to exist, this unit's acceptance has a cross-contract dependency on the C-AS-08 audit-emission unit — flagged as a **finding** (see §5) so the operator can confirm the sibling-contract sequencing.

**Acceptance criterion.**
- Functional: a test surface exists asserting all four §5.3 properties for a `fetch_secret` call — (a) the secret value does not appear in the static prompt-cache prefix; (b) the value does not appear in span attributes / log records; (c) the value does not appear in audit-ledger entries; (d) no resolution path other than `fetch_secret` introduces a secret value into a sandbox (negative test: a secret arriving via manifest / prompt / log / ledger is flagged as a contract violation). Plus: `SecretRef` exposes no string-returning value accessor (§5.4 opacity).
- Integration: the invariant holds across all four tiers (C2 and C3 poles), verified once U-AS05-3 and U-AS05-4 are complete.

---

## 4. Dependency graph

```
U-AS05-1  (SecretRef opaque type)            Depends on: (none)
   │
   ▼
U-AS05-2  (fetch_secret signature)           Depends on: [U-AS05-1]
   │
   ├──────────────┐
   ▼              ▼
U-AS05-3        U-AS05-4                     Depends on: [U-AS05-1, U-AS05-2]
(C2 poles)      (C3 poles)
   │              │
   └──────┬───────┘
          ▼
U-AS05-5  (negative-observation invariant)   Depends on: [U-AS05-1..4]
```

**Topological sort (one valid order):** U-AS05-1 → U-AS05-2 → U-AS05-3 → U-AS05-4 → U-AS05-5. (U-AS05-3 and U-AS05-4 are independent of each other; either order between them is valid.)

**Acyclic invariant:** satisfied — the graph is a DAG; a topological sort exists.

**Foundational-first:** U-AS05-1 (the `SecretRef` type) is the foundational substrate unit with `Depends on: (none)`; all consumers depend on it.

**Cross-contract / cross-axis dependencies (flagged):**
- U-AS05-2 → `SecretScope` type definition site (C-AS-05 §5.1 / C-AS-06 §6.1 shared type; definition site indeterminate from C-AS-05 §5 alone — see Findings F-1).
- U-AS05-3, U-AS05-4 → C-AS-01 sandbox tier-set enum (4-value tier enum committed by C-AS-01, not C-AS-05).
- U-AS05-5 → C-AS-08 audit-ledger emission path, *if* verifying "absence in ledger" requires a live ledger-write path (see Findings F-2).

These are intentionally *not* internal `Depends on:` edges, because the depended-upon products belong to contracts outside this fragment's scope. They are recorded so the operator can place this fragment correctly in the full AS-axis plan.

---

## 5. Coverage matrix and findings

### 5.1 Coverage matrix — C-AS-05 §5 sub-sections × units

| C-AS-05 sub-section | U-AS05-1 | U-AS05-2 | U-AS05-3 | U-AS05-4 | U-AS05-5 |
|---|---|---|---|---|---|
| §5.1 Function signature | ✅ (`SecretRef` return row) | ✅ (signature + params) | — | — | — |
| §5.2 Tier-aware resolution | — | ✅ (dispatch seam) | ✅ (C2 tiers) | ✅ (C3 tiers) | — |
| §5.3 Negative-observation invariant | — | — | — | — | ✅ |
| §5.4 `SecretRef` opaque-type discipline | ✅ (opacity, lifetime, fresh-on-restart) | — | ✅ (env-var access) | ✅ (in-sandbox-HTTP access, fresh-on-restart) | ✅ (opacity test) |

Every sub-section row carries at least one column mark; every unit column carries at least one row mark. **C-AS-05 §5 is fully covered by this fragment.**

### 5.2 Findings

Per skill §2 — spec-shaped gaps are surfaced, not invented.

- **F-1 (Class: surface-to-operator, plan-internal).** `SecretScope` is used by C-AS-05 §5.1 as a parameter type but its definition site and internal structure are not committed by C-AS-05 §5 (§5.4 defers only its *serialization format*; C-AS-06 §6.1 also consumes it). U-AS05-2 must depend on `SecretScope`'s definition unit. Recommendation: confirm whether `SecretScope` is authored by an upstream AS-axis foundational unit or a harness-core shared-types unit, and add that as U-AS05-2's external dependency. Not a spec gap — a cross-contract sequencing question for the full-axis plan.

- **F-2 (Class: surface-to-operator, cross-contract sequencing).** C-AS-05 §5.3 "absence in ledger" asserts a *negative* property whose verification (U-AS05-5) may require a live audit-ledger write path, which is owned by C-AS-08 (out of this fragment's scope). Recommendation: when this fragment is merged into the full AS-axis plan, sequence U-AS05-5 after the C-AS-08 audit-emission unit, or scope U-AS05-5's ledger assertion to a stub-ledger fixture. Not a spec gap.

- **No spec-extension findings.** No unit introduces a library, schema field, protocol, or behavior absent from C-AS-05 §5. Keyring-library bindings, in-sandbox HTTP client implementation, bootstrap-token issuance protocol, `SecretScope` serialization, and `pass`/`gpg` headless fallback are all carried as **deferred-to-implementation-discretion** items per C-AS-05 §5.4 — recorded, not committed.

### 5.3 Coherence pass (skill §5 step 9)

| Check | Result |
|---|---|
| Atomicity (§3, 4 criteria) | PASS — each unit is a single coherent change (one type / one signature / one tier-pole resolution family / one invariant-test surface), single-session-sized, independently testable given declared deps, coherent rollback boundary. |
| Spec-traceability (§4.2) | PASS — every unit cites C-AS-05 by ID and sub-section (§5.1–§5.4). |
| Dependency-awareness (§4.3) | PASS — DAG; topological sort exists; cross-contract deps flagged separately. |
| Implementation-grade detail (§4.4) | PASS — logical files, spec-level signatures, and testable acceptance criteria named per unit; no spec extension. |
| Coverage (§4.2 aggregate) | PASS for the requested scope (C-AS-05 §5). C-AS-06/07/08 explicitly out of scope — not claimed as covered. |

---

*End of C-AS-05 §5 decomposition fragment. 5 atomic units (U-AS05-1 … U-AS05-5). Status: Proposed — pending P6-CK clearance and merge into the full Action Surface implementation plan. Unit IDs are fragment-local; renumber on merge into the canonical AS-axis plan unit space (U-AS-NN).*
