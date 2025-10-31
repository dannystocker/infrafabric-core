#!/usr/bin/env python3
"""
Example: IF Guardians Debate

Demonstrates the Guardian panel evaluating a proposal with weighted debate.

Usage:
    python guardian_debate_example.py
"""

import sys
sys.path.insert(0, '/home/setup/infrafabric')

from infrafabric.guardians import debate_proposal


def main():
    print("="*60)
    print("IF GUARDIANS LIBRARY - EXAMPLE")
    print("="*60 + "\n")

    # Example 1: Persona Agent Proposal
    print("EXAMPLE 1: Persona Agent Pilot\n")

    proposal1 = {
        'title': 'Persona Agent Pilot (5-10 public figures)',
        'description': '''
        Use AI to generate personalized outreach drafts by modeling
        tone/priorities from public data (podcasts, articles, talks).

        Approach:
        - Public figures only (podcast hosts, researchers, authors)
        - Tone modeling from public data
        - 3 variants per person
        - Human review mandatory before send
        - Label all drafts as AI-generated
        ''',
        'risks': [
            'Privacy violation if modeling extends to private data',
            'Impersonation risk if not clearly labeled',
            'GDPR Art. 22 (automated decision-making)',
            'Recipients may feel manipulated',
            'Bias in tone modeling'
        ],
        'safeguards': [
            'Public data only (no private information)',
            'Explicit labeling: [AI-DRAFT inspired by {Name}]',
            'Human review mandatory',
            'No audio/video synthesis',
            'Easy opt-out mechanism',
            'Provenance tracking'
        ]
    }

    result1 = debate_proposal(proposal1, proposal_type='ethical', verbose=True)

    print(f"\n📄 Decision: {result1.decision.upper()}")
    print(f"📋 Required safeguards: {len(result1.required_safeguards)}")

    # Save debate result
    from infrafabric.guardians import GuardianPanel
    panel = GuardianPanel()
    panel.save_debate(result1, 'debate1_result.json')
    print(f"💾 Saved to: debate1_result.json\n")

    # Example 2: Technical Change
    print("\n" + "="*60)
    print("EXAMPLE 2: CMP Simulation Parameter Change\n")

    proposal2 = {
        'title': 'Change CMP Simulation Parameters',
        'description': '''
        Adjust late bloomer detection threshold from 85% to 90%
        confidence improvement to reduce false positives.

        Impact:
        - More stringent late bloomer criteria
        - May miss some edge cases
        - Better precision, potentially lower recall
        ''',
        'risks': [
            'May miss genuine late bloomers',
            'Changes reproducibility of prior results',
            'Affects benchmark comparisons'
        ],
        'safeguards': [
            'Document parameter change in manifest',
            'Run comparison (old vs new parameters)',
            'Version bump for simulation code',
            'Update reproducibility documentation'
        ]
    }

    result2 = debate_proposal(proposal2, proposal_type='technical', verbose=True)

    print(f"\n📄 Decision: {result2.decision.upper()}")

    # Example 3: Business Decision
    print("\n" + "="*60)
    print("EXAMPLE 3: Freemium Pricing Model\n")

    proposal3 = {
        'title': 'Freemium Model for IF Contact Discovery',
        'description': '''
        Offer free tier (5 contacts/month) and paid tier ($49/mo for 100 contacts).

        Free tier:
        - SimulatedUser agent only (conservative)
        - Confidence scores visible
        - Self-service onboarding

        Paid tier:
        - All 6 agents (weighted coordination)
        - Priority support
        - Bulk export
        ''',
        'risks': [
            'Free tier abuse (fake accounts)',
            'Cannibalization of paid tier',
            'Support cost for free users',
            'Complex pricing communication'
        ],
        'safeguards': [
            'Email verification for free tier',
            'Rate limiting (5/month hard limit)',
            'Clear upgrade prompts',
            'Track conversion metrics'
        ]
    }

    result3 = debate_proposal(proposal3, proposal_type='business', verbose=True)

    print(f"\n📄 Decision: {result3.decision.upper()}")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"\nExample 1 (Persona Agents): {result1.decision.upper()}")
    print(f"  Safeguards required: {len(result1.required_safeguards)}")
    print(f"\nExample 2 (Technical Change): {result2.decision.upper()}")
    print(f"  Safeguards required: {len(result2.required_safeguards)}")
    print(f"\nExample 3 (Business Model): {result3.decision.upper()}")
    print(f"  Safeguards required: {len(result3.required_safeguards)}")

    print("\n✅ IF Guardians library demonstration complete!\n")


if __name__ == '__main__':
    main()
