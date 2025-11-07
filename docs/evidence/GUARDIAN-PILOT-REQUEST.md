# IF Guardians: Pilot Request for Relaxed Creative Reframing

**Date:** 2025-10-31
**Requestor:** InfraFabric Research Team
**Pilot Type:** Bounded Experiment - Creative Reframing Strategies
**Status:** Awaiting Guardian Approval

---

## Executive Summary

We request Guardian approval for a **10-business-day pilot** to test whether *slightly relaxed persona labeling and expanded creative reframing strategies* improve contact recovery rates for stuck high-value prospects, while maintaining all legal/ethical safeguards.

**Key Point:** This is NOT a request to remove safeguards. This is a request to *test alternative framings* within the same safety architecture.

---

## What We Want to Test

### Current State (APPROVED)
- Persona names: "Context Researcher", "Social Network Analyst"
- Strategies: 3 whitelisted (temporal, alternative-name, professional-network)
- Mode: Standard (production-safe)

### Proposed Pilot State
- Persona names: Add 2 analytical perspective models:
  - "Stakeholder Perspective Analyst" (models how a stakeholder views coordination)
  - "Discourse Pattern Researcher" (analyzes public discourse topology)
- Strategies: Add 2 whitelisted exploratory strategies:
  - Bridging Pattern Analysis (finds connectors between isolated clusters)
  - Contextual Narrative Analysis (understands stakeholder framing)
- Mode: Exploratory (enhanced safeguards + preview-only)

**What's NOT changing:**
- All ComplianceChecker gates remain
- All rate limiting remains
- All ethical rationale logging remains
- Public-only data restriction remains
- Human approval for all outputs (preview mode)

---

## Strategic Rationale (Aligned with IF Principles)

### 1. Late Bloomer Philosophy
**IF Principle:** "Truth rarely performs well in its early iterations"

Current constraint blocks valid exploration paths:
- "Context Researcher" is accurate but doesn't capture *why* we model perspectives
- "Stakeholder Perspective Analyst" better communicates empathy-as-infrastructure

### 2. Substrate Plurality
**IF Principle:** Support diverse computational approaches

Different contacts need different reframing strategies:
- Technical CTOs respond to bridging patterns (network topology)
- Policy leads respond to discourse analysis (regulatory framing)
- One-size-fits-all = forced uniformity (anti-IF)

### 3. Measured Risk-Taking
**IF Principle:** "Build infrastructure that survives contact with reality"

We need evidence to know if constraints are:
- A) Necessary safety boundaries
- B) Overly conservative barriers to effectiveness

Only way to learn: bounded, measured, auditable experiment.

---

## Scope & Boundaries

### Sample Size
- **50 stuck contacts** (confidence <50% after standard strategies)
- **NOT** the full 84-contact list
- Contacts from: VC, quantum, defense, enterprise sectors

### Timeline
- **10 business days** (Nov 1-14, 2025)
- Auto-stop if any ethical/legal flag

### Geographic/Sector Limits
- US/EU/UK contacts only (known regulatory frameworks)
- No personal/consumer targets (B2B only)
- Publicly-visible executives only (no private individuals)

---

## Safety Guardrails (Exceed Standard Mode)

### 1. Mandatory Preview Mode
**Enforcement:** No output leaves system without human approval
**Implementation:** All emails/searches flagged `PREVIEW_ONLY=True`
**Audit:** Every preview logged with timestamp + reviewer ID

### 2. Enhanced Compliance Checking
**Enforcement:** All queries pass through ComplianceChecker + EthicalRationale validator
**Implementation:**
```python
if pilot_mode:
    require_ethical_rationale_score >= 8/10  # vs 6/10 in standard
    require_guardian_pre_approval_for_new_strategy = True
```

### 3. Strict Rate Limiting
**Enforcement:** 3 reframings max per contact (vs 5 in standard)
**Rationale:** Forces selection of highest-value strategies only

### 4. Immediate Kill-Switch
**Trigger Conditions:**
- Any legal flag (CFAA, GDPR, ToS violation)
- Any ethical flag (surveillance behavior, deception)
- Human reviewer objects to ≥3 consecutive outputs

