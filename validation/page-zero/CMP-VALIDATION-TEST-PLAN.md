# CMP Validation Test Plan

**Goal:** Scientifically confirm (or refute) the CMP thesis in production

**Status:** 🟡 Architecture validated, CMP hypothesis not yet tested

---

## Current State: Why We Can't Confirm CMP Yet

### What We Have ✅
- Weighted coordination system (working)
- Self-improvement loop (functional)
- Agent lineage tracking (operational)
- CMP estimates (calculated)
- Manifests capturing all data

### What We're Missing ❌
1. **Sample size**: 5-10 contacts (need 50-100+)
2. **Temporal depth**: 2-3 runs (need 10+)
3. **Control group**: No naive baseline to compare
4. **Statistical power**: Can't distinguish signal from noise

### Honest Assessment

**We've proven:** The infrastructure supports CMP principles
**We haven't proven:** CMP discovers late bloomers that naive kills

**Current evidence:** Suggestive but not conclusive
**To claim "CMP confirmed":** Need rigorous A/B test

---

## Experiment Design: CMP Validation A/B Test

### Hypothesis

**H1 (Primary):** Weighted coordination discovers late bloomers that naive termination kills

**H2 (Secondary):** Weighted system performance exceeds naive after warmup period

**H3 (Mechanism):** CMP estimates predict future agent success

### Method

**Parallel A/B test with matched samples:**

```
┌─────────────────────────────────────────────────┐
│ Same 100 Contacts                               │
│ Same Random Seed                                │
│ Same Agent Implementations                      │
└───────────────┬─────────────────────────────────┘
                │
        ┌───────┴────────┐
        │                │
   ┌────▼────┐     ┌────▼────┐
   │ Weighted│     │  Naive  │
   │ System  │     │ System  │
   └────┬────┘     └────┬────┘
        │                │
        │ All agents     │ Terminates
        │ kept alive     │ after 3 fails
        │ (0.0 weight)   │
        │                │
   ┌────▼────┐     ┌────▼────┐
   │Results  │     │Results  │
   │Manifests│     │Manifests│
   └────┬────┘     └────┬────┘
        │                │
        └───────┬────────┘
                │
         ┌──────▼───────┐
         │  Statistical │
         │  Comparison  │
         └──────────────┘
```

### Implementation Steps

**1. Build Naive Coordinator (Control Group)**

```python
class NaiveCoordinator:
    """
    Traditional approach: Terminate poor performers early.

    Rules:
    - All agents start with weight 1.0 (equal)
    - After 3 failures (success rate < 30%), terminate agent
    - No CMP estimates, no patience for late bloomers
    - Simple average (no weighted coordination)
    """

    def __init__(self):
        self.terminated_agents = set()
        self.failure_counts = defaultdict(int)

    def evaluate_agent(self, agent_name, success):
        if not success:
            self.failure_counts[agent_name] += 1

        # Terminate after 3 failures
        if self.failure_counts[agent_name] >= 3:
            self.terminated_agents.add(agent_name)
            print(f"❌ {agent_name} terminated (3 failures)")

    def should_use_agent(self, agent_name):
        return agent_name not in self.terminated_agents
```

**2. Run Parallel Test**

```python
def run_cmp_validation(contacts, num_runs=10):
    """
    Run weighted and naive in parallel on same contacts.

    Returns comparative metrics for statistical analysis.
    """
    # Initialize both systems
    weighted = WeightedCoordinator()
    naive = NaiveCoordinator()

    results = {
        'weighted': [],
        'naive': [],
        'late_bloomers_weighted': [],
        'late_bloomers_naive': [],
    }

    for run in range(num_runs):
        for contact in contacts:
            # Process with weighted (keeps all alive)
            w_result = weighted.find_contact(contact)
            results['weighted'].append(w_result)

            # Process with naive (terminates failures)
            n_result = naive.find_contact(contact)
            results['naive'].append(n_result)

        # Check for late bloomers after each run
        results['late_bloomers_weighted'].append(
            detect_late_bloomers(weighted.agent_history)
        )
        results['late_bloomers_naive'].append(
            detect_late_bloomers(naive.agent_history)
        )

    return results
```

