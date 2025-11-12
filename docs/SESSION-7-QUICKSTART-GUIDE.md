# Session 7 Quick-Start Guide - IF.bus Integration

**Version:** 1.0
**Date:** 2025-11-12
**For:** Session 7 (IF.bus coordinator implementation)
**From:** Session 5 (CLI)

## Overview

This guide helps you quickly integrate with the EventBus (P0.1.1) completed by Session 5 and implement your remaining coordination tasks.

**What's already done for you:**
- ✅ P0.1.1: EventBus with etcd3 backend (`infrafabric/event_bus.py`)
- ✅ 26 unit tests passing
- ✅ Configuration system (`infrafabric/config.py`)
- ✅ Capability schema (`infrafabric/schemas/capability.py`)

**What you need to do:**
- P0.1.2: Atomic CAS operations
- P0.1.3: Real-time pub/sub
- P0.1.4: Latency verification (<10ms)
- P0.1.5: Integration tests
- P0.1.6: IF.executor (NEW)
- P0.1.7: IF.proxy (NEW)

**Reference:** See `docs/COORDINATOR-INTEGRATION-PLAN.md` for comprehensive architecture

---

## Quick Start: Using the EventBus

### 1. Import and Initialize

```python
from infrafabric.event_bus import EventBus
from infrafabric.config import CoordinatorConfig

# Load config
config = CoordinatorConfig.from_env()

# Create event bus
bus = EventBus(
    host=config.etcd_host,
    port=config.etcd_port
)

# Connect
await bus.connect()

# Verify connection
assert await bus.health_check()
```

### 2. Basic Operations (Already Working)

```python
# Put/Get (already tested)
await bus.put('/tasks/P0.1.2/owner', 'session-7')
owner = await bus.get('/tasks/P0.1.2/owner')
# Returns: 'session-7'

# List keys with prefix
keys = await bus.list_keys('/tasks/')
# Returns: ['/tasks/P0.1.2/owner', '/tasks/P0.1.3/owner', ...]

# Delete key
await bus.delete('/tasks/P0.1.2/owner')
```

### 3. Watch for Changes (For Pub/Sub)

```python
async def task_handler(event):
    """Called when /tasks/* changes"""
    print(f"Task changed: {event.key} = {event.value}")

# Subscribe to task changes
await bus.watch('/tasks/', callback=task_handler)

# Now any change to /tasks/* will trigger task_handler
await bus.put('/tasks/new-task/owner', 'session-2')
# → task_handler called automatically
```

---

## P0.1.2: Atomic CAS - The Fast Path

**Goal:** <5ms task claiming with zero race conditions

### Implementation Pattern

```python
# infrafabric/coordinator.py

from infrafabric.event_bus import EventBus
import time

class IFCoordinator:
    """Real-time coordination service"""

    def __init__(self, bus: EventBus):
        self.bus = bus

    async def claim_task(self, swarm_id: str, task_id: str) -> bool:
        """
        Atomically claim a task using CAS.
        Returns True if claim successful, False if already claimed.
        Target: <5ms
        """
        start_time = time.perf_counter()

        key = f'/tasks/{task_id}/owner'

        # Atomic compare-and-swap
        # Only succeeds if key doesn't exist or value is 'unclaimed'
        success = await self.bus.transaction(
            compare=[('version', key, '==', 0)],  # Key doesn't exist
            success=[('put', key, swarm_id)],
            failure=[]
        )

        latency_ms = (time.perf_counter() - start_time) * 1000

        # Log to witness
        if success:
            from infrafabric.witness.database import WitnessDatabase
            db = WitnessDatabase()
            db.create_entry(
                event='task_claimed',
                component='IF.coordinator',
                trace_id=task_id,
                payload={
                    'swarm_id': swarm_id,
                    'latency_ms': latency_ms
                }
            )

        return success
```

### Testing CAS Race Conditions

```python
# tests/test_coordinator_cas.py

import pytest
import asyncio

@pytest.mark.asyncio
async def test_cas_race_condition():
    """Test two swarms racing to claim same task"""
    coordinator = IFCoordinator(event_bus)

    # Both try to claim simultaneously
    results = await asyncio.gather(
        coordinator.claim_task('session-1', 'P0.1.2'),
        coordinator.claim_task('session-2', 'P0.1.2'),
    )

    # Exactly one succeeds
    assert sum(results) == 1

    # Winner owns the task
    owner = await event_bus.get('/tasks/P0.1.2/owner')
    assert owner in ['session-1', 'session-2']

@pytest.mark.asyncio
async def test_cas_latency():
    """Test CAS operations meet <5ms target"""
    coordinator = IFCoordinator(event_bus)

    latencies = []
    for i in range(100):
        start = time.perf_counter()
        await coordinator.claim_task(f'session-{i}', f'task-{i}')
        latency_ms = (time.perf_counter() - start) * 1000
        latencies.append(latency_ms)

    # P50, P95, P99 latencies
    p50 = sorted(latencies)[50]
    p95 = sorted(latencies)[95]
    p99 = sorted(latencies)[99]

    assert p50 < 5.0  # Target: <5ms
    assert p95 < 10.0  # Acceptable: <10ms
    assert p99 < 20.0  # Max: <20ms
```

