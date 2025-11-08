# A6 CI Workflow Checklist

Branch: `swarm/w2-a6-ci-workflow`
PR: https://github.com/dannystocker/infrafabric/pull/new/swarm/w2-a6-ci-workflow

Steps:
1) Promote staged workflow
   - Move `docs/ci/review.yml` to `.github/workflows/review.yml` in the PR
   - Commit with message: `ci(workflow): enable review enforcement [SWARM:W2-A6]`
2) Validate on PR
   - Ensure workflow runs on `pull_request`
   - Confirms:
     - IFMessage samples: `messages/examples/*.json` validate against `schemas/ifmessage/v1.0.schema.json`
     - Decision example: `governance/examples/decision_example.json` validates against `schemas/decision/v1.0.schema.json`
3) Notes
   - Requires token with `workflow` scope
   - Evidence-binding: cite `path:line` in any doc changes

Artifacts:
- Schema: `schemas/ifmessage/v1.0.schema.json`
- Sample: `messages/examples/level1_example.json` (+ error/warn/level2 variants)
- Validator: `scripts/validate_message.py`
- Decision schema: `schemas/decision/v1.0.schema.json`
- Decision example: `governance/examples/decision_example.json`
