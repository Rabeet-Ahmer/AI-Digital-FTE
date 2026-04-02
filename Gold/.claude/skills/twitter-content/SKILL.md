# Skill: Twitter/X Content Generator

## Description

Generates tweets and tweet threads for Twitter/X. Handles the 280-character limit per tweet and structures threads of 2-10 tweets for longer-form content.

## When to Use

Invoke `/twitter-content` when:

- The manager requests Twitter content
- `/twitter-poster` delegates content creation
- A scheduled social media calendar triggers content generation
- The manager says "write a tweet", "create a thread", "draft Twitter content"

**This skill generates content only — it does NOT post.** For the full posting flow, use `/twitter-poster`.

## Input

1. **topic** — What the tweet/thread is about
2. **format** — `single` (one tweet, 280 chars) or `thread` (2-10 chained tweets)
3. **key_points** (optional) — Specific points to include
4. **tone_override** (optional) — Override default tone
5. **include_link** (optional) — URL to include in tweet

## Output

### Single Tweet

```markdown
## Tweet Draft

**Topic:** <topic>
**Characters:** <count>/280

---

<tweet text — max 280 characters>

---

**Posting Notes:**
- Character count includes URLs (counted as 23 chars by Twitter)
- Best times: Tue-Thu, 9 AM or 12 PM
- Consider a follow-up tweet if engagement is high
```

### Thread

```markdown
## Thread Draft

**Topic:** <topic>
**Tweets:** <count> (2-10)

---

**1/** <tweet 1 — hook, max 280 chars>

**2/** <tweet 2 — first point>

**3/** <tweet 3 — second point>

...

**N/** <final tweet — CTA + hashtags>

---

**Thread Notes:**
- First tweet is the hook — it must stand alone in the timeline
- Number tweets (1/N, 2/N, etc.) for navigation
- Last tweet should include CTA and 2-3 hashtags
- Keep individual tweets self-contained where possible
```

## Tweet Structure Rules

### Single Tweet (280 chars)
- **Lead with value** — no warmup, get to the point immediately
- **One idea per tweet** — clarity over comprehensiveness
- **CTA optional** — "Agree?", "Reply with yours", "RT if you relate"
- **Hashtags:** 1-2 max, placed at end
- **URLs count as 23 characters** regardless of actual length

### Thread (2-10 tweets)
- **Tweet 1 (Hook):** Must grab attention and stand alone — this is what appears in the timeline
- **Body tweets:** One idea/point per tweet, numbered (1/N format)
- **Last tweet:** Summary + CTA + 2-3 hashtags
- **Each tweet must be ≤280 characters**
- **Self-contained:** Each tweet should make sense even if read alone

## Content Patterns

### Strong Tweet Formats
| Format | Example |
|--------|---------|
| Hot take | "Unpopular opinion: <take>" |
| Listicle | "5 things I learned about <topic>:" (→ thread) |
| Before/After | "Before: <old way>. After: <new way>. The difference: <insight>" |
| Question | "<Provocative question>?" |
| Stat + insight | "<Number>. That's how many <things>. Here's why it matters:" |
| Contrarian | "Everyone says <X>. But actually, <Y>." |

### Thread Formats
| Format | Structure |
|--------|-----------|
| Lessons | Hook → Lesson 1 → ... → Lesson N → Summary |
| Story | Hook → Setup → Conflict → Resolution → Takeaway |
| How-to | Hook → Step 1 → ... → Step N → Resources |
| Analysis | Hook → Observation → Data → Insight → Prediction |

## Reference

Always read `references/twitter-content-guidelines.md` before generating content.

## Important Rules

1. **280 character hard limit.** Count carefully. Every character matters.
2. **Never post directly.** Content only — posting goes through `/twitter-poster` → `/approval-request`.
3. **Threads: 2-10 tweets.** Don't create threads longer than 10 tweets.
4. **No controversial content.** Same rules as other platforms.
5. **One piece of content per invocation.** Either one tweet or one thread.
