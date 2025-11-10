#!/usr/bin/env python3
"""
IF.mission.arxiv - Automated Endorser Outreach
Generate personalized emails for arXiv endorsement + collaboration requests.

Email components:
1. Praise their specific work (cite paper)
2. Explain IF relevance (why their research aligns)
3. Request arXiv endorsement
4. Invite collaboration on integration (not "approval")
"""

import os
import json
from datetime import datetime
from typing import Dict, List

def llm_haiku(prompt: str) -> str:
    """Call Anthropic Haiku for email generation"""
    if not os.getenv("ANTHROPIC_API_KEY"):
        return "[STUB] Set ANTHROPIC_API_KEY to generate real emails"

    try:
        import anthropic
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1500,
            temperature=0.3,  # Slightly creative for natural language
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.content[0].text
    except Exception as e:
        return f"[ERROR] {e}"

def generate_endorsement_email(endorser: Dict, priority_flag: str) -> Dict:
    """
    Generate personalized endorsement request email using Haiku.

    Framing strategy:
    - "Approval" → "collaboration" / "perspective" / "input"
    - Not asking permission to cite (it's published)
    - Inviting them to co-shape the integration
    """

    # Extract key details
    name = endorser['name']
    papers = endorser.get('papers', [])[:3]  # Top 3 papers
    keywords = endorser.get('keywords', [])
    relevance = endorser.get('relevance_score', 0)
    interest_prob = endorser.get('interest_probability', 0)

    # Build context for Haiku
    paper_list = "\n".join([f"- {p}" for p in papers])
    keyword_list = ", ".join(keywords[:5])

    prompt = f"""You are drafting a professional email to request arXiv endorsement and invite research collaboration.

CONTEXT:
Researcher: {name}
Recent Papers:
{paper_list}

Research Areas: {keyword_list}
IF Relevance Score: {relevance:.1f}/10
Interest Probability: {interest_prob}%

ABOUT INFRAFABRIC (IF):
InfraFabric is a multi-agent coordination infrastructure with focus on:
- Trustless agent orchestration (IF.guard Guardian Council)
- Citation provenance + anti-hallucination (IF.citation, IF.witness)
- Token cost optimization (IF.optimise: 50% cost reduction validated)
- Safety verification (IF.armour.yologuard: 111% GitHub-parity recall)
- Transparent metrics (IF.TTT: Traceable, Transparent, Trustworthy)

GitHub: https://github.com/dannystocker/infrafabric

TASK:
Write a concise, professional email (300-400 words) with:

1. **Subject line** (compelling, mentions their work)

2. **Opening** (2 sentences):
   - Genuine praise for their specific paper
   - Why it caught your attention for InfraFabric

3. **IF Overview** (3 sentences):
   - What InfraFabric is (multi-agent coordination infrastructure)
   - Key validation (Guardian Council 18/20 approval, 111% GitHub-parity)
   - Current status (production-ready, open-source)

4. **Relevance Connection** (2-3 sentences):
   - Specific concepts from their work that align with IF components
   - Explain the integration potential (be concrete)

5. **Dual Request** (2 paragraphs):
   a) arXiv Endorsement:
      - Need cs.AI category endorsement for paper submission
      - Mention paper focuses on [relevant topic from their work]

   b) Collaboration Invitation:
      - "We'd value your perspective on integrating concepts from your work on [topic]"
      - NOT "seeking approval" (their work is published)
      - Frame as: "invite you to co-shape how these concepts are implemented in IF"
      - Offer co-authorship on integration paper if interested

6. **Closing** (1 sentence):
   - Thank them for considering
   - Provide contact info

TONE:
- Professional but not corporate
- Specific (cite their actual work)
- Collaborative (not transactional)
- Respectful of their time (concise)

FORMAT:
Subject: [subject line]

[Email body]

---
Output ONLY the email, nothing else.
"""

    email_draft = llm_haiku(prompt)

    return {
        "recipient": name,
        "priority": priority_flag,
        "relevance": relevance,
        "interest": interest_prob,
        "subject": email_draft.split("\n")[0].replace("Subject:", "").strip(),
        "body": "\n".join(email_draft.split("\n")[2:]).strip(),
        "full_draft": email_draft,
        "generated_at": datetime.utcnow().isoformat()
    }

