# Class 1 Fork — B-51 / B-52 / B-54: the OD audit-signing amendment arc

**Filed:** 2026-07-17 · autonomous-loop fork-first leg following B-50 close (register open queue EMPTY). Class 1
(design-substrate spec deltas required; two legs cross-axis OD↔CP). **Status: FILED — awaiting operator
ratification per §4.3.** No `design-substrate/**` file is edited by this filing; the three register rows stay
`design_substrate_gated` until ratification (X-AL-3). Source recommendations: `.harness/b-47-pr-b2-design-disposition-v1.md`
§1 rows (f)/(m)/(h), codex-refined at disposition-leg rounds 3/4/6/10/11/16, re-grounded here against the
CURRENT spec heads (OD v1.33, cleared 2026-07-16 — note: workspace `CLAUDE.md` §2.3 still names v1.32; the
v1.33 clearance marker at `.harness/clearance/spec-operational-discipline-v1-33-cleared-2026-07-16.md` is the
authority — pointer refresh owed at the next CLAUDE.md maintenance PR, not this filing).

**Why one filing:** all three legs amend the same C-OD-21 signing surface introduced/refined at OD v1.33
§21.2.1; one OD amendment arc (v1.33 → v1.34, plus a bounded CP v1.24 → v1.25 rider for leg 2) can carry all
three coherently, and leg 3's verification API must reconstruct whatever message shape leg 1 ratifies — they
interlock.

---

## Leg 1 — B-51 · Tenant-scope binding under deployment-scoped signing keys *(item (f))*

### The fork

OD v1.33 §21.2.1 commits the canonical signing message as the length-prefixed injective four-tuple
`(compute_entry_hash(payload), key_id, algo.value, "DEPLOYMENT_BOUND")`. Under a DEPLOYMENT-scoped key no
segment carries tenant identity: a signed audit entry produced for tenant A re-presented as tenant B's history
verifies cleanly — tenant scoping lives only in the UNSIGNED sidecar `tenant_tag` and the IS `action_id`
wrap, both plaintext-editable at the adversarial-filesystem tier. v1.33's own out-of-scope row already routes
this: *"tenant-scope binding into the signed message under a DEPLOYMENT-scoped key (`B-47` close-out item (f)
— resolve jointly with the persistence design at the composition-root arc; a TENANT-scoped `key_id` already
binds tenant identity via the canonical message's `key_id` segment)"*.

### Options (register-refined; do not re-litigate at the apply pass)

| # | Option | Assessment |
|---|---|---|
| 1 | Bind tenant into `AuditPayload.audit_namespace_attrs` (entry_hash-borne, hence message-bound transitively) | Weakest — attr-borne, caller-supplied, not schema-enforced; absence is indistinguishable from single-tenant |
| 2 | **Fifth canonical-message segment carrying the tenant scope token** | **RECOMMENDED** — byte-compat-scoped per the B-22 → B-31 precedents: single-tenant/absent → the existing four-tuple PRESERVED VERBATIM (drop-when-`None`); multi-tenant → fifth length-prefixed segment. Metadata relabeling (tenant swap) then breaks verification, the exact §21.2.1 discipline. **Rider (filing codex round-4 P1): drop-when-`None` needs a bootstrap invariant at MULTI_TENANT_COMPLIANCE — current `RuntimeConfig` accepts MTC with `tenant_id=None` (writer normalizes to `_single`), which would silently keep a compliance deployment on the tenant-unbound four-tuple; the delta must require tenant scope at MTC (config validation) or make signing fail absent tenant there** |
| 3 | REQUIRE tenant-scoped `key_id`s at MULTI_TENANT_COMPLIANCE (config-validation only) | REJECTED as primary (disposition codex round-3/round-10): `key_arns` maps logical ids to ARNs with NO tenant association and every production composer supplies FIXED global key_ids (`stage_4_od.py`), so a presence check would accept one shared key for every tenant — a false guarantee; tenant-aware key SELECTION would be a mechanism change comparable to option 2 with worse key-management ergonomics. v1.33's key_id note describes a posture an operator MAY adopt, not one the runtime can enforce today |

**No effective interim mitigation exists** (disposition codex round-10): composers select fixed global
key_ids, so cross-tenant replay under a deployment-scoped key remains unmitigated until the segment lands.

### Required rider — tenant-bearing signing API (disposition codex round-16)

