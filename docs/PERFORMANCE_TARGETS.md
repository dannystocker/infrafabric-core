# Performance Targets (v1)

This doc sets honest expectations for initial deployments. Update as we collect more data.

## Scan Speed (local)

| Repo Size | Files      | Target Time | Notes                 |
|-----------|------------|-------------|-----------------------|
| Small     | <100       | <1s         | Instant feedback      |
| Medium    | 100–1,000  | <5s         | CI-friendly           |
| Large     | 1k–10k     | <30s        | Background job        |
| Huge      | >10k       | <5 min      | Batch processing      |

## Connectivity Latency (REST-first)

| Level | Type                      | p95 Target |
|------:|---------------------------|-----------:|
| L1    | function → function       |      <1 ms |
| L2    | module → module           |      <5 ms |
| L3    | service (REST API)        |     <50 ms |
| L4–5  | advanced (defer to v2+)   |        TBD |

Async fallback semantics:
- If validator queue depth exceeds threshold, mark message `validation-deferred`, enqueue for async validation, and proceed with a circuit breaker policy.
- Document retry/backoff; promote failures to WARN, not ERROR.

References:
- IF_CONNECTIVITY_ARCHITECTURE.md (levels)
- schemas/ifmessage/v1.0.schema.json (message contract)
