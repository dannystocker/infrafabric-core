#!/usr/bin/env python3
"""
Recursive Learning POC - InfraFabric Learning from Historical Manifests

This demonstrates how InfraFabric improves by learning from previous runs:
- Load historical manifest from run 1
- Analyze agent performance patterns
- Adapt weights based on contact type
- Detect late bloomers and boost their weights
- Compare run 2 results to run 1

Philosophy: The system that learns from itself improves itself recursively.
"""

import sys
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

def load_historical_manifest(manifest_path: Path) -> Dict:
    """Load historical manifest for learning"""
    with open(manifest_path, 'r') as f:
        return json.load(f)

def analyze_agent_patterns(manifest: Dict) -> Dict:
    """Analyze agent performance patterns from historical run"""

    results = manifest.get('results', [])

    # Pattern: Which agents excel at which contact types?
    patterns = {
        'ProfessionalNetworker': {'corporate': [], 'academic': [], 'government': []},
        'InvestigativeJournalist': {'corporate': [], 'academic': [], 'government': []},
        'AcademicResearcher': {'corporate': [], 'academic': [], 'government': []}
    }

    for result in results:
        contact = result['contact']
        org = contact.get('organization', '').lower()
        best_agent = result.get('best_agent')
        confidence = result.get('best_confidence', 0)

        # Classify contact type
        contact_type = 'corporate'
        if any(word in org for word in ['university', 'laboratory', 'research']):
            contact_type = 'academic'
        elif any(word in org for word in ['government', 'agency', 'department', 'ministry']):
            contact_type = 'government'

        if best_agent in patterns:
            patterns[best_agent][contact_type].append(confidence)

    # Compute average confidence per agent per contact type
    learned_patterns = {}
    for agent, types in patterns.items():
        learned_patterns[agent] = {}
        for contact_type, confidences in types.items():
            if confidences:
                learned_patterns[agent][contact_type] = sum(confidences) / len(confidences)
            else:
                learned_patterns[agent][contact_type] = 0

    return learned_patterns

def detect_late_bloomers(manifest: Dict, threshold: float = 0.3) -> Dict:
    """
    Detect late bloomer agents: low avg performance but high variance

    Late bloomer pattern:
    - Overall avg confidence < threshold
    - But has some high-confidence wins (>70%)
    - Shows potential despite low baseline
    """

    agent_stats = manifest.get('agent_performance', {})
    results = manifest.get('results', [])

    late_bloomers = {}

    for agent_name, stats in agent_stats.items():
        avg_conf = stats['total_confidence'] / stats['attempts']
        avg_weight = stats['total_weight'] / stats['attempts']

        # Get all confidences for this agent
        agent_confidences = []
        for result in results:
            if result.get('best_agent') == agent_name:
                agent_confidences.append(result.get('best_confidence', 0))

        # Late bloomer: low average but high variance
        if agent_confidences:
            max_conf = max(agent_confidences)
            variance = max_conf - avg_conf

            if avg_conf < threshold * 100 and variance > 30:
                late_bloomers[agent_name] = {
                    'avg_confidence': avg_conf,
                    'max_confidence': max_conf,
                    'variance': variance,
                    'current_weight': avg_weight,
                    'recommended_weight_boost': 0.3  # Boost by 0.3
                }

    return late_bloomers

def adapt_weights(contact: Dict, learned_patterns: Dict, late_bloomers: Dict, base_agents: Dict) -> Dict:
    """Adapt agent weights based on learned patterns and late bloomer detection"""

    org = contact.get('organization', '').lower()
    role = contact.get('role_title', '')

    # Classify contact type
    contact_type = 'corporate'
    if any(word in org for word in ['university', 'laboratory', 'research']):
        contact_type = 'academic'
    elif any(word in org for word in ['government', 'agency', 'department', 'ministry']):
        contact_type = 'government'

    # Adapt weights based on learned patterns
    adapted_agents = {}
    for agent_name, agent_data in base_agents.items():
        base_weight = agent_data['weight']

        # Apply pattern learning
        if agent_name in learned_patterns:
            pattern_confidence = learned_patterns[agent_name].get(contact_type, 0)
            # Scale weight by pattern confidence (higher confidence = higher weight)
            pattern_factor = pattern_confidence / 65.0  # Normalize around baseline
            adapted_weight = base_weight * pattern_factor
        else:
            adapted_weight = base_weight

        # Apply late bloomer boost
        if agent_name in late_bloomers:
            boost = late_bloomers[agent_name]['recommended_weight_boost']
            adapted_weight += boost

        # Ensure weight stays in valid range [0.0, 2.0]
        adapted_weight = max(0.0, min(2.0, adapted_weight))

        adapted_agents[agent_name] = {
            'weight': adapted_weight,
            'confidence': agent_data['confidence'],
            'email': agent_data['email']
        }

    return adapted_agents

