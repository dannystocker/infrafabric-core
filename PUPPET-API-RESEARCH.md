# Puppet Server & PuppetDB APIs - Research Report
**Team 3: Server Automation | Haiku-10**

---

## 1. API Overview

### Puppet Server HTTP API
Puppet Server provides two separately versioned APIs for infrastructure configuration management:

| API Family | Prefix | Purpose | Endpoints |
|---|---|---|---|
| **Configuration API** | `/puppet/v3` | Agent & node management | Catalog, Facts, Reports, File Content, Node Data |
| **Certificate Authority** | `/puppet-ca/v1` | PKI management | Certs, CSRs, Cert Status, CRL |

**Key Architecture:**
- RESTful JSON-based endpoints
- Explicit versioning in URL path (e.g., `/puppet/v3/catalog/node.example.com`)
- Authorization via `auth.conf` rules
- All endpoints follow pattern: `/puppet/v3/:indirection/:key?environment=:environment`

### PuppetDB Query API
- **Query Language:** Puppet Query Language (PQL) - string-based alternative to AST queries
- **Version:** v4 (latest, with migration path from v3)
- **Base Path:** `/pdb/query/v4/`
- **Queryable Entities:** Nodes, resources, facts, catalogs, events, reports

**Primary Endpoints:**
- `/catalogs` - Catalog storage & retrieval
- `/resources` - Resource state queries
- `/facts` - Node fact data
- `/nodes` - Node inventory
- `/events` - Puppet run events

---

## 2. Authentication & Authorization

### Certificate-Based Authentication
- **Default Method:** Mutual TLS with X.509 certificates
- **Requirement:** `pp_cli_auth` extension in certificate for CLI/API use
- **Certificate Authority:** Built-in Puppet Server CA manages cert lifecycle
- **Allowlist:** `/etc/puppetlabs/console-services/rbac-certificate-allowlist`
- **CLI Tool:** `puppetserver ca` command for CSR signing/revocation

**SSL Configuration:**
```
Server verifies agent certificate
Agent verifies server certificate (optional but recommended)
Mutual authentication prevents unauthorized access
```

### Token-Based Authentication (Enterprise)
- **RBAC API v1/v2:** Requires authentication tokens
- **Token Generation:** `puppet-access` CLI command
- **Use Case:** Programmatic API access, integrations
- **Token Format:** Bearer token in Authorization header

### Authorization Rules
- Controlled via `/etc/puppetlabs/puppetserver/conf.d/auth.conf`
- RBAC (Role-Based Access Control) in Enterprise edition
- Fine-grained per-endpoint permissions
- Certificate allowlisting for specific clients

---

## 3. Core Capabilities

### Manifest Compilation & Catalog Management
**Catalog Compilation Process:**
1. Primary server evaluates main manifest (global config)
2. Node-specific manifests applied based on facts
3. Conditional logic & hiera lookups resolved
4. Dependencies & ordering evaluated
5. Catalog serialized as JSON, delivered to agent

**API Capabilities:**
- `GET /puppet/v3/catalog/<certname>` - Request compilation
- Catalog versioning with transaction UUIDs
- Environment-aware compilation
- Hiera data integration

### Resource Management
**Resource Declaration & Types:**
- Managed resources: packages, files, services, users, commands, etc.
- Resource API defines provider implementations
- Desired state automation (convergence model)
- Dependency graph with ordering

**PuppetDB Resource Queries:**
- Query current resource state across infrastructure
- Filter by type, title, parameters, certname
- Aggregate resource counts by type
- Track resource changes over time

**Query Examples:**
```
resources[title, parameters] {
  type = 'File' and environment = 'production'
}

resources {
  certname = 'web01.example.com'
  order by type asc
  limit 100
}
```

### Catalog Storage & Retrieval
- **PuppetDB Catalogs Endpoint:** Stores full compilation output
- **Query Fields:** certname, version, environment, transaction_uuid
- **Wire Format:** JSON-serialized with UTF-8 encoding
- **Catalog Inputs:** Experimental v1 format for input tracking

### Fact Collection & Queries
- Facts endpoint returns structured fact data
- Aggregate fact queries (e.g., "all unique OS versions")
- Time-based fact history
- Structured fact support (JSON)

---

## 4. Integration & Rate Limiting

### Available SDKs

| Language | Project | Repository | Focus |
|---|---|---|---|
| **Go** | go-pe-client | github.com/puppetlabs/go-pe-client | Orchestrator, PuppetDB APIs |
| **Ruby** | puppet gem | RubyDoc.info | Native Puppet types, Resources |
| **Ruby** | forge-ruby | github.com/puppetlabs/forge-ruby | Puppet Forge API integration |
| **Python** | pypuppetdb | github.com/voxpupuli/pypuppetdb | PuppetDB wrapper (active) |
| **Python** | python-puppet-apis | github.com/leboncoin/python-puppet-apis | Admin tasks, CA bootstrap |

### Request Queue Management
Puppet Server uses **JRuby pooling** for request handling (not traditional per-client rate limits):

**Configuration** (`puppetserver.conf`):
```
max-queued-requests = 150
  └─ Requests exceeding queue size receive 503 Service Unavailable

max-retry-delay = 1800
  └─ Retry-After header (default: 30 min, matches agent run interval)

pe-jruby-max-active-instances = 4
  └─ Concurrent compilation threads
```

**Load Handling:**
- Adaptive backoff via Retry-After header
- Queue monitoring for capacity planning
- JRuby memory constraints limit parallelism
- Default agent run interval: 30 minutes

