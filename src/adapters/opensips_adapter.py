"""
OpenSIPs SIP Adapter Implementation

Connects to OpenSIPs via MI (Management Interface) using JSON-RPC 2.0 over HTTP.

OpenSIPs is a SIP proxy/load balancer, NOT a PBX. It manages SIP dialogs for routing
but does not originate calls like Asterisk or FreeSWITCH.

Requirements:
- OpenSIPs >= 3.0
- MI_JSON or MI_HTTP module enabled
- HTTP listener configured for MI endpoint

Example Configuration:
```yaml
type: opensips
host: 192.168.1.100
port: 8888
endpoint: /mi
auth:
  api_key: abc123xyz  # Optional
  # OR leave empty for IP-based auth
timeout: 30
```

Author: Agent 5 (OpenSIPs specialist)
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


class OpenSIPSAdapter(SIPAdapterBase):
    """
    OpenSIPs SIP adapter via MI (Management Interface) JSON-RPC 2.0 protocol.

    Supports:
    - Dialog listing and monitoring
    - Dialog termination
    - Active dialog statistics
    - Load balancing metrics
    - User location management

    NOT Supported (OpenSIPs is a proxy, not a PBX):
    - Call origination (make_call)
    - Call recording (server-side)
    - Conferencing
    - Hold/Resume
    - Direct CDR access

    Note: For call origination, use Asterisk or FreeSWITCH adapters.
    """

    adapter_type = "opensips"
    SUPPORTED_VERSIONS = {
        "opensips": ["3.0.x", "3.1.x", "3.2.x", "3.3.x", "3.4.x"],
        "jsonrpc": ["2.0"],
        "sip": ["2.0"],
    }

    def __init__(self, config: Dict[str, Any], **kwargs):
        """Initialize OpenSIPs adapter."""
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
        Connect to OpenSIPs via HTTP MI interface.

        Args:
            host: OpenSIPs server hostname/IP
            port: HTTP port for MI endpoint (default 8888)
            auth_config: Dict with optional api_key

        Returns:
            True if connection successful

        Raises:
            ConnectionError: If connection fails
        """
        try:
            self._update_connection_state(
                ConnectionState.CONNECTING,
                "Connecting to OpenSIPs MI interface"
            )

            # Build base URL
            endpoint = self.config.get("endpoint", "/mi")
            protocol = "https" if self.config.get("tls", False) else "http"
            self.base_url = f"{protocol}://{host}:{port}{endpoint}"

            # Create HTTP session
            self.session = requests.Session()
            self.session.headers.update({
                "Content-Type": "application/json",
                "Accept": "application/json",
            })

            # Add API key if configured
            api_key = auth_config.get("api_key")
            if api_key:
                self.session.headers.update({
                    "X-API-Key": api_key
                })

            # Set timeout
            timeout = self.config.get("timeout", 30)
            self.session.timeout = timeout

            # Test connection with get_statistics
            self.logger.debug(f"Testing connection to {self.base_url}")
            start_time = time.time()

            response = self._rpc_call("get_statistics", ["dialog:"])

            latency = (time.time() - start_time) * 1000
            self.metrics.record_latency(latency)

            if response is None:
                raise ConnectionError("No response from OpenSIPs server")

            self.logger.info(f"Connected to OpenSIPs at {self.base_url} (latency: {latency:.2f}ms)")

            self._update_connection_state(
                ConnectionState.CONNECTED,
                "Connected to OpenSIPs MI interface"
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
        Disconnect from OpenSIPs.

        Since OpenSIPs uses stateless HTTP, just close the session.

        Returns:
            True if successful
        """
        try:
            # No active calls to hangup (OpenSIPs is proxy, we don't control calls)
            # Just log active dialogs
            with self._lock:
                active_count = len(self._active_calls)
                if active_count > 0:
                    self.logger.warning(
                        f"Disconnecting with {active_count} tracked dialogs. "
                        "Note: OpenSIPs dialogs will continue (proxy mode)."
                    )

            # Close HTTP session
            if self.session:
                self.session.close()

            self.session = None
            self.base_url = None

            self._update_connection_state(
                ConnectionState.DISCONNECTED,
                "Disconnected from OpenSIPs"
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
        NOT SUPPORTED: OpenSIPs is a SIP proxy, not a PBX.

        OpenSIPs routes SIP messages but does not originate calls.
        Use Asterisk or FreeSWITCH adapters for call origination.

        Args:
            from_number: Not used
            to_number: Not used
            options: Not used

        Raises:
            CallError: Always (operation not supported)
        """
        error_msg = (
            "OpenSIPs is a SIP proxy/load balancer and does not support call origination. "
            "Use Asterisk, FreeSWITCH, or another PBX adapter for make_call(). "
            "OpenSIPs can only manage and monitor existing SIP dialogs."
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
        Terminate SIP dialog via dlg_end_dlg.

        Args:
            call_id: Call identifier (SIP Call-ID)

        Returns:
            True if successful

        Raises:
            CallError: If hangup fails
            ConnectionError: If not connected
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to OpenSIPs")

        try:
            # Get call data to retrieve SIP parameters
            call_data = self._get_active_call(call_id)
            if not call_data:
                # Try to look up in active dialogs
                dialogs = self._rpc_call("dlg_list", [])
                matching_dialog = self._find_dialog_by_callid(dialogs, call_id)

                if not matching_dialog:
                    raise CallError(f"Call not found: {call_id}")

                call_data = matching_dialog

            # Extract dialog hash parameters
            # OpenSIPs uses dialog hash ID and entry ID
            dialog_id = call_data.get("dialog_id", "")
            h_entry = call_data.get("h_entry", "")
            h_id = call_data.get("h_id", "")

            self.logger.debug(
                f"Terminating dialog: dialog_id={dialog_id}, "
                f"h_entry={h_entry}, h_id={h_id}"
            )

            # Call dlg_end_dlg
            # Parameters: [h_entry, h_id] or [callid, from_tag, to_tag]
            if h_entry and h_id:
                response = self._rpc_call(
                    "dlg_end_dlg",
                    [str(h_entry), str(h_id)]
                )
            else:
                # Fallback to callid/tag method
                sip_callid = call_data.get("callid", call_id)
                from_tag = call_data.get("from_tag", "")
                to_tag = call_data.get("to_tag", "")
                response = self._rpc_call(
                    "dlg_end_dlg",
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
        Query call status via dlg_list.

        Args:
            call_id: Call identifier (SIP Call-ID)

        Returns:
            Call status dictionary

        Raises:
            CallError: If call not found
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to OpenSIPs")

        try:
            # First check local cache
            call_data = self._get_active_call(call_id)

            # Query live dialogs from OpenSIPs
            dialogs = self._rpc_call("dlg_list", [])
            matching_dialog = self._find_dialog_by_callid(dialogs, call_id)

            if matching_dialog:
                # Update local cache with fresh data
                call_data = matching_dialog
                self._add_active_call(call_id, call_data)

            if not call_data:
                raise CallError(f"Call not found: {call_id}")

            # Map OpenSIPs dialog state to CallState
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
                "codec": "N/A",  # OpenSIPs doesn't track codecs (proxy mode)
                "jitter": 0,
                "packet_loss": 0,
                "rtp_quality": 0,  # Not available in proxy mode
                "details": {
                    "callid": call_data.get("callid", call_id),
                    "h_entry": call_data.get("h_entry", ""),
                    "h_id": call_data.get("h_id", ""),
                    "from_tag": call_data.get("from_tag", ""),
                    "to_tag": call_data.get("to_tag", ""),
                    "from_uri": call_data.get("from_uri", ""),
                    "to_uri": call_data.get("to_uri", ""),
                    "state": call_data.get("state", "unknown"),
                    "adapter": "opensips",
                }
            }

        except CallError:
            raise
        except Exception as e:
            self.logger.exception(f"Error getting status for {call_id}: {e}")
            raise CallError(f"Failed to get call status: {e}")

    def health_check(self) -> Dict[str, Any]:
        """
        Return health metrics via get_statistics.

        Returns:
            Health status dictionary
        """
        try:
            metrics = self.metrics.get_metrics()

            # Get active dialog count from OpenSIPs
            if self.is_connected():
                try:
                    stats = self._rpc_call("get_statistics", ["dialog:"])
                    # Parse stats response
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
        Validate OpenSIPs-specific configuration.

        Returns:
            True if valid

        Raises:
            ConfigurationError: If validation fails
        """
        try:
            # Check type
            if config.get("type") != "opensips":
                raise ConfigurationError("Invalid adapter type for OpenSIPs")

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
            endpoint = config.get("endpoint", "/mi")
            if not endpoint.startswith("/"):
                raise ConfigurationError(
                    f"Invalid endpoint: {endpoint} (must start with '/')"
                )

            # Auth is optional for OpenSIPs (IP-based by default)
            auth = config.get("auth", {})
            api_key = auth.get("api_key")
            if api_key and not isinstance(api_key, str):
                raise ConfigurationError("api_key must be a string")

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

        Note: OpenSIPs only tracks active dialogs. Historical data requires
        external CDR storage (e.g., via acc module + database).

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
        Make JSON-RPC 2.0 call to OpenSIPs.

        Args:
            method: RPC method name (e.g., "dlg_list")
            params: List of parameters
            timeout: Optional timeout override

        Returns:
            Result data from JSON-RPC response

        Raises:
            ConnectionError: If HTTP request fails
            CallError: If RPC error returned
        """
        if not self.session or not self.base_url:
            raise ConnectionError("Not connected to OpenSIPs")

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
        Query OpenSIPs server version.

        Uses version RPC method if available.
        """
        try:
            version_info = self._rpc_call("version", [])
            if version_info:
                # OpenSIPs version response format varies
                if isinstance(version_info, dict):
                    self.server_version = version_info.get("Server", version_info.get("version", "unknown"))
                else:
                    self.server_version = str(version_info)
                self.logger.info(f"OpenSIPs version: {self.server_version}")
        except Exception as e:
            self.logger.warning(f"Could not query server version: {e}")
            self.server_version = "unknown"

    def _find_dialog_by_callid(
        self,
        dialogs: Any,
        call_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find dialog in dlg_list response by call_id.

        Args:
            dialogs: Response from dlg_list RPC call
            call_id: SIP Call-ID to search for

        Returns:
            Dialog dict if found, None otherwise
        """
        if not dialogs:
            return None

        # Handle different response formats
        if isinstance(dialogs, dict):
            # Format: {"Dialogs": [...]} or {"dialogs": [...]}
            dialog_list = dialogs.get("Dialogs", dialogs.get("dialogs", []))
        elif isinstance(dialogs, list):
            dialog_list = dialogs
        else:
            return None

        # Search for matching call_id
        for dialog in dialog_list:
            if isinstance(dialog, dict):
                dialog_callid = dialog.get("callid", dialog.get("call-id", dialog.get("call_id", "")))
                if dialog_callid == call_id:
                    return dialog

        return None

    def _map_dialog_state(self, opensips_state: str) -> CallState:
        """
        Map OpenSIPs dialog state to CallState enum.

        OpenSIPs dialog states:
        - 1: UNCONFIRMED (early)
        - 2: EARLY
        - 3: CONFIRMED (established)
        - 4: DELETED (terminated)

        Args:
            opensips_state: OpenSIPs state code or string

        Returns:
            CallState enum value
        """
        state_map = {
            "1": CallState.DIALING,
            "UNCONFIRMED": CallState.DIALING,
            "2": CallState.RINGING,
            "EARLY": CallState.RINGING,
            "3": CallState.CONNECTED,
            "CONFIRMED": CallState.CONNECTED,
            "4": CallState.TERMINATED,
            "DELETED": CallState.TERMINATED,
        }

        return state_map.get(
            str(opensips_state).upper(),
            CallState.CREATED
        )

    def _parse_dialog_stats(self, stats: Any) -> int:
        """
        Parse get_statistics response to get active dialog count.

        Args:
            stats: Response from get_statistics

        Returns:
            Number of active dialogs
        """
        if isinstance(stats, int):
            return stats

        if isinstance(stats, dict):
            # OpenSIPs statistics format: {"dialog:active_dialogs": 5, ...}
            for key in ["dialog:active_dialogs", "active_dialogs", "active", "count"]:
                if key in stats:
                    value = stats[key]
                    if isinstance(value, int):
                        return value
                    elif isinstance(value, str) and value.isdigit():
                        return int(value)

            # Sum all numeric values as fallback
            total = 0
            for key, value in stats.items():
                if "dialog" in key.lower():
                    if isinstance(value, int):
                        total += value
                    elif isinstance(value, str) and value.isdigit():
                        total += int(value)
            return total

        if isinstance(stats, list):
            # Some versions return array of stats
            for stat in stats:
                if isinstance(stat, dict) and "dialog" in str(stat).lower():
                    return self._parse_dialog_stats(stat)

        return 0


if __name__ == "__main__":
    """Example usage of OpenSIPSAdapter."""
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Example 1: Basic configuration (IP-based auth)
    config_basic = {
        "type": "opensips",
        "host": "192.168.1.100",
        "port": 8888,
        "endpoint": "/mi",
        "auth": {},
        "timeout": 30,
    }

    # Example 2: API key auth
    config_apikey = {
        "type": "opensips",
        "host": "opensips.example.com",
        "port": 8888,
        "endpoint": "/mi",
        "auth": {
            "api_key": "your-api-key-here"
        },
        "timeout": 30,
        "tls": True,
    }

    print("=" * 80)
    print("OpenSIPs Adapter - Example Usage")
    print("=" * 80)

    # Create adapter (would fail without real OpenSIPs server)
    try:
        adapter = OpenSIPSAdapter(config_basic)
        print(f"\n✓ Adapter created: {adapter.adapter_type}")
        print(f"  Supported versions: {adapter.SUPPORTED_VERSIONS}")
        print(f"  Capabilities:")

        info = adapter.get_adapter_info()
        for capability, supported in info.get("supports", {}).items():
            status = "✓" if supported else "✗"
            print(f"    {status} {capability}")

        # Note about make_call
        print("\n" + "=" * 80)
        print("IMPORTANT: OpenSIPs is a SIP proxy, not a PBX")
        print("=" * 80)
        print("✗ make_call() - NOT SUPPORTED (proxy doesn't originate calls)")
        print("✓ hangup() - Terminates active dialogs")
        print("✓ get_status() - Queries dialog state")
        print("✓ health_check() - Dialog statistics")
        print("\nFor call origination, use Asterisk or FreeSWITCH adapters.")
        print("OpenSIPs is best used for load balancing and SIP routing.")

        # Demonstrate validation
        print("\n" + "=" * 80)
        print("Configuration Validation")
        print("=" * 80)

        print("\n✓ Valid configuration (basic):")
        print(f"  Host: {config_basic['host']}")
        print(f"  Port: {config_basic['port']}")
        print(f"  Endpoint: {config_basic['endpoint']}")
        print(f"  Auth: IP-based (no API key)")

        print("\n✓ Valid configuration (API key):")
        print(f"  Host: {config_apikey['host']}")
        print(f"  Port: {config_apikey['port']}")
        print(f"  Endpoint: {config_apikey['endpoint']}")
        print(f"  Auth: API key")
        print(f"  TLS: {config_apikey['tls']}")

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

        # Key differences from Kamailio
        print("\n" + "=" * 80)
        print("OpenSIPs vs Kamailio Differences")
        print("=" * 80)
        print("OpenSIPs:")
        print("  - Default port: 8888 (MI interface)")
        print("  - Endpoint: /mi")
        print("  - Methods: dlg_end_dlg, dlg_list, get_statistics")
        print("  - Official Python package: opensips.mi (2024)")
        print("  - Hash-based dialog IDs (h_entry, h_id)")
        print("\nKamailio:")
        print("  - Default port: 5060 (shared with SIP)")
        print("  - Endpoint: /RPC")
        print("  - Methods: dlg.terminate_dlg, dlg.list, dlg.stats_active")
        print("  - Official Python package: kamcli")
        print("  - Simple Call-ID based dialog IDs")

    except ConfigurationError as e:
        print(f"\n✗ Configuration error: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")

    print("\n" + "=" * 80)
    print("Example complete")
    print("=" * 80)
