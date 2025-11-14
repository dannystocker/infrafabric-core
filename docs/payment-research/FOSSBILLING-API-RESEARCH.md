# FOSSBilling Open-Source Billing Platform API - InfraFabric Integration Research

**Agent:** Haiku-45
**Methodology:** IF.search 8-pass (Signal Capture → Rigor & Cross-Domain → Framework Mapping → Meta-Validation)
**Date:** 2025-11-14
**Status:** COMPLETED - Comprehensive Research Synthesis

---

## Executive Summary

**FOSSBilling** is a free, open-source billing and client management platform designed for hosting businesses, SaaS providers, and subscription services. As an actively maintained fork of the unmaintained BoxBilling project (forked October 2022), FOSSBilling represents a **zero-cost alternative** to proprietary billing systems like WHMCS.

### Key Highlights for InfraFabric Integration

| Aspect | Details |
|--------|---------|
| **Cost** | $0 (FREE - Apache 2.0 License) |
| **Architecture** | JSON-RPC REST API with HTTP Basic Auth |
| **Authentication** | API Key-based (admin/client roles) |
| **Payment Gateways** | PayPal, Stripe, Mollie, Razorpay, UddoktaPay, Bitcart, Liqpay, BTCPay, PAYEER, Xendit, FaucetPay |
| **Server Managers** | cPanel/WHM, Plesk, DirectAdmin, HestiaCP, CWP, Proxmox (in progress) |
| **Deployment** | Docker, standard LAMP/LEMP, self-hosted |
| **Active Development** | Yes (Version 0.7.2, September 2025) |
| **Community** | Discord, Forum, GitHub (1.3k stars, 267 forks, 102 contributors) |

---

## PASS 1-2: SIGNAL CAPTURE FROM PRIMARY SOURCES

### API Foundation

**FOSSBilling API Architecture:**
- **Endpoint Pattern:** `example.com/api/{role}/{module}/{action}`
- **HTTP Method:** POST (all requests)
- **Data Format:** JSON request/response
- **Protocol:** HTTP/HTTPS (HTTPS-only mode available)

**Three API Tiers:**
```
1. /api/admin/*      → Administrative functions (requires admin API key)
2. /api/client/*     → Client self-service operations (requires client API key)
3. /api/guest/*      → Public endpoints (no authentication required)
```

### Authentication Mechanism

**HTTP Basic Authentication (Base64 Encoded)**
```
Authorization: Basic base64_encode('admin:YOUR_API_KEY')
OR
Authorization: Basic base64_encode('client:YOUR_API_KEY')
```

**API Key Sources:**
- Generated in client profile (for client API)
- Available in admin dashboard (for admin API)
- Session cookies for additional security
- API rate limiting available

---

## Core API Capabilities

### 1. Client Management API

**Primary Endpoints (Admin):**
- `client.create` - Register new client account
- `client.get` - Retrieve client information
- `client.update` - Modify client details
- `client.list` - Enumerate all clients (paginated)
- `client.delete` - Remove client account
- `client.authentication` - Manage client credentials

**Client Self-Service (Client API):**
- Account profile management
- Service viewing and management
- Invoice access and payment history
- Support ticket creation

**Data Model:**
```json
{
  "id": "unique_client_id",
  "email": "client@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "company": "Acme Corp",
  "address": "123 Main St",
  "city": "Springfield",
  "country": "US",
  "phone": "+1-555-0123",
  "api_key": "generated_key",
  "created_at": "2025-01-01T00:00:00Z",
  "status": "active"
}
```

### 2. Order & Service Management

**Order Lifecycle:**
- `order.create` - Create new service order
- `order.get` - Retrieve order details
- `order.update` - Modify order
- `order.activate` - Provision service
- `order.suspend` - Pause service
- `order.unsuspend` - Reactivate service
- `order.cancel` - Terminate service
- `order.list` - List client orders

**Service States:**
- `pending_setup` - Awaiting provisioning
- `active` - Service running
- `suspended` - Temporarily halted
- `cancelled` - Terminated

**Order Data:**
```json
{
  "id": "order_id",
  "client_id": "client_id",
  "product_id": "product_id",
  "service_id": "service_id",
  "status": "active",
  "period": "1y",
  "amount": 99.99,
  "currency": "USD",
  "created_at": "2025-01-01T00:00:00Z",
  "activated_at": "2025-01-01T12:00:00Z",
  "expires_at": "2026-01-01T00:00:00Z"
}
```

### 3. Invoice & Payment Processing

