# Session 1: NDI Evidence Streaming (IF.witness)

**Workstream:** 1 of 4 (Independent)
**Agent:** Claude Sonnet 4.5
**Budget:** $20, 14 hours
**Dependencies:** None

---

## Copy-Paste This Into New Claude Code Session

```
Hi Claude! I need you to implement Workstream 1 from the InfraFabric real-time communication integration.

REPOSITORY: dannystocker/infrafabric
BRANCH: claude/realtime-workstream-1-ndi (create from claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy)

CONTEXT FILES YOU MUST READ FIRST:
1. docs/IF-REALTIME-COMMUNICATION-INTEGRATION.md (full specification)
2. docs/IF-REALTIME-PARALLEL-ROADMAP.md (your workstream details)
3. papers/IF-witness.md (philosophy grounding)
4. docs/SWARM-COMMUNICATION-SECURITY.md (Ed25519 signatures)

YOUR TASK: Implement NDI evidence streaming for IF.witness

DELIVERABLES:
1. src/communication/ndi_witness_publisher.py (~200 lines)
   - Wrap IF.yologuard scanner output as NDI stream
   - Inject witness hash chain into NDI metadata packets
   - Sign each frame with Ed25519 (use existing IF.witness signing)

2. src/communication/ndi_guardian_viewer.py (~150 lines)
   - Subscribe to NDI streams
   - Verify metadata signatures in real-time
   - Display stream + overlay witness provenance

3. docs/NDI-WITNESS-INTEGRATION.md (case study)
   - How it works
   - Philosophy grounding (Wu Lun 父子, IF.ground observability)
   - Test results

4. tests/test_ndi_witness.py (unit tests)
   - Test witness hash chain continuity
   - Test Ed25519 signature verification
   - Test NDI metadata injection/extraction

TECHNICAL REQUIREMENTS:
- NDI SDK 5.6 (https://ndi.tv/sdk/)
- Python bindings: ndi-python or PyNDI
- Witness hash chain: prev_hash → content_hash → next_hash
- Ed25519 signatures: Use cryptography library (already in project)
- Trace IDs: Propagate from IFMessage v2.1 schema

PHILOSOPHY GROUNDING:
- Wu Lun (五倫) Relationship: 父子 (Parent-Child) — NDI sender creates stream, receivers consume asynchronously
- IF.ground Principle 1: Ground in Observable Artifacts — Every frame is observable, hash is verifiable
- IF.witness: Every frame has provenance (who scanned, what found, when, trace_id)
- IF.TTT: Traceable (hash chain), Transparent (metadata visible), Trustworthy (Ed25519 signed)

SUCCESS CRITERIA:
✅ IF.yologuard scanner output streams as NDI
✅ Every frame has witness hash chain in metadata
✅ Ed25519 signature verifies in real-time
✅ IF.guard can view stream with provenance overlay
✅ Tests pass: hash chain continuity, signature verification

INTERFACE CONTRACT (for Session 4 handoff):
Create docs/INTERFACES/workstream-1-ndi-contract.yaml with:
- NDI stream naming convention: "IF.witness.{component}.{id}"
- Metadata JSON schema: {frame_number, timestamp, content_hash, prev_hash, trace_id, signature}
- Ed25519 public key format: Base64 encoded
- Test fixtures for next session

BUDGET & TIME:
- Estimated: 12-16 hours
- Cost: ~$15-20 (Sonnet 4.5)
- No blockers (no dependencies on other sessions)

START HERE:
1. Read the 4 context files listed above
2. Install NDI SDK and Python bindings
3. Examine existing IF.witness code (search for Ed25519 signature patterns)
4. Implement ndi_witness_publisher.py (start here, it's the core)
5. Implement ndi_guardian_viewer.py (consumer side)
6. Write tests
7. Document in NDI-WITNESS-INTEGRATION.md
8. Create interface contract YAML
9. Commit to branch: claude/realtime-workstream-1-ndi
10. Push and notify me when complete

QUESTIONS? Ask me about:
- IF.witness hash chain format (check papers/IF-witness.md)
- Ed25519 signature patterns (check docs/SWARM-COMMUNICATION-SECURITY.md)
- IFMessage v2.1 trace_id propagation (check schemas/ifmessage/v1.0.schema.json)

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

# Poll for other workstream branches (for awareness only - no dependencies)
git fetch --all
git branch -r | grep "claude/realtime-workstream-"

# Expected branches (eventually):
# - claude/realtime-workstream-1-ndi (YOU)
# - claude/realtime-workstream-2-webrtc
# - claude/realtime-workstream-3-h323
# - claude/realtime-workstream-4-sip
```

### 2. STATUS Reporting Requirements
Create STATUS file on your branch:
```bash
# Create STATUS.md on your branch
cat > STATUS.md <<EOF
# Workstream 1: NDI Evidence Streaming
**Agent:** Claude Sonnet 4.5
**Branch:** claude/realtime-workstream-1-ndi
**Status:** PHASE_0_COORDINATION

## Phase 0 Checklist
- [ ] Branch created from base
- [ ] Context files read
- [ ] Dependencies checked (NONE for Session 1)
- [ ] Ready to begin implementation

## Current Phase: 0 (Coordination)
**Started:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Blockers:** None
**Next:** Phase 1 (Implementation)

## Milestones
- [ ] Phase 0: Coordination complete
- [ ] Phase 1: ndi_witness_publisher.py implemented
- [ ] Phase 2: ndi_guardian_viewer.py implemented
- [ ] Phase 3: Tests passing
- [ ] Phase 4: Documentation complete
- [ ] HANDOFF: Interface contract created
EOF

git add STATUS.md
git commit -m "Phase 0: Initialize workstream status tracking"
```

