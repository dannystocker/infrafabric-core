"""
Cost monitoring test fixtures for IF.witness budget alerts

Provides pre-built scenarios for testing cost monitoring and budget alerts.
"""

from datetime import datetime, timedelta
from typing import Dict, List
from src.witness.models import Cost


def get_budget_scenarios() -> Dict[str, Dict]:
    """
    Get predefined budget scenarios for testing

    Returns:
        Dict mapping scenario name to config with budgets and expected alerts
    """
    return {
        'safe': {
            'description': 'Well under budget',
            'budgets': {'daily': 10.0, 'weekly': 50.0, 'monthly': 200.0},
            'actual_costs': {'daily': 2.5, 'weekly': 12.0, 'monthly': 45.0},
            'expected_alerts': []
        },
        'warning': {
            'description': '75% of daily budget used',
            'budgets': {'daily': 10.0, 'weekly': 50.0, 'monthly': 200.0},
            'actual_costs': {'daily': 7.5, 'weekly': 30.0, 'monthly': 120.0},
            'expected_alerts': ['daily_warning_75']
        },
        'critical': {
            'description': '90% of weekly budget used',
            'budgets': {'daily': 10.0, 'weekly': 50.0, 'monthly': 200.0},
            'actual_costs': {'daily': 8.0, 'weekly': 45.0, 'monthly': 150.0},
            'expected_alerts': ['daily_critical_90', 'weekly_critical_90']
        },
        'exceeded': {
            'description': 'Budget exceeded',
            'budgets': {'daily': 10.0, 'weekly': 50.0, 'monthly': 200.0},
            'actual_costs': {'daily': 12.0, 'weekly': 55.0, 'monthly': 210.0},
            'expected_alerts': ['daily_exceeded', 'weekly_exceeded', 'monthly_exceeded']
        },
        'per_component': {
            'description': 'Component-specific budget limits',
            'budgets': {
                'daily': 20.0,
                'components': {
                    'IF.ndi': 5.0,
                    'IF.webrtc': 7.5,
                    'IF.h323': 4.0,
                    'IF.sip': 3.5
                }
            },
            'actual_costs': {
                'IF.ndi': 4.5,      # Safe
                'IF.webrtc': 8.0,   # Exceeded
                'IF.h323': 3.0,     # Safe
                'IF.sip': 3.2       # Safe
            },
            'expected_alerts': ['component_webrtc_exceeded']
        }
    }


def get_cost_timeline(scenario: str = 'gradual_increase') -> List[Dict]:
    """
    Get time-series cost data for testing monitoring over time

    Args:
        scenario: Timeline scenario name

    Returns:
        List of cost events with timestamps
    """
    now = datetime.utcnow()

    scenarios = {
        'gradual_increase': [
            {'timestamp': now - timedelta(hours=23), 'cost': 0.5, 'component': 'IF.ndi'},
            {'timestamp': now - timedelta(hours=20), 'cost': 1.0, 'component': 'IF.webrtc'},
            {'timestamp': now - timedelta(hours=17), 'cost': 1.5, 'component': 'IF.h323'},
            {'timestamp': now - timedelta(hours=14), 'cost': 2.0, 'component': 'IF.sip'},
            {'timestamp': now - timedelta(hours=11), 'cost': 2.5, 'component': 'IF.ndi'},
            {'timestamp': now - timedelta(hours=8), 'cost': 3.0, 'component': 'IF.webrtc'},
            {'timestamp': now - timedelta(hours=5), 'cost': 3.5, 'component': 'IF.h323'},
            {'timestamp': now - timedelta(hours=2), 'cost': 4.0, 'component': 'IF.sip'},
        ],
        'spike': [
            {'timestamp': now - timedelta(hours=23), 'cost': 0.1, 'component': 'IF.ndi'},
            {'timestamp': now - timedelta(hours=22), 'cost': 0.1, 'component': 'IF.webrtc'},
            {'timestamp': now - timedelta(hours=21), 'cost': 0.1, 'component': 'IF.h323'},
            {'timestamp': now - timedelta(hours=2), 'cost': 8.0, 'component': 'IF.sip'},  # Spike!
            {'timestamp': now - timedelta(hours=1), 'cost': 0.1, 'component': 'IF.ndi'},
        ],
        'steady': [
            {'timestamp': now - timedelta(hours=i), 'cost': 0.5, 'component': f'IF.session{i%4+1}'}
            for i in range(24)
        ]
    }

    return scenarios.get(scenario, scenarios['gradual_increase'])


