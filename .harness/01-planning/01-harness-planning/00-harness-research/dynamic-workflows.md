# A Harness for Every Task: Dynamic Workflows in Claude Code

> Anthropic's new dynamic workflows let Claude Code write its own custom harness on the fly - spinning up coordinated subagents to tackle migrations, deep research, triage, verification, and more. LAXIMA shares the patterns, failure modes, and field-tested tips for getting the most out of them.

**Author:** LAXIMA Team  
**Published:** 2026-06-03  
**Updated:** 2026-06-03  
**Reading time:** 12 min  
**Category:** ai automation  
**Tags:** Claude Code, Dynamic Workflows, AI Agents, Agent Orchestration, Anthropic, AI Automation, Subagents, LLM Workflows, Claude Opus 4.8, Developer Tools  
**Canonical URL:** https://laxima.tech/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code

---
Anthropic just shipped **dynamic workflows** in Claude Code, and it meaningfully widens what the tool is capable of. Claude can now author its own harness in the moment - purpose-built for whatever task it's been handed.

Out of the box, Claude Code's harness is tuned for coding. It happens to stretch much further than that, though, because a great many tasks turn out to _look_ like coding tasks under the hood. Even so, there have always been categories of work that demanded a bespoke harness bolted on top of Claude Code to hit top performance - Research, security analysis, agent teams, Code Review, and so on.

Dynamic workflows close that gap. Claude can now generate those harnesses on the spot and handle all of those problems - plus plenty more - directly inside Claude Code. Better still, once a workflow exists you can save it, hand it to teammates, and reuse it.

For us at LAXIMA, this lines up almost exactly with the work we ship for clients: long-running, parallel, structured automation where dependable results and ROI count for far more than one inspired prompt. Here's what we've picked up so far, so you can get more out of the feature.

A quick caveat first: the playbook is still being written. Dynamic workflows lean on more tokens than a normal request, so be intentional about _when_ and _how_ you bring them in.

## Example prompts

Before getting into the how, here are a few prompts to widen your sense of the possibilities:

-   _"This test fails maybe 1 in 50 runs. Stand up a workflow to reproduce it, form theories, and adversarially test them in worktrees. /goal - keep going until one theory holds."_
    
-   _"Run a workflow over my last 50 sessions, pull out the corrections I keep repeating, and convert the recurring ones into_ `CLAUDE.md` _rules."_
    
-   _"Spin up a workflow that searches #incidents in Slack across the past six months and surfaces recurring root causes nobody ever opened a ticket for."_
    
-   _"Take my business plan and run a workflow where separate agents pick it apart as an investor, a customer, and a competitor would."_
    
-   _"Here are 80 résumés in a folder. Use a workflow to rank them for the backend role and re-check the top ten. Interview me with the AskUserQuestion tool to build the rubric."_
    
-   _"I need a name for this CLI tool. Use a workflow to generate a long list and run a tournament down to the top 3."_
    
-   _"Use a workflow to rename our_ `User` _model to_ `Account` _across the whole codebase."_
    
-   _"Walk my blog post draft through a workflow and check every technical claim against the codebase - I refuse to ship anything inaccurate."_
    

## How dynamic workflows work

At the core, a dynamic workflow executes a JavaScript file that exposes a handful of special functions for spawning subagents and coordinating between them.

