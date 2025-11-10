# Gemini AI Studio - InfraFabric Audit Checklist

**Purpose:** Comprehensive pre-endorsement audit by external validator (Gemini)

**Audit Type:** Re-Audit (all blocking issues from first audit now resolved)

**Initial Audit Date:** 2025-11-10 (Result: NOT READY)
**Re-Audit Date:** 2025-11-10 (after fixes)

**Estimated Time:** 2-3 hours for targeted re-audit (Sections 1, 3, 5, 6)

---

## Files to Upload to Gemini AI Studio

### Core Documentation (Required)
1. `infrafabric.md` - Main project overview
2. `README.md` - GitHub entry point
3. `agents.md` - Agent architecture & traceability
4. `docs/GUARDED-CLAIMS.md` - Claims registry

### Five Core Papers (Required)
5. `papers/IF-vision.md` - Vision & architecture (850 lines)
6. `papers/IF-foundations.md` - Epistemological foundations + IF.ground principles (800 lines)
   - **Note:** IF.ground exists as Part 1 of IF-foundations.md (Section 2, lines 85-140+)
7. `papers/IF-armour.md` - Guardian Council + yologuard (1200 lines)
8. `papers/IF-witness.md` - Meta-validation (600 lines)
9. `papers/IF-momentum.md` - Deployment velocity (15,000 words)

### Yologuard Verification Evidence (Critical)
10. `annexes/DOSSIER-YOLOGUARD-METRIC-2025-11-10.md` - Guardian deliberation
11. `docs/evidence/EPISTEMOLOGICAL-SAGA-YOLOGUARD-VERIFICATION.md` - 5-act verification journey
12. `docs/evidence/GEMINI-TO-SYNTHESIS-SAGA.md` - "You were both correct" synthesis

### Gap Analysis (Context for Endorser Emails)
13. `code/research/IF_GAP_ANALYSIS_EXTENDED.20251110-CLAUDE.md` - 15 papers analyzed (NOT the private emails)

---

## Audit Prompt

**Use the updated re-audit prompt:**

Location: `docs/evidence/GEMINI-AUDIT-PROMPT-2025-11-10.md`

**This prompt now includes:**
- Summary of all 4 blocking issues that have been fixed
- Specific file locations and line numbers of changes
- Non-blocking improvements completed
- Git commit references
- Request for targeted re-audit verification

---

## Expected Outputs from Gemini

### Section-by-Section Findings

**Section 1-9 outputs:**
- Issues found per section
- Severity classification (Blocking | Non-blocking | Nice-to-have)
- Specific line references for errors

**Section 10 output:**
- **Overall Assessment:** READY | NOT READY | NEEDS REVISION
- **Must fix before emails:** [Blocking issues list]
- **Should fix before emails:** [Important non-blocking issues]
- **Nice to have:** [Minor improvements]
- **Endorsement worthiness:** [Go/No-go recommendation]

---

## What to Do with Gemini's Findings

### If READY:
1. ✅ Proceed with sending endorser emails
2. Document Gemini's approval in evidence folder
3. Link to Gemini audit in endorsement emails (optional transparency)

### If NEEDS REVISION:
1. ⚠️ Address all "Must fix" issues immediately
2. ⚠️ Address "Should fix" issues if time permits
3. Re-run audit after fixes (targeted re-check, not full 4-hour review)
4. Proceed once blocking issues resolved

### If NOT READY:
1. ❌ DO NOT send endorsement emails
2. Fix blocking issues identified by Gemini
3. Consider whether the work is premature for publication
4. Schedule full re-audit after major revisions

---

## Gemini AI Studio Setup

**Steps to conduct audit:**

1. **Go to:** https://aistudio.google.com/
2. **Create new chat:** "InfraFabric Pre-Endorsement Audit"
3. **Upload files:** All 14 files listed above (use "Add file" button)
4. **Paste audit prompt:** From `/tmp/gemini_audit_prompt.md`
5. **Start audit:** Gemini will work through 10 sections systematically
6. **Save results:** Export Gemini's full response to `docs/evidence/GEMINI-AUDIT-2025-11-10.md`

---

## Why Gemini for This Audit?

**Gemini's unique value:**
1. **Previous context:** Already validated yologuard, found 55.4% result that triggered investigation
2. **External validator:** Not Claude (we're too close to the work to be objective)
3. **Long context:** Can process all 14 files simultaneously (1M+ token window)
4. **Epistemological rigor:** Gemini caught the original metric discrepancy
5. **Independent judgment:** Will say "NOT READY" if warranted

**What Gemini already knows:**
- Tested yologuard on Leaky Repo, found 97/175 (55.4%)
- This contradicted our claimed 95/96 (98.96%)
- Prompted forensic investigation
- Led to 107/96 (111.46%) GitHub-parity metric
- Their validation is preserved in GEMINI-TO-SYNTHESIS-SAGA.md

**What we're asking Gemini to validate:**
- Did we accurately document their role?
- Is the 111.46% metric defensible?
- Are we ready to ask researchers for endorsement?

---

## Post-Audit Actions

### If Gemini Approves (READY):

1. **Document approval:**
   ```bash
   cp <gemini-output> docs/evidence/GEMINI-AUDIT-2025-11-10.md
   git add docs/evidence/GEMINI-AUDIT-2025-11-10.md
   git commit -m "docs: Add Gemini pre-endorsement audit (READY assessment)"
   ```

2. **Update GUARDED-CLAIMS.md:**
   - Mark Claim 1 (yologuard 111.46%) as VERIFIED with Gemini audit citation
   - Add citation: `if://audit/gemini-pre-endorsement-2025-11-10`

3. **Proceed with emails:**
   - Customize 15 endorser emails with your contact info
   - Send Day 1 batch (Kavathekar + van Rensburg)
   - Track responses in spreadsheet

### If Gemini Finds Issues (NEEDS REVISION):

1. **Address blocking issues first:**
   - Fix all "Must fix before emails" items
   - Run targeted validation on fixed sections

2. **Quick re-audit:**
   - Upload only the fixed files to Gemini
   - Ask: "I've addressed the blocking issues you identified. Please re-audit sections [X, Y, Z]."
   - Get go/no-go on those specific sections

3. **Proceed once clear:**
   - Document fixes in commit messages
   - Link to Gemini re-audit approval

---

## Audit Completion Checklist

- [ ] All 14 files uploaded to Gemini AI Studio
- [ ] Audit prompt pasted and submitted
- [ ] Gemini completed all 10 sections
- [ ] Overall assessment received (READY | NOT READY | NEEDS REVISION)
- [ ] Gemini's output saved to `docs/evidence/GEMINI-AUDIT-2025-11-10.md`
- [ ] If READY: Endorser emails ready to send
- [ ] If NEEDS REVISION: Issues triaged and addressed
- [ ] If NOT READY: Major revisions planned

---

## Audit Prompt Location

**GitHub Link (for Gemini):**
https://github.com/dannystocker/infrafabric/blob/claude/review-cloud-handover-docs-011CUyURbbbYv3twL6dH4r3v/docs/evidence/GEMINI-AUDIT-PROMPT-2025-11-10.md

**Local path:** `docs/evidence/GEMINI-AUDIT-PROMPT-2025-11-10.md`

**Usage:** Copy the content from GitHub link and paste as first message to Gemini AI Studio

---

**Next Step After Audit:** Based on Gemini's READY | NOT READY | NEEDS REVISION assessment

**Goal:** Independent validation that InfraFabric is endorsement-worthy before approaching 15 researchers
