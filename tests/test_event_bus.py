"""
Unit Tests for EventBus

Tests for etcd3-based event bus infrastructure including:
- Connection management
- Put/get operations
- Watch notifications
- Transaction support
- Health checks

Author: InfraFabric Research
Date: November 2025
"""

import pytest
import asyncio
import sys
from unittest.mock import Mock, MagicMock, patch, AsyncMock

# Mock etcd3 module before importing EventBus
mock_etcd3 = MagicMock()
sys.modules['etcd3'] = mock_etcd3

from infrafabric.event_bus import EventBus


@pytest.fixture
def event_bus():
    """Create EventBus instance for testing."""
    return EventBus(host='localhost', port=2379)


@pytest.mark.asyncio
async def test_init_default_values():
    """Test EventBus initialization with default values."""
    bus = EventBus()
    assert bus.host == 'localhost'
    assert bus.port == 2379
    assert bus.client is None
    assert not bus.is_connected()


@pytest.mark.asyncio
async def test_init_custom_values():
    """Test EventBus initialization with custom values."""
    bus = EventBus(host='192.168.1.1', port=2380)
    assert bus.host == '192.168.1.1'
    assert bus.port == 2380


@pytest.mark.asyncio
async def test_init_env_variables(monkeypatch):
    """Test EventBus initialization from environment variables."""
    monkeypatch.setenv('IF_ETCD_HOST', '10.0.0.1')
    monkeypatch.setenv('IF_ETCD_PORT', '2381')

    bus = EventBus()
    assert bus.host == '10.0.0.1'
    assert bus.port == 2381


@pytest.mark.asyncio
async def test_connection_success(event_bus):
    """Test successful connection to etcd."""
    # Mock the etcd3 client
    with patch('etcd3.client') as mock_client_factory:
        # Create a mock client with required methods
        mock_client = MagicMock()
        mock_client.put = MagicMock()
        mock_client.get = MagicMock(return_value=(b'ok', None))
        mock_client.close = MagicMock()

        mock_client_factory.return_value = mock_client

        # Connect
        result = await event_bus.connect()

        # Verify
        assert result is True
        assert event_bus.is_connected()
        assert event_bus.client is not None


@pytest.mark.asyncio
async def test_connection_failure(event_bus):
    """Test connection failure handling."""
    with patch('etcd3.client') as mock_client_factory:
        # Simulate connection error
        mock_client_factory.side_effect = Exception("Connection refused")

        result = await event_bus.connect()

        assert result is False
        assert not event_bus.is_connected()


@pytest.mark.asyncio
async def test_health_check_failure_on_disconnect():
    """Test health check fails when disconnected."""
    bus = EventBus()
    # Don't connect
    result = await bus.health_check()
    assert result is False


@pytest.mark.asyncio
async def test_disconnect(event_bus):
    """Test disconnection from etcd."""
    # Set up a mock client
    with patch('etcd3.client') as mock_client_factory:
        mock_client = MagicMock()
        mock_client.put = MagicMock()
        mock_client.get = MagicMock(return_value=(b'ok', None))
        mock_client.close = MagicMock()

        mock_client_factory.return_value = mock_client

        # Connect
        await event_bus.connect()
        assert event_bus.is_connected()

        # Disconnect
        await event_bus.disconnect()

        # Verify
        assert not event_bus.is_connected()
        assert event_bus.client is None
        mock_client.close.assert_called()


@pytest.mark.asyncio
async def test_put_operation(event_bus):
    """Test put operation."""
    with patch('etcd3.client') as mock_client_factory:
        mock_client = MagicMock()
        mock_client.put = MagicMock()
        mock_client.get = MagicMock(return_value=(b'ok', None))

        mock_client_factory.return_value = mock_client

        # Connect
        await event_bus.connect()

        # Put
        result = await event_bus.put('/test/key', 'test_value')

        # Verify
        assert result is True
        mock_client.put.assert_called()


@pytest.mark.asyncio
async def test_put_when_disconnected(event_bus):
    """Test put fails when disconnected."""
    result = await event_bus.put('/test/key', 'value')
    assert result is False


@pytest.mark.asyncio
async def test_get_operation(event_bus):
    """Test get operation."""
    with patch('etcd3.client') as mock_client_factory:
        mock_client = MagicMock()
        mock_client.put = MagicMock()
        mock_client.get = MagicMock(return_value=(b'ok', None))

        mock_client_factory.return_value = mock_client

        # Connect
        await event_bus.connect()

        # Mock get to return a value
        mock_client.get.return_value = (b'test_value', None)

        # Get
        result = await event_bus.get('/test/key')

        # Verify
        assert result == 'test_value'
        mock_client.get.assert_called()


