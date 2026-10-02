# Omarchy production profile: scope and proof policy

Ticket: `arhugula-harness-trial-193`. Decision date: 2026-09-24. This is the acceptance contract for the first self-hosted Omarchy release, not a release approval. At the initial profile decision, the isolated source candidate was `4dc8476` (strict-offline local L2 source and profile-bound corpus atop B2 public-only inspect, diagnostics correction, the test-only CLI fixture and B1c signer work); the independent contract review used prefix `73e7f06`, before the B1b signer integration. The current clean integrated candidate is `0afafca5dad33b5618a585815ec758d5daee4991`; signer enablement and VM/product-main landing remain held. The frozen trial baseline remains `87c29817`. Evidence from the earlier 6c trial does not transfer to the candidate.

## In scope

- Local Ollama inference, including one-shot runs, fallback/retry, manifest bindings and the L3 router, memory, local L2 embedding, and the advertised six workflow topologies. A source fixture or fake model response alone does not accept a live inference claim. Local L2 needs hash-recorded model files in a stated cache location, an offline installation recipe and a no-network candidate witness.
- Claude Code and Codex subscription CLI inference routes. Each needs an installed candidate run and a security boundary disposition. The existing one-request Claude `READY` witness proves compatibility only; Codex read exposure remains a release hold.
- Local daemon supervision and concurrent clients, long quiet workflows, shutdown cleanup, and HITL pause/resume and elicitation. Required operator surfaces include CLI/MCP cross-process resume, an explicit pause trigger, inbound HTTP answer delivery, a daemon-client elicitation callback, and shipped opt-in configuration and documentation.
- Self-hosted Docker tier 2, gVisor tier 3, OTLP/Tempo/Grafana delivery, tenant isolation and redaction. Static configuration checks do not accept the live stack.
- Local audit chain/signing, key management, protected state, packaging, install/upgrade, recovery, performance, security operations and a usable runbook. The local signer remains disabled until B1/B2 and installed restart/tamper evidence pass.

## Explicit first-release exclusions

- Paid hosted model APIs and managed E2B, S3, database, and KMS services.
- Antigravity, Gemini and generic-command inference routes unless deliberately added to this profile with separate security and installed live evidence. Their code may exist; they are not release claims.
- Runtime download of an unpinned remote L2 embedding model. The pinned offline local embedding path is in scope above.

## Durable HITL resume contract decision

On 2026-09-24 the operator ratified an amendment to B-104 Reading D for this first Omarchy release: durable HITL resume must use at-most-once admission, with an audited manual recovery path after a crash. The earlier replay-permitting Reading D is not the accepted first-release behavior. This decision retains the full HITL operator surface listed above; it does not exclude pause, answer, or cross-process resume.

The operator subsequently adopted the exact first-release terms in [the reviewed B-104 amendment proposal](b104-operator-amendment-proposal-1.md) (SHA256 `b3ca465ec67a88b4f68a45662e49694659d22551aa0d8a7cf5205be25145de29`; LIT `cmt-00d96fe1-8671-4eeb-bc32-d0a522ac5449`). The proposal's two restrictive errata are part of the ratified contract: evidence repair cannot create or alter a lease, and no-token claims use record-level abandon. Direct resume of depth-greater-than-zero child records is refused; parent resume must claim each child. Crash recovery requires an operator attestation that all harness services and workers, including timeout survivors, are stopped. Lost evidence under an audit INTENT remains visibly held. State lives outside every Git checkout or restore scope. The versioned recovery audit joins the C-IS-05 chain and C-IS-07 gains durable payload-comparing append. The one-host, one-trusted-UID POSIX boundary and permanent-hold failure modes also apply.

This is a ratified behavior contract, not an implementation acceptance. The isolated claim code is unaccepted, and no installed pause/answer/resume or crash-recovery witness has passed. This decision does not activate the signer, authorize a VM landing, or declare any gate complete.

## Parent PRE_ACTION placement inheritance decision

On 2026-09-24 the operator chose **“Yes, inherit matching placements”** for the first Omarchy release. A descended child must carry its parent's PRE_ACTION approval placements as additional constraints on matching actions. Preserve each parent's tool filter and placement policy; keep the child's own placements. Omitting a placement in the child, or declaring a narrower one, must not remove a matching parent trigger. Apply the same rule through further child descent. The exact merge, deduplication and resume carrier need a CP/Runtime spec delta and independent review before implementation. Current candidate behavior has not passed this requirement.

## Acceptance rules

