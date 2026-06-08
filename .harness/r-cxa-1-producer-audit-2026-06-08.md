# R-CXA-1 AS→IS Producer Audit — 2026-06-08

## Result

No new wireable AS→IS producer exists at HEAD `883a991a`.

R-CXA-1 remains `PARTIAL`: the AS→IS runtime composer exists and is tested, but no production runtime caller invokes `RuntimeAsIsWiring.emit_secret_fetch_audit_entry(...)`.

## Evidence

Production references to `emit_secret_fetch_audit_entry`, `emit_secret_fetch_audit`, `SecretFetchEvent`, and `compose_secret_fetch_audit_entry` are definition-only:

```text
harness-as/src/harness_as/secret_fetch_emission.py:80:def emit_secret_fetch_audit(
harness-as/src/harness_as/secret_fetch_emission.py:102:    compose_secret_fetch_audit_entry(event_metadata, None)
harness-as/src/harness_as/secret_fetch_audit.py:45:class SecretFetchEvent(BaseModel):
harness-as/src/harness_as/secret_fetch_audit.py:76:def compose_secret_fetch_audit_entry(
harness-runtime/src/harness_runtime/lifecycle/as_is_wiring.py:96:    def emit_secret_fetch_audit_entry(
```

Production scope-bearing secret resolver calls are also absent from runtime call sites. `ProviderSecretResolver.resolve(...)` is implemented by the resolver backends, while stage-3a provider bootstrap still calls `resolve_bootstrap_value(name)` for literal SDK API-key construction.

The only production `fetch_secret(...)` consumer is CP F5 signing-key resolution, which is CP→AS and does not produce the AS→IS secret-fetch audit event:

```text
harness-cp/src/harness_cp/f5_signing_key_resolution.py:134:        scope=SecretScope(name=scope.scope_identifier),
```

Overlay grounding:

```text
just overlay-query --unit U-AS-27
{
  "unit": "U-AS-27",
  "files_citing": [
    "file:harness-as/src/harness_as/as_substrate_seam_exports.py",
    "file:harness-as/src/harness_as/secret_fetch_emission.py",
    "file:harness-runtime/src/harness_runtime/lifecycle/as_is_wiring.py"
  ],
  "cxa_seams": []
}
```

## Disposition

Do not wire bootstrap provider-key fetches into `emit_secret_fetch_audit_entry(...)`: they still use the name-only `resolve_bootstrap_value(...)` path and lack the scope, rotation, thread, and step identity needed for a non-hollow `SecretFetchEvent`.

Re-open R-CXA-1 only when one of these appears:

- a real production scoped `ProviderSecretResolver.resolve(name, scope, tier, ...)` call site with caller context sufficient to compose `SecretFetchEvent`
- a real AS secret-fetch driver path that invokes `RuntimeAsIsWiring.emit_secret_fetch_audit_entry(...)`
- a design/back-flow amendment that changes the `SecretFetchEvent` contract so bootstrap provider-key fetches are no longer hollow
