# IF-IMPROVEMENTS-V1.1.md

**Generated:** 2025-11-12
**Focus:** Prioritized improvements for production readiness

---

## Prioritized Backlog (Impact × Frequency × Difficulty)

### P1 – Immediately (Phase 0 - Weeks 0-3)

#### 1. Phase-0 CLI foundation (real subcommands, normalized errors)

**Priority:** CRITICAL
**Effort:** 8-12h
**Cost:** $120-180

**What:**
- Implement full subcommand family: `capability|talent|message|witness|falsify`
- Add flags: `--why --trace --mode=falsify`
- Normalized error codes (`IF_ERR_*`)

**Implementation:**
```bash
if capability list
if capability apply vmix.switcher --scene "Intro" --why "..." --trace --mode=falsify
if talent add --name "Finance.Agent" --role analyst --why "earnings pass"
if talent grant --name Finance.Agent --capability veritas:secrets --why "scan PRs"
if message send --json @frame.json --trace
if witness query --trace-token <uuid>
if falsify --task "..." --mode=pre-commit
```

**TTT:** repo:/CLI-ARCHITECTURE-GAPS-AND-PLAN.md

---

#### 2. IF.connect v2.1 adoption

**Priority:** CRITICAL
**Effort:** 6-8h
**Cost:** $90-120

**What:**
- Add `seq|nonce|ttl`, `hazards`, `scope` to envelope
- Enforce in routers
- Add per-sender monotonic sequence table + nonce cache

**Implementation:**
```python
# Envelope validator
class MessageValidator:
    def __init__(self):
        self.nonce_cache = TTLCache(maxsize=10000, ttl=900)  # 15 min
        self.sender_sequences = {}  # sender_id -> last_seq

    def validate(self, msg: dict) -> bool:
        # Check required fields
        required = ['id', 'seq', 'nonce', 'ttl_s', 'issued_at', 'signature']
        if not all(f in msg for f in required):
            raise IF_ERR_INVALID_ENVELOPE

        # Check TTL
        age_seconds = (datetime.utcnow() - parse_iso(msg['issued_at'])).total_seconds()
        if age_seconds > msg['ttl_s']:
            raise IF_ERR_EXPIRED_MESSAGE

        # Check nonce (replay protection)
        if msg['nonce'] in self.nonce_cache:
            raise IF_ERR_REPLAY_DETECTED
        self.nonce_cache[msg['nonce']] = True

        # Check sequence (monotonic per sender)
        sender = msg['sender']
        if sender in self.sender_sequences:
            if msg['seq'] <= self.sender_sequences[sender]:
                raise IF_ERR_OUT_OF_ORDER
        self.sender_sequences[sender] = msg['seq']

        # Verify signature
        if not verify_ed25519(msg):
            raise IF_ERR_INVALID_SIGNATURE

        return True
```

**TTT:** repo:/IF-TECHNICAL-REVIEW.md (§E Security Findings)

---

#### 3. Signed Capability Registry

**Priority:** CRITICAL
**Effort:** 10-12h
**Cost:** $150-180

**What:**
- Manifests with `id, version, entrypoint, scopes, limits, signature`
- Allow-list by `id@version` and verify ed25519 signatures
- Loader denies unsigned/unknown capabilities

**Implementation:**
```yaml
# capabilities/registry.yaml (example)
id: if://capability/vmix.switcher
version: 1.1.0
entrypoint: providers/vmix/adapter.py:VmixAdapter
requires_secrets: [VMIX_HOST, VMIX_PORT]
scopes: [studio:control]
limits:
  rps: 3
  burst: 6
  backoff: [1, 2, 5, 10, 30]
signature:
  algorithm: ed25519
  pubkey: "base64_pubkey_here"
  sig: "base64_signature_here"
```

