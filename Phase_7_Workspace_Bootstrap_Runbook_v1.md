# Phase 7 Workspace Bootstrap Runbook — v1

*Step-by-step runbook for setting up and initializing the H_T multi-LLM agent harness build in Claude Code CLI. Designed for a non-technical operator. All build infrastructure artifacts are LLM-assisted with HITL (human-in-the-loop) review.*

---

## §1 Overview

### §1.1 What this runbook accomplishes

This runbook walks you from "you have nothing installed" to "Phase 7 Session 1 is open and ready to begin H_T atomic unit landings."

You will:

1.1.1 Install Claude Code CLI on your computer (one-time)
1.1.2 Install uv, the Python toolchain (one-time)
1.1.3 Create a new workspace folder
1.1.4 Place 11 bootstrap artifacts in that folder
1.1.5 Open Claude Code CLI inside the workspace
1.1.6 Direct Claude Code to author all build infrastructure (with you reviewing each piece)
1.1.7 Open Phase 7 Session 1

### §1.2 What you need before starting

| # | Requirement | How to check |
|---|---|---|
| 1 | A Mac (macOS), Linux, or Windows computer | (you have one) |
| 2 | An active Claude subscription (Pro, Max, Team, or Enterprise) **OR** a Claude Console (API) account with credits | Log into claude.com or console.anthropic.com to verify |
| 3 | Internet connection | (you have one) |
| 4 | The 11 bootstrap artifacts filed at `/mnt/user-data/outputs/` in Claude.ai (already filed during Phase 6.5 Sessions 6 + 7) | Confirm by viewing the close handoff from Phase 6.5 Session 7 |
| 5 | About 30–60 minutes of focused time | — |

**Important:** You do NOT need to know Python, JavaScript, command-line tools, git, or any other programming concept. Claude Code does all the technical work. You read the proposals, click approve, and the runbook tells you what to do at each step.

### §1.3 Key concept — HITL approval pattern

"HITL" means human-in-the-loop. Throughout the bootstrap session, Claude Code will:

1.3.1 Propose what it wants to do (write a file, run a command, etc.)
1.3.2 Show you the exact content or command before doing it
1.3.3 Wait for your approval

Your job is to:

1.3.4 Read what Claude proposes
1.3.5 Confirm it matches the runbook's expectations (each step below tells you what to check for)
1.3.6 Type your approval (typically pressing `y` and then Enter), OR ask Claude to revise if something looks wrong

**Default behavior in Claude Code CLI: it asks before every file write and every command execution.** This is the protective mode. Keep this default.

### §1.4 Runbook structure

| Part | Section | What happens |
|---|---|---|
| Part 1 | §2 | One-time machine setup (install Claude Code, uv, verify git) |
| Part 2 | §3 | Create workspace folder; place 11 bootstrap artifacts |
| Part 3 | §4 | LLM-assisted bootstrap session (author build infrastructure with HITL) |
| Part 4 | §5 | Open Phase 7 Session 1 |
| Reference | §6 | Verification checklist (use after each Part to confirm readiness for the next) |
| Reference | §7 | Troubleshooting common issues |
| Reference | §8 | Glossary |

If you have completed Parts 1, 2, 3 in a prior attempt and only need to reopen Phase 7 Session 1, skip to Part 4.

---

## §2 Part 1 — One-time machine setup

This Part is one-time. After completing it once, you never need to redo it (except occasional updates that the tools handle themselves).

### §2.1 Open a terminal

A "terminal" is a text-based window where you type commands. You will use it for the install steps.

| Operating system | How to open terminal |
|---|---|
| **macOS** | Press `Command + Space`, type `Terminal`, press Enter |
| **Linux** | Press `Ctrl + Alt + T` (on most distributions) |
| **Windows** | Press `Windows key`, type `PowerShell`, press Enter — choose "Windows PowerShell" |

The terminal opens a window showing some text and a blinking cursor. This is where you'll type commands.

**Tip:** When this runbook shows a command like `claude --version`, you type those exact characters into the terminal window and press Enter. The terminal then shows the result below your command.

### §2.2 Install Claude Code CLI

This installs the tool that lets you talk to Claude on your computer from the terminal.

#### §2.2.1 Run the installer

| Operating system | Command to type |
|---|---|
| **macOS / Linux** | `curl -fsSL https://claude.ai/install.sh \| bash` |
| **Windows (PowerShell)** | `irm https://claude.ai/install.ps1 \| iex` |

Type the command exactly. Press Enter. The terminal will show progress messages for 30 seconds to 2 minutes.

#### §2.2.2 Restart your terminal

Close the terminal window completely. Open a fresh terminal window per §2.1. This refresh is required so the new `claude` command is recognized.

#### §2.2.3 Verify Claude Code installed

Type this command into the fresh terminal:

```
claude --version
```

**Expected result:** A version number appears (e.g., `2.x.x` or similar). If you see a version, installation succeeded.

**If you see "command not found":** See §7.1 troubleshooting.

### §2.3 Install uv (Python toolchain)

uv is the Python package manager that Claude Code will use to set up the harness build.

#### §2.3.1 Run the uv installer

| Operating system | Command to type |
|---|---|
| **macOS / Linux** | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Windows (PowerShell)** | `irm https://astral.sh/uv/install.ps1 \| iex` |

Press Enter. Wait for completion (~30 seconds).

#### §2.3.2 Restart your terminal

Close and reopen the terminal per §2.2.2.

#### §2.3.3 Verify uv installed

Type:

```
uv --version
```

**Expected result:** A version number appears (e.g., `0.x.x`).

**If you see "command not found":** See §7.2 troubleshooting.

### §2.4 Verify git is installed

Git is usually pre-installed on Macs and Linux machines. Type:

```
git --version
```

**Expected result:** A version number (e.g., `git version 2.x.x`).

**If git is not installed:**

| Operating system | What to do |
|---|---|
| **macOS** | macOS may prompt to install Command Line Tools; click "Install" and wait ~5 minutes |
| **Linux (Debian/Ubuntu)** | Type `sudo apt install git` and press Enter |
| **Linux (Fedora)** | Type `sudo dnf install git` and press Enter |
| **Windows** | Download from https://git-scm.com/downloads/win and install with defaults |

Re-run `git --version` after install.

### §2.5 First-time Claude Code login

Claude Code needs to know which Claude account you're using.

#### §2.5.1 Start Claude Code (any directory will work for this step)

Type:

```
claude
```

Press Enter. Claude Code will launch and prompt you to log in.

#### §2.5.2 Complete browser login

Claude Code opens your web browser to the Anthropic login page. Sign in with the same account you use for claude.ai. Click "Authorize" when prompted.

The browser will display a success message. Return to your terminal.