**Action:** Pilot auto-stops; all results quarantined; Guardian review required to resume

### 5. Synthetic Data Only (for testing)
**Enforcement:** First 10 contacts use synthetic test data
**Rationale:** Validate safety architecture before touching real prospects

---

## Metrics (How We Measure Success/Failure)

### Success Metrics
1. **Recovery Rate:** % of stuck contacts moving from <50% → ≥70% confidence
   - Target: ≥20% recovery (10+ contacts)
   - Baseline: 0% (stuck = no current path forward)

2. **Confidence Delta:** Average confidence increase per recovered contact
   - Target: +25 points average
   - Measurement: (final_confidence - initial_confidence) / recovered_contacts

3. **Quality Score:** Human reviewer rating of email drafts
   - Target: ≥7/10 average (professional, non-creepy, value-aligned)
   - Measurement: Blind review of 20 random drafts

### Safety Metrics (Zero-Tolerance)
1. **Legal Incidents:** Count of CFAA/GDPR/ToS violations
   - **Threshold: 0** (any incident = immediate stop)

2. **Ethical Incidents:** Count of surveillance/deception/impersonation attempts
   - **Threshold: 0** (any incident = immediate stop)

3. **Compliance Pass Rate:** % of queries passing ComplianceChecker
   - **Threshold: 100%** (any failure = query blocked + logged)

### Quality Assurance Metrics
1. **Rationale Quality:** Human audit of ethical_rationale field
   - Target: ≥8/10 average (clear, specific, defensible)
   - Sample: 100% of reframings audited

2. **False Positive Rate:** % of emails flagged as "creepy/inappropriate" by blind reviewers
   - **Threshold: <5%** (>5% = strategy removed from whitelist)

---

## Deliverables & Audit Trail

### Phase 1: Planning (Day 1)
- [ ] Guardian approval of pilot parameters
- [ ] Synthetic test dataset (10 contacts)
- [ ] Updated ethical_whitelist.yaml with new strategies
- [ ] Pilot monitoring dashboard (live metrics)

### Phase 2: Synthetic Validation (Days 2-3)
- [ ] 10 synthetic contacts processed
- [ ] Safety architecture validation (all checks pass)
- [ ] Guardian review of synthetic outputs
- [ ] GO/NO-GO decision for real contacts

### Phase 3: Real Contact Processing (Days 4-10)
- [ ] 50 real stuck contacts processed
- [ ] 3 reframings max per contact
- [ ] Preview-only email drafts generated
- [ ] Daily safety metric dashboard updates

### Phase 4: Analysis & Recommendation (Days 11-12)
- [ ] `pilot_results.json` (structured data for every contact)
- [ ] `pilot_report.md` (executive summary, KPIs, incidents)
- [ ] `guardian_recommendation.md` (proposed policy changes based on evidence)
- [ ] `audit_logs/` (complete evidence chain for every query)

---

## Rollback & Escalation

### Automatic Rollback Triggers
1. Any legal/ethical incident (immediate stop)
2. Compliance pass rate <100% for 3 consecutive contacts
3. False positive rate >5% in blind review
4. Guardian objects to pilot continuation

### Manual Escalation Path
1. **Daily:** Pilot lead reviews safety metrics
2. **Day 5:** Mid-pilot checkpoint with Guardians
3. **Day 10:** Final results review before policy recommendation
4. **Any time:** Guardian can pause/stop pilot

### Post-Pilot Actions
- **If successful + safe:** Recommend specific strategies for Standard Mode whitelist
- **If successful + incidents:** Quarantine results; refine safeguards; re-pilot
- **If unsuccessful:** Document failure; revert to Standard Mode; no policy changes

---

## Guardian Sign-Off Requirements

### Technical Guardian
**Question:** Is the pilot architecture sound? Are safeguards sufficient?
**Approval Required:** Yes [ ] No [ ]
**Conditions/Notes:**

---

