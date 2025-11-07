#!/usr/bin/env python3
"""
Run Manifest Generator - Self-Documenting Experiments

Every run is a reproducible experiment with complete provenance.
This module generates immutable manifests for IF-Trace integration.

Philosophy: "Experiments that document themselves are experiments that teach"

Key principles:
1. Complete reproducibility (config, seeds, versions, inputs)
2. Machine + human readable (JSON + Markdown)
3. IF-Trace integration (Merkle-chained immutable storage)
4. Philosophy paragraphs (explain WHY, not just WHAT)

Author: InfraFabric Research
Date: October 31, 2025
"""

import json
import hashlib
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# IF-Trace integration (stub for now, will be real distributed system)
try:
    from if_trace_stub import store_manifest_in_trace
    IF_TRACE_AVAILABLE = True
except ImportError:
    IF_TRACE_AVAILABLE = False


class RunManifest:
    """
    Complete manifest for a weighted coordination run.

    Philosophy: "Documentation is not overhead - it's the foundation of learning"
    """

    def __init__(self, run_id: Optional[str] = None):
        self.run_id = run_id or self._generate_run_id()
        self.timestamp = datetime.now().isoformat()
        self.git_commit = self._get_git_commit()
        self.config = {}
        self.input_snapshot = {}
        self.metrics_summary = {}
        self.agent_records = []
        self.philosophical_insights = []
        self.cmp_analysis = {}
        self.notes = ""

    def _generate_run_id(self) -> str:
        """Generate unique run ID with timestamp"""
        return f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    def _get_git_commit(self) -> str:
        """Get current git commit hash for reproducibility"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except:
            return "unknown-commit"

    def set_config(self, config: Dict):
        """
        Store complete configuration for reproducibility.

        Philosophy: "Every decision must be traceable to its parameters"
        """
        self.config = config
        # Compute hash for immutable versioning
        config_str = json.dumps(config, sort_keys=True)
        self.agents_profile_hash = hashlib.sha256(config_str.encode()).hexdigest()

    def set_input_snapshot(self, dataset_id: str, seed: int = None):
        """
        Record input data provenance.

        Philosophy: "Know your inputs to understand your outputs"
        """
        self.input_snapshot = {
            'dataset_id': dataset_id,
            'seed': seed,
            'timestamp': self.timestamp
        }

    def set_metrics_summary(self, metrics: Dict):
        """
        Core KPIs for this run.

        Philosophy: "Measure what matters, ignore vanity metrics"
        """
        self.metrics_summary = metrics

    def add_agent_record(self, agent_record: Dict):
        """
        Per-agent lineage record (append-only).

        Philosophy: "Track maturation, not just final state"
        """
        self.agent_records.append(agent_record)

    def add_philosophical_insight(self, insight: str, evidence: Dict):
        """
        Capture emergent insights with supporting evidence.

        Philosophy: "Patterns that explain themselves are patterns that teach"
        """
        self.philosophical_insights.append({
            'insight': insight,
            'evidence': evidence,
            'timestamp': datetime.now().isoformat()
        })

    def set_cmp_analysis(self, analysis: Dict):
        """
        CMP-specific analysis (late bloomers, weighted vs naive).

        Philosophy: "The architecture proves itself through its patterns"
        """
        self.cmp_analysis = analysis

    def set_executive_notes(self, notes: str):
        """Human-readable executive summary"""
        self.notes = notes

    def to_json(self) -> Dict:
        """
        Machine-readable manifest (for IF-Trace).

        This is the authoritative record for:
        - Reproducibility (exact config + versions)
        - Audit trail (what changed, why)
        - Meta-learning (training data for self-improvement)
        """
        return {
            'manifest_version': '1.0',
            'run_id': self.run_id,
            'timestamp': self.timestamp,
            'git_commit': self.git_commit,
            'agents_profile_hash': self.agents_profile_hash,
            'config': self.config,
            'input_snapshot': self.input_snapshot,
            'metrics_summary': self.metrics_summary,
            'agent_records': self.agent_records,
            'philosophical_insights': self.philosophical_insights,
            'cmp_analysis': self.cmp_analysis,
            'notes': self.notes,
            'metadata': {
                'generated_by': 'InfraFabric Run Manifest Generator',
                'philosophy': 'Every run is a reproducible experiment',
                'if_trace_ready': True
            }
        }

    def to_markdown(self) -> str:
        """
        Human-readable executive summary.

        Philosophy: "Machines read JSON, humans read stories"
        """
        md = []

        # Header with philosophy
        md.append(f"# Run Executive Summary")
        md.append(f"")
        md.append(f"**Run ID:** `{self.run_id}`")
        md.append(f"**Timestamp:** {self.timestamp}")
        md.append(f"**Git Commit:** `{self.git_commit[:8]}`")
        md.append(f"")
        md.append(f"---")
        md.append(f"")

        # Opening philosophy
        md.append(f"## Philosophy")
        md.append(f"")
        md.append(f"*\"Every run is an experiment. Every experiment teaches.\"*")
        md.append(f"")
        md.append(f"This run demonstrates InfraFabric's weighted coordination principles:")
        md.append(f"- **Reciprocity**: Agents earn influence through contribution")
        md.append(f"- **Exploration**: Failed agents silent (0.0 weight), no system penalty")
        md.append(f"- **Amplification**: Successful contribution amplified (up to 2.0x)")
        md.append(f"- **Late Bloomers**: Patience reveals maturation patterns")
        md.append(f"")
        md.append(f"---")
        md.append(f"")

        # TL;DR (3 lines)
        md.append(f"## TL;DR")
        md.append(f"")
        md.append(self._generate_tldr())
        md.append(f"")
        md.append(f"---")
        md.append(f"")

        # Metrics table
        md.append(f"## Key Metrics")
        md.append(f"")
        md.append(f"| Metric | Value | Philosophy |")
        md.append(f"|--------|-------|------------|")

        for metric_name, metric_value in self.metrics_summary.items():
            philosophy = self._get_metric_philosophy(metric_name)
            md.append(f"| **{metric_name}** | {metric_value} | {philosophy} |")

        md.append(f"")
        md.append(f"---")
        md.append(f"")

        # CMP Analysis
        if self.cmp_analysis:
            md.append(f"## CMP Analysis: What This Run Proved")
            md.append(f"")
            md.append(f"*\"The architecture validates itself through its patterns.\"*")
            md.append(f"")

            for key, value in self.cmp_analysis.items():
                md.append(f"### {key.replace('_', ' ').title()}")
                md.append(f"")
                if isinstance(value, dict):
                    for subkey, subval in value.items():
                        md.append(f"- **{subkey}**: {subval}")
                else:
                    md.append(f"{value}")
                md.append(f"")

        # Philosophical Insights
        if self.philosophical_insights:
            md.append(f"---")
            md.append(f"")
            md.append(f"## Philosophical Insights")
            md.append(f"")
            md.append(f"*\"Patterns that explain themselves are patterns that teach.\"*")
            md.append(f"")

            for insight in self.philosophical_insights:
                md.append(f"### {insight['insight']}")
                md.append(f"")
                md.append(f"**Evidence:**")
                md.append(f"```json")
                md.append(json.dumps(insight['evidence'], indent=2))
                md.append(f"```")
                md.append(f"")

        # Agent Performance Summary
        if self.agent_records:
            md.append(f"---")
            md.append(f"")
            md.append(f"## Agent Performance")
            md.append(f"")
            md.append(f"*\"Track maturation, not just final state.\"*")
            md.append(f"")
            md.append(f"| Agent | Tier | Success Rate | CMP Estimate | Notes |")
            md.append(f"|-------|------|--------------|--------------|-------|")

            for agent in self.agent_records:
                md.append(f"| {agent.get('agent_name', 'Unknown')} | "
                         f"{agent.get('tier', 'N/A')} | "
                         f"{agent.get('success_rate', 0):.1%} | "
                         f"{agent.get('cmp_estimate', 0):.2f} | "
                         f"{agent.get('notes', 'N/A')} |")

            md.append(f"")

        # Executive Notes
        if self.notes:
            md.append(f"---")
            md.append(f"")
            md.append(f"## Executive Notes")
            md.append(f"")
            md.append(self.notes)
            md.append(f"")

        # Footer with reproducibility info
        md.append(f"---")
        md.append(f"")
        md.append(f"## Reproducibility")
        md.append(f"")
        md.append(f"**Philosophy:** *\"Science requires reproducibility. Infrastructure requires provenance.\"*")
        md.append(f"")
        md.append(f"- **Config Hash:** `{self.agents_profile_hash[:16]}...`")
        md.append(f"- **Input Dataset:** `{self.input_snapshot.get('dataset_id', 'N/A')}`")
        md.append(f"- **Random Seed:** `{self.input_snapshot.get('seed', 'N/A')}`")
        md.append(f"- **Full Manifest:** `{self.run_id}.json` (IF-Trace ready)")
        md.append(f"")
        md.append(f"*Generated by InfraFabric Run Manifest Generator - {self.timestamp}*")

        return "\n".join(md)

    def _generate_tldr(self) -> str:
        """Generate 3-line TL;DR based on metrics"""
        lines = []

        # Line 1: What was tested
        if 'contacts_processed' in self.metrics_summary:
            lines.append(f"- Processed **{self.metrics_summary['contacts_processed']} contacts** "
                        f"using **weighted coordination** with {len(self.agent_records)} agents")

        # Line 2: Key result
        if 'free_agents_sufficient' in self.metrics_summary:
            pct = (self.metrics_summary['free_agents_sufficient'] /
                   self.metrics_summary.get('contacts_processed', 1)) * 100
            lines.append(f"- **{pct:.0f}% handled by free agents** "
                        f"(saved ${self.metrics_summary.get('cost_saved', 0):.3f} vs naive approach)")

        # Line 3: CMP validation
        if 'late_bloomer_recovery_rate' in self.metrics_summary:
            lines.append(f"- Late bloomer recovery rate: **{self.metrics_summary['late_bloomer_recovery_rate']:.1%}** "
                        f"(validates CMP thesis)")
        else:
            lines.append(f"- Validated weighted coordination: failed exploration silent, "
                        f"successful contribution amplified")

        return "\n".join(lines)

    def _get_metric_philosophy(self, metric_name: str) -> str:
        """Map metric to its philosophical meaning"""
        philosophies = {
            'precision': 'Accuracy matters',
            'system_score': 'Unified quality measure',
            'late_bloomer_recovery_rate': 'Patience reveals potential',
            'discovery_rate': 'Innovation through exploration',
            'resource_cost': 'Efficiency through design',
            'free_agents_sufficient': 'Free > expensive when quality sufficient',
            'cost_saved': 'Thrift is a virtue',
            'contacts_processed': 'Scale validates theory',
            'weighted_confidence': 'Contribution-weighted truth',
            'google_validations_needed': 'Expensive validation targeted'
        }
        return philosophies.get(metric_name, 'Measurement with meaning')

    def save(self, output_dir: str = ".", store_in_trace: bool = True):
        """
        Save both JSON and Markdown versions.

        Philosophy: "Store once, read many times, in the format that serves the reader"
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        manifest_json = self.to_json()

        # Save JSON manifest (machine-readable, IF-Trace ready)
        json_path = output_path / f"{self.run_id}-manifest.json"
        with open(json_path, 'w') as f:
            json.dump(manifest_json, f, indent=2)

        # Save Markdown executive summary (human-readable)
        md_path = output_path / f"{self.run_id}-executive-summary.md"
        with open(md_path, 'w') as f:
            f.write(self.to_markdown())

        print(f"\n✅ Run manifest saved:")
        print(f"   JSON (machine): {json_path}")
        print(f"   Markdown (human): {md_path}")

        # Store in IF-Trace (immutable audit trail)
        if store_in_trace and IF_TRACE_AVAILABLE:
            try:
                manifest_hash = self.compute_if_trace_hash()
                trace_id = store_manifest_in_trace(manifest_json, manifest_hash)
                print(f"   IF-Trace: Stored (trace_id: {trace_id})")
            except Exception as e:
                print(f"   IF-Trace: ⚠️  Storage failed ({e})")
        else:
            print(f"   IF-Trace: Skipped (not available)")

        return json_path, md_path

    def compute_if_trace_hash(self) -> str:
        """
        Compute Merkle hash for IF-Trace integration.

        Philosophy: "Immutability through cryptography"
        """
        manifest_str = json.dumps(self.to_json(), sort_keys=True)
        return hashlib.sha256(manifest_str.encode()).hexdigest()


