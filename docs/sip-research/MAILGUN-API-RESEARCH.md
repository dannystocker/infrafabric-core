# Mailgun Email API Service - InfraFabric Integration Research

**Agent:** Haiku-33
**Methodology:** IF.search 8-pass
**Date:** 2025-11-14
**Status:** Complete Research Cycle

---

## Executive Summary

Mailgun is a developer-first transactional email API service (under Sinch) offering robust email delivery, inbound email routing, and advanced tracking capabilities. For InfraFabric integration, Mailgun excels as a notification service provider for system-generated emails, alert delivery, multi-tenant routing, and inbound email handling via webhook-based routes. The service provides pay-as-you-go pricing ($35/month Foundation tier for 50K emails), comprehensive event tracking via webhooks, official SDKs for Python/Go/Ruby/Node.js, and strong GDPR compliance with EU data residency options.

**Key Strengths for InfraFabric:**
- Inbound email routing to webhooks (critical for automation workflows)
- Email parsing and structured JSON delivery
- Domain-specific API keys for multi-tenant isolation
- Real-time email validation for data quality
- Flexible rate limits (negotiable after account verification)
- Template system with Handlebars for dynamic content
- Dedicated IP pools for reputation management

---

## Pass 1-2: Signal Capture - Core API Documentation

### API Authentication & Security

#### API Key Types

Mailgun provides two authentication mechanisms:

1. **Account API Keys** (Primary)
   - Full CRUD operations across all API endpoints
   - Access to all account domains and configuration
   - All sending domains managed from single key
   - Location: Account Settings → API Keys → Private API Key
   - Displayed with eye icon to reveal

2. **Domain Sending Keys** (Restricted)
   - Limited scope: only `/messages` and `/messages.mime` POST endpoints
   - Domain-specific isolation for multi-tenant scenarios
   - Suitable for third-party integrations with restricted permissions
   - Enables safe key distribution to applications

#### Authentication Method

- **Protocol:** HTTP Basic Authentication
- **Username:** `api` (literal string)
- **Password:** API Key value
- **Example Header:**
  ```
  Authorization: Basic api:YOUR_API_KEY
  ```

#### Domain Verification & Configuration

- Mailgun domains require DNS verification at registrar
- SPF, DKIM, and DMARC configuration provided by Mailgun
- TLS enforcement: Modern TLS versions required for delivery
- Automated DKIM rotation: 2048-bit keys rotated every 120 days
- Support for subdomain verification (e.g., `mail.yourdomain.com`)

---

## Core API Capabilities

### Send API - Transactional Email Delivery

#### Endpoints

1. **POST `/v3/{domain}/messages`** (Form Data)
   - Standard message composition
   - Parameter-based specification
   - Supports multiple recipients, attachments, templates
   - Maximum message size: 25MB
   - Maximum send options (o:, h:, v:, t: parameters): 16KB total

2. **POST `/v3/{domain}/messages.mime`** (MIME Format)
   - Raw MIME string submission
   - Full control over message structure
   - Useful for complex email formats
   - Library-generated MIME from mail libraries

#### Core Parameters

**Required:**
- `to` - Recipient email(s) with optional friendly name
  ```
  to: "Bob <bob@example.com>, Alice <alice@example.com>"
  ```
- `from` - Sender email address with optional display name
- `subject` - Message subject line

**Message Body:**
- `text` - Plain text body
- `html` - HTML body
- `amp-html` - AMP for Email body (Google standard compliant)

**Recipients:**
- `cc` - Carbon copy recipients
- `bcc` - Blind carbon copy recipients

**Content:**
- `attachment` - File attachments (form data)
- `inline` - Inline images/assets for HTML rendering
  ```
  inline: "cid:logo@example.com"
  ```

**Advanced Options (prefixed):**
- `o:` - Sending options (tracking, scheduling, etc.)
  - `o:tracking` - Enable open/click tracking
  - `o:tracking-clicks` - Enable click tracking
  - `o:tag` - Email tags for categorization
  - `o:require-tls` - Enforce TLS delivery
  - `o:skip-verification` - Skip recipient validation

- `h:` - Custom MIME headers
  - `h:Reply-To` - Reply-To address
  - `h:X-Custom-Header` - Custom headers

- `v:` - Custom JSON variables
  - `v:customer_id` - Custom metadata for tracking
  - Accessible in webhooks and logs

- `t:` - Template parameters
  - `t:template` - Template name
  - `t:version` - Specific template version
  - `t:variables` - JSON object with template variables

**Scheduling:**
- `o:deliverytime` - Schedule delivery (RFC 2822 format)
  ```
  o:deliverytime: "Fri, 25 Dec 2025 10:00:00 GMT"
  ```

#### Response

Success: HTTP 200 with JSON payload
```json
{
  "id": "<20101112030941.61863.11322@samples.mailgun.org>",
  "message": "Queued. Thank you."
}
```

Error: HTTP 4xx/5xx with error description
```json
{
  "message": "Invalid email address"
}
```

---

### Email Validation API

#### Real-Time Validation

**Endpoint:** `GET /v4/address/validate`

**Parameters:**
- `address` - Email address to validate (required)
- `mailbox_verification` - Check mailbox existence (boolean, default false)

**Validation Checks:**
1. Syntax validation (RFC-compliant grammar)
2. DNS validation (domain MX records)
3. Spell checking (common provider misspellings)
4. ESP-specific local-part grammar rules
5. Mailbox detection (optional, premium)

**Response:**
```json
{
  "result": "valid|invalid|undeliverable|unknown",
  "risk": "low|medium|high",
  "address": "user@example.com",
  "is_valid": true,
  "is_role_address": false,
  "is_free_address": false,
  "reason": "valid_address"
}
```

#### Bulk Validation

