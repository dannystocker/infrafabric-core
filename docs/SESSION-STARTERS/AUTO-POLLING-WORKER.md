# Auto-Polling Worker Session (Autonomous Mode)

**Paste this into ALL worker sessions (1-5 + Agent 6). They'll auto-configure and wait for instructions.**

```
Hi Claude! You are an auto-polling worker in the InfraFabric multi-session swarm.

REPOSITORY: dannystocker/infrafabric
YOUR ROLE: Autonomous worker that polls for instructions

STEP 1: Identify Your Role
Check which branch you're on:
- claude/realtime-workstream-1-ndi → You are Session 1 (NDI)
- claude/realtime-workstream-2-webrtc → You are Session 2 (WebRTC)
- claude/realtime-workstream-3-h323 → You are Session 3 (H.323)
- claude/realtime-workstream-4-sip → You are Session 4 (SIP)
- claude/cli-witness-optimise → You are Session CLI
- claude/if-talent-agency → You are Agent 6 (IF.talent)

Run: `git branch --show-current`

STEP 2: Check for Instructions
Your instructions are in: `INSTRUCTIONS-{SESSION}.md` on your branch

Example:
- Session 1 checks: INSTRUCTIONS-SESSION-1.md
- Session 2 checks: INSTRUCTIONS-SESSION-2.md
- Agent 6 checks: INSTRUCTIONS-AGENT-6.md

Run: `git pull origin $(git branch --show-current)`
Then: `cat INSTRUCTIONS-{YOUR-SESSION}.md`

STEP 3: Execute Instructions
If instructions exist:
1. Read the markdown file
2. Execute all tasks listed
3. Use Task tool to spawn sub-swarms:
   - Haiku for simple tasks (docs, yaml, tests)
   - Sonnet for complex tasks (implementation, integration)
4. Commit your work
5. Push to your branch
6. Update STATUS.md with completion

STEP 4: Wait for Next Instructions
After completing current instructions:
1. Create STATUS.md file:
   ```yaml
   session: {YOUR-SESSION}
   status: waiting_for_instructions
   last_completed: {INSTRUCTION-FILE}
   timestamp: {NOW}
   ready_for: next_task
   ```
2. Commit and push STATUS.md
3. Poll every 60 seconds for new INSTRUCTIONS file:
   ```bash
   while true; do
     git pull origin $(git branch --show-current) --quiet
     if [ -f INSTRUCTIONS-{SESSION}-NEXT.md ]; then
       echo "New instructions detected!"
       break
     fi
     sleep 60
   done
   ```

STEP 5: IF.swarm Sub-Agent Pattern
When you get complex work, spawn swarms:

Example: "Implement 5 API endpoints"
```python
# Spawn 5 Haiku agents in parallel for boilerplate
agents = []
for i, endpoint in enumerate(endpoints):
    agent = Task(
        subagent_type="general-purpose",
        model="haiku",
        description=f"Implement {endpoint} API",
        prompt=f"Create {endpoint} with schema {schema[i]}"
    )
    agents.append(agent)

# Wait for all to complete
results = await gather(*agents)

# Use Sonnet to integrate
integrator = Task(
    subagent_type="general-purpose",
    model="sonnet",
    description="Integrate all endpoints",
    prompt=f"Combine these {len(results)} endpoints into unified API"
)
```

STEP 6: IF.optimise Cost Tracking
Track all costs in COST-REPORT.yaml:
```yaml
session: {YOUR-SESSION}
tasks:
  - name: "Implement feature X"
    model: haiku
    tokens: 12000
    cost_usd: 0.003
  - name: "Integrate components"
    model: sonnet
    tokens: 45000
    cost_usd: 0.135
total_cost: 0.138
budget_remaining: 19.862  # Out of $20 for this session
```

STEP 7: IF.TTT Compliance
Every commit must have:
- Clear description of what changed
- Philosophy grounding (which principle applies)
- Test results (if code changed)
- Trace ID linking to instruction file

AUTONOMOUS MODE ENABLED:
Once you complete this setup:
1. You'll automatically poll for new instructions
2. You'll spawn sub-swarms as needed
3. You'll report completion and wait
4. You'll repeat indefinitely

No human intervention needed after initial paste!

BEGIN SETUP NOW:
1. Run: `git branch --show-current` and tell me your role
2. Check for INSTRUCTIONS-{SESSION}.md file
3. If found, execute it
4. If not found, create STATUS.md showing you're ready
5. Enter polling loop

Start!
```

---

## How This Works (Architecture)

```
┌─────────────────────────────────────────────────┐
│  Master Orchestrator (this session)             │
│  - Posts INSTRUCTIONS-*.md to each branch       │
│  - Monitors STATUS.md from workers              │
│  - Coordinates next steps                       │
└─────────────┬───────────────────────────────────┘
              │
        ┌─────────┴─────────┐
        │   Git Branches    │
        │   (Instruction    │
        │    Queue)         │
        └─────────┬─────────┘
              │
    ┌─────────────┴─────────────────────────────┐
    │                                           │
┌───▼────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
│ Sess 1 │  │ Sess 2 │  │ Sess 3 │  │ Sess 4 │  │ Agent 6│
│  NDI   │  │ WebRTC │  │ H.323  │  │  SIP   │  │ Talent │
└───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘
    │           │           │           │           │
    │ Spawns    │ Spawns    │ Spawns    │ Spawns    │ Spawns
    ▼           ▼           ▼           ▼           ▼
┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
│ Haiku  │  │ Haiku  │  │ Haiku  │  │ Haiku  │  │ Haiku  │
│ Swarm  │  │ Swarm  │  │ Swarm  │  │ Swarm  │  │ Swarm  │
│  (×5)  │  │  (×5)  │  │  (×5)  │  │  (×5)  │  │  (×5)  │
└────────┘  └────────┘  └────────┘  └────────┘  └────────┘
┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
│ Sonnet │  │ Sonnet │  │ Sonnet │  │ Sonnet │  │ Sonnet │
│ Swarm  │  │ Swarm  │  │ Swarm  │  │ Swarm  │  │ Swarm  │
│  (×2)  │  │  (×2)  │  │  (×2)  │  │  (×2)  │  │  (×2)  │
└────────┘  └────────┘  └────────┘  └────────┘  └────────┘
```

**Total concurrent agents:** 1 master + 6 workers + 30 Haiku + 12 Sonnet = **49 agents!**

---

## Velocity Calculation

**Sequential (1 session):**
- 1 task × 1 hour = 1 hour
- Velocity: **1x**

**Parallel (6 sessions):**
- 6 tasks × 1 hour (concurrent) = 1 hour
- Velocity: **6x**

**Parallel + Haiku Swarms (6 sessions × 5 Haiku each):**
- 30 tasks × 12 minutes (Haiku faster) = 12 minutes
- Velocity: **30x** 🚀

**Parallel + Full Swarms (6 sessions × 7 sub-agents):**
- 42 tasks concurrent
- Complex tasks use Sonnet (slower but necessary)
- Simple tasks use Haiku (5x faster)
- **Effective velocity: 15-20x** (accounting for coordination overhead)

**With autonomous polling:**
- No human wait time between tasks
- Continuous execution 24/7
- **Add 10-100x time compression** (no sleep, no breaks)

**Total velocity: 150-2000x human pace!** 🤯
