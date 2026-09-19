#!/usr/bin/env python3
"""Re-cluster the live gate log against the skill's defect classes.

The checklist in SKILL.md is a distilled map of `.harness/merge-gate-log.jsonl`;
the log is the one authority and only grows. This prints (a) current per-class
counts — compare them to the counts baked into SKILL.md and refresh the text when
they have moved meaningfully — and (b) the most recent findings that match NO
known class: those are candidates for a new class, surfaced mechanically instead
of waiting for recall. The report is advisory by design: it always exits 0 and its
output is for the agent running the preflight, never a gate.

The `classify` verb is the one consumer-facing seam: `tools/review_loop_gate.py`
feeds it an arc's outstanding reviewer findings at sweep template/attest time, and a
finding it leaves unmatched owes the author an `intake:` disposition there (SKILL.md
"When a reviewer catches what this sweep missed"). That verb exits non-zero on
malformed input — the gate must never read 'could not classify' as 'unmatched'.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# One definition per class, mirroring SKILL.md's class sections. When a class is
# added or reworded there, extend this table in the same commit (the counts the
# skill cites are derived HERE, so a drifted table silently mis-buckets, and a
# class absent here can never leave the unmatched bucket — it reads as a
# new-class candidate forever). Classes 11–14 were added by U-SR-01; 11 had been
# carried in SKILL.md since U-HE-47 without a row here.
#
# A row is EITHER one pattern — any alternative IS the class — OR a TUPLE of patterns
# that must ALL match, for the two classes that name two conditions in their own title.
# The conjunction was first written as `(?=.*A)(?=.*B)` and that was a product type
# squeezed into a string: with `re.search` the unanchored lookaheads retry both
# whole-suffix scans at every character, costing 12.3s and 17.4s on the committed corpus
# against under 0.11s for every other row, and degrading as this append-only log grows
# (codex r5 P2, reproduced before absorbing). Two independent searches are linear and say
# what they mean.
#
# UNDER-matching is the safe direction and is chosen deliberately throughout: a missed
# row stays in the unmatched new-class discovery pile, while a false match silently
# removes it from that pile. Prefer to miss.
#
# Known precision bound, named rather than chased: a conjunction still matches on
# CO-OCCURRENCE, so a row pairing an unrelated command term with an unrelated loop term
# can land in class 13, and a finding whose text DISCUSSES a class necessarily contains
# that class's vocabulary. This tool is advisory by its own docstring and multi-match is
# by design; successive regex layers were measured trading one imprecision for another
# without converging, so the bound is documented here rather than chased further.
#
# Vocabulary evaluated and LEFT OUT (so it is not re-proposed): `drift` for class 2
# (handoff-s2 §2 B, 2026-09-16). At that day's corpus of 2,103 findings, 35 rows said
# "drift" and 30 of them matched no class-2 term — but read, they are contract drift
# (a witness that codifies a spec departure), configuration drift, roadmap drift and the
# arc-metrics `drift` cohort/fixture; prose decay in the class-2 sense was at most 2
# rows under any prose-adjacent form tried. A bare `\bdrift` would have moved the 30
# out of the new-class intake pile, the wrong direction under the policy above (codex
# r1 P2 on the class-2-drift-extension arc). The recurring "test codifies the drift"
# shape that note pointed at is now class 16 — 14 unmatched rows in the gate log as of
# base 63e19e3ee (2,162 findings) — and is still not a class-2 term.
# ALSO evaluated and LEFT OUT: a claim-vs-code half for class 2 (2026-09-17, the
# handoff-s2 supersede arc). Shape: prose ASSERTING a mechanism behaviour the code does not
# have — never true, as opposed to the drift half, which was true and decayed. Pattern tried:
# a claim-bearing subject (`claims|states|says|documented|guarantees|asserts`) within 120
# non-sentence characters of a falsity marker (`but|is false|does not|never|contradict|
# incorrectly`). At the 2,191-finding corpus it claimed 40 previously-unmatched rows and
# leaked 0 of the `contradicting C-HE-NN` code-vs-contract cluster (a bare `contradict`
# sweeps that whole cluster in — the same wrong direction as `drift`). It was still REFUSED,
# on codex r2 P2: 6 of the 40 are operational uses of the same verbs in non-prose findings
# (`arc_metrics.py:686` "a peer just claimed it, but"; `lib.sh:803` a lease claim;
# `reservations.py:806` "asserted only via any()"), and a class-2 false positive REMOVES a
# row from the unmatched pile, which is where new classes are discovered — the wrong
# direction again. The discriminator this needs (is "claim" a sentence or a lease?) is not
# in the classifier's input at all: `finding_text` is evidence plus location, and neither
# says which. Two review rounds landed on this one mechanism, so it was subtracted rather
# than hardened further. A future attempt needs a different INPUT (the cited file's own
# bytes), not a wider vocabulary.
# ALSO evaluated and LEFT OUT: a "validator reads a sub-span, accepts the rest unseen" class
# (2026-09-17, the handoff-s2 supersede arc). The SHAPE is real and recurs across arcs — a
# guard examines one element, one cell, one field, and treats the remainder as inspected.
# The vocabulary is what fails. Three measured attempts: bare `only the first|unanchored`
# claimed 10 rows across 9 arcs but two were different defects entirely, one reading too MUCH
# (codex r7); narrowing to `validates only|never validates|does not validate` gave 7 rows
# across 7 arcs but `never validates` / `does not validate` match TOTAL absence of validation,
# which is not this shape at all — the class's own witness row, "Automatic rollback does not
# validate the DELETE result", inspects no part of the result (codex r10); widening instead to
# `checks only|requires only|examines only` reached 21 rows but ~6 were unrelated (a symlink
# TOCTOU, a migration, two skill-doc findings), so precision fell to about 71%.
# The discriminator the class needs is a CONJUNCTION — evidence of an inspected portion AND an
# uninspected remainder — and a finding's free text does not reliably carry both halves. A
# class-17 false positive REMOVES a row from the unmatched pile where new classes are found,
# so precision-first is the stated policy and no variant met it. Same wall as the claim-vs-code
# extension above, reached from a different direction. The shape is worth catching BY HAND —
# "does this check consume its whole input, or match a span and let the rest through?" — and
# that question lives in SKILL.md; a future attempt needs a different INPUT, not a wider
# vocabulary.
# ALSO evaluated and LEFT OUT: an "owed pointer refresh" class (U-HE-45, 2026-09-18). The
# SHAPE is real and recurs — a diff finishes work and leaves a surface consumers read to
# decide what to do next still naming what was just finished (6-8 corpus rows: Step-5-
# executed-but-plan-still-unticked, fence-live-but-roadmap_status-still-says, decisions-
# ratified-but-version-summary-still-open). It is NOT a class because the vocabulary cannot
# carry it, measured over three review rounds -- r2, r3 and r5 of that arc, NOT three
# consecutive ones (r4's findings were elsewhere) -- each trading one imprecision for another:
#   (a) `(?:never|not |un)refreshe?` gave the `never` arm no separator, so it demanded
#       "neverrefresh" and missed the plainest wording. It hid because the arc's own finding
#       matched a DIFFERENT arm — a masked alternative is invisible until a row needs only it.
#   (b) `just completed` / `already landed` need not describe the pointer at all: "The live
#       pointer just completed validation successfully" matched while reporting no staleness.
#   (c) `still (?:says|names|points)` has NO POLARITY, and polarity is not regex-expressible:
#       "The live pointer is fresh and still points to the intended next unit" matches, so a
#       CORRECT pointer reads as a stale one.
# Each round's fix bought exactly one more round in which to find the next false surface, and
# a false match is worse than `unmatched` — unmatched OWES an intake line, a false match
# silences it, so an over-broad row actively hides new classes. Subtracted per the recorded
# rule that an adversarial-hardening loop does not converge by adding layers. The substantive
# defect this shape named on that arc is registered as B-288 instead, where prose can carry
# the polarity a regex cannot. Note also that tools/test_governance_router.py already
# forward-references "class 17" for the sub-span shape, so the number was spoken for.
# ALSO evaluated and LEFT OUT: a "record field contradicts its own body" class (U-HE-45's
# plan-record arc, 2026-09-18). The SHAPE is real and has two measured instances one arc apart:
# `B-282` shipped `status: open` while its own summary said U-HE-40 is HELD (and OPEN_STATUSES
# excludes `held`, so `--open` counted a blocked row as executable), and a U-HE-45 plan tick
# marked a COMBINED step `[x]` while the paragraph beneath it said half that step was never
# performed. Four corpus rows carry it. It is NOT a class because the vocabulary cannot
# distinguish prose that DESCRIBES a field from prose that SETS one, and three review rounds
# each traded one imprecision for another:
#   (a) two independent tuple patterns matched across SENTENCES ("The status field is parsed
#       correctly. The hook still fails even though ..."), fixed with class 16's window;
#   (b) the same terms then matched unrelated text WITHIN one sentence ("The status field is
#       parsed correctly even though a missing verdict file makes the unrelated hook fail") --
#       no window can separate those;
#   (c) `mark` without a word boundary matched inside `benchmarks` ("The benchmarks remain open
#       even though the sample size is small").
# (b) is the terminal one, and it is the wall the withdrawn owed-pointer class hit too: the
# distinction is SEMANTIC, not lexical. A false match is worse than `unmatched` -- unmatched
# OWES an intake line, a false match silences it -- so an arm that cannot tell "describes a
# field" from "sets a field" actively hides the new classes this table exists to surface.
# Sweep the shape BY HAND: for every status, disposition or checkbox a diff SETS, does the body
# of that same record agree, and which consumer reads the field rather than the body?
# ALSO evaluated and LEFT OUT: vocabulary for "a record contradicts its own evidence"
# (U-HE-45's plan-record arc, 2026-09-18). The SHAPE is class 2's own subject and it recurred
# twice in that arc -- a review audit stating finding counts the gate log's round_n refutes, and
# a cleared marker naming two of the four rows `--open` emits. THREE terms were tried against it
# and all three were withdrawn, each for the same reason one layer down:
#   * `omits` -- measured at +84 corpus rows and rejected before shipping.
#   * `,\s*not\s+\d` -- shipped, then removed one round later: it matches ANY numeric contrast
#     ("The API returns 1, not 2."). The error was treating BREADTH on the current corpus (+3
#     rows, each inspected and genuine) as PRECISION -- a corpus that happens not to contain a
#     phrasing does not exclude it, and this table is read against findings that do not exist yet.
#   * `identifies only` -- shipped on the claim that it is SEMANTICALLY bounded to a record's
#     completeness, and removed the next round when that claim proved false: "The sanitizer
#     identifies only SQL injection and therefore lets XSS through" is an implementation defect.
#     Anything that identifies things can identify only some of them.
# The lesson is not about these three words. A finding's prose DESCRIBING a record is lexically
# indistinguishable from prose ABOUT the thing the record describes, which is the same wall the
# withdrawn class-17 (polarity) and class-18 (reference) vocabularies hit. Sweep it by hand: for
# every count, status or completeness claim a record states, which source of truth refutes it,
# and did you read that source THIS session?
CLASSES: dict[str, str | tuple[str, ...]] = {
    "1 race / TOCTOU / atomicity / lock": (
        # `symlink` belongs to this class by its own containment rider (the O_NOFOLLOW +
        # post-open fstat idiom), which the vocabulary did not carry. Measured at the
        # 2,247-finding corpus: 72 rows mention it, 10 of them matched NO class, and all
        # ten are containment defects -- a planted or dangling link read as
        # absent, or followed without containment.
        r"race|TOCTOU|atomic|lock|flock|concurrent|interleav|CAS|exclusive|symlink"
    ),
    "2 prose stale / counts / cites": (
        r"stale|close_out|mis-cite|cite|count|narrat|docstring claim|partition"
    ),
    # No term here describes THIS TABLE, deliberately. Every phrasing tried for it
    # ("intake path", "intake pile", "classifies unrelated") reads just as naturally in
    # findings about ingestion endpoints and queue growth, and the narrowing never converged:
    # successive review rounds of one arc, each finding correct, each attacking the
    # phrase the last one added. A classifier cannot be widened to catch the complaint that
    # it is too wide. Findings ABOUT this table stay in the unmatched pile, where a human
    # reads them -- the prefer-to-miss policy stated above, applied to the table itself.
    "3 silent failure / fallback": (
        r"swallow|silent|fallback|2>/dev/null|\|\| true|exit code|ignored error"
    ),
    "4 vacuous witness": (
        r"witness|vacuous|stays green|cannot fail|only .*presence|never red"
        r"|does not red|remains green|unexercised"
        r"|leaves? (this|the) (test|suite) green"
    ),
    "5 timeout / retry / budget": r"timeout|retry|budget|backoff|deadline",
    "6 unreachable / dead branch": (
        r"unreachable|dead|never reach|no witness could|half-dead|cannot see|restore arm"
    ),
    # A sourced shell file mutating its caller's shell IS this class's concern in another
    # substrate, but no vocabulary for it survives here. `caller's shell` was tried and
    # WITHDRAWN: it claimed a finding this class does not own -- an EXISTENTIAL claim, which
    # survives a growing corpus because a later row cannot unmake an earlier one. Under the
    # prefer-to-miss policy a term that steals from the unmatched pile does not earn its place.
    # What is NOT restated is any COUNT or PRECISION figure; that evidence
    # is deliberately NOT restated here. The gate log only grows -- including with this arc's
    # own findings -- so any statement about what the term matches is true at one anchor and
    # false at the next -- which review rounds of this arc kept proving. Re-derive with
    # `classify` if you need it. Pinned absent by tools/test_refresh_classes.py.
    "7 env-var mutation / restore": (r"monkeypatch|os\.environ|env var|setenv|restore|undo\(\)"),
    "8 subprocess boundary": (r"subprocess|child process|inherit|process boundary|spawns|nested"),
    "9 path / default resolution": (
        r"fallback ledger|venue|QUEUE_DIR|path default|resolves|home default|\$HOME"
    ),
    "10 fixture scope / lifecycle": (
        r"session-scoped|module-scoped|function-scoped|teardown|collection|autouse|fixture"
    ),
    # Bare `adjudicat` alone pulled 48 rows in that merely MENTION adjudication, and
    # `exemption` was equally context-free (codex r8 P2). Every alternative left names a
    # command/permission surface outright. 158 -> 120.
    "11 authority-bearing command surface": (
        r"permission.guard|auto-allow|allowlist|guard venue|exact.shape|carrier parity"
        r"|gate override"
    ),
    # Both u-he-35 P1s must land here — the skill claims both were this shape, and a
    # classifier that says otherwise makes the claim false. `as the verdict` and
    # `schema-parsed BLOCK` are where the exit-code-as-verdict row matches; `is
    # unenforced` is where the pilot-gate row does. Overlap with class 3 is by design.
    # Every alternative carries BOTH halves of the class — a quoted obligation AND its
    # absence — on its own, so each is a PHRASE, not a token. Dropped once measured:
    # `manifest row` / `copied verbatim` (bare nouns), `unenforced` and `schema-parsed`
    # (too loose; narrowed to the phrases the P1s actually use), `spec phrase` and
    # `contract phrase` (name the obligation but not its absence, so "the contract phrase
    # names the wrong component" landed here), and `undischarged`, which matched zero rows
    # in the entire corpus — a dead alternative is not caution, it is noise with no upside.
    "12 quoted contract phrase not discharged": (
        r"is unenforced|declared but|no code discharges|as the verdict"
        r"|schema-parsed BLOCK"
    ),
    # Conjunctions (measured before absorbing): a flat OR mis-bucketed 33 of 64 class-13
    # rows and 6 of 10 class-14 rows. The command conjunct has been narrowed to terms that
    # mean a NEW command: `justfile` went because the matcher sees `location` too and that
    # token pulled in every finding merely LOCATED there; `just recipe` went because it
    # names any recipe, which let a lane-init logging finding in on co-occurrence with the
    # word "loop"; `allow branch` went because it matched zero rows. Each removal was
    # checked to keep justfile:777, the canonical member of this class.
    "13 new command the loop must reach": (
        r"runs_in|new recipe|new command",
        r"loop|headless|guard|auto-allow|permission|ask prompt",
    ),
    "14 signal handler meets lock": (
        r"signal handler|SIGTERM|SIGINT|SIGHUP|async-signal|self-pipe",
        # word-bounded: a bare `lock` also matched `block`/`blocking`, so a Ctrl-C row
        # that "can block in ThreadPoolExecutor shutdown" landed here with no lock in
        # sight (codex r6 P2). `\block\b` excludes both for free — neither has a word
        # boundary before "lock" — so no extra guard is needed. `RLock` gets its own
        # alternative because there is no boundary inside it either.
        r"\block\b|\blocks\b|RLock|mutex|reentran|acquire",
    ),
    # Added by the preflight-finding-intake arc through its own intake line (the first
    # finding to flow in mechanically): the review-loop gate classified the working
    # tree while the attestation bound base..HEAD; the 2026-08-19 row is the same
    # defect on the reviewer wrapper. Conjunction: a tree-state term AND a binding term
    # — either alone is co-occurrence noise (`committed` is in half the corpus).
    "15 bound bytes are not the executed bytes": (
        r"working tree|live worktree|uncommitted|mutable tree|dirty",
        r"binding|base_sha|head_sha|\bHEAD\b|committed (diff|range|bytes|base)",
    ),
    # Every count here is anchored to the gate log AS OF base 63e19e3ee, never to "the
    # current corpus": this class was measured against the same log its own arc's gate
    # rows append to, so a live total is stale before it is committed (merge-gate witness
    # lens r2, P3 — it read 2,165 where the prose said 2,163). At that base the log holds
    # 2,162 findings, 29 carry a blessing verb, and 14 of those matched no other class —
    # exactly the pile this class empties. `pins the` was measured and DROPPED: its one
    # unmatched hit read "--match-head-commit merely pins the merge", a binding claim with
    # no witness in it.
    #
    # PHRASES, not a tuple (codex r1 P2 on this arc). The first draft paired a verb
    # conjunct with an artifact conjunct, and `matches()` reads `finding_text` — evidence
    # PLUS location — so any finding located in a test file satisfied the artifact half
    # for free. Measured under THAT draft's own artifact half
    # (`\btest|witness|assert|fixture|\bCI\b`, the predicate the claim is about): 263 of
    # the base's 2,162 rows carry a location satisfying it and 30 carry it in the location
    # alone, and "the governing spec codifies the required behavior" at
    # `tools/test_widget.py` classified as this class. A conjunct a path can satisfy does
    # not constrain, and a false match is the one direction the policy above forbids — it
    # removes the row from the intake pile silently. Class 13 paid for this same lesson
    # with `justfile`; class 12 states the remedy: each alternative carries BOTH halves on
    # its own ([LAW:types-are-the-program] — the strongest theorem still true is one about
    # a phrase, never two tokens that co-occur).
    #
    # ORDERING is what fences the location out, structurally rather than by luck: the
    # location is appended LAST, so an artifact-BEFORE-verb phrase can never be satisfied
    # by it (a path contains no verb, and nothing follows a path to supply one).
    #
    # The artifact token took THREE reviewed revisions, all on its boundaries, and the
    # third was subtraction rather than another layer (the step-6 arms-race rule: two
    # consecutive rounds on a mechanism the absorption itself invented). What it is now:
    # `\btests?(?![a-z])` — the WORD, refusing a longer word that merely starts with it.
    # What it was, and why each failed: `\btest\b` (draft 1) rejected `test_happy_path`,
    # since `_` is a word character; `tests?[\w-]*` (draft 2) dropped the LEADING `\b` to
    # fix that and so matched "at-TEST-ation" and "la-TEST" — `attest` is this workspace's
    # own vocabulary, making it the likeliest false match of all (lens r1 P2); the leading
    # `\b` came back, but `[\w-]*` still admitted `testament`/`testimony`/`testify` (lens
    # r2 P2). The identifier tail is carried by the window below, NOT by a trailing class
    # — deleting `[\w-]*` was measured byte-identical on every case, so draft 2's comment
    # credited it for work it never did (lens r2, second P2). The artifact token's three
    # drafts are recall-IDENTICAL at the base anchor: 29 corpus / 14 pile each, measured
    # while the noun arm below was still present. The SHIPPED pattern matches 28 of those
    # 29 — the one it drops is the noun arm's only member, and the pile is 14 either way.
    #
    # ONE ALTERNATIVE, because the second one bought nothing. A `\b(it|CI|witness|
    # fixture|which)\s+...` arm carried the phrasings where the blessing verb's subject is
    # a witness noun rather than the word `test`. Measured at the base anchor it added
    # exactly ONE corpus member over the artifact arm alone (29 vs 28) — and that member
    # already matched another class, so its contribution to the NEW-CLASS PILE, the only
    # thing this class exists to fill, was ZERO: 14 with the arm, 14 without.
    #
    # It was cut in two steps, both measured. `it`/`which` went first (lens r3 P2): bare
    # pronouns matched "and it blesses looser SLAs" with no test vocabulary anywhere. The
    # remaining literal nouns went next (lens r5 P2), because they carry the SAME defect
    # one word later — "The team ignoring the fixture blesses the shortcut", "A witness
    # account later enshrines a different version of events" — and no regex can fix it,
    # since it requires knowing that `fixture` is the sentence's object rather than its
    # subject. Subjecthood is grammar. Zero pile contribution against an unclosable false
    # -match surface is not a tradeoff; the arm's own ≤2-word gap went with it.
    #
    # Residual bound — named rather than chased (the same policy as class 13's
    # co-occurrence bound above). Within one sentence the window admits the word `test`
    # before a blessing verb in THREE shapes this row does not try to tell apart, each
    # verified live: the verb's subject is something else ("the test ran green and the
    # spec codifies the older rule"); `test` in its ordinary-English sense rather than the
    # software one ("the A/B test codifies the winning variant"); and the verb NEGATED
    # ("the test does not codify the drift" — lens r8).
    #
    # The negation shape is named rather than guarded, and the measurement is why: ZERO of
    # the base anchor's 2,162 findings put a negation between this class's `test` token and
    # a blessing verb, matched or not. Contrast the `!`/`?` terminator gap one round
    # earlier, where 13 rows carried the shape and the regex was duly fixed. A negation
    # lookahead would also buy a false NEGATIVE that the corpus makes plausible — "the test
    # does not merely codify X, it enshrines Y" is a real member this class would then lose
    # — so guarding it trades one imprecision for another, which is exactly what the header
    # above records as measured-and-non-converging.
    #
    # What keeps the bound narrow enough to accept is that the word `test` must appear AT
    # ALL for this class to fire, and the window is one sentence wide. FOUR earlier
    # wordings of this paragraph understated what the pattern admits (lens r3, r5, r6 and
    # r8 each caught one), so state it against the shipped regex and never against the
    # intent: a named bound that understates admission is a wrong claim with a disclaimer.
    #
    # The window's `{0,80}` is derived, not chosen by eye: the widest artifact→verb gap
    # among the real members is 60 ("test at <path>:1301 enshrines"), and 80 is that plus
    # headroom. n:16 pins it — a 117-char gap that an unbounded window would admit.
    #
    # Every round of review on this row removed something rather than adding a layer
    # (`pins the`, then `[\w-]*`, then `it|which`, then the whole noun arm) and the
    # new-class pile was 14 at every step. An overbuilt first draft worn down to one
    # regex — not the non-convergent hardening the step-6 arms-race rule forbids.
    #
    # `(?:[^.!?]|[.!?]\S)` keeps the window inside ONE sentence while still crossing a
    # file path. A sentence ends with a terminator followed by SPACE; a path's dot is
    # followed by non-space — so "test at tools/x.py:1301 enshrines" matches while "The
    # test passes. The spec codifies the rule" does not. All THREE terminators count:
    # an earlier draft listed only `.`, and "Did the test pass? The spec codifies the
    # older rule." false-matched (merge-gate witness lens r7 P2). 13 base-corpus rows pair
    # this class's own `test` token with `!` or `?`, so that was a live surface, not a
    # hypothetical. n:17/n:18 pin it.
    #
    # The `{0,80}` bounds REPETITIONS, not characters: a repetition is one char, or a
    # terminator plus a non-space, so the reachable character span is ≥ 80. The widest
    # artifact→verb gap among the real members is 60 chars, which is what 80 has headroom
    # over; n:16 pins the cap with a 117-char gap an unbounded window would admit.
    #
    # The false-match shapes this row refuses are enumerated ONCE, in
    # test_class_16_needs_both_a_blessing_verb_and_the_artifact_doing_it's own cases,
    # each with the comment naming the guard it pins. A prose list here was a second
    # authority over the same facts and drifted the moment a case was added — it claimed
    # to be exhaustive and was falsified twice in this arc (lens r2 and r7), which is a
    # copy that cannot be kept true rather than a wording that needs care
    # ([LAW:one-source-of-truth]).
    #
    # Overlap with class 4 is NOT the same defect: a vacuous witness proves nothing, one
    # of these proves the wrong thing.
    "16 witness codifies the divergence": (
        r"\btests?(?![a-z])(?:[^.!?]|[.!?]\S){0,80}(codif|enshrin|blesses)"
    ),
    "18 the code departs from a cleared contract": (
        r"contradict\w*\s+(?:the\s+)?(?:canonical\s+)?C-HE"
        r"|canonical C-HE-\d+[^.]{0,80}(?:still requires|says|table|statement)"
        r"|C-HE-\d+[^.]{0,60}declares the complete"
    ),
    # Measured at the 2,247-finding corpus: the pattern MATCHES 26 rows and this class
    # CLAIMS 23 (earlier classes take the other three — it is appended last), 14 of which
    # matched no other
    # class, and six of those fourteen are ONE defect recurring across rounds (a holder
    # gate admitting a terminal `merged` reservation against C-HE-03 §6). The cluster was
    # already NOTICED by class 2's own note, which refused a bare `contradict` because it
    # "sweeps that whole cluster in, the same wrong direction as `drift`" -- correct for
    # class 2, and the reason the rows sat unmatched: they needed their own home, not a
    # prose-drift class. Placed LAST so it can never steal a row an earlier class claims.
    #
    # Distinct from its two neighbours, which is why it is not an extension of either.
    # Class 12 is a contract phrase QUOTED into the diff with nothing discharging it --
    # the words are present and the line is missing. Class 16 is the WITNESS asserting the
    # departed behaviour, so review reads a covered change. This is the CODE half: the
    # implementation states something the cleared contract explicitly denies, whether or
    # not any prose quotes it and whether or not a test blesses it.
    #
    # EVERY alternative is bound to a `C-HE` reference, and that is the whole precision
    # story. `contradict` is safe HERE only because of that binding -- the bare verb is
    # what class 2 rejected. The second alternative carries its own claim shape
    # (`canonical C-HE-N ... still requires/says/table/statement`) in a bounded window, so
    # a passing cite of a contract number cannot satisfy it. The third was shipped
    # UNQUALIFIED for one round and was wrong: a bare `declares the complete` matches a
    # benign "the schema declares the complete set" with no contract in sight and no
    # negative polarity, silently emptying a row from the intake pile (codex r10 P2). It is
    # now bound to a contract reference within 60 characters like its siblings.
}


def matches(pattern: str | tuple[str, ...], text: str) -> bool:
    """True when `text` satisfies a class row: one pattern, or all of a tuple."""
    patterns = (pattern,) if isinstance(pattern, str) else pattern
    return all(re.search(p, text, re.I) for p in patterns)


def classify(text: str) -> list[str]:
    """Every class name whose row `text` satisfies, in table order; empty = unmatched.
    [LAW:effects-at-boundaries] pure over the text — the report and the review gate's
    intake both derive from this one function, so 'unmatched' means the same thing in
    the corpus report and at a sweep attestation ([LAW:one-source-of-truth])."""
    return [name for name, pat in CLASSES.items() if matches(pat, text)]


def finding_text(row: dict) -> str:
    """The text a finding row is classified on: evidence plus location (the location
    carries file-shaped vocabulary such as `justfile` or `test_` that some rows rely on)."""
    return (row.get("observed_evidence") or "") + " " + (row.get("location") or "")


def classify_stdin() -> int:
    """`classify` verb: JSON list of {"finding_id", "observed_evidence", "location"} on
    stdin → JSON object finding_id → [class names] on stdout. The review-loop gate
    calls this at template and attest time so an unmatched reviewer finding is named
    as one at the moment its author must disposition it (the skill's repair loop,
    made mechanical). Malformed input is a loud non-zero exit, never an empty map
    that would read as 'every finding unmatched' ([LAW:no-silent-failure])."""
    try:
        rows = json.load(sys.stdin)
        if not isinstance(rows, list):
            raise TypeError(f"expected a JSON list of findings, got {type(rows).__name__}")
        out = {str(r["finding_id"]): classify(finding_text(r)) for r in rows}
    except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as exc:
        print(f"refresh-classes classify: malformed input — {exc}", file=sys.stderr)
        return 2
    json.dump(out, sys.stdout)
    return 0


def main() -> int:
    if sys.argv[1:] == ["classify"]:
        return classify_stdin()
    if sys.argv[1:]:
        print("usage: refresh-classes.py [classify]  (no verb: corpus report)", file=sys.stderr)
        return 2
    log = Path(__file__).resolve().parents[3].parent / ".harness" / "merge-gate-log.jsonl"
    if not log.exists():
        # Fallback: resolve from the repo root when the skill is invoked from cwd.
        log = Path(".harness/merge-gate-log.jsonl")
    if not log.exists():
        print(f"refresh-classes: gate log not found at {log} — run from the repo root")
        return 0

    rows = []
    malformed = 0
    for lineno, line in enumerate(log.read_text().splitlines(), start=1):
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            # A damaged row silently dropped would understate counts while the
            # output still reads authoritative — report it and mark the result
            # incomplete below (no-silent-failure; codex round 2 on this PR).
            malformed += 1
            print(f"refresh-classes: WARNING malformed JSONL at line {lineno} — skipped")
            continue
        # Real findings only, by the log's own discriminator: record_kind. A severity
        # filter is NOT a finding filter — it drops warn-severity findings while
        # admitting hard-severity infrastructure rows, skewing the counts this file
        # claims to derive (codex round 1 on the skills PR measured the mismatch).
        if r.get("observed_evidence") and r.get("record_kind", "finding") == "finding":
            rows.append(r)

    counts = dict.fromkeys(CLASSES, 0)
    unmatched = []
    for r in rows:
        hits = classify(finding_text(r))
        for name in hits:
            counts[name] += 1
        if not hits:
            unmatched.append(r)

    status = f" (INCOMPLETE — {malformed} malformed row(s) skipped)" if malformed else ""
    print(f"refresh-classes: {len(rows)} findings in {log}{status}")
    print("\nPer-class counts (multi-match rows count in every class they touch):")
    for name, n in counts.items():
        print(f"  {n:5}  {name}")

    print(f"\nUnmatched findings (new-class candidates): {len(unmatched)}")
    for r in unmatched[-10:]:
        ev = (r.get("observed_evidence") or "").replace("\n", " ")[:150]
        print(f"  {r.get('ts', '')[:10]} {r.get('severity', '?'):3} {r.get('location', '')[:50]}")
        print(f"      {ev}")
    if unmatched:
        print(
            "\nEach unmatched finding is a candidate: either extend an existing class's"
            " pattern (here AND in SKILL.md) or add a new class in both places."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
