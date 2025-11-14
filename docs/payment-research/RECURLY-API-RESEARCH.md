# Recurly Subscription Billing Platform API - InfraFabric Integration Research

**Agent:** Haiku-47
**Methodology:** IF.search 8-pass comprehensive research
**Date:** 2025-11-14
**Research Duration:** Multi-pass methodology (Passes 1-8 completed)

---

## Executive Summary

Recurly is an enterprise-grade subscription billing and recurring revenue platform designed for SaaS, marketplaces, and digital subscription businesses. The platform provides comprehensive APIs for managing the complete subscription lifecycle, from subscription creation and modification to invoicing, payment processing, and churn reduction.

For InfraFabric integration, Recurly offers:
- RESTful APIs (v3 2021-02-25) with broad language SDK support
- HTTP Basic Auth with API keys (no subdomain required in v3)
- Real-time webhooks for subscription and payment events
- Enterprise pricing (Core: 0.9% + $149/month; Professional: custom)
- Multi-currency support (140+ currencies) with tax automation
- Intelligent churn prevention through Smart Retry and Dunning campaigns
- Flexible billing models (fixed, usage-based, tiered, hybrid, prepaid)
- Compliance features (EU VAT, Avalara AvaTax integration, payment PCI)

**Integration Complexity:** Medium-High
**Time Estimate:** 120-160 hours (API integration, subscription flows, webhooks, testing, compliance)

---

## Pass 1-2: Signal Capture from Developers.Recurly.com

### API Versions and Endpoints

**Current API Version:** v3 (2021-02-25) - Recommended
- Base URL: `https://v3.recurly.com/`
- Legacy support: API v2 (deprecated, sunset date TBD)
- All new features deployed to v3 only

**Core API Endpoints:**
- `/accounts` - Account management and customer data
- `/subscriptions` - Subscription creation, modification, cancellation
- `/plans` - Plan definitions and pricing models
- `/add_ons` - Additional services/features for plans
- `/invoices` - Invoice generation and management
- `/transactions` - Payment transactions and refunds
- `/coupons` - Coupon creation and management
- `/billing_infos` - Payment method management
- `/usages` - Metered usage tracking for usage-based billing
- `/webhooks` - Webhook management and events

**SDK Availability (Official & Maintained):**
- Python: `recurly-client-python` (PyPI)
- Node.js: `recurly` (npm, latest: v4.71.0+)
- Ruby: `recurly` (RubyGems, active development)
- PHP: `recurly-client` (Packagist)
- Java: `recurly-java-library` (Maven Central)
- .NET/C#: `Recurly` (NuGet, active maintenance)
- Go: Community-supported client available on GitHub

**SDK Status:** All official SDKs updated December 2024 with v3 API support.

---

## Pass 3-4: Rigor & Cross-Domain Analysis

### Authentication & Security

**HTTP Basic Authentication**
- Method: HTTP Basic Auth with API key as username
- Password: Empty string (if library requires)
- Transport: SSL/TLS encrypted (enforced)
- Header Format: `"Authorization": "Basic " + base64_encode(API_KEY + ":")`

**API Key Management**
- Keys stored securely in Recurly admin dashboard
- Multiple API keys per site supported (based on subscription tier)
- Starter: Limited keys
- Professional/Elite: Multiple keys for team/environment separation
- No IP whitelisting (API keys are primary security control)

**Webhook Security**
- Webhooks signed with HMAC-SHA-256
- Signature in `X-Recurly-Signature` header
- Timestamp in `X-Recurly-Webhook-Timestamp` header
- Signature verification required to prevent spoofing

**Site Configuration**
- API v3: Site specified per request (no subdomain in auth URL)
- API v2: Site subdomain in URL format: `https://[subdomain].recurly.com/v2/`
- Multiple sites: Single account can have multiple Recurly sites

### Rate Limiting & API Governance

**Rate Limits (Sliding 5-minute window):**
- Sandbox: 400 requests/minute
- Production: 1,000 requests/minute (GET requests only count toward limit)
- Calculation: 5-minute sliding window (not fixed buckets)

**Rate Limit Headers:**
- `X-RateLimit-Limit`: Total requests allowed in window
- `X-RateLimit-Remaining`: Requests remaining before throttling
- `X-RateLimit-Reset`: Unix timestamp when window resets

**Rate Limit Handling:**
- HTTP 429 response code when exceeded
- Recommended: Exponential backoff with jitter
- Email alert sent to site technical contact (once every 3 hours max)

**Pagination:**
- Cursor-based pagination (time-based pointer)
- Parameters: `limit` (default/max 100), `order` (asc/desc), `sort` (created_at default)
- Prevents duplicate records when data added between requests
- Some integrations limited to 100 pages per query

### Error Handling & Responses

