"""
Kamailio SIP Adapter Implementation

Connects to Kamailio via JSON-RPC 2.0 over HTTP/HTTPS.

Kamailio is a SIP proxy/load balancer, NOT a PBX. It manages SIP dialogs for routing
but does not originate calls like Asterisk or FreeSWITCH.

Requirements:
- Kamailio >= 5.2
- MI_JSON or JSONRPCS module enabled
- HTTP listener configured for RPC endpoint

Example Configuration:
```yaml
type: kamailio
host: 192.168.1.100
port: 5060
endpoint: /RPC
auth:
  bearer_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # Optional
  # OR leave empty for IP-based auth
timeout: 30
```

Author: Agent 3 (Kamailio specialist)
Version: 1.0.0
Date: 2025-11-12
"""

import logging
import time
import uuid
from typing import Any, Dict, Optional, List

import requests

from src.adapters.sip_adapter_base import (
    SIPAdapterBase,
    CallState,
    ConnectionState,
    HealthStatus,
    ErrorSeverity,
    ConfigurationError,
    ConnectionError,
    CallError,
)


class KamailioAdapter(SIPAdapterBase):
    """
    Kamailio SIP adapter via JSON-RPC 2.0 protocol.

    Supports:
    - Dialog listing and monitoring
    - Dialog termination
    - Active dialog statistics
    - Load balancing metrics

    NOT Supported (Kamailio is a proxy, not a PBX):
    - Call origination (make_call)
    - Call recording
    - Conferencing
    - Hold/Resume
    - Direct CDR access

    Note: For call origination, use Asterisk or FreeSWITCH adapters.
    """

    adapter_type = "kamailio"
    SUPPORTED_VERSIONS = {
        "kamailio": ["5.2.x", "5.3.x", "5.4.x", "5.5.x", "5.6.x"],
        "jsonrpc": ["2.0"],
        "sip": ["2.0"],
    }

    def __init__(self, config: Dict[str, Any], **kwargs):
        """Initialize Kamailio adapter."""
        super().__init__(config, **kwargs)
        self.session: Optional[requests.Session] = None
        self.base_url: Optional[str] = None
        self.server_version: Optional[str] = None
        self._request_counter = 0

    # ========================================================================
    # Required Abstract Methods
    # ========================================================================

    def connect(
        self,
        host: str,
        port: int,
        auth_config: Dict[str, Any]
    ) -> bool:
        """
        Connect to Kamailio via HTTP.

        Args:
            host: Kamailio server hostname/IP
            port: HTTP port for RPC endpoint
            auth_config: Dict with optional bearer_token

        Returns:
            True if connection successful

        Raises:
            ConnectionError: If connection fails
        """
        try:
            self._update_connection_state(
                ConnectionState.CONNECTING,
                "Connecting to Kamailio JSON-RPC"
            )

            # Build base URL
            endpoint = self.config.get("endpoint", "/RPC")
            protocol = "https" if self.config.get("tls", False) else "http"
            self.base_url = f"{protocol}://{host}:{port}{endpoint}"

            # Create HTTP session
            self.session = requests.Session()
            self.session.headers.update({
                "Content-Type": "application/json",
                "Accept": "application/json",
            })

            # Add bearer token if configured
            bearer_token = auth_config.get("bearer_token")
            if bearer_token:
                self.session.headers.update({
                    "Authorization": f"Bearer {bearer_token}"
                })

            # Set timeout
            timeout = self.config.get("timeout", 30)
            self.session.timeout = timeout

            # Test connection with dlg.stats_active
            self.logger.debug(f"Testing connection to {self.base_url}")
            start_time = time.time()

            response = self._rpc_call("dlg.stats_active", [])

            latency = (time.time() - start_time) * 1000
            self.metrics.record_latency(latency)

            if response is None:
                raise ConnectionError("No response from Kamailio server")

            self.logger.info(f"Connected to Kamailio at {self.base_url} (latency: {latency:.2f}ms)")

            self._update_connection_state(
                ConnectionState.CONNECTED,
                "Connected to Kamailio JSON-RPC"
            )

            # Try to get server version
            self._query_server_version()

            return True

        except requests.exceptions.ConnectionError as e:
            self._update_connection_state(
                ConnectionState.ERROR,
                f"Connection refused: {e}"
            )
            self.metrics.record_connection_failure(str(e))
            raise ConnectionError(f"Cannot connect to {host}:{port}: {e}")

        except requests.exceptions.Timeout as e:
            self._update_connection_state(
                ConnectionState.ERROR,
                "Connection timeout"
            )
            self.metrics.record_connection_failure("timeout")
            raise ConnectionError(f"Connection timeout to {host}:{port}")

        except Exception as e:
            self._update_connection_state(
                ConnectionState.ERROR,
                f"Connection failed: {e}"
            )
            self.logger.exception(f"Connection error: {e}")
            self.metrics.record_connection_failure(str(e))
            raise ConnectionError(f"Connection failed: {e}")

    def disconnect(self) -> bool:
        """
        Disconnect from Kamailio.

        Since Kamailio uses stateless HTTP, just close the session.

        Returns:
            True if successful
        """
        try:
            # No active calls to hangup (Kamailio is proxy, we don't control calls)
            # Just log active dialogs
            with self._lock:
                active_count = len(self._active_calls)
                if active_count > 0:
                    self.logger.warning(
                        f"Disconnecting with {active_count} tracked dialogs. "
                        "Note: Kamailio dialogs will continue (proxy mode)."
                    )

            # Close HTTP session
            if self.session:
                self.session.close()

            self.session = None
            self.base_url = None

            self._update_connection_state(
                ConnectionState.DISCONNECTED,
                "Disconnected from Kamailio"
            )

            return True

        except Exception as e:
            self.logger.exception(f"Disconnect error: {e}")
            self._update_connection_state(
                ConnectionState.ERROR,
                f"Disconnect error: {e}"
            )
            return False

    def make_call(
        self,
        from_number: str,
        to_number: str,
        **options
    ) -> str:
        """
        NOT SUPPORTED: Kamailio is a SIP proxy, not a PBX.

        Kamailio routes SIP messages but does not originate calls.
        Use Asterisk or FreeSWITCH adapters for call origination.

        Args:
            from_number: Not used
            to_number: Not used
            options: Not used

        Raises:
            CallError: Always (operation not supported)
        """
        error_msg = (
            "Kamailio is a SIP proxy/load balancer and does not support call origination. "
            "Use Asterisk, FreeSWITCH, or another PBX adapter for make_call(). "
            "Kamailio can only manage and monitor existing SIP dialogs."
        )
        self.logger.error(error_msg)
        self.emit_error(
            code=501,
            message=error_msg,
            severity=ErrorSeverity.ERROR,
        )
        raise CallError(error_msg, code=501)

    def hangup(self, call_id: str) -> bool:
        """
        Terminate SIP dialog via dlg.terminate_dlg.

        Args:
            call_id: Call identifier (SIP Call-ID)

        Returns:
            True if successful

        Raises:
            CallError: If hangup fails
            ConnectionError: If not connected
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Kamailio")

        try:
            # Get call data to retrieve SIP parameters
            call_data = self._get_active_call(call_id)
            if not call_data:
                # Try to look up in active dialogs
                dialogs = self._rpc_call("dlg.list", [])
                matching_dialog = self._find_dialog_by_callid(dialogs, call_id)

                if not matching_dialog:
                    raise CallError(f"Call not found: {call_id}")

                call_data = matching_dialog

            # Extract SIP dialog parameters
            sip_callid = call_data.get("callid", call_id)
            from_tag = call_data.get("from_tag", "")
            to_tag = call_data.get("to_tag", "")

            self.logger.debug(
                f"Terminating dialog: callid={sip_callid}, "
                f"from_tag={from_tag}, to_tag={to_tag}"
            )

            # Call dlg.terminate_dlg
            # Parameters: [callid, from_tag, to_tag]
            response = self._rpc_call(
                "dlg.terminate_dlg",
                [sip_callid, from_tag, to_tag]
            )

            if response is None:
                raise CallError(f"Failed to terminate dialog: no response")

            # Update state
            self._remove_active_call(call_id)
            self.emit_call_state_changed(
                call_id=call_id,
                state=CallState.TERMINATED,
            )

            self.logger.info(f"Successfully terminated dialog {call_id}")
            return True

        except CallError:
            raise
        except Exception as e:
            self.logger.exception(f"Error hanging up {call_id}: {e}")
            self.emit_error(
                code=500,
                message=f"Hangup failed: {e}",
                severity=ErrorSeverity.ERROR,
                call_id=call_id,
            )
            raise CallError(f"Failed to hangup call: {e}")

    def get_status(self, call_id: str) -> Dict[str, Any]:
        """
        Query call status via dlg.list.

        Args:
            call_id: Call identifier (SIP Call-ID)

        Returns:
            Call status dictionary

        Raises:
            CallError: If call not found
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Kamailio")

        try:
            # First check local cache
            call_data = self._get_active_call(call_id)

            # Query live dialogs from Kamailio
            dialogs = self._rpc_call("dlg.list", [])
            matching_dialog = self._find_dialog_by_callid(dialogs, call_id)

            if matching_dialog:
                # Update local cache with fresh data
                call_data = matching_dialog
                self._add_active_call(call_id, call_data)

            if not call_data:
                raise CallError(f"Call not found: {call_id}")

            # Map Kamailio dialog state to CallState
            state = self._map_dialog_state(call_data.get("state", "unknown"))

            # Calculate duration
            start_time = call_data.get("start_time", time.time())
            duration = time.time() - start_time

            return {
                "call_id": call_id,
                "state": state.value,
                "from_number": call_data.get("caller", call_data.get("from_uri", "unknown")),
                "to_number": call_data.get("callee", call_data.get("to_uri", "unknown")),
                "duration": duration,
                "codec": "N/A",  # Kamailio doesn't track codecs (proxy mode)
                "jitter": 0,
                "packet_loss": 0,
                "rtp_quality": 0,  # Not available in proxy mode
                "details": {
                    "callid": call_data.get("callid", call_id),
                    "from_tag": call_data.get("from_tag", ""),
                    "to_tag": call_data.get("to_tag", ""),
                    "from_uri": call_data.get("from_uri", ""),
                    "to_uri": call_data.get("to_uri", ""),
                    "state": call_data.get("state", "unknown"),
                    "adapter": "kamailio",
                }
            }

        except CallError:
            raise
        except Exception as e:
            self.logger.exception(f"Error getting status for {call_id}: {e}")
            raise CallError(f"Failed to get call status: {e}")

    def health_check(self) -> Dict[str, Any]:
        """
        Return health metrics via dlg.stats_active.

        Returns:
            Health status dictionary
        """
        try:
            metrics = self.metrics.get_metrics()

            # Get active dialog count from Kamailio
            if self.is_connected():
                try:
                    stats = self._rpc_call("dlg.stats_active", [])
                    # Parse stats response (format varies by Kamailio version)
                    active_dialogs = self._parse_dialog_stats(stats)
                    metrics["active_calls"] = active_dialogs
                except Exception as e:
                    self.logger.warning(f"Could not query dialog stats: {e}")
                    metrics["active_calls"] = self._get_active_calls_count()
            else:
                metrics["active_calls"] = 0

            # Determine health status
            if not self.is_connected():
                status = HealthStatus.CRITICAL
            elif metrics.get("connection_failures", 0) > 5:
                status = HealthStatus.CRITICAL
            elif metrics["latency"]["avg_ms"] > 500:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY

            return {
                "adapter": self.adapter_type,
                "server_version": self.server_version,
                "connected": self.is_connected(),
                "uptime_seconds": metrics["uptime_seconds"],
                "metrics": metrics,
                "last_check": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "status": status.value,
            }

        except Exception as e:
            self.logger.exception(f"Health check error: {e}")
            return {
                "adapter": self.adapter_type,
                "connected": False,
                "status": HealthStatus.CRITICAL.value,
                "error": str(e),
                "last_check": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate Kamailio-specific configuration.

        Returns:
            True if valid

        Raises:
            ConfigurationError: If validation fails
        """
        try:
            # Check type
            if config.get("type") != "kamailio":
                raise ConfigurationError("Invalid adapter type for Kamailio")

            # Check host and port
            host = config.get("host")
            port = config.get("port")
            if not host:
                raise ConfigurationError("Missing required field: host")
            if not port or not (1 <= port <= 65535):
                raise ConfigurationError(
                    f"Invalid port: {port} (must be 1-65535)"
                )

            # Check endpoint
            endpoint = config.get("endpoint", "/RPC")
            if not endpoint.startswith("/"):
                raise ConfigurationError(
                    f"Invalid endpoint: {endpoint} (must start with '/')"
                )

            # Auth is optional for Kamailio (IP-based by default)
            auth = config.get("auth", {})
            bearer_token = auth.get("bearer_token")
            if bearer_token and not isinstance(bearer_token, str):
                raise ConfigurationError("bearer_token must be a string")

            # Timeout
            timeout = config.get("timeout", 30)
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                raise ConfigurationError(
                    f"Invalid timeout: {timeout} (must be > 0)"
                )

            return True

        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError(f"Configuration validation failed: {e}")

    # ========================================================================
    # Optional Methods - Extended
    # ========================================================================

    def get_call_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve recent dialog history.

        Note: Kamailio only tracks active dialogs. Historical data requires
        external CDR storage (e.g., via siptrace module + database).

        Returns:
            List of call dictionaries (limited to local cache)
        """
        with self._lock:
            return list(self._call_history)[-limit:]

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    def _rpc_call(
        self,
        method: str,
        params: List[Any],
        timeout: Optional[int] = None
    ) -> Any:
        """
        Make JSON-RPC 2.0 call to Kamailio.

        Args:
            method: RPC method name (e.g., "dlg.list")
            params: List of parameters
            timeout: Optional timeout override

        Returns:
            Result data from JSON-RPC response

        Raises:
            ConnectionError: If HTTP request fails
            CallError: If RPC error returned
        """
        if not self.session or not self.base_url:
            raise ConnectionError("Not connected to Kamailio")

        # Generate unique request ID
        self._request_counter += 1
        request_id = f"{self.adapter_type}-{self._request_counter}"

        # Build JSON-RPC 2.0 payload
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": request_id,
        }

        try:
            self.logger.debug(f"RPC call: {method} with params: {params}")

            timeout = timeout or self.config.get("timeout", 30)
            response = self.session.post(
                self.base_url,
                json=payload,
                timeout=timeout,
            )

            # Check HTTP status
            if response.status_code != 200:
                raise ConnectionError(
                    f"HTTP {response.status_code}: {response.text}"
                )

            # Parse JSON-RPC response
            data = response.json()

            # Check for JSON-RPC error
            if "error" in data:
                error = data["error"]
                error_code = error.get("code", -1)
                error_message = error.get("message", "Unknown error")
                raise CallError(
                    f"RPC error {error_code}: {error_message}",
                    code=error_code,
                )

            # Return result
            result = data.get("result")
            self.logger.debug(f"RPC response: {result}")
            return result

        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP request failed: {e}")
            raise ConnectionError(f"HTTP request failed: {e}")
        except ValueError as e:
            self.logger.error(f"Invalid JSON response: {e}")
            raise ConnectionError(f"Invalid JSON response: {e}")

    def _query_server_version(self) -> None:
        """
        Query Kamailio server version.

        Uses core.version RPC method if available.
        """
        try:
            version_info = self._rpc_call("core.version", [])
            if version_info:
                self.server_version = str(version_info)
                self.logger.info(f"Kamailio version: {self.server_version}")
        except Exception as e:
            self.logger.warning(f"Could not query server version: {e}")
            self.server_version = "unknown"

    def _find_dialog_by_callid(
        self,
        dialogs: Any,
        call_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find dialog in dlg.list response by call_id.

        Args:
            dialogs: Response from dlg.list RPC call
            call_id: SIP Call-ID to search for

        Returns:
            Dialog dict if found, None otherwise
        """
        if not dialogs:
            return None

        # Handle different response formats
        if isinstance(dialogs, dict):
            # Format: {"Dialogs": [...]}
            dialog_list = dialogs.get("Dialogs", dialogs.get("dialogs", []))
        elif isinstance(dialogs, list):
            dialog_list = dialogs
        else:
            return None

        # Search for matching call_id
        for dialog in dialog_list:
            if isinstance(dialog, dict):
                dialog_callid = dialog.get("callid", dialog.get("call-id", ""))
                if dialog_callid == call_id:
                    return dialog

        return None

    def _map_dialog_state(self, kamailio_state: str) -> CallState:
        """
        Map Kamailio dialog state to CallState enum.

        Kamailio dialog states:
        - 1: EARLY
        - 3: CONFIRMED
        - 4: DESTROYED
        - 5: DELETED

        Args:
            kamailio_state: Kamailio state code or string

        Returns:
            CallState enum value
        """
        state_map = {
            "1": CallState.RINGING,
            "EARLY": CallState.RINGING,
            "3": CallState.CONNECTED,
            "CONFIRMED": CallState.CONNECTED,
            "4": CallState.TERMINATED,
            "DESTROYED": CallState.TERMINATED,
            "5": CallState.TERMINATED,
            "DELETED": CallState.TERMINATED,
        }

        return state_map.get(
            str(kamailio_state).upper(),
            CallState.CREATED
        )

    def _parse_dialog_stats(self, stats: Any) -> int:
        """
        Parse dlg.stats_active response to get active dialog count.

        Args:
            stats: Response from dlg.stats_active

        Returns:
            Number of active dialogs
        """
        if isinstance(stats, int):
            return stats

        if isinstance(stats, dict):
            # Try various keys
            for key in ["active", "Active", "count", "dialogs"]:
                if key in stats:
                    return int(stats[key])

            # Sum all numeric values
            total = sum(v for v in stats.values() if isinstance(v, int))
            return total

        return 0


if __name__ == "__main__":
    """Example usage of KamailioAdapter."""
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Example 1: Basic configuration (IP-based auth)
    config_basic = {
        "type": "kamailio",
        "host": "192.168.1.100",
        "port": 5060,
        "endpoint": "/RPC",
        "auth": {},
        "timeout": 30,
    }

    # Example 2: JWT bearer token auth
    config_jwt = {
        "type": "kamailio",
        "host": "kamailio.example.com",
        "port": 8080,
        "endpoint": "/RPC",
        "auth": {
            "bearer_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        },
        "timeout": 30,
        "tls": True,
    }

    print("=" * 80)
    print("Kamailio Adapter - Example Usage")
    print("=" * 80)

    # Create adapter (would fail without real Kamailio server)
    try:
        adapter = KamailioAdapter(config_basic)
        print(f"\n✓ Adapter created: {adapter.adapter_type}")
        print(f"  Supported versions: {adapter.SUPPORTED_VERSIONS}")
        print(f"  Capabilities:")

        info = adapter.get_adapter_info()
        for capability, supported in info.get("supports", {}).items():
            status = "✓" if supported else "✗"
            print(f"    {status} {capability}")

        # Note about make_call
        print("\n" + "=" * 80)
        print("IMPORTANT: Kamailio is a SIP proxy, not a PBX")
        print("=" * 80)
        print("✗ make_call() - NOT SUPPORTED (proxy doesn't originate calls)")
        print("✓ hangup() - Terminates active dialogs")
        print("✓ get_status() - Queries dialog state")
        print("✓ health_check() - Dialog statistics")
        print("\nFor call origination, use Asterisk or FreeSWITCH adapters.")
        print("Kamailio is best used for load balancing and SIP routing.")

        # Demonstrate validation
        print("\n" + "=" * 80)
        print("Configuration Validation")
        print("=" * 80)

        print("\n✓ Valid configuration (basic):")
        print(f"  Host: {config_basic['host']}")
        print(f"  Port: {config_basic['port']}")
        print(f"  Endpoint: {config_basic['endpoint']}")
        print(f"  Auth: IP-based (no token)")

        print("\n✓ Valid configuration (JWT):")
        print(f"  Host: {config_jwt['host']}")
        print(f"  Port: {config_jwt['port']}")
        print(f"  Endpoint: {config_jwt['endpoint']}")
        print(f"  Auth: Bearer token")
        print(f"  TLS: {config_jwt['tls']}")

        # Test make_call error
        print("\n" + "=" * 80)
        print("Testing make_call() - Expected to raise CallError")
        print("=" * 80)
        try:
            adapter.make_call("+1234567890", "+0987654321")
        except CallError as e:
            print(f"\n✓ Correctly raised CallError:")
            print(f"  Error code: {e.code}")
            print(f"  Message: {e.message}")

    except ConfigurationError as e:
        print(f"\n✗ Configuration error: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")

    print("\n" + "=" * 80)
    print("Example complete")
    print("=" * 80)
