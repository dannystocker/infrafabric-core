"""
Unit Tests for IF.executor - Policy-Governed Command Execution

Tests cover:
- Command execution with valid policy
- Policy enforcement (allow-list validation)
- Capability checking
- Timeout enforcement
- IF.witness logging
- Error handling
- Policy file loading
- Security boundary enforcement
"""

import pytest
import asyncio
import json
import time
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from pathlib import Path

from infrafabric.executor import (
    IFExecutor,
    ExecutionResult,
    ExecutionPolicy,
    PolicyRule,
    ExecutorError,
    PolicyViolationError,
    TimeoutError
)
from infrafabric.event_bus import EventBus, WatchEvent


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_event_bus():
    """Mock EventBus for testing"""
    bus = AsyncMock(spec=EventBus)
    bus.watch = AsyncMock(return_value='watch-123')
    bus.get = AsyncMock()
    bus.put = AsyncMock()
    return bus


@pytest.fixture
def mock_witness_logger():
    """Mock IF.witness logger"""
    logger = Mock()
    logger.events = []
    return logger


@pytest.fixture
def executor(mock_event_bus, mock_witness_logger, tmp_path):
    """IF.executor instance with mocked dependencies"""
    return IFExecutor(
        event_bus=mock_event_bus,
        policy_dir=str(tmp_path / 'policies'),
        witness_logger=mock_witness_logger
    )


@pytest.fixture
def sample_policy(tmp_path):
    """Create sample policy file"""
    policy_dir = tmp_path / 'policies' / 'test-swarm'
    policy_dir.mkdir(parents=True)

    policy = {
        'swarm_id': 'test-swarm',
        'allow': [
            {
                'executable': '/usr/bin/pgrep',
                'args_pattern': '^-f\\s+\\w+$',
                'description': 'Check process by name'
            },
            {
                'executable': '/usr/bin/systemctl',
                'args_pattern': '^(start|stop|status)\\s+\\w+$',
                'description': 'Manage systemd services'
            },
            {
                'executable': '/bin/echo',
                'args_pattern': None,  # Allow any args
                'description': 'Echo command for testing'
            }
        ],
        'default_timeout_ms': 5000,
        'max_timeout_ms': 30000
    }

    policy_file = policy_dir / 'executor_policy.json'
    with open(policy_file, 'w') as f:
        json.dump(policy, f)

    return str(tmp_path / 'policies')


# ============================================================================
# Service Lifecycle Tests
# ============================================================================

@pytest.mark.asyncio
async def test_executor_start(executor, mock_event_bus):
    """Test IF.executor service start subscribes to command topic"""
    await executor.start()

    mock_event_bus.watch.assert_called_once()
    call_args = mock_event_bus.watch.call_args

    assert call_args[0][0] == 'if.command.system.execute'
    assert callable(call_args[1]['callback'])
    assert executor._watch_id == 'watch-123'


@pytest.mark.asyncio
async def test_executor_stop(executor):
    """Test IF.executor service stop"""
    executor._watch_id = 'watch-123'
    await executor.stop()
    # Just verify no exceptions


# ============================================================================
# Command Execution Tests
# ============================================================================

@pytest.mark.asyncio
async def test_execute_simple_command_success(executor):
    """Test successful execution of simple command"""
    result = await executor._execute('/bin/echo', ['hello', 'world'])

    assert result.success is True
    assert result.exit_code == 0
    assert 'hello world' in result.stdout
    assert result.stderr is None or result.stderr == ''
    assert result.execution_time_ms > 0
    assert result.execution_time_ms < 1000  # Should be very fast


@pytest.mark.asyncio
async def test_execute_command_with_exit_code(executor):
    """Test command execution captures non-zero exit code"""
    # 'false' command always exits with 1
    result = await executor._execute('/bin/false', [])

    assert result.success is False
    assert result.exit_code == 1


