#!/usr/bin/env python3
"""
DeepSeek-Coder Agent for InfraFabric

Uses DeepSeek API for code-focused reasoning and substrate diversity.
DeepSeek is Chinese-developed, adds different reasoning patterns to ensemble.
"""

from openai import OpenAI
import os
from typing import Dict
import re
import time

class DeepSeekCodeAgent:
    """
    DeepSeek-Coder agent using DeepSeek API.

    Features:
    - OpenAI-compatible API
    - Code-focused reasoning
    - Chinese-developed (substrate diversity)
    - Higher rate limits than OpenRouter free tier
    - Low cost (~$0.0001 per request)
    """

    def __init__(self, rate_limit_delay=0.5):
        self.provider = 'deepseek'
        self.weight = 0.5  # Initial exploration weight
        self.requests_made = 0
        self.rate_limit_delay = rate_limit_delay  # Delay between requests (seconds)
        self.last_request_time = 0

        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not set")

        self.client = OpenAI(
            api_key=api_key,
            base_url='https://api.deepseek.com'
        )
        self.model = 'deepseek-chat'  # Or 'deepseek-coder' for code-specific

        print(f"✅ DeepSeekCodeAgent initialized ({self.provider}, {self.model}, rate_limit={rate_limit_delay}s)")

    def find_contact(self, contact: Dict) -> Dict:
        """
        Find contact information using DeepSeek-Coder reasoning.

        DeepSeek's strengths:
        - Technical/code-focused analysis
        - GitHub profiles
        - Developer communities
        - Open source contributions
        - Technical publications
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
   - Technical blog posts or articles
   - Open source contributions
   - Conference talks or presentations
   - Academic publications (Google Scholar, arXiv)
   - Professional networking sites (LinkedIn)
   - Company directory listings
   - Developer communities (Stack Overflow, HackerNews, etc.)

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
                'agent': 'DeepSeekCodeAgent',
                'success': True,
                'confidence': confidence,
                'reasoning': reasoning,
                'provider': self.provider,
                'model': self.model,
                'requests_made': self.requests_made
            }

        except Exception as e:
            return {
                'agent': 'DeepSeekCodeAgent',
                'success': False,
                'confidence': 0,
                'error': str(e),
                'provider': self.provider
            }

    def extract_confidence(self, response: str) -> float:
        """Extract confidence score from DeepSeek response."""
        # Look for "CONFIDENCE: XX" pattern
        match = re.search(r'CONFIDENCE:\\s*(\\d+)', response, re.IGNORECASE)
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
        """Extract reasoning from DeepSeek response."""
        # Look for "REASONING:" pattern
        match = re.search(r'REASONING:\\s*(.+)', response, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()

        # If no pattern, return full response
        return response


# Test function
def test_deepseek_agent():
    """Test DeepSeek agent on sample contact."""
    print("=" * 60)
    print("DeepSeek-Coder Agent Test")
    print("=" * 60)
    print()

    try:
        agent = DeepSeekCodeAgent()
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\\nPlease set DEEPSEEK_API_KEY environment variable:")
        print('export DEEPSEEK_API_KEY="sk-..."')
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

    print("Querying DeepSeek-Coder...")
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
    test_deepseek_agent()
