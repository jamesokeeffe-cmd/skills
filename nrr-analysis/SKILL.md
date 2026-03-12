---
name: nrr-analysis
description: Calculate Net Revenue Retention (NRR) by brand from CSV data. Analyzes expansion vs new business revenue, identifies churn, and generates CS team summary reports.
argument-hint: <csv-file-path> [--fy-year YYYY] [--start-period YYYY-MM] [--end-period YYYY-MM]
user-invocable: true
disable-model-invocation: false
allowed-tools: Bash(python3 *), Read, Write
---

# NRR Analysis Skill

Automatically analyze Net Revenue Retention from CSV data and generate comprehensive reports.

## Usage

Invoke with: `/nrr-analysis /path/to/data.csv`

Optional flags:
- `--fy-year YYYY`: Analyze specific financial year (e.g., 2025 for FY25: Apr 2025 - Mar 2026)
- `--start-period YYYY-MM`: Specify custom start period (e.g., 2025-04)
- `--end-period YYYY-MM`: Specify custom end period (e.g., 2026-01)

## What This Skill Does

1. **Validates CSV file** - Checks file exists and has required columns
2. **Detects financial year periods** - Identifies available FY data (April-March)
3. **Calculates NRR** - Compares start of FY to latest complete month in FY by brand
4. **Identifies segments**:
   - Expansion revenue (existing brands growing)
   - New business (brands added in period)
   - Churned brands (brands lost in period)
5. **Generates markdown report**:
   - Saves to ~/Documents/NRR_Reports/NRR_Analysis_<timestamp>.md
   - Comprehensive CS team summary with insights and recommendations

## Expected CSV Format

Required columns:
- `Account`: Brand/customer name (brand extracted from text before " - ")
- `ARR (converted)`: Annual recurring revenue (format: £X,XXX.XX)
- `Date`: Transaction date (format: M/D/YYYY)

## Workflow

1. Ensure output directory exists: `mkdir -p ~/Documents/NRR_Reports/`
2. Run analysis: `python3 ~/.claude/skills/nrr-analysis/scripts/nrr_analyzer.py "$@" --output-dir ~/Documents/NRR_Reports/`
3. Script generates markdown report directly
4. Display success message with file path to user

## Success Criteria

- Overall portfolio NRR calculated correctly
- Expansion vs new business revenue breakdown shown
- Top performers identified
- Churn analysis included
- Actionable CS recommendations provided
