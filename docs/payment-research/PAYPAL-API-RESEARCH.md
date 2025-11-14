# PayPal Commerce Platform API - InfraFabric Integration Research

**Agent:** Haiku-42
**Methodology:** IF.search 8-pass
**Date:** 2025-11-14
**Status:** Complete - Signal Capture & Cross-Domain Analysis

---

## Executive Summary

PayPal Commerce Platform is a mature, globally-distributed payment acceptance infrastructure serving 200+ countries and 25 currencies. The platform offers enterprise-grade APIs for orders, recurring billing, invoicing, and payouts with OAuth 2.0 security, comprehensive buyer protection (180-day dispute window), and multi-SDK support (JavaScript SDK, REST API, server SDKs). Transaction fees range from 2.89% + $0.29 to 4.99% + $0.49 depending on payment method and recent 2025 pricing updates. Webhook-based asynchronous integration with signature verification reduces polling overhead. PayPal Checkout Advanced (JavaScript SDK) provides modern pop-up UX vs legacy redirects. **Integration complexity: Medium (5-8 days for baseline payment acceptance; 2-3 weeks for full subscription + payout automation).**

---

## Pass 1-2: Signal Capture from Developer Infrastructure

### API Surface & Product Catalog

PayPal Commerce Platform exposes five core REST API products:

| API | Version | Purpose | Key Endpoints |
|-----|---------|---------|---|
| **Orders API** | v2 | Create and manage payment orders | POST /v2/checkout/orders, PATCH, GET, POST /capture |
| **Payments API** | v1 | Direct payment processing (legacy support) | POST /v1/payments/payment, /execute, /authorize |
| **Subscriptions API** | v1 | Recurring billing & plan management | POST /v1/billing/plans, /subscriptions |
| **Invoicing API** | v2 | Invoice creation, sending, payment tracking | POST /v2/invoicing/invoices, /send, /remind |
| **Payouts API** | v1 | Bulk disbursements to recipients | POST /v1/payments/payouts (up to 15,000 recipients/call) |

### Authentication Architecture: OAuth 2.0 Client Credentials

**Token Exchange Flow:**
```
POST /v1/oauth2/token
Authorization: Basic BASE64(CLIENT_ID:CLIENT_SECRET)
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials

Response:
{
  "access_token": "...",
  "token_type": "Bearer",
  "app_id": "...",
  "expires_in": 32400  // 9 hours
}
```

**Key Properties:**
- Access tokens valid for **9 hours** (32,400 seconds)
- **Best practice:** Cache tokens across requests; regenerate on 401
- Sandbox endpoint: `https://api-m.sandbox.paypal.com/v1/oauth2/token`
- Production endpoint: `https://api-m.paypal.com/v1/oauth2/token`
- Bearer token in Authorization header for all API calls

**Credentials Source:**
- Available from PayPal Developer Dashboard (Dashboard > Apps & Credentials)
- Unique per REST API application (sandbox and production environments separate)

### Developer Tools & SDKs

**Official SDKs:**
1. **JavaScript SDK** (Client-side)
   - Script tag injection: `<script src="https://www.paypal.com/sdk/js?client-id=YOUR_ID"></script>`
   - Provides: Smart Payment Buttons, hosted card fields, Apple Pay/Google Pay integration
   - Configuration params: currency, intent (CAPTURE|AUTHORIZE), components (buttons, marks, fields)

2. **@paypal/paypal-server-sdk** (Node.js/JavaScript Server)
   - NPM package, replaces deprecated paypal-rest-sdk
   - Auto-handles OAuth 2.0 token refresh
   - Type-safe API wrappers for Orders, Payments, Subscriptions, Invoicing, Payouts

3. **Deprecated:** paypal-rest-sdk (no longer supported, migrate to @paypal/paypal-server-sdk)

**REST API:** Full REST endpoints accessible via standard HTTP clients (curl, axios, fetch)

---

## Pass 3-4: Rigor & Cross-Domain Analysis

### Core API Capabilities & Implementation Patterns

#### Orders API: Modern Payment Orchestration

**Workflow:**
1. **Create Order** (merchant server → PayPal)
   ```json
   POST /v2/checkout/orders
   {
     "intent": "CAPTURE",  // or "AUTHORIZE" for 3-hour hold
     "purchase_units": [{
       "amount": {
         "currency_code": "USD",
         "value": "100.00"
       },
       "description": "Product description"
     }]
   }
   ```
   Response: Order ID (CREATED state, valid 3 hours)

