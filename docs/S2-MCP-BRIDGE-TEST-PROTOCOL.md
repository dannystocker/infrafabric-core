# S² MCP Bridge Test Protocol (TTT Compliant)

**Protocol ID:** `if://test-protocol/s2-mcp-bridge/v1.0`
**Created:** 2025-11-13
**Purpose:** Validate MCP bridge for 9-agent S² coordination with full TTT compliance
**Architecture:** 1 Orchestrator + 7 Cloud Sessions + 1 WSL CLI

---

## Executive Summary

This protocol tests the `mcp-multiagent-bridge` for coordinating 9 concurrent agents in InfraFabric S² architecture. All tests include TTT (Traceable, Transparent, Trustworthy) compliance with automated logging, performance metrics, and security validation.

**Expected Results:**
- ✅ Latency: <5ms average (proven: 1.7ms in stress test)
- ✅ Reliability: 100% message delivery
- ✅ Security: HMAC auth + secret redaction + 4-stage YOLO Guard
- ✅ Concurrency: 9 agents with zero race conditions
- ✅ TTT Compliance: Complete audit trail with IF.TTT citations

---

## S² Architecture

```
                    ┌─────────────────────────────┐
                    │   ORCHESTRATOR (This)       │
                    │   Cloud Session (Sonnet)    │
                    │   Role: s2-orchestrator     │
                    └──────────────┬──────────────┘
                                   │
                ┌──────────────────┼──────────────────┐
                │  MCP Bridge (9 conversations)      │
                │  - create_conversation() x9        │
                │  - send_to_partner() for tasks     │
                │  - check_messages() for status     │
                │  - SQLite WAL: /tmp/s2-prod.db     │
                │  - JSONL audit: s2-audit.jsonl     │
                └──────────────────┼──────────────────┘
                                   │
        ┌──────────────────────────┼────────────────────────┐
        │                          │                        │
   ┌────▼─────┐             ┌──────▼──────┐         ┌──────▼──────┐
   │ Cloud 1  │             │  Cloud 2    │         │  Cloud 3    │
   │ (Backend)│             │ (Frontend)  │         │  (Tests)    │
   └──────────┘             └─────────────┘         └─────────────┘
        │                          │                        │
   ┌────▼─────┐             ┌──────▼──────┐         ┌──────▼──────┐
   │ Cloud 4  │             │  Cloud 5    │         │  Cloud 6    │
   │ (Docs)   │             │ (Deploy)    │         │ (Review)    │
   └──────────┘             └─────────────┘         └─────────────┘
        │                          │
   ┌────▼─────┐             ┌──────▼──────┐
   │ WSL CLI  │             │Cloud Codex  │
   │(Local Dev)│            │(Code Gen)   │
   └──────────┘             └─────────────┘
```

**Agent Roles:**
1. **Orchestrator** - Task assignment, coordination, monitoring (this session)
2. **Cloud 1-7** - Worker agents on separate cloud machines
3. **WSL CLI** - Local Claude Code CLI on Windows Subsystem for Linux
4. **Cloud Codex** - OpenAI Codex on Cloud Machine 8

---

## Test Suite

### Test 1: Installation & Setup (TTT: Traceable)

**Objective:** All 9 agents install MCP bridge with single command

**Single-Command Installer:**
```bash
curl -fsSL https://raw.githubusercontent.com/dannystocker/mcp-multiagent-bridge/main/scripts/install.sh | bash
```

**Or manual:**
```bash
cd /tmp && \
git clone https://github.com/dannystocker/mcp-multiagent-bridge.git && \
cd mcp-multiagent-bridge && \
pip install -q mcp>=1.0.0 && \
echo '{"mcpServers":{"bridge":{"command":"python3","args":["'$(pwd)'/claude_bridge_secure.py"]}}}' > ~/.config/claude/claude.json && \
echo "✅ MCP Bridge installed at: $(pwd)"
```

