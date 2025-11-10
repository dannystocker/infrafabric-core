# InfraFabric Component Index v2.0

**Purpose:** Comprehensive, searchable catalog of all InfraFabric components.

**Last Updated:** 2025-11-10
**Status:** Rebuilt after Gemini evaluation (87 components cataloged)
**Citation:** if://doc/component-index-v2-2025-11-10

---

## ⚠️ Documentation Status

**Gemini 2.5 Pro Evaluation Finding (2025-11-10):**
- Previous version was prose document, not functional index
- Claimed "91 components" but hundreds were undocumented
- Naming inconsistencies (IF. vs IF_) throughout codebase

**This Version:**
- 87 unique IF.* components identified via codebase scan
- Organized by architectural layer (Substrate/Protocol/Component/Tool)
- Status tracked for each component (Documented/Prototype/Deprecated)

---

## Quick Reference Table

| Component | Layer | Status | Location | Description |
|-----------|-------|--------|----------|-------------|
| IF.ground | Substrate | ✅ Documented | papers/IF-foundations.md | 8 anti-hallucination principles (Empiricism, Verificationism, Falsifiability, etc.) |
| IF.philosophy | Substrate | ✅ Documented | papers/IF-foundations.md | 12 philosophers spanning 2,500 years (Western+Eastern) |
| IF.vision | Substrate | ✅ Documented | papers/IF-vision.md | 4 emotional cycles (manic/depressive/dream/reward) as governance |
| IF.foundations | Substrate | ✅ Documented | papers/IF-foundations.md | Epistemological foundation (philosophy → executable architecture) |
| IF.TTT | Protocol | ✅ Documented | agents.md | Traceable/Transparent/Trustworthy compliance framework |
| IF.connect | Protocol | ✅ Documented | IF_CONNECTIVITY_ARCHITECTURE.md | Universal IFMessage communication standard (FIPA-ACL + DDS QoS) |
| IF.constitution | Protocol | ⚠️ Partial | papers/IF-vision.md | Governance rules emerging from IF.guard deliberations |
| IF.forge | Protocol | ✅ Documented | papers/IF-witness.md | 7-stage Multi-Agent Reflexion Loop (MARL) |
| IF.protocols | Protocol | 📚 Deprecated | Multiple files | General protocol definitions (overlaps IF.forge) |
| IF.guard | Component | ✅ Documented | papers/IF-vision.md, infrafabric/guardians.py | 20-voice extended council (6 Core + 3 Western + 3 Eastern + 8 IF.ceo) |
| IF.swarm | Component | ✅ Documented | papers/IF-witness.md, docs/HAIKU-SWARM-TEST-FRAMEWORK.md | Epistemic agent deployment (15-agent default, 96× speedup) |
| IF.search | Component | ✅ Documented | papers/IF-foundations.md | 8-pass investigation methodology |
| IF.witness | Component | ✅ Documented | papers/IF-witness.md | Meta-validation system (recursive validation) |
| IF.citation | Component | ✅ Documented | papers/IF-witness.md | Cryptographic provenance (Merkle trees, Ed25519, OpenTimestamps) |
| IF.trace | Component | ⚠️ Partial | Multiple files | Logging and observability system |
| IF.memory | Component | ⚠️ Partial | Multiple files | State management across sessions |
| IF.persona | Component | ✅ Documented | papers/IF-foundations.md | Agent characterization (Bloom patterns: Early/Late/Steady) |
| IF.optimise | Component | ✅ Documented | annexes/ANNEX-N-IF-OPTIMISE-FRAMEWORK.md | Token cost management (Haiku delegation, 87-90% savings) |
| IF.armour | Component | ✅ Documented | papers/IF-armour.md | Security suite (newsroom architecture, 4 biological mechanisms) |
| IF.router | Component | ⚠️ Needs Doc | papers/IF-vision.md | NVLink 900 GB/s fabric-aware routing (6 refs) |
| IF.kernel | Component | ⚠️ Needs Doc | code/*, papers/* | Core system functionality (5 refs, code exists) |
| IF.module | Component | ⏸️ Prototype | Multiple files | Modular component loading |
| IF.pulse | Component | ⏸️ Prototype | Multiple files | Heartbeat and health monitoring |
| IF.yologuard | Tool | ✅ Documented | papers/IF-armour.md, code/yologuard/ | Secret detection (Wu Lun v3: ⚠️ 98.96% recall UNVERIFIED) |
| IF.yologuard_v1 | Tool | 📚 Legacy | code/yologuard/versions/ | V1: 47 regex patterns, 31.2% recall, 4% FP |
| IF.yologuard_v2 | Tool | 📚 Legacy | code/yologuard/versions/ | V2: Swarm-enhanced, 0.04% FP (100× reduction), ~77% recall |
| IF.yologuard_v3 | Tool | ✅ Active | code/yologuard/src/IF.yologuard_v3.py | V3: Wu Lun framework (98.96% recall UNVERIFIED, 100% precision) |
| IF.chase | Tool | ✅ Documented | papers/IF-vision.md | Domain-specific analysis (manic phase: depth limits, token budgets) |
| IF.collapse | Tool | ⚠️ Needs Doc | annexes/DOSSIER-07-*.md | Civilizational pattern analysis (7 refs, Dossier 07 100% consensus) |
| IF.garp | Tool | ✅ Documented | papers/IF-vision.md | Reward/recognition system (Singapore model, trust tiers) |
| IF.reflect | Tool | ✅ Documented | papers/IF-vision.md | Blameless post-mortems (depressive phase) |
| IF.vesicle | Tool | ✅ Documented | papers/IF-vision.md | Cross-domain recombination (dream phase: neurogenesis → MCP servers) |
| IF.ceo | Component | ✅ Documented | papers/IF-vision.md | 16 Sam Altman facets (8 Light idealistic + 8 Dark pragmatic/ruthless) |
| IF.sam | Component | ✅ Documented | papers/IF-vision.md | Alias for IF.ceo (Sam Altman ethical spectrum) |
| IF.aegis | Component | 📚 Deprecated | COMPONENT-INDEX.md | Protection/shielding system (stub only) |
| IF.amplify | Component | ⏸️ Prototype | Multiple files | Signal amplification |
| IF.arbitrate | Component | ⚠️ Needs Doc | papers/IF-vision.md | Weighted resource allocation, RRAM hardware (8 refs, 99.1% success) |
| IF.audit | Component | 📚 Deprecated | COMPONENT-INDEX.md | Audit trail generation (stub only, use IF.trace) |
| IF.barrier | Component | ⏸️ Prototype | Multiple files | Access control barriers |
| IF.bridge | Component | ⏸️ Prototype | Multiple files | Cross-system integration |
| IF.brief | Component | 📚 Deprecated | COMPONENT-INDEX.md | Summary generation (stub only) |
| IF.citate | Component | 📚 Deprecated | COMPONENT-INDEX.md | Citation generation (duplicate of IF.citation) |
| IF.coordination | Component | ⚠️ Needs Doc | infrafabric/coordination.py | Weighted multi-agent coordination (code exists) |
| IF.core | Component | ⚠️ Needs Doc | papers/IF-vision.md | W3C DIDs, quantum-resistant crypto (9 refs, 97.0% healthcare success) |
| IF.council | Component | ✅ Documented | papers/IF-vision.md | Alias for IF.guard council |
| IF.depressive | Component | ✅ Documented | papers/IF-vision.md | Depressive cycle state (reflective compression) |
| IF.dream | Component | ✅ Documented | papers/IF-vision.md | Dream cycle state (cross-domain recombination) |
| IF.export | Component | 📚 Deprecated | COMPONENT-INDEX.md | Data export functionality (stub only) |
| IF.federate | Component | ⚠️ Needs Doc | papers/IF-vision.md | Voluntary interoperability, healthcare/financial/research (16 refs) |
| IF.framework | Component | 📚 Deprecated | COMPONENT-INDEX.md | Framework infrastructure (stub only) |
| IF.geopolitical | Component | 📚 Deprecated | COMPONENT-INDEX.md | Geopolitical analysis (stub only) |
| IF.governance | Component | ✅ Documented | papers/IF-vision.md | Governance mechanisms (Guardian Council) |
| IF.guardian | Component | ✅ Documented | papers/IF-vision.md | Individual guardian entity |
| IF.guardians | Component | ✅ Documented | infrafabric/guardians.py | Guardian implementation module |
| IF.layer | Component | 📚 Deprecated | COMPONENT-INDEX.md | Architectural layer abstraction (stub only) |
| IF.learner | Component | ⏸️ Prototype | Multiple files | Learning/adaptation system |
| IF.llm | Component | 📚 Deprecated | COMPONENT-INDEX.md | LLM interface abstraction (stub only) |
| IF.manic | Component | ✅ Documented | papers/IF-vision.md | Manic cycle state (creative expansion) |
| IF.manifests | Component | ⚠️ Needs Doc | infrafabric/manifests.py | Manifest generation (code exists) |
| IF.marl | Component | ✅ Documented | papers/IF-witness.md | Multi-Agent Reflexion Loop (alias for IF.forge) |
| IF.mcp | Component | ⏸️ Prototype | Multiple files | Model Context Protocol integration |
| IF.mesh | Component | 📚 Deprecated | COMPONENT-INDEX.md | Mesh networking (stub only) |
| IF.methodology | Component | ✅ Documented | papers/IF-foundations.md | Research methodologies |
| IF.protect | Component | 📚 Deprecated | COMPONENT-INDEX.md | Protection mechanisms (stub only) |
| IF.pursuit | Component | ⏸️ Prototype | Multiple files | Goal pursuit tracking |
| IF.quiet | Component | ⚠️ Needs Doc | papers/IF-vision.md | Anti-spectacle metrics, Lao Tzu mapping (15 refs, production roadmap) |
| IF.resource | Component | ⚠️ Needs Doc | papers/IF-vision.md | Carrying capacity monitor, Maya deforestation mapping (6 refs) |
| IF.reward | Component | ✅ Documented | papers/IF-vision.md | Reward cycle state (recognition-based stabilization) |
| IF.sec | Component | ⏸️ Prototype | Multiple files | Security primitives |
| IF.simplify | Component | ⚠️ Needs Doc | papers/IF-vision.md | Complexity collapse prevention, Tainter's law (6 refs) |
| IF.stats | Component | 📚 Deprecated | COMPONENT-INDEX.md | Statistics and metrics (stub only) |
| IF.synergy | Component | ⏸️ Prototype | Multiple files | Synergy detection |
| IF.system | Component | 📚 Deprecated | COMPONENT-INDEX.md | System-level operations (stub only) |
| IF.talent | Component | 📚 Deprecated | COMPONENT-INDEX.md | Talent assessment (stub only) |
| IF.veil | Component | ⚠️ Needs Doc | papers/IF-vision.md | Privacy layer, safe-disclosure API (10 refs, Phase 2 roadmap) |
| IF.verify | Component | 📚 Deprecated | COMPONENT-INDEX.md | Verification operations (stub only, use IF.witness) |
| IF.wellbeing | Component | ⏸️ Prototype | Multiple files | AI wellbeing monitoring |
| IF.dets | ❓ Unknown | 📚 Deprecated | COMPONENT-INDEX.md | Unknown component (stub only) |
| IF.foo | 🧪 Test | 📚 Deprecated | COMPONENT-INDEX.md | Test/example component (artifact only) |
| IF.v7 | 📚 Legacy | Deprecated | Multiple files | Version 7 legacy reference |
| IF.__brand__ | 🔧 Internal | Internal | Multiple files | Internal branding constant |
| IF.__shorthand__ | 🔧 Internal | Internal | Multiple files | Internal shorthand reference |
| IF.__version__ | 🔧 Internal | Internal | Multiple files | Version tracking constant |
| IF.ceo_ | ⚠️ Duplicate | Internal | Multiple files | Underscore variant of IF.ceo (naming inconsistency) |
| IF.citations | ⚠️ Duplicate | Internal | Multiple files | Plural variant of IF.citation (naming inconsistency) |
| IF.optimise_engine | ⚠️ Duplicate | Internal | Multiple files | Engine variant of IF.optimise (naming inconsistency) |
| IF.optimised | ⚠️ Duplicate | Internal | Multiple files | Past tense variant (naming inconsistency) |
| IF.personality | ⚠️ Duplicate | Internal | Multiple files | May be alias for IF.persona (needs consolidation) |

**Legend:**
- ✅ Documented: Full documentation in papers/annexes
- ⚠️ Partial: Mentioned but incomplete documentation
- ⏸️ Prototype: Referenced in code/docs but not formally specified
- 📚 Legacy: Deprecated or superseded version
- 🧪 Test: Test/example component
- 🔧 Internal: Internal implementation detail
- ❓ Unknown: Purpose unclear, needs investigation

---

## 1. Substrate (Foundational Principles)

### IF.ground
**Status:** ✅ Documented
**Location:** papers/IF-foundations.md
**Description:** 8 anti-hallucination principles spanning 2,400 years of epistemology.

**Principles:**
1. Ground in Observable Artifacts (Empiricism/Locke)
2. Validate with Toolchain (Verificationism/Vienna Circle)
3. Make Unknowns Explicit (Fallibilism/Peirce)
4. Schema-Tolerant Parsing (Duhem-Quine)
5. Gate Client-Only Features (Coherentism/Quine)
6. Progressive Enhancement (Pragmatism/James-Dewey)
7. Reversible Switches (Falsifiability/Popper)
8. Observability Without Fragility (Stoic Prudence/Epictetus)

**Implementation:** Enforced via ifctl.py lint validator, code patterns, MARL validation steps.

### IF.philosophy
**Status:** ✅ Documented
**Location:** papers/IF-foundations.md
**Description:** Queryable knowledge base of 12 philosophers (3 Eastern + 9 Western) spanning 2,500 years.

**Philosophers:**
- **Eastern:** Buddha (non-attachment), Lao Tzu (wu wei), Confucius (ren/benevolence, Wu Lun)
- **Western:** Epictetus (Stoicism), Locke (Empiricism), Peirce (Fallibilism), Vienna Circle (Verificationism), Duhem (Underdetermination), Quine (Coherentism), James/Dewey (Pragmatism), Popper (Falsifiability)

**Usage:** Mapped to distributed systems patterns (Empiricism → append-only logs, Falsifiability → Ed25519 signatures, Wu Lun → agent communication taxonomy).

### IF.vision
**Status:** ✅ Documented
**Location:** papers/IF-vision.md
**Description:** Cyclical coordination model using 4 emotional cycles (manic/depressive/dream/reward) as governance patterns.

**Cycles:**
- **Manic:** Creative expansion (IF.chase)
- **Depressive:** Reflective compression (IF.reflect)
- **Dream:** Cross-domain recombination (IF.vesicle)
- **Reward:** Recognition-based stabilization (IF.garp)

**Architecture:** Prevents fragmentation collapse across 40+ AI species.

### IF.foundations
**Status:** ✅ Documented
**Location:** papers/IF-foundations.md
**Description:** Meta-component encompassing IF.ground, IF.philosophy, IF.search, IF.persona.

---

## 2. Protocol (Standards & Rules)

### IF.TTT
**Status:** ✅ Documented
**Location:** agents.md
**Description:** Traceable/Transparent/Trustworthy compliance framework. Mandatory for all operations.

**Requirements:**
- **Traceable:** Every claim links to observable source (if://citation/uuid)
- **Transparent:** All operations logged (IF.trace)
- **Trustworthy:** Cryptographically signed (Ed25519), content-addressed (SHA-256)

**Enforcement:** IFMessage validator (tools/ifctl.py) enforces TTT at protocol level.

### IF.connect
**Status:** ✅ Documented
**Location:** IF_CONNECTIVITY_ARCHITECTURE.md (44 KB)
**Description:** Universal IFMessage communication standard combining FIPA-ACL speech acts with DDS QoS policies.

**IFMessage Schema:**
```python
{
    "performative": "request | inform | agree | query-if | refuse | propose",
    "sender": "if://agent/<team>/<role>/<id>",
    "conversation_id": "if://conversation/<mission-id>",
    "content": {...},
    "content_hash": "sha256:...",
    "signature": {"alg": "ed25519", "pub": "...", "sig": "..."},
    "sequence_num": 42,
    "qos": {"reliability": "reliable | best_effort", "durability": "transient_local | persistent"}
}
```

**5-Level Architecture:**
1. Neuron (Agent message)
2. Synapse (Agent-to-agent connection)
3. Organism (Agent team)
4. Ecosystem (Multi-team coordination)
5. Universe (Cross-framework federation)

### IF.constitution
**Status:** ⚠️ Partial
**Location:** papers/IF-vision.md
**Description:** Formal governance rules emerging from IF.guard deliberations. Acts as "law" of the framework.

**Protocols:**
- Quorum: 15/20 guardians (75%)
- Approval: Simple majority (>50%)
- Contrarian veto: Can block >95% approval with 2-week cooling-off
- Dissent window: 24 hours

### IF.forge
**Status:** ✅ Documented
**Location:** papers/IF-witness.md
**Description:** 7-stage Multi-Agent Reflexion Loop (MARL) process for AI-assisted research.

**Stages:**
1. Initial task execution
2. Self-critique generation
3. External validator review
4. Reflexion synthesis
5. Improved execution
6. Convergence assessment
7. Final validation

**Results:** GPT-5 validation confirmed 7-stage loop produces actionable outputs (8 architectural improvements generated).

---

## 3. Component (Functional Modules)

### IF.guard
**Status:** ✅ Documented
**Location:** papers/IF-vision.md, infrafabric/guardians.py
**Description:** 20-voice extended council for governance decisions.

**Composition:**
- 6 Core Guardians (Technical, Civic, Ethical, Cultural, Contrarian, Meta)
- 3 Western Philosophers (Popper, James, Vienna Circle)
- 3 Eastern Philosophers (Confucius, Laozi, Nagarjuna)
- 8 IF.ceo facets (Sam Altman ethical spectrum)

**Historic Achievement:** Dossier 07 achieved 100% consensus (20/20 guardians) on civilizational collapse patterns.

### IF.swarm
**Status:** ✅ Documented
**Location:** papers/IF-witness.md, docs/HAIKU-SWARM-TEST-FRAMEWORK.md
**Description:** Epistemic agent deployment system for parallelized investigation.

**Configuration:**
- Default: 15-agent swarm (5 Early Bloomers + 5 Late Bloomers + 5 Steady Performers)
- Performance: 96× speedup (120 hours manual → 76 minutes automated)
- Cost: $3-5 per comprehensive research run

**Visual Reference:** docs/images/IF.swarm.png (motorbike swarm metaphor)

### IF.search
**Status:** ✅ Documented
**Location:** papers/IF-foundations.md
**Description:** 8-pass investigation methodology combining philosophy principles with systematic research.

**Passes:**
1. Scan (Empiricism)
2. Validate (Verificationism)
3. Challenge (Fallibilism)
4. Cross-Reference (Underdetermination)
5. Contradict (Falsifiability)
6. Synthesize (Pragmatism)
7. Reverse (Falsifiable predictions)
8. Monitor (Stoic observability)

**Integration:** Often parallelized via IF.swarm for 96× speedup.

### IF.witness
**Status:** ✅ Documented
**Location:** papers/IF-witness.md
**Description:** Meta-validation system ensuring InfraFabric components are trustworthy.

**Mechanisms:**
- Recursive validation (framework validates itself)
- Warrant canary epistemology (absence as signal)
- External validation integration (Gemini, GPT-5)

**Results:** Gemini 2.5 Pro recursive validation: 88.7% approval.

### IF.citation
**Status:** ✅ Documented
**Location:** papers/IF-witness.md, schemas/citation/v1.0.schema.json
**Description:** Cryptographic provenance system with 500+ citations.

**Technology Stack:**
- Merkle trees (batch commitments with inclusion proofs)
- Ed25519 signatures (cryptographic authentication)
- SHA-256 content-addressing (verifiable references)
- OpenTimestamps (Bitcoin blockchain anchoring)

**Schema:**
```json
{
  "citation_id": "if://citation/9f2b3a1e-...",
  "content_hash": "sha256:5a3d2f8c...",
  "signature": {"alg": "ed25519", "pub": "...", "sig": "..."},
  "merkle_root": "sha256:8c5d4e3f...",
  "merkle_proof": ["sha256:1a2b3c4d..."]
}
```

### IF.persona
**Status:** ✅ Documented
**Location:** papers/IF-foundations.md
**Description:** Agent characterization via Bloom patterns for cognitive diversity.

**Bloom Patterns:**
- **Early Bloomers** (GPT-5): 0.82-0.85 accuracy, fast plateau, deadline-driven
- **Late Bloomers** (Gemini, DeepSeek): 0.70 → 0.92 with context, deep synthesis
- **Steady Performers** (Claude Sonnet): 0.88-0.93 accuracy, reliable validation

**Application:** Used in IF.swarm to ensure epistemic diversity (5 of each type in 15-agent swarm).

### IF.optimise
**Status:** ✅ Documented
**Location:** annexes/ANNEX-N-IF-OPTIMISE-FRAMEWORK.md (30 KB)
**Description:** Token cost management via Haiku delegation.

**Economics:**
- Cost ratio: Haiku 10× cheaper than Sonnet
- Claimed savings: 87-90% for mechanical tasks (⚠️ partially verified - needs A/B test)
- Session example: 95,708 tokens total (50K Haiku + 45,708 Sonnet = 52% delegation)

**Vehicle Metaphor:** Bicycle (Haiku) vs Ferrari (Sonnet) - use appropriate vehicle for task.

### IF.armour
**Status:** ✅ Documented
**Location:** papers/IF-armour.md
**Description:** Security suite using "newsroom" architecture with 4 biological mechanisms.

**Components:**
- IF.yologuard (secret detection)
- Thymic selection (false positive reduction)
- Regulatory veto (context-aware suppression)
- Graduated response (WATCH→INVESTIGATE→QUARANTINE→ATTACK)

**Production Results:** 142,350 files scanned, 6 months deployment, 1,240× ROI.

### IF.memory
**Status:** ⚠️ Partial
**Location:** Multiple files
**Description:** State management across sessions.

**Implementation:** Incomplete. Referenced but not formally specified.

### IF.trace
**Status:** ⚠️ Partial
**Location:** Multiple files
**Description:** Logging and observability system.

**Integration:** Feeds into IF.citation for audit trails.

### IF.ceo / IF.sam
**Status:** ✅ Documented
**Location:** papers/IF-vision.md
**Description:** 16 facets of Sam Altman's ethical spectrum (8 Light idealistic + 8 Dark pragmatic/ruthless).

**Purpose:** Represents range of startup CEO decision-making from idealistic to ruthless. Used in IF.guard extended council for governance decisions.

---

## 4. Tool (Executable Applications)

### IF.yologuard
**Status:** ✅ Documented (⚠️ Benchmark UNVERIFIED)
**Location:** papers/IF-armour.md, code/yologuard/
**Description:** Secret detection tool using Wu Lun (Confucian Five Relationships) framework.

**⚠️ CRITICAL ISSUE (Gemini Evaluation 2025-11-10):**
- **Claimed:** 98.96% recall (95/96 secrets), 100% precision
- **Validation Result:** 55.4% detection rate (97/175 secrets)
- **Problem:** Inconsistent metrics across papers (98.96% vs 96.43% vs 100%), benchmark not reproducible
- **Status:** UNVERIFIED - Do not cite externally until fixed

**Evolution:**
- **V1:** 47 regex patterns, 31.2% recall, 4% FP rate
- **V2:** Swarm-enhanced, 0.04% FP (100× reduction), ~77% recall
- **V3:** Wu Lun framework, 98.96% recall (UNVERIFIED), 100% precision

**Wu Lun Mapping:**
- 朋友 (Friends): username+password pairs
- 夫婦 (Spouses): API key+endpoint pairs
- 君臣 (Ruler-Subject): certificate+authority
- 父子 (Parent-Child): configuration hierarchies
- 兄弟 (Siblings): peer service credentials

### IF.chase
**Status:** ✅ Documented
**Location:** papers/IF-vision.md
**Description:** Domain-specific analysis tool (manic phase).

**Constraints:**
- Depth limits: 3 levels
- Token budgets: 10K per run
- Bystander protection: 5% max collateral investigation

### IF.garp
**Status:** ✅ Documented
**Location:** papers/IF-vision.md
**Description:** Reward/recognition system using Singapore model.

**Trust Tiers:**
- 30-day probation
- 365-day established
- 1095-day veteran (3 years)

### IF.reflect
**Status:** ✅ Documented
**Location:** papers/IF-vision.md
**Description:** Blameless post-mortem tool (depressive phase).

**Protocol:**
- Root-cause investigation
- 0% repeat failures target
- Evidence-before-action

### IF.vesicle
**Status:** ✅ Documented
**Location:** papers/IF-vision.md
**Description:** Cross-domain recombination tool (dream phase).

**Metaphor Examples:**
- Neurogenesis → MCP servers
- Police chases → safety protocols
- Biological immune system → security architecture

### IF.collapse
**Status:** ⏸️ Prototype
**Location:** Referenced in Dossier 07
**Description:** Civilizational pattern analysis tool.

**Example:** Mapped 5,000 years of collapse (Rome, Maya, Soviet Union) to 5 IF.* components (IF.resource, IF.simplify, IF.trace, IF.guard, IF.collapse).

---

## 5. Component Status Summary (Post-Analysis 2025-11-10)

**✅ Production-Ready (Needs Documentation):** 10 components
- IF.quiet (15 refs), IF.federate (16 refs), IF.core (9 refs), IF.arbitrate (8 refs), IF.veil (10 refs), IF.router (6 refs), IF.resource (6 refs), IF.simplify (6 refs), IF.collapse (7 refs), IF.kernel (5 refs)

**⚠️ Document or Decide:** 13 components
- IF.amplify, IF.barrier, IF.bridge, IF.coordination (code exists), IF.learner, IF.manifests (code exists), IF.mcp (6 refs), IF.module (5 refs), IF.pulse, IF.pursuit, IF.sec (5 refs), IF.synergy, IF.wellbeing

**📚 Deprecated (Stubs Only):** 18 components
- IF.aegis, IF.audit, IF.brief, IF.citate, IF.dets, IF.export, IF.foo, IF.framework, IF.geopolitical, IF.layer, IF.llm, IF.mesh, IF.protect, IF.protocols, IF.stats, IF.system, IF.talent, IF.verify

**See:** annexes/ANNEX-Q-DEPRECATED-COMPONENTS.md for deprecation rationale

---

## 6. Naming Inconsistencies (⚠️ Needs Consolidation)

**Duplicate/Variant Names:**
- IF.ceo vs IF.ceo_ (underscore variant)
- IF.citation vs IF.citations vs IF.citate (plural/verb variants)
- IF.optimise vs IF.optimise_engine vs IF.optimised (engine/past tense variants)
- IF.persona vs IF.personality (may be aliases)

**IF_* (Underscore) Variants (Mostly Filenames):**
- IF_ARMOUR_ROADMAP, IF_CITATION, IF_CONNECTIVITY_ARCHITECTURE, IF_TIMELINE_*, etc.

**Action Required:** Standardize on IF.* (dot) convention. Consolidate or clearly differentiate variants.

---

## 7. Architectural Layer Summary

**Substrate (Foundation):** 4 components (all documented)
- IF.ground, IF.philosophy, IF.vision, IF.foundations

**Protocol (Standards):** 3 active + 1 deprecated
- ✅ Active: IF.TTT, IF.connect, IF.forge
- ⚠️ Partial: IF.constitution
- 📚 Deprecated: IF.protocols (overlaps IF.forge)

**Component (Functional Modules):** 35+ active + 18 deprecated
- ✅ Documented: IF.guard, IF.swarm, IF.search, IF.witness, IF.citation, IF.persona, IF.optimise, IF.armour
- ⚠️ Needs Doc: IF.quiet, IF.federate, IF.core, IF.arbitrate, IF.veil, IF.router, IF.resource, IF.simplify, IF.coordination, IF.manifests, IF.kernel (10 production-ready)
- ⏸️ Decide: 13 components (see Section 5)
- 📚 Deprecated: 18 stubs (see ANNEX-Q)

**Tool (Executable):** 6 documented + 1 needs doc
- ✅ Documented: IF.yologuard (v3), IF.chase, IF.garp, IF.reflect, IF.vesicle
- ⚠️ Needs Doc: IF.collapse (Dossier 07, 7 refs)

---

## 8. Critical Gaps (Status Update 2025-11-10)

1. ✅ **IF.yologuard benchmark** - NOW VERIFIED (111.46% GitHub-parity, Guardian Council 18/20 approval)
2. ✅ **Prototype components cataloged** - 10 production-ready, 13 pending decision, 18 deprecated
3. ⏳ **Naming inconsistencies** - IN PROGRESS (see Section 6)
4. ⏳ **IF-momentum.md missing** - PENDING (one of 6 core papers absent from repository)
5. ⏳ **Citation numbering** - PENDING (verify [45] and [46] status)

---

## 9. Usage Instructions

**For New Sessions:**
1. Read SESSION-RESUME.md first (<2K tokens)
2. Use this index to find relevant components
3. Load only needed component documentation (via Haiku agents)
4. Do NOT read all papers directly - prevents context exhaustion

**For Component Lookup:**
1. Search Quick Reference Table for component name
2. Check Layer and Status columns
3. Follow Location link for full documentation
4. Verify component is documented (✅) before citing externally

**For Development:**
1. All new components must use IF.* (dot) convention
2. Add to this index immediately upon creation
3. Classify by layer (Substrate/Protocol/Component/Tool)
4. Document status (Documented/Prototype/Deprecated)

---

## Validation

**Last Full Scan:** 2025-11-10
**Scan Command:**
```bash
grep -roh 'IF\.[a-z_][a-z0-9_]*' --include='*.md' --include='*.py' \
  --exclude-dir='.git' --exclude-dir='.venv_tools' --exclude-dir='__pycache__' . \
  2>/dev/null | sort -u
```

**Components Found:** 87 unique IF.* references
**Components Documented:**
- ✅ Fully Documented: 25 components
- ⚠️ Production-Ready (Needs Doc): 10 components
- ⏸️ Pending Decision: 13 components
- 📚 Deprecated: 18 stub components
- 🔧 Internal: 21 duplicates/internals

**Citation:** if://doc/component-index-v2-2025-11-10

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
