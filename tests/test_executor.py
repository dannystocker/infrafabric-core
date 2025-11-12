#!/usr/bin/env python3
"""
Unit tests for IF.executor - Policy-Governed Command Execution

Tests cover:
- Policy validation and loading
- Command execution with various outcomes
- Capability checking
- Timeout enforcement
- Error handling
- Audit logging
- Statistics tracking

License: MIT
"""

import asyncio
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime, timezone

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrafabric.executor import IFExecutor, ExecutionPolicy


# =============================================================================
# ExecutionPolicy Tests
# =============================================================================

class TestExecutionPolicy:
    """Test ExecutionPolicy class"""

    def test_policy_initialization(self):
        """Test policy initialization from JSON data"""
        policy_data = {
            'allow': [
                {
                    'executable': '/usr/bin/pgrep',
                    'args_pattern': '^-f\\s+.*$',
                    'description': 'Check process by name'
                }
            ]
        }

        policy = ExecutionPolicy(policy_data)

        assert len(policy.allow_list) == 1
        assert policy.allow_list[0]['executable'] == '/usr/bin/pgrep'
        assert '_compiled_pattern' in policy.allow_list[0]

    def test_policy_allows_matching_command(self):
        """Test policy allows command matching pattern"""
        policy_data = {
            'allow': [
                {
                    'executable': '/usr/bin/pgrep',
                    'args_pattern': '^-f\\s+.*$'
                }
            ]
        }

        policy = ExecutionPolicy(policy_data)

        assert policy.is_allowed('/usr/bin/pgrep', ['-f', 'meilisearch']) is True

    def test_policy_denies_non_matching_command(self):
        """Test policy denies command not matching pattern"""
        policy_data = {
            'allow': [
                {
                    'executable': '/usr/bin/pgrep',
                    'args_pattern': '^-f\\s+.*$'
                }
            ]
        }

        policy = ExecutionPolicy(policy_data)

        # Wrong executable
        assert policy.is_allowed('/usr/bin/kill', ['-9', '1234']) is False

        # Wrong args pattern
        assert policy.is_allowed('/usr/bin/pgrep', ['-x', 'process']) is False

    def test_policy_systemctl_pattern(self):
        """Test systemctl service management pattern"""
        policy_data = {
            'allow': [
                {
                    'executable': '/usr/bin/systemctl',
                    'args_pattern': '^(start|stop|status|restart)\\s+[a-zA-Z0-9_-]+\\.service$'
                }
            ]
        }

        policy = ExecutionPolicy(policy_data)

        # Valid commands
        assert policy.is_allowed('/usr/bin/systemctl', ['start', 'nginx.service']) is True
        assert policy.is_allowed('/usr/bin/systemctl', ['stop', 'redis.service']) is True
        assert policy.is_allowed('/usr/bin/systemctl', ['status', 'docker.service']) is True

        # Invalid commands
        assert policy.is_allowed('/usr/bin/systemctl', ['enable', 'nginx.service']) is False
        assert policy.is_allowed('/usr/bin/systemctl', ['start', 'nginx']) is False  # Missing .service
        assert policy.is_allowed('/usr/bin/systemctl', ['start', '../../../etc/passwd.service']) is False

    def test_policy_no_args_pattern(self):
        """Test policy with no args pattern (command without arguments)"""
        policy_data = {
            'allow': [
                {
                    'executable': '/usr/bin/uptime'
                }
            ]
        }

        policy = ExecutionPolicy(policy_data)

        assert policy.is_allowed('/usr/bin/uptime', []) is True

    def test_policy_multiple_rules(self):
        """Test policy with multiple rules"""
        policy_data = {
            'allow': [
                {
                    'executable': '/usr/bin/pgrep',
                    'args_pattern': '^-f\\s+.*$'
                },
                {
                    'executable': '/usr/bin/systemctl',
                    'args_pattern': '^status\\s+.*$'
                },
                {
                    'executable': '/usr/bin/uptime'
                }
            ]
        }

        policy = ExecutionPolicy(policy_data)

        assert policy.is_allowed('/usr/bin/pgrep', ['-f', 'test']) is True
        assert policy.is_allowed('/usr/bin/systemctl', ['status', 'nginx']) is True
        assert policy.is_allowed('/usr/bin/uptime', []) is True
        assert policy.is_allowed('/usr/bin/kill', ['-9', '1']) is False

    def test_get_matching_rule(self):
        """Test retrieving the matching rule"""
        policy_data = {
            'allow': [
                {
                    'executable': '/usr/bin/pgrep',
                    'args_pattern': '^-f\\s+.*$',
                    'description': 'Find process by pattern'
                }
            ]
        }

        policy = ExecutionPolicy(policy_data)

        rule = policy.get_matching_rule('/usr/bin/pgrep', ['-f', 'meilisearch'])
        assert rule is not None
        assert rule['description'] == 'Find process by pattern'

        rule = policy.get_matching_rule('/usr/bin/kill', ['-9', '1'])
        assert rule is None


