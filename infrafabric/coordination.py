"""
Weighted Coordination Framework

Implements adaptive weighting mechanism (0.0 → 2.0) for multi-agent systems.

Core Principle:
  Failed exploration doesn't penalize (0.0 weight, silent)
  Successful exploration amplified (up to 2.0 weight)
  Late bloomers discovered through patience

Classes:
- AgentProfile: Configuration for weighted agent
- Agent: Individual agent with adaptive weight
- WeightedCoordinator: Orchestrates multi-agent coordination

Author: InfraFabric Research
Date: October 31, 2025
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import json


@dataclass
class AgentProfile:
    """
    Configuration for a weighted agent.

    Attributes:
        name: Agent identifier
        base_weight: Starting weight (0.0 - 2.0)
        success_bonus: Weight increase on success
        success_threshold: Confidence % to count as success
        tier: Agent tier (baseline/specialist/exploratory)
        description: What this agent does
    """

    name: str
    base_weight: float
    success_bonus: float
    success_threshold: int
    tier: str
    description: str


class Agent:
    """
    Weighted agent with adaptive influence.

    The agent's weight determines its influence in the final result:
    - 0.0: Silent (failed, not penalized)
    - 1.0: Baseline (consistent contributor)
    - 2.0: Amplified (high-value discoveries)

    Weight updates based on performance over time.
    """

    def __init__(self, profile: AgentProfile):
        self.profile = profile
        self.current_weight = profile.base_weight
        self.history: List[Dict] = []

    def execute(self, task: Dict) -> Dict:
        """
        Execute task and return result with confidence score.

        Override this in subclasses or pass callable.

        Returns:
            Dict with keys: success, confidence, data, reasoning
        """
        # Stub - override in subclasses
        return {
            'agent': self.profile.name,
            'success': False,
            'confidence': 0,
            'data': None,
            'reasoning': 'Not implemented'
        }

    def update_weight(self, result: Dict):
        """
        Update agent weight based on result.

        Logic:
        - Confidence >= threshold → increase weight
        - Confidence < threshold → decrease toward 0.0
        - Never negative (failed agents go silent, not penalized)
        """

        confidence = result.get('confidence', 0)

        if confidence >= self.profile.success_threshold:
            # Success: increase weight
            self.current_weight = min(
                self.profile.base_weight + self.profile.success_bonus,
                2.0
            )
        else:
            # Low confidence: decrease toward 0.0
            self.current_weight = max(
                self.current_weight - 0.2,
                0.0
            )

        # Record in history
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'confidence': confidence,
            'weight_before': self.current_weight + 0.2 if confidence < self.profile.success_threshold else self.current_weight - self.profile.success_bonus,
            'weight_after': self.current_weight,
            'result': result
        })


class WeightedCoordinator:
    """
    Orchestrates weighted multi-agent coordination.

    Features:
    - Adaptive weighting (agents succeed/fail independently)
    - Late bloomer detection (patience reveals value)
    - Self-documenting execution (manifests)
    - No premature termination (CMP principle)

    Usage:
        coordinator = WeightedCoordinator()
        coordinator.add_agent(agent1)
        coordinator.add_agent(agent2)
        result = coordinator.coordinate(task)
    """

    def __init__(self):
        self.agents: List[Agent] = []
        self.coordination_history: List[Dict] = []

    def add_agent(self, agent: Agent):
        """Add agent to coordination pool"""
        self.agents.append(agent)

    def add_standard_agents(self):
        """Add standard agent profiles for contact discovery"""

        profiles = [
            AgentProfile(
                name="ProfessionalNetworker",
                base_weight=1.0,
                success_bonus=0.0,
                success_threshold=60,
                tier="baseline",
                description="Conservative baseline (firstname.lastname@company patterns)"
            ),
            AgentProfile(
                name="AcademicResearcher",
                base_weight=0.0,
                success_bonus=1.5,
                success_threshold=80,
                tier="specialist",
                description="Google Scholar, arXiv, research networks"
            ),
            AgentProfile(
                name="IntelAnalyst",
                base_weight=0.0,
                success_bonus=1.2,
                success_threshold=75,
                tier="specialist",
                description="SEC filings, investor relations, public company data"
            ),
            AgentProfile(
                name="InvestigativeJournalist",
                base_weight=0.0,
                success_bonus=2.0,
                success_threshold=85,
                tier="exploratory",
                description="PDF mining, archived pages, leaked directories"
            ),
            AgentProfile(
                name="RecruiterUser",
                base_weight=0.0,
                success_bonus=1.3,
                success_threshold=80,
                tier="exploratory",
                description="GitHub, Stack Overflow, tech community presence"
            ),
            AgentProfile(
                name="SocialEngineer",
                base_weight=0.5,
                success_bonus=1.2,
                success_threshold=75,
                tier="exploratory",
                description="Org hierarchy, gatekeepers, admin contacts"
            ),
        ]

        for profile in profiles:
            self.add_agent(Agent(profile))

    def coordinate(self, task: Dict, verbose: bool = False) -> Dict:
        """
        Coordinate agents on task using weighted synthesis.

        Args:
            task: Task dict (depends on agent implementations)
            verbose: Print coordination transcript

        Returns:
            Weighted synthesis of agent results
        """

        if verbose:
            print(f"\n{'='*60}")
            print(f"🤖 WEIGHTED COORDINATION")
            print(f"{'='*60}\n")

        agent_results = []

        # Execute each agent
        for agent in self.agents:
            if verbose and agent.current_weight > 0:
                print(f"  [{agent.profile.name}] weight={agent.current_weight:.2f}")

            # Execute agent (if weight > 0, otherwise silent)
            if agent.current_weight > 0:
                result = agent.execute(task)
                result['weight'] = agent.current_weight
                agent_results.append(result)

                # Update agent weight based on result
                agent.update_weight(result)

                if verbose:
                    print(f"    Confidence: {result.get('confidence', 0)}%")
                    print(f"    New weight: {agent.current_weight:.2f}")
            else:
                if verbose:
                    print(f"    Silent (weight=0.0)")

        # Weighted synthesis
        if not agent_results:
            synthesis = {
                'success': False,
                'confidence': 0,
                'data': None,
                'reasoning': 'No agents active'
            }
        else:
            # Find highest confidence result, weighted by agent influence
            best_result = max(agent_results, key=lambda r: r['confidence'] * r['weight'])

            synthesis = {
                'success': best_result['success'],
                'confidence': best_result['confidence'],
                'data': best_result['data'],
                'best_agent': best_result['agent'],
                'agent_results': agent_results,
                'weighted_by': 'confidence * weight'
            }

        # Record in history
        self.coordination_history.append({
            'timestamp': datetime.now().isoformat(),
            'task': task,
            'synthesis': synthesis,
            'agent_count': len(self.agents),
            'active_agents': len(agent_results)
        })

        if verbose:
            print(f"\n  {'✅' if synthesis['success'] else '⚠️'} Best result: {synthesis.get('best_agent', 'None')} ({synthesis['confidence']}%)")
            print(f"{'='*60}\n")

        return synthesis

    def get_late_bloomers(self, lookback: int = 10) -> List[str]:
        """
        Identify agents that were initially low-weight but improved.

        Late bloomer pattern: weight starts < 0.3, ends > 0.7
        """

        late_bloomers = []

        for agent in self.agents:
            if len(agent.history) < 2:
                continue

            recent = agent.history[-lookback:] if lookback else agent.history

            if recent:
                early_weight = recent[0]['weight_before']
                late_weight = recent[-1]['weight_after']

                if early_weight < 0.3 and late_weight > 0.7:
                    late_bloomers.append(agent.profile.name)

        return late_bloomers

    def get_agent_performance(self) -> Dict[str, Dict]:
        """Get performance stats for all agents"""

        performance = {}

        for agent in self.agents:
            if not agent.history:
                continue

            confidences = [h['confidence'] for h in agent.history]
            weights = [h['weight_after'] for h in agent.history]

            performance[agent.profile.name] = {
                'current_weight': agent.current_weight,
                'executions': len(agent.history),
                'avg_confidence': sum(confidences) / len(confidences) if confidences else 0,
                'avg_weight': sum(weights) / len(weights) if weights else 0,
                'tier': agent.profile.tier
            }

        return performance

    def save_manifest(self, filepath: str):
        """Save coordination history as manifest"""

        manifest = {
            'timestamp': datetime.now().isoformat(),
            'agent_count': len(self.agents),
            'coordination_count': len(self.coordination_history),
            'agent_performance': self.get_agent_performance(),
            'late_bloomers': self.get_late_bloomers(),
            'history': self.coordination_history
        }

        with open(filepath, 'w') as f:
            json.dump(manifest, f, indent=2)