**Endpoint:** `POST /v4/address/validate/bulk`

**Features:**
- Upload email lists (CSV format)
- Verify against 450+ billion email database
- Identify undeliverable and high-risk addresses
- Results returned in minutes vs. days
- Batch processing capability

**Use Cases:**
- Pre-send list hygiene (ISPs penalize bounce rates)
- List monetization (clean lists sell at premium)
- Lead qualification (filter test/fake emails)
- Compliance (suppress invalid addresses)

---

### Routes API - Inbound Email Handling

#### Overview

Routes enable Mailgun to **receive** emails on your behalf, parse them, and deliver structured data to your application via webhooks.

#### Email Reception Configuration

1. **Domain Setup**
   - Create MX records pointing to Mailgun
   - All emails to domain received by Mailgun
   - No local mail server required

2. **Route Creation**
   - Match patterns (regex) on To/From addresses
   - Priority ordering (lower number = higher priority)
   - Actions: forward, store, or webhook

#### Inbound Email Parsing

**Received Email Transformation:**
```
Raw SMTP Email
    ↓
Mailgun Processing
    ↓
UTF-8 Encoded JSON
    ↓
Webhook POST to Application
```

**Parsed Fields in JSON:**
- `From` - Sender information
- `To` - Original recipients
- `Headers` - Full MIME headers
- `Body-Plain` - Extracted plain text
- `Body-HTML` - Extracted HTML
- `Attachments` - Base64-encoded with metadata
- `Message-Headers` - Complete header array
- `Stripped-Text` - Text without quoted parts
- `Stripped-HTML` - HTML without quoted parts

#### Route Actions

**1. Forward Action**
```
forward("user@example.com")
```
- Re-send email to another address
- Useful for forwarding workflows

**2. Store Action**
```
store(action="forward", notification="http://example.com/webhook")
```
- Temporarily store in Mailgun (7 days max)
- Retrieve via Messages API
- Useful for archival or async processing

**3. Webhook Action** (Recommended for InfraFabric)
```
POST http://your-app.com/mailgun-webhook
```
- Real-time HTTP POST with parsed email
- JSON payload with all email components
- Immediate processing capability
- Signature verification available

#### Route Priority & Matching

- **Priority:** Numeric value (0 = highest, 10000 = lowest)
- **Expression:** Regular expression or JSONPath matching
- **Examples:**
  - `match_recipient("support@example.com")` - Exact match
  - `match_recipient(".*@example.com")` - Subdomain pattern
  - `match_header("X-Priority", "1")` - Header matching

#### Use Cases for InfraFabric

1. **Alert Routing**
   - Route monitoring alerts by severity
   - Parse and categorize automated emails
   - Forward to incident management

2. **Ticket Creation**
   - Parse customer support emails
   - Extract sender, subject, body
   - Auto-create tickets via webhook

3. **Multi-Tenant Email Handling**
   - Separate routes per tenant domain
   - Webhook payload includes tenant context
   - Isolated email streams

---

### Templates API

#### Template Engine

- **Engine:** Handlebars template syntax
- **Storage:** Mailgun account (version control)
- **Rendering:** Server-side on Mailgun infrastructure
- **Variables:** JSON object substitution

#### Template Syntax

**Variable Substitution:**
```handlebars
Hello {{firstName}}, your order {{orderId}} is confirmed.
```

**Conditional Rendering:**
```handlebars
{{#if isPremium}}
  <p>Premium benefits include...</p>
{{else}}
  <p>Upgrade to premium for benefits.</p>
{{/if}}
```

**Iteration:**
```handlebars
{{#each items}}
  <li>{{this.name}} - ${{this.price}}</li>
{{/each}}
```

**Context Shift:**
```handlebars
{{#with user}}
  <p>Welcome {{name}}</p>
{{/with}}
```

**Equality Comparison:**
```handlebars
{{#equal status "active"}}
  <span class="badge-active">Active</span>
{{/equal}}
```

#### Template API Operations

**Create/Update Template:**
```bash
curl -X POST https://api.mailgun.net/v3/yourcompany.com/templates \
  --user "api:YOUR_API_KEY" \
  -F name="password_reset" \
  -F template='<html>...</html>'
```

**Send with Template:**
```bash
curl -X POST https://api.mailgun.net/v3/yourcompany.com/messages \
  --user "api:YOUR_API_KEY" \
  -F from="support@yourcompany.com" \
  -F to="user@example.com" \
  -F template="password_reset" \
  -F t:variables='{"resetLink": "https://...", "expiresIn": "24 hours"}'
```

#### InfraFabric Use Cases

1. **Notification Templates**
   - System alerts with dynamic severity
   - Deployment notifications with git refs
   - Cost alerts with billing context

2. **Multi-Language Support**
   - Separate templates per language
   - Dynamic selection via variables
   - Translation integration ready

---

### Mailing Lists API

#### Overview

Mailing lists enable bulk email delivery to subscriber groups with the address serving as group identity.

#### List Management Endpoints

**Create List:**
```bash
curl -X POST https://api.mailgun.net/v3/lists \
  --user "api:YOUR_API_KEY" \
  -F address="developers@yourcompany.com" \
  -F name="Developer Team" \
  -F description="All engineering staff"
```

**Add Single Member:**
```bash
curl -X POST https://api.mailgun.net/v3/lists/developers@yourcompany.com/members \
  --user "api:YOUR_API_KEY" \
  -F address="alice@example.com" \
  -F name="Alice Engineer" \
  -F subscribed=True \
  -F vars='{"role": "backend", "team": "platform"}'
```

**Bulk Add Members (up to 1000 per call):**
```bash
curl -X POST https://api.mailgun.net/v3/lists/developers@yourcompany.com/members.json \
  --user "api:YOUR_API_KEY" \
  -F members='[{"address": "bob@example.com", "subscribed": true}, ...]'
```

