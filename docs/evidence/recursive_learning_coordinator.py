#!/usr/bin/env python3
"""
Recursive Learning Coordinator - IF-Style Multi-Plan Execution

Coordinates all 4 recursive learning plans with weighted contribution.
Implements IF's multi-agent philosophy at the meta-learning level.

Philosophy:
  "Truth rarely performs well in its early iterations."
  Each learning plan contributes weighted insights.
  Failed exploration doesn't penalize.
  Successful patterns amplified.
  Complete audit trail with IF-Trace.
"""

import json
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


class RecursiveLearningCoordinator:
    """
    Coordinates parallel execution of all 4 recursive learning plans.

    Plans:
    1. Agent Weight Learning (weight: 1.5×) - Direct performance impact
    2. Strategy Evolution (weight: 1.2×) - Discovers new approaches
    3. Bug Pattern Recognition (weight: 1.3×) - Prevents failures
    4. Meta-Learning Dashboard (weight: 1.0×) - Visibility and insight

    Coordination principles:
    - All plans run in parallel
    - Each contributes weighted insights
    - Failures logged but don't block
    - Success amplified through weights
    - Complete provenance tracking
    """

    def __init__(self, results_dir: str = "./"):
        self.results_dir = Path(results_dir)
        self.plan_weights = {
            'agent_weight_learner': 1.5,      # Highest impact
            'bug_pattern_learner': 1.3,       # Prevents costly failures
            'strategy_evolver': 1.2,          # Future potential
            'meta_learning_dashboard': 1.0    # Insight generation
        }
        self.execution_results = {}
        self.manifest = {
            'timestamp': datetime.now().isoformat(),
            'coordinator_version': '1.0',
            'plans_executed': [],
            'weighted_outcomes': {},
            'provenance': []
        }

    def execute_plan(self, plan_name: str, plan_script: str) -> Dict:
        """
        Execute a single learning plan and capture results.

        Returns:
        - success: bool
        - output: str
        - execution_time: float
        - results_file: str (if generated)
        """
        print(f"\n🔄 Executing: {plan_name}")
        print(f"   Script: {plan_script}")
        print(f"   Weight: {self.plan_weights.get(plan_name, 1.0)}×")

        start_time = time.time()

        try:
            # Execute the plan
            result = subprocess.run(
                ['python3', plan_script],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per plan
            )

            execution_time = time.time() - start_time

            # Find generated files (results, reports)
            plan_prefix = plan_script.replace('.py', '')
            result_files = list(self.results_dir.glob(f"{plan_prefix.split('_')[0]}*_{datetime.now().strftime('%Y%m%d')}*.json"))
            report_files = list(self.results_dir.glob(f"{plan_prefix.split('_')[0]}*_{datetime.now().strftime('%Y%m%d')}*.txt"))

            success = result.returncode == 0

            execution_result = {
                'plan': plan_name,
                'success': success,
                'execution_time': execution_time,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'result_files': [str(f) for f in result_files],
                'report_files': [str(f) for f in report_files]
            }

            if success:
                print(f"   ✅ Success ({execution_time:.1f}s)")
                print(f"   📄 Generated {len(result_files)} result files, {len(report_files)} reports")
            else:
                print(f"   ❌ Failed ({execution_time:.1f}s)")
                print(f"   Error: {result.stderr[:200]}")

            return execution_result

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            print(f"   ⏱️  Timeout after {execution_time:.1f}s")

            return {
                'plan': plan_name,
                'success': False,
                'execution_time': execution_time,
                'error': 'Timeout (300s)',
                'result_files': [],
                'report_files': []
            }

        except Exception as e:
            execution_time = time.time() - start_time
            print(f"   ❌ Exception: {e}")

            return {
                'plan': plan_name,
                'success': False,
                'execution_time': execution_time,
                'error': str(e),
                'result_files': [],
                'report_files': []
            }

    def execute_all_plans_parallel(self) -> Dict[str, Dict]:
        """
        Execute all 4 plans in parallel using ThreadPoolExecutor.

        IF-style coordination:
        - All plans run simultaneously
        - Independent failures don't block
        - Results collected and weighted
        """
        print("🚀 Starting parallel execution of all 4 recursive learning plans...")
        print(f"   Total plans: {len(self.plan_weights)}")
        print()

        plans_to_execute = [
            ('agent_weight_learner', 'agent_weight_learner.py'),
            ('strategy_evolver', 'strategy_evolver.py'),
            ('bug_pattern_learner', 'bug_pattern_learner.py'),
            ('meta_learning_dashboard', 'meta_learning_dashboard.py')
        ]

        results = {}

        # Execute in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all plans
            future_to_plan = {
                executor.submit(self.execute_plan, plan_name, script): plan_name
                for plan_name, script in plans_to_execute
            }

            # Collect results as they complete
            for future in as_completed(future_to_plan):
                plan_name = future_to_plan[future]
                try:
                    result = future.result()
                    results[plan_name] = result
                except Exception as e:
                    print(f"❌ {plan_name} raised exception: {e}")
                    results[plan_name] = {
                        'plan': plan_name,
                        'success': False,
                        'error': str(e)
                    }

        self.execution_results = results
        return results

    def compute_weighted_outcomes(self) -> Dict:
        """
        Compute weighted contribution from each plan.

        Weighting formula:
        - Base score: 1.0 if success, 0.0 if failure
        - Time bonus: Faster execution = small bonus
        - Impact multiplier: Plan weight (1.0-1.5×)
        - Insight quality: Based on files generated
        """
        print("\n📊 Computing weighted outcomes...")

        weighted_outcomes = {}
        total_weight = sum(self.plan_weights.values())

        for plan_name, result in self.execution_results.items():
            weight = self.plan_weights.get(plan_name, 1.0)

            # Base score
            base_score = 1.0 if result.get('success', False) else 0.0

            # Time efficiency bonus (faster = small bonus)
            exec_time = result.get('execution_time', 300)
            time_bonus = max(0, (60 - exec_time) / 60) * 0.1  # Max 0.1 bonus

            # Output richness (more files = more insights)
            num_files = len(result.get('result_files', [])) + len(result.get('report_files', []))
            output_bonus = min(0.2, num_files * 0.05)  # Max 0.2 bonus

            # Total score
            raw_score = base_score + time_bonus + output_bonus
            weighted_score = raw_score * weight

            weighted_outcomes[plan_name] = {
                'base_score': base_score,
                'time_bonus': time_bonus,
                'output_bonus': output_bonus,
                'raw_score': raw_score,
                'weight': weight,
                'weighted_score': weighted_score,
                'contribution_pct': (weighted_score / (total_weight * 1.3)) * 100  # 1.3 = max possible score
            }

            status = "✅" if result.get('success') else "❌"
            print(f"   {status} {plan_name}:")
            print(f"      Raw score: {raw_score:.2f}")
            print(f"      Weight: {weight}×")
            print(f"      Weighted score: {weighted_score:.2f}")
            print(f"      Contribution: {weighted_outcomes[plan_name]['contribution_pct']:.1f}%")

        return weighted_outcomes

    def generate_provenance_trace(self) -> List[Dict]:
        """
        Generate IF-Trace style provenance for the coordination.

        Tracks:
        - What ran
        - When it ran
        - What it produced
        - How it contributed
        - Why it matters
        """
        provenance = []

        for plan_name, result in self.execution_results.items():
            trace_entry = {
                'plan': plan_name,
                'timestamp': datetime.now().isoformat(),
                'success': result.get('success', False),
                'execution_time_seconds': result.get('execution_time', 0),
                'outputs': {
                    'result_files': result.get('result_files', []),
                    'report_files': result.get('report_files', [])
                },
                'weight': self.plan_weights.get(plan_name, 1.0),
                'weighted_score': self.manifest['weighted_outcomes'].get(plan_name, {}).get('weighted_score', 0),
                'contribution': self.manifest['weighted_outcomes'].get(plan_name, {}).get('contribution_pct', 0)
            }

            # Add stderr if failed
            if not result.get('success'):
                trace_entry['error'] = result.get('stderr', result.get('error', 'Unknown error'))

            provenance.append(trace_entry)

        return provenance

    def generate_coordination_report(self) -> str:
        """Generate human-readable coordination report"""
        report = []
        report.append("=" * 80)
        report.append("RECURSIVE LEARNING COORDINATION REPORT")
        report.append("IF-Style Multi-Plan Execution")
        report.append("=" * 80)
        report.append("")

        report.append(f"🕐 Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"📋 Plans Executed: {len(self.execution_results)}")
        report.append("")

        # Execution summary
        successes = sum(1 for r in self.execution_results.values() if r.get('success'))
        failures = len(self.execution_results) - successes

        report.append(f"📊 Execution Summary:")
        report.append(f"   Successful: {successes}/{len(self.execution_results)}")
        report.append(f"   Failed: {failures}/{len(self.execution_results)}")
        report.append("")

        # Per-plan results
        report.append("📝 Plan-by-Plan Results:")
        report.append("")

        for plan_name, result in sorted(self.execution_results.items()):
            status = "✅ SUCCESS" if result.get('success') else "❌ FAILED"
            weight = self.plan_weights.get(plan_name, 1.0)
            exec_time = result.get('execution_time', 0)

            report.append(f"  {plan_name}:")
            report.append(f"    Status: {status}")
            report.append(f"    Execution time: {exec_time:.1f}s")
            report.append(f"    Weight: {weight}×")

            if result.get('result_files'):
                report.append(f"    Result files: {len(result['result_files'])}")
                for rf in result['result_files'][:3]:  # First 3
                    report.append(f"      • {Path(rf).name}")

            if result.get('report_files'):
                report.append(f"    Report files: {len(result['report_files'])}")
                for rf in result['report_files'][:3]:
                    report.append(f"      • {Path(rf).name}")

            if not result.get('success'):
                error = result.get('error', result.get('stderr', 'Unknown error'))
                report.append(f"    Error: {error[:100]}")

            report.append("")

        # Weighted outcomes
        report.append("🎯 Weighted Contribution Analysis:")
        report.append("")

        for plan_name, outcome in sorted(
            self.manifest.get('weighted_outcomes', {}).items(),
            key=lambda x: x[1].get('weighted_score', 0),
            reverse=True
        ):
            report.append(f"  {plan_name}:")
            report.append(f"    Weighted score: {outcome['weighted_score']:.2f}")
            report.append(f"    Contribution: {outcome['contribution_pct']:.1f}%")
            report.append(f"    Base score: {outcome['base_score']:.2f}")
            report.append(f"    Time bonus: +{outcome['time_bonus']:.2f}")
            report.append(f"    Output bonus: +{outcome['output_bonus']:.2f}")
            report.append("")

        # Key insights
        report.append("💡 Key Insights:")
        report.append("")

        total_contribution = sum(
            o.get('contribution_pct', 0)
            for o in self.manifest.get('weighted_outcomes', {}).values()
        )

        report.append(f"  • Total weighted contribution: {total_contribution:.1f}%")

        top_contributor = max(
            self.manifest.get('weighted_outcomes', {}).items(),
            key=lambda x: x[1].get('weighted_score', 0),
            default=(None, {})
        )

        if top_contributor[0]:
            report.append(f"  • Top contributor: {top_contributor[0]} ({top_contributor[1].get('contribution_pct', 0):.1f}%)")

        if successes == len(self.execution_results):
            report.append("  ✅ All plans succeeded - full recursive learning cycle complete")
        elif successes > 0:
            report.append(f"  ⚠️  Partial success - {successes}/{len(self.execution_results)} plans completed")
        else:
            report.append("  ❌ All plans failed - investigate errors")

        report.append("")

        # Next steps
        report.append("🔄 Next Steps:")
        report.append("")

        if successes >= 3:
            report.append("  1. Review all generated reports for insights")
            report.append("  2. Apply learned weights to next execution")
            report.append("  3. Implement promoted strategies (if any)")
            report.append("  4. Run defensive tests before production")
            report.append("  5. Monitor meta-learning dashboard for plateau detection")
        else:
            report.append("  1. Investigate failed plans")
            report.append("  2. Fix errors and retry")
            report.append("  3. Ensure all dependencies are installed")

        report.append("")
        report.append("=" * 80)
        report.append("")
        report.append("IF-Trace Manifest: See coordination_manifest_*.json")
        report.append("This execution demonstrated recursive learning at 4 levels simultaneously.")
        report.append("")

        return "\n".join(report)

    def save_manifest(self, output_path: str):
        """Save IF-Trace style manifest"""
        with open(output_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)

        print(f"✅ Coordination manifest saved: {output_path}")

    def run_coordination_cycle(self):
        """Execute complete coordination cycle"""
        print("=" * 80)
        print("RECURSIVE LEARNING COORDINATOR")
        print("IF-Style Parallel Multi-Plan Execution")
        print("=" * 80)
        print()

        start_time = time.time()

        # Step 1: Execute all plans in parallel
        results = self.execute_all_plans_parallel()

        # Step 2: Compute weighted outcomes
        weighted_outcomes = self.compute_weighted_outcomes()
        self.manifest['weighted_outcomes'] = weighted_outcomes

        # Step 3: Generate provenance
        provenance = self.generate_provenance_trace()
        self.manifest['provenance'] = provenance
        self.manifest['plans_executed'] = list(results.keys())

        # Step 4: Generate report
        total_time = time.time() - start_time
        self.manifest['total_execution_time'] = total_time

        report = self.generate_coordination_report()
        print("\n" + report)

        # Step 5: Save manifest and report
        manifest_path = f"coordination_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.save_manifest(manifest_path)

        report_path = f"coordination_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"✅ Coordination report saved: {report_path}")

        print()
        print(f"⏱️  Total coordination time: {total_time:.1f}s")
        print()

        return self.manifest


def main():
    """Run the coordination cycle"""
    coordinator = RecursiveLearningCoordinator()
    manifest = coordinator.run_coordination_cycle()

    successes = sum(1 for r in coordinator.execution_results.values() if r.get('success'))
    total = len(coordinator.execution_results)

    print("🎯 Recursive learning coordination complete!")
    print(f"   Success rate: {successes}/{total} plans")
    print()

    if successes == total:
        print("✅ Full recursive learning cycle achieved!")
        print("   The system has learned at all 4 levels:")
        print("   1. Agent weights optimized")
        print("   2. Strategies evolved")
        print("   3. Bug patterns recognized")
        print("   4. Meta-learning tracked")
        print()


if __name__ == "__main__":
    main()
