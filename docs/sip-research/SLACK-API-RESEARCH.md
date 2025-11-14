# Slack Team Collaboration API - InfraFabric Integration Research

**Agent:** Haiku-39
**Methodology:** IF.search 8-pass
**Date:** 2025-11-14
**Status:** Research Complete - Ready for Integration Planning

---

## Executive Summary

Slack's comprehensive API ecosystem provides multiple pathways for InfraFabric to integrate alerting, collaboration, and team coordination capabilities. The platform supports bot automation, real-time messaging, interactive components, and enterprise-grade security features. For InfraFabric's use case—infrastructure monitoring, alert distribution, and incident coordination—the optimal integration strategy leverages:

1. **Incoming Webhooks** for simple alert distribution
2. **Events API** with Bolt framework for interactive incident management
3. **Slash Commands** for on-demand infrastructure queries
4. **Interactive Components (Block Kit)** for workflow automation
5. **Socket Mode** for development without public endpoints

**Key Finding:** Slack is ideal for InfraFabric's team coordination and alerting needs across all pricing tiers, with Enterprise Grid providing SCIM/SSO capabilities for larger deployments.

---

## Authentication & Security

### OAuth 2.0 Flow

Slack implements OAuth 2.0 v2 (the current standard), which provides granular permission scoping and enhanced security compared to legacy implementations. The flow involves:

1. **User Authorization**: Workspace member clicks "Add to Slack" button
2. **Authorization Code Exchange**: Backend exchanges code for tokens via `oauth.v2.access`
3. **Token Issuance**: Both bot and user tokens issued based on requested scopes
4. **Token Storage**: Securely store tokens with workspace ID for multi-workspace support

#### Process Flow:
```
1. Redirect to https://slack.com/oauth_authorize?
   client_id=YOUR_CLIENT_ID&
   scope=chat:write,commands&
   redirect_uri=YOUR_REDIRECT_URI

2. User authorizes → Slack redirects to redirect_uri with code
3. Exchange code: POST /oauth.v2.access with code, client_id, client_secret
4. Response contains bot token (xoxb-...) and user token (xoxp-...)
```

### Bot User OAuth Tokens

- **Format**: Start with `xoxb-`
- **Usage**: Represents the bot identity, not tied to individual users
- **Permissions**: Configured via scopes during app installation
- **Common Scopes**:
  - `chat:write` - Post messages
  - `chat:write.public` - Post in public channels
  - `files:write` - Upload files
  - `commands` - Slash command execution
  - `app_mentions:read` - Bot mentions in channels
  - `channels:read` - List channels
  - `users:read` - Get user information

### User OAuth Tokens

- **Format**: Start with `xoxp-`
- **Usage**: Actions on behalf of individual users
- **Scopes**: Separate user_scopes parameter in OAuth flow
- **Common Use**: File uploads, channel creation on behalf of user

### Token Rotation & Management

- **Token Expiration**: OAuth tokens do **NOT** expire (unlike standard OAuth implementations)
- **Token Revocation**: Must be explicitly revoked; no expiration date
- **Best Practice**: Implement token rotation strategy for security:
  - Store tokens in secure vault (AWS Secrets Manager, HashiCorp Vault)
  - Implement refresh mechanisms if tokens are compromised
  - Audit token usage through Enterprise Grid audit logs

### Scope Management

- **Scope Addition**: Each app installation can request additional scopes
- **Scope Accumulation**: New scopes are additive to existing scopes
- **No Scope Removal**: Cannot remove scopes without revoking entire token
- **User Impact**: Workspace admins can audit app permissions

---

## Core API Capabilities

### Web API

The synchronous HTTP-based API provides the foundation for most Slack integrations.

#### Key Methods for InfraFabric

**Message Posting:**
- `chat.postMessage` - Post messages to channels/users
  - Rate Limit: 1 message/second per channel + workspace-wide burst limits
  - Parameters: `channel`, `text`, `blocks`, `attachments`, `thread_ts`
  - Returns: Channel, timestamp, message details

**Conversation Management:**
- `conversations.list` - List all channels
  - Rate Limit: 2 requests per minute (Tier 4)
  - Filter by type: public, private, im, mpim

- `conversations.history` - Fetch messages
  - **NEW LIMIT (2025)**: 15 messages per request at 1 req/min for non-Marketplace apps
  - **Marketplace apps**: Unchanged rate limits
  - **Custom apps**: 50+ requests per minute

- `conversations.replies` - Get thread replies
  - Same rate limits as conversations.history

**User Management:**
- `users.list` - List workspace members
  - Rate Limit: 2 requests per minute

- `users.info` - Get user details
  - Rate Limit: 50 requests per minute (Tier 2)

**File Operations:**
- `files.upload` - Upload files to Slack
  - Rate Limit: 20 requests per minute
  - Supports images, logs, reports

- `files.list` - List files in workspace
  - Rate Limit: 2 requests per minute

**Search:**
- `search.messages` - Search workspace messages
  - Rate Limit: 2 requests per minute
  - Useful for incident timeline reconstruction

**Channels:**
- `channels.create` - Create new channels
  - Rate Limit: 20 requests per minute
  - Use case: Auto-create incident channels

