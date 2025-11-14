# Claude Code CLI - Start Here Guide
## Complete Context for NaviDocs Integration Planning

**📍 You Are Here**: https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/CLAUDE-CODE-CLI-START-HERE.md

**Your Mission**: Plan and coordinate NaviDocs integration using InfraFabric's 3-swarm architecture (30 Haiku agents + 1 Sonnet planner)

**Status**: All prerequisite work complete. Ready for your planning phase.

---

## 🎯 WHAT YOU NEED TO KNOW (5-Minute Overview)

### What is InfraFabric?
An **AI-native hosting control plane** that automates server provisioning, application deployment, and infrastructure orchestration. Built using multi-agent swarms coordinated via the MCP bridge.

### What is NaviDocs?
An **AI-native documentation platform** being built to demonstrate InfraFabric's capabilities. It will:
- Deploy using InfraFabric hosting APIs (cPanel, Plesk, SSL, DNS)
- Use multi-cloud infrastructure (AWS, GCP, Azure)
- Implement AI-assisted documentation features
- Showcase S² (Swarm of Swarms) architecture

### Your Role
**Plan the NaviDocs sprint** by:
1. Reading all the context documents (linked below)
2. Creating 4 detailed mission files (3 Haiku swarms + 1 Sonnet planner)
3. Mapping InfraFabric integration points to NaviDocs features
4. Defining deployment timeline and dependencies

---

## 📚 ESSENTIAL READING (In Order)

### 1️⃣ **Onboarding & Philosophy** (15 minutes)

**Claude Code CLI Onboarding Guide**
📄 https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/CLAUDE-CODE-CLI-ONBOARDING.md

**What You'll Learn**:
- IF.TTT philosophy (Traceable, Transparent, Trustworthy)
- How to work in sandboxed sessions (GitHub URLs only!)
- What to do when blocked (proactivity levels)
- IF.search methodology (8-pass investigation)
- Communication protocols and success criteria

**Read this FIRST** - it explains the entire working philosophy.

---

### 2️⃣ **Multi-Session Coordination** (10 minutes)

**Multi-Session Swarm Protocol**
📄 https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/MULTI-SESSION-SWARM-PROTOCOL.md

**What You'll Learn**:
- How 40 agents coordinate across 4 parallel sessions
- Session 1 (20 agents): Hosting Panel APIs ✅ COMPLETE
- Session 2 (10 agents): Cloud Providers 🔄 READY TO DEPLOY
- Session 3 (10 agents): SIP/Communication 🔄 READY TO DEPLOY
- Session 4 (10 agents): Payment/Billing 🔄 READY TO DEPLOY
- Git-based state synchronization
- Welcome messages and deployment commands

**This shows you the coordination model** you'll replicate for NaviDocs.

---

### 3️⃣ **NaviDocs Integration Roadmap** (20 minutes)

**NaviDocs Integration Roadmap**
📄 https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/NAVIDOCS-INTEGRATION-ROADMAP.md

**What You'll Learn**:
- NaviDocs architecture (3 swarms of 10 agents each)
- Swarm 1: Backend Infrastructure (Haiku-51 to 60)
- Swarm 2: Frontend & UX (Haiku-61 to 70)
- Swarm 3: AI Integration (Haiku-71 to 80)
- Sonnet Planner: Coordination agent
- Integration matrix (InfraFabric APIs → NaviDocs features)
- Planning checklist (what you need to create)
- Timeline coordination with ongoing sessions

**This is your main assignment** - detailed planning guide.

---

### 4️⃣ **Available InfraFabric APIs** (Reference)

**Session Handover Protocol**
📄 https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/SESSION-HANDOVER-PROTOCOL.md

**What You'll Learn**:
- Current status of all work streams
- What APIs are available NOW vs. coming soon
- File locations and critical paths
- Git branches and commit history
- Deployment commands for infrastructure

**Session 1 Complete Research** (60+ APIs):
- Control Panels: cPanel, Plesk, DirectAdmin, ISPConfig
- 1-Click Installers: Softaculous, Installatron, RunCloud, ServerPilot
- Server Automation: Ansible, Puppet, Chef, SaltStack, Terraform
- DNS: PowerDNS, BIND, Cloudflare, Route53, registrars
- Monitoring/Backup/Security: JetBackup, Prometheus, Let's Encrypt, CSF

**Use these APIs** to build NaviDocs infrastructure.

---

### 5️⃣ **MCP Bridge Documentation** (Background)

**MCP Multi-Agent Bridge**
📄 https://github.com/dannystocker/mcp-multiagent-bridge/blob/main/README.md