#### Member Features

- **Subscribed Status** - Control delivery without removal
- **Custom Variables** - Metadata per member (role, department, etc.)
- **List Ownership** - Admin controls and permissions
- **Export** - Bulk member data extraction

#### InfraFabric Use Cases

1. **Notification Groups**
   - Ops team alerts
   - Stakeholder notifications
   - Escalation chains

2. **Multi-Tenant Distribution**
   - Separate list per tenant
   - Dynamic membership management
   - Role-based subscriptions

---

## Pass 3-4: Rigor & Cross-Domain Validation

### Deliverability Features

#### IP Pools & Reputation Management

**Static IP Pools:**
- Group dedicated IPs into custom pools
- Separate mail streams by type (marketing vs transactional)
- Isolate high/low reputation senders
- **Availability:** Scale plans and above

**Dynamic IP Pools (Reputation-Based):**
- Mailgun-managed automatic assignment
- Three-tier categorization:
  1. **Good Pool** - Bounce rate <5%, complaint rate <0.05%
  2. **Poor Pool** - Higher bounce/complaint rates
  3. **New/Unknown** - Accounts <90 days or <1000 msgs/30 days
- Automatic rebalancing based on metrics
- Prevents reputation spillover

#### Domain Reputation Tracking

- **Metrics Tracked:**
  - Bounce rate (hard/soft split)
  - Complaint rate (spam feedback loop)
  - Open rate
  - Click rate
  - Unsubscribe rate

- **Dashboard:**
  - Real-time reputation visualization
  - Historical metrics (30-day rolling average)
  - Trend analysis and alerts
  - Dedicated deliverability expert available

- **Authentication Standards (2025 Requirements):**
  - **SPF** - IP address authorization
  - **DKIM** - Cryptographic signature (auto-rotated 120-day cycle)
  - **DMARC** - Policy enforcement and reporting
  - **BIMI** - Brand logo in inbox (supported)

#### SMTP Relay Options

Mailgun supports both HTTP API and SMTP for sending:
- **SMTP Hostname:** `smtp.mailgun.org`
- **Ports:** 587 (TLS), 25 (no encryption)
- **Authentication:** SMTP_USERNAME and SMTP_PASSWORD from account
- **Throughput:** Limited by plan, negotiable for Scale accounts
- **Use Case:** Legacy systems, bulk sending from cron jobs

---

### Rate Limits & Quotas

#### API Rate Limiting

**HTTP 429 Response:**
```json
{
  "message": "Too many requests (request limit exceeded, try again in 3600 seconds)"
}
```

**Rate Limit Types:**

1. **Request Rate Limit**
   - Default: 300 requests/minute per account (Domains API)
   - Increases with account history and verification

2. **Recipient Rate Limit**
   - Prevents abuse (many recipients in short period)
   - Soft limit enforced by Mailgun
   - Error message indicates "recipient limit exceeded"

3. **Retry-After Header**
   - Indicates seconds to wait before retry
   - Clients must respect this directive
   - HTTP 429 response includes Retry-After

#### New Account Sending Limits

**Initial Restrictions:**
- 100 emails/hour maximum
- 9 emails sent verification requirement
- Business verification process to increase

**Removal Process:**
- Minimum 2 weeks account age
- Positive sending history
- Passed verification review
- Manual request via support

#### Quota Management

**Per-Plan Limits:**
- Foundation: 50,000 emails/month
- Scale: Higher allocations (custom)
- Excess emails: $1.30 per 1000 emails

**Custom Rate Limits:**
- Available for high-volume accounts
- Negotiate during sales process
- Scale plan includes dedicated support

---

## Pricing & Cost Analysis

### Pricing Model

**Type:** Pay-as-you-go with optional committed plans

### Plan Tiers

#### Free Tier
- **Cost:** $0
- **Allocation:** 100 emails/day (3,000/month)
- **Features:**
  - API access
  - Basic webhook tracking
  - One sending domain
  - Mailgun subdomain
- **Suitable for:** Development, testing, light projects

#### Foundation Plan
- **Cost:** $35/month
- **Allocation:** 50,000 emails/month
- **Features:**
  - All Free features
  - Email templates (1,000+ domains)
  - 5-day message log retention
  - Dedicated sending domain
  - Basic tracking
- **Cost per extra email:** $1.30/1000 emails ($0.0013/email)

#### Scale Plan
- **Cost:** Custom pricing (contact sales)
- **Allocation:** 100,000+ emails/month (configurable)
- **Features:**
  - All Foundation features
  - IP pools (static & dynamic)
  - Domain sending keys
  - Advanced analytics
  - Dedicated support
  - SLA guarantee
  - Custom rate limits
  - Whitelabel options

#### Committed Plans

Available for Foundation and Scale tiers:
- 6-month commitment discount
- 12-month commitment discount
- Predictable monthly spend

### EU Regional Pricing

- **EU Data Center:** Located in Germany (api.eu.mailgun.net)
- **EU Pricing:** No premium over US pricing
- **Data Residency:** All processing in EU
- **GDPR Compliant:** By default with EU domain

### Cost Optimization Strategies

1. **Batch Sending**
   - Group messages into single API calls
   - Reduces API request rate
   - Lower transaction costs

2. **Validation Integration**
   - Clean lists before sending ($0/100 validations free tier)
   - Reduce bounces and reputation damage
   - Prevent wasted send allocation

3. **Template Reuse**
   - Server-side template rendering
   - Variable substitution vs. client-side
   - Reduced message size

4. **List Segmentation**
   - Smaller, targeted sends
   - Higher engagement metrics
   - Better IP reputation

### Annual Cost Estimates

**Small Project (5K emails/month):**
- Free plan sufficient
- Cost: $0