2. **Approve Order** (buyer action via JavaScript SDK)
   - PayPal pop-up: buyer logs in, confirms payment method
   - JavaScript callback: returns order ID upon approval

3. **Capture Order** (merchant server → PayPal)
   ```json
   POST /v2/checkout/orders/{id}/capture
   ```
   Response: Payment details (COMPLETED state)

**Key Constraints:**
- Order creation → capture window: **3 hours** (default, extensible to 72 hours via account manager)
- Authorization hold: **29 days** (PayPal standard)
- Capture honor period: **3 days** (after authorization; reauthorization available)
- No explicit "decline" field in response; failed captures return HTTP 422 with `INSTRUMENT_DECLINED` or similar codes

#### Subscriptions API: Recurring Revenue Engine

**Workflow:**
1. **Create Billing Plan**
   ```json
   POST /v1/billing/plans
   {
     "product_id": "PROD_XXX",
     "name": "Premium Plan",
     "billing_cycles": [{
       "frequency": {
         "interval_unit": "MONTH",
         "interval_count": 1
       },
       "tenure_type": "REGULAR",
       "sequence": 1,
       "total_cycles": 0,  // unlimited
       "pricing_scheme": {
         "fixed_price": {
           "currency_code": "USD",
           "value": "29.99"
         }
       }
     }],
     "payment_preferences": {
       "auto_bill_amount": "YES",
       "setup_fee_failure_action": "CANCEL"
     }
   }
   ```

2. **Create Subscription** (from plan; triggered by buyer approval)
   ```json
   POST /v1/billing/subscriptions
   {
     "plan_id": "P-XXX",
     "subscriber": { "email_address": "buyer@example.com" },
     "application_context": {
       "brand_name": "InfraFabric",
       "user_action": "SUBSCRIBE_NOW"
     }
   }
   ```

**Features:**
- Trial periods with separate pricing
- Billing cycles: daily, weekly, monthly, yearly
- Pause/resume/cancel subscriptions
- Update quantities, plan, shipping address (buyer consent required)
- Webhook notifications: `BILLING.SUBSCRIPTION.CREATED`, `BILLING.SUBSCRIPTION.UPDATED`, `PAYMENT.CAPTURE.COMPLETED`

#### Invoicing API: B2B Payment Initiation

**Capabilities:**
- Create invoices with line items, tax, shipping
- Send invoices (via email or link)
- Issue payment reminders
- Accept partial payments
- Track payment status (DRAFT → SENT → PARTIALLY_PAID → MARKED_AS_PAID)

#### Payouts API: Bulk Disbursement & Creator Economics

**Single Call Limit:** Up to 15,000 recipients per request

```json
POST /v1/payments/payouts
{
  "sender_batch_header": {
    "sender_batch_id": "batch_12345",
    "email_subject": "You have a payment"
  },
  "items": [
    {
      "recipient_type": "EMAIL",
      "recipient_wallet": "paypal",
      "amount": {
        "currency_code": "USD",
        "value": "9.99"
      },
      "receiver": "seller@example.com",
      "note": "Referral payout"
    }
  ]
}
```

Response: Payout batch ID; status tracked via webhook (`PAYMENT.PAYOUTS_BATCH.PROCESSING_COMPLETED`, `PAYMENT.PAYOUTS_ITEM.SUCCEEDED`)

#### Payments API (Direct): Legacy Support

- Direct credit/debit card charging (without buyer redirect)
- Lower conversion rate than PayPal-hosted checkout
- Incrementally being replaced by Orders API
- Still supported for existing integrations

---

### Pricing & Cost Model (2025)

**Standard Transaction Processing (as of January 13, 2025):**

| Payment Method | Fee Structure | Notes |
|---|---|---|
| PayPal Account (buyer) | 2.99% + $0.49 | Via invoicing or checkout |
| Debit/Credit Cards | 2.99% + $0.49 | Through checkout; same as PayPal |
| Cards (keyed-in) | 3.49% + $0.49 | Manual entry at POS or virtual terminal |
| Pay Later (BNPL) | 4.99% + $0.49 | New 2025 rate (was 3.49%) |
| Advanced Card/Alt Methods | 2.89% | New 2025 rate (was 2.59%) |
| Virtual Terminal | 3.39% | New 2025 rate (was 3.09%) |
| Point-of-Sale | 2.29% + $0.09 | PayPal card reader |
| Micropayments | 5% + $0.05 | Per transaction |

