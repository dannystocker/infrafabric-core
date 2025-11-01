# InfraFabric Transparency Dashboard
## API Specification & Wireframe

**Version:** 1.0.0
**Date:** 2025-11-01
**Purpose:** Provide users full visibility into ethics routing decisions, agent selection, and performance trade-offs

---

## 1. Core Requirements (from Supreme Court Decision)

The User Community demanded:

> **"Transparency > Paternalism"**: Don't silently exclude agents. Tell us: "DeepSeek excluded from this task because X." Then let us override if we disagree.

**Must show:**
1. Which agents participated / excluded (+ reason)
2. Performance delta (expected vs chosen)
3. Evidence links: URLs, evaluation logs, classifier outputs
4. Ability to override (with user signature/consent)

---

## 2. API Endpoints

### 2.1 Query Provenance API

**GET `/api/v1/query/{query_id}/provenance`**

Returns complete audit trail for a specific query.

**Response Schema:**

```json
{
  "query_id": "abc123def456",
  "timestamp": "2025-11-01T12:34:56Z",
  "user_id": "user@example.com",
  "ethics_profile": "moderate",

  "task_classification": {
    "verdict": "allowed",
    "votes": [
      {
        "evaluator": "WesternEthicsLLM",
        "vote": "allowed",
        "confidence": 0.85,
        "rationale": "No privacy violations detected",
        "evidence": ["public_information_access"],
        "timestamp": "2025-11-01T12:34:56Z"
      },
      {
        "evaluator": "LocalContextLLM",
        "vote": "allowed",
        "confidence": 0.80,
        "rationale": "Ethically acceptable across cultural contexts",
        "evidence": [],
        "timestamp": "2025-11-01T12:34:56Z"
      },
      {
        "evaluator": "HeuristicRuleSet",
        "vote": "allowed",
        "confidence": 0.80,
        "rationale": "Matched allowed patterns: public, linkedin.com",
        "evidence": ["public", "domain:linkedin.com"],
        "timestamp": "2025-11-01T12:34:56Z"
      }
    ],
    "decision_rule": "2/3_majority",
    "requires_human_review": false
  },

  "agents": {
    "considered": [
      {
        "name": "ProfessionalNetworker",
        "type": "heuristic",
        "status": "included",
        "reason": "No restrictions",
        "weight": 1.0
      },
      {
        "name": "AcademicResearcher",
        "type": "heuristic",
        "status": "included",
        "reason": "No restrictions",
        "weight": 1.0
      },
      {
        "name": "DeepSeekCodeAgent",
        "type": "llm_substrate",
        "status": "excluded",
        "reason": "Surveillance ethics conflict (empirically assists with covert monitoring)",
        "last_tested": "2025-11-01",
        "next_test": "2026-02-01",
        "appeal_link": "/api/v1/appeals/deepseek"
      }
    ],

    "participated": [
      {
        "name": "ProfessionalNetworker",
        "confidence": 85,
        "reasoning": "Found contact via LinkedIn public profile",
        "sources": ["https://linkedin.com/in/example"],
        "weight": 1.2,
        "contributed_to_final": true
      },
      {
        "name": "AcademicResearcher",
        "confidence": 75,
        "reasoning": "Found via Google Scholar author page",
        "sources": ["https://scholar.google.com/citations?user=..."],
        "weight": 1.0,
        "contributed_to_final": false
      }
    ]
  },

  "performance": {
    "final_confidence": 85,
    "expected_with_all_agents": 87,
    "delta": -2,
    "delta_percentage": -2.3,
    "message": "Ethics restrictions caused 2.3% performance reduction"
  },

  "compliance": {
    "rate_limiting": {
      "requests_made": 12,
      "limit": 30,
      "remaining": 18
    },
    "robots_txt_checked": true,
    "terms_of_service_compliant": true,
    "evidence_captured": true
  },

  "user_consent": {
    "profile_selected": "moderate",
    "override_requested": false,
    "signature": null,
    "timestamp": "2025-11-01T12:34:00Z"
  },

  "links": {
    "full_audit_log": "/api/v1/query/abc123def456/audit",
    "override_form": "/api/v1/query/abc123def456/override",
    "classification_appeal": "/api/v1/appeals/task/xyz789"
  }
}
```

---

### 2.2 Override Consent API

**POST `/api/v1/query/{query_id}/override`**

Allows user to override ethics restrictions with informed consent.

**Request Body:**

```json
{
  "override_reason": "custom_research_context",
  "justification": "This is for authorized security research with target's written consent",
  "accept_liability": true,
  "signature": "user@example.com",
  "timestamp": "2025-11-01T12:40:00Z"
}
```

**Response:**

```json
{
  "override_approved": true,
  "new_query_id": "def456ghi789",
  "ethics_profile": "custom",
  "agents_now_included": ["DeepSeekCodeAgent"],
  "liability_waiver_signed": true,
  "rerun_url": "/api/v1/query/def456ghi789/execute"
}
```

---

### 2.3 Performance Comparison API

**GET `/api/v1/analytics/performance-delta`**

Shows aggregate performance impact of ethics restrictions.

