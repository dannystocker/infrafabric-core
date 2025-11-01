#!/usr/bin/env python3
"""
Meta-Creative Debugger Agent

This agent steps OUTSIDE the search problem to:
- Debug why other agents are failing
- Propose creative new search strategies
- Reframe the problem from different perspectives
- Generate novel approaches not in the acquired data

Philosophy: "The solution often requires stepping outside the frame you're using."

Architecture:
    Primary Agents (searching)
        ↓ [get stuck]
    Meta-Debugger (analyzes why stuck)
        ↓ [reframes problem]
    Creative Strategist (generates new approaches)
        ↓ [novel search strategies]
    Primary Agents (try new strategies)

This implements:
- Lateral thinking (Edward de Bono)
- Oblique strategies (Brian Eno)
- Beginner's mind (Shoshin)
- Constraint relaxation
- Perspective shifting
"""

import json
import random
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class CreativeReframing:
    """A creative way to reframe the search problem"""
    perspective: str
    question: str
    search_strategy: str
    reasoning: str

@dataclass
class DebuggingInsight:
    """Insight into why current approach is failing"""
    failure_pattern: str
    root_cause: str
    proposed_fix: str

class MetaDebuggerAgent:
    """
    Steps outside the search problem to analyze and debug

    Personality: Socratic questioner, pattern detective
    """

    def __init__(self):
        self.name = "MetaDebugger"
        self.personality = "Socratic questioner who asks 'why are we searching this way?'"

    def analyze_failure(self, search_results: List[Dict], contact: Dict) -> DebuggingInsight:
        """Debug why search is failing"""

        # Pattern: Are we asking the wrong question?
        all_failed = all(r['confidence'] < 50 for r in search_results)
        all_same = len(set(r['confidence'] for r in search_results)) == 1

        if all_failed:
            return DebuggingInsight(
                failure_pattern="All agents returning low confidence",
                root_cause="We're searching for the wrong signal - maybe public presence is not the right approach",
                proposed_fix="Try inverse search: Look for what they DON'T want public, or search for mentions BY others instead of BY them"
            )

        if all_same:
            return DebuggingInsight(
                failure_pattern="All agents returning identical confidence",
                root_cause="Agents are not diverse enough - they're all using same strategy",
                proposed_fix="Need orthogonal search strategies - try searching in different 'spaces' (time, negative space, relationships)"
            )

        # Pattern: High variance but no success
        confidences = [r['confidence'] for r in search_results]
        variance = max(confidences) - min(confidences)

        if variance > 40 and max(confidences) < 70:
            return DebuggingInsight(
                failure_pattern="High variance, no success",
                root_cause="One agent found something different but not confident enough",
                proposed_fix="Double down on the different approach - it's a weak signal worth amplifying"
            )

        return DebuggingInsight(
            failure_pattern="No clear pattern",
            root_cause="Standard searches are working adequately",
            proposed_fix="No debugging needed - continue current approach"
        )

    def ask_socratic_questions(self, contact: Dict) -> List[str]:
        """Ask questions that reframe the problem"""

        first_name = contact.get('first_name', '')
        last_name = contact.get('last_name', '')
        org = contact.get('organization', '')

        questions = [
            f"Why are we searching for {first_name} {last_name} DIRECTLY? What if we search for people who know them?",
            f"What does {first_name} NOT want us to find? (Controversy, failure, criticism - the hidden web)",
            f"Where would someone at {org} go to HIDE from us? (Dark web, encrypted channels, private forums)",
            f"When was {first_name} most PUBLICLY visible? (Career peaks, launches, controversies) Search that timeframe",
            f"Who would be LOOKING for {first_name}? (Recruiters, journalists, competitors) Search their searches",
            f"What QUESTIONS would {first_name} be answering? (Quora, Stack Overflow, Reddit AMAs)",
            f"What PROBLEMS does {org} have that {first_name} would be solving? Search problem spaces, not people",
            f"If I were AVOIDING discovery, where would I still leave traces? (Legal docs, patents, citations)"
        ]

        return random.sample(questions, 3)


