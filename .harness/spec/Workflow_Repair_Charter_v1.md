# Workflow Repair Charter v1 — the U-HE-35 skill-suite + governance repairs

**Status.** Lean repair charter, 2026-08-26 — deliberately NOT a Phase-5 spec. It scopes the skill-suite and governance repairs (bucket 2 of the U-HE-35 workflow-repair program); the contract-surface repairs (bucket 1) are `Spec_HE_Loop_Lanes` v1.6 change-note X6a–X6f, because those amend contracts that spec already owns and this charter MUST NOT become a second authority for them. Unit decomposition, sequencing (R0→R3), and acceptance criteria live in the workflow-repair section of `.harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md`; this charter is the durable statement of *what is being repaired and why*, so each repair arc can cite one home instead of re-deriving the rationale from two audits.

**Sources.** Every count below carries its source id: **[A]** = `.harness/session-audit-2026-08-26-u-he-35-preflight-suite.md` (the findings audit); **[B]** = `.harness/session-audit-2026-08-26-u-he-35-workflow-efficiency.md` (the cost audit). No number in this charter is new.

## 1. The measured failure this charter repairs

The U-HE-35 arc shipped correct code and paid roughly twice what it should have: 13 review rounds (10 codex + 3 merge-gate) where 4–6 were reachable, at ≈13.8 min and ≈0.84M input-equivalent tokens (IET) per codex round [A][B]. The findings audit's verdict is the load-bearing fact: **zero of the 29 reviewer findings were beyond the reach of knowledge available at authoring time** — ~39% of instances were squarely inside the preflight suite's committed ledger, and the other ~61% were one deliberate analogy, one spec phrase, or one sibling-source read away [A, ledger-novelty partition]. The failure is activation and retrieval, not coverage.

The self-improvement circuit that should convert such an arc into repairs is broken at both ends [A][B]:

- **Nothing flows in.** The suite's own obligation — classify every reviewer-caught miss and repair the skill in the same absorption commit, plus a planted-defect eval case — executed zero times across ten absorption commits [A §4]. The corpus re-derivation trigger has also been missed corpus-wide: 466 findings match no known class [A].
- **The measurement out is corrupted.** The arc-metrics snapshot counted the arc's two `GATE_REFUSED` transcripts as rounds ([B] F15) and the C-HE-24 attribution fields are null on all 44 rows ([B] F16) — the instrument meant to measure whether these repairs work was mis-measuring the arc that motivated them. That is why the program's sequencing rule (plan-encoded) is *instruments before, or with, levers*: bucket 1's R0 instruments land first, or the effect of everything below is unmeasurable.

## 2. Repair inventory

Sixteen repairs, WR-01…WR-16. "Eval-backed" means the acceptance criterion is a case added to `.claude/skills/defect-class-preflight/evals/evals.json` and passing; repairs without a natural eval case name their witness in the plan unit instead.

### The preflight suite (the five [A] repairs, WR-01…WR-07)

[A]'s "Recommended repairs" list is numbered 1–5; its repair 1 carries three sub-classes (i)/(ii)/(iii). WR-01/02/03 split repair 1 by class; WR-04…07 are repairs 2–5 in order.

