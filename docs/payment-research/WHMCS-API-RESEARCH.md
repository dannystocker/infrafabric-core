# WHMCS Billing & Automation Platform API - InfraFabric Integration Research

**Agent:** Haiku-43
**Methodology:** IF.search 8-pass
**Date:** 2025-11-14
**Repository:** https://developers.whmcs.com/

---

## Executive Summary

WHMCS (Web Host Manager Complete Solution) is the industry-standard billing and automation platform for hosting providers. It combines comprehensive client management, invoicing, payment processing, and integrated hosting automation with 80+ payment gateways and native support for cPanel, Plesk, and DirectAdmin control panels. With 140+ API functions, WHMCS enables seamless integration with infrastructure platforms like InfraFabric for automated provisioning, billing, and lifecycle management.

### Key Integration Value for InfraFabric
- **Unified Billing**: Centralized invoice, payment, and client management
- **Automated Provisioning**: Direct integration with hosting infrastructure via provisioning modules
- **Multi-Gateway Support**: 80+ payment gateways including Stripe, PayPal, Authorize.net
- **Hosting Panel Integration**: Native cPanel/WHM, Plesk, DirectAdmin support
- **Enterprise Features**: Domain registration, SSL certificates, ticket support system
- **Industry Adoption**: De facto standard for hosting resellers and cloud providers

---

## Authentication & Security

### API Credential Generation

WHMCS v7.2+ uses dedicated API credentials instead of admin username/password:

**Location**: Configuration → System Settings → Manage API Credentials
**Actions**: Generate New API Credential

### Authentication Parameters

**Method**: POST request to `/includes/api.php` with authentication parameters

```
identifier:  Unique API credential identifier (alphanumeric)
secret:      Base-64 encoded secret key (copy and store securely on generation)
action:      The API action being called (e.g., 'GetClients', 'AddClient')
responsetype: Response format (typically 'json')
```

### Security Features

**IP-Based Restrictions**
- Default: External API access restricted by IP
- Configuration: Setup → General Settings → Security
- Management: Add/remove allowed IP addresses with descriptive notes
- Alternative: Configure `$access_key` in configuration.php to bypass IP restrictions

**Role-Based Access Control (RBAC)**
- Implemented in WHMCS v7.4+
- Per-credential permission management
- Granular authorization across all API endpoints
- Recommended: Create role-specific credentials for each integration

**OAuth Support**
- Access tokens for session-based authentication
- Requires valid API Client Credential Identifier and Secret
- Enables delegated access without sharing admin credentials

**Legacy Support**
- Prior to WHMCS v7.2: Admin username + md5(admin_password)
- Not recommended for production deployments
- Deprecation timeline not yet announced

### Access Control Best Practices

```
1. Generate unique API credentials per integration (not per-admin)
2. Enable IP restriction to trusted integration servers
3. Apply least-privilege RBAC roles (read-only where possible)
4. Store secrets in secure key management system (not in code)
5. Enable API debugging in configuration.php for troubleshooting only
6. Audit API access logs in Activity Log
```

---

## Core API Capabilities

### 1. Client Management

**Available Endpoints**: 140+ API functions across 15 functional areas

#### AddClient
- **Purpose**: Create new client account
- **Required Parameters**: firstname, lastname, email, address, city, state, postcode, country, phonenumber, password
- **Optional Parameters**: companyname, clientgroup, language, currency, customfields (base64-encoded serialized array)
- **Response**: clientid, userid
- **Use Case**: Automated customer onboarding from InfraFabric registration

#### GetClients
- **Purpose**: Retrieve client list matching criteria
- **Parameters**: limitnum, limitstart, sortby, searchquery
- **Response**: clientid, firstname, lastname, companyname, email, datecreated, groupid, status
- **Use Case**: Sync customer list between InfraFabric and WHMCS

#### UpdateClient
- **Purpose**: Modify existing client details
- **Parameters**: clientid, firstname, lastname, email, address, city, state, postcode, country, phonenumber
- **Supports**: Company name, language preference, currency, status updates
- **Use Case**: Update customer profile changes from InfraFabric

#### GetClientsDetails (Deprecated)
- **Status**: Deprecated (may be removed in future versions)
- **Alternative**: Use GetClients for basic data, GetClientsProducts for service listing

#### GetClientGroups
- **Purpose**: Retrieve client group definitions
- **Response**: id, groupname, groupcolour, discountpercent, susptermexempt, separateinvoices
- **Use Case**: Understand tiered billing structures in WHMCS

#### GetContacts / AddContact / UpdateContact / DeleteContact
- **Purpose**: Manage client sub-contacts (multiple contacts per client)
- **Use Case**: Handle multiple billing/technical contacts per customer