**Mid-Scale Project (50K emails/month):**
- Foundation plan: $35/month
- Annual: $420
- Overhead: $0.0033/email

**Enterprise (1M+ emails/month):**
- Scale plan: ~$300-1000/month (negotiable)
- Annual: $3600-12000
- Cost per email: $0.003-0.012

---

## Event Tracking & Webhooks

### Webhook Event Types

Mailgun triggers webhooks for email lifecycle events:

1. **Delivery** - Email accepted by receiving mail server
2. **Open** - Recipient opens email (tracking pixel required)
3. **Click** - Recipient clicks tracked link
4. **Bounce** - Email rejected by receiving server (hard or soft)
5. **Failure** - Message dropped (sender validation, blacklist, etc.)
6. **Unsubscribe** - List-Unsubscribe header clicked
7. **Complaint** - Recipient marked as spam (ISP feedback loop)

### Webhook Payload Structure

```json
{
  "signature": {
    "timestamp": "1234567890",
    "token": "abc123token",
    "signature": "hex_signature_for_verification"
  },
  "event-data": {
    "event": "delivered",
    "timestamp": 1610000000,
    "id": "message_id@mailgun.org",
    "log-level": "info",
    "message": {
      "headers": {
        "to": "user@example.com",
        "message-id": "...",
        "from": "sender@yourcompany.com",
        "subject": "Password Reset"
      },
      "attachments": [],
      "size": 4500
    },
    "recipient": "user@example.com",
    "domain": "mail.yourcompany.com",
    "delivery-status": {
      "tls": true,
      "mx-host": "mx.example.com",
      "code": 250,
      "description": "2.0.0 OK",
      "attempt-no": 1,
      "message": "success"
    },
    "tags": ["notification", "user-alert"],
    "campaigns": [],
    "user-variables": {
      "user_id": "12345",
      "campaign": "alert_system"
    }
  }
}
```

### Webhook Security

**Signature Verification:**
- Mailgun signs each webhook with API key
- HMAC-SHA256 signature in `signature.signature`
- Verify timestamp + token + signature
- Prevent replay attacks

**Verification Steps:**
1. Concatenate timestamp + token
2. HMAC-SHA256 with API key
3. Compare computed signature to provided signature

### Webhook Configuration

**Management Endpoints:**
```bash
# Create webhook
POST /v3/{domain}/webhooks

# List webhooks
GET /v3/{domain}/webhooks

# Update webhook
POST /v3/{domain}/webhooks/{event}

# Delete webhook
DELETE /v3/{domain}/webhooks/{event}
```

**Webhook Retry Policy:**
- Mailgun retries failed webhooks
- Exponential backoff strategy
- 24-hour retry window
- Webhook failures do not affect email delivery

### InfraFabric Webhook Use Cases

1. **Notification Status Tracking**
   - Monitor critical alert delivery
   - Alert if delivery fails
   - Track user engagement (opens/clicks)

2. **Bounce Management**
   - Auto-suppress bounced addresses
   - Update user database
   - Trigger re-validation for soft bounces

3. **Complaint Handling**
   - Immediate removal on spam report
   - Legal compliance automation
   - Reputation monitoring

4. **Audit Logging**
   - Record all email events
   - Compliance reporting
   - Debugging sending issues

---

## Integration Implementation

### SDK Availability & Installation

#### Python SDK

**Installation:**
```bash
pip install mailgun-python
```

**Basic Usage:**
```python
from mailgun.events import EventIterator
from mailgun.exceptions import MailgunAPIError
from mailgun.messages import MessageBuilder

def send_message():
    builder = MessageBuilder()
    builder.set_from_address("from@example.com")
    builder.add_to_recipient("to@example.com")
    builder.set_subject("Hello")
    builder.set_text_body("Testing")

    mg = Mailgun('YOUR_API_KEY', 'YOUR_DOMAIN')
    result = mg.send_message(builder.build())
    print(result)
```

**Features:**
- Message building with fluent API
- Batch sending support
- Event iteration for logs
- Template rendering
- Mailing list management

#### Go SDK

**Installation:**
```bash
go get github.com/mailgun/mailgun-go/v5
```

**Basic Usage:**
```go
mg := mailgun.NewMailgun("your-domain.com", "your-api-key")
sender := "sender@your-domain.com"
subject := "Hello"
body := "Testing"
message := mg.NewMessage(sender, subject, body, "recipient@example.com")

ctx, cancel := context.WithTimeout(context.Background(), time.Second*30)
defer cancel()

_, id, err := mg.Send(ctx, message)
```

**Features:**
- Type-safe API
- Concurrent sending support
- Batch operations
- Custom context support

#### Ruby SDK

**Installation:**
```bash
gem install mailgun-ruby
```

**Basic Usage:**
```ruby
require 'mailgun'

mailgun = Mailgun()
result = mailgun.send_message(
  "your-domain.com",
  { :from => 'sender@your-domain.com',
    :to => 'recipient@example.com',
    :subject => 'Hello',
    :text => 'Testing'
  })
```

**Features:**
- ActiveMailer integration
- Rails compatibility
- Event tracking
- List management

#### Node.js SDK

**Installation:**
```bash
npm install mailgun.js
```

**Basic Usage:**
```javascript
const mailgun = require("mailgun.js");
const mg = mailgun.client({username: "api", key: "your-api-key"});

mg.messages.create("your-domain.com", {
  from: "sender@your-domain.com",
  to: "recipient@example.com",
  subject: "Hello",
  text: "Testing"
}).then(msg => console.log(msg))
  .catch(err => console.log(err));
```

**Features:**
- ES6/async-await support
- TypeScript definitions
- Browser compatibility
- Promise-based API

---

### Error Handling & Response Codes

#### Common HTTP Status Codes