- **WR-01 — spec-phrase-to-code completeness class** (eval-backed). Every quoted contract phrase in a registered row or docstring must name the code that discharges it. Both U-HE-35 P1s were spec-verbatim misses at turn 0 — plan-skeleton deference over spec text the session had already read [A §1]. Source: [A] repair 1, class (i).
- **WR-02 — new-command-surface class** (eval-backed). Any new justfile recipe whose `runs_in` includes "loop" fires the question: permission-guard wiring present, with a paired witness? U-HE-25/U-HE-34 commits already model the recipe⇒allow⇒witness pattern [A]. Source: [A] repair 1, class (ii).
- **WR-03 — signal/lock safety class + grep shapes** (eval-backed). Any signal handler + lock combination demands the reentrancy question. Adds the four greppable shapes to `preflight-grep.sh`: `returncode in (`, `except subprocess.TimeoutExpired` without `OSError`, argparse `type=int` on counts, a new guard `elif` without a paired witness. Source: [A] repair 1, class (iii) + its grep shapes.
- **WR-04 — fix-sweep sharpening** (eval-backed). The tell, verbatim from the arc: "a commit that adds a mechanism can never answer 'no new mechanism'" — the r5 sweep answered exactly that while introducing `_LiveGroups`, whose race was r6's finding; 8 of 29 findings (28%) targeted code the arc's own absorptions introduced [A §2]. Source: [A] repair 2.
- **WR-05 — contract-derived-bounds rule** (eval-backed). Any numeric bound in a guard or allowlist must cite the contract value it derives from — the guard-reps token took four paid touches (any→1–99→1–9→5–9) because each bound was invented syntactically [A §3]. Source: [A] repair 3.
- **WR-06 — hold-policy promotion** (eval-backed). A reviewer finding held as "a later unit's job" must be accompanied *in the same round* by the minimal fail-closed probe, or the hold is presumptively wrong. Promotes the standing memory into the skill; the un-promoted version cost four rounds of pilot-gate re-litigation (r1, r5, r9, r10) — the single costliest policy miss of the arc [A §1]. Source: [A] repair 4.
- **WR-07 — planted-defect eval cases for both P1 shapes** (the eval half of WR-01/WR-06): the exit-code-as-verdict shape and the declared-but-unenforced-gate shape [A]. Source: [A] repair 5.

### Prompt-authoring wiring (the laws:prompt plan + its binding-value completion)

- **WR-08 — laws:prompt durable wiring** (eval-backed), per the memory `feedback-subagent-prompts-are-laws-prompt-medium` (passive memory failed twice in 48h; operator directed durable wiring): (a) a hard skill-text step in `merge-gate` / `fan-out` / `council-workflow` — subagent prompts are authored by a delegated laws:prompt-adopting agent; inline is legal only for literal-value instantiation of a skill-canonical template; (b) a PreToolUse hook matcher on the Agent tool injecting one advisory line at every Agent call (advisory-inject, never deny — a deny would break the delegate itself); (c) the regression eval case (planted defect: freehand lens prompt in a laws:code session). The delegation itself is cheap — 1m13s, 0.11M IET, 3% of one lens run [B] F3.
- **WR-09 — binding values by file, never by hand** ([B] a4). `just merge-gate-binding` writes the six binding values to a file the lens agent reads; the prompt names the path. Both round-3 lens corruptions were orchestrator transcription errors (a truncated `head_sha` → one re-emit; a spliced `base_sha` → a full 0.38M-IET lens rerun, ≈5 min on the critical path) [B] F3. This completes WR-08: delegating was never the cost — hand-copying binding values was.

### Loop-recipe and attestation mechanics

- **WR-10 — attestation labels before answers** ([B] a2). The attest recipe runs `preflight-grep.sh` first and writes its labels into the answers template; three attest calls failed by trial only because answers were authored before the labels existed ([B] F14).
- **WR-11 — mechanism-precedent search into the preflight grounding step** ([B] a5), per the memory `mechanism-precedent-search-before-authoring`: for each mechanism a new tool needs, read the reviewed sibling that already does it (adopt or import), grep the gate-log corpus for that surface, and treat a plan skeleton as unreviewed input. ≥7 of the 29 findings re-derived, one paid round at a time, disciplines the sibling wrappers already embodied [A].
- **WR-12 — codex-check shape** ([B] b6). `just codex-check` always runs `run_in_background` (run 3 hit the 600 s foreground timeout → a 10-minute dead gap, then a background handoff anyway); and the stop-gate tree-dirty test ignores — or re-homes/gitignores — `.harness/.preflight-answers-*` / `.harness/.sweep-answers-*`, so attestation artifacts cannot red a run (two of three runs were red on environment only; ≈20 min avoidable) [B] F6.

### Governance prose that names phantom or mis-homed instruments

