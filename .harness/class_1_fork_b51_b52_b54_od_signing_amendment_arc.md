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
§21.2.1; one OD amendment arc (v1.33 → v1.34, plus a bounded CP delta rider carrying BOTH CP-owned halves —
leg 1's §13.5.1 tenant-bearing converter-signature amendment AND leg 2's §28.10.4 carve-out — plus a Runtime
rider, see the ratification gate) can carry all three coherently, and leg 3's verification API must
reconstruct whatever message shape leg 1 ratifies — they interlock. **CP delta versioning (filing codex round-5 P1): the CP head is `Spec_Control_Plane_v1_100.md`
(cleared 2026-07-15) — §28.10.4's CITE stays `v1.24` (last substantive definition, per the delta-baseline
§-cite convention), but the amendment itself is authored as CP v1.100 → v1.101; every earlier "v1.24 →
v1.25" phrasing in this filing is corrected to that.**

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
| 2 | **Fifth canonical-message segment carrying the tenant scope token** | **RECOMMENDED** — byte-compat-scoped per the B-22 → B-31 precedents: single-tenant/absent → the existing four-tuple PRESERVED VERBATIM (drop-when-`None`); multi-tenant → fifth length-prefixed segment. Metadata relabeling (tenant swap) then breaks verification, the exact §21.2.1 discipline. **Rider (filing codex round-4 P1): drop-when-`None` needs a bootstrap invariant at MULTI_TENANT_COMPLIANCE — current `RuntimeConfig` accepts MTC with `tenant_id=None` (writer normalizes to `_single`), which would silently keep a compliance deployment on the tenant-unbound four-tuple; the delta must require tenant scope at MTC (config validation) or make signing fail absent tenant there. And the invariant needs an UPGRADE story (round-5 P1): an existing MTC deployment with `tenant_id=None` has history persisted under the `_single` tag — requiring a real tenant at bootstrap orphans that history from tenant-scoped reads, so the delta must specify an authenticated migration/retagging procedure or an explicit legacy-read strategy before the invariant enables** |
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
carry both constraints), and the workflow-less prewarm path (round-5 P1): `RuntimeLLMDispatcher.prewarm()`
invokes the LLM cost-attribution converter with `tenant_id=None` because it runs OUTSIDE any workflow —
under MTC, drop-when-`None` leaves that signed row tenant-unbound while fail-on-missing breaks prewarm; the
delta must thread the deployment tenant into prewarm or define an explicit synthetic-scope policy for
workflow-less audit rows** — or move signing to a tenant-aware boundary. Without the rider the segment is
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
ALL TEN sites (or centralized immediately ahead of every catch). **Flag semantics at MTC (filing codex
round-12 P1): an operator-explicit `false` at MTC would persist unsigned history in direct contradiction of
C-CP-20 §20.1's per-entry cryptographic-signature requirement — the delta must either make `false` INVALID
at MTC (config validation; the flag is then only a non-MTC opt-in) or carry an explicit §20.1 relaxation in
the CP rider; the ratification gate decides which (recommend the former — no relaxation of a committed
compliance invariant).** **Plus the eleventh path the ten-site
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
not merely police the runtime failure sites.

**And the twelfth path: prewarm's own swallow-all boundary (filing codex round-8 P1).** Even with the ten
handlers re-raising, `RuntimeLLMDispatcher.prewarm()` catches EVERY exception after the provider call and
returns `FAILED`, and its bootstrap/daemon callers (stage 5, `_keepalive_loop`) suppress failures — a KMS
signing failure after a prewarm provider call leaves that call unaudited while the process continues. Leg 2
must specify the MTC posture for prewarm/keepalive explicitly: disable prewarm at MTC under fail-closed,
propagate its signing failure through the prewarm boundary, or another mechanism preventing unaudited
provider calls — silence here would leave a fail-open bypass exactly where leg 1 newly identifies a signing
path.

**And the retry-classification interaction (filing codex round-10 P1).** Once fail-closed propagation is
on, a KMS signing failure AFTER a successful provider response reaches
`RetryBreakerFallbackDispatcher._run_per_candidate_attempts`, whose `_classify_provider_exception`
currently maps the signing failure types to `TRANSIENT_RETRY` — re-calling the provider for an
already-succeeded response (a duplicate external side effect) and polluting breaker/fallback state. And classification alone is
insufficient (round-11 P1): a TERMINAL outcome still returns an abandoned candidate, after which the outer
dispatch advances to the NEXT provider and records breaker failure — duplicating the external side effect
anyway and polluting breaker state. The delta must require audit-signing failures raised after a successful
provider response to BYPASS the classifier, breaker, and fallback machinery entirely (surface directly,
preserving the already-obtained result for the audit-failure report), or define another result-preserving
mechanism. Delta shape: OD v1.34 addendum (policy +
flag + site enumeration) **plus** CP v1.100 → v1.101 amending §28.10.4 (cite: v1.24, last substantive definition) invariant 2 with the audit-signing
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