def get_alert_configs() -> List[Dict]:
    """
    Get sample alert configurations for testing

    Returns:
        List of alert rule configurations
    """
    return [
        {
            'name': 'daily_warning_50',
            'threshold': 5.0,  # 50% of $10 daily budget
            'period': 'day',
            'action': 'print',
            'message': 'Daily budget 50% used'
        },
        {
            'name': 'daily_warning_75',
            'threshold': 7.5,  # 75% of $10 daily budget
            'period': 'day',
            'action': 'log',
            'message': 'Daily budget 75% used - WARNING'
        },
        {
            'name': 'daily_critical_90',
            'threshold': 9.0,  # 90% of $10 daily budget
            'period': 'day',
            'action': 'print',
            'message': 'Daily budget 90% used - CRITICAL'
        },
        {
            'name': 'weekly_warning_75',
            'threshold': 37.5,  # 75% of $50 weekly budget
            'period': 'week',
            'action': 'log',
            'message': 'Weekly budget 75% used'
        },
        {
            'name': 'weekly_critical_90',
            'threshold': 45.0,  # 90% of $50 weekly budget
            'period': 'week',
            'action': 'print',
            'message': 'Weekly budget 90% used - CRITICAL'
        },
        {
            'name': 'monthly_exceeded',
            'threshold': 200.0,  # 100% of $200 monthly budget
            'period': 'month',
            'action': 'print',
            'message': 'Monthly budget EXCEEDED'
        }
    ]


def get_model_cost_samples() -> List[Cost]:
    """
    Get sample Cost objects for different models

    Returns:
        List of Cost objects with realistic token counts
    """
    return [
        # Claude Haiku (cheap, fast)
        Cost(tokens_in=100, tokens_out=50, cost_usd=0.000031, model='claude-haiku-4.5'),
        Cost(tokens_in=500, tokens_out=200, cost_usd=0.000175, model='claude-haiku-4.5'),
        Cost(tokens_in=1000, tokens_out=500, cost_usd=0.000375, model='claude-haiku-4.5'),

        # Claude Sonnet (balanced)
        Cost(tokens_in=100, tokens_out=50, cost_usd=0.0012, model='claude-sonnet-4.5'),
        Cost(tokens_in=500, tokens_out=200, cost_usd=0.0045, model='claude-sonnet-4.5'),
        Cost(tokens_in=1000, tokens_out=500, cost_usd=0.0105, model='claude-sonnet-4.5'),

        # GPT-5 (expensive)
        Cost(tokens_in=100, tokens_out=50, cost_usd=0.0125, model='gpt-5'),
        Cost(tokens_in=500, tokens_out=200, cost_usd=0.055, model='gpt-5'),
        Cost(tokens_in=1000, tokens_out=500, cost_usd=0.125, model='gpt-5'),

        # Gemini (mid-range)
        Cost(tokens_in=100, tokens_out=50, cost_usd=0.00006, model='gemini-2.5-pro'),
        Cost(tokens_in=500, tokens_out=200, cost_usd=0.0003, model='gemini-2.5-pro'),
        Cost(tokens_in=1000, tokens_out=500, cost_usd=0.0011, model='gemini-2.5-pro'),
    ]


