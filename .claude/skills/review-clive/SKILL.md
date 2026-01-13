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
  review execution, approval workflow, and GitLab publishing.
---

# Review Clive

Code review for Clive project with smart detection and flexible execution.

## Workflow

### Step 0: Detect Language

Determine communication language for this session:

1. **If language clear from context** → use it
2. **Otherwise** → ask: "Polish (recommended) / English?"

**Note:** This only affects communication with user. GitLab comments are always in English.

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
- Nothing → Ask: "What do you want to review?"

### Step 2: Detect Context

```bash
# Quick check: MR info + blocking discussions status
glab mr view <MR_IID> -F json | jq '{user_notes_count, blocking_discussions_resolved}'

# Count unresolved threads (use glab api, NOT MCP - avoids large payloads)
glab api "projects/hive%2Fclive/merge_requests/<MR_IID>/discussions?per_page=100" | \
  jq '[.[] | select(.notes[0].resolvable == true and .notes[0].resolved == false)] | length'

# Preview unresolved threads
glab api "projects/hive%2Fclive/merge_requests/<MR_IID>/discussions?per_page=100" | \
  jq -r '[.[] | select(.notes[0].resolvable == true and .notes[0].resolved == false)] |
         .[] | "\(.id[0:8])... | \(.notes[0].author.username) | \(.notes[0].body[0:50])..."'
```

Determine context type:
| Context | Condition |
|---------|-----------|
| `LOCAL` | No MR, only local changes |
| `INITIAL_MR` | MR exists, no discussions yet (fresh MR, never reviewed) |
| `FOLLOWUP_MR` | MR exists, has discussions (already reviewed - resolved or not) |

For `FOLLOWUP_MR`, additionally check unresolved threads count to determine if action needed.

**Note:** Use `glab api` for counting/listing threads. Use MCP only for creating comments, responding, or resolving.

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

**FOLLOWUP_MR with unresolved threads** - sequential review:

1. Show: "Found X unresolved threads. Show details of thread #1?"
2. For each thread:
   - Show thread content (author, original comment, responses)
   - Verify if suggestion was implemented in code
   - Present verification result
   - Offer: "Resolve thread #1?" or "Skip to thread #2?"
3. After user decision → proceed to next thread
4. Repeat until all threads reviewed

Example flow:
```
Found 3 unresolved threads. Show details of thread #1?
→ [show details + code verification]
Suggestion implemented ✅ → Resolve thread #1, or skip to #2?
→ [user: resolve]
Thread #1 resolved. Show details of thread #2?
```

### Step 5: Present Results

1. **Show findings in user's language** (detected in Step 0)
2. Allow questions and clarifications
3. Allow rejection of individual items
4. **Wait for explicit approval**

### Step 6: Final Verification (After Manual Review)

**If review was manual**, suggest final agent verification:
```
All threads reviewed. Run final agent check to catch anything missed?
```

This ensures comprehensive coverage - manual review focuses on specific threads while agent can spot patterns across entire diff.

### Step 7: Final Summary (After Review Complete)

When all issues are resolved and user confirms review is complete, create and publish summary.

**1. Prepare summary:**

Fetch ALL discussions from MR:
```bash
glab api "projects/hive%2Fclive/merge_requests/<MR_IID>/discussions?per_page=100"
```

Categorize discussions:
- Resolvable threads (code comments) → Issues Addressed table
- General comments → Context for summary
- System notes → Skip

For EACH discussion, read the FULL conversation to verify what was actually done.

Check for created issues:
```bash
glab api "projects/hive%2Fclive/merge_requests/<MR_IID>/discussions?per_page=100" | \
  jq -r '.[] | .notes[] | .body' | grep -oE '#[0-9]+|issues/[0-9]+'
```

Build summary using template from [response-format.md](references/response-format.md#final-summary-comment-template).

**2. Get approval:**

- Show English version that will be published (translate if user's language differs)
- Wait for explicit user approval

**3. Publish:**

- Use `gitlab-discussions` skill for MCP tools
- Create threads on specific code lines (if new issues found)
- Post summary comment to MR

## References

- **[review-principles.md](references/review-principles.md)** - Review guidelines (DRY, CLI/TUI, SRP, commits). Read before reviewing.
- **[response-format.md](references/response-format.md)** - Output format template for review results.
- **[lessons-learned.md](references/lessons-learned.md)** - Accumulated knowledge from past reviews.

## Language Rules

- **Communication with user**: Match user's language (detected in Step 0)
- **GitLab comments**: Always English (mandatory)
- **Code examples**: Keep original (English identifiers)

## Critical Rules

1. **Two-stage approval**: User's language first, then English for GitLab
2. **Never auto-publish**: Always wait for explicit user confirmation
3. **Use gitlab-discussions skill**: For proper MCP tool usage
4. **Same principles for both modes**: Agent and manual use identical review-principles.md
