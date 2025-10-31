#!/usr/bin/env python3
"""
Adaptive Weight Policy - Self-Improvement Through Historical Evidence

This closes the self-improvement loop:
1. Load prior manifests (historical evidence)
2. Analyze what worked (which agents succeeded)
3. Update weights (reward success, maintain exploration)
4. Run with adapted policy (improved performance)

Philosophy: "The system improves by learning from its own history"

Key Innovation:
- Static weights → Adaptive weights
- Each run learns from all prior runs
- Agents that consistently succeed get higher base weights
- Failed exploratory agents kept alive (CMP principle)
- Conservative updates (no sudden destabilization)

Author: InfraFabric Research
Date: October 31, 2025
"""

import json
import glob
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class AdaptiveWeightPolicy:
    """
    Learn optimal agent weights from historical manifest data.

    Philosophy: "Evidence shapes policy, policy shapes evidence (recursive improvement)"

    Strategy:
    - Load all prior run manifests
    - Compute per-agent success rates & CMP estimates
    - Adjust base_weight for consistently successful agents
    - Maintain exploration for late bloomers (0.0 weight when failing)
    - Apply conservative update rules (max 20% change per session)
    """

    def __init__(self, manifest_dir: str = ".", min_sample_size: int = 3):
        self.manifest_dir = Path(manifest_dir)
        self.min_sample_size = min_sample_size
        self.historical_data = defaultdict(lambda: {
            'attempts': 0,
            'successes': 0,
            'total_confidence': 0.0,
            'cmp_estimates': [],
            'tier': 'unknown'
        })

    def load_historical_manifests(self) -> List[Dict]:
        """
        Load all prior run manifests.

        Philosophy: "History is the training set for the future"
        """
        manifest_files = glob.glob(str(self.manifest_dir / "run-*-manifest.json"))

        manifests = []
        for filepath in sorted(manifest_files):
            try:
                with open(filepath, 'r') as f:
                    manifest = json.load(f)
                    manifests.append(manifest)
            except Exception as e:
                print(f"⚠️  Failed to load {filepath}: {e}")

        return manifests

    def analyze_agent_performance(self, manifests: List[Dict]) -> Dict:
        """
        Aggregate agent performance across all historical runs.

        Philosophy: "Patterns emerge from repetition, not single observations"
        """
        for manifest in manifests:
            for agent_record in manifest.get('agent_records', []):
                agent_name = agent_record.get('agent_name')
                if not agent_name:
                    continue

                # Aggregate stats
                data = self.historical_data[agent_name]
                data['tier'] = agent_record.get('tier', 'unknown')

                # Count attempts/successes from iteration_stats
                iter_stats = agent_record.get('iteration_stats', [])
                for stat in iter_stats:
                    data['attempts'] += 1
                    perf = stat.get('perf', 0.0)
                    conf = stat.get('confidence', 0.0)

                    if perf > 0.5:  # Success threshold
                        data['successes'] += 1
                    if conf:
                        data['total_confidence'] += conf

                # Track CMP estimates
                cmp = agent_record.get('cmp_estimate', 0.0)
                if cmp:
                    data['cmp_estimates'].append(cmp)

        return dict(self.historical_data)

    def compute_adaptive_weights(self, agent_performance: Dict,
                                 base_profiles: Dict) -> Dict:
        """
        Compute new weight policy based on historical evidence.

        Philosophy: "Amplify proven success, maintain patient exploration"

        Rules:
        1. Baseline agents (tier=baseline): Never reduce below 1.0
        2. Successful specialists: Increase base_weight up to 1.5x
        3. Failed exploratory: Keep at 0.0 (no penalty, maintain exploration)
        4. Late bloomers (improving CMP): Gradual weight increase
        5. Conservative updates: Max 20% change per session
        """
        new_profiles = {}

        for agent_name, base_profile in base_profiles.items():
            new_profile = base_profile.copy()

            # Get historical performance
            perf = agent_performance.get(agent_name)
            if not perf or perf['attempts'] < self.min_sample_size:
                # Insufficient data - keep original weights
                new_profiles[agent_name] = new_profile
                continue

            success_rate = perf['successes'] / perf['attempts']
            avg_cmp = sum(perf['cmp_estimates']) / len(perf['cmp_estimates']) if perf['cmp_estimates'] else 0.0
            tier = perf['tier']

            # Rule 1: Baseline agents (never reduce below 1.0)
            if tier == 'baseline':
                if success_rate > 0.8:
                    # Excellent baseline - slight increase
                    new_base = min(1.2, base_profile['base_weight'] * 1.1)
                    new_profile['base_weight'] = new_base
                    new_profile['adaptation_reason'] = f"Baseline excellence: {success_rate:.1%} success"

            # Rule 2: Successful specialists (increase base_weight)
            elif tier == 'specialist':
                if success_rate > 0.6:
                    # Proven specialist - reward with higher base weight
                    increase_factor = 1.0 + (success_rate - 0.5) * 0.4  # Up to 1.2x
                    new_base = min(1.0, base_profile['base_weight'] * increase_factor)
                    new_profile['base_weight'] = new_base
                    new_profile['adaptation_reason'] = f"Specialist proven: {success_rate:.1%} success"

            # Rule 3: Exploratory agents (maintain exploration)
            elif tier == 'exploratory':
                if success_rate == 0 and avg_cmp < 0.2:
                    # Still failing, no improvement - maintain 0.0 base (no penalty!)
                    new_profile['adaptation_reason'] = "Exploration continues (no penalty)"

                elif avg_cmp > 0.5:
                    # Late bloomer detected! (improving CMP)
                    new_base = min(0.3, base_profile['base_weight'] + 0.1)
                    new_profile['base_weight'] = new_base
                    new_profile['adaptation_reason'] = f"Late bloomer: CMP {avg_cmp:.2f}"

                elif success_rate > 0.3:
                    # Exploratory breakthrough! Significant reward
                    increase_factor = 1.0 + success_rate  # Up to 2.0x
                    new_base = min(0.5, base_profile['base_weight'] * increase_factor)
                    new_profile['base_weight'] = new_base
                    new_profile['adaptation_reason'] = f"Breakthrough: {success_rate:.1%} success"

            # Conservative update (max 20% change)
            if new_profile['base_weight'] != base_profile['base_weight']:
                max_change = base_profile['base_weight'] * 0.2
                delta = new_profile['base_weight'] - base_profile['base_weight']

                if abs(delta) > max_change:
                    new_profile['base_weight'] = base_profile['base_weight'] + (max_change if delta > 0 else -max_change)
                    new_profile['adaptation_reason'] += " (capped at 20% change)"

            new_profiles[agent_name] = new_profile

        return new_profiles

    def generate_adaptation_report(self, old_profiles: Dict,
                                   new_profiles: Dict) -> str:
        """
        Generate human-readable report of weight adaptations.

        Philosophy: "Transparency builds trust in autonomous adaptation"
        """
        report = []
        report.append("# Adaptive Weight Policy Update")
        report.append("")
        report.append("**Philosophy:** *\"The system improves by learning from its own history\"*")
        report.append("")

        changes = []
        no_changes = []

        for agent_name in old_profiles:
            old = old_profiles[agent_name]
            new = new_profiles[agent_name]

            old_weight = old['base_weight']
            new_weight = new['base_weight']

            if abs(new_weight - old_weight) > 0.001:
                delta = new_weight - old_weight
                pct_change = (delta / old_weight * 100) if old_weight > 0 else 0
                reason = new.get('adaptation_reason', 'Evidence-based adjustment')

                changes.append({
                    'agent': agent_name,
                    'old': old_weight,
                    'new': new_weight,
                    'delta': delta,
                    'pct': pct_change,
                    'reason': reason
                })
            else:
                no_changes.append(agent_name)

        # Report changes
        if changes:
            report.append("## Weight Adjustments")
            report.append("")
            report.append("| Agent | Old Weight | New Weight | Change | Reason |")
            report.append("|-------|------------|------------|--------|--------|")

            for change in changes:
                report.append(f"| {change['agent']} | "
                            f"{change['old']:.2f} | "
                            f"{change['new']:.2f} | "
                            f"{change['delta']:+.2f} ({change['pct']:+.0f}%) | "
                            f"{change['reason']} |")
            report.append("")
        else:
            report.append("## No Weight Adjustments")
            report.append("")
            report.append("*Insufficient evidence for changes (need 3+ runs per agent)*")
            report.append("")

        # Report no changes
        if no_changes:
            report.append("## Weights Maintained")
            report.append("")
            report.append(f"**Agents:** {', '.join(no_changes)}")
            report.append("")
            report.append("*These agents showed consistent performance or insufficient data for adjustment.*")
            report.append("")

        return "\n".join(report)

    def adapt(self, base_profiles: Dict) -> tuple[Dict, str]:
        """
        Main adaptation loop: Load history → Analyze → Update weights.

        Philosophy: "Learn, adapt, improve - the cycle of growth"

        Returns:
            (adapted_profiles, adaptation_report)
        """
        print("\n🔄 Adaptive Weight Policy: Learning from history...")

        # Load historical manifests
        manifests = self.load_historical_manifests()
        print(f"   Loaded {len(manifests)} historical runs")

        if len(manifests) == 0:
            print("   No history - using base profiles")
            return base_profiles, "No historical data available"

        # Analyze performance
        agent_perf = self.analyze_agent_performance(manifests)
        print(f"   Analyzed {len(agent_perf)} agents")

        # Compute adaptive weights
        new_profiles = self.compute_adaptive_weights(agent_perf, base_profiles)

        # Generate report
        report = self.generate_adaptation_report(base_profiles, new_profiles)

        # Count changes
        changes = sum(1 for name in base_profiles
                     if abs(new_profiles[name]['base_weight'] -
                           base_profiles[name]['base_weight']) > 0.001)

        print(f"   Adapted {changes} agent weights")
        print("   ✅ Adaptation complete")

        return new_profiles, report