**International & Currency Conversion:**
- **Cross-border fee:** +1.5% on transaction value
- **Currency conversion:** +3-4% (variable by corridor)
- Example: $100 USD → EUR with 2.99% + $0.49 + 1.5% + 3.5% = ~8.5% total merchant cost

**No Monthly or Annual Fees:** Pure transaction-based pricing; no platform fees or minimums.

**Comparison to Competitors:**
- Stripe: 2.7% + $0.30 (domestic), +2.2% (intl)
- Square: 2.9% + $0.30
- PayPal competitive on standard volume; premium pricing for Pay Later

---

### Webhooks & Event Notification Infrastructure

**Architecture:** Push-based event delivery with signature verification

**Setup:**
1. Register webhook URL in Developer Dashboard (Dashboard > Webhooks)
2. Subscribe to event types (e.g., PAYMENT.CAPTURE.COMPLETED, BILLING.SUBSCRIPTION.CREATED)
3. PayPal POSTs JSON event payload to your URL

**Event Signature Verification (Required for Security):**

PayPal includes three headers:
- `PAYPAL-TRANSMISSION-ID` - Unique event ID
- `PAYPAL-TRANSMISSION-TIME` - ISO 8601 timestamp
- `PAYPAL-TRANSMISSION-SIG` - HMAC SHA256 signature
- `PAYPAL-CERT-URL` - URL to PayPal's public certificate
- `PAYPAL-AUTH-ALGO` - Signature algorithm ("SHA256withRSA")

**Verification Steps:**
1. Extract signature from header
2. Fetch PayPal's certificate from PAYPAL-CERT-URL
3. Construct expected signature: SHA256(transmission_id + "|" + timestamp + "|" + webhook_id + "|" + cert_url)
4. Verify using certificate's public key
5. If verification fails, reject event and retry (PayPal retries up to 100 attempts over 30 days)

**Common Event Types:**
- `PAYMENT.CAPTURE.COMPLETED` - Order captured (funding received)
- `PAYMENT.CAPTURE.DENIED` - Capture failed
- `BILLING.SUBSCRIPTION.CREATED` - Subscription activated
- `BILLING.SUBSCRIPTION.PAYMENT.EXECUTED` - Recurring charge processed
- `BILLING.SUBSCRIPTION.CANCELLED` - Subscription terminated
- `PAYMENT.PAYOUTS_BATCH.PROCESSING_COMPLETED` - Batch payout finished
- `PAYMENT.PAYOUTS_ITEM.SUCCEEDED` / `FAILED` - Individual payout status

**Retry Policy:**
- PayPal retries failed deliveries exponentially: 1 min, 5 min, 30 min, 2 hrs, 5 hrs, etc.
- Maximum: 100 retries over 30 days
- Your endpoint must return HTTP 200-299 to acknowledge

**Gotchas:**
- Webhook events are NOT guaranteed to arrive in order; use `id` and `create_time` for deduplication
- Same event may be delivered multiple times (idempotency required on merchant side)
- Old webhook verification endpoint now deprecated; use verified webhook signature method only

---

## Pass 5-6: Framework Mapping to InfraFabric Payments

### Proposed Integration Architecture

#### Checkout Flow (Orders API)

```
Buyer                PayPal              InfraFabric Server
  |                    |                         |
  +---- Request Product Catalog ----------------->|
  |                                          [List Products]
  |<--------- Product Details --------------------+
  |
  +---- Initiate Checkout ------>|                |
  |                          [Show SDK UI]
  |                               |
  |<----- Approve Payment --------|
  |                               |
  +------------ Create Order ------------------>|
  |                            [POST /v2/checkout/orders]
  |                                 |
  |                            [Cache order_id]
  |                                 |
  |                            [Return order_id to SDK]
  |                                 |
  |<------- Completion Status ----+
  |
  +------ Webhook: PAYMENT.CAPTURE.COMPLETED ------>|
  |                                          [Update DB]
  |                                          [Ship/Deliver]
  |<-------- Confirmation Email --------------------+
```

**Implementation Points:**
1. **Client:** Use `paypal-sdk/js` to render `<PayPalButtons>` with createOrder callback
2. **Server:** Orders API endpoint creates order, returns order_id to SDK
3. **Server:** Implements webhook listener for PAYMENT.CAPTURE.COMPLETED
4. **Database:** Store order_id, order_status, customer_id, amount, currency

#### Subscriptions Flow (Billing API)