@pytest.mark.asyncio
async def test_get_nonexistent_key(event_bus):
    """Test get for nonexistent key."""
    with patch('etcd3.client') as mock_client_factory:
        mock_client = MagicMock()
        mock_client.put = MagicMock()
        mock_client.get = MagicMock(return_value=(None, None))

        mock_client_factory.return_value = mock_client

        # Connect
        await event_bus.connect()

        # Get nonexistent key
        result = await event_bus.get('/nonexistent')

        # Verify
        assert result is None


@pytest.mark.asyncio
async def test_get_when_disconnected(event_bus):
    """Test get fails when disconnected."""
    result = await event_bus.get('/test/key')
    assert result is None


@pytest.mark.asyncio
async def test_delete_operation(event_bus):
    """Test delete operation."""
    with patch('etcd3.client') as mock_client_factory:
        mock_client = MagicMock()
        mock_client.put = MagicMock()
        mock_client.get = MagicMock(return_value=(b'ok', None))
        mock_client.delete = MagicMock()

        mock_client_factory.return_value = mock_client

        # Connect
        await event_bus.connect()

        # Delete
        result = await event_bus.delete('/test/key')

        # Verify
        assert result is True
        mock_client.delete.assert_called()


@pytest.mark.asyncio
async def test_health_check_pass(event_bus):
    """Test successful health check."""
    with patch('etcd3.client') as mock_client_factory:
        mock_client = MagicMock()
        mock_client.put = MagicMock()
        mock_client.get = MagicMock(return_value=(b'ok', None))

        mock_client_factory.return_value = mock_client

        # Connect (which includes health check)
        result = await event_bus.connect()

        # Verify
        assert result is True
        assert event_bus.is_connected()


@pytest.mark.asyncio
async def test_health_check_mismatch(event_bus):
    """Test health check fails with value mismatch."""
    with patch('etcd3.client') as mock_client_factory:
        mock_client = MagicMock()

        # Health check put succeeds but get returns wrong value
        call_count = {'put': 0, 'get': 0}

        def mock_put(*args, **kwargs):
            call_count['put'] += 1

        def mock_get(*args, **kwargs):
            call_count['get'] += 1
            return (b'wrong_value', None)

        mock_client.put = mock_put
        mock_client.get = mock_get

        mock_client_factory.return_value = mock_client

        # Try to connect
        result = await event_bus.connect()

        # Should fail due to health check
        assert result is False


@pytest.mark.asyncio
async def test_watch_notification(event_bus):
    """Test watch notifications trigger callback."""
    with patch('etcd3.client') as mock_client_factory:
        mock_client = MagicMock()
        mock_client.put = MagicMock()
        mock_client.get = MagicMock(return_value=(b'ok', None))

        # Mock watch_prefix
        mock_event = MagicMock()
        mock_event.key = b'/test/watched_key'
        mock_event.value = b'watched_value'
        mock_event.type = 0  # PUT event

        mock_response = MagicMock()
        mock_response.events = [mock_event]

        mock_watch_iterator = iter([mock_response])
        mock_client.watch_prefix = MagicMock(return_value=mock_watch_iterator)

        mock_client_factory.return_value = mock_client

        # Connect
        await event_bus.connect()

        # Set up callback
        notifications = []

        def callback(event):
            notifications.append(event)

        # Start watch
        result = await event_bus.watch('/test/', callback)
        assert result is True

        # Wait a bit for background task
        await asyncio.sleep(0.2)

        # Clean up
        await event_bus.disconnect()


@pytest.mark.asyncio
async def test_watch_when_disconnected(event_bus):
    """Test watch fails when disconnected."""
    def callback(event):
        pass

    result = await event_bus.watch('/test/', callback)
    assert result is False


@pytest.mark.asyncio
async def test_transaction_success(event_bus):
    """Test successful transaction."""
    with patch('etcd3.client') as mock_client_factory:
        mock_client = MagicMock()
        mock_client.put = MagicMock()
        mock_client.get = MagicMock(return_value=(b'ok', None))
        mock_client.transaction = MagicMock(return_value=(True, []))

        mock_client_factory.return_value = mock_client

        # Connect
        await event_bus.connect()

        # Execute transaction
        result = await event_bus.transaction(
            compare=[],
            success=[],
            failure=[]
        )

        # Verify
        assert result is True
        mock_client.transaction.assert_called()


@pytest.mark.asyncio
async def test_transaction_failure(event_bus):
    """Test failed transaction."""
    with patch('etcd3.client') as mock_client_factory:
        mock_client = MagicMock()
        mock_client.put = MagicMock()
        mock_client.get = MagicMock(return_value=(b'ok', None))
        mock_client.transaction = MagicMock(return_value=(False, []))

        mock_client_factory.return_value = mock_client

        # Connect
        await event_bus.connect()

        # Execute transaction
        result = await event_bus.transaction(
            compare=[],
            success=[],
            failure=[]
        )

        # Verify
        assert result is False


@pytest.mark.asyncio
async def test_transaction_when_disconnected(event_bus):
    """Test transaction fails when disconnected."""
    result = await event_bus.transaction(
        compare=[],
        success=[],
        failure=[]
    )
    assert result is False


