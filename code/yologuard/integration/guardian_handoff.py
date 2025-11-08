#!/usr/bin/env python3
"""
IF.yologuard Guardian Handoff

Prepares a proposal and submits it to the IF Guardians for a weighted debate
decision. Saves the result to JSON for audit.

Usage:
  python3 infrafabric/code/yologuard/integration/guardian_handoff.py
"""
from pathlib import Path
import json

import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from infrafabric import guardians as IFG


def main():
    proposal = {
        'title': 'IF.yologuard v3.1 – IEF + TTT + PQ (Immuno-Epistemic Forensics)',
        'description': (
            'This release adds three major frameworks: (1) Immuno-Epistemic Forensics (IEF) with danger signals, '
            'structure checks, APC packets, and Indra graph; (2) TTT (Traceability•Trust•Transparency) with '
            'provenance tracking, rationale capture, and audit manifests; (3) Quantum Readiness (PQ) analysis '
            'with classical crypto detection, QES scoring, and SBOM integration. It introduces audience profiles '
            '(ci/ops/audit/research/forensics) for graduated security posture, maintains reproducible benchmarks '
            '(107/96 component, 95/96 usable), and provides forensics-grade outputs for incident response.'
        ),
        'benefits': [
            'IEF Layer: Danger signals (encoded_blob, honeypot), structure checks (JWT/PEM), Indra graph',
            'TTT Framework: Per-detection provenance (commit/SHA256/timestamp) + rationale + manifests',
            'Quantum Readiness: PQ analysis, QES per detection, classical crypto detection, repo-level reports',
            'Profiles: ci/ops/audit/research/forensics with graduated thresholds (error 0.80→0.65, warn 0.60→0.45)',
            'Reproducible: 107/96 component (111.5%), 95/96 usable (98.96%), 42/42 coverage, 0 FP on falsifiers',
            'SARIF v2.1.0 + JSON + Graph outputs with provenance/rationale for CI/CD + compliance',
            'Wu Lun 兄弟 (metadata-sibling) relationship detection implemented',
            'Governance: TTT manifests support SOC2/ISO27001; weekly forensics audits proposed',
        ],
        'risks': [
            'Sensitivity/Noise: Forensics profile may surface too many signals for daily CI use',
            'Heuristic thresholds: QES and severity thresholds require empirical calibration (commitment: 2-4 weeks)',
            'Structure checks are pattern-based (not cryptographic validation); no live validation per Kantian duty',
            'PQ detection is string-based v1; SBOM assists but not exhaustive',
            'Cross-file relationships not yet implemented (single-file window only)',
        ],
        'safeguards': [
            'Kantian duty constraints: No live validation, no data exfiltration, always redact secrets',
            'Falsifier tests: UUIDs, SHAs, benign base64 → 0 detections',
            'CI gate: ≥95 detections + falsifiers pass before merge',
            'TTT manifests: Machine-readable, timestamped, suitable for evidence chains',
            'Profiles control noise: ci=usable-only+conservative; forensics=both+max sensitivity',
            'Two-source journalism: Gating logic captured in rationale field',
            'Guardian review: Required for all releases, with dissent window',
        ],
        'evidence': [
            'IEF implementation: code/yologuard/src/IF.yologuard_v3.py:257-690',
            'TTT framework: code/yologuard/src/IF.yologuard_v3.py:690-850',
            'PQ analysis: code/yologuard/src/IF.yologuard_v3.py:850-900',
            'Profiles: code/yologuard/src/IF.yologuard_v3.py:700-715',
            'Benchmark: code/yologuard/benchmarks/run_leaky_repo_v3_philosophical_fast_v2.py',
            'CI workflow: .github/workflows/yologuard-ci.yml',
            'Falsifiers: code/yologuard/tests/test_falsifiers.py',
            'Harness: code/yologuard/harness/{fp_eval.py,perf_bench.py,corpus_eval.py}',
            'Handoff doc: code/yologuard/integration/GUARDIAN_HANDOFF_v3.1_IEF.md',
            'Docs: code/yologuard/docs/{BENCHMARKS.md,COMPARISON.md}',
        ],
        'initial_metrics': {
            'leaky_repo_component': '107/96 (111.5%), 42/42 coverage',
            'leaky_repo_usable': '95/96 (98.96%)',
            'falsifiers': '0 FP on UUIDs/SHAs/benign base64',
            'performance': '~116 files/sec, ~3.55 MB/sec (infrafabric repo)',
            'corpus_survey': '349 files (2 repos), 73 detections, ~454 files/sec',
            'quantum': 'avg QES 26.7, 3 high-risk (QES ≥40) on Leaky Repo',
        },
        'roadmap_commitments': [
            'REQUIRED: Calibrate thresholds/QES with curated clean corpus within 2-4 weeks',
            'REQUIRED: User docs update for profiles/IEF/PQ (non-technical stakeholders)',
            '30-day retrospective on adoption, FP rates, governance policy effectiveness',
            'Enhanced IEF: stylometry, git history anomalies, relation triangle severity boosts (4-6 weeks)',
            'SBOM-aware PQ: version checks, dependency graph, library-level analysis (6-8 weeks)',
            'Cross-file relationships: env/config linking, template interpolation (8-10 weeks)',
        ],
        'governance_notes': [
            'IF.ceo strategic framework applied to positioning decisions',
            'Profiles enable graduated security posture across CI/ops/audit/forensics',
            'TTT manifests support SOC2/ISO27001 compliance with audit trails',
            'Proposed policy: CI gates block on ERROR (always-error + validated two-source); forensics weekly',
        ],
        'governance_policy': {
            'ci_gates': 'Block on ERROR (always-error patterns + validated two-source items); log WARN',
            'weekly_forensics': 'Profile=forensics; retain JSON/SARIF/graph/manifest for 1 year',
            'thresholds': 'ci: error=0.80/warn=0.60; forensics: error=0.65/warn=0.45',
            'quantum': 'Establish org QES threshold (e.g., avg ≤30); alert on new classical crypto in sensitive paths',
            'manifest_auditing': 'SOC2/ISO27001 auditors can request manifests by date range for compliance evidence',
        },
    }

    result = IFG.debate_proposal(proposal, proposal_type='technical', verbose=True)

    out = Path(__file__).with_name('guardian_handoff_result.json')
    with open(out, 'w') as f:
        json.dump(result.to_dict(), f, indent=2)
    print(f"Saved guardian decision to: {out}")


if __name__ == '__main__':
    main()