```
Buyer             PayPal             InfraFabric Server
  |                 |                       |
  +- Select Plan -->|                       |
  |                 |                       |
  +- Approve Sub -->|                       |
  |             [Show Billing Plan UI]      |
  |                 |                       |
  +-------- Create Subscription ---------->|
  |                                    [POST /v1/billing/subscriptions]
  |                                         |
  |                                    [Store subscription_id]
  |                                         |
  |<-------- Confirmation Email -----------+
  |
  Month 1:
  +------- Webhook: BILLING.SUBSCRIPTION.PAYMENT.EXECUTED ------->|
  |                                       [Increment cycle count]
  |                                       [Update customer record]
  |
  Month N: (Buyer cancels)
  +------- Webhook: BILLING.SUBSCRIPTION.CANCELLED ------->|
  |                                       [Cleanup]
  |                                       [Churn email]
```

**Implementation Points:**
1. **Plan Management:** Create billing plans via Subscriptions API (or reuse plan_id for recurrence)
2. **Subscription Lifecycle:** Listen to webhook events for state transitions
3. **Dunning Management:** Implement retry logic on failed billing (PayPal auto-retries, but webhook confirms)

#### Payouts Flow (Payout API)

```
InfraFabric Server          PayPal              Recipient
        |                     |                     |
        +---- Submit Batch -->|                     |
        |   [15,000 max items]|                     |
        |                     |                     |
        |<-- Batch ID --------|                     |
        |                     |                     |
        |  [Poll via webhook: PAYMENT.PAYOUTS_BATCH.PROCESSING_COMPLETED]
        |                     |                     |
        |                     +---- Transfer ------>|
        |                     |                     |
        |<- Webhook: Item Status|                   |
        |  [Log success/failure]|                   |
        |                     |                     |
```

**Implementation Points:**
1. **Seller Payout Scheduler:** Batch pending payouts (daily/weekly)
2. **Threshold:** Only payout sellers with balance > minimum (e.g., $10)
3. **Webhook Listener:** Track PAYMENT.PAYOUTS_ITEM.SUCCEEDED / FAILED
4. **Failure Handling:** Retry failed items in next batch or notify seller

---

### Database Schema Mapping

#### Core Tables for InfraFabric

```sql
-- Customers & Authentication
CREATE TABLE customers (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  paypal_buyer_id VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders (Payment Transactions)
CREATE TABLE orders (
  id UUID PRIMARY KEY,
  customer_id UUID NOT NULL REFERENCES customers(id),
  paypal_order_id VARCHAR(255) UNIQUE NOT NULL,
  amount DECIMAL(10, 2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'USD',
  status VARCHAR(50),  -- CREATED, APPROVED, COMPLETED, FAILED
  capture_id VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  captured_at TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Subscriptions
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY,
  customer_id UUID NOT NULL REFERENCES customers(id),
  paypal_subscription_id VARCHAR(255) UNIQUE NOT NULL,
  plan_id VARCHAR(255) NOT NULL,
  plan_name VARCHAR(255),
  amount DECIMAL(10, 2),
  currency VARCHAR(3) DEFAULT 'USD',
  status VARCHAR(50),  -- APPROVAL_PENDING, APPROVED, ACTIVE, SUSPENDED, CANCELLED
  billing_cycle_sequence INT DEFAULT 1,
  started_at TIMESTAMP,
  cancelled_at TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Billing Cycles (Track per-subscription payments)
CREATE TABLE billing_cycles (
  id UUID PRIMARY KEY,
  subscription_id UUID NOT NULL REFERENCES subscriptions(id),
  cycle_number INT,
  paypal_charge_id VARCHAR(255),
  amount DECIMAL(10, 2),
  status VARCHAR(50),  -- PENDING, COMPLETED, FAILED
  scheduled_date DATE,
  processed_date TIMESTAMP,
  FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
);

-- Sellers / Payout Recipients
CREATE TABLE sellers (
  id UUID PRIMARY KEY,
  name VARCHAR(255),
  email VARCHAR(255) UNIQUE NOT NULL,
  paypal_wallet_address VARCHAR(255),  -- email or account reference
  balance DECIMAL(12, 2) DEFAULT 0.00,
  pending_payout DECIMAL(12, 2) DEFAULT 0.00,
  last_payout_date TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payouts Log
CREATE TABLE payouts (
  id UUID PRIMARY KEY,
  paypal_batch_id VARCHAR(255) UNIQUE NOT NULL,
  total_recipients INT,
  total_amount DECIMAL(12, 2),
  status VARCHAR(50),  -- PENDING, PROCESSING, COMPLETED, FAILED
  submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP
);

-- Payout Items
CREATE TABLE payout_items (
  id UUID PRIMARY KEY,
  payout_id UUID NOT NULL REFERENCES payouts(id),
  seller_id UUID NOT NULL REFERENCES sellers(id),
  paypal_item_id VARCHAR(255),
  amount DECIMAL(12, 2),
  status VARCHAR(50),  -- PENDING, SUCCEEDED, FAILED
  error_code VARCHAR(255),
  error_message TEXT,
  FOREIGN KEY (payout_id) REFERENCES payouts(id),
  FOREIGN KEY (seller_id) REFERENCES sellers(id)
);

-- Webhook Events Log
CREATE TABLE webhook_events (
  id VARCHAR(255) PRIMARY KEY,
  event_type VARCHAR(255),
  resource_type VARCHAR(255),
  resource_id VARCHAR(255),
  payload JSONB,
  received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  processed BOOLEAN DEFAULT FALSE
);
```

