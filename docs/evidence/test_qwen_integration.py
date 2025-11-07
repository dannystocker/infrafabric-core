#!/usr/bin/env python3
"""
Test Qwen3-Coder Integration with InfraFabric
Tests Qwen on sample contacts and compares vs existing agents
"""

import os
import sys
import csv
from qwen_code_agent import QwenCodeAgent

# Set API key
os.environ['OPENROUTER_API_KEY'] = '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'

def test_qwen_on_contacts(num_contacts=10):
    """Test Qwen on first N contacts from CSV"""

    print("=" * 80)
    print("Qwen3-Coder Integration Test")
    print("=" * 80)
    print()

    # Initialize Qwen
    try:
        qwen = QwenCodeAgent(provider='openrouter')
    except Exception as e:
        print(f"❌ Failed to initialize Qwen: {e}")
        return

    # Load contacts
    contacts_file = 'outreach-targets-FINAL-RANKED.csv'
    if not os.path.exists(contacts_file):
        print(f"❌ Contact file not found: {contacts_file}")
        return

    with open(contacts_file) as f:
        reader = csv.DictReader(f)
        contacts = list(reader)[:num_contacts]

    print(f"Testing Qwen on {len(contacts)} contacts...")
    print()

    # Test each contact
    results = []
    for i, contact in enumerate(contacts, 1):
        print(f"\n[{i}/{len(contacts)}] {contact['first_name']} {contact['last_name']} - {contact['organization']}")

        result = qwen.find_contact(contact)

        if result['success']:
            print(f"  ✅ Confidence: {result['confidence']}%")
            print(f"  💭 {result['reasoning'][:150]}...")
        else:
            print(f"  ❌ Error: {result.get('error', 'Unknown')}")

        results.append({
            'name': f"{contact['first_name']} {contact['last_name']}",
            'org': contact['organization'],
            'confidence': result.get('confidence', 0),
            'success': result['success']
        })

    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)

    successes = sum(1 for r in results if r['success'])
    avg_confidence = sum(r['confidence'] for r in results if r['success']) / successes if successes > 0 else 0

    print(f"Successful queries: {successes}/{len(results)} ({successes/len(results)*100:.1f}%)")
    print(f"Average confidence: {avg_confidence:.1f}%")
    print(f"Total requests: {qwen.requests_made}")

    print("\nTop 5 by confidence:")
    sorted_results = sorted(results, key=lambda x: x['confidence'], reverse=True)
    for r in sorted_results[:5]:
        print(f"  {r['name']:30s} ({r['org']:20s}): {r['confidence']}%")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--num', type=int, default=10, help='Number of contacts to test')
    args = parser.parse_args()

    test_qwen_on_contacts(args.num)