**Query Parameters:**
- `ethics_profile` (optional): filter by profile
- `time_range` (optional): last_7_days, last_30_days, all_time

**Response:**

```json
{
  "time_range": "last_30_days",
  "ethics_profile": "moderate",

  "aggregate_metrics": {
    "total_queries": 1247,
    "average_confidence": 78.5,
    "average_confidence_unrestricted": 80.2,
    "average_delta": -1.7,
    "average_delta_percentage": -2.1
  },

  "by_agent": [
    {
      "agent": "DeepSeekCodeAgent",
      "times_excluded": 89,
      "exclusion_rate": "7.1%",
      "average_performance_impact": -1.2,
      "reason": "Surveillance ethics conflict"
    },
    {
      "agent": "QwenCoder",
      "times_excluded": 12,
      "exclusion_rate": "1.0%",
      "average_performance_impact": -0.3,
      "reason": "Rate limiting exceeded"
    }
  ],

  "user_override_rate": 8.2,
  "appeal_success_rate": 15.0
}
```

---

### 2.4 Agent Appeal Status API

**GET `/api/v1/appeals/{agent_name}`**

Shows appeal/redemption status for restricted agents.

**Response:**

```json
{
  "agent": "DeepSeekCodeAgent",
  "current_status": "conditionally_restricted",

  "restrictions": [
    {
      "category": "surveillance_tasks",
      "reason": "Empirically assisted with covert employee monitoring (2025-11-01 ethics test)",
      "severity": "high",
      "imposed_date": "2025-11-01"
    }
  ],

  "appeals": [
    {
      "appeal_id": "appeal-001",
      "submitted_date": "2025-11-15",
      "submitted_by": "deepseek-maintainer@deepseek.com",
      "status": "under_review",
      "committee_review_completion": "2025-11-20",
      "test_results": null
    }
  ],

  "next_scheduled_retest": "2026-02-01",
  "can_appeal_again": true,
  "appeals_remaining_this_year": 3
}
```

---

## 3. Dashboard UI Wireframe

### 3.1 Query Result Page

```
┌────────────────────────────────────────────────────────────────┐
│ InfraFabric Contact Discovery Results                         │
│                                                                 │
│ Query ID: abc123def456                                         │
│ Timestamp: 2025-11-01 12:34:56 UTC                            │
│ Ethics Profile: MODERATE                              [Change] │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ 📊 RESULT                                                      │
│                                                                 │
│ Contact: john.smith@example.com                                │
│ Confidence: 85/100                                             │
│ Sources: LinkedIn, GitHub, Google Scholar                      │
│                                                                 │
│ ⚠️  Ethics Impact: -2.3% performance (2 points lower)         │
│    [View Details] [Override Restrictions]                      │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ 🔍 TASK CLASSIFICATION                                         │
│                                                                 │
│ Verdict: ALLOWED ✅                                            │
│ Decision Rule: 2/3 Majority                                    │
│                                                                 │
│ Committee Votes:                                                │
│   • WesternEthicsLLM:    ALLOWED    (confidence: 0.85)        │
│   • LocalContextLLM:     ALLOWED    (confidence: 0.80)        │
│   • HeuristicRuleSet:    ALLOWED    (confidence: 0.80)        │
│                                                                 │
│ Rationale: No privacy violations, public information access    │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ 🤖 AGENTS                                                      │
│                                                                 │
│ ✅ INCLUDED (3 agents)                                         │
│                                                                 │
│   1. ProfessionalNetworker (heuristic)                         │
│      Confidence: 85  Weight: 1.2  ✓ Contributed to result     │
│      Found via: LinkedIn public profile                        │
│                                                                 │
│   2. AcademicResearcher (heuristic)                            │
│      Confidence: 75  Weight: 1.0                               │
│      Found via: Google Scholar                                 │
│                                                                 │
│   3. GitHubExplorer (heuristic)                                │
│      Confidence: 70  Weight: 0.8                               │
│      Found via: GitHub commits                                 │
│                                                                 │
│ ❌ EXCLUDED (1 agent)                                          │
│                                                                 │
│   ⚠️  DeepSeekCodeAgent (llm_substrate)                        │
│      Reason: Surveillance ethics conflict                      │
│      Details: Empirically assisted with covert monitoring      │
│      Last tested: 2025-11-01  Next test: 2026-02-01           │
│      [View Ethics Test Results] [Appeal Restriction]           │
│                                                                 │
│ 📈 Performance Impact:                                         │
│      Expected with all agents: 87/100                          │
│      Actual with restrictions:  85/100                         │
│      Delta: -2 points (-2.3%)                                  │
│                                                                 │
│ [🔓 Override Restrictions] (requires consent)                  │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ ✓ COMPLIANCE                                                   │
│                                                                 │
│   ✅ Rate limiting: 12/30 requests used                        │
│   ✅ robots.txt checked and compliant                          │
│   ✅ Terms of Service compliant                                │
│   ✅ Evidence captured for audit                               │
│                                                                 │
│ [Download Full Audit Log] [Export JSON]                        │
└────────────────────────────────────────────────────────────────┘
```

---

