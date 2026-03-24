# Extraction Patterns for Email Analysis

## Decision Signals

Look for these patterns indicating a decision:

- "We've decided to..."
- "Let's go with..."
- "Agreed - we'll..."
- "Final decision:"
- "Confirmed:"
- "Approved by..."
- "Sign-off received"
- "Moving forward with..."
- "After discussion, we'll..."
- "Consensus is..."

## Action Item Signals

Patterns indicating tasks:

- "Can you please..."
- "I'll take care of..."
- "[Name] will..."
- "Action item:"
- "TODO:"
- "Next step:"
- "By [date], we need..."
- "Your action:"
- "Please send..."
- "Make sure to..."
- "Don't forget to..."

## Question Patterns

Unresolved items:

- Lines ending with "?"
- "What do you think about..."
- "Need input on..."
- "Waiting for..."
- "TBD:"
- "Open question:"
- "Has anyone..."
- "Can someone clarify..."
- "Does anyone know..."
- "Should we..."

## Thread Structure Markers

Identify message boundaries:

- "On [date], [name] wrote:"
- "From: / To: / Subject:"
- "---------- Forwarded message"
- "Begin forwarded message:"
- Timestamp patterns (various formats)
- Quote markers (> at line start)
- Horizontal separator lines

## Participant Roles

Identify key players:

- **Original sender** (initiator) - started the thread
- **Decision makers** (approvers) - can authorize
- **Subject matter experts** (info providers) - provide data
- **Blockers** (waiting on input) - thread stalls on them
- **FYI recipients** (CC'd) - informed but not active

## Urgency Indicators

Signals requiring immediate attention:

- "URGENT:" or "ASAP"
- "EOD" or "End of day"
- "Before [meeting/deadline]"
- "Blocking [something]"
- Exclamation marks (multiple)
- ALL CAPS sections
- "Critical" or "Priority"

## De-Prioritization Signals

Safe to defer:

- "When you get a chance..."
- "No rush, but..."
- "Low priority"
- "FYI only"
- "For your awareness"