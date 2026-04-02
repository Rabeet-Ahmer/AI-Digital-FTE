# Skill: CEO Weekly Briefing

## Description

Generates a weekly executive briefing summarizing all AI Employee activity for the past 7 days. Reviews completed tasks, pending approvals, active plans, email activity, multi-platform social media posts, and Odoo financial data to give the manager a comprehensive status update.

## When to Use

Invoke `/ceo-briefing` when:

- Monday morning cron trigger (`scripts/weekly_briefing.sh`)
- The manager asks "what happened this week?", "weekly summary", "briefing", "status report"
- End of week review is requested

## Input

No explicit input required — the skill reads from vault folders and external systems:

- `/Done/` — completed items from the past 7 days
- `/Logs/` — JSON action logs for the past 7 days
- `/Needs_Action/` — items still pending
- `/Pending_Approval/` — approvals awaiting decision
- `/Plans/` — active and completed plans
- `/Rejected/` — rejected items (to note what was declined)
- **Odoo ERP** — via `/odoo-reports` for financial summary (if connected)

## Output

A briefing file placed in `/Plans/`:

### File Naming
```
BRIEFING_weekly_YYYY-MM-DD.md
```

### Structure

```markdown
---
type: briefing
period: "YYYY-MM-DD to YYYY-MM-DD"
generated_at: <ISO timestamp>
---

# Weekly Briefing — Week of <date>

## Executive Summary

<2-3 sentence overview of the week's activity>

## Key Metrics

| Metric | This Week | Previous Week | Trend |
|--------|-----------|---------------|-------|
| Items Processed | <N> | <N> | <up/down/flat> |
| Emails Handled | <N> | -- | -- |
| Approvals Processed | <N> | -- | -- |
| Social Media Posts | <N> | -- | -- |
| Plans Completed | <N> | -- | -- |

## Social Media Activity

| Date | Platform | Topic | Status | Engagement |
|------|----------|-------|--------|------------|
| <date> | LinkedIn | <topic> | Published | <metrics> |
| <date> | Facebook | <topic> | Published | <metrics> |
| <date> | Instagram | <topic> | Published | <metrics> |
| <date> | Twitter/X | <topic> | Published | <metrics> |

**Summary:** <N> posts across <N> platforms. Top performer: <platform> — <engagement>.

## Financial Summary (Odoo)

| Metric | Amount |
|--------|--------|
| Total Outstanding AR | $X,XXX |
| Overdue AR (>30 days) | $X,XXX |
| Payments Received (This Week) | $X,XXX |
| New Invoices Created | X |
| Expenses Submitted | $X,XXX |

*If Odoo is not connected, this section shows "Odoo ERP not connected — run scripts/docker/odoo-setup.sh"*

## Completed Items

| Item | Type | Priority | Completed |
|------|------|----------|-----------|
| <file> | <type> | <priority> | <date> |

## Pending Items

### Needs Action (<N> items)
| Item | Priority | Age |
|------|----------|-----|
| <file> | <priority> | <days> |

### Pending Approval (<N> items)
| Item | Action Type | Risk | Age |
|------|------------|------|-----|
| <file> | <type> | <risk> | <hours/days> |

## Active Plans

| Plan | Status | Progress |
|------|--------|----------|
| <plan> | <status> | <N/M steps> |

## API Rate Limits

| Service | Used | Limit | Remaining |
|---------|------|-------|-----------|
| Twitter/X | <N>/1,500 monthly | 1,500 | <N> |
| Meta Graph API | <N> calls this hour | 200/hr | <N> |

## Highlights

- <Notable achievement or event>
- <Important decision or outcome>
- <Pattern or trend worth noting>

## Recommendations

- <Suggested action based on this week's data>
- <Process improvement opportunity>
- <Items that need manager attention>

## Next Week Outlook

- <Scheduled tasks>
- <Expected incoming work>
- <Items carrying over>
- <Token/auth renewals needed>
```

## Generation Process

1. **Gather data:** Read Done/ files from the past 7 days (by file modification time or frontmatter date)
2. **Parse logs:** Read Logs/YYYY-MM-DD.json for each of the past 7 days, aggregate action counts
3. **Check pending:** Count and list items in Needs_Action/ and Pending_Approval/
4. **Review plans:** Check Plans/ for active, completed, and blocked plans
5. **Check rejected:** Note any items in Rejected/ (patterns in what gets rejected are valuable)
6. **Social media:** Extract linkedin_post, meta_post, and tweet entries from logs
7. **Financial data:** Invoke `/odoo-reports` for Financial Summary (skip if Odoo not connected)
8. **Rate limits:** Check Twitter monthly usage and Meta token expiry
9. **Synthesize:** Write the briefing with metrics, highlights, and recommendations
10. **Save:** Write to `Plans/BRIEFING_weekly_YYYY-MM-DD.md`
11. **Log:** Record `action_type: briefing` in today's log

## Important Rules

1. **Data-driven, not speculative.** Only report on actual data found in the vault. Don't fabricate metrics.
2. **Highlight anomalies.** If something is unusual (spike in errors, stale approvals, empty week), call it out.
3. **Actionable recommendations.** Don't just report — suggest what the manager should do about it.
4. **Keep it scannable.** Tables, bullet points, clear headers. The manager should get the gist in 30 seconds.
5. **Previous week comparison.** If previous week's briefing exists, compare metrics for trend analysis.
6. **Financial section optional.** If Odoo is not connected, note it and skip — don't error.
7. **Token/auth alerts.** Flag any upcoming expirations (Meta token, Twitter auth) in Recommendations.