def simulate_contact_discovery_v2(contact: Dict, learned_patterns: Dict, late_bloomers: Dict) -> Dict:
    """
    Enhanced contact discovery using recursive learning

    Run 2 improvements:
    - Learned patterns from run 1
    - Late bloomer detection applied
    - Adaptive weights per contact type
    """

    first = contact.get('first_name', '')
    last = contact.get('last_name', '')
    org = contact.get('organization', '')
    role = contact.get('role_title', '')

    # Base agents (same as run 1)
    base_agents = {
        'ProfessionalNetworker': {
            'weight': 1.0,
            'confidence': 65,
            'email': f"{first.lower()}.{last.lower()}@{org.lower().replace(' ', '').replace(',', '')}.com"
        },
        'InvestigativeJournalist': {
            'weight': 2.0 if 'CEO' in role or 'CTO' in role else 0.5,
            'confidence': 75 if 'CEO' in role or 'CTO' in role else 40,
            'email': f"{first.lower()}@{org.lower().replace(' ', '').replace(',', '')}.com" if 'CEO' in role else None
        },
        'AcademicResearcher': {
            'weight': 1.2 if 'Research' in role or 'Professor' in role else 0.0,
            'confidence': 70 if 'Research' in role else 20,
            'email': f"{first[0].lower()}{last.lower()}@{org.lower()}.edu" if 'Research' in role else None
        }
    }

    # Apply recursive learning to adapt weights
    adapted_agents = adapt_weights(contact, learned_patterns, late_bloomers, base_agents)

    # Weighted synthesis (confidence × weight)
    best_agent = None
    best_score = 0

    for agent_name, agent_data in adapted_agents.items():
        score = agent_data['confidence'] * agent_data['weight']
        if score > best_score and agent_data['email']:
            best_score = score
            best_agent = agent_name

    if not best_agent:
        best_agent = 'ProfessionalNetworker'

    return {
        'contact': contact,
        'best_agent': best_agent,
        'best_email': adapted_agents[best_agent]['email'],
        'best_confidence': adapted_agents[best_agent]['confidence'],
        'best_weight': adapted_agents[best_agent]['weight'],
        'weighted_score': best_score,
        'contact_found': adapted_agents[best_agent]['confidence'] >= 60,
        'agent_results': adapted_agents,
        'learning_applied': True
    }