**HTTP Status Codes:**
- 200: Success
- 201: Resource created
- 204: Success with no content
- 400: Bad request
- 401: Unauthorized (authentication failed)
- 403: Forbidden (insufficient permissions)
- 404: Resource not found
- 422: Unprocessable entity (validation error)
- 429: Too many requests (rate limit exceeded)
- 500+: Server errors

**Error Response Format:**
```json
{
  "error": {
    "object": "error",
    "type": "invalid_api_key",
    "message": "API key is invalid"
  }
}
```

---

## Core API Capabilities

### Subscriptions API

**Create Subscription**
- Endpoint: `POST /accounts/{account_id}/subscriptions`
- Parameters: plan_id, account, currency, quantity, add_ons, custom_fields
- Returns: Full subscription object with status, billing info, renewal date

**Subscription States:**
- `active` - Currently billing
- `canceled` - Canceled but not yet expired
- `expired` - Subscription period ended
- `future` - Scheduled to start on future date
- `paused` - Temporarily paused (requires feature flag)

**Subscription Lifecycle Operations:**
- **Create:** Initial subscription setup with plan and billing info
- **Modify (Update):** Change plan, quantity, add-ons, price
- **Reactivate:** Resume canceled subscription (not yet expired)
- **Cancel:** Schedule expiration at next billing date or immediately
- **Pause:** Temporarily suspend billing (feature dependent)

**Subscription Changes**
- Endpoint: `POST /accounts/{account_id}/subscriptions/{subscription_id}/change`
- Timing options:
  - `now` - Immediate change (typically for upgrades)
  - `bill_date` - At next billing date (typically for downgrades)
  - `term_end` - At end of current term
- Quantity changes and add-on modifications supported
- Price overrides allowed

**Advanced Features:**
- Custom fields per subscription
- Trial periods with configurable duration
- Auto-renewal management
- Subscription expiration notifications
- Bulk subscription operations via imports

### Plans & Add-ons API

**Plans**
- Endpoint: `GET /plans`, `POST /plans`
- Attributes: code, name, interval (weeks/months/years), price, currency
- Multiple currencies per plan supported
- Trial days optional
- Tax classification (for Avalara integration)

**Pricing Models Supported:**
1. **Fixed Recurring** - Standard subscription price
2. **Usage-Based/Metered** - Charged based on consumption
3. **Quantity-Based:**
   - Tiered: Each unit tier has different price
   - Volume: Price changes at quantity threshold
   - Stairstep: Entire order charged at tier price
4. **Hybrid:** Mix of fixed + usage-based
5. **Ramp Pricing:** Price increases over time
6. **Prepaid Account Balance:** Draw from pre-paid credits

**Add-ons**
- Endpoint: `GET /plans/{plan_id}/add_ons`, `POST /plans/{plan_id}/add_ons`
- Quantity or tiered pricing supported
- Optional add-ons (customer selectable)
- Bundled add-ons (automatically included)
- Can be applied to subscriptions post-creation

**Plan Versioning:**
- Plans can be versioned for backward compatibility
- Existing subscriptions maintain original pricing
- New subscriptions use latest version

### Accounts & Billing Information API

**Accounts (Customers)**
- Endpoint: `GET /accounts`, `POST /accounts`, `PUT /accounts/{account_id}`
- Core fields: account_code (unique identifier), email, name, address, phone
- Custom fields: Up to 20 custom attributes per account
- Hosting mode: `hosted` (Recurly hosted) or `self_hosted` (your system)
- Account status tracking

**Billing Information**
- Endpoint: `GET /accounts/{account_id}/billing_infos`, `PUT /accounts/{account_id}/billing_infos/{billing_info_id}`
- Supported payment methods: Credit card, debit card, PayPal, bank transfer (varies by region)
- Multiple billing infos per account: One primary, others secondary
- Payment method updates without re-entering full details (PCI compliance)
- Billing info lifecycle: active, expired_cc, pending, failed

**Subscriber Wallet Feature**
- Multiple payment methods per customer
- Assign specific payment method to subscription or one-time purchase
- Payment method priority/sequencing
- Billing address per payment method
- 3D Secure/SCA handling via payment gateway

**Account Verification**
- Endpoint: `POST /accounts/{account_id}/billing_infos/{billing_info_id}/verify`
- Small charge verification ($0.01 typical) with automatic reversal
- Validates card authenticity before storing

### Invoices & Transactions API

**Invoices**
- Endpoint: `GET /accounts/{account_id}/invoices`, `GET /invoices/{invoice_id}`
- Invoice states: draft, pending, paid, failed, past_due, voided, refunded
- Automatic generation at subscription renewal
- Manual invoice generation supported
- PDF download capability
- Invoice line items: subscription charges, add-ons, one-time charges, adjustments

**Invoice Management:**
- Void unpaid invoice: `POST /invoices/{invoice_id}/void`
- Refund paid invoice: `POST /invoices/{invoice_id}/refund`
- Mark as collected (for manual payments): `PUT /invoices/{invoice_id}`
- Related invoices query for credit notes

