# Claude Code Architecture

Graph of information sources used by Claude in this project.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLAUDE.md                                       │
│                         (Main source of truth)                               │
│                                                                              │
│  • Project overview & architecture                                           │
│  • Code style & conventions                                                  │
│  • Code Review Guidelines (naming, coding practices, class structure)        │
│  • Test conventions                                                          │
│  • GitLab instance info                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ references
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               .claude/                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────┐         ┌─────────────────────┐                    │
│  │      skills/        │         │      agents/        │                    │
│  └─────────────────────┘         └─────────────────────┘                    │
│            │                               │                                 │
│            ▼                               ▼                                 │
│  ┌───────────────────┐          ┌───────────────────────┐                   │
│  │   review-clive/   │◄─────────│  clive-code-reviewer  │                   │
│  │                   │ uses     │                       │                   │
│  │  • SKILL.md       │ refs     │  • Invoked by skill   │                   │
│  │  • references/    │          │  • Reads skill refs   │                   │
│  │    ├─ review-     │          │  • Returns findings   │                   │
│  │    │  principles  │          └───────────────────────┘                   │
│  │    ├─ response-   │                                                      │
│  │    │  format      │                                                      │
│  │    └─ lessons-    │                                                      │
│  │       learned     │                                                      │
│  └───────────────────┘                                                      │
│            │                                                                 │
│            │ uses                                                            │
│            ▼                                                                 │
│  ┌───────────────────┐                                                      │
│  │gitlab-discussions/│                                                      │
│  │                   │                                                      │
│  │  • MCP tools      │                                                      │
│  │  • Formatting     │                                                      │
│  │  • Link generation│                                                      │
│  └───────────────────┘                                                      │
│                                                                              │
│  ┌───────────────────┐                                                      │
│  │  skill-creator/   │                                                      │
│  │                   │                                                      │
│  │  • Skill creation │                                                      │
│  │    guidelines     │                                                      │
│  │  • scripts/       │                                                      │
│  │    init_skill.py  │                                                      │
│  └───────────────────┘                                                      │
│                                                                              │
│  ┌─────────────────────┐                                                    │
│  │      commands/      │                                                    │
│  └─────────────────────┘                                                    │
│            │                                                                 │
│            ▼                                                                 │
│  ┌───────────────────┐                                                      │
│  │  Simple commands  │                                                      │
│  │                   │                                                      │
│  │  • /lint          │                                                      │
│  │  • /test          │                                                      │
│  │  • /smoke         │                                                      │
│  │  • /reflection    │                                                      │
│  └───────────────────┘                                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘


## Flow: /review-clive

┌──────────┐     ┌─────────────────┐     ┌────────────────────┐
│  User    │────▶│  review-clive   │────▶│ clive-code-reviewer│
│          │     │  (skill)        │     │ (agent) - optional │
└──────────┘     └─────────────────┘     └────────────────────┘
                        │                         │
                        │                         │ reads
                        │                         ▼
                        │                 ┌───────────────┐
                        │                 │review-principles│
                        │                 │response-format │
                        │                 │lessons-learned │
                        │                 └───────────────┘
                        │
                        │ after approval
                        ▼
                 ┌─────────────────┐
                 │gitlab-discussions│
                 │ (MCP tools)     │
                 └─────────────────┘
                        │
                        ▼
                 ┌─────────────────┐
                 │   GitLab MR     │
                 │   (threads +    │
                 │    summary)     │
                 └─────────────────┘


## Information Hierarchy

1. CLAUDE.md
   └── Project conventions (used everywhere)

2. Skills (workflow orchestration)
   └── review-clive/
       ├── SKILL.md (workflow steps)
       └── references/ (shared by skill & agent)
           ├── review-principles.md  ← DRY, CLI/TUI, SRP, commits
           ├── response-format.md    ← output template
           └── lessons-learned.md    ← accumulated knowledge

3. Agents (specialized execution)
   └── clive-code-reviewer
       └── References skill's files (no duplication)

4. Supporting skills
   ├── gitlab-discussions (MCP tools for GitLab)
   └── skill-creator (creating new skills)

5. Commands (simple slash commands)
   ├── /lint      → pre-commit hooks
   ├── /test      → pytest runner
   ├── /smoke     → quick smoke test
   └── /reflection → analyze Claude config
```

## Key Principles

- **Single source of truth**: Review principles live in skill, agent references them
- **No duplication**: Agent doesn't copy guidelines, only points to skill files
- **Progressive disclosure**: SKILL.md is lean, details in references/
- **Separation of concerns**:
  - CLAUDE.md = project conventions
  - Skill = workflow orchestration
  - Agent = code analysis execution
  - References = shared detailed guidelines
