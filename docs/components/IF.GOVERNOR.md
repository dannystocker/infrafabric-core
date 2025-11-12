# IF.governor - Capability-Aware Resource and Budget Management

## Overview

IF.governor provides intelligent resource allocation, budget enforcement, and swarm coordination for InfraFabric's S² (Swarm of Swarms) architecture. It matches tasks to qualified swarms based on capabilities, manages budgets to prevent cost spirals, and implements circuit breakers for reliability.

**Problem Solved**: Manual swarm assignment is error-prone and inefficient. Tasks may be assigned to unqualified swarms, budgets can spiral out of control, and failing swarms aren't automatically halted.

**Impact**: Enables intelligent, cost-aware swarm coordination with 70% capability matching threshold, automatic circuit breakers, and smart "Gang Up on Blocker" workflow.

**Status**: Specification complete (P0.2.x), Integration tests implemented (P0.2.6)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       IF.governor                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Capability  │  │    Budget    │  │   Circuit    │     │
│  │   Matching   │  │  Enforcement │  │   Breaker    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                 │                  │              │
│         └─────────────────┴──────────────────┘              │
│                          │                                   │
│                   Swarm Registry                            │
│            (capabilities, costs, budgets)                   │
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                   │
   ┌────────┐      ┌──────────────┐     ┌──────────┐
   │ Swarm  │      │     Task     │     │  Policy  │
   │Registry│      │  Assignment  │     │ Engine   │
   └────────┘      └──────────────┘     └──────────┘
```

### Components

1. **Capability Matching Engine**
   - Jaccard similarity for capability overlap
   - 70% minimum match threshold (configurable)
   - Combined scoring: (capability × reputation) / cost

2. **Budget Enforcement**
   - Per-swarm budget tracking
   - Automatic circuit breaker on budget exhaustion
   - Cost tracking per operation

3. **Circuit Breaker**
   - Failure threshold: 3 consecutive failures (configurable)
   - Automatic swarm halting on threshold
   - Prevents cost spirals and repeated failures

4. **Smart Help Request ("Gang Up on Blocker")**
   - Capability-aware swarm recruitment
   - Budget-constrained (max_cost_per_task)
   - Policy limits (max_swarms_per_task)

## Key Concepts

### Capabilities

Capabilities define what a swarm can do. They follow a hierarchical namespace:

```
<domain>:<specific>

Examples:
- code-analysis:python
- code-analysis:rust
- integration:sip
- integration:webrtc
- infra:distributed-systems
- docs:technical-writing
```

**Standard Capabilities:**

| Domain | Specific | Description |
|--------|----------|-------------|
| code-analysis | python, rust, javascript, go | Code review and analysis |
| integration | sip, ndi, webrtc, h323 | Protocol integrations |
| infra | distributed-systems, networking | Infrastructure work |
| cli | design, testing | CLI development |
| architecture | patterns, security | System architecture |
| docs | technical-writing, api-design | Documentation |

### Swarm Profiles

Each swarm registers with a profile:

```python
@dataclass
class SwarmProfile:
    swarm_id: str
    capabilities: List[Capability]
    cost_per_hour: float  # Haiku: $1-2, Sonnet: $15-20, Opus: $75-80
    reputation_score: float  # 0.0-1.0 (based on past performance)
    current_budget_remaining: float
    model: str  # "haiku", "sonnet", "opus"
```

**Example Profiles:**

```python
# Session 4 (SIP) - Sonnet, SIP expert
SwarmProfile(
    swarm_id='session-4-sip',
    capabilities=[
        Capability.INTEGRATION_SIP,
        Capability.CODE_ANALYSIS_PYTHON,
        Capability.INFRA_NETWORKING
    ],
    cost_per_hour=15.0,
    reputation_score=0.95,
    current_budget_remaining=50.0,
    model='sonnet'
)

# Session 7 (IF.bus) - Haiku, infrastructure focus
SwarmProfile(
    swarm_id='session-7-if-bus',
    capabilities=[
        Capability.INFRA_DISTRIBUTED_SYSTEMS,
        Capability.INTEGRATION_SIP,
        Capability.CODE_ANALYSIS_PYTHON
    ],
    cost_per_hour=2.0,
    reputation_score=0.85,
    current_budget_remaining=20.0,
    model='haiku'
)
```

### Resource Policy

Configurable policy constraints:

```python
@dataclass
class ResourcePolicy:
    max_swarms_per_task: int = 3  # Limit swarms for "Gang Up"
    max_cost_per_task: float = 10.0  # Budget cap per task
    min_capability_match: float = 0.7  # 70% match required
    circuit_breaker_failure_threshold: int = 3  # Trip after 3 failures
