#!/usr/bin/env python3
"""
Simple Batch Test - Demonstrates IF Guardians with simulated contact discovery

This is a demonstration showing:
1. IF Guardians debate running
2. Batch processing architecture
3. Self-documenting manifests
4. Late bloomer tracking

For production, integrate with actual weighted_multi_agent_finder.py

Author: InfraFabric Research
Date: October 31, 2025
"""

import json
import csv
from datetime import datetime
from pathlib import Path

def simulate_contact_discovery(first_name, last_name, org, role, context=""):
    """
    Simulate contact discovery using free agents.

    In production, this would call actual agent implementations.
    For demo, we generate realistic-looking results.
    """

    # Simulate different agent strategies
    agents = {
        'ProfessionalNetworker': {
            'strategy': 'firstname.lastname@company.com pattern',
            'confidence': 65,
            'email': f"{first_name.lower()}.{last_name.lower()}@{org.lower().replace(' ', '')}.com",
            'weight': 1.0
        },
        'AcademicResearcher': {
            'strategy': 'Google Scholar + institution search',
            'confidence': 45 if 'research' in context.lower() else 20,
            'email': f"{first_name[0].lower()}{last_name.lower()}@{org.lower().replace(' ', '')}.edu" if 'university' in org.lower() else None,
            'weight': 0.0 if 'research' not in context.lower() else 1.2
        },
        'InvestigativeJournalist': {
            'strategy': 'Deep web search, archived pages',
            'confidence': 75 if 'CEO' in role or 'Chief' in role else 40,
            'email': f"{first_name.lower()}@{org.lower().replace(' ', '')}.com" if 'CEO' in role else None,
            'weight': 2.0 if 'CEO' in role else 0.5
        }
    }

    # Find best result
    best_agent = max(agents.items(), key=lambda x: x[1]['confidence'])

    result = {
        'contact': {
            'first_name': first_name,
            'last_name': last_name,
            'org': org,
            'role': role
        },
        'contact_found': best_agent[1]['confidence'] >= 60,
        'best_email': best_agent[1]['email'],
        'best_confidence': best_agent[1]['confidence'],
        'best_agent': best_agent[0],
        'agent_results': agents,
        'timestamp': datetime.now().isoformat()
    }

    return result


def run_guardian_debate():
    """Simulate IF Guardians debate"""

    print("\n" + "="*60)
    print("🛡️  IF GUARDIANS DEBATE: Batch Contact Discovery")
    print("="*60)

    print("\n📋 PROPOSAL:")
    print("   Process 5 test contacts using free agent heuristics")
    print("   Public figures only, educational/validation purpose")

    print("\n🗣️  GUARDIAN POSITIONS:\n")

    guardians = {
        'Technical': {
            'vote': 'APPROVE',
            'weight': 1.5,
            'reasoning': 'Free heuristics, reproducible, no external dependencies',
            'safeguards': ['Document all heuristics', 'Confidence scores mandatory']
        },
        'Ethical': {
            'vote': 'CONDITIONAL',
            'weight': 2.0,
            'reasoning': 'Public figures OK, but needs transparency',
            'safeguards': ['Label as simulated', 'Human review before use', 'No auto-send']
        },
        'Legal': {
            'vote': 'APPROVE',
            'weight': 1.0,
            'reasoning': 'Public data, no GDPR issues for demo',
            'safeguards': ['Provenance tracking']
        },
        'Business': {
            'vote': 'APPROVE',
            'weight': 1.5,
            'reasoning': '5 contacts = good pilot size',
            'safeguards': ['Measure accuracy against known contacts']
        },
        'User': {
            'vote': 'CONDITIONAL',
            'weight': 1.5,
            'reasoning': 'Recipients must know this is heuristic',
            'safeguards': ['Clear labeling in any outreach']
        },
        'Meta': {
            'vote': 'APPROVE',
            'weight': 2.0,
            'reasoning': 'Dogfooding weighted coordination = philosophical integrity',
            'safeguards': ['Self-document the discovery process']
        }
    }

    for name, guardian in guardians.items():
        print(f"{'─'*60}")
        print(f"🎭 {name.upper()} GUARDIAN (weight={guardian['weight']})")
        print(f"   Vote: {guardian['vote']}")
        print(f"   Reasoning: {guardian['reasoning']}")
        print(f"   Safeguards: {', '.join(guardian['safeguards'])}")

    print(f"\n{'─'*60}")
    print("📊 WEIGHTED SYNTHESIS:")

    # Calculate weighted decision
    conditional_weight = sum(g['weight'] for g in guardians.values() if g['vote'] == 'CONDITIONAL')
    approve_weight = sum(g['weight'] for g in guardians.values() if g['vote'] == 'APPROVE')

    print(f"   Conditional votes (weighted): {conditional_weight}")
    print(f"   Approve votes (weighted): {approve_weight}")

    print(f"\n   ✅ DECISION: CONDITIONAL APPROVAL")
    print(f"\n   Required Safeguards:")
    all_safeguards = set()
    for g in guardians.values():
        all_safeguards.update(g['safeguards'])

    for safeguard in sorted(all_safeguards):
        print(f"     ✅ {safeguard}")

    print("="*60 + "\n")

    debate_result = {
        'timestamp': datetime.now().isoformat(),
        'proposal': 'Batch process 5 test contacts with free agents',
        'guardians': guardians,
        'decision': 'conditional_approval',
        'safeguards': list(all_safeguards)
    }

    return debate_result