### 3. Filler Task Strategy
**Workstream 1 has NO dependencies** - proceed directly to implementation after Phase 0!

However, if you encounter blockers during implementation:
- Research NDI SDK documentation
- Create test fixtures for Session 4 integration
- Write additional unit tests
- Document edge cases in NDI-WITNESS-INTEGRATION.md

### 4. Milestone Reporting
Update STATUS.md after each milestone:
```bash
# After completing each phase, update STATUS.md
sed -i 's/Status:** PHASE_0/Status:** PHASE_1_IMPLEMENTATION/' STATUS.md
sed -i 's/- \[ \] Phase 0/- [x] Phase 0/' STATUS.md

git add STATUS.md
git commit -m "Milestone: Phase 0 complete, beginning Phase 1"
```

### 5. Phase 0 Completion Checklist
Before moving to implementation:
- ✅ Branch created: `claude/realtime-workstream-1-ndi`
- ✅ STATUS.md created and committed
- ✅ All 4 context files read
- ✅ Dependencies verified (NONE - fully independent)
- ✅ Development plan confirmed
- ✅ Ready to implement

**Phase 0 Complete? Proceed to "Additional Resources" below and begin implementation!**

---

## Additional Resources for This Session

### NDI SDK Installation
```bash
# Download NDI SDK 5.6
wget https://downloads.ndi.tv/SDK/NDI_SDK_Linux/Install_NDI_SDK_v5_Linux.tar.gz
tar -xzf Install_NDI_SDK_v5_Linux.tar.gz
cd NDI\ SDK\ for\ Linux/
./Install_NDI_SDK_v5_Linux.sh

# Install Python bindings
pip install ndi-python
# OR
pip install PyNDI
```

### Existing IF.witness Code to Reference
```bash
# Find existing Ed25519 signature code
grep -r "ed25519" --include="*.py" .

# Find existing witness hash chain code
grep -r "prev_hash\|witness.*hash" --include="*.py" .

# Find existing trace_id usage
grep -r "trace_id" --include="*.py" .
```

### Quick Test Command (once implemented)
```bash
# Terminal 1: Start IF.yologuard with NDI publisher
python src/communication/ndi_witness_publisher.py --source yologuard

# Terminal 2: View stream with signature verification
python src/communication/ndi_guardian_viewer.py --stream "IF.witness.yologuard.01"
```

---

## What the Next Session (Session 4: SIP) Will Need From You

Session 4 (SIP External Expert Calls) will need:
- **Nothing!** Session 1 is fully independent
- But optionally: If SIP calls want to share NDI evidence streams, they'll use your interface contract

Your contract will document:
- How to discover NDI streams (mDNS or Discovery Server)
- How to verify witness signatures in metadata
- How to parse the metadata JSON schema

---

## Handoff Checklist (When You're Done)

Before marking this session complete:

- ✅ All tests passing (`pytest tests/test_ndi_witness.py`)
- ✅ NDI stream can be discovered via mDNS
- ✅ Metadata contains valid witness hash chain
- ✅ Ed25519 signatures verify correctly
- ✅ Interface contract documented (`docs/INTERFACES/workstream-1-ndi-contract.yaml`)
- ✅ IF.witness log complete (`logs/workstream-1-ndi-witness.jsonl`)
- ✅ Code committed to `claude/realtime-workstream-1-ndi`
- ✅ Documentation in `docs/NDI-WITNESS-INTEGRATION.md`

---

## Expected Output Structure

```
infrafabric/
├── src/communication/
│   ├── ndi_witness_publisher.py      # NEW: NDI sender with witness metadata
│   └── ndi_guardian_viewer.py        # NEW: NDI receiver with signature verification
├── tests/
│   └── test_ndi_witness.py           # NEW: Unit tests
├── docs/
│   ├── NDI-WITNESS-INTEGRATION.md    # NEW: Case study
│   └── INTERFACES/
│       └── workstream-1-ndi-contract.yaml  # NEW: Interface contract
└── logs/
    └── workstream-1-ndi-witness.jsonl      # NEW: Development log
```

---

## Philosophy Check (Self-Test Before Completing)

Ask yourself:

1. **Wu Lun 父子 (Parent-Child):** Does the NDI sender create the stream independently of receivers? ✓
2. **IF.ground Observable:** Can every frame's content be verified by hash? ✓
3. **IF.witness Provenance:** Does metadata include who/what/when/trace_id? ✓
4. **IF.TTT Traceable:** Can you follow the hash chain back to genesis frame? ✓
5. **IF.TTT Transparent:** Is metadata human-readable JSON in NDI stream? ✓
6. **IF.TTT Trustworthy:** Does Ed25519 signature prove authenticity? ✓

If all 6 are ✓, you're done!

---

**Session Start:** [Paste the "Copy-Paste This" block above into new Claude Code session]
**Session Complete:** [Push to `claude/realtime-workstream-1-ndi` and post handoff checklist]