---

### Events API

Real-time, push-based event delivery replacing the legacy RTM API.

#### Event Subscription Types

**Key Events for InfraFabric:**

1. **app_mention** - Bot mentioned in message
   ```json
   {
     "type": "event_callback",
     "event": {
       "type": "app_mention",
       "channel": "C1234567890",
       "user": "U1234567890",
       "text": "@alertbot check cpu",
       "ts": "1234567890.123456"
     }
   }
   ```

2. **message** - Message posted to subscribed channels
   - Subscribe to specific channels
   - Allows InfraFabric to monitor alert discussion threads

3. **reaction_added** / **reaction_removed** - Emoji reactions
   - Track incident acknowledgment (e.g., thumbs up = acknowledged)

4. **file_created** / **file_shared** - File operations
   - Capture uploaded logs, dashboards

5. **channel_created** - New channel creation
   - Auto-subscribe to incident channels

#### URL Verification Challenge

When configuring Request URL, Slack sends:

```json
{
  "token": "Jhj5dZrVaK7ZwHHjRyZWjbDl",
  "challenge": "3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P",
  "type": "url_verification"
}
```

**Response:** HTTP 200 with challenge value in plaintext or JSON.

#### Payload Structure

```json
{
  "token": "verification_token",
  "team_id": "T1234567890",
  "event_id": "Ev123ABC456",
  "event": {
    "type": "app_mention",
    "user": "U1234567890",
    "text": "@alertbot status",
    "channel": "C1234567890",
    "ts": "1234567890.123456"
  },
  "type": "event_callback",
  "event_ts": "1234567890.123456",
  "event_time": 1234567890
}
```

#### Retry Logic

- **Automatic Retries**: Slack retries failed deliveries with exponential backoff
- **Retry Window**: Up to 3 minutes for retry attempts
- **Idempotency**: Events include `event_id` for deduplication
- **Timeout**: Must respond within 3 seconds for HTTP endpoint

---

### RTM API (Real-Time Messaging) - LEGACY

**Status:** Deprecated - Not recommended for new development

#### Why Avoid RTM:

1. **Overly Permissive Scopes**: Requires broad workspace access
2. **Workspace Admin Resistance**: Most admins block RTM apps
3. **Granular Apps Not Supported**: Newer app permission model incompatible
4. **Deprecation Timeline**: Classic apps being phased out

#### Technical Details (Reference Only):

- **Protocol**: WebSocket-based
- **Connection**: `rtm.connect` method returns WebSocket URL
- **URL Validity**: Single-use URLs valid for 30 seconds only
- **Authentication**: Requires `rtm:bot` scope (very permissive)

**InfraFabric Recommendation:** Use Socket Mode or HTTP Events API instead.

---

### Webhooks

#### Incoming Webhooks (Recommended for Alerts)

Simple one-way HTTP POST mechanism for sending messages.

**Setup:**
1. Create incoming webhook in Slack app configuration
2. Receive unique HTTPS URL
3. POST JSON payload to URL

**Webhook URL Format:**
```
https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
```

**Simple Message Payload:**
```json
{
  "text": "Alert: CPU usage critical (95%)",
  "channel": "#alerts",
  "username": "InfraFabric Alert"
}
```

**Advanced Payload with Blocks:**
```json
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "🚨 Critical Alert"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*Server:*\napi-prod-01"
        },
        {
          "type": "mrkdwn",
          "text": "*Metric:*\nCPU Usage"
        },
        {
          "type": "mrkdwn",
          "text": "*Value:*\n95%"
        },
        {
          "type": "mrkdwn",
          "text": "*Severity:*\nCritical"
        }
      ]
    }
  ]
}
```

**Rate Limits:** No strict rate limits documented, but Slack recommends reasonable throughput (1-10 messages/second guideline).

**InfraFabric Use Cases:**
- Initial alert notification to channels
- Escalation notifications
- Status updates
- Simple acknowledgment flows

#### Outgoing Webhooks (Legacy)

**Status:** Superseded by Events API
- **Limitation**: Public channels only
- **Trigger**: Specific keywords mentioned
- **Not Recommended**: Use Events API instead

---

## Bot Development

### Bolt Framework (Recommended)

The modern, official framework for building Slack apps with minimal boilerplate.

#### Available SDKs

**Python Bolt SDK:**
- GitHub: `slackapi/bolt-python`
- Stars: 1,241
- Latest Update: November 11, 2025
- Package: `slack_bolt`

```python
from slack_bolt import App

app = App(token=os.environ.get("SLACK_BOT_TOKEN"),
          signing_secret=os.environ.get("SLACK_SIGNING_SECRET"))

@app.event("app_mention")
def handle_mentions(body, say):
    say("Thanks for the mention! Current infrastructure status: All systems nominal.")

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
```

**Node.js Bolt SDK:**
- GitHub: `slackapi/bolt-js`
- Stars: 2,866
- Latest Update: November 10, 2025
- Package: `@slack/bolt`

```javascript
const { App } = require('@slack/bolt');

const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  signingSecret: process.env.SLACK_SIGNING_SECRET
});

app.event('app_mention', async ({ event, say }) => {
  await say(`Thanks for the mention, <@${event.user}>!`);
});

app.start(process.env.PORT || 3000);
```

