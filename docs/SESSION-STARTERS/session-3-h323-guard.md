# Session 3: H.323 Guardian Council (IF.guard)

**Workstream:** 3 of 4 (Independent)
**Agent:** Gemini 2.5 Pro (Late Bloomer - deep policy design)
**Budget:** $30, 24 hours
**Dependencies:** None (but Session 4 will depend on this)

---

## Copy-Paste This Into New Claude Code Session

```
Hi Claude! I need you to implement Workstream 3 from the InfraFabric real-time communication integration.

REPOSITORY: dannystocker/infrafabric
BRANCH: claude/realtime-workstream-3-h323 (create from claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy)

CONTEXT FILES YOU MUST READ FIRST:
1. docs/IF-REALTIME-COMMUNICATION-INTEGRATION.md (H.323 section)
2. docs/IF-REALTIME-PARALLEL-ROADMAP.md (your workstream)
3. papers/IF-vision.md (Guardian Council architecture)
4. docs/SWARM-COMMUNICATION-SECURITY.md (Ed25519 admission control)

YOUR TASK: Implement H.323 Guardian Council conferencing for IF.guard

DELIVERABLES:
1. src/communication/h323_gatekeeper.py (~500 lines)
   - H.323 Gatekeeper wrapper (GNU Gatekeeper or OpenH323)
   - Ed25519 admission control (ARQ → ACF/ARJ)
   - Bandwidth quotas per guardian
   - IF.witness logging for all RAS messages

2. src/communication/h323_mcu_config.py (~200 lines)
   - MCU configuration (Jitsi Videobridge or Kurento)
   - Centralized audio mixing
   - Continuous presence video (4x4 grid)
   - T.120 whiteboard for evidence display

3. docs/H323-GUARD-COUNCIL.md (architecture doc)
   - System architecture (Gatekeeper + MCU + Terminals)
   - Call flow (ARQ → ACF → H.245 → Media)
   - Philosophy grounding (Ubuntu consensus, Kantian gates)

4. docs/H323-KANTIAN-POLICY.md (policy specification)
   - Admission rules (who can join)
   - Constraints (PII, bandwidth, quotas)
   - ESCALATE triggers

5. tests/test_h323_admission.py (policy tests)
   - Test Ed25519 admission control
   - Test PII rejection
   - Test bandwidth quota enforcement

TECHNICAL REQUIREMENTS:
- H.323 Gatekeeper: GNU Gatekeeper (https://www.gnugk.org/) OR OpenH323
- H.323 MCU: Jitsi Videobridge (https://jitsi.org/jitsi-videobridge/) OR Kurento
- Python bindings: Use subprocess to call gnugk CLI, parse output
- Ed25519: Use cryptography library (already in project)
- IF.witness: Log every ARQ (Admission Request), ACF (Confirm), ARJ (Reject)

PHILOSOPHY GROUNDING:
- Wu Lun (五倫): 君臣 (Ruler-Subject) — Gatekeeper grants admission, terminals obey
- Ubuntu: Communal consensus via MCU centralized audio mixing (everyone hears everyone)
- Kantian Duty: Admission gates enforce categorical imperatives:
  - NO PII in ESCALATE calls
  - NO unregistered terminals
  - NO bandwidth abuse
- IF.TTT: Traceable (call logs), Transparent (policy explicit), Trustworthy (Ed25519 signatures)

SUCCESS CRITERIA:
✅ Gatekeeper running, terminals can register
✅ 15+ guardians can join MCU concurrently
✅ Ed25519 admission control rejects invalid signatures
✅ PII policy rejects calls with has_pii=true
✅ Bandwidth quota enforced (max 10 Mbps per terminal)
✅ IF.witness logs all RAS messages (ARQ/ACF/ARJ)
✅ MCU mixes audio from all guardians
✅ Tests pass: admission, PII, bandwidth, Ed25519

KANTIAN POLICY GATES (must implement):
```python
def h323_admission_request(arq: AdmissionRequest) -> AdmissionResponse:
    # 1. Verify Ed25519 signature
    if not verify_signature(arq.signature, arq.terminal_id):
        return AdmissionReject(reason="INVALID_SIGNATURE")

    # 2. Check registry (prevent sybil)
    if not guardian_registry.is_registered(arq.terminal_id):
        return AdmissionReject(reason="NOT_REGISTERED")

    # 3. Kantian constraint: NO PII
    if arq.call_type == "ESCALATE" and arq.has_pii:
        return AdmissionReject(reason="PII_POLICY_VIOLATION")

    # 4. Bandwidth quota
    if arq.bandwidth_bps > 10_000_000:
        return AdmissionReject(reason="BANDWIDTH_EXCEEDED")

    # 5. Log to IF.witness
    witness.log({...})

    return AdmissionConfirm(call_id=..., mcu_address=...)
