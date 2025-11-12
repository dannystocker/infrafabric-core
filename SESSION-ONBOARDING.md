# InfraFabric Session Onboarding Protocol

**READ THIS FIRST** - You are a Claude instance starting a new session or window for InfraFabric work.

**CRITICAL:** Do NOT read the papers folder directly. Follow the protocol below to avoid the 50K+ token context trap.

---

## WHY This Protocol Exists

### The Problem (Documented Failure)
On 2025-11-09, a Claude session attempted to understand InfraFabric by reading documentation directly:
- Read 6 papers (6,078 lines total)
- Read 102 evidence documents
- Consumed 50,000+ tokens just for intake
- **Result:** Ran out of context before completing any actual work

### Current Context: Phase 0 Work
You're joining during **Phase 0** - building production-ready coordination:
- **IF.coordinator**: Real-time task coordination (etcd/NATS, <10ms latency)
- **IF.governor**: Resource management with capability matching
- **IF.chassis**: WASM sandbox runtime for secure agent execution

Your session has specific tasks on the Phase 0 task board. Focus on those first.

### The Root Cause
InfraFabric has extensive documentation across multiple layers:
- **6 Research Papers** (316 KB, 6,078 lines) - Theoretical foundation
- **102 Evidence Files** (11 MB) - Validation data
- **549 Git-tracked files** - Implementation code
- **3,634 total files** (98 MB) - Complete repository

Reading this directly violates **IF.optimise** principles (using expensive Sonnet context for mechanical reading).

### The Solution
**3-Tier Context Architecture** - Load only what you need, when you need it.

---

## HOW To Onboard (Read in Order)

### STEP 1: Read SESSION-RESUME.md ONLY
**Target:** <2,000 tokens
**Location:** `/home/user/infrafabric/SESSION-RESUME.md`