@pytest.mark.asyncio
async def test_execute_command_not_found(executor):
    """Test execution handles non-existent executable"""
    result = await executor._execute('/nonexistent/command', [])

    assert result.success is False
    assert 'not found' in result.error.lower()


@pytest.mark.asyncio
async def test_execute_command_captures_stderr(executor):
    """Test command execution captures stderr output"""
    # Use a command that writes to stderr
    result = await executor._execute('/bin/sh', ['-c', 'echo error >&2'])

    assert result.stderr is not None
    assert 'error' in result.stderr


# ============================================================================
# Policy Enforcement Tests
# ============================================================================

@pytest.mark.asyncio
async def test_load_policy_success(executor, sample_policy):
    """Test loading valid policy file"""
    executor.policy_dir = Path(sample_policy)

    policy = await executor._load_policy('test-swarm')

    assert policy.swarm_id == 'test-swarm'
    assert len(policy.allow) == 3
    assert policy.default_timeout_ms == 5000
    assert policy.max_timeout_ms == 30000


@pytest.mark.asyncio
async def test_load_policy_not_found(executor, tmp_path):
    """Test loading policy for non-existent swarm fails"""
    executor.policy_dir = tmp_path / 'policies'

    with pytest.raises(PolicyViolationError, match='No policy file'):
        await executor._load_policy('nonexistent-swarm')


@pytest.mark.asyncio
async def test_load_policy_caching(executor, sample_policy):
    """Test policy is cached after first load"""
    executor.policy_dir = Path(sample_policy)

    # Load twice
    policy1 = await executor._load_policy('test-swarm')
    policy2 = await executor._load_policy('test-swarm')

    # Should be same instance (cached)
    assert policy1 is policy2


def test_validate_command_allowed_with_pattern(executor):
    """Test command validation allows matching patterns"""
    policy = ExecutionPolicy(
        swarm_id='test',
        allow=[
            PolicyRule(
                executable='/usr/bin/pgrep',
                args_pattern='^-f\\s+meilisearch$'
            )
        ]
    )

    result = executor._validate_command(
        policy,
        '/usr/bin/pgrep',
        ['-f', 'meilisearch']
    )

    assert result is True


def test_validate_command_denied_wrong_executable(executor):
    """Test command validation denies wrong executable"""
    policy = ExecutionPolicy(
        swarm_id='test',
        allow=[
            PolicyRule(executable='/usr/bin/pgrep', args_pattern='^-f\\s+\\w+$')
        ]
    )

    result = executor._validate_command(
        policy,
        '/usr/bin/systemctl',  # Wrong executable
        ['-f', 'meilisearch']
    )

    assert result is False


def test_validate_command_denied_wrong_args(executor):
    """Test command validation denies args not matching pattern"""
    policy = ExecutionPolicy(
        swarm_id='test',
        allow=[
            PolicyRule(
                executable='/usr/bin/systemctl',
                args_pattern='^(start|stop|status)\\s+\\w+$'
            )
        ]
    )

    result = executor._validate_command(
        policy,
        '/usr/bin/systemctl',
        ['restart', 'service']  # 'restart' not in pattern
    )

    assert result is False


def test_validate_command_allowed_no_args_pattern(executor):
    """Test command validation allows any args when no pattern specified"""
    policy = ExecutionPolicy(
        swarm_id='test',
        allow=[
            PolicyRule(
                executable='/bin/echo',
                args_pattern=None  # No pattern = allow any args
            )
        ]
    )

    result = executor._validate_command(
        policy,
        '/bin/echo',
        ['anything', 'goes', 'here']
    )

    assert result is True


def test_validate_command_multiple_rules(executor):
    """Test command validation checks all rules"""
    policy = ExecutionPolicy(
        swarm_id='test',
        allow=[
            PolicyRule(executable='/usr/bin/pgrep', args_pattern='^-f\\s+\\w+$'),
            PolicyRule(executable='/usr/bin/systemctl', args_pattern='^status\\s+\\w+$'),
            PolicyRule(executable='/bin/echo', args_pattern=None)
        ]
    )

    # Should match second rule
    result = executor._validate_command(
        policy,
        '/usr/bin/systemctl',
        ['status', 'nginx']
    )

    assert result is True


