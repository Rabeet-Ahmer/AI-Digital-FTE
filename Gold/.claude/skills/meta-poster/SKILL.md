# Skill: Meta Poster (Facebook & Instagram)

## Description

Orchestrates the full Meta posting flow: content generation → HITL approval → Graph API posting via `scripts/meta_poster.py`. Single entry point for all Facebook and Instagram publishing.

## When to Use

Invoke `/meta-poster` when:

- The manager says "post to Facebook", "post to Instagram", "share on FB/IG"
- A scheduled social media post is due
- The manager has content ready for Facebook or Instagram

**Do NOT use this skill for just generating content.** If the manager only wants a draft, use `/meta-content` directly.

## Workflow

### Step 1: Generate Content
1. Invoke `/meta-content` with the provided topic, platform, and parameters
2. Present the generated post to the manager for review
3. If the manager edits the content, use the edited version

### Step 2: Request Approval
1. Invoke `/approval-request` with:
   - `action_type: meta_post`
   - `description: "<Platform> post: <topic>"`
   - `proposed_content: <full post text>`
   - `risk_level: high`
   - `metadata:` `platform` (facebook|instagram), `image_url` (if Instagram)
2. The approval file is created in `/Pending_Approval/`
3. **STOP and wait** — do not proceed until the file appears in `/Approved/`

### Step 3: Execute Posting (After Approval)
1. Verify the approved content in `/Approved/`
2. Invoke `scripts/meta_poster.py` with the approved content:

   **Facebook:**
   ```bash
   cd scripts
   uv run python meta_poster.py --content "<post_text>" --platform facebook
   ```

   **Instagram:**
   ```bash
   cd scripts
   uv run python meta_poster.py --content "<caption>" --platform instagram --image-url "<public_url>"
   ```

3. For testing, use dry-run mode:
   ```bash
   uv run python meta_poster.py --content "<text>" --platform facebook --dry-run
   ```

### Step 4: Confirm and Log
1. Verify the script's JSON output for success/failure
2. Log the action to `/Logs/` with `action_type: meta_post`
3. Update `Dashboard.md` Social Media Activity section
4. Move the approval file to `/Done/`

## Prerequisites

### Environment Variables (set by user)
```
META_PAGE_ACCESS_TOKEN=<long-lived page access token>
META_PAGE_ID=<facebook page id>
META_IG_USER_ID=<instagram business account id>
META_APP_ID=<facebook app id>
META_APP_SECRET=<facebook app secret>
```

### Token Health Check
```bash
cd scripts
uv run python meta_poster.py --check-token
```

### Token Refresh (before 60-day expiry)
```bash
cd scripts
uv run python meta_poster.py --refresh-token
```

## Integration Points

- **Calls:** `/meta-content` (content generation), `/approval-request` (HITL gate)
- **Executes:** `scripts/meta_poster.py` (Graph API)
- **Logged to:** `/Logs/` with `action_type: meta_post`
- **Dashboard:** Updates Social Media Activity table

## Important Rules

1. **Always go through approval.** No Meta post is published without manager sign-off.
2. **Instagram requires an image.** Always confirm a public image URL before posting to Instagram.
3. **One post at a time.** Don't queue multiple posts in one execution.
4. **Check token before posting.** If `meta_poster.py` fails with auth error, run `--check-token`.
5. **Log everything.** Success, failure, dry-run — all go to audit log.
6. **Content is final after approval.** Don't modify approved content before posting.