def get_threshold_test_data() -> List[Dict]:
    """
    Get test data for threshold crossing scenarios

    Returns:
        List of scenarios testing threshold crossings
    """
    return [
        {
            'scenario': 'approaching_50',
            'budget': 10.0,
            'costs': [1.0, 2.0, 3.0, 4.5],  # Approaching 50%
            'expected_triggered': False
        },
        {
            'scenario': 'crossing_50',
            'budget': 10.0,
            'costs': [1.0, 2.0, 3.0, 5.5],  # Crosses 50%
            'expected_triggered': True,
            'expected_level': 'INFO'
        },
        {
            'scenario': 'crossing_75',
            'budget': 10.0,
            'costs': [1.0, 2.0, 3.0, 5.0, 7.6],  # Crosses 75%
            'expected_triggered': True,
            'expected_level': 'WARNING'
        },
        {
            'scenario': 'crossing_90',
            'budget': 10.0,
            'costs': [1.0, 2.0, 3.0, 5.0, 9.5],  # Crosses 90%
            'expected_triggered': True,
            'expected_level': 'CRITICAL'
        },
        {
            'scenario': 'exceeding_100',
            'budget': 10.0,
            'costs': [1.0, 2.0, 3.0, 5.0, 12.0],  # Exceeds 100%
            'expected_triggered': True,
            'expected_level': 'EXCEEDED'
        }
    ]


def get_suppression_test_data() -> Dict:
    """
    Get test data for alert suppression (avoiding spam)

    Returns:
        Dict with suppression test scenarios
    """
    now = datetime.utcnow()

    return {
        'rapid_fire': {
            'description': 'Multiple budget checks within suppression window',
            'checks': [
                {'time': now, 'cost': 9.0, 'should_alert': True},
                {'time': now + timedelta(minutes=5), 'cost': 9.1, 'should_alert': False},  # Suppressed
                {'time': now + timedelta(minutes=10), 'cost': 9.2, 'should_alert': False},  # Suppressed
                {'time': now + timedelta(minutes=35), 'cost': 9.3, 'should_alert': True},  # After cooldown
            ],
            'suppression_window': 30  # minutes
        },
        'escalation': {
            'description': 'Cost increases trigger higher severity alerts',
            'checks': [
                {'time': now, 'cost': 7.5, 'should_alert': True, 'expected_level': 'WARNING'},
                {'time': now + timedelta(minutes=35), 'cost': 9.0, 'should_alert': True, 'expected_level': 'CRITICAL'},
                {'time': now + timedelta(minutes=70), 'cost': 11.0, 'should_alert': True, 'expected_level': 'EXCEEDED'},
            ],
            'suppression_window': 30
        }
    }


def create_cost_test_database(db_path: str, scenario: str = 'gradual_increase'):
    """
    Create a test database populated with cost timeline data

    Args:
        db_path: Path to database file
        scenario: Timeline scenario to use

    Returns:
        WitnessDatabase instance with test data
    """
    from pathlib import Path
    from src.witness.database import WitnessDatabase
    from src.witness.crypto import WitnessCrypto

    # Create database
    key_path = Path(db_path).parent / 'test_key.pem'
    crypto = WitnessCrypto(key_path)
    db = WitnessDatabase(db_path, crypto)

    # Get timeline data
    timeline = get_cost_timeline(scenario)
    model_costs = get_model_cost_samples()

    # Insert events
    for i, event_data in enumerate(timeline):
        cost_sample = model_costs[i % len(model_costs)]

        db.create_entry(
            event=f"test_event_{i}",
            component=event_data['component'],
            trace_id=f"cost-test-{scenario}",
            payload={'scenario': scenario, 'index': i},
            cost=Cost(
                tokens_in=cost_sample.tokens_in,
                tokens_out=cost_sample.tokens_out,
                cost_usd=event_data['cost'],  # Use timeline cost
                model=cost_sample.model
            )
        )

    return db
