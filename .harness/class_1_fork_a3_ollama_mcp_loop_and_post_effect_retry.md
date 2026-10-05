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

## Contract corrections after independent spec review of 619cab32 (historical Proposed draft; subsequently reviewed below)

The review is recorded in `.harness/a3_runtime_fence_fold_authority.md`.

- **Cell 5 claim corrected.** A provider-origin carrier is not always §14.6.4 cell 5: its `fault` selects cell 2, cell 5 or the waived re-arm. A new cell 10 states this, together with the non-provider row and the carrier-preserving emission.
- **Execution map split.** U-RT-157 is split into 157a and 157b, with criteria and mutation probes allocated to each portion.
- **Authority pointers.** Pointers to authority now resolve inside this repository.
- **Renumbering.** The claim that the number can change without a content change is withdrawn.
- **P3 clarifications.** The tools-unsupported discriminator and the projection's required keys are stated as the source implements them.

## Unit5 formal pass1 P2 absorption (Proposed)

- **Ollama offer membership.** The pass1 Codex finding is confirmed by cleared Runtime v1.132 §14.14.8 "Harness-owned durable snapshot persistence", run-in paragraph "Runtime-created contexts outside the CP driver" at `Spec_Harness_Runtime_v1_132.md:6526`: registered tools omitted from a descended step's `tools[]` can still pass C-RT-38. The historical design verdict's claim that an unoffered tool must be `<unregistered>` is therefore insufficient. Proposed v1.134 now requires a non-memory name to belong to the final Ollama offer, derived from the effective superset after projection and memory injection/collision filtering, before assessment or effects. A registered tool absent from `step.tools` remains eligible if that effective offer includes it. Standard memory rules and Anthropic's recorded residual are preserved. U-RT-157b gains registered-but-unoffered, empty-offer, projection-omission and mixed-memory controls, plus membership-removal/registry-only and declaration-only mutations. [LAW:one-source-of-truth]
- **HITL carrier routing.** The contradictory cells 6-9 sentence is corrected: signing and `BaseException` exclusions retain their carriers, while a HITL terminal error keeps its identity before effects (cell 7) and becomes a non-provider `PostToolEffectError` after effects (cell 10). This matches `619cab32785927142deb01876c260cbb696ec4b1`'s `ToolEffectFence.guard` and C-RT-16 carrier-before-generic catch order; it is source-derived, not an executed acceptance claim. Provider charging is unchanged; post-effect HITL is never charged or replayed and its half-open trial re-arms with the carrier preserved. U-RT-157a gains paired before/after identity, CP fail-class and half-open controls and mutations; 157b supplies the Ollama cases. [LAW:verifiable-goals]

The pass1 source/spec opinions and historical attachments remain evidence for their pinned heads. At that historical Proposed-draft boundary these repairs added future criteria only. The integrated acceptance below supplies implementation, independent source/spec review and source-consumption clearance; shipping and installed gates remain owed.

## Source reconciliation against main c995ec9f and candidate 47ca58b5 (Proposed)

Main `c995ec9f9fa5945a40ffe30734b859bb6e88e2a8` carries these Proposed documents but none of the A3 source. The committed candidate `47ca58b507133e7c9839e822d5925026c53cc8e9` (`prep/a3-current-controls-20261003`, not on main) implements them. This pass changes text only. It changes no behavior and does not bring back any frozen-2217 text.

- **Description is never null.** On the production path, every projected MCP `description` is a `ToolContract`'s required `str`, which may be empty. Spec v1.134 item 1 cites the registry chain at `c995ec9f`.
- **Entry differs by provider.** Ollama enters whenever a superset and the loop are bound, including when the step declares no tools. Anthropic keeps main's condition. The cleared v1.132 §14.27 wording is quoted as written, and the bound-loop precondition is attributed to the implementation, not to cleared authority.
- **Re-prompt residual registered.** An answer that does not dispatch is not an effect. A later transient failure before any effect may therefore be retried, which re-asks the model and may prompt the operator again under new call ids. The lead's disposition is to register this as a nonbehavioral residual. U-RT-157a gains a control that pins it.
- **Register row named.** The candidate's `retry.post_tool_effect.origin` key needs a row in CP's B-126 wire register. The spec and the plan now name that row and its test pins; it is a CP source change, not a CP contract change.
- **Citations rebound.** Main facts are cited at `c995ec9f`, A3 behavior at `47ca58b5`, and the A5/A4 lineage is read rather than assumed. The candidate cites spec line 57, so that line must not move.

## Integrated source acceptance

The integrated source is `a06c0abd8d09a78b1fc63ff2b9c2c98b79dcba5d` on `ship/a3-source09-20261004`; its 14 source hashes match the independently reviewed snapshot, including the accepted preparation beyond historical `47ca58b5`. The actual Opus source/spec GO, its byte binding, completed criteria 1-5 and lead acceptance are pinned in `.harness/a3_runtime_fence_fold_authority.md`. The actual original authorizing assignment is portable at `.harness/review-evidence/a3-contract-authority/lit-cmt-5b08f51a.json.md`. The two markers below clear source consumption after that review. No formal shipping review, landing or installed acceptance is implied.

## Open (not decided here)

- The B-84 memory-only arms with no superset keep their registered replay residual.
- A no-dispatch C-RT-38 answer followed by a pre-effect transient failure may be re-asked and re-prompted under new ids (spec v1.134 Scope limits). This is registered, not fenced; fencing answered gates would need its own design change.
- Landing integrated candidate `a06c0abd` (or a source-identical successor), with formal shipping review, CI and main landing, remains owed. Each citation to the candidate must be rechecked at the head that actually lands.
- Installed Ollama tool-calling (daemon `0.34.3` and model capability), installed audit and signing, and the installed C-RT-38 witness remain separate gates.

## Clearance

Filed after accepted independent source/spec review: `.harness/clearance/spec-harness-runtime-v1-134-cleared-2026-10-04.md` and `.harness/clearance/implementation-plan-harness-runtime-v2-65-cleared-2026-10-04.md`. Artifact heads derive from those markers. Formal shipping review, CI, main landing and installed acceptance remain separate gates.