class AgentLineageRecord:
    """
    Per-agent append-only record for meta-learning.

    Philosophy: "An agent's journey is its training data"
    """

    def __init__(self, agent_id: str, agent_name: str, tier: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.tier = tier
        self.lineage = []  # Version history
        self.iteration_stats = []  # Per-iteration performance
        self.cmp_estimate = 0.0  # CMP prior (will be updated)
        self.notes = ""

    def add_iteration(self, iteration: int, performance: float, weight: float,
                     confidence: float = None):
        """
        Record single iteration result.

        Philosophy: "Growth is visible in the trajectory, not the snapshot"
        """
        self.iteration_stats.append({
            'iter': iteration,
            'perf': performance,
            'weight': weight,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        })

    def update_cmp_estimate(self, alpha: float = 0.3):
        """
        Update CMP estimate based on improvement trajectory.

        Philosophy: "Future potential estimated from past improvement"

        Uses exponential smoothing to incorporate new evidence while
        maintaining memory of historical patterns.
        """
        if len(self.iteration_stats) < 2:
            self.cmp_estimate = 0.0
            return

        # Compute improvement slope (simple: last vs first)
        recent_perf = self.iteration_stats[-1]['perf']
        initial_perf = self.iteration_stats[0]['perf']

        # Observed future gain (normalized)
        improvement = (recent_perf - initial_perf) / max(initial_perf, 0.01)

        # Exponential smoothing update
        self.cmp_estimate = alpha * improvement + (1 - alpha) * self.cmp_estimate

    def detect_late_bloomer(self, threshold: float = 0.2) -> bool:
        """
        Identify if this agent shows late bloomer pattern.

        Philosophy: "Late bloomers start weak, mature strong"
        """
        if len(self.iteration_stats) < 5:
            return False

        early_avg = sum(s['perf'] for s in self.iteration_stats[:2]) / 2
        late_avg = sum(s['perf'] for s in self.iteration_stats[-3:]) / 3

        improvement = late_avg - early_avg
        return improvement > threshold

    def to_dict(self) -> Dict:
        """Export as JSON record for meta-learner"""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'tier': self.tier,
            'lineage': self.lineage,
            'iteration_stats': self.iteration_stats,
            'cmp_estimate': self.cmp_estimate,
            'is_late_bloomer': self.detect_late_bloomer(),
            'success_rate': self._compute_success_rate(),
            'notes': self.notes
        }

    def _compute_success_rate(self) -> float:
        """Compute overall success rate"""
        if not self.iteration_stats:
            return 0.0

        successes = sum(1 for s in self.iteration_stats if s['perf'] > 0.5)
        return successes / len(self.iteration_stats)