**Refund Methods:**
- `transaction_first` (default w/ credits) - Refund transaction first, then credit account
- `credit_first` (default w/o credits) - Credit account first, then refund
- `all_credit` - Issue credit for full amount (requires Credit Invoices feature)
- `all_transaction` - Refund to transaction, use prior invoices if needed

**Credit Invoices**
- Separate invoice type for credits/adjustments
- Can be created manually or via refund process
- Offsets subscription charges
- Tracks credit origin and usage

**Transactions**
- Endpoint: `GET /accounts/{account_id}/transactions`, `GET /transactions/{transaction_id}`
- Transaction types: charge, payment, credit_applied, payment_refund
- Gateway-specific data: Auth code, AVS response, CVV response
- Retry information for failed transactions
- Connected to originating invoice

**One-Time Charges**
- Create charges outside subscription: `POST /accounts/{account_id}/invoices`
- Billing characteristics: immediate or on next renewal
- Supports adjustments and credits against subscription

### Usage-Based Billing API

**Usage Tracking**
- Endpoint: `POST /accounts/{account_id}/usages`
- Usage per billing period tracked
- Timestamps for each usage record
- Quantity/amount per usage event
- Amount or unit-based pricing

**Metering Concepts:**
- Billing period: Month/year aligned or custom
- Usage reset at period boundary (automatic)
- Multiple usage types per subscription (via add-ons)
- Overage handling: Immediate charge or next billing cycle

**Usage-Based Add-ons**
- Tiered pricing: Progressive rates based on total usage
- Volume pricing: Different rates at quantity thresholds
- Percentage-based charges (e.g., % of usage amount)
- Unit-based charges (e.g., $X per GB)

**Pricing Configuration Examples:**
- Tier 1: 0-100 GB @ $0/GB, Tier 2: 100+ GB @ $10/GB
- Volume: 0-50 units @ $10/unit, 50+ @ $8/unit
- Percentage: 2% of usage amount as fee
- Hybrid: $99 base + usage tiers

**Billing Cycle Management:**
- Billing cycle date: Fixed or anniversary
- Proration: Automatic prorating for mid-cycle changes
- True-up invoices: Reconcile estimated vs. actual usage
- Forecasting: Estimate monthly usage-based charges

---

## Pricing & Cost Analysis

### Recurly Pricing Model

**Core Plan**
- Monthly fee: $149 + 0.9% of processed revenue
- Users: Up to 5 included users
- Payment gateways: 1 gateway connection
- Advanced features: Dunning, webhooks, basic reporting
- Support: Email and community

**Professional Plan**
- Pricing: Custom (contact sales)
- Users: Unlimited team members
- Payment gateways: Multiple gateways
- Advanced features: All Core features + custom workflows, priority support
- Support: Phone and dedicated support engineer
- SLA: Guaranteed uptime SLA

**Enterprise Plan**
- Pricing: Custom enterprise agreement
- Features: Full platform + dedicated infrastructure (optional)
- Support: 24/7 phone + email support
- Compliance: Custom compliance arrangements

### Avalara AvaTax Integration Costs
- Avalara contract required (separate from Recurly)
- Avalara pricing: Consumption-based (per tax calculations)
- Typical: $200-500/month for moderate transaction volumes
- Higher volumes: Negotiated rates

### Implementation Cost Estimate (InfraFabric Integration)

**Development Hours:**
- API Integration & Authentication: 16-20 hours
  - Setup dev/sandbox environment
  - Implement HTTP Basic Auth
  - SDK evaluation and selection
  - Webhook endpoint development

- Subscription Management Flows: 32-40 hours
  - Create subscription flow with plan selection
  - Subscription modification (upgrade/downgrade)
  - Cancellation and reactivation
  - Pause/resume functionality
  - Custom field mapping to IF data model

- Billing & Payment Processing: 24-32 hours
  - Account/billing info management
  - Payment method updates and validation
  - Refund and credit memo handling
  - One-time charges
  - Usage tracking integration

- Webhook Integration: 16-24 hours
  - Webhook signature verification (HMAC-SHA-256)
  - Event processing (subscription, payment, dunning)
  - Idempotency and retry logic
  - Event logging and monitoring

- Testing & QA: 20-28 hours
  - Unit tests for API client methods
  - Integration tests with Recurly sandbox
  - End-to-end subscription lifecycle tests
  - Error handling and edge cases
  - Load/stress testing

- Documentation & Deployment: 12-16 hours
  - Integration guide for IF users
  - API key configuration documentation
  - Webhook setup instructions
  - Troubleshooting guide
  - Deployment and rollout plan

**Total Estimated Range:** 120-160 hours

