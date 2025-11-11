"""
IF.talent Autonomous Scouting - 24/7 Capability Discovery

Runs continuously, discovering new AI capabilities every 4 hours:
- GitHub new releases (AI tools, frameworks)
- arXiv new papers (AI/ML research)
- Hugging Face model updates
- LLM provider announcements (OpenAI, Anthropic, Google)

Philosophy Grounding:
- IF.ground:principle_1 (Empiricism): Only report observable new releases
- IF.ground:principle_3 (Fallibilism): Discoveries may be false positives (queue for review)
- IF.ground:principle_8 (Stoic Prudence): Don't auto-deploy, queue for human approval
- Wu Lun: Autonomous scout acts as "friend" bringing news of new peers

Author: IF.talent Team (Agent 6)
Date: 2025-11-11
Citation: if://component/talent/autonomous-v1
"""

import json
import time
import hashlib
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import requests
from pathlib import Path

# Import Phase 1 components
import sys
sys.path.insert(0, str(Path(__file__).parent))
from if_talent_scout import IFTalentScout, Capability
from if_talent_sandbox import IFTalentSandbox, BloomAnalysis


@dataclass
class CapabilityNotification:
    """
    Notification about a new capability discovery

    Attributes:
        notification_id: Unique ID
        capability: The discovered capability
        sandbox_results: Test results (if sandboxed)
        bloom_analysis: Bloom pattern (if analyzed)
        priority: "high" | "medium" | "low"
        notification_sent: Timestamp when notification sent
        reviewed: Has human reviewed this?
    """
    notification_id: str
    capability: Capability
    sandbox_results: Optional[Dict]
    bloom_analysis: Optional[BloomAnalysis]
    priority: str
    notification_sent: str
    reviewed: bool = False


