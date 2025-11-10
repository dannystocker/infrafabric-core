#!/usr/bin/env python3
"""
IF.optimise - Anthropic Credit Maximization Strategy
Optimize $974 Anthropic credit usage over 7 days for maximum research value.

Budget: $974
Timeline: 7 days
Goal: Maximize endorser discovery + integration pattern analysis
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List

# Pricing (Haiku-3.5 - fast and cheap)
HAIKU_PRICING = {
    "input": 0.25 / 1_000_000,   # $0.25 per million tokens
    "output": 1.25 / 1_000_000,  # $1.25 per million tokens
}

# Estimated token usage per analysis type
TOKEN_ESTIMATES = {
    "gap_analysis_input": 2500,    # Paper abstract + IF components context
    "gap_analysis_output": 1000,   # Patterns + Gaps + Integration ideas
    "endorser_interest_input": 1500,  # Paper title + keywords analysis
    "endorser_interest_output": 500,   # Interest scoring + reasoning
}

def calculate_cost_per_analysis(analysis_type: str) -> float:
    """Calculate cost for one analysis"""
    if analysis_type == "gap_analysis":
        input_cost = TOKEN_ESTIMATES["gap_analysis_input"] * HAIKU_PRICING["input"]
        output_cost = TOKEN_ESTIMATES["gap_analysis_output"] * HAIKU_PRICING["output"]
    elif analysis_type == "endorser_interest":
        input_cost = TOKEN_ESTIMATES["endorser_interest_input"] * HAIKU_PRICING["input"]
        output_cost = TOKEN_ESTIMATES["endorser_interest_output"] * HAIKU_PRICING["output"]
    else:
        return 0.0

    return input_cost + output_cost

def calculate_max_analyses(budget: float, analysis_type: str) -> int:
    """Calculate maximum number of analyses possible"""
    cost_per = calculate_cost_per_analysis(analysis_type)
    return int(budget / cost_per)

def generate_7day_schedule(total_budget: float) -> Dict:
    """
    Generate optimal 7-day research schedule.

    Strategy:
    - Days 1-3: Broad gap analysis (200 papers/day)
    - Days 4-5: Deep endorser interest scoring (100 endorsers/day)
    - Days 6-7: Targeted follow-up + integration proposals (100 papers/day)
    """
    daily_budget = total_budget / 7

    gap_cost = calculate_cost_per_analysis("gap_analysis")
    endorser_cost = calculate_cost_per_analysis("endorser_interest")

    schedule = {
        "total_budget": total_budget,
        "daily_budget": daily_budget,
        "days": []
    }

    # Day 1-3: Broad gap analysis
    for day in range(1, 4):
        papers_per_day = int(daily_budget / gap_cost)
        schedule["days"].append({
            "day": day,
            "focus": "gap_analysis",
            "target": papers_per_day,
            "budget": daily_budget,
            "cost_per_item": gap_cost,
            "description": f"Analyze {papers_per_day} papers for IF patterns + gaps"
        })

    # Day 4-5: Deep endorser analysis
    for day in range(4, 6):
        endorsers_per_day = int(daily_budget / endorser_cost)
        schedule["days"].append({
            "day": day,
            "focus": "endorser_interest",
            "target": endorsers_per_day,
            "budget": daily_budget,
            "cost_per_item": endorser_cost,
            "description": f"Score {endorsers_per_day} endorsers for interest + employment potential"
        })

    # Day 6-7: Targeted deep-dive + integration proposals
    for day in range(6, 8):
        papers_per_day = int(daily_budget / gap_cost)
        schedule["days"].append({
            "day": day,
            "focus": "targeted_integration",
            "target": papers_per_day,
            "budget": daily_budget,
            "cost_per_item": gap_cost,
            "description": f"Deep-dive on {papers_per_day} high-value papers for integration"
        })

    return schedule

def estimate_total_coverage(schedule: Dict) -> Dict:
    """Estimate total research coverage"""
    total_papers_analyzed = sum(
        day["target"] for day in schedule["days"]
        if day["focus"] in ["gap_analysis", "targeted_integration"]
    )
    total_endorsers_scored = sum(
        day["target"] for day in schedule["days"]
        if day["focus"] == "endorser_interest"
    )

    return {
        "papers_analyzed": total_papers_analyzed,
        "endorsers_scored": total_endorsers_scored,
        "total_analyses": total_papers_analyzed + total_endorsers_scored
    }

def print_optimization_report(schedule: Dict, coverage: Dict):
    """Print human-readable optimization plan"""
    print("=" * 80)
    print("IF.optimise - Anthropic Credit Maximization Plan")
    print("=" * 80)
    print()
    print(f"💰 Total Budget:      ${schedule['total_budget']:.2f}")
    print(f"📅 Timeline:          7 days")
    print(f"💵 Daily Budget:      ${schedule['daily_budget']:.2f}")
    print()
    print("📊 EXPECTED COVERAGE")
    print("-" * 80)
    print(f"📄 Papers Analyzed:   {coverage['papers_analyzed']:,}")
    print(f"👤 Endorsers Scored:  {coverage['endorsers_scored']:,}")
    print(f"🎯 Total Analyses:    {coverage['total_analyses']:,}")
    print()
    print("📋 7-DAY SCHEDULE")
    print("-" * 80)

    for day_plan in schedule["days"]:
        print(f"\n**Day {day_plan['day']}:** {day_plan['focus'].replace('_', ' ').title()}")
        print(f"   Target:      {day_plan['target']:,} items")
        print(f"   Budget:      ${day_plan['budget']:.2f}")
        print(f"   Cost/item:   ${day_plan['cost_per_item']:.4f}")
        print(f"   Description: {day_plan['description']}")

    print()
    print("=" * 80)
    print("🚀 EXECUTION STRATEGY")
    print("=" * 80)
    print()
    print("Phase 1 (Days 1-3): DISCOVERY")
    print("  - Run if_gap_analysis.py on 200 papers/day")
    print("  - Identify top 50 integration opportunities")
    print("  - Extract all authors for endorser pool")
    print()
    print("Phase 2 (Days 4-5): TARGETING")
    print("  - Run analyze_endorser_interest.py on all discovered endorsers")
    print("  - Score for: Interest probability + Employment potential")
    print("  - Identify top 20 strategic targets")
    print()
    print("Phase 3 (Days 6-7): DEEP DIVE")
    print("  - Deep analysis on top 20 endorsers' recent work")
    print("  - Generate personalized outreach templates")
    print("  - Create integration proposals for IF.guard deliberation")
    print()
    print("💡 OPTIMIZATION TIPS")
    print("-" * 80)
    print("1. Batch process papers in groups of 50 (rate limit: 2s between calls)")
    print("2. Use if_gap_analysis.py with top_n=200 for daily runs")
    print("3. Run check_fang_affiliations.py on top 50 endorsers (web scraping)")
    print("4. Save all outputs to gitignored paths for privacy")
    print()

def save_schedule_json(schedule: Dict, output_path: str):
    """Save schedule as JSON for automation"""
    with open(output_path, 'w') as f:
        json.dump(schedule, f, indent=2)
    print(f"📁 Schedule saved: {output_path}")
    print("   Use this for GitHub Actions / cron automation")
    print()

def generate_daily_commands(schedule: Dict):
    """Generate shell commands for each day"""
    print("🔧 DAILY EXECUTION COMMANDS")
    print("=" * 80)

    for day_plan in schedule["days"]:
        day = day_plan["day"]
        focus = day_plan["focus"]
        target = day_plan["target"]

        print(f"\n# Day {day}: {day_plan['description']}")

        if focus == "gap_analysis":
            print(f"python3 if_gap_analysis.py --top_n={target} --output=IF_GAP_ANALYSIS.day{day}.md")
        elif focus == "endorser_interest":
            print(f"python3 analyze_endorser_interest.py --batch_size={target}")
        elif focus == "targeted_integration":
            print(f"python3 if_gap_analysis.py --top_n={target} --deep_dive=true --output=IF_INTEGRATION_PROPOSALS.day{day}.md")

    print()

if __name__ == "__main__":
    import sys

    # Configuration
    BUDGET = 974.0  # USD
    DAYS = 7

    print()
    print("Calculating optimal Anthropic credit usage...")
    print()

    # Generate schedule
    schedule = generate_7day_schedule(BUDGET)
    coverage = estimate_total_coverage(schedule)

    # Print report
    print_optimization_report(schedule, coverage)

    # Show cost breakdown
    gap_cost = calculate_cost_per_analysis("gap_analysis")
    endorser_cost = calculate_cost_per_analysis("endorser_interest")

    print()
    print("💵 COST BREAKDOWN")
    print("-" * 80)
    print(f"Gap Analysis:         ${gap_cost:.6f} per paper")
    print(f"Endorser Scoring:     ${endorser_cost:.6f} per endorser")
    print()
    print(f"With ${BUDGET:.2f} you can afford:")
    print(f"  - {calculate_max_analyses(BUDGET, 'gap_analysis'):,} gap analyses OR")
    print(f"  - {calculate_max_analyses(BUDGET, 'endorser_interest'):,} endorser scores OR")
    print(f"  - Balanced mix: {coverage['total_analyses']:,} total analyses")
    print()

    # Generate commands
    generate_daily_commands(schedule)

    # Save JSON
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    schedule_path = f"ANTHROPIC_CREDIT_SCHEDULE.{timestamp}.json"
    save_schedule_json(schedule, schedule_path)

    print("✅ Optimization plan generated")
    print()
    print("NEXT STEPS:")
    print("1. Set ANTHROPIC_API_KEY environment variable")
    print("2. Run Day 1 command to start discovery phase")
    print("3. Review outputs daily and adjust targets as needed")
    print("4. Track actual costs vs estimates in IF.trace logs")
    print()
