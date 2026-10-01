# A5 frozen correction: source GO within the reviewed boundary

TO: Buford lead `01a0f594-02cb-72a1-8a9b-46c32e99f1a8`.
FROM: Codex independent source reviewer `01a0f692-3256-72e3-8d95-4bf7e7046e8f`, actual GPT-6.1-sol/high.
Assignment: `arhugula-harness-trial-193` / `cmt-7445a7ac-c28b-4cd4-a0a6-0ba34ce22f57`.

**Disposition: the four demonstrated P2 counterexamples are corrected. No new demonstrated P1/P2 was established.** One independent bounded run passed all **16 newly added counterexample cases**, exit 0. This is a source correction review, with the limits below. It does not accept the complete first-release filesystem/subscription requirement, discharge the socket permission HOLD, produce formal-cycle rows, or approve an installed candidate.

The immutable head is `a2573ac217103bb2c9a72f33b12f3ef86df0abb0`, sole parent `c33ed91578570c9ed5ed16c07eb9f5f884ff84a7`, in `.worktrees/a5-codex-read-boundary-20261001`. Commit UTC is 2026-10-01T08:59:59Z. The nine correction files matched the author's committed SHA-256 pins before verification; the final check is in `pins.json`. All changed production code, the nine-file corrective diff, relevant original launcher/runner/configuration code, changed normative rows, operator document, production constructors/callers and selected fixtures were inspected. The prior independent report belongs to reviewer `01a0f67a-8beb-7353-8603-ac9ebf915873`; its counterexamples and results retain that attribution.

## Four P2 dispositions

Line references below resolve in the frozen A5 worktree. `cli` means `harness-runtime/src/harness_runtime/lifecycle/cli_read_boundary.py`; `runner` means its sibling `external_cli_provider.py`.

| Earlier P2 | Independent disposition and evidence |
| --- | --- |
| 1. A symlink allowance reaches broad HOME | **Closed for the demonstrated cases.** `cli:310` opens each grant once with NOFOLLOW/CLOEXEC, checks the fd's actual path, symlink mode and device/inode against protected roots/ancestors, then adds the rule to that same fd (`cli:375`). The production runner canonicalizes ordinary allowances first (`runner:634`, `runner:664`); an alias resolving to HOME therefore reaches the protected-inode refusal, rather than retaining a harmless alias spelling. Seven independent cases passed: five broad paths, a symlink to fake HOME, and an ancestor symlink supplied directly to the launcher. `[LAW:single-enforcer]` Safety is enforced on the granted object. This does not establish a universal concurrent-renaming proof. |
| 2. Interactive `.codex` passes as dedicated | **Closed for the demonstrated residence cases.** `runner:629` seals the harness process's `CODEX_HOME`, otherwise HOME/.codex. `cli:300` includes the sealed root's ancestors in the forbidden grant identities; `cli:323` rejects grants whose pathname lineage intersects the sealed root. Final home symlinks also fail preflight (`runner:668`); canonical ancestor aliases are checked at launch. Five independent cases passed: direct residence/descendant launcher grants and the runner's dot-codex, inside-dot-codex and CODEX_HOME cases. Ancestor and ordinary symlink-alias refusal follows the inspected composition, but those additional runner variants were not newly executed. Private directory metadata does **not** prove dedicated contents. `[LAW:parse-dont-validate]` Keep this narrower proof distinct from content provenance. |
| 3. fd 256 survives soft limit 64 | **Closed.** `cli:257` uses syscall `close_range(3, UINT_MAX, 0)` and refuses a failure, before opening its own descriptors (`cli:409`). The independent real-launch test opens an owned dummy file at inheritable fd 256, lowers the soft limit to 64, execs the actual launcher, and observes EBADF in the target. No unrelated file contents are read. `[LAW:verifiable-goals]` The test exercises the original high-fd counterexample. |
| 4. Named Codex selects generic-command | **Closed for the configured named route and default construction.** `types.py:1735` rejects a provider name equal to an adapter kind carrying another kind, after field normalization. The production path is `providers.py:710` → `construct_external_cli_adapter` (`runner:1489`) → `construct_codex_cli_adapter` (`runner:1397`) → `_CodexReadBoundaryRunner`. Both auth (`runner:1305`) and inference (`runner:738`) use the chosen runner. The boundary error subclasses command error (`runner:119`), maps to ProviderTransientError (`providers.py:717`), and optional construction degrades (`providers.py:804`). The independent conflicting-config case and both real stage-3a optional/required cases passed, using fake Ollama construction and no Codex process. An independently named generic-command entry is still excluded by the existing profile. `[LAW:types-are-the-program]` The named identity/kind conflict cannot parse. |

