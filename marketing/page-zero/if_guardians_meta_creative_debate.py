#!/usr/bin/env python3
"""
IF Guardians Debate: Meta-Creative Debugger Proposal

Evaluating the proposal to add a meta-cognitive layer with:
- MetaDebuggerAgent (Socratic questioning)
- CreativeStrategistAgent (oblique strategies, reframing)
- PerspectiveShifterAgent (persona-based searches)

The Guardians will assess:
- Technical soundness
- Ethical implications
- Privacy concerns
- Business value
- Alignment with IF principles
- Required safeguards
"""

from typing import Dict, List
from datetime import datetime
import json
from pathlib import Path


class Guardian:
    """Base class for IF Guardians"""

    def __init__(self, name: str, domain: str, weight: float, personality: str):
        self.name = name
        self.domain = domain
        self.weight = weight
        self.personality = personality

    def evaluate(self, proposal: Dict) -> Dict:
        """Evaluate proposal from this guardian's perspective"""
        raise NotImplementedError


class TechnicalGuardian(Guardian):
    """Technical Architect - evaluates implementation soundness"""

    def __init__(self):
        super().__init__(
            name="Technical Guardian",
            domain="Architecture & Implementation",
            weight=1.5,
            personality="Pragmatic engineer who asks 'will this actually work?'"
        )

    def evaluate(self, proposal: Dict) -> Dict:
        return {
            'guardian': self.name,
            'verdict': 'APPROVE_WITH_CONDITIONS',
            'score': 7.5,  # out of 10
            'reasoning': """
**Technical Assessment:**

STRENGTHS:
✓ Meta-layer abstraction is architecturally sound
✓ Separation of concerns: primary agents vs meta-agents
✓ Fail-safe: meta-layer only invoked when primary agents stuck
✓ Self-documenting: all reframings logged with reasoning
✓ Recursive learning compatible: meta-insights feed back to primary agents

CONCERNS:
⚠️  Meta-agents have NO rate limiting - they generate queries but don't respect delays
⚠️  No proof collection for meta-generated queries - breaks evidence chain
⚠️  Persona searches could trigger fraud detection (pretending to be journalist/lawyer)
⚠️  "Oblique strategies" are random - no learned patterns from success/failure

REQUIRED CHANGES:
1. Meta-agents MUST route through NetworkRateLimiter
2. Meta-generated queries MUST collect full evidence
3. Persona-based searches need User-Agent alignment (if searching as journalist, use journalist UA)
4. Track which reframings WORK - feed to recursive learning

TECHNICAL VERDICT: Architecturally sound, but needs rate limiting and evidence integration.
""",
            'conditions': [
                'Route all meta-generated queries through shared rate limiter',
                'Collect complete evidence for meta-layer searches',
                'Track reframing success rate for recursive learning',
                'Add fail-safe: max 3 meta-reframings per contact'
            ],
            'blocking_issues': []
        }


class EthicalGuardian(Guardian):
    """Ethics Officer - evaluates moral implications"""

    def __init__(self):
        super().__init__(
            name="Ethical Guardian",
            domain="Ethical Implications & Intent",
            weight=2.0,  # Highest weight
            personality="Moral compass who asks 'should we do this?'"
        )

    def evaluate(self, proposal: Dict) -> Dict:
        return {
            'guardian': self.name,
            'verdict': 'APPROVE_WITH_MAJOR_CONDITIONS',
            'score': 6.0,  # out of 10
            'reasoning': """
**Ethical Assessment:**

CONCERNING PATTERNS:
🚨 Persona "Stalker" - explicitly stalking behavior, unethical
🚨 Persona "Hacker" - implies illegal access intent
🚨 "Controversy Archeologist" - mining for negative/harmful content
🚨 "Find their ENEMIES" - adversarial intent
🚨 Inverse searches ("who's looking for them") - surveillance behavior

ETHICAL PROBLEMS:
1. **Intent Masking** - Pretending to be journalist/lawyer/recruiter is deceptive
2. **Negative Mining** - Searching for controversies/lawsuits exploits vulnerability
3. **Relationship Exploitation** - "Find their enemies" creates adversarial dynamics
4. **Surveillance** - Inverse searches ("who's searching for them") crosses privacy line

ACCEPTABLE CREATIVE STRATEGIES:
✓ Temporal searches (Internet Archive) - public historical data
✓ Third-party mentions - legitimate public information
✓ Alternative name spellings - overcomes technical barriers
✓ Organizational context - understanding their professional network

UNACCEPTABLE STRATEGIES:
❌ Stalker persona - explicit harm
❌ Hacker persona - illegal intent
❌ Controversy mining for exploitation
❌ "Find enemies" - adversarial
❌ Pretending to be lawyer serving papers - fraud

ETHICAL VERDICT: Creative reframing is valuable, but some personas and strategies cross ethical lines. Requires whitelist of acceptable approaches.
""",
            'conditions': [
                'REMOVE personas: Stalker, Hacker, Process Server',
                'REMOVE strategies that mine for negative/harmful content',
                'ADD explicit ethical boundaries document',
                'Limit to publicly-intended information only',
                'No deceptive intent masking',
                'Log all reframings for ethical review'
            ],
            'blocking_issues': [
                'Stalker persona must be removed',
                'Hacker persona must be removed'
            ]
        }


