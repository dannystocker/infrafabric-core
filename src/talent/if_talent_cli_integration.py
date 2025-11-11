"""
IF.talent CLI Integration - Command-line interface for talent management

CLI commands:
- if talent scout --source github          # Manually trigger scouting
- if talent sandbox --capability <id>      # Test a capability
- if talent certify --capability-id <id>   # Guardian approval
- if talent deploy --capability-id <id>    # Deploy to IF.swarm
- if talent status                         # Show pipeline status

Integration with Session CLI (IF.witness + IF.optimise)

Author: IF.talent Team (Agent 6)
Date: 2025-11-11
Citation: if://component/talent/cli-v1
"""

import argparse
import sys
import json
from pathlib import Path

# Import IF.talent components
from if_talent_scout import IFTalentScout
from if_talent_sandbox import IFTalentSandbox
from if_talent_autonomous import IFTalentAutonomous


def cmd_scout(args):
    """Scout for new capabilities"""
    print(f"🔍 Scouting {args.source}...")

    scout = IFTalentScout(github_token=args.github_token)

    if args.source == "github":
        results = scout.scout_github_repos(
            args.query or "llm agent framework",
            min_stars=args.min_stars,
            limit=args.limit
        )
    elif args.source == "anthropic":
        results = scout.scout_anthropic_models()
    elif args.source == "openai":
        results = scout.scout_openai_models()
    elif args.source == "google":
        results = scout.scout_google_models()
    elif args.source == "all":
        results = scout.scout_all_models()
    else:
        print(f"❌ Unknown source: {args.source}")
        return 1

    print(f"\n✅ Found {len(results)} capabilities")

    for cap in results:
        print(f"\n  - {cap.name} ({cap.provider})")
        print(f"    Type: {cap.type}")
        print(f"    Evidence: {cap.evidence_url}")

    # Save discoveries
    if args.save:
        scout.save_discoveries(args.save)
        print(f"\n💾 Saved to {args.save}")

    return 0


def cmd_sandbox(args):
    """Test a capability in sandbox"""
    print(f"🧪 Sandboxing {args.capability}...")

    sandbox = IFTalentSandbox(use_docker=args.docker)

    # Run test harness
    test_summary = sandbox.run_test_harness(args.capability)

    print(f"\n📊 Results:")
    print(f"  Success Rate: {test_summary['success_rate']:.1f}%")
    print(f"  Avg Accuracy: {test_summary['avg_accuracy']:.1f}%")
    print(f"  Avg Latency: {test_summary['avg_latency_ms']:.0f}ms")
    print(f"  Total Tokens: {test_summary['total_tokens']:,}")

    # Bloom analysis
    if args.bloom:
        bloom_analysis = sandbox.analyze_bloom_pattern(args.capability)
        print(f"\n🌸 Bloom Pattern:")
        print(f"  Detected: {'✅ Yes' if bloom_analysis.bloom_detected else '❌ No'}")
        print(f"  Score: {bloom_analysis.bloom_score}/100")
        print(f"  {bloom_analysis.interpretation}")

    # Save results
    if args.save:
        with open(args.save, 'w') as f:
            json.dump({
                'test_summary': test_summary,
                'bloom_analysis': bloom_analysis.__dict__ if args.bloom else None
            }, f, indent=2)
        print(f"\n💾 Saved to {args.save}")

    return 0


def cmd_certify(args):
    """Submit capability for Guardian certification"""
    print(f"✅ Certifying {args.capability_id}...")

    if args.approve:
        # Manual approval (bypass Guardian vote)
        print(f"  ⚠️  Manual approval (bypassing Guardian vote)")
        print(f"  ✅ Capability approved")
        # TODO: Update database status to 'certified'
        return 0

    # TODO: Integrate with infrafabric.guardians.GuardianPanel
    print(f"  📋 Submitting to Guardian Panel...")
    print(f"  ⏳ Awaiting Guardian deliberation...")
    print(f"\n  (Guardian integration in Phase 3)")

    return 0


def cmd_deploy(args):
    """Deploy capability to IF.swarm"""
    print(f"🚀 Deploying {args.capability_id}...")

    # TODO: Integrate with IF.swarm router
    print(f"  📋 Adding to IF.swarm router...")
    print(f"  ⏳ Gradual rollout: 1% → 10% → 50% → 100%")
    print(f"\n  (Deployment integration in Phase 3)")

    return 0


def cmd_status(args):
    """Show talent pipeline status"""
    print("📊 IF.talent Pipeline Status\n")

    # Check autonomous scout state
    state_file = Path("data/talent/autonomous_state.json")
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
            print(f"🔍 Scout:")
            print(f"  Capabilities tracked: {len(state.get('seen_capabilities', []))}")
            print(f"  Last scout: {state.get('last_scout_time', 'Never')[:19]}")

    # Check notification queue
    notifications_dir = Path("data/talent/notifications")
    if notifications_dir.exists():
        notifications = list(notifications_dir.glob("*.json"))
        print(f"\n🔔 Notifications:")
        print(f"  Pending review: {len(notifications)}")

    # Check dashboard database
    db_path = Path("data/talent/dashboard.db")
    if db_path.exists():
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT status, COUNT(*) FROM capabilities GROUP BY status")
        status_counts = dict(cursor.fetchall())

        print(f"\n📋 Capabilities:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")

        conn.close()

    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="if talent",
        description="IF.talent - AI Talent Agency CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Scout command
    scout_parser = subparsers.add_parser("scout", help="Scout for new capabilities")
    scout_parser.add_argument("--source", default="all", choices=["github", "anthropic", "openai", "google", "all"])
    scout_parser.add_argument("--query", help="GitHub search query")
    scout_parser.add_argument("--min-stars", type=int, default=500, help="Minimum GitHub stars")
    scout_parser.add_argument("--limit", type=int, default=10, help="Max results")
    scout_parser.add_argument("--save", help="Save discoveries to file")
    scout_parser.add_argument("--github-token", help="GitHub PAT")

    # Sandbox command
    sandbox_parser = subparsers.add_parser("sandbox", help="Test capability in sandbox")
    sandbox_parser.add_argument("--capability", required=True, help="Capability ID to test")
    sandbox_parser.add_argument("--bloom", action="store_true", help="Run bloom analysis")
    sandbox_parser.add_argument("--docker", action="store_true", help="Use Docker isolation")
    sandbox_parser.add_argument("--save", help="Save results to file")

    # Certify command
    certify_parser = subparsers.add_parser("certify", help="Submit for Guardian certification")
    certify_parser.add_argument("--capability-id", required=True, help="Capability ID")
    certify_parser.add_argument("--approve", action="store_true", help="Manual approval (bypass Guardian)")

    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy to IF.swarm")
    deploy_parser.add_argument("--capability-id", required=True, help="Capability ID")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show pipeline status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Dispatch to command handlers
    if args.command == "scout":
        return cmd_scout(args)
    elif args.command == "sandbox":
        return cmd_sandbox(args)
    elif args.command == "certify":
        return cmd_certify(args)
    elif args.command == "deploy":
        return cmd_deploy(args)
    elif args.command == "status":
        return cmd_status(args)

    return 1


if __name__ == "__main__":
    sys.exit(main())