def load_adaptive_profiles(base_profiles: Dict,
                           manifest_dir: str = ".",
                           min_sample_size: int = 3) -> tuple[Dict, str]:
    """
    Convenience function: Load adaptive profiles based on history.

    Usage:
        from adaptive_weight_policy import load_adaptive_profiles

        adapted_profiles, report = load_adaptive_profiles(AGENT_PROFILES)
        # Use adapted_profiles instead of static AGENT_PROFILES
    """
    policy = AdaptiveWeightPolicy(manifest_dir, min_sample_size)
    return policy.adapt(base_profiles)


if __name__ == "__main__":
    print("="*80)
    print("ADAPTIVE WEIGHT POLICY - Self-Improvement Through History")
    print("="*80)
    print("\nPhilosophy:")
    print('  "The system improves by learning from its own history"')
    print("\nHow it works:")
    print("  1. Load all prior run manifests")
    print("  2. Analyze agent performance (success rates, CMP estimates)")
    print("  3. Adapt weights (reward success, maintain exploration)")
    print("  4. Generate transparency report (why each change)")
    print("\nRules:")
    print("  - Baseline agents: Never below 1.0")
    print("  - Successful specialists: Increase base_weight up to 1.5x")
    print("  - Failed exploratory: Keep 0.0 (no penalty!)")
    print("  - Late bloomers: Gradual increase as CMP improves")
    print("  - Conservative: Max 20% change per session")
    print("="*80)
    print("\nReady to enable self-improvement.")
    print("Import load_adaptive_profiles() to use in production.\n")