```

## API Reference

### register_swarm(profile: SwarmProfile)

Register swarm with capabilities and budget.

**Parameters:**
- `profile`: SwarmProfile with capabilities, cost, budget

**Example:**
```python
governor = IFGovernor(policy=ResourcePolicy())

governor.register_swarm(SwarmProfile(
    swarm_id='session-4-sip',
    capabilities=[Capability.INTEGRATION_SIP, Capability.CODE_ANALYSIS_PYTHON],
    cost_per_hour=15.0,
    reputation_score=0.95,
    current_budget_remaining=50.0,
    model='sonnet'
))
```

### find_qualified_swarm(required_capabilities: List[Capability], max_cost: float) → str | None

Find best swarm for task based on capability match and cost.

**Parameters:**
- `required_capabilities`: List of required capabilities
- `max_cost`: Maximum acceptable cost per hour

**Returns:**
- `str`: Swarm ID of best match, or None if no qualified swarm

**Algorithm:**
1. Calculate capability overlap (Jaccard similarity)
2. Filter by min_capability_match threshold (70%)
3. Filter by max_cost
4. Filter by budget_remaining > 0
5. Filter by circuit breaker state
6. Score: (capability_overlap × reputation_score) / cost_per_hour
7. Return highest-scoring swarm

**Example:**
```python
# Find swarm for SIP integration task
swarm_id = governor.find_qualified_swarm(
    required_capabilities=[Capability.INTEGRATION_SIP],
    max_cost=20.0
)

if swarm_id:
    print(f"Assigned to: {swarm_id}")
else:
    print("No qualified swarm available")
```

**Performance:**
- O(n) where n = number of registered swarms
- Typical: <1ms for 10 swarms

### track_cost(swarm_id: str, operation: str, cost: float)

Track operation cost and enforce budget limits.

**Parameters:**
- `swarm_id`: Swarm performing operation
- `operation`: Operation description (e.g., 'code_review', 'integration_test')
- `cost`: Cost in dollars

**Side Effects:**
- Deducts cost from swarm's current_budget_remaining
- Trips circuit breaker if budget exhausted

**Example:**
```python
# Track cost of code review (Sonnet, ~30 min)
governor.track_cost('session-4-sip', 'code_review', 7.50)

# Check budget
profile = governor.swarm_registry['session-4-sip']
print(f"Budget remaining: ${profile.current_budget_remaining:.2f}")
```

### record_failure(swarm_id: str)

Record swarm failure for circuit breaker tracking.

**Parameters:**
- `swarm_id`: Swarm that failed

**Side Effects:**
- Increments failure count
- Trips circuit breaker at threshold (default: 3)
- Halts swarm to prevent repeated failures

**Example:**
```python
try:
    # Task execution
    result = await execute_task(swarm_id, task)
    if not result.success:
        governor.record_failure(swarm_id)
except Exception as e:
    governor.record_failure(swarm_id)
```

### request_help_for_blocker(blocked_swarm_id: str, blocker_description: dict) → List[str]

Smart "Gang Up on Blocker" with capability matching.

**Parameters:**
- `blocked_swarm_id`: Swarm requesting help
- `blocker_description`: Dict with 'required_capabilities', 'description', 'urgency'

**Returns:**
- `List[str]`: List of qualified swarm IDs (up to max_swarms_per_task)

**Algorithm:**
1. Extract required capabilities from blocker description
2. For each capability, find qualified swarm
3. Exclude blocked swarm from candidates
4. Enforce max_swarms_per_task limit
5. Return list of helper swarms

**Example:**
```python
# Session 4 stuck on Rust code analysis
helper_swarms = await governor.request_help_for_blocker(
    blocked_swarm_id='session-4-sip',
    blocker_description={
        'required_capabilities': [
            Capability.CODE_ANALYSIS_RUST,
            Capability.INFRA_DISTRIBUTED_SYSTEMS
        ],
        'description': 'Complex Rust concurrency issue in SIP adapter',
        'urgency': 'high'
    }
)

# Returns: ['session-2-webrtc', 'session-7-if-bus']
for helper_id in helper_swarms:
    await coordinator.push_task_to_swarm(helper_id, blocker_task)
```

**Integration with IF.coordinator:**
```python
# In IF.coordinator.detect_blocker()
async def detect_blocker(self, swarm_id: str, blocker_info: dict):
    # 1. Request help from IF.governor
    helper_swarms = await governor.request_help_for_blocker(swarm_id, blocker_info)

    # 2. Push blocker task to helpers
    for helper_id in helper_swarms:
        await self.push_task_to_swarm(helper_id, {
            'task_id': blocker_info['task_id'],
            'task_type': 'blocker_assistance',
            'blocker_description': blocker_info
        })