- **Message-format cutover for pre-v1.34 REAL signatures** (round-5 P1): an upgraded KMS-backed MTC ledger
  holds GENUINE v1.33-era signatures over the four-segment message on rows that carry tenant tags —
  five-tuple reconstruction fails them, and the placeholder exemption does not cover them. The contract
  must version the message format via an authenticated cutover: pre-cutover real signatures verify against
  the four-tuple, post-cutover rows require the five-tuple.
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
  signed by a trusted key or anchored outside the rewritable ledger, AND to bind IMMUTABLE ledger
  identities (round-5 P1) — the exact legacy entry hashes or an externally monotonic ledger position, not
  merely a date/version/row-position (an adversary with rewrite access can forge an unsigned row "before"
  a positional boundary and recompute the unkeyed hashes while the external record stays untouched) —
  AND to bind each legacy identity to its ORIGINAL TENANT (round-6 P1): `tenant_tag` is mutable, tenant is
  absent from `entry_hash`, and pre-v1.34 real signatures cover only the four-tuple, so a bare entry-hash
  cutover still lets an authenticated legacy row be moved from tenant A to B. The record binds signed
  `(tenant_scope, entry_hash, verification_disposition)` TRIPLES (round-7 P1 — an upgraded ledger holds
  both pre-v1.34 REAL four-tuple signatures and older `unsigned:*` placeholders; a bare pair cannot tell
  the verifier which mode a listed row takes, and inspecting `signature_attrs` to decide reintroduces the
  forbidden downgrade — the disposition/message-format-version is part of the authenticated record), and
  the verifier compares the recorded scope against its tenant input; the round-46
  explicit-operator-action posture carries over, its carrier does not.
  A config-declared pre-backend KEY-PERIOD set is NOT a viable cutover mechanism (filing codex round-3 P2):
  both the placeholder era and the real-KMS era store `"DEPLOYMENT_BOUND"` / project `key_period=0`, so a
  period set either exempts every row or none; period-based cutover only becomes possible if B-33
  introduces distinct periods first.

### Council

Conditional, preserved verbatim from the register rows (filing codex round-2 — this filing does NOT resolve
whether verification may ever be BLOCKING): the recommended §21.2.2 contract is a non-blocking verify API
(seam shape settled by the B-22 precedent — no council needed for that half), but IF ratification makes
verification blocking anywhere (e.g. read-path enforcement), the C7-compliance ⊥ C1/C9-reliability dyad
convenes at the apply leg before that half lands. **And the non-blocking default must be RECONCILED with
C-CP-20 §20.3.1 (filing codex round-12 P1): that CP-owned contract already commits walking audit entries,
verifying every signature, and FAILING the audit on invalid signatures (semantics preserved through CP
v1.98) — ratifying a non-blocking OD API without touching §20.3.1 leaves canonical CP and OD requirements
contradictory. The CP rider must either bring §20.3.1 into scope (aligning its blocking audit-walk with the
new backend-aware API) or the OD API must conform to §20.3.1's fail-on-invalid semantics where that
protocol invokes it; the ratification gate decides.**

---

## Ratification gate (the ONE operator decision this filing surfaces)

Per §4.3 the design-substrate amendments halt here. The operator ratifies, in one decision:

1. **Leg 1 option 2** (fifth segment + tenant-bearing signing API rider, incl. the redaction-map path) — or
   names an alternative.
2. **Leg 2 two-spec shape** (OD flag + CP §28.10.4 carve-out, redaction path declared unconditionally
   fail-closed) vs the weaker single-spec alternative.
3. **Leg 3 acceptance** (filing codex round-2 — leg 3 needs its own explicit ratification, not a ride-along):
   the new C-OD-21 §21.2.2 backend verification API with its three contract requirements (message-format
   cutover so pre-v1.34 REAL four-tuple signatures keep verifying; tenant scope as verifier input;
   authenticated tenant-bound cutover-gated legacy exemption) and its NON-BLOCKING default — or an
   alternative/defer.
4. **Arc bundling** — one OD v1.33 → v1.34 delta carrying legs 1+3, with a CP v1.100 → v1.101 rider
   carrying BOTH CP-owned halves, **and a Runtime v1.100 → v1.101 rider (filing codex round-9 P1): the
   Runtime spec owns the prewarm/keepalive/boot contracts (B-18-KEEPALIVE lineage) that currently commit
   the swallow-all fail-open behavior, plus RuntimeConfig surface — the rider covers the MTC prewarm
   posture, the `audit_signing_fail_closed` flag's config contract, and the tenant threading through
   runtime-owned call sites; without it the implementation would contradict a committed Runtime surface
   (X-AL-3)** (recommended), vs splitting. The CP rider is not leg 2's alone (filing
   codex round-7 P1): `cp_audit_to_od_audit` is a CP-owned contract (`Spec_Control_Plane_v1_7.md` §13.5.1
   declares its signature), so leg 1's tenant-bearing converter signature change amends CP too — the rider
   carries the §13.5.1 signature amendment alongside the §28.10.4 invariant-2 carve-out.

On ratification: spec-writer apply pass (with the two dyadic council convenings at the apply leg), clearance
markers per §4.5, **and the Phase-6 plan deltas in the same arc (filing codex round-11 P2): the OD plan pins
U-OD-30 to the tenant-less `sign_audit_entry(payload, key_id, algo)` / `verify_hash_chain_integrity`
signatures (`Implementation_Plan_Operational_Discipline_v2_6.md` §U-OD-30, preserved through the v2.28 head)
and the plan lineage pins `cp_audit_to_od_audit` without tenant scope (v2.17), and the Runtime plan (v2.48
head) has no acceptance criteria for the new RuntimeConfig flag, bootstrap validation, handler policy,
prewarm/keepalive posture, or tenant threading — the apply arc carries OD, CP, AND Runtime plan deltas
(round-12 P2) — implementing against the
amended specs without clearing those plan deltas would leave the Phase-6 execution authority stale**, then
the register rows flip `design_substrate_gated` → open/buildable and the impl arc proceeds under the
standard pipeline. (The post-merge §12.2 terminating refresh repoints `roadmap_status.md`'s next-action at
ratification — that refresh PR is separate by the §12.2.1 content rule.)
