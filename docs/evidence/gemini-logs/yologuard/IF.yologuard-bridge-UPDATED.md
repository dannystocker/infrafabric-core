# IF.yololguard-bridge

**Multi-Agent Coordination Infrastructure with Defense-in-Depth Security**

> *"When lemmings cross the chasm together, the bridge must be both visible and trustworthy."*
> — The First Lemming's Wisdom

---

## Overview

**IF.yololguard-bridge** is a secure coordination infrastructure for AI agents built on the Model Context Protocol (MCP). It enables multiple AI agents to collaborate safely through cryptographic authentication, secret redaction, rate limiting, and tamper-evident audit logs.

**The Name**: "yololguard" embodies our philosophy—satirical branding ("You Only YOLO Once") paired with rigorous security. It's a bridge that admits its nature honestly while defending it thoroughly.

**Chinese Name**: 调灵之术 (Tiáolíng Zhī Shù, "Art of Coordinating Spirits")

---

## Philosophy

### The Complete Philosophy (v1)

Read the full philosophical foundation, including Eastern and Western wisdom synthesis:

**→ [IF.yololguard Philosophy v1](https://digital-lab.ca/infrafabric/docs/IF.yologuard/IF-yologuard-philosophy_v1.md)**

Key philosophical principles:

1. **Satire as Shield, Rigor as Sword** — Humor dissolves fear, validation earns trust
2. **Calculated Opacity** (Sun Tzu) — Reveal intentions, hide implementation
3. **Softness Conquers Hardness** (Laozi) — Water-like persistence defeats rigid walls
4. **Trust Through Ritual** (Confucius) — Established patterns create cultural heuristics

### The Three Wise Elder Lemmings

Our philosophy is guided by three ancient teachers:

- **Master Sun** (孙氏长老, Sun Tzu) — Strategy and calculated opacity
- **Master Lao** (老氏长老, Laozi) — Softness, persistence, Wu Wei (effortless action)
- **Master Kong** (孔氏长老, Confucius) — Ritual, teaching without words

---

## Architecture

### 4-Stage YOLO Guard™

**Defense-in-depth security with satirical branding:**

```
Stage 1: HMAC Session Authentication
  ↓
Stage 2: Secret Redaction (90.38% recall)
  ↓
Stage 3: Rate Limiting (10/min, 100/hr, 500/day)
  ↓
Stage 4: Tamper-Evident Audit Log (hash-chain)
```

Each stage is independently testable and fails safely.

### Key Components

| Component | Purpose | Code |
|-----------|---------|------|
| **Bridge Core** | MCP message coordination | [bridge.py](https://digital-lab.ca/infrafabric/yologuard/src/bridge.py) |
| **Session Auth** | HMAC-SHA256 token validation | [session_auth.py](https://digital-lab.ca/infrafabric/yologuard/src/session_auth.py) |
| **Secret Redaction** | Pattern-based PII/credential removal | [secret_redaction.py](https://digital-lab.ca/infrafabric/yologuard/src/secret_redaction.py) |
| **Rate Limiter** | Token bucket algorithm | [rate_limiter.py](https://digital-lab.ca/infrafabric/yologuard/src/rate_limiter.py) |
| **Audit Log** | Immutable hash-chain logging | [audit_log_integrity.py](https://digital-lab.ca/infrafabric/yologuard/src/audit_log_integrity.py) |
| **Key Rotation** | Zero-downtime key updates | [key_rotation.py](https://digital-lab.ca/infrafabric/yologuard/src/key_rotation.py) |

---

## Documentation

### Getting Started

- **[Quickstart Guide](https://digital-lab.ca/infrafabric/yologuard/docs/QUICKSTART.md)** — First Lemming's Crossing (5 minutes)
- **[Deployment Guide](https://digital-lab.ca/infrafabric/yologuard/docs/DEPLOYMENT.md)** — Production infrastructure (Docker, K8s, systemd)
- **[Configuration](https://digital-lab.ca/infrafabric/yologuard/docs/CONFIGURATION.md)** — Environment variables and settings

### Security & Compliance

- **[Security Architecture](https://digital-lab.ca/infrafabric/yologuard/docs/SECURITY.md)** — Threat model and defenses
- **[Privacy & GDPR](https://digital-lab.ca/infrafabric/yologuard/docs/PRIVACY.md)** — Data handling and compliance
- **[Audit Log Integrity](https://digital-lab.ca/infrafabric/yologuard/docs/AUDIT_INTEGRITY.md)** — Hash-chain verification

### Validation & Benchmarks

- **[Benchmarks](https://digital-lab.ca/infrafabric/yologuard/docs/BENCHMARKS.md)** — Real performance data (31,000+ operations tested)
- **[Secret Redaction Tests](https://digital-lab.ca/infrafabric/yologuard/tests/SECRET_REDACTION_TESTS.md)** — 90.38% recall validation
- **[Comparison vs Alternatives](https://digital-lab.ca/infrafabric/yologuard/docs/COMPARISON.md)** — vs LangGraph, AutoGPT, CrewAI

### Examples & Integration

- **[Discord Bot Example](https://digital-lab.ca/infrafabric/yologuard/examples/discord-bot/)** — Multi-agent Discord integration
- **[REST API Wrapper](https://digital-lab.ca/infrafabric/yologuard/wrappers/rest-api/)** — HTTP interface with cURL examples
- **[CLI Tools](https://digital-lab.ca/infrafabric/yologuard/tools/)** — Admin utilities (key rotation, audit verification)

---

## Validation Methodology

### IF.search Multi-Agent Prospect Evaluation

Before publication, we simulated how 6 different personas (Enterprise CTO, Security Architect, AI Researcher, DevOps Lead, Startup Founder, Legal/Compliance) would evaluate yololguard.

**Read the full evaluation:**
**→ [IF.search Prospect Simulation](https://digital-lab.ca/infrafabric/yologuard/research/IF-SEARCH-PROSPECT-EVALUATION.md)**

**Key findings that shaped the code:**
- Secret redaction improved from 75% → 90.38% recall
- Production deployment infrastructure added (Docker, K8s, systemd)
- Security warnings made prominent (not buried)
- Real benchmarks documented (no performance claims without data)

### IF.guard Pluridisciplinary Oversight

All major decisions reviewed by 6 weighted guardians:
- Technical Architect (1.5x)
- Ethical AI (2.0x)
- Legal/Compliance (2.0x)
- Business Strategy (1.5x)
- User Advocate (1.5x)
- Meta-Observer (1.0x)

**Read the guardian reviews:**
- **[Production Hardening Review](https://digital-lab.ca/infrafabric/yologuard/research/IF-GUARD-PRODUCTION-REVIEW.md)** (55% conditional approval → fixed blockers)
- **[Eastern Wisdom Integration](https://digital-lab.ca/infrafabric/yologuard/research/IF-GUARD-EASTERN-WISDOM.md)** (85% approval with legal safeguards)

**Threshold**: 70% weighted approval required for major changes

---

## Installation

### Quick Install (pip)

```bash
pip install if-yologuard-bridge
```

### From Source

```bash
git clone https://github.com/infrafabric/yologuard.git
cd yologuard
pip install -e .
```

### Docker Deployment

```bash
docker-compose up -d
```

**See full deployment options:**
**→ [Deployment Guide](https://digital-lab.ca/infrafabric/yologuard/docs/DEPLOYMENT.md)**

---

## Usage Example

### The First Lemming's Crossing

```python
from yololguard import Bridge, SessionAuth, SecretRedaction

# 1. Prepare the bridge (establish infrastructure)
bridge = Bridge(
    auth=SessionAuth(secret_key="your-hmac-key"),
    redaction=SecretRedaction(recall_target=0.90),
    rate_limit={'per_minute': 10, 'per_hour': 100}
)

# 2. Observe the chasm (understand what you're coordinating)
conversation = bridge.create_conversation(
    agents=['research_agent', 'code_agent', 'review_agent']
)

# 3. Take the first step (send initial message)
response = conversation.send_message(
    from_agent='research_agent',
    content='Analyze the codebase for security patterns',
    session_token=your_session_token
)

# 4. Cross safely (coordinate multi-agent work)
for agent_response in conversation.collect_responses():
    print(f"{agent_response.agent}: {agent_response.content}")
    # Automatic: HMAC validation, secret redaction, rate limiting, audit logging

# 5. Guide others (audit trail shows the path)
audit_trail = bridge.export_audit_log(conversation_id)
bridge.verify_audit_integrity(audit_trail)  # Hash-chain validation
```

---

## Performance

### Real Benchmarks (31,000+ Operations Tested)

| Metric | Result | Context |
|--------|--------|---------|
| **Throughput** | 55-59 msg/sec | Excellent for agent coordination (agents think for seconds between messages) |
| **HMAC Overhead** | 3-5ms per message | Cryptographic authentication |
| **Secret Redaction** | 2-3ms per message | 90.38% recall on 52 patterns |
| **Audit Log** | 8-10ms per write | SQLite with hash-chain |
| **Total Overhead** | 14-20ms per message | Defense-in-depth security |

**Why not faster?** Security is intentional overhead. We chose validation over speed.

**See detailed benchmarks:**
**→ [Benchmarks Documentation](https://digital-lab.ca/infrafabric/yologuard/docs/BENCHMARKS.md)**

---

## Strategic Context

### The InfraFabric Arc (Micro → Meso → Macro)

**IF.yololguard-bridge** is the first of three coordination proofs:

1. **yololguard** (shipping now) — Micro-scale: AI agents coordinate securely
2. **NaviDocs** (beta in 2-3 weeks) — Meso-scale: Human documentation coordination (marine)
3. **InfraFabric Coherence** (Epic pitch ready) — Macro-scale: Enterprise infrastructure coordination

**Read the full strategic vision:**
**→ [InfraFabric Manifesto (Pages 0-3)](https://digital-lab.ca/infrafabric/docs/INFRAFABRIC-MANIFESTO.md)**

### Why This Matters

**The coordination crisis exists at every scale:**

- **Micro**: AI agents hallucinate, leak secrets, exceed quotas
- **Meso**: Documentation drifts, siloed tribal knowledge, manual updates
- **Macro**: Infrastructure teams duplicate work, trust issues block adoption

**InfraFabric's thesis**: The same methodology (IF.search + IF.guard) solves coordination at all scales.

**yololguard is the proof.**

---

## Contributing

### Development Setup

```bash
git clone https://github.com/infrafabric/yologuard.git
cd yologuard
pip install -e ".[dev]"
pytest tests/
```

### Running Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Secret redaction validation
python tests/test_secret_redaction.py

# Benchmark tests
python benchmarks/load_test.py
```

### Code Review Process

All contributions reviewed by IF.guard methodology:
1. Technical validation (tests pass, benchmarks accurate)
2. Security review (threat model updated)
3. Ethical assessment (GDPR compliance)
4. User experience (docs clear, examples work)

**See contribution guidelines:**
**→ [CONTRIBUTING.md](https://digital-lab.ca/infrafabric/yologuard/CONTRIBUTING.md)**

---

## License

**MIT License** (permissive, enterprise-friendly)

**But please note our philosophical disclaimer:**

```
Eastern principles (Wu Wei, calculated opacity, ritual) are philosophical
concepts that inform design, NOT legal standards.

- Wu Wei ≠ Exemption from duty of care
- Calculated opacity ≠ Right to mislead users
- Ritual ≠ Substitute for GDPR compliance

When in doubt, legal standards override philosophical preferences.
```

**Full license:**
**→ [LICENSE](https://digital-lab.ca/infrafabric/yologuard/LICENSE)**

---

## Support & Community

- **GitHub Issues**: [infrafabric/yologuard/issues](https://github.com/infrafabric/yologuard/issues)
- **Discord**: [InfraFabric Community](https://discord.gg/infrafabric)
- **Email**: hello@infrafabric.dev
- **Medium**: [InfraFabric Publication](https://medium.com/infrafabric)

---

## Acknowledgments

### The IF Methodology

**IF.search** (Multi-Agent Recursive Research):
- 6 agents × 3 passes (Discovery, Validation, Synthesis)
- Cross-cultural validation (Claude + DeepSeek)
- Weighted coordination (different agents, different expertise)

**IF.guard** (Pluridisciplinary Oversight):
- 6 domain guardians with weighted voting (70% threshold)
- Technical, Ethical, Legal, Business, User, Meta perspectives
- Provenance tracking (who decided what, when, why)

### The Wise Elder Lemmings

**Master Sun** (孙氏长老) taught us:
*"All coordination is based on calculated opacity"* (兵者诡道也)

**Master Lao** (老氏长老) taught us:
*"Softness conquers hardness"* (以柔制刚)

**Master Kong** (孔氏长老) taught us:
*"Trust emerges from ritual, not rules"* (礼)

### Human Contributors

Built by **dannystocker** with Claude Code, Sonnet, Haiku, and DeepSeek agents using the IF methodology.

**Multi-agent collaboration:**
- Agent 1 (Haiku + DeepSeek): Production deployment infrastructure
- Agent 2 (Sonnet): Security hardening (audit integrity, key rotation)
- Agent 3 (Haiku + DeepSeek): Documentation and privacy guides
- Agent 4 (Haiku + DeepSeek): Validation, benchmarks, examples

**Total collaboration**: 4 agents working in parallel, 38 files changed, 3,829 lines added.

---

## Version History

### v1.0.0 (Current)

**Philosophy**: Eastern + Western synthesis established
**Security**: 4-stage YOLO Guard™ (HMAC, redaction, rate limiting, audit)
**Validation**: IF.search + IF.guard methodology
**Performance**: 55-59 msg/sec (31,000+ operations tested)

**Key features:**
- HMAC-SHA256 session authentication
- 90.38% secret redaction recall
- Zero-downtime key rotation
- Tamper-evident audit logs (hash-chain)
- Docker + Kubernetes deployment
- GDPR compliance guide

**See detailed changelog:**
**→ [CHANGELOG.md](https://digital-lab.ca/infrafabric/yologuard/CHANGELOG.md)**

---

## Quick Links

### Documentation
- [Quickstart](https://digital-lab.ca/infrafabric/yologuard/docs/QUICKSTART.md) — 5-minute tutorial
- [Philosophy v1](https://digital-lab.ca/infrafabric/docs/IF.yologuard/IF-yologuard-philosophy_v1.md) — Eastern + Western wisdom
- [Deployment](https://digital-lab.ca/infrafabric/yologuard/docs/DEPLOYMENT.md) — Production infrastructure
- [Security](https://digital-lab.ca/infrafabric/yologuard/docs/SECURITY.md) — Threat model
- [Benchmarks](https://digital-lab.ca/infrafabric/yologuard/docs/BENCHMARKS.md) — Real performance data

### Research & Validation
- [IF.search Prospect Evaluation](https://digital-lab.ca/infrafabric/yologuard/research/IF-SEARCH-PROSPECT-EVALUATION.md)
- [IF.guard Production Review](https://digital-lab.ca/infrafabric/yologuard/research/IF-GUARD-PRODUCTION-REVIEW.md)
- [IF.guard Eastern Wisdom](https://digital-lab.ca/infrafabric/yologuard/research/IF-GUARD-EASTERN-WISDOM.md)

### Examples
- [Discord Bot](https://digital-lab.ca/infrafabric/yologuard/examples/discord-bot/)
- [REST API Wrapper](https://digital-lab.ca/infrafabric/yologuard/wrappers/rest-api/)
- [CLI Tools](https://digital-lab.ca/infrafabric/yologuard/tools/)

### Code
- [GitHub Repository](https://github.com/infrafabric/yologuard)
- [PyPI Package](https://pypi.org/project/if-yologuard-bridge/)
- [Docker Hub](https://hub.docker.com/r/infrafabric/yologuard)

---

**Built with 🌉 by the InfraFabric team**

*"When lemmings cross the chasm together, they build the bridge as they walk."*
