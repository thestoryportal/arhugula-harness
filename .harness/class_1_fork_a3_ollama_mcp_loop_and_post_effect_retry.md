# Fork record — A3 Ollama model-MCP tool loop and shared post-effect retry fence

**Class:** 1 (design-substrate amendment), absorbed through a documented bundled-absorption arc (CLAUDE.md §11.4). Authorized by the lead orchestrator under the operator's autonomous full-goal directive (LIT `arhugula-harness-trial-193`, assignment `cmt-5b08f51a-a023-4f11-bba6-3970a76bc2a4`). No new H_T primitive, cross-axis edge or contract number.

## Fork

1. **Coverage gap.** Runtime v1.132 §14.27 C-RT-38 "Provider scope" wires model-emitted tool gating only to the Anthropic path. On the first-release Ollama route every non-memory model tool call is refused, so the profile's local-Ollama MCP tool capability is absent. The independent design verdict selected one shared Ollama tool-turn path. Its full SHA256 and provenance are recorded in `.harness/a3_runtime_fence_fold_authority.md`.
2. **Retry defect (A2 current-main source review, P2-1).** C-RT-16 classifies any generic exception as `TRANSIENT_RETRY` and re-runs the whole dispatch. After a tool effect, that re-asks the model, which can emit the call again under a new id, so the tool runs twice. The review found this by reading the source. A provider-free RED at base (`test_post_tool_effect_replay.py`) reproduced it: the tool effect ran twice through the real wrapper, dispatcher and loop.

## Disposition

- Runtime spec **v1.134** amends C-RT-38 §14.27 with the Ollama provider scope and the post-effect fence.
- Plan **v2.65** adds unit U-RT-157.
- Source and tests land in the same arc.
- Both design documents are numbered relative to main's v1.133/v2.64. A renumber is not content-neutral; see the spec's Numbering paragraph.
- The design's original premise of an audit-integration slice at v1.134, with this slice at v1.135, is superseded: the audit responder was already integrated at v1.131.

## Correction after independent review of bb275eff (accepted by the lead)

- **Codex P2-1: the fence ended before turn capture.** A real probe showed 3 effects, 3 captures and 3 attempts. The effect state is now owned by each retried `dispatch` attempt, so capture is inside it.
- **Codex P2-2: post-effect provider faults went uncharged.** The carrier now records its structural origin. Provider-origin failures are charged under the existing §14.6.3/§14.6.4 rules (closed: once; half-open: cell 5); non-provider failures are never charged. Spec v1.134 states this C-RT-16 clause explicitly and withdraws the earlier "no breaker charge" wording. *(Superseded: "half-open: cell 5" is replaced by §14.6.4 cell 10; see the contract corrections below.)*
- **Codex P2 (correction re-review): post-effect response-parsing faults lost their charge.** Provider origin covered only the SDK call, so a malformed provider reply after an effect became `non-provider` (half-open 5 → 5) although §14.6.3 row 2b and §14.6.4 cell 2 count it. The provider boundary now also covers parsing that provider's own reply, on both arms; memory validation, tool and memory execution, capture and bookkeeping stay `non-provider`. Row 2b and cell 2 are unchanged.
- **Opus P2: the served Ollama memory-write fence had no witness.** A witness and its mutation probe are added.

## Contract corrections after independent spec review of 619cab32 (Proposed, not yet reviewed)

The review is recorded in `.harness/a3_runtime_fence_fold_authority.md`.

- **Cell 5 claim corrected.** A provider-origin carrier is not always §14.6.4 cell 5: its `fault` selects cell 2, cell 5 or the waived re-arm. A new cell 10 states this, together with the non-provider row and the carrier-preserving emission.
- **Execution map split.** U-RT-157 is split into 157a and 157b, with criteria and mutation probes allocated to each portion.
- **Authority pointers.** Pointers to authority now resolve inside this repository.
- **Renumbering.** The claim that the number can change without a content change is withdrawn.
- **P3 clarifications.** The tools-unsupported discriminator and the projection's required keys are stated as the source implements them.

## Open (not decided here)

- The B-84 memory-only arms with no superset keep their registered replay residual.
- Installed Ollama tool-calling (daemon `0.34.3` and model capability), installed audit and signing, and the installed C-RT-38 witness remain separate gates.

## Clearance

Owed after independent review: `.harness/clearance/spec-harness-runtime-v1-134-cleared-<date>.md` and `.harness/clearance/implementation-plan-harness-runtime-v2-65-cleared-<date>.md`, plus the derived artifact-head rows. None is filed by the authoring arc.