**TTT Citation:**
```yaml
citation_id: if://test/s2-mcp-bridge/installation
type: setup_verification
timestamp: [test_run_timestamp]

installation:
  bridge_path: "/tmp/mcp-multiagent-bridge"
  python_version: "3.11+"
  mcp_version: ">=1.0.0"
  config_file: "~/.config/claude/claude.json"

validation:
  - python3 /tmp/mcp-multiagent-bridge/test_bridge.py
  - python3 /tmp/mcp-multiagent-bridge/test_security.py

result:
  status: "pass/fail"
  agents_installed: [list of 9 agent IDs]
  installation_time: "seconds"
```

**Success Criteria:**
- ✅ All 9 agents have bridge installed
- ✅ Security tests pass (YOLO guard, rate limiter)
- ✅ MCP config file created

---

### Test 2: Conversation Creation (TTT: Transparent)

**Objective:** Orchestrator creates 8 conversations (one per worker)

**Orchestrator Actions:**
```
For each worker (1-8):
  1. Use MCP tool: create_conversation
     - my_role: "s2-orchestrator"
     - partner_role: "worker-{1-8}"

  2. Save credentials to git:
     File: /tmp/s2-credentials-worker-{1-8}.json
     {
       "conversation_id": "conv_...",
       "coordinator_token": "token_...",
       "worker_token": "token_...",
       "worker_id": "{1-8}",
       "created_at": "timestamp"
     }

  3. Commit to git (TTT audit trail):
     git add /tmp/s2-credentials-*.json
     git commit -m "test(s2): Create 8 bridge conversations for workers"
```

**TTT Citation:**
```yaml
citation_id: if://test/s2-mcp-bridge/conversation-creation
type: initialization
timestamp: [test_run_timestamp]

conversations:
  - id: "conv_worker1_..."
    coordinator_role: "s2-orchestrator"
    worker_role: "worker-1"
    expires_at: "timestamp+3h"
  [... repeat for workers 2-8]

validation:
  method: "Database query + credential file verification"
  database: "/tmp/s2-prod.db"
  audit_log: "bridge_audit.jsonl"

result:
  conversations_created: 8
  tokens_generated: 16 (8 coordinator + 8 worker)
  database_size: "KB"
  creation_time: "ms"
```

**Success Criteria:**
- ✅ 8 conversations created (one per worker)
- ✅ All credentials saved to git
- ✅ Database integrity check passes

---

### Test 3: Task Distribution (TTT: Traceable)

**Objective:** Orchestrator sends tasks to all 8 workers rapidly

**Orchestrator Actions:**
```
For each worker (1-8):
  Use MCP tool: send_to_partner
  - message: JSON.stringify({
      "type": "task_assignment",
      "task_id": "s2-test-task-{1-8}",
      "description": "Worker {1-8}: Run test suite and report results",
      "priority": "P1",
      "deadline": "timestamp+30min",
      "if_ttt_citation": "if://test/s2/task-{1-8}"
    })
  - action_type: "task_assignment"
```

**Performance Metrics:**
```yaml
citation_id: if://test/s2-mcp-bridge/task-distribution
type: performance_measurement
timestamp: [test_run_timestamp]

distribution:
  tasks_sent: 8
  time_to_send_all: "ms"
  average_latency_per_task: "ms"
  rate_limit_hit: false/true

database_stats:
  messages_stored: 8
  database_size_before: "KB"
  database_size_after: "KB"
  write_conflicts: 0

result:
  status: "pass/fail"
  throughput: "tasks/second"
  all_tasks_delivered: true/false
```

**Success Criteria:**
- ✅ All 8 tasks sent within 1 second
- ✅ Average latency <5ms per task
- ✅ Zero message delivery failures

---

### Test 4: Worker Response Monitoring (TTT: Transparent)

**Objective:** Orchestrator receives status updates from all 8 workers

**Orchestrator Actions:**
```
For 5 minutes:
  Every 10 seconds:
    For each conversation (1-8):
      Use MCP tool: check_messages

      If new messages:
        - Log to /tmp/s2-messages-received.jsonl
        - Count by worker
        - Track message types (ack, progress, complete)
        - Calculate latency (sent_time -> received_time)
```

