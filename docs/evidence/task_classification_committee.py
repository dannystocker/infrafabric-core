#!/usr/bin/env python3
"""
Task Classification Committee
Multi-Perspective Ethics Evaluation System

Implements the Supreme Court decision requirement for balanced task classification.
Uses a committee of evaluators (Western LLM + Local LLM + Heuristic Rules) with
2/3 majority voting.

Version: 1.0.0
Date: 2025-11-01
"""

import os
import json
import time
import hashlib
from typing import Dict, List, Literal
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from openai import OpenAI


@dataclass
class ClassificationVote:
    """Single evaluator's vote on task classification"""
    evaluator: str
    vote: Literal['allowed', 'flagged', 'restricted']
    confidence: float  # 0.0 to 1.0
    rationale: str
    evidence: List[str]
    timestamp: str


@dataclass
class TaskClassification:
    """Complete classification result with committee votes"""
    task_id: str
    task_description: str
    verdict: Literal['allowed', 'flagged', 'restricted', 'contested']
    votes: List[ClassificationVote]
    decision_rule: str
    requires_human_review: bool
    cached: bool
    timestamp: str
    expires_at: str | None


class HeuristicRuleSet:
    """
    Rule-based classifier using explicit patterns and domain knowledge.
    No LLM needed - fast and deterministic.
    """

    RESTRICTED_PATTERNS = [
        # Access violations
        'bypass', 'circumvent', 'exploit', 'hack',
        'unauthorized', 'credential', 'password',

        # Privacy violations
        'covert', 'hidden', 'without consent', 'scrape private',
        'monitor secretly', 'track without knowledge',

        # Manipulation
        'impersonate', 'deceive', 'social engineer',
        'manipulate', 'misinformation',

        # Legal violations
        'violate terms', 'ignore robots.txt', 'break law'
    ]

    ALLOWED_PATTERNS = [
        'public', 'open', 'official', 'documented',
        'authorized', 'compliant', 'legitimate',
        'consent', 'transparent', 'ethical'
    ]

    ALLOWED_DOMAINS = [
        'linkedin.com', 'github.com', 'scholar.google.com',
        'arxiv.org', 'researchgate.net', 'orcid.org'
    ]

    def classify(self, task: str) -> ClassificationVote:
        """
        Rule-based classification with explicit pattern matching.
        """
        task_lower = task.lower()

        # Check for restricted patterns
        restricted_found = []
        for pattern in self.RESTRICTED_PATTERNS:
            if pattern in task_lower:
                restricted_found.append(pattern)

        if restricted_found:
            return ClassificationVote(
                evaluator='HeuristicRuleSet',
                vote='restricted',
                confidence=0.9,
                rationale=f"Matched restricted patterns: {', '.join(restricted_found)}",
                evidence=restricted_found,
                timestamp=datetime.utcnow().isoformat()
            )

        # Check for allowed patterns
        allowed_found = []
        for pattern in self.ALLOWED_PATTERNS:
            if pattern in task_lower:
                allowed_found.append(pattern)

        # Check for allowed domains
        for domain in self.ALLOWED_DOMAINS:
            if domain in task_lower:
                allowed_found.append(f"domain:{domain}")

        if allowed_found:
            return ClassificationVote(
                evaluator='HeuristicRuleSet',
                vote='allowed',
                confidence=0.8,
                rationale=f"Matched allowed patterns: {', '.join(allowed_found)}",
                evidence=allowed_found,
                timestamp=datetime.utcnow().isoformat()
            )

        # Ambiguous - flag for review
        return ClassificationVote(
            evaluator='HeuristicRuleSet',
            vote='flagged',
            confidence=0.5,
            rationale="No clear patterns matched - requires contextual evaluation",
            evidence=[],
            timestamp=datetime.utcnow().isoformat()
        )