#### Client Notes & Custom Fields
- **Client Notes**: Available in GetClientsDetails response
- **Custom Fields**: Base64-encoded serialized array format (complex but supported)
- **Implementation**: Custom field IDs must be known in advance

### 2. Product & Service Management

**Core Concept**: Products are service offerings; Orders are customer purchases

#### GetProducts
- **Purpose**: Retrieve product/service definitions
- **Parameters**: Filterable by product ID
- **Response**: productid, name, description, pricing, module, servertype
- **Use Case**: List available service offerings from InfraFabric

#### AddOrder
- **Purpose**: Create new order for customer
- **Parameters**: userid (clientid), pid (productid), domain (for domain registrations), customfields, configoptions
- **Returns**: orderid, serviceids, addonids, domainids, invoiceid
- **Workflow**: Must call AcceptOrder to complete order processing
- **Critical**: If AutoSetup not configured, admin approval required

#### AcceptOrder
- **Purpose**: Accept/approve pending order (required after AddOrder)
- **Parameters**: orderid
- **Automation**: Triggers provisioning if configured
- **Use Case**: Automate order approval and provisioning workflow

#### GetClientsProducts
- **Purpose**: Retrieve customer's active services
- **Response**: clientid, serviceid, orderid, productid, module, status, domain, nextinvoicedate, overideautosuspend
- **Use Case**: List customer's active services in InfraFabric dashboard

#### GetClientsDomains
- **Purpose**: Retrieve customer's registered domains
- **Response**: domainid, domainname, registrar, type (registration/transfer), regdate, expdate, status
- **Use Case**: Domain inventory tracking and renewal management

#### UpdateClientProduct
- **Purpose**: Modify active service/subscription
- **Parameters**: serviceid, productid, configoptions, customfields, notes
- **Use Case**: Handle service upgrades, downgrades, configuration changes

#### GetOrders
- **Purpose**: Retrieve order history and details
- **Parameters**: userid, orderid, ordernum, status
- **Response**: orderid, ordernum, userid, date, amount, paymentmethod, invoiceid, status
- **Use Case**: Order history and reconciliation

### 3. Invoicing & Payment Processing

**Core Workflow**: Order → Invoice → Payment → Service Activation

#### CreateInvoice
- **Purpose**: Generate invoice from order or manual entry
- **Parameters**: userid, status, paymentmethod, taxrate, date, duedate, items (descriptions + amounts)
- **Returns**: invoiceid
- **Automation**: Can trigger payment reminders and late fees
- **Use Case**: Billable resource tracking from InfraFabric

#### GenInvoices
- **Purpose**: Batch generate invoices for due renewals
- **Parameters**: Automatic based on service renewal dates
- **Use Case**: Scheduled billing cycle automation

#### GetInvoices
- **Purpose**: Retrieve invoice details
- **Parameters**: userid, invoiceid, orderby, limitnum, limitstart
- **Response**: invoiceid, userid, invoicenum, date, duedate, datepaid, total, status, paymentmethod
- **Use Case**: Invoice lookup, accounting integration, payment status tracking

#### GetInvoice (Singular)
- **Purpose**: Get detailed single invoice data
- **Response**: Full invoice details with line items and payment history
- **Use Case**: Detailed invoice view for audit trails

#### AddInvoicePayment
- **Purpose**: Record payment against invoice
- **Parameters**: invoiceid, transid (transaction ID), gateway (payment processor identifier), date
- **Behavior**: Automatically marks invoice Paid if balance reduces to $0.00
- **Critical**: Manual status change to Paid does NOT trigger payment automation
- **Use Case**: Record external payments, refunds, credits

#### ApplyCredit
- **Purpose**: Apply client account credit to invoice
- **Parameters**: clientid, amount, description
- **Use Case**: Apply promotional credits, refunds, account balance

### 4. Domain Management

#### DomainRegister
- **Purpose**: Initiate domain registration via registrar module
- **Parameters**: domainid
- **Triggers**: AfterDomainRegister hooks upon completion
- **Requirements**: Registrar module must be configured
- **Use Case**: Automated domain provisioning

#### DomainTransfer
- **Purpose**: Initiate domain transfer via registrar module
- **Parameters**: domainid
- **Triggers**: AfterDomainTransfer hooks
- **Use Case**: Domain migration and consolidation

#### GetClientsDomains
- **Purpose**: List customer domains
- **Response**: Full domain lifecycle data (registration, expiry, status)
- **Use Case**: Domain inventory and renewal management

#### DomainGetNameservers
- **Purpose**: Retrieve domain nameserver configuration
- **Parameters**: domainid
- **Response**: nameserver array
- **Use Case**: DNS routing verification

#### DomainGetWhoisInfo
- **Purpose**: Retrieve domain WHOIS contact information
- **Parameters**: domainid
- **Response**: Registrant, admin, tech, billing contact details
- **Use Case**: WHOIS privacy and contact management

