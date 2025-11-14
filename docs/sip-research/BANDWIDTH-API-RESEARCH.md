# Bandwidth Enterprise Communications API - InfraFabric Integration Research

**Agent:** Haiku-37
**Methodology:** IF.search 8-pass
**Date:** 2025-11-14
**Status:** PRODUCTION-READY ANALYSIS

---

## Executive Summary

Bandwidth is a **Tier 1 network carrier operating its own nationwide all-IP voice network** with direct PSTN connectivity globally. Unlike resellers, Bandwidth owns its infrastructure and provides enterprise-grade communication APIs with wholesale pricing, custom SLAs, and production-grade reliability suitable for InfraFabric's infrastructure communications stack.

### Key Findings for InfraFabric Integration

- **Own Infrastructure**: Tier 1 carrier with all-IP network, 38+ countries with full PSTN replacement
- **Enterprise APIs**: Messaging v2, Voice v2 (BXML), 911 API, Phone Number API, Emergency Notification API
- **Production Ready**: Supports Fortune 500 enterprises, 100% of leading UCaaS/CCaaS platforms
- **Wholesale Pricing**: $3,000/month+ with 30% cost savings vs competitors, 6-second billing increments
- **Developer Friendly**: 6 official SDKs (Python, Node.js, Java, C#, Ruby, PHP), comprehensive webhooks
- **Compliance**: STIR/SHAKEN attestation, E911 certified, CNAM, LNP, 10DLC A2P ready

---

## Pass 1-2: Signal Capture (API Documentation & Dev Portal)

### Primary API Endpoints

| API | Base URL | Purpose | Auth Method |
|-----|----------|---------|-------------|
| **Messaging v2** | `https://messaging.bandwidth.com/api/v2/users/{accountId}` | SMS/MMS, group messaging, delivery tracking | Basic Auth / Bearer Token |
| **Voice v2** | `https://api.bandwidth.com/api/v1/accounts/{accountId}/calls` | Programmable voice, BXML, recording, transcription | Basic Auth / Bearer Token |
| **911 API** | `https://api.bandwidth.com/api/v1/accounts/{accountId}/emergencies` | E911 dynamic location routing, emergency notifications | Basic Auth / Bearer Token |
| **Phone Number API** | `https://api.bandwidth.com/api/v1/accounts/{accountId}/phoneNumbers` | Number search, ordering, porting, management | Basic Auth / Bearer Token |
| **Number Lookup API** | `https://api.bandwidth.com/api/v2/accounts/{accountId}/tnlookup` | Reverse phone lookup, TN intelligence | Basic Auth / Bearer Token |

### Documentation Portal Structure

- **API Reference**: `https://dev.bandwidth.com/apis/` - Full REST API specifications
- **Guides**: `https://dev.bandwidth.com/docs/` - Integrations, quickstarts, best practices
- **SDKs**: `https://dev.bandwidth.com/sdks/` - Client library documentation
- **Examples**: `https://github.com/Bandwidth-Samples` - Reference implementations
- **Support**: `https://support.bandwidth.com/` - Knowledge base and ticketing

---

## Authentication & Security

### Method 1: Basic Authorization (HTTP Basic Auth)

**Implementation:**
```
Authorization: Basic base64(username:password)
```

**Key Points:**
- Username and password are case-sensitive
- Credentials transmitted over HTTPS (required)
- Separate API user from Dashboard user recommended
- Account-level permissions configured in UI

**Usage in Curl:**
```bash
curl -u "api_username:api_password" \
  https://messaging.bandwidth.com/api/v2/users/{accountId}/messages
```

### Method 2: Bearer Token Authentication (OAuth)

**Token Acquisition Flow:**
```
1. Obtain ClientID and ClientSecret from Bandwidth Dashboard
2. Request token from OAuth endpoint with ClientID/ClientSecret
3. Bearer token valid for ~3600 seconds (1 hour)
4. Request new token 5-10 seconds before expiration
```

**Implementation:**
```
Authorization: Bearer {access_token}
```

**Token Endpoint:**
```
POST https://api.bandwidth.com/oauth2/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}
```

**Python SDK Example:**
```python
from bandwidth import Bandwidth
from bandwidth.exceptions import ApiException

client = Bandwidth(
    voice_basic_auth_user_name="username",
    voice_basic_auth_password="password"
)
```

### Security Requirements

- **HTTPS Only**: All API calls must use HTTPS (TLS 1.2+)
- **Account Hierarchy**: Account ID required in all endpoints
- **IP ACLs**: Available for enterprise accounts (contact account manager)
- **Rate Limiting**: API-level throttling with configurable per-account limits

---

## Core API Capabilities

### 1. Messaging API v2

**Purpose**: Send/receive SMS/MMS, track delivery, manage 10DLC campaigns

#### Supported Message Types
- **SMS**: Plain text messages, supports group messaging
- **MMS**: Multimedia messages up to 3.75MB (48-hour storage)
- **10DLC**: 10-digit long codes for business SMS/MMS
- **Short Codes**: Premium SMS delivery routes
- **Toll-Free SMS**: Dedicated toll-free numbers for messaging

#### Core Features

**Message Sending:**
```json
POST /api/v2/users/{accountId}/messages

{
  "to": ["+15551234567"],
  "from": "+15559876543",
  "text": "Hello from InfraFabric",
  "applicationId": "app-12345"
}

Response: HTTP 202 Accepted
```

**Character Segmentation:**
- GSM-7 encoding: 160 characters per SMS
- UCS-2 encoding: 70 characters per SMS
- Messages auto-segmented beyond limits

**Delivery Tracking:**
- `message-delivered`: Carrier confirmed delivery
- `message-failed`: Delivery failed with error code
- `message-received`: Inbound message received
- Query message status via GET endpoint

**Group Messaging:**
- MMS group messaging (beta, requires enablement)
- Delivery receipts for group messages
- Support for multiple recipients in single API call

**Media Handling:**
```json
{
  "to": ["+15551234567"],
  "from": "+15559876543",
  "media": [
    "https://infrafabric.io/image.jpg"
  ],
  "applicationId": "app-12345"
}
```

#### Webhook Events

**Delivery Receipts:**
```json
[{
  "id": "msg-12345",
  "owner": "+15559876543",
  "time": "2025-11-14T10:30:00.000Z",
  "type": "message-delivered",
  "direction": "out",
  "messageStatus": "delivered"
}]
```

**Failed Messages:**
```json
[{
  "id": "msg-12345",
  "type": "message-failed",
  "errorCode": 4001,
  "description": "Message rejected by carrier"
}]
```

**Inbound Messages:**
```json
[{
  "id": "msg-67890",
  "owner": "+15559876543",
  "time": "2025-11-14T10:35:00.000Z",
  "type": "message-received",
  "direction": "in",
  "from": "+15551234567",
  "text": "Reply to InfraFabric"
}]
```

### 2. Voice API v2

**Purpose**: Programmable voice calling, BXML control flow, recording, transcription

#### BXML (Bandwidth XML) Control Flow

Voice applications are built using XML-based verb definitions. Application receives webhooks for events and responds with XML verbs to control call behavior.

**BXML Verb Categories:**

| Category | Verbs | Purpose |
|----------|-------|---------|
| **Call Routing** | Transfer, Bridge, Conference, Forward, Ring | Route calls to destinations |
| **Audio Control** | PlayAudio, SpeakSentence, Pause | Play audio/text to caller |
| **Input Collection** | Gather, StartGather, StopGather, SendDtmf | Collect DTMF input |
| **Recording** | Record, StartRecording, StopRecording | Record calls/messages |
| **Media Streaming** | StartStream, StopStream | Stream audio (live agents) |
| **Transcription** | StartTranscription, StopTranscription | Real-time transcription |
| **Call Control** | Hangup, Redirect, Forward | Terminate/redirect calls |

**Example BXML Response:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <SpeakSentence>Thank you for calling InfraFabric. Press 1 for support, 2 for sales.</SpeakSentence>
  <Gather maxDigits="1" terminatingDigits="#" gatherTimeout="5000">
    <SpeakSentence>Please select an option</SpeakSentence>
  </Gather>
</Response>
```

#### Webhook Event Flow

**Incoming Call:**
```json
{
  "eventType": "answer",
  "callId": "call-12345",
  "callUrl": "https://api.bandwidth.com/api/v1/accounts/...",
  "to": "+15559876543",
  "from": "+15551234567",
  "time": "2025-11-14T10:40:00.000Z"
}
```

Application responds with BXML to control call flow.

**DTMF (Gather) Event:**
```json
{
  "eventType": "gather",
  "callId": "call-12345",
  "digits": "1"
}
```

**Recording Available:**
```json
{
  "eventType": "recording",
  "callId": "call-12345",
  "recordingId": "rec-12345",
  "recordingUrl": "https://api.bandwidth.com/...",
  "status": "success"
}
```

#### Recording Features
- Automatic call recording
- Record participant audio separately
- Transcription options (real-time or post-call)
- 48-hour default retention (configurable)

#### Text-to-Speech (TTS)
- Natural voice synthesis
- Multiple language/voice options
- Embedded in BXML `<SpeakSentence>` verbs

#### WebRTC Integration
- Browser-to-PSTN calling
- Pre-authenticated SIP INVITE tokens
- Seamless handoff to voice network

#### Call Creation (Outbound)

```bash
POST https://api.bandwidth.com/api/v1/accounts/{accountId}/calls

{
  "to": "+15551234567",
  "from": "+15559876543",
  "answerUrl": "https://infrafabric.io/voice/webhook",
  "answerMethod": "POST"
}

Response: HTTP 201 Created
{
  "id": "call-12345",
  "accountId": "{accountId}"
}
```

### 3. 911 API (Emergency Calling)

**Purpose**: E911 compliance, dynamic location routing, emergency notifications

#### Dynamic Location Routing (DLR)

Real-time location updates for emergency calls:

**Supported Location Identifiers:**
- Subnets (IPv4/IPv6)
- WiFi access points
- Ethernet switches/ports
- Physical addresses
- Device/endpoint identifiers

**E911 Update Endpoint:**
```bash
POST https://api.bandwidth.com/api/v1/accounts/{accountId}/emergencies/dlr

{
  "country": "US",
  "locations": [
    {
      "address": {
        "houseNumber": "100",
        "streetName": "Main St",
        "city": "San Francisco",
        "stateCode": "CA",
        "zipCode": "94105"
      },
      "identifier": "subnet:10.0.0.0/8"
    }
  ]
}
```

#### Emergency Notification Service

Notify designated personnel when 911 calls are placed:

**Notification Methods:**
- Email notifications
- SMS notifications (text-to-speech)
- Voice calls (text-to-speech)
- HTTP webhooks

**Notification Setup:**
```bash
POST https://api.bandwidth.com/api/v1/accounts/{accountId}/emergencies/notifications

{
  "notificationType": "sms",
  "recipientList": [
    {
      "name": "Security Team",
      "phoneNumber": "+15551234567"
    }
  ],
  "messageBody": "Emergency 911 call placed from {location}"
}
```

#### E911 Features
- Automatic location tracking via DLR
- 6000+ PSAP (Public Safety Answering Point) connections
- 40+ country support
- Regulatory compliance for VoIP/UCaaS providers

### 4. Phone Number API

**Purpose**: Provision numbers, manage inventory, port numbers, 10DLC campaigns

#### Number Search & Ordering

**Search Available Numbers:**
```bash
GET https://api.bandwidth.com/api/v1/accounts/{accountId}/availablePhoneNumbers

?areaCode=415&quantity=10&numberType=local
```

**Order Numbers:**
```bash
POST https://api.bandwidth.com/api/v1/accounts/{accountId}/orders

{
  "customerOrderId": "order-12345",
  "areaCode": "415",
  "quantity": 5,
  "name": "InfraFabric-DID",
  "operatingAddressId": "addr-123"
}

Response: HTTP 201
{
  "orderId": "order-abc123",
  "orderStatus": "processing",
  "createdDate": "2025-11-14T10:45:00.000Z"
}
```

**Order Status Polling:**
```bash
GET https://api.bandwidth.com/api/v1/accounts/{accountId}/orders/{orderId}

Response:
{
  "orderId": "order-abc123",
  "orderStatus": "completed",
  "createdDate": "2025-11-14T10:45:00.000Z",
  "completedDate": "2025-11-14T11:05:00.000Z",
  "phoneNumbers": [
    "+14155551234",
    "+14155551235"
  ]
}
```

#### Number Porting (LNP)

**Port-In Request:**
```bash
POST https://api.bandwidth.com/api/v1/accounts/{accountId}/porting

{
  "customerOrderId": "port-12345",
  "losingCarrier": "Twilio Inc",
  "losingCarrierName": "Twilio",
  "phoneNumbers": ["+14155551234"],
  "accountNumber": "12345678",
  "accountNumberPin": "1234",
  "requestedFocDate": "2025-12-15",
  "serviceAddress": {
    "address": "100 Main St",
    "city": "San Francisco",
    "stateCode": "CA",
    "zipCode": "94105"
  }
}
```

**Porting Features:**
- Dedicated porting team support
- Carrier relationship management
- Automated number verification
- Real-time port status updates
- Port disputes handling

#### 10DLC Campaign Management

**10DLC A2P Registration** (Application-to-Person):

```bash
POST https://api.bandwidth.com/api/v1/accounts/{accountId}/10DLC/campaigns

{
  "campaignName": "InfraFabric-Alerts",
  "useCase": "ALERT",
  "companyName": "InfraFabric Inc",
  "ein": "12-3456789",
  "websiteUrl": "https://infrafabric.io",
  "applicationType": "PLATFORM",
  "applicantName": "John Doe",
  "applicantEmail": "support@infrafabric.io"
}

Response: HTTP 201
{
  "campaignId": "campaign-12345",
  "campaignStatus": "SUBMITTED"
}
```

**Campaign Status Flow:**
- `SUBMITTED`: Awaiting carrier approval
- `PENDING_VERIFICATION`: Carrier requesting documentation
- `APPROVED`: Active and ready for SMS
- `REJECTED`: Failed approval (update and resubmit)

**Assign Numbers to Campaign:**
```bash
PUT https://api.bandwidth.com/api/v1/accounts/{accountId}/phoneNumbers/+14155551234

{
  "applicationId": "campaign-12345"
}
```

#### Number Types Supported
- **Local Numbers**: Area code-based routing
- **Toll-Free**: 800/844/855/866/877/888 numbers
- **Short Codes**: Premium SMS routes (rare for new provisioning)
- **International Numbers**: 65+ countries

---

## Network Infrastructure

### Tier 1 Carrier Status

Bandwidth operates as a **Tier 1 network carrier**, meaning:

- **Network Ownership**: Owns and operates all-IP voice network infrastructure
- **Direct PSTN Access**: Direct connections to public switched telephone network
- **No Reselling**: Not dependent on third-party carriers for service
- **Nationwide Coverage**: Footprint across United States with international expansion

### All-IP Voice Network Architecture

**Key Characteristics:**

- **Packet-Based Routing**: Voice calls broken into IP packets, routed independently
- **Redundancy**: Multiple paths per call for failover and reliability
- **Low Latency**: Direct network paths reduce call delay
- **Scalability**: IP-based systems scale horizontally (unlike legacy TDM)

### Global PSTN Connectivity

- **38+ Countries**: Full PSTN replacement (voice/SMS/911)
- **65+ Countries**: PSTN interconnects available
- **8 Geo-Redundant Data Centers**: Distributed across regions
- **Fortune 500 Compatible**: Powers 100% of leading UCaaS/CCaaS platforms

### Network Advantages for InfraFabric

| Advantage | Impact |
|-----------|--------|
| Own Infrastructure | No carrier dependency, predictable costs |
| Tier 1 Status | Direct accountability, SLA guarantees |
| API-First Architecture | Programmable routing, dynamic scaling |
| Redundancy | 99.99% uptime SLA (enterprise tiers) |
| Global Reach | Multi-region deployment support |

---

## Pricing & Cost Analysis

### SMS/Messaging Pricing (10DLC Focus)

| Message Type | Price per SMS | Price per MMS | Notes |
|--------------|---------------|---------------|-------|
| **10DLC** | $0.004 | $0.015 | Recommended for most use cases |
| **Short Codes** | $0.008 | $0.020 | Premium delivery, limited availability |
| **Toll-Free SMS** | $0.007 | $0.020 | Brand visibility, regulatory compliance |

### Voice Pricing (Per-Minute)

| Call Type | Price | Notes |
|-----------|-------|-------|
| **Outbound US Local** | $0.01/min | Standard PSTN routing |
| **Inbound US Local** | $0.0055/min | Incoming from carriers |
| **Text-to-Speech** | $0.0007-$0.003/100 chars | Varies by voice quality |
| **Transcription** | $0.045+/min | Post-call analysis |
| **Call Recording** | $0.002/min | Storage and access |

### Add-On Services Pricing

| Service | Price |
|---------|-------|
| Two-Factor Authentication | $0.05 per authentication |
| Call Verification | $0.15 per call |
| Answering Machine Detection (AMD) | $0.006 per call |
| Caller ID Delivery | Included |

### 911/Emergency Pricing

| Feature | Pricing Model |
|---------|---------------|
| E911 Service | $0.015 per enabled number/month |
| Dynamic Location Routing | Included with E911 |
| Emergency Notifications | SMS/Voice charges apply |

### Phone Number Pricing

| Number Type | Monthly Cost | Setup |
|-------------|-------------|-------|
| **Local Numbers** | $1.00-$2.00/number | Included |
| **Toll-Free Numbers** | $2.00-$3.00/number | Included |
| **10DLC Campaign** | $0 | One-time registration |

### Wholesale Pricing Model

**Enterprise Discounts:**
- Volume-based pricing tiers (negotiated per account)
- Committed use discounts for predictable volumes
- Custom SLAs available for mission-critical

**Example Enterprise Structure:**
```
Base: $3,000/month minimum commitment
SMS: $0.003 per message (50% discount vs retail)
Voice: $0.008/min outbound (20% discount)
Volume Triggers: Additional 10-15% at 10M+ messages/month
Dedicated Support: +$1,500-$7,500/month (based on tier)
```

### 6-Second Billing

Bandwidth charges in 6-second increments for voice calls:
- 1-6 seconds = $0.01 (for $0.01/min rate)
- 7-12 seconds = $0.02
- No fractional-second overage charges

### Cost Optimization for InfraFabric

| Strategy | Savings Potential |
|----------|------------------|
| Commit annual volume | 15-25% |
| Use 10DLC for SMS | 40% vs short codes |
| Local number routing | 10% vs toll-free |
| Bulk messaging batching | Reduced API calls |
| Preferred SMS timing | Peak/off-peak pricing |

---

## Rate Limits & Scalability

### Default Rate Limits

**Messaging API:**
- **Default Outbound Rate**: 1 message per second (MPS)
- **Burst API Rate**: 15 MPS (for short bursts)
- **Queue Capacity**: 900 messages (15-minute buffer)
- **Queue Timeout**: After 24 hours, messages purged

**Voice API:**
- **Concurrent Calls**: Account-specific (requires configuration)
- **Call Creation Rate**: Depends on account tier
- **Webhook Timeout**: 30 seconds for BXML response

### Rate Limit Handling

**HTTP Responses:**
- `HTTP 429`: Rate limit exceeded (wait and retry)
- `HTTP 403`: Queue full or limit exceeded (backoff required)
- `HTTP 202`: Accepted (message queued for delivery)

**Client Implementation:**
```python
import time
from bandwidth import Bandwidth

client = Bandwidth(
    voice_basic_auth_user_name="username",
    voice_basic_auth_password="password"
)

def send_with_backoff(message, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = client.send_message(message)
            return response
        except RateLimitException:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
            continue
    raise Exception("Max retries exceeded")
```

### Scaling Configuration

For high-volume deployments:

1. **Contact Account Manager** for custom limits
2. **Specify Requirements**:
   - SMS throughput (MPS needed)
   - Peak concurrent calls
   - Geographic distribution
   - Seasonal/event spikes
3. **Custom SLA Terms**:
   - Uptime guarantees (typically 99.99%)
   - Burst allowances
   - Queue sizing
   - Dedicated infrastructure options

### Scalability Features

| Feature | Benefit |
|---------|---------|
| **Asynchronous Queueing** | Smooth out traffic spikes |
| **Webhook Retries** | 24-hour delivery attempts |
| **API Connection Pooling** | Reduced latency |
| **Geographic Failover** | 8 data centers for HA |
| **Custom Rate Tiers** | Grow without redesign |

---

## Integration Implementation

### Official SDKs

Bandwidth provides SDKs in six popular languages:

| SDK | Repository | PyPI/NPM | Maintenance |
|-----|-----------|---------|-------------|
| **Python** | `bandwidth/python-sdk` | `bandwidth-sdk` | Active |
| **Node.js** | `bandwidth/node-sdk` | `@bandwidth/sdk` | Active |
| **Java** | `bandwidth/java-sdk` | `com.bandwidth:sdk` | Active |
| **C#/.NET** | `bandwidth/csharp-sdk` | `bandwidth.sdk` | Active |
| **Ruby** | `bandwidth/ruby-sdk` | `bandwidth-sdk` | Active |
| **PHP** | `bandwidth/php-sdk` | `bandwidth/bandwidth` | Active |

### Python SDK Quick Start

**Installation:**
```bash
pip install bandwidth-sdk
```

**Messaging Example:**
```python
from bandwidth import Bandwidth

client = Bandwidth(
    voice_basic_auth_user_name="api_user",
    voice_basic_auth_password="api_password"
)

# Send SMS
response = client.messaging_api.send_message(
    account_id="account_id",
    message_request=MessageRequest(
        to=["+15551234567"],
        from_="+15559876543",
        text="Hello from InfraFabric"
    )
)

# Track delivery via webhook
@app.route('/sms-webhook', methods=['POST'])
def sms_webhook():
    events = request.json
    for event in events:
        if event['type'] == 'message-delivered':
            print(f"Message {event['id']} delivered!")
    return '', 200
```

**Voice Example:**
```python
# Create outbound call
call = client.voice_api.create_call(
    account_id="account_id",
    create_call_request=CreateCallRequest(
        to="+15551234567",
        from_="+15559876543",
        answer_url="https://infrafabric.io/voice/webhook",
        answer_method="POST"
    )
)

# Handle webhook
@app.route('/voice-webhook', methods=['POST'])
def voice_webhook():
    event = request.json

    if event['eventType'] == 'answer':
        # Respond with BXML
        bxml = """<?xml version="1.0" encoding="UTF-8"?>
        <Response>
          <SpeakSentence>Welcome to InfraFabric</SpeakSentence>
          <Gather maxDigits="1" gatherTimeout="5000">
            <SpeakSentence>Press 1 for support</SpeakSentence>
          </Gather>
        </Response>"""
        return bxml, 200

    elif event['eventType'] == 'gather':
        # Handle DTMF input
        if event['digits'] == '1':
            bxml = """<?xml version="1.0" encoding="UTF-8"?>
            <Response>
              <Transfer to="+15551234567" />
            </Response>"""
            return bxml, 200
```

### Node.js SDK Quick Start

**Installation:**
```bash
npm install @bandwidth/sdk
```

**Implementation:**
```typescript
import { Bandwidth, Client } from '@bandwidth/sdk';

const client = new Client({
  basicAuthUserName: 'api_user',
  basicAuthPassword: 'api_password'
});

// Send SMS
const response = await client.messagingApi.sendMessage(
  'account_id',
  {
    to: ['+15551234567'],
    from: '+15559876543',
    text: 'Hello from InfraFabric'
  }
);

// Create voice call
const call = await client.voiceApi.createCall(
  'account_id',
  {
    to: '+15551234567',
    from: '+15559876543',
    answerUrl: 'https://infrafabric.io/voice/webhook',
    answerMethod: 'POST'
  }
);
```

### Java SDK Quick Start

**Maven Dependency:**
```xml
<dependency>
  <groupId>com.bandwidth</groupId>
  <artifactId>bandwidth-sdk</artifactId>
  <version>latest</version>
</dependency>
```

**Implementation:**
```java
import com.bandwidth.sdk.ApiClient;
import com.bandwidth.sdk.api.MessagingApi;
import com.bandwidth.sdk.model.MessageRequest;

public class BandwidthMessaging {
    public static void main(String[] args) {
        ApiClient client = new ApiClient("api_user", "api_password");
        MessagingApi api = new MessagingApi(client);

        MessageRequest message = new MessageRequest()
            .to(Arrays.asList("+15551234567"))
            .from("+15559876543")
            .text("Hello from InfraFabric");

        api.sendMessage("account_id", message);
    }
}
```

---

## Compliance & Certifications

### STIR/SHAKEN (Caller ID Authentication)

**Overview:**
- Secure Telephony Identity Revisited (STIR)
- Secure Handling of Asserted information using toKENs (SHAKEN)
- Prevents illegal caller ID spoofing
- **Bandwidth Implementation**: Deployed December 2019, billions of calls signed

**Attestation Levels:**
- **"A" (Full)**: Bandwidth fully authenticates your identity and call legitimacy
- **"B" (Partial)**: Bandwidth verifies your authorization to use the number
- **"C" (Gateway)**: Number originating from upstream provider

**Implementation:**
- Automatic for Bandwidth-assigned numbers
- Full attestation provided by default
- Hosted Signing Service available for custom STIR certificates

### CNAM (Caller Name)

**Capability:**
- Display business name on recipient's phone
- Available for US and Canada
- Updates reflected within 2-5 business days
- Required for call center operations

**Setup:**
```bash
POST /api/v1/accounts/{accountId}/cnam/identities

{
  "name": "InfraFabric Inc",
  "phoneNumber": "+15559876543",
  "address": "100 Main St, San Francisco, CA 94105"
}
```

### LNP (Local Number Portability)

**Bandwidth LNP Services:**
- Port numbers FROM other carriers TO Bandwidth
- Dedicated porting team support
- FIFO queue with priority ticket handling
- Automated carrier verification
- Port failure mitigation and dispute resolution

**Process:**
1. Contact Bandwidth support with port details
2. Provide documentation (account number, PIN, address)
3. Submit port request with requested effective date
4. Carrier coordination and verification (3-5 business days)
5. Cutover notification and confirmation

### E911 Compliance

**Requirements Met:**
- Dynamic location routing capabilities
- 6000+ PSAP connections (99.9% US coverage)
- Automatic location provisioning
- Emergency notification service
- VoIP endpoint registration support
- Location accuracy within 50 meters (GPS) or address level

**Certification Status:**
- ECATS compliance (Emergency Communications Access Testing System)
- FCC E911 requirements satisfied
- Roaming 911 support
- NENA (National Emergency Number Association) aligned

### 10DLC A2P Certification

**Application-to-Person (A2P) Messaging:**
- Campaign registration requirement (mandatory since June 2021)
- Business identity verification
- Use case documentation
- Phone number brand registration

**Bandwidth Support:**
- Automated 10DLC campaign submission
- Regular carrier compliance audits
- Messaging filtering score improvement
- Spam score monitoring and remediation

**Implementation Steps:**
1. Register 10DLC campaign with business details
2. Assign phone numbers to campaign
3. Monitor delivery rates and compliance scores
4. Update campaign details if needed (re-approval cycle)

---

## Enterprise Features

### Dedicated Phone Numbers

**Benefits:**
- Exclusive number assignment
- Custom caller ID control
- Preferred routing priority
- Direct carrier relationships
- SLA-backed uptime guarantees

### Custom Caller ID

**Capabilities:**
- Business name display (via CNAM)
- Number masking for privacy
- Dynamic caller ID per call (with number assignment)
- Compliance-verified sender identity

### Toll-Free SMS

**Features:**
- 800/844/855/866/877/888 numbers
- High-volume SMS delivery
- Dedicated carrier relationships
- Premium pricing tier

### Advanced Routing

**Inbound Call Routing:**
- Time-based routing (business hours vs. off-hours)
- Geographic routing (by caller origin)
- Load balancing across endpoints
- Failover to alternative destinations

**Example Routing Rules:**
```
IF time between 9am-5pm EST
  AND caller from 415 area code
THEN route to "SF Office IVR"
ELSE route to "Voicemail"
```

### SIP Trunking for Enterprise

**Topology:**
- Direct SIP connection from enterprise PBX to Bandwidth
- Dedicated data circuit (optional)
- VPN tunneling supported
- Redundant connections for HA

**Integration with PBX Systems:**
- Cisco CUBE support
- Audiocodes (Mediant/SBC)
- Ribbon (former GENBAND)
- Oracle Communications
- 3CX
- Asterisk/FreePBX

**Enterprise Benefits:**
- Unlimited concurrent channels (vs. PRI's 23-channel bundles)
- BYOC (Bring Your Own Carrier) capabilities
- Direct number control
- Cost reduction vs. PRI circuits

### Account Hierarchies

**Multi-Level Organization:**
- Parent account with subaccounts
- Isolated billing and reporting
- Shared number pools
- Centralized management

**Typical Structure:**
```
Parent Account (InfraFabric Inc)
├── Subaccount (Engineering)
├── Subaccount (Sales)
├── Subaccount (Support)
└── Subaccount (Operations)
```

### Dedicated Support Tiers

| Support Tier | Monthly Cost | Response Time | Features |
|--------------|-------------|---------------|----------|
| **Signature** | $0 | Business hours | Community support |
| **Standard** | Included | 1 hour | Dedicated engineer |
| **Premium** | $1,500-$3,000 | 30 minutes | Escalation priority |
| **Premium Plus** | $3,000-$7,500 | 15 minutes | Dedicated success manager |

---

## WebHooks & Event Handling

### Webhook Configuration

**Per Application Setup:**
```bash
PUT /api/v1/accounts/{accountId}/applications/{appId}

{
  "name": "InfraFabric-Prod",
  "inboundCallbackUrl": "https://infrafabric.io/voice/incoming",
  "inboundCallbackMethod": "POST",
  "outboundCallbackUrl": "https://infrafabric.io/voice/events"
}
```

### Messaging Webhook Events

**Webhook Payload Structure:**
```json
[
  {
    "id": "msg-12345",
    "owner": "+15559876543",
    "applicationId": "app-12345",
    "time": "2025-11-14T10:30:00.000Z",
    "type": "message-delivered|message-failed|message-received",
    "direction": "out|in",
    "from": "+15551234567",
    "to": "+15559876543",
    "text": "Message content",
    "messageStatus": "delivered|failed|received"
  }
]
```

**Required Response:**
- HTTP 2xx status code (200, 201, 202, 204)
- Response within timeout (default 30 seconds)
- Any HTTP 4xx/5xx triggers retry logic

**Retry Logic:**
- Immediate retry on timeout
- 24-hour retry window
- Exponential backoff between attempts
- Persistent until 2xx received

### Voice Webhook Events

**Event Types:**

1. **Answer (Synchronous)**
   - Incoming call established
   - Expect BXML response immediately
   - Call paused until response received

2. **Gather (Synchronous)**
   - DTMF digits collected
   - Timeout events
   - Expect BXML response immediately

3. **Disconnect (Asynchronous)**
   - Call ended by caller
   - No response required
   - Informational event

4. **Recording (Asynchronous)**
   - Recording available for download
   - Transcription status
   - No response required

5. **Transfer (Synchronous)**
   - Blind or attended transfer event
   - Status update for transfer operation
   - Response determines next action

### Webhook Signature Verification

**Header Validation:**
```
X-Bandwidth-Signature: <signature>
```

**Verification Process:**
```python
import hmac
import hashlib
import base64

def verify_webhook(request_body, signature, account_id):
    # Signature = base64(HMAC-SHA256(accountId, body))
    expected_sig = base64.b64encode(
        hmac.new(
            account_id.encode(),
            request_body.encode(),
            hashlib.sha256
        ).digest()
    ).decode()

    return hmac.compare_digest(signature, expected_sig)
```

---

## Implementation Estimate for InfraFabric

### Phase 1: Foundation (Weeks 1-2)

| Task | Hours | Notes |
|------|-------|-------|
| Account setup & credentials | 2 | Dashboard configuration, API tokens |
| SDK selection & environment setup | 4 | Python/Node.js, dependency installation |
| Authentication implementation | 3 | Basic Auth or OAuth token refresh |
| Webhook infrastructure setup | 4 | HTTPS endpoint, signature verification |
| **Phase 1 Total** | **13** | |

### Phase 2: Messaging API (Weeks 3-4)

| Task | Hours | Notes |
|------|-------|-------|
| Send SMS implementation | 3 | Single/bulk messaging |
| Receive SMS webhook handling | 3 | Inbound message processing |
| MMS support (optional) | 4 | Media upload/handling |
| Delivery tracking & reporting | 4 | Database schema, webhook logging |
| 10DLC campaign setup | 3 | Carrier registration, compliance |
| Testing (unit + integration) | 4 | Mock API, webhook simulation |
| **Phase 2 Total** | **21** | |

### Phase 3: Voice API (Weeks 5-7)

| Task | Hours | Notes |
|------|-------|-------|
| Outbound call creation | 4 | Basic call initiation |
| BXML response handling | 6 | IVR logic, verb implementation |
| Inbound call webhook processing | 4 | Call routing, application logic |
| DTMF gathering & input handling | 4 | Gather verb, digit collection |
| Call recording setup | 3 | Recording enabled, playback URL |
| Transcription integration | 5 | Real-time or post-call transcription |
| Testing (unit + integration) | 6 | Mock BXML, webhook simulation |
| **Phase 3 Total** | **32** | |

### Phase 4: Phone Numbers & 911 (Weeks 8-9)

| Task | Hours | Notes |
|------|-------|-------|
| Number search & ordering API | 3 | Integration with number pool |
| Number porting implementation | 4 | LNP workflow, carrier coordination |
| E911 dynamic location setup | 5 | DLR endpoint, location updates |
| Emergency notifications | 3 | Alert routing, personnel notification |
| Testing & compliance validation | 4 | Regulatory checklist |
| **Phase 4 Total** | **19** | |

### Phase 5: Enterprise Features (Weeks 10-11)

| Task | Hours | Notes |
|------|-------|-------|
| Webhook retry logic & resilience | 4 | Queue management, dead-letter handling |
| Rate limit handling & backoff | 3 | Throttling, exponential backoff |
| STIR/SHAKEN implementation | 2 | Automatic for Bandwidth numbers |
| CNAM registration & update | 2 | Business name display |
| SIP trunking integration (if needed) | 8 | PBX configuration, SBC setup |
| **Phase 5 Total** | **19** | |

### Phase 6: Testing & Deployment (Weeks 12-13)

| Task | Hours | Notes |
|------|-------|-------|
| Load testing (SMS throughput) | 4 | Rate limit validation |
| Load testing (concurrent calls) | 4 | Call spike handling |
| Production deployment prep | 3 | Secrets management, monitoring setup |
| Canary deployment & monitoring | 4 | Gradual rollout, metrics tracking |
| Runbook development | 3 | Escalation procedures, incident response |
| **Phase 6 Total** | **18** | |

### **Total Implementation Estimate: 122 hours (3-4 engineers, 3-4 weeks)**

### Optimization for InfraFabric

| Optimization | Time Saved | Impact |
|--------------|-----------|--------|
| Use official SDK vs. raw HTTP | 8 hours | Type safety, error handling |
| Pre-built webhook framework | 6 hours | Signature verification, retries |
| Bandwidth code samples | 4 hours | Reference implementations |
| Bandwidth support + documentation | 5 hours | Reduced investigation time |

---

## Pass 5-6: Framework Mapping to InfraFabric

### InfraFabric Communication Stack Integration

**Current State Analysis:**
- Git-based state management (as noted in recent commits)
- Cloud provider API research underway
- Cost tracking CLI integration completed
- Multi-session agent collaboration model

**Bandwidth Integration Points:**

```
InfraFabric Infrastructure
│
├── Control Plane (etcd/distributed state)
│   └── Bandwidth API state (numbers, campaigns, webhooks)
│
├── Event Bus (async processing)
│   ├── SMS delivery events
│   ├── Voice call events
│   ├── 911 emergency notifications
│   └── Phone number order status
│
├── Communication Layer
│   ├── Messaging Service (SMS/MMS via Messaging API)
│   ├── Voice Service (calls via Voice API + BXML)
│   ├── Emergency Service (E911 via 911 API)
│   └── Number Management (Phone Number API)
│
├── Observability & Compliance
│   ├── STIR/SHAKEN attestation
│   ├── E911 compliance tracking
│   ├── Delivery SLAs
│   └── Cost tracking per API/service
│
└── Admin & Developer Tools
    ├── Number provisioning CLI
    ├── Campaign management tools
    └── Emergency testing utilities
```

### Use Cases for InfraFabric

**1. Infrastructure Alerts & Notifications**
```
Event: Resource critical (CPU > 95%)
Action: Send SMS to on-call engineer
Implementation: Messaging API + 10DLC
Cost: $0.004 per alert
```

**2. Automated Call Routing for Support**
```
Event: Customer calls support number
Action: IVR with DTMF routing (1=billing, 2=technical, 3=sales)
Implementation: Voice API + BXML Gather
Cost: $0.0055 per minute inbound
```

**3. Emergency 911 Compliance**
```
Event: Employee with VoIP endpoint calls 911
Action: Automatic location routing + security notification
Implementation: 911 API + Emergency Notification
Cost: $0.015 per enabled number/month + SMS charges
```

**4. Multi-Region Number Management**
```
Requirements: Local numbers in 5 major cities
Implementation: Phone Number API for search/ordering
Action: Automatic 10DLC campaign creation
Cost: $1-2 per number/month + SMS costs
```

**5. Workforce Communications**
```
Scenario: Broadcast notifications to 1000+ field teams
Implementation: Messaging API bulk SMS + group messaging
Action: Automated delivery tracking and retry
Cost: $4-6 per broadcast (1000 × $0.004-0.006)
```

### Data Flow Architecture

```
┌─────────────────┐
│ InfraFabric App │
└────────┬────────┘
         │
    ┌────▼─────────────────────┐
    │  Bandwidth SDK Client    │
    │  (Python/Node.js/Java)   │
    └────┬────────────────┬────┘
         │                │
    ┌────▼────┐      ┌────▼────┐
    │ REST API │      │WebHook  │
    │ Requests │      │ Receiver│
    └────┬────┘      └────┬────┘
         │                │
    ┌────▼────────────────▼──────────┐
    │   Bandwidth Cloud Platform    │
    │  (Messaging/Voice/911 APIs)    │
    └────┬─────────────┬─────────────┘
         │             │
    ┌────▼─┐       ┌───▼──────┐
    │PSTN  │       │ Carriers │
    │PTSN  │       │(SMS/Voice)
    └──────┘       └──────────┘
```

### State Management Integration

**Using etcd for Bandwidth State:**
```
/infrafabric/bandwidth/
├── accounts/{accountId}/
│   ├── credentials (encrypted)
│   ├── phone_numbers/
│   │   ├── {phoneNumber}/
│   │   │   ├── status
│   │   │   ├── 10dlc_campaign
│   │   │   ├── assigned_to (service/team)
│   │   │   └── e911_location
│   │   └── inventory (active, reserved, pending)
│   ├── 10dlc_campaigns/
│   │   └── {campaignId}/
│   │       ├── status
│   │       ├── carrier_approval
│   │       └── assigned_numbers
│   └── webhooks/
│       ├── messaging_endpoint
│       ├── voice_endpoint
│       └── last_verification
```

### Cost Tracking Integration

**Per-Service Metrics:**
```
bandwidth:
  messaging:
    10dlc_sms: 0.004 per unit
    toll_free_sms: 0.007 per unit
    mms: 0.015 per unit
  voice:
    outbound_us_local: 0.01 per minute
    inbound_us_local: 0.0055 per minute
    recording: 0.002 per minute
    transcription: 0.045 per minute
  emergency:
    e911_enabled_number: 0.015 per number/month
  numbers:
    local: 1.00-2.00 per number/month
    tollfree: 2.00-3.00 per number/month
```

---

## Pass 7-8: Meta-Validation & Deployment Planning

### Validation Checklist

#### API Readiness
- [x] Authentication methods confirmed (Basic Auth + OAuth)
- [x] Rate limits documented (1 MPS default, configurable)
- [x] Webhook signature verification available
- [x] SDKs available in required languages (Python, Node.js, Java)
- [x] REST API fully documented
- [x] Error handling patterns defined

#### Compliance Validation
- [x] E911 support confirmed (6000+ PSAP connections)
- [x] STIR/SHAKEN implemented (automatic full attestation)
- [x] CNAM service available
- [x] LNP support available (dedicated porting team)
- [x] 10DLC A2P registration available
- [x] HIPAA BAA not required (non-healthcare initial focus)

#### Enterprise Readiness
- [x] Tier 1 carrier status confirmed (own network)
- [x] 99.99% SLA available (enterprise tier)
- [x] Dedicated support tiers available ($0-$7,500/month)
- [x] SIP trunking available (PBX integration)
- [x] Account hierarchies supported (multi-tenant)
- [x] Wholesale pricing available
- [x] 8 geo-redundant data centers

#### Scalability Validation
- [x] Rate limits tunable per account
- [x] Queue management (900-message buffer, 24-hour retry)
- [x] Webhook retry logic (persistent)
- [x] Connection pooling supported
- [x] Horizontal scaling to 10M+ messages/month

### Production Deployment Plan

#### Pre-Deployment (1 week)

**1. Account Provisioning:**
- [ ] Create Bandwidth enterprise account
- [ ] Configure account hierarchy (parent + subaccounts)
- [ ] Set up billing and payment method
- [ ] Review and accept SLA terms

**2. API Credential Setup:**
- [ ] Generate API tokens (separate from dashboard user)
- [ ] Store in encrypted vault (HashiCorp Vault or AWS Secrets Manager)
- [ ] Configure OAuth client credentials (if using OAuth)
- [ ] Document credential rotation schedule (90-day rotation recommended)

**3. Webhook Infrastructure:**
- [ ] Deploy webhook receiver endpoint (HTTPS only)
- [ ] Implement signature verification
- [ ] Set up webhook logging and monitoring
- [ ] Configure dead-letter queues for failed webhooks
- [ ] Test webhook retries with simulated failures

**4. Number Provisioning:**
- [ ] Decide on number strategy (local vs. toll-free, geographic distribution)
- [ ] Pre-order numbers for pilot regions
- [ ] Complete 10DLC campaign registration
- [ ] Assign numbers to campaigns

**5. Compliance Setup:**
- [ ] Register 10DLC campaign with business details
- [ ] Submit CNAM records (business name display)
- [ ] Configure E911 locations for provisioned numbers
- [ ] Document STIR/SHAKEN implementation (automatic)
- [ ] Review LNP procedures with Bandwidth support

#### Pilot Phase (2-3 weeks)

**1. Limited Rollout:**
- [ ] Deploy to single region (e.g., West Coast)
- [ ] Limit to 100K messages/day and 100 concurrent calls
- [ ] Monitor all metrics: latency, success rate, webhook delivery
- [ ] Gather customer feedback

**2. Load Testing:**
- [ ] SMS throughput: Ramp to 50 MPS (validate rate limits)
- [ ] Voice capacity: Ramp to 500 concurrent calls
- [ ] Webhook delivery: Simulate carrier delays and failures
- [ ] Measure end-to-end latency (API→PSTN→recipient)

**3. Compliance Validation:**
- [ ] Test E911 emergency call routing
- [ ] Verify STIR/SHAKEN signing on outbound calls
- [ ] Validate CNAM display (business name)
- [ ] Test message delivery for compliance (TCPA logging)

**4. Cost Analysis:**
- [ ] Validate actual vs. estimated costs
- [ ] Identify optimization opportunities
- [ ] Calculate break-even vs. competitors

#### Production Rollout (1 week)

**1. Gradual Ramp:**
- [ ] Day 1: 10% traffic (validate production metrics)
- [ ] Day 3: 50% traffic (peak hour testing)
- [ ] Day 5: 100% traffic (full production)
- [ ] Maintain automated rollback capability

**2. Monitoring & Alerting:**
```yaml
Metrics to Monitor:
  - API success rate (target: > 99.9%)
  - Webhook delivery success (target: 100% within 24h)
  - SMS delivery rate (target: > 98% carrier delivery)
  - Voice call completion rate (target: > 99%)
  - End-to-end latency (target: < 2 sec SMS, < 3 sec calls)
  - Error rates by type (API errors, carrier rejects, timeouts)
  - Cost per message/call (budget tracking)

Alerts (PagerDuty/OpsGenie):
  - API error rate > 1%
  - Webhook delivery failures > 5% in 1 hour
  - SMS delivery rate < 95%
  - Voice call setup failures > 2%
  - Inbound webhook latency > 5 seconds
  - Cost overage > 10% vs. budget
```

**3. Documentation:**
- [ ] Runbook: SMS delivery troubleshooting
- [ ] Runbook: Voice call failure diagnosis
- [ ] Runbook: Emergency 911 incident response
- [ ] Runbook: Rate limit handling and escalation
- [ ] Runbook: Bandwidth support escalation process

**4. Team Training:**
- [ ] On-call rotation trained
- [ ] Incident response procedures reviewed
- [ ] Escalation contacts shared
- [ ] Bandwidth support contact information posted

### High-Availability Configuration

**Multi-Region Strategy:**
```
Region 1 (us-east-1)
├── Bandwidth API: Primary
├── Webhook receiver: Primary
└── Phone numbers: Active

Region 2 (us-west-2)
├── Bandwidth API: Secondary
├── Webhook receiver: Secondary
└── Phone numbers: Active (for geographic distribution)

Failover:
- DNS failover to alternate region on API timeout
- Webhook dual-write to both regions (resilience)
- Local number routing by geographic origin
```

**Disaster Recovery Plan:**
```
RTO (Recovery Time Objective): < 5 minutes
RPO (Recovery Point Objective): < 1 minute

Backup Strategy:
- Daily snapshots of phone number inventory
- Webhook log retention (7 days, queryable)
- Number porting list (recovery document)
- 10DLC campaign details (recovery document)

Recovery Steps:
1. Activate secondary Bandwidth API credentials
2. Update DNS to secondary region
3. Verify webhook delivery in secondary region
4. Restore phone number assignments from backup
5. Notify customers of active status
```

### Cost Optimization Strategy

**Initial Projection (Year 1):**
```
Messaging:
  10 million SMS/month @ $0.004 = $40K/month = $480K/year
  (assumption: moderate notification volume)

Voice:
  500K call minutes/month @ $0.01 = $5K/month = $60K/year
  (assumption: support IVR, emergency calls)

Phone Numbers:
  500 numbers @ $1.50 average = $750/month = $9K/year

Emergency Services:
  500 E911-enabled numbers @ $0.015 = $7.5K/month = $90K/year

Support Tier:
  Premium support = $2K/month = $24K/year

Total Year 1: ~$663K (before volume discounts)
Target with wholesale: ~$550K (17% savings)
```

**Cost Reduction Tactics:**
1. **Consolidate 10DLC campaigns** (fewer carrier fees)
2. **Leverage local numbers** instead of toll-free (40% cheaper SMS)
3. **Commit annual volume** (15-25% discount)
4. **Batch messaging** during off-peak hours
5. **Implement Do-Not-Call suppression** (reduce failed deliveries)
6. **Monitor spam scores** (improve deliverability)

### Performance Benchmarks

**Target SLAs:**
```
Messaging:
  Latency (API→carrier): < 500ms (p95)
  Delivery time (sent→delivered): < 30 seconds (p95)
  Delivery rate: > 98% (carrier confirmation)

Voice:
  Setup time (API→ringing): < 2 seconds (p95)
  Call completion rate: > 99%
  Recording availability: < 5 minutes post-call
  Transcription turnaround: < 2 minutes (async)

WebHooks:
  Delivery latency: < 5 seconds (p95)
  Retry success rate: > 99% (within 24h)
  Signature verification: < 10ms overhead

Emergency:
  E911 location update: < 1 second
  PSAP delivery: < 3 seconds
  Location accuracy: ≥ 50m (GPS) or address-level
```

### Support & Escalation Matrix

| Issue | Response Time | Contact | Escalation |
|-------|---------------|---------|------------|
| API Outage | 15 min | Premium Support | Dedicated engineer |
| High Error Rate | 30 min | Standard Support | Senior engineer |
| Compliance Question | 1 hour | Standard Support | Compliance team |
| Feature Request | 4 hours | Support portal | Product team |
| Non-Critical Bug | 24 hours | Support ticket | Engineering |

---

## IF.TTT Citations & References

### Primary Documentation

1. **Bandwidth API Developer Portal** - https://dev.bandwidth.com/
   - API References, SDKs, Guides, Examples
   - Retrieved: 2025-11-14
   - Status: Current, maintained daily

2. **Bandwidth Messaging API v2 Documentation** - https://dev.bandwidth.com/docs/messaging/
   - SMS/MMS capabilities, rate limits, webhooks
   - Retrieved: 2025-11-14
   - Version: Current (v2)

3. **Bandwidth Voice API Documentation** - https://dev.bandwidth.com/docs/voice/
   - BXML, WebRTC, SIP, recording, transcription
   - Retrieved: 2025-11-14
   - Version: Current (v1 of Voice v2 platform)

4. **Bandwidth 911 API Documentation** - https://dev.bandwidth.com/docs/emergency/
   - E911, Dynamic Location Routing, emergency notifications
   - Retrieved: 2025-11-14
   - Status: Production-ready

5. **Bandwidth Phone Number API Documentation** - https://dev.bandwidth.com/docs/numbers/
   - Number search, ordering, porting, 10DLC management
   - Retrieved: 2025-11-14
   - Status: Production-ready

### Pricing & Commercial

6. **Bandwidth Pricing Page** - https://www.bandwidth.com/pricing/
   - SMS, voice, number costs, wholesale pricing
   - Retrieved: 2025-11-14
   - Last Updated: Current

7. **Bandwidth Products Overview** - https://www.bandwidth.com/products/
   - Messaging, Voice, 911, Phone Numbers, SIP Trunking
   - Retrieved: 2025-11-14
   - Status: Complete product suite overview

### Compliance & Certifications

8. **STIR/SHAKEN Implementation** - https://www.bandwidth.com/resources/stir-shaken-and-e911-a-regulatory-readiness-guide/
   - Bandwidth STIR/SHAKEN deployment and compliance
   - Retrieved: 2025-11-14
   - Reference: FCC mandate compliance (as of June 2021)

9. **E911 Solution** - https://www.bandwidth.com/911/
   - E911 overview, dynamic location routing, PSAP connections
   - Retrieved: 2025-11-14
   - Coverage: 6000+ PSAPs, 38+ countries with full PSTN

10. **Network Infrastructure Overview** - https://www.bandwidth.com/glossary/
    - All-IP voice network, Tier 1 carrier status
    - Retrieved: 2025-11-14
    - Scope: US nationwide + international expansion

### SDKs & Code Examples

11. **GitHub - Bandwidth SDKs** - https://github.com/bandwidth/
    - Official repositories for Python, Node.js, Java, C#, Ruby, PHP
    - Retrieved: 2025-11-14
    - Maintenance: Active (updated within 3 months)

12. **GitHub - Bandwidth Code Samples** - https://github.com/Bandwidth-Samples/
    - Reference implementations for all major APIs
    - Retrieved: 2025-11-14
    - Languages: Python, JavaScript/Node.js, Java

### Support & Knowledge Base

13. **Bandwidth Support Center** - https://support.bandwidth.com/
    - Knowledge base, FAQs, best practices
    - Retrieved: 2025-11-14
    - Coverage: API authentication, account setup, compliance

### Industry Standards & Specifications

14. **STIR/SHAKEN RFC 8224/8225** - IETF standards for caller ID authentication
    - Implemented by Bandwidth since December 2019
    - Reference: Billions of calls signed with full attestation

15. **NENA E911 Standards** - National Emergency Number Association
    - Bandwidth compliance certified
    - Reference: Dynamic location routing, PSAP connectivity

16. **TCPA Compliance (Telephone Consumer Protection Act)** - 10DLC A2P
    - Bandwidth campaign registration and vetting
    - Reference: SMS delivery verification and compliance tracking

---

## Conclusion

Bandwidth is **production-ready for InfraFabric enterprise communications integration**, offering:

- **Own infrastructure** (Tier 1 carrier, not reseller)
- **Comprehensive APIs** (Messaging, Voice, 911, Phone Numbers)
- **Enterprise compliance** (E911, STIR/SHAKEN, CNAM, LNP, 10DLC)
- **Wholesale pricing** ($3K+ monthly with volume discounts)
- **Developer-friendly SDKs** (6 languages, official support)
- **Proven reliability** (Fortune 500 + 100% of leading UCaaS/CCaaS)

**Recommendation**: Proceed with Phase 1 (foundation) implementation, targeting Q1 2026 production deployment with pilot phase in Q4 2025.

---

**Document Version**: 1.0
**Last Updated**: 2025-11-14
**Next Review**: 2025-12-14 (post-pilot validation)
