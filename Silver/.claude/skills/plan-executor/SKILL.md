# Skill: Plan Executor

## Description

Creates and executes structured Plan.md files for complex multi-step tasks. Plans provide a transparent reasoning loop — the manager can see exactly what the AI is doing, what's completed, and what's next. Plans also serve as checkpoint/resume points if the AI is interrupted.

## When to Use

Invoke `/plan-executor` when:

- A task requires **3 or more distinct steps**
- A task involves **multiple skills or subagents** (e.g., draft email + get approval + send)
- A task has **dependencies between steps** (step 2 depends on step 1's output)
- A task involves **both approval-gated and non-gated actions**
- The manager asks for a **plan before execution**
- A file in `Needs_Action/` is classified as complex (keyword: "review", multi-part request)

## Plan File Format

### Naming
```
PLAN_<short-description>_YYYY-MM-DD_HHMMSS.md
```

Examples:
- `PLAN_onboard-new-client_2026-03-17_090000.md`
- `PLAN_quarterly-report-email_2026-03-17_140000.md`
- `PLAN_linkedin-content-series_2026-03-17_100000.md`

### Structure

```markdown
---
type: plan
description: "What this plan accomplishes"
status: pending | in_progress | blocked | completed | failed
steps_total: <N>
steps_completed: <M>
current_step: <step number currently being executed>
created_at: <ISO timestamp>
updated_at: <ISO timestamp>
blocked_by: "" | "approval_pending:<approval_file>" | "error:<description>"
source: "<what triggered this plan — file path, user request, etc.>"
---

## Plan: <Human-readable title>

**Goal:** <What this plan will accomplish>
**Triggered by:** <Source of the request>
**Created:** <timestamp>

### Steps

- [ ] Step 1: <description>
- [ ] Step 2: <description>
- [x] Step 3: <completed step — shows what was done>
- [ ] Step 4: <description> *(requires approval)*

### Step Log

| Step | Started | Completed | Result |
|------|---------|-----------|--------|
| 1 | <timestamp> | <timestamp> | <outcome> |
| 2 | <timestamp> | -- | in_progress |
```

## Execution Protocol

### Creating a Plan

1. Analyze the task and break it into discrete, sequential steps
2. Identify which steps require approval (outbound actions, destructive actions)
3. Mark approval-gated steps with `*(requires approval)*`
4. Write the Plan.md to `/Plans/`
5. Set `status: in_progress` and `current_step: 1`
6. Log `plan_create` to `/Logs/`
7. Begin executing Step 1

### Executing Steps

1. Read the plan file and find the current unchecked step (`- [ ]`)
2. Execute the step using the appropriate skill/agent
3. Mark the step as done: `- [x] Step N: <description> — <outcome>`
4. Update frontmatter: increment `steps_completed`, update `current_step`, update `updated_at`
5. Log `plan_step` to `/Logs/`
6. If all steps are complete, set `status: completed` and log `plan_complete`

### Blocking on Approval

When a step requires approval:

1. Invoke `/approval-request` to create the approval file
2. Update the plan's `blocked_by` field: `blocked_by: "approval_pending:APPROVAL_file.md"`
3. Set `status: blocked`
4. STOP execution — do not proceed to the next step
5. The orchestrator will detect when the approval moves to `/Approved/` and resume the plan

### Blocking on Error

When a step fails:

1. Update the plan's `blocked_by` field: `blocked_by: "error:<description>"`
2. Set `status: blocked`
3. Log the error
4. STOP execution — await manual intervention or retry

### Resuming a Blocked Plan

When the orchestrator detects a blocked plan whose blocking condition is resolved:

1. Clear the `blocked_by` field
2. Set `status: in_progress`
3. Continue with the next unchecked step

## Integration Points

- **Called by:** `/email-assistant` (complex email workflows), direct user request, orchestrator (for complex Needs_Action items)
- **Calls:** Any skill needed by individual steps — `/email-drafter`, `/approval-request`, `/linkedin-content`, etc.
- **Monitored by:** `orchestrator.py` (`_check_active_plans()`)
- **Dashboard:** Active plans shown in `Dashboard.md` with progress bars

## Important Rules

1. **One step at a time.** Never execute multiple steps in parallel. Sequential execution ensures auditability.
2. **Update the file after every step.** The Plan.md is the source of truth — keep it current.
3. **Never skip approval-gated steps.** If a step requires approval, block and wait.
4. **Plans are not pre-approval.** Creating a plan doesn't pre-approve any actions within it. Each outbound step still goes through `/approval-request`.
5. **Keep steps atomic.** Each step should be a single, clear action. "Draft and send email" should be two steps: "Draft email" and "Send email (requires approval)".
6. **Maximum 10 steps per plan.** If a task needs more, break it into multiple sequential plans.
