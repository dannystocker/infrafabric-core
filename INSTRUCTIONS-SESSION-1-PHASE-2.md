# Session 1 (NDI) - Phase 2 Instructions

**Status:** Phase 1 Complete ✅
**Next Phase:** Integration Testing + Production Deployment

## Task 1: SIP-NDI Integration
Session 4 (SIP) needs optional NDI evidence streaming during external expert calls.

**Deliverables:**
- Add optional NDI streaming to SIP integration point
- Create example: External expert requests evidence → NDI stream shared
- Update docs/NDI-WITNESS-INTEGRATION.md with SIP use case

**Use IF.swarm:**
- Spawn 1 Haiku agent: Update documentation
- Spawn 1 Sonnet agent: Implement SIP-NDI bridge in src/communication/ndi_sip_bridge.py

## Task 2: Production Deployment Guide
Create docs/NDI-PRODUCTION-DEPLOYMENT.md:
- Real NDI SDK installation (not mock)
- Performance tuning (bandwidth, latency optimization)
- Grafana monitoring dashboards
- Troubleshooting guide

**Use Haiku** (documentation task)

## Task 3: Cost Report
Update COST-REPORT-SESSION-1.yaml:
```yaml
session: session-1-ndi
phase1_cost: $X
phase2_cost: $Y
total_cost: $Z
budget_remaining: $(40 - Z)  # $40 allocated to Session 1
```

Use `if optimise report` CLI command to get accurate numbers.

## Completion Protocol
After finishing all 3 tasks:
1. Commit your work to claude/realtime-workstream-1-ndi
2. Push to origin
3. Create STATUS-PHASE-2.md:
   ```yaml
   session: session-1-ndi
   status: phase_2_complete
   completed: [sip_integration, production_docs, cost_report]
   ready_for: phase_3_production_deployment
   ```
4. **AUTOMATICALLY CHECK FOR NEXT INSTRUCTIONS:**
   ```bash
   git pull origin claude/realtime-workstream-1-ndi
   if [ -f INSTRUCTIONS-SESSION-1-PHASE-3.md ]; then
     cat INSTRUCTIONS-SESSION-1-PHASE-3.md
     # Execute Phase 3 immediately
   else
     # Enter 60-second polling loop
     while true; do
       sleep 60
       git pull origin $(git branch --show-current) --quiet
       if [ -f INSTRUCTIONS-SESSION-1-PHASE-3.md ]; then
         cat INSTRUCTIONS-SESSION-1-PHASE-3.md
         break
       fi
     done
   fi
   ```

**Estimated Time:** 3-4 hours with swarms
**Estimated Cost:** $5-8

Begin Phase 2 implementation now!
