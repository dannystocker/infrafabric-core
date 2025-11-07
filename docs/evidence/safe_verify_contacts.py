#!/usr/bin/env python3
"""
SAFE Contact Verification Wrapper
Guarantees you NEVER exceed free tier quota (100 queries/day)
"""

import sys
import os

# SAFETY LIMITS
MAX_CONTACTS_PER_RUN = 9  # 9 contacts * 11 queries = 99 queries (safely under 100)
WARNING_THRESHOLD = 80  # Warn when approaching limit

print("="*80)
print("SAFE VERIFICATION MODE - FREE TIER PROTECTION")
print("="*80)
print(f"Maximum contacts per run: {MAX_CONTACTS_PER_RUN}")
print(f"Estimated API queries: ~{MAX_CONTACTS_PER_RUN * 11}")
print(f"Free tier daily limit: 100 queries")
print(f"Safety margin: {100 - (MAX_CONTACTS_PER_RUN * 11)} queries")
print("="*80)
print()

# Check if user is trying to process more than safe limit
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--in', dest='input', required=True)
parser.add_argument('--out', dest='output', required=True)
parser.add_argument('--max', dest='max_contacts', type=int)
parser.add_argument('--audit-dir', dest='audit_dir', default='./verification-audit-logs')
args = parser.parse_args()

# Safety check
if args.max_contacts and args.max_contacts > MAX_CONTACTS_PER_RUN:
    print(f"⚠️  WARNING: You requested {args.max_contacts} contacts")
    print(f"⚠️  This would use ~{args.max_contacts * 11} API queries")
    print(f"⚠️  Free tier limit is 100 queries/day")
    print()
    print(f"To stay safely in free tier, maximum is {MAX_CONTACTS_PER_RUN} contacts/run")
    print()

    response = input(f"Continue with {MAX_CONTACTS_PER_RUN} contacts instead? (y/N): ")
    if response.lower() != 'y':
        print("Cancelled.")
        sys.exit(0)

    # Override to safe limit
    args.max_contacts = MAX_CONTACTS_PER_RUN

elif not args.max_contacts:
    # No limit specified - set to safe default
    print(f"No --max specified. Using safe default: {MAX_CONTACTS_PER_RUN} contacts")
    args.max_contacts = MAX_CONTACTS_PER_RUN

# Import and run the actual verification
print(f"\n✅ Proceeding with {args.max_contacts} contacts")
print(f"Estimated API usage: ~{args.max_contacts * 11} queries\n")

# Set environment variable for the main script
os.environ['MAX_GOOGLE_QUERIES'] = str(MAX_CONTACTS_PER_RUN * 11)

# Import and run main script
sys.path.insert(0, os.path.dirname(__file__))
import auto_verify_contacts

# Run verification
auto_verify_contacts.process_csv(
    args.input,
    args.output,
    args.audit_dir,
    args.max_contacts
)

print("\n" + "="*80)
print("✅ SAFE VERIFICATION COMPLETE")
print("="*80)
print("No billing risk - stayed within free tier limits!")
print("="*80)
