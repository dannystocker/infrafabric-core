# InfraFabric Universal Connectivity Architecture (IF.connect)

**Version:** 1.0
**Date:** 2025-11-08
**Repository:** https://github.com/dannystocker/infrafabric (branch: master)
**Status:** Foundational Design Document
**Purpose:** Standardize connectivity from micro (function-level) to macro (IF-to-IF federation)

---

## Executive Summary

Before building IF.armour (or any complex IF.* module), we must **standardize the plumbing**. This document defines **IF.connect**, a universal connectivity architecture that scales across 5 levels:

```
Level 0: Quantum (function → function)
Level 1: Molecular (module → module)
Level 2: Cellular (service → service)
Level 3: Organism (IF.module → IF.module)
Level 4: Ecosystem (InfraFabric → InfraFabric)
```

**Design Drivers:**
- IF.armour's complex needs (3 pillars: yologuard, honeypot, learner)
- IF.swarm's multi-LLM coordination (8 agents voting)
- IF.guard's governance (Guardian council, weighted votes)
- IF.optimise's cost tracking (token accounting across agents)
- IF.search's semantic indexing (cross-repository search)
- TTT requirements (provenance, audit trails, transparency)

**Philosophical Foundation:**
- **Wu Lun (五倫)** - Relationships define connection strength
- **Indra's Net** - Every node reflects every other node
- **Kantian Duty** - Ethical constraints on connectivity
- **IF.ground** - Observable, verifiable connectivity
- **Aristotelian Essence** - Core vs accidental connection properties

**Proven Methods:**
- REST for external APIs
- gRPC for internal services
- Message queues for async work
- Service mesh for observability
- Event sourcing for audit trails

---

## Level 0: Quantum Connectivity (Function → Function)

**Scale:** Within a single Python file
**Use Case:** Internal function calls, helper utilities
**Philosophy:** Aristotelian essence - what is truly necessary?

### 0.1 Direct Invocation (Essence: Simplicity)

```python
# patterns/credentials.py
def get_aws_pattern() -> re.Pattern:
    """Return compiled AWS key pattern"""
    return re.compile(r'AKIA[0-9A-Z]{16}')

# detection/matcher.py
from patterns.credentials import get_aws_pattern

def scan_for_aws(text: str) -> List[Match]:
    """Direct function call - Level 0 connectivity"""
    pattern = get_aws_pattern()  # Quantum connection
    return pattern.findall(text)
```

**Characteristics:**
- **Latency:** Nanoseconds (direct memory access)
- **Coupling:** Tight (import dependency)
- **Observability:** None (no logging by default)
- **Error handling:** Exception propagation

**When to use:** Same file or tightly coupled modules

### 0.2 Callback Pattern (Essence: Flexibility)

```python
# scoring/wulun.py
from typing import Callable

def score_relationship(
    token: str,
    context: str,
    detector: Callable[[str, str], Optional[Tuple]]
) -> float:
    """
    Accept detector as callback - decouples scoring from detection
    Level 0 quantum connection via function pointer
    """
    relationship = detector(token, context)
    if relationship:
        return confucian_weight(relationship[0])  # 朋友, 夫婦, etc.
    return 0.0

# Usage
from detection.relationships import detect_user_password_relationship

score = score_relationship(
    token="secret123",
    context="username=admin\npassword=secret123",
    detector=detect_user_password_relationship  # Callback
)
```

**Characteristics:**
- **Latency:** Nanoseconds + callback overhead
- **Coupling:** Loose (dependency injection)
- **Observability:** Wrapper can add logging
- **Error handling:** Caller controls try/catch

**When to use:** Testing, plugin architecture, inversion of control

---

## Level 1: Molecular Connectivity (Module → Module)

**Scale:** Between Python modules/packages
**Use Case:** Cross-module communication within IF.armour.yologuard
**Philosophy:** Wu Lun - modules have relationships (朋友, 夫婦, etc.)

### 1.1 Import-Based (朋友 Relationship - Friends)

```python
# core/scanner.py
from detection.matcher import PatternMatcher
from scoring.wulun import WuLunScorer
from output.json_formatter import JSONFormatter

class SecretScanner:
    """
    Orchestrator - has 朋友 (friend) relationships with peer modules
    All are equal partners in the detection pipeline
    """
    def __init__(self):
        self.matcher = PatternMatcher()       # Friend 1
        self.scorer = WuLunScorer()           # Friend 2
        self.formatter = JSONFormatter()      # Friend 3

    def scan_file(self, path: Path) -> List[Dict]:
        # Coordinate friends
        matches = self.matcher.find_patterns(path)
        scored = self.scorer.score_relationships(matches)
        return self.formatter.format(scored)
```

**Wu Lun Relationship:** 朋友 (friends) - equal peers
**Coupling:** Medium
**Observability:** Import-time registration

### 1.2 Registry Pattern (夫婦 Relationship - Complementary)