### Integration Points
- **Orchestration:** PE Orchestrator API (`/orchestrator/v1/`)
- **RBAC:** Role-based access control APIs
- **Activity Service:** Audit logging APIs
- **Third-party:** AWS, Splunk, VMware, ServiceNow, Slack, Jenkins
- **Webhook:** Custom integrations via Puppet hooks

---

## 5. Pricing Model

### Open Source Puppet
- **Cost:** Free
- **Support:** Community-based
- **SLA:** None
- **Management:** CLI/file-based configuration
- **Use Case:** Development, small deployments, advanced users

### Puppet Core (Free Developer Edition)
- **Cost:** Free up to 25 nodes; commercial licensing per-node (25+)
- **Support:** Access to support portal, CVE fixes (high/critical)
- **License:** Available for development use
- **Features:** Core agent + server, no GUI

### Puppet Enterprise (PE)
- **Pricing Model:** Subscription-based, per-node/year
- **Standard Support:** $112/node/year
- **Premium Support:** $199/node/year
- **Features:**
  - Enterprise GUI (console)
  - RBAC & token-based auth
  - Advanced reporting & analytics
  - Orchestrator & compliance features
  - Official SLAs for incidents/CVEs
  - Priority support ticketing
  - API integrations with 3rd-party platforms

**API Availability:**
- Open Source: `/puppet/v3`, `/puppet-ca/v1` endpoints
- PE: All above + Orchestrator, RBAC, Activity Service APIs
- PuppetDB: Included in all editions (can be self-hosted)

---

## 6. Infra Fabric Assessment (IF Assessment)

### Applicability to Infra Fabric
**Use Cases:**
- Node auto-discovery via PuppetDB queries
- Catalog compilation for declarative infrastructure
- Configuration enforcement with event-driven orchestration
- Resource state reporting via PuppetDB API

**Integration Readiness:**
- ✅ HTTP API fully documented & stable
- ✅ Open-source compatible (OSS + PuppetDB)
- ✅ Language support (Go, Python, Ruby SDKs)
- ✅ Multi-cloud agent support (AWS, Azure, GCP)
- ⚠️  Request queue mgmt requires capacity planning
- ⚠️  Certificate authority adds PKI complexity

### Architectural Fit
**Strengths:**
- Declarative configuration model aligns with IaC principles
- Distributed agent architecture enables scale
- Facts system provides node context (OS, IP, etc.)
- Resource API extensible for custom types

**Considerations:**
- PuppetDB external dependency (PostgreSQL backend)
- Agent-pull model (not push-based automation)
- Catalog compilation latency (can impact rapid convergence)
- No built-in secrets management (requires Hiera + external provider)

### Operational Requirements
- **Primary Server:** JRuby pooling, PostgreSQL for PuppetDB
- **Agents:** Ruby + Puppet agent (lightweight)
- **Network:** Bidirectional HTTPS (agents → server)
- **Certificate Rotation:** Manual or automated via infra

---

## 7. IF.TTT Citation

### Testing & Tooling Framework (IF.TTT)

**Test Scenario: Catalog Compilation API**
```bash
# Test manifest compilation
curl -k --cert client.pem --key key.pem \
  https://puppet.example.com:8140/puppet/v3/catalog/node01 \
  -H "Accept: application/json" \
  -d '{"facts": {...}}'
```

**Tooling Integration:**
- **Puppet CLI:** `puppet agent -t` (trigger run, fetch catalog)
- **PDK (Puppet Dev Kit):** Module testing, linting, metadata
- **PuppetDB CLI:** `puppetdb query` (PQL queries)
- **Bolt:** Task orchestration, agentless execution
- **rspec-puppet:** Unit testing for manifests

**Citation Example:**
```
Source: Puppet Server HTTP API v7
Reference: https://www.puppet.com/docs/puppet/7/server/http_api_index.html
Endpoint: /puppet/v3/catalog/{certname}
Method: POST/GET
Auth: TLS Certificate (pp_cli_auth extension required)
Format: JSON
```

**Technology Stack:**
| Layer | Technology | Version |
|---|---|---|
| Runtime | Ruby | 2.7+ |
| Server | JRuby | 9.x |
| Backend DB | PostgreSQL | 10+ |
| Query API | PuppetDB | 7.x+ |
| Query Language | PQL | v4 |
| Protocol | HTTP/1.1 | TLS 1.2+ |

**Validation Checklist:**
- [ ] Puppet Server & PuppetDB deployed
- [ ] Certificates generated & signed
- [ ] auth.conf rules configured
- [ ] Network connectivity verified (port 8140)
- [ ] PuppetDB backend operational
- [ ] Client certificate in certificate-allowlist
- [ ] API endpoint responses HTTP 200

---

## Summary Table

| Dimension | Details |
|---|---|
| **API Base** | `/puppet/v3` (config), `/puppet-ca/v1` (CA), `/pdb/query/v4` (PuppetDB) |
| **Auth** | TLS certs (mutual) + RBAC tokens (Enterprise) |
| **Query Language** | PQL (Puppet Query Language) v4 |
| **Request Handling** | JRuby queue (max-queued-requests configurable) |
| **Open Source** | Yes, fully functional API |
| **Enterprise APIs** | Orchestrator, RBAC, Activity Service (add $112-199/node/yr) |
| **SDKs** | Go, Ruby, Python (officially supported) |
| **Catalog Compilation** | POST to `/puppet/v3/catalog/{certname}` |
| **Resource Queries** | GET `/pdb/query/v4/resources` with PQL filters |