---

### Error Handling & Resilience

**PayPal Error Response Pattern:**
```json
{
  "name": "INVALID_REQUEST",
  "message": "Invalid request syntax.",
  "debug_id": "2b6a6e7e5ad1b",
  "details": [
    {
      "issue": "INVALID_PARAMETER",
      "field": "purchase_units",
      "description": "Field is missing"
    }
  ]
}
```

**Common Errors:**
| Error | HTTP Status | Handling |
|---|---|---|
| INSTRUMENT_DECLINED | 422 | Buyer's payment method rejected; ask for retry |
| UNVERIFIED_ACCOUNT | 422 | Buyer account not verified |
| PERMISSION_DENIED | 403 | API credentials insufficient |
| RATE_LIMIT_REACHED | 429 | Exponential backoff; retry after 60s+ |
| INTERNAL_SERVER_ERROR | 500 | Retry with jitter |

**Retry Strategy:**
- Exponential backoff: 1s, 2s, 4s, 8s, 16s (max 5 attempts for transient errors)
- Idempotent keys: Use `Idempotency-Key` header (custom; PayPal recommends unique request IDs)

---

## Pass 7: Buyer Protection & Dispute Resolution

### 180-Day Dispute Window

**Scope:**
- **Item Not Received:** Claim within 180 days of payment date
- **Significantly Not as Described:** Claim within 30 days of delivery (or 180 days of payment, whichever is sooner) — **recent 2024 change shortens effective window**

**Resolution Timeline:**
1. **Dispute Opened:** 20-day negotiation window
2. **Escalate to Claim:** If unresolved after 20 days
3. **PayPal Investigation:** 30 days (average 14 days)
4. **Final Decision:** Merchant or buyer refunded

**Merchant Defense:**
- Provide proof of delivery (tracking + signature)
- Document goods shipped per buyer's address
- Screenshots of product description at time of sale
- Communicate with buyer during negotiation period

**Implications for InfraFabric:**
- **Digital goods:** Delivery proof is harder; consider email receipts + login credentials
- **SaaS subscriptions:** Document account creation email, access logs
- **Chargebacks:** PayPal disputes < chargebacks; favorable merchant win rates

---

## Pass 8: Global Coverage & Implementation Planning

### Supported Countries & Currencies

**Markets:**
- **200+ countries and regions** (sellers in 190+ countries)
- **25 currencies:** USD, EUR, GBP, JPY, AUD, CAD, CHF, CNY, INR, MXN, NZD, SEK, PLN, BRL, CZK, DKK, HUF, ILS, MYR, NOK, PHP, RUB, SGD, THB, TWD, VND, HKD, KRW, NTD, TRY, ZAR, AED, QAR, SAR, ANG, BBD, BMD, BZD, FJD, GHS, JMD, KYD, LBP, MAD, NGN, PKR, SCR, TND, VEF

**Local Payment Methods:**
- Credit/Debit Cards (Visa, Mastercard, Amex)
- PayPal wallet (150M+ active accounts)
- Local payment methods (varies by country):
  - **Europe:** iDEAL (NL), Giropay (DE), Sofort (AT, BE, IT, ES)
  - **Asia-Pacific:** Alipay, WeChat Pay, local bank transfers
  - **Latin America:** Local card schemes
  - **India:** UPI, IMPS

**Currency Conversion:**
- Settled in merchant's base currency or local currency (per configuration)
- 3-4% conversion margin applies to cross-border transactions
- Real-time rates updated daily

---

### Checkout Variants & Integration Complexity

