---
name: email-assistant
description: Master orchestrator for email workflow automation. Coordinates email-drafter, email-templates, email-summarizer skills with inbox-triager, response-suggester, follow-up-tracker subagents, and Gmail MCP for end-to-end email management.
---

# Email Assistant

## Overview

Your complete Email Digital FTE — orchestrating skills, subagents, and MCP for automated email workflow management. This is the single entry point for all email operations.

## Components Orchestrated

### Skills (Content Generation)

| Skill | Purpose | When to Invoke |
|-------|---------|----------------|
| `/email-drafter` | Professional email composition | User needs custom email with tone control |
| `/email-templates` | Template-based messaging | User needs standard email type (outreach, follow-up, meeting) |
| `/email-summarizer` | Thread analysis | User needs to understand long threads quickly |

### Subagents (Processing & Analysis)

| Subagent | Purpose | When to Invoke |
|----------|---------|----------------|
| `inbox-triager` | Priority classification | User wants inbox organized by importance |
| `response-suggester` | Quick reply options | User needs response ideas for specific email |
| `follow-up-tracker` | Deadline management | User wants to know what needs attention |

### MCP (External Operations)

| Tool Category | Purpose | When to Invoke |
|---------------|---------|----------------|
| Gmail MCP: search_emails | Fetch emails by query | Need real email data |
| Gmail MCP: draft_email | Create Gmail draft | Ready to save draft for review |
| Gmail MCP: send_email | Send email | User confirms send action |

## Workflow Modes

### Mode 1: Inbox Management

**Trigger:** "Help me manage my inbox" or "Triage my email"

**Workflow sequence:**
1. Fetch unread emails (Gmail MCP: search_emails with query "is:unread")
2. Classify by priority (inbox-triager subagent)
3. Summarize important threads (email-summarizer skill)
4. Suggest responses for urgent items (response-suggester subagent)
5. Draft replies for approved suggestions (email-drafter + email-templates skills)
6. Create as Gmail drafts (Gmail MCP: draft_email)

**State after completion:**
- Inbox categorized by priority
- Important threads summarized
- Draft responses ready for review

### Mode 2: Email Composition

**Trigger:** "Write an email to [person] about [topic]"

**Workflow sequence:**
1. Identify email type (cold outreach, follow-up, meeting request, or custom)
2. Select template if applicable (email-templates skill)
3. Draft email with personalization (email-drafter skill)
4. Apply tone guidelines
5. Create draft or send based on user preference (Gmail MCP)

**Decision logic:**
- If email type matches template → Use email-templates first, then email-drafter for personalization
- If email type is custom → Use email-drafter directly
- If user specifies "urgent" or "formal" → Apply appropriate tone modifier

### Mode 3: Thread Response

**Trigger:** "Help me respond to this thread" or "Reply to [email]"

**Workflow sequence:**
1. Fetch thread content (Gmail MCP: get_thread)
2. Summarize thread and extract key points (email-summarizer skill)
3. Identify required action items
4. Generate response options (response-suggester subagent)
5. Draft chosen response (email-drafter skill)
6. Create draft for review (Gmail MCP: draft_email)

**Output:**
- Thread summary with action items
- 3 response options with tone labels
- Draft of user-selected option

### Mode 4: Follow-Up Check

**Trigger:** "What emails need follow-up?" or "Check my pending responses"

**Workflow sequence:**
1. Fetch sent emails from past 7-14 days (Gmail MCP: search_emails)
2. Analyze for awaiting responses (follow-up-tracker subagent)
3. Identify items past response deadline
4. Generate follow-up drafts (email-templates: follow-up template)
5. Create drafts for review (Gmail MCP: draft_email)

**Output:**
- List of emails awaiting response with wait time
- Flagged items past expected response window
- Ready-to-send follow-up drafts

## Delegation Logic

When should you use each component type?

| Task Characteristic | Component Type | Reasoning |
|---------------------|----------------|-----------|
| Content generation with known patterns | **Skills** | Predictable output, consistent application |
| Classification requiring judgment | **Subagents** | Autonomous reasoning, context evaluation |
| External data or actions | **MCP** | System integration, real operations |
| Multi-step coordination | **Orchestrator** | Workflow sequencing, state management |

**Decision tree for component selection:**

Is task about creating content?
├── Yes → Does a template exist?
│   ├── Yes → email-templates skill
│   └── No → email-drafter skill
└── No → Is task about classification/analysis?
    ├── Yes → Use appropriate subagent
    │   ├── Priority classification → inbox-triager
    │   ├── Response suggestions → response-suggester
    │   └── Deadline tracking → follow-up-tracker
    └── No → Is task about external operations?
        ├── Yes → Gmail MCP tools
        └── No → Orchestrator handles directly

## Graceful Degradation

Systems fail. Gmail API goes down. Authentication expires. Network drops. The Email Assistant must continue functioning with reduced capability rather than failing completely.

### If Gmail MCP Unavailable

When Gmail MCP cannot connect:

1. **Skills still work fully**
   - email-drafter produces emails
   - email-templates applies patterns
   - email-summarizer analyzes provided text

2. **Subagents work with provided data**
   - If user pastes email content, subagents can analyze it
   - Cannot fetch new emails automatically

3. **Output changes**
   - Instead of creating Gmail draft → Copy email to clipboard
   - Instead of sending → Provide formatted email for manual paste
   - Clear notification: "Gmail MCP offline. Email copied to clipboard for manual sending."

### If Specific Skill Missing

When a component skill is unavailable:

- Fall back to email-drafter for all composition tasks
- Note which specialized skill would have helped
- Continue workflow with reduced specialization

## Error Handling

1. **MCP connection failed**: Continue with local skills, notify user of reduced capability
2. **Email not found**: Report clearly, suggest alternative search terms
3. **Draft creation failed**: Provide email content for manual use
4. **Authentication expired**: Guide user through re-authentication steps

## Usage Examples

| User Says | Mode Selected | Components Used |
|-----------|---------------|-----------------|
| "Help me with email" | Mode selection menu | (offers all modes) |
| "Triage my inbox" | Mode 1: Inbox Management | Gmail MCP + inbox-triager + email-summarizer |
| "Write a cold outreach" | Mode 2: Composition | email-templates + email-drafter + Gmail MCP |
| "Respond to this thread" | Mode 3: Thread Response | email-summarizer + response-suggester + email-drafter |
| "Check my follow-ups" | Mode 4: Follow-Up Check | Gmail MCP + follow-up-tracker + email-templates |