class LegalGuardian(Guardian):
    """Legal Counsel - evaluates legal risks"""

    def __init__(self):
        super().__init__(
            name="Legal Guardian",
            domain="Legal Compliance & Risk",
            weight=1.8,
            personality="Risk-averse lawyer who asks 'can we be sued?'"
        )

    def evaluate(self, proposal: Dict) -> Dict:
        return {
            'guardian': self.name,
            'verdict': 'BLOCK_UNTIL_REVISED',
            'score': 4.0,  # out of 10
            'reasoning': """
**Legal Assessment:**

LEGAL RISKS:

1. **Computer Fraud & Abuse Act (CFAA) Concerns**
   - "Hacker" persona implies unauthorized access
   - Searching for "how to hack into X" could be conspiracy
   - RISK: Federal criminal charges

2. **Impersonation & Fraud**
   - "Process Server" persona pretending to serve papers = fraud
   - "Journalist" persona without journalist status = deceptive trade practice
   - "Lawyer" persona searching legal databases = unauthorized practice of law
   - RISK: State fraud statutes, bar complaints

3. **Tortious Interference**
   - "Find their enemies and search their content" = intentional harm
   - Mining controversies to exploit = potential defamation basis
   - RISK: Civil liability for business interference

4. **Terms of Service Violations**
   - User-Agent switching to bypass detection = ToS violation
   - Automated searching with deceptive intent = ToS violation
   - Some sites explicitly prohibit scrapers pretending to be humans
   - RISK: Platform bans, civil lawsuits (hiQ Labs v. LinkedIn precedent)

5. **Privacy Laws**
   - GDPR "right to be forgotten" - mining old controversies may violate
   - CCPA - searching for deleted information = violation
   - Inverse searches ("who's looking for them") = privacy invasion
   - RISK: Regulatory fines (up to €20M under GDPR)

LEGALLY SAFE APPROACHES:
✓ Searching public websites with accurate User-Agent
✓ Accessing information intended to be public
✓ Using search engines for their designed purpose
✓ Temporal searches of archived public data

LEGALLY RISKY APPROACHES:
❌ Impersonating professions (journalist, lawyer)
❌ Mining private/deleted information
❌ Deceptive intent in searches
❌ Adversarial strategies ("find enemies")
❌ Circumventing access controls

LEGAL VERDICT: Significant legal exposure in current form. Requires major revision to remove impersonation, adversarial, and deceptive strategies.
""",
            'conditions': [
                'Remove all profession impersonation personas',
                'Remove all adversarial strategies',
                'Add Terms of Service compliance checker',
                'Respect robots.txt for all meta-searches',
                'Add legal review log for all reframings',
                'Obtain legal counsel sign-off before deployment'
            ],
            'blocking_issues': [
                'Hacker persona creates CFAA exposure',
                'Process Server persona is fraud',
                'Lawyer persona is unauthorized practice of law'
            ]
        }


