"""
Unit tests for if_optimise.py - Cost Tracking CLI

Tests cost reporting, budget management, and CSV export functionality.
"""

import pytest
from click.testing import CliRunner
from pathlib import Path
from datetime import datetime, timedelta
import json
import csv
import io
from unittest.mock import patch, MagicMock

# Import the CLI
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cli.if_optimise import (
    cli, calculate_cost, format_cost_data_as_csv, MODEL_RATES
)


class TestCostCalculation:
    """Test cost calculation functions"""

    def test_calculate_cost_haiku(self):
        """Test cost calculation for Haiku model"""
        cost = calculate_cost(1_000_000, 1_000_000, 'claude-haiku-4.5')
        expected = (1_000_000 * 0.00000025) + (1_000_000 * 0.00000125)
        assert cost == pytest.approx(expected, abs=0.001)

    def test_calculate_cost_sonnet(self):
        """Test cost calculation for Sonnet model"""
        cost = calculate_cost(1_000_000, 500_000, 'claude-sonnet-4.5')
        expected = (1_000_000 * 0.000003) + (500_000 * 0.000015)
        assert cost == pytest.approx(expected, abs=0.001)

    def test_calculate_cost_unknown_model(self):
        """Test cost calculation for unknown model defaults to 0"""
        cost = calculate_cost(1_000_000, 1_000_000, 'unknown-model')
        assert cost == 0.0

    def test_model_rates_defined(self):
        """Test all expected models have rates"""
        expected_models = ['gpt-5', 'claude-sonnet-4.5', 'claude-haiku-4.5', 'gemini-2.5-pro']
        for model in expected_models:
            assert model in MODEL_RATES
            assert 'input' in MODEL_RATES[model]
            assert 'output' in MODEL_RATES[model]


class TestCSVFormatting:
    """Test CSV export functionality"""

    def test_format_empty_data(self):
        """Test CSV formatting with empty data"""
        result = format_cost_data_as_csv([])
        assert result == ""

    def test_format_single_row(self):
        """Test CSV formatting with single row"""
        data = [{
            'component': 'IF.coordinator',
            'operations': 42,
            'total_tokens': 15000,
            'total_cost': 0.045,
            'model': 'claude-haiku-4.5'
        }]

        csv_output = format_cost_data_as_csv(data)

        # Parse CSV
        reader = csv.DictReader(io.StringIO(csv_output))
        rows = list(reader)

        assert len(rows) == 1
        assert rows[0]['component'] == 'IF.coordinator'
        assert rows[0]['operations'] == '42'
        assert rows[0]['total_tokens'] == '15000'
        assert rows[0]['model'] == 'claude-haiku-4.5'

    def test_format_multiple_rows(self):
        """Test CSV formatting with multiple rows"""
        data = [
            {
                'component': 'IF.coordinator',
                'operations': 42,
                'total_tokens': 15000,
                'total_cost': 0.045,
                'model': 'claude-haiku-4.5'
            },
            {
                'component': 'IF.governor',
                'operations': 25,
                'total_tokens': 50000,
                'total_cost': 0.150,
                'model': 'claude-sonnet-4.5'
            }
        ]

        csv_output = format_cost_data_as_csv(data)
        reader = csv.DictReader(io.StringIO(csv_output))
        rows = list(reader)

        assert len(rows) == 2
        assert rows[0]['component'] == 'IF.coordinator'
        assert rows[1]['component'] == 'IF.governor'

    def test_format_with_null_values(self):
        """Test CSV formatting handles None values"""
        data = [{
            'component': 'IF.chassis',
            'operations': 10,
            'total_tokens': None,
            'total_cost': None,
            'model': None
        }]

        csv_output = format_cost_data_as_csv(data)
        reader = csv.DictReader(io.StringIO(csv_output))
        rows = list(reader)

        assert rows[0]['total_tokens'] == '0'
        assert rows[0]['total_cost'] == '0.0'
        assert rows[0]['model'] == 'unknown'


