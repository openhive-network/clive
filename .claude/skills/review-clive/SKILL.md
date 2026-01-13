---
name: review-clive
description: |
  Code review skill for Clive project with intelligent input detection and mode selection.
  Use this skill when:
  - User invokes /review-clive or /review-clive <MR_NUMBER> or /review-clive <URL>
  - Reviewing merge request changes for Clive project
  - Reviewing local branch changes before creating MR
  - Need to publish review comments to GitLab with approval workflow

  This skill orchestrates: input detection, context analysis, mode selection (agent vs manual),
  review execution, Polish approval, English approval, and GitLab publishing.
---

# Review Clive

Code review for Clive project with smart detection and flexible execution.

## Workflow

### Step 1: Detect Input

**If argument provided:**
- Number (e.g., `123`) → MR number
- URL → Extract MR number from URL

**If no argument:**
```bash
# Check current branch for MR
git branch --show-current
glab mr list --source-branch=<branch>
```

Then offer choices:
- MR found → Suggest reviewing it, offer alternatives
- Local changes only → Suggest local review
- Nothing → Ask: "Co chcesz zreviewować?"

### Step 2: Detect Context

```bash
# Check if MR exists and has discussions
glab mr view <MR_IID>
mcp__gitlab__mr_discussions(project_id="hive/clive", merge_request_iid="<MR_IID>")
```

Determine context type:
| Context | Condition |
|---------|-----------|
| `LOCAL` | No MR, only local changes |
| `INITIAL_MR` | MR exists, no/few discussions |
| `FOLLOWUP_MR` | MR exists, has discussions (review after fixes) |

### Step 3: Suggest Mode

| Context | Suggested Mode | Reason |
|---------|----------------|--------|
| `LOCAL` | Manual | Quick feedback, no publishing |
| `INITIAL_MR` | Agent (Recommended) | Thorough analysis of new MR |
| `FOLLOWUP_MR` | Manual (Recommended) | Check specific fixes, respond to threads |

**Always allow user to override the suggestion.**

### Step 4: Execute Review

**Agent mode:**
```
Task(subagent_type="clive-code-reviewer", prompt="Review MR !<N> for Clive project. Diff: <diff>")
```

**Manual mode:**
- Read [references/review-principles.md](references/review-principles.md) for review guidelines
- Analyze diff applying DRY, CLI/TUI, SRP, commit organization principles
- Use format from [references/response-format.md](references/response-format.md)

### Step 5: Present Results

1. **Show findings in Polish** (for user review)
2. Allow questions and clarifications
3. Allow rejection of individual items
4. **Wait for explicit approval** ("yes", "ok", "approve")

### Step 6: Publish (After Approval)

1. **Show English version** that will be published
2. **Wait for publication approval** ("publish", "send")
3. Use `gitlab-discussions` skill to learn how to publish on GitLab
4. Create threads on specific code lines
5. Add summary comment with thread references

## References

- **[review-principles.md](references/review-principles.md)** - Review guidelines (DRY, CLI/TUI, SRP, commits). Read before reviewing.
- **[response-format.md](references/response-format.md)** - Output format template for review results.
- **[lessons-learned.md](references/lessons-learned.md)** - Accumulated knowledge from past reviews.

## Language Rules

- **Console output**: Polish (for approval workflow)
- **GitLab comments**: Always English
- **Code examples**: Keep original (English identifiers)

## Critical Rules

1. **Two-stage approval**: Polish first, then English
2. **Never auto-publish**: Always wait for explicit user confirmation
3. **Use gitlab-discussions skill**: For proper MCP tool usage
4. **Same principles for both modes**: Agent and manual use identical review-principles.md