class CreativeStrategistAgent:
    """
    Generates novel search strategies through creative techniques

    Personality: Brazen experimenter, rule-breaker
    """

    def __init__(self):
        self.name = "CreativeStrategist"
        self.personality = "Brazen experimenter who breaks search conventions"

        # Oblique strategies (inspired by Brian Eno/Peter Schmidt)
        self.oblique_strategies = [
            "Search for the OPPOSITE of what you're looking for",
            "Remove the most important search term",
            "Search in a language they might use privately",
            "Look for what's MISSING from the web about them",
            "Search for them in the PAST (Internet Archive)",
            "Search for them in the FUTURE (scheduled events, announced talks)",
            "Find their ENEMIES and search their content",
            "Search for their FAILURES not successes",
            "Look for DERIVATIVE works (people citing them, mentioning them)",
            "Search in SPACES they don't control (competitors, critics, ex-colleagues)"
        ]

    def generate_creative_reframings(self, contact: Dict) -> List[CreativeReframing]:
        """Generate creative new search approaches"""

        first_name = contact.get('first_name', '')
        last_name = contact.get('last_name', '')
        org = contact.get('organization', '')
        role = contact.get('role_title', '')

        reframings = []

        # Reframing 1: Temporal Shift
        reframings.append(CreativeReframing(
            perspective="Temporal Detective",
            question="When were they most visible/vulnerable?",
            search_strategy=f'site:archive.org "{first_name} {last_name}" {org}',
            reasoning="Internet Archive captures moments of high visibility (launches, controversies). People's digital footprint is strongest at career inflection points."
        ))

        # Reframing 2: Relationship Network
        reframings.append(CreativeReframing(
            perspective="Social Network Analyst",
            question="Who talks ABOUT them?",
            search_strategy=f'"about {first_name} {last_name}" OR "interview with {first_name}" -site:{org.lower()}',
            reasoning="Third-party mentions are harder to scrub than self-published content. Journalists, competitors, former colleagues leave traces."
        ))

        # Reframing 3: Negative Space
        reframings.append(CreativeReframing(
            perspective="Controversy Archeologist",
            question="What are they trying to hide?",
            search_strategy=f'"{first_name} {last_name}" (lawsuit OR controversy OR fired OR resigned OR criticism)',
            reasoning="Negative content is often more revealing and less controlled. Legal docs are public and un-erasable."
        ))

        # Reframing 4: Domain Expert
        reframings.append(CreativeReframing(
            perspective="Domain Specialist",
            question="What EXPERTISE do they claim?",
            search_strategy=f'"{first_name} {last_name}" (speaker OR conference OR keynote OR panel) filetype:pdf',
            reasoning="Conference materials, speaker bios, panel descriptions often include contact info and are preserved in PDFs."
        ))

        # Reframing 5: Beginner's Mind
        reframings.append(CreativeReframing(
            perspective="Naive Observer",
            question="What would a child search for?",
            search_strategy=f'{first_name} {last_name} email phone contact',
            reasoning="Sometimes the simplest query works. We overthink. A child would just ask directly."
        ))

        # Reframing 6: Constraint Relaxation
        reframings.append(CreativeReframing(
            perspective="Constraint Breaker",
            question="What if we DON'T search for them at all?",
            search_strategy=f'site:linkedin.com/in {org} {role.split()[0]} -"{last_name}"',
            reasoning="Search for the ROLE at the ORG, exclude them, see who else has it. Might find org contact patterns, or them in related results."
        ))

        return random.sample(reframings, 3)

    def apply_oblique_strategy(self, contact: Dict) -> Dict:
        """Apply random oblique strategy to generate novel approach"""

        strategy = random.choice(self.oblique_strategies)

        first_name = contact.get('first_name', '')
        last_name = contact.get('last_name', '')
        org = contact.get('organization', '')

        # Interpret strategy
        if "OPPOSITE" in strategy:
            query = f'-"{first_name} {last_name}" {org} leadership team'
            reasoning = "Searching for EVERYONE ELSE at org, might find them in group photos, team pages"

        elif "Remove the most important" in strategy:
            query = f'{first_name} {org}'  # Remove last name
            reasoning = "First name + org might find informal mentions, nicknames, team pages"

        elif "MISSING" in strategy:
            query = f'"{first_name} {last_name}" -site:linkedin.com -site:twitter.com'
            reasoning = "Exclude obvious places, find obscure mentions"

        elif "PAST" in strategy:
            query = f'site:archive.org "{first_name} {last_name}"'
            reasoning = "Internet Archive has old versions with unredacted info"

        elif "ENEMIES" in strategy:
            query = f'"{first_name} {last_name}" (competitor OR critic OR "former employee")'
            reasoning = "Critics and competitors dig deeper than friends"

        elif "FAILURES" in strategy:
            query = f'"{first_name} {last_name}" (failed OR mistake OR apology OR "stepped down")'
            reasoning = "Failure narratives are less curated, more honest"

        else:
            query = f'"{org}" "{role}" contact -"{last_name}"'
            reasoning = "Random oblique strategy - search orthogonally"

        return {
            'oblique_strategy': strategy,
            'query': query,
            'reasoning': reasoning
        }


