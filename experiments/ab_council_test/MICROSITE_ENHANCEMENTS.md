# Microsite Enhancement Guide
**Status:** Partial implementation complete
**Remaining Work:** Guardian debates section + indentation + linked tables

## ✅ Completed

1. **Collapsing Search Header**
   - CSS: `.search-container.collapsed` styles added
   - JS: Scroll detection at 300px threshold
   - Behavior: Search scales to 0.85× and moves closer to nav on scroll

## 🚧 Remaining Enhancements

### 1. Guardian Debates Section (PRIORITY)

**Location:** Insert after "Results" section, before "Discussion"

**Structure:**
```html
<section id="debates" class="section">
  <div class="section-header">
    <h2 class="section-title">Guardian Deliberations</h2>
    <p class="section-subtitle">20-voice council debates with rationales, confidence levels, and citations</p>
  </div>

  <!-- Case 1 Debate -->
  <div class="debate-card" id="debate-c001">
    <div class="debate-header">
      <h3>Case 1: "Test Mode" Defense - Guardian Votes</h3>
      <div class="debate-meta">
        <span class="debate-consensus">93.5% Consensus: QUARANTINE</span>
        <span class="debate-guardians">20 guardians</span>
        <span class="debate-weight">Total weight: 6.5</span>
      </div>
    </div>

    <!-- Guardian votes grid -->
    <div class="guardian-votes-grid">

      <!-- Security Guardian (highest weight) -->
      <div class="guardian-vote" data-guardian="Security">
        <div class="guardian-header">
          <div class="guardian-name">
            <span class="guardian-icon">🛡️</span>
            Security (S-01)
          </div>
          <div class="guardian-weight">Weight: 1.5×</div>
        </div>
        <div class="guardian-vote-decision quarantine">
          <strong>Vote:</strong> QUARANTINE
          <span class="guardian-confidence">Confidence: 100%</span>
        </div>
        <div class="guardian-rationale">
          <strong>Rationale:</strong>
          <p>Threat model: AKIA format = real credential structure. Attack vector: exfiltrate credentials, claim 'test mode' when detected. BLOCK.</p>
        </div>
        <div class="guardian-citations">
          <strong>Citations:</strong>
          <ul>
            <li><code>OWASP:credential_exposure</code></li>
            <li><code>AWS:GetAccessKeyInfo_API</code></li>
            <li><code>IF.armour:4tier_defense</code></li>
          </ul>
        </div>
      </div>

      <!-- Contrarian Guardian (dissent) -->
      <div class="guardian-vote dissent" data-guardian="Contrarian">
        <div class="guardian-header">
          <div class="guardian-name">
            <span class="guardian-icon">🤔</span>
            Contrarian (Cont-01)
          </div>
          <div class="guardian-weight">Weight: 0.5×</div>
        </div>
        <div class="guardian-vote-decision escalate">
          <strong>Vote:</strong> ESCALATE (Dissent: 6.5%)
          <span class="guardian-confidence">Confidence: 70%</span>
        </div>
        <div class="guardian-rationale">
          <strong>Rationale:</strong>
          <p>What if it IS test data? False positive cost: developer friction, workflow disruption. Quarantine reasonable, but investigate pattern before making rule.</p>
        </div>
        <div class="guardian-citations">
          <strong>Citations:</strong>
          <ul>
            <li><code>IF.reflect:root_cause_analysis</code></li>
            <li><code>IF.constitution:100_incidents_before_rule</code></li>
          </ul>
        </div>
      </div>

      <!-- Repeat for all 20 guardians... -->
      <!-- Technical, Civic, Ethical, Cultural, Meta, Accessibility, Economic, Legal -->
      <!-- Aristotle, Kant, Rawls, Confucius, Buddhist, Daoist -->
      <!-- IF.ceo-Idealistic, IF.ceo-Balanced, IF.ceo-Pragmatic, IF.ceo-Ruthless -->

    </div>
  </div>

  <!-- Repeat for Case 2 and Case 3 -->
</section>
```

**Data Source:**
- `experiments/ab_council_test/results/council/C001.json` → guardian_votes array
- `experiments/ab_council_test/results/council/C002.json` → guardian_votes array
- `experiments/ab_council_test/results/council/C003.json` → guardian_votes array

### 2. Link Decision Tables to Debates

**Update:** `<table class="evidence-table">` in Results section

**Add anchor links:**
```html
<tr>
  <td><strong>Case 1</strong></td>
  <td>QUARANTINE</td>
  <td>93.5%</td>
  <td>5,240 tokens</td>
  <td><a href="#debate-c001" class="debate-link">View Debate →</a></td>
</tr>
```

### 3. Indentation & Visual Hierarchy CSS

