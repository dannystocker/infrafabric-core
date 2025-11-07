# CODE Concepts → Immediate IF Implementation
## (No Paid APIs Required)

**Date:** 2025-10-31
**Constraint:** Using only Python, Claude Code, local files, free web scraping
**Goal:** Identify CODE concepts we can implement TODAY

---

## ✅ Immediately Implementable (Zero Cost)

### 1. Auto Drive - Autonomous Task Orchestration ⭐⭐⭐⭐⭐

**STATUS: ALREADY PARTIALLY IMPLEMENTED**

We already demonstrated this:
- Autonomous debugging (fixed 3 bugs without intervention)
- Autonomous learning (4 plans executed in parallel)
- Auto-recovery (retried on failure, learned from errors)

**What to Add:**
```python
# Extend existing autonomous coordinator
class IFAutoDriveV2(RecursiveLearningCoordinator):
    """
    Enhanced autonomous orchestration.

    New capabilities:
    - Pre-execution bug scanning
    - Auto-retry with learned recovery
    - Guardian pre-approval
    - Complete session without human input
    """

    def autonomous_session(self, tasks):
        """
        Run entire session autonomously.

        Example:
        >>> tasks = [
        ...     "Find contacts for quantum sector",
        ...     "Generate outreach templates",
        ...     "Validate email patterns"
        ... ]
        >>> driver.autonomous_session(tasks)
        # Runs all tasks, learns, recovers, reports
        ```

**Implementation: 30 minutes**
- Extend `recursive_learning_coordinator.py`
- Add pre-execution scanning
- Add auto-retry logic
- No new dependencies

---

### 2. Card-Based Activity Logs ⭐⭐⭐⭐⭐

**STATUS: EASY TO IMPLEMENT**

We have IF-Trace JSON manifests. Convert to visual cards:

```python
# IF Activity Card Generator
class IFActivityCardGenerator:
    """
    Convert IF-Trace manifests to human-readable cards.

    Input: coordination_manifest_20251031_233242.json
    Output: Rich terminal cards with progress bars
    """

    def generate_card(self, manifest_entry):
        """
        Create card for a single activity.

        Example Output:
        ┌─────────────────────────────────────────────────────┐
        │ 🔍 Agent Weight Learning                            │
        │ Status: ✅ Success (0.0s)                            │
        ├─────────────────────────────────────────────────────┤
        │ Performance:                                        │
        │   ProfessionalNetworker ━━━━━━━━━━━━━━━━ 71.4%     │
        │   InvestigativeJournalist ━━━━ 25.0%               │
        │   SocialEngineer ━━━ 21.4%                         │
        ├─────────────────────────────────────────────────────┤
        │ Contribution: 25.4% (1.5× weight)                   │
        │ Files: learned_weights_*.json                       │
        └─────────────────────────────────────────────────────┘
        """

        # Use rich library (already available in Python)
        from rich.console import Console
        from rich.table import Table
        from rich.progress import BarColumn

        console = Console()

        # Create card table
        table = Table(title=manifest_entry['plan'])
        # ... build visualization

        console.print(table)
```

**Implementation: 1 hour**
- Use Python `rich` library (no cost)
- Read existing IF-Trace manifests
- Generate terminal-based cards
- Add to coordination report

**Tools Available:**
- `rich` - Terminal formatting
- `termcolor` - Color output
- ASCII box drawing

---

### 3. Explicit Reasoning Effort Control ⭐⭐⭐⭐⭐

**STATUS: TRIVIAL TO ADD**

Add effort levels to agent profiles:

```python
# Current agent profile
AGENT_PROFILES = {
    'ProfessionalNetworker': {
        'weight': 1.2,
        'data_sources': ['linkedin', 'company_website'],
        # NEW: Add effort control
        'effort': 'low',           # Fast heuristics
        'max_queries': 3,          # Limit search depth
        'timeout_seconds': 5       # Quick results
    },
    'DeepResearcher': {
        'weight': 0.8,
        'data_sources': ['scholar', 'arxiv', 'patents'],
        # NEW: Higher effort for research-heavy
        'effort': 'high',
        'max_queries': 10,         # Deep search
        'timeout_seconds': 30      # Thorough results
    }
}

# Usage in contact discovery
def find_contact_with_effort(contact, effort_level='auto'):
    """
    Control computational effort based on contact importance.

    effort_level:
    - 'low': Fast heuristics (< 5s)
    - 'medium': Balanced (< 15s)
    - 'high': Deep search (< 60s)
    - 'auto': Decide based on contact tier
    """

    if effort_level == 'auto':
        # C-level = high effort, others = low
        effort_level = 'high' if contact.is_executive else 'low'

    # Select agents matching effort level
    agents = [a for a in AGENT_PROFILES.values()
              if a['effort'] == effort_level]

    return weighted_multi_agent_search(contact, agents)
```

