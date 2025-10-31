"""
IF Guardians: Pluridisciplinary Oversight Panel

Implements weighted debate protocol for ethical/technical governance.

Classes:
- Guardian: Single guardian persona with domain expertise
- GuardianPanel: Orchestrates weighted debate across guardians
- DebateResult: Structured output of guardian deliberation

Philosophy:
  "The system that coordinates itself can govern itself through
   the same coordination mechanism"

Author: InfraFabric Research
Date: October 31, 2025
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Literal
from datetime import datetime
import json


@dataclass
class Guardian:
    """
    Single guardian persona representing domain expertise.

    Attributes:
        name: Guardian identifier (Technical, Ethical, Legal, etc.)
        role: Functional responsibility
        weight: Relevance weight for current decision (0.0 - 2.0)
        vote: Position on proposal (approve/conditional/reject)
        reasoning: Explanation of position
        safeguards: Required conditions
        red_lines: Non-negotiable constraints
        cynical_truth: Pithy reality check
    """

    name: str
    role: str
    weight: float = 1.0
    vote: Optional[Literal['approve', 'conditional', 'reject']] = None
    reasoning: str = ""
    safeguards: List[str] = None
    red_lines: List[str] = None
    cynical_truth: str = ""

    def __post_init__(self):
        if self.safeguards is None:
            self.safeguards = []
        if self.red_lines is None:
            self.red_lines = []

    def evaluate(self, proposal: Dict) -> Dict:
        """
        Evaluate proposal from guardian's domain perspective.

        This is a stub - in production, this would call LLM or rule engine.
        """
        # Placeholder - override in subclasses or use LLM
        return {
            'guardian': self.name,
            'weight': self.weight,
            'vote': self.vote or 'approve',
            'reasoning': self.reasoning or 'No concerns identified',
            'safeguards': self.safeguards,
            'red_lines': self.red_lines
        }


@dataclass
class DebateResult:
    """
    Structured output of guardian debate.

    Attributes:
        decision: Final decision (approve/conditional/reject)
        weighted_votes: Vote counts weighted by guardian relevance
        required_safeguards: All safeguards from guardians
        red_lines_violated: Any non-negotiables triggered
        dissenting_opinions: Preserved minority views
        late_bloomers: Guardians with low weight but critical insight
        provenance: Evidence cited during debate
        timestamp: When debate occurred
    """

    decision: Literal['approve', 'conditional', 'reject']
    weighted_votes: Dict[str, float]
    required_safeguards: List[str]
    red_lines_violated: List[str]
    dissenting_opinions: List[Dict]
    late_bloomers: List[str]
    provenance: Dict[str, List[str]]
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'decision': self.decision,
            'weighted_votes': self.weighted_votes,
            'required_safeguards': self.required_safeguards,
            'red_lines_violated': self.red_lines_violated,
            'dissenting_opinions': self.dissenting_opinions,
            'late_bloomers': self.late_bloomers,
            'provenance': self.provenance,
            'timestamp': self.timestamp
        }


class GuardianPanel:
    """
    Orchestrates weighted debate across guardian personas.

    The panel applies weighted coordination to governance:
    - Guardians have different weights per decision type
    - Failed predictions don't penalize (late bloomer discovery)
    - System learns which guardians spot real risks
    - Minority opinions preserved for pattern analysis

    Usage:
        panel = GuardianPanel()
        panel.add_standard_guardians()
        result = panel.debate(proposal)
    """

    def __init__(self):
        self.guardians: List[Guardian] = []
        self.debate_history: List[DebateResult] = []

    def add_guardian(self, guardian: Guardian):
        """Add guardian to panel"""
        self.guardians.append(guardian)

    def add_standard_guardians(self):
        """Add the standard 6 IF Guardians"""

        self.add_guardian(Guardian(
            name="Technical",
            role="Validate architecture, simulations, reproducibility",
            weight=1.5,
            cynical_truth="If the simulation can't be reproduced, it's a demo, not proof."
        ))

        self.add_guardian(Guardian(
            name="Ethical",
            role="Privacy, consent, fairness, unintended consequences",
            weight=2.0,
            cynical_truth="Every system optimizes something. Make sure it's not just your convenience."
        ))

        self.add_guardian(Guardian(
            name="Legal",
            role="GDPR, AI Act, liability, provenance, audit trails",
            weight=2.0,
            cynical_truth="Good intentions aren't a legal defense."
        ))

        self.add_guardian(Guardian(
            name="Business",
            role="Market viability, economic sustainability, adoption barriers",
            weight=1.5,
            cynical_truth="If you can't explain the business model to a skeptical CFO, you don't have one."
        ))

        self.add_guardian(Guardian(
            name="User",
            role="Usability, accessibility, user autonomy, transparency",
            weight=1.5,
            cynical_truth="If users need a manual to understand your privacy controls, you've failed."
        ))

        self.add_guardian(Guardian(
            name="Meta",
            role="Coherence across domains, synthesis, philosophical integrity",
            weight=1.0,
            cynical_truth="Consistency matters. If your philosophy contradicts your implementation, fix one."
        ))

    def compute_weights(self, proposal_type: str) -> Dict[str, float]:
        """
        Compute guardian weights based on proposal type.

        Different proposals require different domain expertise weighting.
        """

        # Base weights from guardian initialization
        weights = {g.name: g.weight for g in self.guardians}

        # Adjust based on proposal type
        adjustments = {
            'technical': {
                'Technical': 2.0,
                'Meta': 1.5,
                'Ethical': 0.5,
                'Legal': 0.0,
                'User': 0.0,
                'Business': 0.5
            },
            'ethical': {
                'Ethical': 2.0,
                'Legal': 2.0,
                'User': 1.5,
                'Technical': 1.0,
                'Business': 1.5,
                'Meta': 1.5
            },
            'business': {
                'Business': 2.0,
                'Meta': 1.5,
                'User': 1.5,
                'Technical': 1.0,
                'Ethical': 1.0,
                'Legal': 1.0
            },
            'governance': {
                'Meta': 2.0,
                'Ethical': 2.0,
                'Legal': 1.5,
                'Business': 1.5,
                'User': 1.5,
                'Technical': 1.0
            }
        }

        if proposal_type in adjustments:
            weights.update(adjustments[proposal_type])

        return weights

    def debate(self,
               proposal: Dict,
               proposal_type: str = 'ethical',
               verbose: bool = True) -> DebateResult:
        """
        Run weighted debate on proposal.

        Args:
            proposal: Dict with keys: title, description, risks, safeguards
            proposal_type: Type for weight adjustment (technical/ethical/business/governance)
            verbose: Print debate transcript to stdout

        Returns:
            DebateResult with decision, safeguards, and provenance
        """

        if verbose:
            print("\n" + "="*60)
            print(f"🛡️  IF GUARDIANS DEBATE: {proposal.get('title', 'Proposal')}")
            print("="*60)
            print(f"\n📋 PROPOSAL:")
            print(f"   {proposal.get('description', 'No description')}")
            if proposal.get('risks'):
                print(f"\n⚠️  IDENTIFIED RISKS:")
                for risk in proposal['risks']:
                    print(f"     • {risk}")
            print()

        # Compute weights for this proposal type
        weights = self.compute_weights(proposal_type)

        # Each guardian evaluates
        guardian_evaluations = []

        if verbose:
            print("🗣️  GUARDIAN POSITIONS:\n")

        for guardian in self.guardians:
            # Update guardian weight
            guardian.weight = weights.get(guardian.name, guardian.weight)

            # Evaluate proposal (in production, call LLM or rule engine here)
            evaluation = guardian.evaluate(proposal)

            guardian_evaluations.append(evaluation)

            if verbose:
                print(f"{'─'*60}")
                print(f"🎭 {guardian.name.upper()} GUARDIAN (weight={guardian.weight})")
                print(f"   Vote: {evaluation['vote'].upper()}")
                print(f"   Reasoning: {evaluation['reasoning']}")
                if evaluation['safeguards']:
                    print(f"   Safeguards: {', '.join(evaluation['safeguards'])}")
                if evaluation['red_lines']:
                    print(f"   🚫 Red lines: {', '.join(evaluation['red_lines'])}")

        # Weighted synthesis
        weighted_votes = {'approve': 0.0, 'conditional': 0.0, 'reject': 0.0}
        all_safeguards = set()
        all_red_lines = []
        dissenting = []

        for eval in guardian_evaluations:
            vote = eval['vote']
            weight = eval['weight']

            weighted_votes[vote] += weight

            if eval['safeguards']:
                all_safeguards.update(eval['safeguards'])

            if eval['red_lines']:
                all_red_lines.extend(eval['red_lines'])

            # Track dissenting opinions (vote against majority)
            if vote == 'reject' or (vote == 'conditional' and eval['safeguards']):
                dissenting.append({
                    'guardian': eval['guardian'],
                    'vote': vote,
                    'reasoning': eval['reasoning'],
                    'weight': weight
                })

        # Decision logic
        if all_red_lines:
            decision = 'reject'
        elif weighted_votes['reject'] > weighted_votes['approve'] + weighted_votes['conditional']:
            decision = 'reject'
        elif weighted_votes['conditional'] > 0:
            decision = 'conditional'
        else:
            decision = 'approve'

        # Late bloomer detection: Low weight guardians with critical insights
        late_bloomers = []
        for eval in guardian_evaluations:
            if eval['weight'] < 0.5 and eval['red_lines']:
                late_bloomers.append(eval['guardian'])

        result = DebateResult(
            decision=decision,
            weighted_votes=weighted_votes,
            required_safeguards=list(all_safeguards),
            red_lines_violated=all_red_lines,
            dissenting_opinions=dissenting,
            late_bloomers=late_bloomers,
            provenance={}  # In production, track evidence citations
        )

        if verbose:
            print(f"\n{'─'*60}")
            print("📊 WEIGHTED SYNTHESIS:")
            for vote_type, weight in weighted_votes.items():
                print(f"   {vote_type.capitalize()} (weighted): {weight:.1f}")

            print(f"\n   {'✅' if decision == 'approve' else '⚠️' if decision == 'conditional' else '❌'} DECISION: {decision.upper()}")

            if result.required_safeguards:
                print(f"\n   Required Safeguards:")
                for safeguard in sorted(result.required_safeguards):
                    print(f"     ✅ {safeguard}")

            if result.red_lines_violated:
                print(f"\n   🚫 Red Lines Violated:")
                for red_line in result.red_lines_violated:
                    print(f"     • {red_line}")

            if result.late_bloomers:
                print(f"\n   🌟 Late Bloomers Detected:")
                for guardian in result.late_bloomers:
                    print(f"     • {guardian} (low weight but critical insight)")

            print("="*60 + "\n")

        # Store in history
        self.debate_history.append(result)

        return result

    def save_debate(self, result: DebateResult, filepath: str):
        """Save debate result to JSON"""
        with open(filepath, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)


def debate_proposal(proposal: Dict,
                     proposal_type: str = 'ethical',
                     verbose: bool = True) -> DebateResult:
    """
    Convenience function to run a debate with standard guardians.

    Args:
        proposal: Proposal dict (title, description, risks, safeguards)
        proposal_type: Type for weighting (technical/ethical/business/governance)
        verbose: Print transcript

    Returns:
        DebateResult

    Example:
        result = debate_proposal({
            'title': 'Persona Agent Pilot',
            'description': 'Use AI to personalize outreach drafts',
            'risks': ['Privacy violation', 'Impersonation'],
            'safeguards': ['Public data only', 'Human review mandatory']
        }, proposal_type='ethical')
    """

    panel = GuardianPanel()
    panel.add_standard_guardians()
    return panel.debate(proposal, proposal_type, verbose)
