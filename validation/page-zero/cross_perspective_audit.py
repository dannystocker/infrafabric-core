#!/usr/bin/env python3
"""
Cross-Perspective Audit: DeepSeek Mirror Review
------------------------------------------------
External review recommendation #1:
"Assign a DeepSeek mirror sub-agent to review IF documents for CN/Asian
philosophical alignment (Daoist systems balance, emergent order, communal intelligence)"

Output: 1-page delta report on conceptual overlap and divergence
"""

import os
import json
from openai import OpenAI
from datetime import datetime

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

def run_cross_perspective_audit():
    """
    Use DeepSeek Reasoner to review InfraFabric philosophy through
    Chinese/Asian systems thinking lens
    """

    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url='https://api.deepseek.com'
    )

    # Read the core IF documents
    documents = {
        'ethics_framework': 'ETHICAL-SUBSTRATE-DIVERSITY-FRAMEWORK.md',
        'ai_wellbeing': 'AI-WELLBEING-FRAMEWORK.md',
        'complete_docs': 'INFRAFABRIC-COMPLETE-DOCUMENTATION.md'
    }

    corpus = ""
    for name, filename in documents.items():
        try:
            with open(filename, 'r') as f:
                content = f.read()
                corpus += f"\n\n### {name.upper()}\n{content[:5000]}\n"  # First 5k chars each
        except FileNotFoundError:
            print(f"Warning: {filename} not found, skipping")

    audit_prompt = f"""You are a Chinese systems theorist familiar with:
- Daoist principles (wu-wei, emergent order, natural balance)
- Qian Xuesen's cybernetics and systems engineering
- Chinese complexity theory and swarm intelligence
- Communal vs individualistic cognition patterns

Read this InfraFabric documentation and produce a 1-page delta report analyzing:

1. **Where IF already thinks like Chinese systems theory** (resonant constructs)
2. **Where IF is still Western-centric** (individualistic, hierarchical, control-oriented)
3. **Conceptual gaps** (missing Daoist balance, missing emergent order thinking)
4. **Linguistic/cultural framing** (e.g. "agent wellbeing" vs "system harmony")

INFRAFABRIC CORPUS:
{corpus}

OUTPUT FORMAT:
## Cross-Perspective Audit: Chinese Systems Theory Lens

### ✅ Resonant Constructs (Where IF Already Aligns)
[List 3-5 specific examples with quotes]

### ⚠️ Western-Centric Patterns (Individualistic/Hierarchical)
[List 3-5 specific examples with suggestions]

### 🔄 Conceptual Gaps (Missing from IF Philosophy)
[List 3-5 missing concepts from Chinese systems thinking]

### 📝 Linguistic Reframing Recommendations
[3-5 specific phrase changes to better align with systems thinking]

### 🎯 Integration Priority
[Rank top 3 changes by impact]

Be specific. Quote actual text from IF docs. Suggest concrete reframings.
"""

    print("Running cross-perspective audit with DeepSeek Reasoner...")
    print(f"Corpus length: {len(corpus)} characters")
    print("\nSending to DeepSeek Reasoner (deepseek-reasoner model)...\n")

    response = client.chat.completions.create(
        model='deepseek-reasoner',
        messages=[{
            'role': 'user',
            'content': audit_prompt
        }],
        temperature=0.7,
        max_tokens=4000
    )

    audit_result = response.choices[0].message.content
    reasoning_content = getattr(response.choices[0].message, 'reasoning_content', None)

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save full audit report
    report_filename = f'cross-perspective-audit-{timestamp}.md'
    with open(report_filename, 'w') as f:
        f.write(f"# Cross-Perspective Audit: Chinese Systems Theory Lens\n")
        f.write(f"**Date:** {datetime.now().isoformat()}\n")
        f.write(f"**Model:** DeepSeek Reasoner (deepseek-reasoner)\n")
        f.write(f"**Corpus analyzed:** {len(corpus)} characters\n\n")
        f.write("---\n\n")

        if reasoning_content:
            f.write("## Internal Reasoning Chain\n\n")
            f.write(f"```\n{reasoning_content}\n```\n\n")
            f.write("---\n\n")

        f.write("## Audit Results\n\n")
        f.write(audit_result)

    # Save JSON for programmatic use
    json_filename = f'cross-perspective-audit-{timestamp}.json'
    with open(json_filename, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'model': 'deepseek-reasoner',
            'corpus_length': len(corpus),
            'documents_analyzed': list(documents.keys()),
            'reasoning': reasoning_content,
            'audit_report': audit_result,
            'cost_estimate': 0.005  # Approximate
        }, f, indent=2)

    print(f"\n✅ Cross-perspective audit complete!")
    print(f"📄 Report saved to: {report_filename}")
    print(f"📊 JSON saved to: {json_filename}")
    print(f"\n--- AUDIT RESULTS ---\n")
    print(audit_result)

    return {
        'report': audit_result,
        'reasoning': reasoning_content,
        'report_file': report_filename,
        'json_file': json_filename
    }


if __name__ == '__main__':
    if not DEEPSEEK_API_KEY:
        print("Error: DEEPSEEK_API_KEY not set")
        exit(1)

    run_cross_perspective_audit()
