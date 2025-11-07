#!/usr/bin/env python3
"""
Qwen3-Coder Agent for InfraFabric

Uses OpenRouter free tier for zero-cost substrate diversity.
Adds Chinese-developed model to multi-agent ecosystem.
"""

from openai import OpenAI
import os
from typing import Dict
import re
import time

class QwenCodeAgent:
    """
    Qwen3-Coder agent using OpenRouter free tier.

    Features:
    - OpenAI-compatible API
    - Free tier (rate-limited)
    - Code-focused reasoning
    - Chinese-developed (substrate diversity)
    """

    def __init__(self, provider='openrouter', rate_limit_delay=4.0):
        self.provider = provider
        self.weight = 0.5  # Initial exploration weight
        self.requests_made = 0
        self.rate_limit_delay = rate_limit_delay  # Delay between requests (seconds)
        self.last_request_time = 0

        if provider == 'openrouter':
            api_key = os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY not set")

            self.client = OpenAI(
                api_key=api_key,
                base_url='https://openrouter.ai/api/v1'
            )
            self.model = 'qwen/qwen3-coder:free'

        print(f"✅ QwenCodeAgent initialized ({self.provider}, {self.model}, rate_limit={rate_limit_delay}s)")

    def find_contact(self, contact: Dict) -> Dict:
        """
        Find contact information using Qwen3-Coder reasoning.

        Qwen's strengths:
        - GitHub profiles
        - Technical communities
        - Open source contributions
        - Academic publications (arXiv, Google Scholar)
        """

        # Construct search prompt
        name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}"
        org = contact.get('organization', 'Unknown')
        role = contact.get('role_title', 'Unknown')
        context = contact.get('why_relevant', '')

        prompt = f"""You are a technical contact researcher specializing in finding information about professionals in technology and research.

Contact to research:
Name: {name}
Organization: {org}
Role: {role}
Context: {context}

Your task:
1. Assess likelihood of finding this person's contact information
2. Consider these signals:
   - GitHub profile existence
   - Academic publications (Google Scholar, arXiv)
   - Technical blog posts or articles
   - Conference talks or presentations
   - Open source contributions
   - Professional networking sites (LinkedIn)
   - Company directory listings

3. Provide a confidence score (0-100) indicating how likely you could find accurate contact info
4. Explain your reasoning

Format:
CONFIDENCE: [0-100]
REASONING: [your analysis]

Focus on public, ethical information sources only."""

        # Rate limiting: ensure minimum delay between requests
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a technical contact research specialist. Provide confidence scores based on the likelihood of finding public, professional contact information."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower for more deterministic
                max_tokens=500,
                timeout=30  # 30 second timeout
            )

            self.requests_made += 1
            self.last_request_time = time.time()

            # Parse response
            content = response.choices[0].message.content
            confidence = self.extract_confidence(content)
            reasoning = self.extract_reasoning(content)

            return {
                'agent': 'QwenCodeAgent',
                'success': True,
                'confidence': confidence,
                'reasoning': reasoning,
                'provider': self.provider,
                'model': self.model,
                'requests_made': self.requests_made
            }

        except Exception as e:
            return {
                'agent': 'QwenCodeAgent',
                'success': False,
                'confidence': 0,
                'error': str(e),
                'provider': self.provider
            }

    def extract_confidence(self, response: str) -> float:
        """Extract confidence score from Qwen response."""
        # Look for "CONFIDENCE: XX" pattern
        match = re.search(r'CONFIDENCE:\s*(\d+)', response, re.IGNORECASE)
        if match:
            return float(match.group(1))

        # Fallback: heuristic analysis
        response_lower = response.lower()
        if any(word in response_lower for word in ['very likely', 'highly confident', 'definitely']):
            return 85.0
        elif any(word in response_lower for word in ['likely', 'probably', 'good chance']):
            return 70.0
        elif any(word in response_lower for word in ['possibly', 'might', 'could be']):
            return 50.0
        elif any(word in response_lower for word in ['unlikely', 'difficult', 'challenging']):
            return 30.0
        else:
            return 60.0  # Default moderate

    def extract_reasoning(self, response: str) -> str:
        """Extract reasoning from Qwen response."""
        # Look for "REASONING:" pattern
        match = re.search(r'REASONING:\s*(.+)', response, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()

        # If no pattern, return full response
        return response


# Test function
def test_qwen_agent():
    """Test Qwen agent on sample contact."""
    print("=" * 60)
    print("Qwen3-Coder Agent Test")
    print("=" * 60)
    print()

    try:
        agent = QwenCodeAgent(provider='openrouter')
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nPlease set OPENROUTER_API_KEY environment variable:")
        print('export OPENROUTER_API_KEY="sk-or-v1-..."')
        return

    test_contact = {
        'first_name': 'Amin',
        'last_name': 'Vahdat',
        'organization': 'Google',
        'role_title': 'VP Engineering',
        'why_relevant': 'Quantum computing infrastructure lead',
        'sector': 'quantum'
    }

    print(f"Testing contact: {test_contact['first_name']} {test_contact['last_name']}")
    print(f"Organization: {test_contact['organization']}")
    print(f"Role: {test_contact['role_title']}")
    print()

    print("Querying Qwen3-Coder via OpenRouter...")
    result = agent.find_contact(test_contact)
    print()

    if result['success']:
        print(f"✅ Success!")
        print(f"📊 Confidence: {result.get('confidence', 0)}%")
        print(f"🤖 Model: {result['model']}")
        print(f"📈 Requests made: {result['requests_made']}")
        print()
        print(f"💭 Reasoning:")
        print(result.get('reasoning', 'N/A'))
    else:
        print(f"❌ Failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")

    print()
    print("=" * 60)


if __name__ == "__main__":
    test_qwen_agent()