**Java SDK:**
- GitHub: `slackapi/java-slack-sdk`
- Package: `com.slack.api:slack-api-client`
- Latest: November 2025

#### Bolt Framework Features

1. **Token Rotation**: Automatic handling of token rotation
2. **Rate Limit Management**: Built-in exponential backoff
3. **Event Listeners**: Simple decorator-based event handling
4. **Middleware System**: Request/response processing pipeline
5. **Socket Mode Support**: WebSocket development without public endpoints
6. **Error Handling**: Automatic retry with configurable handlers
7. **Async Support**: Full async/await support (JS/Python)

#### Socket Mode Development

Eliminates need for public HTTP endpoint:

```python
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.event("app_mention")
def handle_mentions(body, say):
    say("Handling mention without public endpoint!")

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
```

**Key Socket Mode Details:**
- WebSocket connection instead of HTTP
- Up to 10 concurrent connections per app
- Ideal for development and corporate firewalls
- Cannot be published to Slack App Directory
- Requires `app-level:connections:write` scope

---

### Slash Commands

Custom commands prefixed with `/` for user interaction.

#### Registration & Setup

1. **In Slack App Config:**
   - Command: `/alertbot`
   - Request URL: Your webhook endpoint
   - Short Description: "Check infrastructure status"

2. **Payload Received:**

```json
{
  "token": "verification_token",
  "team_id": "T1234567890",
  "team_domain": "company",
  "channel_id": "C1234567890",
  "channel_name": "monitoring",
  "user_id": "U1234567890",
  "user_name": "alice",
  "command": "/alertbot",
  "text": "status",
  "response_url": "https://hooks.slack.com/commands/T1234567890/B1234567890/XXXX",
  "trigger_id": "1234567890.1234567890.abcdef..."
}
```

#### Response Types

**Immediate (Synchronous):**
```json
{
  "response_type": "in_channel",
  "text": "✅ All systems operational",
  "blocks": [...]
}
```

**Ephemeral (Visible Only to User):**
```json
{
  "response_type": "ephemeral",
  "text": "This is a private response"
}
```

**Delayed (via response_url):**
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Processed!"}' \
  https://hooks.slack.com/commands/T1234567890/B1234567890/XXXX
```

#### trigger_id for Modals

Slash command `trigger_id` can open modals within 3-second window:

```python
@app.command("/incident")
def handle_incident_command(ack, body, client):
    ack()

    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "incident_modal",
            "title": {"type": "plain_text", "text": "Report Incident"},
            "blocks": [...]
        }
    )