class PerspectiveShifterAgent:
    """
    Embodies different personas to generate diverse search strategies

    Personality: Method actor, shape-shifter
    """

    def __init__(self):
        self.name = "PerspectiveShifter"
        self.personalities = {
            'Recruiter': "I'm headhunting this person for a VP role",
            'Journalist': "I'm writing an investigative piece about them",
            'Stalker': "I'm obsessed and want every detail (ethically simulated)",
            'Competitor': "I need to know their strategy and contacts",
            'Lawyer': "I'm serving them papers and need verified address",
            'Fan': "I want to send them fan mail",
            'Hacker': "I'm social engineering their company (ethically simulated)",
            'Librarian': "I'm archiving their contributions to knowledge"
        }

    def search_as_persona(self, contact: Dict, persona: str) -> Dict:
        """Generate search from specific persona's perspective"""

        first_name = contact.get('first_name', '')
        last_name = contact.get('last_name', '')
        org = contact.get('organization', '')

        persona_mindset = self.personalities.get(persona, "Generic searcher")

        if persona == 'Recruiter':
            query = f'"{first_name} {last_name}" (resume OR CV OR "looking for") {org}'
            reasoning = "Recruiters search for career materials, job changes, professional updates"

        elif persona == 'Journalist':
            query = f'"{first_name} {last_name}" {org} (quote OR "said that" OR "according to")'
            reasoning = "Journalists search for quotable statements, press releases, attributed claims"

        elif persona == 'Stalker':
            query = f'"{first_name} {last_name}" (hometown OR education OR family OR hobby)'
            reasoning = "Personal details often leaked in alumni news, local press, hobby forums (ethically simulated)"

        elif persona == 'Competitor':
            query = f'"{first_name} {last_name}" (strategy OR roadmap OR "plans to" OR acquisition)'
            reasoning = "Competitors look for strategic info in investor calls, conference talks, leaked docs"

        elif persona == 'Lawyer':
            query = f'"{first_name} {last_name}" {org} (address OR "served with" OR legal OR court)'
            reasoning = "Legal searches find verified addresses, court filings, official registrations"

        elif persona == 'Fan':
            query = f'"{first_name} {last_name}" (AMA OR "ask me anything" OR Q&A OR office hours)'
            reasoning = "Fans look for interactive content - often has contact info for follow-up"

        elif persona == 'Hacker':
            query = f'{org} employee email format OR "{first_name[0]}{last_name}@" OR "{first_name}.{last_name}@"'
            reasoning = "Social engineers look for email patterns, org structure (ethically simulated)"

        elif persona == 'Librarian':
            query = f'"{first_name} {last_name}" (publication OR author OR "contributed to" OR citation)'
            reasoning = "Librarians archive contributions - papers often have author contact info"

        else:
            query = f'"{first_name} {last_name}" {org}'
            reasoning = "Generic search"

        return {
            'persona': persona,
            'mindset': persona_mindset,
            'query': query,
            'reasoning': reasoning
        }


