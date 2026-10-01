# HR Employee Assistant (Dust) – from 100 use cases to a working POC

## Problem
Employees ask HR the same questions again and again (leave, onboarding, policies, tools, benefits). HR spends time on answers that already exist in documents.

## What I did
1. **Discovery:** collected and documented about **100 HR use cases** in Confluence and an Excel backlog, grouped by theme and ranked by value and feasibility.
2. **Knowledge base:** structured the HR content in Confluence as the single source of truth (clear pages, one topic per page, owner and last-update date).
3. **4 proofs of concept (POC)** to compare approaches:
   | POC | Stack | Finding |
   |---|---|---|
   | 1 | Gemini Gem | Quick to build, but limited knowledge feed and Slack integration |
   | 2 | Dust + Confluence knowledge | **Best result**: reliable answers from the knowledge base, Slack access |
   | 3 | Zapier automation | Good for triggers and routing, not for answering questions |
   | 4 | Slack integration | Where employees actually ask, so adoption is easiest |
4. **Selected Dust** and connected it to Slack so employees ask in the tool they already use.

## Architecture
```
Confluence (HR knowledge)  ->  Dust assistant  ->  Slack (employee question / answer)
                                     |
                                     -> "I can't answer this, please contact HR" (escalation)
```

## Guardrails
- Answers only from the knowledge base; no invention.
- Sensitive topics (salary, disputes, health, personal data) are redirected to HR.
- No personal employee data in the knowledge base.

## Evaluation
- Test set: **[N] questions** covering the main themes, run against each POC.
- Result: **[X]% correct answers** for the selected POC (fill in your real figure; if you did not measure it, say "qualitative testing").
- Hours saved / questions deflected: **[X]** (only if measured or estimated; label estimates as estimates).

## Adoption
User guide, short demo, feedback loop with HR, monthly review of unanswered questions to improve the knowledge base.

## Lessons learned
- The quality of the knowledge base matters more than the choice of tool.
- Put the assistant where people already work (Slack).
- Start with the highest-volume, lowest-risk questions.