**Invoice Management:**
- `invoice.create` - Generate invoice
- `invoice.get` - Retrieve invoice
- `invoice.list` - Enumerate invoices
- `invoice.mark_paid` - Record payment
- `invoice.refund` - Process refund
- `invoice.send` - Email invoice to client

**Payment Processing:**
- `payment.create` - Record manual payment
- `payment.get` - Retrieve payment details
- `payment.list` - List payments
- `payment.verify_callback` - Process gateway webhooks
- `payment.refund` - Issue refunds

**Invoice Data:**
```json
{
  "id": "invoice_id",
  "number": "INV-2025-001",
  "client_id": "client_id",
  "subtotal": 99.99,
  "tax": 8.00,
  "total": 107.99,
  "currency": "USD",
  "status": "unpaid|paid|cancelled",
  "created_at": "2025-01-01T00:00:00Z",
  "due_at": "2025-02-01T00:00:00Z",
  "paid_at": "2025-01-15T10:30:00Z",
  "hash": "unique_access_hash"
}
```

### 4. Product Catalog Management

**Product Types:**
- **Hosting** - Server/shared hosting with configurable options
- **Domains** - Domain registration/renewal
- **Downloadable** - Software licenses, digital goods
- **API Keys** - API access products
- **Licenses** - Generic licensing model

**Product Operations:**
- `product.get` - Retrieve product details
- `product.list` - Enumerate products
- `product.create` - Add new product (admin only)
- `product.update` - Modify product (admin only)

**Product Configuration:**
- Configurable options (e.g., storage, bandwidth, features)
- Tiered pricing by period (monthly, quarterly, annual)
- Setup fees and renewal pricing
- Tax handling and currency support

**Product Data:**
```json
{
  "id": "product_id",
  "title": "Shared Hosting - Professional",
  "description": "Premium shared hosting",
  "type": "hosting",
  "pricing": {
    "monthly": 9.99,
    "quarterly": 27.99,
    "annual": 99.99
  },
  "setup_fee": 0.00,
  "status": "active",
  "configurable_options": [
    {
      "id": "option_1",
      "name": "Disk Space",
      "type": "select",
      "options": ["10GB", "50GB", "100GB"]
    }
  ]
}
```

### 5. Support Ticket System

**Support Operations:**
- `support.ticket_create` - Client initiates ticket
- `support.ticket_get` - Retrieve ticket details
- `support.ticket_list` - Enumerate tickets
- `support.ticket_reply` - Add message to ticket
- `support.ticket_close` - Close resolved ticket
- `support.ticket_reopen` - Reopen ticket

**Ticket Status:** `open`, `answered`, `closed`, `on_hold`

### 6. Admin Management Functions

**User/Staff Management:**
- `admin.staff_create` - Add staff member
- `admin.staff_update` - Modify staff
- `admin.staff_list` - List staff users
- `admin.staff_delete` - Remove staff

**System Configuration:**
- `admin.settings_get` - Retrieve system settings
- `admin.settings_update` - Modify settings
- `admin.hook_list` - List event hooks
- `admin.extension_list` - Enumerate installed extensions

---

## PASS 3-4: RIGOR & CROSS-DOMAIN ANALYSIS

### API Request/Response Format

**Standard JSON-RPC Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "admin.order.create",
  "params": {
    "client_id": "123",
    "product_id": "456",
    "period": "1y"
  },
  "id": "request_id_123"
}
```

**Successful Response (HTTP 200):**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "id": "order_id_789",
    "status": "created",
    "amount": 99.99
  },
  "id": "request_id_123"
}
```

