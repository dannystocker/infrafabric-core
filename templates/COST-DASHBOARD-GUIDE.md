# Cost Tracking Dashboard Guide

## Overview
This guide explains how to aggregate cost tracking data across all sessions for comprehensive budget monitoring and efficiency analysis.

## Data Aggregation Strategy

### 1. Session-Level Aggregation
Collect all `COST-TRACKING-*.yaml` files from each session directory:
```bash
find . -name "COST-TRACKING-*.yaml" -type f
```

### 2. Cross-Session Metrics

#### Total Budget Overview
```yaml
project_totals:
  total_allocated: sum(all sessions.budget_allocated)
  total_spent: sum(all sessions.budget_spent)
  total_remaining: sum(all sessions.budget_remaining)
  burn_rate: total_spent / elapsed_days
  projected_completion: total_remaining / burn_rate
```

#### Model Usage Analytics
```yaml
model_efficiency:
  total_haiku_tasks: sum(all sessions.efficiency_metrics.haiku_tasks)
  total_sonnet_tasks: sum(all sessions.efficiency_metrics.sonnet_tasks)
  haiku_percentage: (haiku_tasks / total_tasks) * 100
  sonnet_percentage: (sonnet_tasks / total_tasks) * 100

  haiku_cost: sum(tasks where model=haiku.cost_usd)
  sonnet_cost: sum(tasks where model=sonnet.cost_usd)
  cost_per_haiku_task: haiku_cost / total_haiku_tasks
  cost_per_sonnet_task: sonnet_cost / total_sonnet_tasks
```

#### Token Usage Patterns
```yaml
token_analytics:
  total_tokens_in: sum(all sessions.total_tokens_in)
  total_tokens_out: sum(all sessions.total_tokens_out)
  avg_tokens_per_task: total_tokens / total_tasks
  input_output_ratio: total_tokens_in / total_tokens_out

  by_model:
    haiku:
      tokens_in: sum(tasks where model=haiku.tokens_in)
      tokens_out: sum(tasks where model=haiku.tokens_out)
    sonnet:
      tokens_in: sum(tasks where model=sonnet.tokens_in)
      tokens_out: sum(tasks where model=sonnet.tokens_out)
```

### 3. Phase-Based Analysis

Track costs by development phase:
```yaml
phase_breakdown:
  phase-0:
    sessions: [list of sessions in phase-0]
    total_cost: $XXX.XX
    task_count: XX
    avg_cost_per_task: $XX.XX

  phase-1:
    sessions: [list of sessions in phase-1]
    total_cost: $XXX.XX
    task_count: XX
    avg_cost_per_task: $XX.XX
```

### 4. Milestone Progress Tracking

```yaml
milestone_costs:
  "25%":
    total_cost: sum(tasks where milestone=25%.cost_usd)
    task_count: count(tasks where milestone=25%)
  "50%":
    total_cost: sum(tasks where milestone=50%.cost_usd)
    task_count: count(tasks where milestone=50%)
  "75%":
    total_cost: sum(tasks where milestone=75%.cost_usd)
    task_count: count(tasks where milestone=75%)
  "100%":
    total_cost: sum(tasks where milestone=100%.cost_usd)
    task_count: count(tasks where milestone=100%)
```

### 5. Waste Detection and Optimization

```yaml
efficiency_analysis:
  total_waste_cost: sum(all sessions.budget_spent * cost_waste_percent)
  waste_by_category:
    - redundant_tasks: tasks with duplicate descriptions
    - over_engineered: tasks exceeding normal token usage
    - failed_attempts: tasks followed by retry tasks

  optimization_opportunities:
    - switch_to_haiku: sonnet tasks that could use haiku
    - batch_processing: similar tasks that could be combined
    - prompt_optimization: tasks with high input tokens
```

## Dashboard Visualization Recommendations

