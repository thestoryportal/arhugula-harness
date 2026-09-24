# Local HITL webhook binding

The first Omarchy profile can deliver a HITL escalation to an operator receiver on the same VM. Supply all three fields in `harness.toml`:

```toml
[runtime.webhook_delivery_composer_config]
webhook_id = "local-approval"
endpoint_url = "http://127.0.0.1:8723/hitl"
timeout_seconds = 3
```

The receiver must bind to `127.0.0.1` (or `::1` with a bracketed URL) and handle an HTTP `POST` with an `Idempotency-Key` header. Start it before the harness. The harness makes one attempt, waits at most 1–5 seconds as configured, and fails closed on delivery failure. The HTTP client ignores proxy environment variables and does not follow redirects. Configure a receiver that deduplicates requests by the idempotency key; one attempt does not guarantee exactly-once receipt across process failure.

Only literal `127.0.0.1` and `::1` HTTP URLs with an explicit port and simple path are accepted. DNS names, `localhost`, LAN/public/metadata addresses, URL credentials, queries, fragments, TLS and remote delivery are outside this profile. The URL is hashed before cost attribution so its path is absent from signed cost records. `webhook_id` is a public, non-secret label; do not put credentials in it or in the URL.

Omit the entire `[runtime.webhook_delivery_composer_config]` table to keep webhook delivery off. The legacy empty marker may still bind an unconfigured composer for older integrations, but it is refused at bootstrap when durable pause is enabled. A working durable HITL flow needs the complete local endpoint configuration, a running receiver, and separate end-to-end acceptance. The component-level loopback checks do not establish a full operator response or recovery workflow.
