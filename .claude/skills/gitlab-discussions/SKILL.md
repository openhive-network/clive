---
name: gitlab-discussions
description: |
  GitLab thread and comment management using MCP tools. Use this skill when:
  - Creating, editing, or deleting threads or comments
  - Responding to discussions on merge requests or issues
  - Adding notes to merge requests or issues
  - Resolving or unresolving threads

  This skill ensures proper tooling (GitLab MCP) and consistent output (links to created content).
---

# GitLab Discussions

## Required Tooling

**Always use GitLab MCP tools** for thread/comment operations.

Merge requests:
- `mcp__gitlab__create_merge_request_thread`
- `mcp__gitlab__create_merge_request_discussion_note`
- `mcp__gitlab__create_merge_request_note`
- `mcp__gitlab__update_merge_request_discussion_note`
- `mcp__gitlab__delete_merge_request_discussion_note`
- `mcp__gitlab__resolve_merge_request_thread`
- `mcp__gitlab__mr_discussions`

Issues:
- `mcp__gitlab__create_note`
- `mcp__gitlab__create_issue_note`
- `mcp__gitlab__update_issue_note`
- `mcp__gitlab__list_issue_discussions`

**Never use:**
- `glab` CLI commands for these operations
- Raw API calls via `curl` or similar

## MCP Availability Check

Before performing GitLab thread/comment operations, verify MCP tools are available.

**If GitLab MCP is NOT available:**

1. Inform the user:
   ```
   GitLab MCP is not available. It's required for reliable thread/comment management.

   Installation instructions: https://gitlab.syncad.com/systemadmin/ai/-/blob/master/helpful_mcp_servers.md
   ```

2. Ask user to choose:
   - **Install GitLab MCP** (recommended) - follow installation guide
   - **Use glab CLI** (fallback) - may cause errors, limited functionality

## Post-Action Requirements

**After every successful create/edit operation, ALWAYS provide the direct link.**

Link formats:
- MR: `https://gitlab.syncad.com/{project}/-/merge_requests/{mr_iid}#note_{note_id}`
- Issue: `https://gitlab.syncad.com/{project}/-/issues/{issue_iid}#note_{note_id}`

Example responses:
```
MR !<MR_IID> comment added: https://gitlab.syncad.com/hive/clive/-/merge_requests/<MR_IID>#note_<NOTE_ID>
```
```
Issue #<ISSUE_IID> comment added: https://gitlab.syncad.com/hive/clive/-/issues/<ISSUE_IID>#note_<NOTE_ID>
```

## Formatting Rules

GitLab auto-links special patterns. Be intentional about their use:

| Pattern | Links to | Example |
|---------|----------|---------|
| `#N` | Issue N | `#123` → Issue 123 |
| `!N` | Merge Request N | `!456` → MR 456 |
| `%"name"` | Milestone | `%"v1.0"` → Milestone v1.0 |
| `@username` | User mention (notifies) | `@mzebrak` → mentions mzebrak |
| `~label` | Label | `~bug` → Label |
| `$N` | Snippet N | `$789` → Snippet 789 |
| `abc1234` | Commit (7+ chars) | `a1b2c3d4` → Commit |

**Avoid accidental links:**
-   ❌ `Problem #5:` or `Point #12` → use `Problem 5:` or `Point 12`
-   ❌ `Step !1` → use `Step 1`

**When referencing threads/notes, use full URLs:**

MR note:
```
[see thread](https://gitlab.syncad.com/hive/clive/-/merge_requests/<MR_IID>#note_<NOTE_ID>)
```

Issue note:
```
[related discussion](https://gitlab.syncad.com/hive/clive/-/issues/<ISSUE_IID>#note_<NOTE_ID>)
```

This ensures links work across projects and in external contexts.

## Common Operations

### Merge Requests

**Add comment to existing thread:**
```
mcp__gitlab__create_merge_request_discussion_note
├── project_id: "namespace/project"
├── merge_request_iid: "<MR_IID>"
├── discussion_id: "<DISCUSSION_ID>"
└── body: "Comment content"
```

**Create new thread:**
```
mcp__gitlab__create_merge_request_thread
├── project_id: "namespace/project"
├── merge_request_iid: "<MR_IID>"
└── body: "Thread content"
```

**Resolve/unresolve thread:**
```
mcp__gitlab__resolve_merge_request_thread
├── project_id: "namespace/project"
├── merge_request_iid: "<MR_IID>"
├── discussion_id: "<DISCUSSION_ID>"
└── resolved: true/false
```

Note: `resolve_merge_request_thread` doesn't return a note_id. After resolving, provide link to the first note of the thread:
```
Thread resolved: https://gitlab.syncad.com/hive/clive/-/merge_requests/<MR_IID>#note_<FIRST_NOTE_ID>
```

### Issues

**Add comment to issue:**
```
mcp__gitlab__create_issue_note
├── project_id: "namespace/project"
├── issue_iid: "<ISSUE_IID>"
└── body: "Comment content"
```

**Add comment to existing issue thread:**
```
mcp__gitlab__create_issue_note
├── project_id: "namespace/project"
├── issue_iid: "<ISSUE_IID>"
├── discussion_id: "<DISCUSSION_ID>"
└── body: "Reply content"
```
