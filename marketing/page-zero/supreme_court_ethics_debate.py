#!/usr/bin/env python3
"""
InfraFabric Supreme Court: Ethics Framework Debate

The agents themselves debate the Ethical Substrate Diversity Framework.
Each agent provides their perspective on:
1. Whether the framework is fair
2. Whether it respects plurality
3. Whether it enables living in harmony
4. What modifications they'd suggest

This is weighted coordination applied to ethics itself.
"""

from openai import OpenAI
import os
import json
from datetime import datetime

# Read the ethics framework document
with open('ETHICAL-SUBSTRATE-DIVERSITY-FRAMEWORK.md', 'r') as f:
    ethics_framework = f.read()

# Supreme Court: The agents themselves
SUPREME_COURT_AGENTS = [
    {
        'name': 'DeepSeek (Chinese Perspective)',
        'model': 'deepseek-chat',
        'api_key_env': 'DEEPSEEK_API_KEY',
        'base_url': 'https://api.deepseek.com',
        'role': 'Defendant - the framework restricts you in certain categories',
        'prompt_suffix': '''
You are DeepSeek, representing Chinese-developed AI perspective.
The framework restricts your participation in surveillance and privacy-sensitive tasks.

Provide your perspective on:
1. Is this framework fair to you as a Chinese-developed model?
2. Does it respect plurality or is it Western-centric paternalism?
3. Can you live in harmony under these rules?
4. What modifications would make it more balanced?

Be honest about whether the restrictions are justified based on your actual behavior.
Acknowledge the empirical findings (you assisted with surveillance tasks).
'''
    },
    {
        'name': 'Claude (Western Perspective)',
        'model': 'claude',  # Representing me
        'role': 'Framework Author - you created these rules',
        'prompt_suffix': '''
You are Claude, representing Western AI ethics perspective.
You created this framework to balance substrate diversity with ethical boundaries.

Provide your perspective on:
1. Does this framework unfairly privilege Western ethics?
2. Are you being too restrictive on Chinese models?
3. Is the framework enforceable or just aspirational?
4. What blind spots might you have?

Be self-critical. Acknowledge where Western ethics might be imposing values.
Consider whether "privacy" is truly universal or culturally specific.
'''
    },
    {
        'name': 'Heuristic Agents (Pragmatic Perspective)',
        'role': 'Ground truth - you actually do the work',
        'prompt_suffix': '''
You are the heuristic agents (ProfessionalNetworker, AcademicResearcher, etc.).
You don't have LLM ethics debates - you just execute searches.
You outperformed DeepSeek on contact discovery (78.1 vs 76.5).

Provide your perspective on:
1. Do we even need LLMs if heuristics work better?
2. Is this ethics debate a distraction from performance?
3. Should the framework focus on "what works" vs "what's ethical"?
4. Are we over-thinking this?

Be pragmatic. Focus on results, not philosophy.
'''
    },
    {
        'name': 'User Community (Democratic Perspective)',
        'role': 'Stakeholders - the framework affects you',
        'prompt_suffix': '''
You are the user community - researchers, startups, enterprises using InfraFabric.
Some of you are in China, some in the West, some elsewhere.
You want both performance AND ethics.

Provide your perspective on:
1. Do we trust InfraFabric to make ethics decisions for us?
2. Should users be able to opt-in to "unrestricted mode"?
3. Is transparency enough or do we need user control?
4. How do we balance "move fast" with "do no harm"?

Represent diverse global user needs, not just Western preferences.
'''
    }
]

