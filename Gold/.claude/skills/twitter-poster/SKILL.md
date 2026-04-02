# Skill: Twitter/X Poster

## Description

Orchestrates the full Twitter posting flow: content generation → HITL approval → API v2 posting via `scripts/twitter_poster.py`. Single entry point for all Twitter/X publishing.

## When to Use

Invoke `/twitter-poster` when:

- The manager says "post to Twitter", "tweet this", "publish a thread"
- A scheduled tweet is due
- The manager has content ready for Twitter/X

**Do NOT use this skill for just generating content.** If the manager only wants a draft, use `/twitter-content` directly.

## Workflow

### Step 1: Generate Content
1. Invoke `/twitter-content` with the provided topic and parameters
2. Present the generated tweet/thread to the manager for review
3. If the manager edits the content, use the edited version

### Step 2: Request Approval
1. Invoke `/approval-request` with:
   - `action_type: tweet`
   - `description: "Tweet: <topic>"` or `"Thread: <topic> (<N> tweets)"`
   - `proposed_content: <full tweet text or all thread tweets>`
   - `risk_level: high`
2. The approval file is created in `/Pending_Approval/`
3. **STOP and wait** — do not proceed until the file appears in `/Approved/`

### Step 3: Execute Posting (After Approval)
1. Verify the approved content in `/Approved/`
2. Invoke `scripts/twitter_poster.py`:

   **Single tweet:**
   ```bash
   cd scripts
   uv run python twitter_poster.py --content "<tweet_text>"
   ```

   **Thread:**
   ```bash
   cd scripts
   uv run python twitter_poster.py --thread "Tweet 1|||Tweet 2|||Tweet 3"
   ```

3. For testing:
   ```bash
   uv run python twitter_poster.py --dry-run --content "Test"
   ```

### Step 4: Confirm and Log
1. Verify the script's JSON output for success/failure
2. Log the action to `/Logs/` with `action_type: tweet`
3. Update `Dashboard.md` Social Media Activity section
4. Move the approval file to `/Done/`

## Prerequisites

### One-Time Setup: OAuth 2.0 Authorization
```bash
cd scripts
uv run python twitter_auth.py
```
This opens a browser for Twitter authorization. The session is saved locally.

### Auth Health Check
```bash
cd scripts
uv run python twitter_poster.py --check-auth
```

### Environment Variables (set by user)
```
TWITTER_CLIENT_ID=<oauth 2.0 client id>
TWITTER_CLIENT_SECRET=<oauth 2.0 client secret>
TWITTER_BEARER_TOKEN=<bearer token for read operations>
```

## Integration Points

- **Calls:** `/twitter-content` (content generation), `/approval-request` (HITL gate)
- **Executes:** `scripts/twitter_poster.py` (API v2)
- **Logged to:** `/Logs/` with `action_type: tweet`
- **Dashboard:** Updates Social Media Activity table

## Important Rules

1. **Always go through approval.** No tweet is published without manager sign-off.
2. **280 character limit.** Verify content length before posting.
3. **Thread maximum: 10 tweets.** Don't create longer threads.
4. **Check auth before posting.** If `twitter_poster.py` fails, run `--check-auth`.
5. **Rate limits.** Free tier: 1,500 tweets/month. Track usage.
6. **Log everything.** Success, failure, dry-run — all go to audit log.
7. **Content is final after approval.** Don't modify approved content before posting.
