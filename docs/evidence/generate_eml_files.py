#!/usr/bin/env python3
"""
Generate RFC 5322 compliant .eml files from email drafts for Gmail import.
"""

import csv
import json
import os
from datetime import datetime
from email.utils import formatdate
from urllib.parse import urlparse

# Paths
BASE_DIR = "/home/setup/infrafabric/marketing/page-zero"
DRAFTS_DIR = f"{BASE_DIR}/email-drafts"
EML_DIR = f"{BASE_DIR}/email-drafts-eml"
METADATA_PATH = f"{BASE_DIR}/email-metadata.json"
CSV_PATH = f"{BASE_DIR}/outreach-targets-FINAL-RANKED.csv"

# Load metadata
with open(METADATA_PATH, 'r') as f:
    metadata = json.load(f)

# Load CSV and create contact lookup
contacts = {}
with open(CSV_PATH, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = f"{row['first_name']}_{row['last_name']}_{row['organization']}"
        contacts[key] = row

def extract_domain(url):
    """Extract domain from company website URL."""
    if not url or url.startswith('http'):
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')
    return url.replace('www.', '')

def construct_email(first_name, last_name, email_public, company_website):
    """Construct email address or use public one."""
    if email_public and email_public.strip():
        return email_public.strip(), True  # verified

    # Construct email
    domain = extract_domain(company_website)
    if domain:
        email = f"{first_name.lower()}.{last_name.lower()}@{domain}"
        return email, False  # constructed, not verified

    return None, False

def create_eml_file(email_data, contact_info, txt_content):
    """Create RFC 5322 compliant .eml file."""
    first_name = contact_info['first_name']
    last_name = contact_info['last_name']
    email_addr, verified = construct_email(
        first_name,
        last_name,
        contact_info.get('email_if_public', ''),
        contact_info.get('company_website', '')
    )

    if not email_addr:
        print(f"WARNING: Could not construct email for {first_name} {last_name}")
        return None, None, False

    # Parse the text file - remove "Subject: " line from body
    lines = txt_content.strip().split('\n')
    subject = email_data['subject_line']

    # Find where the actual email body starts (after "Subject:" line and blank line)
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith('Subject:'):
            body_start = i + 1
            # Skip any blank lines after subject
            while body_start < len(lines) and not lines[body_start].strip():
                body_start += 1
            break

    body = '\n'.join(lines[body_start:]).strip()

    # Create RFC 5322 headers
    date_header = formatdate(localtime=True)

    eml_content = f"""From: InfraFabric Research Team <research@infrafabric.ai>
To: {first_name} {last_name} <{email_addr}>
Subject: {subject}
Date: {date_header}
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit

{body}
"""

    # Generate .eml filename
    eml_filename = email_data['filename'].replace('.txt', '.eml')
    eml_path = f"{EML_DIR}/{eml_filename}"

    # Write .eml file
    with open(eml_path, 'w', encoding='utf-8') as f:
        f.write(eml_content)

    return eml_filename, email_addr, verified

# Process all emails
print("Generating .eml files...")
print("=" * 60)

updated_emails = []
email_verification_status = []

for email_entry in metadata['emails']:
    filename = email_entry['filename']
    contact_name = email_entry['contact']

    # Read the text file
    txt_path = f"{DRAFTS_DIR}/{filename}"
    with open(txt_path, 'r', encoding='utf-8') as f:
        txt_content = f.read()

    # Find matching contact in CSV
    contact_match = None
    for key, contact_info in contacts.items():
        if (contact_info['first_name'] in contact_name and
            contact_info['last_name'] in contact_name):
            contact_match = contact_info
            break

    if not contact_match:
        print(f"WARNING: No CSV match found for {contact_name}")
        continue

    # Create .eml file
    eml_filename, email_addr, verified = create_eml_file(
        email_entry,
        contact_match,
        txt_content
    )

    if eml_filename:
        # Update metadata entry
        email_entry['eml_filename'] = eml_filename
        email_entry['email_address'] = email_addr
        email_entry['email_verified'] = verified
        email_entry['gmail_import_ready'] = True

        status = "VERIFIED" if verified else "CONSTRUCTED"
        print(f"✓ {contact_match['first_name']} {contact_match['last_name']}")
        print(f"  Email: {email_addr} ({status})")
        print(f"  File: {eml_filename}")
        print()

        email_verification_status.append({
            'contact': contact_name,
            'email': email_addr,
            'verified': verified,
            'organization': contact_match['organization']
        })

    updated_emails.append(email_entry)

# Update metadata
metadata['emails'] = updated_emails
metadata['eml_generation_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

with open(METADATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2)

print("=" * 60)
print(f"Generated {len(email_verification_status)} .eml files")
print(f"Verified emails: {sum(1 for e in email_verification_status if e['verified'])}")
print(f"Constructed emails: {sum(1 for e in email_verification_status if not e['verified'])}")
print()
print("Metadata updated at:", METADATA_PATH)
print("EML files saved to:", EML_DIR)