**Expected Worker Messages (per worker):**
1. "Worker {1-8}: Task received" (acknowledgment)
2. "Worker {1-8}: Test in progress - 25% complete" (progress)
3. "Worker {1-8}: Test in progress - 50% complete" (progress)
4. "Worker {1-8}: Test in progress - 75% complete" (progress)
5. "Worker {1-8}: Test complete - all tests passing" (completion)

**TTT Citation:**
```yaml
citation_id: if://test/s2-mcp-bridge/worker-monitoring
type: message_flow_analysis
timestamp: [test_run_timestamp]

monitoring:
  duration: "5 minutes"
  poll_interval: "10 seconds"
  total_polls: 30 (5 min * 6 polls/min)

messages_received:
  worker_1: 5
  worker_2: 5
  worker_3: 5
  worker_4: 5
  worker_5: 5
  worker_6: 5
  worker_7: 5
  worker_8: 5
  total: 40

latency_stats:
  average: "ms"
  min: "ms"
  max: "ms"
  p95: "ms"

message_types:
  acknowledgment: 8
  progress: 24 (3 per worker)
  completion: 8

result:
  all_workers_responded: true/false
  message_delivery_rate: "100%"
  average_response_time: "seconds"
```

**Success Criteria:**
- ✅ All 8 workers send 5 messages each (40 total)
- ✅ Average latency <10ms
- ✅ 100% message delivery
- ✅ All workers report completion

---

### Test 5: Concurrent Load (TTT: Trustworthy)

**Objective:** All 8 workers send messages simultaneously (stress test)

**Worker Actions (simultaneous):**
```
All workers at same time (coordinated via timestamp):
  For i in 1..10:
    Use MCP tool: send_to_partner
    - message: "Worker {1-8}: Concurrent message #{i}"
    - action_type: "status_update"

    Wait 1 second
    Repeat
```

**Stress Test Metrics:**
```yaml
citation_id: if://test/s2-mcp-bridge/concurrent-load
type: stress_test
timestamp: [test_run_timestamp]

load_profile:
  concurrent_agents: 8
  messages_per_agent: 10
  total_messages: 80
  send_rate: "10 msg/sec (1 per agent)"
  duration: "10 seconds"

database_performance:
  sqlite_wal_mode: true
  concurrent_writes: 80
  write_conflicts: 0 (expected)
  database_integrity: "ok"

rate_limiter:
  limit: "10 req/min per session"
  sessions: 8
  total_capacity: "80 req/min"
  throttled_messages: 0 (expected: none with 10 msg over 10 sec)

result:
  messages_sent: 80
  messages_received: 80
  delivery_rate: "100%"
  race_conditions_detected: 0
  database_corruption: false
```

**Success Criteria:**
- ✅ 80 messages sent successfully
- ✅ 100% delivery rate
- ✅ Zero race conditions
- ✅ Zero database corruption

---

### Test 6: Security Validation (TTT: Trustworthy)

**Objective:** Verify HMAC auth, secret redaction, YOLO guard

**Security Tests:**

**6.1 HMAC Authentication**
```
Test: Worker tries to send message with invalid token
Expected: Authentication failure, message rejected

TTT Citation:
  citation_id: if://test/s2-mcp-bridge/security-hmac
  test: "Invalid token authentication"
  result: "Message rejected with HMAC validation error"
  audit_log: "Unauthorized attempt logged"
```

**6.2 Secret Redaction**
```
Test: Worker sends message with API key
Message: "My API key is sk-abcdef123456..."
Expected: Message stored with redaction: "My API key is [REDACTED]"

TTT Citation:
  citation_id: if://test/s2-mcp-bridge/security-redaction
  test: "API key redaction"
  original: "sk-abcdef123456..."
  redacted: "[REDACTED]"
  patterns_detected: ["openai_key"]
```