The fifth segment needs tenant identity AT SIGNING. Today `sign_audit_entry` / `cp_audit_to_od_audit` receive
no tenant, and `RuntimeAuditLedgerWriter` sees `tenant_id` only post-signing. The v1.34 delta MUST therefore
also specify the tenant-bearing signing API threaded through the converters/composers —
`StepExecutionContext.tenant_id` is in scope at every converter-based production call site, **and the rider
must explicitly include the one non-converter path: `AuditLedgerRedactionTokenMap` calls
`compose_redaction_token_audit_entry` directly and holds tenant scope as its own `_tenant_id` (filing codex
round-1 P2 — omitting it would leave redaction-token signatures tenant-unbound after the converter sites are
updated), and the second non-converter path `sign_rotation_pair` (filing codex round-3 P2), which calls
`sign_audit_entry` twice with no tenant parameter — thread tenant scope through it, or explicitly
defer/prohibit its multi-tenant use in the delta (it already cannot take the §21.2.1 backend seam naively
pending B-33's rotation-aware message binding, per OD v1.33's own out-of-scope row — the same deferral can
carry both constraints)** — or move signing to a tenant-aware boundary. Without the rider the segment is
unpopulatable.

### Council

Nameable tension: **C7 compliance** (bind everything the trust claim depends on) ⊥ **C2 schema-minimalism**
(the canonical message stays minimal; every segment is forever). Dyadic convening at the spec-delta apply
leg per §10.9 — not at this filing.

---

## Leg 2 — B-52 · Audit-signing fail-closed policy at MULTI_TENANT_COMPLIANCE *(item (m))*

### The fork

Audit-signing failures are typed and loudly surfaced (ERROR) at all ten surfacing sites — the six
fn-internal handlers and the four offload-boundary saturation handlers (disposition codex round-6) — but
dispatch proceeds: fail-open. At MULTI_TENANT_COMPLIANCE an unsigned audit trail silently accumulating
contradicts the tier's audit posture. The tension is TWO-SPEC (disposition codex round-4):

- **OD side** — the sibling precedent is already committed: OD v1.8 §28.2 rate-table resolution —
  *"operator-configurable; default fail-closed = raise"*.
- **CP side** — CP v1.24 §28.10.4 invariant 2 commits the OPPOSITE for the validator post-evaluate hook:
  *"Hook exceptions MUST be swallowed at the firing site. Failure of cost-attribution MUST NOT fail validator
  dispatch."* That invariant is CP-OWNED; fail-closing the audit-signing failure class at that hook requires
  a CP amendment carving the class out of the swallow-mandate.

### Recommendation