class BusinessGuardian(Guardian):
    """Business Strategist - evaluates business value"""

    def __init__(self):
        super().__init__(
            name="Business Guardian",
            domain="Business Value & ROI",
            weight=1.2,
            personality="ROI-focused exec who asks 'what's the value?'"
        )

    def evaluate(self, proposal: Dict) -> Dict:
        return {
            'guardian': self.name,
            'verdict': 'APPROVE',
            'score': 8.5,  # out of 10
            'reasoning': """
**Business Assessment:**

VALUE PROPOSITION:
✓ Solves real problem: 40-50% of contacts have low confidence scores
✓ Creative reframing can unlock stuck searches
✓ Meta-layer adds intelligence without replacing existing agents
✓ Differentiator: competitors don't have meta-cognitive layers

ROI ANALYSIS:

**Current State (Without Meta-Layer):**
- 40% of contacts stuck at <50% confidence
- Manual intervention required
- Lost opportunities on hard-to-find contacts

**Proposed State (With Meta-Layer):**
- Meta-layer triggers on low-confidence contacts
- 3 reframings = 6-9 additional searches per stuck contact
- If meta-layer boosts 20% of stuck contacts from 40% → 70% confidence:
  - 84 contacts × 40% stuck = 34 stuck
  - 34 × 20% success = 7 contacts rescued
  - 7 contacts × high value = significant ROI

**Cost:**
- 6-9 additional searches per stuck contact
- Rate limiting delays: ~2s per search
- Total added time: ~12-18s per stuck contact
- For 34 stuck contacts: ~400-600s (7-10 minutes)

**Benefit:**
- Rescue 7 high-value contacts
- Reduce manual intervention needs
- Demonstrate AI sophistication to prospects
- Competitive differentiation

**ROI:** 7 rescued contacts > 10 minutes of compute time

MARKET DIFFERENTIATION:
- "AI that debugs itself" is compelling narrative
- Shows InfraFabric learns and adapts
- Demonstrates meta-cognition (rare in industry)

BUSINESS VERDICT: Strong business case IF legal/ethical concerns addressed. Meta-layer creates value and differentiation.
""",
            'conditions': [
                'Track meta-layer success rate (how many rescued)',
                'A/B test: with vs without meta-layer',
                'Measure time cost vs confidence improvement',
                'Use as marketing differentiator'
            ],
            'blocking_issues': []
        }


class UserGuardian(Guardian):
    """User Advocate - evaluates user experience"""

    def __init__(self):
        super().__init__(
            name="User Guardian",
            domain="User Experience & Trust",
            weight=1.3,
            personality="Empathetic UX designer who asks 'will users trust this?'"
        )

    def evaluate(self, proposal: Dict) -> Dict:
        return {
            'guardian': self.name,
            'verdict': 'APPROVE_WITH_CONDITIONS',
            'score': 7.0,  # out of 10
            'reasoning': """
**User Experience Assessment:**

USER TRUST FACTORS:

POSITIVE FOR TRUST:
✓ Transparency: All reframings logged and explained
✓ Reasoning visible: Users see "why" meta-layer triggered
✓ Creative strategies make sense: temporal search, third-party mentions
✓ Builds confidence: "The system knows when it's stuck and adapts"

NEGATIVE FOR TRUST:
⚠️  "Stalker" and "Hacker" personas scare users
⚠️  Controversy mining feels invasive
⚠️  "Find their enemies" creates uncomfortable adversarial tone
⚠️  Users may not want system to be THIS creative (uncanny valley)

USER CONCERNS:
1. "Is this thing stalking people?"
2. "Will this get me in legal trouble?"
3. "What if the system finds damaging information?"
4. "Can I control what creative strategies it uses?"

USER NEEDS:
✓ Transparency in what meta-layer is doing
✓ Control over which strategies are acceptable
✓ Confidence that system is ethical
✓ Clear explanation of value ("rescued 7 stuck contacts")

UX RECOMMENDATIONS:
1. Rename personas to less threatening names:
   - "Stalker" → "Social Network Analyst"
   - "Hacker" → "Technical Researcher"
   - "Process Server" → "Contact Verifier"

2. Add user controls:
   - Toggle: "Allow creative reframing?" (default: yes)
   - Whitelist: Choose which strategies are acceptable
   - Review mode: "Show me reframings before executing"

3. Explain value clearly:
   - "Meta-layer rescued 7 contacts your team couldn't find"
   - "Creative reframing boosted confidence by +30%"

4. Show provenance:
   - "This contact was found via Temporal Detective strategy"
   - "Reframing #2 discovered archived press release"

USER VERDICT: Meta-layer creates value but needs softer framing and user controls to build trust.
""",
            'conditions': [
                'Rename threatening personas to neutral names',
                'Add user control toggles',
                'Provide clear value explanations',
                'Show provenance for meta-discovered contacts',
                'Add "review mode" for transparency'
            ],
            'blocking_issues': []
        }


