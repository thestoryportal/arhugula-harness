# Phase 7 — Sub-phase 7a Substitution Scaffolding

*7a substitution-scaffolding ledger. Operator-authored Convention-mechanism
declarations standing in for not-yet-built H_T primitives. NOT canonical —
each section is retired per its X-AL-2 retirement criterion. Authority:
Phase_7_Session_1_Entry_Directive_v1.md §6.2; Phase_7_Meta_Architecture_v1.md
§10.1.3 + §5.2.*

---

## §1 Surface 1 — Path conventions  [substitutes H_T-IS-1; C-IS-01 §1]

**Mechanism:** Convention. The 4-class path semantics below are declared here;
Read/Write/Glob operations during 7a obey these roots via prompt-discipline.
**Retirement:** this section retires when U-IS-01 + U-IS-02 + U-IS-03 land
(the typed path-class registry supersedes this convention).

### §1.1 The 4 canonical artifact classes (per C-IS-01 §1)

| Path class       | C-IS-01 residence contract                          | 7a convention root (provisional)        |
|------------------|-----------------------------------------------------|-----------------------------------------|
| SKILLS           | SKILL.md-as-directory; one folder per skill         | `.harness/skills/`                      |
| PROMPTS          | plain-text-file-in-git; one file per prompt         | `.harness/prompts/`                     |
| ROUTING_MANIFEST | single file in git; per-role/-class/-step model map | `.harness/routing.manifest.json`        |
| STATE_LEDGER     | two-mode: JSONL event ledger + git commit stream    | JSONL: `.harness/state.jsonl`; commit stream: workspace git repo |

### §1.2 Prompt-discipline rule

During 7a, all H_T artifact Read/Write/Glob operations resolve against the
roots in §1.1. `Glob` enumerates a path class against its declared root only.

### §1.3 Anti-leakage (IS-AL-1)

The H_T path-class roots live under `.harness/` (H_T-canonical runtime root).
They are NOT `.claude/` — `.claude/skills/` hosts the four H_E Phase 7-specific
skills (execution-harness scaffolding), which are categorically distinct from
the H_T SKILLS path class. `.harness/` ≠ `.claude/`; this convention is a
substitution, not the typed registry (IS-AL-1).

### §1.4 Provisional-binding note

The §1.1 root strings are 7a-provisional. C-IS-01 §1 defers canonical path
strings to implementation; the typed binding lands at U-IS-01/U-IS-02. If
the IS plan v2.2 unit declarations bind different strings, reconcile at
U-IS-01 landing (this section retires at that point regardless).

---

## §2 Surface 2 — State ledger  [substitutes H_T-IS-5; C-IS-05 §5]

**Mechanism:** Shell-out. The state ledger is a JSONL file at
`.harness/state.jsonl` (STATE_LEDGER path class, §1.1). During 7a:
entries are produced via `Bash(python -c 'import json…')`, appended via
`Bash(cat <<EOF >> .harness/state.jsonl)`, and consumed via `Read`.
**Retirement:** retires when U-IS-07 lands (typed entry shape); full
H_T-IS-5 retirement per U-IS-07/08/09/10.

### §2.1 Entry shape — canonical 6-field tuple (C-IS-05 §5)

| Field            | Type / format             | Semantic                                    |
|------------------|---------------------------|---------------------------------------------|
| action_id        | identifier, unique/action | identifies the action this entry records    |
| idempotency_key  | identifier, stable/op     | harness-canonical join key (ADD §2.2)       |
| actor            | identifier                | agent / sub-agent / operator originator     |
| response_hash    | SHA-256 digest            | hash of canonical-JSON of the payload       |
| timestamp        | monotonic timestamp       | wall-clock instant the entry was written    |
| prior_event_hash | SHA-256 digest OR zeros   | hash of prior entry; all-zeros at inception |

### §2.2 7a-provisional field formats (C-IS-05 defers these to implementation)

| Field           | 7a-provisional convention                                            |
|-----------------|----------------------------------------------------------------------|
| action_id       | UUID v4                                                              |
| idempotency_key | hex string (Stripe-style); keying tuple per C-IS-07 §7.1 deferred per §7.4 |
| timestamp       | RFC 3339 UTC (e.g. `2026-05-15T12:00:00Z`)                           |

Provisional; reconciled at U-IS-07 landing.

### §2.3 Scope boundary vs surface 3

`response_hash` + `prior_event_hash` are entry *fields* (shape declared
here); their *computation* (SHA-256 + RFC 8785 canonicalization) is
surface 3 (hash-chain). Surface 2 establishes the file + shape + append
convention only.

### §2.4 Anti-leakage (IS-AL-3, IS-AL-4)

IS-AL-3: H_E conversation history `(role, content, tool_calls,
tool_results)` ≠ the 6-field H_T entry shape. IS-AL-4: the `Bash`
shell-out is a substitution, not the C-IS-05/C-IS-06 typed contract
(that lands at U-IS-07/08/09/10).

---

## §3 Surface 3 — Hash-chain  [substitutes H_T-IS-6; C-IS-06 §6]

**Mechanism:** Shell-out. State-ledger hash-chain integrity is
constructed at write-time via `Bash` invocation of Python stdlib
(`hashlib.sha256` + `json`). **Retirement:** retires when
U-IS-08 + U-IS-09 + U-IS-10 land.

### §3.1 The 4-step discipline (C-IS-06 §6.1–§6.4)

1. canonicalize(entry) -> deterministic bytes
2. response_hash = SHA-256(canonicalize(entry))
3. chain construct: prior_event_hash links entry N to entry N-1
4. verify_chain: re-canonicalize, re-hash, check linkage + inception

### §3.2 7a canonicalization convention

C-IS-06 §6.1 names RFC 8785 JSON Canonicalization Scheme (JCS) as the
baseline candidate; the library binding is deferred to a downstream
D-ADR. The 7a state-ledger entry (§2.1) has six all-string fields and
no numeric values; JCS's only non-trivial divergence is numeric
serialization. Therefore the 7a substitution uses Python stdlib:

    json.dumps(entry, sort_keys=True, separators=(',', ':'),
               ensure_ascii=False).encode('utf-8')

— which is byte-faithful to RFC 8785 JCS for all-string entries. A
true JCS library binding becomes mandatory when any numeric field is
introduced; deferred per C-IS-06 §6.1 + §6 Deferred-to-implementation.

### §3.3 Chain construction (C-IS-06 §6.3)

- prior_event_hash stored as 64-hex-char string.
- Inception (entry 1): prior_event_hash = "0"*64 (ALL_ZEROS_SENTINEL,
  32 zero bytes).
- Entry N>1: prior_event_hash = response_hash of entry N-1
  = SHA-256(canonicalize(entry N-1)).

### §3.4 Hash-input scoping  [PROVISIONAL — under-specified by C-IS-06]

C-IS-06 §6.2 writes "response_hash = SHA-256(canonicalize(entry))",
but response_hash is itself a field of entry — self-reference. C-IS-06
does not state which fields are excluded from the canonicalization
input. 7a-provisional resolution: response_hash is computed over the
entry with the response_hash field omitted; prior_event_hash IS
included (it is known before hashing). verify_chain re-canonicalizes
identically. This scoping is reconciled at U-IS-08 (canonicalize) /
U-IS-09 (chain construct) / U-IS-10 (verify).

### §3.5 Anti-leakage (IS-AL-4)

The `Bash`+stdlib hash-chain is a substitution, not the C-IS-06 typed
contract. "We have a Python script that does SHA-256 chaining" does
NOT mean U-IS-08/09/10 are complete (IS-AL-4 anti-pattern, verbatim).
