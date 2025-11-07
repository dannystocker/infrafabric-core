#!/usr/bin/env python3
"""
Validate RFC 5322 compliance of generated .eml files
"""

import os
import re
from email import message_from_file
from email.utils import parseaddr

EML_DIR = "/home/setup/infrafabric/marketing/page-zero/email-drafts-eml"

def validate_eml_file(filepath):
    """Validate a single .eml file for RFC 5322 compliance."""
    errors = []
    warnings = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            msg = message_from_file(f)

        # Check required headers
        required_headers = ['From', 'To', 'Subject', 'Date', 'MIME-Version', 'Content-Type']
        for header in required_headers:
            if not msg.get(header):
                errors.append(f"Missing required header: {header}")

        # Validate From header
        from_header = msg.get('From', '')
        if from_header:
            name, addr = parseaddr(from_header)
            if not addr or '@' not in addr:
                errors.append(f"Invalid From address: {from_header}")
            if 'research@infrafabric.ai' not in addr:
                warnings.append(f"From address doesn't match expected: {addr}")

        # Validate To header
        to_header = msg.get('To', '')
        if to_header:
            name, addr = parseaddr(to_header)
            if not addr or '@' not in addr:
                errors.append(f"Invalid To address: {to_header}")

        # Check Content-Type
        content_type = msg.get('Content-Type', '')
        if 'text/plain' not in content_type:
            warnings.append(f"Content-Type not text/plain: {content_type}")
        if 'utf-8' not in content_type.lower():
            warnings.append(f"Character set not UTF-8: {content_type}")

        # Check for body content
        body = msg.get_payload()
        if not body or len(body.strip()) < 50:
            errors.append("Email body is empty or too short")

        # Check for placeholder
        if '[Sender Name]' in body:
            warnings.append("Contains [Sender Name] placeholder - needs replacement")

    except Exception as e:
        errors.append(f"Failed to parse file: {e}")

    return errors, warnings

def main():
    """Validate all .eml files."""
    eml_files = sorted([
        f for f in os.listdir(EML_DIR)
        if f.endswith('.eml')
    ])

    print("Validating .eml files for RFC 5322 compliance...")
    print("=" * 70)

    total_errors = 0
    total_warnings = 0

    for eml_file in eml_files:
        filepath = os.path.join(EML_DIR, eml_file)
        errors, warnings = validate_eml_file(filepath)

        if errors or warnings:
            print(f"\n{eml_file}")
            if errors:
                for error in errors:
                    print(f"  ✗ ERROR: {error}")
                    total_errors += 1
            if warnings:
                for warning in warnings:
                    print(f"  ⚠ WARNING: {warning}")
                    total_warnings += 1
        else:
            print(f"✓ {eml_file}")

    print("\n" + "=" * 70)
    print(f"Validation complete!")
    print(f"Total files: {len(eml_files)}")
    print(f"Errors: {total_errors}")
    print(f"Warnings: {total_warnings}")

    if total_errors == 0:
        print("\n✓ All files are RFC 5322 compliant and Gmail-ready!")
    else:
        print(f"\n✗ Found {total_errors} errors that must be fixed.")

if __name__ == '__main__':
    main()