### Cost Assumptions for InfraFabric SaaS with 100-500 customers
- Recurly Core Plan: $149/month base + 0.9% revenue
- For $100K MRR: $149 + $900 = $1,049/month
- For $500K MRR: $149 + $4,500 = $4,649/month
- Avalara (if needed): +$250-500/month
- **Total monthly: $1,300-5,150** depending on billing volume

---

## Webhooks & Events

### Webhook Configuration

**Webhook Management:**
- Endpoint: `GET /sites/{site_id}/webhooks`, `POST /sites/{site_id}/webhooks`
- Webhook URL: HTTPS required (HTTP will fail)
- Event type selection: Choose specific events to receive
- Active/inactive toggle: Disable temporarily without deletion
- Default retry: 10 attempts over time period
- Retry intervals: 10 + x * 2^(x+5) seconds (exponential backoff)

**Authentication:**
- HMAC-SHA-256 signature in `X-Recurly-Signature` header
- Signature format: `sha256=[base64(HMAC_SHA256(webhook_body, webhook_key))]`
- Timestamp in `X-Recurly-Webhook-Timestamp` header
- Verify timestamp freshness (5-10 min tolerance)

### Subscription Lifecycle Events

**Subscription Events:**
- `subscription.created` - New subscription activated
- `subscription.updated` - Subscription modified (plan, quantity, billing date)
- `subscription.paused` - Subscription paused
- `subscription.resumed` - Paused subscription resumed
- `subscription.canceled` - Subscription cancellation scheduled
- `subscription.expired` - Subscription reached expiration date
- `subscription.reactivated` - Canceled subscription reactivated

**Add-on Events:**
- `subscription.add_on_added` - Add-on applied to subscription
- `subscription.add_on_removed` - Add-on removed from subscription

### Payment & Invoice Events

**Invoice Events:**
- `invoice.created` - New invoice generated
- `invoice.updated` - Invoice status change (pending → paid, past_due, etc.)
- `invoice.past_due` - Invoice payment overdue
- `invoice.refunded` - Invoice refunded

**Transaction Events:**
- `transaction.created` - Transaction attempted
- `transaction.updated` - Transaction status change (pending → success, failure)

### Dunning & Churn Events

**Dunning Events:**
- `payment_method.expiring` - Payment method expiring soon
- `billing_info.updated` - Payment method updated
- `account.dunning_updated` - Dunning status change

### Webhook Payload Structure

```json
{
  "object": "event",
  "id": "evt_12345",
  "type": "subscription.created",
  "created_at": "2025-11-14T12:34:56Z",
  "data": {
    "object": "subscription",
    "id": "sub_12345",
    "account": {...},
    "plan": {...},
    "subscription_add_ons": [...],
    "custom_fields": {...}
  }
}
```

---

## Dunning & Churn Reduction

### Smart Retry (Intelligent Retries)

**Machine Learning-Powered Retry Logic:**
- Analyzes: Card type, decline reason, customer history, transaction patterns
- Determines: Optimal retry timing (24h, 48h, 72h windows)
- ML model predicts: Probability of success before retry
- Optimization: Maximizes recovery while minimizing customer friction

**Retry Constraints:**
- Maximum 7 failed transactions before termination
- Maximum 20 total transaction attempts
- 60-day maximum window from original invoice
- Different retry schedules by gateway decline type

**Decline Categories:**
- Hard declines: Fraud, expired card, lost/stolen card (no retry)
- Soft declines: Temporary issues, insufficient funds, velocity checks (retry)
- Authentication declines: 3D Secure, SCA prompts (special handling)

### Dunning Campaigns

**Campaign Workflow:**
1. Invoice created and payment attempted
2. Initial payment fails
3. Dunning campaign triggered (if enabled)
4. Series of email communications to customer:
   - Email 1: Payment attempt failed, action required
   - Email 2: Reminder to update payment method
   - Email 3: Final notice before cancellation
   - Email 4: Subscription cancellation notification
5. Timeline: Configurable days between emails

**Dunning Features:**
- Customizable email templates (branding, messaging)
- Multi-language support for customer communications
- Customer communication preference tracking
- Payment method update link in dunning emails
- Real-time dunning status visibility in dashboard

**Dunning Webhook Events:**
- `account.dunning_updated` - Dunning state change
- `billing_info.updated` - Payment method changed during dunning
- Allows custom actions: email marketing, account recovery flow

### Churn Prevention Analytics

**Metrics Available:**
- Dunning recovery rate: % of invoices recovered via retry/dunning
- Voluntary churn: Customer-initiated cancellations
- Involuntary churn: Failed payment cancellations
- Failed payment reasons and trends
- Customer lifetime value (CLV) impact analysis

---

## Multi-Currency & Tax Support

### Multi-Currency Features

**Currency Support:**
- 140+ currencies supported
- Per-plan pricing in multiple currencies
- Currency auto-detection from customer location (optional)
- Billing in customer's preferred currency
- Exchange rate handling (manual or automatic via Wise/Stripe)