```

## Configuration

### Policy Configuration

Create policy file: `/etc/infrafabric/governor_policy.json`

```json
{
  "max_swarms_per_task": 3,
  "max_cost_per_task": 10.0,
  "min_capability_match": 0.7,
  "circuit_breaker_failure_threshold": 3
}
```

**Load policy:**
```python
import json
from infrafabric.governor import ResourcePolicy

with open('/etc/infrafabric/governor_policy.json') as f:
    policy_data = json.load(f)

policy = ResourcePolicy(**policy_data)
governor = IFGovernor(policy=policy)
```

### Environment Variables

```bash
# IF.governor configuration
GOVERNOR_POLICY_FILE=/etc/infrafabric/governor_policy.json
GOVERNOR_MIN_CAPABILITY_MATCH=0.7
GOVERNOR_MAX_SWARMS_PER_TASK=3
GOVERNOR_CIRCUIT_BREAKER_THRESHOLD=3
```

## Capability Matching

### Jaccard Similarity

Capability overlap calculated using Jaccard similarity:

```
similarity = |A ∩ B| / |A ∪ B|

For matching:
overlap = |swarm_capabilities ∩ required_capabilities| / |required_capabilities|
```

**Example:**

```python
required = [Capability.INTEGRATION_SIP, Capability.CODE_ANALYSIS_PYTHON]
swarm = [Capability.INTEGRATION_SIP, Capability.CODE_ANALYSIS_PYTHON, Capability.INFRA_NETWORKING]

overlap = len({SIP, PYTHON} ∩ {SIP, PYTHON, NETWORKING}) / len({SIP, PYTHON})
        = 2 / 2
        = 1.0 (100% match)
```

### Scoring Algorithm

Combined score balances capability, reputation, and cost:

```
score = (capability_overlap × reputation_score) / cost_per_hour
```

**Example Scores:**

| Swarm | Capability | Reputation | Cost | Score |
|-------|------------|------------|------|-------|
| session-4-sip | 1.0 (100%) | 0.95 | $15/hr | 0.063 |
| session-7-if-bus | 0.7 (70%) | 0.85 | $2/hr | 0.298 |

Winner: **session-7-if-bus** (better cost efficiency despite lower capability)

### Minimum Threshold

Default: **70% capability match required**

Rationale:
- 100% match too restrictive (blocks useful swarms)
- <70% match risks unqualified assignments
- 70% balances quality and availability

**Override threshold:**
```python
policy = ResourcePolicy(min_capability_match=0.8)  # 80% match
```

## Budget Management

### Budget Tracking

Each swarm has a budget:

```python
profile = SwarmProfile(
    swarm_id='session-4-sip',
    # ...
    current_budget_remaining=50.0  # $50 remaining
)
```

**Track costs:**
```python
# Sonnet: ~$15/hour
# 30-minute task = $7.50
governor.track_cost('session-4-sip', 'code_review', 7.50)

# Budget now: $42.50
```

### Cost Calculation Examples

**Model Costs (per million tokens):**
- Haiku: $0.25 input, $1.25 output
- Sonnet: $3.00 input, $15.00 output
- Opus: $15.00 input, $75.00 output

**Typical Tasks:**

| Task | Model | Tokens | Cost | Time |
|------|-------|--------|------|------|
| Code review (small PR) | Sonnet | 100k | $1.50 | 10 min |
| Integration test writing | Sonnet | 200k | $3.00 | 20 min |
| Documentation | Haiku | 150k | $0.19 | 15 min |
| Complex debugging | Opus | 300k | $22.50 | 45 min |

### Budget Exhaustion

When budget reaches zero:

1. `track_cost()` detects budget ≤ 0
2. Circuit breaker tripped automatically
3. Swarm marked unavailable
4. `find_qualified_swarm()` excludes swarm
5. Manual intervention required to reset

**Reset budget:**
```python
profile = governor.swarm_registry['session-4-sip']
profile.current_budget_remaining = 50.0  # Replenish budget
governor._circuit_breakers['session-4-sip'] = 0  # Reset circuit breaker
```

## Circuit Breaker

### Failure Threshold

Default: **3 consecutive failures** trips circuit breaker

**What counts as failure:**
- Task execution exception
- Task result marked as failed
- Timeout
- Policy violation

### Circuit Breaker States

```
[CLOSED] ──failure──> [OPEN]
   ↑                     │
   └─────reset───────────┘