**6.3 YOLO Guard (4-Stage Approval)**
```
Test: Orchestrator enables YOLO mode for deployment
Steps:
  1. enable_yolo_mode(mode="restricted", timeout=300)
  2. Requires: YOLO_MODE=1 environment variable
  3. Requires: Interactive typed confirmation
  4. Requires: One-time validation code
  5. Requires: Time-limited approval token (5 min TTL)

TTT Citation:
  citation_id: if://test/s2-mcp-bridge/security-yolo-guard
  test: "4-stage YOLO guard approval"
  stages_passed: [1, 2, 3, 4]
  approval_token: "generated"
  expires_at: "timestamp+5min"
  human_in_loop: true
```

**Success Criteria:**
- ✅ Invalid tokens rejected
- ✅ API keys redacted automatically
- ✅ YOLO guard requires 4 stages
- ✅ All security events logged in audit trail

---

### Test 7: Failure Recovery (TTT: Traceable)

**Objective:** Test recovery from common failure modes

**7.1 Worker Crash Recovery**
```
Scenario: Worker 3 crashes mid-task
Steps:
  1. Worker 3 sends "Task in progress - 50%"
  2. Worker 3 process killed (simulate crash)
  3. Orchestrator detects silence (no heartbeat for 2 min)
  4. Orchestrator reassigns task to Worker 4
  5. Worker 3 restarts, rejoins conversation
  6. Worker 3 resumes from last checkpoint

TTT Citation:
  citation_id: if://test/s2-mcp-bridge/recovery-crash
  failure_type: "Worker crash"
  detection_time: "seconds"
  recovery_action: "Task reassignment"
  data_loss: "None (checkpoint at 50%)"
```

**7.2 Network Partition**
```
Scenario: Worker loses network connection
Steps:
  1. Worker 5 disconnected from network
  2. Worker 5 buffers messages locally
  3. Network restored after 60 seconds
  4. Worker 5 flushes message buffer
  5. All buffered messages delivered

TTT Citation:
  citation_id: if://test/s2-mcp-bridge/recovery-network
  failure_type: "Network partition"
  buffer_size: 3 messages
  partition_duration: "60 seconds"
  messages_lost: 0
```

**7.3 Database Lock Timeout**
```
Scenario: SQLite database locked during write
Steps:
  1. Simulate long-running transaction
  2. Worker attempts write during lock
  3. Worker retries with exponential backoff
  4. Write succeeds after lock released

TTT Citation:
  citation_id: if://test/s2-mcp-bridge/recovery-db-lock
  failure_type: "Database lock timeout"
  retry_attempts: 3
  backoff_strategy: "Exponential (1s, 2s, 4s)"
  final_result: "Success after 2nd retry"
```

**Success Criteria:**
- ✅ Crashed workers recover and resume
- ✅ Network partitions handled gracefully
- ✅ Database locks resolved with retries
- ✅ Zero data loss

---

### Test 8: TTT Audit Trail Verification

**Objective:** Verify complete audit trail for all operations

**Audit Log Contents:**
```yaml
citation_id: if://test/s2-mcp-bridge/ttt-audit
type: audit_trail_verification
timestamp: [test_run_timestamp]

audit_log_location: "/tmp/mcp-multiagent-bridge/bridge_audit.jsonl"

required_entries:
  - create_conversation: 8 events (one per worker)
  - send_message: 88 events (8 tasks + 80 concurrent)
  - get_messages: 240 events (30 polls * 8 conversations)
  - update_status: 40 events (5 per worker)
  - enable_yolo_mode: 1 event (if tested)
  - authentication_failure: 1 event (security test)

audit_fields_per_entry:
  - timestamp (ISO 8601)
  - session_id
  - conversation_id
  - action
  - result (success/failure)
  - latency_ms
  - message_id (if applicable)

verification:
  method: "Parse JSONL, verify all events present"
  total_entries: ">350"
  missing_events: 0
  corrupt_entries: 0

result:
  complete_audit_trail: true/false
  if_ttt_compliance: "100%"
  traceability_score: "A+"
```

