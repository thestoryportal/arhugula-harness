# Governance pack — repo layout

*Relocated BYTE-VERBATIM from Root `CLAUDE.md` §3.3 by U-CTX-13 (R-CTX-1 Arc 5, 2026-08-11).*
*The root file keeps every heading with its number and position, plus a resolving
pointer to this file. Query this pack for the detail; do not preload it.*

---

### 3.3 Repo layout

```
<workspace_root>/
├── CLAUDE.md                                # This file
├── Sub_Agent_Boundary_Specification_v1.md   # §5 sub-agent boundary
├── .claude/
│   └── skills/                              # Phase 7-specific skills (§6)
│       ├── phase-7-implementation/SKILL.md
│       ├── phase-7-cross-axis-composition/SKILL.md
│       ├── phase-7-substitution-retirement/SKILL.md
│       └── phase-7-back-flow-routing/SKILL.md
├── pyproject.toml                           # uv workspace root
├── uv.lock
├── harness-core/                            # Shared types + cross-axis utilities
│   ├── pyproject.toml
│   └── ...
├── harness-is/
│   ├── CLAUDE.md
│   ├── pyproject.toml
│   └── ...
├── harness-as/
│   ├── CLAUDE.md
│   ├── pyproject.toml
│   └── ...
├── harness-cp/
│   ├── CLAUDE.md
│   ├── pyproject.toml
│   └── ...
├── harness-od/
│   ├── CLAUDE.md
│   ├── pyproject.toml
│   └── ...
└── harness-cxa/                             # CXA seam instantiation
    ├── pyproject.toml
    └── ...
```

---