Contains:
- Current mission state (what we're working on RIGHT NOW)
- Phase 0 progress: IF.coordinator, IF.governor, IF.chassis status
- Active branches, uncommitted changes, blockers
- Decisions pending user input
- Last updated timestamp

**Action:** Read this file. Nothing else yet.

**Note:** If SESSION-RESUME.md doesn't exist yet, start with INSTRUCTIONS-SESSION-{N}.md for your assigned session.

### STEP 2: IF Needed - Read COMPONENT-INDEX.md Sections
**Target:** <5,000 tokens (selective reading)
**Location:** `/home/setup/infrafabric/COMPONENT-INDEX.md`

Contains:
- One-paragraph summaries of each major component
- File locations and MD5 hashes for verification
- Last updated dates
- Links to deep archives

**Action:** Read ONLY the sections relevant to your current task.

### STEP 3: NEVER Read Papers Directly
**Location:** `/home/setup/infrafabric/papers/*.md` (6 files, 6,078 lines)

**DO NOT READ THESE FILES DIRECTLY**

If you need deep understanding:
1. Check if COMPONENT-INDEX.md summary is sufficient
2. If not, spawn a Haiku agent to read and summarize specific sections
3. Use Task tool: `subagent_type: "general-purpose"`, `model: "haiku"`

**Why:** Haiku is 10× cheaper than Sonnet. Preserve your (expensive) context for high-value reasoning.

### STEP 4: For Deep Research - Delegate to Haiku Agents
**Pattern:**
```
Task(
  subagent_type="general-purpose",
  model="haiku",
  description="Research specific InfraFabric component",
  prompt="Read /home/setup/infrafabric/papers/IF-vision.md and answer: [specific question]"
)
```

**Examples:**
- "What are the 4 emotional cycles in IF.vision?"
- "What is the Wu Lun breakthrough in IF-armour?"
- "What are the 8 anti-hallucination principles in IF.ground?"

Haiku reads, summarizes, returns answer. You stay focused on the current task.

---

## WHEN To Use This Protocol

### Triggers (Always Use Handover System)
1. **New session start** - You just connected to InfraFabric project
2. **Window reload** - User closed/reopened the session
3. **Context approaching 150K tokens** - Preemptive handoff before hitting limit
4. **Major milestone completed** - Release, architecture change, council decision
5. **User types `/resume`** - Explicit handoff request

### Exceptions (Rare - Confirm With User First)
- User explicitly requests full paper reading
- Creating comprehensive external review package
- Deep architectural refactoring requiring complete context

**Default:** ALWAYS use tiered onboarding unless user overrides.

---

## WHAT Each Tier Contains

### Tier 1: SESSION-RESUME.md (<2K tokens)
```
MISSION: [Current task - e.g., "Implementing V3.2.1 budget enforcement"]
STATUS: [In progress / Blocked / Awaiting decision]
BRANCH: [Git branch name, uncommitted changes]
BLOCKERS: [Dependencies, user decisions needed]
UPDATED: [ISO 8601 timestamp]
```

### Tier 2: COMPONENT-INDEX.md (<5K tokens, selective reading)
```
For each component:
- Name: IF.guard, IF.yologuard, IF.search, etc.
- One-paragraph summary
- Key metrics/results
- File locations + MD5 hashes
- Last updated date
- Related components
```

### Tier 3: Deep Archives (Access via Haiku agents)
```
/papers/InfraFabric.md - Complete 14-day journey
/papers/IF-vision.md - Cyclical coordination model
/papers/IF-foundations.md - Epistemology, IF.ground, IF.search
/papers/IF-armour.md - Security architecture, IF.yologuard
/papers/IF-witness.md - Meta-validation, IF.forge, IF.swarm
/docs/evidence/ - 102 validation documents
/annexes/ - Complete council debates
```

---

## IF.optimise Integration (Default-ON)

**Status Indicators You Should Use:**
- ⚡ **Active** - Using Haiku delegation for mechanical tasks
- 🧠 **Sonnet mode** - Complex reasoning requires direct involvement
- 🚀 **Multi-Haiku** - Parallel Haiku agents running (use single message, multiple Task calls)
- 💤 **Disabled** - User explicitly requested Sonnet-only mode

**Decision Framework:**
```
User Request → IF.optimise Evaluation:
├─ Mechanical? (file ops, git, searches, transforms) → Haiku agent
├─ Complex reasoning? (architecture, council debate, design) → Sonnet (you)
├─ Independent parallel tasks? → 🚀 Multi-Haiku (spawn all in one message)
└─ Sequential dependency? → Mixed (Haiku first, then Sonnet review)
```

**Example - Reading Papers:**
- ❌ BAD: Read all papers directly (50K tokens wasted)
- ✅ GOOD: Spawn 4 Haiku agents in parallel to summarize (5K tokens, 10× cheaper)

---

## Quick Reference Card

**First 5 Minutes In New Session:**
1. ✅ Read SESSION-RESUME.md (current state) or INSTRUCTIONS-SESSION-{N}.md
2. ✅ Check git status (uncommitted changes?)
3. ✅ Check Phase 0 task board: `docs/PHASE-0-TASK-BOARD.md`
4. ✅ Scan COMPONENT-INDEX.md relevant sections ONLY (if needed)
5. ⚠️ Do NOT read /papers/ directly
6. ⚡ Activate IF.optimise (delegate mechanical work to Haiku)

**Quick Glossary (Phase 0 Terms):**
- **etcd**: Distributed key-value store for coordination (like Redis but with strong consistency)
- **NATS**: Lightweight message bus for real-time events
- **CAS (Compare-And-Swap)**: Atomic operation preventing race conditions (updates only if value unchanged)
- **WASM**: WebAssembly - secure, isolated sandbox for running code
- **S² (Swarm of Swarms)**: Multiple agent swarms (50-100+ agents) working together

**If User Asks "What is InfraFabric?":**
- Check COMPONENT-INDEX.md first
- If insufficient, spawn Haiku agent to read InfraFabric.md
- Synthesize answer from summary, don't load full 1,668 lines

**If You Need Philosophy Details:**
- Check COMPONENT-INDEX.md "Philosophy Database" section
- If need specific philosopher quotes, spawn Haiku to read IF-foundations.md section

**If You Need Production Metrics:**
- Check COMPONENT-INDEX.md "IF.yologuard" section
- 98.96% recall, 100% precision, 1,240× ROI documented there

---

## Validation Checklist

Before proceeding with work, confirm:
- [ ] Read SESSION-RESUME.md (know current mission)
- [ ] Checked git status (understand repo state)
- [ ] IF.optimise status indicator visible (⚡/🧠/🚀/💤)
- [ ] Did NOT load full papers into context
- [ ] Ready to spawn Haiku agents for research needs

**If all checked:** You're ready to work efficiently.

**If any unchecked:** Review the section above before proceeding.

---

## Meta: Updating This Document

**When to update SESSION-ONBOARDING.md:**
- New tier added to handover system
- Onboarding protocol changes
- Common failure patterns discovered

**Who updates:**
- Any Claude session that identifies improvement
- Requires user approval for changes

**Last Updated:** 2025-11-10 (initial creation after documented session failure)

---

## Emergency Escape Hatch

**If this protocol is broken or blocking you:**
1. Ask user: "The onboarding protocol seems insufficient for [specific reason]. May I read [specific file] directly?"
2. Explain token cost trade-off
3. Get explicit approval
4. Document the exception in SESSION-RESUME.md

**Never silently bypass the protocol** - it exists because we documented a real failure.

---

**NOW:** Go read SESSION-RESUME.md and get started. You have 150K+ tokens available for actual work instead of documentation intake.
