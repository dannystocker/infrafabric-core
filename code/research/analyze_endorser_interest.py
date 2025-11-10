#!/usr/bin/env python3
"""
IF.mission.arxiv - Interest & Employment Analysis
Enhances endorser discovery with:
1. Interest probability (likelihood to engage with InfraFabric)
2. Employment opportunity potential
3. Anthropic/Epic Games affiliation check
"""

import json
import os
from typing import List, Dict
from dataclasses import dataclass

# InfraFabric focus areas for interest matching
IF_FOCUS_AREAS = {
    # Core themes (highest interest signal)
    "multi-agent coordination": 10,
    "AI safety": 9,
    "verification": 8,
    "trustless systems": 8,
    "epistemic reasoning": 8,

    # Architecture themes (high interest)
    "distributed systems": 7,
    "consensus protocols": 7,
    "Byzantine fault tolerance": 7,
    "orchestration": 6,

    # Applied themes (medium-high interest)
    "governance": 6,
    "audit": 6,
    "provenance": 6,
    "citation analysis": 6,

    # Tangential but relevant (medium interest)
    "LLM reasoning": 5,
    "planning": 5,
    "reinforcement learning": 4,
}

# Employment opportunity signals
EMPLOYMENT_SIGNALS = {
    # Direct hiring indicators
    "hiring": 10,
    "we are recruiting": 10,
    "join our team": 10,

    # Lab/group indicators (potential positions)
    "research group": 7,
    "research lab": 7,
    "we are building": 6,
    "open positions": 8,

    # Collaboration signals
    "collaborators": 5,
    "seeking partnerships": 6,
    "research partnership": 6,
}

# Priority affiliations
PRIORITY_AFFILIATIONS = [
    "Anthropic",
    "Epic Games",
    "Epic",
    "OpenAI",
    "DeepMind",
    "Google Research",
    "Meta AI",
    "Microsoft Research"
]

@dataclass
class EnhancedEndorser:
    name: str
    relevance_score: float
    interest_probability: float  # 0-100
    employment_potential: float  # 0-100
    affiliations: List[str]
    papers: List[str]
    urls: List[str]
    keywords: List[str]
    priority_flag: str  # "ANTHROPIC", "EPIC_GAMES", "MAJOR_LAB", "ACADEMIC", "UNKNOWN"

def calculate_interest_probability(keywords: List[str], papers: List[str]) -> float:
    """
    Calculate likelihood that endorser would be interested in InfraFabric.
    Based on focus area alignment.
    """
    # Score from keywords
    keyword_score = 0
    keyword_text = " ".join(keywords).lower()

    for focus_area, weight in IF_FOCUS_AREAS.items():
        if focus_area in keyword_text:
            keyword_score += weight

    # Score from paper titles (deeper alignment signal)
    paper_text = " ".join(papers).lower()
    paper_score = 0

    for focus_area, weight in IF_FOCUS_AREAS.items():
        if focus_area in paper_text:
            paper_score += weight * 1.5  # Paper title match is stronger signal

    # Normalize to 0-100
    total_score = keyword_score + paper_score
    max_possible = sum(IF_FOCUS_AREAS.values()) * 2.5  # Rough upper bound

    probability = min(100, (total_score / max_possible) * 100)
    return round(probability, 1)

def calculate_employment_potential(papers: List[str], affiliations: List[str]) -> float:
    """
    Estimate potential for employment opportunities.
    Looks for hiring signals in abstracts + affiliation type.
    """
    # Note: Would need full abstracts for deep analysis
    # Using paper titles as proxy

    text = " ".join(papers).lower()
    score = 0

    # Check for employment signals
    for signal, weight in EMPLOYMENT_SIGNALS.items():
        if signal in text:
            score += weight

    # Affiliation boost
    if any(aff in ["Anthropic", "Epic Games", "OpenAI"] for aff in affiliations):
        score += 20  # These are actively hiring companies
    elif any(aff in ["DeepMind", "Google Research", "Meta AI", "Microsoft Research"] for aff in affiliations):
        score += 10  # Major labs with ongoing recruitment
    elif affiliations and "university" in " ".join(affiliations).lower():
        score += 5  # Academic labs may have postdoc/RA positions

    # Normalize to 0-100
    return min(100, score)

def determine_priority_flag(affiliations: List[str], interest: float) -> str:
    """Categorize endorser by strategic priority"""
    aff_text = " ".join(affiliations).lower()

    if "anthropic" in aff_text:
        return "🔥 ANTHROPIC"
    elif "epic games" in aff_text or "epic" in aff_text:
        return "🎮 EPIC_GAMES"
    elif any(lab.lower() in aff_text for lab in ["openai", "deepmind", "google research", "meta ai"]):
        return "⭐ MAJOR_LAB"
    elif interest >= 70:
        return "✨ HIGH_INTEREST_ACADEMIC"
    elif "university" in aff_text or "institute" in aff_text:
        return "🎓 ACADEMIC"
    else:
        return "❓ UNKNOWN"