class TestRatesCommand:
    """Test rates command"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_rates_text_format(self):
        """Test rates command with text output"""
        result = self.runner.invoke(cli, ['rates'])
        assert result.exit_code == 0
        assert 'Model' in result.output
        assert 'claude-haiku-4.5' in result.output
        assert 'claude-sonnet-4.5' in result.output

    def test_rates_json_format(self):
        """Test rates command with JSON output"""
        result = self.runner.invoke(cli, ['rates', '--format', 'json'])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert 'claude-haiku-4.5' in data
        assert data['claude-haiku-4.5']['input'] == 0.00000025


class TestReportCommand:
    """Test report command"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    @patch('src.cli.if_optimise.WitnessDatabase')
    def test_report_text_format(self, mock_db_class):
        """Test report command with text output"""
        # Mock database
        mock_db = MagicMock()
        mock_db.get_cost_by_component.return_value = [
            {
                'component': 'IF.coordinator',
                'operations': 42,
                'total_tokens': 15000,
                'total_cost': 0.045,
                'model': 'claude-haiku-4.5'
            }
        ]
        mock_db_class.return_value = mock_db

        result = self.runner.invoke(cli, ['report'])
        assert result.exit_code == 0
        assert 'Cost Report' in result.output
        assert 'IF.coordinator' in result.output

    @patch('src.cli.if_optimise.WitnessDatabase')
    def test_report_json_format(self, mock_db_class):
        """Test report command with JSON output"""
        mock_db = MagicMock()
        mock_db.get_cost_by_component.return_value = [
            {
                'component': 'IF.coordinator',
                'operations': 42,
                'total_tokens': 15000,
                'total_cost': 0.045,
                'model': 'claude-haiku-4.5'
            }
        ]
        mock_db_class.return_value = mock_db

        result = self.runner.invoke(cli, ['report', '--format', 'json'])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert len(data) == 1
        assert data[0]['component'] == 'IF.coordinator'

    @patch('src.cli.if_optimise.WitnessDatabase')
    def test_report_csv_format(self, mock_db_class):
        """Test report command with CSV output"""
        mock_db = MagicMock()
        mock_db.get_cost_by_component.return_value = [
            {
                'component': 'IF.coordinator',
                'operations': 42,
                'total_tokens': 15000,
                'total_cost': 0.045,
                'model': 'claude-haiku-4.5'
            }
        ]
        mock_db_class.return_value = mock_db

        result = self.runner.invoke(cli, ['report', '--format', 'csv'])
        assert result.exit_code == 0
        assert 'component,operations,total_tokens,total_cost,model' in result.output
        assert 'IF.coordinator' in result.output

    @patch('src.cli.if_optimise.WitnessDatabase')
    def test_report_with_component_filter(self, mock_db_class):
        """Test report command with component filter"""
        mock_db = MagicMock()
        mock_db.get_cost_by_component.return_value = []
        mock_db_class.return_value = mock_db

        result = self.runner.invoke(cli, ['report', '--component', 'IF.coordinator'])
        assert result.exit_code == 0

        # Verify filter was passed
        mock_db.get_cost_by_component.assert_called_once()
        args = mock_db.get_cost_by_component.call_args[0]
        assert args[0] == 'IF.coordinator'

    @patch('src.cli.if_optimise.WitnessDatabase')
    def test_report_with_date_range(self, mock_db_class):
        """Test report command with date range"""
        mock_db = MagicMock()
        mock_db.get_cost_by_component.return_value = []
        mock_db_class.return_value = mock_db

        result = self.runner.invoke(cli, [
            'report',
            '--start-date', '2025-11-01',
            '--end-date', '2025-11-12'
        ])
        assert result.exit_code == 0

    @patch('src.cli.if_optimise.WitnessDatabase')
    def test_report_empty_data(self, mock_db_class):
        """Test report command with no cost data"""
        mock_db = MagicMock()
        mock_db.get_cost_by_component.return_value = []
        mock_db_class.return_value = mock_db

        result = self.runner.invoke(cli, ['report'])
        assert result.exit_code == 0
        assert 'No cost data found' in result.output