Metadata OSErrors from the configured home/root and auth lstat now become the typed boundary refusal. Launcher faults also refuse through the marker/exit mapping; there is no bare-runner fallback in the default production graph. Public runner injection remains a trusted Python caller convention. The current production default caller supplies no injected runner; this review did not certify arbitrary embedding callers.

## New findings and qualified hypotheses

### P3: configured symlink refusal is overstated in prose

`docs/operations/omarchy-codex-read-boundary.md:31` says an allowed path reaching its target through a symlink refuses. Runtime spec v1.135:69 makes a similar overall-launch claim. But `runner:634–636,664` resolves ordinary grants before constructing the spec. A configured alias to an otherwise permitted public directory can become its canonical target and pass `cli:319`. The direct-launch ancestor-symlink test exercises an uncanonicalized spec, so it does not prove the stronger production configuration claim.

This is a **static prose/contract mismatch**, with that concrete input and call trace; the benign alias was not separately executed in this bounded review. It does not reopen broad-HOME exposure: the canonical target still meets the protected-root check. Disposition: describe canonical-target enforcement and distinguish it from the executable's symlink refusal and the configured home's final-symlink preflight. Retain it as a P3/prose follow-up under the standing review policy. `[LAW:one-source-of-truth]` The description must follow the actual runner/launcher composition.

### P2-impact hypotheses: mount topology and concurrent path replacement remain unproved

These are **qualified hypotheses, not newly established defects**. The grant fd's identity and the fd used for the rule agree, but `_lineage(actual)` and protected/sealed root discovery use separate pathname stats (`cli:274–323`). A concurrent rename/replacement could alter that lineage between observation and enforcement. Ownership/mode/auth preflight similarly is not bound to the granted fd. This assignment performed no race probe.

Device/inode equality handles an alias of the sealed root itself. It does not by itself prove ancestry for every alias: binding a *descendant* of the sealed residence at an unrelated mountpoint could yield a visible ancestor chain with no sealed-root inode. The static trace is `_lineage(alias)` → alias and visible parents → intersection with the sealed-root identity. **No bind mount was created or exercised**, and no universal mount-alias guarantee is accepted. Before installed acceptance, Buford must either establish the applicable filesystem/configuration assumptions with evidence or retain this boundary as held. The spec's UNVERIFIED disclosure is preserved.

## Scope and trust assumptions

The original `profile-contract-decision-1.md` was read in full and hash-pinned. Its generic-command, Gemini and Antigravity **inference** exclusions are already explicit; this review requests no re-ratification of them and changes no standing OAuth Antigravity development-review authority. An excluded generic route running a configured Codex binary is not evidence that the now-validated named Codex route bypasses its boundary.

For the included route, the source establishes filesystem rules for the declared grants. It depends on trusted runtime configuration and filesystem state: the dedicated home must contain only harness state, and public read allowances must contain no unrelated user data. `~/Documents` is not automatically refused. Those are substantive conditions on the accepted configuration, not proof of the unconditional claim “all unrelated user files are inaccessible.” The Proposed spec and operator document now disclose them; installed acceptance must bind the actual configuration and home provenance. No existing profile hold is silently narrowed or closed by this report.

Other disclosed residuals remain: unknown ABI versions are accepted with the known bits 0–16 mask (`cli:107,116`); networking is unhandled (`cli:363`), including local TCP file servers; executable hashing and exec share one descriptor but cannot freeze in-place inode modification (`cli:328,415`); running the harness with its dedicated home as the harness's own CODEX_HOME seals that home and refuses. No current-host new counterexample was established from these residuals. They prevent a whole-isolation or future-ABI guarantee. Subscription login/status/version/inference and token-refresh behavior remain NOTRUN.

## Independent verification and retained author evidence

The new run used the existing author's Python 3.12.14 at `.worktrees/a3-ollama-mcp-20261001/.venv/bin/python`, with a minimal environment, private owned TMPDIR/fake HOME, bytecode/cache writes disabled, and existing pytest-asyncio explicitly loaded while other external plugin autoload was disabled. All seven actual package origins were asserted equal to A5/src before pytest ran (`logs/origins.json`). The selected tests create disposable fake HOME/history/auth fixtures, or run the pinned interpreter as a dummy target. They execute no real Codex or model. The shared autouse capacity-reset fixture and the new simulated-operator fixture were inspected.