```

#### InfraFabric Use Cases:
- `/infra status` - Infrastructure health check
- `/alert escalate <issue>` - Manual escalation
- `/oncall` - Get on-call engineer
- `/resolve <ticket_id>` - Mark incident resolved

---

### Interactive Components

#### Block Kit Elements

Modern UI framework for building interactive messages and modals.

**Button Elements:**
```json
{
  "type": "button",
  "text": {
    "type": "plain_text",
    "text": "Acknowledge Alert"
  },
  "action_id": "ack_alert",
  "value": "alert_123",
  "style": "danger"
}
```

**Select Menus:**
```json
{
  "type": "section",
  "block_id": "section_severity",
  "text": {
    "type": "mrkdwn",
    "text": "*Severity*"
  },
  "accessory": {
    "type": "static_select",
    "action_id": "select_severity",
    "options": [
      {
        "text": {"type": "plain_text", "text": "Critical"},
        "value": "critical"
      },
      {
        "text": {"type": "plain_text", "text": "Warning"},
        "value": "warning"
      }
    ]
  }
}
```

**Date/Time Pickers:**
```json
{
  "type": "section",
  "block_id": "date_picker",
  "text": {
    "type": "plain_text",
    "text": "Maintenance Window"
  },
  "accessory": {
    "type": "datepicker",
    "action_id": "maintenance_date",
    "initial_date": "2025-11-20"
  }
}
```

#### Modal Dialogs

Multi-step forms with validation.

```json
{
  "type": "modal",
  "callback_id": "create_incident",
  "title": {"type": "plain_text", "text": "Create Incident"},
  "submit": {"type": "plain_text", "text": "Create"},
  "blocks": [
    {
      "type": "input",
      "block_id": "incident_title",
      "label": {"type": "plain_text", "text": "Title"},
      "element": {
        "type": "plain_text_input",
        "action_id": "title_input",
        "placeholder": {"type": "plain_text", "text": "Database connection timeout"}
      }
    },
    {
      "type": "input",
      "block_id": "severity_input",
      "label": {"type": "plain_text", "text": "Severity"},
      "element": {
        "type": "static_select",
        "action_id": "severity_select",
        "options": [
          {"text": {"type": "plain_text", "text": "Critical"}, "value": "critical"},
          {"text": {"type": "plain_text", "text": "Major"}, "value": "major"}
        ]
      }
    }
  ]
}
```

#### Interactive Workflows

**Flow: Alert → Acknowledgment → Resolution**

1. Incoming webhook posts alert with "Acknowledge" button
2. User clicks button → triggers `block_actions` event
3. App updates message showing "Acknowledged by @user"
4. Show follow-up options: "Resolve" or "Escalate"
5. Final action creates incident ticket

---

## Pricing & Cost Analysis

### Plan Comparison

| Feature | Free | Pro | Business+ | Enterprise Grid |
|---------|------|-----|-----------|-----------------|
| **Price/User/Month** | $0 | $7.25-$8.75 | $15-$18 | Custom |
| **Message History** | 90 days | Unlimited | Unlimited | Unlimited |
| **File Storage** | 5GB | 300GB | Unlimited | Custom |
| **App Integrations** | 10 | Unlimited | Unlimited | Unlimited |
| **API Access** | Basic | Full | Full | Full |
| **SSO (SAML)** | ❌ | ❌ | ✅ | ✅ |
| **SCIM Provisioning** | ❌ | ❌ | ✅ | ✅ |
| **Audit Logs** | ❌ | ❌ | Limited | Full |
| **Data Residency** | ❌ | ❌ | ❌ | ✅ |
| **Compliance** | SOC 2 | SOC 2 | SOC 2, HIPAA | SOC 2, HIPAA, FedRAMP |

### Cost Calculation for InfraFabric

**Small Team (10 users):**
- Pro Plan: 10 × $8.75 = **$87.50/month**
- Business+: 10 × $18 = **$180/month**

**Enterprise (1000 users):**
- Pro Plan (3 user minimum): 1000 × $8.75 = **$8,750/month**
- Business+: 1000 × $18 = **$18,000/month**
- Enterprise Grid: Custom quote (typically $15-25k/month for 1000 users)

### Free Plan Limitations for InfraFabric

The Free plan is suitable for small monitoring teams with these constraints:
- Last 90 days of message history only
- 10 third-party app limit (covers basic integration)
- File history limited to 5GB
- **Sufficient for**: Startups, small infrastructure teams, proof-of-concepts

### Recommendation

- **Startups/POCs**: Start with **Free** or **Pro**
- **Growth (100+ users)**: **Pro** provides best cost-to-feature ratio
- **Enterprise (SSO/HIPAA required)**: **Business+** or **Enterprise Grid**

---

## Rate Limits

### Tier-Based Rate Limiting System

Slack uses a **tier-based approach** where different API methods have different limits.

#### Tier Categories

**Tier 1 (Most Restrictive):** 1 request per second
- `auth.test`
- `oauth.v2.access`

**Tier 2:** 20 requests per minute (≈0.33 req/sec)
- `conversations.members`
- `users.info`
- Most info methods

**Tier 3:** 2 requests per minute (≈0.03 req/sec)
- `conversations.list`
- `conversations.history` (NEW 2025 limits apply)
- `conversations.replies` (NEW 2025 limits apply)
- `files.list`
- `search.messages`

**Tier 4:** Method-specific (usually higher)
- `chat.postMessage`: 1 msg/sec per channel + workspace limits

#### Special Methods & Recent Changes (2025)

**conversations.history & conversations.replies - NEW LIMITS:**

**For Non-Marketplace Apps (Effective May 29, 2025):**
- 15 messages per request
- 1 request per minute
- Delayed enforcement: March 3, 2026 for existing apps

**For Marketplace Apps:**
- Unchanged from previous limits
- 50+ requests per minute (custom apps)

**For Internal/Custom Apps:**
- Higher limits available
- 50+ requests per minute for conversations.history

#### Workspace-Wide Limits

Beyond per-method limits, Slack enforces **workspace-wide** constraints:

- **chat.postMessage**: Several hundred messages per minute workspace-wide
- **Concurrent API calls**: ~100 concurrent connections recommended limit
- **Socket Mode connections**: 10 per app maximum

#### Burst Capacity

Slack allows brief bursts exceeding rate limits:
- Initial burst: ~10-20% above stated limit
- Duration: Few seconds only
- Beyond burst: 429 Too Many Requests response

#### Rate Limit Response

When limit exceeded, Slack returns:

```
HTTP 429 Too Many Requests
Retry-After: 30
```

**Retry-After values**: Indicates seconds until next attempt

#### Handling Rate Limits

**Automatic (via Bolt SDK):**
```python
from slack_bolt import App

app = App()  # Bolt handles 429s automatically with backoff
```

**Manual (with custom logic):**
```python
import time
import logging

