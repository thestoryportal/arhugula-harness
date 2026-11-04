# Spec: Operational Discipline — v1.43 (delta over v1.42)

*Delta-only file. One amendment site: C-OD-30.5.1, the cause-attribution row of the required-content
table (`Spec_Operational_Discipline_v1_36.md:62`, unchanged through v1.42). Every other v1.42 and
earlier term, including the rest of §30.5, remains in force. Cleared predecessor files are not
edited.*

**Status: Cleared** for source consumption by
`.harness/clearance/spec-operational-discipline-v1-43-cleared-2026-11-04.md` after independent review GREEN
(LIT `cmt-53662ef5`) and integration-lead ratification `cmt-7cc5fc50`, retained at unchanged bytes by `cmt-9733f3e9`.

**Authority.** Companion to Runtime spec v1.137 Rule A4 and plan v2.68 U-RT-160 portion 160a
(`Spec_Harness_Runtime_v1_137.md`, `Implementation_Plan_Harness_Runtime_v2_68.md`; authority
`.harness/runtime-resume-contract-authority.md`, fork
`.harness/class_1_fork_runtime_resume_cli_supersession.md`). Owner assignment: integration-lead
disposition LIT `cmt-1ba063e7`, under claim `cmt-792618a5`. This delta neither ratifies the Runtime
delta nor changes any OD behavior beyond the one row below.

## 1. C-OD-30.5.1 — cause attribution (AMENDED)

The cause-attribution row's note, "one of the five stable identifiers Runtime v1.107 §30 declares —
`absent` / `empty-journal` / `read-error` / `corrupt-latest` / `workflow-mismatch`", becomes:

> one of six stable identifiers: the five Runtime v1.107 §30 declares — `absent` / `empty-journal` /
> `read-error` / `corrupt-latest` / `workflow-mismatch` — plus `superseded` (Runtime v1.137 Rule A4: a
> later fresh root run of the workflow appended a supersession record after the read's pause record)

The audit vocabulary stays closed. `PauseStateCauseAttribution` in `harness-od` gains exactly one
member, `SUPERSEDED = "superseded"`, and keeps the existing five members and values. It stays
re-declared in `harness-od`, not imported from `harness-runtime`.

Unchanged: a failed read with cause `superseded` carries `workflow_id`, its cause attribution and no
staleness token or per-variant counts, like every other failed read. A successful read carries no
cause attribution. The §30.5.3 pairing rule is unaffected, because a refusal is only reachable from a
read that produced a token. The §30.5.1 disclosure limits apply unchanged.

## 2. Required witnesses (after application)

Future tests, not run by this delta.

1. Six-value identity: the OD `PauseStateCauseAttribution` values equal the Runtime accessor's failure
   cause values as sets of exactly six strings; removing, renaming or adding a member on either side
   fails the existing cross-surface identity witness.
2. Superseded emission: on a superseded record, exactly one `pause.state.read` event is retrievable
   from the real sink in a fresh process, with `succeeded=false`, `cause_attribution` `superseded`,
   the `workflow_id`, no token and no per-variant counts (Runtime v1.137 witness I.13).
3. Negative, vocabulary: an identifier outside the six (for example `stale` or an empty string) is
   rejected by `PauseStateCauseAttribution` construction; nothing maps it to a member.
4. Negative, success shape: a successful read never carries `superseded` or any cause attribution.
5. Negative, existing causes: each of the five prior causes still emits its own identifier, never
   `superseded`.
