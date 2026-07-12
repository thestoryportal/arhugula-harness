# B-OD19-LOCAL-INSPECTION slice (c) — otelcol-contrib config manifest reconciliation

**Status:** CLOSED as documented residual (grounding-first close per the R-FS-2 register's own framing — "grounding question decides the unit").

## 1. The grounding question

C-OD-19 §19.1 (`Spec_Operational_Discipline_v1_2.md:1063-1073`, preserved verbatim into the
delta-only chain per v1.3 §0.1) commits:

> **Collector placement** — In-process `otelcol-contrib` instance running within the harness
> process. **No separate daemon** — operator does NOT run a separate collector daemon; collector
> lifecycle is bound to the harness lifecycle.

§19.1's `InProcessCollectorBinding` (`local_first_otlp_collector.py:128-141`) types this as
`exporter_class: Literal["OTLP_EXPORTER_IN_PROCESS_LOOPBACK"]` with `network_hop_required=False`.

An `otelcol-contrib` configuration manifest (receivers/processors/exporters YAML) configures a
real `otelcol-contrib` **binary process**. Slice (c)'s task was to ground whether the as-built
collector is that binary (in which case a manifest is a real, validatable artifact) or something
else (in which case a manifest configures nothing that runs, and the honest close is a cited
reconciliation note, per the plan's own "(c) manifest validates against the in-process collector,
or a cited reconciliation close").

## 2. What is actually built (verified this session)

Two disconnected subsystems exist under the OD/runtime axis, neither of which is an
`otelcol-contrib` binary:

1. **The real span-export path** (`harness_runtime/lifecycle/span_processor.py:77-79`
   `materialize_span_processor_stage`, U-RT-28): a `BatchSpanProcessor` backed by the standard
   `opentelemetry.exporter.otlp.proto.grpc.trace_exporter.OTLPSpanExporter`, exporting over
   **real gRPC to `config.otel.otlp_endpoint`** — a field with **no default**, documented at
   `harness_runtime/types.py:1490-1493` as "genuinely operator-specific and cannot reasonably
   default. Operators MUST provide either `[runtime.otel] otlp_endpoint = "..."` ... or pass via
   CLI override." This is a real network export requiring an operator-supplied external endpoint
   — the literal opposite of "no separate daemon" / `network_hop_required=False`.

2. **The in-process daemon** (`harness_runtime/lifecycle/collector_daemon.py`, U-RT-29): an
   asyncio-task supervisor with a placeholder in-memory `ingest_span_row()` method. Its own
   docstring (lines 34-42) states plainly: *"The OD `local_first_otlp_collector` library lands
   the policy... as pure functions; it does NOT land a real OTLP-gRPC server... The real
   OTLP-gRPC receiver wiring (so the U-RT-28 BSP → OTLPSpanExporter pipeline actually reaches this
   daemon) is deferred to a future Phase-2 runtime sub-unit."* Confirmed empirically this session:
   `ingest_span_row` has no production caller (grep across `harness-runtime/src` +
   `harness-od/src` finds only its own definition + tests); `stage_4_od.py:81` discards the
   `RingBufferStage` return value without retaining it on `HarnessContext`; `flush_to_sqlite` /
   `initialize_span_store` likewise have no production caller.

Neither subsystem is `otelcol-contrib`. §19.1's "in-process `otelcol-contrib` instance"
commitment is realized by neither — the real pipeline is a hand-rolled Python
supervisor-plus-library that never receives real spans, and the actually-running exporter is a
generic network gRPC client pointed at an operator-supplied external endpoint (which, if the
operator points it at a real `otelcol-contrib` they run themselves, is exactly the "separate
collector daemon" §19.1 says the operator does NOT run).

## 3. Disposition

**No manifest artifact is authored.** Writing an `otelcol-contrib` receivers/processors/exporters
YAML would configure a binary that is not part of this codebase's runtime path today — it would
be documentation of a hypothetical future integration, not an artifact "validating against the
in-process collector" (there is no in-process collector binary to validate against). Authoring
one now would be the "half-proof" / "wired-handler-unreachable" failure pattern this workspace's
memory explicitly warns against (`[[wired-handler-unreachable-two-halves-of-one-mechanism]]`,
`[[full-chain-witness-not-half-proofs]]`) — a manifest with nothing on the other end.

**This is a pre-existing, already-documented deferral, not a new defect.** Both
`collector_daemon.py` (lines 34-42) and `local_first_otlp_collector.py` (module docstring,
"Phase 1/2 boundary") already name the OTLP-gRPC-receiver-into-the-daemon wiring as a deferred
Phase-2 runtime sub-unit. B-OD19 was never scoped by the R-FS-2 register to build that receiver —
its three slices (browser / rotation / manifest) are explicitly acceptance-tested against
**seeded** ring-buffer data (plan: "browser walks a *seeded* ring buffer"; "rotation witness
(fill → rotate → chain-readable)"), not against live production span flow. Slices (a) and (b) in
this arc are built and tested against that seeded-data bar and do not claim to make live traces
browsable.

**Recorded residual (surface at the Wave-4 batched AUQ per the R-FS-2 register, not a blocking
ask mid-arc):** the in-process collector commitment (§19.1) will not be genuinely realized until
either (i) a real in-process OTLP receiver is built so the BSP → OTLPSpanExporter pipeline reaches
`CollectorDaemonSupervisor.ingest_span_row`, or (ii) the exporter is swapped for an in-process
loopback transport that doesn't require an operator-supplied network endpoint. Until then: the
inspection tooling built in this arc (harness-inspect extensions, TUI browser) operates correctly
against whatever the sqlite span store contains, but nothing in production writes real spans
there yet. This is an honest scope boundary, not a silent gap — operators should not be told they
can browse live traces today.

## 4. Citations

- `Spec_Operational_Discipline_v1_2.md:1063-1099` §19.1/§19.2/§19.3 (preserved verbatim per v1.3
  §0.1; canonical HEAD `Spec_Operational_Discipline_v1_30.md` is delta-only and does not re-table
  §19).
- `harness-od/src/harness_od/local_first_otlp_collector.py` (module docstring "Phase 1/2 boundary";
  `InProcessCollectorBinding`).
- `harness-runtime/src/harness_runtime/lifecycle/span_processor.py:1-79` (U-RT-28, real gRPC
  exporter).
- `harness-runtime/src/harness_runtime/lifecycle/collector_daemon.py:34-42` (U-RT-29, deferred
  receiver).
- `harness-runtime/src/harness_runtime/types.py:1487-1493` (`OTelConfig.otlp_endpoint` required,
  no default).
- `.harness/r-fs-2-final-closure-implementation-plan-v1.md` §3 B-OD19-LOCAL-INSPECTION register
  entry (acceptance criteria are seeded-data-scoped).
- `.harness/class_1_tension_u_rt_30_trace_storage_pathclass_gap.md` (RESOLVED 2026-05-20, Path B —
  unrelated to this residual; confirms the sqlite-path X-AL-3 concern is already cleared and does
  not gate slice (b)).

Filed 2026-07-12 as part of the B-OD19-LOCAL-INSPECTION arc (R-FS-2 Wave 2, third arc).