#### Standard Checkout (Buttons + Simple Flow)
- **Time to integrate:** 2-3 hours
- **Complexity:** Low
- Implementation: Render `<PayPalButtons>` with SDK
- PCI scope: Merchant out of scope (redirect to PayPal)
- Features: Basic payment capture, PayPal wallet, cards

#### Advanced Checkout (Buttons + Fields)
- **Time to integrate:** 4-6 hours
- **Complexity:** Medium
- Implementation: JavaScript SDK + custom form + hosted card fields
- PCI scope: Merchant qualifies for SAQ A (hosted fields reduce compliance burden)
- Features: Custom checkout UI, faster repeat payments, card tokenization

#### No-Code (Hosted Buttons & Links)
- **Time to integrate:** 30 minutes
- **Complexity:** Very Low
- Implementation: Generate PayPal button link in Dashboard; embed in email/invoice
- Use case: Invoicing, email payments, no developer needed

#### Enterprise (Braintree Advanced Integration)
- **Time to integrate:** 2-4 weeks
- **Complexity:** High
- Features: Advanced fraud detection, multi-currency settlement, advanced reporting
- Suitable for: High-volume merchants, complex payment workflows

---

### Implementation Estimate for InfraFabric

**Baseline: Payment Acceptance (Orders API)**
- API integration & testing: 8-12 hours
- Frontend JavaScript SDK setup: 4-6 hours
- Webhook listener (events + signature verification): 6-8 hours
- Database schema & order tracking: 4-6 hours
- **Subtotal: 22-32 hours (3-4 days)**

**Add-on: Recurring Billing (Subscriptions API)**
- Billing plan creation & management: 4-6 hours
- Subscription lifecycle (create, update, cancel): 6-8 hours
- Dunning & retry logic: 4-6 hours
- Billing cycle tracking: 4-6 hours
- **Subtotal: 18-26 hours (2-3 days)**

**Add-on: Seller Payouts (Payouts API)**
- Payout batch scheduler: 4-6 hours
- Recipient management UI: 6-8 hours
- Webhook processing for payout status: 4-6 hours
- Failure & retry handling: 4-6 hours
- **Subtotal: 18-26 hours (2-3 days)**

**Testing & QA:**
- Sandbox environment setup: 2-3 hours
- Happy path + error scenarios: 8-10 hours
- Production readiness checklist: 2-3 hours
- **Subtotal: 12-16 hours (1.5-2 days)**

**Total Estimate: 70-100 hours (9-13 days) for full implementation**

**Prioritization:**
1. **Week 1:** Orders API (baseline)
2. **Week 2:** Subscriptions API (if recurring revenue model)
3. **Week 3:** Payouts API (if marketplace/creator model)

---

## Integration Implementation Details

### JavaScript SDK Configuration

```html
<!-- Client-side: Render PayPal button -->
<script src="https://www.paypal.com/sdk/js?client-id=YOUR_CLIENT_ID&currency=USD"></script>

<div id="paypal-button-container"></div>

<script>
paypal.Buttons({
  createOrder: function(data, actions) {
    // Call server to create order
    return fetch('/api/orders', {
      method: 'post',
      body: JSON.stringify({
        items: [{ name: 'Product', quantity: 1, unit_amount: { currency_code: 'USD', value: '100.00' } }]
      })
    })
    .then(response => response.json())
    .then(orderData => orderData.id);  // Return order ID
  },

  onApprove: function(data, actions) {
    // Merchant server captures order
    return fetch('/api/orders/' + data.orderID + '/capture', {
      method: 'post'
    })
    .then(response => response.json())
    .then(orderData => {
      // Order captured; proceed with fulfillment
      window.location.href = '/order-confirmation?order=' + data.orderID;
    });
  },

  onError: function(err) {
    console.error('PayPal error:', err);
    alert('Payment failed. Please try again.');
  }
}).render('#paypal-button-container');
</script>
```

### Server-Side (Node.js with @paypal/paypal-server-sdk)