@pytest.mark.asyncio
async def test_get_prefix(event_bus):
    """Test get_prefix operation."""
    with patch('etcd3.client') as mock_client_factory:
        mock_client = MagicMock()
        mock_client.put = MagicMock()
        mock_client.get = MagicMock(return_value=(b'ok', None))

        # Mock get_prefix to return multiple key-value pairs
        mock_metadata1 = MagicMock()
        mock_metadata1.key = b'/test/key1'

        mock_metadata2 = MagicMock()
        mock_metadata2.key = b'/test/key2'

        mock_get_prefix_result = [
            (b'value1', mock_metadata1),
            (b'value2', mock_metadata2),
        ]

        mock_client.get_prefix = MagicMock(return_value=mock_get_prefix_result)

        mock_client_factory.return_value = mock_client

        # Connect
        await event_bus.connect()

        # Get prefix
        result = await event_bus.get_prefix('/test/')

        # Verify
        assert '/test/key1' in result
        assert result['/test/key1'] == 'value1'
        assert '/test/key2' in result
        assert result['/test/key2'] == 'value2'


@pytest.mark.asyncio
async def test_get_prefix_when_disconnected(event_bus):
    """Test get_prefix fails when disconnected."""
    result = await event_bus.get_prefix('/test/')
    assert result == {}


@pytest.mark.asyncio
async def test_multiple_operations_sequence(event_bus):
    """Test sequence of multiple operations."""
    with patch('etcd3.client') as mock_client_factory:
        mock_client = MagicMock()
        mock_client.put = MagicMock()
        mock_client.get = MagicMock()
        mock_client.delete = MagicMock()

        # Set up mock responses
        responses = {
            'connect': (b'ok', None),
            'get1': (b'value1', None),
            'get2': (None, None),
        }

        def mock_get(*args, **kwargs):
            if mock_get.call_count == 1:  # Health check
                return responses['connect']
            elif mock_get.call_count == 2:  # First get after put
                return responses['get1']
            else:  # Get after delete
                return responses['get2']

        mock_get.call_count = 0

        def wrapped_get(*args, **kwargs):
            mock_get.call_count += 1
            return mock_get(*args, **kwargs)

        mock_client.get = wrapped_get

        mock_client_factory.return_value = mock_client

        # Connect
        result = await event_bus.connect()
        assert result is True

        # Put
        result = await event_bus.put('/test/key', 'value1')
        assert result is True

        # Get after put
        result = await event_bus.get('/test/key')
        assert result == 'value1'

        # Delete
        result = await event_bus.delete('/test/key')
        assert result is True

        # Get after delete
        result = await event_bus.get('/test/key')
        assert result is None


@pytest.mark.asyncio
async def test_bytes_decoding(event_bus):
    """Test proper decoding of bytes from etcd."""
    with patch('etcd3.client') as mock_client_factory:
        mock_client = MagicMock()
        mock_client.put = MagicMock()

        # Set up get to return ok for health check, then test_value
        get_calls = [0]
        def mock_get(*args, **kwargs):
            get_calls[0] += 1
            if get_calls[0] == 1:  # Health check
                return (b'ok', None)
            else:  # Actual get
                return (b'test_value', None)

        mock_client.get = mock_get

        mock_client_factory.return_value = mock_client

        # Connect
        await event_bus.connect()

        # Get and verify decoding
        result = await event_bus.get('/test/key')
        assert isinstance(result, str)
        assert result == 'test_value'


@pytest.mark.asyncio
async def test_error_handling_on_put_exception(event_bus):
    """Test error handling when put raises exception."""
    with patch('etcd3.client') as mock_client_factory:
        mock_client = MagicMock()
        mock_client.put = MagicMock(side_effect=Exception("etcd error"))
        mock_client.get = MagicMock(return_value=(b'ok', None))

        mock_client_factory.return_value = mock_client

        # Connect
        await event_bus.connect()

        # Try to put - should handle exception gracefully
        result = await event_bus.put('/test/key', 'value')
        assert result is False


@pytest.mark.asyncio
async def test_error_handling_on_get_exception(event_bus):
    """Test error handling when get raises exception."""
    with patch('etcd3.client') as mock_client_factory:
        mock_client = MagicMock()
        mock_client.put = MagicMock()
        mock_client.get = MagicMock(side_effect=Exception("etcd error"))

        # For health check, make it return ok first time
        get_calls = [0]

        def mock_get_with_side_effect(*args, **kwargs):
            get_calls[0] += 1
            if get_calls[0] == 1:  # Health check
                return (b'ok', None)
            else:
                raise Exception("etcd error")

        mock_client.get = mock_get_with_side_effect

        mock_client_factory.return_value = mock_client

        # Connect
        await event_bus.connect()

        # Try to get - should handle exception gracefully
        result = await event_bus.get('/test/key')
        assert result is None
