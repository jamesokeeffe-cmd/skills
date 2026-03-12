#!/usr/bin/env python3
"""
Net Revenue Retention (NRR) Analysis by Brand
Analyzes data by financial year (April-March) and generates comprehensive reports
"""

import csv
import argparse
from datetime import datetime
from collections import defaultdict
from decimal import Decimal
import os
import sys

def get_fy_year(date):
    """Return FY year (year of April start month)"""
    if date.month >= 4:  # April or later
        return date.year
    else:  # Jan-Mar
        return date.year - 1

def parse_arr(arr_str):
    """Parse ARR string, handling currency symbols and commas"""
    arr_str = arr_str.replace('£', '').replace(',', '').strip()
    if not arr_str or arr_str == '-':
        return Decimal('0')
    return Decimal(arr_str)

def format_currency(amount):
    """Format Decimal as currency string"""
    return f"£{amount:,.0f}"

def format_percentage(value):
    """Format Decimal as percentage string"""
    return f"{value:.1f}%"

def load_csv_data(csv_file):
    """Load and parse CSV data, return dict of {(year, month): {brand: arr}}"""
    data = defaultdict(lambda: defaultdict(Decimal))

    with open(csv_file, 'r', encoding='latin-1') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Extract brand name (part before " - ")
            account = row['Account']
            brand = account.split(' - ')[0] if ' - ' in account else account

            # Parse ARR
            arr = parse_arr(row['ARR (converted)'])

            # Parse date (format is M/D/YYYY)
            date = datetime.strptime(row['Date'], '%m/%d/%Y')

            # Store data by period
            period = (date.year, date.month)
            data[period][brand] += arr

    return data

def determine_periods(data, fy_year=None, start_period=None, end_period=None):
    """Determine start and end periods for analysis"""
    periods = sorted(data.keys())

    if start_period and end_period:
        # Custom periods provided
        return start_period, end_period

    if fy_year:
        # Specific FY requested
        start = (fy_year, 4)  # April of FY
        # Find latest period in that FY (up to March of next year)
        fy_periods = [p for p in periods if
                      (p[0] == fy_year and p[1] >= 4) or
                      (p[0] == fy_year + 1 and p[1] <= 3)]
        if not fy_periods:
            raise ValueError(f"No data found for FY{fy_year} (Apr {fy_year} - Mar {fy_year+1})")
        end = max(fy_periods)
        return start, end

    # Auto-detect: Find most recent complete FY
    if not periods:
        raise ValueError("No data found in CSV")

    latest_period = max(periods)
    current_fy = get_fy_year(datetime(latest_period[0], latest_period[1], 1))

    # Start of current FY
    start = (current_fy, 4)

    # Latest period in current FY
    fy_periods = [p for p in periods if
                  (p[0] == current_fy and p[1] >= 4) or
                  (p[0] == current_fy + 1 and p[1] <= 3)]

    if not fy_periods:
        # Try previous FY
        current_fy -= 1
        start = (current_fy, 4)
        fy_periods = [p for p in periods if
                      (p[0] == current_fy and p[1] >= 4) or
                      (p[0] == current_fy + 1 and p[1] <= 3)]

    end = max(fy_periods)
    return start, end

def calculate_nrr(data, start_period, end_period):
    """Calculate NRR metrics between two periods"""
    start_arr = data[start_period]
    end_arr = data[end_period]

    results = []

    # Process brands in end period
    for brand in end_arr:
        end_value = end_arr[brand]

        if brand in start_arr:
            # Existing brand - calculate NRR
            start_value = start_arr[brand]
            if start_value > 0:
                nrr = (end_value / start_value) * 100
                if nrr >= 100:
                    status = "Growth"
                else:
                    status = "Contraction"
            else:
                nrr = Decimal('0')
                status = "N/A"

            results.append({
                'brand': brand,
                'start_arr': start_value,
                'end_arr': end_value,
                'growth': end_value - start_value,
                'nrr': nrr,
                'status': status
            })
        else:
            # New business
            results.append({
                'brand': brand,
                'start_arr': None,
                'end_arr': end_value,
                'growth': end_value,
                'nrr': None,
                'status': "New Business"
            })

    # Process churned brands
    for brand in start_arr:
        if brand not in end_arr:
            results.append({
                'brand': brand,
                'start_arr': start_arr[brand],
                'end_arr': Decimal('0'),
                'growth': -start_arr[brand],
                'nrr': Decimal('0'),
                'status': "Churned"
            })

    return results, start_arr, end_arr