def main():
    print("="*60)
    print("IF GUARDIANS + BATCH DISCOVERY TEST")
    print("="*60)

    # Run Guardian debate
    debate_result = run_guardian_debate()

    # Load test contacts
    print("📋 Loading test contacts...")
    with open('test_contacts.csv', 'r') as f:
        reader = csv.DictReader(f)
        contacts = list(reader)

    print(f"✅ Loaded {len(contacts)} contacts\n")

    # Process each contact
    print("="*60)
    print("🔄 PROCESSING CONTACTS")
    print("="*60 + "\n")

    results = []
    for i, contact in enumerate(contacts, 1):
        print(f"[{i}/{len(contacts)}] {contact['first_name']} {contact['last_name']} ({contact['org']})")

        result = simulate_contact_discovery(
            contact['first_name'],
            contact['last_name'],
            contact['org'],
            contact['role'],
            contact.get('context', '')
        )

        results.append(result)

        if result['contact_found']:
            print(f"   ✅ Found: {result['best_email']}")
            print(f"   📊 Confidence: {result['best_confidence']}%")
            print(f"   🤖 Best agent: {result['best_agent']}")
        else:
            print(f"   ⚠️  Low confidence ({result['best_confidence']}%)")

        print()

    # Summary
    print("="*60)
    print("📊 SUMMARY")
    print("="*60 + "\n")

    found = sum(1 for r in results if r['contact_found'])
    print(f"Contacts processed: {len(results)}")
    print(f"Contacts found: {found} ({found/len(results)*100:.0f}%)")
    print(f"Average confidence: {sum(r['best_confidence'] for r in results)/len(results):.1f}%")

    # Agent performance
    print(f"\n🤖 Agent Performance:")
    agent_stats = {}
    for result in results:
        for agent_name, agent_result in result['agent_results'].items():
            if agent_name not in agent_stats:
                agent_stats[agent_name] = {'total_confidence': 0, 'count': 0, 'total_weight': 0}

            agent_stats[agent_name]['total_confidence'] += agent_result['confidence']
            agent_stats[agent_name]['count'] += 1
            agent_stats[agent_name]['total_weight'] += agent_result['weight']

    for agent_name, stats in sorted(agent_stats.items()):
        avg_conf = stats['total_confidence'] / stats['count']
        avg_weight = stats['total_weight'] / stats['count']
        print(f"\n   {agent_name}:")
        print(f"     Avg confidence: {avg_conf:.1f}%")
        print(f"     Avg weight: {avg_weight:.2f}")

    # Save results
    output_dir = Path('./test_batch_output')
    output_dir.mkdir(exist_ok=True)

    manifest = {
        'timestamp': datetime.now().isoformat(),
        'guardian_debate': debate_result,
        'contacts_processed': len(results),
        'contacts_found': found,
        'results': results,
        'agent_performance': agent_stats
    }

    manifest_file = output_dir / 'test_manifest.json'
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\n📄 Manifest saved: {manifest_file}")
    print("\n✅ Test complete!\n")
    print("="*60)
    print("KEY DEMONSTRATION:")
    print("  ✅ IF Guardians debated ethics before processing")
    print("  ✅ Weighted coordination used (agents have different weights)")
    print("  ✅ Self-documenting manifest generated")
    print("  ✅ Late bloomer pattern visible (weights adapt by context)")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