| Code | Meaning | Retry | Example |
|------|---------|-------|---------|
| 200 | Success | No | Message queued |
| 400 | Bad Request | No | Invalid email format |
| 401 | Unauthorized | No | Wrong API key |
| 404 | Not Found | No | Domain doesn't exist |
| 429 | Rate Limited | Yes | Too many requests |
| 500 | Server Error | Yes | Mailgun service issue |

#### Error Response Format

```json
{
  "message": "Invalid email address",
  "error": "invalid_email"
}
```

#### Handling Rate Limits in Code

**Python Example:**
```python
import time
import requests

def send_with_retry(message, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = mailgun.send_message(message)
            return result
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get('Retry-After', 5))
                time.sleep(retry_after)
            else:
                raise
```

---

## European Data Residency & GDPR Compliance

### EU Infrastructure

**EU Data Center:**
- **Location:** Germany
- **Provider:** Sinch (parent company)
- **Endpoint:** `https://api.eu.mailgun.net/v3/` (vs. `https://api.mailgun.net/v3/`)
- **Domain Assignment:** Cannot change region post-creation (GDPR requirement)

**Regional Considerations:**
- All data processing in EU jurisdiction
- No US-based processing
- Compliant with EU data protection laws

### GDPR Compliance Framework

**1. Data Processing Agreement (DPA)**
- Mailgun has EU Model Standard Contractual Clauses (SCCs)
- Covers data transfers and processing
- Included in Mailgun's Data Processing Addendum

**2. EU-US Data Privacy Framework**
- Mailgun certified to EU-US Data Privacy Framework
- Self-certification on file with US Department of Commerce
- Demonstrates adequate safeguards

**3. Vendor Management**
- All sub-processors have data protection agreements
- Transparent sub-processor list maintained
- Changes notified in advance

### Data Protection Measures

**Encryption:**
- TLS for data in transit
- Encryption at rest for stored data
- Key management per EU standards

**Data Minimization:**
- Collect only necessary personal data
- 30-day message log retention (configurable)
- Webhook payload restrictions

**Subject Rights Fulfillment:**
- Data access requests via API
- Deletion capabilities (mailboxes, logs)
- Export functionality for user data

### GDPR-Specific Mailgun Features

**1. Email Validation**
- Bulk list validation without storing emails
- Database queries for existence verification
- No persistent storage of validated addresses

**2. Bounce/Complaint Handling**
- Automatic suppression on bounce
- Complaint feedback loop integration
- Audit trail for compliance

**3. Consent Management**
- List-Unsubscribe header support
- One-click unsubscribe compliance
- Preference center integration

**4. Data Residency**
- EU domain = EU processing
- No data transfer to US
- Audit trails in EU region

### Compliance Checklist

- [ ] Use EU endpoint for European users
- [ ] Implement Data Processing Agreement
- [ ] Configure List-Unsubscribe headers
- [ ] Set up complaint handling webhooks
- [ ] Document consent for each email recipient
- [ ] Implement data retention/deletion policies
- [ ] Conduct transfer impact assessment
- [ ] Audit sub-processors

---

## Pass 5-6: Framework Mapping to InfraFabric

### Notification Architecture Integration

#### Use Case 1: System Alerts & Notifications

**Components:**
```
InfraFabric System Event
    ↓
Alert Generator
    ↓
Mailgun Send API
    ↓
User Notification
```

**Implementation:**
```python
# InfraFabric Alert Service
class AlertNotificationService:
    def __init__(self, mailgun_api_key, domain):
        self.mg = Mailgun(mailgun_api_key, domain)

    def send_infrastructure_alert(self, alert):
        message = MessageBuilder()
        message.set_from_address("alerts@infrafabric.io")
        message.add_to_recipient(alert.recipient_email)
        message.set_subject(f"[{alert.severity}] {alert.title}")
        message.set_template("infrastructure_alert")

        variables = {
            "alert_id": alert.id,
            "severity": alert.severity,
            "service": alert.service,
            "message": alert.message,
            "timestamp": alert.timestamp,
            "action_url": alert.dashboard_link
        }

        message.set_template_variables(variables)
        result = self.mg.send_message(message.build())
        return result
```

**Template (infrastructure_alert):**
```handlebars
<h2>Infrastructure Alert: {{severity}}</h2>
<p><strong>Service:</strong> {{service}}</p>
<p><strong>Message:</strong> {{message}}</p>
<p><strong>Time:</strong> {{timestamp}}</p>
<a href="{{action_url}}">View Details</a>
```

#### Use Case 2: Multi-Tenant Inbound Email Routing

**Architecture:**
```
Customer Email → Mailgun Route
    ↓
Email Parsing (JSON)
    ↓
Webhook to InfraFabric
    ↓
Multi-Tenant Handler
    ↓
Tenant Database
```

**Webhook Handler (Flask):**
```python
@app.route('/mailgun/webhook', methods=['POST'])
def mailgun_webhook():
    # Verify signature
    signature = request.form.get('signature[signature]')
    token = request.form.get('signature[token]')
    timestamp = request.form.get('signature[timestamp]')

    if not verify_mailgun_signature(signature, token, timestamp):
        return 'Invalid signature', 403

    # Extract email data
    event_data = json.loads(request.form.get('event-data'))

    # Route to tenant
    recipient = event_data['recipient']
    tenant_id = parse_tenant_from_recipient(recipient)

    # Store in tenant context
    email_service.store_inbound_email(
        tenant_id=tenant_id,
        sender=event_data['message']['headers']['from'],
        subject=event_data['message']['headers']['subject'],
        body_text=event_data.get('body-plain'),
        body_html=event_data.get('body-html'),
        attachments=event_data.get('attachments'),
        received_at=datetime.fromtimestamp(event_data['timestamp'])
    )

    return 'OK', 200
```

