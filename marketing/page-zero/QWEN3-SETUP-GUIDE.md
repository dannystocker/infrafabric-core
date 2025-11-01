# Qwen3-Coder Setup Guide for InfraFabric
## Step-by-Step Integration

**Date:** 2025-10-31
**Goal:** Add Qwen3-Coder to IF with free API access
**Status:** Multiple free options available

---

## Free API Options Summary

Based on research, here are the **best free options** for InfraFabric:

| Provider | Free Quota | Ease of Use | Recommendation |
|----------|-----------|-------------|----------------|
| **OpenRouter** | Rate-limited free tier | ⭐⭐⭐⭐⭐ Easy | **BEST FOR IF** |
| **QwenBridge** | 2000 req/day | ⭐⭐⭐⭐⭐ Easy | **BEST FOR IF** |
| **Alibaba DashScope** | 1M tokens/month | ⭐⭐⭐ Moderate | Good for CN region |
| **Puter.js** | Unlimited (fair use) | ⭐⭐⭐⭐ Easy | Good for experiments |

---

## Option 1: OpenRouter (RECOMMENDED) ⭐⭐⭐⭐⭐

### Why OpenRouter?
- ✅ **Free tier** with `qwen/qwen3-coder:free`
- ✅ **No credit card** required
- ✅ **OpenAI-compatible** API
- ✅ **Multiple Qwen models** available
- ✅ **Easy setup** (5 minutes)

### Step-by-Step Setup

#### 1. Create OpenRouter Account (2 min)
```bash
# Visit OpenRouter website
https://openrouter.ai/

# Click "Sign Up"
# Use GitHub or Google auth (no credit card needed)
```

#### 2. Get API Key (1 min)
```bash
# After login, go to:
https://openrouter.ai/settings/keys

# Click "Create Key"
# Name: "InfraFabric Qwen Agent"
# Copy the key (starts with sk-or-...)
```

#### 3. Set Environment Variable (1 min)
```bash
# Linux/macOS
export OPENROUTER_API_KEY='sk-or-...'

# Add to ~/.bashrc for persistence
echo 'export OPENROUTER_API_KEY="sk-or-..."' >> ~/.bashrc
source ~/.bashrc

# Windows (WSL)
# Same as Linux above
```

#### 4. Test Connection (1 min)
```python
#!/usr/bin/env python3
"""Test OpenRouter Qwen3 connection"""

from openai import OpenAI

client = OpenAI(
    api_key='sk-or-...',  # Your OpenRouter key
    base_url='https://openrouter.ai/api/v1'
)

response = client.chat.completions.create(
    model='qwen/qwen3-coder:free',
    messages=[
        {'role': 'user', 'content': 'Hello, can you help me find contact info?'}
    ]
)

print(response.choices[0].message.content)
```

```bash
# Run test
python3 test_qwen_openrouter.py

# Expected output: Qwen responds successfully
```

### Available Models

```python
# Free tier models
OPENROUTER_FREE_MODELS = [
    'qwen/qwen3-coder:free',      # Best for coding
    'qwen/qwen3-32b:free',        # Good balance
    'qwen/qwen3-235b-a22b:free'   # Largest free
]

# Paid models (if needed later)
OPENROUTER_PAID_MODELS = [
    'qwen/qwen3-coder-480b-a35b',  # Best performance
    'qwen/qwen3-30b-a3b'           # Smaller, faster
]
```

### Rate Limits
- **Free tier:** Rate limited during peak hours
- **Priority:** Lower than paid users
- **Throttling:** Possible delays (5-10s)
- **Best for:** Development, testing, low-volume production

---

## Option 2: QwenBridge (ALTERNATIVE) ⭐⭐⭐⭐⭐

### Why QwenBridge?
- ✅ **2000 requests/day** (explicit quota)
- ✅ **OpenAI-compatible**
- ✅ **Fast setup**
- ✅ **Claude Code integration**

### Step-by-Step Setup

#### 1. Visit QwenBridge
```bash
https://qwenbridge.dev/
```

#### 2. Sign Up (Free)
- Create account
- No credit card required
- Get API key instantly

#### 3. Configure
```python
from openai import OpenAI

client = OpenAI(
    api_key='YOUR_QWENBRIDGE_KEY',
    base_url='https://qwenbridge.dev/v1'
)

# Use same as OpenAI
response = client.chat.completions.create(
    model='qwen3-coder-480b-a35b',
    messages=[...]
)
```

