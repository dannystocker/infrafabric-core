# API Research: SaltStack vs Terraform Cloud
**Team 3 - Server Automation | Haiku-12**

---

## SALTSTACK API

### 1. API Overview
- **Protocol**: REST API via CherryPy WSGI server
- **Module**: `rest_cherrypy` (netapi)
- **Deployment**: Native CherryPy server (production-ready, multi-threaded, SSL/TLS encrypted) or WSGI-compliant servers (Apache mod_wsgi, Nginx FastCGI)
- **Purpose**: Thin wrapper around Salt's Python API, HTTP-based equivalent to Salt CLI tools
- **Core Components**: Three client types:
  - **local**: Commands to minions (`salt` CLI equivalent)
  - **runner**: Master-side functions (`salt-run` CLI equivalent)
  - **wheel**: Master resource management (`salt-key` CLI equivalent)

### 2. Authentication
- **Primary Method**: Salt eauth system (external authentication backend configured in master config)
- **Session-Based**:
  - Obtain session ID via `/login` endpoint
  - Send via `X-Auth-Token` header or cookies (browser requests)
- **Direct Auth** (programmatic):
  - Pass `username`/`password`/`eauth` parameters directly
  - Alternative: Direct token in requests bypassing session handling
- **Security Note**: Must use HTTPS to prevent credential exposure (credentials sent in clear over HTTP)

### 3. Capabilities
- **State Execution**: Apply SaltStack states (`.sls` files) across minions for configuration management
- **Remote Execution**: Execute modules/functions on minions across thousands of systems in seconds
- **Job Management**: Query job cache, retrieve results, track execution status
- **Key Management**: Minion key operations via `/keys` endpoint
- **Event Stream**: Real-time event monitoring via `/events` (SSE) and `/ws` (WebSocket)
- **Webhooks**: External webhook integration via `/hook` endpoint
- **Asynchronous Operations**: High-performance async clients (3x faster LocalClient, 17x faster RunnerClient vs. sync)

**Key Endpoints**:
```
/              - RPC entry point
/login         - Authentication
/minions       - Minion management & job submission
/jobs          - Job queries & results
/events        - Event stream
/ws            - WebSocket connection
/run           - Direct execution with inline auth
/keys          - Key management
```

### 4. Integration
- **CI/CD Systems**: Jenkins, Travis, GitLab CI, GitHub Actions
- **Version Control**: Git integration for state files and configuration
- **Cloud Platforms**: AWS, Azure, Google Cloud, OpenStack
- **Containers**: Docker orchestration, container management
- **Monitoring**: Event bus integration with monitoring/observability systems
- **Third-Party Tools**: Puppet, Chef, Docker compatibility
- **Enterprise API**: SaltStack Enterprise offers exclusive API layer for proprietary system integration

### 5. Pricing
| Edition | Cost | Features |
|---------|------|----------|
| **Salt Open** (Free) | $0 | CLI-only, limited REST API, in-memory job cache, community support |
| **SaltStack Enterprise** | $120+/node/year | Enterprise console (web GUI), PostgreSQL job persistence, LDAP integration, RBAC, advanced reporting, priority support |

### 6. Infrastructure Assessment (IF)
**Strengths**:
- Agentless option (Python minions act as agents, lightweight)
- Sub-second command execution (thousands of systems in seconds)
- Powerful state management via YAML/Jinja2
- Flexible authentication (eauth, LDAP via Enterprise)
- Cost-effective for open source deployments

**Considerations**:
- REST API is "thin wrapper" - programmatic capabilities less mature vs. CLI
- Job data ephemeral in open source (requires external storage config)
- Enterprise features expensive for compliance/RBAC requirements
- Learning curve: Salt syntax and minion management concepts

**Use Case Fit**: Excellent for large-scale server automation, configuration management, and complex orchestration workflows. Open source suitable for non-regulated environments; Enterprise for RBAC/audit requirements.

### 7. Citation
- Official SaltStack Documentation: https://docs.saltproject.io/en/latest/ref/netapi/all/salt.netapi.rest_cherrypy.html
- Rest CherryPy API: https://docs.saltproject.io/en/latest/ref/netapi/all/salt.netapi.rest_cherrypy.html
- Remote Execution: https://docs.saltproject.io/en/latest/topics/execution/remote_execution.html

---

## TERRAFORM CLOUD API

### 1. API Overview
- **Protocol**: REST API v2 (JSON:API specification)
- **Base Path**: `/api/v2/`
- **Endpoint**: `https://app.terraform.io/api/v2/` (HCP Terraform)
- **Purpose**: Programmatic infrastructure management and workspace automation
- **Features**: Workspaces, runs, state management, configuration versioning, VCS integration, policy enforcement

