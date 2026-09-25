# Spec: Control Plane — v1.121 (delta over v1.120)

*Delta-only file. v1.120 and every earlier C-CP-01 … C-CP-29 body are preserved verbatim
except at **two** amendment sites, both bounded to `EVALUATOR_OPTIMIZER`: (1) C-CP-25
§25.11 — the encoding of the evaluator's accept signal becomes a strict typed verdict read
at every decision point; (2) C-CP-25 §25.17 — a new failure row, "verdict absent or
malformed → FAILED". No new `RunStatus` value, no new contract number, no ledger, pause-cursor
or hash-byte change. A Runtime-side delta (the provider-response reader and its binding) is
owed and is NOT specified here (§0.7).*

**Filed:** 2026-09-24
**Authority:** first-release evaluator accept contract decision
(`evaluation/production-readiness-arch/evaluator-accept-first-release-decision-1.md`);
independent Opus design `evidence-evaluator-accept-design-opus-1/verdict.md`.
**Predecessor:** `Spec_Control_Plane_v1_120.md`

## §0 Change-note (v1.120 → v1.121)

### §0.1 The gap

C-CP-25 §25.11 says an EVALUATOR_OPTIMIZER run is "terminal on evaluator accept or cap" and
§25.18 leaves the accept signal's encoding to implementation discretion. The driver read it as
`bool(evaluation.get("accepted", False))`: an absent key meant *regenerate*, and any truthy
value — including the string `"false"` — meant *accept*. A real model evaluator returns text;
under that reading a mis-shaped or truncated reply either silently regenerated forever to the
cap or was silently accepted. Neither is a verdict.

### §0.2 §25.11 (AMENDED) — the accept signal is a strict typed verdict

The evaluate step's output is read through one checkpoint,
`harness_cp.evaluator_verdict.parse_evaluator_verdict_mapping`, into a frozen
`EvaluatorVerdict(accepted: bool, feedback: str | None)`. A valid output is a mapping with:

- `accepted` present and a **literal bool** (not `"false"`, `1`, `None`);
- `feedback` absent or a **string**;
- **no other key**.

Anything else raises `EvaluatorVerdictMalformedError(reason)`. Acceptance is exactly
`verdict.accepted is True`; nothing else terminates on accept and nothing is coerced.

### §0.3 The three decision points share one read

The driver reads the verdict at (a) the live loop, after each evaluate; (b) the resume
pending-evaluate; and (c) resume-prefix coherence. An optional `evaluator_verdict_reader`
on the driver context (a callable `Mapping -> EvaluatorVerdict`) may convert a provider-shaped
response at all three points; when unbound the CP mapping is parsed directly, so an unbound
context fails closed on a raw provider dump rather than accepting it.

### §0.4 §25.17 (AMENDED) — verdict absent or malformed → FAILED

- **Live and pending-evaluate:** a malformed verdict ends the run `FAILED` with fail class
  `evaluator-optimizer-verdict-malformed at entry <n>: <reason>`, where `<n>` is the evaluate
  entry just buffered. The prior buffered entries **drain** (no silent loss). It is FAILED for
  every cascade policy: never a retry, never a resumable `PAUSED`, never a fallback candidate,
  because the evaluate effect already landed and any of those would re-fire it. It is
  deliberately distinct from `evaluator-optimizer-setup-or-bookkeeping-failure`.
- **Resume prefix:** a malformed recovered verdict is a resume **mismatch**, not an escaping
  exception: `malformed-verdict-in-prefix at entry <n>: <reason>` (surfaced through the existing
  resume-body-mismatch failure). A recovered **accepting** verdict remains the existing
  `accepted-step-in-prefix` mismatch; only a rejecting verdict is coherent.

### §0.5 Cap semantics are unchanged and stated

Explicit rejects (`accepted is False`) may run to the existing iteration cap and end `SUCCESS`
with `final_state.accepted == False` (§25.11 "terminal on accept or cap"; §25.17 lists no
cap-failure mode). **`SUCCESS`, `completed` and CLI exit 0 never prove evaluator acceptance;**
acceptance is `final_state["accepted"] is True`. A consumer that must know MUST test that.

### §0.6 Behavior changes, stated

- An absent `accepted` moves from *regenerate* to `FAILED`.
- A non-bool `accepted` (including `"false"`, which was a false accept) and any extra key move to
  `FAILED`.
- An EO pause cursor minted before this delta whose recovered evaluations lack a valid verdict
  now fails closed on resume (`malformed-verdict-in-prefix`) instead of continuing. No such durable
  cursor is known.
- Test doubles that execute EVALUATOR_OPTIMIZER must emit explicit booleans; the parser is not
  loosened for them.

### §0.7 What this delta does NOT specify

- The Runtime reader that extracts an assistant message from a provider response (for example an
  Ollama chat reply), strict-parses JSON (duplicate keys, NaN/Infinity, truncation, tool calls) and
  returns this same `EvaluatorVerdict`, and its stage-5 binding. Owed at the next free Runtime version;
  this delta only fixes the CP type and the binding point.
- Recording a compact verdict instead of the raw evaluation. The raw evaluation output stays the
  recorded value everywhere (`final_state.evaluation`, pause cursor, engine-output store,
  inter-step channel), so those bytes and the ledger are unchanged.
- Installed model acceptance: this is source/contract only.

## §1 Preservation guarantees

| Element | Disposition |
|---|---|
| v1.120 body + all earlier CP spec bodies | Preserved verbatim |
| `RunStatus` values, `RunResult` shape, CLI response surface | Unchanged |
| `final_state["evaluation"]`, pause-cursor and ledger bytes | Unchanged (raw evaluation recorded) |
| Iteration cap and cap-terminal `SUCCESS accepted=False` | Unchanged |
| Other five topologies | Unchanged |