**Implementation: 15 minutes**
- Add `effort`, `max_queries`, `timeout_seconds` to profiles
- Update `weighted_multi_agent_finder.py`
- No new dependencies

---

### 4. Session Memory Persistence ⭐⭐⭐⭐

**STATUS: ALREADY PARTIALLY IMPLEMENTED**

We save learned weights to JSON. Extend to full session memory:

```python
# IF Session Memory (already have the foundation)
class IFSessionMemory:
    """
    Persistent learning across sessions.

    Current: learned_weights_*.json
    Add: contact_patterns, bug_patterns, template_performance
    """

    def __init__(self):
        self.memory_file = Path("~/.infrafabric/session_memory.json")
        self.load_or_create()

    def load_or_create(self):
        if self.memory_file.exists():
            with open(self.memory_file) as f:
                self.memory = json.load(f)
        else:
            self.memory = {
                'agent_weights': {},           # From weight_learner
                'bug_patterns': [],            # From bug_learner
                'contact_sector_performance': {}, # NEW: Which agents work for which sectors
                'successful_templates': [],    # NEW: Outreach templates that worked
                'last_updated': None
            }

    def update_from_execution(self, results):
        """
        Learn from each execution.

        Example:
        >>> memory.update_from_execution({
        ...     'quantum_sector': {
        ...         'best_agent': 'AcademicResearcher',
        ...         'success_rate': 0.82
        ...     }
        ... })
        ```

        # Update sector patterns
        for sector, perf in results.items():
            self.memory['contact_sector_performance'][sector] = perf

        # Save
        self.save()

    def save(self):
        self.memory['last_updated'] = datetime.now().isoformat()
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
```

**Implementation: 20 minutes**
- Extend existing JSON persistence
- Add sector performance tracking
- No new dependencies

---

### 5. Approval Policies (Guardian Enhancement) ⭐⭐⭐⭐

**STATUS: GUARDIANS ALREADY EXIST, ADD POLICIES**

Guardians already provide scores. Add configurable thresholds:

```python
# IF Approval Policies
APPROVAL_POLICIES = {
    'conservative': {
        'min_guardian_score': 9.0,
        'require_human_approval': True,
        'allowed_risk_categories': ['low']
    },
    'balanced': {
        'min_guardian_score': 7.5,
        'require_human_approval': False,
        'allowed_risk_categories': ['low', 'medium'],
        'notify_user': True
    },
    'experimental': {
        'min_guardian_score': 6.0,
        'require_human_approval': False,
        'allowed_risk_categories': ['low', 'medium', 'high'],
        'notify_user': False
    }
}

# Apply policy
def execute_with_policy(task, policy='balanced'):
    """
    Execute task only if Guardian approval meets policy.
    """
    guardian_score = guardians.review(task)

    policy_config = APPROVAL_POLICIES[policy]

    if guardian_score.score >= policy_config['min_guardian_score']:
        if policy_config['require_human_approval']:
            print(f"Guardian score: {guardian_score.score}/10")
            print("Approve? (y/n): ", end='')
            if input().lower() != 'y':
                return {'status': 'rejected_by_user'}

        return execute_task(task)
    else:
        return {
            'status': 'blocked_by_guardians',
            'score': guardian_score.score,
            'concerns': guardian_score.blocking_issues
        }
```

**Implementation: 15 minutes**
- Add policy config dict
- Update Guardian execution
- No new dependencies

---

### 6. Non-Interactive Batch Mode ⭐⭐⭐⭐

**STATUS: TRIVIAL - ALREADY HAVE BATCH PROCESSING**

Just add flags:

```bash
# Current usage (interactive)
python3 weighted_multi_agent_finder.py

# New: Non-interactive batch mode
python3 weighted_multi_agent_finder.py \
  --batch outreach-targets.csv \
  --no-approval \
  --max-cost 0.00 \
  --effort low \
  --output batch-results/

# Returns exit code 0 on success, non-zero on error
# Perfect for CI/CD pipelines
```

```python
# Add argparse to existing scripts
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--batch', help='CSV file for batch processing')
parser.add_argument('--no-approval', action='store_true',
                    help='Skip human approval (auto-approve if Guardian score OK)')
parser.add_argument('--max-cost', type=float, default=0.0,
                    help='Maximum $ cost for execution')
parser.add_argument('--effort', choices=['low', 'medium', 'high'],
                    default='low', help='Computational effort level')
parser.add_argument('--output', help='Output directory')

args = parser.parse_args()

# Use args.no_approval to skip prompts
if args.no_approval:
    execute_without_prompts()
