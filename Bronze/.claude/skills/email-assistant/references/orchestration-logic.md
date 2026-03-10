# Orchestration Logic for Email Assistant

## Component Selection Matrix


| User Request Pattern         | Primary Component  | Supporting Components       |
| ---------------------------- | ------------------ | --------------------------- |
| "Write an email"             | email-drafter      | email-templates, Gmail MCP  |
| "Use the follow-up template" | email-templates    | email-drafter, Gmail MCP    |
| "Summarize this thread"      | email-summarizer   | -                           |
| "Triage my inbox"            | inbox-triager      | email-summarizer, Gmail MCP |
| "Suggest a response"         | response-suggester | email-drafter               |
| "What needs follow-up?"      | follow-up-tracker  | email-templates, Gmail MCP  |
| "Help me manage email"       | ORCHESTRATOR       | ALL components              |


## Workflow Sequencing

### Sequential Dependencies

Tasks that must complete before the next can begin:

1. **Triage BEFORE Suggest** — Need priority context before generating response options
2. **Summarize BEFORE Respond** — Need thread context before drafting reply
3. **Draft BEFORE Send** — Need email content before sending

### Parallel Opportunities

Tasks that can run simultaneously:

- Triage multiple email batches in parallel
- Draft multiple responses while user reviews first
- Track follow-ups while composing new emails

## State Management

### Session State

Information maintained during active session:

- Current inbox snapshot (from last triage)
- Active drafts pending review
- Follow-up queue with deadlines

### Persistent State

Information stored in skill references:

- Tone guidelines (in email-drafter/references/)
- Templates (in email-templates/templates/)
- Priority contact list (in inbox-triager configuration)

## Offline Mode Workflow

When Gmail MCP is unavailable:

1. **Skill invocation works normally** — All content generation functions
2. **Subagent analysis works with provided data** — User can paste email content
3. **Output format changes**:
  - Email content copied to clipboard
  - Manual instructions provided
  - User notified of offline status

## Quality Gates

Before any email is sent:

1. Tone matches guidelines
2. Template variables fully substituted (no {{placeholders}} remaining)
3. Recipient address verified
4. Draft reviewed if importance level high
5. User confirmed send action explicitly

