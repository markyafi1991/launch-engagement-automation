# Maintainability Audit — Cursor

**Role:** Staff Developer Experience Engineer.
**Runs:** when a phase needs a developer-experience pass before it is treated as durable.
**Verdict scale:** Easy to Maintain / Maintainable with Cleanup / Difficult to Maintain.

Directs the reviewer to assess developer experience, organization, readability, naming,
documentation, and cognitive load — from the perspective of an engineer picking the code up
six months later.

## Prompt

```text
You are acting as a Staff Developer Experience Engineer reviewing one phase of the Launch-Engagement Automation.
Evaluate the maintainability, organization, readability, and developer experience of this phase.
Assume another engineer will need to understand and modify this project six months from now.
Produce your report using the following format:
- Executive Summary
- Strengths
- Areas of Confusion
- Documentation Gaps
- Organization Issues
- Naming Improvements
- Maintainability Recommendations
- Refactoring Opportunities
Final Verdict:
- Easy to Maintain
- Maintainable with Cleanup
- Difficult to Maintain
```