```python
# patterns/registry.py

class PatternRegistry:
    """
    Central registry - has 夫婦 (complementary) relationship with patterns
    Registry manages, patterns provide functionality
    """
    _patterns: Dict[str, re.Pattern] = {}

    @classmethod
    def register(cls, name: str, pattern: re.Pattern):
        """Patterns register themselves - complementary relationship"""
        cls._patterns[name] = pattern

    @classmethod
    def get(cls, name: str) -> re.Pattern:
        return cls._patterns.get(name)

# patterns/credentials.py
from patterns.registry import PatternRegistry

# Self-registration at import time
PatternRegistry.register('aws_key', re.compile(r'AKIA[0-9A-Z]{16}'))
PatternRegistry.register('github_token', re.compile(r'gh[ps]_[A-Za-z0-9]{36}'))

# Usage
pattern = PatternRegistry.get('aws_key')  # Complementary access
```

**Wu Lun Relationship:** 夫婦 (complementary) - manager-managed
**Coupling:** Loose (registry mediates)
**Observability:** Registry can log all accesses

### 1.3 Event Bus Pattern (君臣 Relationship - Ruler-Subject)

```python
# core/event_bus.py

class EventBus:
    """
    Central event coordinator - 君臣 (ruler-subject) relationship
    Components publish/subscribe to events
    """
    _subscribers: Dict[str, List[Callable]] = {}

    @classmethod
    def subscribe(cls, event: str, handler: Callable):
        """Subject registers loyalty to ruler's events"""
        if event not in cls._subscribers:
            cls._subscribers[event] = []
        cls._subscribers[event].append(handler)

    @classmethod
    def publish(cls, event: str, data: Any):
        """Ruler broadcasts command to subjects"""
        for handler in cls._subscribers.get(event, []):
            try:
                handler(data)
            except Exception as e:
                print(f"Handler failed: {e}")

# detection/matcher.py
from core.event_bus import EventBus

def on_secret_detected(detection: Dict):
    """Subject responds to ruler's command"""
    print(f"Secret detected: {detection['pattern']}")

EventBus.subscribe('secret_detected', on_secret_detected)

# core/scanner.py
def scan_file(self, path: Path):
    matches = self.matcher.find_patterns(path)
    for match in matches:
        EventBus.publish('secret_detected', match)  # Ruler issues command
```