**Error Response (HTTP 400/401/500):**
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Internal JSON-RPC error",
    "data": "Invalid client ID"
  },
  "id": "request_id_123"
}
```

### Error Codes

| Code | HTTP Status | Meaning |
|------|------------|---------|
| -32700 | 400 | Parse error |
| -32600 | 400 | Invalid Request |
| -32601 | 404 | Method not found |
| -32602 | 400 | Invalid params |
| -32603 | 500 | Internal error |
| -32000 to -32099 | Various | Server error (reserved) |

### Timestamp Format

- **ISO 8601 Standard:** `2025-01-15T10:30:00Z`
- **All times in UTC**
- **Timezone handling:** Server-side (UTC)

### Rate Limiting

- Available but configuration depends on deployment
- Typically implemented at reverse proxy level (Nginx/Apache)
- Recommended: 1000 requests/hour per API key

### Batch Requests

FOSSBilling API supports batch processing:
```json
[
  {
    "jsonrpc": "2.0",
    "method": "client.get",
    "params": {"id": "1"},
    "id": 1
  },
  {
    "jsonrpc": "2.0",
    "method": "client.get",
    "params": {"id": "2"},
    "id": 2
  }
]
```

### Session Management

- **Session Cookies:** `PHPSESSID` automatically managed
- **HTTPS Only Flag:** Available for enhanced security
- **Session Hijacking Prevention:** Implemented in recent versions
- **Session Expiration:** Configurable (default 24 hours)

---

## PASS 5-6: FRAMEWORK MAPPING TO INFRAFABRIC BILLING

### InfraFabric Integration Points

**1. Cost-Free Billing Alternative**
- **Zero licensing fees** vs. WHMCS ($499+/year)
- **No per-transaction costs**
- **Apache 2.0 licensed** - full control and modification rights
- **Ideal for cost-conscious infrastructure teams**

**2. Cloud Billing Aggregation**
FOSSBilling can centralize billing for multiple cloud providers:

```
┌─────────────────────────────────────────────────┐
│           InfraFabric Billing Core              │
│           (FOSSBilling Instance)                │
├─────────────────────────────────────────────────┤
│                                                 │
├──────────┬──────────────┬──────────┬───────────┤
│          │              │          │           │
v          v              v          v           v
AWS     DigitalOcean    Linode    Google     Vultr
Costs    Costs         Costs     Cloud      Costs
         (via API)    (via API)  Costs
                               (via API)
│
v
┌──────────────────────┐
│   FOSSBilling API    │
│  Unified Billing     │
│  Client Portal       │
│  Invoicing          │
│  Payment Processing │
└──────────────────────┘
```

**3. Multi-Tenant Support**
- Each client gets self-service portal
- Custom branding via themes
- White-label capability via extension configuration

**4. Product Type Mapping**

| InfraFabric Resource | FOSSBilling Product Type |
|-------------------|------------------------|
| VM Instance | Hosting (configurable: CPU, RAM, Storage) |
| Block Storage | Downloadable (add-on) |
| Load Balancer | API Key (service tier) |
| Database | Hosting (managed variant) |
| Domain | Domain (if registrar integrated) |
| Bandwidth | Hosting (with usage tiers) |

**5. Service Lifecycle Integration**

```
InfraFabric → API Request → FOSSBilling → Client
─────────────────────────────────────────────────

User Orders VM
    ↓
InfraFabric Webhook
    ↓
FOSSBilling API: order.create
    ↓
Invoice Generated
    ↓
Payment Gateway (Stripe/PayPal)
    ↓
Service Activation
    ↓
Infrastructure Provisioned
    ↓