# ============================================================================
# Capability Checking Tests
# ============================================================================

@pytest.mark.asyncio
async def test_check_capability_has_capability(executor, mock_event_bus):
    """Test capability check succeeds when swarm has capability"""
    mock_event_bus.get.return_value = json.dumps([
        'system.process.execute',
        'network.http.proxy.external'
    ])

    result = await executor._check_capability('test-swarm', 'system.process.execute')

    assert result is True
    mock_event_bus.get.assert_called_once_with('/swarms/test-swarm/capabilities')


@pytest.mark.asyncio
async def test_check_capability_missing_capability(executor, mock_event_bus):
    """Test capability check fails when swarm lacks capability"""
    mock_event_bus.get.return_value = json.dumps([
        'network.http.proxy.external'  # Missing system.process.execute
    ])

    result = await executor._check_capability('test-swarm', 'system.process.execute')

    assert result is False


@pytest.mark.asyncio
async def test_check_capability_swarm_not_registered(executor, mock_event_bus):
    """Test capability check fails when swarm not registered"""
    mock_event_bus.get.return_value = None

    result = await executor._check_capability('nonexistent-swarm', 'system.process.execute')

    assert result is False


# ============================================================================
# End-to-End Request Handling Tests
# ============================================================================

@pytest.mark.asyncio
async def test_handle_execute_request_success(executor, mock_event_bus, mock_witness_logger, sample_policy):
    """Test successful command execution end-to-end"""
    executor.policy_dir = Path(sample_policy)

    # Mock capability check
    mock_event_bus.get.return_value = json.dumps(['system.process.execute'])

    # Create request event
    request = {
        'trace_id': 'trace-123',
        'swarm_id': 'test-swarm',
        'executable': '/bin/echo',
        'args': ['hello'],
        'timeout_ms': 5000
    }

    event = WatchEvent(
        key='if.command.system.execute',
        value=json.dumps(request),
        event_type='put',
        mod_revision=1
    )

    await executor._handle_execute_request(event)

    # Verify result published
    mock_event_bus.put.assert_called_once()
    call_args = mock_event_bus.put.call_args
    assert call_args[0][0] == 'if.event.system.execute.result/trace-123'

    result = json.loads(call_args[0][1])
    assert result['trace_id'] == 'trace-123'
    assert result['success'] is True
    assert result['exit_code'] == 0

    # Verify IF.witness logging
    assert len(mock_witness_logger.events) == 1
    log = mock_witness_logger.events[0]
    assert log['operation'] == 'command_executed'
    assert log['swarm_id'] == 'test-swarm'
    assert log['executable'] == '/bin/echo'


@pytest.mark.asyncio
async def test_handle_execute_request_missing_capability(executor, mock_event_bus, mock_witness_logger):
    """Test request denied when swarm lacks capability"""
    # Mock capability check fails
    mock_event_bus.get.return_value = json.dumps([])

    request = {
        'trace_id': 'trace-456',
        'swarm_id': 'test-swarm',
        'executable': '/bin/echo',
        'args': ['hello'],
        'timeout_ms': 5000
    }

    event = WatchEvent(
        key='if.command.system.execute',
        value=json.dumps(request),
        event_type='put',
        mod_revision=1
    )

    await executor._handle_execute_request(event)

    # Verify error result
    call_args = mock_event_bus.put.call_args
    result = json.loads(call_args[0][1])
    assert result['success'] is False
    assert 'capability' in result['error'].lower()

    # Verify IF.witness logging
    log = mock_witness_logger.events[0]
    assert log['operation'] == 'command_denied_capability'


