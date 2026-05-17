# Phase 2 — Research Corpus Review

**Question reviewed:** how can the existing research folder be leveraged for Phase 2
(runtime + composition root + DevEx agentic plane)?

**Authored:** 2026-05-17. **Source:** Google Drive folder `1acBgfpyLjK_9l3fN9fbFqQgQvVDlXukB`
— manifest read, Triaged Source Inventory + Brainstorm Synthesis read in full; the
Pattern Reference Catalog and cluster deep-dives characterized from those two, not read
end-to-end (425KB + 5×~70KB — too large to read for a review; they are *inputs to* the
Phase 2 research step, not review material).

---

## 1. What's in the folder

A complete research substrate — raw sources → digested research → a synthesized catalog,
plus a NotebookLM layer. Three tiers:

**Tier 1 — digested research (the high-value layer):**
- `Pattern_Reference_Catalog_v1.0.md` (425KB) — 35 harness profiles, pattern-extracted,
  across 7 strata (research papers, production harnesses, emerging harnesses, methodology
  frameworks, thought-leader bodies, aggregators, approach experiments).
- 5 cluster deep-dives — orchestration/control, context/prompts/memory,
  tools/skills/validation, observability/reliability/security, surfaces/primitives/cross-cutting.
- `Triaged_Source_Inventory` — triages 40+ sources into the 35-entry catalog scope.
- `agent-harness-eng-deep-research-baseline`, `-github-repos`, `-thought-leaders`.

**Tier 2 — NotebookLM layer:**
- **`Brainstorm_Synthesis_For_Phase_2.md`** — 10 NotebookLM brainstorm rounds synthesized
  into per-axis convergence/divergence maps, F1–F5 foundational decisions, T1–T4 permanent
  tensions, and a 23-question architect's scaffold. *(See §4 — this is the design project's
  "Phase 2" = persona surfacing, not this workspace's Phase 2.)*
- ~10 NotebookLM-generated topic briefings (Google Docs) + audio/video overviews (.m4a/.mp4).

**Tier 3 — raw sources (`Sources/`):**
- 30+ topic files (`01_Anthropic_Claude_Core` … `28_Misc`), ~1,140 URL scrapes. Several
  are huge (6–7MB). The reference floor; the digested tiers are the usable form.

---

## 2. Headline — direct domain fit, but mined for contracts, not for runtime

This is **agent-harness research**, and Phase 2 **builds the harness's runtime**. The fit
is direct — but with a sharp qualification.

The catalog's 35 profiles are *running harnesses*: OpenHands, Cline, Goose, pi-mono,
DeerFlow, Crush, kilocode, oh-my-pi. Each one **is** a composition root + entrypoint +
agent loop + (often) a TUI + a provider abstraction + a deployment story — i.e. each is a
worked example of Phase 2's exact deliverable set. pi-mono in particular (`pi-ai` unified
LLM API + `pi-agent-core` + `pi-tui` + `pi-web-ui`, multi-surface from one core) is close
to a reference design for the DevEx agentic plane.

**The qualification:** Phase 1 mined this corpus for *contract and primitive* design — it
became the ADRs, specs, and the 144-unit library. Phase 1 did **not** mine it for *runtime
architecture*, because Phase 1 wasn't building a runtime. The runtime-specific patterns —
how real harnesses wire a composition root, structure an agent loop, bootstrap a tracer
provider, abstract providers at call time, deliver multi-surface — are **in the corpus but
not yet extracted**. That re-mine is the single highest-leverage Phase 2 use of this folder.

So: don't treat the research as "already consumed, nothing left." Treat it as a corpus
that was read through a contract lens and now needs a second read through a runtime lens.

---

## 3. Per-artifact leverage for Phase 2

| Artifact | Phase 2 leverage |
|---|---|
| **Pattern Reference Catalog v1.0** | Highest. Re-mine the 35 profiles for runtime patterns: composition-root structure, entrypoint/CLI/agent-loop shape, TUI/operator surface, provider abstraction, deployment. The empirical grounding Phase 2's design voices cite. |
| **Cluster 1 — orchestration/control** | Directly the runtime agent-loop + topology design (Phase 2 §3). |
| **Cluster 4 — observability/reliability/security** | The runtime operational layer — tracer bootstrap, collector, breakers (Phase 2 §3–§4). |
| **Cluster 5 — surfaces/primitives/cross-cutting** | Composition seams + cross-cutting runtime concerns. |
| **Brainstorm Synthesis §1, §4, §5** | §1: 5 topology classes + routing strategies → the multi-LLM runtime core (closes the §9 Class 2 commitment). §4: the "seven commitments of production-grade-from-day-one" — a runtime checklist; HITL spectrum; cost-knob mechanics. §5: deployment surface + multi-surface delivery (the DevEx-plane reference). |
| **Brainstorm Synthesis §9** | A 23-question architect's scaffold — reusable as the persona/scoping interview for Phase 2's DevEx-plane design. |
| **F1–F5 / T1–T4 framing (§6, §7)** | Foundational-decision and permanent-tension vocabulary; orientation for Phase 2 design deliberation. Note F1–F5 here are the *design project's* labels, distinct from the ADR F1–F5 — reconcile, don't conflate. |
| **NotebookLM notebook** | A live Q&A surface over the whole corpus — Phase 2 research can query it interactively rather than re-reading 7MB files. Audio/video overviews are operator-consumption artifacts. |
| **`Sources/` raw files** | Reference floor only. Cite specific files (`03_Claude_Code_CLI`, `04_Agent_Harness_Patterns`, `17_Durable_Execution_Workflows`, `16_Evals_Observability`) when a digested tier needs source-grounding. Don't bulk-load. |