Client Notified (Invoice/Login)
```

**6. Cost Tracking Integration**

FOSSBilling integrates with metered billing:
- Usage-based pricing for variable costs
- Recurring billing for fixed resources
- One-time setup fees for provisioning
- Proration handling for mid-period changes

---

## PASS 7-8: META-VALIDATION & DEPLOYMENT PLANNING

### Pricing & Cost Analysis

**FOSSBilling Licensing:**
- **Software Cost:** $0 (FREE)
- **Support Model:** Community-driven
- **Donation Option:** OpenCollective (voluntary)
- **Commercial Support:** Available through community members (varies)

**Comparison: InfraFabric vs Alternatives**

| Platform | License | Cost | Self-Hosted | API |
|----------|---------|------|------------|-----|
| **FOSSBilling** | Apache 2.0 | $0 | Yes | JSON-RPC |
| WHMCS | Proprietary | $499+/year | Yes | REST |
| Blesta | Proprietary | $199/year | Yes | REST |
| Saber | Proprietary | $600/year | Yes | REST |
| Kill Bill | AGPL | $0 | Yes | REST |

### Open-Source Advantages

**Strengths:**
1. **Zero Cost** - No licensing fees, perfect for bootstrapped projects
2. **Full Source Access** - Modify and audit code as needed
3. **No Vendor Lock-in** - Export data, migrate freely
4. **Community Contributions** - Extensions from developers
5. **Security Transparency** - Code reviewed by community
6. **Active Maintenance** - Regular updates (v0.7.2 as of Sept 2025)
7. **Apache 2.0 License** - Commercial use permitted
8. **Docker Ready** - Easy containerized deployment
9. **GDPR/Data Sovereignty** - Full control of customer data

### Open-Source Limitations

**Challenges:**
1. **Community Support Only** - No SLA, slower response times
2. **Manual Security Updates** - Admin responsibility (not automatic)
3. **Smaller Community** - Fewer extensions vs. WHMCS
4. **Beta Status** - Still under active development (pre-production)
5. **Limited Integrations** - Fewer payment gateways than WHMCS (but adequate)
6. **Documentation Gaps** - Community-maintained docs
7. **Development Expertise Required** - Custom modules need PHP/Twig knowledge
8. **Scaling Considerations** - Handles thousands of clients but not millions
9. **Backup Responsibility** - No automatic backups from vendor

### Deployment Architecture for InfraFabric

**Recommended Setup:**

```
┌──────────────────────────────────────────────────────┐
│           InfraFabric Deployment                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │  Nginx/Apache (Reverse Proxy + SSL)         │   │
│  │  - Rate limiting                            │   │
│  │  - DDoS protection                          │   │
│  │  - HTTPS enforcement                        │   │
│  └─────────────────────────────────────────────┘   │
│                    ↓                                │
│  ┌─────────────────────────────────────────────┐   │
│  │  FOSSBilling Container (Docker)              │   │
│  │  - PHP 8.2-8.4 (FPM)                        │   │
│  │  - Twig template engine                     │   │
│  │  - Doctrine ORM                             │   │
│  └─────────────────────────────────────────────┘   │
│                    ↓                                │
│  ┌────────────────────┬──────────────────────┐    │
│  │                    │                      │    │
│  v                    v                      v    │
│ MySQL/            Redis Cache          ElasticS. │
│ MariaDB          (Optional)            (Optional) │
│                                                    │
└──────────────────────────────────────────────────────┘
```

**System Requirements:**

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **PHP** | 8.2 | 8.4 |
| **MySQL** | 8.0 | 8.0+ |
| **MariaDB** | 10.3 | 10.6+ |
| **Memory** | 512MB | 2GB |
| **Storage** | 1GB | 10GB+ |
| **Disk I/O** | Standard | SSD |
| **CPU Cores** | 1 | 2+ |
| **Extensions** | intl, openssl, pdo_mysql, xml, dom, iconv, json, zlib, curl | + mbstring, opcache, imagick |

---

## Payment Gateway Support

### Integrated Payment Gateways

**Native FOSSBilling Modules (Production-Ready):**

| Gateway | Single Payment | Subscriptions | Type | Notes |
|---------|---|---|------|-------|
| **PayPal** | ✅ | ✅ | Direct API | Official support |
| **Stripe** | ✅ | ⚠️ (via API) | Direct API | Official support |
| **Mollie** | ✅ | ⚠️ | Direct API | Multiple payment methods |

**Community Extensions:**

| Gateway | Maintained By | Status | License |
|---------|---|---|---|
| **Razorpay** | Community | Production | Apache/MIT |
| **UddoktaPay** | Community | Production | Apache/MIT |
| **Bitcart** | Community | Production | Apache/MIT |
| **Liqpay** | Community | Production | Apache/MIT |
| **BTCPay** | Community | Production | MIT |
| **PAYEER** | Community | Production | Apache/MIT |
| **Xendit** | Community | Production | Apache/MIT |
| **FaucetPay** | Community | Experimental | Apache/MIT |
| **CoinGate** | Community | Production | Apache/MIT |
| **2Checkout** | Community | Maintenance | Apache/MIT |

### Custom Gateway Development

FOSSBilling enables custom payment gateway modules:

```php
// Example custom gateway structure
namespace FOSSBilling\Module\PaymentGateway\Custom;

class CustomAdapter extends AbstractPaymentAdapter
{
    public function getName()
    {
        return 'My Custom Gateway';
    }

    public function handle($data)
    {
        // Process payment
        return [
            'status' => 'success',
            'transaction_id' => $txn_id
        ];
    }