![](https://hfbnuyccaqnjpljtffvu.supabase.co/storage/v1/object/public/blog-images/harness1.jpeg)

The same file carries the usual JavaScript building blocks too - `JSON`, `Math`, `Array`, and the rest - so Claude can wrangle and transform data as the workflow runs.

Two capabilities deserve special attention. A workflow can choose **which model powers each agent**, and it can decide **whether a given subagent runs inside its own worktree**. Practically, that means Claude can tune both the horsepower and the isolation each unit of work calls for.

There's also a nice safety net: if a workflow is interrupted - say you intervene, or you close the terminal - reopening the session lets it resume from exactly where it stopped.

## Why dynamic workflows

Hand a task to Claude Code's default harness and it has to **plan and carry it out in a single context window**. Plenty of coding work fits that mold just fine. The cracks show on tasks that run long, parallelize heavily, or are tightly structured and adversarial.

Here's why: the more time Claude spends churning on a complex task within one context window, the more vulnerable it becomes to three particular failure modes.

-   **Agentic laziness** - Claude bails on a complex, multi-step task and announces it's finished after only partial progress. Picture it knocking out 20 of 50 items in a security review and calling that done.
    
-   **Self-preferential bias** - Claude leans toward its own outputs and conclusions, most noticeably when it's the one verifying or scoring them against a rubric.
    
-   **Goal drift** - the gradual fraying of fidelity to the original objective over many turns, particularly after compaction. Each round of summarization loses a little, and that's precisely where edge-case requirements and "don't do X" constraints tend to slip away.
    

Reaching for a workflow heads off all three by design, because it orchestrates **independent Claudes**, each holding its own context window and chasing one narrow, isolated goal.

## Dynamic vs. static workflows

If you've ever wired several Claude Code instances together - with the Claude Agent SDK or `claude -p` - you've already built what amounts to a _static_ workflow.

The catch with static workflows is that they have to cover every edge case, which pushes them toward the generic. With **Claude Opus 4.8** plus dynamic workflows, Claude is now capable enough to write a harness custom-fit to the situation in front of it, rather than a catch-all script.

![](https://hfbnuyccaqnjpljtffvu.supabase.co/storage/v1/object/public/blog-images/harness2.jpeg)

## Patterns worth knowing

Getting a dynamic workflow going is as simple as asking Claude to build one - or dropping in the trigger word **"ultracode"** to make certain Claude Code spins up a workflow.

That said, a mental model of _how_ workflows fit together will tell you when to use them and how to steer Claude with your prompts. These are the recurring building blocks Claude reaches for, frequently stacked on top of one another:

![](https://hfbnuyccaqnjpljtffvu.supabase.co/storage/v1/object/public/blog-images/harness3.jpeg)

**Classify-and-act.** A classifier agent figures out what kind of task this is, then routes to the appropriate agents or behaviors. You can also drop a classifier at the _end_ to determine how the output is shaped.

**Fan-out-and-synthesize.** Break a task into many smaller pieces, run an agent on each, then synthesize. This is ideal when there are lots of little steps, or when each step does better with a clean context window so they can't bleed into or contaminate one another. The synthesize step is a **barrier** - it holds until every fan-out agent has finished, then folds their structured outputs into one result.

**Adversarial verification.** For every agent you spawn, spawn a partner agent whose sole purpose is to adversarially test the first one's output against a rubric or set of criteria.

**Generate-and-filter.** Produce a batch of ideas, screen them through a rubric or verification, strip out the duplicates, and keep only the strongest, vetted candidates.

**Tournament.** Rather than splitting the work, let agents _contend_ for it. Spawn N agents that each take a run at the same task using different approaches, then have prompts or models judge the outputs pairwise - through a judging agent - until one winner stands.

**Loop until done.** When the workload is open-ended, keep spawning agents until a stop condition trips (nothing new surfacing, or no errors left in the logs) instead of locking in a fixed number of passes.

## Use cases

It's worth being imaginative about when you ask Claude Code to build a dynamic workflow. In our experience, the biggest wins often come from _non-technical_ work.

![](https://hfbnuyccaqnjpljtffvu.supabase.co/storage/v1/object/public/blog-images/harness4.jpeg)

### Migrations and refactors

Bun was ported from Zig to Rust with workflows - Jarred laid out the approach in an X thread. The move is to break the migration into a stream of units that all need the same treatment: callsites, failing tests, modules, and the like. Fire off a subagent per fix in its own worktree, have another agent adversarially review it, and merge. One practical note: instruct the agents to steer clear of resource-heavy commands so you can parallelize hard without starving your machine.

### Deep research

Anthropic released a deep research skill (`/deep-research`) within Claude Code that runs on dynamic workflows. It fans out web searches, pulls sources, adversarially checks the claims in them, and assembles a fully cited report.

The pattern reaches well past web search, too. Aim it at Slack to stitch together a status report from scattered threads, or turn it loose on a codebase to trace how a feature genuinely works end to end.

### Deep verification

![](https://hfbnuyccaqnjpljtffvu.supabase.co/storage/v1/object/public/blog-images/harness5.jpeg)

Now run the research workflow in reverse. When you've got a report and you want every factual claim verified and sourced, set up a workflow where one agent catalogs all the claims, then spins off a dedicated subagent to scrutinize each one. You can push it a level further by adding a verification agent that audits the claim-checking subagent to make sure the source it landed on is actually credible.

### Sorting

![](https://hfbnuyccaqnjpljtffvu.supabase.co/storage/v1/object/public/blog-images/harness6.jpeg)

Suppose you've got a list to sort along some qualitative dimension that Claude is genuinely good at assessing - support tickets ordered by bug severity, for example. Ask it to sort 1,000+ rows in one prompt and quality falls apart, it won't fit in context to begin with. Use a tournament instead, or a pipeline of pairwise-comparison agents (head-to-head judgment beats absolute scoring), or bucket-rank in parallel and merge afterward. Since each comparison is its own agent, the deterministic loop keeps the bracket and only the running order has to sit in context.

### Memory and rule adherence

![](https://hfbnuyccaqnjpljtffvu.supabase.co/storage/v1/object/public/blog-images/harness7.jpeg)

When there's a set of rules Claude keeps overlooking - even after you've written them into your `CLAUDE.md` files - set up a workflow that lists the rules out and assigns **one verifier agent per rule**. Layering in a skeptic persona subagent to vet the rules themselves keeps the false positives in check.

The reverse path works just as well. Sift your recent sessions and code-review comments for the corrections you keep making, cluster them with parallel agents, adversarially test each candidate (_would this rule actually have caught a real mistake?_), and boil the survivors down into a `CLAUDE.md`.

### Root-cause investigation

The best debugging comes from generating several independent hypotheses and putting each to the test - but inside one context window, Claude slides into self-preferential bias.

A workflow heads that off structurally by spinning up agents that build hypotheses from **non-overlapping evidence**: one on logs, one on files, one on data. Each hypothesis then runs the gauntlet of a panel of verifiers and refuters.

This goes well beyond code. The very same shape fits sales (_why did revenue dip in March?_), data engineering (_why did this pipeline fail?_), and any post-mortem you care to run.

### Triaging at scale

![](https://hfbnuyccaqnjpljtffvu.supabase.co/storage/v1/object/public/blog-images/harness8.jpeg)

Every team is sitting on a support queue, a stack of bug reports, or some other backlog no human team can fully chew through. A triage workflow classifies each item, dedupes it against what's already on the books, and acts - either attempting the fix or kicking it up to a person.

A pattern that earns its keep here is **quarantine**: keep the agents reading untrusted public content away from high-privilege actions, and route those actions to a separate set of agents tasked with acting on the findings. Combine triage workflows with `/loop` to keep them running nonstop.

### Exploration and taste

Workflows are a strong fit for exploring competing approaches - especially the taste-driven kind, like design or naming, that benefit from a rubric. Ask Claude to range across a set of solutions and give a review agent a rubric for what "good" looks like. The job wraps when the review agent decides the bar has been cleared. You can also rank or pick among the candidates with a tournament scored against that rubric.

### Evals

You can run lightweight evals by firing off separate agents in a worktree and then spinning up comparison agents to grade their outputs against a rubric. A natural fit: assessing - and then iteratively sharpening - a skill you've built against a defined set of criteria.

### Model and intelligence routing

Set up a classifier agent tuned to your workload that picks the model for the job. It's particularly useful when a task is heavy on tool calls and a little upfront research can point to the right model. Take _"explain how the auth module works"_ - the ideal model hinges on how many files sit in that module and the shape of the broader codebase. A classifier agent can scout that out first and then route to Sonnet or Opus based on the complexity it expects.

## When _not_ to use dynamic workflows

Workflows are new, and although they deliver outsized results in many settings, they aren't required for every task - and they can run up a meaningfully larger token bill.

Use them inventively to push Claude Code somewhere you couldn't go before. For everyday coding, ask the honest question: _does this genuinely need more compute?_ Most ordinary coding tasks don't warrant a panel of five reviewers.

## Tips for building dynamic workflows

**Prompt with detail.** The specific techniques above pay off most when you write them out explicitly in your prompt.

**Go small when it fits.** Workflows aren't reserved for big jobs. You can ask for a _"quick workflow"_ - for instance, a fast adversarial gut-check on a single assumption.

**Pair with** `/goal` **and** `/loop`**.** For workflows you'll rerun - triage, research, verification - combine them with `/loop` to fire on a schedule and `/goal` to lock in a hard completion bar.

**Cap your tokens.** You can put a ceiling on a task's token spend. Just say something like _"use 10k tokens"_ and that becomes the limit.

**Save and share.** Hit **"s"** in the workflow menu to save one. Stash the files in `~/.claude/workflows`, or ship them inside a skill. To share through a skill, place your JavaScript workflow files in the skill folder and point to them in the `SKILL.md`. For more headroom, prompt Claude to treat a skill's workflows as _templates_ rather than scripts to run word for word.

![](https://hfbnuyccaqnjpljtffvu.supabase.co/storage/v1/object/public/blog-images/harness9.jpeg)

To share them via a skill, put your JavaScript workflow files in the skill and folder and reference them in the `SKILL.md`. To allow for more flexibility, you may want to prompt Claude to think of the workflows in the skill as a template instead of a script that needs to be run verbatim.

![](https://hfbnuyccaqnjpljtffvu.supabase.co/storage/v1/object/public/blog-images/harness10.jpeg)

## A whole new world

Dynamic workflows are a powerful addition to Claude Code - and we suspect this is just the opening move. At LAXIMA, they've already changed how we tackle migrations, triage, research, and verification across the systems we build for clients. There's still a lot left to learn about wielding them well.

_Many thanks to_ [_Thariq_](https://x.com/trq212?s=21) _from the Anthropic team for providing the information._
