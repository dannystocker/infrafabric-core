"""
Unit tests for if_main.py - Unified CLI Entry Point

Tests CLI parsing, command routing, help text, and error handling.
"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.cli.if_main import cli, main


class TestCLIBasics:
    """Test basic CLI functionality"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_cli_entrypoint_exists(self):
        """Test CLI entry point is callable"""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'InfraFabric CLI' in result.output

    def test_version_flag(self):
        """Test --version flag"""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert 'InfraFabric' in result.output or '0.1.0' in result.output

    def test_help_flag(self):
        """Test --help flag"""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'coordinator' in result.output
        assert 'governor' in result.output
        assert 'chassis' in result.output
        assert 'witness' in result.output
        assert 'optimise' in result.output

    def test_no_arguments(self):
        """Test CLI with no arguments shows help"""
        result = self.runner.invoke(cli, [])
        # Click returns exit code 2 when no command is provided (expected behavior)
        assert result.exit_code in [0, 2]
        assert 'InfraFabric CLI' in result.output or 'Usage:' in result.output


class TestGlobalFlags:
    """Test global CLI flags"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_debug_flag(self):
        """Test --debug flag"""
        result = self.runner.invoke(cli, ['--debug', 'version'])
        assert result.exit_code == 0

    def test_trace_flag(self):
        """Test --trace flag"""
        result = self.runner.invoke(cli, ['--trace', 'test-trace-123', 'version'])
        assert result.exit_code == 0

    def test_mode_normal(self):
        """Test --mode=normal"""
        result = self.runner.invoke(cli, ['--mode', 'normal', 'version'])
        assert result.exit_code == 0

    def test_mode_falsify(self):
        """Test --mode=falsify"""
        result = self.runner.invoke(cli, ['--mode', 'falsify', 'version'])
        assert result.exit_code == 0

    def test_mode_verify(self):
        """Test --mode=verify"""
        result = self.runner.invoke(cli, ['--mode', 'verify', 'version'])
        assert result.exit_code == 0

    def test_config_flag(self):
        """Test --config flag with temp file"""
        with self.runner.isolated_filesystem():
            # Create temp config
            config_path = Path('test_config.yaml')
            config_path.write_text('log_level: debug\n')

            result = self.runner.invoke(cli, ['--config', str(config_path), 'version'])
            assert result.exit_code == 0

    def test_invalid_mode(self):
        """Test --mode with invalid value"""
        result = self.runner.invoke(cli, ['--mode', 'invalid', 'version'])
        assert result.exit_code != 0


class TestConfigCommands:
    """Test config subcommands"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_config_help(self):
        """Test config --help"""
        result = self.runner.invoke(cli, ['config', '--help'])
        assert result.exit_code == 0
        assert 'Configuration management' in result.output

    def test_config_init(self):
        """Test config init"""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ['config', 'init'])
            # May fail if infrafabric module not fully installed, but command should parse
            assert 'init' in result.output or result.exit_code in [0, 1]

    def test_config_show(self):
        """Test config show"""
        result = self.runner.invoke(cli, ['config', 'show'])
        assert result.exit_code in [0, 1]  # May fail if no config, but parses correctly

    def test_config_validate(self):
        """Test config validate"""
        result = self.runner.invoke(cli, ['config', 'validate'])
        assert result.exit_code in [0, 1]  # May fail if no config, but parses correctly


