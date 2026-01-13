# Review Principles

Core principles for reviewing Clive project code. Apply these in both agent and manual mode.

> **Note:** Always apply coding conventions from **CLAUDE.md** alongside these review principles.

## 1. Reusability and DRY (CRITICAL)

Clive is a mature project. **Actively search** for existing implementations before accepting new code.

**Process:**
Search for similar implementations in `clive/__private/` - check commands, models, utilities, widgets.

**Actions:**
- If duplication found → **Demand refactoring** toward existing code
- Show existing code with `file:line` references
- Never accept workarounds that bypass existing architecture

## 2. CLI/TUI Cross-Check (MANDATORY)

Dual interfaces must maintain consistency.

**For CLI changes (`clive/__private/cli/`):**
- Check if equivalent functionality exists in TUI (`clive/__private/ui/`)
- Verify shared logic is extracted to common modules
- Reference `docs/cli_commands_structure.md`

**For TUI changes (`clive/__private/ui/`):**
- Check if equivalent functionality exists in CLI
- Ensure shared business logic uses same underlying commands

**Always use comparison tables** for discrepancies:
```markdown
| Value | TUI | CLI |
|-------|-----|-----|
| **HP** | `humanize_hive_power()` | `humanize_hive_power_with_comma()` |
```

## 3. Single Responsibility Principle (SRP)

Verify SRP compliance at all levels:

| Level | Requirement |
|-------|-------------|
| **Functions** | Each does one thing well |
| **Classes** | Single responsibility, no "God classes" |
| **Commands** | One atomic operation each |
| **Modules** | Cohesive - all code relates to single concept |

**Common violations to catch:**
- Function that both modifies data AND returns formatted output
- Class handling both business logic AND UI presentation
- Mixing validation with transformation in same method

## 4. Commit Organization

Each commit should represent ONE logical change.

**Rules:**
- Separate refactoring from behavior changes
- Separate constant definitions from their usage
- Separate bug fixes from features
- Separate style changes from logic changes

**Bad example:**
```
"Add user validation and refactor error messages"
```

**Good example:**
```
Commit 1: "Refactor error messages to use constants"
Commit 2: "Add user validation for profile updates"
```

**Demand commit splitting** when SRP is violated in commits.

## 5. Architecture Compliance

Verify code follows Clive patterns from CLAUDE.md:

- **Command Pattern**: Use `world.commands` not direct API calls
- **World Object**: Single source of truth for application state
- **Profile System**: Factory methods, proper persistence
- **Async context managers**: Required for World, Node resources

## Review Process Summary

1. **Read code thoroughly** - Understand intent and implementation
2. **Search for existing patterns** - Use grep/find for similar implementations
3. **Verify architectural alignment** - Check against CLAUDE.md patterns
4. **Cross-check interfaces** - Verify CLI/TUI consistency
5. **Check SRP compliance** - Single responsibilities in code and commits
6. **Document findings** - Clear, actionable feedback with code examples