def analyze_endorser_portfolio(json_path: str, affiliation_cache: Dict = None) -> List[EnhancedEndorser]:
    """
    Load endorsers from JSON and enhance with interest/employment analysis.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        endorsers = json.load(f)

    enhanced = []

    for endorser in endorsers:
        # Calculate metrics
        interest = calculate_interest_probability(
            endorser.get('keywords', []),
            endorser.get('papers', [])
        )

        # Use cached affiliations if available
        affiliations = []
        if affiliation_cache and endorser['name'] in affiliation_cache:
            affiliations = affiliation_cache[endorser['name']]

        employment = calculate_employment_potential(
            endorser.get('papers', []),
            affiliations
        )

        priority = determine_priority_flag(affiliations, interest)

        enhanced.append(EnhancedEndorser(
            name=endorser['name'],
            relevance_score=endorser.get('relevance_score', 0),
            interest_probability=interest,
            employment_potential=employment,
            affiliations=affiliations,
            papers=endorser.get('papers', []),
            urls=endorser.get('urls', []),
            keywords=endorser.get('keywords', []),
            priority_flag=priority
        ))

    # Sort by composite score: relevance + interest + employment
    enhanced.sort(
        key=lambda e: (
            e.relevance_score * 0.4 +
            e.interest_probability * 0.4 +
            e.employment_potential * 0.2
        ),
        reverse=True
    )

    return enhanced

def generate_strategic_report(endorsers: List[EnhancedEndorser], output_path: str):
    """Generate strategic endorser targeting report"""
    lines = []
    lines.append("# InfraFabric Strategic Endorser Analysis\n")
    lines.append("**Analysis:** Interest probability + Employment potential\n")
    lines.append("---\n")

    # Separate by priority
    anthropic = [e for e in endorsers if "ANTHROPIC" in e.priority_flag]
    epic = [e for e in endorsers if "EPIC" in e.priority_flag]
    major_labs = [e for e in endorsers if "MAJOR_LAB" in e.priority_flag]
    high_interest = [e for e in endorsers if "HIGH_INTEREST" in e.priority_flag]

    # Anthropic candidates
    if anthropic:
        lines.append("## 🔥 Anthropic Researchers\n")
        for e in anthropic:
            lines.append(f"### {e.name}")
            lines.append(f"- **Interest Probability:** {e.interest_probability}%")
            lines.append(f"- **Employment Potential:** {e.employment_potential}%")
            lines.append(f"- **Relevance Score:** {e.relevance_score:.1f}")
            lines.append(f"- **Papers:** {len(e.papers)}")
            lines.append(f"- **Topics:** {', '.join(e.keywords[:5])}")
            lines.append("")

    # Epic Games candidates
    if epic:
        lines.append("## 🎮 Epic Games Researchers\n")
        for e in epic:
            lines.append(f"### {e.name}")
            lines.append(f"- **Interest Probability:** {e.interest_probability}%")
            lines.append(f"- **Employment Potential:** {e.employment_potential}%")
            lines.append(f"- **Relevance Score:** {e.relevance_score:.1f}")
            lines.append(f"- **Papers:** {len(e.papers)}")
            lines.append(f"- **Topics:** {', '.join(e.keywords[:5])}")
            lines.append("")

    # Major lab candidates
    if major_labs:
        lines.append("## ⭐ Major AI Lab Researchers\n")
        for e in major_labs[:5]:  # Top 5
            lines.append(f"### {e.name}")
            lines.append(f"- **Affiliation:** {', '.join(e.affiliations)}")
            lines.append(f"- **Interest Probability:** {e.interest_probability}%")
            lines.append(f"- **Employment Potential:** {e.employment_potential}%")
            lines.append(f"- **Relevance Score:** {e.relevance_score:.1f}")
            lines.append("")

    # High interest academic candidates
    lines.append("## ✨ High-Interest Academic Candidates\n")
    for e in high_interest[:10]:  # Top 10
        lines.append(f"### {e.name}")
        lines.append(f"- **Interest Probability:** {e.interest_probability}%")
        lines.append(f"- **Employment Potential:** {e.employment_potential}%")
        lines.append(f"- **Relevance Score:** {e.relevance_score:.1f}")
        lines.append(f"- **Key Papers:**")
        for paper in e.papers[:2]:
            lines.append(f"  - {paper[:100]}...")
        lines.append("")

    # Strategy recommendations
    lines.append("---\n")
    lines.append("## 🎯 Outreach Strategy\n")
    lines.append("### Priority 1: Anthropic + Epic Games")
    lines.append("- **Goal:** Endorsement + employment opportunities")
    lines.append("- **Approach:** Direct, highlight IF.TTT alignment + real-world validation")
    lines.append("")
    lines.append("### Priority 2: Major AI Labs")
    lines.append("- **Goal:** Endorsement + research collaboration")
    lines.append("- **Approach:** Technical depth, cite their work, show IF integration potential")
    lines.append("")
    lines.append("### Priority 3: High-Interest Academics")
    lines.append("- **Goal:** Endorsement + co-authorship opportunities")
    lines.append("- **Approach:** Collaborative framing, offer IF components for their research")
    lines.append("")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    return output_path

if __name__ == "__main__":
    import sys
    import glob

    # Find most recent endorser JSON
    json_files = sorted(glob.glob("arxiv_endorsers.*.json"), reverse=True)
    if not json_files:
        print("Error: No arxiv_endorsers.*.json found. Run find_arxiv_endorsers.py first.")
        sys.exit(1)

    latest = json_files[0]
    print(f"Analyzing: {latest}\n")

    # Analyze (no affiliation cache for now - would need to run check_fang_affiliations.py separately)
    endorsers = analyze_endorser_portfolio(latest)

    # Generate report
    from datetime import datetime
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    report_path = f"IF_ENDORSER_STRATEGY.{timestamp}.md"

    generate_strategic_report(endorsers, report_path)

    print(f"✅ Strategic analysis complete: {report_path}")
    print(f"\nTop 5 Strategic Targets:")
    for i, e in enumerate(endorsers[:5], 1):
        print(f"{i}. {e.priority_flag} {e.name}")
        print(f"   Interest: {e.interest_probability}% | Employment: {e.employment_potential}% | Relevance: {e.relevance_score:.1f}")
        print()