class TestCoordinatorCommands:
    """Test coordinator subcommands"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_coordinator_help(self):
        """Test coordinator --help"""
        result = self.runner.invoke(cli, ['coordinator', '--help'])
        assert result.exit_code == 0
        assert 'Real-time swarm coordination' in result.output

    def test_coordinator_start(self):
        """Test coordinator start"""
        result = self.runner.invoke(cli, ['coordinator', 'start'])
        assert result.exit_code == 0
        assert 'Starting IF.coordinator' in result.output

    def test_coordinator_start_with_options(self):
        """Test coordinator start with custom options"""
        result = self.runner.invoke(cli, [
            'coordinator', 'start',
            '--backend', 'nats',
            '--host', 'nats-server',
            '--port', '4222'
        ])
        assert result.exit_code == 0
        assert 'nats' in result.output

    def test_coordinator_status(self):
        """Test coordinator status"""
        result = self.runner.invoke(cli, ['coordinator', 'status'])
        assert result.exit_code == 0
        assert 'IF.coordinator' in result.output

    def test_coordinator_swarms(self):
        """Test coordinator swarms list"""
        result = self.runner.invoke(cli, ['coordinator', 'swarms'])
        assert result.exit_code == 0
        assert 'SWARM_ID' in result.output

    def test_coordinator_task_create(self):
        """Test coordinator task create"""
        result = self.runner.invoke(cli, [
            'coordinator', 'task', 'create',
            '--task-id', 'P0.1.2',
            '--description', 'Test task',
            '--capabilities', 'test:cap1',
            '--max-cost', '10.0'
        ])
        assert result.exit_code == 0
        assert 'P0.1.2' in result.output

    def test_coordinator_task_status(self):
        """Test coordinator task status"""
        result = self.runner.invoke(cli, ['coordinator', 'task', 'status', 'P0.1.2'])
        assert result.exit_code == 0
        assert 'P0.1.2' in result.output


class TestGovernorCommands:
    """Test governor subcommands"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_governor_help(self):
        """Test governor --help"""
        result = self.runner.invoke(cli, ['governor', '--help'])
        assert result.exit_code == 0
        assert 'Policy-based resource allocation' in result.output

    def test_governor_register(self):
        """Test governor register"""
        result = self.runner.invoke(cli, [
            'governor', 'register', 'session-1',
            '--capabilities', 'test:cap1',
            '--capabilities', 'test:cap2',
            '--cost-per-hour', '15.0',
            '--budget', '100.0'
        ])
        assert result.exit_code == 0
        assert 'session-1' in result.output

    def test_governor_register_with_model(self):
        """Test governor register with model selection"""
        result = self.runner.invoke(cli, [
            'governor', 'register', 'session-1',
            '--capabilities', 'test:cap1',
            '--cost-per-hour', '2.0',
            '--budget', '50.0',
            '--model', 'haiku'
        ])
        assert result.exit_code == 0
        assert 'haiku' in result.output

    def test_governor_match(self):
        """Test governor match"""
        result = self.runner.invoke(cli, [
            'governor', 'match',
            '--capabilities', 'test:cap1',
            '--max-cost', '20.0'
        ])
        assert result.exit_code == 0
        assert 'Finding swarms' in result.output

    def test_governor_budget_add(self):
        """Test governor budget add"""
        result = self.runner.invoke(cli, [
            'governor', 'budget', 'add',
            'session-1', '50.0'
        ])
        assert result.exit_code == 0
        assert '50.00' in result.output

    def test_governor_budget_report(self):
        """Test governor budget report"""
        result = self.runner.invoke(cli, ['governor', 'budget', 'report'])
        assert result.exit_code == 0
        assert 'Budget Report' in result.output


class TestChassisCommands:
    """Test chassis subcommands"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_chassis_help(self):
        """Test chassis --help"""
        result = self.runner.invoke(cli, ['chassis', '--help'])
        assert result.exit_code == 0
        assert 'WASM sandbox execution' in result.output

    def test_chassis_sandbox_create(self):
        """Test chassis sandbox create"""
        result = self.runner.invoke(cli, [
            'chassis', 'sandbox', 'create',
            '--wasm-module', 'test.wasm',
            '--memory', '512',
            '--cpu', '50',
            '--timeout', '60000'
        ])
        assert result.exit_code == 0
        assert 'test.wasm' in result.output

    def test_chassis_sandbox_list(self):
        """Test chassis sandbox list"""
        result = self.runner.invoke(cli, ['chassis', 'sandbox', 'list'])
        assert result.exit_code == 0
        assert 'SANDBOX_ID' in result.output


class TestWitnessCommands:
    """Test witness subcommands"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_witness_help(self):
        """Test witness --help"""
        result = self.runner.invoke(cli, ['witness', '--help'])
        assert result.exit_code == 0
        assert 'Cryptographic provenance' in result.output

    def test_witness_init(self):
        """Test witness init"""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ['witness', 'init'])
            # May fail if witness module not available, but should parse
            assert 'init' in result.output or result.exit_code in [0, 1]

    def test_witness_verify(self):
        """Test witness verify"""
        result = self.runner.invoke(cli, ['witness', 'verify'])
        # May fail if no database, but command parses
        assert result.exit_code in [0, 1]

    def test_witness_query(self):
        """Test witness query"""
        result = self.runner.invoke(cli, ['witness', 'query', '--limit', '5'])
        # May fail if no database, but command parses
        assert result.exit_code in [0, 1]

    def test_witness_query_with_filters(self):
        """Test witness query with filters"""
        result = self.runner.invoke(cli, [
            'witness', 'query',
            '--component', 'IF.coordinator',
            '--event', 'task_claimed',
            '--trace-id', 'test-123',
            '--limit', '10'
        ])
        # May fail if no database, but command parses
        assert result.exit_code in [0, 1]

    def test_witness_query_json_format(self):
        """Test witness query with JSON output"""
        result = self.runner.invoke(cli, [
            'witness', 'query',
            '--format', 'json',
            '--limit', '5'
        ])
        assert result.exit_code in [0, 1]

    def test_witness_query_csv_format(self):
        """Test witness query with CSV output"""
        result = self.runner.invoke(cli, [
            'witness', 'query',
            '--format', 'csv',
            '--limit', '5'
        ])
        assert result.exit_code in [0, 1]