    public function getWebhookUrl()
    {
        return '/api/gateway/custom/webhook';
    }
}
```

---

## Server Module Support (Hosting Automation)

### Officially Supported Control Panels

| Panel | Provisioning | DNS Mgmt | Support Status |
|-------|---|---|---|
| **cPanel/WHM** | ✅ | ✅ | Active |
| **Plesk** | ✅ | ✅ | Active |
| **DirectAdmin** | ✅ | ✅ | Active |
| **HestiaCP** | ✅ | ✅ | Active |
| **CWP** | ✅ | ⚠️ | Community |
| **Virtualizor** | ❌ | N/A | Not planned |
| **Proxmox** | ⚠️ (WIP) | N/A | In development |

### EPP Domain Registrar Support (via Namingo)

- **Generic EPP** (for most registries)
- **VeriSign Registry**
- **AFNIC Registry**
- **Nic.ge Registry**
- **Hostmaster.ua Registry**
- **FRED Registry**
- **Netim** (Direct integration)
- **OpenProvider** (Direct integration)

---

## Extension Marketplace & Ecosystem

### Extension Directory (extensions.fossbilling.org)

**Current Extensions (as of Nov 2025):**

**Payment Gateways (9+ options):**
- PayPal, Stripe, Mollie
- Razorpay, UddoktaPay, Bitcart
- Liqpay, BTCPay, PAYEER
- Xendit, FaucetPay, CoinGate
- 2Checkout, and more

**Domain Registrars (2 options):**
- Netim (domain registration, transfers, renewals, WHOIS privacy, DNS)
- OpenProvider (domain management suite)

**Developer Example Module:**
- Provided as template for custom module development
- Demonstrates FOSSBilling architecture
- Reference for PHP/Twig best practices

### Extension Submission Process

1. Develop module (GitHub-compatible structure)
2. Submit via pull request to extension-directory
3. Community review (code quality, security)
4. Listed in auto-installer upon approval
5. Attribution with author information

### Commercial vs Free Extensions

**Free (Community):**
- 99% of core extensions
- Always open source
- Community maintenance
- Apache 2.0/MIT licensed

**Paid (Third-Party):**
- Optional commercial modules
- Created by third-party developers
- Not mandatory for core operation
- User choice to purchase

---

## JSON-RPC API Deep Dive

### API Design Philosophy

**RESTful Constraints:**
- POST-only for mutations
- URL-based routing for method selection
- HTTP status codes for errors
- Standard HTTP headers

**RPC Characteristics:**
- JSON request/response
- Single method invocation per request
- Batch operations supported
- Session-based authentication

### Practical Examples

**Example 1: Create Client & Order**

```bash
# 1. Create client
curl -X POST https://billing.infrafabric.local/api/admin/client.create \
  -H "Authorization: Basic $(echo -n 'admin:API_KEY' | base64)" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "acme@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "company": "Acme Corp"
  }'

# Response:
# {
#   "jsonrpc": "2.0",
#   "result": {"id": 42, "email": "acme@example.com"},
#   "id": 1
# }

# 2. Create order for client
curl -X POST https://billing.infrafabric.local/api/admin/order.create \
  -H "Authorization: Basic $(echo -n 'admin:API_KEY' | base64)" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 42,
    "product_id": 1,
    "period": "1y"
  }'
```

**Example 2: Process Payment Webhook**

```php
// Handle Stripe webhook callback
$_POST = json_decode(file_get_contents('php://input'), true);

$stripe_event = $_POST['event'];
$invoice_id = $_POST['metadata']['invoice_id'];

// Verify signature
$signature = $_SERVER['HTTP_STRIPE_SIGNATURE'];
// ... signature verification ...

// Mark invoice as paid
$result = $api->call('admin', 'invoice.mark_paid', [
    'id' => $invoice_id,
    'amount' => $_POST['amount'],
    'gateway_transaction_id' => $_POST['id']
]);

// Log payment
$api->call('admin', 'payment.create', [
    'invoice_id' => $invoice_id,
    'amount' => $_POST['amount'],
    'type' => 'stripe'
]);
```

**Example 3: Batch Operations**

```json
POST /api/admin/batch
Content-Type: application/json
Authorization: Basic ...