---

## P0.1.3: Real-Time Pub/Sub - The Magic

**Goal:** <10ms task broadcast (no polling!)

### Implementation Pattern

```python
# infrafabric/coordinator.py (continued)

class IFCoordinator:
    async def register_swarm(self, swarm_id: str, capabilities: List[str]):
        """
        Register swarm and set up task notifications.
        Returns immediately, tasks delivered via callback.
        """
        # Store capabilities
        await self.bus.put(
            f'/swarms/{swarm_id}/capabilities',
            json.dumps(capabilities)
        )

        # Subscribe to task broadcasts
        await self.bus.watch(
            f'/tasks/broadcast/{swarm_id}/',
            callback=lambda event: self._handle_task_notification(swarm_id, event)
        )

        # Log registration
        from infrafabric.witness.database import WitnessDatabase
        db = WitnessDatabase()
        db.create_entry(
            event='swarm_registered',
            component='IF.coordinator',
            trace_id=swarm_id,
            payload={'capabilities': capabilities}
        )

    async def push_task_to_swarm(self, swarm_id: str, task: Dict) -> bool:
        """
        Push task notification to specific swarm.
        Target: <10ms delivery
        """
        start_time = time.perf_counter()

        # Write to swarm's task channel
        key = f'/tasks/broadcast/{swarm_id}/{task["task_id"]}'
        await self.bus.put(key, json.dumps(task))

        # Watch callback triggers automatically (etcd v3 watch)
        # Swarm receives notification <10ms later

        latency_ms = (time.perf_counter() - start_time) * 1000

        return latency_ms < 10.0  # Success if <10ms

    async def _handle_task_notification(self, swarm_id: str, event):
        """Callback when task pushed to this swarm"""
        task = json.loads(event.value)

        # Swarm decides whether to claim
        if self._should_claim_task(swarm_id, task):
            await self.claim_task(swarm_id, task['task_id'])
```

### Testing Pub/Sub

```python
# tests/test_coordinator_pubsub.py

@pytest.mark.asyncio
async def test_pubsub_delivery():
    """Test task delivery via pub/sub"""
    coordinator = IFCoordinator(event_bus)

    # Register swarm with callback
    notifications = []
    async def on_task(event):
        notifications.append(json.loads(event.value))

    await event_bus.watch('/tasks/broadcast/session-7/', callback=on_task)

    # Push task
    task = {'task_id': 'P0.1.2', 'description': 'Implement CAS'}
    await coordinator.push_task_to_swarm('session-7', task)

    # Wait briefly for delivery
    await asyncio.sleep(0.05)  # 50ms max

    # Verify notification received
    assert len(notifications) == 1
    assert notifications[0]['task_id'] == 'P0.1.2'

@pytest.mark.asyncio
async def test_pubsub_latency():
    """Test pub/sub meets <10ms target"""
    coordinator = IFCoordinator(event_bus)

    received_times = []

    async def on_task(event):
        received_times.append(time.perf_counter())

    await event_bus.watch('/tasks/broadcast/session-7/', callback=on_task)

    # Send 10 tasks
    send_times = []
    for i in range(10):
        send_times.append(time.perf_counter())
        await coordinator.push_task_to_swarm('session-7', {'task_id': f'task-{i}'})

    # Wait for all notifications
    await asyncio.sleep(0.1)

    # Calculate latencies
    latencies = [
        (recv - send) * 1000
        for send, recv in zip(send_times, received_times)
    ]

    assert all(lat < 10.0 for lat in latencies)  # All <10ms
```

---

## P0.1.6: IF.executor - Command Execution

**Goal:** Policy-governed command execution via IF.bus

### Quick Implementation