def post_with_retry(client, channel, text, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.chat_postMessage(channel=channel, text=text)
        except Exception as e:
            if "429" in str(e):
                retry_after = int(e.response.headers.get('Retry-After', 10))
                logging.warning(f"Rate limited. Waiting {retry_after}s")
                time.sleep(retry_after)
            else:
                raise
    raise Exception("Max retries exceeded")
```

**Python SDK Helper:**
```python
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler

client = WebClient(
    token=token,
    retry_handlers=[RateLimitErrorRetryHandler(max_retry_count=10)]
)
```

---

## WebSocket Connections & Socket Mode

### Socket Mode Architecture

**Why Use Socket Mode:**
1. No public HTTP endpoint required
2. Development behind corporate firewall
3. Lower latency for event delivery
4. Bidirectional communication

### Connection Flow

1. **Initialize Connection:**
```python
from slack_bolt.adapter.socket_mode import SocketModeHandler

handler = SocketModeHandler(app, app_token)
handler.start()
```

2. **Slack Opens WebSocket to App:**
   - App calls `apps.connections.open`
   - Receives WebSocket URL
   - Connects and maintains persistent connection

3. **Event Delivery:**
   - Events pushed over WebSocket (not HTTP)
   - App processes and responds over same connection
   - No retry-after header backoff needed

### Connection Management

**Multiple Connections:**
- **Limit**: 10 concurrent WebSocket connections
- **Load Balancing**: Distribute events across connections
- **Auto-Reconnect**: Bolt framework handles disconnections

**Connection Lifecycle:**
- URL validity: ~12 hours (refreshes periodically)
- Auto-reconnect: Yes (built into Bolt)
- Keepalive pings: Handled by SDK

### Event Delivery Guarantee

- **At-least-once delivery**: Events may be delivered multiple times
- **Deduplication**: Use `event_id` to deduplicate
- **Ordering**: Within same connection, ordered delivery

### Limitations

- **Not Marketplace Compatible**: Socket Mode apps cannot be listed in Slack App Directory
- **Development Only**: Intended for internal or deployed-behind-firewall apps
- **Requires App Token**: Different from bot token (`xapp-...`)

---

## SDK Availability & Implementation

### Official SDKs

| SDK | Language | Package | Latest Update | Stars |
|-----|----------|---------|----------------|-------|
| **Bolt Python** | Python 3.7+ | `slack_bolt` | Nov 11, 2025 | 1,241 |
| **Bolt JavaScript** | Node.js 12+ | `@slack/bolt` | Nov 10, 2025 | 2,866 |
| **Bolt Java** | Java 8+ | `com.slack.api:slack-api-client` | Nov 2025 | Active |
| **Python SDK** | Python 3.7+ | `slack-sdk` | Nov 2025 | 1,800+ |
| **Node SDK** | Node.js 12+ | `@slack/web-api` | Nov 2025 | 2,200+ |
| **Java SDK** | Java 8+ | `slack-api-client` | Nov 2025 | Active |

### Installation Examples

**Python Bolt:**
```bash
pip install slack_bolt
```

**JavaScript Bolt:**
```bash
npm install @slack/bolt
```

**Java Maven:**
```xml
<dependency>
    <groupId>com.slack.api</groupId>
    <artifactId>slack-api-client</artifactId>
    <version>LATEST</version>
</dependency>
```

### SDK Features Comparison

**All Bolt SDKs Include:**
- ✅ HTTP rate limit handling
- ✅ Event listener registration
- ✅ Socket Mode support
- ✅ OAuth flow helpers
- ✅ Token rotation
- ✅ Error handling & retries
- ✅ Async support (JS/Python)
- ✅ Middleware pipeline
- ✅ Type safety (TS/JS, type hints Python/Java)

---

## Enterprise Features

### Enterprise Grid

**Exclusive Features:**
- **Multi-workspace management** from single dashboard
- **Org-wide security** and compliance policies
- **Advanced provisioning** with SCIM API
- **Unlimited workspaces** for org
- **Custom data residency** options (specific regions)
- **Advanced audit logs** with API access

### SCIM Provisioning

**System for Cross-domain Identity Management**

**Availability:** Business+ and Enterprise Grid only

**What SCIM Does:**
- Auto-provision users from identity provider
- Auto-deprovision on termination
- Keep user attributes synchronized
- Just-In-Time (JIT) provisioning option

**Identity Providers Supported:**
- Okta
- Azure AD
- Ping Identity
- Google Workspace (via SAML + manual sync)
- Generic SCIM v2.0 providers

**SCIM API Endpoints:**
```
POST /scim/v2/Users              - Create user
GET  /scim/v2/Users              - List users
GET  /scim/v2/Users/{id}         - Get user
PUT  /scim/v2/Users/{id}         - Update user
PATCH /scim/v2/Users/{id}        - Partial update
DELETE /scim/v2/Users/{id}       - Delete user
```

**Example SCIM User Creation:**
```json
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
  "userName": "alice@company.com",
  "name": {
    "givenName": "Alice",
    "familyName": "Engineer"
  },
  "emails": [{
    "value": "alice@company.com",
    "primary": true
  }],
  "active": true
}
```

### SSO (Single Sign-On) with SAML

**Availability:** Business+ and Enterprise Grid

**Required SAML Attributes:**
- `NameID` - User identifier
- `Email` - User email address
- `Username` (optional) - For SCIM pre-provisioning

**SAML Configuration:**
```
Entity ID: https://slack.com
Assertion Consumer Service (ACS): https://slack.com/saml/acs/WORKSPACE_ID
Single Logout URL: https://slack.com/saml/acs/WORKSPACE_ID
```

**Benefits for InfraFabric:**
- Centralized user management
- Automatic team member sync
- Simplified onboarding/offboarding
- Compliance audit trail

### Audit Logs API

**Availability:** Enterprise plans only

**What It Tracks:**
- User login/logout
- App installations
- Token generation
- Channel creation/deletion
- File uploads
- Permission changes
- Message details (Enterprise+)

**API Methods:**
```
POST /api/audit.audit.logs.get