```

INTERFACE CONTRACT (for Session 4 handoff):
Create docs/INTERFACES/workstream-3-h323-contract.yaml:
```yaml
h323_gatekeeper_interface:
  admission_control:
    endpoint: "if://service/guard/gatekeeper:1719"
    methods:
      - name: request_admission
        params: {terminal_id, bandwidth_bps, call_type, has_pii}
        returns: {call_id, mcu_address} OR {reject_reason}

  mcu:
    endpoint: "if://service/guard/mcu:1720"
    capabilities:
      max_participants: 25
      audio_mixing: centralized
      video_layout: continuous_presence_4x4
```

BUDGET & TIME:
- Estimated: 20-28 hours
- Cost: ~$25-35 (Gemini deep policy design)
- No blockers (can mock IFMessage v2.1 for testing)

START HERE:
1. Read context files (especially IF-vision.md for Guardian archetypes)
2. Install GNU Gatekeeper: `apt-get install gnugk`
3. Install Jitsi Videobridge OR Kurento MCU
4. Implement h323_gatekeeper.py (Python wrapper)
5. Configure MCU (h323_mcu_config.py)
6. Write Kantian policy gates (most important!)
7. Document architecture + policy
8. Write admission tests
9. Create interface contract
10. Commit to claude/realtime-workstream-3-h323

CRITICAL: Session 4 depends on your interface contract!
Session 4 (SIP) will need:
- How to trigger H.323 call from IFMessage ESCALATE
- How to bridge SIP → H.323 gateway
- Your gatekeeper endpoint + API

BEGIN!
```

---

## Phase 0: Coordination Protocol (Complete This First!)

**BEFORE implementing, complete Phase 0 coordination:**

### 1. Branch Polling
```bash
# Check current branch status
git status
git branch -a

# Poll for other workstream branches (Session 4 depends on YOU!)
git fetch --all
git branch -r | grep "claude/realtime-workstream-"

# Expected branches (eventually):
# - claude/realtime-workstream-1-ndi
# - claude/realtime-workstream-2-webrtc
# - claude/realtime-workstream-3-h323 (YOU)
# - claude/realtime-workstream-4-sip (WAITING ON YOU!)
```

### 2. STATUS Reporting Requirements
Create STATUS file on your branch:
```bash
# Create STATUS.md on your branch
cat > STATUS.md <<EOF
# Workstream 3: H.323 Guardian Council
**Agent:** Gemini 2.5 Pro (or Claude Sonnet 4.5)
**Branch:** claude/realtime-workstream-3-h323
**Status:** PHASE_0_COORDINATION

## Phase 0 Checklist
- [ ] Branch created from base
- [ ] Context files read
- [ ] Dependencies checked (NONE for Session 3)
- [ ] Session 4 notified (they depend on us!)
- [ ] Ready to begin implementation

## Current Phase: 0 (Coordination)
**Started:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Blockers:** None
**Next:** Phase 1 (Implementation)
**Downstream Dependency:** Session 4 (SIP) is waiting for our interface contract

## Milestones
- [ ] Phase 0: Coordination complete
- [ ] Phase 1: h323_gatekeeper.py implemented
- [ ] Phase 2: h323_mcu_config.py implemented
- [ ] Phase 3: Kantian policy gates implemented
- [ ] Phase 4: Tests passing (admission, PII, bandwidth)
- [ ] Phase 5: Documentation complete
- [ ] HANDOFF: Interface contract created (CRITICAL for Session 4!)
EOF

git add STATUS.md
git commit -m "Phase 0: Initialize workstream status tracking"
```

