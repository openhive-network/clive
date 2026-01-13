# Response Format

Templates for structuring code review output at different stages.

## Review Template (Claude Code Only)

**Purpose:** Present review findings to user locally. NOT published to GitLab.

If issues are found, they are later published as **individual threads on specific code lines** - not as this template.

```markdown
## Code Review

### Positive Aspects
[What was done well - acknowledge good patterns and practices]

---

### Must Fix (Critical Issues)

#### Consistency Violations
- [Specific inconsistencies with code examples]

#### Reusability Concerns
- [Existing code to reuse, with file:line references]

#### CLI/TUI Alignment Issues
- [Discrepancies with comparison tables]

#### SRP Violations
- [Functions/classes with multiple responsibilities]

#### Commit Organization Issues
- [Mixed concerns that should be split]

---

### Nice to Have (Suggestions)
[Optional improvements]

---

### Summary
[1-2 sentences on what needs to be done]
```

## Code Examples Guidelines

**Always include code examples** to make feedback actionable.

### Referencing Existing Code

```markdown
#### Description (`filename.py:line_start-line_end`):
```python
# actual code from the file
```
```

**Example:**
```markdown
#### TUI formatting (`dashboard.py:178-180`):
```python
if self.is_staking_hive_power:
    return humanize_hive_power(cast("Asset.Hive", asset_value))
return humanize_asset(asset_value, use_short_form=self.is_stake)
```
```

### Comparison Tables for CLI/TUI

```markdown
| Value | TUI (Dashboard) | CLI (this MR) |
|-------|-----------------|---------------|
| **HP** | `humanize_hive_power()` | `humanize_hive_power_with_comma()` |
| **VESTS** | `humanize_asset(..., use_short_form=True)` | `humanize_asset(...)` missing flag |
```

### Suggested Fixes

Always show the suggested fix:

```markdown
#### Suggested fix:
```python
hp_stake = humanize_hive_power(self._account_data.owned_hp_balance.hp_balance)
vests_stake = humanize_asset(self._account_data.owned_hp_balance.vests_balance, use_short_form=True)
```
```

## Immediate Action Feedback

**Every GitLab action MUST show link immediately after execution:**

```markdown
Thread #1 resolved ✅: https://gitlab.syncad.com/hive/clive/-/merge_requests/<MR_IID>#note_<NOTE_ID>

Comment published ✅: https://gitlab.syncad.com/hive/clive/-/merge_requests/<MR_IID>#note_<NOTE_ID>

New thread created ✅: https://gitlab.syncad.com/hive/clive/-/merge_requests/<MR_IID>#note_<NOTE_ID>
```

**Rule:** Never confirm an action without providing the link. User must be able to verify immediately.

## Link Format Rules

**CRITICAL:** GitLab links require numeric `note_id`, NOT `discussion_id` hash.

| Field | Format | Example | Works in URL? |
|-------|--------|---------|---------------|
| `discussion_id` | 40-char hash | `8650b0213b91d2531ec4...` | ❌ NO |
| `note_id` | Numeric | `237760` | ✅ YES |

**Correct format:**
```
https://gitlab.syncad.com/hive/clive/-/merge_requests/800#note_237760
```

**Wrong format (won't navigate to note):**
```
https://gitlab.syncad.com/hive/clive/-/merge_requests/800#note_8650b0213b91d2531ec4ff7210803cadb9706395
```

**How to get note_id from glab:**
```bash
glab api "projects/hive%2Fclive/merge_requests/<MR_IID>/discussions" | \
  jq '.[] | {discussion_id: .id, note_id: .notes[0].id}'
```

## Actions Summary Table

When presenting summary of multiple executed actions, **always include links**:

```markdown
| # | Action | Thread | Link |
|---|--------|--------|------|
| 1 | Resolve | PRIVATE_KEY_ERROR_MATCH | [note_243229](https://gitlab.syncad.com/.../merge_requests/800#note_243229) |
| 2 | Comment | Docstring (pydoclint) | [note_244167](https://gitlab.syncad.com/.../merge_requests/800#note_244167) |
| 3 | New thread | Duplicate commits | [note_244168](https://gitlab.syncad.com/.../merge_requests/800#note_244168) |
```

**Rule:** Every row with published comment or resolved thread MUST have a clickable link.

## Final Summary Comment Template (GitLab)

**Purpose:** Published to GitLab as closing comment when review is complete. Summarizes all resolved issues with links to threads.

```markdown
## Code Review Summary ✅

**Verdict: Approve** / **Request Changes**

[Brief 1-2 sentence assessment of the MR]

---

### Positive Aspects

| Area | Assessment |
|------|------------|
| **DRY Principle** | ✅ [Assessment with specifics] |
| **CLI/TUI Alignment** | ✅ [Assessment] |
| **SRP Compliance** | ✅ [Assessment] |
| **Test Coverage** | ✅ [Assessment] |
| **Commit Organization** | ✅ [Assessment] |

---

### Issues Addressed During Review

All X review threads were resolved. Key issues and resolutions:

#### [Category 1, e.g., Architecture & Design]
| Issue | Resolution | Thread |
|-------|------------|--------|
| [Exact issue from thread] | [What was ACTUALLY done] | [#<note_id>](url#note_<note_id>) |

#### [Category 2, e.g., Code Quality]
| Issue | Resolution | Thread |
|-------|------------|--------|
| ... | ... | ... |

#### [Category 3, e.g., Testing]
| Issue | Resolution | Thread |
|-------|------------|--------|
| ... | ... | ... |

---

### Follow-up Issues Created

| Issue | Description |
|-------|-------------|
| [#518](url) | [Brief description - what was deferred and why] |

*(Include this section only if issues were created during review)*

---

**All X threads resolved. No blocking issues remaining.** Ready to merge.
```

### Issues Table Guidelines

**CRITICAL - Verify resolutions before writing:**
- Read the FULL thread conversation (original + all responses)
- Check what the author ACTUALLY did, don't assume
- Example mistake: Writing "Added @override" when it was actually "Removed @override"

**Minimum issues count:** At least as many rows as resolvable threads (code discussions). Some threads may contain multiple issues - include them all.

**Categories:** Group issues logically (Architecture, Code Quality, Testing, CI/Dependencies, etc.)

## Best Practices

- Include **file paths with line numbers** (e.g., `filename.py:42-45`)
- Use syntax highlighting with ```python blocks
- Quote **actual code** from the codebase, don't paraphrase
- Show **before/after** when suggesting changes
- Use comparison tables for CLI/TUI discrepancies
- **Always include links** in action summary tables
- **Verify resolutions** by reading full thread conversations
