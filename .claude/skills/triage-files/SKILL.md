---
name: triage-files
description: Triage and classify files in the Inbox folder, creating structured action files in Needs_Action. Use when the user says "triage files", "check inbox", "sort inbox", or when new files appear in the Inbox.
argument-hint: [directory-path]
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(mv *), Bash(ls *), Bash(mkdir *)
---

Triage files dropped into `Bronze/Inbox/` (or a specified directory) and create structured action files in `Bronze/Needs_Action/`.

## Steps

1. **Scan** the target directory (default: `Bronze/Inbox/`) for all files
2. **Skip** hidden files (starting with `.`) and sensitive files (`.env`, `.key`, `.pem`)
3. **For each file**, read its content and metadata:
   - File name, extension, size
   - Content keywords for priority classification
4. **Classify priority** using these keyword rules:
   - **Critical**: "critical", "emergency", "outage"
   - **High**: "urgent", "asap", "important"
   - **Medium**: "invoice", "report", "review", "todo"
   - **Low**: "info", "fyi", "note", "readme"
   - **Default**: medium (if no keywords match)
5. **Create an action file** in `Bronze/Needs_Action/` with this format:

```markdown
---
type: file_drop
original_name: "<filename>"
file_type: <markdown|text|pdf|image|script|unknown>
size_bytes: <size>
priority: <critical|high|medium|low>
source_path: "<original path>"
received: <ISO timestamp>
status: pending
---

## New File for Processing

**File:** <name>
**Type:** <type>
**Size:** <size> bytes
**Priority:** <priority>
**Received:** <timestamp>

## Content Preview
<first 500 chars of file content if text-readable>

## Suggested Actions
- [ ] Review file content
- [ ] Categorize and file appropriately
- [ ] Move to /Done when processed
```

6. **Log** each triage action to `Bronze/Logs/YYYY-MM-DD.json`
7. **Update dashboard** after triaging all files (invoke /update-dashboard)

## File Naming Convention

Action files: `FILE_<safe-name>_YYYY-MM-DD_HHMMSS.md`

## Security Rules

- NEVER process `.env`, `.key`, `.pem`, `.p12`, `.pfx`, or `.credentials` files
- NEVER execute scripts dropped into Inbox — only read their content
- Flag suspicious files in the action file metadata

$ARGUMENTS
