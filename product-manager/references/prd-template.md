# PRD Template

Use this template when creating Product Requirements Documents. Adapt sections based on feature complexity—simple features need fewer sections.

---

## [Feature Name]

**Author:** [Name]  
**Last Updated:** [Date]  
**Status:** Draft | In Review | Approved | In Development | Shipped

---

## 1. Problem Statement

### The Problem
[2-3 sentences describing the problem. Be specific about who has this problem and when they experience it.]

### Evidence
- [Data point or user feedback supporting the problem]
- [Data point or user feedback supporting the problem]
- [Quantify if possible: "X% of users abandon at this step"]

### Impact of Not Solving
[What happens if we don't address this? Lost revenue, churn risk, competitive disadvantage?]

---

## 2. Goals & Success Metrics

### Primary Goal
[One sentence: What does success look like?]

### Success Metrics

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Primary: [e.g., Conversion rate] | X% | Y% | 30 days post-launch |
| Secondary: [e.g., Time to complete] | X min | Y min | 30 days post-launch |

### Anti-Metrics (Guardrails)
- [Metric we don't want to negatively impact, e.g., "Support ticket volume should not increase >10%"]

---

## 3. User Context

### Target Users
[Who is this for? Be specific—not "all users" but "new users in their first week" or "admin users managing teams >10 people"]

### User Journey
```
[Current state]
1. User does X
2. User encounters problem Y  ← Pain point
3. User works around with Z (or gives up)

[Future state]
1. User does X
2. New feature enables Y seamlessly
3. User achieves goal
```

### Jobs to Be Done
When [situation], I want to [motivation], so I can [expected outcome].

---

## 4. Solution Overview

### Proposed Solution
[2-3 sentences describing the approach at a high level. Focus on the "what" not the "how."]

### Key User Stories

**Story 1: [Title]**
As a [user type], I want to [action], so that [benefit].

Acceptance Criteria:
- [ ] Given [context], when [action], then [result]
- [ ] Given [context], when [action], then [result]
- [ ] Edge case: [description]

**Story 2: [Title]**
As a [user type], I want to [action], so that [benefit].

Acceptance Criteria:
- [ ] Given [context], when [action], then [result]
- [ ] Given [context], when [action], then [result]

[Add more stories as needed]

---

## 5. Requirements

### Functional Requirements

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-1 | [Requirement description] | Must Have | |
| FR-2 | [Requirement description] | Must Have | |
| FR-3 | [Requirement description] | Should Have | |
| FR-4 | [Requirement description] | Could Have | |

### Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| Performance | [e.g., Page load <2s, API response <200ms] |
| Security | [e.g., Data encrypted at rest, audit logging] |
| Accessibility | [e.g., WCAG 2.1 AA compliance] |
| Scalability | [e.g., Support 10x current load] |

---

## 6. Scope

### In Scope
- [Specific capability included]
- [Specific capability included]
- [Specific capability included]

### Out of Scope (This Release)
- [Explicitly excluded item] — [reason, e.g., "Phase 2" or "Separate initiative"]
- [Explicitly excluded item] — [reason]

### Dependencies
- [Dependency on other team/feature/system]
- [External dependency, e.g., third-party API]

---

## 7. Design & Technical Considerations

### UX/Design Notes
[Link to designs or describe key UX decisions]

### Technical Considerations
[Notes for engineering: suggested approaches, constraints, risks]

### Data Requirements
- New data to collect: [fields]
- Data migrations needed: [yes/no, details]
- Analytics events to track: [list]

---

## 8. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk description] | High/Med/Low | High/Med/Low | [Mitigation strategy] |
| [Risk description] | High/Med/Low | High/Med/Low | [Mitigation strategy] |

---

## 9. Timeline & Milestones

| Milestone | Target Date | Owner |
|-----------|-------------|-------|
| PRD Approved | [Date] | PM |
| Design Complete | [Date] | Design |
| Development Complete | [Date] | Eng |
| QA Complete | [Date] | QA |
| Launch | [Date] | PM |

---

## 10. Open Questions

- [ ] [Question that needs resolution before/during development]
- [ ] [Question that needs resolution before/during development]

---

## Appendix

### A. Research & References
- [Link to user research]
- [Link to competitive analysis]
- [Link to related documents]

### B. Changelog

| Date | Author | Changes |
|------|--------|---------|
| [Date] | [Name] | Initial draft |