def generate_markdown_report(results, start_arr, end_arr, start_period, end_period, csv_file, output_file):
    """Generate comprehensive markdown report"""

    # Calculate summary metrics
    total_start = sum(start_arr.values())
    total_end = sum(end_arr.values())
    overall_nrr = (total_end / total_start * 100) if total_start > 0 else Decimal('0')
    total_growth = total_end - total_start

    # Segment results
    expansion = [r for r in results if r['status'] == "Growth"]
    contraction = [r for r in results if r['status'] == "Contraction"]
    new_business = [r for r in results if r['status'] == "New Business"]
    churned = [r for r in results if r['status'] == "Churned"]
    flat = [r for r in results if r['status'] not in ["New Business", "Churned"] and r['nrr'] == 100]

    expansion_revenue = sum(r['growth'] for r in expansion)
    new_business_revenue = sum(r['end_arr'] for r in new_business)
    churned_revenue = sum(r['start_arr'] for r in churned)

    # Calculate average NRR for existing brands
    existing_brands = [r for r in results if r['status'] not in ["New Business", "Churned"]]
    existing_nrrs = [r['nrr'] for r in existing_brands if r['nrr'] is not None]
    avg_nrr = sum(existing_nrrs) / len(existing_nrrs) if existing_nrrs else Decimal('0')

    # Calculate GRR (Gross Revenue Retention) - revenue retained without expansion
    retained_revenue = Decimal('0')
    for brand in start_arr:
        if brand in end_arr:
            # Brand retained - count the minimum (excludes expansion)
            retained_revenue += min(start_arr[brand], end_arr[brand])
        # If churned, we add 0 (no retained revenue)

    grr = (retained_revenue / total_start * 100) if total_start > 0 else Decimal('0')

    # Calculate LRR (Logo Retention Rate) - brand retention percentage
    starting_brands = len(start_arr)
    churned_brands = len(churned)
    retained_brands = starting_brands - churned_brands
    lrr = (Decimal(retained_brands) / Decimal(starting_brands) * 100) if starting_brands > 0 else Decimal('0')

    # Calculate period length in months
    start_date = datetime(start_period[0], start_period[1], 1)
    end_date = datetime(end_period[0], end_period[1], 1)
    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

    # Sort expansion by absolute growth
    expansion_sorted = sorted(expansion, key=lambda x: x['growth'], reverse=True)

    # Sort by NRR percentage
    expansion_by_nrr = sorted(expansion, key=lambda x: x['nrr'], reverse=True)

    # Sort new business by ARR
    new_business_sorted = sorted(new_business, key=lambda x: x['end_arr'], reverse=True)

    # Sort churned by lost ARR
    churned_sorted = sorted(churned, key=lambda x: x['start_arr'], reverse=True)

    # Format period labels
    start_label = start_date.strftime("%B %Y")
    end_label = end_date.strftime("%B %Y")

    # Generate report
    lines = []
    lines.append("# Net Revenue Retention (NRR) Analysis")
    lines.append("## Customer Success Team Summary")
    lines.append(f"**Period:** {start_label} → {end_label} ({months} months)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"Our portfolio achieved **{format_percentage(overall_nrr)} NRR** over the {months}-month period, growing from {format_currency(total_start)} to {format_currency(total_end)} in ARR. This {'exceptional' if overall_nrr > 120 else 'solid'} performance was driven by {'both strong expansion from existing customers' if expansion_revenue > new_business_revenue else 'a combination of expansion and new business acquisition'} ({format_currency(expansion_revenue)}) {'and significant new business acquisition' if new_business_revenue > 0 else ''} ({format_currency(new_business_revenue)}), with {'minimal' if churned_revenue < total_start * Decimal('0.05') else 'some'} churn ({format_currency(churned_revenue)}).")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Key Metrics Overview
    lines.append("## Key Metrics Overview")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| **Overall Portfolio NRR** | **{format_percentage(overall_nrr)}** |")
    lines.append(f"| **Total ARR Growth** | **{format_currency(total_growth)}** |")
    lines.append(f"| **Starting ARR ({start_label})** | {format_currency(total_start)} |")
    lines.append(f"| **Ending ARR ({end_label})** | {format_currency(total_end)} |")
    lines.append(f"| **Average NRR (Existing Brands)** | {format_percentage(avg_nrr)} |")
    lines.append(f"| **Gross Revenue Retention (GRR)** | **{format_percentage(grr)}** {'✅' if grr >= 95 else '⚠️'} |")
    lines.append(f"| **Logo Retention Rate (LRR)** | **{format_percentage(lrr)}** {'✅' if lrr >= 90 else '⚠️'} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Retention Health Indicators
    lines.append("## Retention Health Indicators")
    lines.append("")
    lines.append("### Gross Revenue Retention (GRR)")
    lines.append(f"**{format_percentage(grr)}** - Revenue retained from existing customers, excluding expansion")
    lines.append("")
    if grr >= 95:
        lines.append(f"✅ **Excellent**: GRR exceeds the 95% target, indicating strong baseline retention and customer experience automation.")
    else:
        gap = Decimal('95') - grr
        lines.append(f"⚠️ **Below Target**: GRR is {format_percentage(gap)} below the 95% target. Focus on reducing churn and contraction.")

    lines.append("")
    lines.append("### Logo Retention Rate (LRR)")
    lines.append(f"**{format_percentage(lrr)}** - Percentage of brands retained ({retained_brands} of {starting_brands} brands)")
    lines.append("")
    if lrr >= 90:
        lines.append(f"✅ **Excellent**: LRR exceeds the 90% target, indicating strong customer satisfaction and healthy referral pipeline.")
    else:
        gap = Decimal('90') - lrr
        lines.append(f"⚠️ **Below Target**: LRR is {format_percentage(gap)} below the 90% target. Focus on improving customer satisfaction and onboarding.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Revenue Growth Breakdown
    lines.append("## Revenue Growth Breakdown: New Business vs Expansion")
    lines.append("")
    lines.append("### 📊 Growth Composition")
    lines.append("")
    lines.append("| Component | Amount | % of Growth | % of Starting ARR |")
    lines.append("|-----------|--------|-------------|-------------------|")

    expansion_pct_growth = (expansion_revenue / total_growth * 100) if total_growth > 0 else Decimal('0')
    expansion_pct_start = (expansion_revenue / total_start * 100) if total_start > 0 else Decimal('0')
    lines.append(f"| **🟢 Expansion Revenue** | **{format_currency(expansion_revenue)}** | **{format_percentage(expansion_pct_growth)}** | **+{format_percentage(expansion_pct_start)}** |")

    new_pct_growth = (new_business_revenue / total_growth * 100) if total_growth > 0 else Decimal('0')
    new_pct_start = (new_business_revenue / total_start * 100) if total_start > 0 else Decimal('0')
    lines.append(f"| **🔵 New Business ARR** | **{format_currency(new_business_revenue)}** | **{format_percentage(new_pct_growth)}** | **+{format_percentage(new_pct_start)}** |")

    churn_pct_growth = (churned_revenue / total_growth * 100) if total_growth > 0 else Decimal('0')
    churn_pct_start = (churned_revenue / total_start * 100) if total_start > 0 else Decimal('0')
    lines.append(f"| **🔴 Churned ARR** | **({format_currency(churned_revenue)})** | **({format_percentage(churn_pct_growth)})** | **({format_percentage(churn_pct_start)})** |")

    lines.append(f"| **Net Growth** | **{format_currency(total_growth)}** | **100.0%** | **+{format_percentage(total_growth / total_start * 100 if total_start > 0 else 0)}** |")
    lines.append("")

    lines.append("### Key Insight: Expansion Drives Growth")
    if expansion_revenue > new_business_revenue:
        ratio = expansion_revenue / (expansion_revenue + new_business_revenue) * 100 if (expansion_revenue + new_business_revenue) > 0 else 0
        lines.append(f"**{format_percentage(ratio).replace('.0', '')} of our ARR growth came from existing customers expanding their usage**, demonstrating strong product-market fit and effective customer success engagement. New business contributed the remaining {'third' if ratio >= 60 and ratio < 70 else 'portion'}, showing healthy acquisition alongside retention.")
    else:
        lines.append("**Growth was driven by a mix of new business acquisition and customer expansion**, showing strong market traction and customer success engagement.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Portfolio Composition
    lines.append("## Portfolio Composition")
    lines.append("")
    lines.append("### Brand Count Movement")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Starting Brands ({start_label}) | {len(start_arr)} |")
    lines.append(f"| Brands Added | +{len(new_business)} |")
    lines.append(f"| Brands Churned | -{len(churned)} |")
    lines.append(f"| **Ending Brands ({end_label})** | **{len(end_arr)}** |")
    net_brand_growth = len(end_arr) - len(start_arr)
    net_brand_pct = (net_brand_growth / len(start_arr) * 100) if len(start_arr) > 0 else Decimal('0')
    lines.append(f"| **Net Brand Growth** | **{'+' if net_brand_growth >= 0 else ''}{net_brand_growth} ({'+' if net_brand_pct >= 0 else ''}{format_percentage(net_brand_pct)})** |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Expansion Revenue Analysis
    lines.append("## Expansion Revenue Analysis")
    lines.append("")
    lines.append("### Top 10 Expansion Winners (Absolute £ Growth)")
    lines.append("")
    lines.append("| Brand | Starting ARR | Ending ARR | Growth | NRR % |")
    lines.append("|-------|--------------|------------|--------|-------|")

    for r in expansion_sorted[:10]:
        lines.append(f"| **{r['brand']}** | {format_currency(r['start_arr'])} | {format_currency(r['end_arr'])} | **{format_currency(r['growth'])}** | {format_percentage(r['nrr'])} |")

    top_10_expansion = sum(r['growth'] for r in expansion_sorted[:10])
    top_10_pct = (top_10_expansion / expansion_revenue * 100) if expansion_revenue > 0 else Decimal('0')
    lines.append("")
    lines.append(f"**These 10 brands contributed {format_currency(top_10_expansion)} ({format_percentage(top_10_pct)}) of total expansion revenue.**")
    lines.append("")

    # Highest NRR Growth Rates
    lines.append("### Highest NRR Growth Rates")
    lines.append("")
    lines.append("| Brand | NRR % | ARR Growth |")
    lines.append("|-------|-------|------------|")

    for r in expansion_by_nrr[:7]:
        lines.append(f"| **{r['brand']}** | {format_percentage(r['nrr'])} | {format_currency(r['start_arr'])} → {format_currency(r['end_arr'])} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # New Business Analysis
    if new_business:
        lines.append("## New Business Analysis")
        lines.append("")
        lines.append(f"### Total New Business: {format_currency(new_business_revenue)} across {len(new_business)} brands")
        lines.append("")
        lines.append("### Top 10 New Brands by ARR")
        lines.append("")
        lines.append("| Brand | Ending ARR |")
        lines.append("|-------|------------|")

        for r in new_business_sorted[:10]:
            lines.append(f"| **{r['brand']}** | {format_currency(r['end_arr'])} |")

        top_10_new = sum(r['end_arr'] for r in new_business_sorted[:10])
        top_10_new_pct = (top_10_new / new_business_revenue * 100) if new_business_revenue > 0 else Decimal('0')
        lines.append("")
        lines.append(f"**These {min(10, len(new_business))} brands represent {format_currency(top_10_new)} ({format_percentage(top_10_new_pct)}) of new business ARR.**")
        lines.append("")

        avg_new_arr = new_business_revenue / len(new_business) if len(new_business) > 0 else Decimal('0')
        lines.append("### New Business Highlights")
        lines.append(f"- {'Strong enterprise wins' if len([r for r in new_business if r['end_arr'] > avg_new_arr * 2]) > 0 else 'Diverse customer base'}")
        lines.append(f"- Average new brand ARR: {format_currency(avg_new_arr)}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Churn Analysis
    if churned:
        lines.append("## Churn Analysis")
        lines.append("")
        churn_rate = (churned_revenue / total_start * 100) if total_start > 0 else Decimal('0')
        lines.append(f"### Total Churn: {format_currency(churned_revenue)} across {len(churned)} brands ({format_percentage(churn_rate)} of starting ARR)")
        lines.append("")
        lines.append("| Brand | Lost ARR |")
        lines.append("|-------|----------|")

        for r in churned_sorted:
            lines.append(f"| **{r['brand']}** | {format_currency(r['start_arr'])} |")

        lines.append("")
        lines.append("### Churn Profile")
        brand_churn_rate = (len(churned) / len(start_arr) * 100) if len(start_arr) > 0 else Decimal('0')
        lines.append(f"- {'All churned accounts were small-to-mid size' if all(r['start_arr'] < Decimal('50000') for r in churned) else 'Mix of account sizes churned'}")
        lines.append(f"- **Churn rate: {format_percentage(brand_churn_rate)} of brands, {format_percentage(churn_rate)} of ARR**")
        lines.append(f"- {'Low impact relative to expansion and new business' if churn_rate < 5 else 'Significant impact requiring attention'}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Customer Success Insights
    lines.append("## Customer Success Insights")
    lines.append("")
    lines.append("### 🎯 What's Working")
    lines.append("")
    lines.append("1. **Enterprise Expansion Excellence**")
    lines.append(f"   - Top 10 accounts expanded by {format_currency(top_10_expansion)}")
    if expansion_sorted:
        top_brands = ', '.join([r['brand'] for r in expansion_sorted[:3]])
        lines.append(f"   - Major brands like {top_brands} showing strong NRR")
    lines.append("   - Clear product-market fit at enterprise level")
    lines.append("")

    retained_growing = len([r for r in expansion if r['nrr'] >= 100])
    total_retained = len(existing_brands)
    retention_rate = (retained_growing / total_retained * 100) if total_retained > 0 else Decimal('0')
    lines.append("2. **Land-and-Expand Success**")
    lines.append(f"   - {retained_growing} of {total_retained} retained brands ({format_percentage(retention_rate)}) maintained or grew ARR")
    if contraction:
        lines.append(f"   - {len(contraction)} brands contracted")
    lines.append(f"   - Average expansion customer NRR: {format_percentage(avg_nrr)}")
    lines.append("")

    if new_business:
        lines.append("3. **Strong New Business Pipeline**")
        lines.append(f"   - {len(new_business)} new brands in {months} months")
        lines.append(f"   - {format_currency(new_business_revenue)} new ARR")
        lines.append("")

    if churn_rate < 5:
        lines.append(f"{'4' if new_business else '3'}. **Minimal Churn Risk**")
        lines.append(f"   - Very low revenue churn ({format_percentage(churn_rate)})")
        if churned:
            lines.append("   - Churn concentrated in smaller accounts")
        lines.append("")

    lines.append("### ⚠️ Areas for Attention")
    lines.append("")

    if contraction:
        lines.append(f"1. **Contraction Accounts ({len(contraction)} brands)**")
        for r in sorted(contraction, key=lambda x: x['nrr'])[:5]:
            lines.append(f"   - **{r['brand']}**: {format_percentage(r['nrr'])} NRR ({format_currency(r['start_arr'])} → {format_currency(r['end_arr'])})")
        lines.append("   - Action: Priority check-ins to understand usage challenges")
        lines.append("")

    if flat:
        lines.append(f"{'2' if contraction else '1'}. **Flat Accounts ({len(flat)} brands at 100% NRR)**")
        flat_brands = ', '.join([r['brand'] for r in flat[:5]])
        lines.append(f"   - {flat_brands}{', ...' if len(flat) > 5 else ''}")
        lines.append("   - Action: Identify expansion opportunities and additional use cases")
        lines.append("")

    if churned:
        point_num = 3 if contraction and flat else 2 if contraction or flat else 1
        lines.append(f"{point_num}. **Churned Accounts**")
        lines.append(f"   - {len(churned)} brands churned")
        lines.append("   - Action: Review onboarding and engagement strategies")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Recommendations
    lines.append("## Recommendations for CS Team")
    lines.append("")
    lines.append("### Priority 1: Protect & Grow Top Accounts")
    top_3 = sorted(existing_brands, key=lambda x: x['end_arr'], reverse=True)[:3]
    for r in top_3:
        lines.append(f"- **{r['brand']}** ({format_currency(r['end_arr'])} ARR) - {'Schedule executive business review' if r['nrr'] > 150 else 'Ensure continued engagement'}")
    lines.append("")

    lines.append("### Priority 2: Expansion Playbook")
    if expansion_by_nrr:
        top_performers = ', '.join([r['brand'] for r in expansion_by_nrr[:2]])
        lines.append(f"- Document what drove high NRR at {top_performers}")
    lines.append("- Identify patterns in high-growth accounts")
    if flat:
        lines.append("- Apply learnings to flat accounts (100% NRR segment)")
    lines.append("")

    if contraction:
        lines.append("### Priority 3: At-Risk Account Management")
        for r in sorted(contraction, key=lambda x: x['nrr'])[:3]:
            lines.append(f"- Immediate outreach to {r['brand']} ({format_percentage(r['nrr'])} NRR)")
        lines.append("- Understand contraction drivers and create recovery plan")
        lines.append("")

    if new_business:
        priority_num = 4 if contraction else 3
        lines.append(f"### Priority {priority_num}: New Customer Onboarding")
        lines.append(f"- Ensure {len(new_business)} new brands are set up for expansion success")
        lines.append("- First 90-day engagement critical")
        if new_business_sorted:
            top_new = ', '.join([r['brand'] for r in new_business_sorted[:3]])
            lines.append(f"- Focus on {top_new} (largest new accounts)")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Context
    lines.append("## Month-over-Month Context")
    lines.append("")
    if months > 0:
        monthly_growth_rate = ((total_end / total_start) ** (Decimal('1') / Decimal(str(months))) - 1) * 100 if total_start > 0 else Decimal('0')
        lines.append(f"This {months}-month period ({start_label} → {end_label}) represents:")
        lines.append(f"- **{format_percentage(monthly_growth_rate)} monthly compounded growth rate**")
        lines.append(f"- {'Strong momentum maintained over multiple quarters' if monthly_growth_rate > 4 else 'Steady growth trajectory'}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Conclusion
    lines.append("## Conclusion")
    lines.append("")
    lines.append(f"Our {format_percentage(overall_nrr)} NRR demonstrates {'exceptional' if overall_nrr > 130 else 'solid'} performance, with expansion revenue ({format_currency(expansion_revenue)}) {'driving the majority of growth' if expansion_revenue > new_business_revenue else 'contributing significantly to growth'}. The combination of strong enterprise {'retention and expansion' if len(expansion) > 0 else 'performance'}, {'healthy new business acquisition' if new_business else 'focused customer success'}, and {'minimal' if churn_rate < 5 else 'managed'} churn positions us well for continued growth.")
    lines.append("")
    lines.append("**Key Takeaway:** Customer Success efforts are clearly working at the enterprise level. Focus should remain on protecting large accounts, {'expanding flat accounts' if flat else 'maintaining momentum'}, and ensuring new customers follow similar expansion trajectories.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Metadata
    lines.append(f"*Report generated: {datetime.now().strftime('%Y-%m-%d')}*")
    lines.append(f"*Data source: {os.path.basename(csv_file)}*")
    lines.append(f"*Analysis period: {start_label} - {end_label}*")
    lines.append("")

    # Write report
    with open(output_file, 'w') as f:
        f.write('\n'.join(lines))

def main():
    parser = argparse.ArgumentParser(description='NRR Analysis by Financial Year')
    parser.add_argument('csv_file', help='Path to CSV file')
    parser.add_argument('--fy-year', type=int, help='Financial year to analyze (e.g., 2025 for FY25: Apr 2025 - Mar 2026)')
    parser.add_argument('--start-period', help='Custom start period (format: YYYY-MM)')
    parser.add_argument('--end-period', help='Custom end period (format: YYYY-MM)')
    parser.add_argument('--output-dir', default='~/Documents/NRR_Reports/', help='Output directory for reports')

    args = parser.parse_args()

    # Expand home directory
    csv_file = os.path.expanduser(args.csv_file)
    output_dir = os.path.expanduser(args.output_dir)

    # Validate CSV file
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found: {csv_file}", file=sys.stderr)
        sys.exit(1)

    # Parse custom periods if provided
    start_period = None
    end_period = None
    if args.start_period:
        parts = args.start_period.split('-')
        start_period = (int(parts[0]), int(parts[1]))
    if args.end_period:
        parts = args.end_period.split('-')
        end_period = (int(parts[0]), int(parts[1]))

    try:
        # Load data
        data = load_csv_data(csv_file)

        # Determine periods
        start, end = determine_periods(data, args.fy_year, start_period, end_period)

        # Check periods exist
        if start not in data:
            print(f"Error: No data found for start period {start[0]}-{start[1]:02d}", file=sys.stderr)
            sys.exit(1)
        if end not in data:
            print(f"Error: No data found for end period {end[0]}-{end[1]:02d}", file=sys.stderr)
            sys.exit(1)

        # Calculate NRR
        results, start_arr, end_arr = calculate_nrr(data, start, end)

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Generate output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f'NRR_Analysis_{timestamp}.md')

        # Generate report
        generate_markdown_report(results, start_arr, end_arr, start, end, csv_file, output_file)

        print(f"SUCCESS: Report generated at {output_file}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