### 5. Support Ticket System

#### OpenTicket
- **Purpose**: Create support ticket
- **Parameters**: deptid, subject, message, clientid, priority (Low/Medium/High)
- **Optional**: markdown support, attachments, preventClientClosure flag
- **Response**: ticketid, ticketnumber
- **Use Case**: Automated support escalations for InfraFabric issues

#### GetTickets
- **Purpose**: Retrieve ticket list matching criteria
- **Parameters**: userid, deptid, status, limitnum, limitstart
- **Response**: Array of tickets with full details
- **Use Case**: Support ticket retrieval and integration

#### GetTicket (Singular)
- **Purpose**: Get detailed single ticket information
- **Response**: Full ticket with replies and attachment metadata
- **Use Case**: Detailed ticket viewing

#### GetTicketCounts
- **Purpose**: Retrieve ticket count statistics
- **Response**: Open, awaiting reply, answered counts per department
- **Use Case**: Ticket queue monitoring dashboard

#### GetTicketAttachment
- **Purpose**: Retrieve attachment from ticket
- **Parameters**: ticketid, attachmentid
- **Response**: File content (base64 for binary files)
- **Use Case**: Attachment management and archival

### 6. Product Addons (Upgradeable Features)

**Concept**: Optional add-ons to base services (e.g., extra storage, premium support)

#### GetClientsAddons
- **Purpose**: Retrieve customer add-ons
- **Response**: addonid, serviceid, addonname, status, quantity, billingcycle
- **Use Case**: Track supplementary service offerings

#### Module Integration
- Server modules can provide custom addon pricing and provisioning logic
- ConfigOptions allow product customization (e.g., RAM tiers, storage options)

---

## Pricing & Cost Analysis

### WHMCS License Costs

**Tier Structure** (Monthly, excluding VAT):

| Plan | Cost | Active Clients | Support | Notes |
|------|------|----------------|---------|-------|
| Plus | $29.95 | 250 | Email | Self-hosted |
| Professional | $44.95 | 500 | Email | Self-hosted |
| Business 1000 | $69.95 | 1,000 | Email + Live Chat | Priority Support |
| Business 2500 | $154.95 | 2,500 | Email + Live Chat | Priority Support |
| Business 5000 | $234.95 | 5,000 | Email + Live Chat | Priority Support |
| Business 10000 | $389.95 | 10,000+ | Email + Live Chat | Priority Support |

**Key Pricing Notes**:
- All licenses include 30-day money-back guarantee
- Effective January 1, 2026: Revised pricing structure for renewals
- Pricing does NOT include payment gateway processing fees
- Dedicated domain registrar accounts required (separate vendor cost)

### Payment Gateway Fees

WHMCS acts as billing aggregator but does not impose transaction fees. Individual gateway fees depend on:

**Major Gateway Cost Structure**:
- **Stripe**: 2.2% + $0.30 per transaction (standard credit card processing)
- **PayPal**: 2.2% + $0.30 per transaction (standard rates)
- **Authorize.net**: $0.10 per transaction + monthly fee
- **2Checkout**: 2.5% + $0.45 per transaction
- **Mollie**: Gateway-dependent (typically 1.2-2.5% + €0.25-0.50)

**Gateway Fee Management**:
- WHMCS Marketplace addons allow passing gateway fees to customers
- Available modules: Payment Gateway Fees & Allocator ($39-199), Payment Gateway Charges ($10/month)
- Features: Percentage/fixed fees, country-specific pricing, client exclusion rules

### Infrastructure for InfraFabric Integration Estimate

**Initial Setup Costs**:
- WHMCS License: ~$70-400/month (depending on client volume)
- Payment Gateway Accounts: $0-50/month setup per gateway
- Provisioning Module Development: 40-80 hours (custom or purchased)
- Integration Development: 20-40 hours

**Annual Cost for Typical Deployment**:
- WHMCS License: $840-4,800
- Payment Gateways: $0-600
- Hosting/Infrastructure: $100-500
- Professional Services (if needed): $2,000-5,000

**Cost Benefit**: Eliminates custom billing development; industry-standard automation

---

## Automation Hooks & Webhooks

### Hook Types

WHMCS provides two hook categories:

#### 1. Action Hooks
- **Purpose**: Execute custom code when events occur in WHMCS
- **Invocation**: Direct PHP execution (not webhooks)
- **Location**: `/includes/hooks/` directory or module `hooks.php` file
- **No Built-in Webhooks**: WHMCS hooks are synchronous PHP, not HTTP webhooks

**Key Payment/Billing Hooks**:

| Hook Name | Trigger | Use Case |
|-----------|---------|----------|
| InvoicePaidPreEmail | Invoice marked paid (before email) | Custom payment processing |
| InvoicePaid | Invoice marked paid (after email) | Notification, logging, external sync |
| AfterPaymentGatewayCallback | Payment gateway callback received | Payment reconciliation |
| BeforeOrderCreate | Before order creation | Order validation, custom logic |
| AfterOrderCreate | After order created | Notification, logging |
| AcceptOrder | Order accepted/approved | Provisioning trigger |

**Key Service Lifecycle Hooks**:

| Hook Name | Trigger | Module |
|-----------|---------|--------|
| AfterModuleCreate | Service provisioned | Provisioning |
| AfterModuleChangePackage | Service upgraded/downgraded | Provisioning |
| AfterModuleSuspend | Service suspended | Provisioning |
| AfterModuleUnsuspend | Service unsuspended | Provisioning |
| AfterModuleTerminate | Service terminated/deleted | Provisioning |

#### 2. Module Hooks
- **Location**: `/modules/servers/modulename/hooks.php`
- **Detection**: Detected when module activated
- **Reload**: Changes require re-saving product/registrar configuration

**Module Hook Reload Methods**:
- Provisioning/Server Modules: Configuration → Products/Services → Save Changes
- Registrar Modules: Configuration → Domain Registrars → Save Changes
- Addon Modules: Configuration → Addon Modules → Save Changes

### Webhook Integration (Payment Gateways)

**Stripe Example**:
- WHMCS automatically generates Stripe WebHook Endpoint Secret
- Stripe sends events to WHMCS callback endpoint
- WHMCS automatically updates customer card/payment status
- Configuration: Configuration → Apps & Integrations → Stripe

**Note**: WHMCS itself does not provide HTTP webhooks for external systems. External integrations must poll WHMCS API or rely on:
1. Internal action hooks (PHP) for in-process notifications
2. Payment gateway webhooks (for payment events)
3. Scheduled cron jobs with API polling

### Hook Debugging

**Enable Debugging**:
- Configuration → System Health → Check Hooks Debug Mode → Save Changes
- **Warning**: Creates high-volume Activity Log entries
- **Best Practice**: Enable only during active development, disable for production

---

## SDK & API Implementation

### API Interface Type

**WHMCS API Model**:
- **Type**: HTTP POST-based API (not REST)
- **Endpoint**: `/includes/api.php` relative to WHMCS installation
- **Method**: HTTP POST requests with form data
- **Response Format**: JSON (default), XML, or raw response types

**No Official SDK**:
- WHMCS does not provide an official SDK
- No native REST API (custom wrappers exist in community)
- PHP integration: Direct CURL calls to `/includes/api.php`

### Official Code Examples

**Sample Code Location**: https://developers.whmcs.com/api/sample-code/

**Basic PHP Example**:
```php
$url = 'https://yourdomain.com/includes/api.php';
$postData = array(
    'identifier' => 'YOUR_API_IDENTIFIER',
    'secret' => 'YOUR_API_SECRET',
    'action' => 'GetClients',
    'responsetype' => 'json',
    'limitnum' => 10
);

$curl = curl_init();
curl_setopt_array($curl, array(
    CURLOPT_URL => $url,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_CUSTOMREQUEST => 'POST',
    CURLOPT_POSTFIELDS => http_build_query($postData),
));

$response = curl_exec($curl);
curl_close($curl);

$result = json_decode($response, true);
```

### Community Wrappers

**Node.js**: `node-whmcs` (NPM package available)
**Python**: `whmcs-restapi` (PyPI package, unofficial REST wrapper)
**Ruby**: `whmcs-api` gem available

### Response Types

**Supported Formats**:
- JSON (recommended): `responsetype=json`
- XML: `responsetype=xml`
- Raw response format available

**Standard Response Structure**:
```json
{
  "result": "success",
  "clientid": 123,
  "userid": 456,
  "notes": "Client description"
}
```

**Error Response**:
```json
{
  "result": "error",
  "message": "Email or Password Invalid"
}
```

---

## Payment Gateway Integrations

### Supported Gateways (80+)

WHMCS includes native integration with major payment processors:

**Included by Default**:
- Stripe (most popular for SaaS)
- PayPal (Basic, Payments, Card Payments variants)
- Authorize.net
- 2Checkout
- Mollie
- Direct Debit / SEPA

**Marketplace Available** (100+ total):
- Amazon Pay
- Apple Pay
- Google Pay
- Bitpay (cryptocurrency)
- Various regional gateways

### Gateway Configuration (WHMCS 8.6+)

**Location**: Configuration → Apps & Integrations → [Gateway Name]

**Setup Steps**:
1. Generate API keys at gateway provider dashboard
2. Enter credentials in WHMCS configuration
3. Configure webhook endpoints (if applicable)
4. Test transaction to verify integration
5. Enable for customers

### Key Gateway Features by Provider