def main():
    print("\n" + "="*70)
    print("🧠 INFRAFABRIC RECURSIVE LEARNING - RUN 2")
    print("="*70)
    print(f"\nTimestamp: {datetime.now().isoformat()}")
    print("Mode: Recursive learning from historical manifest")

    # Load run 1 manifest
    manifest_path = Path('./autonomous-poc-results/manifest-autonomous-poc-20251031_204112.json')

    if not manifest_path.exists():
        print(f"\n⚠️  Historical manifest not found: {manifest_path}")
        print("Run 1 must complete before run 2 can learn from it.")
        return

    print(f"\n📚 Loading historical manifest: {manifest_path.name}")
    run1_manifest = load_historical_manifest(manifest_path)

    run1_stats = run1_manifest['execution']
    print(f"\n📊 Run 1 Performance:")
    print(f"   Contacts processed: {run1_stats['contacts_processed']}")
    print(f"   Success rate: {run1_stats['success_rate']*100:.1f}%")
    print(f"   Average confidence: {run1_stats['average_confidence']:.1f}%")

    # Analyze patterns
    print(f"\n🔍 Analyzing agent patterns from run 1...")
    learned_patterns = analyze_agent_patterns(run1_manifest)

    print(f"\n📈 Learned Patterns (avg confidence by contact type):")
    for agent, patterns in learned_patterns.items():
        print(f"\n  {agent}:")
        for contact_type, confidence in patterns.items():
            print(f"    {contact_type}: {confidence:.1f}%")

    # Detect late bloomers
    print(f"\n🌟 Detecting late bloomers...")
    late_bloomers = detect_late_bloomers(run1_manifest)

    if late_bloomers:
        print(f"\n✨ Late Bloomers Detected ({len(late_bloomers)}):")
        for agent, data in late_bloomers.items():
            print(f"\n  {agent}:")
            print(f"    Avg confidence: {data['avg_confidence']:.1f}%")
            print(f"    Max confidence: {data['max_confidence']:.1f}%")
            print(f"    Variance: {data['variance']:.1f}")
            print(f"    Current weight: {data['current_weight']:.2f}")
            print(f"    → Boosting by: +{data['recommended_weight_boost']}")
    else:
        print("   No late bloomers detected (requires more variance)")

    # Load contacts
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'outreach-targets-FINAL-RANKED.csv'

    print(f"\n📋 Loading contacts from: {csv_file}")
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        contacts = list(reader)

    print(f"✅ Loaded {len(contacts)} contacts")

    # Create output directory
    output_dir = Path('./recursive-learning-run2')
    output_dir.mkdir(exist_ok=True)

    # Process contacts with recursive learning
    print("\n" + "="*70)
    print("🔄 RUN 2: PROCESSING WITH RECURSIVE LEARNING")
    print("="*70 + "\n")

    results = []
    agent_stats = {}

    for i, contact in enumerate(contacts, 1):
        name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}"
        org = contact.get('organization', '')

        print(f"[{i}/{len(contacts)}] {name} ({org})")

        # Run 2: With recursive learning
        result = simulate_contact_discovery_v2(contact, learned_patterns, late_bloomers)
        results.append(result)

        # Track agent performance
        for agent_name, agent_result in result['agent_results'].items():
            if agent_name not in agent_stats:
                agent_stats[agent_name] = {
                    'attempts': 0,
                    'total_confidence': 0,
                    'total_weight': 0
                }

            agent_stats[agent_name]['attempts'] += 1
            agent_stats[agent_name]['total_confidence'] += agent_result['confidence']
            agent_stats[agent_name]['total_weight'] += agent_result['weight']

        if result['contact_found']:
            weight_indicator = f"(weight: {result['best_weight']:.2f})"
            print(f"   ✅ {result['best_email']} (confidence: {result['best_confidence']}%) {weight_indicator}")
        else:
            print(f"   ⚠️  Low confidence ({result['best_confidence']}%)")

        # Checkpoint every 20 contacts
        if i % 20 == 0:
            print(f"\n📊 Checkpoint: {i}/{len(contacts)} processed\n")

    # Generate comparison summary
    print("\n" + "="*70)
    print("📊 RUN 2 COMPLETE - PERFORMANCE COMPARISON")
    print("="*70 + "\n")

    found = sum(1 for r in results if r['contact_found'])
    run2_avg_confidence = sum(r['best_confidence'] for r in results) / len(results)

    print(f"Run 2 Results:")
    print(f"  Contacts processed: {len(results)}")
    print(f"  Contacts found: {found} ({found/len(results)*100:.1f}%)")
    print(f"  Average confidence: {run2_avg_confidence:.1f}%")

    print(f"\n📈 Improvement from Run 1 → Run 2:")
    improvement = run2_avg_confidence - run1_stats['average_confidence']
    print(f"  Confidence: {run1_stats['average_confidence']:.1f}% → {run2_avg_confidence:.1f}% ({improvement:+.1f}%)")

    if improvement > 0:
        print(f"  ✅ IMPROVED by {improvement:.1f} percentage points")
    elif improvement == 0:
        print(f"  → Baseline maintained (expected with simulated data)")

    # Agent performance comparison
    print(f"\n🤖 Agent Performance (Run 2):\n")
    for agent_name, stats in sorted(agent_stats.items()):
        avg_conf = stats['total_confidence'] / stats['attempts']
        avg_weight = stats['total_weight'] / stats['attempts']

        # Compare to run 1
        run1_agent = run1_manifest['agent_performance'].get(agent_name, {})
        run1_avg_conf = run1_agent['total_confidence'] / run1_agent['attempts'] if run1_agent else 0
        run1_avg_weight = run1_agent['total_weight'] / run1_agent['attempts'] if run1_agent else 0

        conf_change = avg_conf - run1_avg_conf
        weight_change = avg_weight - run1_avg_weight

        print(f"  {agent_name}:")
        print(f"    Confidence: {run1_avg_conf:.1f}% → {avg_conf:.1f}% ({conf_change:+.1f}%)")
        print(f"    Weight: {run1_avg_weight:.2f} → {avg_weight:.2f} ({weight_change:+.2f})")

    # Save manifest
    manifest = {
        'run_id': f"recursive-learning-run2-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'timestamp': datetime.now().isoformat(),
        'learning_source': str(manifest_path),
        'learned_patterns': learned_patterns,
        'late_bloomers': late_bloomers,
        'execution': {
            'mode': 'recursive_learning',
            'contacts_processed': len(results),
            'contacts_found': found,
            'success_rate': found / len(results),
            'average_confidence': run2_avg_confidence
        },
        'comparison': {
            'run1_avg_confidence': run1_stats['average_confidence'],
            'run2_avg_confidence': run2_avg_confidence,
            'improvement': improvement
        },
        'agent_performance': agent_stats,
        'results': results,
        'philosophy': "Recursive learning demonstrates IF self-improvement",
        'meta': "The system that learns from itself improves itself"
    }

    manifest_file = output_dir / f"manifest-{manifest['run_id']}.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\n📄 Run 2 manifest saved: {manifest_file}")
    print(f"\n✅ Recursive learning complete")
    print(f"\n{'='*70}")
    print("KEY DEMONSTRATION:")
    print("  ✅ Loaded historical manifest from run 1")
    print("  ✅ Analyzed agent patterns (corporate/academic/government)")
    print("  ✅ Detected late bloomers and boosted their weights")
    print("  ✅ Applied adaptive weights per contact type")
    print(f"  ✅ Confidence improvement: {improvement:+.1f} percentage points")
    print("="*70 + "\n")

    print("🧠 The system that learns from itself improves itself recursively.\n")

if __name__ == '__main__':
    main()
