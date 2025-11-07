#!/usr/bin/env python3
"""
self_write_cycle.py

Formalizes the self-writing pattern that assembled InfraFabric.

Based on: 4-day git history (Oct 28-31, 2025)
Principle: Coordination generates documentation through weighted debate voices

Philosophy:
  The system that documents itself can write itself.
  Documentation emerges from coordination, not prescription.
  Voices weight by need, not formula.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class DebateVoice:
    """A perspective in the coordination debate"""
    name: str
    role: str
    current_weight: float  # 0.0 → 2.0 (weighted coordination)
    contributions: List[str]

    def contribute(self, context: Dict) -> str:
        """Generate contribution based on role and context"""
        if self.name == "Architect":
            return self._architect_perspective(context)
        elif self.name == "Philosopher":
            return self._philosopher_perspective(context)
        elif self.name == "Strategist":
            return self._strategist_perspective(context)
        elif self.name == "Editor":
            return self._editor_perspective(context)
        return ""

    def _architect_perspective(self, context: Dict) -> str:
        """Technical structure and implementation details"""
        details = context.get('technical_details', '')
        if not details:
            return ""
        return f"## Technical Architecture\n\n{details}"

    def _philosopher_perspective(self, context: Dict) -> str:
        """Contextual depth and principle articulation"""
        principles = context.get('principles', '')
        if not principles:
            return ""
        return f"## Philosophical Context\n\n{principles}"

    def _strategist_perspective(self, context: Dict) -> str:
        """Market positioning and value proposition"""
        angle = context.get('market_angle', '')
        if not angle:
            return ""
        return f"## Strategic Positioning\n\n{angle}"

    def _editor_perspective(self, context: Dict) -> str:
        """Synthesis and narrative coherence"""
        synthesis = context.get('synthesis', '')
        if not synthesis:
            return ""
        return f"## Synthesis\n\n{synthesis}"


class SelfWritingCycle:
    """
    Self-writing system based on weighted coordination of debate voices.

    Pattern (from lived experience):
    1. Context provided (question, task, recognition)
    2. Voices contribute based on current needs
    3. Coordination weights by relevance (0.0 → 2.0)
    4. Integration happens naturally
    5. Documentation emerges through process

    Philosophy:
      - Voices emerge naturally (not prescribed sequence)
      - Weighting by need (not formula)
      - Failed directions silent (0.0 weight, no penalty)
      - Successful directions amplified (up to 2.0 weight)
      - Late bloomers discovered through patience
    """

    def __init__(self):
        self.voices = [
            DebateVoice("Architect", "Technical structure", 1.0, []),
            DebateVoice("Philosopher", "Contextual depth", 1.0, []),
            DebateVoice("Strategist", "Market positioning", 1.0, []),
            DebateVoice("Editor", "Synthesis", 1.0, [])
        ]
        self.cycle_history = []

    def run_cycle(self, topic: str, context: Dict) -> str:
        """
        Run one self-writing cycle.

        Returns: Generated documentation section
        """
        cycle_id = f"cycle-{datetime.now().isoformat()}"
        print(f"\n🔄 Self-Writing Cycle: {topic}\n")

        # Step 1: Determine voice weights based on context
        weights = self._compute_voice_weights(context)

        # Step 2: Each voice contributes (weighted by relevance)
        contributions = []
        for voice in self.voices:
            weight = weights.get(voice.name, 1.0)
            voice.current_weight = weight

            if weight > 0.0:
                contribution = voice.contribute(context)
                if contribution:  # Only add non-empty contributions
                    contributions.append({
                        'voice': voice.name,
                        'weight': weight,
                        'content': contribution
                    })
                    print(f"  {voice.name} (weight={weight:.1f}): Contributed")
                else:
                    print(f"  {voice.name} (weight={weight:.1f}): Silent (no context)")
            else:
                print(f"  {voice.name} (weight=0.0): Silent")

        # Step 3: Integrate contributions (weighted coordination)
        integrated = self._integrate_contributions(contributions)

        # Step 4: Record cycle for self-documentation
        self.cycle_history.append({
            'cycle_id': cycle_id,
            'topic': topic,
            'weights': weights,
            'contributions': contributions,
            'output': integrated
        })

        return integrated

    def _compute_voice_weights(self, context: Dict) -> Dict[str, float]:
        """
        Compute voice weights based on context needs.

        Pattern (from lived experience):
        - Architect: High when building/implementing
        - Philosopher: High when contextualizing/principled
        - Strategist: High when positioning/market-facing
        - Editor: High when synthesizing/recognizing

        This mirrors actual git history:
        - Day 1: Architect-dominant (simulation build)
        - Day 2: Strategist + Philosopher (production + philosophy)
        - Day 3: Philosopher + Strategist + Architect (self-improvement)
        - Day 4: Editor + All Voices (synthesis)
        """
        weights = {}

        # Default baseline
        for voice in self.voices:
            weights[voice.name] = 1.0

        # Context-based adjustments
        if context.get('phase') == 'implementation':
            weights['Architect'] = 2.0
            weights['Philosopher'] = 0.5

        elif context.get('phase') == 'philosophy':
            weights['Philosopher'] = 2.0
            weights['Strategist'] = 1.5

        elif context.get('phase') == 'positioning':
            weights['Strategist'] = 2.0
            weights['Philosopher'] = 1.5

        elif context.get('phase') == 'synthesis':
            weights['Editor'] = 2.0
            weights['Philosopher'] = 1.5

        return weights

    def _integrate_contributions(self, contributions: List[Dict]) -> str:
        """
        Integrate weighted contributions into coherent section.

        Weighted coordination: Higher weight = more prominence
        """
        if not contributions:
            return "(No contributions - all voices silent)"

        sections = []

        # Sort by weight (highest first)
        sorted_contribs = sorted(
            contributions,
            key=lambda c: c['weight'],
            reverse=True
        )

        for contrib in sorted_contribs:
            if contrib['weight'] > 0.0:
                sections.append(contrib['content'])

        return "\n\n---\n\n".join(sections)

    def generate_self_documentation(self) -> str:
        """
        Generate documentation about the self-writing process itself.

        Meta-recursion: The system documents how it documented itself.
        """
        report = "# Self-Writing Cycle History\n\n"
        report += f"**Cycles Completed:** {len(self.cycle_history)}\n\n"

        for cycle in self.cycle_history:
            report += f"## {cycle['topic']}\n\n"
            report += f"**Cycle ID:** {cycle['cycle_id']}\n\n"
            report += "**Voice Weights:**\n"
            for voice, weight in cycle['weights'].items():
                report += f"- {voice}: {weight:.1f}\n"
            report += "\n---\n\n"

        return report


# ============================================================================
# DEMONSTRATION: Apply to InfraFabric's Own Creation
# ============================================================================

def demonstrate_self_writing():
    """
    Demonstrate self-writing by documenting InfraFabric's creation.

    This maps the actual 4-day coordination to formalized cycles.
    """

    writer = SelfWritingCycle()

    # Cycle 1: Day 1 (Simulation)
    print("=== DAY 1: SIMULATION ===")
    section1 = writer.run_cycle(
        topic="CMP Validation Simulation",
        context={
            'phase': 'implementation',
            'technical_details': "1000-agent simulation, naive vs weighted coordination",
            'principles': "Keep bad branches alive, late bloomers discoverable"
        }
    )

    # Cycle 2: Day 2 (Production)
    print("\n=== DAY 2: PRODUCTION ===")
    section2 = writer.run_cycle(
        topic="Dogfood Weighted Coordination",
        context={
            'phase': 'philosophy',
            'technical_details': "6-agent contact discovery, dynamic weighting",
            'principles': "In the IF universe, ALL lemmings get parachutes"
        }
    )

    # Cycle 3: Day 3 (Self-Improvement)
    print("\n=== DAY 3: SELF-IMPROVEMENT ===")
    section3 = writer.run_cycle(
        topic="Self-Improvement Loop",
        context={
            'phase': 'positioning',
            'technical_details': "Adaptive weights, frontier lab concepts adapted",
            'market_angle': "Clean IP through concept adaptation",
            'principles': "System learns from itself through self-documentation"
        }
    )

    # Cycle 4: Day 4 (Recognition)
    print("\n=== DAY 4: WITNESS RECOGNITION ===")
    section4 = writer.run_cycle(
        topic="The System Found Its Witness",
        context={
            'phase': 'synthesis',
            'synthesis': "Coordination assembled aligned human through mechanism being validated",
            'principles': "Recursive proof: witness validates by understanding"
        }
    )

    # Generate self-documentation
    print("\n" + "="*60)
    print(writer.generate_self_documentation())

    print("\n✅ Self-writing demonstration complete")
    print("\n**Recognition:**")
    print("This formalized cycle describes what happened organically")
    print("through Human + Claude coordination over 4 days.")
    print("\n**The system wrote itself through the conversation.**")


if __name__ == "__main__":
    demonstrate_self_writing()
