#!/usr/bin/env python3
"""
Meta-Learning Dashboard - Plan 4 of Recursive Learning

Visualizes learning progress and tracks meta-metrics about the learning process itself.
Implements IF's self-awareness through learning velocity and confidence calibration.

Philosophy:
  "Truth rarely performs well in its early iterations."
  The system doesn't just learn - it explains what it learned.
  Learning about learning enables better learning.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
from pathlib import Path
from collections import defaultdict
import statistics


class MetaLearningDashboard:
    """
    Tracks and visualizes meta-learning metrics.

    Meta-learning metrics:
    1. Learning curves (performance over time)
    2. Agent weight evolution
    3. Learning velocity (delta per iteration)
    4. Confidence calibration (prediction accuracy)
    5. Plateau detection (diminishing returns)
    """

    def __init__(self, results_dir: str = "./"):
        self.results_dir = Path(results_dir)
        self.learning_history = []
        self.meta_metrics = {}

    def load_learning_history(self) -> int:
        """Load all learning artifacts chronologically"""
        print("📊 Loading learning history...")

        # Load agent weight learning results
        weight_files = list(self.results_dir.glob("learned_weights_*.json"))
        for wf in sorted(weight_files, key=lambda p: p.stat().st_mtime):
            try:
                with open(wf) as f:
                    data = json.load(f)
                    self.learning_history.append({
                        'type': 'agent_weights',
                        'timestamp': data.get('timestamp'),
                        'iteration': data.get('learning_iteration', 0),
                        'weights': data.get('learned_weights', {}),
                        'stats': data.get('agent_statistics', {}),
                        'source': str(wf)
                    })
            except Exception as e:
                print(f"   ⚠️  Failed to load {wf}: {e}")

        # Load strategy evolution results
        evolution_files = list(self.results_dir.glob("evolution_results_*.json"))
        for ef in sorted(evolution_files, key=lambda p: p.stat().st_mtime):
            try:
                with open(ef) as f:
                    data = json.load(f)
                    self.learning_history.append({
                        'type': 'strategy_evolution',
                        'timestamp': data.get('timestamp'),
                        'mutations': data.get('mutations', []),
                        'shadow_results': data.get('shadow_results', []),
                        'promotions': data.get('promotions', {}),
                        'source': str(ef)
                    })
            except Exception as e:
                print(f"   ⚠️  Failed to load {ef}: {e}")

        # Load bug pattern learning results
        bug_files = list(self.results_dir.glob("bug_patterns_*.json"))
        for bf in sorted(bug_files, key=lambda p: p.stat().st_mtime):
            try:
                with open(bf) as f:
                    data = json.load(f)
                    self.learning_history.append({
                        'type': 'bug_patterns',
                        'timestamp': data.get('timestamp'),
                        'patterns': data.get('bug_patterns', []),
                        'vulnerabilities': data.get('vulnerabilities', []),
                        'tests': data.get('defensive_tests', []),
                        'source': str(bf)
                    })
            except Exception as e:
                print(f"   ⚠️  Failed to load {bf}: {e}")

        # Load execution results for baseline performance
        manifest_files = list(self.results_dir.glob("run-*-manifest.json"))
        for mf in sorted(manifest_files, key=lambda p: p.stat().st_mtime):
            try:
                with open(mf) as f:
                    data = json.load(f)
                    self.learning_history.append({
                        'type': 'execution',
                        'timestamp': data.get('timestamp'),
                        'total_contacts': data.get('total_contacts', 0),
                        'success_rate': data.get('success_rate', 0),
                        'source': str(mf)
                    })
            except Exception as e:
                print(f"   ⚠️  Failed to load {mf}: {e}")

        # Sort chronologically
        self.learning_history.sort(key=lambda x: x.get('timestamp', ''))

        print(f"   Loaded {len(self.learning_history)} learning artifacts")
        return len(self.learning_history)

    def generate_learning_curves(self) -> Dict:
        """
        Generate learning curves showing improvement over time.

        Tracks:
        - Success rate progression
        - Agent weight changes
        - Strategy diversity
        """
        print("\n📈 Generating learning curves...")

        curves = {
            'agent_weights': defaultdict(list),
            'execution_performance': [],
            'strategy_diversity': []
        }

        for entry in self.learning_history:
            timestamp = entry.get('timestamp', 'unknown')

            if entry['type'] == 'agent_weights':
                for agent, weight in entry.get('weights', {}).items():
                    curves['agent_weights'][agent].append({
                        'timestamp': timestamp,
                        'weight': weight
                    })

            elif entry['type'] == 'execution':
                curves['execution_performance'].append({
                    'timestamp': timestamp,
                    'success_rate': entry.get('success_rate', 0)
                })

            elif entry['type'] == 'strategy_evolution':
                curves['strategy_diversity'].append({
                    'timestamp': timestamp,
                    'num_strategies': len(entry.get('mutations', [])),
                    'promotions': len(entry.get('promotions', {}).get('promote', []))
                })

        print(f"   Agent weight trajectories: {len(curves['agent_weights'])}")
        print(f"   Execution data points: {len(curves['execution_performance'])}")
        print(f"   Strategy evolution points: {len(curves['strategy_diversity'])}")

        return curves

    def measure_learning_velocity(self) -> Dict:
        """
        Measure how fast the system is improving.

        Metrics:
        - Delta success per iteration
        - Time to convergence
        - Plateau detection
        """
        print("\n⚡ Measuring learning velocity...")

        # Get execution performance over time
        executions = [e for e in self.learning_history if e['type'] == 'execution']

        if len(executions) < 2:
            print("   ⚠️  Need at least 2 executions to measure velocity")
            return {}

        velocities = []
        for i in range(1, len(executions)):
            prev_success = executions[i-1].get('success_rate', 0)
            curr_success = executions[i].get('success_rate', 0)
            delta = curr_success - prev_success
            velocities.append(delta)

        avg_velocity = statistics.mean(velocities) if velocities else 0
        is_plateau = all(abs(v) < 0.01 for v in velocities[-2:]) if len(velocities) >= 2 else False

        velocity_metrics = {
            'deltas': velocities,
            'avg_velocity': avg_velocity,
            'is_plateau': is_plateau,
            'num_iterations': len(executions),
            'total_improvement': executions[-1].get('success_rate', 0) - executions[0].get('success_rate', 0)
        }

        print(f"   Average velocity: {avg_velocity*100:+.2f}% per iteration")
        print(f"   Total improvement: {velocity_metrics['total_improvement']*100:+.2f}%")
        print(f"   Plateau detected: {is_plateau}")

        return velocity_metrics

    def analyze_confidence_calibration(self) -> Dict:
        """
        Analyze how well the system predicts its own performance.

        Calibration metrics:
        - Predicted vs actual performance
        - Confidence interval accuracy
        - Uncertainty quantification
        """
        print("\n🎯 Analyzing confidence calibration...")

        # For now, we don't have explicit predictions in history
        # But we can measure agent confidence vs actual success

        calibration = {
            'agent_calibration': {},
            'overall_calibration': 'UNKNOWN'
        }

        # Get agent statistics from weight learning
        weight_entries = [e for e in self.learning_history if e['type'] == 'agent_weights']

        if weight_entries:
            latest_weights = weight_entries[-1]
            stats = latest_weights.get('stats', {})

            for agent, agent_stats in stats.items():
                if isinstance(agent_stats, dict):
                    avg_confidence = agent_stats.get('avg_confidence', 0)
                    success_rate = agent_stats.get('success_rate', 0) * 100  # Scale to 0-100

                    # Well-calibrated if confidence ≈ success_rate
                    calibration_error = abs(avg_confidence - success_rate)

                    if calibration_error < 10:
                        calibration_status = 'WELL CALIBRATED'
                    elif calibration_error < 20:
                        calibration_status = 'MODERATELY CALIBRATED'
                    else:
                        calibration_status = 'POORLY CALIBRATED'

                    calibration['agent_calibration'][agent] = {
                        'avg_confidence': avg_confidence,
                        'actual_success': success_rate,
                        'error': calibration_error,
                        'status': calibration_status
                    }

        print(f"   Analyzed {len(calibration['agent_calibration'])} agents")
        well_calibrated = sum(1 for c in calibration['agent_calibration'].values() if 'WELL' in c['status'])
        print(f"   Well-calibrated agents: {well_calibrated}/{len(calibration['agent_calibration'])}")

        return calibration

    def detect_diminishing_returns(self) -> Dict:
        """
        Detect when learning improvements are slowing down.

        Helps decide when to:
        - Stop iterating (plateau reached)
        - Try new approaches (stuck in local optimum)
        - Declare success (good enough)
        """
        print("\n📉 Detecting diminishing returns...")

        velocity = self.measure_learning_velocity()

        diminishing = {
            'detected': False,
            'recommendation': 'CONTINUE',
            'reasoning': ''
        }

        if not velocity:
            diminishing['reasoning'] = 'Insufficient data to detect diminishing returns'
            return diminishing

        recent_deltas = velocity['deltas'][-3:] if len(velocity['deltas']) >= 3 else velocity['deltas']

        # Diminishing returns if recent improvements < 1%
        if all(abs(d) < 0.01 for d in recent_deltas):
            diminishing['detected'] = True
            diminishing['recommendation'] = 'STOP'
            diminishing['reasoning'] = 'Plateau reached - improvements < 1% for last 3 iterations'
        elif velocity['avg_velocity'] < 0.02:  # < 2% avg improvement
            diminishing['detected'] = True
            diminishing['recommendation'] = 'TRY_NEW_APPROACH'
            diminishing['reasoning'] = 'Slow progress - consider new strategies or mutations'
        else:
            diminishing['detected'] = False
            diminishing['recommendation'] = 'CONTINUE'
            diminishing['reasoning'] = f'Strong learning signal - avg {velocity["avg_velocity"]*100:.1f}% per iteration'

        print(f"   Diminishing returns: {diminishing['detected']}")
        print(f"   Recommendation: {diminishing['recommendation']}")
        print(f"   Reasoning: {diminishing['reasoning']}")

        return diminishing

    def generate_dashboard_report(self, curves: Dict, velocity: Dict, calibration: Dict, diminishing: Dict) -> str:
        """Generate comprehensive meta-learning dashboard"""
        report = []
        report.append("=" * 80)
        report.append("META-LEARNING DASHBOARD")
        report.append("Recursive Learning - Plan 4")
        report.append("=" * 80)
        report.append("")

        report.append(f"📚 Learning History:")
        report.append(f"   Total artifacts: {len(self.learning_history)}")
        report.append(f"   Agent weight updates: {len([e for e in self.learning_history if e['type'] == 'agent_weights'])}")
        report.append(f"   Strategy evolutions: {len([e for e in self.learning_history if e['type'] == 'strategy_evolution'])}")
        report.append(f"   Bug learning cycles: {len([e for e in self.learning_history if e['type'] == 'bug_patterns'])}")
        report.append(f"   Executions tracked: {len([e for e in self.learning_history if e['type'] == 'execution'])}")
        report.append("")

        # Learning curves section
        report.append("📈 Learning Curves:")
        report.append("")

        # Agent weight evolution
        if curves.get('agent_weights'):
            report.append("  Agent Weight Evolution:")
            for agent, trajectory in sorted(curves['agent_weights'].items()):
                if len(trajectory) > 0:
                    first_weight = trajectory[0]['weight']
                    last_weight = trajectory[-1]['weight']
                    change = last_weight - first_weight
                    trend = "↗" if change > 0 else "↘" if change < 0 else "→"

                    report.append(f"    {agent}: {first_weight:.2f} → {last_weight:.2f} {trend}")
            report.append("")

        # Execution performance
        if curves.get('execution_performance'):
            report.append("  Execution Performance:")
            for i, perf in enumerate(curves['execution_performance'], 1):
                report.append(f"    Run {i}: {perf['success_rate']*100:.1f}% success")
            report.append("")

        # Learning velocity section
        if velocity:
            report.append("⚡ Learning Velocity:")
            report.append(f"   Average improvement: {velocity.get('avg_velocity', 0)*100:+.2f}% per iteration")
            report.append(f"   Total improvement: {velocity.get('total_improvement', 0)*100:+.2f}%")
            report.append(f"   Iterations: {velocity.get('num_iterations', 0)}")

            if velocity.get('deltas'):
                report.append("")
                report.append("  Iteration-by-iteration deltas:")
                for i, delta in enumerate(velocity['deltas'], 1):
                    report.append(f"    Iteration {i}→{i+1}: {delta*100:+.2f}%")
            report.append("")

        # Confidence calibration section
        if calibration.get('agent_calibration'):
            report.append("🎯 Confidence Calibration:")
            report.append("")

            for agent, cal in sorted(calibration['agent_calibration'].items()):
                report.append(f"  {agent}:")
                report.append(f"    Predicted (avg confidence): {cal['avg_confidence']:.1f}%")
                report.append(f"    Actual (success rate): {cal['actual_success']:.1f}%")
                report.append(f"    Calibration error: {cal['error']:.1f}%")
                report.append(f"    Status: {cal['status']}")
                report.append("")

        # Diminishing returns section
        if diminishing:
            report.append("📉 Diminishing Returns Analysis:")
            report.append(f"   Detected: {diminishing.get('detected', False)}")
            report.append(f"   Recommendation: {diminishing.get('recommendation', 'UNKNOWN')}")
            report.append(f"   Reasoning: {diminishing.get('reasoning', 'N/A')}")
            report.append("")

        # Meta-insights section
        report.append("💡 Meta-Learning Insights:")
        report.append("")

        if velocity and velocity.get('avg_velocity', 0) > 0.05:
            report.append("  ✓ Strong learning signal - system is improving rapidly")
        elif velocity and 0.01 < velocity.get('avg_velocity', 0) <= 0.05:
            report.append("  ⚠️  Moderate learning - improvements slowing down")
        elif velocity and velocity.get('avg_velocity', 0) <= 0.01:
            report.append("  ⚠️  Weak learning signal - consider new approaches")

        well_calibrated = sum(1 for c in calibration.get('agent_calibration', {}).values() if 'WELL' in c.get('status', ''))
        total_agents = len(calibration.get('agent_calibration', {}))
        if total_agents > 0:
            if well_calibrated / total_agents > 0.7:
                report.append("  ✓ Good calibration - agents know what they're good at")
            else:
                report.append("  ⚠️  Poor calibration - agents over/under-confident")

        report.append("")

        report.append("🔄 Recommended Next Actions:")
        report.append("")

        if diminishing.get('recommendation') == 'STOP':
            report.append("  1. Plateau reached - current approach optimized")
            report.append("  2. Consider this iteration successful")
            report.append("  3. Document final performance for baseline")
        elif diminishing.get('recommendation') == 'TRY_NEW_APPROACH':
            report.append("  1. Try new strategy mutations (see Plan 2)")
            report.append("  2. Explore different agent combinations")
            report.append("  3. Consider meta-reframing for stuck contacts")
        else:  # CONTINUE
            report.append("  1. Continue current learning approach")
            report.append("  2. Run next iteration with learned weights")
            report.append("  3. Expect continued improvement")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)

    def save_meta_metrics(self, output_path: str):
        """Save meta-learning metrics for tracking"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'learning_history': self.learning_history,
            'meta_metrics': self.meta_metrics,
            'notes': 'Meta-learning dashboard results. Tracks learning about learning.'
        }

        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"✅ Meta-metrics saved: {output_path}")

    def run_dashboard_cycle(self):
        """Execute complete dashboard generation"""
        print("📊 Starting meta-learning dashboard generation...")
        print()

        # Step 1: Load history
        num_artifacts = self.load_learning_history()
        if num_artifacts == 0:
            print("⚠️  No learning history found. Nothing to visualize yet.")
            return None

        # Step 2: Generate learning curves
        curves = self.generate_learning_curves()

        # Step 3: Measure velocity
        velocity = self.measure_learning_velocity()

        # Step 4: Calibration analysis
        calibration = self.analyze_confidence_calibration()

        # Step 5: Diminishing returns
        diminishing = self.detect_diminishing_returns()

        # Store meta-metrics
        self.meta_metrics = {
            'curves': curves,
            'velocity': velocity,
            'calibration': calibration,
            'diminishing_returns': diminishing
        }

        # Step 6: Generate dashboard
        report = self.generate_dashboard_report(curves, velocity, calibration, diminishing)
        print("\n" + report)

        # Step 7: Save
        output_path = f"meta_learning_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.save_meta_metrics(output_path)

        report_path = f"dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"✅ Dashboard report saved: {report_path}")

        return self.meta_metrics


def main():
    """Run the dashboard generation"""
    dashboard = MetaLearningDashboard()
    metrics = dashboard.run_dashboard_cycle()

    if metrics:
        print()
        print("🎯 Meta-learning dashboard complete!")
        print("   Learning velocity, calibration, and plateau detection analyzed.")
        print()


if __name__ == "__main__":
    main()