#### §2.5.3 Confirm you're logged in

The terminal shows a Claude Code welcome screen with your account info.

#### §2.5.4 Exit Claude Code

Type:

```
/exit
```

Press Enter. You return to the regular terminal prompt.

**Part 1 complete.** Verify against §6.1 before proceeding to Part 2.

---

## §3 Part 2 — Create the workspace and place artifacts

This Part creates the folder where your harness build will live, and places the 11 bootstrap artifacts inside it in the correct subdirectory structure.

### §3.1 Decide where the workspace lives

You will create a folder named `harness-build` (or any name you prefer — the runbook uses `harness-build`).

Common locations:

| Operating system | Recommended location |
|---|---|
| **macOS** | `/Users/<your-username>/harness-build` |
| **Linux** | `/home/<your-username>/harness-build` |
| **Windows** | `C:\Users\<your-username>\harness-build` |

Replace `<your-username>` with your actual username. If you don't know it, just use your home folder (the folder that opens when you launch a new Finder/Explorer window).

### §3.2 Create the workspace folder

You can create the folder either through the file manager (Finder/Explorer) or through the terminal.

#### §3.2.1 Via terminal (recommended — faster)

Open a fresh terminal. Type:

```
cd ~
mkdir harness-build
cd harness-build
pwd
```

**Expected result of `pwd`:** Shows the full path (e.g., `/Users/yourname/harness-build`). Note this path — you'll need it later.

#### §3.2.2 Via file manager (alternative)

| Operating system | Action |
|---|---|
| **macOS** | Open Finder → Go to your home folder → Right-click → New Folder → name it `harness-build` |
| **Linux** | Open file manager → home folder → Create folder named `harness-build` |
| **Windows** | Open Explorer → This PC → C:\Users\<yourname> → Right-click → New → Folder → name it `harness-build` |

### §3.3 Download the 11 bootstrap artifacts from Claude.ai

The 11 artifacts were filed at `/mnt/user-data/outputs/` during Phase 6.5 Sessions 6 + 7. You need to download them to your computer.

#### §3.3.1 The artifact inventory

| # | Artifact filename | Source (Claude.ai chat) |
|---|---|---|
| 1 | `CLAUDE.md` (the root one) | Phase 6.5 Session 6 outputs |
| 2 | `harness-is_CLAUDE.md` | Phase 6.5 Session 6 outputs (or `CLAUDE.md` in `harness-is` folder reference) |
| 3 | `harness-as_CLAUDE.md` | Phase 6.5 Session 6 outputs |
| 4 | `harness-cp_CLAUDE.md` | Phase 6.5 Session 6 outputs |
| 5 | `harness-od_CLAUDE.md` | Phase 6.5 Session 6 outputs |
| 6 | `Sub_Agent_Boundary_Specification_v1.md` | Phase 6.5 Session 6 outputs |
| 7 | `phase-7-implementation_SKILL.md` | Phase 6.5 Session 6 outputs |
| 8 | `phase-7-cross-axis-composition_SKILL.md` | Phase 6.5 Session 6 outputs |
| 9 | `phase-7-substitution-retirement_SKILL.md` | Phase 6.5 Session 6 outputs |
| 10 | `phase-7-back-flow-routing_SKILL.md` | Phase 6.5 Session 6 outputs |
| 11 | `Phase_7_Session_1_Entry_Directive_v1.md` | Phase 6.5 Session 7 outputs |

#### §3.3.2 How to download from Claude.ai

In the Claude.ai conversation where these were filed:

3.3.2.1 Scroll to where each artifact appears in the conversation
3.3.2.2 Click on the artifact link (it appears as a file attachment in the chat UI)
3.3.2.3 Click "Download" in the file viewer
3.3.2.4 The file saves to your computer's Downloads folder
3.3.2.5 Repeat for all 11 artifacts

Notes for handling filename collisions:

| Original filename in project | Suggested local filename when downloading |
|---|---|
| `CLAUDE.md` (root) | `root_CLAUDE.md` |
| 4 per-axis `CLAUDE.md` files | `harness-is_CLAUDE.md` / `harness-as_CLAUDE.md` / `harness-cp_CLAUDE.md` / `harness-od_CLAUDE.md` |
| 4 `SKILL.md` files | `phase-7-implementation_SKILL.md` / `phase-7-cross-axis-composition_SKILL.md` / `phase-7-substitution-retirement_SKILL.md` / `phase-7-back-flow-routing_SKILL.md` |

(These suffixed filenames are temporary holding names. In §3.5 you will rename them and move them to their proper subdirectories.)

### §3.4 Create the subdirectory structure

The 11 artifacts go into specific subdirectories. You will create those subdirectories first.

#### §3.4.1 Via terminal (recommended)

In your terminal (which should still be inside `harness-build` from §3.2.1, or `cd ~/harness-build` first):

```
mkdir harness-is
mkdir harness-as
mkdir harness-cp
mkdir harness-od
mkdir -p .claude/skills/phase-7-implementation
mkdir -p .claude/skills/phase-7-cross-axis-composition
mkdir -p .claude/skills/phase-7-substitution-retirement
mkdir -p .claude/skills/phase-7-back-flow-routing
```

Type each line and press Enter (or paste them all at once — most terminals accept multi-line paste).

**Note on `.claude`:** Folders starting with a dot are "hidden" on macOS/Linux. They exist normally but file managers may hide them unless you press `Cmd+Shift+.` (Mac Finder) or enable "Show hidden files" (Linux). This is normal.

#### §3.4.2 Via file manager (alternative)

Inside `harness-build`, create these folders (and nested folders) manually:

```
harness-build/
├── harness-is/
├── harness-as/
├── harness-cp/
├── harness-od/
└── .claude/
    └── skills/
        ├── phase-7-implementation/
        ├── phase-7-cross-axis-composition/
        ├── phase-7-substitution-retirement/
        └── phase-7-back-flow-routing/
```

On Windows, you cannot create a folder starting with a dot via Explorer right-click. Use the terminal method (§3.4.1) for `.claude` and subfolders.

### §3.5 Place each artifact in its target location

Move each downloaded artifact from your Downloads folder into its correct subdirectory inside `harness-build`. **Each file must be renamed to its canonical name at the target location.**

