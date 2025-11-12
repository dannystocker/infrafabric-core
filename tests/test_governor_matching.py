"""Unit tests for IF.governor capability matching (P0.2.2)

Tests 70%+ capability matching algorithm:
- Capability overlap scoring (Jaccard similarity)
- 70% threshold enforcement
- Combined scoring: (capability × reputation) / cost
- Best swarm selection
- Budget and availability filtering
"""

import pytest
from infrafabric.governor import IFGovernor
from infrafabric.schemas.capability import (
    SwarmProfile,
    ResourcePolicy,
    Capability,
    calculate_jaccard_similarity,
    calculate_capability_overlap,
)
from infrafabric import witness, optimise


@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset global state before each test"""
    witness.clear_operations()
    optimise.clear_cost_records()
    yield
    witness.clear_operations()
    optimise.clear_cost_records()


@pytest.fixture
def governor():
    """Create IF.governor instance with standard policy"""
    policy = ResourcePolicy(
        max_cost_per_task=20.0,
        min_capability_match=0.7,  # 70% threshold
    )
    return IFGovernor(coordinator=None, policy=policy)


def test_calculate_jaccard_similarity():
    """Test Jaccard similarity calculation"""
    caps_a = [Capability.CODE_ANALYSIS_PYTHON, Capability.CODE_ANALYSIS_GO]
    caps_b = [Capability.CODE_ANALYSIS_PYTHON, Capability.CODE_ANALYSIS_RUST]

    # Intersection: {PYTHON} = 1
    # Union: {PYTHON, GO, RUST} = 3
    # Similarity: 1/3 = 0.333...
    similarity = calculate_jaccard_similarity(caps_a, caps_b)
    assert 0.33 < similarity < 0.34


def test_calculate_jaccard_similarity_perfect_match():
    """Test Jaccard similarity with perfect match"""
    caps = [Capability.CODE_ANALYSIS_PYTHON, Capability.INFRA_DISTRIBUTED_SYSTEMS]

    similarity = calculate_jaccard_similarity(caps, caps)
    assert similarity == 1.0


def test_calculate_jaccard_similarity_no_overlap():
    """Test Jaccard similarity with no overlap"""
    caps_a = [Capability.CODE_ANALYSIS_PYTHON]
    caps_b = [Capability.INTEGRATION_SIP]

    similarity = calculate_jaccard_similarity(caps_a, caps_b)
    assert similarity == 0.0


def test_calculate_capability_overlap():
    """Test capability overlap calculation"""
    required = [
        Capability.CODE_ANALYSIS_PYTHON,
        Capability.INFRA_DISTRIBUTED_SYSTEMS,
        Capability.TESTING_UNIT
    ]
    available = [
        Capability.CODE_ANALYSIS_PYTHON,
        Capability.INFRA_DISTRIBUTED_SYSTEMS,
        Capability.DOCS_TECHNICAL_WRITING
    ]

    # Intersection: {PYTHON, DISTRIBUTED_SYSTEMS} = 2
    # Required: 3
    # Overlap: 2/3 = 0.666...
    overlap = calculate_capability_overlap(required, available)
    assert 0.66 < overlap < 0.67


def test_calculate_capability_overlap_full():
    """Test capability overlap with full coverage"""
    required = [Capability.CODE_ANALYSIS_PYTHON]
    available = [
        Capability.CODE_ANALYSIS_PYTHON,
        Capability.CODE_ANALYSIS_GO,
        Capability.TESTING_UNIT
    ]

    overlap = calculate_capability_overlap(required, available)
    assert overlap == 1.0


def test_find_qualified_swarm_exact_match(governor):
    """Test finding swarm with exact capability match"""
    # Register swarm with exact capabilities
    profile = SwarmProfile(
        swarm_id='session-7-exact',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=15.0,
        reputation_score=0.95,
        current_budget_remaining=100.0,
    )
    governor.register_swarm(profile)

    # Find swarm
    swarm = governor.find_qualified_swarm(
        required_capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        max_cost=20.0
    )

    assert swarm == 'session-7-exact'


def test_find_qualified_swarm_above_70_percent(governor):
    """Test finding swarm with >70% capability match"""
    # Swarm has 3 capabilities, 2 match requirements
    profile = SwarmProfile(
        swarm_id='session-7-match',
        capabilities=[
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.INFRA_DISTRIBUTED_SYSTEMS,
            Capability.DOCS_TECHNICAL_WRITING,
        ],
        cost_per_hour=15.0,
        reputation_score=0.95,
        current_budget_remaining=100.0,
    )
    governor.register_swarm(profile)

    # Require 2 capabilities, swarm has both (100% overlap)
    swarm = governor.find_qualified_swarm(
        required_capabilities=[
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.INFRA_DISTRIBUTED_SYSTEMS,
        ],
        max_cost=20.0
    )

    assert swarm == 'session-7-match'


def test_find_qualified_swarm_below_70_percent_rejected(governor):
    """Test swarm with <70% capability match is rejected"""
    # Swarm has 1 out of 3 required capabilities (33% < 70%)
    profile = SwarmProfile(
        swarm_id='session-low-match',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=15.0,
        reputation_score=0.95,
        current_budget_remaining=100.0,
    )
    governor.register_swarm(profile)

    # Require 3 capabilities, swarm has only 1 (33% overlap)
    swarm = governor.find_qualified_swarm(
        required_capabilities=[
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.INFRA_DISTRIBUTED_SYSTEMS,
            Capability.TESTING_UNIT,
        ],
        max_cost=20.0
    )

    assert swarm is None


def test_find_qualified_swarm_chooses_higher_reputation(governor):
    """Test that higher reputation swarm is preferred"""
    # Swarm 1: High reputation
    profile1 = SwarmProfile(
        swarm_id='session-high-rep',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=15.0,
        reputation_score=0.95,
        current_budget_remaining=100.0,
    )

    # Swarm 2: Low reputation, same capabilities and cost
    profile2 = SwarmProfile(
        swarm_id='session-low-rep',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=15.0,
        reputation_score=0.50,
        current_budget_remaining=100.0,
    )

    governor.register_swarm(profile1)
    governor.register_swarm(profile2)

    swarm = governor.find_qualified_swarm(
        required_capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        max_cost=20.0
    )

    # Score = (capability × reputation) / cost
    # High rep: (1.0 × 0.95) / 15 = 0.0633
    # Low rep: (1.0 × 0.50) / 15 = 0.0333
    assert swarm == 'session-high-rep'


def test_find_qualified_swarm_chooses_lower_cost(governor):
    """Test that lower cost swarm is preferred when capabilities equal"""
    # Swarm 1: Cheap (Haiku)
    profile1 = SwarmProfile(
        swarm_id='session-cheap',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=2.0,
        reputation_score=0.90,
        current_budget_remaining=100.0,
        model='haiku',
    )

    # Swarm 2: Expensive (Sonnet), same capabilities and reputation
    profile2 = SwarmProfile(
        swarm_id='session-expensive',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=15.0,
        reputation_score=0.90,
        current_budget_remaining=100.0,
        model='sonnet',
    )

    governor.register_swarm(profile1)
    governor.register_swarm(profile2)

    swarm = governor.find_qualified_swarm(
        required_capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        max_cost=20.0
    )

    # Score = (capability × reputation) / cost
    # Cheap: (1.0 × 0.90) / 2 = 0.45
    # Expensive: (1.0 × 0.90) / 15 = 0.06
    assert swarm == 'session-cheap'


def test_find_qualified_swarm_too_expensive(governor):
    """Test swarm exceeding max_cost is rejected"""
    profile = SwarmProfile(
        swarm_id='session-expensive',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=25.0,  # Exceeds max_cost of 20
        reputation_score=0.95,
        current_budget_remaining=100.0,
    )
    governor.register_swarm(profile)

    swarm = governor.find_qualified_swarm(
        required_capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        max_cost=20.0
    )

    assert swarm is None


def test_find_qualified_swarm_budget_exhausted(governor):
    """Test swarm with zero budget is rejected"""
    profile = SwarmProfile(
        swarm_id='session-broke',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=15.0,
        reputation_score=0.95,
        current_budget_remaining=0.0,  # Budget exhausted
    )
    governor.register_swarm(profile)

    swarm = governor.find_qualified_swarm(
        required_capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        max_cost=20.0
    )

    assert swarm is None


def test_find_qualified_swarm_circuit_breaker_tripped(governor):
    """Test swarm with tripped circuit breaker is rejected"""
    profile = SwarmProfile(
        swarm_id='session-tripped',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=15.0,
        reputation_score=0.95,
        current_budget_remaining=100.0,
    )
    governor.register_swarm(profile)

    # Trip circuit breaker
    governor._circuit_breakers['session-tripped'] = True

    swarm = governor.find_qualified_swarm(
        required_capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        max_cost=20.0
    )

    assert swarm is None


def test_find_qualified_swarm_combined_scoring(governor):
    """Test combined scoring algorithm"""
    # Swarm 1: Perfect capability match, high cost
    profile1 = SwarmProfile(
        swarm_id='session-perfect',
        capabilities=[
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.INFRA_DISTRIBUTED_SYSTEMS,
        ],
        cost_per_hour=20.0,
        reputation_score=0.95,
        current_budget_remaining=100.0,
    )

    # Swarm 2: Partial capability match (75%), low cost
    profile2 = SwarmProfile(
        swarm_id='session-partial',
        capabilities=[
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.INFRA_DISTRIBUTED_SYSTEMS,
            Capability.TESTING_UNIT,
            Capability.DOCS_TECHNICAL_WRITING,
        ],
        cost_per_hour=5.0,
        reputation_score=0.90,
        current_budget_remaining=100.0,
    )

    governor.register_swarm(profile1)
    governor.register_swarm(profile2)

    required = [
        Capability.CODE_ANALYSIS_PYTHON,
        Capability.INFRA_DISTRIBUTED_SYSTEMS,
    ]

    swarm = governor.find_qualified_swarm(
        required_capabilities=required,
        max_cost=25.0
    )

    # Calculate scores:
    # Perfect: (1.0 × 0.95) / 20 = 0.0475
    # Partial: (1.0 × 0.90) / 5 = 0.18
    # Partial wins despite having extra capabilities
    assert swarm == 'session-partial'


def test_find_qualified_swarm_logs_to_witness(governor):
    """Test that successful match is logged to witness"""
    profile = SwarmProfile(
        swarm_id='session-7-test',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=15.0,
        reputation_score=0.95,
        current_budget_remaining=100.0,
    )
    governor.register_swarm(profile)

    swarm = governor.find_qualified_swarm(
        required_capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        max_cost=20.0
    )

    assert swarm == 'session-7-test'

    # Check witness logging
    ops = witness.get_operations(component='IF.governor', operation='swarm_matched')
    assert len(ops) == 1
    assert ops[0].params['matched_swarm'] == 'session-7-test'
    assert 'score' in ops[0].params
    assert 'capability_overlap' in ops[0].params


def test_find_qualified_swarm_multiple_candidates(governor):
    """Test selection from multiple qualified candidates"""
    # Register 5 different swarms with varying characteristics
    swarms = [
        ('session-1', [Capability.INTEGRATION_NDI], 2.0, 0.85),  # Haiku, no match
        ('session-4', [Capability.CODE_ANALYSIS_PYTHON], 2.0, 0.90),  # Haiku, match
        ('session-7', [Capability.CODE_ANALYSIS_PYTHON, Capability.INFRA_DISTRIBUTED_SYSTEMS], 15.0, 0.95),  # Sonnet, match
        ('session-2', [Capability.INTEGRATION_WEBRTC], 2.0, 0.88),  # Haiku, no match
        ('session-5', [Capability.CODE_ANALYSIS_PYTHON], 15.0, 0.92),  # Sonnet, match
    ]

    for swarm_id, capabilities, cost, reputation in swarms:
        profile = SwarmProfile(
            swarm_id=swarm_id,
            capabilities=capabilities,
            cost_per_hour=cost,
            reputation_score=reputation,
            current_budget_remaining=100.0,
        )
        governor.register_swarm(profile)

    swarm = governor.find_qualified_swarm(
        required_capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        max_cost=20.0
    )

    # Calculate scores for matching swarms:
    # session-4: (1.0 × 0.90) / 2 = 0.45
    # session-7: (1.0 × 0.95) / 15 = 0.0633
    # session-5: (1.0 × 0.92) / 15 = 0.0613
    # session-4 should win (highest score)
    assert swarm == 'session-4'


def test_find_qualified_swarm_no_candidates(governor):
    """Test when no swarms are qualified"""
    # Register swarms that don't match
    profile1 = SwarmProfile(
        swarm_id='session-1',
        capabilities=[Capability.INTEGRATION_NDI],
        cost_per_hour=2.0,
        reputation_score=0.90,
        current_budget_remaining=100.0,
    )
    profile2 = SwarmProfile(
        swarm_id='session-2',
        capabilities=[Capability.INTEGRATION_WEBRTC],
        cost_per_hour=2.0,
        reputation_score=0.90,
        current_budget_remaining=100.0,
    )

    governor.register_swarm(profile1)
    governor.register_swarm(profile2)

    swarm = governor.find_qualified_swarm(
        required_capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        max_cost=20.0
    )

    assert swarm is None


def test_policy_min_capability_match_configurable(governor):
    """Test that policy min_capability_match is configurable"""
    # Create policy with 80% threshold
    policy = ResourcePolicy(min_capability_match=0.8)
    gov = IFGovernor(coordinator=None, policy=policy)

    # Swarm has 75% match (would pass 70% but not 80%)
    profile = SwarmProfile(
        swarm_id='session-test',
        capabilities=[
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.INFRA_DISTRIBUTED_SYSTEMS,
            Capability.TESTING_UNIT,
        ],
        cost_per_hour=15.0,
        reputation_score=0.95,
        current_budget_remaining=100.0,
    )
    gov.register_swarm(profile)

    # Require 4 capabilities, swarm has 3 (75% overlap)
    swarm = gov.find_qualified_swarm(
        required_capabilities=[
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.INFRA_DISTRIBUTED_SYSTEMS,
            Capability.TESTING_UNIT,
            Capability.DOCS_TECHNICAL_WRITING,
        ],
        max_cost=20.0
    )

    # 75% < 80% threshold, should be rejected
    assert swarm is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
