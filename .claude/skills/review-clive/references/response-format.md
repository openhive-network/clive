# Response Format

Template for structuring code review output.

## Review Template

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

## Best Practices

- Include **file paths with line numbers** (e.g., `filename.py:42-45`)
- Use syntax highlighting with ```python blocks
- Quote **actual code** from the codebase, don't paraphrase
- Show **before/after** when suggesting changes
- Use comparison tables for CLI/TUI discrepancies