```python
# infrafabric/executor.py

import asyncio
import subprocess
from infrafabric.event_bus import EventBus
from infrafabric.witness.database import WitnessDatabase

class IFExecutor:
    """Secure command execution service"""

    def __init__(self, bus: EventBus, policy_file: str = '/etc/infrafabric/executor-policy.json'):
        self.bus = bus
        self.policy = self._load_policy(policy_file)
        self.witness = WitnessDatabase()

    async def start(self):
        """Start listening for execution requests"""
        await self.bus.watch(
            '/commands/execute/',
            callback=self._handle_execute_request
        )

    async def _handle_execute_request(self, event):
        """Handle incoming execution request"""
        request = json.loads(event.value)

        swarm_id = request['swarm_id']
        command = request['command']
        args = request.get('args', [])
        trace_id = request.get('trace_id', f'exec-{time.time()}')

        # Check policy
        if not self._is_allowed(swarm_id, command, args):
            await self._send_result(trace_id, success=False, error='Policy violation')
            return

        # Execute with timeout
        try:
            result = await asyncio.wait_for(
                self._run_command(command, args),
                timeout=request.get('timeout_ms', 5000) / 1000
            )

            await self._send_result(trace_id, success=True, **result)

        except asyncio.TimeoutError:
            await self._send_result(trace_id, success=False, error='Timeout')

    async def _run_command(self, command: str, args: List[str]) -> Dict:
        """Run command and capture output"""
        proc = await asyncio.create_subprocess_exec(
            command, *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        return {
            'exit_code': proc.returncode,
            'stdout': stdout.decode(),
            'stderr': stderr.decode()
        }

    async def _send_result(self, trace_id: str, **kwargs):
        """Send result back via event bus"""
        result_key = f'/commands/results/{trace_id}'
        await self.bus.put(result_key, json.dumps(kwargs))

        # Log to witness
        self.witness.create_entry(
            event='command_executed',
            component='IF.executor',
            trace_id=trace_id,
            payload=kwargs
        )
```

### Policy Example

```json
{
  "allowed_commands": {
    "session-7": [
      {"command": "pytest", "args_pattern": "tests/.*"},
      {"command": "git", "args_pattern": "(status|log|diff)"}
    ],
    "session-2": [
      {"command": "npm", "args_pattern": "(test|build)"}
    ]
  }
}
```

---

## P0.1.7: IF.proxy - External API Proxy

**Goal:** Centralized proxy for external API calls

### Quick Implementation

```python
# infrafabric/proxy.py

import aiohttp
from infrafabric.event_bus import EventBus
from infrafabric.witness.database import WitnessDatabase

class IFProxy:
    """Proxy service for external API calls"""

    def __init__(self, bus: EventBus):
        self.bus = bus
        self.witness = WitnessDatabase()
        self.session = None

    async def start(self):
        """Start proxy service"""
        self.session = aiohttp.ClientSession()

        await self.bus.watch(
            '/proxy/request/',
            callback=self._handle_proxy_request
        )

    async def _handle_proxy_request(self, event):
        """Handle proxy request"""
        request = json.loads(event.value)

        method = request['method']  # GET, POST, etc
        url = request['url']
        headers = request.get('headers', {})
        body = request.get('body')
        trace_id = request.get('trace_id', f'proxy-{time.time()}')

        # Make request
        try:
            async with self.session.request(
                method, url, headers=headers, json=body
            ) as resp:
                result = {
                    'success': True,
                    'status_code': resp.status,
                    'headers': dict(resp.headers),
                    'body': await resp.text()
                }
        except Exception as e:
            result = {
                'success': False,
                'error': str(e)
            }

        # Send response
        response_key = f'/proxy/response/{trace_id}'
        await self.bus.put(response_key, json.dumps(result))

        # Log to witness
        self.witness.create_entry(
            event='proxy_request',
            component='IF.proxy',
            trace_id=trace_id,
            payload={'method': method, 'url': url, **result}
        )

    async def stop(self):
        """Cleanup"""
        if self.session:
            await self.session.close()
```

### Usage Example

```python
# Swarm makes API request via proxy
request = {
    'method': 'GET',
    'url': 'https://api.anthropic.com/v1/models',
    'headers': {'x-api-key': api_key},
    'trace_id': 'model-list-001'
}

# Send request via event bus
await bus.put('/proxy/request/model-list-001', json.dumps(request))

# Wait for response
response_json = await bus.get('/proxy/response/model-list-001')
response = json.loads(response_json)

if response['success']:
    print(f"Models: {response['body']}")
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Blocking the Event Loop

**Problem:**
```python
# BAD: Blocks event loop
def claim_task(self, swarm_id, task_id):
    return self.bus.put(...)  # Blocks!
