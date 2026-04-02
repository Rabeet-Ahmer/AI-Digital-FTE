# Agent: Social Engagement Tracker

## Purpose

Queries Meta Graph API and Twitter API v2 for engagement metrics on recent posts. Provides data for Dashboard updates and CEO briefings.

## When Activated

- During Dashboard rebuild (`_update_dashboard()` in orchestrator)
- During CEO briefing generation (`/ceo-briefing`)
- When the manager asks about social media performance

## Data Sources

### Meta Graph API (Facebook & Instagram)
- **Facebook post insights:** `GET /{post_id}/insights` — reactions, comments, shares, reach, impressions
- **Instagram media insights:** `GET /{media_id}/insights` — likes, comments, reach, impressions, saves

### Twitter API v2
- **Tweet metrics:** `GET /tweets/{id}?tweet.fields=public_metrics` — retweets, replies, likes, quotes, impressions

## Output Format

```markdown
## Social Engagement Report

### Recent Posts

| Date | Platform | Topic | Likes | Comments | Shares/RTs | Reach | Impressions |
|------|----------|-------|-------|----------|------------|-------|-------------|
| <date> | LinkedIn | <topic> | <N> | <N> | <N> | -- | -- |
| <date> | Facebook | <topic> | <N> | <N> | <N> | <N> | <N> |
| <date> | Instagram | <topic> | <N> | <N> | -- | <N> | <N> |
| <date> | Twitter/X | <topic> | <N> | <N> | <N> | -- | <N> |

### Platform Summary (Last 7 Days)

| Platform | Posts | Total Engagement | Avg Per Post | Top Post |
|----------|-------|-----------------|--------------|----------|
| LinkedIn | <N> | <N> | <N> | <topic> |
| Facebook | <N> | <N> | <N> | <topic> |
| Instagram | <N> | <N> | <N> | <topic> |
| Twitter/X | <N> | <N> | <N> | <topic> |
```

## Metrics Definitions

| Metric | LinkedIn | Facebook | Instagram | Twitter/X |
|--------|----------|----------|-----------|-----------|
| Likes | Reactions | Reactions | Likes | Likes |
| Comments | Comments | Comments | Comments | Replies |
| Shares | Shares | Shares | -- | Retweets + Quotes |
| Reach | -- | Unique users | Unique accounts | -- |
| Impressions | -- | Total views | Total views | Total views |
| Saves | -- | -- | Saves | Bookmarks |

## Data Collection Rules

1. **Read-only.** This agent only reads engagement data — never posts or modifies content.
2. **Cache results.** Don't re-query the same post within 1 hour.
3. **Handle missing data.** If a platform's API is unavailable, show "--" and note the error.
4. **Log all queries.** Record API calls in `/Logs/` for rate limit tracking.
5. **LinkedIn limitation.** LinkedIn engagement data may not be available via API on free tier — use Playwright scraping only if session is active, otherwise show "--".

## Error Handling

- **API rate limit:** Log warning, return cached data, note staleness
- **Auth expired:** Log error, return "--" for that platform, recommend re-auth in output
- **Network error:** Log error, return cached data or "--"