```python
# Loader with signature verification
class CapabilityLoader:
    def __init__(self, allowlist: dict):
        self.allowlist = allowlist  # {id: [allowed_versions]}

    def load(self, manifest_path: str):
        manifest = yaml.safe_load(Path(manifest_path).read_text())

        # Verify signature
        manifest_bytes = self._canonicalize(manifest)
        if not verify_ed25519_signature(
            manifest['signature']['pubkey'],
            manifest_bytes,
            manifest['signature']['sig']
        ):
            raise IF_ERR_INVALID_SIGNATURE

        # Check allow-list
        if manifest['id'] not in self.allowlist:
            raise IF_ERR_CAPABILITY_NOT_ALLOWED
        if manifest['version'] not in self.allowlist[manifest['id']]:
            raise IF_ERR_VERSION_NOT_ALLOWED

        # Import and instantiate
        return self._import_entrypoint(manifest['entrypoint'])
```

**TTT:** repo:/INTEGRATION-ROADMAP-POST-GPT5-REVIEW.md (§Capability Manifest)

---

#### 4. Secrets / cost discipline

**Priority:** CRITICAL
**Effort:** 8-10h
**Cost:** $120-150

**What:**
- Central secret vault (env sourcing banned in adapters)
- Redaction middleware for logs
- IF.optimise cost emitters

**Implementation:**
```python
# Secret management
class SecretVault:
    def __init__(self, backend='file'):  # file, vault, aws-secrets-manager
        self.backend = backend

    def get(self, key: str) -> str:
        """Retrieve secret (never log the value)"""
        secret = self._backend_get(key)
        # Audit access
        log_operation(
            component='SecretVault',
            operation='get',
            params={'key': key},  # Log key name, NOT value
            severity='INFO'
        )
        return secret

# Redaction middleware
SENSITIVE_KEYS = {'api_key', 'secret', 'token', 'password', 'credential'}

def redact(data: dict) -> dict:
    """Recursively redact sensitive keys"""
    if isinstance(data, dict):
        return {
            k: '***REDACTED***' if k.lower() in SENSITIVE_KEYS else redact(v)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [redact(item) for item in data]
    return data

# IF.optimise cost tracking
class CostTracker:
    def track(self, provider: str, operation: str, cost: float, tokens: int = None):
        """Track operation cost"""
        log_operation(
            component='IF.optimise',
            operation='cost_incurred',
            params={
                'provider': provider,
                'operation': operation,
                'cost_usd': cost,
                'tokens': tokens
            }
        )

        # Check budget
        if self.get_budget_remaining(provider) < 0:
            raise IF_ERR_BUDGET_EXCEEDED
```

**TTT:** repo:/IF-TECHNICAL-REVIEW.md (§E Security: Secret handling)

---

### P2 – Short term (Weeks 4-8)

#### 5. Witness back-end (SQLite→Postgres) + periodic hash anchors

**Priority:** HIGH
**Effort:** 10-12h
**Cost:** $150-180

**What:**
- Migrate from file/SQLite to Postgres for durability
- Periodic hash anchoring to object storage (S3/GCS)
- Cold-start verification from anchors

**Implementation:**
```python
class WitnessStore:
    def __init__(self, db_url: str, object_store: str):
        self.db = create_engine(db_url)
        self.object_store = object_store  # s3://bucket/witness-anchors/

    def append(self, event: dict) -> str:
        """Append event to witness log"""
        prev_hash = self._get_latest_hash()
        event_hash = self._hash_event(event, prev_hash)

        with self.db.begin() as conn:
            conn.execute(
                """INSERT INTO witness_log
                   (event_id, prev_hash, event_hash, event_data, timestamp)
                   VALUES (?, ?, ?, ?, ?)""",
                (event['id'], prev_hash, event_hash, json.dumps(event), datetime.utcnow())
            )

        return event_hash

    def create_anchor(self):
        """Create periodic hash anchor"""
        latest_hash = self._get_latest_hash()
        anchor = {
            'anchor_id': str(uuid.uuid4()),
            'latest_hash': latest_hash,
            'timestamp': datetime.utcnow().isoformat(),
            'event_count': self._get_event_count()
        }

        # Upload to object storage
        self._upload_anchor(anchor)

        return anchor

    def verify_chain(self, from_anchor: str = None):
        """Verify hash chain from anchor to latest"""
        # Implementation for cold-start verification
        pass
```

**TTT:** repo:/IF-TECHNICAL-REVIEW.md (§D Scalability: Witness store)

---