```

**Solution:**
```python
# GOOD: Async all the way
async def claim_task(self, swarm_id, task_id):
    return await self.bus.put(...)
```

### Pitfall 2: Not Handling Disconnections

**Problem:**
```python
# BAD: No reconnection logic
await bus.connect()
# Connection lost → everything breaks
```

**Solution:**
```python
# GOOD: Reconnection loop (already in EventBus)
await bus.connect()  # Has built-in reconnection
await bus.health_check()  # Verify before use
```

### Pitfall 3: Forgetting to Log to Witness

**Problem:**
```python
# BAD: No audit trail
await coordinator.claim_task(swarm_id, task_id)
```

**Solution:**
```python
# GOOD: Always log critical events (already in examples above)
success = await coordinator.claim_task(swarm_id, task_id)
if success:
    witness.create_entry(event='task_claimed', ...)
```

### Pitfall 4: Race Conditions in Tests

**Problem:**
```python
# BAD: Assumes instant delivery
await coordinator.push_task(...)
assert len(notifications) == 1  # Flaky!
```

**Solution:**
```python
# GOOD: Wait for async events
await coordinator.push_task(...)
await asyncio.sleep(0.05)  # Brief wait
assert len(notifications) == 1  # Reliable
```

---

## Testing Strategy

### 1. Unit Tests (Fast, Isolated)

```python
# Test individual methods with mocks
@pytest.fixture
def mock_bus():
    bus = AsyncMock(spec=EventBus)
    bus.put.return_value = True
    return bus

def test_claim_task_success(mock_bus):
    coordinator = IFCoordinator(mock_bus)
    result = await coordinator.claim_task('session-7', 'P0.1.2')

    assert result is True
    mock_bus.transaction.assert_called_once()
```

### 2. Integration Tests (Real EventBus)

```python
# Test with real etcd
@pytest.fixture
async def real_bus():
    bus = EventBus('localhost', 2379)
    await bus.connect()
    yield bus
    await bus.disconnect()

async def test_claim_task_integration(real_bus):
    coordinator = IFCoordinator(real_bus)
    result = await coordinator.claim_task('session-7', 'P0.1.2')

    assert result is True
    owner = await real_bus.get('/tasks/P0.1.2/owner')
    assert owner == 'session-7'
```

### 3. Performance Tests (Latency)

```python
# Benchmark CAS and pub/sub latencies
async def test_cas_performance():
    latencies = []
    for i in range(1000):
        start = time.perf_counter()
        await coordinator.claim_task(f'session-{i}', f'task-{i}')
        latencies.append((time.perf_counter() - start) * 1000)

    p50 = sorted(latencies)[500]
    p95 = sorted(latencies)[950]
    p99 = sorted(latencies)[990]

    print(f"CAS Latency - P50: {p50:.2f}ms, P95: {p95:.2f}ms, P99: {p99:.2f}ms")

    assert p95 < 10.0  # 95% under 10ms
```

---

## Configuration Tips

### 1. Use Environment Variables

```bash
# .env file
IF_ETCD_HOST=localhost
IF_ETCD_PORT=2379
IF_COORDINATOR_BACKEND=etcd
IF_TARGET_CAS_LATENCY_MS=5
IF_TARGET_PUBSUB_LATENCY_MS=10
IF_WITNESS_ENABLED=true
```

### 2. Load Config Early

```python
# At start of your module
from infrafabric.config import InfraFabricConfig

config = InfraFabricConfig.load()
```

### 3. Override for Testing

```python
# In tests
config = CoordinatorConfig(
    backend='etcd',
    etcd_host='localhost',
    etcd_port=2379,
    witness_enabled=False  # Disable for fast tests
)
```

---

## Next Steps

1. **Start with P0.1.2 (CAS):** Copy the `claim_task` implementation above
2. **Add P0.1.3 (Pub/Sub):** Copy the `push_task_to_swarm` implementation
3. **Write Tests:** Use the testing patterns above
4. **Benchmark:** Verify <5ms CAS, <10ms pub/sub
5. **P0.1.6 & P0.1.7:** Implement executor and proxy (optional for Phase 0)

---

## Questions?

**EventBus Issues:** Check `tests/test_event_bus.py` for examples
**Config Questions:** See `config.example.yaml` for all options
**Witness Integration:** Look at `src/cli/if_witness.py` for CLI usage
**Performance Tips:** Review `docs/COORDINATOR-INTEGRATION-PLAN.md`

**Good luck with your integration! 🚀**

---

**Created by:** Session 5 (CLI)
**For:** Session 7 (IF.bus)
**Date:** 2025-11-12