### 2. Authentication
**Token Types**:
| Token Type | Purpose | Capabilities |
|------------|---------|--------------|
| **User Token** | Personal API access | Full user permissions, run operations |
| **Team Token** | CI/CD pipeline execution | Team-level plans/applies via automation |
| **Organization Token** | Admin operations | Team/workspace management (no run execution) |
| **Audit Trail Token** | Compliance/monitoring | Read-only audit log access |

**Implementation**:
- Header: `Authorization: Bearer <token>`
- Invalid/missing token: HTTP 401 response
- Content-Type: `application/vnd.api+json` (required)

### 3. Capabilities
- **Workspace Management**: Create, update, configure workspaces without VCS
- **Run Execution**: Plan and apply operations via API (API-driven workflow)
- **State Management**:
  - Remote state storage with automatic locking
  - Version history tracking
  - Secure download URLs (securely-generated secrets, valid 25 hours)
  - Endpoint: `GET /workspaces/:workspace_id/current-state-version`
- **Configuration Versions**: Upload and manage Terraform code versions
- **State Versioning**: Incremental state creation with finalized snapshots
- **VCS Integration**: Repository linking and webhook-driven runs
- **Policy Enforcement**: Sentinel policy checks and run tasks
- **Cost Estimation**: Resource-based cost previews

### 4. Integration
- **VCS Platforms**: GitHub, GitLab, Bitbucket, Azure DevOps
- **CI/CD Tools**: tfci (HashiCorp Docker tool for CI integration), GitHub Actions, Jenkins, etc.
- **Rate Limiting**: **30 requests/second** per user (some endpoints lower to prevent abuse)
  - Check `x-ratelimit-limit` header in responses
  - Rate limit information available for endpoint-specific thresholds
- **Workflow Types**:
  - VCS-driven (webhook on repo change)
  - API-driven (external tooling triggers runs)
  - CLI-driven (local Terraform runs)
- **State Locking**: Automatic state locking during operations

### 5. Pricing
| Tier | Cost | Features |
|------|------|----------|
| **Free** | $0 | 500 resources/month free, remote execution, VCS integration, private module registry, SSO, policy enforcement, run tasks |
| **Standard** | $0.00014/resource/hour | First 500 resources/month free, all free features |
| **Plus** | Custom | Enterprise standardization, custom configurations, dedicated support |
| **Enterprise (Self-Managed)** | Custom | On-premises, custom security/compliance, additional operational features |

*Note: Recent migration from per-user to resource-under-management (RUM) billing model*

### 6. Infrastructure Assessment (IF)
**Strengths**:
- Mature, stable API with comprehensive workspace/state management
- Strong state locking and version control
- VCS integration out-of-box (GitHub, GitLab, etc.)
- Flexible pricing (free tier viable for small teams)
- Excellent for CI/CD integration with native token types
- Official Go/Python SDKs + community libraries
- Feature entitlements queryable (graceful degradation)

**Considerations**:
- 30 req/sec rate limit requires caching strategy in high-frequency workflows
- Pricing shift to RUM model may impact cost predictability for large deployments
- Enterprise tier requires custom pricing negotiation
- JSON:API specification learning curve for new integrations

**Use Case Fit**: Ideal for infrastructure-as-code pipelines, team-based infrastructure automation, and organizations requiring managed/cloud-hosted Terraform state. Excellent for VCS-integrated workflows and compliance-heavy environments (audit trails, policy enforcement).

### 7. Citation
- Official HCP Terraform API Docs: https://developer.hashicorp.com/terraform/cloud-docs/api-docs
- Runs API Reference: https://developer.hashicorp.com/terraform/cloud-docs/api-docs/run
- Workspaces API: https://developer.hashicorp.com/terraform/cloud-docs/api-docs/workspaces
- State API: https://developer.hashicorp.com/terraform/cloud-docs/workspaces/state
- API-Driven Workflow: https://developer.hashicorp.com/terraform/cloud-docs/run/api

---

## COMPARATIVE SUMMARY

| Dimension | SaltStack | Terraform Cloud |
|-----------|-----------|-----------------|
| **API Type** | REST (CherryPy WSGI) | REST (JSON:API v2) |
| **Primary Use** | Server automation, config management | Infrastructure-as-code orchestration |
| **Authentication** | eauth (session/token) | Bearer tokens (user/team/org) |
| **State Model** | Job cache (ephemeral, requires config) | Remote state (versioned, locked) |
| **Rate Limit** | Not documented | 30 req/sec |
| **Open Source** | Yes (Salt Open) | No (cloud/enterprise only) |
| **Enterprise Cost** | $120+/node/year | Custom (starts $0.00014/resource/hr) |
| **Best For** | Large-scale minion orchestration | IaC pipelines & team collaboration |
| **Integration Depth** | Deep infrastructure control | VCS-native, policy-driven |

---

**Research Date**: November 2025
**Team**: Server Automation (Team 3)
**Researcher**: Haiku-12
