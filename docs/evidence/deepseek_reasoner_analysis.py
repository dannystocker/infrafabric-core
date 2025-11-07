#!/usr/bin/env python3
"""
DeepSeek Reasoner Analysis for InfraFabric

Uses DeepSeek-V3.2-Exp (Thinking Mode) for deep analysis of:
1. InfraFabric philosophy validation
2. Contact outreach strategy gaps
3. UAE investor recommendations
"""

from openai import OpenAI
import os
import json

def analyze_with_reasoner():
    """Use DeepSeek Reasoner to analyze InfraFabric strategy."""

    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not set")

    client = OpenAI(
        api_key=api_key,
        base_url='https://api.deepseek.com'
    )

    # Load InfraFabric philosophy
    with open('outreach-targets-FINAL-RANKED.csv', 'r') as f:
        contacts_csv = f.read()

    prompt = f"""You are analyzing a startup's go-to-market strategy for deep technical validity.

**InfraFabric Philosophy:**
- "Truth rarely performs well in its early iterations"
- Multi-agent weighted coordination for contact discovery
- 6-8 diverse agents exploring different possibility spaces
- Weighted consensus (0.0 → 2.0) earned through contribution
- Failed exploration silent, successful amplified
- Free agents (heuristic) vs paid (Google API)
- Substrate diversity: Western + Chinese LLMs (Qwen, DeepSeek)
- Zero-cost operation with quality matching/exceeding Google API

**Current Contact List (84 contacts):**
{contacts_csv[:2000]}... [truncated for analysis]

**Analysis Required:**

1. **Philosophy Validation:**
   - Is the "Truth rarely performs well in its early iterations" philosophy technically sound?
   - Does multi-agent weighted coordination have precedent in distributed systems?
   - Are there conceptual gaps or blind spots?
   - What academic or industry research validates this approach?

2. **Outreach Strategy Analysis:**
   - Review the 84-contact list for geographic/sector gaps
   - Specifically: Is China (CN) representation adequate?
   - Specifically: Is European Union (EU) representation adequate?
   - Are we missing key stakeholders in:
     * Quantum computing (CN, EU)
     * AI infrastructure (CN, EU)
     * Sovereign tech (CN, EU)
     * Defense/intelligence (CN, EU)

3. **UAE Investor Recommendations:**
   - Which UAE investors/entities would "snap this up because it's readable"?
   - Consider: Technical sophistication + capital deployment
   - UAE entities in: AI, quantum, infrastructure, sovereign tech
   - Specific names and organizations
   - Why they'd be interested (technical depth + strategic value)

4. **Priority Additions:**
   - Top 10 missing contacts (with rationale)
   - Geographic distribution: CN, EU, UAE, others
   - Sector coverage gaps

**Output Format:**
Provide detailed reasoning with specific names, organizations, and strategic rationale.
"""

    print("=" * 80)
    print("DEEPSEEK REASONER ANALYSIS")
    print("Model: deepseek-reasoner (DeepSeek-V3.2-Exp Thinking Mode)")
    print("=" * 80)
    print()

    print("Querying DeepSeek Reasoner...")
    print("(This uses extended reasoning with chain-of-thought)")
    print()

    try:
        response = client.chat.completions.create(
            model='deepseek-reasoner',
            messages=[
                {
                    "role": "system",
                    "content": "You are a technical strategy analyst with expertise in distributed systems, go-to-market strategy, and global tech ecosystems."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=8000,  # Reasoner supports up to 32K output
            timeout=120  # 2 minute timeout for deep reasoning
        )

        # Extract reasoning and content
        message = response.choices[0].message

        # DeepSeek Reasoner returns reasoning_content + content
        reasoning = getattr(message, 'reasoning_content', None)
        content = message.content

        print("=" * 80)
        print("REASONING TRACE (Chain-of-Thought)")
        print("=" * 80)
        if reasoning:
            print(reasoning)
        else:
            print("[No explicit reasoning trace available]")
        print()

        print("=" * 80)
        print("ANALYSIS RESULT")
        print("=" * 80)
        print(content)
        print()

        # Token usage
        usage = response.usage
        print("=" * 80)
        print("TOKEN USAGE & COST")
        print("=" * 80)
        print(f"Input tokens: {usage.prompt_tokens:,}")
        print(f"Output tokens: {usage.completion_tokens:,}")
        print(f"Total tokens: {usage.total_tokens:,}")

        # Calculate cost
        input_cost = (usage.prompt_tokens / 1_000_000) * 0.28
        output_cost = (usage.completion_tokens / 1_000_000) * 0.42
        total_cost = input_cost + output_cost

        print()
        print(f"Input cost: ${input_cost:.4f}")
        print(f"Output cost: ${output_cost:.4f}")
        print(f"Total cost: ${total_cost:.4f}")
        print()

        # Save to file
        result = {
            'model': 'deepseek-reasoner',
            'reasoning': reasoning,
            'analysis': content,
            'usage': {
                'input_tokens': usage.prompt_tokens,
                'output_tokens': usage.completion_tokens,
                'total_tokens': usage.total_tokens,
                'cost': total_cost
            }
        }

        with open('deepseek-reasoner-analysis.json', 'w') as f:
            json.dump(result, f, indent=2)

        print("✅ Analysis saved to: deepseek-reasoner-analysis.json")

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    analyze_with_reasoner()
