#!/usr/bin/env python3
"""
Single Contact Verification Test
Debug the verification process with just 1 contact
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("="*80)
print("SINGLE CONTACT VERIFICATION TEST")
print("="*80)
print()
print("This will verify exactly 1 contact to test the process.")
print("Expected API usage: ~11 queries")
print()

# Import the main verification module
import auto_verify_contacts

# Check if API credentials are set
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')

if not GOOGLE_API_KEY or GOOGLE_API_KEY == 'YOUR_API_KEY_HERE':
    print("❌ ERROR: GOOGLE_API_KEY not set")
    print()
    print("Please run:")
    print('export GOOGLE_API_KEY="AIzaSyBxcqXfSRavUnN7KKF-ywWb_sXbDGHb3AY"')
    print('export GOOGLE_CSE_ID="011079723395396642122:0xx-5mjdafi"')
    print()
    sys.exit(1)

if not GOOGLE_CSE_ID or GOOGLE_CSE_ID == 'YOUR_CSE_ID_HERE':
    print("❌ ERROR: GOOGLE_CSE_ID not set")
    print()
    print("Please run:")
    print('export GOOGLE_CSE_ID="011079723395396642122:0xx-5mjdafi"')
    print()
    sys.exit(1)

print(f"✅ API Key: {GOOGLE_API_KEY[:20]}...")
print(f"✅ CSE ID: {GOOGLE_CSE_ID}")
print()

# Get input/output files
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--in', dest='input', default='outreach-targets-hyper-personalized.csv')
parser.add_argument('--out', dest='output', default='verified-single-test.csv')
parser.add_argument('--audit-dir', dest='audit_dir', default='./verification-audit-logs')
args = parser.parse_args()

print(f"Input: {args.input}")
print(f"Output: {args.output}")
print()

# Confirm
response = input("Ready to verify 1 contact? (y/N): ")
if response.lower() != 'y':
    print("Cancelled.")
    sys.exit(0)

print()
print("="*80)
print("Starting verification...")
print("="*80)
print()

# Run verification on just 1 contact
auto_verify_contacts.process_csv(
    args.input,
    args.output,
    args.audit_dir,
    max_contacts=1
)

print()
print("="*80)
print("✅ VERIFICATION COMPLETE")
print("="*80)
print()
print(f"Results saved to: {args.output}")
print()
print("Next steps:")
print("1. Check the output CSV for verification results")
print("2. Review the audit log in: {}/".format(args.audit_dir))
print("3. If everything looks good, run with --max 9 for full daily batch")
print()