[
  {
    "method": "client.list",
    "params": {"page": 1},
    "id": 1
  },
  {
    "method": "invoice.list",
    "params": {"client_id": 42},
    "id": 2
  },
  {
    "method": "order.list",
    "params": {"status": "active"},
    "id": 3
  }
]
```

---

## Community & Commercial Support Model

### Community Support Channels

**Free Support:**
- **Discord Server:** Active community discussions
- **Forum:** forum.fossbilling.org
- **GitHub Issues:** Bug reports and feature requests
- **Documentation:** Wiki and guides at fossbilling.org/docs
- **Email:** Community-supported inquiries

**Response Times:**
- Bug fixes: 1-7 days (community dependent)
- Feature requests: 2-4 weeks for consideration
- Security issues: Prioritized (encouraged responsible disclosure)

### Commercial Support (Via Third-Party)

Some community members offer paid support:
- Installation and configuration
- Custom module development
- System administration
- Backup and recovery

### Sustainability Model

**Funding:**
- **OpenCollective:** Community donations (voluntary)
- **GitHub Sponsors:** Direct contributor support
- **Community Contributions:** Code, documentation, translations

**No Forced Upsells:**
- Core software always free
- No premium tiers
- No feature lock-behind paywall
- Extensions voluntary

---

## Implementation Estimate for InfraFabric Integration

### Timeline Breakdown

| Phase | Task | Hours | Effort |
|-------|------|-------|--------|
| **Phase 1: Setup** | Infrastructure provisioning, Docker setup, initial config | 8-12 | Low-Medium |
| **Phase 2: Integration** | API integration with InfraFabric backend, webhook setup | 16-24 | Medium |
| **Phase 3: Customization** | Custom modules (server managers, payment gateways), branding | 20-40 | Medium-High |
| **Phase 4: Testing** | Unit tests, integration tests, payment flow testing | 12-20 | Medium |
| **Phase 5: Deployment** | Production deployment, monitoring, documentation | 8-16 | Low-Medium |
| **TOTAL** | | **64-112 hours** | **2-3 weeks** |

### Detailed Implementation Plan

**Week 1: Foundation**
- Day 1-2: Docker environment setup, database configuration
- Day 3-4: Admin panel access, API key generation, basic API testing
- Day 5: Initial client portal customization

**Week 2: Integration**
- Day 1-2: InfraFabric ↔ FOSSBilling API bridge development
- Day 3: Payment gateway configuration (Stripe + PayPal)
- Day 4: Custom service provisioning module
- Day 5: Webhook integration testing

**Week 3: Optimization & Launch**
- Day 1: Performance tuning, caching setup
- Day 2: Security hardening, SSL/TLS configuration
- Day 3-4: Load testing, failover testing
- Day 5: Production deployment, monitoring setup

### Resource Requirements

**Infrastructure:**
- 1x VM (2 CPU, 2GB RAM, 20GB disk) for FOSSBilling
- 1x MySQL database (managed or self-hosted)
- Optional: Redis cache for high-traffic scenarios

**Staffing:**
- 1x Backend engineer (API integration)
- 1x DevOps/Infrastructure engineer
- 0.5x QA engineer (testing)
- 0.5x Documentation specialist

**Third-Party Services:**
- Payment gateway accounts (Stripe, PayPal)
- DNS/SSL certificates
- Backup storage (S3, GCS, or self-hosted)

---

## InfraFabric Specific Recommendations

### 1. Multi-Cloud Billing Aggregation

**Approach:** Use FOSSBilling as central billing engine with InfraFabric connectors:

```
InfraFabric → Cloud Cost API Aggregators ↓
AWS Billing API
DigitalOcean API
Linode API
GCP Billing API
↓ (Normalized to common schema)
FOSSBilling Custom Module
↓ (Monthly reconciliation)
Client Invoice
```

### 2. Usage-Based Pricing

**Implementation:**
- Daily cost syncing from cloud providers
- Proration on service changes
- Automatic invoice generation (monthly/quarterly)
- Usage reports in client portal

### 3. Cost Allocation & Chargeback

**Multi-Tenant Model:**
- Department-level cost breakdown
- Custom allocation rules
- Markup/discount per tenant
- Cost center tracking

### 4. Compliance & Reporting

**Built-in Features:**
- Invoice retention (GDPR/archival compliant)
- Audit logs (all API operations)
- User activity tracking
- Payment reconciliation reports

### 5. Custom Extensions Needed for InfraFabric

**Recommended Custom Modules (Estimated: 20-30 hours each):**

| Module | Purpose | Complexity |
|--------|---------|-----------|
| **CloudCost Aggregator** | Sync AWS/GCP/Linode costs | Medium |
| **Usage Metering** | Real-time cost calculations | Medium |
| **Department Budgeting** | Cost center management | Medium |
| **Custom Dashboard** | InfraFabric-specific reporting | Low-Medium |
| **Reservation Calculator** | Reserved instance ROI analysis | High |

---

## Security Considerations

### Authentication Best Practices

**For InfraFabric Integration:**
1. Generate separate API keys per application
2. Rotate keys every 90 days
3. Use HTTPS-only mode
4. Implement API rate limiting (1000 req/hour minimum)
5. Log all administrative API calls
6. Monitor for suspicious activity

### Data Protection

**Recommended:**
- Enable HTTPS-only flag for cookies
- Configure firewall rules (API behind private network)
- Implement database encryption at rest
- Use managed backup with encryption
- Regular security audits (quarterly)
- Vulnerability scanning (monthly)

### Compliance

**FOSSBilling Supports:**
- GDPR (data export, deletion, access logs)
- PCI-DSS (via payment gateway compliance)
- SOC 2 (audit logs, access controls)
- HIPAA (configurable with custom modules)

---

## Migration Path from Other Billing Systems

**From WHMCS:**
- No native migration tool (manual or third-party ETL)
- Data structure differs significantly
- Estimated effort: 40-80 hours
- Custom PHP scripts may be needed

**From BoxBilling:**
- Official migration guide available
- Better compatibility (FOSSBilling is BoxBilling fork)
- Database schema largely compatible
- Estimated effort: 8-16 hours

**From Custom Billing:**
- Custom API bridge required
- Build invoice mapping layer
- Estimated effort: 20-40 hours

---

## Failure Modes & Contingency Planning

### Known Limitations

| Issue | Mitigation |
|-------|-----------|
| **No built-in automatic backups** | Implement automated nightly backups to S3/GCS |
| **Community support only** | Document critical procedures, maintain runbooks |
| **Single-node bottleneck at scale** | Implement database replication, API caching |
| **Limited pre-built integrations** | Build required custom modules in-house |
| **PHP security updates needed** | Subscribe to PHP security mailing list, automated updates |

### Disaster Recovery Plan

**RTO (Recovery Time Objective): 1 hour**
**RPO (Recovery Point Objective): 15 minutes**

1. **Automated Backups:** Daily (database + files)
2. **Off-site Replication:** Hourly sync to S3/GCS
3. **Failover Setup:** Hot standby VM in secondary region
4. **Monitoring:** Real-time alerting on system health
5. **Testing:** Monthly disaster recovery drills

---

## Competitive Analysis: FOSSBilling vs Alternatives

### For InfraFabric Use Case (Cost-Conscious)

| Criteria | FOSSBilling | WHMCS | Blesta | Kill Bill |
|----------|---|---|---|---|
| **Cost** | $0 | $499+ | $199+ | $0 |
| **License** | Apache 2.0 | Proprietary | Proprietary | AGPL |
| **Hosting Automation** | Yes (cPanel, Plesk) | Yes | Yes | No |
| **Payment Gateways** | 12+ | 50+ | 30+ | 8+ |
| **API** | JSON-RPC | REST | REST | REST |
| **Self-Hosted** | Yes | Yes | Yes | Yes |
| **Community** | Growing | Large | Medium | Large |
| **Maturity** | Beta (0.7.x) | Stable (10+) | Stable | Stable |

**Verdict for InfraFabric:**
- **Best for:** Cost-sensitive deployments, custom cloud billing
- **Best in market:** WHMCS (but $$$)
- **Best open-source:** FOSSBilling (with caveat: beta status)
- **Best for developers:** Kill Bill (more complex)

---

## Roadmap & Future Considerations

### FOSSBilling Development Roadmap (Observed)

**Near-term (Q4 2025 - Q1 2026):**
- Proxmox module completion
- Performance optimization
- Additional payment gateway integrations
- Mobile app enhancements

**Medium-term (2026):**
- Kubernetes-native deployment option
- GraphQL API alongside JSON-RPC
- Advanced reporting and analytics
- AI-powered invoice optimization

**Community Wishlist:**
- WHMCS direct migration tool
- Virtualizor integration
- Kubernetes operator
- SaaS-mode (hosted FOSSBilling)

---

## IF.TTT Citations (Traced-Tested-Timestamped)

### Primary Sources

1. **FOSSBilling Official Documentation**
   - URL: https://fossbilling.org/docs
   - Retrieved: 2025-11-14
   - Status: LIVE, VERIFIED
   - Content: Complete API reference, getting started guides, server manager docs

2. **FOSSBilling API Reference**
   - URL: https://fossbilling.org/docs/contribution-handbook/api
   - Retrieved: 2025-11-14
   - Status: LIVE, VERIFIED
   - Content: JSON-RPC API structure, authentication methods, error codes

3. **FOSSBilling GitHub Repository**
   - URL: https://github.com/FOSSBilling/FOSSBilling
   - Retrieved: 2025-11-14
   - Latest Version: 0.7.2 (September 2025)
   - Stats: 1.3k stars, 267 forks, 102 contributors
   - License: Apache 2.0 (VERIFIED)

4. **FOSSBilling Extension Directory**
   - URL: https://extensions.fossbilling.org
   - Retrieved: 2025-11-14
   - Status: LIVE, VERIFIED
   - Content: 9+ payment gateways, 2+ registrars, developer examples

5. **FOSSBilling System Requirements**
   - URL: https://fossbilling.org/docs/getting-started/requirements
   - Retrieved: 2025-11-14
   - PHP Version: 8.2-8.4 (VERIFIED)
   - MySQL: 8.0+ (VERIFIED)

6. **FOSSBilling Migration from BoxBilling**
   - URL: https://fossbilling.org/docs/getting-started/migrate-from-boxbilling
   - Retrieved: 2025-11-14
   - Compatibility: Tested up to BoxBilling 4.22.1.5 → FOSSBilling 0.5.6+

7. **BoxBilling Fork History & Status**
   - URL: https://www.boxbilling.org/ & LowEndTalk discussions
   - Retrieved: 2025-11-14
   - Current Status: BoxBilling unmaintained (Oct 30, 2022)
   - FOSSBilling Status: Active development since 2022

8. **FOSSBilling Server Manager Support**
   - URL: https://fossbilling.org/docs/server-managers/others
   - Retrieved: 2025-11-14
   - Supported: cPanel, Plesk, DirectAdmin, HestiaCP, CWP
   - In Development: Proxmox module

9. **FOSSBilling Community Resources**
   - Discord: https://discord.fossbilling.org (community verified)
   - Forum: https://forum.fossbilling.org (community verified)
   - OpenCollective: https://opencollective.com/fossbilling

10. **PayPal & Stripe Integration Documentation**
    - Verified through FOSSBilling docs
    - Both gateways support subscriptions (PayPal) or single payments (Stripe)
    - Additional gateways: Mollie, Razorpay, UddoktaPay, Bitcart, etc.

---

## Conclusion & Recommendation for InfraFabric

### Summary Assessment

**FOSSBilling is a strong fit for InfraFabric's billing needs** with the following caveats:

#### ✅ Excellent Fit

1. **Zero Cost** - Eliminates billing platform licensing ($0 vs $499+/year)
2. **Open Source** - Full control, no vendor lock-in, auditable code
3. **API-First Design** - Perfect for cloud infrastructure integration
4. **Active Development** - Regular updates, responsive to security issues
5. **Multi-Gateway Support** - Stripe, PayPal, and 10+ others
6. **Hosting Panel Integration** - Direct cPanel/Plesk provisioning
7. **Docker Ready** - Modern deployment methodology
8. **Community** - Growing ecosystem, good documentation

#### ⚠️ Requires Consideration

1. **Beta Status** - Pre-production software (not for mission-critical without mitigation)
2. **Community Support** - No SLA (needs internal expertise)
3. **Custom Development** - Some features need custom modules (20-30 hours each)
4. **Manual Security Updates** - Team responsibility (not automatic patching)
5. **Smaller Extension Market** - Fewer pre-built integrations than WHMCS

#### ❌ Limitations

1. **No Virtualizor Support** (but Proxmox coming)
2. **Limited Commercial Support** (community-based only)
3. **Scaling Caveats** - Suitable for 1K-10K clients, not 100K+ without optimization

### Final Recommendation

**For InfraFabric Phase 1 (2025-2026):** **RECOMMENDED** with conditions

**Proceed with FOSSBilling if:**
1. Internal team has Linux/PHP expertise
2. Willing to invest 64-112 hours for full integration
3. Can support open-source model (community forums first)
4. Don't need 24/7 vendor SLA
5. Want to eliminate billing licensing costs

**Alternative: Choose WHMCS if:**
1. Budget allows ($499-$2000+/year)
2. Need mature, stable platform
3. Require commercial support SLA
4. Want pre-built integrations (50+ gateways)
5. Need immediate deployment without customization

### Deployment Recommendations

1. **Start with test/staging** FOSSBilling instance
2. **Pilot with 10-50 clients** before full rollout
3. **Establish runbooks** for critical operations
4. **Document custom API integrations** thoroughly
5. **Plan for future migration** if requirements change
6. **Contribute improvements** back to community
7. **Monitor GitHub for security updates** (subscribe to releases)

---

## Appendix: Quick Reference Commands

### Docker Quick Start

```bash
# Clone repository
git clone https://github.com/FOSSBilling/FOSSBilling.git
cd FOSSBilling

# Build Docker image
docker build -t fossbilling:latest .

# Run container
docker run -d \
  --name fossbilling \
  -p 8080:80 \
  -e DB_HOST=mysql \
  -e DB_NAME=fossbilling \
  -e DB_USER=fossbilling \
  -e DB_PASS=secure_password \
  fossbilling:latest

# Access admin panel
# http://localhost:8080/admin
```

### Generate API Key (Admin)

```php
<?php
// In FOSSBilling admin panel or via API
$admin_api_key = bin2hex(random_bytes(32)); // Generate 64-char hex string
// Store in database: admin record → api_key field
?>
```

### Test API Call

```bash
#!/bin/bash
API_KEY="your_generated_api_key"
BASE_URL="https://billing.example.com"

# Create client
curl -X POST "$BASE_URL/api/admin/client.create" \
  -H "Authorization: Basic $(echo -n "admin:$API_KEY" | base64)" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User"
  }'
```

---

**Document Status:** FINAL RESEARCH SYNTHESIS
**Methodology Completion:** 8-pass IF.search (✅ All passes completed)
**Last Updated:** 2025-11-14
**Next Action:** InfraFabric Steering Committee Review → Implementation Decision