```javascript
const { Client, Environment } = require('@paypal/paypal-server-sdk');
const { OrdersController } = require('@paypal/paypal-server-sdk').Controllers;

const client = new Client({
  clientId: process.env.PAYPAL_CLIENT_ID,
  clientSecret: process.env.PAYPAL_CLIENT_SECRET,
  environment: Environment.Sandbox  // or Production
});

// Create Order
app.post('/api/orders', async (req, res) => {
  const { items } = req.body;

  const request = {
    body: {
      intent: 'CAPTURE',
      purchase_units: [{
        amount: {
          currency_code: 'USD',
          value: items.reduce((sum, item) => sum + item.unit_amount.value * item.quantity, 0)
        },
        items: items
      }]
    }
  };

  try {
    const response = await client.ordersController.ordersCreate(request);
    res.json({ id: response.result.id });
  } catch (error) {
    console.error('Order creation failed:', error);
    res.status(500).json({ error: error.message });
  }
});

// Capture Order
app.post('/api/orders/:id/capture', async (req, res) => {
  const { id } = req.params;

  try {
    const response = await client.ordersController.ordersCapture({ id });
    res.json(response.result);
  } catch (error) {
    console.error('Capture failed:', error);
    res.status(500).json({ error: error.message });
  }
});
```

### Webhook Listener (Signature Verification)

```javascript
const crypto = require('crypto');
const axios = require('axios');

app.post('/webhook/paypal', async (req, res) => {
  const transmissionId = req.headers['paypal-transmission-id'];
  const transmissionTime = req.headers['paypal-transmission-time'];
  const transmissionSig = req.headers['paypal-transmission-sig'];
  const certUrl = req.headers['paypal-cert-url'];
  const authAlgo = req.headers['paypal-auth-algo'];

  const webhookId = process.env.PAYPAL_WEBHOOK_ID;

  // Fetch PayPal's certificate
  const cert = await axios.get(certUrl);

  // Construct expected signature
  const expectedSig = crypto
    .createVerify(authAlgo)
    .update(`${transmissionId}|${transmissionTime}|${webhookId}|${JSON.stringify(req.body)}`)
    .verify(cert.data, transmissionSig, 'base64');

  if (!expectedSig) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  const event = req.body;
  console.log(`Webhook: ${event.event_type}`, event.resource);

  // Process event
  switch (event.event_type) {
    case 'PAYMENT.CAPTURE.COMPLETED':
      handlePaymentCompleted(event.resource);
      break;
    case 'PAYMENT.CAPTURE.DENIED':
      handlePaymentDenied(event.resource);
      break;
    case 'BILLING.SUBSCRIPTION.CREATED':
      handleSubscriptionCreated(event.resource);
      break;
    // ... more events
  }

  res.json({ status: 'received' });
});

function handlePaymentCompleted(capture) {
  const orderId = capture.supplementary_data.related_ids.order_id;

  // Update order in DB
  db.query('UPDATE orders SET status = $1, captured_at = NOW() WHERE paypal_order_id = $2',
    ['COMPLETED', orderId]);

  // Trigger fulfillment (shipment, email, etc.)
  // ...
}
```

---

## IF.TTT Citations (Information Trustworthiness & Temporal Tags)

1. **PayPal Commerce Platform - Official Documentation**
   - Source: https://developer.paypal.com/docs/api
   - Access Method: WebSearch
   - Retrieved: 2025-11-14
   - Confidence: High (official API documentation)

2. **OAuth 2.0 Authentication Protocol**
   - Source: https://developer.paypal.com/docs/api-basics/#oauth-20-authorization-protocol
   - Retrieved: 2025-11-14
   - Confidence: High (official PayPal developer portal)

3. **Orders API v2 Reference**
   - Source: https://developer.paypal.com/docs/api/orders/v2/
   - Retrieved: 2025-11-14
   - Confidence: High

4. **Subscriptions API v1 Reference**
   - Source: https://developer.paypal.com/docs/api/subscriptions/v1/
   - Retrieved: 2025-11-14
   - Confidence: High

5. **Invoicing API v2 Reference**
   - Source: https://developer.paypal.com/docs/api/invoicing/v2/
   - Retrieved: 2025-11-14
   - Confidence: High

6. **Payouts API (Batch Payments)**
   - Source: https://developer.paypal.com/docs/api/payments.payouts-batch/v1/
   - Retrieved: 2025-11-14
   - Confidence: High

7. **PayPal Payment Processing Fees 2025**
   - Source: https://www.paypal.com/us/business/paypal-business-fees & https://www.valueaddedresource.net/paypal-hikes-fees-january-2025/
   - Retrieved: 2025-11-14
   - Confidence: High (official fee schedule; verified via multiple sources)

8. **Webhooks Integration Guide**
   - Source: https://developer.paypal.com/docs/api/webhooks/v1/ & https://developer.paypal.com/api/rest/webhooks/
   - Retrieved: 2025-11-14
   - Confidence: High (official documentation)

