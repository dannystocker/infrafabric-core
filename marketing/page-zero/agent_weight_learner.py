#!/usr/bin/env python3
"""
Agent Weight Learning - Recursive Improvement

Analyzes historical agent performance and adjusts weights for future runs.
This implements IF's recursive learning at the agent level.

Philosophy:
  "Truth rarely performs well in its early iterations."
  Agents that consistently succeed earn more influence.
  Agents that fail gracefully maintain exploration budget.
"""

import json
import os
from datetime import datetime
from typing import Dict, List
from pathlib import Path
from collections import defaultdict


class AgentWeightLearner:
    """
    Learns optimal agent weights from historical performance.

    Recursive learning loop:
    1. Analyze past runs
    2. Compute success patterns
    3. Adjust weights
    4. Apply to next run
    5. Measure improvement
    6. Repeat
    """

    def __init__(self, results_dir: str = "./"):
        self.results_dir = Path(results_dir)
        self.history = []
        self.agent_stats = defaultdict(lambda: {
            'attempts': 0,
            'successes': 0,
            'total_confidence': 0.0,
            'failures': 0,
            'avg_confidence': 0.0,
            'success_rate': 0.0,
            'contribution_score': 0.0
        })

    def load_historical_runs(self) -> int:
        """Load all previous run manifests"""
        manifests = list(self.results_dir.glob("run-*-manifest.json"))
        batch_summaries = list(self.results_dir.glob("**/batch_summary.json"))

        print(f"📊 Loading historical data...")
        print(f"   Found {len(manifests)} run manifests")
        print(f"   Found {len(batch_summaries)} batch summaries")

        for manifest_path in manifests:
            try:
                with open(manifest_path) as f:
                    data = json.load(f)
                    self.history.append({
                        'timestamp': data.get('timestamp'),
                        'results': data.get('results', []),
                        'source': str(manifest_path)
                    })
            except Exception as e:
                print(f"   ⚠️  Failed to load {manifest_path}: {e}")

        for summary_path in batch_summaries:
            try:
                with open(summary_path) as f:
                    data = json.load(f)
                    if 'agent_performance' in data:
                        self.history.append({
                            'timestamp': data.get('timestamp', 'unknown'),
                            'agent_performance': data['agent_performance'],
                            'source': str(summary_path)
                        })
            except Exception as e:
                print(f"   ⚠️  Failed to load {summary_path}: {e}")

        return len(self.history)

    def analyze_agent_performance(self):
        """Analyze each agent's contribution patterns"""
        print(f"\n🔍 Analyzing agent performance across {len(self.history)} runs...")

        for run in self.history:
            # Handle run manifests
            if 'results' in run:
                for result in run['results']:
                    if 'agent_results' in result:
                        for agent_result in result['agent_results']:
                            agent_name = agent_result.get('agent', 'Unknown')
                            confidence = agent_result.get('confidence', 0)

                            stats = self.agent_stats[agent_name]
                            stats['attempts'] += 1
                            stats['total_confidence'] += confidence

                            if confidence >= 70:
                                stats['successes'] += 1
                            else:
                                stats['failures'] += 1

            # Handle batch summaries
            if 'agent_performance' in run:
                for agent_name, perf in run['agent_performance'].items():
                    stats = self.agent_stats[agent_name]
                    stats['attempts'] += perf.get('attempts', 0)
                    stats['successes'] += perf.get('successes', 0)
                    stats['total_confidence'] += perf.get('total_confidence', 0.0)

        # Compute derived metrics
        for agent_name, stats in self.agent_stats.items():
            if stats['attempts'] > 0:
                stats['avg_confidence'] = stats['total_confidence'] / stats['attempts']
                stats['success_rate'] = stats['successes'] / stats['attempts']
                # Contribution score = success_rate * avg_confidence * log(attempts)
                import math
                stats['contribution_score'] = (
                    stats['success_rate'] *
                    stats['avg_confidence'] *
                    math.log(max(stats['attempts'], 1) + 1)
                )

    def compute_learned_weights(self) -> Dict[str, float]:
        """
        Compute new agent weights based on historical performance.

        Strategy:
        - High success rate = higher weight
        - High avg confidence = bonus weight
        - Low attempts = exploration bonus (late bloomer discovery)
        - Zero success = minimum weight (keep exploring)
        """
        weights = {}

        if not self.agent_stats:
            print("⚠️  No agent statistics available")
            return weights

        # Find best performer for normalization
        max_contribution = max(
            (stats['contribution_score'] for stats in self.agent_stats.values()),
            default=1.0
        )

        for agent_name, stats in self.agent_stats.items():
            # Base weight from contribution score
            if max_contribution > 0:
                base_weight = stats['contribution_score'] / max_contribution
            else:
                base_weight = 0.5

            # Late bloomer bonus (exploration encouragement)
            if stats['attempts'] < 10:
                late_bloomer_bonus = 0.3
            else:
                late_bloomer_bonus = 0.0

            # Consistency bonus
            if stats['success_rate'] > 0.5 and stats['attempts'] > 20:
                consistency_bonus = 0.2
            else:
                consistency_bonus = 0.0

            # Minimum exploration weight
            min_weight = 0.1

            # Final weight
            final_weight = max(
                min_weight,
                base_weight + late_bloomer_bonus + consistency_bonus
            )

            weights[agent_name] = round(final_weight, 2)

        return weights

    def generate_learning_report(self, weights: Dict[str, float]) -> str:
        """Generate human-readable learning report"""
        report = []
        report.append("=" * 80)
        report.append("RECURSIVE LEARNING REPORT")
        report.append("Agent Weight Learning - Historical Analysis")
        report.append("=" * 80)
        report.append("")

        report.append(f"📚 Historical Data:")
        report.append(f"   Runs analyzed: {len(self.history)}")
        report.append(f"   Agents tracked: {len(self.agent_stats)}")
        report.append("")

        report.append("📊 Agent Performance (Sorted by Contribution):")
        report.append("")

        # Sort by contribution score
        sorted_agents = sorted(
            self.agent_stats.items(),
            key=lambda x: x[1]['contribution_score'],
            reverse=True
        )

        for agent_name, stats in sorted_agents:
            learned_weight = weights.get(agent_name, 0.0)

            report.append(f"  {agent_name}:")
            report.append(f"    Attempts: {stats['attempts']}")
            report.append(f"    Success Rate: {stats['success_rate']*100:.1f}%")
            report.append(f"    Avg Confidence: {stats['avg_confidence']:.1f}")
            report.append(f"    Contribution Score: {stats['contribution_score']:.2f}")
            report.append(f"    → Learned Weight: {learned_weight}")
            report.append("")

        report.append("🎯 Weight Changes (Learning Outcome):")
        report.append("")

        # Show weight recommendations
        for agent_name in sorted(weights.keys()):
            weight = weights[agent_name]
            stats = self.agent_stats[agent_name]

            if weight > 0.8:
                status = "🟢 HIGH (dominant contributor)"
            elif weight > 0.5:
                status = "🟡 MEDIUM (valuable contributor)"
            elif weight > 0.3:
                status = "🔵 LOW (exploratory contributor)"
            else:
                status = "⚪ MINIMAL (keep for diversity)"

            report.append(f"  {agent_name}: {weight} - {status}")

        report.append("")
        report.append("💡 Insights:")
        report.append("")

        # Generate insights
        best_agent = max(self.agent_stats.items(), key=lambda x: x[1]['contribution_score'])
        worst_agent = min(self.agent_stats.items(), key=lambda x: x[1]['contribution_score'])

        report.append(f"  • Best performer: {best_agent[0]} ({best_agent[1]['success_rate']*100:.1f}% success)")
        report.append(f"  • Needs improvement: {worst_agent[0]} ({worst_agent[1]['success_rate']*100:.1f}% success)")

        # Late bloomer detection
        late_bloomers = [
            name for name, stats in self.agent_stats.items()
            if stats['attempts'] < 10 and stats['success_rate'] > 0.3
        ]
        if late_bloomers:
            report.append(f"  • Late bloomers (high potential): {', '.join(late_bloomers)}")

        report.append("")
        report.append("🔄 Next Steps:")
        report.append("  1. Apply learned weights to next run")
        report.append("  2. Measure improvement (delta vs baseline)")
        report.append("  3. Iterate weights based on new results")
        report.append("  4. Gradually reduce underperforming agent budget")
        report.append("")
        report.append("=" * 80)

        return "\n".join(report)

    def save_learned_weights(self, weights: Dict[str, float], output_path: str):
        """Save learned weights for next run"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'learning_iteration': len(self.history),
            'learned_weights': weights,
            'agent_statistics': dict(self.agent_stats),
            'notes': 'Weights learned from historical performance. Apply to next run.'
        }

        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"✅ Learned weights saved: {output_path}")

    def run_learning_cycle(self):
        """Execute complete learning cycle"""
        print("🔄 Starting recursive learning cycle...")
        print()

        # Step 1: Load history
        num_runs = self.load_historical_runs()
        if num_runs == 0:
            print("⚠️  No historical data found. Nothing to learn from yet.")
            return None

        print(f"✅ Loaded {num_runs} historical runs")

        # Step 2: Analyze
        self.analyze_agent_performance()

        # Step 3: Learn weights
        weights = self.compute_learned_weights()

        # Step 4: Report
        report = self.generate_learning_report(weights)
        print(report)

        # Step 5: Save
        output_path = f"learned_weights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.save_learned_weights(weights, output_path)

        # Save report
        report_path = f"learning_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"✅ Learning report saved: {report_path}")

        return weights


def main():
    """Run the learning cycle"""
    learner = AgentWeightLearner()
    weights = learner.run_learning_cycle()

    if weights:
        print()
        print("🎯 Learned weights ready for next run!")
        print("   Apply these weights in weighted_multi_agent_finder.py")
        print()


if __name__ == "__main__":
    main()