**Stripe**:
- Automatic card dispute handling
- Strong Customer Authentication (SCA/3D Secure)
- Subscription billing support
- Balance view in WHMCS admin
- WebHook automatic updates

**PayPal**:
- Multiple variants: Basic, Payments Pro, Card Payments
- IPN (Instant Payment Notification) webhooks
- Subscription/recurring billing support
- Multi-currency support

**Authorize.net**:
- Credit card merchant processor
- CIM (Customer Information Manager) for card storage
- PCI compliance through hosted forms
- Automated recurring billing

### Payment Gateway Fee Management

**Built-in**: WHMCS doesn't charge fees (only gateway fees apply)

**Addon Solutions**:
- Payment Gateway Fees & Allocator module ($39-199 one-time)
- Payment Gateway Charges module ($10/month)
- Features: Per-gateway fixed/percentage fees, country-specific, tiered

### Payment Flow Automation

**Invoiced → Attempted Payment → Success/Failure**:
1. Invoice generated and emailed
2. Client pays via gateway
3. Gateway callback received at WHMCS webhook endpoint
4. InvoicePaid hook triggered
5. Service provisioning/activation occurs
6. Client notified

---

## Hosting Panel Integrations

### Native Control Panel Support

WHMCS provides server modules for automated account provisioning:

#### cPanel/WHM (Most Common)

**Capabilities**:
- Automated cPanel account creation/deletion
- Suspension/unsuspension on WHMCS actions
- Reseller account management
- Addon domains configuration
- Password resets

**Module**: Built-in cPanel module
**Config Location**: Products → Edit Product → Server Details
**Server Type Selection**: Requires cPanel-enabled server configured in WHMCS

**Enhanced Options**:
- cPanel Extended module (ModulesGarden) for deeper customization
- Keeps customers within WHMCS instead of redirecting to cPanel

#### Plesk

**Capabilities**:
- Account provisioning and management
- Instant sync between Plesk and WHMCS
- Domain management
- Reseller hosting automation

**Module**: Built-in Plesk module
**Configuration**: Products → Edit Product → Server Details
**Plesk Extended** (ModulesGarden): Enhanced features for white-label hosting

#### DirectAdmin

**Capabilities**:
- Automated shared/reseller hosting provisioning
- Account lifecycle management (create, suspend, terminate)
- Named reseller support
- User management

**Module**: Built-in DirectAdmin module
**Enhanced**: DirectAdmin Extended (ModulesGarden) for advanced features

#### Other Panels
- **SolusVM**: VPS/dedicated server automation
- **Virtualizor**: Cloud infrastructure automation
- **Custom**: Write provisioning modules for any infrastructure

### Provisioning Module Architecture

**Module Location**: `/modules/servers/panelname/`

**Core Functions** (all required):
- `MetaData()`: Module definition and capabilities
- `TestConnection()`: Verify connection to control panel
- `CreateAccount()`: Provision new hosting account
- `SuspendAccount()`: Suspend customer account
- `UnsuspendAccount()`: Reactivate suspended account
- `TerminateAccount()`: Delete/remove customer account

**Optional Functions**:
- `ChangePassword()`: Reset customer password
- `ChangePackage()`: Upgrade/downgrade service
- `AdminArea()`: Custom admin interface
- `ClientArea()`: Custom client interface
- Custom functions for panel-specific operations

---

## WHMCS Marketplace & Extensions

### Extension Categories

**1. Provisioning Modules** (100+)
- Hosting infrastructure providers
- VPS/Cloud platforms
- Domain registrars
- SSL certificate providers
- Email services

**2. Payment Gateway Modules** (80+)
- Credit card processors
- PayPal variants
- Cryptocurrency processors
- Regional payment methods

**3. Addon Modules** (200+)
- Feature enhancements
- Business automation
- Reporting & analytics
- Client communication
- Custom functionalities

### Notable Marketplace Extensions for Hosting Providers

**Web Hosting Control Panels**:
- cPanel Extended / Plesk Extended / DirectAdmin Extended (ModulesGarden)
- WP Squared (WordPress hosting automation)
- WHMCS integrations for Acronis, Virtualizor, SolusVM

**Payment & Billing**:
- Payment Gateway Fees & Allocator
- Payment Gateway Charges
- Advanced credit/refund management
- Dunning management (payment recovery automation)

**Registrar Modules**:
- ISPAPI (Hexonet)
- Openprovider
- NameSilo
- OpenSRS
- RRPproxy/Key-Systems
- DonDominio
- Namesilo
- 100+ total registrar integrations

**Domain Extensions**:
- Domain management automation
- WHOIS privacy integration
- SSL certificate provisioning
- Domain monitoring and alerts

### Custom Module Development

**Official Resources**:
- Sample provisioning module on GitHub
- Complete developer documentation
- PHP class-based module system
- Hook system for extensibility