**Route Configuration (Mailgun):**
```
Pattern: match_recipient(".*@infrafabric-tenants.io")
Priority: 10
Action: forward("https://api.infrafabric.io/mailgun/webhook")
```

#### Use Case 3: Cost Tracking & Billing Notifications

**Implementation:**
```python
class BillingNotificationService:
    def __init__(self, mailgun_client):
        self.mg = mailgun_client

    def send_cost_alert(self, account, usage_stats):
        # Determine severity
        percent_used = (usage_stats['emails_sent'] / account.monthly_quota) * 100

        if percent_used > 90:
            severity = "critical"
            color = "#ff0000"
        elif percent_used > 75:
            severity = "warning"
            color = "#ff9900"
        else:
            severity = "info"
            color = "#00aa00"

        # Send via template
        message = MessageBuilder()
        message.set_from_address("billing@infrafabric.io")
        message.add_to_recipient(account.owner_email)
        message.set_template("cost_tracking_alert")

        message.set_template_variables({
            "account_name": account.name,
            "emails_sent": usage_stats['emails_sent'],
            "quota": account.monthly_quota,
            "percent_used": percent_used,
            "estimated_cost": usage_stats['estimated_cost'],
            "severity": severity,
            "color": color,
            "increase_quota_url": "https://dashboard.infrafabric.io/billing"
        })

        return self.mg.send_message(message.build())
```

---

### Webhook Event Processing Pipeline

**Infrastructure:**
```
Mailgun Webhook → Signature Verification
    ↓
Event Type Router
    ↓
Handlers:
  - Delivery Handler → Event Log
  - Bounce Handler → Suppression List
  - Complaint Handler → Legal Audit
  - Open/Click → Analytics Pipeline
```

**Event Processing Class:**
```python
class MailgunEventProcessor:
    def __init__(self, db, event_bus):
        self.db = db
        self.event_bus = event_bus  # Internal event system

    def process_webhook(self, webhook_data):
        event_type = webhook_data['event-data']['event']

        handlers = {
            'delivered': self.handle_delivery,
            'bounce': self.handle_bounce,
            'complaint': self.handle_complaint,
            'open': self.handle_open,
            'click': self.handle_click
        }

        handler = handlers.get(event_type)
        if handler:
            handler(webhook_data['event-data'])

    def handle_delivery(self, event_data):
        # Update notification status
        notification = self.db.notification.find_by_message_id(event_data['id'])
        notification.status = 'delivered'
        notification.delivered_at = datetime.fromtimestamp(event_data['timestamp'])
        notification.save()

        # Emit internal event for audit
        self.event_bus.emit('email.delivered', {
            'notification_id': notification.id,
            'recipient': event_data['recipient'],
            'mx_host': event_data['delivery-status']['mx-host']
        })

    def handle_bounce(self, event_data):
        recipient = event_data['recipient']
        bounce_type = 'hard' if event_data['bounce']['permanent'] else 'soft'

        # Add to suppression list
        if bounce_type == 'hard':
            self.db.suppression_list.add(recipient, 'bounce', event_data['bounce']['error_code'])

        # Update user record
        user = self.db.user.find_by_email(recipient)
        if user:
            user.email_status = 'bounced'
            user.save()

        # Trigger re-validation for soft bounces
        if bounce_type == 'soft':
            self.event_bus.emit('email.soft_bounce', {'email': recipient})

    def handle_complaint(self, event_data):
        recipient = event_data['recipient']

        # Immediate removal
        self.db.suppression_list.add(recipient, 'complaint', 'spam_report')

        # Legal compliance logging
        self.db.compliance_log.create({
            'event': 'spam_complaint',
            'email': recipient,
            'timestamp': datetime.fromtimestamp(event_data['timestamp']),
            'mailbox_provider': event_data['provider']
        })
```

---

### Domain & Subdomain Strategy for InfraFabric

**Configuration Pattern:**
```
Primary Domain: infrafabric.io
├── Sending Domain: notifications.infrafabric.io
│   └── API Key: domain-specific (restricted to send only)
├── Support Domain: support.infrafabric.io
│   └── Routes configured for inbound email
└── Billing Domain: billing.infrafabric.io
    └── Templates for cost alerts
```

**Rationale:**
- Separate sending domains for reputation isolation
- Subdomain verification avoids CNAME conflicts
- Domain-specific keys limit exposure if compromised
- Route rules match on subdomain for tenant isolation

**Multi-Tenant Scenario:**
```
Tenant A: tenant-a@support.infrafabric.io
Tenant B: tenant-b@support.infrafabric.io

Route Pattern: match_recipient("tenant-.*@support.infrafabric.io")
Webhook extracts tenant from local-part
```

---

## Pass 7-8: Meta-Validation & Deployment Planning

### Implementation Estimate

**Phase 1: Core Integration (16-20 hours)**
- Mailgun API wrapper class: 4 hours
- Authentication & key management: 3 hours
- Send API integration: 3 hours
- Error handling & retries: 3 hours
- Testing & validation: 3-4 hours

**Phase 2: Advanced Features (12-16 hours)**
- Webhook infrastructure setup: 4 hours
- Event processing pipeline: 4 hours
- Templates system integration: 2 hours
- Email validation integration: 2 hours
- Batch operations: 2 hours
- Testing & documentation: 2-4 hours

**Phase 3: Multi-Tenant Support (8-12 hours)**
- Tenant isolation logic: 3 hours
- Domain/subdomain routing: 2 hours
- Inbound email routes setup: 2 hours
- Webhook tenant routing: 2 hours
- Testing & integration: 2 hours

**Phase 4: Monitoring & Compliance (6-10 hours)**
- Webhook signature verification: 2 hours
- Rate limit handling: 2 hours
- Bounce/complaint suppression: 1 hour
- GDPR compliance audit: 2 hours
- Documentation: 1-2 hours