---

## 4. Terminology collision — read this before consuming the folder

`Brainstorm_Synthesis_For_Phase_2.md` says "Phase 2" — but that is the **design project's**
Phase 2 (= *persona surfacing*, the step before ADR council deliberation). It is **not**
this workspace's Phase 2 (runtime + DevEx agentic plane).

The two phasings:
- **Design project:** research → Phase 2 persona surfacing → Phase 3 ADRs/ADD → Phase 4
  PRD → Phase 5 specs → Phase 6 plans → Phase 7 implementation.
- **This workspace:** "Phase 1" = all of the above; **"Phase 2"** = runtime + DevEx plane.

Same collision flagged for the council skills ([[phase-1-council-skills]]). Anyone reading
the Drive folder for *this workspace's* Phase 2 must keep the two straight — the synthesis
is still high-value content, it just predates and is named for a different "Phase 2."

---

## 5. Caveats and gaps

1. **The DevEx agentic plane is under-covered.** The corpus richly covers harness
   *architecture* — which includes runtime topics — and has operator-surface material
   (HITL granularity spectrum, Cline per-step approval, pi-mono multi-surface, Paperclip
   operator model). But "the operating brain of the workflow + personalized operator
   features" is a newer framing the operator added at the runtime-gap ruling. There is no
   dedicated treatment of it. Phase 2's research step should run a **fresh, targeted probe**
   on the DevEx-plane question specifically — the existing corpus is a strong base, not a
   complete answer.

2. **Dated 2026-05-08/09 — ~9 days old.** Minor, but this is a fast-moving space and the
   Triaged Inventory itself flags sources needing fresh probes. A light refresh probe
   (new harness releases, the two arXiv papers' follow-ups) is worth doing; the bulk reuses.

3. **The corpus already fed the existing design corpus.** The ADRs/ADD/PRD/specs are
   *derived* from this research — it is not net-new input. Its Phase 2 value is the
   re-mine (§2), the framing reuse (§3), and the 35 harnesses as concrete reference
   implementations — not "research we haven't looked at yet."

4. **Confidence cap.** The Brainstorm Synthesis self-rates MODERATE — it's NotebookLM's
   reading of the corpus, not direct extraction. Verify specific harness claims against the
   catalog/clusters before they become load-bearing in a Phase 2 ADR.

---

## 6. Recommended use in the Phase 2 design pipeline

Phase 2 opens with research → brainstorm. This folder front-loads both:

- **Research step:** start from the Pattern Reference Catalog + clusters, not a blank page.
  Do the runtime-lens re-mine (§2). Add one targeted fresh probe on the DevEx agentic plane
  (§5.1) and a light recency refresh (§5.2).
- **Brainstorm step:** the Brainstorm Synthesis is a ready-made brainstorm input — reuse
  its convergence/divergence map and the §9 question scaffold as the Phase 2 scoping
  interview, re-pointed at runtime/DevEx-plane decisions.
- **Throughout:** the 35 catalogued harnesses are the reference implementations to cite
  when a Phase 2 design voice (C1, C6, C7, C11 — see `phase-2-council-skill-review.md`)
  commits to a runtime pattern. pi-mono, Crush, OpenHands, DeerFlow, oh-my-openagent are
  the highest-relevance profiles for Phase 2's specific surfaces.

The folder should be brought into the workspace (or a stable pointer kept) so Phase 2's
design pipeline cites it the way Phase 1's voices cited the deep-research artifact.

---

## 7. Open questions for the scoping session

1. Pull the folder into the workspace (`design-substrate/research/` or similar), or keep
   it Drive-resident and cite by pointer? Bulk is ~25MB+ raw; the digested tier is ~1MB.
2. Does Phase 2 commission the runtime-lens re-mine of the catalog as an explicit
   research deliverable, or fold it into per-voice research as voices are convened?
3. Is a NotebookLM refresh (re-ingest with Phase-2-runtime framing) worth it, or is the
   existing notebook sufficient as a Q&A surface?
4. Reconcile the design-project F1–F5 labels in the Brainstorm Synthesis against the
   canonical ADR F1–F5 before any Phase 2 artifact cites them.
