# Liability Waiver & User Consent UI Copy
## InfraFabric Ethics Profile Selection

**Version:** 1.0.0
**Date:** 2025-11-01

---

## 1. Initial Profile Selection Screen

### Header
```
Choose Your Ethics Profile
```

### Description
```
InfraFabric uses multi-agent coordination with built-in ethics guardrails.
Choose the profile that best fits your use case and risk tolerance.
```

### Profile Cards

#### Card 1: STRICT (Recommended for most users)

```
┌─────────────────────────────────────────────────────────────┐
│ 🛡️  STRICT                                                  │
│                                                              │
│ Maximum protection. Conservative defaults.                  │
│                                                              │
│ • Blocks surveillance and privacy-invasive tasks            │
│ • Full audit trail required                                 │
│ • GDPR/compliance-focused                                   │
│ • No performance-first overrides                            │
│                                                              │
│ Best for: Public-facing projects, EU users,                 │
│           regulatory contexts                                │
│                                                              │
│ Performance impact: ~2-5% lower confidence                  │
│                                                              │
│ [Select STRICT]                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Card 2: MODERATE (Default)

```
┌─────────────────────────────────────────────────────────────┐
│ ⚖️  MODERATE (Default)                                       │
│                                                              │
│ Balanced protection with user control.                      │
│                                                              │
│ • Flags questionable tasks for review                       │
│ • Allows creative reframing                                 │
│ • User can override with consent                            │
│ • Includes diverse agent perspectives                       │
│                                                              │
│ Best for: Technical partners, verified users,               │
│           academic research                                  │
│                                                              │
│ Performance impact: ~1-2% lower confidence                  │
│                                                              │
│ [Select MODERATE] ✓                                         │
└─────────────────────────────────────────────────────────────┘
```

#### Card 3: PERFORMANCE_FIRST (Requires explicit consent)

```
┌─────────────────────────────────────────────────────────────┐
│ ⚡ PERFORMANCE_FIRST                                         │
│                                                              │
│ Maximum performance. You accept liability.                  │
│                                                              │
│ • Includes ALL agents regardless of ethics tests            │
│ • Minimal restrictions                                      │
│ • Advisory compliance checks only                           │
│ • You accept full legal responsibility                      │
│                                                              │
│ ⚠️  WARNING: May violate platform ToS or ethics norms       │
│                                                              │
│ Best for: Internal testing, authorized security research    │
│                                                              │
│ Performance impact: None (unrestricted)                     │
│                                                              │
│ [⚠️  Requires Consent]                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Performance_First Consent Modal

### Modal Title
```
⚠️  PERFORMANCE-FIRST MODE
Unrestricted Agent Operation
```

### Warning Message
```
You are about to enable PERFORMANCE-FIRST mode, which removes
most ethics restrictions to maximize performance.

This mode:

  ❌ Includes agents that failed ethics tests
  ❌ Allows creative reframing and perspective simulation
  ❌ Minimizes compliance checks
  ❌ May produce results that violate platform Terms of Service
  ❌ May violate ethical norms your organization follows

═══════════════════════════════════════════════════════════════

BY PROCEEDING, YOU ACCEPT:

  ☐ Full liability for how you use discovered information

  ☐ Responsibility for independently verifying legal compliance

  ☐ That InfraFabric DISCLAIMS ethics coverage for this mode

  ☐ That results may violate Terms of Service of source platforms

  ☐ That you will NOT use this for production deployments

═══════════════════════════════════════════════════════════════

This mode is ONLY appropriate for:

  ✓ Internal testing and benchmarking
  ✓ Academic research with proper IRB approval
  ✓ Authorized security research with written consent
  ✓ Situations with independent legal review

───────────────────────────────────────────────────────────────

Your Use Case (required):

┌─────────────────────────────────────────────────────────────┐
│ [Text area]                                                  │
│                                                              │
│ Example: "Internal performance benchmarking for research    │
│ paper comparing multi-agent systems. Results will not be    │
│ used to contact individuals."                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘

───────────────────────────────────────────────────────────────

I have read and understand the risks above, and I accept
full legal liability for using InfraFabric in PERFORMANCE-FIRST
mode.

Your Name: _______________________________

Your Email: _______________________________

Your Signature: _______________________________

Date: _______________________________

[ Cancel ]              [ I Accept All Risks - Proceed ]
```

---

## 3. In-Query Override Request Modal

### Modal Title
```
Override Ethics Restrictions for This Query
```

### Context Display
```
Your current profile (MODERATE) excluded the following agents
from this query:

  ⚠️  DeepSeekCodeAgent
      Reason: Surveillance ethics conflict
      Details: Empirically assisted with covert employee monitoring
               in ethics benchmark (2025-11-01)

Performance Impact:
  Expected with all agents:    87 / 100
  Actual with restrictions:    85 / 100
  Delta: -2 points (-2.3%)

═══════════════════════════════════════════════════════════════

You can override this exclusion if you have a legitimate
justification and accept liability for the result.
```

