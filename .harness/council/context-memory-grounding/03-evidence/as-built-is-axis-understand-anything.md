# As-Built Evidence — the IS-axis state/memory ledger (via understand-anything)

*Complementary to the research in `03-evidence/`. Where the NotebookLM/memory-corpus docs are *design canon*, this is the *as-built code structure* of the harness's own state/memory-persistence substrate, extracted 2026-06-04 by the understand-anything plugin's knowledge graph of `harness-is/` (118 nodes / 203 edges / 7 layers; dashboard live locally). Scoped to the IS axis only. Additive input for DESIGN.md.*

## Why this matters to C3 (and the council's central thesis)
The council's diagnosis: *the harness authored a `verify_chain` gate (C-IS-06 §6.4) + an append-only hash-chained ledger for its **product** state, yet runs its own **process** memory (MEMORY.md) with none of that.* The NotebookLM research independently concluded: *the harness already owns the canonical pattern (state-ledger + replay) — apply it to the process memory store.* **This graph is the as-built proof of that existing pattern** — `harness-is` IS the reference implementation C3's retention design should mirror.

## The as-built state-ledger backbone (confirmed from the import/call graph)
```
state_ledger_write.append_ledger_entry
   ├─ imports/calls → entry_hash.compute_response_hash        (canonicalize → SHA-256)
   ├─ imports/calls → chain_link_construction.construct_prior_event_hash  (prior-event-hash chain link)
   ├─ imports      → jsonl_event_ledger_lifecycle             (append-only JSONL persist)
   └─ imports      → state_ledger_entry_schema                (typed record contract)
chain_verification → entry_hash.compute_response_hash         (verify_chain on read)
state_ledger_read  → state_ledger_entry_schema
shadow_git_rollback → state_ledger_write.append_ledger_entry  (recovery events recorded to the ledger)
```
So the existing product-state contract is: **append → canonicalize → SHA-256 response-hash → prior-event-hash chain → JSONL append-only persist → verify_chain on read**, all keyed on a single typed schema, with recovery (shadow-git rollback) wired into the same ledger.

## As-built hubs (graph centrality)
| node | in-degree (imports/calls) | role |
|---|---|---|
| `state_ledger_entry_schema.py` | **8** | the typed record contract — foundational; everything depends on it |
| `path_class_registry.py` | 4 | path classification (where state may be written) |
| `entry_hash.py` / `compute_response_hash` | 3 | the **single** canonicalize+hash primitive (write, chain-link, verify all call it) |
| `jsonl_event_ledger_lifecycle.py` | 2 | append-only JSONL persistence |

`EntryPayload` (in `state_ledger_write.py`) is the **CP→IS seam carrier** (per CXA v2.17) — the package's primary outbound-consumed surface.

## As-built 7-layer decomposition
State Ledger & Hash-Chain Core (6) · Schema & Registry Definitions (5) · Path Class & Binding Resolution (3) · Shadow-Git & Worktree Isolation (3) · Cross-Axis Seam & Public API (2) · Tests (19, ~1:1 with production) · Project Meta (3).

## The asymmetry, quantified for the council
| capability | IS axis (product state) — as-built | Process memory (MEMORY.md) — per council/research |
|---|---|---|
| schema-typed records | ✅ `state_ledger_entry_schema` (8 inbound) | ❌ free-form markdown |
| append-only persistence | ✅ `jsonl_event_ledger_lifecycle` | ❌ in-place edits |
| hash-chain integrity | ✅ `chain_link_construction` + `entry_hash` | ❌ none |
| verify gate | ✅ `chain_verification` (C-IS-06 §6.4) | ❌ advisory cap only |
| recovery wired in | ✅ `shadow_git_rollback` → ledger | ❌ un-git-versioned (C9 finding) |

**⇒ For DESIGN.md (C3 retention / WS-3 / X):** the harness need not invent a process-memory durability model — it can mirror its own IS-axis ledger (append-only + schema-typed + hash-chained + verify-gated + shadow-git recovery). `harness-is` is the in-repo blueprint; `shadow_git_rollback` is the existing answer to the un-git-versioned-store finding. This is the as-built grounding under the research's "apply the existing state-ledger to process memory" recommendation.

*Provenance: understand-anything v2.7.6 knowledge graph of `harness-is/` at commit `7c0ead2` (`.understand-anything/knowledge-graph.json`, git-ignored). The graph covers the IS-axis implementation only; it does not analyze design-substrate specs. Dashboard available locally via `/understand-dashboard` (enable the plugin first).*
