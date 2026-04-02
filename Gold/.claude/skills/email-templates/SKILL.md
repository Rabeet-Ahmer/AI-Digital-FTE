---
name: email-templates
description: This skill provides reusable email templates with variable substitution. Use when the user needs to send recurring email types like cold outreach, follow-ups, or meeting requests. Automatically selects appropriate template and fills variables.
---

# Email Templates

## Overview

Reusable email templates with variable substitution for consistent, efficient communication.

## When to Use This Skill

Activate this skill when user needs to:

- Send cold outreach to new contacts
- Follow up on unanswered emails
- Request meetings or calls
- Draft any recurring email type

## Available Templates

### 1. Cold Outreach (`templates/cold-outreach.md`)

For first contact with new connections. Focuses on:

- Personalized hook (why reaching out to THEM)
- Brief credibility (proof you're worth hearing)
- Clear value proposition (what's in it for them)
- Low-friction CTA (easy next step)

### 2. Follow-Up (`templates/follow-up.md`)

For re-engaging after no response. Focuses on:

- Non-accusatory reference to previous message
- New value addition (not just "checking in")
- Easier response options

### 3. Meeting Request (`templates/meeting-request.md`)

For scheduling calls or meetings. Focuses on:

- Clear context (why meeting makes sense)
- Specific agenda (what you'll discuss)
- Multiple time options (respect their calendar)

## Variable Syntax

Templates use `{{variable_name}}` syntax:

| Variable             | Description              |
| -------------------- | ------------------------ |
| `{{recipient_name}}` | First name of recipient  |
| `{{company}}`        | Recipient's company name |
| `{{topic}}`          | Email subject matter     |
| `{{sender_name}}`    | Rabeet Ahmer             |

Additional template-specific variables are documented in each template file.

## Workflow

1. **Identify email type** from user request
2. **Load appropriate template** from templates/ directory
3. **Gather variable values** from context or ask user
4. **Substitute variables** into template
5. **Apply tone adjustments** if user has preferences
6. **Present filled template** for review and refinement

## Integration Notes

This skill works well with:

- Gmail MCP for direct sending
- Calendar tools for meeting request coordination
- CRM data for personalization