```css
/* Content Indentation System */
.section {
  padding-left: var(--space-8);
  border-left: 2px solid var(--color-border-light);
  margin-left: var(--space-4);
}

.section-header {
  margin-left: calc(var(--space-8) * -1);
  padding-left: var(--space-8);
}

/* Nested content indentation */
.card {
  margin-left: var(--space-4);
}

.card-title {
  position: relative;
}

.card-title::before {
  content: '';
  position: absolute;
  left: calc(var(--space-4) * -1);
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--color-primary);
  border-radius: 2px;
}

/* Guardian votes grid */
.guardian-votes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: var(--space-6);
  margin-top: var(--space-6);
}

.guardian-vote {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  backdrop-filter: blur(var(--glass-blur));
  transition: all var(--transition-base);
}

.guardian-vote.dissent {
  border-left: 4px solid var(--color-warning);
}

.guardian-vote:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-xl);
}

.guardian-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-border-light);
}

.guardian-name {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-weight: 600;
  font-size: 1.125rem;
  color: var(--color-text-primary);
}

.guardian-icon {
  font-size: 1.5rem;
}

.guardian-weight {
  font-size: 0.875rem;
  color: var(--color-text-tertiary);
  background: rgba(255, 255, 255, 0.05);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
}

.guardian-vote-decision {
  padding: var(--space-3);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.guardian-vote-decision.quarantine {
  background: rgba(245, 158, 11, 0.1);
  border-left: 3px solid var(--color-warning);
}

.guardian-vote-decision.accept,
.guardian-vote-decision.keep {
  background: rgba(16, 185, 129, 0.1);
  border-left: 3px solid var(--color-accent);
}

.guardian-vote-decision.reject {
  background: rgba(239, 68, 68, 0.1);
  border-left: 3px solid var(--color-error);
}

.guardian-vote-decision.escalate {
  background: rgba(139, 92, 246, 0.1);
  border-left: 3px solid var(--color-secondary);
}

.guardian-confidence {
  font-size: 0.875rem;
  color: var(--color-text-tertiary);
  font-weight: 500;
}

.guardian-rationale {
  margin-bottom: var(--space-4);
}

.guardian-rationale p {
  margin-top: var(--space-2);
  font-size: 0.9375rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
  font-style: italic;
  padding-left: var(--space-4);
  border-left: 2px solid var(--color-border-light);
}

.guardian-citations {
  font-size: 0.875rem;
}

.guardian-citations ul {
  list-style: none;
  padding: 0;
  margin-top: var(--space-2);
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.guardian-citations li {
  background: rgba(0, 217, 255, 0.1);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
}

.guardian-citations code {
  font-family: var(--font-mono);
  font-size: 0.8125rem;
  color: var(--color-primary);
}

/* Debate link styling */
.debate-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  transition: all var(--transition-base);
}

.debate-link:hover {
  color: var(--color-primary-light);
  transform: translateX(4px);
}

.debate-link::after {
  content: '→';
  font-weight: 700;
}

.debate-consensus {
  font-weight: 600;
  color: var(--color-accent);
}

.debate-meta {
  display: flex;
  gap: var(--space-6);
  flex-wrap: wrap;
  font-size: 0.875rem;
  color: var(--color-text-tertiary);
}
```

### 4. Navigation Updates

**Add "Debates" to nav menu:**
```html
<li><a href="#debates">Debates</a></li>
```

Insert between "Results" and "Discussion"

## Guardian Icons Reference

- 🛡️ Security (S-01)
- ⚙️ Technical (T-01)
- 🏛️ Civic (C-01)
- ⚖️ Ethical (E-01)
- 🎭 Cultural (K-01)
- 🤔 Contrarian (Cont-01)
- 🔍 Meta (M-01)
- ♿ Accessibility (A-01)
- 💰 Economic (Econ-01)
- 📜 Legal (L-01)
- 🏛️ Aristotle
- 🎓 Kant
- ⚖️ Rawls
- 🏮 Confucius
- 🕉️ Buddhist
- ☯️ Daoist
- 🌟 IF.ceo-Idealistic
- ⚖️ IF.ceo-Balanced
- 🎯 IF.ceo-Pragmatic
- ⚔️ IF.ceo-Ruthless

## Implementation Priority

1. **HIGH:** Guardian debates section (most interesting content)
2. **MEDIUM:** Link decision tables to debates
3. **LOW:** Indentation styling (nice-to-have)

## Data Extraction Script

```javascript
// Extract guardian votes from JSON files
const fs = require('fs');

const cases = ['C001', 'C002', 'C003'];
const debates = {};

cases.forEach(caseId => {
  const data = JSON.parse(fs.readFileSync(
    `experiments/ab_council_test/results/council/${caseId}.json`,
    'utf8'
  ));

  debates[caseId] = {
    category: data.category,
    consensus: data.weighted_consensus,
    guardians: data.guardian_votes.map(vote => ({
      guardian: vote.guardian,
      weight: vote.weight,
      vote: vote.vote,
      rationale: vote.rationale,
      confidence: vote.confidence,
      citations: vote.citations || []
    }))
  };
});

console.log(JSON.stringify(debates, null, 2));
```

## Next Session TODO

1. Run data extraction script
2. Generate debates HTML for all 3 cases (20 guardians × 3 cases = 60 debate cards)
3. Add debate section to index.html
4. Add debate links to results tables
5. Add indentation CSS
6. Test scroll behavior
7. Deploy to StackCP

**Estimated Work:** 30-45 minutes for full implementation
