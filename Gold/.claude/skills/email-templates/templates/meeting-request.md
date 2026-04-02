# Meeting Request Template

## Purpose

Schedule time efficiently by demonstrating value upfront. The recipient should know exactly why meeting is worth their time.

## Variables

| Variable             | Description                | Example                                            |
| -------------------- | -------------------------- | -------------------------------------------------- |
| `{{recipient_name}}` | First name                 | "Priya"                                            |
| `{{context}}`        | Why meeting makes sense    | "Based on our Slack thread about rate limiting"    |
| `{{topic}}`          | Meeting subject            | "API integration"                                  |
| `{{duration}}`       | Time commitment            | "30 min"                                           |
| `{{agenda_items}}`   | Specific topics (bulleted) | Review limits, discuss patterns, agree on solution |
| `{{time_options}}`   | 3 specific time slots      | Tuesday 2 PM, Wednesday 10 AM, Thursday 3 PM       |
| `{{sender_name}}`    | Rabeet Ahmer               | "Rabeet Ahmer"                                     |

## Template

Subject: {{duration}} sync on {{topic}} - {{number}} time options

Hi {{recipient_name}},

{{context}}

Proposed agenda ({{duration}}):
{{agenda_items}}

Would any of these work?
{{time_options}}

{{sender_name}}

## Example Filled

**Subject:** 30-min sync on API integration - 3 time options

Hi Ali,

Based on our Slack thread about the rate limiting issue, I think we'd resolve this faster in a quick call.

Proposed agenda (30 min):

- Review current rate limits (5 min)
- Discuss your usage patterns (10 min)
- Agree on solution approach (15 min)

Would any of these work?

- Tuesday 2-2:30 PM EST
- Wednesday 10-10:30 AM EST
- Thursday 3-3:30 PM EST

Alex

## Best Practices

| Practice                     | Why It Works                               |
| ---------------------------- | ------------------------------------------ |
| Include specific agenda      | Shows you've prepared, respects their time |
| Offer 3 time options minimum | Increases chance of fit                    |
| State duration clearly       | Sets expectations, shows respect           |
| Include time zone            | Prevents confusion, especially remote      |
| Time-boxed agenda items      | Demonstrates efficiency                    |

## Anti-Patterns

| Pattern                | Problem                  | Instead                      |
| ---------------------- | ------------------------ | ---------------------------- |
| "Let's hop on a call"  | Vague, no agenda         | Specific purpose with agenda |
| "When are you free?"   | Puts burden on them      | Offer specific times         |
| "Quick sync" (no time) | Unclear commitment       | State exact duration         |
| Back-to-back requests  | Assumes first time works | Offer alternatives upfront   |