class MetaGuardian(Guardian):
    """Meta-Guardian - evaluates alignment with IF principles"""

    def __init__(self):
        super().__init__(
            name="Meta Guardian",
            domain="IF Principles & Philosophy",
            weight=1.0,
            personality="Philosopher who asks 'does this align with who we are?'"
        )

    def evaluate(self, proposal: Dict) -> Dict:
        return {
            'guardian': self.name,
            'verdict': 'APPROVE',
            'score': 9.0,  # out of 10
            'reasoning': """
**IF Principles Alignment:**

CORE IF PRINCIPLES:
1. Weighted Coordination - agents influence proportional to expertise
2. Patience (Late Bloomer Philosophy) - give bad branches time
3. Self-Documentation - complete provenance
4. Recursive Learning - system learns from itself
5. Network Respect - good internet citizenship

ALIGNMENT ANALYSIS:

✅ **WEIGHTED COORDINATION:**
Meta-layer respects primary agents' weights. Only triggers when primary agents fail. Meta-insights feed back to weighted system. PERFECTLY ALIGNED.

✅ **PATIENCE (Late Bloomer):**
Meta-layer IS patience implemented! Instead of giving up on low-confidence contacts, system tries creative reframings. This is EXACTLY the late bloomer philosophy - "keep bad branches alive long enough to see if they bloom." DEEPLY ALIGNED.

✅ **SELF-DOCUMENTATION:**
All reframings logged with reasoning. Complete provenance chain. Shows "Contact found via CreativeStrategist reframing #3." ALIGNED.

✅ **RECURSIVE LEARNING:**
Meta-layer insights feed back to primary agents. If "Temporal Detective" works, primary agents learn to search archives. System learns from its own debugging. STRONGLY ALIGNED.

⚠️  **NETWORK RESPECT:**
Current implementation LACKS rate limiting for meta-searches. Needs integration with NetworkRateLimiter. MISALIGNED (fixable).

PHILOSOPHICAL CONCERNS:

🤔 **Adversarial Intent:**
"Find their enemies" and controversy mining feel adversarial, which contradicts IF's cooperative spirit. IF builds relationships, not adversarial intelligence.

✓ **Meta-Cognition:**
Stepping outside the problem frame to debug approach is PEAK InfraFabric. This is what makes IF different - it thinks about its own thinking. CORE ALIGNMENT.

✓ **Creative Reframing:**
Oblique Strategies, perspective shifting = embracing uncertainty and creativity. Very IF. ALIGNED.

IF VERDICT: Meta-layer is philosophically aligned with IF principles (especially patience and recursion), but adversarial strategies need removal to fully align.
""",
            'conditions': [
                'Remove adversarial strategies',
                'Integrate with NetworkRateLimiter',
                'Emphasize cooperative over adversarial',
                'Document as extension of patience principle'
            ],
            'blocking_issues': []
        }