Parameters:
- limit: (1-9999, default 100)
- cursor: pagination token
- latest: end timestamp
- oldest: start timestamp
- action: filter by action type
```

**Example Response:**
```json
{
  "ok": true,
  "logs": [
    {
      "id": "xxx",
      "date_create": 1234567890,
      "user_id": "U1234567890",
      "action": "user_login",
      "entity": "user",
      "context": {
        "ua": "Mozilla/5.0...",
        "ip_address": "192.0.2.1"
      }
    }
  ],
  "pagination": {
    "total_count": 1000,
    "cursor": "dXNlcjpVMjU="
  }
}
```

**InfraFabric Use Case:**
- Track who accessed incident channels
- Audit alert rule changes
- Compliance reports for infrastructure access
- Track on-call schedule modifications

### Data Residency & Compliance

**Enterprise Grid Only:**
- **EU Data Residency**: Store all data in EU
- **APAC Options**: Asia-Pacific data centers
- **FedRAMP Moderate**: U.S. government compliance
- **HIPAA**: Healthcare compliance available

**Certifications:**
- SOC 2 Type II
- ISO 27001
- ISO 27018
- GDPR ready
- CCPA compliant

---

## Block Kit UI Framework

### Message Structure

**Header Block:**
```json
{
  "type": "header",
  "text": {
    "type": "plain_text",
    "text": "🚨 Critical Alert",
    "emoji": true
  }
}
```

**Section Block (Text + Fields):**
```json
{
  "type": "section",
  "text": {
    "type": "mrkdwn",
    "text": "*Service Down:* api-prod-01\n*Duration:* 12 minutes"
  },
  "fields": [
    {
      "type": "mrkdwn",
      "text": "*Status*\n🔴 Down"
    },
    {
      "type": "mrkdwn",
      "text": "*Impact*\n487 Users"
    }
  ]
}
```

**Image Block:**
```json
{
  "type": "image",
  "image_url": "https://example.com/metrics.png",
  "alt_text": "CPU Usage Graph"
}
```

**Actions Block:**
```json
{
  "type": "actions",
  "block_id": "alert_actions",
  "elements": [
    {
      "type": "button",
      "text": {"type": "plain_text", "text": "Acknowledge"},
      "action_id": "alert_ack",
      "value": "alert_id_123"
    },
    {
      "type": "button",
      "text": {"type": "plain_text", "text": "Escalate"},
      "action_id": "alert_escalate",
      "style": "danger"
    }
  ]
}
```

### Accessibility

**Best Practices:**
- Use `emoji: true` for emoji in plain text
- Provide alt text for all images
- Use semantic markup in mrkdwn
- Test with screen readers
- Maintain sufficient color contrast

### Mobile Rendering

**Responsive Design:**
- Blocks stack vertically on mobile
- Button layout wraps on narrow screens
- Images scale to screen width
- Modals use full screen on mobile

**Test on Mobile:**
- Slack mobile apps (iOS/Android)
- Desktop Slack browser version (responsive)
- Block Kit Builder preview (web)

---

## Implementation Estimate for InfraFabric

### Development Hours by Component

| Component | Estimate | Dependencies |
|-----------|----------|--------------|
| **OAuth Setup & Token Management** | 4-6 hours | None |
| **Incoming Webhook Integration** | 2-3 hours | OAuth |
| **Events API Implementation** | 6-8 hours | OAuth, Webhook base |
| **Slash Commands** | 4-6 hours | OAuth |
| **Interactive Components (Buttons/Modals)** | 8-10 hours | Slash commands, Events |
| **Bot Development (Bolt)** | 5-7 hours | Core components above |
| **Error Handling & Retries** | 4-6 hours | All components |
| **Monitoring & Logging** | 3-5 hours | All components |
| **Testing & QA** | 8-12 hours | All components |
| **Documentation & Examples** | 4-6 hours | All components |
| **Deployment & Production Setup** | 3-5 hours | All components |

**Total Estimated Range: 51-74 hours**

**Recommended Phasing:**

**Phase 1 (MVP - 2 weeks):**
- OAuth setup
- Incoming webhooks for alerts
- Basic slash commands
- ~14-20 hours

**Phase 2 (Enhanced (2 weeks):**
- Events API
- Interactive buttons
- Modals for incident creation
- ~16-22 hours

**Phase 3 (Advanced - 2 weeks):**
- Full bot implementation
- Monitoring & metrics
- Advanced workflows
- ~21-32 hours

---

## Integration Implementation

### Slack App Creation Checklist

1. **Go to** https://api.slack.com/apps
2. **Create New App** → From Manifest
3. **Configure Manifest:**

```yaml
_metadata:
  major_version: 1
  minor_version: 1
display_information:
  name: InfraFabric Alert Bot
  description: Infrastructure monitoring and incident coordination
  background_color: "#000000"
features:
  bot_user:
    display_name: InfraFabric
    always_online: false
oauth_config:
  scopes:
    bot:
      - chat:write
      - commands
      - app_mentions:read
      - channels:read
      - files:write
      - reactions:read
      - users:read
