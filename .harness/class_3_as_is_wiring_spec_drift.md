# Class 3 (informational) — U-RT-34 spec/plan wording drift

**Filed at:** U-RT-34 landing (2026-05-19)
**Locus:** `Spec_Harness_Runtime_v1.md` §12.2 vs `Implementation_Plan_Action_Surface_v1.md` U-AS-27 body
**Classification:** Class 3 (informational) per Project_Workflow_v1_8.md §2.7.6
**Routing:** Non-blocking; future runtime spec revision pass

## Drift

Spec §12.2 describes the AS → IS edge as:
> "AS skill-load completion site (skill-discovery emission) ... carrying skill-load metadata"

The actual U-AS-27 plan-level unit body (AS plan v1.md §2.6, line 1360) implements:
> "Per-fetch emission discipline + span emission alongside + cross-axis composition reference" — per C-AS-08 §8.4 SECRET-fetch audit emission

Carrier modules: `harness_as.secret_fetch_audit` (compose), `harness_as.secret_fetch_emission` (emit).

## Why this is Class 3, not Class 1

The wiring CONTRACT is identical in both readings:
- Payload: `StateLedgerEntry` (per C-IS-05 §5)
- Consumer surface: `ctx.ledger_writer.append`
- Post-wiring invariant: emitted event appears in `.harness/state.jsonl` with chain integrity intact (verifiable via C-IS-06 §6)

The descriptive prose ("skill-load metadata") doesn't match U-AS-27's actual surface (secret-fetch metadata), but the materializable surface is unambiguous: secret-fetch audit emission via `compose_secret_fetch_audit_entry` → IS `LedgerWriter.append`.

U-RT-34 landed against the materializable surface. The spec prose mismatch is documentation drift, not a contract defect.

## Suggested resolution (future revision pass)

Either:
(a) Update spec §12.2 prose to reflect "AS secret-fetch audit-emission site" (matches plan).
(b) Verify whether a future U-AS unit adds a skill-load emission site that's distinct from the secret-fetch site (in which case §12.2's row may need a second edge added — but no such unit appears in AS plan v1.2 §1.3 coverage table).

## Reading 1 vs reading 2

Reading 1 (spec literal): The §12.2 edge is meant for a skill-load surface that doesn't yet exist. → unimplementable today → Class 1 fork.

Reading 2 (materializable, applied at U-RT-34): The §12.2 edge is meant for the U-AS-27 secret-fetch surface; the "skill-load" prose is stale wording from an earlier draft (Skills + secret-fetch were both U-AS-2x cluster at one point per AS-axis CLAUDE.md §1.3 grouping). → materializable, Class 3.

Reading 2 is canonical for U-RT-34 because (a) the plan-level unit body is unambiguous, (b) `Implementation_Plan_Action_Surface_v1_2.md` §3.4 + workspace `harness-as/CLAUDE.md` §2.4 both cite U-AS-27 → U-IS-11 via JSONL_EVENT_LEDGER_FORMAT_EXPORT (write contract carrier), and (c) U-AS-27 AC #5 explicitly says "ledger write delegates to U-IS-11" — that's the wiring contract U-RT-34 implements.