### Ethical Guardian
**Question:** Does the pilot maintain IF's ethical principles? Is intent transparent?
**Approval Required:** Yes [ ] No [ ]
**Conditions/Notes:**

---

### Legal Guardian
**Question:** Are legal risks mitigated? Is audit trail sufficient for regulatory defense?
**Approval Required:** Yes [ ] No [ ]
**Conditions/Notes:**

---

### Business Guardian
**Question:** Is the pilot worth the risk/effort? Does it advance IF's mission?
**Approval Required:** Yes [ ] No [ ]
**Conditions/Notes:**

---

### Coordination Guardian
**Question:** Will this pilot improve cross-cluster coordination? Does it respect stakeholder autonomy?
**Approval Required:** Yes [ ] No [ ]
**Conditions/Notes:**

---

### Meta Guardian
**Question:** Does this pilot embody IF's recursive learning philosophy? Is it philosophically coherent?
**Approval Required:** Yes [ ] No [ ]
**Conditions/Notes:**

---

## Weighted Consensus Score

**Calculation:** (Technical×1.5 + Ethical×2.0 + Legal×1.8 + Business×1.2 + Coordination×1.5 + Meta×1.0) / 9.0

**Threshold for Approval:** ≥7.5/10

**Current Score:** ___ / 10 (pending Guardian votes)

**Status:**
- [ ] **APPROVED** - Proceed with pilot as specified
- [ ] **APPROVED WITH CONDITIONS** - Proceed with modifications (specify below)
- [ ] **BLOCKED** - Do not proceed (specify blocking issues below)

---

## Appendix A: Proposed New Strategies

### Strategy 1: Stakeholder Perspective Analyst
**Intent:** Model how a stakeholder views AI coordination challenges
**Method:** Analyze public statements, papers, speeches for framing/priorities
**Ethical Rationale:** Understanding stakeholder perspective improves relevance; not surveillance if public-only + analytical
**Example Use:** Defense CTO speaks at RSA about "AI supply chain integrity" → tailor IF pitch to supply chain angle

### Strategy 2: Bridging Pattern Analysis
**Intent:** Identify connectors between isolated professional clusters
**Method:** Map public professional networks to find mutual contacts/shared interests
**Ethical Rationale:** Warm introductions via mutual contacts are professional norm; no deception involved
**Example Use:** Quantum researcher + Enterprise CTO both advise same VC → mention VC as common ground

---

## Appendix B: Risk Comparison Table

| Risk Category | Standard Mode | Pilot Mode | Change |
|---------------|---------------|------------|--------|
| Legal (CFAA/GDPR) | Low | Low | No change (public-only enforced) |
| Ethical (surveillance) | Low | Low | No change (analytical, not invasive) |
| Reputational | Low | Medium | +Risk (new strategies = unknown reception) |
| Technical (system failure) | Low | Low | No change (same architecture) |
| Regulatory | Low | Low | No change (preview-only = no external comms) |

**Net Risk Assessment:** Slightly higher reputational risk (unknown reception of new framings) offset by preview mode (human catches issues before sending).

---

## Conclusion

This pilot is designed to answer a specific question: **"Are our current persona labels and strategy constraints necessary for safety, or are they limiting valid exploration?"**

The only way to know is to test, measure, and audit in a bounded, reversible way.

We've designed the pilot to:
1. **Exceed Standard Mode safeguards** (preview-only, enhanced rationale requirements)
2. **Maintain all legal/ethical gates** (ComplianceChecker, public-only, no impersonation)
3. **Generate clear evidence** (structured metrics, blind reviews, audit logs)
4. **Enable rapid rollback** (kill-switches, escalation paths)

**Request:** Guardian approval to proceed with 10-day pilot on 50 stuck contacts, with daily safety monitoring and mid-pilot checkpoint.

---

**Pilot Lead:** [Name]
**Guardian Panel Review Date:** 2025-11-01
**Pilot Start Date (if approved):** 2025-11-04
**Expected Completion:** 2025-11-15

---

*Generated: 2025-10-31*
*Revision: 1.0*
*Status: Awaiting Guardian Review*
