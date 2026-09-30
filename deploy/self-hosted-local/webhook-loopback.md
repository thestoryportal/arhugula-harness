# Local HITL webhook binding

The first Omarchy profile can deliver a HITL escalation to an operator receiver on the same VM. Supply all three fields in `harness.toml`:

```toml
[runtime.webhook_delivery_composer_config]
webhook_id = "local-approval"
endpoint_url = "http://127.0.0.1:8723/hitl"
timeout_seconds = 3
```

The receiver must bind to `127.0.0.1` (or `::1` with a bracketed URL) and handle an HTTP `POST` with an `Idempotency-Key` header. Start it before the harness. The harness makes one HTTP attempt with a 1–5 second deadline as configured and fails closed on delivery failure. Audit attribution and shutdown occur outside that HTTP deadline. The HTTP client ignores proxy environment variables and does not follow redirects. Configure a receiver that deduplicates requests by the idempotency key; one attempt does not guarantee exactly-once receipt across process failure.

Only literal `127.0.0.1` and `::1` HTTP URLs with an explicit port and simple path are accepted. DNS names, `localhost`, LAN/public/metadata addresses, URL credentials, queries, fragments, TLS and remote delivery are outside this profile. The URL is hashed before cost attribution, so its path is absent if signed cost records are enabled. This hash is not a secrecy mechanism for short paths. `webhook_id` is a public, non-secret label; do not put credentials in it or in the URL. Loopback alone does not authenticate the receiver: another local user could bind the port first. Use a single-user host or add a separately reviewed authentication and receiver-ownership contract before exposing sensitive approvals.

Omit the entire `[runtime.webhook_delivery_composer_config]` table to keep webhook delivery off. The legacy empty marker may still bind an unconfigured composer for older integrations, but it is refused at bootstrap whenever a pause protocol is bound. A working HITL flow needs the complete local endpoint configuration, a running receiver, and separate end-to-end acceptance. The component-level loopback checks do not establish a full operator response or recovery workflow.
