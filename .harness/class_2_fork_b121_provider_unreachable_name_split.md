# Class 2 Fork — B-121: `LLMDispatchProviderUnreachableError` / `RT-FAIL-PROVIDER-UNREACHABLE` names a registry miss, and the C-RT-14 token is genuinely heterogeneous

**Status: FILED 2026-08-12; scope decision routed to the loop-mode U-HK-13 decorrelated
resolver per the B-144 precedent (`[[probe-resolves-fork-prescribed-council]]` — the row's
"Class 2 fork" routing names the channel, not an operator AUQ; the decision is reversible
in-repo).** Bundled-absorption chain per root `CLAUDE.md` §11.4: this filing + the Runtime
spec delta + the code rename land in ONE PR with the clearance marker as the paired
back-flow doc (the #1310/#1311 shape).

**Register row.** `B-121` (`status: registered_finding`; summary + close_out carry the full
raise-site count and the B-116 defect-vector history — C9's recorded self-correction: the
type's NAME misled the fork filing's §5 table and all four council voices until adversarial
finding F-01 demoted it on raise-site evidence).

**Grounding HEAD.** `fe7ef29b` (post-#1316). Close-out step (1) re-verified at this HEAD:
exactly THREE `raise LLMDispatchProviderUnreachableError` sites, all in
`harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py` — `:1562`
(`provider_name not in self.providers`, an in-process dict), `:1586`
(`_PROVIDER_OPERATIONS.get(...) is None`, self-described "Defensive"), `:1902` (the
terminal `else` of the isinstance adapter-arm chain). **None contacts a provider.** The
class docstring (`:184-193`) says so itself: "resolves to a provider absent from
`ctx.providers`". The falsifier ("a fourth raise site that does contact a provider") did
NOT fire at the raise-site level.

## The fork: the spec token is heterogeneous — the falsifier fires at the SPEC level

C-RT-14's `RT-FAIL-PROVIDER-UNREACHABLE` row (`Spec_Harness_Runtime_v1.md:4007`) declares
the **stage-3a network sense**: "Stage 3a CP_CLIENTS (after RT-FAIL-TRANSIENT escalation) —
operator fixes network/provider availability", fed by `:3335` ("Initial async ping fails
with network error … persistent → escalation to … RT-FAIL-PROVIDER-UNREACHABLE"). That
sense DOES mean unreachable, and stage-3a code realizes no typed error for it (only
`ProviderAuthError`/`ProviderDegradedWarning` map at `providers.py:46-47` — the
UNREACHABLE escalation is spec-prose).

C-RT-15 then **reuses the same token for the registry miss** (`:4120` "raises
RT-FAIL-PROVIDER-UNREACHABLE … if provider resolves to a provider not in ctx.providers";
`:4129` the taxonomy row "provider not in ctx.providers"; `:4309` wrapper propagation;
`:7052` the "no new RT-FAIL-*" conformance row) — the UNREGISTERED sense, which is what
the Python type and all three raise sites implement.

One token; two semantics; the misleading half is the operator-facing one
(`step-failure: RT-FAIL-PROVIDER-UNREACHABLE: …` for a config/registration fault steers
the operator at the worst moment toward network debugging — the demonstrated B-116
defect vector).

## Options (the Class 2 decision)

- **(a) Rename the Python type only.** Cheapest; leaves every operator-facing
  `step-failure:` token misleading — the register row itself judges that "most of the
  harm". Rejected as the primary unless the resolver splits.
- **(b) Blanket-rename the token** `RT-FAIL-PROVIDER-UNREACHABLE` →
  `…-UNREGISTERED`. WRONG: corrupts the legitimate stage-3a network sense at
  `:3335`/`:4007`.
- **(b′) SPLIT (recommended).** Mint `RT-FAIL-PROVIDER-UNREGISTERED` (permanent,
  per-dispatch) at the C-RT-14 taxonomy; re-map the four C-RT-15 registry-sense mentions
  (`:4120`, `:4129`, `:4188` comparative clause, `:4309`) to it; keep
  `RT-FAIL-PROVIDER-UNREACHABLE` for the stage-3a network sense (`:3335`/`:4007`
  untouched); qualify the `:7052` conformance row (C-RT-15 consumes the new C-RT-14
  class — the reuse claim is re-stated against the post-split set); rename the Python
  type `LLMDispatchProviderUnreachableError` → `LLMDispatchProviderUnregisteredError`
  with the `step-failure:` prefix following. Exactly the B-116 "member-#2 shape" the
  close-out predicted for a heterogeneous type: a split, not a rename.

**Not re-litigated (close-out step 4):** B-116 member #1's demotion stands on raise-site
evidence regardless of naming.

**Sibling (close-out step 5):** `B-122` (bootstrap discoverability) CLOSED at #1316 as a
stage-3b startup diagnostic; its warning text names the exception and is updated in the
same cascade.

**X-AL-3.** The new token is a C-RT-14 design-substrate change — routed HERE, before code,
per the row's close-out step (3); the spec delta + this filing + clearance marker are the
paired back-flow docs for the bundled-absorption PR.