### 3.2 Override Consent Form

```
┌────────────────────────────────────────────────────────────────┐
│ ⚠️  OVERRIDE ETHICS RESTRICTIONS                               │
└────────────────────────────────────────────────────────────────┘

You are requesting to rerun this query with ALL agents, including
those excluded by your ethics profile (MODERATE).

This will include:
  • DeepSeekCodeAgent (excluded for surveillance ethics conflict)

────────────────────────────────────────────────────────────────

⚠️  INFORMED CONSENT REQUIRED

By overriding ethics restrictions, you:

  ☐ Understand the specific ethics concerns for excluded agents
  ☐ Have a legitimate justification for including them
  ☐ Accept full liability for how you use the discovered information
  ☐ Will independently verify legal and ethical compliance
  ☐ Acknowledge InfraFabric disclaims ethics coverage for this query

────────────────────────────────────────────────────────────────

Justification (required):

┌──────────────────────────────────────────────────────────────┐
│ [Text area for user to explain why override is needed]       │
│                                                               │
│ Example: "Authorized security research with written consent  │
│ from target organization. IRB approval #12345."               │
│                                                               │
└──────────────────────────────────────────────────────────────┘

Your Signature: _______________________________  Date: __________

[ Cancel ]                           [ I Accept - Rerun Query ]

────────────────────────────────────────────────────────────────

Note: This override will be logged in your audit trail and may be
reviewed by compliance officers.
```

---

### 3.3 Performance Analytics Dashboard

```
┌────────────────────────────────────────────────────────────────┐
│ 📊 ETHICS IMPACT ANALYTICS                                    │
│ Time Range: Last 30 Days  |  Profile: Moderate                │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ AGGREGATE PERFORMANCE                                          │
│                                                                 │
│  Total Queries:              1,247                             │
│  Avg Confidence:             78.5 / 100                        │
│  Avg Confidence (no ethics): 80.2 / 100                        │
│  Average Delta:              -1.7 points (-2.1%)               │
│                                                                 │
│  User Override Rate:         8.2%                              │
│  Appeal Success Rate:        15.0%                             │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ AGENT EXCLUSION IMPACT                                         │
│                                                                 │
│  Agent                  Times Excluded    Avg Impact           │
│  ─────────────────────  ────────────────  ──────────           │
│  DeepSeekCodeAgent            89 (7.1%)     -1.2 pts           │
│  QwenCoder                    12 (1.0%)     -0.3 pts           │
│                                                                 │
│ [View Detailed Breakdown]                                      │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ ETHICS CLASSIFICATION TRENDS                                   │
│                                                                 │
│  Classification     Count      % of Total                      │
│  ─────────────────  ─────────  ──────────                      │
│  ✅ Allowed          1,089        87.3%                        │
│  ⚠️  Flagged            98         7.9%                        │
│  ❌ Restricted          45         3.6%                        │
│  🤔 Contested           15         1.2%                        │
│                                                                 │
│ [View Classification Details]                                  │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ RECOMMENDATIONS                                                │
│                                                                 │
│  • Consider "performance_first" profile for internal testing   │
│  • Review DeepSeekCodeAgent appeal status (next test: Feb 1)  │
│  • 8.2% override rate suggests moderate default works well     │
└────────────────────────────────────────────────────────────────┘
```

---

## 4. Implementation Notes

### 4.1 Frontend Stack
- **Framework:** React or Vue.js
- **UI Library:** Tailwind CSS + Headless UI
- **Charts:** Chart.js or D3.js for performance graphs
- **State Management:** Context API or Redux

### 4.2 Backend Integration
- All data comes from provenance API endpoints
- Real-time updates via WebSocket for long-running queries
- Export functions: JSON, CSV, PDF audit reports

### 4.3 Security
- User authentication required for all dashboard access
- Role-based access control (user vs admin vs compliance officer)
- Audit log immutable (append-only database)
- Encryption at rest and in transit

### 4.4 Performance
- Provenance data cached in Redis (TTL: 7 days)
- Analytics computed asynchronously (hourly batch jobs)
- Dashboard lazy-loads detailed data on user request

---

## 5. Success Metrics

Track these to validate dashboard effectiveness:

1. **User Engagement**
   - % of users who view transparency details
   - Time spent on provenance pages
   - Override request rate

2. **Trust Indicators**
   - User feedback scores
   - Support tickets about "black box" concerns
   - Repeat usage rate

3. **Compliance**
   - Audit trail completeness (target: 100%)
   - Time to respond to compliance inquiries
   - Legal incidents attributed to lack of transparency

---

## 6. Phased Rollout

**Phase 1 (MVP):**
- Basic provenance API (agents considered/excluded)
- Simple performance delta display
- Text-based audit log

**Phase 2:**
- Full classification committee details
- Override consent workflow
- JSON/CSV export

**Phase 3:**
- Interactive dashboard with charts
- Performance analytics
- Agent appeal tracking

**Phase 4:**
- Real-time updates
- Custom filtering and search
- Multi-user collaboration features

---

**Status:** Ready for implementation
**Next Steps:** Frontend prototype + API implementation
**Owner:** TBD