def batch_generate_emails(endorsers: List[Dict], top_n: int = 20) -> List[Dict]:
    """Generate emails for top N endorsers"""
    print(f"Generating personalized emails for top {top_n} endorsers...\n")

    emails = []
    for i, endorser in enumerate(endorsers[:top_n], 1):
        print(f"[{i}/{top_n}] Drafting email for: {endorser['name']}")

        priority = endorser.get('priority_flag', '❓ UNKNOWN')
        email = generate_endorsement_email(endorser, priority)
        emails.append(email)

        print(f"   Subject: {email['subject'][:60]}...")
        print()

        # Rate limiting (Haiku: 10 requests/sec, be conservative)
        import time
        time.sleep(0.5)

    return emails

def save_email_batch(emails: List[Dict], output_path: str):
    """Save generated emails as JSON for review"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(emails, f, indent=2, ensure_ascii=False)

def generate_email_review_report(emails: List[Dict], output_path: str):
    """Generate human-readable email review document"""
    lines = []
    lines.append("# InfraFabric Endorser Outreach - Email Drafts\n")
    lines.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"**Total Drafts:** {len(emails)}\n")
    lines.append("---\n")

    for i, email in enumerate(emails, 1):
        lines.append(f"## {i}. {email['recipient']} {email['priority']}\n")
        lines.append(f"**Relevance:** {email['relevance']:.1f} | **Interest:** {email['interest']:.0f}%\n")
        lines.append(f"**Subject:** {email['subject']}\n")
        lines.append("**Email Body:**")
        lines.append("```")
        lines.append(email['body'])
        lines.append("```\n")
        lines.append("**Action Items:**")
        lines.append("- [ ] Review and personalize")
        lines.append("- [ ] Add specific technical detail if needed")
        lines.append("- [ ] Send from professional email")
        lines.append("- [ ] Track response in IF.trace")
        lines.append("\n---\n")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    return output_path

def load_endorsers_from_strategy(json_path: str) -> List[Dict]:
    """Load endorsers from analyze_endorser_interest.py output"""
    # Note: This expects the JSON export, not the strategy report
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    import sys
    import glob

    # Find most recent endorser JSON
    json_files = sorted(glob.glob("arxiv_endorsers.*.json"), reverse=True)
    if not json_files:
        print("Error: No arxiv_endorsers.*.json found.")
        print("Run: python3 find_arxiv_endorsers.py")
        sys.exit(1)

    latest = json_files[0]
    print(f"Loading endorsers from: {latest}\n")

    endorsers = load_endorsers_from_strategy(latest)

    # Generate emails for top 20
    emails = batch_generate_emails(endorsers, top_n=20)

    # Save outputs
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    json_path = f"IF_ENDORSER_EMAILS.{timestamp}.json"
    report_path = f"IF_ENDORSER_EMAILS.{timestamp}.md"

    save_email_batch(emails, json_path)
    generate_email_review_report(emails, report_path)

    print(f"✅ Email generation complete:")
    print(f"   - {json_path} (structured data)")
    print(f"   - {report_path} (review document)")
    print()
    print("📋 NEXT STEPS:")
    print("1. Review emails in report document")
    print("2. Personalize with specific technical details")
    print("3. Send from professional email address")
    print("4. Track responses in IF.trace (response_rate metric)")
    print("5. Follow up after 7 days if no response")
    print()
    print("💡 PRO TIP:")
    print("   Start with 🔥 ANTHROPIC and 🎮 EPIC_GAMES candidates first")
    print("   These have highest employment opportunity potential")
    print()