9. **Webhook Signature Verification Updates**
   - Source: https://developer.paypal.com/community/blog/paypal-has-updated-its-webhook-verification-endpoint
   - Retrieved: 2025-11-14
   - Confidence: High (official PayPal blog)

10. **Buyer Protection & Dispute Resolution (180-Day Window)**
    - Source: https://www.paypal.com/us/digital-wallet/buyer-purchase-protection & PayPal legal hub
    - Retrieved: 2025-11-14
    - Confidence: High (official buyer protection policy)

11. **Purchase Protection Not As Described Update (2024)**
    - Source: https://www.valueaddedresource.net/paypal-shortens-not-as-described-claim-time-purchase-protection-update
    - Retrieved: 2025-11-14
    - Confidence: Medium-High (reputable PayPal news aggregator)

12. **Orders API Authorization & Capture Flow**
    - Source: https://developer.paypal.com/docs/checkout/standard/customize/auth-capture/
    - Retrieved: 2025-11-14
    - Confidence: High (official integration guide)

13. **Rate Limiting Guidelines**
    - Source: https://developer.paypal.com/api/rest/reference/rate-limiting/
    - Retrieved: 2025-11-14
    - Confidence: High (official documentation)

14. **JavaScript SDK & Server SDKs**
    - Source: https://www.npmjs.com/package/@paypal/paypal-server-sdk & PayPal developer docs
    - Retrieved: 2025-11-14
    - Confidence: High (official NPM package & documentation)

15. **Global Coverage (200+ Countries, 25 Currencies)**
    - Source: https://www.paypal.com/us/webapps/mpp/country-worldwide & https://www.paypal.com/us/brc/article/global-differences-in-payment-methods
    - Retrieved: 2025-11-14
    - Confidence: High (official PayPal global marketplace page)

---

## Research Methodology Notes (IF.search 8-pass)

**Pass 1:** API catalog & core products enumerated via official PayPal Developer Portal
**Pass 2:** OAuth 2.0 authentication flow, token exchange, credential sourcing captured
**Pass 3:** Rigor check: Price structure cross-referenced with Tipalti, Business.com (2025 updates)
**Pass 4:** Cross-domain analysis: Webhook architecture, dispute resolution (legal), global coverage
**Pass 5:** Framework mapping: Database schema, order/subscription workflows for InfraFabric
**Pass 6:** Implementation roadmap: Hour estimates per feature, phased rollout strategy
**Pass 7:** Buyer protection deep-dive: 180-day window, recent 2024 policy changes, merchant defense
**Pass 8:** Deployment planning: PCI compliance, JavaScript SDK setup, error handling, testing strategy

---

## Key Takeaways for InfraFabric

1. **Authentication:** OAuth 2.0 client credentials; cache tokens for 9 hours; automatic via @paypal/paypal-server-sdk
2. **Payment Flow:** Orders API is modern standard; 3-hour create-to-capture window; 29-day authorization holds
3. **Recurring:** Subscriptions API handles billing cycles, trials, dunning; webhook-driven state machine
4. **Payouts:** Up to 15,000 recipients per batch; webhook confirmation required; ~2-3 day settlement
5. **Pricing:** 2.99% + $0.49 standard; intl adds 1.5-4%; no monthly fees
6. **Security:** Webhook signature verification required; PCI scope reduced with hosted fields (SAQ A)
7. **Global:** 200+ countries, 25 currencies; supports local payment methods per region
8. **Compliance:** 180-day dispute window; merchant proof-of-delivery essential for chargebacks
9. **Effort:** 9-13 days for full integration (orders + subscriptions + payouts)
10. **Risk:** Rate limiting not published; idempotency key recommended; retry strategy essential

---

## Recommendations

### Phase 1 (Week 1): Orders API + Checkout
- Integrate JavaScript SDK
- Server-side order creation/capture
- Webhook listener for payment confirmations
- Database order tracking

### Phase 2 (Week 2-3): Subscriptions API
- Billing plan creation
- Subscription lifecycle management
- Billing cycle webhook processing
- Retention analytics

### Phase 3 (Week 4+): Payouts API
- Seller balance tracking
- Batch payout scheduler
- Payout status webhooks
- Tax reporting (1099-K)

### Security & Compliance
- Enable webhook signature verification (mandatory)
- Implement idempotency for all API calls
- Use HTTPS for webhook endpoints; validate cert URLs
- PCI SAQ A via hosted fields (Braintree)
- Monitor rate limiting; implement backoff

---

**End of IF.search 8-pass Analysis**