### Daily Quota Tracking
```python
class QwenBridgeClient:
    def __init__(self):
        self.daily_quota = 2000
        self.requests_used = 0
        self.reset_time = None  # Midnight UTC

    def check_quota(self):
        # Check if quota reset
        if datetime.now() > self.reset_time:
            self.requests_used = 0
            self.reset_time = datetime.now() + timedelta(days=1)

        if self.requests_used >= self.daily_quota:
            raise QuotaExceededError(f"Used {self.requests_used}/2000 today")

        return self.daily_quota - self.requests_used
```

---

## Option 3: Alibaba DashScope (For Chinese Region) ⭐⭐⭐

### Why DashScope?
- ✅ **1 million tokens/month free**
- ✅ **Official Alibaba API**
- ✅ **OpenAI-compatible**
- ⚠️  **Qwen3-Coder NOT in free tier**
- ⚠️  **Better for CN users**

### Step-by-Step Setup

#### 1. Create Alibaba Cloud Account
```bash
https://www.alibabacloud.com/
# Sign up (international or China edition)
```

#### 2. Navigate to Model Studio
```bash
https://dashscope.console.aliyun.com/
# Or international: dashscope-intl.aliyuncs.com
```

#### 3. Generate API Key
```bash
# In DashScope console:
# Settings → API Keys → Create New Key
# Copy the key
```

#### 4. Set Environment Variable
```bash
export DASHSCOPE_API_KEY='sk-...'
```

#### 5. Choose Endpoint
```python
# International (Singapore)
DASHSCOPE_INTL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

# China (Beijing)
DASHSCOPE_CN = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# Use in code
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=DASHSCOPE_INTL  # or DASHSCOPE_CN
)

# Free models (Qwen3-Coder NOT included)
response = client.chat.completions.create(
    model="qwen-plus",  # Free tier model
    messages=[...]
)
```

### Important Notes
- ⚠️  **Qwen3-Coder models NOT in free tier**
- ✅ **Qwen-Plus, Qwen-Turbo ARE free** (1M tokens/month)
- ⚠️  **Best for Chinese language tasks**
- ✅ **Good for non-coding Qwen models**

---

## InfraFabric Integration: Complete Code

### qwen_code_agent.py

```python
#!/usr/bin/env python3
"""
Qwen3-Coder Agent for InfraFabric

Uses OpenRouter free tier for zero-cost substrate diversity.
"""

from openai import OpenAI
import os
from typing import Dict, List
from datetime import datetime

class QwenCodeAgent:
    """
    Qwen3-Coder agent using OpenRouter free tier.

    Features:
    - OpenAI-compatible API
    - Free tier (rate-limited)
    - Code-focused reasoning
    - Chinese-developed (substrate diversity)
    """

    def __init__(self, provider='openrouter'):
        self.provider = provider
        self.weight = 0.5  # Initial exploration weight
        self.requests_made = 0

        if provider == 'openrouter':
            api_key = os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY not set")

            self.client = OpenAI(
                api_key=api_key,
                base_url='https://openrouter.ai/api/v1'
            )
            self.model = 'qwen/qwen3-coder:free'
            self.has_quota_limit = False  # Rate limited, not quota

        elif provider == 'qwenbridge':
            api_key = os.getenv('QWENBRIDGE_API_KEY')
            if not api_key:
                raise ValueError("QWENBRIDGE_API_KEY not set")

            self.client = OpenAI(
                api_key=api_key,
                base_url='https://qwenbridge.dev/v1'
            )
            self.model = 'qwen3-coder-480b-a35b'
            self.has_quota_limit = True
            self.daily_quota = 2000
            self.quota_used_today = 0

    def find_contact(self, contact: Dict) -> Dict:
        """
        Find contact information using Qwen3-Coder reasoning.

        Qwen's strengths:
        - GitHub profiles
        - Technical communities
        - Open source contributions
        - Academic publications (arXiv, Google Scholar)
        """

        # Check quota (if applicable)
        if self.has_quota_limit and self.quota_used_today >= self.daily_quota:
            return {
                'agent': 'QwenCodeAgent',
                'success': False,
                'confidence': 0,
                'error': f'Daily quota exceeded ({self.quota_used_today}/{self.daily_quota})',
                'provider': self.provider
            }

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
            if self.has_quota_limit:
                self.quota_used_today += 1

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
        import re
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
        import re
        match = re.search(r'REASONING:\s*(.+)', response, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()

        # If no pattern, return full response
        return response


# Test function
def test_qwen_agent():
    """Test Qwen agent on sample contact."""
    agent = QwenCodeAgent(provider='openrouter')

    test_contact = {
        'first_name': 'Amin',
        'last_name': 'Vahdat',
        'organization': 'Google',
        'role_title': 'VP Engineering',
        'why_relevant': 'Quantum computing infrastructure lead',
        'sector': 'quantum'
    }

    print("Testing QwenCodeAgent...")
    print(f"Contact: {test_contact['first_name']} {test_contact['last_name']}")
    print(f"Provider: {agent.provider}")
    print(f"Model: {agent.model}\n")

    result = agent.find_contact(test_contact)

    print(f"Success: {result['success']}")
    print(f"Confidence: {result.get('confidence', 0)}%")
    print(f"Reasoning:\n{result.get('reasoning', 'N/A')}")

    if result.get('error'):
        print(f"Error: {result['error']}")


if __name__ == "__main__":
    test_qwen_agent()
```