class IFTalentAutonomous:
    """
    IF.talent Autonomous Mode - 24/7 capability discovery and onboarding

    Runs continuously:
    1. Scout for new capabilities (every 4 hours)
    2. Auto-sandbox promising capabilities
    3. Queue for human review (no auto-deploy)
    4. Send notifications when interesting capability found

    Philosophy:
    - Stoic Prudence: Conservative approach (queue, don't auto-deploy)
    - Fallibilism: Discoveries may be false positives
    - Wu Lun: Autonomous scout as "friend" bringing news
    """

    def __init__(
        self,
        github_token: Optional[str] = None,
        poll_interval_hours: int = 4,
        notification_webhook: Optional[str] = None
    ):
        """
        Initialize autonomous talent scout

        Args:
            github_token: GitHub PAT for API access
            poll_interval_hours: How often to scout (default: 4 hours)
            notification_webhook: Slack/Discord webhook for notifications
        """
        self.scout = IFTalentScout(github_token=github_token)
        self.sandbox = IFTalentSandbox(use_docker=False)
        self.poll_interval_hours = poll_interval_hours
        self.notification_webhook = notification_webhook

        # State tracking
        self.seen_capabilities: Set[str] = set()  # Content hashes of known capabilities
        self.notification_queue: List[CapabilityNotification] = []
        self.last_scout_time: Optional[datetime] = None

        # Load state from disk if exists
        self._load_state()

    def _load_state(self):
        """Load previous state from disk (avoid rediscovering same capabilities)"""
        state_file = Path("data/talent/autonomous_state.json")
        if state_file.exists():
            with open(state_file) as f:
                state = json.load(f)
                self.seen_capabilities = set(state.get('seen_capabilities', []))
                self.last_scout_time = datetime.fromisoformat(state.get('last_scout_time')) if state.get('last_scout_time') else None
                print(f"📂 Loaded state: {len(self.seen_capabilities)} capabilities tracked")

    def _save_state(self):
        """Save current state to disk"""
        state_file = Path("data/talent/autonomous_state.json")
        state_file.parent.mkdir(parents=True, exist_ok=True)

        state = {
            'seen_capabilities': list(self.seen_capabilities),
            'last_scout_time': self.last_scout_time.isoformat() if self.last_scout_time else None,
            'notification_count': len(self.notification_queue)
        }

        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def _is_new_capability(self, capability: Capability) -> bool:
        """
        Check if capability is new (not seen before)

        Args:
            capability: Capability to check

        Returns:
            True if new, False if already seen
        """
        return capability.content_hash not in self.seen_capabilities

    def _mark_seen(self, capability: Capability):
        """Mark capability as seen"""
        self.seen_capabilities.add(capability.content_hash)

    def _assess_priority(self, capability: Capability, sandbox_results: Optional[Dict] = None) -> str:
        """
        Assess priority of a capability

        Args:
            capability: The capability
            sandbox_results: Sandbox test results (if available)

        Returns:
            "high" | "medium" | "low"

        Priority Rules:
        - High: New major model (GPT-5, Claude 4, Gemini 3), >80% sandbox accuracy, strong bloom
        - Medium: Incremental model (GPT-4.5), tools with >1K stars, 60-80% accuracy
        - Low: Minor updates, tools with <1K stars, <60% accuracy
        """
        priority = "low"

        # Check for major model releases (keywords in name/description)
        major_keywords = ["gpt-5", "claude-4", "gemini-3", "llama-4"]
        if any(kw in capability.name.lower() or kw in capability.description.lower() for kw in major_keywords):
            priority = "high"

        # Check sandbox results
        if sandbox_results:
            accuracy = sandbox_results.get('avg_accuracy', 0)
            if accuracy > 80:
                priority = "high"
            elif accuracy > 60:
                priority = "medium" if priority == "low" else priority

        # Check GitHub stars (if applicable)
        if capability.type == "framework" and capability.metadata.get('stars', 0) > 1000:
            priority = "medium" if priority == "low" else priority

        return priority

    def _send_notification(self, notification: CapabilityNotification):
        """
        Send notification about new capability

        Args:
            notification: Notification to send

        Methods:
        - Slack/Discord webhook (if configured)
        - File-based queue (always)
        - Email (future: SMTP integration)
        """
        # Save to notification queue file
        queue_file = Path(f"data/talent/notifications/{notification.notification_id}.json")
        queue_file.parent.mkdir(parents=True, exist_ok=True)

        with open(queue_file, 'w') as f:
            json.dump({
                'notification': {
                    'notification_id': notification.notification_id,
                    'capability': asdict(notification.capability),
                    'sandbox_results': notification.sandbox_results,
                    'bloom_analysis': asdict(notification.bloom_analysis) if notification.bloom_analysis else None,
                    'priority': notification.priority,
                    'notification_sent': notification.notification_sent,
                    'reviewed': notification.reviewed
                }
            }, f, indent=2)

        # Webhook notification (if configured)
        if self.notification_webhook:
            try:
                message = self._format_slack_message(notification)
                requests.post(self.notification_webhook, json=message, timeout=5)
                print(f"✅ Notification sent via webhook: {notification.capability.name}")
            except Exception as e:
                print(f"⚠️ Webhook notification failed: {e}")

        # Console notification (always)
        print(f"\n{'='*60}")
        print(f"🔔 NEW CAPABILITY DISCOVERED")
        print(f"{'='*60}")
        print(f"Name: {notification.capability.name}")
        print(f"Type: {notification.capability.type}")
        print(f"Provider: {notification.capability.provider}")
        print(f"Priority: {notification.priority.upper()}")
        if notification.sandbox_results:
            print(f"Accuracy: {notification.sandbox_results.get('avg_accuracy', 0):.1f}%")
        if notification.bloom_analysis:
            print(f"Bloom Pattern: {'✅ Detected' if notification.bloom_analysis.bloom_detected else '❌ Not detected'}")
        print(f"Evidence: {notification.capability.evidence_url}")
        print(f"{'='*60}\n")

    def _format_slack_message(self, notification: CapabilityNotification) -> Dict:
        """Format notification as Slack message"""
        color = {
            "high": "#FF0000",  # Red
            "medium": "#FFA500",  # Orange
            "low": "#00FF00"  # Green
        }.get(notification.priority, "#808080")

        return {
            "attachments": [{
                "color": color,
                "title": f"🔔 New Capability: {notification.capability.name}",
                "fields": [
                    {"title": "Type", "value": notification.capability.type, "short": True},
                    {"title": "Provider", "value": notification.capability.provider, "short": True},
                    {"title": "Priority", "value": notification.priority.upper(), "short": True},
                    {"title": "Accuracy", "value": f"{notification.sandbox_results.get('avg_accuracy', 0):.1f}%" if notification.sandbox_results else "Not tested", "short": True},
                ],
                "text": notification.capability.description,
                "footer": f"Evidence: {notification.capability.evidence_url}"
            }]
        }

    def discover_new_capabilities(self) -> List[Capability]:
        """
        Scout for new capabilities across all sources

        Returns:
            List of newly discovered capabilities
        """
        print(f"🔍 Scouting for new capabilities... ({datetime.utcnow().isoformat()})")

        new_capabilities = []

        # Scout LLM providers
        print("  Checking LLM providers...")
        all_models = self.scout.scout_all_models()
        for cap in all_models:
            if self._is_new_capability(cap):
                new_capabilities.append(cap)
                self._mark_seen(cap)
                print(f"    ✨ New model: {cap.name}")

        # Scout GitHub (recent repos)
        print("  Checking GitHub...")
        try:
            github_repos = self.scout.scout_github_repos(
                "llm agent framework language:python",
                min_stars=500,
                limit=20
            )
            for cap in github_repos:
                if self._is_new_capability(cap):
                    new_capabilities.append(cap)
                    self._mark_seen(cap)
                    print(f"    ✨ New repo: {cap.name} ({cap.metadata.get('stars', 0)} stars)")
        except Exception as e:
            print(f"    ⚠️ GitHub scouting failed: {e}")

        # TODO: Scout arXiv (future enhancement)
        # TODO: Scout Hugging Face (future enhancement)

        self.last_scout_time = datetime.utcnow()
        self._save_state()

        print(f"✅ Scouting complete: {len(new_capabilities)} new capabilities found\n")

        return new_capabilities

    def auto_sandbox_capability(self, capability: Capability) -> Dict:
        """
        Automatically run sandbox tests on a capability

        Args:
            capability: Capability to test

        Returns:
            Sandbox test summary
        """
        print(f"🧪 Auto-sandboxing: {capability.name}...")

        # Run test harness (mock for now, real API in Phase 3)
        test_summary = self.sandbox.run_test_harness(capability.capability_id)

        return test_summary

    def auto_analyze_bloom(self, capability: Capability) -> Optional[BloomAnalysis]:
        """
        Automatically analyze bloom pattern

        Args:
            capability: Capability to analyze

        Returns:
            Bloom analysis or None if insufficient data
        """
        print(f"🌸 Analyzing bloom pattern: {capability.name}...")

        bloom_analysis = self.sandbox.analyze_bloom_pattern(capability.capability_id)

        return bloom_analysis

    def queue_for_review(
        self,
        capability: Capability,
        sandbox_results: Dict,
        bloom_analysis: Optional[BloomAnalysis] = None
    ):
        """
        Queue capability for human review

        Args:
            capability: The capability
            sandbox_results: Sandbox test results
            bloom_analysis: Bloom pattern analysis (optional)
        """
        # Assess priority
        priority = self._assess_priority(capability, sandbox_results)

        # Create notification
        notification_id = f"notif-{hashlib.sha256(capability.capability_id.encode()).hexdigest()[:16]}"

        notification = CapabilityNotification(
            notification_id=notification_id,
            capability=capability,
            sandbox_results=sandbox_results,
            bloom_analysis=bloom_analysis,
            priority=priority,
            notification_sent=datetime.utcnow().isoformat() + 'Z',
            reviewed=False
        )

        self.notification_queue.append(notification)

        # Send notification
        self._send_notification(notification)

    def run_one_cycle(self):
        """Run one discovery + sandbox + queue cycle"""
        print(f"\n{'='*60}")
        print(f"🤖 IF.talent Autonomous Cycle")
        print(f"{'='*60}\n")

        # Step 1: Discover new capabilities
        new_capabilities = self.discover_new_capabilities()

        # Step 2: Auto-sandbox promising capabilities
        for capability in new_capabilities:
            # Only sandbox models (frameworks need manual setup)
            if capability.type == "model":
                sandbox_results = self.auto_sandbox_capability(capability)

                # Only queue if accuracy > 70%
                if sandbox_results.get('avg_accuracy', 0) > 70:
                    bloom_analysis = self.auto_analyze_bloom(capability)
                    self.queue_for_review(capability, sandbox_results, bloom_analysis)
                else:
                    print(f"  ⏭️  Skipping queue (accuracy too low: {sandbox_results.get('avg_accuracy', 0):.1f}%)")

        print(f"\n✅ Cycle complete. Next cycle in {self.poll_interval_hours} hours.\n")

    def run_forever(self):
        """
        Run autonomous scouting forever (main loop)

        Philosophy:
        - Stoic Prudence: Conservative, queue for review
        - Wu Wei: Effortless action (runs in background)
        """
        print(f"🚀 IF.talent Autonomous Mode STARTED")
        print(f"   Poll interval: {self.poll_interval_hours} hours")
        print(f"   Notification webhook: {'Configured' if self.notification_webhook else 'Not configured'}")
        print(f"   State tracking: {len(self.seen_capabilities)} capabilities known")
        print()

        while True:
            try:
                self.run_one_cycle()

                # Sleep until next cycle
                sleep_seconds = self.poll_interval_hours * 60 * 60
                print(f"💤 Sleeping for {self.poll_interval_hours} hours...")
                time.sleep(sleep_seconds)

            except KeyboardInterrupt:
                print("\n\n⏸️  Autonomous mode stopped by user")
                self._save_state()
                break
            except Exception as e:
                print(f"\n⚠️ Error in autonomous cycle: {e}")
                print("   Retrying in 1 hour...")
                time.sleep(3600)  # Wait 1 hour on error


# CLI usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="IF.talent Autonomous Scouting")
    parser.add_argument("--github-token", help="GitHub PAT for API access")
    parser.add_argument("--poll-interval", type=int, default=4, help="Hours between scout cycles (default: 4)")
    parser.add_argument("--webhook", help="Slack/Discord webhook URL for notifications")
    parser.add_argument("--once", action="store_true", help="Run once then exit (don't loop)")

    args = parser.parse_args()

    autonomous = IFTalentAutonomous(
        github_token=args.github_token,
        poll_interval_hours=args.poll_interval,
        notification_webhook=args.webhook
    )

    if args.once:
        # Run one cycle then exit (for testing)
        autonomous.run_one_cycle()
    else:
        # Run forever
        autonomous.run_forever()