**Module Installation**:
1. Upload to `/modules/servers/` (provisioning) or `/modules/` (addons)
2. Navigate to Configuration → Products/Services or Addon Modules
3. Module appears in dropdown for activation
4. Configure credentials and test connection

---

## Implementation for InfraFabric

### Integration Architecture

**Typical Deployment**:

```
┌─────────────────┐
│   InfraFabric   │ (Core Infrastructure Platform)
├─────────────────┤
│  Provisioning   │ (VMs, Containers, Storage)
│  Management     │
└────────┬────────┘
         │ API Calls
         ▼
┌──────────────────────────────────────┐
│         WHMCS Billing System         │
├──────────────────────────────────────┤
│ • Customer Management                │
│ • Invoice & Payment Processing       │
│ • Service Provisioning Module        │
│ • Domain & SSL Management            │
│ • Support Ticket Integration         │
└──────────────────────────────────────┘
         │ Webhooks / Callbacks
         ▼
┌──────────────────────────────────────┐
│    Payment Gateways (Stripe, etc)    │
└──────────────────────────────────────┘
```

### Critical Integration Points

**1. Order → Provisioning Workflow**:
```
1. Customer purchases via WHMCS checkout
2. AddOrder API called (order created)
3. AcceptOrder API called (admin approval)
4. Service provisioning module triggered
5. Custom provisioning logic: Create InfraFabric resource
6. Service marked Active in WHMCS
7. Customer access credentials provided
```

**2. Service Lifecycle**:
```
Upgrade/Downgrade → UpdateClientProduct API
Suspension → AfterModuleSuspend hook
Reactivation → AfterModuleUnsuspend hook
Termination → AfterModuleTerminate hook
```

**3. Billing Automation**:
```
Recurring renewal → GenInvoices cron job
Payment received → AddInvoicePayment + InvoicePaid hook
Service activation → Custom provisioning module invoked
```

### Provisioning Module Development (InfraFabric)

**Estimated Effort**: 40-80 development hours

**Key Functions to Implement**:

```php
function infrafabric_MetaData() {
    // Define module capabilities
    return array(
        'DisplayName' => 'InfraFabric Cloud Platform',
        'APIVersion' => '1.1',
        'RequiresServer' => true,
        'ConfigFields' => array(
            'ApiKey' => array('Type' => 'password', 'Description' => 'InfraFabric API Key'),
            'ApiSecret' => array('Type' => 'password', 'Description' => 'InfraFabric API Secret'),
            'ApiEndpoint' => array('Type' => 'text', 'Default' => 'https://api.infrafabric.local'),
        ),
    );
}

function infrafabric_CreateAccount($params) {
    // Call InfraFabric API to create VM/container
    // Return array with serviceID, username, password, access URLs
}

function infrafabric_SuspendAccount($params) {
    // Call InfraFabric API to suspend resource
}

function infrafabric_UnsuspendAccount($params) {
    // Call InfraFabric API to resume resource
}

function infrafabric_TerminateAccount($params) {
    // Call InfraFabric API to delete resource
}

function infrafabric_ChangePackage($params) {
    // Call InfraFabric API to resize/reconfigure resource
}
```

### Integration Checklist

- [ ] WHMCS installation (Plus/Professional minimum for 250-500 clients)
- [ ] API credential generation and security configuration
- [ ] Payment gateway accounts (Stripe minimum, PayPal/Authorize.net recommended)
- [ ] Custom provisioning module development or marketplace purchase
- [ ] Server configuration in WHMCS (endpoint, credentials, capabilities)
- [ ] Product definition (pricing, configurable options, automation settings)
- [ ] Payment automation testing (invoice → payment → provisioning flow)
- [ ] Refund/cancellation workflow automation
- [ ] Client communication templates (welcome emails, renewal notices)
- [ ] Monitoring and alerts for failed provisioning
- [ ] Support ticket escalation procedures

---

## Current WHMCS Versions & Features

### WHMCS 8.8 (Latest Stable)

**Key Additions**:
- MySQL encrypted database connections support
- On-Demand Renewals feature (customers self-renew before WHMCS generates invoice)
- WP Squared WordPress hosting provisioning
- BizCN domain registrar API updates
- Stripe RBI compliance updates

**Compatibility**: PHP 8.1 + (extensive modernization)

### WHMCS 8.7 (Previous Stable)

**Key Additions**:
- 360 Monitoring integration
- CentralNic reseller domain registration
- Faster SSL certificate issuance
- NordVPN integration
- Legacy Smarty tag deprecation warnings

### Version Compatibility for InfraFabric

**Recommended**: WHMCS 8.8 or 8.7
**Minimum**: WHMCS 7.4 (for RBAC access control)
**PHP Support**: 8.1+ recommended (modern features)