### 1. Executive Summary View
```
┌─────────────────────────────────────────┐
│  PROJECT COST DASHBOARD                 │
├─────────────────────────────────────────┤
│  Budget Allocated:    $XXX,XXX          │
│  Budget Spent:        $XXX,XXX (XX%)    │
│  Budget Remaining:    $XXX,XXX          │
│  Burn Rate:          $XXX/day           │
│  Projected End Date:  YYYY-MM-DD        │
└─────────────────────────────────────────┘
```

### 2. Model Usage Pie Chart
```
   Haiku vs Sonnet Distribution
   ┌─────────────┐
   │  Haiku XX%  │  $XXX.XX
   │  Sonnet XX% │  $XXX.XX
   └─────────────┘
```

### 3. Phase Cost Timeline
```
Phase-0  ████████░░  $XXX.XX
Phase-1  ██████░░░░  $XXX.XX
Phase-2  ███░░░░░░░  $XXX.XX
Phase-3  ░░░░░░░░░░  $XXX.XX
```

### 4. Daily Cost Trend Line Graph
```
Cost ($)
  │
  │         ╱╲
  │      ╱╲╱  ╲
  │   ╱╲╱      ╲╱╲
  │╱╲╱            ╲
  └─────────────────── Time
```

### 5. Task Efficiency Heat Map
```
              Low Cost → High Cost
Simple    ░░░░░░░░ ▓▓▓▓ ████
Medium    ░░░░ ▓▓▓▓ ████ ████
Complex   ▓▓▓▓ ████ ████ ████
```

## Automation Scripts

### Python Aggregation Script
```python
import yaml
from pathlib import Path
from datetime import datetime

def aggregate_costs(root_dir):
    total_cost = 0
    all_tasks = []

    for cost_file in Path(root_dir).rglob("COST-TRACKING-*.yaml"):
        with open(cost_file) as f:
            data = yaml.safe_load(f)
            total_cost += float(data['total_cost'].replace('$', ''))
            all_tasks.extend(data['tasks'])

    return {
        'total_cost': total_cost,
        'total_tasks': len(all_tasks),
        'avg_cost_per_task': total_cost / len(all_tasks) if all_tasks else 0
    }
```

### Shell Script for Quick Summary
```bash
#!/bin/bash
# aggregate-costs.sh

echo "=== Cost Tracking Summary ==="
find . -name "COST-TRACKING-*.yaml" | while read file; do
    session=$(grep "^session:" "$file" | cut -d' ' -f2)
    cost=$(grep "^total_cost:" "$file" | cut -d' ' -f2)
    echo "$session: $cost"
done
```

## Alerts and Thresholds

Set up monitoring alerts:
```yaml
alerts:
  - type: budget_threshold
    condition: budget_spent > (budget_allocated * 0.8)
    action: "WARNING: 80% budget consumed"

  - type: daily_limit
    condition: daily_cost > $100
    action: "ALERT: Daily cost exceeds $100"

  - type: waste_percentage
    condition: cost_waste_percent > 15%
    action: "OPTIMIZE: Waste exceeds 15%"

  - type: model_imbalance
    condition: sonnet_tasks > (total_tasks * 0.7)
    action: "SUGGEST: Consider more Haiku usage"
```

## Export Formats

### JSON Export
```json
{
  "project": "infrafabric",
  "export_date": "2025-11-12",
  "total_cost": "XXX.XX",
  "sessions": [...]
}
```

### CSV Export
```csv
session,phase,date,budget_allocated,budget_spent,haiku_tasks,sonnet_tasks,total_cost
session-001,phase-0,2025-11-01,$500,$234,12,8,$234.56
session-002,phase-0,2025-11-02,$500,$189,15,5,$189.23
```

## Integration Points

- **CI/CD**: Automatically update cost tracking on each session completion
- **Reporting**: Generate weekly cost reports via cron jobs
- **Alerts**: Send notifications when thresholds are exceeded
- **Analytics**: Feed data into business intelligence tools

## Best Practices

1. Update cost tracking in real-time during sessions
2. Review efficiency metrics weekly
3. Identify waste patterns and optimize prompts
4. Balance Haiku/Sonnet usage based on task complexity
5. Set phase-specific budget targets
6. Archive historical data for trend analysis
7. Document cost-saving measures and their impact