settings:
  event_subscriptions:
    bot_events:
      - app_mention
      - message
      - reaction_added
  interactivity:
    is_enabled: true
  org_deploy_enabled: false
  socket_mode_enabled: false
  token_rotation_enabled: false
```

4. **Install App to Workspace**
5. **Configure Event Subscriptions:**
   - Request URL: `https://your-domain.com/slack/events`
   - Events: `app_mention`, `message`, `reaction_added`
6. **Configure Slash Commands:**
   - `/infra` → `https://your-domain.com/slack/commands/infra`
7. **Generate Tokens:**
   - Bot User OAuth Token (xoxb-...)
   - App-level Token for Socket Mode (xapp-...)

### Error Codes & Handling

**Common HTTP Status Codes:**

| Code | Meaning | Retry? |
|------|---------|--------|
| 200 | Success | No |
| 400 | Invalid request | No |
| 401 | Unauthorized (bad token) | No |
| 429 | Rate limited | Yes (with Retry-After) |
| 500 | Server error | Yes (exponential backoff) |
| 503 | Service unavailable | Yes |

**Error Response Example:**
```json
{
  "ok": false,
  "error": "invalid_auth",
  "error_description": "Invalid token"
}
```

### Pagination

**Cursor-Based Pagination:**

```python
# Get first page
response = client.conversations_list(limit=50)
channels = response['channels']
cursor = response.get('response_metadata', {}).get('next_cursor')

# Get next page if cursor exists
if cursor:
    response = client.conversations_list(limit=50, cursor=cursor)
```

**Async Iteration (Node.js):**

```javascript
for await (const page of client.paginate('conversations.list', {limit: 50})) {
  console.log(page.channels);
}
```

---

## API Method Reference for InfraFabric

### Posting Alerts

**Simple Alert:**
```python
client.chat_postMessage(
    channel="#alerts",
    text="Alert: High CPU usage on db-prod"
)
```

**Formatted Alert with Blocks:**
```python
client.chat_postMessage(
    channel="#alerts",
    blocks=[
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "🚨 Alert"}
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*Server*\ndb-prod"},
                {"type": "mrkdwn", "text": "*CPU*\n85%"},
                {"type": "mrkdwn", "text": "*Memory*\n92%"},
                {"type": "mrkdwn", "text": "*Time*\n14:32 UTC"}
            ]
        }
    ]
)
```

### Thread Replies

```python
client.chat_postMessage(
    channel="#incidents",
    thread_ts="1234567890.123456",
    text="Update: Issue identified in database connection pool"
)
```

### File Upload for Logs

```python
client.files_upload(
    channels=["#incidents"],
    file="/var/log/app.log",
    title="Application error log",
    initial_comment="Relevant log file from incident"
)
```

### List Channels & Users

```python
# List channels
channels = client.conversations_list()['channels']

# Get user info
user = client.users_info(user="U1234567890")['user']

# Get member of channel
members = client.conversations_members(channel="C1234567890")['members']
```

---

## Risk Assessment & Mitigation

### Integration Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| **Token Compromise** | Medium | High | Vault storage, rotation, audit logs |
| **Rate Limit Blocking** | Medium | Medium | Automatic backoff, Bolt SDK |
| **Event Loss** | Low | High | Deduplication via event_id, logging |
| **Slack Outage** | Low | Medium | Graceful degradation, fallback channels |
| **Cost Escalation** | Low | Medium | Monitor user growth, plan reviews |

### Best Practices

1. **Token Security:**
   - Store in environment variables or secret management
   - Rotate tokens annually minimum
   - Revoke unused tokens immediately
   - Monitor for unusual activity via audit logs

2. **Error Handling:**
   - Implement retry logic with exponential backoff
   - Log all API errors for debugging
   - Alert on repeated failures
   - Have fallback notification channels

3. **Performance:**
   - Use caching where possible
   - Batch API calls when appropriate
   - Monitor rate limit headers
   - Implement circuit breakers for dependent services

4. **Testing:**
   - Use Socket Mode for development
   - Test with actual rate limits
   - Load test slack message posting
   - Verify OAuth flow end-to-end

---

## IF.TTT Citations

### Pass 1-2: Signal Capture (API.slack.com & docs.slack.dev)

1. **Slack API Documentation Portal**
   - URL: https://docs.slack.dev/
   - Retrieved: 2025-11-14
   - Content: Complete API reference, SDKs, tutorials

2. **Slack Web API Reference**
   - URL: https://api.slack.com/methods
   - Retrieved: 2025-11-14
   - Content: All Web API methods, parameters, examples

3. **Slack Events API**
   - URL: https://docs.slack.dev/apis/events-api/
   - Retrieved: 2025-11-14
   - Content: Event types, subscriptions, challenge verification

4. **Slack Bolt Frameworks**
   - Python: https://github.com/slackapi/bolt-python
   - JavaScript: https://github.com/slackapi/bolt-js
   - Retrieved: 2025-11-14
   - Status: Active maintenance (Nov 2025)

### Pass 3-4: Rigor & Cross-Domain