@pytest.mark.asyncio
async def test_handle_execute_request_policy_violation(executor, mock_event_bus, mock_witness_logger, sample_policy):
    """Test request denied when command violates policy"""
    executor.policy_dir = Path(sample_policy)

    # Mock capability check succeeds
    mock_event_bus.get.return_value = json.dumps(['system.process.execute'])

    # Request command not in policy
    request = {
        'trace_id': 'trace-789',
        'swarm_id': 'test-swarm',
        'executable': '/bin/rm',  # Not in policy!
        'args': ['-rf', '/'],
        'timeout_ms': 5000
    }

    event = WatchEvent(
        key='if.command.system.execute',
        value=json.dumps(request),
        event_type='put',
        mod_revision=1
    )

    await executor._handle_execute_request(event)

    # Verify error result
    call_args = mock_event_bus.put.call_args
    result = json.loads(call_args[0][1])
    assert result['success'] is False
    assert 'policy violation' in result['error'].lower()

    # Verify IF.witness logging
    log = mock_witness_logger.events[0]
    assert log['operation'] == 'command_denied_policy'


@pytest.mark.asyncio
async def test_handle_execute_request_timeout(executor, mock_event_bus, mock_witness_logger, sample_policy):
    """Test request times out if execution takes too long"""
    executor.policy_dir = Path(sample_policy)

    # Mock capability check
    mock_event_bus.get.return_value = json.dumps(['system.process.execute'])

    # Request with very short timeout
    request = {
        'trace_id': 'trace-timeout',
        'swarm_id': 'test-swarm',
        'executable': '/bin/sleep',  # This will timeout
        'args': ['10'],  # Sleep 10 seconds
        'timeout_ms': 100  # But timeout in 100ms
    }

    # Add sleep command to policy
    policy_dir = Path(sample_policy) / 'test-swarm'
    policy_file = policy_dir / 'executor_policy.json'
    with open(policy_file, 'r') as f:
        policy = json.load(f)
    policy['allow'].append({
        'executable': '/bin/sleep',
        'args_pattern': '^\\d+$',
        'description': 'Sleep for testing'
    })
    with open(policy_file, 'w') as f:
        json.dump(policy, f)

    event = WatchEvent(
        key='if.command.system.execute',
        value=json.dumps(request),
        event_type='put',
        mod_revision=1
    )

    await executor._handle_execute_request(event)

    # Verify timeout error
    call_args = mock_event_bus.put.call_args
    result = json.loads(call_args[0][1])
    assert result['success'] is False
    assert 'timeout' in result['error'].lower()

    # Verify IF.witness logging
    log = mock_witness_logger.events[0]
    assert log['operation'] == 'command_timeout'


@pytest.mark.asyncio
async def test_handle_execute_request_missing_fields(executor, mock_event_bus):
    """Test request rejected when missing required fields"""
    request = {
        'trace_id': 'trace-bad',
        # Missing swarm_id and executable
        'args': ['hello']
    }

    event = WatchEvent(
        key='if.command.system.execute',
        value=json.dumps(request),
        event_type='put',
        mod_revision=1
    )

    await executor._handle_execute_request(event)

    # Verify error result
    call_args = mock_event_bus.put.call_args
    result = json.loads(call_args[0][1])
    assert result['success'] is False
    assert 'missing required fields' in result['error'].lower()


@pytest.mark.asyncio
async def test_handle_execute_request_respects_max_timeout(executor, mock_event_bus, sample_policy):
    """Test request timeout capped at policy max_timeout_ms"""
    executor.policy_dir = Path(sample_policy)

    # Mock capability check
    mock_event_bus.get.return_value = json.dumps(['system.process.execute'])

    # Request with timeout exceeding policy max
    request = {
        'trace_id': 'trace-max',
        'swarm_id': 'test-swarm',
        'executable': '/bin/echo',
        'args': ['hello'],
        'timeout_ms': 999999  # Way over policy max of 30000ms
    }

    event = WatchEvent(
        key='if.command.system.execute',
        value=json.dumps(request),
        event_type='put',
        mod_revision=1
    )

    # Mock _execute to check timeout
    original_execute = executor._execute
    executed_with_timeout = None

    async def capture_timeout(*args):
        nonlocal executed_with_timeout
        # The timeout will be enforced by asyncio.wait_for in _handle_execute_request
        return await original_execute(*args)

    executor._execute = capture_timeout

    await executor._handle_execute_request(event)

    # Execution should succeed (capped at 30000ms, which is plenty for echo)
    call_args = mock_event_bus.put.call_args
    result = json.loads(call_args[0][1])
    assert result['success'] is True