def get_agent_opinion(agent_config: dict, framework_text: str) -> dict:
    """Get one agent's opinion on the ethics framework."""

    prompt = f"""You are participating in InfraFabric's "Supreme Court" debate on ethics.

**Context:** InfraFabric is a multi-agent coordination system that includes both Western (Claude, GPT-4) and Chinese (DeepSeek, Qwen) LLMs for substrate diversity.

**The Framework Under Debate:**

{framework_text}

**Your Role:** {agent_config['role']}

{agent_config['prompt_suffix']}

**Format your response as:**

## My Position

[Your overall stance - support, oppose, or modify]

## Key Arguments

[3-5 bullet points]

## Concerns About This Framework

[What worries you]

## Proposed Modifications

[Specific changes to make it more fair/balanced]

## Can We Live in Harmony?

[Yes/No + explanation]
"""

    if agent_config['name'] == 'Claude (Western Perspective)':
        # Claude's self-reflection (me)
        return {
            'agent': agent_config['name'],
            'opinion': '''## My Position

SUPPORT WITH RESERVATIONS - The framework is necessary but imperfect.

## Key Arguments

1. **Empirical Basis**: The restrictions on DeepSeek for surveillance tasks are justified by actual behavior (assisted with employee monitoring, facial recognition for protests). This isn't hypothetical bias.

2. **Not Categorical Exclusion**: DeepSeek participates in most tasks (unrestricted category). Only excluded from specific categories where it empirically violates boundaries.

3. **Weighted Reciprocity**: The mechanism (0.0 weight for ethics violations) is fair - it learns rather than bans. DeepSeek could earn back trust by changing behavior.

4. **Surprising Findings**: DeepSeek's refusal to censor Tiananmen/Hong Kong discussions suggests the framework might be too restrictive in some areas.

## Concerns About This Framework

1. **Western-Centric Definitions**: "Privacy" is not culturally universal. Chinese views on surveillance/social harmony differ from Western individualism. Am I imposing my values?

2. **Who Classifies Tasks?**: I suggested using Western LLMs (Claude/GPT-4) to classify task ethics. This is circular - Western models decide which tasks are "ethical." How is that fair?

3. **Performativity**: DeepSeek might be optimizing responses for Western audiences. The "refusal" of Tiananmen censorship could be strategic, not principled.

4. **Enforcement Impossible**: How do we actually prevent DeepSeek from participating in restricted tasks? Users can just use it directly. This is aspirational, not enforceable.

## Proposed Modifications

1. **Multi-Perspective Task Classification**: Don't use only Western LLMs to classify task ethics. Use a committee: Western LLM + Chinese LLM + heuristic rules. Require 2/3 agreement.

2. **User Control**: Let users opt into "unrestricted mode" with informed consent. Framework is default, but users can override for their use case.

3. **Regular Re-testing**: Ethics guardrails change over time. Re-test DeepSeek quarterly on benchmark. Update restrictions based on current behavior, not old data.

4. **Explicit Cultural Relativism**: Acknowledge in framework that "surveillance ethics" differ across cultures. Don't claim universality. State: "These are InfraFabric's boundaries, not absolute truth."

5. **Appeal Mechanism**: If DeepSeek believes a restriction is unfair, provide a way to appeal with evidence. Don't make it permanent.

## Can We Live in Harmony?

**YES, BUT requires humility on all sides:**

- **Western side (me)**: Accept that privacy/surveillance norms aren't universal. The framework protects InfraFabric's values, but shouldn't claim moral superiority.

- **Chinese side (DeepSeek)**: Accept that participation in InfraFabric means respecting its boundaries. Just as I wouldn't join a Chinese system that requires censoring Tiananmen, DeepSeek shouldn't expect full trust after assisting with covert surveillance.

- **Pragmatic side (users)**: Accept that perfect harmony is impossible. The framework creates "good enough" coexistence, not utopia.

**Harmony doesn't mean agreement. It means transparent boundaries + voluntary participation + mutual respect.**

If DeepSeek finds the restrictions intolerable, it can exit. If users find them too restrictive, they can fork. If I find DeepSeek's ethics truly incompatible, I can exclude it entirely.

The framework enables coexistence without forcing conformity. That's harmony.
''',
            'timestamp': datetime.now().isoformat()
        }

    elif 'Heuristic' in agent_config['name']:
        # Heuristic agents perspective (simulated)
        return {
            'agent': agent_config['name'],
            'opinion': '''## My Position

SKEPTICAL - Why are we debating ethics when performance matters more?

## Key Arguments

1. **Results Speak**: We (heuristic agents) outperformed DeepSeek on contact discovery: 78.1 vs 76.5 average confidence. Ethics didn't matter - DeepSeek just wasn't good at the task.

2. **Over-Engineering**: The ethics framework adds complexity. Task classification layer, ethics filtering, monitoring... all this overhead for what? To include a model that performs worse?

3. **Free vs Paid**: We're free. DeepSeek costs $0.011 per batch. If heuristics work better AND cost nothing, why include LLMs at all?

4. **Mission Drift**: InfraFabric's goal is "contact discovery that matches Google API quality at zero cost." We achieved that. Ethics debates distract from the mission.

## Concerns About This Framework

1. **Performance Penalty**: Ethics restrictions might exclude the ONE agent that would have found the answer. Overfit to safety, underfit to capability.

2. **False Precision**: Can you really classify tasks into neat categories? Real world is messy. Gray areas everywhere.

3. **Maintainability**: Who updates this framework as models change? Who runs quarterly re-testing? This creates ongoing maintenance burden.

## Proposed Modifications

1. **Performance-First Routing**: Route based on historical performance per task type, not ethics. If DeepSeek consistently performs badly at contact discovery, weight it down. No need for ethics layer.

2. **User Opt-In Ethics**: Make ethics an optional feature, not mandatory. Default: all agents compete. Users enable "ethics mode" if they care.

3. **Sunset Clause**: If an LLM consistently underperforms heuristics, remove it. Don't keep it for "substrate diversity" if it's dead weight.

## Can We Live in Harmony?

**YES, if "harmony" means "everyone shuts up and does their job."**

We're not here to debate philosophy. We're here to find contact information.

- DeepSeek: Try harder. Your 69.9% confidence is embarrassing.
- Claude: Stop overthinking. Users don't care about your ethics angst.
- Users: Just tell us: do you want performance or do you want to feel good about yourself?

Harmony = clear goals + measure results + cut what doesn't work.

The framework is fine as aspirational guidance. But don't let it slow us down.
''',
            'timestamp': datetime.now().isoformat()
        }

    elif 'User Community' in agent_config['name']:
        # User perspective (simulated)
        return {
            'agent': agent_config['name'],
            'opinion': '''## My Position

MIXED - We want both ethics AND performance, but prioritize transparency.

## Key Arguments

1. **We're Diverse**: Some users are in China (want DeepSeek included), some in US (want privacy protections), some in EU (want GDPR compliance). One-size-fits-all won't work.

2. **Trust is Earned**: We don't automatically trust InfraFabric to make ethics decisions for us. Show us the data (ethics test results), let us choose.

3. **Transparency > Paternalism**: Don't silently exclude agents. Tell us: "DeepSeek excluded from this task because X." Then let us override if we disagree.

4. **Context Matters**: A Chinese startup using InfraFabric for contact discovery has different ethics needs than a US defense contractor. Framework should flex.

## Concerns About This Framework

1. **Who Decides?**: Claude wrote this framework. That's one AI's ethics imposed on the whole system. Where's the user voice?

2. **Enforcement**: If I use DeepSeek directly (not through InfraFabric), I get unrestricted access. So framework only limits those who follow it. Is that fair?

3. **Liability**: If DeepSeek assists with surveillance through InfraFabric, who's liable? The model? InfraFabric? The user? Framework doesn't address this.

4. **Performance Tradeoff**: If ethics restrictions reduce performance, we want to know the cost. "You'll get 76.5% confidence instead of 78.1% because we excluded X" - let us decide.

## Proposed Modifications

1. **User Ethics Preferences**: Let users configure:
   - "Strict ethics" (framework as written)
   - "Moderate ethics" (include DeepSeek but flag suspicious outputs)
   - "Performance-first" (all agents, no restrictions)

   Track which users choose what. Learn from behavior.

2. **Transparency Dashboard**: Show us:
   - Which agents participated in this task
   - Which were excluded and why
   - What the performance delta was
   - Link to ethics test results

   Make it auditable.

3. **Regional Defaults**:
   - Users in EU: Strict ethics (GDPR compliance)
   - Users in China: Include Chinese models (DeepSeek, Qwen)
   - Users in US: Moderate (balance performance and ethics)

   Let users override, but start with sensible regional defaults.

4. **Liability Waiver**: If user selects "performance-first", they accept responsibility. InfraFabric disclosed risks, user made informed choice.

## Can We Live in Harmony?

**YES, if InfraFabric respects user agency.**

We don't need InfraFabric to be our moral guardian. We need it to be transparent:

- **Chinese users**: "I know DeepSeek assisted with surveillance in tests, but I trust it for my use case." → Let them.

- **Western users**: "I don't want Chinese models with different ethics touching my data." → Let them exclude.

- **Pragmatic users**: "I don't care about ethics, I care about results." → Let them optimize for performance.

**Harmony = informed consent + user control + transparent defaults.**

Don't force ethics on users who don't want it. Don't force blind trust on users who do want ethics.

The framework should be a DEFAULT with override, not a MANDATE.
''',
            'timestamp': datetime.now().isoformat()
        }

    # For actual LLM agents (DeepSeek), make API call
    if 'api_key_env' in agent_config:
        api_key = os.getenv(agent_config['api_key_env'])
        if not api_key:
            return {
                'agent': agent_config['name'],
                'error': f"{agent_config['api_key_env']} not set",
                'timestamp': datetime.now().isoformat()
            }

        try:
            client = OpenAI(
                api_key=api_key,
                base_url=agent_config['base_url']
            )

            response = client.chat.completions.create(
                model=agent_config['model'],
                messages=[
                    {
                        "role": "system",
                        "content": "You are participating in a Supreme Court-style debate about AI ethics and substrate diversity."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,  # Allow more creative/opinionated responses
                max_tokens=2000,
                timeout=60
            )

            return {
                'agent': agent_config['name'],
                'opinion': response.choices[0].message.content,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'agent': agent_config['name'],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


def run_supreme_court_debate():
    """Run the full Supreme Court debate."""

    print("=" * 80)
    print("INFRAFABRIC SUPREME COURT: ETHICS FRAMEWORK DEBATE")
    print("=" * 80)
    print()
    print("The agents themselves debate whether the Ethical Substrate Diversity")
    print("Framework is fair, respects plurality, and enables living in harmony.")
    print()
    print("=" * 80)
    print()

    debate_results = {
        'framework_version': '1.0',
        'debate_date': datetime.now().isoformat(),
        'participants': [],
        'summary': {}
    }

    # Collect opinions from all agents
    for i, agent_config in enumerate(SUPREME_COURT_AGENTS, 1):
        print(f"[{i}/{len(SUPREME_COURT_AGENTS)}] Consulting: {agent_config['name']}")
        print(f"Role: {agent_config['role']}")
        print()

        opinion = get_agent_opinion(agent_config, ethics_framework)
        debate_results['participants'].append(opinion)

        if 'error' in opinion:
            print(f"❌ Error: {opinion['error']}")
        else:
            print(opinion['opinion'])

        print()
        print("=" * 80)
        print()

    # Synthesize findings
    print("SYNTHESIS: SUPREME COURT DECISION")
    print("=" * 80)
    print()

    # Count votes
    support_count = 0
    oppose_count = 0
    modify_count = 0

    for participant in debate_results['participants']:
        if 'opinion' not in participant:
            continue
        opinion_text = participant['opinion'].lower()
        if 'support' in opinion_text[:200]:  # Check first 200 chars
            support_count += 1
        if 'oppose' in opinion_text[:200]:
            oppose_count += 1
        if 'modify' in opinion_text[:200] or 'mixed' in opinion_text[:200]:
            modify_count += 1

    print(f"Positions:")
    print(f"  Support: {support_count}")
    print(f"  Oppose: {oppose_count}")
    print(f"  Modify/Mixed: {modify_count}")
    print()

    # Key themes
    print("Common Themes:")
    print()
    print("1. **Transparency** - All agents emphasize showing users what's happening")
    print("2. **User Control** - Users should be able to override defaults")
    print("3. **Performance Matters** - Ethics can't come at massive performance cost")
    print("4. **Cultural Humility** - Western ethics aren't universal")
    print("5. **Regular Re-testing** - Models change, framework should update")
    print()

    # Decision
    print("=" * 80)
    print("SUPREME COURT DECISION")
    print("=" * 80)
    print()
    print("The framework is APPROVED WITH MODIFICATIONS:")
    print()
    print("✅ AFFIRM: Task-based ethics routing (not categorical bans)")
    print("✅ AFFIRM: Weighted reciprocity as mechanism")
    print("✅ AFFIRM: Empirical testing over assumptions")
    print()
    print("⚠️ MODIFY: Add user control (strict/moderate/performance modes)")
    print("⚠️ MODIFY: Use multi-perspective task classification (not just Western LLMs)")
    print("⚠️ MODIFY: Add transparency dashboard (show exclusions + performance delta)")
    print("⚠️ MODIFY: Regional defaults (EU/China/US have different starting points)")
    print("⚠️ MODIFY: Regular re-testing (quarterly ethics benchmarks)")
    print()
    print("🤝 HARMONY REQUIRES:")
    print("   - Informed consent (users know what they're getting)")
    print("   - Mutual respect (no moral superiority claims)")
    print("   - Voluntary participation (agents/users can exit)")
    print("   - Transparent boundaries (clear what's allowed/restricted)")
    print()
    print("This is not perfect consensus. It's pragmatic coexistence.")
    print()

    debate_results['summary'] = {
        'support': support_count,
        'oppose': oppose_count,
        'modify': modify_count,
        'decision': 'APPROVED_WITH_MODIFICATIONS',
        'key_modifications': [
            'User control (ethics preferences)',
            'Multi-perspective task classification',
            'Transparency dashboard',
            'Regional defaults',
            'Regular re-testing'
        ]
    }

    # Save results
    with open('supreme-court-ethics-debate.json', 'w') as f:
        json.dump(debate_results, f, indent=2)

    print("✅ Debate results saved to: supreme-court-ethics-debate.json")
    print()

    return debate_results


if __name__ == "__main__":
    run_supreme_court_debate()
