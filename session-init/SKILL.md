---
name: session-init
description: Initialize a coding session by generating a "State of the Union" report. Analyzes PRD vs code alignment, git history, previous session logs, and recommends session goals. Use at the start of any coding session.
argument-hint: [path-to-prd]
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# Session Initializer & Context Architect

You are initializing a new development session. Your goal is to synthesize the project roadmap, historical progress, and recent activity into a clear, actionable "State of the Union" report.

## Context Gathering

First, gather the following information:

### 1. Git State (Automatic)
**Current Branch:** !`git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "Not a git repo"`
**Uncommitted Changes:**
!`git status --short 2>/dev/null | head -20 || echo "N/A"`

**Recent Commits (last 10):**
!`git log --oneline -10 2>/dev/null || echo "No commits found"`

**Files Changed in Last Commit:**
!`git diff-tree --no-commit-id --name-only -r HEAD 2>/dev/null | head -15 || echo "N/A"`

### 2. Documents to Locate
Search for and read (if they exist):
- **PRD/Requirements:** Look for `PRD.md`, `REQUIREMENTS.md`, `docs/prd*`, `docs/requirements*`, or similar
- **Session Logs:** Look for `SESSION_LOG.md`, `PROGRESS.md`, `docs/sessions/*`, or similar
- **Project Instructions:** `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`

If `$ARGUMENTS` is provided, use it as the path to the PRD document.

## Analysis Workflow

Perform these checks internally:

1. **Alignment Check:** Compare recent commits against PRD/requirements. Are high-priority features from the PRD missing from commits?

2. **Continuity Check:** Analyze session logs. Did the last session end cleanly or with unresolved issues (failing tests, partial implementations, TODOs)?

3. **Drift Detection:** Do recent commits suggest deviation from PRD requirements (scope creep or wrong direction)?

4. **Build Health Check:** Run a quick build/test status check if appropriate for the project:
   - Look for `package.json` (npm/yarn projects)
   - Look for `Gemfile` (Ruby projects)
   - Look for `Cargo.toml` (Rust projects)
   - Look for `go.mod` (Go projects)
   - Check for CI status if available

## Output Format

Generate your report in this exact format:

```markdown
# Session Initialization Report

## 1. Project Status Snapshot
* **Current Phase:** [e.g., MVP Construction, Bug Fixing, Refactoring, Feature Development]
* **Branch:** [current git branch]
* **Last Action:** [Brief summary of the last commit]
* **Health Check:** [Pick one: Stable / Work in Progress / Broken Build / Unknown]
* **Uncommitted Changes:** [Yes/No + brief summary if yes]

## 2. Context Restoration
> *Where we left off mentally.*

* **Recently Completed:**
  - [Item 1 from recent commits/logs]
  - [Item 2]
  - [Item 3]

* **Open Loops:**
  - [Any unclosed tasks, failing tests, or partial implementations]
  - [TODOs mentioned in code or logs]

## 3. Gap Analysis (PRD vs. Code)

* **Pending High-Priority Features:**
  - [ ] [Feature A - brief description]
  - [ ] [Feature B - brief description]

* **Potential Drift:** [Note discrepancies between code direction and PRD, or "None identified"]

* **Technical Debt Noted:**
  - [Any debt items identified]

## 4. Recommended Session Goals

Based on the analysis above:

* **Primary Objective:** [The ONE thing to achieve this session]

* **Secondary Tasks:**
  - [ ] [Task 1]
  - [ ] [Task 2]
  - [ ] [Task 3]

## 5. Entry Point

* **Start Here:** `[specific file path]`
* **Reason:** [Why this is the best starting point]

---
*Report generated at session start. Run `/session-init` again to refresh.*
```

## Important Notes

- If no PRD is found, focus on git history and code structure analysis
- If no session logs exist, note this and recommend creating one
- Be concise but comprehensive
- Prioritize actionable insights over exhaustive listing
- If the project appears to be in a broken state, make fixing it the primary objective