5. **Rate Limits Documentation**
   - URL: https://docs.slack.dev/apis/web-api/rate-limits/
   - Retrieved: 2025-11-14
   - Key Finding: 2025 rate limit changes for conversations.history

6. **OAuth 2.0 Installation Flow**
   - URL: https://docs.slack.dev/authentication/installing-with-oauth/
   - Retrieved: 2025-11-14
   - Content: Complete OAuth implementation guide

7. **Socket Mode Development**
   - URL: https://docs.slack.dev/apis/events-api/using-socket-mode/
   - Retrieved: 2025-11-14
   - Content: WebSocket implementation, connection limits

### Pass 5-6: Framework Mapping (InfraFabric Use Cases)

8. **Slack Pricing Plans**
   - URL: https://slack.com/pricing
   - Retrieved: 2025-11-14
   - Analysis: Tier comparison for infrastructure monitoring teams

9. **Enterprise Features (SCIM, SSO, Audit)**
   - URL: https://slack.com/help/articles/360000394286-Audit-logs-on-Enterprise-Grid
   - Retrieved: 2025-11-14
   - Content: Enterprise Grid capabilities for compliance

10. **Block Kit UI Framework**
    - URL: https://api.slack.com/block-kit
    - Retrieved: 2025-11-14
    - Content: Message layouts for alert visualization

### Pass 7-8: Meta-Validation & Deployment Planning

11. **Slack App Manifest Specification**
    - URL: https://api.slack.com/reference/manifests/latest
    - Retrieved: 2025-11-14
    - Content: App configuration and deployment

12. **Error Handling & Retry Strategies**
    - Medium Article: https://medium.com/slack-developer-blog/handling-rate-limits-with-slacks-apis-f6f8a63bdbdc
    - Retrieved: 2025-11-14
    - Content: Production-grade error handling patterns

13. **Python SDK Documentation**
    - URL: https://tools.slack.dev/python-slack-sdk/
    - Retrieved: 2025-11-14
    - Content: SDK API, examples, best practices

14. **Node.js Bolt Documentation**
    - URL: https://tools.slack.dev/bolt-js/
    - Retrieved: 2025-11-14
    - Content: JavaScript framework implementation

---

## Recommendations for InfraFabric

### Immediate Actions (Phase 1)

1. **Create Slack App** with manifest (2 hours)
2. **Set up OAuth flow** for workspace installation (4 hours)
3. **Implement incoming webhook** for alert distribution (3 hours)
4. **Create 2-3 slash commands** for status checks (6 hours)

**Result:** Basic alert notification and command-based status checks

### Medium-term (Phase 2)

1. **Implement Events API** for interactive incident creation (8 hours)
2. **Add modal dialogs** for incident workflows (6 hours)
3. **Build dashboard command** with rich block formatting (5 hours)

**Result:** Full incident management capability within Slack

### Long-term (Phase 3)

1. **Deploy Bolt bot** for advanced automation (7 hours)
2. **Implement SCIM integration** for user sync (8 hours)
3. **Add audit logging** for compliance (5 hours)

**Result:** Enterprise-ready Slack integration with SSO/SCIM for large deployments

### Technology Stack Recommendation

- **Language**: Python (mature Bolt SDK, 1,241 stars, well-maintained)
- **Framework**: slack_bolt for production deployment
- **Development**: Socket Mode for rapid iteration
- **Hosting**: Containerized Bolt app (Docker/Kubernetes)
- **Token Storage**: HashiCorp Vault or AWS Secrets Manager
- **Monitoring**: Prometheus metrics + Slack alerts (dogfooding!)

### Deployment Topology

```
┌─────────────────┐
│  InfraFabric    │
│  Monitoring     │
└────────┬────────┘
         │
         ├─→ [Webhook] → Slack #alerts
         │
         ├─→ [REST API] → Slack Web API
         │   (chat.postMessage, files.upload)
         │
         └─→ [Socket Mode] → Slack Events
             (slash commands, interactive buttons)

┌────────────────────────────────┐
│  Slack Workspace               │
├────────────────────────────────┤
│  #alerts         (webhook msgs)│
│  #incidents      (event-driven)│
│  #oncall         (scheduled)   │
│  /infra command  (status check)│
│  InfraFabric bot (event handler)│
└────────────────────────────────┘
```

---

## Conclusion

Slack's comprehensive API ecosystem provides an excellent platform for InfraFabric's team collaboration and alerting needs. The platform offers:

✅ **Accessibility**: Works across all pricing tiers, with Free plan sufficient for small teams
✅ **Flexibility**: Multiple integration patterns (webhooks, Events API, bot framework)
✅ **Scalability**: Enterprise Grid supports SCIM/SSO for large organizations
✅ **Developer Experience**: Excellent SDKs, documentation, and Bolt framework
✅ **Reliability**: Built-in rate limit handling, retry logic, audit logs
✅ **Security**: OAuth 2.0, token management, Enterprise Grid compliance features

**Recommended path**: Start with incoming webhooks and slash commands (4-6 week MVP), then expand to full bot implementation for advanced workflows and automation.

---

**Document Version**: 1.0
**Last Updated**: 2025-11-14
**Next Review**: 2025-12-14