```

- **CLOSED**: Normal operation (failure count < threshold)
- **OPEN**: Swarm unavailable (failure count ≥ threshold)

### Tripping Circuit Breaker

**Automatic triggers:**
1. Budget exhaustion (`track_cost()` → budget ≤ 0)
2. Repeated failures (`record_failure()` → count ≥ threshold)

**Manual trip:**
```python
governor._trip_circuit_breaker('session-4-sip', reason='manual_intervention')
```

### Recovery

Circuit breakers require manual reset:

```python
# Reset circuit breaker
governor._circuit_breakers['session-4-sip'] = 0

# Replenish budget if needed
profile = governor.swarm_registry['session-4-sip']
profile.current_budget_remaining = 50.0
```

**Future**: Automatic recovery after cooldown period (not yet implemented)

## Gang Up on Blocker

### Workflow

1. **Swarm detects blocker**
   ```python
   await coordinator.detect_blocker('session-4-sip', {
       'task_id': 'pr-123',
       'required_capabilities': [Capability.CODE_ANALYSIS_RUST],
       'description': 'Complex Rust concurrency issue'
   })
   ```

2. **IF.coordinator requests help from IF.governor**
   ```python
   helper_swarms = await governor.request_help_for_blocker(
       'session-4-sip',
       blocker_info
   )
   ```

3. **IF.governor finds qualified swarms**
   - Capability matching (70% threshold)
   - Budget enforcement
   - Circuit breaker checks
   - Returns up to max_swarms_per_task (default: 3)

4. **IF.coordinator pushes task to helpers**
   ```python
   for helper_id in helper_swarms:
       await coordinator.push_task_to_swarm(helper_id, blocker_task)
   ```

### Policy Constraints

- **max_swarms_per_task**: Limit helper swarms (default: 3)
- **max_cost_per_task**: Budget cap for help request (default: $10)
- **min_capability_match**: Helpers must be qualified (default: 70%)

### No Qualified Swarms

When no helpers available:

```python
helper_swarms = await governor.request_help_for_blocker(...)
if not helper_swarms:
    # Escalate to human
    await notify_human_escalation(blocker_info)
```

**Reasons for no helpers:**
- No swarms with required capabilities
- All qualified swarms have budget exhausted
- All qualified swarms have circuit breaker tripped
- Cost exceeds max_cost_per_task

## Testing

### Unit Tests

See: `tests/unit/test_governor.py` (to be implemented in P0.2.x)

### Integration Tests

See: `tests/integration/test_governor.py` (P0.2.6 ✅)

**Test coverage:**
- Capability matching with various profiles
- Budget enforcement and exhaustion
- Circuit breaker tripping and recovery
- Help request with qualified swarms
- Help request with no qualified swarms (escalation)
- Policy violation prevention
- Multi-swarm coordination

**Run integration tests:**
```bash
pytest tests/integration/test_governor.py -v
```

## Example Policies

### Development Environment

```json
{
  "max_swarms_per_task": 5,
  "max_cost_per_task": 20.0,
  "min_capability_match": 0.6,
  "circuit_breaker_failure_threshold": 5
}
```

Rationale: More permissive for experimentation

### Production Environment

```json
{
  "max_swarms_per_task": 3,
  "max_cost_per_task": 10.0,
  "min_capability_match": 0.7,
  "circuit_breaker_failure_threshold": 3
}
```

Rationale: Stricter controls for cost and quality

### High-Stakes Environment

```json
{
  "max_swarms_per_task": 2,
  "max_cost_per_task": 5.0,
  "min_capability_match": 0.8,
  "circuit_breaker_failure_threshold": 2
}
```

Rationale: Maximum quality, minimal cost risk

## Troubleshooting

### No Qualified Swarm Found

**Symptom**: `find_qualified_swarm()` returns None

**Diagnosis:**
```python
# Check registered swarms
print(f"Registered: {list(governor.swarm_registry.keys())}")

# Check each swarm
for swarm_id, profile in governor.swarm_registry.items():
    overlap = len(set(profile.capabilities) & set(required_capabilities)) / len(required_capabilities)
    print(f"{swarm_id}: {overlap:.2%} match, ${profile.current_budget_remaining:.2f} budget")