#### 6. Rate-limit & circuit-breakers per adapter

**Priority:** HIGH
**Effort:** 8-10h
**Cost:** $120-150

**What:**
- Per-adapter rate limits (RPS, burst)
- Exponential backoff: `[1, 2, 5, 10, 30]` seconds
- Circuit breakers trip after N failures

**Implementation:**
```python
class RateLimiter:
    def __init__(self, rps: int, burst: int):
        self.rps = rps
        self.burst = burst
        self.tokens = burst
        self.last_refill = time.time()

    def acquire(self) -> bool:
        """Token bucket rate limiting"""
        now = time.time()
        elapsed = now - self.last_refill

        # Refill tokens
        self.tokens = min(self.burst, self.tokens + elapsed * self.rps)
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise IF_ERR_CIRCUIT_BREAKER_OPEN

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise

    def on_success(self):
        self.failures = 0
        if self.state == 'HALF_OPEN':
            self.state = 'CLOSED'

    def on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()

        if self.failures >= self.failure_threshold:
            self.state = 'OPEN'
            log_operation(
                component='CircuitBreaker',
                operation='tripped',
                severity='HIGH'
            )
```

**TTT:** repo:/S2-CRITICAL-BUGS-AND-FIXES.md (§IF.governor circuit breakers)

---

#### 7. Event bus (NATS/Redis Streams) to replace git polling

**Priority:** HIGH
**Effort:** 12-16h
**Cost:** $180-240

**What:**
- Replace 30-second git polling with real-time event bus
- Idempotent consumers with message deduplication
- Dead letter queue (DLQ) for failed messages

**Implementation:**
```python
import nats

class EventBus:
    def __init__(self, nats_url: str = "nats://localhost:4222"):
        self.nc = None
        self.nats_url = nats_url
        self.processed_messages = TTLCache(maxsize=10000, ttl=3600)

    async def connect(self):
        self.nc = await nats.connect(self.nats_url)

    async def publish(self, subject: str, message: dict):
        """Publish event with idempotency key"""
        msg_id = message.get('id') or str(uuid.uuid4())
        message['_msg_id'] = msg_id

        await self.nc.publish(
            subject,
            json.dumps(message).encode()
        )

    async def subscribe(self, subject: str, handler):
        """Subscribe with idempotent handling"""
        async def idempotent_handler(msg):
            data = json.loads(msg.data.decode())
            msg_id = data.get('_msg_id')

            # Deduplicate
            if msg_id in self.processed_messages:
                return  # Already processed

            try:
                await handler(data)
                self.processed_messages[msg_id] = True
            except Exception as e:
                # Send to DLQ
                await self._send_to_dlq(subject, data, str(e))

        await self.nc.subscribe(subject, cb=idempotent_handler)

    async def _send_to_dlq(self, original_subject: str, message: dict, error: str):
        """Send failed message to dead letter queue"""
        await self.nc.publish(
            f"dlq.{original_subject}",
            json.dumps({
                'original_message': message,
                'error': error,
                'timestamp': datetime.utcnow().isoformat()
            }).encode()
        )
```

