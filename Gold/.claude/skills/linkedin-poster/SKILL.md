# Skill: LinkedIn Poster

## Description

Orchestrates the full LinkedIn posting flow: content generation → HITL approval → Playwright-based automated posting. This is the single entry point for all LinkedIn publishing — it coordinates `/linkedin-content` for content, `/approval-request` for HITL review, and `scripts/linkedin_poster.py` for browser-based posting.

## When to Use

Invoke `/linkedin-poster` when:

- The manager says "post to LinkedIn", "publish on LinkedIn", "share on LinkedIn"
- A scheduled post is due (from content calendar or cron)
- The manager has content ready and wants it posted

**Do NOT use this skill for just generating content.** If the manager only wants a draft, use `/linkedin-content` directly.

## Workflow

### Step 1: Generate Content
1. Invoke `/linkedin-content` with the provided topic and parameters
2. Present the generated post to the manager for review
3. If the manager edits the content, use the edited version

### Step 2: Request Approval
1. Invoke `/approval-request` with:
   - `action_type: linkedin_post`
   - `description: "LinkedIn post: <topic>"`
   - `proposed_content: <full post text>`
   - `risk_level: high`
2. The approval file is created in `/Pending_Approval/`
3. **STOP and wait** — do not proceed until the file appears in `/Approved/`

### Step 3: Execute Posting (After Approval)
1. Verify the approved content in `/Approved/`
2. Invoke `scripts/linkedin_poster.py` with the approved content:
   ```bash
   cd scripts
   uv run python linkedin_poster.py --content "<post_text>"
   ```
3. For testing, use dry-run mode:
   ```bash
   uv run python linkedin_poster.py --content "<post_text>" --dry-run
   ```

### Step 4: Confirm and Log
1. Verify the script's JSON output for success/failure
2. Log the action to `/Logs/` with `action_type: linkedin_post`
3. Update `Dashboard.md` LinkedIn Activity section
4. Move the approval file to `/Done/`

## Prerequisites

### One-Time Setup
Before first use, the manager must run the LinkedIn login setup:

```bash
cd scripts
uv run python linkedin_setup.py
```

This opens a visible browser window where the manager logs into LinkedIn manually. The session is saved locally for reuse.

### Session Expired
If the Playwright script fails with a session error:
1. Notify the manager that LinkedIn session has expired
2. Ask them to re-run `linkedin_setup.py`
3. Do NOT attempt to log in automatically

## Integration Points

- **Calls:** `/linkedin-content` (content generation), `/approval-request` (HITL gate)
- **Executes:** `scripts/linkedin_poster.py` (Playwright automation)
- **Logged to:** `/Logs/` with `action_type: linkedin_post`
- **Dashboard:** Updates LinkedIn Activity table

## Important Rules

1. **Always go through approval.** No LinkedIn post is published without manager sign-off.
2. **Never auto-login.** Session setup is always manual.
3. **One post at a time.** Don't queue multiple posts in one execution.
4. **Check session first.** If `linkedin_poster.py` fails, check if session is valid before retrying.
5. **Log everything.** Success, failure, dry-run — all go to audit log.
6. **Content is final after approval.** Don't modify approved content before posting.