1. All included behavior must be tested from the same installed release candidate on this Omarchy VM. Unit/fake-process tests establish implementation behavior but never substitute for a live model, Docker, or telemetry witness.
2. The installed `harness` executable must report shell exits 0 through 5 for the corresponding result classes, and the operator docs must describe all six. Help 0 and config 3 were witnessed on earlier candidate `f7b519e`; manifest parse 2 and daemon connection 4 were witnessed on `73e7f06`. Run-result 0/1/5 remains open. `docs/how-to-operate-runtime.md` currently lists only 0 through 4. The earlier subprocess test timeout is a bounded test-harness investigation, not a product failure conclusion.
3. Every historical matrix-16 skip must resolve to an explicit exclusion or a candidate replacement witness. The old 13 PASS / 25 SKIP snapshot is preserved as prior-lineage evidence only.
4. No live test is accepted without its exact candidate commit, installed artifact identity, environment, command, observed result and sealed evidence. Evidence at a candidate prefix is reviewed for impact and rerun when later product changes touch the tested path; the final matrix must run on the final installed artifact. No VM landing occurs during evaluation.
5. A gate with an unmet in-scope criterion remains open. Host-dependent Docker and quiet-Ollama checks stay held until their prerequisites are available; they cannot be waived by elapsed time.
6. Numeric latency, throughput, recovery and soak targets must be fixed before Gate 5 measurements, then measured on the declared host and workload profile. A passing functional test alone does not establish operating capacity.

## Current critical holds

| Hold | Required closure |
|---|---|
| Codex CLI filesystem read exposure | Enforce and test a boundary that prevents access to unrelated user files while preserving subscription login. The route stays held until then. |
| Claude CLI safety | Prove hook/MCP suppression, output cap, error hygiene and live grandchild cancellation on the candidate; the one-request `READY` result is compatibility evidence only. |
| HITL operator surface | Implement the exact ratified at-most-once B-104 terms above with audited manual crash recovery, then prove CLI/MCP cross-process resume, explicit live pause, inbound HTTP answer, daemon-client elicitation callback and shipped opt-in configuration/docs. No claim/API integration or installed witness is accepted yet. |
| Daemon operation | Prove supervised startup/restart, long quiet workflow, concurrent clients, SIGINT/drain, socket/pidfile cleanup and failure recovery. Current `mech-gamma` recipe is deferred. |
| Six workflow topologies | Supply profile-correct Ollama manifests and a live candidate witness for each; current YAML examples still mention Anthropic. |
| Local L2 embedding | Verify the embedding extra is installed in the final environment. Hash-record model files, install them in a stated cache location, prevent runtime network access, then witness the three historical L2 nodes. Reviewed strict-offline source and profile-bound corpus at isolated candidate `4dc8476` require four configured provider labels, a local manifest and model/cache paths before FastEmbed construction; 30 focused integrated tests pass. The historical L2 witness now fails on a broken installed FastEmbed/ONNX path and uses the product config loader. The manifest lacks an independent trust pin, and project typecheck and broader async routing timed out; real model hashes, ARM ONNX and installed no-network witnesses remain open. |
| Local signer | B1b physical-key alias refusal, the direct record-migration caller correction and B1c historical-key/public-map handling are independently source-reviewed, integrated and focused-tested at `0b960c0`. B2 public-only inspect and its focused diagnostics correction are independently source-reviewed and focused-tested in isolated candidate `937d43b`; installed restart/tamper witness, a nonblocking malformed-KMS diagnostic wording improvement and B-33 rotation disposition remain open. The signer remains disabled. |
| Live Docker/gVisor/telemetry proof | Docker service is active and `runsc` registered. Run tier 2/3 and telemetry end-to-end witnesses on the installed candidate; Grafana image and live stack are still absent. |
| Local Ollama host capacity | Use a verified quiet window for bounded installed live requests; no host-idle inference from VM counters. |
| Exit contract and docs | Prove installed run-result exits 0/1/5 on the final artifact and document exit 5. |
| Other CLI examples | Label or move shipped Antigravity/Gemini overlays as unsupported for this first release; Gemini currently passes its prompt in argv. |
| Operating targets | Numeric latency, throughput, recovery and soak targets are fixed in `operating-targets-v1.md`; run the bounded Gate 5 measurements against them. |
| Final release artifact | Reconcile candidate, build wheel/images, rerun or impact-review prefix evidence, run full installed matrix and operations/security checks, then issue a separate go/no-go review. |

The 19-cluster feature map and all 25 historical skip dispositions are source-grounded in `evidence-profile-contract-candidate-refresh-sonnet-1/report.md`. Its source pin is `edde786`; newer CLI process-boundary integration and the live Claude compatibility witness are separately sealed in `evidence-cli-process-boundary-integration-1` and `evidence-claude-cli-process-group-live-1`.