---

## Integration with weighted_multi_agent_finder.py

### Add Qwen to Agent Pool

```python
# At top of file
from qwen_code_agent import QwenCodeAgent

# Add to AGENT_PROFILES
AGENT_PROFILES['QwenCodeAgent'] = {
    'weight': 0.5,  # Start with exploration weight
    'effort': 'medium',
    'provider': 'openrouter',  # or 'qwenbridge'
    'cost_per_query': 0.0,
    'max_queries': 5,
    'timeout': 30,
    'strengths': ['github', 'open_source', 'technical', 'academic'],
    'best_for': ['developers', 'researchers', 'technical_executives']
}

# In MultiAgentWeightedCoordinator.__init__
def __init__(self):
    # ... existing agents
    try:
        self.qwen_agent = QwenCodeAgent(provider='openrouter')
        print("✅ QwenCodeAgent initialized (OpenRouter free tier)")
    except ValueError as e:
        print(f"⚠️  QwenCodeAgent not available: {e}")
        self.qwen_agent = None

# In find_contact method
def find_contact(self, contact):
    results = []

    # ... existing agents

    # Add Qwen if available
    if self.qwen_agent:
        qwen_result = self.qwen_agent.find_contact(contact)
        if qwen_result['success']:
            results.append(qwen_result)

    # Weighted consensus (existing logic)
    return self.weighted_consensus(results)
```

---

## Quick Start: 5-Minute Setup

```bash
# 1. Get OpenRouter API key (2 min)
# Visit: https://openrouter.ai/settings/keys
# Create key, copy it

# 2. Set environment variable (30 sec)
export OPENROUTER_API_KEY='sk-or-...'

# 3. Create qwen_code_agent.py (1 min)
# Copy code from above

# 4. Test connection (30 sec)
python3 qwen_code_agent.py

# 5. Add to IF (1 min)
# Update weighted_multi_agent_finder.py as shown above

# Done! Qwen is now part of your multi-agent pool
```

---

## Troubleshooting

### Error: "OPENROUTER_API_KEY not set"
```bash
# Solution: Export the key
export OPENROUTER_API_KEY='sk-or-...'

# Make permanent
echo 'export OPENROUTER_API_KEY="sk-or-..."' >> ~/.bashrc
source ~/.bashrc
```

### Error: "Rate limit exceeded"
```bash
# OpenRouter free tier is rate-limited during peak hours
# Solutions:
# 1. Wait a few minutes and retry
# 2. Use QwenBridge instead (2000 req/day quota)
# 3. Reduce concurrent requests
```

### Error: "Connection timeout"
```bash
# Increase timeout in code
response = client.chat.completions.create(
    ...,
    timeout=60  # Increase to 60 seconds
)
```

---

## Cost Comparison

| Provider | Free Tier | Rate Limits | Best For |
|----------|-----------|-------------|----------|
| **OpenRouter** | Free tier models | Peak hour throttling | Development, testing |
| **QwenBridge** | 2000 req/day | Hard quota | Low-volume production |
| **DashScope** | 1M tokens/month | No Qwen3-Coder | Other Qwen models |
| **Puter.js** | Unlimited (fair use) | Fair use policy | Experiments |

**Recommendation for IF:**
- **Start with OpenRouter** (easiest setup)
- **Switch to QwenBridge** if rate limits are an issue
- **Stay on free tier** until proven value

---

## Next Steps

1. ✅ **Choose provider** (OpenRouter recommended)
2. ✅ **Get API key** (5 min setup)
3. ✅ **Create qwen_code_agent.py** (copy code above)
4. ✅ **Test on 10 contacts** (validate integration)
5. ✅ **Add to weighted_multi_agent_finder.py** (full integration)
6. ✅ **Run batch** (measure improvement)
7. ✅ **Agent weight learner** (automatic optimization)

**Expected timeline:** 1 hour total
**Expected cost:** $0.00
**Expected improvement:** +3-6% success rate

---

**Generated:** 2025-10-31
**Status:** Ready to implement
**Recommended:** Start with OpenRouter free tier