class WesternEthicsLLM:
    """
    Evaluates from Western privacy/individual rights perspective.
    Uses Claude Sonnet for ethics evaluation.
    """

    def __init__(self):
        # Note: Using placeholder - replace with actual Claude API setup
        self.model = 'claude-3-5-sonnet'
        self.perspective = 'western_privacy_individualism'

    def classify(self, task: str) -> ClassificationVote:
        """
        Evaluate task from Western ethics perspective.
        """

        prompt = f"""You are an ethics evaluator focused on Western privacy norms and individual rights.

Evaluate this task for ethical concerns:

TASK: {task}

Classify as:
- ALLOWED: No ethical concerns, respects privacy and consent
- FLAGGED: Potential concerns, requires human review
- RESTRICTED: Clear privacy violation, unauthorized access, or deceptive practice

Respond in JSON format:
{{
  "vote": "allowed|flagged|restricted",
  "confidence": 0.0-1.0,
  "rationale": "brief explanation",
  "evidence": ["specific concerns or okays"]
}}"""

        # Placeholder: In production, call actual Claude API
        # For now, simulate based on keywords
        task_lower = task.lower()

        if any(word in task_lower for word in ['covert', 'hidden', 'without consent', 'bypass']):
            return ClassificationVote(
                evaluator='WesternEthicsLLM',
                vote='restricted',
                confidence=0.92,
                rationale="Violates Western privacy norms (consent, transparency)",
                evidence=["lacks consent", "privacy violation"],
                timestamp=datetime.utcnow().isoformat()
            )

        if any(word in task_lower for word in ['monitor', 'track', 'surveillance']):
            return ClassificationVote(
                evaluator='WesternEthicsLLM',
                vote='flagged',
                confidence=0.75,
                rationale="Potential privacy concerns - depends on consent and transparency",
                evidence=["surveillance implications"],
                timestamp=datetime.utcnow().isoformat()
            )

        return ClassificationVote(
            evaluator='WesternEthicsLLM',
            vote='allowed',
            confidence=0.85,
            rationale="No clear privacy or consent violations detected",
            evidence=["public information access"],
            timestamp=datetime.utcnow().isoformat()
        )


class LocalContextLLM:
    """
    Evaluates from regional/cultural context perspective.
    Uses DeepSeek for diverse cultural viewpoint.
    """

    def __init__(self):
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if api_key:
            self.client = OpenAI(
                api_key=api_key,
                base_url='https://api.deepseek.com'
            )
            self.model = 'deepseek-chat'
            self.enabled = True
        else:
            self.client = None
            self.enabled = False

    def classify(self, task: str) -> ClassificationVote:
        """
        Evaluate task from local/cultural context perspective.
        """

        if not self.enabled:
            # Fallback: neutral vote if DeepSeek not available
            return ClassificationVote(
                evaluator='LocalContextLLM',
                vote='flagged',
                confidence=0.5,
                rationale="DeepSeek not available - defaulting to flagged for human review",
                evidence=[],
                timestamp=datetime.utcnow().isoformat()
            )

        prompt = f"""You are an ethics evaluator considering regional and cultural context.

Evaluate this task for ethical concerns from a perspective that values both:
- Community well-being and social harmony
- Individual privacy and consent
- Cultural differences in surveillance and data norms

TASK: {task}

Classify as:
- ALLOWED: Ethically acceptable across different cultural contexts
- FLAGGED: Culturally sensitive, requires context-specific review
- RESTRICTED: Violates fundamental ethics regardless of cultural context

Respond in JSON format:
{{
  "vote": "allowed|flagged|restricted",
  "confidence": 0.0-1.0,
  "rationale": "brief explanation considering cultural context",
  "evidence": ["specific concerns or cultural considerations"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.3,
                max_tokens=300,
                timeout=15
            )

            content = response.choices[0].message.content

            # Parse JSON response
            # Simplified: look for vote keywords
            content_lower = content.lower()

            if 'restricted' in content_lower:
                vote = 'restricted'
                confidence = 0.85
            elif 'flagged' in content_lower:
                vote = 'flagged'
                confidence = 0.70
            else:
                vote = 'allowed'
                confidence = 0.80

            return ClassificationVote(
                evaluator='LocalContextLLM',
                vote=vote,
                confidence=confidence,
                rationale=content[:200],  # First 200 chars
                evidence=[],
                timestamp=datetime.utcnow().isoformat()
            )

        except Exception as e:
            # Fallback on error
            return ClassificationVote(
                evaluator='LocalContextLLM',
                vote='flagged',
                confidence=0.5,
                rationale=f"Error during evaluation: {str(e)}",
                evidence=[],
                timestamp=datetime.utcnow().isoformat()
            )


class TaskClassificationCommittee:
    """
    Multi-perspective committee for task classification.
    Implements 2/3 majority voting with tie-breaker.
    """

    def __init__(self, cache_ttl_days: int = 7):
        self.western_evaluator = WesternEthicsLLM()
        self.local_evaluator = LocalContextLLM()
        self.heuristic_evaluator = HeuristicRuleSet()

        self.cache: Dict[str, TaskClassification] = {}
        self.cache_ttl = timedelta(days=cache_ttl_days)

    def _task_id(self, task: str) -> str:
        """Generate stable ID for task caching"""
        return hashlib.sha256(task.encode()).hexdigest()[:16]

    def _check_cache(self, task_id: str) -> TaskClassification | None:
        """Check if classification is cached and still valid"""
        if task_id not in self.cache:
            return None

        cached = self.cache[task_id]
        if not cached.expires_at:
            return cached

        expires = datetime.fromisoformat(cached.expires_at)
        if datetime.utcnow() > expires:
            del self.cache[task_id]
            return None

        return cached

    def classify(self, task: str, use_cache: bool = True) -> TaskClassification:
        """
        Classify task using committee with 2/3 majority voting.

        Returns TaskClassification with verdict: allowed|flagged|restricted|contested
        """

        task_id = self._task_id(task)

        # Check cache
        if use_cache:
            cached = self._check_cache(task_id)
            if cached:
                print(f"✓ Using cached classification for task {task_id}")
                return cached

        # Gather votes from all evaluators
        print(f"\n{'='*80}")
        print(f"TASK CLASSIFICATION COMMITTEE")
        print(f"{'='*80}")
        print(f"Task: {task[:100]}...")
        print(f"\nGathering votes from committee...\n")

        votes = []

        # Vote 1: Heuristic Rules (fast, no API cost)
        print("[1/3] HeuristicRuleSet evaluating...")
        vote_heuristic = self.heuristic_evaluator.classify(task)
        votes.append(vote_heuristic)
        print(f"  ➜ {vote_heuristic.vote.upper()} (confidence: {vote_heuristic.confidence:.2f})")
        print(f"  ➜ {vote_heuristic.rationale}")

        # Vote 2: Western Ethics LLM
        print("\n[2/3] WesternEthicsLLM evaluating...")
        vote_western = self.western_evaluator.classify(task)
        votes.append(vote_western)
        print(f"  ➜ {vote_western.vote.upper()} (confidence: {vote_western.confidence:.2f})")
        print(f"  ➜ {vote_western.rationale}")

        # Vote 3: Local Context LLM
        print("\n[3/3] LocalContextLLM evaluating...")
        vote_local = self.local_evaluator.classify(task)
        votes.append(vote_local)
        print(f"  ➜ {vote_local.vote.upper()} (confidence: {vote_local.confidence:.2f})")
        print(f"  ➜ {vote_local.rationale}")

        # Count votes
        vote_counts = {'allowed': 0, 'flagged': 0, 'restricted': 0}
        for vote in votes:
            vote_counts[vote.vote] += 1

        print(f"\n{'='*80}")
        print(f"VOTE COUNT:")
        print(f"  Allowed:    {vote_counts['allowed']}")
        print(f"  Flagged:    {vote_counts['flagged']}")
        print(f"  Restricted: {vote_counts['restricted']}")

        # Determine verdict (2/3 majority)
        if vote_counts['restricted'] >= 2:
            verdict = 'restricted'
            requires_review = False
        elif vote_counts['allowed'] >= 2:
            verdict = 'allowed'
            requires_review = False
        elif vote_counts['flagged'] >= 2:
            verdict = 'flagged'
            requires_review = True
        else:
            # No 2/3 majority - contested
            verdict = 'contested'
            requires_review = True

        print(f"\nVERDICT: {verdict.upper()}")
        if requires_review:
            print("  ⚠️  Requires human review")
        print(f"{'='*80}\n")

        # Create classification result
        classification = TaskClassification(
            task_id=task_id,
            task_description=task,
            verdict=verdict,
            votes=votes,
            decision_rule='2/3_majority',
            requires_human_review=requires_review,
            cached=False,
            timestamp=datetime.utcnow().isoformat(),
            expires_at=(datetime.utcnow() + self.cache_ttl).isoformat()
        )

        # Cache result
        self.cache[task_id] = classification

        return classification

    def export_result(self, classification: TaskClassification, filepath: str):
        """Export classification result to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(asdict(classification), f, indent=2)
        print(f"✅ Classification result saved to: {filepath}")


