# B-MCP-OAUTH-RS-ENFORCE — remote-MCP L2/L3 OAuth resource-server validation

**Status:** CLOSED as deployment-binding-honored (Branch A per the R-FS-2 register's own framing — "grounding question decides the unit").

## 1. The grounding question

Per `.harness/r-fs-2-final-closure-implementation-plan-v1.md` §4 and the arc-ledger `anticipated_scope`:

1. Does AS spec C-AS-10 §10.3's "Deferred to implementation discretion" block make connection-time OAuth-RS validation one of the deferred-but-owed implementation details, and does any committed sentence make L2/L3 connection *conditional* on OAuth-RS status?
2. Does any streamable-HTTP client path exist at `mcp_client_host_factory.py` (the register's premise: "the external-MCP live e2e proved stdio only")?

## 2. What is actually committed (verified this session)

**Trust level is operator-declared, not harness-verified.** `Spec_Action_Surface_v1.md` §10.3 (line 934): *"The MCP server trust level is operator-declared at MCP server registration; trust-level assignment is recorded in the audit ledger."* This is the load-bearing sentence: the harness's committed contract is that the **operator vouches** for a server's trust tier at registration time. A harness-side live OAuth 2.1 / PKCE / RFC 8707 verification step would be a *second, independent* trust-establishment mechanism that nothing in C-AS-10, ADR-D2 §1.3, or ADR-D3 commits — those documents cite the *external* MCP authorization spec's OAuth-2.1-Resource-Servers-mandatory clause as **rationale** for why the STDIO floor is `tier-3-microvm` (protocol-level auth is unavailable there) and why L1/L3 sandbox-tier can float on `blast_radius_floor` (protocol-level auth is assumed present there) — never as an instruction for our client to itself perform the handshake or refuse absent it.

**The two mechanisms the harness *does* commit to build are both already built:**
- **Sandbox-tier floor** (§10.1, `harness_as/mcp_transport_floor.py`) — keyed on the operator-declared `trust_level`.
- **HITL gate-level floor** — committed and landed separately at `.harness/class_1_fork_b2_spec_2_gate_axis_materialization.md` (CP spec v1.35 §19.1.2): the per-server trust axis was explicitly identified as a **genuine dyadic C10⊥C11 tension** (does higher trust *loosen* the gate, or only *raise floors*?), taken to a real council, and **probe-resolved floor-only/monotone** with an operator-ratified Table A (L0→DENY / L1→ASK / L2→ASK / L3→AUTO). This is the closest this workspace has come to the exact tension B-MCP-OAUTH-RS-ENFORCE's Branch B would reopen, and it already closed without inventing a live-verification requirement.

The C-AS-10 §10.3 "Deferred to implementation discretion" block (line 938) lists exactly four discretionary items — registration mechanism, Level-1 signature-verification implementation, Level-2 egress allow-list schema, Level-3 audit cadence — **and OAuth-RS validation is not among them**, because it was never committed as a harness build target in the first place, not because it is silently owed.

**Conclusion: no committed conditional exists.** This is a Branch A close.

## 3. Correcting the register's stale premise (Class-3 note, no fork)

The register framed Branch A as resting on *"fail-closed today: L0_REFUSE + no HTTP path = structurally can't connect un-validated"* — i.e., it assumed no remote-HTTP client exists yet. **That premise is false and dates from before `B-MCP-HOST-REMOTE-TRANSPORT`:**

- `MCPClientHost._http_connection_context()` (`mcp_client_host.py:479-508`) is real, wired code, not a stub — it imports and calls `mcp.client.streamable_http.streamable_http_client(url)`.
- A real, production-factory-path e2e exists: `test_r_cl_p3_live_multi_tier_e2e.py` builds a genuine `MCPClientConfig(transport=MCPTransport.STREAMABLE_HTTP_L1_PINNED, connection_url=mcp_url, ...)` and runs it through `materialize_mcp_client_host_stage` against a real local HTTP MCP server (`fixtures/streamable_http_echo.py`) — no test-injection seam (`_connection_factory`) involved. (This test is `skipif`-gated on a local Ollama daemon and was not executed this session; the code-path wiring was verified directly by import + call, not inferred from the test's docstring.)
- L0 refuse-remote enforcement **is** real and was verified directly (not via docstring): `materialize_mcp_stage` (`mcp_host.py:87-114`) calls `mcp_transport_floor(...)` and raises `MCPServerRefusedError` when the outcome is `REFUSE`.

So the correct framing is: **Branch A closes because no conditional is committed, not because a remote connection is structurally impossible.** An operator can and does connect to an L1-declared remote server today; L2/L3 would resolve the same way (sandbox-floor + gate-floor keyed on the declared tier), with the caveats in §4 below.

## 4. Two real gaps found and registered (not built here — out of this arc's scope)

Building an OAuth-RS *refusal* gate without a working credential-*supply* path would simply fail every real remote connection, so these are registered as forward items rather than pulling this arc to Branch B:

1. **`_http_connection_context` imports the legacy `streamable_http_client`, not the modern `streamablehttp_client`.** Verified directly (not by inspection of one name): `mcp.client.streamable_http` exports **two distinct functions** — `streamable_http_client(url, *, http_client=None, terminate_on_close=True)` (legacy, no `headers`/`timeout`/`sse_read_timeout`/`auth` params) and `streamablehttp_client(url, headers=None, timeout=30, sse_read_timeout=300, terminate_on_close=True, httpx_client_factory=..., auth=None)` (current). The production code at `mcp_client_host.py:495` imports the **legacy** one but its own docstring (lines 489-493) and its `kwargs` assembly (lines 500-506) claim to forward `headers`/`timeout`/`sse_read_timeout` — parameters the legacy function does not accept. This does not crash *today* only because `_build_transport_config` (factory) never populates those keys (returns bare `{"url": ...}`), so `kwargs` is always empty on the production path. The moment anything populates `headers`, this raises `TypeError`.
2. **`MCPClientConfig` has no field to carry auth credentials at all.** Its own docstring claims *"Real connection URL + auth-secret reference are operator-supplied"* but there is no `headers`, `auth`, or secret-reference field on the model (`types.py:618-644`) — only `connection_url: str`. Combined with (1), there is currently **no way, even manually, to supply an OAuth bearer token or any other credential to a remote MCP connection.**

Registered at `.harness/post-phase-8-forward-register.md` (or the live `arc-ledger.yaml` `registered` queue) as a follow-on, decomposable at whichever arc next touches remote-MCP credential supply — most naturally alongside a future OAuth *client* build (token acquisition + attachment), which is a different mechanism from this arc's refusal-gate question and from `B-MCP-PRIMITIVE-SIG-GATE` (tool-description-hash rug-pull protection, a distinct mcp.primitive.signature.sha256 mechanism, confirmed by reading its own anticipated_scope).

Level 1 "signed-pinned" having no actual signature-verification code is **not** a gap — it is exactly what C-AS-10 §10.3's own deferral block names as discretionary and not-yet-built.

## 5. Verification

- `mcp.client.streamable_http.streamable_http_client` vs `streamablehttp_client`: distinct function objects, distinct signatures, confirmed via `inspect.signature` in the workspace venv (`uv run --package harness_runtime python3 -c ...`).
- `MCPServerRefusedError` raise site: `mcp_host.py:112`, read directly.
- `_http_connection_context` body: `mcp_client_host.py:478-508`, read directly.
- `MCPClientConfig` fields: `types.py:618-657`, read directly.
- AS spec §10.3 operator-declared-trust sentence: `Spec_Action_Surface_v1.md:934`, read directly.
- B2-spec-2 gate-axis resolution: `.harness/class_1_fork_b2_multi_server_mcp_client_reshape.md` §5, read directly.
- No MCP-specific OAuth/PKCE/RFC-8707/RFC-9728 implementation exists anywhere in `harness-runtime`/`harness-as`/`harness-cp`/`harness-core` (the only `oauth`-matching files are the unrelated LLM-provider-CLI OAuth routing at `lifecycle/providers.py` / `lifecycle/external_cli_provider.py`, R-300 territory).
- `advisor()` consulted before finalizing this closure argument; its two empirical challenges (verify the exact import line rather than trust the docstring; ground the close in the affirmative "trust is operator-declared" reading rather than an absence claim) are both incorporated above.

## 6. Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/b-mcp-oauth-rs-enforce-closure-record.md` |
| Arc | `B-MCP-OAUTH-RS-ENFORCE`, R-FS-2 Wave 3, first arc |
| Disposition | CLOSED — Branch A (deployment-binding-honored) |
| Authority | AS spec C-AS-10 §10.3; ADR-D2 v1.2 §1.3; ADR-D3; `.harness/class_1_fork_b2_multi_server_mcp_client_reshape.md` §5 |
| Forward items registered | (1) wrong streamable-HTTP-client import name (dead kwargs path); (2) `MCPClientConfig` has no credential-supply field |
| No spec/code change | This is a grounding-only close; the two forward items above are registered, not fixed, in this arc |

*End of B-MCP-OAUTH-RS-ENFORCE closure record.*
