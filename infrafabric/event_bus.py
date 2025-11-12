"""
Event Bus for Real-time Coordination

Provides etcd3-based event bus infrastructure for real-time coordination
in InfraFabric, replacing 30-second git polling with instant event propagation.

Classes:
    EventBus: Main event bus class for distributed coordination

Author: InfraFabric Research
Date: November 2025
"""

import asyncio
import os
from typing import Optional, Callable, Any, List
import logging
from concurrent.futures import ThreadPoolExecutor

try:
    import etcd3
except ImportError:
    # etcd3 might not be installed in test environments
    # Tests will mock this dependency
    etcd3 = None

logger = logging.getLogger(__name__)


class EventBus:
    """Real-time event bus for IF.coordinator using etcd3

    Provides async interface for:
    - Put/get key-value operations
    - Watch for key changes with callbacks
    - Atomic compare-and-swap transactions
    - Health checks and connection management
    - Environment-based configuration

    Attributes:
        host (str): etcd server hostname
        port (int): etcd server port
        client: etcd3 client instance
        _watch_callbacks (dict): Maps prefixes to watch callbacks
        _executor: ThreadPoolExecutor for running blocking operations
    """

    def __init__(
        self,
        host: str = None,
        port: int = None
    ):
        """Initialize EventBus with connection parameters.

        Args:
            host: etcd server hostname (default: localhost)
            port: etcd server port (default: 2379)

        Environment Variables:
            IF_ETCD_HOST: Override hostname
            IF_ETCD_PORT: Override port
        """
        self.host = host or os.getenv('IF_ETCD_HOST', 'localhost')
        self.port = port or int(os.getenv('IF_ETCD_PORT', '2379'))
        self.client = None
        self._watch_callbacks = {}
        self._watch_tasks = {}
        self._executor = ThreadPoolExecutor(max_workers=5)
        self._connected = False

    async def connect(self) -> bool:
        """Establish connection to etcd.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if etcd3 is None:
                logger.error("etcd3 module not available. Install with: pip install etcd3>=0.12.0")
                return False

            # Create etcd3 client (synchronous, so run in executor)
            self.client = await asyncio.get_event_loop().run_in_executor(
                self._executor,
                lambda: etcd3.client(
                    host=self.host,
                    port=self.port,
                    timeout=5
                )
            )

            # Test connection with health check
            health = await self.health_check()
            if health:
                self._connected = True
                logger.info(f"Connected to etcd at {self.host}:{self.port}")
                return True
            else:
                self._connected = False
                logger.error(f"Health check failed for etcd at {self.host}:{self.port}")
                return False

        except Exception as e:
            self._connected = False
            logger.error(f"Failed to connect to etcd at {self.host}:{self.port}: {e}")
            return False

    async def disconnect(self):
        """Close connection to etcd and cancel all watches.

        Gracefully shuts down event bus, cleaning up resources.
        """
        try:
            # Cancel all watch tasks
            for prefix, task in self._watch_tasks.items():
                if task and not task.done():
                    task.cancel()
                    logger.info(f"Cancelled watch task for prefix: {prefix}")

            self._watch_tasks.clear()
            self._watch_callbacks.clear()

            # Close client
            if self.client:
                await asyncio.get_event_loop().run_in_executor(
                    self._executor,
                    self.client.close
                )
                self.client = None
                self._connected = False
                logger.info("Disconnected from etcd")

        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

    async def put(self, key: str, value: str) -> bool:
        """Store a key-value pair in etcd.

        Args:
            key: The key to store
            value: The value to store

        Returns:
            bool: True if successful, False otherwise
        """
        if not self._connected or not self.client:
            logger.error(f"Not connected to etcd, cannot put {key}")
            return False

        try:
            await asyncio.get_event_loop().run_in_executor(
                self._executor,
                lambda: self.client.put(key, value)
            )
            logger.debug(f"Put {key} = {value}")
            return True
        except Exception as e:
            logger.error(f"Failed to put {key}: {e}")
            return False

    async def get(self, key: str) -> Optional[str]:
        """Retrieve value by key from etcd.

        Args:
            key: The key to retrieve

        Returns:
            Optional[str]: The value if found, None otherwise
        """
        if not self._connected or not self.client:
            logger.error(f"Not connected to etcd, cannot get {key}")
            return None

        try:
            value, metadata = await asyncio.get_event_loop().run_in_executor(
                self._executor,
                lambda: self.client.get(key)
            )

            if value:
                result = value.decode('utf-8') if isinstance(value, bytes) else value
                logger.debug(f"Got {key} = {result}")
                return result
            else:
                logger.debug(f"Key {key} not found")
                return None

        except Exception as e:
            logger.error(f"Failed to get {key}: {e}")
            return None

    async def watch(self, prefix: str, callback: Callable) -> bool:
        """Watch for changes to keys with given prefix.

        Starts a background task that watches for changes and calls
        the callback for each event.

        Args:
            prefix: The key prefix to watch
            callback: Function to call on events: callback(event_type, key, value)

        Returns:
            bool: True if watch started successfully
        """
        if not self._connected or not self.client:
            logger.error(f"Not connected to etcd, cannot watch {prefix}")
            return False

        try:
            self._watch_callbacks[prefix] = callback

            # Start watch in background task
            task = asyncio.create_task(self._watch_loop(prefix, callback))
            self._watch_tasks[prefix] = task

            logger.info(f"Started watching prefix: {prefix}")
            return True

        except Exception as e:
            logger.error(f"Failed to start watch for {prefix}: {e}")
            return False

    async def _watch_loop(self, prefix: str, callback: Callable):
        """Background loop for watching key changes.

        Runs in executor to handle blocking watch operations.

        Args:
            prefix: The key prefix to watch
            callback: Function to call on events
        """
        try:
            loop = asyncio.get_event_loop()

            def _watch_generator():
                """Wrapper for etcd3 watch_prefix that yields events"""
                watch_iterator = self.client.watch_prefix(prefix)
                for response in watch_iterator:
                    yield response

            # Run the watch generator in executor
            watch_iterator = self.client.watch_prefix(prefix)

            for response in watch_iterator:
                # Process events in executor context
                await loop.run_in_executor(
                    self._executor,
                    self._process_watch_event,
                    response,
                    callback,
                    prefix
                )

        except asyncio.CancelledError:
            logger.info(f"Watch cancelled for prefix: {prefix}")
        except Exception as e:
            logger.error(f"Watch error for {prefix}: {e}")

    def _process_watch_event(self, response, callback: Callable, prefix: str):
        """Process a single watch event and call the callback.

        Args:
            response: etcd3 watch response
            callback: User callback function
            prefix: The watched prefix
        """
        try:
            for event in response.events:
                key = event.key.decode('utf-8') if isinstance(event.key, bytes) else event.key

                if event.type == 0:  # PUT event
                    value = event.value.decode('utf-8') if isinstance(event.value, bytes) else event.value
                    logger.debug(f"Watch event: PUT {key} = {value}")
                    callback({
                        'type': 'put',
                        'key': key,
                        'value': value,
                        'event': event
                    })

                elif event.type == 1:  # DELETE event
                    logger.debug(f"Watch event: DELETE {key}")
                    callback({
                        'type': 'delete',
                        'key': key,
                        'value': None,
                        'event': event
                    })

        except Exception as e:
            logger.error(f"Error processing watch event for {prefix}: {e}")

    async def transaction(
        self,
        compare: List,
        success: List,
        failure: List = None
    ) -> bool:
        """Execute atomic compare-and-swap transaction.

        Performs an atomic transaction on etcd, comparing conditions and
        executing success or failure operations based on comparison result.

        Example:
            # Atomic increment
            from etcd3.transactions import Value, Put
            compare = [Value('/counter') == '5']
            success = [Put('/counter', '6')]
            result = await bus.transaction(compare, success)

        Args:
            compare: List of comparison conditions (etcd3 compare objects)
            success: List of operations to execute if compare succeeds
            failure: List of operations to execute if compare fails (optional)

        Returns:
            bool: True if transaction succeeded, False otherwise
        """
        if not self._connected or not self.client:
            logger.error("Not connected to etcd, cannot execute transaction")
            return False

        try:
            failure = failure or []

            result = await asyncio.get_event_loop().run_in_executor(
                self._executor,
                lambda: self.client.transaction(
                    compare=compare,
                    success=success,
                    failure=failure
                )
            )

            # result is a tuple: (succeeded: bool, responses: list)
            succeeded = result[0] if isinstance(result, tuple) else result
            logger.debug(f"Transaction result: {succeeded}")
            return bool(succeeded)

        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            return False

    async def health_check(self) -> bool:
        """Check connection health to etcd.

        Performs a simple put/get test to verify etcd is accessible
        and responsive.

        Returns:
            bool: True if health check passed, False otherwise
        """
        if not self.client:
            logger.debug("No client available for health check")
            return False

        try:
            test_key = '/__health_check__'
            test_value = 'ok'

            # Put test value
            await asyncio.get_event_loop().run_in_executor(
                self._executor,
                lambda: self.client.put(test_key, test_value)
            )

            # Get test value
            value, _ = await asyncio.get_event_loop().run_in_executor(
                self._executor,
                lambda: self.client.get(test_key)
            )

            if value:
                actual = value.decode('utf-8') if isinstance(value, bytes) else value
                health = actual == test_value
                logger.debug(f"Health check: {health}")
                return health
            else:
                logger.warning("Health check: key not found after put")
                return False

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def is_connected(self) -> bool:
        """Check if currently connected to etcd.

        Returns:
            bool: True if connected, False otherwise
        """
        return self._connected and self.client is not None

    async def delete(self, key: str) -> bool:
        """Delete a key from etcd.

        Args:
            key: The key to delete

        Returns:
            bool: True if deletion successful, False otherwise
        """
        if not self._connected or not self.client:
            logger.error(f"Not connected to etcd, cannot delete {key}")
            return False

        try:
            await asyncio.get_event_loop().run_in_executor(
                self._executor,
                lambda: self.client.delete(key)
            )
            logger.debug(f"Deleted {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {key}: {e}")
            return False

    async def get_prefix(self, prefix: str) -> dict:
        """Get all keys with a given prefix.

        Args:
            prefix: The key prefix to search

        Returns:
            dict: Dictionary of key-value pairs matching the prefix
        """
        if not self._connected or not self.client:
            logger.error(f"Not connected to etcd, cannot get prefix {prefix}")
            return {}

        try:
            results = {}

            values = await asyncio.get_event_loop().run_in_executor(
                self._executor,
                lambda: self.client.get_prefix(prefix)
            )

            for value, metadata in values:
                key = metadata.key.decode('utf-8') if isinstance(metadata.key, bytes) else metadata.key
                val = value.decode('utf-8') if isinstance(value, bytes) else value
                results[key] = val

            logger.debug(f"Got {len(results)} keys with prefix {prefix}")
            return results

        except Exception as e:
            logger.error(f"Failed to get prefix {prefix}: {e}")
            return {}
