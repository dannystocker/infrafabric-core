#!/usr/bin/env python3
"""
Example: IF Alias Style

Demonstrates the recommended import pattern: `import infrafabric as IF`

This gives developers the best of both worlds:
- Type "IF" (short, practical)
- Brand awareness (InfraFabric in docs/imports)

Usage:
    python if_alias_example.py
"""

import sys
sys.path.insert(0, '/home/setup/infrafabric')

import infrafabric as IF


def main():
    print("="*60)
    print("INFRAFABRIC - IF ALIAS STYLE EXAMPLE")
    print("="*60)
    print(f"\nPackage: {IF.__brand__}")
    print(f"Shorthand: {IF.__shorthand__}")
    print(f"Version: {IF.__version__}\n")

    # Example 1: Using IF.guardians
    print("="*60)
    print("EXAMPLE 1: IF.guardians.debate_proposal()")
    print("="*60 + "\n")

    proposal = {
        'title': 'Developer Ergonomics Test',
        'description': 'Test the IF alias import style',
        'risks': ['None - this is a test'],
        'safeguards': ['Clean API', 'Type less code']
    }

    # Notice: IF.guardians.debate_proposal() - clean and short!
    result = IF.guardians.debate_proposal(proposal, proposal_type='technical')

    print(f"\n✅ Decision: {result.decision}")
    print(f"📊 Weighted votes: {result.weighted_votes}")

    # Example 2: Using IF.coordination
    print("\n" + "="*60)
    print("EXAMPLE 2: IF.coordination.WeightedCoordinator()")
    print("="*60 + "\n")

    coordinator = IF.coordination.WeightedCoordinator()
    coordinator.add_standard_agents()

    print(f"✅ Coordinator created with {len(coordinator.agents)} agents")
    print("\nAgent profiles:")
    for agent in coordinator.agents:
        print(f"  - {agent.profile.name} (tier={agent.profile.tier})")

    # Example 3: Using IF.manifests
    print("\n" + "="*60)
    print("EXAMPLE 3: IF.manifests.create_manifest()")
    print("="*60 + "\n")

    manifest = IF.manifests.create_manifest(
        run_id="example-001",
        config={'style': 'IF alias'},
        results={'success': True}
    )

    manifest.add_philosophical_insight(
        "Typing 'IF' is practical. Reading 'InfraFabric' builds brand awareness."
    )

    print(f"✅ Manifest created: {manifest.run_id}")
    print(f"📊 Hash: {manifest.compute_hash()[:16]}...")

    # Summary
    print("\n" + "="*60)
    print("DEVELOPER ERGONOMICS SUMMARY")
    print("="*60)
    print("\n✅ Benefits of 'import infrafabric as IF':")
    print("   1. Type less: IF.guardians vs infrafabric.guardians")
    print("   2. Clear intent: IF = infrastructure framework")
    print("   3. Brand awareness: InfraFabric in documentation")
    print("   4. Pythonic: Uppercase for module aliases (convention)")
    print("\n🪂 In the IF universe, ALL lemmings get parachutes.\n")


if __name__ == '__main__':
    main()