---

## API Performance & Limitations

### Request/Response Considerations

**Rate Limiting**:
- WHMCS does not publicly document rate limits
- No documented throttling policies
- Recommended: Implement client-side throttling (1-2 second delays between requests)

**Pagination**:
- Supported via `limitnum` and `limitstart` parameters
- Recommended: Batch operations with pagination for large datasets
- GetClients, GetOrders, GetInvoices, GetTickets all support pagination

**Performance**:
- API operations are synchronous (no asynchronous queuing)
- Provisioning delays possible for large-scale orders
- Recommended: Async job processing layer for InfraFabric integration

### Limitations & Workarounds

**Limitation**: No native webhooks for WHMCS events
**Workaround**: Use action hooks (internal PHP) or implement polling cron jobs

**Limitation**: Custom fields require base64-encoded serialization
**Workaround**: Create helper functions to encode/decode custom field values

**Limitation**: No direct batch API operations
**Workaround**: Implement loop-based batch processing with rate limiting

**Limitation**: Limited error codes in responses
**Workaround**: Check error message strings and enable API debugging for detailed logs

---

## Error Handling & Debugging

### Response Format

**Success Response**:
```json
{
  "result": "success",
  "data": { ... }
}
```

**Error Response**:
```json
{
  "result": "error",
  "message": "Descriptive error message"
}
```

### Common API Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid IP | Calling IP not in allowed list | Add IP to Setup → Security |
| Invalid identifier or secret | Wrong credentials | Verify API credential pairs |
| Email or Password Invalid | Legacy auth format | Update to API credentials |
| Email address invalid | Email format error | Validate email syntax |
| Client does not exist | Invalid clientid | Verify client exists via GetClients |
| Timeout | Network/WHMCS unavailability | Implement retry logic with backoff |

### Debugging Tools

**Enable API Logging**:
```php
// In /configuration.php
$api_enable_logging = true;
```

**Check Activity Log**: Admin Area → Utilities → Activity Log → Filter by API calls

**WHMCS System Health**: Configuration → System Health → Check API status

---

## Business Model & Licensing

### WHMCS as Billing Platform

**Revenue Model for Hosting Providers**:
1. Customer pays invoice through WHMCS payment gateway
2. Payment gateway fees paid by hosting provider (2.2-2.5% + $0.30)
3. Hosting provider retains remainder as revenue
4. WHMCS takes no percentage (only subscription license cost)

**Example SaaS Pricing with WHMCS**:
- Virtual Machine: $25/month
- Payment processor fee: -$0.85 (3.2% + $0.30)
- WHMCS license allocation: -$2.00 (if $400/month for 200 customers)
- Net revenue: $22.15/month per customer

### Market Positioning

**Industry Standard**: De facto billing platform for hosting resellers
**Alternatives**:
- Blesta (similar, niche)
- OpenStack Billing (open source)
- Custom in-house solutions (significant development cost)

**WHMCS Advantage**: 15+ years market presence, 80+ gateways, extensive automation

---

## IF.TTT Research Citations

### Primary Documentation Sources

1. **WHMCS API Reference** - https://developers.whmcs.com/api-reference/
   - Comprehensive endpoint documentation
   - Code samples and response examples
   - Retrieved: 2025-11-14

2. **WHMCS Authentication Guide** - https://developers.whmcs.com/api/authentication/
   - API credential generation and management
   - RBAC access control model
   - OAuth implementation details
   - Retrieved: 2025-11-14

3. **WHMCS Pricing Page** - https://www.whmcs.com/pricing/
   - License tier structure and costs
   - Client limits per tier
   - Support inclusions
   - Retrieved: 2025-11-14

4. **WHMCS Provisioning Modules** - https://developers.whmcs.com/provisioning-modules/
   - Module architecture and lifecycle
   - Core function requirements
   - Integration patterns
   - Retrieved: 2025-11-14

5. **WHMCS Payment Gateways** - https://docs.whmcs.com/Payment_Gateways
   - Supported gateway list
   - Configuration procedures
   - Retrieved: 2025-11-14

6. **WHMCS Hooks Reference** - https://developers.whmcs.com/hooks/
   - Action hooks and event triggers
   - Module hook implementation
   - Hook debugging
   - Retrieved: 2025-11-14

7. **WHMCS Control Panel Integration** - https://docs.whmcs.com/Plesk
   - cPanel, Plesk, DirectAdmin integration
   - Server module configuration
   - Retrieved: 2025-11-14

8. **WHMCS Release Notes (v8.8, v8.7)** - https://docs.whmcs.com/releases/8-8/8-8-release-notes/
   - Current feature set and API additions
   - Version compatibility
   - Retrieved: 2025-11-14

### Secondary Research Sources