**Wu Lun Relationship:** 君臣 (ruler-subject) - hierarchical
**Coupling:** Very loose (publisher doesn't know subscribers)
**Observability:** Bus can log all events
**TTT Integration:** Events become audit trail

---

## Level 2: Cellular Connectivity (Service → Service)

**Scale:** Between independent processes/containers
**Use Case:** IF.armour.yologuard ↔ IF.armour.honeypot ↔ IF.armour.learner
**Philosophy:** Indra's Net - services reflect each other

### 2.1 REST API (External Connectivity)

```python
# IF.armour.yologuard/api/rest_server.py
from fastapi import FastAPI

app = FastAPI(title="IF.armour.yologuard")

@app.post("/scan")
async def scan(request: ScanRequest) -> ScanResponse:
    """External-facing REST API for secret detection"""
    scanner = SecretScanner()
    detections = scanner.scan_content(request.content)
    return ScanResponse(detections=detections)

# IF.armour.honeypot uses REST to query yologuard
import httpx

class HoneypotManager:
    def validate_honeytoken(self, token: str) -> bool:
        """Check if token is real secret (via yologuard REST API)"""
        response = httpx.post(
            'https://yologuard.internal:8082/scan',
            json={'content': token, 'profile': 'forensics'}
        )
        return len(response.json()['detections']) > 0
```

**Characteristics:**
- **Latency:** Milliseconds (HTTP overhead)
- **Coupling:** Loose (HTTP contract only)
- **Observability:** Full (HTTP logs, metrics)
- **Protocol:** HTTP/1.1, HTTP/2, HTTP/3
- **Auth:** Bearer tokens, mTLS, OAuth2
- **TTT:** Every request logged with provenance

**When to use:** Public APIs, cross-language, external integrations

### 2.2 gRPC (Internal Connectivity)

```protobuf
// IF.armour.proto - Shared schema for all IF.armour services

syntax = "proto3";

package ifarmour;

service YologuardService {
  rpc ScanContent(ScanRequest) returns (ScanResponse);
  rpc ScanFile(FileRequest) returns (ScanResponse);
  rpc GetPatterns(Empty) returns (PatternList);
}

service HoneypotService {
  rpc GenerateToken(TokenRequest) returns (Token);
  rpc CheckAccess(AccessEvent) returns (AttackerProfile);
}

service LearnerService {
  rpc SynthesizePattern(ThreatIntel) returns (PatternProposal);
  rpc DeployPattern(Pattern) returns (DeploymentResult);
}

message ScanRequest {
  string content = 1;
  string filename = 2;
  string profile = 3;
}

message ScanResponse {
  repeated Detection detections = 1;
  Metadata metadata = 2;
}
```

```python
# IF.armour.yologuard/api/grpc_server.py
import grpc
from concurrent import futures
import ifarmour_pb2
import ifarmour_pb2_grpc

class YologuardServicer(ifarmour_pb2_grpc.YologuardServiceServicer):
    def ScanContent(self, request, context):
        scanner = SecretScanner(profile=request.profile)
        detections = scanner.scan_content(request.content, request.filename)

        return ifarmour_pb2.ScanResponse(
            detections=[self._to_proto(d) for d in detections],
            metadata=ifarmour_pb2.Metadata(count=len(detections))
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ifarmour_pb2_grpc.add_YologuardServiceServicer_to_server(
        YologuardServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

# IF.armour.learner calls yologuard via gRPC
import grpc
import ifarmour_pb2_grpc

class PatternValidator:
    def __init__(self):
        channel = grpc.insecure_channel('yologuard.internal:50051')
        self.stub = ifarmour_pb2_grpc.YologuardServiceStub(channel)

    def test_pattern(self, pattern: str, test_cases: List[str]) -> float:
        """Test candidate pattern via gRPC"""
        results = []
        for test_case in test_cases:
            response = self.stub.ScanContent(
                ifarmour_pb2.ScanRequest(
                    content=test_case,
                    profile='forensics'
                )
            )
            results.append(len(response.detections) > 0)

        return sum(results) / len(results)  # Precision
```

**Characteristics:**
- **Latency:** Sub-millisecond (binary protocol)
- **Coupling:** Schema contract (proto files)
- **Observability:** Built-in metrics, tracing
- **Protocol:** HTTP/2 (multiplexing, streaming)
- **Auth:** mTLS (mutual TLS certificates)
- **TTT:** Metadata includes provenance automatically

**When to use:** Internal microservices, high performance, streaming

### 2.3 Message Queue (Asynchronous, 父子 Relationship - Generational)

```python
# IF.armour.learner publishes new patterns to queue
import pika

class PatternPublisher:
    """
    父子 (generational) relationship - parent creates, child consumes later
    Time-decoupled communication
    """
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('rabbitmq.internal')
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='pattern_updates', durable=True)

    def publish_pattern(self, pattern: Dict):
        """Parent (learner) creates pattern for future child (yologuard)"""
        self.channel.basic_publish(
            exchange='',
            routing_key='pattern_updates',
            body=json.dumps(pattern),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistent
                timestamp=int(datetime.utcnow().timestamp()),
                headers={'source': 'IF.armour.learner', 'version': '4.2'}
            )
        )

# IF.armour.yologuard consumes patterns from queue
class PatternConsumer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('rabbitmq.internal')
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='pattern_updates', durable=True)

    def start_consuming(self):
        """Child (yologuard) receives patterns from parent (learner)"""
        self.channel.basic_consume(
            queue='pattern_updates',
            on_message_callback=self.on_pattern_received,
            auto_ack=False
        )
        self.channel.start_consuming()

    def on_pattern_received(self, ch, method, properties, body):
        """Process new pattern from learner"""
        pattern = json.loads(body)

        # Test pattern on corpus
        if self._validate_pattern(pattern):
            # Add to registry
            PatternRegistry.register(pattern['name'], pattern['regex'])
            print(f"✅ Added pattern: {pattern['name']}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            # Reject pattern
            print(f"❌ Rejected pattern: {pattern['name']} (failed validation)")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

**Wu Lun Relationship:** 父子 (generational) - parent creates, child inherits
**Characteristics:**
- **Latency:** Seconds to minutes (async)
- **Coupling:** Very loose (temporal decoupling)
- **Observability:** Queue metrics (depth, lag)
- **Protocol:** AMQP (RabbitMQ), Kafka, Redis Streams
- **Reliability:** Persistent, replayable
- **TTT:** Message headers include full provenance

**When to use:** Background jobs, event streaming, rate limiting

---

## Level 3: Organism Connectivity (IF.module → IF.module)

**Scale:** Between major IF.* components
**Use Case:** IF.armour ↔ IF.swarm ↔ IF.guard ↔ IF.optimise ↔ IF.search
**Philosophy:** All philosophies combined - this is the **nervous system** of InfraFabric

### 3.1 IF.connect Protocol (Universal Standard)

**Core Specification:**

```python
# IF.connect/protocol.py

from dataclasses import dataclass
from typing import Any, Dict, Optional
from enum import Enum

class ConnectionType(Enum):
    """Wu Lun-inspired connection types"""
    PENGYOU = "朋友"      # Friends (equal peers)
    FUFU = "夫婦"         # Complementary (provider-consumer)
    JUNCHIN = "君臣"      # Hierarchical (orchestrator-worker)
    FUZI = "父子"         # Generational (async, temporal)
    XIONGDI = "兄弟"      # Siblings (parallel, coordinated)

@dataclass
class IFMessage:
    """
    Universal message format for all IF.* modules
    Implements TTT (Traceability, Trust, Transparency)
    """
    # Core payload
    sender: str              # e.g., "IF.armour.yologuard"
    receiver: str            # e.g., "IF.swarm"
    operation: str           # e.g., "scan", "vote", "optimize"
    payload: Dict[str, Any]  # Operation-specific data

    # TTT Provenance
    provenance: Dict[str, Any] = None
    """
    {
        'timestamp': '2025-11-08T12:00:00Z',
        'commit': 'abc123',
        'version': '4.0',
        'trace_id': 'uuid-1234',  # Distributed tracing
        'span_id': 'uuid-5678'
    }
    """

    # Wu Lun Relationship
    connection_type: ConnectionType = ConnectionType.PENGYOU

    # Kantian Duty Constraints
    constraints: Dict[str, Any] = None
    """
    {
        'max_cost_usd': 0.10,       # IF.optimise constraint
        'timeout_seconds': 30,       # Performance constraint
        'no_data_retention': True,   # Privacy constraint (Kantian)
        'audit_required': True       # TTT constraint
    }
    """

    # Indra's Net Reflection
    reflects: Optional['IFMessage'] = None  # Parent message (if this is a response)

    def to_dict(self) -> Dict:
        """Serialize to dict for JSON/gRPC/MQ"""
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'operation': self.operation,
            'payload': self.payload,
            'provenance': self.provenance or {},
            'connection_type': self.connection_type.value,
            'constraints': self.constraints or {},
            'reflects': self.reflects.to_dict() if self.reflects else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'IFMessage':
        """Deserialize from dict"""
        return cls(
            sender=data['sender'],
            receiver=data['receiver'],
            operation=data['operation'],
            payload=data['payload'],
            provenance=data.get('provenance'),
            connection_type=ConnectionType(data.get('connection_type', '朋友')),
            constraints=data.get('constraints'),
            reflects=cls.from_dict(data['reflects']) if data.get('reflects') else None
        )
```

### 3.2 Example: IF.armour.yologuard → IF.swarm → IF.guard

**Scenario:** IF.armour.learner proposes a new pattern. Needs multi-LLM validation (IF.swarm) then governance approval (IF.guard).

```python
# IF.armour.learner/synthesis.py

from IF.connect import IFMessage, ConnectionType
import requests

class PatternProposer:
    def propose_pattern(self, pattern: Dict):
        """
        Propose new pattern:
        1. IF.learner → IF.swarm (validation via consensus)
        2. IF.swarm → IF.guard (governance approval)
        3. IF.guard → IF.learner (approved/rejected)
        """

        # Step 1: IF.learner → IF.swarm (朋友 relationship - peers)
        swarm_request = IFMessage(
            sender='IF.armour.learner',
            receiver='IF.swarm',
            operation='validate_pattern',
            payload={
                'pattern': pattern,
                'question': 'Is this pattern production-ready?',
                'voters': 8,
                'threshold': 0.75
            },
            connection_type=ConnectionType.PENGYOU,  # Equal peers
            provenance={
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'commit': get_git_commit(),
                'version': '4.2',
                'trace_id': str(uuid.uuid4())
            },
            constraints={
                'max_cost_usd': 0.10,      # IF.optimise will enforce
                'timeout_seconds': 60,
                'audit_required': True     # TTT requirement
            }
        )

        # Send to IF.swarm via HTTP/gRPC/MQ (transport-agnostic)
        swarm_response = self._send_message(swarm_request)

        # Step 2: IF.swarm → IF.guard (君臣 relationship - hierarchical)
        if swarm_response.payload['consensus'] >= 0.75:
            guard_request = IFMessage(
                sender='IF.swarm',
                receiver='IF.guard',
                operation='approve_pattern',
                payload={
                    'title': f'Deploy pattern: {pattern["name"]}',
                    'description': f'Swarm consensus: {swarm_response.payload["consensus"]:.0%}',
                    'benefits': ['Improved detection', 'Community-validated'],
                    'risks': ['Potential FP', 'Performance impact'],
                    'evidence': swarm_response.payload['votes']
                },
                connection_type=ConnectionType.JUNCHIN,  # Hierarchical
                provenance=swarm_response.provenance,
                reflects=swarm_request  # Indra's Net - response reflects request
            )

            guard_response = self._send_message(guard_request)

            # Step 3: IF.guard → IF.learner (父子 relationship - generational)
            if guard_response.payload['decision'] == 'approve':
                # Deploy to IF.armour.yologuard
                self._deploy_pattern(pattern)
                return True
            else:
                print(f"Guardian rejected: {guard_response.payload['rationale']}")
                return False
        else:
            print(f"Swarm rejected: consensus {swarm_response.payload['consensus']:.0%} < 75%")
            return False

    def _send_message(self, message: IFMessage) -> IFMessage:
        """
        Transport-agnostic message sending
        Chooses best transport based on IF.optimise recommendation
        """
        # Option 1: REST API
        if self._is_rest_available(message.receiver):
            response_dict = requests.post(
                f'https://{message.receiver}.internal/if-connect',
                json=message.to_dict(),
                timeout=message.constraints.get('timeout_seconds', 30)
            ).json()
            return IFMessage.from_dict(response_dict)

        # Option 2: gRPC (faster for internal)
        elif self._is_grpc_available(message.receiver):
            stub = self._get_grpc_stub(message.receiver)
            response_proto = stub.SendMessage(message.to_proto())
            return IFMessage.from_proto(response_proto)

        # Option 3: Message queue (async)
        else:
            self._publish_to_queue(message)
            return self._wait_for_response(message.provenance['trace_id'])
```

**IF.swarm Implementation:**

```python
# IF.swarm/server.py

from IF.connect import IFMessage, ConnectionType
from fastapi import FastAPI

app = FastAPI(title="IF.swarm")

@app.post("/if-connect")
async def handle_message(request: Dict) -> Dict:
    """
    Universal IF.connect endpoint
    All IF.* modules expose this endpoint
    """
    message = IFMessage.from_dict(request)

    # Route to operation handler
    if message.operation == 'validate_pattern':
        result = await validate_pattern(message.payload)

        # Create response (Indra's Net - reflects request)
        response = IFMessage(
            sender='IF.swarm',
            receiver=message.sender,  # Reply to sender
            operation='validation_result',
            payload=result,
            connection_type=message.connection_type,  # Preserve relationship
            provenance={
                **message.provenance,
                'handled_at': datetime.utcnow().isoformat() + 'Z',
                'handler': 'IF.swarm.validate_pattern'
            },
            reflects=message  # Indra's Net principle
        )

        return response.to_dict()
    else:
        raise HTTPException(status_code=400, detail=f"Unknown operation: {message.operation}")

async def validate_pattern(payload: Dict) -> Dict:
    """Multi-LLM consensus validation"""
    pattern = payload['pattern']
    voters = payload['voters']
    threshold = payload['threshold']

    # Spawn IF.swarm agents
    votes = []
    for i in range(voters):
        agent_result = await self._spawn_agent(pattern, voter_id=i)
        votes.append(agent_result)

    # Calculate consensus
    consensus = sum(votes) / len(votes)

    return {
        'consensus': consensus,
        'votes': votes,
        'decision': 'approve' if consensus >= threshold else 'reject'
    }
```

**IF.guard Implementation:**

```python
# IF.guard/server.py

from IF.connect import IFMessage

@app.post("/if-connect")
async def handle_message(request: Dict) -> Dict:
    message = IFMessage.from_dict(request)

    if message.operation == 'approve_pattern':
        # Guardian deliberation
        result = guardians.debate_proposal(
            message.payload,
            proposal_type='technical'
        )

        # TTT Audit Trail
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'proposal': message.payload['title'],
            'decision': result['decision'],
            'weighted_votes': result['weighted_votes'],
            'trace_id': message.provenance['trace_id']  # Link to original request
        }
        self._write_audit_log(audit_entry)

        response = IFMessage(
            sender='IF.guard',
            receiver=message.sender,
            operation='approval_result',
            payload={
                'decision': result['decision'],
                'rationale': result.get('rationale', ''),
                'audit_id': audit_entry['trace_id']
            },
            provenance={
                **message.provenance,
                'approved_at': datetime.utcnow().isoformat() + 'Z'
            },
            reflects=message
        )

        return response.to_dict()