# =============================================================================
# IFExecutor Tests
# =============================================================================

@pytest.fixture
def mock_event_bus():
    """Create mock event bus"""
    bus = AsyncMock()
    bus.subscribe = AsyncMock()
    bus.unsubscribe = AsyncMock()
    bus.publish = AsyncMock()
    return bus


@pytest.fixture
def temp_policy_dir():
    """Create temporary policy directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def executor(mock_event_bus, temp_policy_dir):
    """Create IF.executor instance"""
    return IFExecutor(
        event_bus=mock_event_bus,
        policy_dir=str(temp_policy_dir),
        default_timeout_ms=5000
    )


class TestIFExecutor:
    """Test IFExecutor class"""

    @pytest.mark.asyncio
    async def test_executor_initialization(self, executor):
        """Test executor initializes correctly"""
        assert executor.default_timeout_ms == 5000
        assert executor.max_timeout_ms == 30000
        assert executor.stats['total_requests'] == 0

    @pytest.mark.asyncio
    async def test_executor_start(self, executor, mock_event_bus):
        """Test executor subscribes to command topic on start"""
        await executor.start()

        mock_event_bus.subscribe.assert_called_once()
        call_args = mock_event_bus.subscribe.call_args
        assert call_args[1]['topic'] == 'if.command.system.execute'

    @pytest.mark.asyncio
    async def test_executor_stop(self, executor, mock_event_bus):
        """Test executor unsubscribes on stop"""
        await executor.stop()

        mock_event_bus.unsubscribe.assert_called_once_with('if.command.system.execute')

    @pytest.mark.asyncio
    async def test_execute_command_success(self, executor):
        """Test successful command execution"""
        result = await executor._execute_command('/bin/echo', ['hello', 'world'])

        assert result['exit_code'] == 0
        assert 'hello world' in result['stdout']
        assert result['stderr'] == ''
        assert result['execution_time_ms'] >= 0

    @pytest.mark.asyncio
    async def test_execute_command_with_stderr(self, executor):
        """Test command execution with stderr output"""
        result = await executor._execute_command('/bin/sh', ['-c', 'echo error >&2'])

        assert result['exit_code'] == 0
        assert 'error' in result['stderr']

    @pytest.mark.asyncio
    async def test_execute_command_nonzero_exit(self, executor):
        """Test command execution with non-zero exit code"""
        result = await executor._execute_command('/bin/sh', ['-c', 'exit 42'])

        assert result['exit_code'] == 42

    @pytest.mark.asyncio
    async def test_policy_loading(self, executor, temp_policy_dir):
        """Test policy file loading"""
        # Create policy file
        swarm_dir = temp_policy_dir / 'session-1-ndi'
        swarm_dir.mkdir()

        policy_file = swarm_dir / 'executor_policy.json'
        policy_data = {
            'allow': [
                {
                    'executable': '/usr/bin/pgrep',
                    'args_pattern': '^-f\\s+.*$'
                }
            ]
        }

        with open(policy_file, 'w') as f:
            json.dump(policy_data, f)

        # Load policy
        policy = await executor._load_policy('session-1-ndi')

        assert policy is not None
        assert len(policy.allow_list) == 1
        assert policy.is_allowed('/usr/bin/pgrep', ['-f', 'test']) is True

    @pytest.mark.asyncio
    async def test_policy_caching(self, executor, temp_policy_dir):
        """Test policy is cached after first load"""
        # Create policy file
        swarm_dir = temp_policy_dir / 'session-1-ndi'
        swarm_dir.mkdir()

        policy_file = swarm_dir / 'executor_policy.json'
        with open(policy_file, 'w') as f:
            json.dump({'allow': []}, f)

        # Load twice
        policy1 = await executor._load_policy('session-1-ndi')
        policy2 = await executor._load_policy('session-1-ndi')

        # Should be same instance (cached)
        assert policy1 is policy2

    @pytest.mark.asyncio
    async def test_policy_not_found(self, executor):
        """Test handling of missing policy file"""
        policy = await executor._load_policy('nonexistent-swarm')

        assert policy is None

    @pytest.mark.asyncio
    async def test_send_result(self, executor, mock_event_bus):
        """Test sending execution result"""
        await executor._send_result(
            trace_id='trace-001',
            success=True,
            exit_code=0,
            stdout='output',
            stderr='',
            execution_time_ms=50
        )

        mock_event_bus.publish.assert_called_once()
        call_args = mock_event_bus.publish.call_args
        assert call_args[1]['topic'] == 'if.event.system.execute.result'
        message = call_args[1]['message']
        assert message['trace_id'] == 'trace-001'
        assert message['success'] is True
        assert message['exit_code'] == 0

    @pytest.mark.asyncio
    async def test_send_error(self, executor, mock_event_bus):
        """Test sending error response"""
        await executor._send_error('trace-002', 'Test error')

        mock_event_bus.publish.assert_called_once()
        call_args = mock_event_bus.publish.call_args
        message = call_args[1]['message']
        assert message['trace_id'] == 'trace-002'
        assert message['success'] is False
        assert message['error'] == 'Test error'

    @pytest.mark.asyncio
    async def test_handle_request_missing_swarm_id(self, executor, mock_event_bus):
        """Test request with missing swarm_id"""
        request = {
            'trace_id': 'trace-003',
            'executable': '/bin/echo',
            'args': ['hello']
        }

        await executor._handle_execute_request(request)

        # Should send error
        mock_event_bus.publish.assert_called_once()
        message = mock_event_bus.publish.call_args[1]['message']
        assert message['success'] is False
        assert 'swarm_id' in message['error']

    @pytest.mark.asyncio
    async def test_handle_request_missing_executable(self, executor, mock_event_bus):
        """Test request with missing executable"""
        request = {
            'trace_id': 'trace-004',
            'swarm_id': 'session-1-ndi',
            'args': ['hello']
        }

        await executor._handle_execute_request(request)

        # Should send error
        mock_event_bus.publish.assert_called_once()
        message = mock_event_bus.publish.call_args[1]['message']
        assert message['success'] is False
        assert 'executable' in message['error']

    @pytest.mark.asyncio
    async def test_handle_request_timeout_exceeded(self, executor, mock_event_bus):
        """Test request with timeout exceeding maximum"""
        request = {
            'trace_id': 'trace-005',
            'swarm_id': 'session-1-ndi',
            'executable': '/bin/echo',
            'args': ['hello'],
            'timeout_ms': 999999  # Exceeds max
        }

        await executor._handle_execute_request(request)

        # Should send error
        mock_event_bus.publish.assert_called_once()
        message = mock_event_bus.publish.call_args[1]['message']
        assert message['success'] is False
        assert 'exceeds maximum' in message['error']

    @pytest.mark.asyncio
    async def test_handle_request_no_policy(self, executor, mock_event_bus):
        """Test request when no policy exists for swarm"""
        request = {
            'trace_id': 'trace-006',
            'swarm_id': 'nonexistent-swarm',
            'executable': '/bin/echo',
            'args': ['hello']
        }

        await executor._handle_execute_request(request)

        # Should deny and send error
        assert executor.stats['denied'] == 1
        mock_event_bus.publish.assert_called()
        message = mock_event_bus.publish.call_args[1]['message']
        assert message['success'] is False
        assert 'No policy' in message['error']

    @pytest.mark.asyncio
    async def test_handle_request_command_denied(self, executor, mock_event_bus, temp_policy_dir):
        """Test request with command denied by policy"""
        # Create restrictive policy
        swarm_dir = temp_policy_dir / 'session-1-ndi'
        swarm_dir.mkdir()

        policy_file = swarm_dir / 'executor_policy.json'
        with open(policy_file, 'w') as f:
            json.dump({
                'allow': [
                    {
                        'executable': '/usr/bin/pgrep',
                        'args_pattern': '^-f\\s+.*$'
                    }
                ]
            }, f)

        # Try to run disallowed command
        request = {
            'trace_id': 'trace-007',
            'swarm_id': 'session-1-ndi',
            'executable': '/bin/kill',  # Not in allow list
            'args': ['-9', '1234']
        }

        await executor._handle_execute_request(request)

        # Should deny
        assert executor.stats['denied'] == 1
        mock_event_bus.publish.assert_called()
        message = mock_event_bus.publish.call_args[1]['message']
        assert message['success'] is False
        assert 'not allowed by policy' in message['error']

    @pytest.mark.asyncio
    async def test_handle_request_successful_execution(self, executor, mock_event_bus, temp_policy_dir):
        """Test successful command execution flow"""
        # Create policy allowing echo
        swarm_dir = temp_policy_dir / 'session-1-ndi'
        swarm_dir.mkdir()

        policy_file = swarm_dir / 'executor_policy.json'
        with open(policy_file, 'w') as f:
            json.dump({
                'allow': [
                    {
                        'executable': '/bin/echo',
                        'args_pattern': '.*'
                    }
                ]
            }, f)

        # Execute allowed command
        request = {
            'trace_id': 'trace-008',
            'swarm_id': 'session-1-ndi',
            'executable': '/bin/echo',
            'args': ['hello', 'world']
        }

        await executor._handle_execute_request(request)

        # Should execute and send result
        assert executor.stats['allowed'] == 1
        assert executor.stats['executed'] == 1
        mock_event_bus.publish.assert_called()
        message = mock_event_bus.publish.call_args[1]['message']
        assert message['success'] is True
        assert message['exit_code'] == 0
        assert 'hello world' in message['stdout']

    @pytest.mark.asyncio
    async def test_handle_request_command_timeout(self, executor, mock_event_bus, temp_policy_dir):
        """Test command execution timeout"""
        # Create policy allowing sleep
        swarm_dir = temp_policy_dir / 'session-1-ndi'
        swarm_dir.mkdir()

        policy_file = swarm_dir / 'executor_policy.json'
        with open(policy_file, 'w') as f:
            json.dump({
                'allow': [
                    {
                        'executable': '/bin/sleep',
                        'args_pattern': '^[0-9]+$'
                    }
                ]
            }, f)

        # Execute command that will timeout
        request = {
            'trace_id': 'trace-009',
            'swarm_id': 'session-1-ndi',
            'executable': '/bin/sleep',
            'args': ['10'],  # 10 seconds
            'timeout_ms': 100  # But timeout after 100ms
        }

        await executor._handle_execute_request(request)

        # Should timeout
        assert executor.stats['timeouts'] == 1
        mock_event_bus.publish.assert_called()
        message = mock_event_bus.publish.call_args[1]['message']
        assert message['success'] is False
        assert 'timeout' in message['error'].lower()

    def test_get_stats(self, executor):
        """Test getting executor statistics"""
        executor.stats['total_requests'] = 10
        executor.stats['executed'] = 8
        executor.stats['denied'] = 2

        stats = executor.get_stats()

        assert stats['total_requests'] == 10
        assert stats['executed'] == 8
        assert stats['denied'] == 2

        # Should be a copy
        stats['total_requests'] = 999
        assert executor.stats['total_requests'] == 10

    def test_clear_policy_cache(self, executor):
        """Test clearing policy cache"""
        executor._policy_cache['test-swarm'] = ExecutionPolicy({'allow': []})
        assert len(executor._policy_cache) == 1

        executor.clear_policy_cache()

        assert len(executor._policy_cache) == 0


# =============================================================================
# Integration Tests
# =============================================================================

class TestIFExecutorIntegration:
    """Integration tests for IF.executor"""

    @pytest.mark.asyncio
    async def test_full_execution_flow(self, temp_policy_dir):
        """Test complete execution flow with real event bus simulation"""
        # Create policy
        swarm_dir = temp_policy_dir / 'session-test'
        swarm_dir.mkdir()

        policy_file = swarm_dir / 'executor_policy.json'
        with open(policy_file, 'w') as f:
            json.dump({
                'allow': [
                    {
                        'executable': '/bin/echo',
                        'args_pattern': '.*',
                        'description': 'Echo command'
                    },
                    {
                        'executable': '/usr/bin/uptime'
                    }
                ]
            }, f)

        # Create mock bus
        results = []

        class MockBus:
            async def subscribe(self, topic, callback):
                self.callback = callback

            async def unsubscribe(self, topic):
                pass

            async def publish(self, topic, message):
                results.append(message)

        bus = MockBus()
        executor = IFExecutor(bus, policy_dir=str(temp_policy_dir))
        await executor.start()

        # Send command request
        request = {
            'trace_id': 'integration-test-001',
            'swarm_id': 'session-test',
            'executable': '/bin/echo',
            'args': ['integration', 'test']
        }

        await bus.callback(request)

        # Check result
        assert len(results) == 1
        result = results[0]
        assert result['trace_id'] == 'integration-test-001'
        assert result['success'] is True
        assert result['exit_code'] == 0
        assert 'integration test' in result['stdout']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