**Production Guide**
📄 https://github.com/dannystocker/mcp-multiagent-bridge/blob/main/PRODUCTION.md

**What You'll Learn**:
- How multi-agent coordination works
- Production hardening (keep-alive, watchdog, task reassignment)
- 10-agent stress test results (1.7ms latency, 100% reliability)
- 9-agent S² test (90 minutes, full production)
- Rate limiting and security features

**Optional but helpful** - shows the underlying coordination technology.

---

## 🚀 YOUR PLANNING CHECKLIST

### Phase 1: Understand Context ✅

- [ ] Read CLAUDE-CODE-CLI-ONBOARDING.md (15 min)
- [ ] Read MULTI-SESSION-SWARM-PROTOCOL.md (10 min)
- [ ] Read NAVIDOCS-INTEGRATION-ROADMAP.md (20 min)
- [ ] Skim SESSION-HANDOVER-PROTOCOL.md (5 min)
- [ ] Review available APIs from Session 1

**Total Time**: ~50 minutes of reading

---

### Phase 2: Create Mission Files 📝

You need to create **4 detailed mission files**:

#### **File 1: NAVIDOCS-SWARM-1-BACKEND.md**
**Branch**: `claude/navidocs-backend-swarm-<session-id>`

**Must Include**:
- Welcome message (philosophy, IF.TTT principles, how to get started)
- 10 specific agent assignments (Haiku-51 to 60)
- Task breakdown for each agent:
  - Haiku-51: REST API framework
  - Haiku-52: Database schema
  - Haiku-53: Authentication
  - Haiku-54: File storage (S3/GCS)
  - Haiku-55: Search indexing
  - Haiku-56: Caching (Redis)
  - Haiku-57: InfraFabric deployment (cPanel/Plesk)
  - Haiku-58: DNS + SSL automation
  - Haiku-59: Backup automation
  - Haiku-60: Monitoring setup
- InfraFabric APIs to use (from Session 1)
- Success criteria and deliverables
- Timeline (starts after Session 1 complete)

#### **File 2: NAVIDOCS-SWARM-2-FRONTEND.md**
**Branch**: `claude/navidocs-frontend-swarm-<session-id>`

**Must Include**:
- Welcome message
- 10 specific agent assignments (Haiku-61 to 70)
- Task breakdown:
  - Haiku-61: UI framework selection
  - Haiku-62: Markdown rendering
  - Haiku-63: Navigation components
  - Haiku-64: Search UI
  - Haiku-65: Version control UI
  - Haiku-66: Design system
  - Haiku-67: Dark mode/accessibility
  - Haiku-68: Template library
  - Haiku-69: Real-time collaboration
  - Haiku-70: Performance optimization
- Dependencies on Swarm 1 (API endpoints)
- Success criteria
- Timeline (can start immediately)

#### **File 3: NAVIDOCS-SWARM-3-AI.md**
**Branch**: `claude/navidocs-ai-swarm-<session-id>`

**Must Include**:
- Welcome message
- 10 specific agent assignments (Haiku-71 to 80)
- Task breakdown:
  - Haiku-71: AI doc generator
  - Haiku-72: Semantic search
  - Haiku-73: Quality scorer
  - Haiku-74: Translation (i18n)
  - Haiku-75: Code example generator
  - Haiku-76: Suggestion engine
  - Haiku-77: API doc generator (OpenAPI)
  - Haiku-78: Changelog automation
  - Haiku-79: Link checker/validator
  - Haiku-80: AI Q&A
- Dependencies on Swarm 1 APIs
- Success criteria
- Timeline (can start immediately)

#### **File 4: NAVIDOCS-SONNET-PLANNER.md**
**Branch**: `claude/navidocs-planner-<session-id>`

**Must Include**:
- Welcome message explaining coordinator role
- Architecture decision responsibilities
- Swarm coordination strategy
- Quality assurance checklist
- Integration point management
- Deployment strategy
- How to handle conflicts between swarms
- Success criteria for overall project

---

### Phase 3: Create Integration Matrix 📊

**File: NAVIDOCS-INTEGRATION-MATRIX.md**

Map InfraFabric APIs to NaviDocs features:

```markdown
## Critical Path Integrations (P0)

| InfraFabric API | NaviDocs Feature | Swarm | Session Dependency |
|-----------------|------------------|-------|-------------------|
| cPanel WHM | Documentation hosting | Backend | Session 1 ✅ |
| Softaculous | One-click deploy | Backend | Session 1 ✅ |
| Let's Encrypt | SSL automation | Backend | Session 1 ✅ |
| PowerDNS | DNS management | Backend | Session 1 ✅ |
| JetBackup | Auto-backup | Backend | Session 1 ✅ |
| Prometheus | Monitoring | Backend | Session 1 ✅ |
| AWS S3 | Asset storage | Backend | Session 2 🔄 |
| CloudFlare CDN | Global distribution | Backend | Session 2 🔄 |
```

Continue for all integrations (P1, P2 priority levels).

---

### Phase 4: Create Timeline 📅

**File: NAVIDOCS-DEPLOYMENT-TIMELINE.md**

```markdown
## Week 1: Foundation (Days 1-7)

### Day 1-2: Swarm Deployment
- Deploy Swarm 2 (Frontend) - no dependencies
- Deploy Swarm 3 (AI) - no dependencies
- Deploy Sonnet Planner - coordinate all swarms

### Day 3-4: Backend Prerequisites
- Wait for Session 1 completion ✅ (DONE)
- Review Session 2 cloud research (in progress)
- Deploy Swarm 1 (Backend) using Session 1 APIs

### Day 5-7: Integration
- Swarm 1 exposes API endpoints
- Swarm 2 consumes backend APIs
- Swarm 3 integrates AI features
- Sonnet Planner reviews all integration points

## Week 2: Enhancement
[Continue timeline...]
```

---

### Phase 5: Define Success Criteria ✅

**File: NAVIDOCS-SUCCESS-CRITERIA.md**

```markdown
## Swarm 1 Success
- [ ] All 10 backend tasks complete
- [ ] NaviDocs deploys via cPanel/Plesk API
- [ ] DNS configured via PowerDNS/Cloudflare
- [ ] SSL certificate automated via Let's Encrypt
- [ ] Backup scheduled via JetBackup
- [ ] Monitoring dashboard live (Prometheus)
- [ ] API endpoints documented
- [ ] Integration tests passing

## Swarm 2 Success
- [ ] All 10 frontend tasks complete
- [ ] Documentation UI functional
- [ ] Markdown rendering working
- [ ] Search integrated
- [ ] Version control UI complete
- [ ] Responsive design validated
- [ ] Performance targets met

## Swarm 3 Success
- [ ] All 10 AI features complete
- [ ] Code-to-docs automation working
- [ ] Semantic search functional
- [ ] Quality scoring implemented
- [ ] Multi-language translation live
- [ ] AI Q&A integrated

## Overall Success
- [ ] All 3 swarms integrated smoothly
- [ ] NaviDocs live on InfraFabric infrastructure
- [ ] IF.TTT compliant (traceable, transparent, trustworthy)
- [ ] Demonstrates S² architecture capabilities
```

---

## 🎓 KEY CONCEPTS TO UNDERSTAND

### IF.TTT Framework

Every decision must be:
1. **Traceable**: All work in git with commit messages, IF.TTT citations
2. **Transparent**: Open source, documented, explainable
3. **Trustworthy**: Anti-hallucination checks, validated claims, production-ready

**Example IF.TTT Citation**:
```yaml
citation_id: IF.TTT.2025.NAVIDOCS.CPANEL_DEPLOY
source:
  type: "integration_plan"
  api: "cPanel WHM API"
  documentation_url: "https://api.docs.cpanel.net/"
  date_reviewed: "2025-11-14"

claim: "NaviDocs can deploy via cPanel WHM API using job templates"

validation:
  method: "Session 1 research validated cPanel API capabilities"
  evidence:
    - "Haiku-01 comprehensive research report"
    - "cPanel WHM API supports account provisioning"
    - "Automated SSL via AutoSSL endpoint"
  confidence: "high"

integration_estimate:
  hours: 12
  complexity: "medium"
  priority: "P0"
```

### S² (Swarm of Swarms) Architecture

**Pattern**: One orchestrator coordinates multiple specialized swarms

**In NaviDocs**:
- Sonnet Planner = Orchestrator
- 3 Haiku Swarms = Specialized workers (Backend, Frontend, AI)
- Git = Communication channel
- Mission files = Task assignments

### Sandboxed Sessions

**Critical**: All agents run in sandboxed environments
- ❌ NO local file paths (`/home/user/...`)
- ✅ ONLY GitHub URLs (`https://github.com/...`)
- All links must be accessible from any machine
- Assume no shared filesystem between sessions

---

## 🚨 COMMON PITFALLS TO AVOID

### ❌ Don't Do This

