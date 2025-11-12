"""
IF.talent Scout Phase - Discover and evaluate new AI capabilities

Uses multiple Haiku agents (lightweight, fast) to research and evaluate
potential capabilities before onboarding.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class CapabilitySource(Enum):
    """Source of capability discovery"""
    MANUAL = "manual"           # Manually specified by user
    AUTO_DETECTED = "auto"      # Detected from task history
    RECOMMENDED = "recommended" # Recommended by IF.governor
    PEER_LEARNED = "peer"       # Learned from peer agents


@dataclass
class ScoutResult:
    """Result of scouting phase"""
    approved: bool
    capability_profile: Optional[Dict[str, Any]]
    reason: str
    confidence: float  # 0.0-1.0
    metrics: Dict[str, Any]
    scout_votes: List[Dict[str, Any]]  # Individual scout agent votes


class Scout:
    """
    Scout phase: Multi-agent capability evaluation

    Uses 10 Haiku agents to:
    - Research capability requirements
    - Evaluate market demand
    - Assess implementation feasibility
    - Recommend skill levels and bloom patterns
    - Vote on whether to proceed with onboarding
    """

    def __init__(self, num_agents: int = 10):
        """
        Initialize scout with multiple Haiku agents

        Args:
            num_agents: Number of Haiku agents for parallel research (default: 10)
        """
        self.num_agents = num_agents
        self.scout_agents = [f"scout-haiku-{i+1}" for i in range(num_agents)]

    async def evaluate_capability(self,
                                 capability_name: str,
                                 target_agent: str,
                                 source: CapabilitySource = CapabilitySource.MANUAL) -> ScoutResult:
        """
        Evaluate whether to onboard a new capability

        Uses parallel Haiku agents to research and vote on capability.

        Args:
            capability_name: Name of capability (e.g., "python.async_programming")
            target_agent: Agent/swarm ID that would receive this capability
            source: Source of capability discovery

        Returns:
            ScoutResult with approval decision and recommended profile
        """
        print(f"[Scout] Deploying {self.num_agents} Haiku agents to evaluate '{capability_name}'...")

        # Parse capability name into domain, category, skill
        parts = capability_name.split('.')
        if len(parts) == 3:
            domain, category, skill = parts
        elif len(parts) == 2:
            domain, category = parts
            skill = parts[1]  # Use category as skill name
        else:
            domain = "unknown"
            category = "unknown"
            skill = capability_name

        # Spawn parallel scout agents
        scout_tasks = [
            self._scout_agent_evaluate(
                agent_id=agent_id,
                capability_name=capability_name,
                domain=domain,
                category=category,
                skill=skill,
                target_agent=target_agent
            )
            for agent_id in self.scout_agents
        ]

        scout_votes = await asyncio.gather(*scout_tasks)

        # Aggregate votes
        approval_votes = sum(1 for vote in scout_votes if vote['approved'])
        rejection_votes = self.num_agents - approval_votes
        approval_rate = approval_votes / self.num_agents

        # Require 70% approval (7/10 agents)
        approved = approval_rate >= 0.70

        # Build capability profile from scout recommendations
        if approved:
            capability_profile = self._build_profile_from_votes(
                capability_name=capability_name,
                domain=domain,
                category=category,
                skill=skill,
                scout_votes=scout_votes
            )
            reason = f"Approved by {approval_votes}/{self.num_agents} scout agents ({approval_rate*100:.0f}%)"
        else:
            capability_profile = None
            reason = f"Rejected: Only {approval_votes}/{self.num_agents} scouts approved ({approval_rate*100:.0f}%). Need 70%."

        print(f"[Scout] ✅ Evaluation complete: {approval_votes} approve, {rejection_votes} reject")

        return ScoutResult(
            approved=approved,
            capability_profile=capability_profile,
            reason=reason,
            confidence=approval_rate,
            metrics={
                'approval_votes': approval_votes,
                'rejection_votes': rejection_votes,
                'approval_rate': approval_rate,
                'num_agents': self.num_agents
            },
            scout_votes=scout_votes
        )

    async def _scout_agent_evaluate(self,
                                    agent_id: str,
                                    capability_name: str,
                                    domain: str,
                                    category: str,
                                    skill: str,
                                    target_agent: str) -> Dict[str, Any]:
        """
        Individual scout agent evaluation

        Simulates a Haiku agent researching and voting on capability.

        Returns:
            Vote dict with approval, reasoning, recommendations
        """
        # Simulate Haiku agent research time (lightweight, fast)
        await asyncio.sleep(0.1)

        # Scout evaluation logic (simplified for Phase 0)
        # In production, this would call actual Haiku LLM for research

        # Check if capability name is well-formed
        well_formed = len(capability_name.split('.')) >= 2

        # Check if domain is recognized (from F6.12 taxonomy)
        recognized_domains = [
            'video', 'telephony', 'crypto', 'infra', 'cloud',
            'smart_home', 'programming', 'documentation', 'architecture',
            'talent', 'payment', 'chat', 'ai_ml'
        ]
        domain_recognized = domain in recognized_domains

        # Estimate market demand (simplified heuristic)
        high_demand_skills = [
            'async_programming', 'networking', 'api_design',
            'performance', 'security', 'testing', 'docker'
        ]
        market_demand = skill in high_demand_skills or 'async' in skill or 'network' in skill

        # Vote approval if majority of checks pass
        checks_passed = sum([well_formed, domain_recognized, market_demand])
        approved = checks_passed >= 2

        # Recommend skill level based on skill name complexity
        if 'expert' in skill or 'advanced' in skill:
            recommended_level = 'advanced'
        elif 'basic' in skill or 'simple' in skill:
            recommended_level = 'novice'
        else:
            recommended_level = 'intermediate'

        # Recommend bloom pattern (simplified heuristic)
        if 'performance' in skill or 'optimization' in skill or 'complex' in skill:
            recommended_bloom = 'late_bloomer'
        elif 'simple' in skill or 'basic' in skill or 'cli' in skill:
            recommended_bloom = 'early_bloomer'
        else:
            recommended_bloom = 'steady_performer'

        return {
            'agent_id': agent_id,
            'approved': approved,
            'confidence': 0.85 if approved else 0.60,
            'reasoning': self._generate_reasoning(
                approved=approved,
                well_formed=well_formed,
                domain_recognized=domain_recognized,
                market_demand=market_demand
            ),
            'recommendations': {
                'skill_level': recommended_level,
                'bloom_pattern': recommended_bloom,
                'priority': 'high' if market_demand else 'medium'
            }
        }

    def _generate_reasoning(self,
                           approved: bool,
                           well_formed: bool,
                           domain_recognized: bool,
                           market_demand: bool) -> str:
        """Generate human-readable reasoning for vote"""
        reasons = []

        if well_formed:
            reasons.append("well-formed capability name")
        else:
            reasons.append("ISSUE: malformed capability name")

        if domain_recognized:
            reasons.append("recognized domain from F6.12 taxonomy")
        else:
            reasons.append("ISSUE: unrecognized domain")

        if market_demand:
            reasons.append("high market demand skill")
        else:
            reasons.append("moderate market demand")

        if approved:
            return f"APPROVE: {', '.join(reasons)}"
        else:
            return f"REJECT: {', '.join(reasons)}"

    def _build_profile_from_votes(self,
                                  capability_name: str,
                                  domain: str,
                                  category: str,
                                  skill: str,
                                  scout_votes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build capability profile from scout votes

        Uses majority vote for skill level and bloom pattern recommendations.

        Returns:
            Capability profile dict compatible with F6.12 schema
        """
        # Aggregate recommendations
        skill_levels = [vote['recommendations']['skill_level'] for vote in scout_votes]
        bloom_patterns = [vote['recommendations']['bloom_pattern'] for vote in scout_votes]

        # Majority vote
        recommended_level = max(set(skill_levels), key=skill_levels.count)
        recommended_bloom = max(set(bloom_patterns), key=bloom_patterns.count)

        # Build F6.12-compatible profile
        return {
            'capability_name': capability_name,
            'domain': domain,
            'category': category,
            'skill': skill,
            'recommended_level': recommended_level,
            'recommended_bloom': recommended_bloom,
            'scout_confidence': sum(v['confidence'] for v in scout_votes) / len(scout_votes),
            'scout_votes': len([v for v in scout_votes if v['approved']]),
            'scout_total': len(scout_votes)
        }

    async def auto_discover_capabilities(self,
                                        agent_history: List[Dict[str, Any]],
                                        min_frequency: int = 3) -> List[str]:
        """
        Auto-discover capabilities from agent task history

        Analyzes completed tasks to identify frequently used skills
        that should be formalized as capabilities.

        Args:
            agent_history: List of completed tasks with metadata
            min_frequency: Minimum times skill must appear to recommend (default: 3)

        Returns:
            List of capability names to consider onboarding
        """
        # Count skill usage in task history
        skill_counts: Dict[str, int] = {}

        for task in agent_history:
            if 'skills_used' in task:
                for skill in task['skills_used']:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1

        # Recommend capabilities that meet frequency threshold
        recommended = [
            skill for skill, count in skill_counts.items()
            if count >= min_frequency
        ]

        return sorted(recommended, key=lambda s: skill_counts[s], reverse=True)