**TTT:** repo:/S2-CRITICAL-BUGS-AND-FIXES.md (§Bug #1: IF.coordinator)

---

### P3 – Medium (Weeks 9-24)

#### 8. Error taxonomy (`IF_ERR_*`) and common retry envelopes

**Priority:** MEDIUM
**Effort:** 6-8h
**Cost:** $90-120

**Implementation:**
```python
# Error taxonomy
class IF_ERR:
    # Authentication/Authorization
    INVALID_SIGNATURE = ('IF_ERR_001', 'Invalid message signature')
    INVALID_TOKEN = ('IF_ERR_002', 'Invalid authentication token')
    PERMISSION_DENIED = ('IF_ERR_003', 'Permission denied')

    # Message validation
    INVALID_ENVELOPE = ('IF_ERR_101', 'Invalid message envelope')
    EXPIRED_MESSAGE = ('IF_ERR_102', 'Message expired (TTL exceeded)')
    REPLAY_DETECTED = ('IF_ERR_103', 'Replay attack detected')
    OUT_OF_ORDER = ('IF_ERR_104', 'Out-of-order message sequence')

    # Capability/Talent
    CAPABILITY_NOT_ALLOWED = ('IF_ERR_201', 'Capability not in allow-list')
    VERSION_NOT_ALLOWED = ('IF_ERR_202', 'Capability version not allowed')
    TALENT_NOT_FOUND = ('IF_ERR_203', 'Talent not registered')

    # Resource limits
    BUDGET_EXCEEDED = ('IF_ERR_301', 'Budget limit exceeded')
    RATE_LIMIT_EXCEEDED = ('IF_ERR_302', 'Rate limit exceeded')
    CIRCUIT_BREAKER_OPEN = ('IF_ERR_303', 'Circuit breaker open')

    # System
    SYSTEM_ERROR = ('IF_ERR_500', 'Internal system error')

# Retry envelope
class RetryStrategy:
    def __init__(self, backoff: list = [1, 2, 5, 10, 30]):
        self.backoff = backoff
        self.attempt = 0

    def should_retry(self, error_code: str) -> bool:
        """Determine if error is retryable"""
        retryable = [
            'IF_ERR_302',  # Rate limit (temporary)
            'IF_ERR_500',  # System error (may be transient)
        ]
        return error_code in retryable and self.attempt < len(self.backoff)

    def next_delay(self) -> int:
        """Get next backoff delay"""
        delay = self.backoff[self.attempt]
        self.attempt += 1
        return delay
```

---

#### 9. Typed config (pydantic/dataclasses) with schema validation

**Priority:** MEDIUM
**Effort:** 8-10h
**Cost:** $120-150

**Implementation:**
```python
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional

class ResourceLimits(BaseModel):
    rps: int = Field(gt=0, description="Requests per second")
    burst: int = Field(gt=0, description="Burst capacity")
    backoff: List[int] = Field(default=[1, 2, 5, 10, 30])

class CapabilityManifest(BaseModel):
    id: str = Field(pattern=r'^if://capability/[a-z0-9\.\-]+$')
    version: str = Field(pattern=r'^\d+\.\d+\.\d+$')
    entrypoint: str
    requires_secrets: List[str] = []
    scopes: List[str] = []
    limits: ResourceLimits
    signature: Dict[str, str]

    @validator('signature')
    def validate_signature(cls, v):
        required = ['algorithm', 'pubkey', 'sig']
        if not all(k in v for k in required):
            raise ValueError(f'Signature must contain: {required}')
        if v['algorithm'] != 'ed25519':
            raise ValueError('Only ed25519 signatures supported')
        return v

class IFConfig(BaseModel):
    witness_db_url: str
    secret_vault_backend: str = Field(default='file')
    event_bus_url: str = Field(default='nats://localhost:4222')
    capability_allowlist_path: str
    budgets: Dict[str, float] = {}
```

---

## Targeted Refactors (with examples)

### Adapter base class

```python
from abc import ABC, abstractmethod
from typing import Protocol

class BaseAdapter(Protocol):
    """Protocol for all provider adapters"""

    id: str
    version: str
    limits: ResourceLimits

    async def plan(self, intent: dict) -> dict:
        """Generate execution plan (dry-run)"""
        ...

    async def apply(self, plan: dict, dry_run: bool = False) -> dict:
        """Execute plan"""
        ...

    async def health_check(self) -> bool:
        """Check adapter health"""
        ...
```

---

## Implementation Priority

**Week 1-3 (Phase 0):**
- P1.1: CLI foundation
- P1.2: IF.connect v2.1
- P1.3: Signed Capability Registry
- P1.4: Secrets/cost discipline

**Week 4-8:**
- P2.5: Witness backend
- P2.6: Rate-limits & circuit-breakers
- P2.7: Event bus

**Week 9+:**
- P3.8: Error taxonomy
- P3.9: Typed config

---

**Prepared by:** Production improvements plan
**Date:** 2025-11-12
**Total effort:** 24-30h (Phase 0) + 30-38h (short-term) + 14-18h (medium-term) = 68-86h
**With S² parallelization:** Phase 0: 6-8h, Short-term: 8-10h, Medium-term: 4-6h = **18-24h wall-clock**