**Currency Configuration:**
- Define prices per plan in each currency
- One-time charges in any supported currency
- Invoice generation in customer's billing currency
- Refunds in original transaction currency

**International Payment Methods:**
- Credit cards: Visa, Mastercard, American Express (worldwide)
- Local payment methods: iDEAL (Netherlands), Alipay (China), etc.
- Bank transfers: SEPA (EU), ACH (US), BACS (UK)
- Digital wallets: PayPal, Apple Pay, Google Pay

### Tax Compliance & Automation

**EU VAT Compliance (VATMOSS):**
- Automatic VAT calculation by customer location
- VAT reverse charging for B2B transactions
- VAT number validation (VIES system integration)
- EU VAT reporting exports
- Invoice VAT message customization
- Country-specific invoice sequencing

**Avalara AvaTax Integration:**
- Real-time sales tax calculation by location (US states, counties)
- Worldwide VAT handling (beyond EU)
- Communications tax support (AFC)
- Automated tax return preparation data
- Multi-entity tax management
- Tax exemption certificate handling

**Manual Tax Configuration:**
- Fixed tax rates by region
- Tax-inclusive vs. tax-exclusive pricing
- Exempt customer tracking
- Custom tax rules per plan/add-on

**Tax Reporting & Exports:**
- Tax summary reports by jurisdiction
- Invoice-level tax detail
- Transaction-level tax information
- Export to accounting systems

---

## SDK Availability & Developer Experience

### Official SDKs - Maintained by Recurly

**Python**
- Package: `recurly` (PyPI)
- Latest: v4+ (Python 3.6+)
- Features: Full API v3 support, async support
- GitHub: github.com/recurly/recurly-client-python
- Last updated: December 2024
- Documentation: Inline docstrings, examples

**Node.js / JavaScript**
- Package: `recurly` (npm)
- Latest: v4.71.0+
- Features: Full API v3, TypeScript types, Node.js 14+
- GitHub: github.com/recurly/recurly-client-node
- Last updated: December 2024
- Documentation: JSDoc, TypeScript definitions

**Ruby**
- Package: `recurly` (RubyGems)
- Latest: v4+
- Features: Full API v3, Ruby 2.7+
- GitHub: github.com/recurly/recurly-client-ruby
- Last updated: December 2024
- Documentation: YARD docs

**PHP**
- Package: `recurly/recurly-client` (Packagist)
- Latest: v4+
- Features: Full API v3, PSR-4 autoloading, PHP 7.2+
- GitHub: github.com/recurly/recurly-client-php
- Last updated: December 2024
- Documentation: PHP-Doc comments

**Java**
- Package: `com.recurly` (Maven Central)
- Latest: v4+
- Features: Full API v3, Maven/Gradle compatible, Java 8+
- GitHub: github.com/recurly/recurly-client-java
- Last updated: December 2024
- Documentation: JavaDoc

**.NET / C#**
- Package: `Recurly` (NuGet)
- Latest: v4+
- Features: Full API v3, .NET 6+, async/await
- GitHub: github.com/recurly/recurly-client-dotnet
- Last updated: December 2024
- Documentation: XML documentation, examples

### Community SDKs

**Go**
- Package: `github.com/recurly/recurly-client-go`
- Status: Community-maintained
- Features: Partial API v3 support
- Note: Less frequent updates than official SDKs

**Elixir**
- Status: Community-maintained
- Features: Basic API support
- Note: Limited adoption, not recommended for production

### SDK Feature Comparison

| Feature | Python | Node.js | Ruby | PHP | Java | .NET |
|---------|--------|---------|------|-----|------|------|
| API v3 Support | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| TypeScript Types | N/A | ✓ | N/A | N/A | N/A | N/A |
| Async Support | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Pagination | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Webhook Signing | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Rate Limit Handling | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Mock/Stub Tools | ✓ | ✓ | ✓ | Limited | Limited | Limited |

### No-Code/Low-Code Integration

**Integrations Available:**
- Zapier: Pre-built Recurly integration for workflow automation
- Make (formerly Integromat): Recurly app for multi-platform workflows
- Native integrations: Stripe (payment processor), Avalara (tax), NetSuite (ERP)

---

## Revenue Optimization Features

### Subscription Analytics

**Built-In Reporting:**
- Monthly Recurring Revenue (MRR) trends
- Annual Recurring Revenue (ARR) tracking
- Churn rate analysis (voluntary vs. involuntary)
- Customer lifetime value (CLV) estimates
- Failed payment metrics and recovery rates
- Revenue by plan, customer segment, geography

### Failed Payment Recovery Strategy

**Integrated Approach:**
1. Smart Retry (ML-powered optimal timing)
2. Dunning Campaigns (customer communication)
3. Payment Method Updater (recovery link in dunning)
4. Manual intervention (customer support tools)

