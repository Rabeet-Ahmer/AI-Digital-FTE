# Skill: Meta Content Generator (Facebook & Instagram)

## Description

Generates content for Facebook Page posts and Instagram captions. Adapts format and style per platform while maintaining consistent brand voice.

## When to Use

Invoke `/meta-content` when:

- The manager requests Facebook or Instagram content
- `/meta-poster` delegates content creation
- A scheduled social media calendar triggers content generation
- The manager says "write a Facebook post", "create an Instagram post", "draft social media content"

**This skill generates content only — it does NOT post.** For the full posting flow, use `/meta-poster`.

## Input

1. **topic** — What the post is about
2. **platform** — `facebook` or `instagram`
3. **post_type** — One of: `business_update`, `thought_leadership`, `industry_insight`, `milestone`, `hiring`, `event`, `product`, `behind_the_scenes`
4. **key_points** (optional) — Specific points to include
5. **tone_override** (optional) — Override default tone
6. **image_description** (optional) — For Instagram, describe the image to pair with

## Output

### Facebook Post

```markdown
## Facebook Post Draft

**Topic:** <topic>
**Type:** <post_type>
**Word Count:** <count> (target: 100-500 words)

---

<opening hook — first 2 lines visible in feed>

<body — 2-5 paragraphs, can be longer-form than LinkedIn>

<CTA — call to action>

---

**Posting Notes:**
- Best times: Wed-Fri, 1-4 PM
- Facebook allows longer content — use it for storytelling
- Consider adding a link or image for higher engagement
```

### Instagram Caption

```markdown
## Instagram Caption Draft

**Topic:** <topic>
**Type:** <post_type>
**Caption Length:** <chars> (max: 2200 chars)
**Image Suggestion:** <description of ideal image>

---

<caption — compelling first line (shows before "more")>

<body — 3-5 short paragraphs>

<CTA>

.
.
.
<hashtags — up to 30, separated by spaces>

---

**Posting Notes:**
- First line is critical — appears before "more" tap
- Use line breaks and dots to separate hashtags from caption
- Image must be a public URL for Instagram API posting
```

## Platform-Specific Rules

### Facebook
- **Length:** 100-500 words (longer-form OK, engagement drops after 500)
- **Links:** Can include URLs directly in post body
- **Formatting:** Supports emoji, line breaks, basic formatting
- **Hashtags:** 1-3 max (Facebook hashtags have lower reach than Instagram)
- **Tone:** Slightly more conversational than LinkedIn

### Instagram
- **Caption length:** Up to 2,200 characters
- **Hashtags:** Up to 30 (use 15-25 for optimal reach)
- **Image required:** Every Instagram post needs an image (public URL)
- **First line:** Critical — only ~125 chars show before "more"
- **Hashtag placement:** Separate from caption with line breaks + dots

## Reference

Always read `references/meta-content-guidelines.md` before generating content.

## Important Rules

1. **Never post directly.** Content only — posting goes through `/meta-poster` → `/approval-request`.
2. **Platform-appropriate.** Don't reuse LinkedIn content verbatim — adapt for each platform.
3. **Instagram always needs an image.** If no image URL is available, note this in the output.
4. **No controversial content.** Same rules as LinkedIn — no politics, religion, competitor bashing.
5. **One post at a time.** Generate one complete post per invocation.