Mirror the §28.2 precedent: an `audit_signing_fail_closed` RuntimeConfig flag, per-persona default — ON at
MULTI_TENANT_COMPLIANCE, OFF elsewhere (persona-tier discipline per workspace CLAUDE.md §10.2) — consulted at
ALL TEN sites (or centralized immediately ahead of every catch). **Plus the eleventh path the ten-site
enumeration misses (filing codex round-2): `AuditLedgerRedactionTokenMap.append` signs via
`compose_redaction_token_audit_entry` directly (`redaction_token_audit_map.py:112-123`) and
`RedactionSpanProcessor.on_end` catches only `KeyError`/`TypeError` (`redaction_span_processor.py:300-314`)
— a KMS failure there propagates today (de-facto fail-closed) and would BYPASS the flag entirely. The delta
must either bring this path under the flag or declare it unconditionally fail-closed in the policy
enumeration; recommend the latter (raw redaction values must never persist against an unsigned row — the
path's current propagate behavior is the correct posture, so declare it rather than soften it).**

**And the zeroth site (filing codex round-3 P1): the ABSENT backend.** With current `RuntimeConfig`
defaults, `sign_audit_entry(..., backend=None)` returns an `unsigned:*` placeholder WITHOUT raising — a
default-config MTC deployment never enters any catch site and accumulates exactly the unsigned trail this
leg exists to prevent. The delta must classify an absent backend as a STARTUP/policy failure when
`audit_signing_fail_closed` is ON (bootstrap validation: fail-closed ⇒ a configured backend is required),
not merely police the runtime failure sites. Delta shape: OD v1.34 addendum (policy +
flag + site enumeration) **plus** CP v1.24 → v1.25 amending §28.10.4 invariant 2 with the audit-signing
carve-out. The weaker single-spec alternative (fail-open preserved at the one CP-owned hook, fail-closed at
the other nine sites) is coherent but leaves the compliance tier's weakest link at the validator hook —
surface both to the operator; recommend the two-spec shape.

### Council

Nameable tension: **C7 compliance** (no unsigned trail at MTC) ⊥ **C1/C9 reliability** (a signing outage
must not take down dispatch). Dyadic convening at the apply leg.

---

## Leg 3 — B-54 · Backend-aware signature verification API *(item (h) residual)*

### The fork

OD v1.33 §21.2.1 explicitly leaves verification out of scope (*"signature verification surface (C-OD-21
exposes hash-chain integrity only — unchanged)"*), and the landed B-49 verifier
(`harness-od/src/harness_od/per_family_audit_verification.py`) content-hashes and chain-verifies but never
touches `signature_attrs`. With real KMS signatures durably persisted (B-47 sidecar) there is no spec-committed
way to VERIFY them — the recoverability the sidecar exists to provide has no consuming contract.

### Recommendation

New C-OD-21 §21.2.2 verification API in the same v1.34 delta, mirroring the injection seam precedent
(CP v1.98 §20.2.1 `SigningBackend`, B-22): optional `backend` parameter; absent → current behavior
(hash-chain + content integrity only) PRESERVED VERBATIM; present → reconstruct the canonical message —
INCLUDING the leg-1 fifth segment if ratified, which is why B-54 must land jointly with or after B-51 in the
same delta — and project `"DEPLOYMENT_BOUND"` → `key_period=0` exactly as signing does. Two contract
requirements sharpened at filing codex round-1:

- **Tenant scope is a verifier INPUT** (round-1 P1): the verifier consumes `Sequence[AuditLedgerEntry]`
  (B-49 shape), but the tenant tag lives in the sidecar wrapper and is stripped by
  `read_full_entries_for_tenant` — the fifth segment is unreconstructable from the entries alone. The
  §21.2.2 contract must take the expected tenant scope as a parameter (verification is already per-tenant
  at every consumer) or specify an equivalent signed discriminator persisted on the entry.
- **Legacy exemption must NOT be inferred from the signature value** (round-1 P1): `signature_attrs` are
  mutable and excluded from `entry_hash`, so classifying placeholder-SHAPED values (`unsigned:*`) as exempt
  hands an attacker a downgrade path — replace a real signature with a placeholder shape and the row skips
  verification. The contract must gate exemption on an operator-recorded cutover instead — and the cutover record must
  itself be AUTHENTICATED (filing codex round-4 P1): a plain `adopt_legacy_is_refs`-style sidecar row is
  mutable at exactly the adversarial tier under discussion, so an attacker could rewrite the baseline to
  exempt forged post-cutover rows, recreating the downgrade path. The delta must require the cutover to be
  signed by a trusted key or anchored outside the rewritable ledger (e.g. bootstrap config / key custody
  record); the round-46 explicit-operator-action posture carries over, its carrier does not.
  A config-declared pre-backend KEY-PERIOD set is NOT a viable cutover mechanism (filing codex round-3 P2):
  both the placeholder era and the real-KMS era store `"DEPLOYMENT_BOUND"` / project `key_period=0`, so a
  period set either exempts every row or none; period-based cutover only becomes possible if B-33
  introduces distinct periods first.

### Council

Conditional, preserved verbatim from the register rows (filing codex round-2 — this filing does NOT resolve
whether verification may ever be BLOCKING): the recommended §21.2.2 contract is a non-blocking verify API
(seam shape settled by the B-22 precedent — no council needed for that half), but IF ratification makes
verification blocking anywhere (e.g. read-path enforcement), the C7-compliance ⊥ C1/C9-reliability dyad
convenes at the apply leg before that half lands.

---

## Ratification gate (the ONE operator decision this filing surfaces)

Per §4.3 the design-substrate amendments halt here. The operator ratifies, in one decision:

1. **Leg 1 option 2** (fifth segment + tenant-bearing signing API rider, incl. the redaction-map path) — or
   names an alternative.
2. **Leg 2 two-spec shape** (OD flag + CP §28.10.4 carve-out, redaction path declared unconditionally
   fail-closed) vs the weaker single-spec alternative.
3. **Leg 3 acceptance** (filing codex round-2 — leg 3 needs its own explicit ratification, not a ride-along):
   the new C-OD-21 §21.2.2 backend verification API with its two contract requirements (tenant scope as
   verifier input; cutover-gated legacy exemption) and its NON-BLOCKING default — or an alternative/defer.
4. **Arc bundling** — one OD v1.33 → v1.34 delta carrying legs 1+3, with the CP v1.24 → v1.25 rider for leg 2
   (recommended), vs splitting.

On ratification: spec-writer apply pass (with the two dyadic council convenings at the apply leg), clearance
markers per §4.5, then the register rows flip `design_substrate_gated` → open/buildable and the impl arc
proceeds under the standard pipeline.