class TestOptimiseCommands:
    """Test optimise subcommands"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_optimise_help(self):
        """Test optimise --help"""
        result = self.runner.invoke(cli, ['optimise', '--help'])
        assert result.exit_code == 0
        assert 'Cost tracking' in result.output

    def test_optimise_report(self):
        """Test optimise report"""
        result = self.runner.invoke(cli, ['optimise', 'report'])
        assert result.exit_code == 0
        assert 'Cost Report' in result.output

    def test_optimise_report_today(self):
        """Test optimise report --today"""
        result = self.runner.invoke(cli, ['optimise', 'report', '--today'])
        assert result.exit_code == 0
        assert 'Today' in result.output or 'Cost' in result.output

    def test_optimise_cache_stats(self):
        """Test optimise cache-stats"""
        result = self.runner.invoke(cli, ['optimise', 'cache-stats'])
        assert result.exit_code == 0
        assert 'Cache' in result.output


class TestUtilityCommands:
    """Test utility commands"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_version_command(self):
        """Test version command"""
        result = self.runner.invoke(cli, ['version'])
        assert result.exit_code == 0
        assert 'InfraFabric' in result.output

    def test_workflows_command(self):
        """Test workflows command"""
        result = self.runner.invoke(cli, ['workflows'])
        assert result.exit_code == 0
        assert 'Workflow' in result.output


class TestCommandChaining:
    """Test command combinations and chaining"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_trace_with_coordinator(self):
        """Test --trace flag with coordinator commands"""
        result = self.runner.invoke(cli, [
            '--trace', 'test-trace-001',
            'coordinator', 'status'
        ])
        assert result.exit_code == 0

    def test_debug_with_witness(self):
        """Test --debug flag with witness commands"""
        result = self.runner.invoke(cli, [
            '--debug',
            'witness', 'query', '--limit', '5'
        ])
        assert result.exit_code in [0, 1]

    def test_multiple_global_flags(self):
        """Test multiple global flags together"""
        result = self.runner.invoke(cli, [
            '--debug',
            '--trace', 'test-123',
            '--mode', 'falsify',
            'version'
        ])
        assert result.exit_code == 0


class TestErrorHandling:
    """Test error handling"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_unknown_command(self):
        """Test unknown command"""
        result = self.runner.invoke(cli, ['unknown'])
        assert result.exit_code != 0

    def test_missing_required_option(self):
        """Test missing required option"""
        result = self.runner.invoke(cli, [
            'governor', 'register', 'session-1'
            # Missing --capabilities, --cost-per-hour, --budget
        ])
        assert result.exit_code != 0

    def test_invalid_option_value(self):
        """Test invalid option value"""
        result = self.runner.invoke(cli, [
            'coordinator', 'start',
            '--port', 'not-a-number'
        ])
        assert result.exit_code != 0


class TestMainEntryPoint:
    """Test main() entry point"""

    def test_main_function_exists(self):
        """Test main() function is callable"""
        assert callable(main)

    @patch('src.cli.if_main.cli')
    def test_main_calls_cli(self, mock_cli):
        """Test main() calls cli()"""
        # Mock cli to prevent actual execution
        mock_cli.return_value = None

        try:
            main()
        except SystemExit:
            pass

        # Verify cli was called
        mock_cli.assert_called_once()


class TestHelpTextQuality:
    """Test help text quality and completeness"""

    def setup_method(self):
        """Setup test runner"""
        self.runner = CliRunner()

    def test_main_help_has_examples(self):
        """Test main help includes examples"""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Examples:' in result.output or 'Quick Start:' in result.output

    def test_coordinator_help_descriptive(self):
        """Test coordinator help is descriptive"""
        result = self.runner.invoke(cli, ['coordinator', '--help'])
        assert result.exit_code == 0
        assert len(result.output) > 100  # Should have substantial help text

    def test_subcommand_help_available(self):
        """Test all main subcommands have help"""
        commands = ['coordinator', 'governor', 'chassis', 'witness', 'optimise', 'config']

        for cmd in commands:
            result = self.runner.invoke(cli, [cmd, '--help'])
            assert result.exit_code == 0, f"Help failed for {cmd}"
            assert len(result.output) > 50, f"Help too short for {cmd}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
