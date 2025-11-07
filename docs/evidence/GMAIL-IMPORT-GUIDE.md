# Gmail Import Guide for InfraFabric Email Drafts

**Generated:** 2025-10-30
**Total Drafts:** 20 RFC 5322 compliant .eml files
**Location:** `/home/setup/infrafabric/marketing/page-zero/email-drafts-eml/`

---

## Email Verification Status

### Verified Emails (From CSV - 1)
| Contact | Email | Organization |
|---------|-------|--------------|
| Mark Papermaster | mark.papermaster@amd.com | AMD |

### Constructed Emails (19)
| Contact | Email | Organization |
|---------|-------|--------------|
| Emil Michael | emil.michael@diu.mil | Department of Defense |
| Amin Vahdat | amin.vahdat@cloud.google.com | Google Cloud |
| Jeremy O'Brien | jeremy.o'brien@psiquantum.com | PsiQuantum |
| Swami Sivasubramanian | swami.sivasubramanian@aws.amazon.com | AWS |
| Michael Kagan | michael.kagan@nvidia.com | NVIDIA |
| Mustafa Suleyman | mustafa.suleyman@microsoft.com | Microsoft |
| Doreen Bogdan-Martin | doreen.bogdan-martin@itu.int | ITU |
| Mark Russinovich | mark.russinovich@azure.microsoft.com | Microsoft Azure |
| Manuela Veloso | manuela.veloso@jpmorgan.com | JPMorgan Chase |
| Shaun Maguire | shaun.maguire@sequoiacap.com | Sequoia Capital |
| Jonathan Ross | jonathan.ross@groq.com | Groq |
| Travis Humble | travis.humble@quantum.ornl.gov | Oak Ridge National Laboratory |
| Sachin Katti | sachin.katti@intel.com | Intel |
| Gil Herrera | gil.herrera@nsa.gov | NSA |
| Daniel Marcu | daniel.marcu@goldmansachs.com | Goldman Sachs |
| Matt Ocko | matt.ocko@dcvc.com | DCVC |
| Bill Dally | bill.dally@nvidia.com | NVIDIA |
| Niccolo de Masi | niccolo.de masi@ionq.com | IonQ |
| Lan Guan | lan.guan@accenture.com | Accenture |

**Note:** Constructed emails follow the pattern `firstname.lastname@domain` extracted from company websites. You should **verify these addresses** before sending, especially for high-priority contacts.

---

## Method 1: Manual Import via Gmail Web Interface

### Desktop Browser (Recommended)

1. **Access Gmail Drafts:**
   - Open Gmail in your browser
   - Navigate to the "Drafts" folder in the left sidebar

2. **Import Individual .eml Files:**
   - Open your file manager to `/home/setup/infrafabric/marketing/page-zero/email-drafts-eml/`
   - Drag and drop an .eml file directly into your Gmail browser window
   - Gmail will automatically parse the .eml file and create a draft

3. **Verify the Draft:**
   - Check that the recipient, subject, and body are correctly populated
   - Review the email address (especially constructed ones marked above)
   - Edit the draft to replace `[Sender Name]` with your actual name

4. **Repeat for All 20 Files:**
   - Process each .eml file one at a time
   - Keep track of which drafts have been imported

### Alternative: Upload via Gmail Settings

1. **Enable IMAP in Gmail:**
   - Go to Settings → See all settings → Forwarding and POP/IMAP
   - Enable IMAP access

2. **Use Desktop Email Client:**
   - Configure an email client (Thunderbird, Apple Mail, Outlook)
   - Copy .eml files to the Drafts folder
   - Wait for IMAP sync to Gmail

---

## Method 2: Gmail API (Programmatic Import)

For developers who want to automate the import process:

### Prerequisites
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Python Script for Batch Import

```python
#!/usr/bin/env python3
"""
Import .eml files to Gmail Drafts via Gmail API
"""

import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.compose']
EML_DIR = '/home/setup/infrafabric/marketing/page-zero/email-drafts-eml/'

def get_gmail_service():
    """Authenticate and return Gmail API service."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def import_eml_to_draft(service, eml_path):
    """Import a single .eml file as a Gmail draft."""
    with open(eml_path, 'rb') as f:
        eml_content = f.read()

    # Encode the .eml content
    raw_message = base64.urlsafe_b64encode(eml_content).decode('utf-8')

    # Create draft
    draft = {
        'message': {
            'raw': raw_message
        }
    }

    try:
        draft = service.users().drafts().create(
            userId='me',
            body=draft
        ).execute()
        print(f"✓ Imported: {os.path.basename(eml_path)}")
        return draft['id']
    except Exception as e:
        print(f"✗ Failed: {os.path.basename(eml_path)} - {e}")
        return None

def main():
    """Import all .eml files to Gmail drafts."""
    service = get_gmail_service()

    eml_files = sorted([
        f for f in os.listdir(EML_DIR)
        if f.endswith('.eml')
    ])

    print(f"Importing {len(eml_files)} .eml files to Gmail drafts...")
    print("=" * 60)

    for eml_file in eml_files:
        eml_path = os.path.join(EML_DIR, eml_file)
        import_eml_to_draft(service, eml_path)

    print("=" * 60)
    print("Import complete!")

if __name__ == '__main__':
    main()
```