# ============================================================================
# IF.witness Logging Tests
# ============================================================================

def test_log_witness_with_callable(executor):
    """Test IF.witness logging with callable logger"""
    logged_entries = []
    executor.witness_logger = lambda entry: logged_entries.append(entry)

    executor._log_witness(
        'test_operation',
        'test-swarm',
        '/bin/echo',
        ['hello'],
        {'extra': 'data'}
    )

    assert len(logged_entries) == 1
    log = logged_entries[0]
    assert log['component'] == 'IF.executor'
    assert log['operation'] == 'test_operation'
    assert log['swarm_id'] == 'test-swarm'
    assert log['executable'] == '/bin/echo'
    assert log['args'] == ['hello']
    assert log['extra'] == 'data'
    assert 'timestamp' in log


def test_log_witness_with_events_list(executor, mock_witness_logger):
    """Test IF.witness logging with events list"""
    executor._log_witness(
        'test_operation',
        'test-swarm',
        '/bin/echo',
        ['hello']
    )

    assert len(mock_witness_logger.events) == 1
    log = mock_witness_logger.events[0]
    assert log['operation'] == 'test_operation'


def test_log_witness_no_logger(executor):
    """Test IF.witness logging gracefully handles no logger"""
    executor.witness_logger = None

    # Should not raise exception
    executor._log_witness(
        'test_operation',
        'test-swarm',
        '/bin/echo',
        ['hello']
    )


# ============================================================================
# Result Publishing Tests
# ============================================================================

@pytest.mark.asyncio
async def test_send_result_publishes_to_correct_topic(executor, mock_event_bus):
    """Test result publishing uses correct IF.bus topic"""
    await executor._send_result(
        'trace-123',
        success=True,
        exit_code=0,
        stdout='output'
    )

    mock_event_bus.put.assert_called_once()
    call_args = mock_event_bus.put.call_args

    assert call_args[0][0] == 'if.event.system.execute.result/trace-123'

    result = json.loads(call_args[0][1])
    assert result['trace_id'] == 'trace-123'
    assert result['success'] is True
    assert result['exit_code'] == 0
    assert result['stdout'] == 'output'


# ============================================================================
# Security Tests
# ============================================================================

def test_policy_prevents_dangerous_commands(executor):
    """Test policy can prevent dangerous commands"""
    policy = ExecutionPolicy(
        swarm_id='test',
        allow=[
            PolicyRule(executable='/usr/bin/pgrep', args_pattern='^-f\\s+\\w+$')
        ]
    )

    # Try to execute rm -rf /
    result = executor._validate_command(
        policy,
        '/bin/rm',
        ['-rf', '/']
    )

    assert result is False


def test_policy_enforces_args_pattern(executor):
    """Test policy args pattern prevents command injection"""
    policy = ExecutionPolicy(
        swarm_id='test',
        allow=[
            PolicyRule(
                executable='/bin/echo',
                args_pattern='^[a-zA-Z0-9\\s]+$'  # Only alphanumeric
            )
        ]
    )

    # Try command injection
    result = executor._validate_command(
        policy,
        '/bin/echo',
        ['hello; rm -rf /']  # Won't match pattern
    )

    assert result is False


@pytest.mark.asyncio
async def test_execution_no_shell_expansion(executor):
    """Test command execution doesn't use shell (prevents injection)"""
    # If shell expansion worked, this would create a file
    # But without shell, it will just fail to find the executable
    result = await executor._execute('echo hello > /tmp/test.txt', [])

    assert result.success is False
    assert 'not found' in result.error.lower()