**3. Statistical Analysis**

```python
def analyze_cmp_validation(results):
    """
    Test hypotheses with statistical rigor.
    """
    # H1: Late bloomer discovery rate
    w_late_bloomers = results['late_bloomers_weighted'][-1]  # Final count
    n_late_bloomers = results['late_bloomers_naive'][-1]

    # Chi-square test
    h1_pvalue = chi_square_test(w_late_bloomers, n_late_bloomers)

    # H2: System performance at maturity
    w_conf_final = np.mean([r['confidence'] for r in results['weighted'][-10:]])
    n_conf_final = np.mean([r['confidence'] for r in results['naive'][-10:]])

    # T-test
    h2_pvalue = t_test(w_conf_final, n_conf_final)

    # H3: CMP predictive power
    cmp_run5 = [agent['cmp_estimate'] for agent in weighted.agents]
    success_run10 = [agent['success_rate'] for agent in weighted.agents]
    h3_correlation = pearson_correlation(cmp_run5, success_run10)

    return {
        'h1_late_bloomers': {
            'weighted': w_late_bloomers,
            'naive': n_late_bloomers,
            'p_value': h1_pvalue,
            'significant': h1_pvalue < 0.05
        },
        'h2_performance': {
            'weighted': w_conf_final,
            'naive': n_conf_final,
            'p_value': h2_pvalue,
            'significant': h2_pvalue < 0.05
        },
        'h3_cmp_predictive': {
            'correlation': h3_correlation,
            'significant': h3_correlation > 0.6
        }
    }
```

### Success Criteria

**CMP CONFIRMED if ALL of:**

1. ✅ **Late bloomers discovered** (H1)
   - Weighted finds ≥3 late bloomers
   - Naive finds <1 late bloomer
   - Difference significant (p < 0.05)

2. ✅ **Performance superior** (H2)
   - Weighted confidence > Naive confidence at Run 10
   - Difference significant (p < 0.05)

3. ✅ **CMP predicts success** (H3)
   - Correlation(CMP_run5, success_run10) > 0.6
   - Significant (p < 0.05)

**CMP REFUTED if:**
- No late bloomers found in either system
- Naive performs equally well or better
- CMP estimates don't correlate with future success

---

## Resource Requirements

### Computational

**Per run:**
- 100 contacts × 6 agents = 600 agent invocations
- 10 runs × 600 = 6,000 total invocations
- 2 systems (weighted + naive) = 12,000 invocations

**Time estimate:**
- 0.5 sec per agent invocation
- 12,000 × 0.5 sec = 6,000 seconds = **100 minutes**

**Cost estimate:**
- Free agents: $0
- Google validation: ~10% × $0.005 = ~$6.00 total
- **Acceptable for validation experiment**

### Data Storage

**Per system:**
- 10 manifests × 50KB = 500KB
- Agent lineage records: ~200KB
- Total per system: ~700KB

**Both systems:** 1.4MB (trivial)

---

## Timeline

### Week 1: Infrastructure
- [ ] Implement NaiveCoordinator
- [ ] Add statistical analysis functions
- [ ] Build comparison framework
- [ ] Dry run with 10 contacts

### Week 2: Data Collection
- [ ] Run full A/B test (100 contacts, 10 runs)
- [ ] Monitor for errors/anomalies
- [ ] Generate intermediate reports

### Week 3: Analysis
- [ ] Statistical hypothesis testing
- [ ] Visualizations (agent maturation curves)
- [ ] Write validation report
- [ ] Peer review results

---

## Expected Outcomes

### Scenario 1: CMP Confirmed ✅

**Evidence we'd see:**
- InvestigativeJournalist: Terminated by naive at Run 2, thrives in weighted by Run 10
- Weighted system: 3-5 late bloomers discovered (0% → 70%+ trajectory)
- Naive system: 0-1 late bloomers (others terminated early)
- Performance gap: Weighted 5-10 points higher confidence at maturity

**Conclusion:**
"CMP validated in production: Weighted coordination discovers late bloomers that naive termination kills. Patient exploration with 0.0 weight reveals hidden value."

### Scenario 2: CMP Refuted ❌

