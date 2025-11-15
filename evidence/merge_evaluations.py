#!/usr/bin/env python3
"""
InfraFabric Evaluation Merger
Compares and merges YAML evaluations from Codex, Gemini, and Claude
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

def load_evaluation(filepath: Path) -> Dict:
    """Load a YAML evaluation file."""
    with open(filepath) as f:
        return yaml.safe_load(f)

def compare_scores(evals: List[Dict]) -> Dict:
    """Compare numeric scores across evaluators."""
    scores = defaultdict(list)

    for eval_data in evals:
        evaluator = eval_data['evaluator']

        # Executive summary
        scores['overall_score'].append({
            'evaluator': evaluator,
            'value': eval_data['executive_summary']['overall_score']
        })

        # Conceptual quality
        for key in ['substance_score', 'novelty_score', 'rigor_score', 'coherence_score']:
            scores[key].append({
                'evaluator': evaluator,
                'value': eval_data['conceptual_quality'][key]
            })

        # Technical implementation
        scores['code_quality_score'].append({
            'evaluator': evaluator,
            'value': eval_data['technical_implementation']['code_quality_score']
        })
        scores['test_coverage'].append({
            'evaluator': evaluator,
            'value': eval_data['technical_implementation']['test_coverage']
        })

    return scores

def calculate_consensus(scores: Dict) -> Dict:
    """Calculate average scores and identify outliers."""
    consensus = {}

    for metric, values in scores.items():
        nums = [v['value'] for v in values]
        avg = sum(nums) / len(nums)
        variance = sum((x - avg) ** 2 for x in nums) / len(nums)

        consensus[metric] = {
            'average': round(avg, 2),
            'variance': round(variance, 2),
            'values': values,
            'outliers': [
                v for v in values
                if abs(v['value'] - avg) > variance * 1.5
            ]
        }

    return consensus

def merge_if_components(evals: List[Dict]) -> Dict:
    """Merge IF.* component assessments from all evaluators."""
    merged = {
        'implemented': {},
        'partial': {},
        'vaporware': {}
    }

    for eval_data in evals:
        evaluator = eval_data['evaluator']
        components = eval_data['technical_implementation']['if_components']

        # Process each category
        for category in ['implemented', 'partial', 'vaporware']:
            for component in components.get(category, []):
                name = component['name']

                if name not in merged[category]:
                    merged[category][name] = {
                        'evaluators': [],
                        'data': []
                    }

                merged[category][name]['evaluators'].append(evaluator)
                merged[category][name]['data'].append(component)

    return merged

def merge_issues(evals: List[Dict]) -> Dict:
    """Merge P0/P1/P2 issues and identify consensus blockers."""
    merged = {
        'p0_blockers': {},
        'p1_high_priority': {},
        'p2_medium_priority': {}
    }

    for eval_data in evals:
        evaluator = eval_data['evaluator']
        gaps = eval_data['gaps_and_issues']

        for priority in ['p0_blockers', 'p1_high_priority', 'p2_medium_priority']:
            for issue_data in gaps.get(priority, []):
                issue = issue_data['issue']

                if issue not in merged[priority]:
                    merged[priority][issue] = {
                        'count': 0,
                        'evaluators': [],
                        'details': []
                    }

                merged[priority][issue]['count'] += 1
                merged[priority][issue]['evaluators'].append(evaluator)
                merged[priority][issue]['details'].append(issue_data)

    return merged

def merge_citation_issues(evals: List[Dict]) -> Dict:
    """Merge citation verification findings."""
    merged = {
        'papers': defaultdict(int),
        'citations': defaultdict(int),
        'readme_issues': {},
        'broken_links': set()
    }

    for eval_data in evals:
        cit_data = eval_data['technical_implementation'].get('citation_verification', {})

        merged['papers']['total'] += cit_data.get('papers_reviewed', 0)
        merged['citations']['total'] += cit_data.get('total_citations', 0)
        merged['citations']['verified'] += cit_data.get('citations_verified', 0)

        # Collect citation issues
        for issue in cit_data.get('issues', []):
            issue_text = issue['issue']
            if issue_text not in merged['readme_issues']:
                merged['readme_issues'][issue_text] = {
                    'count': 0,
                    'evaluators': [],
                    'severity': issue['severity'],
                    'details': []
                }
            merged['readme_issues'][issue_text]['count'] += 1
            merged['readme_issues'][issue_text]['evaluators'].append(eval_data['evaluator'])
            merged['readme_issues'][issue_text]['details'].append(issue)

        # Collect broken links
        readme = cit_data.get('readme_audit', {})
        for link in readme.get('broken_link_examples', []):
            merged['broken_links'].add(link['url'])

    return merged

def generate_consensus_report(evals: List[Dict]) -> str:
    """Generate a consensus report from multiple evaluations."""

    scores = compare_scores(evals)
    consensus = calculate_consensus(scores)
    components = merge_if_components(evals)
    issues = merge_issues(evals)
    citations = merge_citation_issues(evals)

    report = []
    report.append("# InfraFabric Evaluation Consensus Report\n")
    report.append(f"**Evaluators:** {', '.join(e['evaluator'] for e in evals)}\n")
    report.append(f"**Generated:** {evals[0]['evaluation_date']}\n\n")

    # Score consensus
    report.append("## Score Consensus\n")
    for metric, data in consensus.items():
        report.append(f"### {metric}")
        report.append(f"- **Average:** {data['average']}/10")
        report.append(f"- **Variance:** {data['variance']}")
        report.append(f"- **Individual scores:**")
        for v in data['values']:
            report.append(f"  - {v['evaluator']}: {v['value']}")
        if data['outliers']:
            report.append(f"- **Outliers:** {', '.join(o['evaluator'] for o in data['outliers'])}")
        report.append("")

    # IF.* Component Consensus
    report.append("\n## IF.* Component Status (Consensus)\n")

    for category in ['implemented', 'partial', 'vaporware']:
        report.append(f"\n### {category.upper()}\n")
        for name, data in components[category].items():
            evaluator_count = len(data['evaluators'])
            total_evaluators = len(evals)
            consensus_level = evaluator_count / total_evaluators * 100

            report.append(f"**{name}** ({evaluator_count}/{total_evaluators} evaluators agree - {consensus_level:.0f}% consensus)")
            report.append(f"- Evaluators: {', '.join(data['evaluators'])}")

            if category == 'implemented':
                # Show average completeness
                completeness_vals = [c.get('completeness', 0) for c in data['data']]
                avg_completeness = sum(completeness_vals) / len(completeness_vals) if completeness_vals else 0
                report.append(f"- Average completeness: {avg_completeness:.0f}%")

            report.append("")

    # Critical Issues (P0) with consensus
    report.append("\n## P0 Blockers (Consensus)\n")
    p0_sorted = sorted(
        issues['p0_blockers'].items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )

    for issue, data in p0_sorted:
        consensus_level = data['count'] / len(evals) * 100
        report.append(f"\n**{issue}** ({data['count']}/{len(evals)} evaluators - {consensus_level:.0f}% consensus)")
        report.append(f"- Identified by: {', '.join(data['evaluators'])}")

        # Get effort estimate range
        efforts = [d.get('effort', 'Unknown') for d in data['details']]
        report.append(f"- Effort estimates: {', '.join(set(efforts))}")
        report.append("")

    # Citation Verification Consensus
    report.append("\n## Citation & Documentation Quality (Consensus)\n")

    report.append(f"\n### Overall Citation Stats\n")
    avg_papers = citations['papers']['total'] / len(evals) if evals else 0
    total_cits = citations['citations']['total']
    total_verified = citations['citations']['verified']
    verification_rate = (total_verified / total_cits * 100) if total_cits > 0 else 0

    report.append(f"- **Papers reviewed:** {avg_papers:.0f} (average across evaluators)")
    report.append(f"- **Total citations found:** {total_cits}")
    report.append(f"- **Citations verified:** {total_verified} ({verification_rate:.0f}%)")
    report.append("")

    # Citation issues sorted by consensus
    report.append("\n### Citation Issues (by consensus)\n")
    citation_issues_sorted = sorted(
        citations['readme_issues'].items(),
        key=lambda x: (x[1]['count'], {'high': 3, 'medium': 2, 'low': 1}[x[1]['severity']]),
        reverse=True
    )

    for issue, data in citation_issues_sorted[:10]:  # Top 10 issues
        consensus_level = data['count'] / len(evals) * 100
        severity_badge = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[data['severity']]
        report.append(f"\n{severity_badge} **{issue}** ({data['count']}/{len(evals)} evaluators - {consensus_level:.0f}% consensus)")
        report.append(f"- Severity: {data['severity']}")
        report.append(f"- Identified by: {', '.join(data['evaluators'])}")
        if data['details']:
            example = data['details'][0]
            if 'file' in example:
                report.append(f"- Example: {example['file']}")
        report.append("")

    # Broken links
    if citations['broken_links']:
        report.append("\n### Broken Links Found\n")
        for link in sorted(citations['broken_links'])[:10]:
            report.append(f"- {link}")
        if len(citations['broken_links']) > 10:
            report.append(f"- ... and {len(citations['broken_links']) - 10} more")
        report.append("")

    # Buyer Persona Consensus
    report.append("\n## Buyer Persona Consensus\n")
    personas = defaultdict(lambda: {'fit_scores': [], 'wtp_scores': [], 'evaluators': []})

    for eval_data in evals:
        evaluator = eval_data['evaluator']
        for persona in eval_data['market_analysis'].get('buyer_personas', []):
            name = persona['name']
            personas[name]['fit_scores'].append(persona['fit_score'])
            personas[name]['wtp_scores'].append(persona['willingness_to_pay'])
            personas[name]['evaluators'].append(evaluator)

    for name, data in sorted(personas.items(), key=lambda x: sum(x[1]['fit_scores'])/len(x[1]['fit_scores']), reverse=True):
        avg_fit = sum(data['fit_scores']) / len(data['fit_scores'])
        avg_wtp = sum(data['wtp_scores']) / len(data['wtp_scores'])
        report.append(f"**{name}**")
        report.append(f"- Avg Fit Score: {avg_fit:.1f}/10")
        report.append(f"- Avg Willingness to Pay: {avg_wtp:.1f}/10")
        report.append(f"- Identified by: {', '.join(set(data['evaluators']))}")
        report.append("")

    return "\n".join(report)

def main():
    if len(sys.argv) < 2:
        print("Usage: ./merge_evaluations.py <eval1.yaml> <eval2.yaml> [eval3.yaml ...]")
        print("\nExample:")
        print("  ./merge_evaluations.py codex_eval.yaml gemini_eval.yaml claude_eval.yaml")
        sys.exit(1)

    # Load all evaluations
    evals = []
    for filepath in sys.argv[1:]:
        path = Path(filepath)
        if not path.exists():
            print(f"Error: File not found: {filepath}")
            sys.exit(1)

        evals.append(load_evaluation(path))
        print(f"✓ Loaded {filepath} ({evals[-1]['evaluator']})")

    # Generate consensus report
    print(f"\n✓ Generating consensus report from {len(evals)} evaluations...")
    report = generate_consensus_report(evals)

    # Write output
    output_file = Path("INFRAFABRIC_CONSENSUS_REPORT.md")
    with open(output_file, 'w') as f:
        f.write(report)

    print(f"✓ Consensus report written to {output_file}")

    # Show summary
    print("\n" + "="*60)
    print(report[:500] + "...")
    print("="*60)
    print(f"\n✓ Full report available at: {output_file}")

if __name__ == "__main__":
    main()