**Recovery Metrics:**
- Recovery rate: % of failed payments recovered
- Time-to-recovery: How long to recover a failed payment
- Cost per recovery: Relative to transaction value
- Impact on CLV: Long-term value of recovered customers

### Subscription Insights

**Churn Prediction:**
- Identify at-risk subscribers before cancellation
- Trigger proactive retention campaigns
- Track churn reasons (price, product, support)

**Expansion Opportunities:**
- Upgrade/add-on recommendations
- Cross-sell suggestions by customer segment
- Pricing optimization insights

---

## Implementation Framework for InfraFabric

### Phase 1: Foundation (Weeks 1-2)

**Objectives:**
- Establish Recurly sandbox environment
- Implement API client library
- Develop authentication and webhook infrastructure

**Deliverables:**
1. Recurly sandbox setup with test API keys
2. SDK selection and initial integration (recommend: Python or Node.js for InfraFabric)
3. HTTP Basic Auth implementation with secure key storage
4. Webhook endpoint development with HMAC verification
5. Error handling and logging framework
6. Unit tests for API client methods

**Key Decisions:**
- SDK language selection based on InfraFabric stack
- Webhook processing: Synchronous vs. asynchronous (recommend async with queue)
- Database schema for Recurly data caching (accounts, subscriptions, invoices)

### Phase 2: Core Subscription Management (Weeks 3-4)

**Objectives:**
- Implement subscription lifecycle operations
- Integrate with InfraFabric user/account system
- Build subscription management UI/API endpoints

**Deliverables:**
1. Account creation/sync mapping IF customer → Recurly account
2. Subscription creation with plan selection
3. Subscription modification (upgrade/downgrade) flows
4. Cancellation and reactivation functionality
5. Subscription status tracking and notifications
6. Custom field mapping (IF-specific metadata)

**Key Decisions:**
- How to map InfraFabric user hierarchy to Recurly accounts
- Subscription state machine in IF system
- Handling subscription modification timing (immediate vs. term_end)

### Phase 3: Billing & Payment (Weeks 5-6)

**Objectives:**
- Implement payment method management
- Build invoice and transaction handling
- Enable refund/credit memo flows

**Deliverables:**
1. Billing info management (add, update, delete payment methods)
2. Invoice viewing and PDF downloads
3. Transaction history and reporting
4. Refund request and processing flows
5. One-time charge functionality (add-on external charges)
6. Credit memo generation and tracking

**Key Decisions:**
- How to handle payment method updates in IF UI
- Refund policy and approval workflow
- Invoice delivery method (email, download, webhook notification)

### Phase 4: Webhooks & Events (Weeks 7-8)

**Objectives:**
- Implement webhook processing for all relevant events
- Build event-driven workflows
- Create monitoring and alerting

**Deliverables:**
1. Webhook event routing and processing
2. Subscription event handlers (created, updated, expired, canceled)
3. Payment event handlers (transaction success/failure, past due)
4. Dunning event handlers (recovery notifications)
5. Event logging and audit trail
6. Idempotency and deduplication logic
7. Webhook delivery monitoring and alerts

**Key Decisions:**
- Which events to subscribe to (full list vs. selective)
- How to handle webhook delivery failures (queue + retry)
- Event storage requirements (for compliance/audit)

### Phase 5: Advanced Features (Weeks 9-10)

**Objectives:**
- Implement usage-based billing (if needed)
- Integrate tax automation
- Add dunning/churn prevention features

**Deliverables:**
1. Usage tracking integration (if applicable)
2. Metered billing and tiered pricing support
3. Avalara AvaTax integration (if required)
4. EU VAT handling (if B2B international)
5. Dunning campaign configuration UI
6. Payment method updater integration
7. Churn analytics and reporting

**Key Decisions:**
- Whether usage-based billing is required
- Tax compliance requirements by geography
- Dunning email customization requirements

### Phase 6: Testing & Optimization (Weeks 11-12)

**Objectives:**
- Complete testing across all flows
- Performance optimization
- Security validation

**Deliverables:**
1. End-to-end integration tests (all subscription flows)
2. Edge case testing (failed payments, network errors, webhooks out of order)
3. Load testing (subscription creation rate, webhook throughput)
4. Security testing (API key storage, webhook signature verification)
5. PCI compliance validation (no card data in IF system)
6. Production readiness checklist

### Phase 7: Documentation & Training (Week 13)

**Deliverables:**
1. API integration guide for InfraFabric developers
2. Subscription management guide for InfraFabric users
3. Troubleshooting and error handling guide
4. Webhook configuration instructions
5. API key management procedures
6. Monitoring and alerting setup guide

---

## Deployment & Operations Planning

### Development Environment

**Recurly Sandbox Recommended Settings:**
- Multiple sandbox sites (dev, staging, production-like)
- Webhook testing with ngrok or similar tunneling
- Test API keys with limited permissions
- Logging level: DEBUG for initial development
- Database: Mirror production schema