### Setup Steps for Gmail API

1. **Create Google Cloud Project:**
   - Go to https://console.cloud.google.com/
   - Create a new project (e.g., "InfraFabric Email Import")

2. **Enable Gmail API:**
   - Navigate to "APIs & Services" → "Library"
   - Search for "Gmail API" and enable it

3. **Create OAuth 2.0 Credentials:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Select "Desktop app"
   - Download the JSON file and save as `credentials.json`

4. **Run the Script:**
   ```bash
   python3 gmail_import_script.py
   ```
   - First run will open a browser for authentication
   - Subsequent runs will use the saved token

---

## Method 3: Email Client Import (Thunderbird)

1. **Install Thunderbird:**
   ```bash
   sudo apt install thunderbird  # Linux
   # Or download from https://www.thunderbird.net/
   ```

2. **Configure Gmail Account:**
   - Add your Gmail account to Thunderbird
   - Enable IMAP sync

3. **Import .eml Files:**
   - Go to Drafts folder in Thunderbird
   - Drag and drop all .eml files into the Drafts folder
   - Files will automatically sync to Gmail

---

## Pre-Send Checklist

Before sending any email, **verify:**

- [ ] **Email Address:** Double-check constructed emails (especially those marked "CONSTRUCTED" above)
- [ ] **Sender Name:** Replace `[Sender Name]` placeholder with your actual name
- [ ] **Personalization:** Ensure all personalization elements are accurate
- [ ] **Subject Line:** Confirm subject line is appropriate
- [ ] **Links:** Check any URLs in the email body
- [ ] **Signature:** Add your professional signature if needed
- [ ] **Testing:** Send one test email to yourself first

---

## Email Validation Recommendations

### High-Priority Verification (Tier A Contacts)

These contacts are marked as "immediate" priority and should have emails verified:

1. **Emil Michael** (DoD) - emil.michael@diu.mil
2. **Amin Vahdat** (Google Cloud) - amin.vahdat@cloud.google.com
3. **Jeremy O'Brien** (PsiQuantum) - jeremy.o'brien@psiquantum.com
4. **Mark Papermaster** (AMD) - ✓ VERIFIED
5. **Swami Sivasubramanian** (AWS) - swami.sivasubramanian@aws.amazon.com

### Verification Methods

1. **LinkedIn Direct:** Message them on LinkedIn to request email
2. **Company Directory:** Check organization's employee directory
3. **Email Verification Tools:** Use tools like Hunter.io, RocketReach, or ZoomInfo
4. **Cold Email Test:** Send a brief test message asking to confirm best email
5. **Executive Assistant:** Contact their EA/admin for correct email

---

## Batch Import Tips

### For 20 Emails

1. **Phased Import:**
   - Week 1: Import 5 high-priority drafts
   - Week 2: Import next 5 drafts
   - Continue until all are imported

2. **Label Organization:**
   - Create Gmail label: "InfraFabric - Page Zero Outreach"
   - Tag all imported drafts with this label
   - Create sub-labels: "Tier A", "Tier B" by priority

3. **Scheduling:**
   - Use Gmail's "Schedule Send" feature
   - Stagger sends across different days/times
   - Avoid sending all 20 simultaneously

4. **Tracking:**
   - Enable "Request read receipt" for important contacts
   - Use email tracking tools (Mailtrack, Streak, etc.)
   - Keep a spreadsheet of sent/responded/no response

---

## Troubleshooting

### Issue: .eml File Won't Import

**Solution:**
- Check file encoding (should be UTF-8)
- Verify RFC 5322 compliance
- Try opening in a text editor to inspect headers

### Issue: Missing Headers in Gmail

**Solution:**
- Ensure MIME-Version and Content-Type headers are present
- Check that Date header uses RFC 2822 format
- Verify From/To/Subject headers are properly formatted

### Issue: Special Characters Display Incorrectly

**Solution:**
- Confirm UTF-8 encoding in .eml files
- Check Content-Transfer-Encoding is set to 8bit
- Re-generate .eml files if needed

---

## Support Resources

- **Gmail Help:** https://support.google.com/mail/answer/6579
- **Gmail API Documentation:** https://developers.google.com/gmail/api
- **RFC 5322 Specification:** https://tools.ietf.org/html/rfc5322
- **Email Testing Tool:** https://www.mail-tester.com/

---

## Next Steps

1. **Verify Email Addresses:** Prioritize Tier A contacts (immediate priority)
2. **Test Import:** Import 1-2 .eml files to verify the process
3. **Customize Drafts:** Replace placeholders and add your signature
4. **Schedule Sends:** Use Gmail's schedule feature for optimal timing
5. **Track Responses:** Set up a system to monitor replies and follow-ups

**Good luck with your outreach campaign!**