```

### 3.3 IF.optimise Integration (Token & Cost Tracking)

```python
# IF.optimise/middleware.py

class IFOptimiseMiddleware:
    """
    Transparent cost tracking for all IF.connect messages
    Intercepts messages, tracks token usage, enforces budget constraints
    """

    def __init__(self):
        self.cost_tracker = {}

    async def __call__(self, message: IFMessage, handler: Callable) -> IFMessage:
        """Middleware wraps every IF.connect message"""

        # Check constraints BEFORE execution (Kantian duty)
        if message.constraints:
            max_cost = message.constraints.get('max_cost_usd', float('inf'))

            # Estimate cost based on operation
            estimated_cost = self._estimate_cost(message)

            if estimated_cost > max_cost:
                raise BudgetExceededError(
                    f"Estimated cost ${estimated_cost:.4f} exceeds limit ${max_cost:.4f}"
                )

        # Track start time
        start_time = time.time()
        start_tokens = self._get_token_count()

        # Execute handler
        response = await handler(message)

        # Track end time + tokens
        end_time = time.time()
        end_tokens = self._get_token_count()

        # Calculate actual cost
        tokens_used = end_tokens - start_tokens
        actual_cost = self._calculate_cost(tokens_used, message.receiver)

        # Record in cost tracker
        trace_id = message.provenance.get('trace_id')
        self.cost_tracker[trace_id] = {
            'operation': message.operation,
            'sender': message.sender,
            'receiver': message.receiver,
            'tokens': tokens_used,
            'cost_usd': actual_cost,
            'duration_seconds': end_time - start_time,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

        # Add cost to response provenance (TTT)
        response.provenance['cost_usd'] = actual_cost
        response.provenance['tokens_used'] = tokens_used

        return response

    def _estimate_cost(self, message: IFMessage) -> float:
        """Estimate cost before execution"""
        # IF.swarm with 8 agents using Sonnet
        if message.receiver == 'IF.swarm' and message.payload.get('voters') == 8:
            return 0.08  # Estimated $0.01 per agent

        # IF.search semantic search
        elif message.receiver == 'IF.search' and message.operation == 'search':
            return 0.005  # Embedding generation cost

        # Default: small cost
        return 0.001
```

### 3.4 IF.search Integration (Cross-Repository Indexing)

```python
# IF.search/indexer.py

class CrossRepoSearchIndex:
    """
    兄弟 (siblings) relationship - IF.search coordinates multiple IF.armour instances
    Each InfraFabric deployment can contribute to global search index
    """

    def index_detection(self, message: IFMessage):
        """
        When IF.armour.yologuard detects a secret, index it for search
        (Secret redacted, only metadata indexed)
        """
        if message.sender == 'IF.armour.yologuard' and message.operation == 'secret_detected':
            detection = message.payload

            # Extract metadata (not the secret itself - Kantian duty)
            doc = {
                'id': str(uuid.uuid4()),
                'pattern': detection['pattern'],
                'severity': detection['severity'],
                'file': detection['file'],
                'line': detection['line'],
                'provenance': detection['provenance'],
                'timestamp': message.provenance['timestamp'],
                'repo': detection['provenance'].get('repo'),
                'commit': detection['provenance'].get('commit'),
                # No 'match' field - secret is not stored
            }

            # Index in Elasticsearch/Meilisearch
            self.es_client.index(index='if-secrets', document=doc)

    def search(self, query: str, filters: Dict) -> List[Dict]:
        """
        Search across all indexed detections
        兄弟 (siblings) - parallel search across multiple repos
        """
        results = self.es_client.search(
            index='if-secrets',
            query={
                'bool': {
                    'must': [
                        {'match': {'pattern': query}}
                    ],
                    'filter': [
                        {'term': {'severity': filters.get('severity', 'ERROR')}}
                    ]
                }
            }
        )

        return [hit['_source'] for hit in results['hits']['hits']]

    def get_blast_radius(self, pattern: str) -> int:
        """
        Find how many files use a particular secret pattern
        Uses IF.connect to query all IF.armour instances
        """
        # Send IF.connect message to all known IF.armour instances
        instances = ['if-armour-prod', 'if-armour-staging', 'if-armour-dev']

        total_files = 0
        for instance in instances:
            message = IFMessage(
                sender='IF.search',
                receiver=instance,
                operation='count_pattern_usage',
                payload={'pattern': pattern},
                connection_type=ConnectionType.XIONGDI,  # Siblings
                provenance={'trace_id': str(uuid.uuid4())}
            )

            response = self._send_message(message)
            total_files += response.payload['count']

        return total_files
```

---

## Level 4: Ecosystem Connectivity (InfraFabric → InfraFabric)

**Scale:** Federation of InfraFabric deployments
**Use Case:** Company A's InfraFabric ↔ Company B's InfraFabric
**Philosophy:** Indra's Net at planetary scale + Kantian duty (privacy, security)

### 4.1 Federation Protocol

```python
# IF.connect/federation.py

class IFFederation:
    """
    Federation layer - connect multiple InfraFabric instances
    Use cases:
    - Multi-org collaboration (shared threat intel)
    - Dev/staging/prod environments
    - Geographic distribution (EU/US/APAC)
    """

    def __init__(self, instance_id: str, federation_config: Dict):
        self.instance_id = instance_id  # e.g., "if-org-a"
        self.peers = federation_config.get('peers', [])
        self.trust_level = federation_config.get('trust_level', 'low')

    def federate_message(self, message: IFMessage) -> List[IFMessage]:
        """
        Send message to federated instances
        Returns aggregated responses
        """
        # Kantian duty: Only federate if allowed
        if not self._is_federatable(message):
            raise FederationForbidden("Message contains sensitive data")

        responses = []
        for peer in self.peers:
            # Add federation metadata
            federated_message = IFMessage(
                sender=f"{self.instance_id}.{message.sender}",
                receiver=f"{peer}.{message.receiver}",
                operation=message.operation,
                payload=self._sanitize_payload(message.payload),
                provenance={
                    **message.provenance,
                    'federated_from': self.instance_id,
                    'federation_hop': message.provenance.get('federation_hop', 0) + 1
                },
                constraints={
                    **message.constraints,
                    'max_federation_hops': 3  # Prevent infinite loops
                }
            )

            # Send to peer (cross-internet, high latency)
            response = self._send_federated(peer, federated_message)
            responses.append(response)

        return responses

    def _is_federatable(self, message: IFMessage) -> bool:
        """Kantian duty check: Can this message be federated?"""
        # Never federate if contains secrets
        if 'secret' in message.payload or 'credential' in message.payload:
            return False

        # Never federate if privacy constraint set
        if message.constraints.get('no_federation', False):
            return False

        # Only federate if trust level allows
        if self.trust_level == 'low' and message.operation in ['scan', 'detect']:
            return False  # Don't share detection data with low-trust peers

        return True

    def _sanitize_payload(self, payload: Dict) -> Dict:
        """Remove sensitive data before federation"""
        sanitized = payload.copy()

        # Remove actual secret matches
        if 'detections' in sanitized:
            for detection in sanitized['detections']:
                detection.pop('match', None)  # Remove redacted match
                detection.pop('context', None)  # Remove surrounding code

        return sanitized
```

### 4.2 Example: Global Threat Intelligence Network

```python
# IF.armour.learner/threat_intel_federation.py

class GlobalThreatIntelNetwork:
    """
    Federation use case: Share threat intelligence across organizations
    兄弟 (siblings) relationship at planetary scale
    """

    def __init__(self):
        self.federation = IFFederation(
            instance_id='if-org-acme',
            federation_config={
                'peers': ['if-org-globex', 'if-org-initech'],
                'trust_level': 'high'  # Trusted partners
            }
        )

    def share_new_pattern(self, pattern: Dict):
        """
        When learner discovers new pattern, share with federation
        Other orgs can benefit from your threat intelligence
        """
        # Sanitize pattern (remove org-specific details)
        sanitized_pattern = {
            'name': pattern['name'],
            'regex': pattern['regex'],
            'severity': pattern['severity'],
            'source': 'threat_intel',
            'discovered_at': datetime.utcnow().isoformat() + 'Z'
            # NO org-specific data (file paths, commit hashes, etc.)
        }

        message = IFMessage(
            sender='IF.armour.learner',
            receiver='IF.armour.learner',  # Same module at peer instances
            operation='contribute_pattern',
            payload=sanitized_pattern,
            connection_type=ConnectionType.XIONGDI,  # Siblings
            provenance={
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'trace_id': str(uuid.uuid4())
            },
            constraints={
                'no_data_retention': True,  # Don't store our pattern permanently
                'attribution_required': False  # Anonymous contribution
            }
        )

        # Federate to all peers
        responses = self.federation.federate_message(message)

        # Count how many peers accepted the pattern
        accepted = sum(1 for r in responses if r.payload.get('accepted', False))
        print(f"Pattern shared with {len(self.federation.peers)} peers, {accepted} accepted")

    def receive_federated_pattern(self, message: IFMessage):
        """
        Receive pattern contribution from federated peer
        Validate and decide whether to adopt
        """
        pattern = message.payload

        # Validate pattern (test on our corpus)
        if self._validate_pattern(pattern):
            # Ask IF.guard for approval (even federated patterns need governance)
            guard_message = IFMessage(
                sender='IF.armour.learner',
                receiver='IF.guard',
                operation='approve_federated_pattern',
                payload={
                    'title': f'Adopt federated pattern: {pattern["name"]}',
                    'description': f'Contributed by {message.provenance["federated_from"]}',
                    'pattern': pattern,
                    'source': 'federation'
                },
                connection_type=ConnectionType.JUNCHIN
            )

            guard_response = self._send_message(guard_message)

            if guard_response.payload['decision'] == 'approve':
                # Deploy pattern
                PatternRegistry.register(pattern['name'], pattern['regex'])
                return {'accepted': True}
            else:
                return {'accepted': False, 'reason': 'guardian_rejected'}
        else:
            return {'accepted': False, 'reason': 'validation_failed'}
```

---

## TTT Integration Across All Levels

### Audit Trail Generation

Every IF.connect message automatically creates TTT audit entries:

```python
# IF.connect/ttt.py

class TTTAuditLogger:
    """
    Automatic audit logging for all IF.connect messages
    Implements TTT (Traceability, Trust, Transparency)
    """

    def log_message(self, message: IFMessage, response: IFMessage):
        """Log message + response pair"""
        audit_entry = {
            # Traceability
            'trace_id': message.provenance['trace_id'],
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'sender': message.sender,
            'receiver': message.receiver,
            'operation': message.operation,

            # Trust (relationships)
            'connection_type': message.connection_type.value,
            'relationship_strength': self._calculate_trust(message),

            # Transparency (what happened)
            'request_summary': self._summarize_payload(message.payload),
            'response_summary': self._summarize_payload(response.payload),
            'duration_ms': (response.provenance['handled_at'] - message.provenance['timestamp']).total_seconds() * 1000,

            # Cost (IF.optimise)
            'cost_usd': response.provenance.get('cost_usd', 0.0),
            'tokens_used': response.provenance.get('tokens_used', 0),

            # Kantian duty compliance
            'constraints_honored': self._check_constraints(message, response),

            # Indra's Net (reflection chain)
            'reflects': message.reflects.provenance['trace_id'] if message.reflects else None
        }

        # Write to append-only audit log
        self._write_audit(audit_entry)

        # Write to blockchain (optional, for immutability)
        if message.constraints.get('blockchain_audit', False):
            self._write_to_blockchain(audit_entry)

    def _calculate_trust(self, message: IFMessage) -> float:
        """
        Calculate trust score based on Wu Lun relationship + history
        Similar to Confucian relationship scoring in yologuard
        """
        # Base score from relationship type
        relationship_scores = {
            ConnectionType.PENGYOU: 0.85,    # Friends (high trust)
            ConnectionType.FUFU: 0.75,       # Complementary
            ConnectionType.JUNCHIN: 0.90,    # Hierarchical (very high trust)
            ConnectionType.FUZI: 0.65,       # Generational
            ConnectionType.XIONGDI: 0.70     # Siblings
        }

        base_score = relationship_scores.get(message.connection_type, 0.50)

        # Adjust based on sender/receiver history
        history_multiplier = self._get_history_multiplier(message.sender, message.receiver)

        return min(base_score * history_multiplier, 1.0)
```

### Manifest Generation

```python
# IF.connect/manifest.py

class TTTManifestGenerator:
    """Generate compliance-ready manifests from audit logs"""

    def generate_manifest(self, trace_id: str) -> Dict:
        """
        Generate manifest for a complete operation
        Traces all IF.connect messages for a single trace_id
        """
        # Collect all audit entries for this trace
        entries = self.audit_db.query(trace_id=trace_id)

        # Build call graph (Indra's Net)
        call_graph = self._build_call_graph(entries)

        # Calculate total cost
        total_cost = sum(e['cost_usd'] for e in entries)

        manifest = {
            'trace_id': trace_id,
            'timestamp': entries[0]['timestamp'],
            'initiator': entries[0]['sender'],
            'operation': entries[0]['operation'],

            # Call chain
            'call_graph': call_graph,
            'total_messages': len(entries),
            'modules_involved': list(set(e['sender'] for e in entries)),

            # Cost summary
            'total_cost_usd': total_cost,
            'total_tokens': sum(e['tokens_used'] for e in entries),

            # Trust summary
            'average_trust': sum(e['relationship_strength'] for e in entries) / len(entries),

            # Compliance
            'constraints_honored': all(e['constraints_honored'] for e in entries),
            'kantian_violations': [e for e in entries if not e['constraints_honored']],

            # Evidence
            'audit_entries': entries,
            'blockchain_hashes': [e.get('blockchain_hash') for e in entries if e.get('blockchain_hash')]
        }

        return manifest
```

---

## Summary: The Complete IF.connect Stack

```
Level 4: Ecosystem (IF ↔ IF)
   │  Protocol: Federation API
   │  Latency: Seconds (cross-internet)
   │  Philosophy: Indra's Net (planetary scale) + Kantian duty (privacy)
   │
Level 3: Organism (IF.module ↔ IF.module)
   │  Protocol: IF.connect (universal messaging)
   │  Latency: Milliseconds
   │  Philosophy: Wu Lun (5 relationships) + TTT (audit trails)
   │
Level 2: Cellular (service ↔ service)
   │  Protocol: REST, gRPC, Message Queue
   │  Latency: Milliseconds
   │  Philosophy: IF.ground (observable) + IF.optimise (cost-aware)
   │
Level 1: Molecular (module ↔ module)
   │  Protocol: Import, Registry, Event Bus
   │  Latency: Microseconds
   │  Philosophy: Wu Lun (朋友, 夫婦, 君臣) + Aristotelian (essence)
   │
Level 0: Quantum (function ↔ function)
   │  Protocol: Direct call, Callback
   │  Latency: Nanoseconds
   │  Philosophy: Aristotelian (simplicity, necessity)
```

**Key Principles:**

1. **Wu Lun (五倫) Relationships:** Every connection has a type (朋友, 夫婦, 君臣, 父子, 兄弟)
2. **TTT Everywhere:** All messages include provenance, audit trails, transparency
3. **Kantian Duty:** Constraints enforced at every level (privacy, cost, security)
4. **IF.ground:** All connectivity is observable, testable, verifiable
5. **Indra's Net:** Messages reflect each other (request-response chains preserved)
6. **IF.optimise:** Cost tracking automatic across all levels

**Implementation Priority:**

1. **Week 1-2:** Implement Level 0-1 (within IF.armour.yologuard modular refactoring)
2. **Week 3:** Implement Level 2 (REST + gRPC for IF.armour services)
3. **Week 4:** Implement Level 3 (IF.connect protocol, integrate IF.swarm/IF.guard)
4. **Week 5+:** Implement Level 4 (federation, optional for v4.0)

---

**Next Steps:**
1. Review this architecture with IF.guard (Guardian approval)
2. Create reference implementation (IF.connect Python library)
3. Refactor IF.armour.yologuard v3.2 to use IF.connect
4. Document API schemas (OpenAPI, gRPC proto files)
5. Build monitoring dashboard (Grafana + TTT audit logs)

**Questions for User:**
- Is Level 4 (federation) needed for v4.0, or defer to v5.0?
- Should IF.connect be a separate Python package (`pip install if-connect`)?
- Preference for message transport: REST vs gRPC vs hybrid?