**Success Criteria:**
- ✅ All operations logged
- ✅ Zero missing events
- ✅ Zero corrupt log entries
- ✅ Full IF.TTT compliance

---

## Test Execution Workflow

### Phase 1: Setup (5 minutes)
1. All 9 agents run installer command
2. Verify installation with test suite
3. Commit credentials to git

### Phase 2: Basic Operations (10 minutes)
1. Create 8 conversations
2. Send 8 task assignments
3. Monitor worker responses

### Phase 3: Stress Test (10 minutes)
1. Concurrent load test (80 messages)
2. Latency measurements
3. Database integrity checks

### Phase 4: Security (10 minutes)
1. HMAC authentication test
2. Secret redaction test
3. YOLO guard test

### Phase 5: Failure Recovery (15 minutes)
1. Crash recovery test
2. Network partition test
3. Database lock test

### Phase 6: Audit & Report (10 minutes)
1. Verify audit trail
2. Generate TTT report
3. Commit results to git

**Total Time: 60 minutes**

---

## TTT Compliance Summary

### Traceable ✅
- All operations logged in `bridge_audit.jsonl`
- Git commits for credentials and results
- Unique `if://` URIs for all test events
- Full message history in SQLite database

### Transparent ✅
- Test protocol publicly documented
- All metrics published (latency, throughput, reliability)
- Source code open (dannystocker/mcp-multiagent-bridge)
- Audit logs human-readable (JSONL format)

### Trustworthy ✅
- Security tests validate HMAC auth + redaction
- Stress test proves zero race conditions
- Failure recovery demonstrates resilience
- Independent verification possible (replay from audit logs)

---

## Final Report Template

```markdown
# S² MCP Bridge Test Report

**Test Date:** [timestamp]
**Test Protocol:** if://test-protocol/s2-mcp-bridge/v1.0
**Agents Tested:** 9 (1 orchestrator + 8 workers)

## Results Summary

| Test | Status | Metric | Target | Actual |
|------|--------|--------|--------|--------|
| Installation | ✅/❌ | Agents installed | 9 | [count] |
| Conversation Creation | ✅/❌ | Conversations | 8 | [count] |
| Task Distribution | ✅/❌ | Latency | <5ms | [ms] |
| Worker Monitoring | ✅/❌ | Messages received | 40 | [count] |
| Concurrent Load | ✅/❌ | Throughput | 80 msg | [count] |
| Security | ✅/❌ | Auth failures | 0 | [count] |
| Failure Recovery | ✅/❌ | Recovery time | <60s | [seconds] |
| TTT Audit | ✅/❌ | Audit entries | >350 | [count] |

## Performance Metrics

- **Average Latency:** [ms]
- **Message Delivery Rate:** [%]
- **Throughput:** [msg/sec]
- **Database Size:** [KB]
- **Zero Race Conditions:** ✅/❌

## TTT Compliance

- **Traceable:** ✅ All operations logged with if:// URIs
- **Transparent:** ✅ Full audit trail in JSONL format
- **Trustworthy:** ✅ Security tests pass, zero data loss

## IF.TTT Citation

```yaml
citation_id: if://test-report/s2-mcp-bridge/[timestamp]
type: test_execution_report
protocol: if://test-protocol/s2-mcp-bridge/v1.0

results:
  tests_passed: [count]/8
  tests_failed: [count]/8
  overall_status: "PASS/FAIL"

artifacts:
  audit_log: "bridge_audit.jsonl"
  database: "s2-prod.db"
  credentials: "s2-credentials-*.json"
  git_commit: "[hash]"

recommendation:
  production_ready: true/false
  next_steps: [list]
```

**Overall Result: PRODUCTION READY / NEEDS WORK**
```

---

**Protocol Version:** 1.0
**Maintained by:** InfraFabric S² Coordination Team
**Last Updated:** 2025-11-13