Exact outer argv/environment are in `logs/counterexamples.json`; exact pytest argv is in `verification-child.py` and `selected-nodes.json`, and all 16 actual collected nodes are in `logs/collected.json`. The 300-second bound did not trigger. UTC **09:28:14.476164 → 09:30:12.549123**, elapsed **118.073 seconds**, **16 passed in 31.54s**, exit **0**, empty stderr. The process was reaped; no review handle remains. This was one run, without source mutations, assertions weakened, permission escalation or a repeat pass. `[LAW:behavior-not-structure]` Its load-bearing assertions observe actual launcher refusal, descriptor closure and production-stage behavior.

The author's committed-head final run remains **author evidence**: UTC 09:00:14.184189330 → 09:03:54.823116909, 222 passed in 53.58s, exit 0. The retained five final mutants were killed and restored to matching committed hashes (two, five, three, one and one failures respectively); this reviewer did not rerun mutations. The author strict Pyright configuration has three actual relative targets, explicit existing-venv discovery, and statistics naming all three files: zero errors, exit 0. That supersedes neither the retained vacuous old author includes log nor this review's NOTRUN typecheck. Ruff/format results remain attributed author results.

Historical failures remain intact: red-1 had 15 failures/31 passes, including the cancellation fixture's missing PID file after its two-second bound. The author's host-load explanation is unverified here; no historical cause is inferred. Green-1 had one symlink failure/45 passes because the target ran; the final `S_ISLNK` refusal addresses that case. Neither log was overwritten or reclassified.

### Socket provenance: earlier permission HOLD remains open

The author final command selects the **entire** `test_cli_read_boundary.py`, including `test_unix_sockets_created_outside_the_domain_are_unreachable`. That function is byte-identical across c33 and a257 (SHA-256 in `logs/socket-fixture-provenance.json`). It calls pathname and abstract socket bind/listen and then confined connect probes. The retained author final result contains no skipped or failed tests, so it supports an **author-lane** success for that selected fixture. It does not establish normal approval provenance or resolve the earlier independent EPERM-at-bind question.

Accordingly, the author's statement that this was “not a retry” is not independently accepted as permission/no-retry compliance. This review did not run any socket bind/connect fixture, change permissions or retry the denied operation. Buford still owes the permission/evidence disposition. The earlier independent 138-pass/one-fixture-failure result remains unchanged and attributed to its original reviewer.

## Complete sizing before formal pass 1

Counts are actual Git numstat additions plus deletions; every changed non-test file is included. Tests are separately identified by their `/tests/` paths. Full file rows are retained in pins and `logs/*.numstat`.

| Frozen diff | Production changed | Other non-test changed | All non-test changed | Test changed | All changed |
| --- | ---: | ---: | ---: | ---: | ---: |
| c33 → a257 correction | 193 | 63 | **256** | 179 | 435 |
| c6d017 → a257 complete A5 arc | 665 | 286 | **951** | 712 | 1663 |
| main 5d93b0 → a257, including inherited A3 | 1182 | 470 | **1652** | 1768 | 3420 |

The author's four cut points are an unexecuted source proposal. The complete 951-line A5 arc exceeds the near-300 changed non-test rule (`.claude/skills/merge-gate/SKILL.md:279`); the correction's 256 does not make the whole arc a small unit. Count the actual packaged docs/contracts and gates with each unit before formal pass 1. The previously delivered A3 plan was read fully in this session; its 298/267 figures also allocate production hunks, not whole-unit non-test totals. No source package, intermediate head, branch/ref, reservation or clearance marker was created here.

## Remaining gates and release

Buford owns disposition, packaging and integration. Runtime v1.135/plan v2.66 remain Proposed; the final A3 619 parsing/contract fold into this older c6 lineage, collision check and clearance remain owed. No A4/A5 ownership was borrowed. Product grounding/preflight/closeout helpers, full codex-check, formal bounded-cycle producer rows/lenses, PR/base CI, main landing/post-main CI and installed/security/subscription gates were **NOTRUN**. Read-only source traces supplied the review; no Graft/overlay verification or gate compliance is claimed.

Root AGENTS, context/role/routing authority and applicable full Laws:Code, Laws:Chat and Laws:Prose plus its craft were retrieved. Relevant product review/sizing guidance was inspected as reference; no shipping or merge skill was executed. The user-selected model/effort persists. Root repair_paused=false was verified.

**RELEASED.** Source, tests, specs, credentials and Git refs remain unchanged. Only owned report/pins/log artifacts and the required LIT completion/one native queue pointer are written. No provider/helper/service/live operation, installed action, agent or remaining writer/process handle. Final evidence hashes, context measurement and coordination disposition are retained in `pins.json`.
