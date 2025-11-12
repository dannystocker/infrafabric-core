## Summary
<!-- Provide a 2–3 sentence overview of what changed and why. -->
<!-- Link the related task (e.g., P0.X.X) and brief context. -->

**Task:** P0.X.X
**Type:** feature | bugfix | refactor | docs
**Component:** [IF.coordinator | IF.bus | IF.worker | shared]

<!-- Example:
Implemented exponential backoff retry logic for SIP registration failures in IF.bus.
Addresses P0.2.1 to reduce session drop rates during network transients.
Includes comprehensive test coverage and observability instrumentation.
-->

---

## Tests
<!-- Describe testing at each level. Provide links to test runs or CI artifacts. -->

- [ ] **Unit:** New/updated unit tests passing
  *Evidence: [test run link](https://ci.example.com/run/123)*

- [ ] **Integration:** Integration tests against staging environment
  *Evidence: [test run link](https://ci.example.com/run/124)*

- [ ] **E2E:** End-to-end tests on representative workload
  *Evidence: [test run link](https://ci.example.com/run/125)*

- [ ] **No regressions:** Full test suite passes; no new failures
  *Summary: X tests passed, 0 failed, 0 skipped*

<!-- Provide coverage metrics if relevant (e.g., code coverage ≥ 80%). -->

---

## Security & Privacy
<!-- Address threats, data handling, and compliance. -->

**Threat Model & Review:**
[Link to threat analysis document / PR comment with threat notes](https://link)

**Data Classification:**
- [ ] None touched
- [ ] Internal (PII, logs)
- [ ] Restricted (API keys, credentials)
- [ ] Confidential (customer data)

**Key Mitigations:**
<!-- Brief statement (1–2 sentences) on how sensitive data is protected, e.g.: -->
<!-- "Credentials never logged; all secrets stored in sealed vault; network calls encrypted TLS 1.3." -->

**Dependencies Reviewed:**
- [ ] Yes (new dependencies audited)
- [ ] No (no new dependencies)

---

## Cost & Model Use
<!-- Estimate resource impact and cost implications. -->

**Est. Tokens/Compute:**
- Inference tokens: ~X per request
- Training tokens: ~Y (if applicable)
- Model tier: T1 | T2 | T3

**Cost Note:**
<!-- Brief explanation, e.g.: "Caching strategy reduces token use by ~30% vs. baseline." -->

**Performance Impact:**
<!-- E.g., "Adds ~50ms latency; offset by 20% throughput gain." -->

---

## Provenance
<!-- Security requirement: all commits must be cryptographically signed. -->

- [ ] **All commits Ed25519-signed** (or GPG for humans)
  *(Verify via `git log --oneline --format="%H %G?"` – should show "G" for each commit)*

- [ ] **Build attestation available**
  [Link to SLSA provenance / attestation](https://example.com/attestation)

- [ ] **Author verified**
  *@github-handle*

---

## Ops & Deployment
<!-- Provide deployment and rollback procedures; update observability. -->

**Rollout Plan:**
1. Canary: Deploy to 5% of traffic for 4 hours
2. Staged: Increase to 25% for 2 hours; monitor error rate
3. Full rollout: Promote to 100% if no critical alerts

<!-- Or for manual deployments: -->
<!-- 1. Stop IF.bus service: `kubectl delete deployment if-bus -n prod`
2. Apply new config: `kubectl apply -f deploy/if-bus-v2.yaml`
3. Verify readiness: `kubectl logs -f deployment/if-bus -n prod`
-->

**Rollback Steps:**
```bash
kubectl rollout undo deployment/if-bus -n prod
kubectl rollout status deployment/if-bus -n prod --timeout=5m
# Verify: curl https://api.infrafabric.local/health
```

**Observability Updated:**
- [ ] Metrics added (e.g., Prometheus counters/histograms)
- [ ] Logs instrumented (structured JSON, appropriate levels)
- [ ] Alerts configured for anomalies (high error rate, latency spike, etc.)

**Monitoring Links:**
- Dashboard: [Grafana link](https://monitoring.example.com/d/abc123)
- Alert rules: [Alertmanager config](https://link)

---

### Reviewer Checklist

- [ ] Code is well-scoped and follows SOLID principles
- [ ] Naming conventions are clear and consistent
- [ ] Error handling covers happy path and edge cases
- [ ] No hardcoded values; configuration externalized
- [ ] Logging is structured and helpful for troubleshooting
- [ ] Security & privacy concerns documented and mitigated
- [ ] Tests validate requirements; coverage is adequate
- [ ] Documentation updated (README, API docs, threat model, etc.)
- [ ] No performance regressions or unintended side effects
- [ ] Commits are atomic; history is clear and reviewable

**Approved by:** [Maintainer or code owner]
**Reviewed on:** YYYY-MM-DD