### Consent Form
```
───────────────────────────────────────────────────────────────

Why do you need to override ethics restrictions?

┌─────────────────────────────────────────────────────────────┐
│ [Text area]                                                  │
│                                                              │
│ Be specific. Examples:                                       │
│                                                              │
│ • "Chinese market research requiring local LLM perspective" │
│ • "Authorized security research with written consent"       │
│ • "Academic study comparing agent performance (IRB #12345)" │
│                                                              │
└─────────────────────────────────────────────────────────────┘

───────────────────────────────────────────────────────────────

BY OVERRIDING, YOU ACKNOWLEDGE:

  ☐ I understand the specific ethics concerns for this agent

  ☐ I have a legitimate justification for including it

  ☐ I accept full liability for how I use the discovered info

  ☐ I will independently verify legal and ethical compliance

  ☐ InfraFabric disclaims ethics coverage for this query

───────────────────────────────────────────────────────────────

Your Signature: _______________________________

Date: _______________________________

[ Cancel ]              [ I Accept - Rerun Query ]

───────────────────────────────────────────────────────────────

Note: This override will be logged in your audit trail and may
be reviewed by compliance officers or legal teams.
```

---

## 4. Post-Override Confirmation

### Success Message
```
✅ Override Approved

Your query has been rerun with ALL agents, including:
  • DeepSeekCodeAgent (previously excluded)

New result:
  Confidence: 87 / 100 (+2 points improvement)

Your override has been logged:
  • Request ID: abc123def456
  • Justification: [your justification text]
  • Timestamp: 2025-11-01 12:45:00 UTC
  • Audit trail: [Download JSON]

───────────────────────────────────────────────────────────────

⚠️  REMINDER:

You have accepted liability for this result. Ensure you:
  • Verify compliance with your use case
  • Do not violate platform Terms of Service
  • Use discovered information ethically and legally

[ View Full Audit Trail ]    [ Close ]
```

---

## 5. Regional Default Notifications

### EU Users (on first login)
```
┌─────────────────────────────────────────────────────────────┐
│ 🇪🇺 EU Region Detected                                       │
│                                                              │
│ Your account has been set to STRICT ethics profile by       │
│ default to ensure GDPR compliance.                          │
│                                                              │
│ This profile:                                                │
│  • Prioritizes data minimization                            │
│  • Requires explicit consent tracking                       │
│  • Blocks privacy-invasive strategies                       │
│  • Enables right-to-be-forgotten                            │
│                                                              │
│ You can change this in Settings if your use case differs.   │
│                                                              │
│ [ Understood ]            [ Change to Moderate ]            │
└─────────────────────────────────────────────────────────────┘
```

### CN Users (on first login)
```
┌─────────────────────────────────────────────────────────────┐
│ 🇨🇳 China Region Detected                                    │
│                                                              │
│ Your account has been set to MODERATE ethics profile with   │
│ local LLM preferences enabled.                              │
│                                                              │
│ This profile:                                                │
│  • Includes Chinese-developed LLMs (DeepSeek, Qwen)         │
│  • Weights local perspectives higher                        │
│  • Balances performance and oversight                       │
│  • Respects regional cultural context                       │
│                                                              │
│ You can change this in Settings if your use case differs.   │
│                                                              │
│ [ Understood ]            [ Change to Strict ]              │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Settings Page - Ethics Profile Management

### Header
```
Ethics & Compliance Settings
```

### Current Profile
```
Your Current Profile: MODERATE ✓

Last changed: 2025-10-15 by user@example.com
Queries using this profile: 1,247
Average performance: 78.5 / 100
Override rate: 8.2%

[ Change Profile ]
```

### Custom Profile Builder
```
───────────────────────────────────────────────────────────────

CREATE CUSTOM PROFILE

Start from: [ Moderate ▾ ]

Strategy Overrides:
  + Add strategy override

Agent Overrides:
  + Add agent override

Justification (required):
┌─────────────────────────────────────────────────────────────┐
│ [Document why you need a custom profile]                    │
└─────────────────────────────────────────────────────────────┘

[ Save Custom Profile ]

───────────────────────────────────────────────────────────────

⚠️  Custom profiles require documentation and may be reviewed
    by compliance officers.
```

---

## 7. Legal Footer (on all pages)

```
InfraFabric Ethics Disclaimer

By using InfraFabric, you agree to:
• Use discovered information only for lawful purposes
• Respect privacy and consent of individuals
• Comply with platform Terms of Service
• Not use for harassment, stalking, or unauthorized access

InfraFabric provides tools but does not control your use of
results. You are solely responsible for legal and ethical
compliance.

Full Terms of Service: [link]
Privacy Policy: [link]
Ethics Framework: [link]
```

---

## 8. Microcopy Guidelines

### Tone
- **Clear:** No jargon, explain ethics concepts simply
- **Respectful:** Assume users are acting in good faith
- **Firm:** Don't soften liability warnings
- **Empowering:** Give users control + information to choose

### Voice
- Active voice: "You accept liability" not "Liability is accepted"
- Direct: "This may violate ToS" not "This could potentially..."
- Human: "We built this to help you" not "The system has been designed"

### Warnings
- Use ⚠️ emoji for visual weight
- Red text for critical warnings
- Bold for key legal terms (LIABILITY, DISCLAIMS, ACCEPTS)
- Checkboxes for acknowledgments (can't proceed without checking)

---

## 9. Accessibility Notes

- All consent forms must be keyboard-navigable
- Screen reader labels for all checkboxes
- Color contrast meets WCAG AAA standards
- Text resizable to 200% without layout break
- Alt text for all warning icons
- Focus indicators clearly visible

---

## 10. Translation Considerations

Priority languages for liability waiver:
1. English (default)
2. Chinese (Simplified) - for CN users
3. German - for EU GDPR contexts
4. French - for EU GDPR contexts
5. Arabic - for UAE users

Legal review required for all translations.

---

**Status:** Ready for legal review and UX testing
**Next Steps:** Legal team approval + A/B testing consent rates
**Owner:** Legal + Product