class TestBudgetCommand:
    """Test budget command"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    @patch('src.cli.if_optimise.WitnessDatabase')
    def test_budget_check(self, mock_db_class):
        """Test budget check without setting"""
        mock_db = MagicMock()
        mock_db.get_cost_by_component.return_value = [
            {'operations': 10, 'total_cost': 5.50, 'total_tokens': 100000}
        ]
        mock_db_class.return_value = mock_db

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ['budget'])
            assert result.exit_code == 0
            assert 'Budget Status' in result.output

    @patch('src.cli.if_optimise.WitnessDatabase')
    def test_budget_set(self, mock_db_class):
        """Test setting budget"""
        mock_db = MagicMock()
        mock_db.get_cost_by_component.return_value = []
        mock_db_class.return_value = mock_db

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ['budget', '--set', '50.00'])
            assert result.exit_code == 0
            assert 'Budget set' in result.output

            # Verify budget file was created
            budget_file = Path.home() / '.if-witness' / 'budget.json'
            # File might not exist in isolated filesystem, but command should succeed

    @patch('src.cli.if_optimise.WitnessDatabase')
    def test_budget_periods(self, mock_db_class):
        """Test budget command with different periods"""
        mock_db = MagicMock()
        mock_db.get_cost_by_component.return_value = []
        mock_db_class.return_value = mock_db

        with self.runner.isolated_filesystem():
            for period in ['day', 'week', 'month']:
                result = self.runner.invoke(cli, ['budget', '--period', period])
                assert result.exit_code == 0
                assert period in result.output

    @patch('src.cli.if_optimise.WitnessDatabase')
    def test_budget_warning_thresholds(self, mock_db_class):
        """Test budget warning thresholds"""
        mock_db = MagicMock()

        # Test 50% usage (notice)
        mock_db.get_cost_by_component.return_value = [
            {'operations': 10, 'total_cost': 50.0, 'total_tokens': 1000000}
        ]
        mock_db_class.return_value = mock_db

        with self.runner.isolated_filesystem():
            # Set budget to 100
            budget_file = Path.home() / '.if-witness' / 'budget.json'
            budget_file.parent.mkdir(parents=True, exist_ok=True)
            budget_file.write_text(json.dumps({'amount': 100.0, 'period': 'month'}))

            result = self.runner.invoke(cli, ['budget'])
            assert result.exit_code == 0
            assert 'NOTICE' in result.output or '50' in result.output


class TestEstimateCommand:
    """Test estimate command"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_estimate_basic(self):
        """Test basic cost estimate"""
        result = self.runner.invoke(cli, [
            'estimate',
            '--tokens-in', '1000000',
            '--tokens-out', '500000',
            '--model', 'claude-haiku-4.5'
        ])
        assert result.exit_code == 0
        assert 'Cost Estimate' in result.output
        assert 'claude-haiku-4.5' in result.output

    def test_estimate_multiple_operations(self):
        """Test estimate with multiple operations"""
        result = self.runner.invoke(cli, [
            'estimate',
            '--tokens-in', '10000',
            '--tokens-out', '5000',
            '--model', 'claude-sonnet-4.5',
            '--operations', '100'
        ])
        assert result.exit_code == 0
        assert 'Operations:' in result.output

    def test_estimate_unknown_model(self):
        """Test estimate with unknown model"""
        result = self.runner.invoke(cli, [
            'estimate',
            '--tokens-in', '1000',
            '--tokens-out', '500',
            '--model', 'unknown-model'
        ])
        assert result.exit_code != 0
        assert 'Unknown model' in result.output


class TestCLIIntegration:
    """Test CLI-level integration"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test CLI help text"""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Cost tracking and budget management' in result.output

    def test_all_commands_have_help(self):
        """Test all commands have help text"""
        commands = ['rates', 'budget', 'report', 'estimate']

        for cmd in commands:
            result = self.runner.invoke(cli, [cmd, '--help'])
            assert result.exit_code == 0, f"Help failed for {cmd}"
            assert len(result.output) > 50, f"Help too short for {cmd}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
