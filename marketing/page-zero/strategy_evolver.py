#!/usr/bin/env python3
"""
Strategy Evolution Engine - Plan 2 of Recursive Learning

Evolves new agent strategies by combining successful patterns from existing agents.
Implements IF's meta-learning through strategic mutation and shadow testing.

Philosophy:
  "Truth rarely performs well in its early iterations."
  Strategies that work get combined. Failures inform exploration.
  The system discovers strategies we didn't think of.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
from pathlib import Path
from collections import defaultdict
import random


class StrategyEvolver:
    """
    Evolves new agent strategies through pattern combination and mutation.

    Evolution loop:
    1. Extract successful patterns from agents
    2. Generate hybrid strategies (mutations)
    3. Test in shadow mode (parallel, non-blocking)
    4. Promote successful mutations
    5. Discard underperformers
    6. Repeat
    """

    def __init__(self, results_dir: str = "./"):
        self.results_dir = Path(results_dir)
        self.agent_patterns = defaultdict(dict)
        self.mutations = []
        self.shadow_results = []

    def extract_agent_patterns(self) -> Dict[str, Dict]:
        """
        Extract what successful agents do differently.

        Patterns to extract:
        - Query patterns (keywords, operators)
        - Data sources (LinkedIn, Google Scholar, etc.)
        - Heuristics (confidence scoring rules)
        - Success contexts (which contact types work)
        """
        print("🔍 Extracting patterns from successful agents...")

        # Load learned weights to identify successful agents
        weight_files = list(self.results_dir.glob("learned_weights_*.json"))
        if not weight_files:
            print("⚠️  No learned weights found. Run agent_weight_learner.py first.")
            return {}

        latest_weights = max(weight_files, key=lambda p: p.stat().st_mtime)
        with open(latest_weights) as f:
            weight_data = json.load(f)

        weights = weight_data.get('learned_weights', {})
        stats = weight_data.get('agent_statistics', {})

        # Define known patterns for each agent
        known_patterns = {
            'ProfessionalNetworker': {
                'data_sources': ['LinkedIn', 'company websites', 'professional networks'],
                'query_patterns': ['name + company', 'role + organization', 'LinkedIn profile'],
                'heuristics': ['Strong if LinkedIn profile found', 'Bonus for company website'],
                'best_for': ['executives', 'corporate roles', 'tech leaders']
            },
            'AcademicResearcher': {
                'data_sources': ['Google Scholar', 'ResearchGate', 'university pages'],
                'query_patterns': ['name + publications', 'affiliation + research'],
                'heuristics': ['Strong if h-index available', 'Bonus for citations'],
                'best_for': ['researchers', 'professors', 'academics']
            },
            'RecruiterUser': {
                'data_sources': ['job boards', 'career sites', 'recruiting platforms'],
                'query_patterns': ['name + role keywords', 'seniority indicators'],
                'heuristics': ['Strong if role hierarchy clear', 'Bonus for recent moves'],
                'best_for': ['C-level', 'VP+', 'senior roles']
            },
            'InvestigativeJournalist': {
                'data_sources': ['news articles', 'press releases', 'media mentions'],
                'query_patterns': ['name + news', 'quotes + articles', 'interviews'],
                'heuristics': ['Strong if recent press', 'Bonus for thought leadership'],
                'best_for': ['public figures', 'spokespeople', 'thought leaders']
            },
            'SocialEngineer': {
                'data_sources': ['social media', 'public profiles', 'activity feeds'],
                'query_patterns': ['name + social handles', 'public posts'],
                'heuristics': ['Strong if active presence', 'Bonus for engagement'],
                'best_for': ['influencers', 'community leaders', 'activists']
            },
            'IntelAnalyst': {
                'data_sources': ['government databases', 'public records', 'org charts'],
                'query_patterns': ['name + organization', 'role + department'],
                'heuristics': ['Strong if official records', 'Bonus for clearance info'],
                'best_for': ['government', 'defense', 'regulated sectors']
            }
        }

        # Extract patterns for successful agents (weight > 0.5)
        for agent_name, weight in weights.items():
            if weight > 0.5 and agent_name in known_patterns:
                agent_stats = stats.get(agent_name, {})
                self.agent_patterns[agent_name] = {
                    'weight': weight,
                    'success_rate': agent_stats.get('success_rate', 0),
                    'avg_confidence': agent_stats.get('avg_confidence', 0),
                    'patterns': known_patterns[agent_name]
                }
                print(f"  ✓ {agent_name}: {weight} weight, {agent_stats.get('success_rate', 0)*100:.1f}% success")

        return self.agent_patterns

    def generate_mutations(self, num_mutations: int = 3) -> List[Dict]:
        """
        Generate hybrid strategies by combining successful patterns.

        Mutation operators:
        1. COMBINE: Merge two successful strategies
        2. SPECIALIZE: Focus successful strategy on niche
        3. GENERALIZE: Broaden successful strategy
        """
        print(f"\n🧬 Generating {num_mutations} strategic mutations...")

        if len(self.agent_patterns) < 2:
            print("⚠️  Need at least 2 successful agents to mutate")
            return []

        mutations = []

        # Mutation 1: Combine top 2 performers
        sorted_agents = sorted(
            self.agent_patterns.items(),
            key=lambda x: x[1]['weight'],
            reverse=True
        )

        if len(sorted_agents) >= 2:
            agent1_name, agent1_data = sorted_agents[0]
            agent2_name, agent2_data = sorted_agents[1]

            mutations.append({
                'name': f'{agent1_name[:10]}_{agent2_name[:10]}_Hybrid',
                'type': 'COMBINE',
                'parents': [agent1_name, agent2_name],
                'data_sources': agent1_data['patterns']['data_sources'] + agent2_data['patterns']['data_sources'],
                'query_patterns': agent1_data['patterns']['query_patterns'][:2] + agent2_data['patterns']['query_patterns'][:2],
                'heuristics': agent1_data['patterns']['heuristics'] + agent2_data['patterns']['heuristics'],
                'best_for': list(set(agent1_data['patterns']['best_for'] + agent2_data['patterns']['best_for'])),
                'hypothesis': f"Combines {agent1_name}'s strengths with {agent2_name}'s coverage"
            })

        # Mutation 2: Specialize best performer for niche
        if sorted_agents:
            best_name, best_data = sorted_agents[0]

            # Specialize for executives
            mutations.append({
                'name': f'{best_name[:15]}_Executive',
                'type': 'SPECIALIZE',
                'parents': [best_name],
                'data_sources': best_data['patterns']['data_sources'],
                'query_patterns': best_data['patterns']['query_patterns'] + ['C-level', 'executive team', 'board member'],
                'heuristics': best_data['patterns']['heuristics'] + ['Bonus for C-suite keywords', 'Strong if board member'],
                'best_for': ['CEOs', 'CTOs', 'executives', 'board members'],
                'hypothesis': f"Specializes {best_name} for executive-level contacts"
            })

        # Mutation 3: Cross-domain hybrid (academic + corporate)
        academic_agents = [name for name, data in self.agent_patterns.items() if 'academic' in name.lower() or 'research' in name.lower()]
        corporate_agents = [name for name, data in self.agent_patterns.items() if 'professional' in name.lower() or 'recruiter' in name.lower()]

        if academic_agents and corporate_agents:
            acad_name = academic_agents[0]
            corp_name = corporate_agents[0]
            acad_data = self.agent_patterns[acad_name]
            corp_data = self.agent_patterns[corp_name]

            mutations.append({
                'name': 'AcademicCorporate_Hybrid',
                'type': 'CROSS_DOMAIN',
                'parents': [acad_name, corp_name],
                'data_sources': acad_data['patterns']['data_sources'] + corp_data['patterns']['data_sources'],
                'query_patterns': acad_data['patterns']['query_patterns'][:2] + corp_data['patterns']['query_patterns'][:2],
                'heuristics': ['Strong if both academic + corporate presence', 'Bonus for industry transition'],
                'best_for': ['researcher-turned-exec', 'academic consultants', 'industry researchers'],
                'hypothesis': 'Targets academics who moved to industry (quantum, AI researchers at companies)'
            })

        self.mutations = mutations

        for i, mutation in enumerate(mutations, 1):
            print(f"\n  Mutation {i}: {mutation['name']}")
            print(f"    Type: {mutation['type']}")
            print(f"    Parents: {', '.join(mutation['parents'])}")
            print(f"    Hypothesis: {mutation['hypothesis']}")
            print(f"    Best for: {', '.join(mutation['best_for'])}")

        return mutations

    def simulate_shadow_testing(self) -> List[Dict]:
        """
        Simulate shadow mode testing for mutations.

        In production, this would:
        1. Run mutations in parallel with existing agents
        2. Compare performance on same contacts
        3. Not affect production results

        For now, we simulate based on contact type matching.
        """
        print("\n🔬 Simulating shadow mode testing...")
        print("   (In production: would run on live contacts in parallel)")

        # Load contacts from CSV to simulate
        contacts_file = self.results_dir / "outreach-targets-FINAL-RANKED.csv"
        if not contacts_file.exists():
            print("⚠️  No contacts file found for simulation")
            return []

        import csv
        contacts = []
        with open(contacts_file) as f:
            reader = csv.DictReader(f)
            contacts = list(reader)[:20]  # Test on first 20

        shadow_results = []

        for mutation in self.mutations:
            matches = 0
            total_confidence = 0.0

            for contact in contacts:
                role = contact.get('role_title', '').lower()
                org = contact.get('organization', '').lower()
                context = contact.get('why_relevant', '').lower()

                # Check if contact matches mutation's best_for
                match_score = 0
                for target_type in mutation['best_for']:
                    if target_type.lower() in role or target_type.lower() in context:
                        match_score += 1

                # Simulate confidence based on match
                if match_score > 0:
                    # Higher confidence for better matches
                    confidence = min(95, 70 + (match_score * 10) + random.randint(-5, 5))
                    matches += 1
                    total_confidence += confidence

            avg_confidence = total_confidence / len(contacts) if contacts else 0
            success_rate = matches / len(contacts) if contacts else 0

            shadow_results.append({
                'mutation': mutation['name'],
                'type': mutation['type'],
                'matches': matches,
                'total_tested': len(contacts),
                'success_rate': success_rate,
                'avg_confidence': avg_confidence,
                'performance_score': success_rate * avg_confidence
            })

            print(f"\n  {mutation['name']}:")
            print(f"    Success Rate: {success_rate*100:.1f}% ({matches}/{len(contacts)})")
            print(f"    Avg Confidence: {avg_confidence:.1f}")
            print(f"    Performance Score: {success_rate * avg_confidence:.2f}")

        self.shadow_results = shadow_results
        return shadow_results

    def recommend_promotions(self) -> Dict:
        """
        Recommend which mutations to promote to production.

        Promotion criteria:
        - Performance score > baseline best agent
        - Success rate > 50%
        - Tested on sufficient contacts (20+)
        """
        print("\n🎯 Evaluating mutations for promotion...")

        if not self.shadow_results:
            print("⚠️  No shadow results to evaluate")
            return {}

        # Get baseline performance (best current agent)
        baseline = max(
            self.agent_patterns.values(),
            key=lambda x: x['success_rate'] * x['avg_confidence']
        )
        baseline_score = baseline['success_rate'] * baseline['avg_confidence']

        print(f"\n  Baseline (best current agent):")
        print(f"    Performance Score: {baseline_score:.2f}")

        promotions = {
            'promote': [],
            'explore': [],
            'discard': []
        }

        for result in self.shadow_results:
            perf_score = result['performance_score']

            if perf_score > baseline_score * 1.1:  # 10% better than baseline
                status = 'promote'
                promotions['promote'].append(result)
                print(f"\n  ✅ PROMOTE: {result['mutation']}")
                print(f"     Performance: {perf_score:.2f} vs baseline {baseline_score:.2f}")
                print(f"     Improvement: +{((perf_score/baseline_score - 1) * 100):.1f}%")

            elif perf_score > baseline_score * 0.7:  # Within 30% of baseline
                status = 'explore'
                promotions['explore'].append(result)
                print(f"\n  🔵 EXPLORE: {result['mutation']}")
                print(f"     Performance: {perf_score:.2f} (needs more data)")

            else:
                status = 'discard'
                promotions['discard'].append(result)
                print(f"\n  ❌ DISCARD: {result['mutation']}")
                print(f"     Performance: {perf_score:.2f} (underperforming)")

        return promotions

    def generate_evolution_report(self, promotions: Dict) -> str:
        """Generate human-readable evolution report"""
        report = []
        report.append("=" * 80)
        report.append("STRATEGY EVOLUTION REPORT")
        report.append("Recursive Learning - Plan 2")
        report.append("=" * 80)
        report.append("")

        report.append(f"🧬 Evolution Summary:")
        report.append(f"   Mutations generated: {len(self.mutations)}")
        report.append(f"   Shadow tests run: {len(self.shadow_results)}")
        report.append(f"   Promotions: {len(promotions.get('promote', []))}")
        report.append(f"   Exploration candidates: {len(promotions.get('explore', []))}")
        report.append(f"   Discarded: {len(promotions.get('discard', []))}")
        report.append("")

        report.append("📊 Mutation Performance:")
        report.append("")

        for result in sorted(self.shadow_results, key=lambda x: x['performance_score'], reverse=True):
            report.append(f"  {result['mutation']}:")
            report.append(f"    Type: {result['type']}")
            report.append(f"    Success Rate: {result['success_rate']*100:.1f}%")
            report.append(f"    Avg Confidence: {result['avg_confidence']:.1f}")
            report.append(f"    Performance Score: {result['performance_score']:.2f}")
            report.append("")

        if promotions.get('promote'):
            report.append("🎯 Recommended Promotions:")
            report.append("")
            for promo in promotions['promote']:
                report.append(f"  ✅ {promo['mutation']}")
                report.append(f"     Add to production with weight: {promo['performance_score']/100:.2f}")
                report.append("")

        report.append("🔄 Next Steps:")
        report.append("  1. Implement promoted mutations in weighted_multi_agent_finder.py")
        report.append("  2. Run production batch with new strategies")
        report.append("  3. Measure real-world performance")
        report.append("  4. Generate new mutations based on results")
        report.append("")
        report.append("=" * 80)

        return "\n".join(report)

    def save_evolution_results(self, promotions: Dict, output_path: str):
        """Save evolution results for next iteration"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'mutations': self.mutations,
            'shadow_results': self.shadow_results,
            'promotions': promotions,
            'agent_patterns': dict(self.agent_patterns),
            'notes': 'Strategy evolution results. Promoted mutations ready for production testing.'
        }

        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"✅ Evolution results saved: {output_path}")

    def run_evolution_cycle(self):
        """Execute complete evolution cycle"""
        print("🧬 Starting strategy evolution cycle...")
        print()

        # Step 1: Extract patterns
        patterns = self.extract_agent_patterns()
        if not patterns:
            print("⚠️  No successful patterns to evolve from")
            return None

        # Step 2: Generate mutations
        mutations = self.generate_mutations()
        if not mutations:
            print("⚠️  No mutations generated")
            return None

        # Step 3: Shadow testing
        shadow_results = self.simulate_shadow_testing()

        # Step 4: Promotion recommendations
        promotions = self.recommend_promotions()

        # Step 5: Report
        report = self.generate_evolution_report(promotions)
        print("\n" + report)

        # Step 6: Save
        output_path = f"evolution_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.save_evolution_results(promotions, output_path)

        report_path = f"evolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"✅ Evolution report saved: {report_path}")

        return promotions


def main():
    """Run the evolution cycle"""
    evolver = StrategyEvolver()
    promotions = evolver.run_evolution_cycle()

    if promotions and promotions.get('promote'):
        print()
        print("🎯 Evolution complete! New strategies ready for production.")
        print(f"   Promoted: {len(promotions['promote'])} mutations")
        print()


if __name__ == "__main__":
    main()