- **WR-13 — `advisor()` reconciliation** ([B] b8) — **carries open decision #1, surfaced in the plan, NOT decided here.** `advisor()` is not provisioned anywhere: the session tool inventory has no such tool, and the 65 mentions are skill-body prose (`CLAUDE.md` §13.1, `roadmap-continue/SKILL.md:106`, `merge-gate/SKILL.md:9,17`, `resolve/SKILL.md:35`) [B] §3 item 1. Either rewrite those carriers to the instrument that exists (a fresh-context Agent given the transcript summary, or `just codex-review` alone), or provision the tool. A discipline that cannot be followed trains the agent to skip disciplines.
- **WR-14 — session-shape codification** ([B] b10 + d2 + d3). Three habit lines into the loop skills: (a) heavy audits/documents are authored in a fresh session from a facts brief — the closing session writes the brief and handoff only (S3 at 540k context cost 0.93M IET; ≈0.3M fresh [B] F10); (b) before any background wait expected to exceed the cache TTL at >400k context, prefer a handoff — one re-warm cost ≈0.7M IET [B] F4; (c) read-before-grep — for a file the agent will read anyway, Read or one script beats a chain of `sed -n`/grep calls (33 `sed -n`, 101 grep-shaped calls, one API call each [B] F5/d3).

### Context-noise deletions

- **WR-15 — context-save preamble trim** ([B] c2). 53.8 KB of gstack-generic preamble per invocation → the workspace-relevant subset (the only sink used is the local checkpoint directory) [B] F11.
- **WR-16 — PreToolUse:Bash hook noise** ([B] c3). The hook emits only on an actual rewrite or guard decision; 143 attachments ≈ 108 KB were mostly "rewrote nothing" chatter [B] F12.

### Deliberately absent from this charter

Worktree pruning and branch hygiene ([B] b7) are operator one-offs, not repair units. The mechanical sweep — pin scope ([B] b1), rtk rewrite shapes ([B] b4), edit-hook timing ([B] b5) — is one batched plan unit (R2), not charter items: each is a tool fix with its own witness, needing no rationale beyond its [B] entry.

## 3. Acceptance mechanism and baselines

The acceptance mechanism for eval-backed repairs is the preflight suite's existing harness: `.claude/skills/defect-class-preflight/evals/evals.json` — each such unit closes on "eval case added and passing." Repairs without an eval-shaped criterion (WR-12, WR-14–16) name a mechanical witness in their plan unit.

The program is judged against the recorded U-HE-35 baseline, all from [B] — assert the shape against these numbers, never recall: **13 rounds** (10 codex + 3 gate) to all-approve; **≈25.6M IET** grand total (21.0M main / 4.64M subagents — corrected 2026-08-27 at U-HE-48: [B]'s printed 25.5M/4.52M were first-copy-read undercounts of the subagent usage copies; the ratifying note lives at the plan's U-HE-48 acceptance bullet and its clearance marker); **≈2h agent-active** inside 5h19m foreground; **29 PR commits, 13 of them pin commits**; **418 main API calls**; spec-conformance lens **0 findings per 1.34M IET**; **29 wasted rtk calls**; **12 re-pins**; **3 attest-by-trial failures**. The A/B read happens on the R3 eval arc (plan-encoded), with the X6f mid-budget lens trial riding it and the repaired instruments (X6c–X6e) doing the measuring.

## 4. What NOT to repair

The keep-as-is list from [B] §6 is normative for every repair arc — a unit that "improves" one of these is out of scope: the background live probe shape; background codex rounds with task notifications; the 10-round budget refusal (it stopped the loop exactly where B-215 says); the merge-gate itself (its 9 findings were real and post-codex — the cost to cut is the spec lens's yield and the paste path, not the gate); CI waits and the door; the laws:prompt delegate; the mutation probe as witness (only the whole-file pin scope is the defect); and the facts-brief → fresh-session audit pattern (WR-14 codifies it; nothing dismantles it).

## 5. Filing

Filed 2026-08-26 alongside `Spec_HE_Loop_Lanes` v1.6 and the plan's workflow-repair section, as one doc-only PR under the LEAN review protocol, with a `harness-adversarial-reviewer` pass before the clearance marker. Revisions to this charter ride ordinary doc PRs; it carries no clearance marker of its own (H_E tooling; the spec's marker is the version-binding record for the contract half of the program). The two open operator decisions (advisor() provisioning; U-HE-36 ordering relative to R0) are surfaced in the plan's open-decisions section — this charter decides neither.