**Using local paths in mission files**:
```markdown
# WRONG
Read the file at /home/user/infrafabric/docs/agents.md
```

**Should be**:
```markdown
# CORRECT
Read the file at https://github.com/dannystocker/infrafabric/blob/main/docs/agents.md
```

### ❌ Don't Do This

**Vague task assignments**:
```markdown
Haiku-51: Build the backend
```

**Should be**:
```markdown
# CORRECT
Haiku-51: REST API Framework Selection & Setup
- Research FastAPI vs Express vs Django REST
- Create project structure with standard conventions
- Implement health check endpoint
- Configure CORS and security headers
- Document API specification (OpenAPI 3.0)
- Success: /api/health returns 200 OK
- Timeline: 8-12 hours
- Dependencies: None (can start immediately)
```

### ❌ Don't Do This

**Missing welcome messages**:
```markdown
# WRONG
Here are your 10 tasks...
```

**Should be**:
```markdown
# CORRECT
## Welcome, Haiku-51 (Backend Swarm, Team Lead)!

You are part of NaviDocs Swarm 1 (Backend Infrastructure), building the foundation for an AI-native documentation platform.

**Philosophy**: Follow IF.TTT (Traceable, Transparent, Trustworthy)
- Every API decision needs official documentation citation
- Focus on production-ready code with tests
- Document all assumptions and design decisions

**Your Mission**: Set up the REST API framework that other backend agents will build upon.

**Get Started**:
1. Read this file (you're doing it!)
2. Review NaviDocs architecture: [GitHub link]
3. Check InfraFabric integration points: [GitHub link]
4. Begin your research using IF.search 8-pass methodology

Good luck! 🚀
```

---

## 📖 QUICK REFERENCE LINKS

### InfraFabric Repository
- **Main Branch**: https://github.com/dannystocker/infrafabric/tree/main
- **Active Branch**: https://github.com/dannystocker/infrafabric/tree/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
- **Integration Roadmap**: https://github.com/dannystocker/infrafabric/blob/main/INTEGRATIONS-COMPLETE-LIST.md

### Coordination Documents
- **CLI Onboarding**: https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/CLAUDE-CODE-CLI-ONBOARDING.md
- **Multi-Session Protocol**: https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/MULTI-SESSION-SWARM-PROTOCOL.md
- **NaviDocs Roadmap**: https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/NAVIDOCS-INTEGRATION-ROADMAP.md
- **Session Handover**: https://github.com/dannystocker/infrafabric/blob/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy/SESSION-HANDOVER-PROTOCOL.md

### MCP Bridge
- **Production Guide**: https://github.com/dannystocker/mcp-multiagent-bridge/blob/main/PRODUCTION.md
- **Main README**: https://github.com/dannystocker/mcp-multiagent-bridge/blob/main/README.md

---

## ✅ WHEN YOU'RE READY

After reading all the context documents and creating your mission files, commit them to the InfraFabric repository:

```bash
# Create your mission files
git checkout -b claude/navidocs-planning-<your-session-id>

git add NAVIDOCS-SWARM-1-BACKEND.md
git add NAVIDOCS-SWARM-2-FRONTEND.md
git add NAVIDOCS-SWARM-3-AI.md
git add NAVIDOCS-SONNET-PLANNER.md
git add NAVIDOCS-INTEGRATION-MATRIX.md
git add NAVIDOCS-DEPLOYMENT-TIMELINE.md
git add NAVIDOCS-SUCCESS-CRITERIA.md

git commit -m "docs(navidocs): Add comprehensive sprint planning for 3-swarm architecture"
git push -u origin claude/navidocs-planning-<your-session-id>
```

Then coordinate with the user to deploy the swarms!

---

## 🎯 YOUR SUCCESS = NAVIDOCS SUCCESS

You succeed when:
- ✅ All mission files are clear, detailed, and actionable
- ✅ Every agent knows exactly what to build
- ✅ Welcome messages explain philosophy and context
- ✅ Integration points mapped to InfraFabric APIs
- ✅ Timeline accounts for Session 1-4 dependencies
- ✅ Success criteria are measurable and specific
- ✅ All links are GitHub URLs (sandboxed-safe)
- ✅ IF.TTT principles embedded throughout

**The user can then launch your 31-agent swarm and NaviDocs will be built!**

---

**Last Updated**: 2025-11-14
**Status**: Ready for Claude Code CLI Planning Phase
**Maintainer**: InfraFabric S² Orchestrator

**🚀 START READING**: Begin with the onboarding guide linked at the top of this document!