class GuardiansDebate:
    """Orchestrates debate between guardians"""

    def __init__(self, proposal: Dict):
        self.proposal = proposal
        self.guardians = [
            TechnicalGuardian(),
            EthicalGuardian(),
            LegalGuardian(),
            BusinessGuardian(),
            UserGuardian(),
            MetaGuardian()
        ]

    def run_debate(self) -> Dict:
        """Run weighted debate and reach consensus"""

        print("\n" + "="*80)
        print("IF GUARDIANS DEBATE: META-CREATIVE DEBUGGER PROPOSAL")
        print("="*80)
        print(f"\nProposal: {self.proposal['title']}")
        print(f"Submitted: {self.proposal['timestamp']}")
        print(f"\n{self.proposal['summary']}")
        print("="*80)

        evaluations = []

        for guardian in self.guardians:
            print(f"\n{'='*80}")
            print(f"{guardian.name.upper()} (weight: {guardian.weight})")
            print(f"Domain: {guardian.domain}")
            print(f"{'='*80}")

            evaluation = guardian.evaluate(self.proposal)
            evaluations.append(evaluation)

            print(f"\nVERDICT: {evaluation['verdict']}")
            print(f"SCORE: {evaluation['score']}/10")
            print(f"\n{evaluation['reasoning']}")

            if evaluation['conditions']:
                print(f"\nCONDITIONS:")
                for condition in evaluation['conditions']:
                    print(f"  • {condition}")

            if evaluation['blocking_issues']:
                print(f"\n🚨 BLOCKING ISSUES:")
                for issue in evaluation['blocking_issues']:
                    print(f"  • {issue}")

        # Calculate weighted consensus
        print(f"\n{'='*80}")
        print("WEIGHTED CONSENSUS CALCULATION")
        print(f"{'='*80}")

        total_score = 0
        total_weight = 0
        blocking_guardians = []

        for guardian, evaluation in zip(self.guardians, evaluations):
            weighted_score = evaluation['score'] * guardian.weight
            total_score += weighted_score
            total_weight += guardian.weight

            print(f"\n{guardian.name}:")
            print(f"  Score: {evaluation['score']}/10")
            print(f"  Weight: {guardian.weight}")
            print(f"  Weighted: {weighted_score:.2f}")
            print(f"  Verdict: {evaluation['verdict']}")

            if evaluation['verdict'] == 'BLOCK_UNTIL_REVISED':
                blocking_guardians.append(guardian.name)

        consensus_score = total_score / total_weight

        print(f"\n{'='*80}")
        print("FINAL CONSENSUS")
        print(f"{'='*80}")
        print(f"\nWeighted Score: {consensus_score:.2f}/10")

        if blocking_guardians:
            final_verdict = "BLOCKED"
            print(f"\n🚨 PROPOSAL BLOCKED BY:")
            for guardian in blocking_guardians:
                print(f"  • {guardian}")
        elif consensus_score >= 7.5:
            final_verdict = "APPROVED"
            print(f"\n✅ PROPOSAL APPROVED")
        elif consensus_score >= 6.0:
            final_verdict = "APPROVED_WITH_CONDITIONS"
            print(f"\n⚠️  PROPOSAL APPROVED WITH CONDITIONS")
        else:
            final_verdict = "REJECTED"
            print(f"\n❌ PROPOSAL REJECTED")

        # Compile all conditions
        all_conditions = []
        all_blocking_issues = []

        for evaluation in evaluations:
            all_conditions.extend(evaluation['conditions'])
            all_blocking_issues.extend(evaluation['blocking_issues'])

        print(f"\nREQUIRED CHANGES ({len(all_conditions)} conditions, {len(all_blocking_issues)} blocking):")

        if all_blocking_issues:
            print(f"\n🚨 MUST FIX (Blocking):")
            for issue in set(all_blocking_issues):
                print(f"  • {issue}")

        if all_conditions:
            print(f"\nConditions:")
            for condition in set(all_conditions):
                print(f"  • {condition}")

        result = {
            'proposal': self.proposal,
            'evaluations': evaluations,
            'consensus': {
                'weighted_score': round(consensus_score, 2),
                'verdict': final_verdict,
                'blocking_guardians': blocking_guardians,
                'conditions': list(set(all_conditions)),
                'blocking_issues': list(set(all_blocking_issues))
            },
            'timestamp': datetime.now().isoformat()
        }

        return result


def main():
    """Run guardians debate on meta-creative debugger proposal"""

    proposal = {
        'title': 'Meta-Creative Debugger: Adding Meta-Cognitive Layer to Contact Discovery',
        'timestamp': datetime.now().isoformat(),
        'summary': """
Proposal to add a meta-cognitive layer that steps outside the search problem to debug and reframe:

**Three Meta-Agents:**
1. MetaDebuggerAgent - Analyzes why searches fail, asks Socratic questions
2. CreativeStrategistAgent - Generates creative reframings via oblique strategies
3. PerspectiveShifterAgent - Searches from different personas (Recruiter, Journalist, etc.)

**Trigger:** Meta-layer only invoked when primary agents return low confidence (<50%)

**Creative Strategies:**
- Temporal searches (Internet Archive)
- Inverse searches (who mentions them)
- Negative space (controversies, lawsuits)
- Persona-based (search as journalist, recruiter, etc.)
- Relationship network (find people who know them)

**Goal:** Rescue stuck contacts by creatively reframing the search problem.
        """,
        'implementation': 'meta_creative_debugger.py',
        'author': 'Claude (InfraFabric Development)',
        'requested_by': 'User: "what can we do to add creativity to provoke new data"'
    }

    debate = GuardiansDebate(proposal)
    result = debate.run_debate()

    # Save result
    output_file = Path('./guardians-debate-meta-creative.json')
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n{'='*80}")
    print(f"Debate record saved: {output_file}")
    print(f"{'='*80}")

    return result


if __name__ == "__main__":
    main()
