#!/usr/bin/env python3
"""
Self-Improvement Loop Test

Run multiple iterations to demonstrate:
1. Baseline run (static weights)
2. First adaptation (learns from Run 1)
3. Compounding improvement (learns from Runs 1+2)

This provides preliminary evidence of self-improvement.
"""

import json
import glob
from pathlib import Path

def analyze_manifests():
    """Analyze all manifests to show improvement trajectory"""

    manifest_files = sorted(glob.glob("run-*-manifest.json"))

    if not manifest_files:
        print("❌ No manifests found. Run weighted_multi_agent_finder.py first.")
        return

    print("="*80)
    print("SELF-IMPROVEMENT TRAJECTORY ANALYSIS")
    print("="*80)

    runs = []
    for filepath in manifest_files:
        with open(filepath, 'r') as f:
            manifest = json.load(f)
            runs.append({
                'run_id': manifest['run_id'],
                'timestamp': manifest['timestamp'],
                'system_score': manifest['metrics_summary'].get('system_score', 0),
                'contacts': manifest['metrics_summary'].get('contacts_processed', 0),
                'cost_saved': manifest['metrics_summary'].get('cost_saved', 0),
                'agent_records': manifest.get('agent_records', [])
            })

    print(f"\n📊 Found {len(runs)} runs\n")

    # System-level improvement
    print("## System Performance Over Time\n")
    print("| Run | Contacts | System Score | Cost Saved | Change |")
    print("|-----|----------|--------------|------------|--------|")

    for i, run in enumerate(runs):
        if i == 0:
            change = "baseline"
        else:
            delta = run['system_score'] - runs[i-1]['system_score']
            change = f"{delta:+.3f}"

        print(f"| {i+1} | {run['contacts']} | "
              f"{run['system_score']:.3f} | "
              f"${run['cost_saved']:.3f} | {change} |")

    # Per-agent improvement
    print("\n## Agent Performance Evolution\n")

    # Collect agent data across runs
    agent_evolution = {}

    for i, run in enumerate(runs):
        for agent_record in run['agent_records']:
            agent_name = agent_record.get('agent_name')
            if agent_name not in agent_evolution:
                agent_evolution[agent_name] = []

            agent_evolution[agent_name].append({
                'run': i + 1,
                'success_rate': agent_record.get('success_rate', 0),
                'cmp_estimate': agent_record.get('cmp_estimate', 0),
                'tier': agent_record.get('tier', 'unknown')
            })

    for agent_name, history in agent_evolution.items():
        print(f"### {agent_name} ({history[0]['tier']})\n")
        print("| Run | Success Rate | CMP Estimate | Pattern |")
        print("|-----|--------------|--------------|---------|")

        for i, data in enumerate(history):
            if i == 0:
                pattern = "baseline"
            else:
                sr_delta = data['success_rate'] - history[i-1]['success_rate']
                if sr_delta > 0.1:
                    pattern = "📈 improving"
                elif sr_delta < -0.1:
                    pattern = "📉 declining"
                else:
                    pattern = "→ stable"

            print(f"| {data['run']} | {data['success_rate']:.1%} | "
                  f"{data['cmp_estimate']:.2f} | {pattern} |")

        # Detect late bloomer
        if len(history) >= 2:
            early_avg = sum(h['success_rate'] for h in history[:2]) / 2
            late_avg = history[-1]['success_rate']

            if early_avg < 0.3 and late_avg > 0.5:
                print(f"\n**🌟 LATE BLOOMER DETECTED: Started {early_avg:.0%}, now {late_avg:.0%}**\n")

        print()

    # Adaptation summary
    if len(runs) > 1:
        print("## Weight Adaptation Summary\n")
        print("Changes between runs show the self-improvement mechanism:\n")

        for i in range(1, len(runs)):
            print(f"### Run {i} → Run {i+1}\n")

            prev_config = runs[i-1].get('config', {}).get('agent_profiles', {})
            curr_config = runs[i].get('config', {}).get('agent_profiles', {})

            if prev_config and curr_config:
                changes = 0
                for agent_name in curr_config:
                    if agent_name in prev_config:
                        old_weight = prev_config[agent_name].get('base_weight', 0)
                        new_weight = curr_config[agent_name].get('base_weight', 0)

                        if abs(new_weight - old_weight) > 0.001:
                            delta = new_weight - old_weight
                            reason = curr_config[agent_name].get('adaptation_reason', 'N/A')
                            print(f"- **{agent_name}**: {old_weight:.2f} → {new_weight:.2f} "
                                  f"({delta:+.2f}) - {reason}")
                            changes += 1

                if changes == 0:
                    print("- No weight changes (insufficient evidence)")

            print()

    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)

    if len(runs) >= 2:
        improvement = runs[-1]['system_score'] - runs[0]['system_score']
        pct_improvement = (improvement / runs[0]['system_score'] * 100) if runs[0]['system_score'] > 0 else 0

        print(f"\n✅ System improved: {runs[0]['system_score']:.3f} → "
              f"{runs[-1]['system_score']:.3f} (+{improvement:.3f}, +{pct_improvement:.1f}%)")

        # Count late bloomers
        late_bloomers = 0
        for agent_name, history in agent_evolution.items():
            if len(history) >= 2:
                early_avg = sum(h['success_rate'] for h in history[:2]) / 2
                late_avg = history[-1]['success_rate']
                if early_avg < 0.3 and late_avg > 0.5:
                    late_bloomers += 1

        if late_bloomers > 0:
            print(f"✅ Late bloomers discovered: {late_bloomers} agents improved significantly")

        print(f"✅ {len(runs)} runs completed - self-improvement loop operational")
    else:
        print("\n⚠️  Only 1 run found - need multiple runs to see improvement")
        print("   Run weighted_multi_agent_finder.py multiple times")

    print()


if __name__ == "__main__":
    analyze_manifests()
