---
name: email-summarizer
description: This skill summarizes email threads and extracts key information. Use when the user has a long email thread to understand, needs to identify action items, or wants context before replying. Extracts decisions made, action items, and open questions.
---

# Email Summarizer

## Overview

Transform long email threads into actionable summaries with extracted decisions, action items, and context.

## When to Use This Skill

- Email thread has 5+ messages
- Need to quickly understand thread state
- Preparing to reply to a thread
- Extracting action items from discussions
- Creating meeting notes from email exchanges
- Briefing someone on thread status

## Extraction Targets

### 1. Decisions Made

Explicit agreements or conclusions:
- Who decided what
- When it was decided
- Any conditions attached

### 2. Action Items

Tasks assigned to specific people:
- WHO is responsible
- WHAT they need to do
- WHEN it's due (if stated)

### 3. Open Questions

Unresolved items needing response:
- Questions asked but not answered
- Items waiting for input
- Blockers mentioned

### 4. Key Context

Background for response:
- Current state of discussion
- Positions of key stakeholders
- Recent developments

## Output Formats

### Executive Summary (Default)

Quick overview for busy professionals:
- 3-5 sentence summary
- Top 3 action items
- Immediate next step

### Detailed Breakdown

For complex threads:
- Decision log with timestamps
- Full action item list with owners
- Open questions with context
- Stakeholder positions

### Response Context

When preparing to reply:
- What the thread is asking of you
- Your pending action items
- Key points to address

## Workflow

1. Parse thread structure (identify messages and senders)
2. Identify participants and their roles
3. Extract decisions chronologically
4. Extract action items with ownership
5. Identify open questions
6. Format based on user need
7. Offer to chain with /email-drafter for response

## Integration with Other Skills

- Chains with `/email-drafter` for response generation
- Uses tone from `email-drafter/references/tone-guidelines.md`
- Can feed `/email-templates` for structured replies