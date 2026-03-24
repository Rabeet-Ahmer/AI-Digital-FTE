# Skill: LinkedIn Content Generator

## Description

Generates professional LinkedIn post content for the manager's profile. Covers business updates, thought leadership, industry insights, company milestones, and professional development topics. All content follows brand voice guidelines and is structured for maximum engagement.

## When to Use

Invoke `/linkedin-content` when:

- The manager requests LinkedIn post content
- A scheduled content calendar triggers content generation
- `/linkedin-poster` delegates content creation
- The manager says "write a LinkedIn post", "create social content", "draft something for LinkedIn"

**This skill generates content only — it does NOT post.** For the full posting flow, use `/linkedin-poster`.

## Input

1. **topic** — What the post is about (e.g., "Q1 results", "new hire announcement", "industry trend")
2. **post_type** — One of: `business_update`, `thought_leadership`, `industry_insight`, `milestone`, `hiring`, `event`
3. **key_points** (optional) — Specific points to include
4. **tone_override** (optional) — Override default tone (e.g., "more casual", "celebratory")
5. **cta_type** (optional) — Call-to-action style: `engage` (comment/like), `visit` (link), `connect`, `share`, `none`

## Output

A structured LinkedIn post with:

```markdown
## LinkedIn Post Draft

**Topic:** <topic>
**Type:** <post_type>
**Word Count:** <count>
**Estimated Read Time:** <time>

---

<hook — first 2 lines that appear before "see more">

<body — main content, 3-5 short paragraphs>

<CTA — call to action>

<hashtags — 3-5 relevant hashtags>

---

**Posting Notes:**
- Best posting times: Tue-Thu, 8-10 AM or 12-1 PM
- Preview the first 2 lines carefully — they determine click-through
- Consider tagging relevant people/companies mentioned
```

## Post Structure Rules

### Hook (First 2 Lines)
- Must grab attention immediately — this is what shows before "see more"
- Use one of these patterns:
  - **Bold statement:** "Most companies get [X] wrong. Here's why."
  - **Question:** "What's the one thing that [audience] needs to know about [topic]?"
  - **Statistic:** "We [achieved X] in [timeframe]. Here's what we learned."
  - **Contrarian:** "Unpopular opinion: [claim]"
  - **Story opener:** "Last week, something happened that changed how I think about [topic]."

### Body (3-5 Short Paragraphs)
- Short paragraphs (1-3 sentences each)
- Use line breaks between paragraphs (LinkedIn formatting)
- Include specific numbers, examples, or anecdotes — not generic advice
- Write in first person ("I", "we", "our team")
- Avoid jargon unless the audience shares it

### Call to Action
- One clear ask — don't combine multiple CTAs
- Examples: "What's your experience with [topic]? Drop a comment below.", "Link in comments.", "If this resonates, share it with someone who needs to hear it."

### Hashtags
- 3-5 relevant hashtags
- Mix of broad (#Leadership, #Business) and niche (#StartupLife, #AIinBusiness)
- Always include at least one industry-specific hashtag

## Content Length

- **Target:** 150-300 words
- **Minimum:** 100 words (too short lacks substance)
- **Maximum:** 400 words (too long loses engagement)
- **Ideal for engagement:** 200-250 words

## Reference

Always read `references/content-guidelines.md` before generating content for brand voice, topic guidelines, and hashtag strategy.

## Important Rules

1. **Never post directly.** This skill generates content only. Posting goes through `/linkedin-poster` → `/approval-request`.
2. **No controversial content.** Avoid politics, religion, competitor bashing, or divisive opinions.
3. **Authentic voice.** Write as the manager, not as a generic AI. Use their name, their company, their perspective.
4. **No AI disclosure.** Don't mention that the content was AI-generated unless the manager specifically requests it.
5. **One post at a time.** Generate one complete post per invocation.
