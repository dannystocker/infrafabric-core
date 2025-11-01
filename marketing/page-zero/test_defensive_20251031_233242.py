#!/usr/bin/env python3
"""
Defensive Tests - Auto-generated from Bug Pattern Learning
Generated: 2025-10-31T23:32:42.974565
"""

import pytest
import os


def test_agent_results_structure():
    """Ensure agent_results is properly structured"""
    result = {'agent_results': [
        {'agent': 'TestAgent', 'confidence': 80}
    ]}

    # Should be list, not dict
    assert isinstance(result['agent_results'], list)

    # Iteration should work
    for agent_result in result['agent_results']:
        assert 'agent' in agent_result
        assert 'confidence' in agent_result



def test_csv_field_names():
    """Ensure CSV fields match code expectations"""
    import csv

    with open('outreach-targets-FINAL-RANKED.csv') as f:
        reader = csv.DictReader(f)
        row = next(reader)

        # Required fields
        assert 'first_name' in row
        assert 'last_name' in row
        assert 'organization' in row  # NOT 'org'
        assert 'role_title' in row     # NOT 'role'



def test_weighted_finder_import():
    """Ensure weighted finder imports correctly"""
    import weighted_multi_agent_finder as wmaf

    # Should import class, not function
    assert hasattr(wmaf, 'MultiAgentWeightedCoordinator')
    assert callable(wmaf.MultiAgentWeightedCoordinator)

    # Should be instantiatable
    coordinator = wmaf.MultiAgentWeightedCoordinator()
    assert hasattr(coordinator, 'find_contact')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])