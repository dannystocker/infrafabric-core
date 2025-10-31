"""
Self-Documenting Manifests

Generates complete provenance manifests for every coordination run.

Philosophy:
  "The system that documents itself can improve itself"

Classes:
- ManifestGenerator: Creates structured manifests
- create_manifest: Convenience function

Author: InfraFabric Research
Date: October 31, 2025
"""

from datetime import datetime
from typing import Dict, List, Optional
import json
import hashlib


class ManifestGenerator:
    """
    Generates self-documenting manifests for coordination runs.

    Manifests include:
    - Complete provenance (git commit, config, inputs)
    - Agent performance metrics
    - Philosophical insights
    - CMP analysis (late bloomers, patience reveals value)
    """

    def __init__(self, run_id: Optional[str] = None):
        self.run_id = run_id or self._generate_run_id()
        self.timestamp = datetime.now().isoformat()
        self.data = {}

    def _generate_run_id(self) -> str:
        """Generate unique run ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"run-{timestamp}"

    def add_config(self, config: Dict):
        """Add configuration snapshot"""
        self.data['config'] = config

    def add_inputs(self, inputs: Dict):
        """Add input snapshot"""
        self.data['inputs'] = inputs

    def add_results(self, results: Dict):
        """Add execution results"""
        self.data['results'] = results

    def add_agent_performance(self, performance: Dict):
        """Add agent performance metrics"""
        self.data['agent_performance'] = performance

    def add_philosophical_insight(self, insight: str):
        """Add philosophical reflection"""
        if 'philosophical_insights' not in self.data:
            self.data['philosophical_insights'] = []
        self.data['philosophical_insights'].append(insight)

    def add_cmp_analysis(self, late_bloomers: List[str], patience_metrics: Dict):
        """Add CMP (Clayed Meta-Productivity) analysis"""
        self.data['cmp_analysis'] = {
            'late_bloomers': late_bloomers,
            'patience_metrics': patience_metrics,
            'philosophy': 'Keep bad branches alive - patience reveals value'
        }

    def compute_hash(self) -> str:
        """Compute SHA256 hash of manifest for provenance"""
        content = json.dumps(self.data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        manifest = {
            'run_id': self.run_id,
            'timestamp': self.timestamp,
            'manifest_hash': self.compute_hash(),
            **self.data
        }
        return manifest

    def save(self, filepath: str):
        """Save manifest to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


def create_manifest(run_id: Optional[str] = None,
                    config: Optional[Dict] = None,
                    inputs: Optional[Dict] = None,
                    results: Optional[Dict] = None,
                    agent_performance: Optional[Dict] = None) -> ManifestGenerator:
    """
    Convenience function to create manifest.

    Args:
        run_id: Optional run identifier
        config: Configuration dict
        inputs: Input snapshot
        results: Execution results
        agent_performance: Agent performance metrics

    Returns:
        ManifestGenerator instance

    Example:
        manifest = create_manifest(
            config={'batch_size': 10},
            results={'contacts_found': 45}
        )
        manifest.save('run-001-manifest.json')
    """

    generator = ManifestGenerator(run_id)

    if config:
        generator.add_config(config)
    if inputs:
        generator.add_inputs(inputs)
    if results:
        generator.add_results(results)
    if agent_performance:
        generator.add_agent_performance(agent_performance)

    return generator