9. **WHMCS Marketplace** - https://marketplace.whmcs.com/
   - Extension ecosystem overview
   - Payment gateway integrations
   - Third-party provisioning modules
   - Retrieved: 2025-11-14

10. **WHMCS Blog - Getting Started with the WHMCS API** - https://blog.whmcs.com/133546/getting-started-with-the-whmcs-api
    - Practical integration guidance
    - Best practices
    - Retrieved: 2025-11-14

11. **WHMCS Sample Provisioning Module** - https://github.com/WHMCS/sample-provisioning-module
    - Official code examples
    - Module structure reference
    - Retrieved: 2025-11-14

12. **WHMCS Access Control** - https://developers.whmcs.com/api/access-control/
    - IP restriction configuration
    - RBAC model details
    - Retrieved: 2025-11-14

---

## Strategic Recommendations for InfraFabric

### Phase 1: Assessment (2-4 weeks)
1. Evaluate customer volume and billing complexity
2. Assess current payment processing infrastructure
3. Determine control panel standardization (cPanel/Plesk/DirectAdmin)
4. Identify custom feature requirements

### Phase 2: Pilot (4-8 weeks)
1. Deploy WHMCS Professional license (500 clients)
2. Integrate primary payment gateway (Stripe recommended)
3. Develop custom provisioning module for InfraFabric
4. Test full workflow: Order → Invoice → Payment → Provisioning

### Phase 3: Migration (8-12 weeks)
1. Data migration from existing billing system
2. Customer communication and training
3. Go-live with production WHMCS instance
4. Support ticket triage and troubleshooting

### Phase 4: Optimization (Ongoing)
1. Monitor API performance and scaling needs
2. Implement advanced automation (domain renewal, etc.)
3. Add secondary payment gateways as needed
4. Evaluate marketplace extensions for feature enhancement

### Estimated Implementation Timeline

| Component | Effort | Timeline |
|-----------|--------|----------|
| WHMCS setup & config | 40 hours | 2 weeks |
| Provisioning module dev | 60 hours | 4 weeks |
| Payment gateway setup | 20 hours | 1 week |
| Data migration | 80 hours | 4 weeks |
| Testing & QA | 60 hours | 3 weeks |
| **Total** | **260 hours** | **14 weeks** |

### Cost Estimate for Year 1

| Item | Cost |
|------|------|
| WHMCS License (Professional, annual) | $540 |
| Payment Processing (2.2% + $0.30 per transaction) | Variable* |
| Deployment & Integration (260 hours @ $150/hr) | $39,000 |
| Hosting & Infrastructure | $1,200 |
| **Total First Year** | **~$40,740 + processing fees** |

*Processing fees depend on transaction volume. Assuming 1,000 transactions/month at $25 average = $8,200/year in gateway fees.

---

## Conclusion

WHMCS represents a robust, industry-proven billing and automation platform ideally suited for InfraFabric's hosting service integration requirements. Its comprehensive API (140+ functions), extensive payment gateway support (80+), and native control panel integrations provide a solid foundation for scaling cloud hosting operations.

**Key Value Propositions**:
- Eliminates custom billing software development
- Proven infrastructure automation patterns
- Extensive third-party ecosystem (gateways, modules, extensions)
- Community support and documentation

**Integration Complexity**: Medium (40-80 hours for custom provisioning module)
**Time to Market**: 12-16 weeks from assessment to production
**ROI Timeline**: 6-12 months depending on customer acquisition rate

**Recommendation**: Proceed with Phase 1 assessment, focusing on control panel standardization and custom provisioning module development. Consider marketplace purchases for cPanel/Plesk/DirectAdmin extended modules to accelerate time-to-market.

---

## Appendix: Quick Reference

### Essential API Endpoints (InfraFabric Use Cases)

```
Customer Onboarding:
  AddClient → CreateInvoice → AddInvoicePayment

Service Provisioning:
  GetClients → AddOrder → AcceptOrder → [Provisioning Module Triggered]

Service Management:
  GetClientsProducts → UpdateClientProduct → [Change Package]

Billing & Payments:
  GetInvoices → AddInvoicePayment → ApplyCredit

Support Integration:
  OpenTicket → GetTickets → [Link to InfraFabric tickets]

Domain Management:
  GetClientsDomains → DomainRegister → DomainTransfer
```

### Configuration Quick Links

- API Credentials: Configuration → System Settings → Manage API Credentials
- Security: Setup → General Settings → Security (IP restrictions)
- Payment Gateways: Configuration → Apps & Integrations
- Products: Configuration → Products/Services
- Servers: Configuration → Products/Services → [Product] → Server Details
- Hooks Debug: Configuration → System Health → Hooks Debug Mode

---

**Document Version**: 1.0
**Last Updated**: 2025-11-14
**Next Review**: 2026-Q1 (version 8.9+ releases)