```

**Implementation: 10 minutes**
- Add argparse to existing scripts
- Add `--no-approval` flag logic
- Already have batch processing

---

### 7. Multi-Worktree Consensus (Simplified) ⭐⭐⭐

**STATUS: IMPLEMENTABLE WITH GIT**

We already use git. Add worktree-based testing:

```python
# IF Multi-Worktree Code Generation
class IFWorktreeConsensus:
    """
    Generate code in parallel worktrees, weighted consensus.

    Use case: Generate outreach email templates
    """

    def generate_template_consensus(self, contact, num_variants=3):
        """
        Generate N template variants, weighted vote for best.

        No git worktrees needed - just temp directories:
        """

        variants = []

        for i, agent in enumerate(self.template_agents):
            # Generate in separate directory
            temp_dir = Path(f"/tmp/if_template_{i}")
            temp_dir.mkdir(exist_ok=True)

            # Agent generates template
            template = agent.generate_template(contact)

            # Guardian review
            safety = self.guardians.review_template(template)

            # Weighted scoring
            score = agent.learned_weight * safety.score

            variants.append({
                'agent': agent.name,
                'template': template,
                'score': score,
                'path': temp_dir
            })

        # Weighted consensus (not majority vote)
        best = max(variants, key=lambda v: v['score'])

        # IF-Trace
        self.trace_template_generation(variants, best)

        return best['template']
```

**Implementation: 30 minutes**
- Use temp directories (not actual git worktrees)
- Generate templates in parallel
- Weighted consensus selection
- No new dependencies

---

## 🔧 Implementation Priority Queue

### Priority 1: Immediate Value (< 1 hour total)

1. **Explicit Effort Control** (15 min)
   - Add effort levels to agent profiles
   - Immediate cost/quality control

2. **Non-Interactive Batch Mode** (10 min)
   - Add CLI flags
   - Enable automation

3. **Approval Policies** (15 min)
   - Extend Guardian framework
   - Configurable risk tolerance

4. **Session Memory** (20 min)
   - Persist sector performance
   - Learn across sessions

**Total: 60 minutes, high impact**

---

### Priority 2: High-Value Enhancements (1-2 hours)

5. **Card-Based Activity Logs** (1 hour)
   - Visual terminal output
   - Better transparency UX

6. **Auto Drive V2** (30 min)
   - Enhanced autonomous orchestration
   - Pre-execution scanning

7. **Multi-Worktree Template Generation** (30 min)
   - Parallel template variants
   - Weighted consensus

**Total: 2 hours, significant UX improvement**

---

## 📋 Detailed Implementation Plan

### Implementation 1: Explicit Effort Control

**File:** `weighted_multi_agent_finder.py`

```python
# Add to AGENT_PROFILES
AGENT_PROFILES = {
    'ProfessionalNetworker': {
        'weight': 1.2,
        'data_sources': ['linkedin', 'company'],
        'effort': 'low',         # NEW
        'max_queries': 3,        # NEW
        'timeout': 5             # NEW
    },
    # ... other agents
}

# Add effort-based selection
def select_agents_by_effort(effort_level):
    return [
        (name, profile)
        for name, profile in AGENT_PROFILES.items()
        if profile['effort'] == effort_level
    ]

# Update main execution
def find_contact(contact, effort='auto'):
    if effort == 'auto':
        effort = 'high' if contact.tier == 'C-level' else 'low'

    agents = select_agents_by_effort(effort)
    return weighted_search(contact, agents)
```

**Test:**
```bash
# Fast search (low effort)
python3 weighted_multi_agent_finder.py --effort low

# Deep search (high effort)
python3 weighted_multi_agent_finder.py --effort high --contacts c_level.csv
```

---

### Implementation 2: Card-Based Activity Logs

**File:** `if_activity_cards.py`

```python
#!/usr/bin/env python3
"""
IF Activity Cards - Visual terminal output for IF-Trace manifests.
"""

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn
import json