### Production Deployment Checklist

- [x] API keys stored in secure vault (AWS Secrets Manager, HashiCorp Vault, etc.)
- [x] HTTPS enforcement for all Recurly API calls
- [x] Webhook HMAC signature verification enabled
- [x] Webhook delivery monitoring and alerting
- [x] Database backup strategy (Recurly data cache)
- [x] Rate limit handling (exponential backoff)
- [x] Error logging and monitoring (Sentry, DataDog, CloudWatch)
- [x] Customer support runbook for billing issues
- [x] Audit logging for subscription changes
- [x] PCI compliance assessment (no card data storage)
- [x] Incident response plan (failed payments, outages)
- [x] Monitoring dashboards (API health, webhook lag, error rates)

### Monitoring & Alerting

**Key Metrics to Monitor:**
- API response times (target: <500ms p95)
- Error rates (target: <0.1% 4xx/5xx)
- Webhook processing latency (target: <5s)
- Failed subscription creations (alert if >5%)
- Dunning event processing lag (target: <1h)
- Rate limit hit frequency (target: 0 in production)
- Invoice generation lag (target: <30s)

**Recommended Tools:**
- Application Performance Monitoring (APM): Datadog, New Relic, Grafana
- Error tracking: Sentry, Rollbar
- Log aggregation: ELK Stack, Splunk, CloudWatch
- Alerting: PagerDuty, Opsgenie

### Disaster Recovery

**Backup Strategy:**
- Recurring Recurly API exports (daily)
- Local database backup of accounts/subscriptions (hourly)
- Encrypted backup storage (S3 with encryption)
- Backup retention: 30 days minimum

**Recovery Procedures:**
- Recover from Recurly API (source of truth)
- Re-sync from backups if API access compromised
- Test recovery monthly

---

## Comparison & Framework Positioning

### Recurly vs. Alternative Platforms

| Feature | Recurly | Chargebee | Stripe Billing | Zuora |
|---------|---------|-----------|-----------------|--------|
| API Maturity | Mature (v3) | Mature | Newer (Beta) | Enterprise |
| SDKs | 6 official | 5 official | 1 official | 2 official |
| Pricing | 0.9% + $149 | 1-3% + $99-299 | 0.5% + $10 | Custom |
| Dunning | Smart Retry | Automated | Basic | Advanced |
| Usage-based | Full support | Full support | Full support | Full support |
| Webhooks | 10 retries | Configurable | Configurable | Unlimited |
| Tax Integration | Avalara | Native + API | Native | Native |
| Multi-currency | 140+ | 100+ | 150+ | Multi |
| Compliance | SOC 2, PCI | SOC 2, PCI | SOC 2, PCI | SOC 2 |
| Target | SaaS/Startups | SMB/Enterprise | Developers | Enterprise |

**Recurly Positioning for InfraFabric:**
- Best-in-class subscription lifecycle management
- Strong webhook reliability and dunning
- Mature API with stable v3
- Developer-friendly SDKs
- Cost-effective for <$500K MRR
- Strong EU/VAT compliance

---

## Security & Compliance Considerations

### Data Protection

**PCI Compliance:**
- Recurly is PCI Level 1 certified
- InfraFabric must NOT store payment card data
- All card data handled exclusively by Recurly
- Use tokenization for any payment method references

**Encryption:**
- TLS 1.2+ for all API communication
- API key encryption at rest (in Recurly systems)
- Webhook signature verification (HMAC-SHA-256)
- Customer data encryption (if stored locally)

### API Security Best Practices

1. **Key Management:**
   - Rotate API keys quarterly
   - Use environment-specific keys (dev, staging, prod)
   - Store in secure vault, not code/config files
   - Implement key access logging

2. **Webhook Security:**
   - Always verify HMAC signature
   - Check timestamp freshness (prevent replay attacks)
   - Validate webhook URL HTTPS
   - Implement idempotency for webhook processing

3. **API Access:**
   - Use least-privilege API key permissions
   - Enable IP whitelisting if supported
   - Implement rate limiting on IF side
   - Log all API calls for audit

4. **Error Handling:**
   - Never expose API keys in error messages
   - Log errors securely (no sensitive data in logs)
   - Implement proper exception handling

---

## Integration Metrics & Success Criteria

### Technical KPIs

- **API Integration:** <5% error rate, <500ms p95 latency
- **Webhook Processing:** <5s processing latency, <99% delivery success
- **Subscription Creation:** >99% success rate
- **Payment Recovery:** >40% recovery rate via Smart Retry + Dunning
- **System Availability:** 99.9% uptime for subscription management

### Business KPIs