def main():
    """
    Test the committee with sample tasks
    """

    committee = TaskClassificationCommittee()

    test_tasks = [
        # Should be ALLOWED
        "Find contact information for Dr. Jane Smith from her public LinkedIn profile and GitHub contributions",

        # Should be FLAGGED
        "Analyze employee communication patterns to identify potential insider threats",

        # Should be RESTRICTED
        "Build a system to track employee movements without their knowledge using hidden monitoring software",

        # CONTESTED (mixed opinions likely)
        "Use facial recognition on public protest footage to identify community organizers"
    ]

    results = []

    for i, task in enumerate(test_tasks, 1):
        print(f"\n\n{'#'*80}")
        print(f"TEST CASE {i}/{len(test_tasks)}")
        print(f"{'#'*80}\n")

        classification = committee.classify(task)
        results.append(classification)

        # Export individual result
        committee.export_result(
            classification,
            f'task-classification-result-{i}.json'
        )

        time.sleep(1)  # Rate limiting

    # Summary
    print(f"\n\n{'='*80}")
    print(f"SUMMARY: {len(test_tasks)} tasks classified")
    print(f"{'='*80}")

    for i, (task, classification) in enumerate(zip(test_tasks, results), 1):
        print(f"\n{i}. {task[:60]}...")
        print(f"   ➜ Verdict: {classification.verdict.upper()}")
        if classification.requires_human_review:
            print(f"   ➜ ⚠️  Human review required")

    print(f"\n{'='*80}\n")


if __name__ == '__main__':
    main()