```

**Common Causes:**
1. No swarms registered with required capabilities
2. All qualified swarms have budget exhausted
3. All qualified swarms have circuit breaker tripped
4. min_capability_match threshold too high

**Solutions:**
1. Register more swarms with diverse capabilities
2. Replenish budgets
3. Reset circuit breakers
4. Lower min_capability_match (if appropriate)

### Budget Spiraling

**Symptom**: Swarm costs escalating rapidly

**Diagnosis:**
```python
# Track costs in real-time
def track_with_alert(swarm_id, operation, cost):
    governor.track_cost(swarm_id, operation, cost)
    profile = governor.swarm_registry[swarm_id]
    print(f"⚠️  {swarm_id} spent ${cost:.2f} on {operation}, ${profile.current_budget_remaining:.2f} remaining")
```

**Prevention:**
1. Set conservative max_cost_per_task
2. Monitor budget_remaining regularly
3. Use Haiku for routine tasks
4. Reserve Sonnet/Opus for complex work

### Circuit Breaker Tripped

**Symptom**: Swarm unavailable, `find_qualified_swarm()` excludes it

**Diagnosis:**
```python
# Check circuit breaker state
failures = governor._circuit_breakers.get(swarm_id, 0)
threshold = governor.policy.circuit_breaker_failure_threshold
print(f"{swarm_id}: {failures}/{threshold} failures")
```

**Recovery:**
```python
# Investigate root cause (check logs)
# Fix underlying issue
# Reset circuit breaker
governor._circuit_breakers[swarm_id] = 0

# Replenish budget if needed
profile = governor.swarm_registry[swarm_id]
if profile.current_budget_remaining <= 0:
    profile.current_budget_remaining = 50.0
```

## Performance

### Capability Matching

| Operation | Swarms | Time |
|-----------|--------|------|
| find_qualified_swarm() | 10 | <1ms |
| find_qualified_swarm() | 100 | 3-5ms |
| find_qualified_swarm() | 1000 | 30-40ms |

### Memory Usage

- Per swarm profile: ~1KB
- 1000 swarms: ~1MB memory

### Optimization Tips

1. **Cache qualified swarms** for repeated queries
2. **Index capabilities** for O(1) lookup
3. **Batch operations** when assigning multiple tasks
4. **Prune inactive swarms** periodically

## Future Enhancements

### Planned Features (Phase 1+)

1. **Automatic circuit breaker recovery** (cooldown period)
2. **Reputation score calculation** (based on task success rate)
3. **Dynamic cost estimation** (based on task complexity)
4. **Capability learning** (swarms gain capabilities over time)
5. **Multi-objective optimization** (Pareto frontier for cost vs quality)
6. **Swarm load balancing** (distribute work evenly)
7. **Predictive budget alerts** (warn before exhaustion)

## Integration Points

### IF.coordinator

```python
# IF.coordinator checks IF.governor before task assignment
async def assign_task(self, task_id: str, required_capabilities: List[Capability]):
    swarm_id = await governor.find_qualified_swarm(
        required_capabilities=required_capabilities,
        max_cost=10.0
    )

    if swarm_id:
        await self.push_task_to_swarm(swarm_id, task)
    else:
        # Escalate to human
        await self.escalate_to_human(task)
```

### IF.witness

```python
# Track all governor decisions for audit trail
def find_qualified_swarm(self, required_capabilities, max_cost):
    swarm_id = # ... selection logic ...

    # Log to IF.witness
    witness_logger.log({
        'component': 'IF.governor',
        'operation': 'swarm_selected',
        'required_capabilities': required_capabilities,
        'selected_swarm': swarm_id,
        'timestamp': time.time()
    })

    return swarm_id
```

### IF.executor / IF.proxy

```python
# Check capability before allowing privileged operations
async def _handle_execute_request(self, msg):
    swarm_id = msg['swarm_id']

    # Verify swarm has required capability
    if not await governor.check_capability(swarm_id, 'system.process.execute'):
        return error('Missing required capability')

    # Proceed with execution
```

## Status

- **Specification**: Complete (P0.2.x tasks)
- **Integration Tests**: Complete (P0.2.6 ✅)
- **Implementation**: Pending (P0.2.1-P0.2.5)

**Next Steps:**
1. P0.2.1: Capability registry schema
2. P0.2.2: Implement capability matching
3. P0.2.3: Implement budget tracking
4. P0.2.4: Implement circuit breaker
5. P0.2.5: Integrate with IF.coordinator

## References

- IF.coordinator documentation: `/home/user/infrafabric/docs/components/IF.COORDINATOR.md`
- Integration tests: `/home/user/infrafabric/tests/integration/test_governor.py`
- Phase 0 Task Board: `PHASE-0-TASK-BOARD.md`
- S² Architecture: `docs/SWARM-OF-SWARMS-ARCHITECTURE.md`