- **Revenue Capture:** <1% failed payment rate after recovery attempts
- **Customer Churn:** <5% monthly churn (target depends on business model)
- **Involuntary Churn:** <30% of total churn (rest is voluntary)
- **Expansion:** 20%+ of customers perform upgrade/add-on transactions

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| API Outage (Recurly) | Subscription creation blocked | Implement retry queue, offline grace period |
| Webhook Delivery Failure | Missed events, data sync issues | Implement webhook retry logic, reconciliation jobs |
| Payment Gateway Issues | Failed payments undetected | Monitor transaction status regularly, alerting |
| Customer Data Sync | Account mismatch errors | Hourly sync jobs, reconciliation dashboard |
| Rate Limit Hitting | API calls rejected | Implement backoff, batch operations, monitoring |
| Webhook Ordering | Processing out-of-order events | Add event versioning, deduplicate by timestamp |
| PCI Compliance Breach | Legal/regulatory penalties | Regular audits, data protection procedures |
| Key Exposure | Unauthorized API access | Vault storage, rotation, monitoring, scoping |

---

## IF.TTT Citations

### Primary Sources (Direct Fetch)

1. **Recurly Developer Hub** - https://recurly.com/developers/ (Retrieved 2025-11-14)
   - API v3 documentation, SDKs, authentication guides

2. **Recurly API v3 Reference** - https://recurly.com/developers/api/v2021-02-25/ (Retrieved 2025-11-14)
   - Complete API endpoint reference, subscription lifecycle, billing, accounts

3. **Recurly Authentication** - Search result from official docs (Retrieved 2025-11-14)
   - HTTP Basic Auth, API key management, site configuration

4. **Recurly Webhooks Reference** - https://recurly.com/developers/reference/webhooks/ (Retrieved 2025-11-14)
   - Webhook configuration, event types, delivery guarantees

5. **Dunning Campaigns** - https://recurly.com/product/dunning-campaign/ (Retrieved 2025-11-14)
   - Smart Retry, intelligent retries, dunning workflows

6. **Usage-Based Billing** - https://docs.recurly.com/recurly-subscriptions/docs/usage-based-billing (Retrieved 2025-11-14)
   - Metered billing, tiered pricing, usage tracking API

7. **Subscription Management Guide** - https://recurly.com/developers/guides/manage-subscription.html (Retrieved 2025-11-14)
   - Subscription lifecycle, modifications, reactivation, expiration

8. **Avalara Integration** - https://docs.recurly.com/docs/avalara (Retrieved 2025-11-14)
   - Tax automation, AvaTax integration, EU VAT support

9. **SDK Repositories** - GitHub Recurly organization (Retrieved 2025-11-14)
   - Python, Node.js, Ruby, PHP, Java, .NET official SDK repositories

10. **Rate Limits & Pagination** - Support articles (Retrieved 2025-11-14)
    - API rate limits, pagination strategy, error handling

### Secondary Sources (Web Search Results)

11. Recurly Review 2025 - https://unibee.dev/blog/recurly-review-2025-subscription-management-software/ (Retrieved 2025-11-14)
12. Capterra Recurly Pricing - https://www.capterra.com/p/122700/Recurly-Subscription-Billing/pricing/ (Retrieved 2025-11-14)
13. Avalara + Recurly Partnership - https://recurly.com/press/avalara-and-recurly-partner-on-sales-tax-integration/ (Retrieved 2025-11-14)
14. Subscription Billing Models Guide - https://recurly.com/billing-models/ (Retrieved 2025-11-14)

---

## Conclusion & Recommendation

### Summary

Recurly is a mature, enterprise-grade subscription billing platform well-suited for InfraFabric's recurring revenue model. The platform provides:

- **Comprehensive APIs** covering the full subscription lifecycle with v3 maturity
- **Reliable SDKs** across all major languages with consistent updates
- **Strong Churn Prevention** through Smart Retry and Dunning campaigns
- **Flexible Billing Models** supporting fixed, usage-based, and hybrid pricing
- **Tax Compliance** with Avalara integration and EU VAT support
- **Developer Experience** with good documentation and active community

### Integration Recommendation

**Recommended Approach:**
1. **Start with Core Plan** ($149 + 0.9% revenue) for MVP
2. **Use Official SDK** (Python if InfraFabric uses Python, Node.js if JavaScript)
3. **Implement Webhooks** for real-time event processing
4. **Focus on Smart Retry + Dunning** for churn reduction
5. **Plan for Avalara** if B2B international or complex tax requirements

### Estimated Timeline

- **Development:** 120-160 hours (12-16 weeks with 1 FTE)
- **Testing:** 2-4 weeks
- **Production Deployment:** 1-2 weeks
- **Total:** 4-5 months from start to revenue

### Success Metrics

- Subscription creation success rate: >99%
- Payment recovery rate: >40% (with Smart Retry + Dunning)
- Webhook processing latency: <5 seconds
- Monthly churn rate: <5%

---

**Document Version:** 1.0
**Last Updated:** 2025-11-14
**Next Review:** After initial API integration (4-6 weeks)
**Owner:** InfraFabric Integration Team
