---
name: process-inbox
description: Process pending items in the Needs_Action folder. Use when there are new files to process, when the user says "process inbox", "check needs action", or "process pending items". Reads action files, determines what needs to be done, and moves completed items to Done.
argument-hint: [optional-filter]
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(mv *), Bash(ls *)
---

You are the AI Employee (Bronze Tier). Process all pending items in the `Bronze/Needs_Action/` folder.

## Steps

1. **Scan** `Bronze/Needs_Action/` for all `.md` files with `status: pending` in their frontmatter
2. **Read** each file's content and metadata (type, priority, original filename)
3. **Analyze** what action is needed based on the file type and content
4. **Act** on each item:
   - For simple file drops: summarize the file, mark suggested actions as complete
   - For tasks: extract action items and note them
   - For unknown types: flag for human review
5. **Update** the file's `status` frontmatter from `pending` to `done`
6. **Add** a `## Completion` section with timestamp and summary of action taken
7. **Move** the processed file from `Bronze/Needs_Action/` to `Bronze/Done/`
8. **Log** the action by appending a JSON entry to `Bronze/Logs/YYYY-MM-DD.json`

## Log Entry Format

```json
{
  "timestamp": "ISO-8601",
  "action_type": "process",
  "actor": "claude_code",
  "source": "Bronze/Needs_Action/filename.md",
  "destination": "Bronze/Done/filename.md",
  "details": "Summary of what was done",
  "result": "success"
}
```

## Rules

- Never delete any files — only move between folders
- If unsure about an action, create a plan in `Bronze/Plans/` instead of acting
- Always update `Bronze/Dashboard.md` after processing (invoke /update-dashboard)
- Skip files with `status: error` — leave them for human review
- Process items in order of priority: critical > high > medium > low

$ARGUMENTS