class IFActivityCards:
    def __init__(self):
        self.console = Console()

    def render_coordination_summary(self, manifest_path):
        """
        Render coordination manifest as rich terminal cards.
        """
        with open(manifest_path) as f:
            manifest = json.load(f)

        # Create summary table
        table = Table(title="🔄 Recursive Learning Coordination")
        table.add_column("Plan", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Time", justify="right")
        table.add_column("Contribution", justify="right")

        for entry in manifest['provenance']:
            status = "✅" if entry['success'] else "❌"
            time = f"{entry['execution_time_seconds']:.1f}s"
            contrib = f"{entry['contribution']:.1f}%"

            table.add_row(
                entry['plan'],
                status,
                time,
                contrib
            )

        self.console.print(table)

        # Show progress bars for contributions
        self.console.print("\n📊 Weighted Contributions:")
        for entry in sorted(manifest['provenance'],
                           key=lambda x: x['contribution'],
                           reverse=True):
            bar_length = int(entry['contribution'] / 2)  # Scale to 50 chars
            bar = "━" * bar_length
            self.console.print(
                f"  {entry['plan']:30s} {bar} {entry['contribution']:.1f}%"
            )

# Usage
if __name__ == "__main__":
    cards = IFActivityCards()
    cards.render_coordination_summary("coordination_manifest_20251031_233242.json")
```

**Test:**
```bash
python3 if_activity_cards.py
# Outputs rich terminal visualization
```

---

### Implementation 3: Session Memory Enhancement

**File:** `if_session_memory.py`

```python
#!/usr/bin/env python3
"""
IF Session Memory - Persistent learning across executions.
"""

import json
from pathlib import Path
from datetime import datetime

class IFSessionMemory:
    def __init__(self):
        self.memory_dir = Path.home() / ".infrafabric"
        self.memory_dir.mkdir(exist_ok=True)
        self.memory_file = self.memory_dir / "session_memory.json"
        self.load_or_create()

    def load_or_create(self):
        if self.memory_file.exists():
            with open(self.memory_file) as f:
                self.memory = json.load(f)
        else:
            self.memory = {
                'agent_weights': {},
                'bug_patterns': [],
                'sector_performance': {},  # Which agents work for which sectors
                'template_effectiveness': {},
                'last_updated': None,
                'total_executions': 0
            }

    def record_execution(self, sector, agent_performance):
        """
        Learn which agents work for which sectors.

        Example:
        >>> memory.record_execution('quantum', {
        ...     'AcademicResearcher': 0.82,
        ...     'ProfessionalNetworker': 0.65
        ... })
        ```

        if sector not in self.memory['sector_performance']:
            self.memory['sector_performance'][sector] = {}

        # Update running averages
        for agent, success_rate in agent_performance.items():
            if agent not in self.memory['sector_performance'][sector]:
                self.memory['sector_performance'][sector][agent] = {
                    'avg_success': success_rate,
                    'num_samples': 1
                }
            else:
                current = self.memory['sector_performance'][sector][agent]
                # Running average
                n = current['num_samples']
                current['avg_success'] = (
                    (current['avg_success'] * n + success_rate) / (n + 1)
                )
                current['num_samples'] = n + 1

        self.memory['total_executions'] += 1
        self.save()

    def get_best_agents_for_sector(self, sector):
        """
        Recommend best agents based on historical performance.
        """
        if sector not in self.memory['sector_performance']:
            return None  # No history

        perf = self.memory['sector_performance'][sector]
        sorted_agents = sorted(
            perf.items(),
            key=lambda x: x[1]['avg_success'],
            reverse=True
        )

        return sorted_agents

    def save(self):
        self.memory['last_updated'] = datetime.now().isoformat()
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)

# Usage
memory = IFSessionMemory()
memory.record_execution('quantum', {
    'AcademicResearcher': 0.82,
    'ProfessionalNetworker': 0.71
})

best = memory.get_best_agents_for_sector('quantum')
print(f"Best agents for quantum: {best}")
```

**Integration with existing code:**
```python
# In batch_contact_discovery.py
from if_session_memory import IFSessionMemory

memory = IFSessionMemory()

# After batch completes
memory.record_execution(
    sector=contact['sector'],
    agent_performance=batch_results['agent_performance']
)

# Before next batch
best_agents = memory.get_best_agents_for_sector(contact['sector'])
if best_agents:
    print(f"Historical best agents for {contact['sector']}: {best_agents[0][0]}")
```

---

## 🎯 Quick Wins Summary

**What we can build TODAY (no paid APIs):**

1. ✅ Explicit effort control (15 min)
2. ✅ Non-interactive batch mode (10 min)
3. ✅ Approval policy configs (15 min)
4. ✅ Session memory enhancement (20 min)
5. ✅ Card-based activity logs (1 hour)
6. ✅ Auto Drive V2 (30 min)
7. ✅ Multi-worktree template generation (30 min)

**Total implementation time: ~3 hours**
**Total cost: $0.00**
**Value: Significant UX and automation improvements**

---

## Next Steps

**Recommended sequence:**

1. **Start with effort control** (15 min) - Immediate practical value
2. **Add session memory** (20 min) - Enables cross-session learning
3. **Implement activity cards** (1 hour) - Better transparency
4. **Add batch mode flags** (10 min) - Enable automation

**After 2 hours:** You'll have:
- Cost/quality control (effort levels)
- Cross-session learning (session memory)
- Better UX (activity cards)
- Automation support (batch flags)

All at zero cost, using only existing tools.

---

**Generated:** 2025-10-31
**Status:** Ready to implement
**Cost:** $0.00