### 3. Filler Task Strategy
**Workstream 3 has NO dependencies** - proceed directly to implementation after Phase 0!

However, if you encounter blockers during implementation:
- Research H.323 protocol specifications (ITU-T H.323)
- Design additional Kantian policy gates
- Create guardian registry test fixtures
- Document MCU architecture options (Jitsi vs Kurento)
- **CRITICAL:** Draft interface contract early for Session 4

### 4. Milestone Reporting
Update STATUS.md after each milestone:
```bash
# After completing each phase, update STATUS.md
sed -i 's/Status:** PHASE_0/Status:** PHASE_1_IMPLEMENTATION/' STATUS.md
sed -i 's/- \[ \] Phase 0/- [x] Phase 0/' STATUS.md

git add STATUS.md
git commit -m "Milestone: Phase 0 complete, beginning Phase 1"
```

**IMPORTANT:** Notify Session 4 when interface contract is ready:
```bash
# After creating docs/INTERFACES/workstream-3-h323-contract.yaml
echo "SESSION 4 UNBLOCKED: H.323 interface contract available" >> STATUS.md
git add STATUS.md docs/INTERFACES/workstream-3-h323-contract.yaml
git commit -m "HANDOFF: Interface contract ready for Session 4"
```

### 5. Phase 0 Completion Checklist
Before moving to implementation:
- ✅ Branch created: `claude/realtime-workstream-3-h323`
- ✅ STATUS.md created and committed
- ✅ All 4 context files read
- ✅ Dependencies verified (NONE - fully independent)
- ✅ Downstream dependency acknowledged (Session 4 waiting)
- ✅ Development plan confirmed
- ✅ Ready to implement

**Phase 0 Complete? Proceed to "H.323 Infrastructure Setup" below and begin implementation!**

---

## H.323 Infrastructure Setup

```bash
# Install GNU Gatekeeper
sudo apt-get update
sudo apt-get install gnugk

# Configure gatekeeper
sudo nano /etc/gnugk/gnugk.ini
# Add:
# [Gatekeeper::Main]
# Fourtytwo=42
# [RasSrv::ARQFeatures]
# CallUnregisteredEndpoints=0

# Start gatekeeper
sudo systemctl start gnugk
sudo systemctl enable gnugk

# Check status
sudo gnugk -s status
```

---

## Guardian Registry (Ed25519 Public Keys)

```yaml
# config/guardian-registry.yaml
guardians:
  - terminal_id: "if://guardian/sage"
    public_key: "ed25519:AAAC3NzaC1lZDI1NTE5AAAAIOMq..."
    role: "Technical Guardian"
    bandwidth_quota_bps: 10_000_000

  - terminal_id: "if://guardian/skeptic"
    public_key: "ed25519:BBBD4OzaC2lZDI1NTE5AAAAIPNr..."
    role: "Contrarian Guardian"
    bandwidth_quota_bps: 10_000_000
```

---

## Test Scenario (15-Guardian Council Call)

```
ESCALATE trigger → IFMessage{hazard: ["legal"]}
  ↓
IF.guard receives message
  ↓
h323_gatekeeper.request_admission() called 15 times
  ↓
Each guardian verified:
  - Ed25519 signature ✓
  - In registry ✓
  - No PII ✓
  - Bandwidth < 10 Mbps ✓
  ↓
All 15 guardians admitted → ACF sent
  ↓
Terminals connect to MCU
  ↓
MCU mixes audio, displays 4x4 video grid
  ↓
Decision recorded → IF.witness
```

---

**Session Start:** [Copy-paste block above]
**Session Complete:** Push to `claude/realtime-workstream-3-h323` + create interface contract
