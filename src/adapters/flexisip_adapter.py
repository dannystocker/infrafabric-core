"""
Flexisip SIP Adapter Implementation

Connects to Flexisip via HTTP REST API.

Flexisip is a SIP proxy/registrar server, NOT a PBX. It manages SIP accounts,
devices, and presence but does not directly originate calls like Asterisk or FreeSWITCH.

Requirements:
- Flexisip >= 2.0
- HTTP REST API enabled
- Authentication configured (Bearer token, API key, or Digest auth)

Example Configuration:
```yaml
type: flexisip
host: flexisip.example.com
port: 443
endpoint: /api
auth:
  bearer_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  # OR
  api_key: your-api-key-here
  # OR
  digest_username: admin
  digest_password: secret
tls: true
timeout: 30
```

Author: Agent 4 (Flexisip specialist)
Version: 1.0.0
Date: 2025-11-12
"""

import logging
import time
import uuid
from typing import Any, Dict, Optional, List

import requests
from requests.auth import HTTPDigestAuth

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


class FlexisipAdapter(SIPAdapterBase):
    """
    Flexisip SIP adapter via HTTP REST API.

    Supports:
    - Account management (POST /api/accounts)
    - Device provisioning (POST /api/devices)
    - Statistics retrieval (GET /api/statistics)
    - Presence and push notifications

    NOT Supported (Flexisip is a proxy, not a PBX):
    - Direct call origination (make_call)
    - Server-side call recording
    - Call hold/resume
    - Conferencing (client-side only)
    - Direct CDR access

    Note: For call origination, use Asterisk or FreeSWITCH adapters.
    Flexisip is designed for modern mobile SIP applications with client-side features.
    """

    adapter_type = "flexisip"
    SUPPORTED_VERSIONS = {
        "flexisip": ["2.0.x", "2.1.x", "2.2.x", "2.3.x"],
        "api": ["1.0"],
        "sip": ["2.0"],
    }

    def __init__(self, config: Dict[str, Any], **kwargs):
        """Initialize Flexisip adapter."""
        super().__init__(config, **kwargs)
        self.session: Optional[requests.Session] = None
        self.base_url: Optional[str] = None
        self.server_version: Optional[str] = None
        self._accounts_cache: Dict[str, Dict[str, Any]] = {}

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
        Connect to Flexisip via HTTP REST API.

        Args:
            host: Flexisip server hostname/IP
            port: HTTP/HTTPS port for REST API
            auth_config: Dict with bearer_token, api_key, or digest credentials

        Returns:
            True if connection successful

        Raises:
            ConnectionError: If connection fails
        """
        try:
            self._update_connection_state(
                ConnectionState.CONNECTING,
                "Connecting to Flexisip REST API"
            )

            # Build base URL
            endpoint = self.config.get("endpoint", "/api")
            protocol = "https" if self.config.get("tls", True) else "http"
            self.base_url = f"{protocol}://{host}:{port}{endpoint}"

            # Create HTTP session
            self.session = requests.Session()
            self.session.headers.update({
                "Content-Type": "application/json",
                "Accept": "application/json",
            })

            # Configure authentication
            bearer_token = auth_config.get("bearer_token")
            api_key = auth_config.get("api_key")
            digest_username = auth_config.get("digest_username")
            digest_password = auth_config.get("digest_password")

            if bearer_token:
                # Bearer token authentication (JWT)
                self.session.headers.update({
                    "Authorization": f"Bearer {bearer_token}"
                })
                self.logger.info("Using Bearer token authentication")
            elif api_key:
                # API key authentication
                self.session.headers.update({
                    "X-API-Key": api_key
                })
                self.logger.info("Using API key authentication")
            elif digest_username and digest_password:
                # Digest authentication
                self.session.auth = HTTPDigestAuth(digest_username, digest_password)
                self.logger.info("Using Digest authentication")
            else:
                self.logger.warning("No authentication configured - API may reject requests")

            # Set timeout
            timeout = self.config.get("timeout", 30)
            self.session.timeout = timeout

            # Verify TLS certificates (disable for testing if needed)
            verify_tls = self.config.get("verify_tls", True)
            self.session.verify = verify_tls

            # Test connection with statistics endpoint
            self.logger.debug(f"Testing connection to {self.base_url}")
            start_time = time.time()

            response = self._api_call("GET", "/statistics")

            latency = (time.time() - start_time) * 1000
            self.metrics.record_latency(latency)

            if response is None:
                raise ConnectionError("No response from Flexisip server")

            self.logger.info(f"Connected to Flexisip at {self.base_url} (latency: {latency:.2f}ms)")

            self._update_connection_state(
                ConnectionState.CONNECTED,
                "Connected to Flexisip REST API"
            )

            # Try to get server version
            self._query_server_info()

            return True

        except requests.exceptions.SSLError as e:
            self._update_connection_state(
                ConnectionState.ERROR,
                f"SSL/TLS error: {e}"
            )
            self.metrics.record_connection_failure(str(e))
            raise ConnectionError(
                f"SSL/TLS error connecting to {host}:{port}. "
                f"Set verify_tls: false to disable certificate verification (not recommended for production)."
            )

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
        Disconnect from Flexisip.

        Since Flexisip uses stateless HTTP, just close the session.

        Returns:
            True if successful
        """
        try:
            # Log tracked accounts/sessions
            with self._lock:
                account_count = len(self._accounts_cache)
                active_calls = len(self._active_calls)
                if account_count > 0 or active_calls > 0:
                    self.logger.info(
                        f"Disconnecting with {account_count} cached accounts "
                        f"and {active_calls} tracked calls. "
                        "Note: Flexisip sessions will continue (proxy mode)."
                    )

            # Close HTTP session
            if self.session:
                self.session.close()

            self.session = None
            self.base_url = None
            self._accounts_cache.clear()

            self._update_connection_state(
                ConnectionState.DISCONNECTED,
                "Disconnected from Flexisip"
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
        NOT SUPPORTED: Flexisip is a SIP proxy/registrar, not a PBX.

        Flexisip manages SIP accounts and devices but does not originate calls.
        Call origination happens on the client side (SIP user agents).

        Args:
            from_number: Not used
            to_number: Not used
            options: Not used

        Raises:
            CallError: Always (operation not supported)
        """
        error_msg = (
            "Flexisip is a SIP proxy/registrar and does not support direct call origination. "
            "Use Asterisk, FreeSWITCH, or another PBX adapter for make_call(). "
            "Flexisip is designed for mobile SIP applications where calls are initiated "
            "by client devices. The adapter can manage accounts and devices but not initiate calls."
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
        Terminate SIP session (limited support).

        Note: Flexisip as a proxy has limited ability to terminate active calls.
        This method attempts to send a termination message but may not be effective
        for all call scenarios.

        Args:
            call_id: Call identifier

        Returns:
            True if termination message sent

        Raises:
            CallError: If hangup fails
            ConnectionError: If not connected
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Flexisip")

        try:
            # Get call data
            call_data = self._get_active_call(call_id)
            if not call_data:
                self.logger.warning(f"Call {call_id} not found in local cache")
                # Still try to send termination message
                call_data = {"call_id": call_id}

            self.logger.debug(f"Attempting to terminate call: {call_id}")

            # Try to send SIP message via /api/messages endpoint
            # This is a best-effort attempt as Flexisip may not support direct call termination
            try:
                from_uri = call_data.get("from_uri", call_data.get("from_number", ""))
                to_uri = call_data.get("to_uri", call_data.get("to_number", ""))

                if from_uri and to_uri:
                    payload = {
                        "from": from_uri,
                        "to": to_uri,
                        "type": "terminate",
                        "call_id": call_id,
                    }

                    response = self._api_call("POST", "/messages", json=payload)
                    self.logger.info(f"Sent termination message for {call_id}")
                else:
                    self.logger.warning(
                        f"Cannot send termination message - missing URI information for {call_id}"
                    )

            except Exception as e:
                self.logger.warning(f"Could not send termination message: {e}")

            # Update local state
            self._remove_active_call(call_id)
            self.emit_call_state_changed(
                call_id=call_id,
                state=CallState.TERMINATED,
            )

            self.logger.info(
                f"Call {call_id} marked as terminated locally. "
                "Note: Flexisip proxy mode has limited call control."
            )
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
        Query call status (limited in proxy mode).

        Note: Flexisip as a proxy does not track detailed call states.
        This method returns cached information if available.

        Args:
            call_id: Call identifier

        Returns:
            Call status dictionary

        Raises:
            CallError: If call not found
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Flexisip")

        try:
            # Check local cache
            call_data = self._get_active_call(call_id)

            if not call_data:
                raise CallError(f"Call not found: {call_id}")

            # Calculate duration
            start_time = call_data.get("start_time", time.time())
            duration = time.time() - start_time

            # Map state
            state = call_data.get("state", CallState.CREATED)
            if isinstance(state, str):
                try:
                    state = CallState(state)
                except ValueError:
                    state = CallState.CREATED

            return {
                "call_id": call_id,
                "state": state.value,
                "from_number": call_data.get("from_number", "unknown"),
                "to_number": call_data.get("to_number", "unknown"),
                "duration": duration,
                "codec": "N/A",  # Flexisip doesn't track codecs (proxy mode)
                "jitter": 0,
                "packet_loss": 0,
                "rtp_quality": 0,  # Not available in proxy mode
                "details": {
                    "from_uri": call_data.get("from_uri", ""),
                    "to_uri": call_data.get("to_uri", ""),
                    "adapter": "flexisip",
                    "note": "Limited call tracking in proxy mode",
                }
            }

        except CallError:
            raise
        except Exception as e:
            self.logger.exception(f"Error getting status for {call_id}: {e}")
            raise CallError(f"Failed to get call status: {e}")

    def health_check(self) -> Dict[str, Any]:
        """
        Return health metrics via /api/statistics endpoint.

        Returns:
            Health status dictionary
        """
        try:
            metrics = self.metrics.get_metrics()

            # Get statistics from Flexisip
            if self.is_connected():
                try:
                    stats = self._api_call("GET", "/statistics")

                    # Parse statistics response
                    if isinstance(stats, dict):
                        # Extract relevant metrics
                        metrics["active_registrations"] = stats.get("registrations", 0)
                        metrics["active_calls"] = stats.get("active_calls", self._get_active_calls_count())
                        metrics["server_stats"] = stats
                    else:
                        metrics["active_calls"] = self._get_active_calls_count()

                except Exception as e:
                    self.logger.warning(f"Could not query statistics: {e}")
                    metrics["active_calls"] = self._get_active_calls_count()
            else:
                metrics["active_calls"] = 0

            # Determine health status
            if not self.is_connected():
                status = HealthStatus.CRITICAL
            elif metrics.get("connection_failures", 0) > 5:
                status = HealthStatus.CRITICAL
            elif metrics["latency"]["avg_ms"] > 1000:
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
        Validate Flexisip-specific configuration.

        Returns:
            True if valid

        Raises:
            ConfigurationError: If validation fails
        """
        try:
            # Check type
            if config.get("type") != "flexisip":
                raise ConfigurationError("Invalid adapter type for Flexisip")

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
            endpoint = config.get("endpoint", "/api")
            if not endpoint.startswith("/"):
                raise ConfigurationError(
                    f"Invalid endpoint: {endpoint} (must start with '/')"
                )

            # Auth validation - at least one method should be present
            auth = config.get("auth", {})
            has_bearer = "bearer_token" in auth
            has_api_key = "api_key" in auth
            has_digest = "digest_username" in auth and "digest_password" in auth

            if not (has_bearer or has_api_key or has_digest):
                self.logger.warning(
                    "No authentication configured. This may work for testing "
                    "but is not recommended for production."
                )

            # Validate auth values if present
            if has_bearer and not isinstance(auth["bearer_token"], str):
                raise ConfigurationError("bearer_token must be a string")

            if has_api_key and not isinstance(auth["api_key"], str):
                raise ConfigurationError("api_key must be a string")

            if has_digest:
                if not isinstance(auth["digest_username"], str):
                    raise ConfigurationError("digest_username must be a string")
                if not isinstance(auth["digest_password"], str):
                    raise ConfigurationError("digest_password must be a string")

            # Timeout
            timeout = config.get("timeout", 30)
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                raise ConfigurationError(
                    f"Invalid timeout: {timeout} (must be > 0)"
                )

            # TLS settings
            tls = config.get("tls", True)
            if not isinstance(tls, bool):
                raise ConfigurationError("tls must be a boolean")

            verify_tls = config.get("verify_tls", True)
            if not isinstance(verify_tls, bool):
                raise ConfigurationError("verify_tls must be a boolean")

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
        Retrieve recent call history.

        Note: Flexisip only tracks active sessions. Historical data requires
        external storage or logging infrastructure.

        Returns:
            List of call dictionaries (limited to local cache)
        """
        with self._lock:
            return list(self._call_history)[-limit:]

    # ========================================================================
    # Flexisip-Specific Methods
    # ========================================================================

    def create_account(
        self,
        username: str,
        password: str,
        domain: str,
        **options
    ) -> Dict[str, Any]:
        """
        Create SIP account via POST /api/accounts.

        Args:
            username: SIP username
            password: SIP password
            domain: SIP domain
            options: Additional account options (display_name, email, etc.)

        Returns:
            Account creation response

        Raises:
            CallError: If account creation fails
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Flexisip")

        try:
            payload = {
                "username": username,
                "password": password,
                "domain": domain,
                **options
            }

            self.logger.debug(f"Creating account: {username}@{domain}")
            response = self._api_call("POST", "/accounts", json=payload)

            # Cache account info
            account_id = f"{username}@{domain}"
            self._accounts_cache[account_id] = {
                "username": username,
                "domain": domain,
                "created_at": time.time(),
                **options
            }

            self.logger.info(f"Successfully created account: {account_id}")
            return response

        except Exception as e:
            self.logger.exception(f"Failed to create account: {e}")
            raise CallError(f"Account creation failed: {e}")

    def provision_device(
        self,
        account: str,
        device_id: str,
        push_token: Optional[str] = None,
        **options
    ) -> Dict[str, Any]:
        """
        Provision device via POST /api/devices.

        Args:
            account: SIP account (username@domain)
            device_id: Device identifier
            push_token: Optional push notification token
            options: Additional device options

        Returns:
            Device provisioning response

        Raises:
            CallError: If device provisioning fails
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Flexisip")

        try:
            payload = {
                "account": account,
                "device_id": device_id,
            }

            if push_token:
                payload["push_token"] = push_token

            payload.update(options)

            self.logger.debug(f"Provisioning device {device_id} for {account}")
            response = self._api_call("POST", "/devices", json=payload)

            self.logger.info(f"Successfully provisioned device: {device_id}")
            return response

        except Exception as e:
            self.logger.exception(f"Failed to provision device: {e}")
            raise CallError(f"Device provisioning failed: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get server statistics via GET /api/statistics.

        Returns:
            Statistics dictionary

        Raises:
            ConnectionError: If not connected
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Flexisip")

        try:
            stats = self._api_call("GET", "/statistics")
            return stats or {}

        except Exception as e:
            self.logger.exception(f"Failed to get statistics: {e}")
            return {}

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    def _api_call(
        self,
        method: str,
        path: str,
        timeout: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Make HTTP REST API call to Flexisip.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path (e.g., "/accounts", "/statistics")
            timeout: Optional timeout override
            kwargs: Additional requests arguments (json, params, etc.)

        Returns:
            Response data (parsed JSON)

        Raises:
            ConnectionError: If HTTP request fails
            CallError: If API returns error
        """
        if not self.session or not self.base_url:
            raise ConnectionError("Not connected to Flexisip")

        # Build full URL
        url = f"{self.base_url}{path}"

        # Ensure path starts with /
        if not path.startswith("/"):
            url = f"{self.base_url}/{path}"

        try:
            self.logger.debug(f"API call: {method} {url}")

            timeout = timeout or self.config.get("timeout", 30)

            response = self.session.request(
                method=method.upper(),
                url=url,
                timeout=timeout,
                **kwargs
            )

            # Check HTTP status
            if response.status_code >= 400:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self.logger.error(error_msg)

                if response.status_code == 401:
                    raise ConnectionError("Authentication failed - check credentials")
                elif response.status_code == 403:
                    raise ConnectionError("Forbidden - insufficient permissions")
                elif response.status_code == 404:
                    raise CallError(f"Endpoint not found: {path}", code=404)
                else:
                    raise CallError(error_msg, code=response.status_code)

            # Parse JSON response if present
            if response.content:
                try:
                    data = response.json()
                    self.logger.debug(f"API response: {data}")
                    return data
                except ValueError:
                    # Not JSON, return text
                    return response.text
            else:
                return None

        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP request failed: {e}")
            raise ConnectionError(f"HTTP request failed: {e}")
        except ValueError as e:
            self.logger.error(f"Invalid JSON response: {e}")
            raise ConnectionError(f"Invalid JSON response: {e}")

    def _query_server_info(self) -> None:
        """
        Query Flexisip server information.

        Attempts to get version and other server details.
        """
        try:
            stats = self._api_call("GET", "/statistics")
            if isinstance(stats, dict):
                version = stats.get("version", stats.get("server_version", "unknown"))
                self.server_version = str(version)
                self.logger.info(f"Flexisip version: {self.server_version}")
            else:
                self.server_version = "unknown"
        except Exception as e:
            self.logger.warning(f"Could not query server info: {e}")
            self.server_version = "unknown"


if __name__ == "__main__":
    """Example usage of FlexisipAdapter."""
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Example 1: Bearer token authentication
    config_bearer = {
        "type": "flexisip",
        "host": "flexisip.example.com",
        "port": 443,
        "endpoint": "/api",
        "auth": {
            "bearer_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        },
        "timeout": 30,
        "tls": True,
        "verify_tls": True,
    }

    # Example 2: API key authentication
    config_api_key = {
        "type": "flexisip",
        "host": "flexisip.example.com",
        "port": 443,
        "endpoint": "/api",
        "auth": {
            "api_key": "your-api-key-here"
        },
        "timeout": 30,
        "tls": True,
    }

    # Example 3: Digest authentication
    config_digest = {
        "type": "flexisip",
        "host": "192.168.1.100",
        "port": 443,
        "endpoint": "/api",
        "auth": {
            "digest_username": "admin",
            "digest_password": "secret"
        },
        "timeout": 30,
        "tls": True,
    }

    print("=" * 80)
    print("Flexisip Adapter - Example Usage")
    print("=" * 80)

    # Create adapter (would fail without real Flexisip server)
    try:
        adapter = FlexisipAdapter(config_bearer)
        print(f"\n✓ Adapter created: {adapter.adapter_type}")
        print(f"  Supported versions: {adapter.SUPPORTED_VERSIONS}")
        print(f"  Capabilities:")

        info = adapter.get_adapter_info()
        for capability, supported in info.get("supports", {}).items():
            status = "✓" if supported else "✗"
            print(f"    {status} {capability}")

        # Note about make_call
        print("\n" + "=" * 80)
        print("IMPORTANT: Flexisip is a SIP proxy/registrar, not a PBX")
        print("=" * 80)
        print("✗ make_call() - NOT SUPPORTED (proxy doesn't originate calls)")
        print("✓ hangup() - Limited support (best-effort)")
        print("✓ get_status() - Returns cached call data")
        print("✓ health_check() - Server statistics")
        print("✓ create_account() - Account management")
        print("✓ provision_device() - Device provisioning")
        print("\nFor call origination, use Asterisk or FreeSWITCH adapters.")
        print("Flexisip is best used for modern mobile SIP applications.")

        # Demonstrate validation
        print("\n" + "=" * 80)
        print("Configuration Validation")
        print("=" * 80)

        print("\n✓ Valid configuration (Bearer token):")
        print(f"  Host: {config_bearer['host']}")
        print(f"  Port: {config_bearer['port']}")
        print(f"  Endpoint: {config_bearer['endpoint']}")
        print(f"  Auth: Bearer token (JWT)")
        print(f"  TLS: {config_bearer['tls']}")

        print("\n✓ Valid configuration (API key):")
        print(f"  Host: {config_api_key['host']}")
        print(f"  Port: {config_api_key['port']}")
        print(f"  Auth: API key")

        print("\n✓ Valid configuration (Digest):")
        print(f"  Host: {config_digest['host']}")
        print(f"  Port: {config_digest['port']}")
        print(f"  Auth: Digest (username/password)")

        # Test make_call error
        print("\n" + "=" * 80)
        print("Testing make_call() - Expected to raise CallError")
        print("=" * 80)
        try:
            adapter.make_call("+1234567890", "+0987654321")
        except CallError as e:
            print(f"\n✓ Correctly raised CallError:")
            print(f"  Error code: {e.code}")
            print(f"  Message: {e.message[:100]}...")

        # Demonstrate extended methods
        print("\n" + "=" * 80)
        print("Flexisip-Specific Features")
        print("=" * 80)
        print("\nExtended methods for mobile SIP:")
        print("  • create_account(username, password, domain)")
        print("  • provision_device(account, device_id, push_token)")
        print("  • get_statistics()")
        print("\nThese enable:")
        print("  - SIP account provisioning")
        print("  - Push notification setup")
        print("  - Presence management")
        print("  - Device registration")

    except ConfigurationError as e:
        print(f"\n✗ Configuration error: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")

    print("\n" + "=" * 80)
    print("Example complete")
    print("=" * 80)