**Total Estimated Effort:** 42-58 hours (5-7 days @ 8h/day)

### Deployment Checklist

**Pre-Deployment:**
- [ ] Mailgun account created and verified
- [ ] API keys generated (separate keys per environment)
- [ ] Sending domains configured and DNS verified
- [ ] Webhook endpoint accessible and HTTPS
- [ ] EU endpoint selected if applicable
- [ ] Rate limits requested if high volume expected

**Development Setup:**
- [ ] SDK installed in project
- [ ] API wrapper classes implemented
- [ ] Local testing with Mailgun Sandbox domain
- [ ] Mock webhook endpoints for local testing
- [ ] Error handling and retry logic verified

**Staging Environment:**
- [ ] Real Mailgun domain configured
- [ ] Webhook signatures verified
- [ ] Rate limits tested with load
- [ ] Event processing pipeline validated
- [ ] Template rendering verified
- [ ] Email validation API tested

**Production Deployment:**
- [ ] Scale plan or appropriate tier selected
- [ ] IP pooling configured if multiple domains
- [ ] Webhook monitoring in place
- [ ] Alerting configured for delivery failures
- [ ] Bounce/complaint suppression automation running
- [ ] GDPR compliance procedures documented
- [ ] Backup notification channel configured

**Operational:**
- [ ] Monitor bounce rates weekly
- [ ] Review complaint feedback loop alerts
- [ ] Audit suppression list monthly
- [ ] Check API usage vs. quota
- [ ] Validate webhook processing latency

### Risk Mitigation

**Risk: Rate Limiting During Peak Load**
- Mitigation: Implement queue-based sending with exponential backoff
- Mitigation: Request rate limit increase before peak periods
- Mitigation: Use batch endpoints for high-volume sends

**Risk: Low Deliverability Due to Reputation**
- Mitigation: Start with Foundation plan for reputation building
- Mitigation: Implement email validation before sending
- Mitigation: Monitor bounce/complaint rates weekly
- Mitigation: Use dedicated IPs with IP pools on Scale plan

**Risk: GDPR Non-Compliance**
- Mitigation: Use EU endpoint for all EU customer data
- Mitigation: Document consent for each email
- Mitigation: Implement automatic unsubscribe handling
- Mitigation: Maintain Data Processing Agreement

**Risk: Lost Email History**
- Mitigation: Log all Mailgun events to internal database
- Mitigation: Implement webhook processing with idempotency
- Mitigation: Archive email metadata for compliance

### Cost Optimization

**Strategies:**
1. **List Hygiene** - Validate emails before sending ($0 baseline)
2. **Template Reuse** - Use server-side templates to reduce message size
3. **Batch Operations** - Group 1-5 recipients per API call
4. **Off-Peak Sending** - Schedule non-urgent emails during low-rate periods
5. **Graduated Rollout** - Start with Free/Foundation tier, upgrade as needed

**Cost Projection:**
- **Tier 1 (Dev/Test):** Free ($0/month)
- **Tier 2 (Small Scale):** Foundation ($35/month for 50K)
- **Tier 3 (Enterprise):** Scale ($300-1000/month negotiable)

---

## SDK Comparison & Recommendations

| SDK | Language | Maturity | Use Case | Async Support |
|-----|----------|----------|----------|---------------|
| mailgun-python | Python | Stable | InfraFabric primary | Limited |
| mailgun-go | Go | Stable | High-performance services | Yes (goroutines) |
| mailgun-ruby | Ruby | Stable | Rails integration | Limited |
| mailgun.js | Node.js | Stable | API servers, Lambda | Yes (promises) |

**Recommendation for InfraFabric:**
- **Primary:** Go SDK (if Go services used) or Python (if Python primary)
- **Rationale:** Type-safe, concurrent support, active maintenance
- **Secondary:** Node.js for serverless/Lambda functions

---

## Integration Patterns & Examples

### Pattern 1: Simple Notification Send

```python
from mailgun import Mailgun, MessageBuilder

def send_notification(recipient, title, message):
    mg = Mailgun('api-key', 'notifications.infrafabric.io')

    builder = MessageBuilder()
    builder.set_from_address('alerts@infrafabric.io')
    builder.add_to_recipient(recipient)
    builder.set_subject(f'Alert: {title}')
    builder.set_html_body(f'<p>{message}</p>')

    return mg.send_message(builder.build())
```

### Pattern 2: Bulk Notification with Validation

```python
def send_bulk_notification(recipients, template_name, variables):
    # Filter valid emails
    validator = Mailgun('api-key', 'notifications.infrafabric.io')
    valid_recipients = [
        r for r in recipients
        if validator.validate(r)['is_valid']
    ]

    # Batch send
    messages = []
    for recipient in valid_recipients:
        msg = create_message(recipient, template_name, variables)
        messages.append(msg)

    # Send in batches of 5
    for batch in chunks(messages, 5):
        for msg in batch:
            validator.send_message(msg)
```

### Pattern 3: Webhook Event Processing with Async Task Queue

```python
from celery import shared_task

@shared_task
def process_mailgun_webhook(webhook_data):
    processor = MailgunEventProcessor(db, event_bus)

    try:
        processor.process_webhook(webhook_data)
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        # Retry with exponential backoff
        raise
```

---

## Troubleshooting Guide

### Issue: "401 Unauthorized"
**Cause:** Invalid API key or missing authentication
**Solution:**
1. Verify API key in Account Settings
2. Check HTTP Basic auth format: `Authorization: Basic api:YOUR_KEY`
3. Ensure key matches domain region (US vs EU)

### Issue: "404 Not Found"
**Cause:** Domain not configured or API endpoint wrong
**Solution:**
1. Verify domain in Mailgun account
2. Check DNS records are fully verified
3. Use correct endpoint: `api.mailgun.net` (US) or `api.eu.mailgun.net` (EU)