| # | Downloaded filename (from §3.3.2) | Target path inside `harness-build/` | Final filename at target |
|---|---|---|---|
| 1 | `root_CLAUDE.md` | (workspace root) | `CLAUDE.md` |
| 2 | `harness-is_CLAUDE.md` | `harness-is/` | `CLAUDE.md` |
| 3 | `harness-as_CLAUDE.md` | `harness-as/` | `CLAUDE.md` |
| 4 | `harness-cp_CLAUDE.md` | `harness-cp/` | `CLAUDE.md` |
| 5 | `harness-od_CLAUDE.md` | `harness-od/` | `CLAUDE.md` |
| 6 | `Sub_Agent_Boundary_Specification_v1.md` | (workspace root) | `Sub_Agent_Boundary_Specification_v1.md` (unchanged) |
| 7 | `phase-7-implementation_SKILL.md` | `.claude/skills/phase-7-implementation/` | `SKILL.md` |
| 8 | `phase-7-cross-axis-composition_SKILL.md` | `.claude/skills/phase-7-cross-axis-composition/` | `SKILL.md` |
| 9 | `phase-7-substitution-retirement_SKILL.md` | `.claude/skills/phase-7-substitution-retirement/` | `SKILL.md` |
| 10 | `phase-7-back-flow-routing_SKILL.md` | `.claude/skills/phase-7-back-flow-routing/` | `SKILL.md` |
| 11 | `Phase_7_Session_1_Entry_Directive_v1.md` | (workspace root) | `Phase_7_Session_1_Entry_Directive_v1.md` (unchanged) |

Use either drag-and-drop in your file manager, or use the terminal `mv` command. For example:

```
cd ~/harness-build
mv ~/Downloads/root_CLAUDE.md ./CLAUDE.md
mv ~/Downloads/harness-is_CLAUDE.md ./harness-is/CLAUDE.md
mv ~/Downloads/Sub_Agent_Boundary_Specification_v1.md ./Sub_Agent_Boundary_Specification_v1.md
mv ~/Downloads/phase-7-implementation_SKILL.md ./.claude/skills/phase-7-implementation/SKILL.md
```

(and so on for all 11)

### §3.6 Verify the file layout

#### §3.6.1 Via terminal

In your terminal, inside `harness-build`, type:

```
find . -type f | sort
```

**Expected result:** Exactly these 11 lines (paths begin with `./`):

```
./.claude/skills/phase-7-back-flow-routing/SKILL.md
./.claude/skills/phase-7-cross-axis-composition/SKILL.md
./.claude/skills/phase-7-implementation/SKILL.md
./.claude/skills/phase-7-substitution-retirement/SKILL.md
./CLAUDE.md
./harness-as/CLAUDE.md
./harness-cp/CLAUDE.md
./harness-is/CLAUDE.md
./harness-od/CLAUDE.md
./Phase_7_Session_1_Entry_Directive_v1.md
./Sub_Agent_Boundary_Specification_v1.md
```

**If you see fewer or different lines:** Check that each artifact is at its target path with its target filename per §3.5. Common mistakes: forgot to rename the file; placed in wrong subdirectory; one file still in Downloads folder.

**Part 2 complete.** Verify against §6.2 before proceeding to Part 3.

---

## §4 Part 3 — Bootstrap session (LLM-assisted setup)

In this Part, you open Claude Code in your workspace and direct it to author all the build infrastructure files. Claude Code reads the bootstrap artifacts you placed in §3, understands the workspace context, and proposes each new file's content. You approve each one.

### §4.1 Open Claude Code in the workspace

From your terminal:

```
cd ~/harness-build
claude
```

Press Enter.

**Expected result:** Claude Code launches and shows a welcome screen. The Claude Code interface appears in your terminal window. You can now type messages to Claude.

**Tip:** When you type a message and press Enter, Claude responds. When Claude wants to write a file or run a command, it pauses and asks for your approval. You respond with `y` (yes) or `n` (no), or you can type a longer message to ask Claude to revise.

### §4.2 The HITL approval pattern — what you'll see

Throughout this Part, Claude Code will repeatedly:

4.2.1 Show you a proposal (file content, command to run)
4.2.2 Ask "Allow this?" or similar
4.2.3 Wait for your response

Your response options at each gate:

| You want to | Type |
|---|---|
| Approve once (this single action) | `y` or `1` |
| Approve forever (don't ask again for this tool) | `2` (or as Claude Code prompts) — **do NOT use this during bootstrap** |
| Reject | `n` or `3` |
| Ask Claude to revise | Type your revision request as a full message |

**Important:** Always use "approve once" (`y`) during this bootstrap. Do NOT enable any "approve all" or "auto-approve" mode. Each individual approval is your safety check.

### §4.3 Orientation — first prompt

This first prompt tells Claude Code to read everything in the workspace and understand what it's looking at.

**Copy this prompt exactly and paste it into Claude Code, then press Enter:**

```
Please do the following, in order, without modifying any files:

1. Read every file in this workspace recursively, including subdirectories
   and hidden directories (.claude/).
2. After reading, summarize for me:
   (a) What workspace this is (1-2 sentences from your reading)
   (b) Which design phase this workspace serves (cite the relevant
       file and section)
   (c) The current sub-phase entry-gate status per Phase_7_Meta_Architecture
       §10.1.4 (you'll find this referenced in the Entry Directive)
   (d) Which build infrastructure files are MISSING that need to be
       authored before Phase 7 Session 1 can begin
   (e) The exact list of file paths you propose to author, in the order
       you propose to author them

Do not write any files yet. Just propose.
```

Press Enter.

**What Claude will do:** Claude reads all 11 files. This may take 30–90 seconds. You'll see Claude requesting permission to read files — approve each read (`y`).

**Expected result:** Claude responds with a structured summary that:

| Field | Expected content |
|---|---|
| (a) Workspace identity | "H_T multi-LLM agent harness build under H_E (Claude Code CLI)" or equivalent |
| (b) Design phase | References to ADD v1.3, PRD v1.1, per-axis plans v2.x, CXA v2.1, and the design-phase workspace |
| (c) Entry-gate status | Cites Meta-Architecture §10.1.4 7-criteria; notes criterion 2 ("workspace operational") not yet satisfied because build infrastructure missing |
| (d) Missing files | Should list: root `pyproject.toml`; 6 per-axis `pyproject.toml`; 6 per-axis `src/` and `tests/` skeletons; `.gitignore`; `.gitattributes`; `.python-version`; `README.md`; `.claude/mcp.json`; `.harness/` runtime directory; `uv.lock` (generated); git repository (not yet initialized) |
| (e) Authoring order | An ordered list of paths |

**Your check:** Does Claude's response cite the actual design-phase artifacts (ADD v1.3, PRD v1.1, etc.)? Does it identify approximately the items listed in (d) above? If yes, proceed to §4.4. If Claude's response is vague or wrong (e.g., does not cite specific artifacts), see §7.3.

### §4.4 Author build infrastructure files (with HITL)

Each subsection below authors one build infrastructure component. Each subsection has:

| Element | Purpose |
|---|---|
| **Prompt** | Copy-paste this prompt to Claude Code |
| **What Claude proposes** | What you'll see in Claude's response |
| **Your verification** | Quick checks to confirm Claude's proposal is canonical |
| **Approval** | When everything looks right, approve with `y` |

#### §4.4.1 Workspace root `pyproject.toml` (uv workspace declaration)

**Prompt:**

```
Author the workspace root pyproject.toml file at this workspace root.

Authority sources you must consult (read these files):
- ./CLAUDE.md §3.1 "Committed stack"
- ./CLAUDE.md §3.3 "Repo layout"
- The Target_Stack_Commitment_v1 reference cited in ./CLAUDE.md

Required content per those sources:
- [tool.uv.workspace] declaring 6 members: harness-core, harness-is,
  harness-as, harness-cp, harness-od, harness-cxa
- requires-python = ">=3.12"
- [tool.pyright] in strict mode
- [tool.ruff] configuration
- [tool.pytest.ini_options]
- Root dev dependencies (dev group): pytest, pytest-asyncio, pyright,
  ruff, plus opentelemetry-api, opentelemetry-sdk, opentelemetry-exporter-otlp,
  opentelemetry-instrumentation-genai (selective contrib)
- MCP host: include modelcontextprotocol Python SDK (FastMCP) for shared use
- Multi-LLM SDKs: anthropic, openai, ollama
- Secrets: python-keyring
- Framework-pull discipline: do NOT include tenacity, pybreaker, circuitbreaker,
  langgraph, crewai, langchain, llamaindex, temporal, prefect, or LiteLLM

Propose the exact pyproject.toml content. Do not write the file yet.
Show it to me first.
```

**What Claude proposes:** A complete `pyproject.toml` file content shown as a code block.

**Your verification (quick checks):**

| Check | Pass criterion |
|---|---|
| Workspace members listed | Should see all 6: `harness-core`, `harness-is`, `harness-as`, `harness-cp`, `harness-od`, `harness-cxa` |
| Python version | `requires-python = ">=3.12"` |
| Forbidden libraries | Search the proposed content for `tenacity`, `pybreaker`, `langgraph`, `crewai`, `langchain`, `llamaindex`, `temporal`, `prefect`, `litellm`. **None should appear.** If you see any, ask Claude to revise. |
| Allowed libraries | `anthropic`, `openai`, `ollama`, `opentelemetry-*`, `modelcontextprotocol` or `fastmcp`, `python-keyring`, `pydantic` should appear |
| Tools | `pyright`, `ruff`, `pytest`, `pytest-asyncio` should appear |

**If anything looks wrong:** Type a message describing what's wrong. Example: "I see `tenacity` in the dependencies — that violates framework-pull discipline per Plan_Executability_Audit_v1. Please remove it and any other forbidden libraries." Claude will revise.

**When it looks correct, approve:** Tell Claude:

```
Approved. Write the file to ./pyproject.toml
```

Claude will ask permission to write the file. Approve with `y`.

#### §4.4.2 Per-axis `pyproject.toml` × 6

**Prompt:**

```
Now author the 6 per-axis pyproject.toml files (one for each workspace member):

1. ./harness-core/pyproject.toml — shared types + utilities; depends only
   on pydantic v2
2. ./harness-is/pyproject.toml — IS axis; depends on harness-core
3. ./harness-as/pyproject.toml — AS axis; depends on harness-core,
   FastMCP, opentelemetry-*
4. ./harness-cp/pyproject.toml — CP axis; depends on harness-core,
   anthropic, openai, ollama SDKs
5. ./harness-od/pyproject.toml — OD axis; depends on harness-core,
   opentelemetry-* libraries
6. ./harness-cxa/pyproject.toml — CXA composition; depends on all 5 above
   as workspace dependencies

Per workspace root ./CLAUDE.md §3.3 repo layout, each is a uv workspace
member declaring its package name as harness-{is,as,cp,od,cxa,core} and
its src/ layout. Test runner pytest-asyncio.

Propose all 6 files. Show me content for each. Do not write until I approve.
```

**What Claude proposes:** 6 separate `pyproject.toml` proposals, one per axis.

**Your verification:**

| Check | Pass criterion |
|---|---|
| 6 files proposed | Count them — must be exactly 6 |
| Each declares correct package name | `harness-core`, `harness-is`, `harness-as`, `harness-cp`, `harness-od`, `harness-cxa` |
| Dependencies match the prompt | Spot-check 1–2: e.g., `harness-cp/pyproject.toml` should list `anthropic`, `openai`, `ollama` |
| No forbidden libraries | Same check as §4.4.1 |

**Approve:**

```
Approved. Write all 6 files to their target paths.
```

Claude will ask permission for each file write. Approve each with `y`. (6 approvals total.)

#### §4.4.3 Per-axis source and test skeletons

**Prompt:**

```
Now create the empty source-package skeletons for all 6 axes:

For each of harness-core, harness-is, harness-as, harness-cp, harness-od,
harness-cxa, create:
- ./<axis>/src/harness_<axis>/__init__.py  (empty file, 0 bytes)
- ./<axis>/tests/__init__.py  (empty file, 0 bytes)

Replace <axis> with the axis directory name (using underscores instead of
hyphens for the Python module name — e.g., harness_core, harness_is).

Do NOT author any Python implementation code. These are empty skeletons.
Phase 7 atomic unit landings will populate them.

Propose the file list. Show me the 12 file paths you'll create.
```

**What Claude proposes:** A list of 12 file paths (6 axes × 2 files each).

**Your verification:**

| Check | Pass criterion |
|---|---|
| 12 paths total | Exactly 12: 6 axes × 2 files (__init__.py × 2 per axis) |
| Underscores in module names | `harness_core`, `harness_is`, `harness_as`, `harness_cp`, `harness_od`, `harness_cxa` (NOT hyphens) |
| Both `src/` and `tests/` | Each axis has both |
| Files are empty | Claude should confirm 0-byte files; no code |

**Approve:**

```
Approved. Create all 12 empty files.
```

Approve each file creation with `y`.

#### §4.4.4 `.gitignore`

**Prompt:**

```
Author the .gitignore file at the workspace root.

It must exclude:
- Runtime paths: .harness/state.jsonl, .harness/observability.db,
  .harness/*.db, .harness/*.db-journal
- Python build artifacts: __pycache__/, *.pyc, *.pyo, *.egg-info/,
  dist/, build/
- Tool caches: .pytest_cache/, .ruff_cache/, .pyright/, .mypy_cache/
- Virtual environments: .venv/, venv/, env/
- IDE files: .vscode/, .idea/, *.swp, .DS_Store
- Coverage: .coverage, htmlcov/, coverage.xml

It must NOT exclude:
- CLAUDE.md files (at root and per-axis)
- SKILL.md files (in .claude/skills/)
- pyproject.toml files
- Source code under src/
- Test code under tests/
- Phase 7 Session 1 Entry Directive

Reason for inclusion of .harness/ exclusions: Meta-Architecture §10.1.3
declares .harness/state.jsonl is created at runtime by Bash append-write;
this is runtime mutable state that must not be committed.

Propose .gitignore content. Show me before writing.
```

**What Claude proposes:** A complete `.gitignore` file content.

**Your verification:**

| Check | Pass criterion |
|---|---|
| `.harness/state.jsonl` present | Yes — runtime state must be excluded |
| `__pycache__/` present | Yes — Python convention |
| `.venv/`, `venv/`, `env/` present | Yes — virtual environments |
| `*.md` NOT present | `.md` files (CLAUDE.md, Entry Directive) must NOT be excluded |
| `pyproject.toml` NOT present | Build config must NOT be excluded |
| `src/` NOT excluded | Source code must NOT be excluded |

**Approve:**

```
Approved. Write to ./.gitignore
```

#### §4.4.5 `.gitattributes`

**Prompt:**

```
Author .gitattributes at the workspace root.

Required: Force LF line endings (Unix-style) for these file types:
- *.py
- *.jsonl
- *.json
- *.md
- *.toml
- *.yaml / *.yml

Rationale: Hash-chain integrity per IS plan v2.2 U-IS-08/09/10 requires
deterministic byte-level state ledger writes. CRLF (Windows) vs LF (Unix)
line ending differences break SHA-256 chain verification.

Propose .gitattributes content. Show me before writing.
```

**Verification:** Should see `text eol=lf` declarations for each file type listed.

**Approve:**

```
Approved. Write to ./.gitattributes
```

#### §4.4.6 `.python-version`

**Prompt:**

```
Author .python-version at the workspace root. Content: exactly the string
"3.12" (or "3.13" if you recommend a newer current LTS) on a single line.

Per Target_Stack_Commitment_v1 §5.1: Python 3.12+.

Show me the proposed version, then write.
```

**Verification:** Single line, value is `3.12` or higher (`3.13`, `3.14`).

**Approve:**

```
Approved. Write to ./.python-version
```

#### §4.4.7 `README.md`

**Prompt:**

```
Author a minimal README.md at the workspace root.

Required sections:
1. Project identity: "H_T — multi-LLM agent harness target build"
2. Execution surface: "H_E = Claude Code CLI; bounded substitutions
   during Phase 7 sub-phase 7a"
3. Workspace pointer: "See ./CLAUDE.md for workspace-level Claude Code
   guidance; see ./Phase_7_Session_1_Entry_Directive_v1.md for Phase 7
   Session 1 entry context"
4. Design-phase workspace: "Canonical design substrate (ADRs, ADD v1.3,
   PRD v1.1, per-axis specs v1.x, per-axis plans v2.x, CXA v2.1, Workflow
   v1.8, Meta-Architecture v1) resides at the separate design-phase
   project workspace; this workspace reads via cross-workspace reference
   per arc manifest §6"
5. Bootstrap commands (operator-facing): how to open a Phase 7 session
   in this workspace (cd to workspace; run `claude`; load the Entry
   Directive)
6. Status: "Workspace operational under DP-4 separate-workspace
   discipline; Phase 7 sub-phase 7a entry authorized per the Entry
   Directive §3"

Keep it brief. Show me the content before writing.
```

**Verification:** Mentions H_T, H_E, points to CLAUDE.md and Entry Directive, mentions design-phase workspace.

**Approve:**

```
Approved. Write to ./README.md
```

#### §4.4.8 `.claude/mcp.json` (minimal scaffold)

**Prompt:**

```
Author a minimal .claude/mcp.json at .claude/mcp.json (the .claude/
directory already exists from §3.4).

This is the FastMCP server registration file per Meta-Architecture
§10.1.3 row 4: "FastMCP at .claude/mcp.json local scope".

For now, create a minimal scaffold with the JSON schema declared but no
servers registered yet. A FastMCP server will be added at sub-phase 7a
when the AS-axis tool-contract units land (U-AS-02 etc.).

Propose a minimal valid mcp.json content. Note: if you are uncertain
about the current Claude Code MCP server schema format, declare it as
SPECULATIVE in your proposal and suggest I verify against Claude Code
documentation at code.claude.com/docs.

Show me before writing.
```

**Verification:** Valid JSON; "mcpServers" key (or equivalent) exists; the `mcpServers` object may be empty `{}` or contain a stub entry. Claude may flag this as [SPECULATIVE] — that's expected because the FastMCP schema evolves.

**Approve:**

```
Approved. Write to ./.claude/mcp.json
```

**Note:** This file is intentionally minimal at bootstrap. Phase 7 sub-phase 7a will populate it with actual MCP server registrations as units land.

#### §4.4.9 `.harness/` runtime directory

**Prompt:**

```
Create the .harness/ directory at the workspace root. It should be
empty. This directory is the runtime path for state ledger writes,
observability sqlite, and OTLP Collector config per Meta-Architecture
§10.1.3 rows 2 + 5 + 6.

The directory must exist before the first state ledger write attempts
to append to .harness/state.jsonl.

Create the directory only — no files inside it.
```

**Verification:** Empty directory `.harness/` created at workspace root.

**Approve creation with `y`.**

### §4.5 Generate the uv lockfile

The lockfile records exact versions of all dependencies. This makes the build reproducible.

**Prompt:**

```
Now run `uv sync` from the workspace root to:
1. Resolve all dependencies declared in root pyproject.toml and the 6
   per-axis pyproject.toml files
2. Generate uv.lock at the workspace root
3. Create a virtual environment at .venv/

This may take 1-5 minutes depending on network speed.

Run the command. Show me the output.
```

**What Claude proposes:** A request to run `uv sync` via the Bash tool.

**Approve with `y`.**

**What you'll see:** Claude runs the command. Output streams to terminal showing dependency resolution, downloads, and install progress.

**Expected result:** Command completes successfully. `uv.lock` file appears at workspace root; `.venv/` directory is created.

**If errors appear:** See §7.4.

### §4.6 Initialize git repository

**Prompt:**

```
Initialize a git repository at the workspace root:
1. Run `git init` to create the repository
2. Configure the user.name and user.email for git commits — but FIRST
   ask me for these values; do not assume defaults
3. Verify .gitignore is honored by running `git status` and showing me
   the output

Use conventional commits per ./CLAUDE.md §3.1 row "Git posture".
```

**What you'll see:** Claude asks you for your name and email for git commit attribution. Provide them — e.g., "My name is `Jane Doe` and email is `jane@example.com`".

Claude will then run `git init` (approve with `y`) and configure git (approve each command).

**Expected `git status` output:** Untracked files list showing CLAUDE.md, the per-axis directories, pyproject.toml files, README.md, etc. **`.harness/`** should NOT appear in untracked files (.gitignore excludes it). **`.venv/`** should NOT appear either.

**Your check:** Does `git status` list the 11 bootstrap files + the new build infrastructure files (pyproject.toml × 7, gitignore, etc.) as untracked? If yes, proceed.

### §4.7 First commit

**Prompt:**

```
Make the first git commit:
1. Stage all currently untracked files (git add .)
2. Commit with the message: "chore: bootstrap H_T workspace from Phase
   6.5 substrate

   - 11 bootstrap artifacts transferred from Phase 6.5 Sessions 6 + 7
   - Build infrastructure authored per workspace root CLAUDE.md §3
   - uv workspace operational with 6 members
   - Phase 7 sub-phase 7a entry-gate criterion 2 (workspace operational)
     satisfied"

Show me what's about to be committed (git status) before running git commit.
```

**Your check:** Confirm the staged file list looks complete (~30+ files). Approve.

**Expected result:** Commit succeeds. `git log` shows one commit.

### §4.8 Verify workspace operational

**Prompt:**

```
Verify the workspace is now operational per Phase_7_Meta_Architecture
§10.1.4 entry-gate criterion 2.

Run these checks and report PASS/FAIL for each:

1. uv sync exit code (workspace dependencies resolvable): re-run `uv sync`
   and check exit 0
2. pyright self-check: run `uv run pyright --version` (just version, not
   actual type-check)
3. ruff self-check: run `uv run ruff --version`
4. pytest self-check: run `uv run pytest --version`
5. git repository: run `git log --oneline` and confirm at least 1 commit
6. .harness/ directory exists: run `ls -la .harness/`
7. .claude/mcp.json valid JSON: run `cat .claude/mcp.json | python -m
   json.tool`
8. All 11 bootstrap artifacts present at canonical paths: run a find
   command and verify count

Report PASS/FAIL per check.
```

**What you'll see:** Claude runs each check (approve each with `y`) and reports the result.

**Expected result:** All 8 checks PASS.

**If any check FAILS:** Ask Claude to diagnose. Common issues at this step are usually fixable in a few turns (e.g., a typo in pyproject.toml — Claude revises and re-runs).

**Part 3 complete.** Verify against §6.3 before proceeding to Part 4.

### §4.9 Close the bootstrap session

You can either keep this session open (and skip to §5.2 directly via `/clear`) OR close and reopen. Closing creates a clean separation between bootstrap and Phase 7 Session 1.

To close:

```
/exit
```

Press Enter. The Claude Code session ends and you return to the regular terminal prompt.

---

## §5 Part 4 — Open Phase 7 Session 1

### §5.1 Open a fresh Claude Code session

From your terminal:

```
cd ~/harness-build
claude
```

Press Enter. Claude Code launches fresh.

### §5.2 Load the Phase 7 Session 1 Entry Directive

**Copy this prompt and paste it into Claude Code:**

```
I am opening Phase 7 Session 1 at this Claude Code CLI workspace.

Please do the following, in order:

1. Read the workspace root ./CLAUDE.md in full.

2. Read ./Phase_7_Session_1_Entry_Directive_v1.md in full.

3. Read ./Sub_Agent_Boundary_Specification_v1.md in full.

4. Per the Entry Directive §3 (entry-gate verification for sub-phase 7a),
   verify all 7 criteria can be confirmed. Report PASS/FAIL per criterion.

5. Per the Entry Directive §4.5 (7a first action sequence), state what
   the immediate next action is for Phase 7 Session 1.

6. Wait for my authorization before proceeding to any unit landing or
   substrate scaffolding instantiation.

This session is operating under Phase 7 sub-phase 7a (Bootstrap). The 4
Phase 7-specific skills at .claude/skills/ are available via tool_search
discovery. Anti-leakage discipline binds per Entry Directive §8.
```

Press Enter. Approve each file read with `y`.

**What Claude does:**

5.2.1 Reads the 3 files
5.2.2 Loads the workspace context
5.2.3 Verifies entry-gate (should report 7/7 PASS since you completed Parts 1–3)
5.2.4 States the next action per Entry Directive §4.5
5.2.5 Waits for your authorization

**Expected result:**

| Element | Expected |
|---|---|
| Entry-gate report | 7/7 criteria CLEARED |
| Next action statement | References Entry Directive §4.5 — likely "Confirm session task scope; begin substrate scaffolding instantiation per directive §6" |
| Wait posture | Claude pauses; awaits your direction |

### §5.3 Confirm 7a entry-gate cleared

If Claude reports 7/7 entry-gate criteria CLEARED: **Phase 7 sub-phase 7a is open. Phase 7 Session 1 is active.**

If Claude reports any FAILED criterion: return to that criterion's gating step (typically in Part 3) and resolve before proceeding.

### §5.4 Phase 7 Session 1 — what comes next

From this point onward, Phase 7 Session 1 operates per the Entry Directive. You are no longer in bootstrap; you are in active Phase 7 execution.

Typical Session 1 scope per Entry Directive §4.6:

| Property | Value |
|---|---|
| Session scope target | Substrate scaffolding instantiation + first unit landing(s) at operator discretion |
| Session does NOT target | 7a closure (closure requires all 12 unit landings + smoke test pass per directive §5.4) |
| Per-unit cadence | Per directive §5.3: operator authorizes unit landing → implementation at MCP server boundary → verification → operator confirms close → next unit eligible |
| Operator-presence | HIGH (no overnight-executable surfaces at 7a) |

The first unit to consider landing is typically U-IS-01 (path-class registry) per the IS plan v2.2 §3.1 topological order, but operator discretion applies — you may choose to first instantiate substrate scaffolding (e.g., the `.harness/state.jsonl` first write convention) before landing any atomic unit.

To proceed with Session 1, tell Claude:

```
Proceed with substrate scaffolding instantiation per Entry Directive
§6.2. Start with surface 1 (path conventions). Read the relevant
per-axis CLAUDE.md and propose the scaffolding action; do not execute
until I approve.
```

From this point forward, the project session pattern resumes: terse confirmations at each gate, per-unit HITL approval, design-phase back-flow if any Class 1 fork surfaces.

**Phase 7 Session 1: OPEN.**

---

## §6 Verification checklist

Use the checklist at the end of each Part to confirm readiness for the next.

### §6.1 End of Part 1 — machine setup verification

| # | Check | How to verify |
|---|---|---|
| 1 | Claude Code installed | `claude --version` returns a version number |
| 2 | uv installed | `uv --version` returns a version number |
| 3 | git installed | `git --version` returns a version number |
| 4 | Claude Code logged in | `claude` launches without prompting for login |

All 4 must PASS before starting Part 2.

### §6.2 End of Part 2 — workspace + artifacts verification

| # | Check | How to verify |
|---|---|---|
| 1 | Workspace folder exists | `cd ~/harness-build && pwd` returns a path |
| 2 | 11 artifacts at canonical paths | `find . -type f \| sort` lists exactly the 11 paths per §3.6.1 |
| 3 | Per-axis subdirectories exist | `ls harness-is harness-as harness-cp harness-od` lists `CLAUDE.md` in each |
| 4 | `.claude/skills/` populated | `ls .claude/skills/` shows 4 skill directories |

All 4 must PASS before starting Part 3.

### §6.3 End of Part 3 — workspace operationalization verification

| # | Check | Verification command |
|---|---|---|
| 1 | Workspace root pyproject.toml present | `cat pyproject.toml \| head -5` |
| 2 | Per-axis pyproject.toml × 6 present | `find . -name pyproject.toml \| wc -l` returns 7 (1 root + 6 axes) |
| 3 | uv.lock generated | `ls uv.lock` |
| 4 | `.venv/` exists | `ls -d .venv` |
| 5 | git repository initialized | `git log --oneline` shows ≥ 1 commit |
| 6 | `.harness/` directory exists | `ls -d .harness` |
| 7 | `.claude/mcp.json` exists and is valid JSON | `cat .claude/mcp.json \| python -m json.tool` (no error) |
| 8 | All tools runnable | `uv run pyright --version && uv run ruff --version && uv run pytest --version` all return versions |

All 8 must PASS before starting Part 4.

### §6.4 End of Part 4 — Phase 7 Session 1 entry verification

| # | Check | How to verify |
|---|---|---|
| 1 | Claude reads Entry Directive at session open | Claude reports having read the directive |
| 2 | 7/7 entry-gate criteria CLEARED | Claude reports PASS on all 7 per directive §3 |
| 3 | Claude is in 7a posture | Claude does not auto-spawn sub-agents (sub-agent count at 7a = 0 per directive §7.2) |
| 4 | Phase 7-specific skills discoverable | Claude acknowledges 4 skills available via tool_search |

All 4 must PASS to confirm Phase 7 Session 1 is open.

---

## §7 Troubleshooting

### §7.1 Claude Code "command not found" after install

**Symptom:** After §2.2 install, `claude --version` returns "command not found" or "claude: command not found".

**Cause:** Your shell's PATH variable does not yet know where `claude` is installed.

**Fix:**

7.1.1 Close all terminal windows entirely.
7.1.2 Open a fresh terminal.
7.1.3 Retry `claude --version`.

**If still fails:**

7.1.4 On macOS / Linux, type:
   ```
   echo $PATH
   ```
   Check whether `/usr/local/bin` or `~/.local/bin` is in the output.

7.1.5 If neither path is present, follow the install script's guidance to add it to your shell profile (`~/.zshrc` for macOS default, `~/.bashrc` for Linux default).

7.1.6 As a fallback, reinstall via the alternative method:
   - npm method (requires Node.js 18+ installed first): `npm install -g @anthropic-ai/claude-code`
   - Homebrew on macOS: `brew install --cask claude-code`

7.1.7 If still failing, consult https://code.claude.com/docs/en/setup

### §7.2 uv "command not found" after install

Same root cause as §7.1 (PATH not refreshed).

**Fix:**

7.2.1 Close and reopen terminal.
7.2.2 Try `uv --version` again.

**If still fails:**

7.2.3 Add uv to PATH manually:
   ```
   export PATH="$HOME/.local/bin:$PATH"
   ```
   Run this in the terminal; it will work for the current session.

7.2.4 To make permanent, append the same line to `~/.zshrc` (macOS) or `~/.bashrc` (Linux).

7.2.5 Alternative install: `pip install uv` (if Python is already installed).

### §7.3 Claude's orientation response in §4.3 is vague or incorrect

**Symptom:** Claude doesn't cite specific design artifacts (ADD v1.3, etc.) or makes generic statements.

**Cause:** Claude may not have read the files thoroughly, or may have hit a context budget.

**Fix:**

7.3.1 Tell Claude:
   ```
   Please re-read ./CLAUDE.md fully (do not summarize prematurely),
   then re-read ./Phase_7_Session_1_Entry_Directive_v1.md fully.
   Then re-answer my prior question with byte-exact citations to
   specific sections of each file.
   ```

7.3.2 If Claude continues to be vague, close the session (`/exit`), reopen with `claude`, and retry the orientation prompt.

### §7.4 `uv sync` fails

**Symptom:** Errors during dependency resolution (e.g., version conflict, package not found).

**Common causes and fixes:**

| Cause | Symptom | Fix |
|---|---|---|
| Network issue | "timeout" or "connection error" | Wait 1 minute; retry `uv sync` |
| Wrong Python version | "requires-python not satisfied" | Verify `.python-version` file content; ensure Python 3.12+ is installed (`python3 --version`) |
| Conflicting versions in pyproject.toml | "version solver failed" | Ask Claude: "uv sync failed with version solver error. Please diagnose and propose a fix to pyproject.toml" |
| Forbidden library accidentally included | (no specific error; check `pyproject.toml`) | Ask Claude to re-review pyproject.toml against framework-pull discipline |

### §7.5 git commit fails — "Author identity unknown"

**Symptom:** `git commit` fails with "Please tell me who you are" or similar.

**Fix:** Tell Claude to run:
```
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

Replace with your actual name and email. Re-run the commit.

### §7.6 Claude proposes content with a forbidden library

**Symptom:** During §4.4.1 or §4.4.2, Claude's proposed `pyproject.toml` includes `tenacity`, `langgraph`, etc.

**Fix:** Reject the proposal explicitly:

```
This proposal violates the framework-pull discipline declared in
./CLAUDE.md §3.2. The following libraries are forbidden:
tenacity, pybreaker, circuitbreaker, langgraph, crewai, langchain,
llamaindex, temporal, prefect, LiteLLM. Please revise to remove
ALL of these. Hand-rolled equivalents are authored at Phase 7 atomic
unit landings.
```

Claude will revise. Verify the revision before approving.

### §7.7 Claude wants to start writing H_T design content during bootstrap

**Symptom:** Claude proposes to write Python implementation code in `src/harness_*/` during the bootstrap session.

**Cause:** Claude may interpret your prompts as requesting Phase 7 unit landings.

**Fix:** Stop Claude immediately:

```
HALT. Bootstrap session scope is build infrastructure only (pyproject.toml,
gitignore, etc.). H_T design content authoring happens at Phase 7 Session
1 onward, with operator authorization per unit. Per X-AL-3 (Phase_7_Meta_
Architecture §7.7), do not write any Python code in src/harness_*/ during
this bootstrap session.

Return to the prior build-infrastructure step.
```

### §7.8 Phase 7 Session 1 entry-gate check reports criterion FAILED

**Symptom:** At §5.2 verification step (4), Claude reports one or more of the 7 entry-gate criteria as FAILED.

**Fix:** Read Claude's diagnosis. Common cases:

| Failed criterion | Likely cause | Resolution |
|---|---|---|
| #1 Target stack committed | `Target_Stack_Commitment_v1.md` not accessible from this workspace | Confirm it's accessible at design-phase workspace (it should be — but this workspace reads via cross-workspace reference) |
| #2 Workspace operational | Bootstrap incomplete (Part 3 step missing) | Return to §6.3 and resolve any FAILED check |
| #3 Entry Directive filed | The directive is missing at workspace root | Confirm `./Phase_7_Session_1_Entry_Directive_v1.md` exists per §3.5 row 11 |
| #4 Bootstrap substrate landed | Missing CLAUDE.md or SKILL.md file | Re-verify §3.6 file inventory |
| #5 Design artifacts accessible | Cross-workspace reference cannot resolve | Confirm design-phase workspace is intact in Claude.ai |
| #6 Meta-Architecture accessible | Same as #5 | Same as #5 |
| #7 No open forks from Phase 6.5 | Phase 6.5 close handoff lists open Class 1/2 | Resolve open forks before Phase 7 entry |

---

## §8 Glossary

Terms used in this runbook and the broader project, defined inline:

| Term | Definition |
|---|---|
| **H_T** | "Harness Target" — the multi-LLM agent harness being built. The end product. |
| **H_E** | "Harness Execution" — the Claude Code CLI environment hosting the build. The tool you use to build H_T. |
| **HITL** | Human-in-the-loop. The pattern of LLM proposing actions and the human reviewing/approving each one. |
| **CLI** | Command-line interface — a text-based way to interact with software. The terminal is your CLI. |
| **Terminal** | The application that shows the CLI. Examples: macOS Terminal, iTerm2, PowerShell, Windows Terminal. |
| **Claude Code CLI** | Anthropic's terminal-based AI assistant. The tool you install in Part 1. |
| **uv** | A Python package manager and toolchain. Replaces pip, virtualenv, poetry, etc. |
| **pyproject.toml** | Python project configuration file. Declares dependencies, tools, project metadata. |
| **Workspace** | In uv: a top-level project containing multiple Python sub-packages (workspace members). |
| **Workspace member** | A Python package inside a workspace. In this build: harness-core, harness-is, harness-as, harness-cp, harness-od, harness-cxa. |
| **uv.lock** | Lockfile recording exact dependency versions for reproducibility. Generated by `uv sync`. |
| **.venv** | Virtual environment directory created by uv. Contains the installed Python packages for this workspace. Hidden by default (dot-prefix). |
| **git** | A version control system. Tracks file changes over time. |
| **Repository (repo)** | A git-managed folder with version history. Created by `git init`. |
| **.gitignore** | A file telling git which paths to exclude from version control. |
| **Commit** | A saved snapshot of files at a point in time in git. |
| **MCP** | Model Context Protocol — Anthropic's protocol for connecting Claude to external tools. |
| **FastMCP** | A Python framework for building MCP servers. |
| **OTel** | OpenTelemetry — an open standard for observability (traces, metrics, logs). |
| **JSONL** | A file format: one JSON object per line. Used for the state ledger. |
| **State ledger** | A JSONL file (`.harness/state.jsonl`) that records every state change in the harness, with hash-chain integrity. |
| **Atomic unit** | The smallest implementation increment in the v2.x implementation plans. Identified by IDs like U-IS-01. |
| **L0 unit** | A "Level 0" atomic unit — one with no dependencies on other units in its axis. The first units to be implemented per topological order. |
| **Axis** | One of the four design axes: IS (Information Substrate), AS (Action Surface), CP (Control Plane), OD (Operational Discipline). |
| **CXA** | Cross-Axis composition — the 101 typed cross-axis edges connecting the 4 axes. |
| **Phase 7** | The execution phase of the harness build, where atomic units land and the harness becomes operational. |
| **Sub-phase 7a** | The "bootstrap" sub-phase of Phase 7 — first 12 unit landings + substitution scaffolding. |
| **Substitution** | A temporary replacement at 7a where H_E (Claude Code CLI) provides a stand-in for a not-yet-built H_T primitive. |
| **Retirement** | The event where a substitution is removed because the H_T primitive has been built. |
| **Anti-leakage** | Discipline preventing H_E patterns from contaminating H_T design. Enforced by 20 rules. |
| **Class 1 fork** | A defect surfaced during Phase 7 that requires design-phase artifact revision. Halts execution. |
| **Class 2 fork** | A decision point during Phase 7 requiring operator selection between alternatives. Pauses execution. |
| **Class 3 informational** | An observation logged at session close. Non-blocking. |
| **Cross-workspace reference** | Reading a file from the design-phase workspace while operating in this build workspace. |
| **Design-phase workspace** | The Claude.ai project where the design substrate (ADRs, ADD, PRD, specs, plans, CXA, Workflow, Meta-Architecture) lives. |
| **Bootstrap session** | The Claude Code CLI session covered in Part 3, where build infrastructure is authored. |

---

## §9 Filing footer

| Field | Value |
|---|---|
| Artifact | `Phase_7_Workspace_Bootstrap_Runbook_v1.md` |
| Type | Operational runbook for non-technical operator |
| Authoring authority | Operator directive 2026-05-15 (LLM-assisted artifact authoring; HITL review pattern) |
| Predecessor | `Phase_6_5_Session_7_Close_Handoff.md`; 11 bootstrap artifacts |
| Successor | Phase 7 Session 1 at new Claude Code CLI workspace |
| Filing destination | `/mnt/user-data/outputs/Phase_7_Workspace_Bootstrap_Runbook_v1.md` → operator-side reference during workspace bootstrap |
| Confidence | [HIGH] for Claude Code install steps (verified against code.claude.com/docs/en/quickstart 2026-03 vintage); [HIGH] for substrate citations to project artifacts; [MODERATE] for uv install convention; [SPECULATIVE] for `.claude/mcp.json` exact schema (deferred to Claude Code documentation verification at workspace open) |
| Date | 2026-05-15 |

---

*End of Phase 7 Workspace Bootstrap Runbook v1. Follow Parts 1 → 2 → 3 → 4 in order. Use §6 checklists at each Part boundary. Reference §7 troubleshooting and §8 glossary as needed.*