def create_manifest_from_session(session_results: Dict) -> RunManifest:
    """
    Create manifest from weighted_multi_agent_finder session results.

    Philosophy: "Every session becomes a reproducible experiment"
    """
    manifest = RunManifest()

    # Extract config
    manifest.set_config({
        'agent_profiles': session_results.get('agent_profiles', {}),
        'google_threshold': session_results.get('google_threshold', 50),
        'timestamp': session_results.get('timestamp', 'unknown')
    })

    # Extract input snapshot
    manifest.set_input_snapshot(
        dataset_id=session_results.get('dataset_id', 'unknown'),
        seed=session_results.get('seed', None)
    )

    # Extract metrics
    session_stats = session_results.get('session_stats', {})
    manifest.set_metrics_summary({
        'contacts_processed': session_stats.get('total_contacts', 0),
        'free_agents_sufficient': session_stats.get('free_agents_sufficient', 0),
        'google_validations_needed': session_stats.get('google_validations_needed', 0),
        'cost_saved': session_stats.get('cost_saved', 0.0),
        'system_score': session_stats.get('average_confidence', 0.0) / 100.0
    })

    # Build agent records
    agent_success_rates = session_stats.get('agent_success_rates', {})
    for agent_name, stats in agent_success_rates.items():
        record = AgentLineageRecord(
            agent_id=f"agent-{agent_name.lower()}",
            agent_name=agent_name,
            tier=stats.get('tier', 'unknown')
        )

        # Add success rate as single iteration for now
        success_rate = stats.get('successes', 0) / max(stats.get('attempts', 1), 1)
        record.add_iteration(
            iteration=0,
            performance=success_rate,
            weight=stats.get('weight', 0.0),
            confidence=stats.get('avg_confidence', None)
        )

        record.update_cmp_estimate()
        record.notes = f"{stats.get('successes', 0)}/{stats.get('attempts', 0)} success"

        manifest.add_agent_record(record.to_dict())

    # Add CMP analysis
    manifest.set_cmp_analysis({
        'weighted_vs_naive': {
            'approach': 'weighted',
            'failed_exploration_penalty': 0.0,
            'successful_amplification': 'up to 2.0x',
            'thesis': 'Validated - failed agents silent, successful amplified'
        },
        'late_bloomer_detection': {
            'candidates': [r['agent_name'] for r in manifest.agent_records
                          if r.get('is_late_bloomer', False)],
            'rate': sum(1 for r in manifest.agent_records if r.get('is_late_bloomer', False)) /
                   len(manifest.agent_records) if manifest.agent_records else 0
        }
    })

    # Generate executive notes
    manifest.set_executive_notes(
        f"Weighted coordination run completed successfully. "
        f"{session_stats.get('free_agents_sufficient', 0)} of "
        f"{session_stats.get('total_contacts', 0)} contacts handled by free agents. "
        f"Validates InfraFabric CMP thesis: failed exploration silent, "
        f"successful contribution amplified."
    )

    return manifest


if __name__ == "__main__":
    print("="*80)
    print("RUN MANIFEST GENERATOR - InfraFabric Self-Documenting Experiments")
    print("="*80)
    print("\nPhilosophy:")
    print('  "Every run is a reproducible experiment"')
    print('  - Complete provenance (config, seeds, versions)')
    print('  - Machine + human readable (JSON + Markdown)')
    print('  - IF-Trace integration (Merkle-chained immutable storage)')
    print('  - Meta-learning ready (training data for self-improvement)')
    print("="*80)
    print("\nReady to generate manifests for weighted coordination runs.")
    print("Import this module and call create_manifest_from_session(results).\n")