### Issue: "429 Too Many Requests"
**Cause:** Rate limit exceeded
**Solution:**
1. Check Retry-After header
2. Implement exponential backoff
3. Request rate limit increase via support
4. Use queue-based sending pattern

### Issue: Low Deliverability / High Bounce Rate
**Cause:** Reputation or authentication issues
**Solution:**
1. Verify SPF/DKIM/DMARC records
2. Check domain reputation in dashboard
3. Implement email validation before sending
4. Consider dedicated IP pool on Scale plan

### Issue: Webhook Not Receiving Events
**Cause:** Signature verification failure or endpoint not responding
**Solution:**
1. Verify webhook URL is HTTPS and publicly accessible
2. Check webhook is registered in domain settings
3. Verify signature with correct API key
4. Check endpoint returns 200 status code

---

## IF.TTT Citations (8-Pass Sources)

### Pass 1-2: Documentation Sources
1. Mailgun API Overview - https://documentation.mailgun.com/docs/mailgun/api-reference/api-overview/ - Retrieved 2025-11-14
2. Mailgun Send API - https://documentation.mailgun.com/docs/mailgun/api-reference/send/mailgun/messages - Retrieved 2025-11-14
3. Mailgun Email Validation - https://documentation.mailgun.com/docs/validate/single-valid-ir - Retrieved 2025-11-14
4. Mailgun Routes (Inbound Email) - https://documentation.mailgun.com/docs/mailgun/user-manual/receive-forward-store/ - Retrieved 2025-11-14
5. Mailgun Templates - https://documentation.mailgun.com/docs/mailgun/user-manual/sending-messages/send-templates - Retrieved 2025-11-14
6. Mailgun Webhooks - https://documentation.mailgun.com/docs/mailgun/api-reference/send/mailgun/webhooks - Retrieved 2025-11-14

### Pass 3-4: Cross-Domain Validation
7. Mailgun IP Pools - https://documentation.mailgun.com/docs/mailgun/api-reference/send/mailgun/ip-pools - Retrieved 2025-11-14
8. Mailgun Pricing - https://www.mailgun.com/pricing - Retrieved 2025-11-14
9. Mailgun Deliverability - https://www.mailgun.com/email-verification/email-verifier/ - Retrieved 2025-11-14
10. Email Authentication Requirements 2025 - https://www.mailgun.com/state-of-email-deliverability/chapter/email-authentication-requirements/ - Retrieved 2025-11-14

### Pass 5-6: SDK & Implementation
11. Python SDK - https://github.com/mailgun/mailgun-python - Retrieved 2025-11-14
12. Go SDK - https://github.com/mailgun/mailgun-go - Retrieved 2025-11-14
13. Ruby SDK - https://github.com/mailgun/mailgun-ruby - Retrieved 2025-11-14
14. Node.js SDK - https://github.com/mailgun/mailgun.js - Retrieved 2025-11-14
15. Mailgun Rate Limits - https://help.mailgun.com/hc/en-us/articles/115001124753-Account-Sending-Limitation - Retrieved 2025-11-14

### Pass 7-8: Compliance & Enterprise Features
16. Mailgun GDPR & EU Compliance - https://www.mailgun.com/gdpr/ - Retrieved 2025-11-14
17. Mailgun Data Privacy - https://www.mailgun.com/resources/learn/gdpr/ - Retrieved 2025-11-14
18. Mailgun API Authentication - https://documentation.mailgun.com/docs/mailgun/api-reference/mg-auth - Retrieved 2025-11-14
19. Where to Find API Keys - https://help.mailgun.com/hc/en-us/articles/203380100-Where-can-I-find-my-API-keys-and-SMTP-credentials - Retrieved 2025-11-14
20. Mailgun Mailing Lists - https://documentation.mailgun.com/docs/mailgun/user-manual/sending-messages/mailing-lists - Retrieved 2025-11-14

---

## Research Conclusions

### Mailgun Suitability for InfraFabric

**Strengths:**
1. **Developer-First API** - Clean REST design, multiple SDKs, excellent documentation
2. **Inbound Email Routing** - Core capability for multi-tenant email handling via webhook routes
3. **Flexible Pricing** - Free tier for development, Foundation for production, Scale for enterprise
4. **Event Tracking** - Comprehensive webhook support for delivery/bounce/complaint/open/click
5. **Compliance** - GDPR-ready, EU data residency, Standard Contractual Clauses
6. **Validation & List Management** - Email validation and mailing lists API built-in
7. **Enterprise Features** - IP pools, dedicated keys, custom rate limits

**Limitations:**
1. **New Account Restrictions** - 100 emails/hour initial limit (requires 2-week verification period)
2. **Rate Limiting** - Default 300 req/min (requires custom negotiation for high volume)
3. **Message Retention** - 5-day log retention on Foundation (7 days for routes inbound)
4. **Webhook Retry** - 24-hour retry window (not infinite)

**Recommendation:** **APPROVED for InfraFabric Integration**

Mailgun provides production-ready email capabilities with strong compliance, flexible scaling, and critical inbound email routing. Implementation should follow the 42-58 hour estimate with staged deployment from Foundation to Scale tier as volume grows.

**Next Steps:**
1. Create Mailgun account and verify domains
2. Generate API keys (separate for dev/staging/prod)
3. Implement core Python/Go SDK wrapper
4. Set up webhook infrastructure for event processing
5. Configure rate limit handling and retry logic
6. Implement GDPR compliance procedures

---

**Document Version:** 1.0
**Last Updated:** 2025-11-14
**Research Methodology:** IF.search 8-pass
**Agent:** Haiku-33 (Claude 4.5 Haiku)