class MetaCreativeCoordinator:
    """
    Coordinates meta-debugging and creative strategy generation

    When primary agents fail or plateau, invoke meta-layer
    """

    def __init__(self):
        self.meta_debugger = MetaDebuggerAgent()
        self.creative_strategist = CreativeStrategistAgent()
        self.perspective_shifter = PerspectiveShifterAgent()

    def invoke_meta_layer(self, contact: Dict, search_results: List[Dict], pass_number: int) -> Dict:
        """
        Invoke meta-layer when stuck

        Triggers:
        - All agents < 50% confidence
        - No improvement over previous pass
        - Requesting creative breakthrough
        """

        print(f"\n{'='*80}")
        print(f"🎭 META-CREATIVE LAYER ACTIVATED (Pass {pass_number})")
        print(f"{'='*80}")
        print(f"\nPrimary agents stuck. Stepping outside the frame...\n")

        # Step 1: Debug why we're stuck
        print("🔍 [MetaDebugger] Analyzing failure patterns...")
        debug_insight = self.meta_debugger.analyze_failure(search_results, contact)

        print(f"\n   Pattern: {debug_insight.failure_pattern}")
        print(f"   Root Cause: {debug_insight.root_cause}")
        print(f"   Proposed Fix: {debug_insight.proposed_fix}")

        # Step 2: Ask Socratic questions
        print(f"\n💭 [MetaDebugger] Socratic Questions:")
        questions = self.meta_debugger.ask_socratic_questions(contact)
        for i, q in enumerate(questions, 1):
            print(f"   {i}. {q}")

        # Step 3: Generate creative reframings
        print(f"\n🎨 [CreativeStrategist] Creative Reframings:")
        reframings = self.creative_strategist.generate_creative_reframings(contact)
        for i, r in enumerate(reframings, 1):
            print(f"\n   Reframing {i}: {r.perspective}")
            print(f"      Question: {r.question}")
            print(f"      Strategy: {r.search_strategy}")
            print(f"      Reasoning: {r.reasoning}")

        # Step 4: Apply oblique strategy
        print(f"\n🎲 [CreativeStrategist] Oblique Strategy:")
        oblique = self.creative_strategist.apply_oblique_strategy(contact)
        print(f"   Strategy: {oblique['oblique_strategy']}")
        print(f"   Query: {oblique['query']}")
        print(f"   Reasoning: {oblique['reasoning']}")

        # Step 5: Perspective shifting
        print(f"\n🎭 [PerspectiveShifter] Persona Searches:")
        personas = random.sample(list(self.perspective_shifter.personalities.keys()), 3)
        persona_searches = []

        for persona in personas:
            search = self.perspective_shifter.search_as_persona(contact, persona)
            persona_searches.append(search)
            print(f"\n   As {persona}: \"{search['mindset']}\"")
            print(f"      Query: {search['query']}")
            print(f"      Reasoning: {search['reasoning']}")

        print(f"\n{'='*80}")
        print("🎭 META-CREATIVE LAYER COMPLETE")
        print(f"{'='*80}")
        print(f"\nGenerated {len(reframings)} reframings + {len(persona_searches)} persona searches")
        print("Primary agents can now try these novel strategies...\n")

        return {
            'debug_insight': debug_insight.__dict__,
            'socratic_questions': questions,
            'creative_reframings': [r.__dict__ for r in reframings],
            'oblique_strategy': oblique,
            'persona_searches': persona_searches,
            'meta_layer_invoked': True,
            'pass_number': pass_number
        }


def demo():
    """Demonstrate meta-creative layer"""

    # Simulate stuck search
    contact = {
        'first_name': 'Emil',
        'last_name': 'Michael',
        'organization': 'Department of Defense',
        'role_title': 'Former Uber Executive',
        'company_website': 'defense.gov'
    }

    # Simulate failed search results
    search_results = [
        {'agent': 'ProfessionalNetworker', 'confidence': 45, 'query': 'Emil Michael LinkedIn'},
        {'agent': 'InvestigativeJournalist', 'confidence': 40, 'query': 'Emil Michael filetype:pdf'},
        {'agent': 'AcademicResearcher', 'confidence': 0, 'query': 'skipped'}
    ]

    # Invoke meta-layer
    coordinator = MetaCreativeCoordinator()
    meta_result = coordinator.invoke_meta_layer(contact, search_results, pass_number=4)

    # Save result
    output_file = f"meta-creative-output-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(meta_result, f, indent=2)

    print(f"\n✅ Meta-creative output saved: {output_file}")
    print("\nThis demonstrates:")
    print("  ✓ Stepping outside the search frame")
    print("  ✓ Debugging why agents are stuck")
    print("  ✓ Generating creative reframings")
    print("  ✓ Perspective shifting")
    print("  ✓ Novel search strategies")
    print("\n🪂 Sometimes the solution requires changing the question.")


if __name__ == "__main__":
    demo()
