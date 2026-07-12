# B-MCP-PRIMITIVE-SIG-GATE — `mcp.primitive.signature.sha256` registration-time verification gate

**Status:** CLOSED as research-only-gate / attribute-complete (Branch B per the R-FS-2 register's own framing — "grounding question decides the unit").

## 1. The grounding question

Per `.harness/r-fs-2-final-closure-implementation-plan-v1.md` §4 and the arc-ledger `anticipated_scope`: the 7-attribute `mcp.*` namespace including `mcp.primitive.signature.sha256` is canonical and emitted. Does anything commit a **registration-time verification gate** (rug-pull protection: persist a first-seen hash, refuse on mismatch), or is the attribute observability-only?

## 2. What is actually committed (verified this session)

**The contract surface itself is observability-only.** `Spec_Action_Surface_v1.md` §14 (C-AS-14) states its own contract surface plainly: *"Six attribute namespaces + per-namespace attribute enumeration + per-namespace sampling discipline + audit-floor commitments."* Its PRD linkage is explicit: **R-AS-07 (Anthropic-primitive adoption depth — *observability emission half*)**. Every cite of `mcp.primitive.signature.sha256` across AS spec §14.3, ADR-D2 (line 456, cataloging "MCP tool poisoning; rug-pull" as a **failure mode**, not a build commitment), and ADR-D3 (lines 281/329/566) frames the attribute the same way: **"tool-poisoning *detection*"** — never verification, prevention, or a registration-time refusal.

**The committed detection mechanism is the always-sampled telemetry, not an in-line gate.** §14.8's audit-floor commitment fixes `mcp.tool.call` at `head=1.0 with tail-keep-on-trust-tier-floor-violations` — every dispatch's hash lands in the trace unconditionally. Downstream trace analysis (comparing a primitive's hash across calls over time) *is* the designed detection method. An in-process registration-time gate would be **redundant** with this committed telemetry-based detection, not required by it — this is why the attribute is observability-only **by design**, not by omission. Tamper-*evidence* (a forensic trail a human/system can audit later) is the committed floor; tamper-*prevention* (an active connection/dispatch-blocking check) is a distinct, uncommitted mechanism.

**Affirmative absence check (not just a keyword-miss).** Grepped the AS spec directly for the enforcement verbs (`reject`/`refuse`) near any hash/signature/mutation concept, not just the detection nouns: every "reject"/"refuse" hit in the spec is unrelated to this question — `minimum_tier` missing at authoring time (C-AS-03 §3, not registration mutation), MCP-server-connection `REFUSE` at trust-level-0 registration (C-AS-10, already covered by `B-MCP-OAUTH-RS-ENFORCE`), `search_tools` name reservation (C-AS-13), and `schema_violation` (a per-call response-vs-declared-output-schema mismatch, not a definition-mutation check). None attaches an enforcement verb to `mcp.primitive.signature.sha256` or a first-seen-hash comparison.

**The arc register's own pointer to "C-AS-03 registration contract" is a mis-cite.** C-AS-03 §3 is "Per-tool `minimum_tier` authoring-time declaration" — unrelated to primitive-registration mutation detection. No other spec section commits a registration-mutation gate either (confirmed by the absence check above), so this doesn't change the disposition, but it's worth correcting for future citers.

## 3. Attribute-complete, verified by execution (not by docstring)

The attribute is not merely declared — it is computed on a real, reachable path and asserted present on a real emitted span:

- `runtime_tool_dispatcher.py:1212` `_compute_primitive_signature_hash(name, input_schema, output_schema)` — sha256 over the primitive's name + sorted-JSON input/output schema, computed **fresh at every dispatch** (no persistence, no first-seen store, no comparison — confirmed by reading the function body directly).
- Called at `runtime_tool_dispatcher.py:1050`, threaded into `mcp_client_namespace_emitter.py:204`'s `span.set_attribute(ATTR_MCP_PRIMITIVE_SIGNATURE_SHA256, signature_hash)` — the emitter itself only stamps a caller-supplied value; it does not compute, store, or compare hashes either.
- **Reachability witness:** `test_u_rt_86_mcp_client_external_server_e2e.py:349-353` asserts the full 7-attribute `mcp.*` set — including `mcp.primitive.signature.sha256` — is present on a span from a **real external stdio MCP server subprocess** (the same test R-800 cites as "unconditional, no LLM, 9/9 green"). No `skipif` marker in this file — this is not credential-gated, it runs in CI today.

**`ToolRegistry.register` (`tool_registry.py`) confirms no mutation-detection gate exists anywhere in the registration path** — it guards exactly two conditions (`DuplicateToolNameError` for a repeated `client_name`, `ReservedToolNameError` for the `search_tools` name collision), neither of which is a content-hash check.

## 4. Disposition

**Branch B: research-only-gate / attribute-complete, closed with cites.** Building an active first-seen-hash-persistence + mismatch-refusal gate now would be an **uncommitted new mechanism** (spec commits an attribute for detection via telemetry, not an enforcement gate) — building it would be X-AL-3 silent design extension, not a Phase-7 implementation of an existing commitment.

**Forward item (not built, registered for symmetry with FULL-SPEC discipline).** If the operator ever wants **active** rug-pull prevention (not just forensic detection), the natural shape — matching the arc register's own sketch — is: persist the first-seen `signature_hash` per primitive in `ToolRegistry`; on a later registration/dispatch where the recomputed hash disagrees with the stored first-seen value, emit a violation (composing with the existing fail-class/violation-event shapes at C-AS-04/C-AS-08) and fail closed per the resolved gate level. This is a genuinely new committed behavior, not a Phase-7 gap-fill — it would need a Class 1 fork to `design-substrate/Spec_Action_Surface_v1.md` §14 before implementation, per X-AL-3.

## 5. Verification

- C-AS-14 contract-surface framing + PRD linkage: `Spec_Action_Surface_v1.md` lines 1246-1256, read directly.
- All `mcp.primitive.signature.sha256` cites across AS spec / ADR-D2 / ADR-D3: grepped and read in context (`design-substrate/Spec_Action_Surface_v1.md:1292,1739`; `design-substrate/ADR-D2.md:456`; `design-substrate/ADR-D3.md:281,329,566`).
- §14.8 audit-floor sampling commitment: `Spec_Action_Surface_v1.md` lines 1347-1368, read directly.
- Affirmative enforcement-verb absence check: `rg "SHALL verify|MUST verify|reject|refuse" -i design-substrate/Spec_Action_Surface_v1.md`, every hit read in context.
- `_compute_primitive_signature_hash` body (no persistence/comparison): `runtime_tool_dispatcher.py:1212-1225`, read directly.
- Emitter call-site (stamps caller-supplied value only): `mcp_client_namespace_emitter.py:184-204`, read directly.
- Reachability/attribute-complete witness: `test_u_rt_86_mcp_client_external_server_e2e.py:249,349-353`, read directly; no `skipif` marker in the file (grepped).
- `ToolRegistry.register` guard conditions: `tool_registry.py` `DuplicateToolNameError`/`ReservedToolNameError` sites, read directly.
- `advisor()` consulted before finalizing; its two challenges (verify attribute-complete by execution/test-cite rather than call-site reading; lead with the affirmative "telemetry-based detection is the committed mechanism" framing rather than an absence claim) are both incorporated above.

## 6. Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/b-mcp-primitive-sig-gate-closure-record.md` |
| Arc | `B-MCP-PRIMITIVE-SIG-GATE`, R-FS-2 Wave 3, second arc |
| Disposition | CLOSED — Branch B (research-only-gate / attribute-complete) |
| Authority | AS spec C-AS-14 §14.3/§14.8; ADR-D2 (failure-mode catalog, line 456); ADR-D3 (attribute-set commitment, lines 281/329/566) |
| Forward item registered | Active registration-time first-seen-hash mismatch gate — NOT built, would require a Class 1 fork before implementation |
| No spec/code change | Grounding-only close; the forward item above is registered, not fixed, in this arc |

*End of B-MCP-PRIMITIVE-SIG-GATE closure record.*