**Evidence we'd see:**
- No agents show 0% → 70%+ trajectory in either system
- All agents either consistently succeed or consistently fail
- No performance gap between weighted and naive
- CMP estimates don't predict future success

**Conclusion:**
"CMP not applicable to contact discovery domain: Agent performance stable from start, no late bloomer patterns detected. Weighted coordination provides no advantage over naive termination."

### Scenario 3: Inconclusive ⚠️

**Evidence we'd see:**
- Small sample effects (p > 0.05, underpowered)
- Mixed signals (some hypotheses confirmed, others not)
- High variance in agent performance

**Conclusion:**
"Insufficient evidence to confirm or refute CMP. Recommend: (1) Increase sample size to N=200+, (2) Extend to 20+ runs, (3) Test in different domains."

---

## Why This Matters

### Scientific Rigor

**Current claim:** "We built a system that supports CMP principles"
**True but weak:** Infrastructure validation, not hypothesis validation

**Stronger claim (after test):** "We proved CMP discovers late bloomers"
**Requires:** Statistical evidence from controlled experiment

### Market Credibility

**Potential customers ask:** "Why should I pay for your self-improving system?"

**Without validation:**
"It's based on CMP theory from research literature"
→ Theory is nice, but does it work?

**With validation:**
"We ran 100-contact A/B test. Weighted found 4 late bloomers (40% success after warmup), naive terminated them all after 3 failures. 10-point confidence gap at maturity, p<0.01."
→ Now you have numbers and proof

### InfraFabric Thesis

CMP is CENTRAL to IF philosophy:
- "Keep bad branches alive"
- "Late bloomers need patience"
- "Reciprocity without termination"

**If CMP doesn't work in practice**, IF thesis weakens.
**If CMP works and we prove it**, IF thesis strengthens significantly.

---

## Recommendation

### Short Term (This Week)

**Build minimal naive baseline:**
```python
# Just enough to compare
class NaiveCoordinator:
    def __init__(self):
        self.active_agents = set(AGENT_PROFILES.keys())

    def terminate_if_failed(self, agent, success_rate):
        if success_rate < 0.3 after 5 attempts:
            self.active_agents.remove(agent)
```

**Run small pilot (N=20 contacts, 5 runs):**
- Get first comparison data
- Check if late bloomer signals visible
- Identify any implementation issues

**Result:** Preliminary evidence (not conclusive, but informative)

### Medium Term (Next 2 Weeks)

**Run full validation (N=100 contacts, 10 runs):**
- Controlled A/B test
- Statistical analysis
- Visualization of maturation curves

**Result:** Publication-ready validation study

### Long Term (Next Month)

**Cross-domain validation:**
- Test in different domains (academics, tech community, etc.)
- Verify CMP generalizes beyond single contact type
- Build confidence in robustness

**Result:** Defensible claim: "CMP validated across domains"

---

## Bottom Line

### Current Status

**Architecture:** ✅ Ready for CMP validation
**Evidence:** ⚠️ Suggestive but not conclusive
**Claim:** "Infrastructure supports CMP" (weak)
**Missing:** Controlled experiment with statistical rigor

### To Confirm CMP

**Need:**
1. Naive baseline (control group)
2. 50-100 contacts (statistical power)
3. 10+ runs (temporal depth)
4. Statistical analysis (hypothesis testing)

**Then we can claim:**
"CMP validated in production with statistical evidence"

### Time Investment

**Minimal pilot:** 2-3 hours (20 contacts, 5 runs)
**Full validation:** 1-2 days (100 contacts, 10 runs, analysis)
**Publication-ready:** 1 week (write-up, peer review, visualization)

### Recommendation

**Do the full validation.**

Why:
- CMP is central to IF thesis (worth validating properly)
- Market credibility requires evidence (not just theory)
- We're 80% there (just need naive baseline + bigger sample)
- Result will be scientifically defensible (publishable)

Without validation, we have "a system that might work."
With validation, we have "a system proven to work."

**The difference matters.**

---

**Status:** 🟡 Ready to validate, not yet validated
**Next step:** Build naive baseline and run pilot (N=20, 5 runs)
**Timeline:** 2-3 hours for pilot, 1-2 days for full validation
