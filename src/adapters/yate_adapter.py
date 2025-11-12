"""
Yate SIP Adapter Implementation

Connects to Yate via External Module Protocol (custom message-based).

Requirements:
- Yate >= 5.0
- External module protocol enabled on port 5039 (default)
- Custom message-based protocol with special encoding

Example Configuration:
```yaml
type: yate
host: 192.168.1.100
port: 5039
auth:
  role: global  # global, channel, play, record, playrec
timeout: 30
retry_count: 3
pool_size: 10
```

Protocol Details:
- Connect: %%>connect:role
- Message: %%>message:<name>:[key=value]*
- Watch: %%>watch:<message_type>
- Install: %%>install:<priority>:<message_type>:[filter]
- Special encoding: ASCII<32 -> %<upcode> where upcode=64+ASCII_value

Author: Agent 6 (Yate specialist)
Version: 1.0.0
"""

import logging
import socket
import time
import threading
import re
from typing import Any, Dict, Optional, List, Tuple
from collections import deque

from src.adapters.sip_adapter_base import (
    SIPAdapterBase,
    CallState,
    ConnectionState,
    HealthStatus,
    ErrorSeverity,
    ConfigurationError,
    ConnectionError,
    CallError,
    TimeoutError,
)


class YateProtocol:
    """
    Yate External Module Protocol handler.

    Implements:
    - Message encoding/decoding with special character handling
    - Protocol parsing for %%> and %%< messages
    - Key-value pair extraction
    """

    # Protocol constants
    CLIENT_PREFIX = "%%>"
    SERVER_PREFIX = "%%<"

    @staticmethod
    def encode_value(value: str) -> str:
        """
        Encode special characters for Yate protocol.

        ASCII < 32 is converted to %<upcode> where upcode = 64 + ASCII_value.
        Also encode special characters: : = %

        Args:
            value: String to encode

        Returns:
            Encoded string
        """
        result = []
        for char in value:
            ascii_val = ord(char)
            if ascii_val < 32:
                # Special encoding for control characters
                upcode = 64 + ascii_val
                result.append(f"%{chr(upcode)}")
            elif char in [':', '=', '%']:
                # Escape special protocol characters
                result.append(f"%{ord(char):02x}")
            else:
                result.append(char)
        return ''.join(result)

    @staticmethod
    def decode_value(value: str) -> str:
        """
        Decode Yate protocol encoded strings.

        Args:
            value: Encoded string

        Returns:
            Decoded string
        """
        result = []
        i = 0
        while i < len(value):
            if value[i] == '%' and i + 1 < len(value):
                next_char = value[i + 1]
                # Check if it's upcode encoding (ASCII 64-95)
                if 64 <= ord(next_char) <= 95:
                    # Decode upcode
                    ascii_val = ord(next_char) - 64
                    result.append(chr(ascii_val))
                    i += 2
                # Check if it's hex encoding
                elif i + 2 < len(value):
                    try:
                        hex_val = int(value[i+1:i+3], 16)
                        result.append(chr(hex_val))
                        i += 3
                    except ValueError:
                        result.append(value[i])
                        i += 1
                else:
                    result.append(value[i])
                    i += 1
            else:
                result.append(value[i])
                i += 1
        return ''.join(result)

    @staticmethod
    def build_message(message_type: str, **params) -> str:
        """
        Build a Yate protocol message.

        Format: %%>message:<name>:[key=value]*

        Args:
            message_type: Message type (e.g., 'call.execute')
            **params: Key-value pairs

        Returns:
            Formatted message string
        """
        parts = [YateProtocol.CLIENT_PREFIX, "message:", message_type]

        for key, value in params.items():
            encoded_value = YateProtocol.encode_value(str(value))
            parts.append(f":{key}={encoded_value}")

        return ''.join(parts) + "\n"

    @staticmethod
    def parse_message(line: str) -> Dict[str, Any]:
        """
        Parse a Yate protocol message.

        Format: %%<message:<name>:[key=value]*

        Args:
            line: Message line from server

        Returns:
            Dictionary with 'type' and parameters
        """
        result = {}

        # Remove prefix and split
        if line.startswith(YateProtocol.SERVER_PREFIX):
            line = line[len(YateProtocol.SERVER_PREFIX):]
        elif line.startswith(YateProtocol.CLIENT_PREFIX):
            line = line[len(YateProtocol.CLIENT_PREFIX):]

        # Split by colon
        parts = line.split(':')

        if len(parts) < 2:
            return result

        # First part is command type (e.g., 'message', 'connect', 'install')
        result['command'] = parts[0]

        # Second part is message type or role
        if len(parts) > 1:
            result['type'] = parts[1]

        # Parse key=value pairs
        for i in range(2, len(parts)):
            if '=' in parts[i]:
                key, value = parts[i].split('=', 1)
                result[key] = YateProtocol.decode_value(value)
            else:
                # Parameter without value
                result[f'param_{i}'] = parts[i]

        return result

    @staticmethod
    def build_connect(role: str = "global") -> str:
        """Build connection handshake message."""
        return f"{YateProtocol.CLIENT_PREFIX}connect:{role}\n"

    @staticmethod
    def build_watch(message_type: str) -> str:
        """Build watch command."""
        return f"{YateProtocol.CLIENT_PREFIX}watch:{message_type}\n"

    @staticmethod
    def build_unwatch(message_type: str) -> str:
        """Build unwatch command."""
        return f"{YateProtocol.CLIENT_PREFIX}unwatch:{message_type}\n"

    @staticmethod
    def build_install(priority: int, message_type: str, filter_str: str = "") -> str:
        """Build install handler command."""
        if filter_str:
            return f"{YateProtocol.CLIENT_PREFIX}install:{priority}:{message_type}:{filter_str}\n"
        return f"{YateProtocol.CLIENT_PREFIX}install:{priority}:{message_type}\n"


class YateAdapter(SIPAdapterBase):
    """
    Yate SIP adapter via External Module Protocol.

    Supports:
    - Outbound calls (call.execute message)
    - Inbound call handling (call.route, call.execute events)
    - Call state tracking (chan.* messages)
    - Call transfer (call.transfer message)
    - Call hold (chan.masquerade)
    - Conference calls (conference room routing)
    - Call recording (chan.record message)

    Features:
    - Custom message-based protocol
    - Special character encoding/decoding
    - Event-driven architecture
    - Role-based authentication
    - Channel ID tracking
    - Message handler installation

    Complexity: HIGH (custom protocol implementation)
    """

    adapter_type = "yate"
    SUPPORTED_VERSIONS = {
        "yate": ["5.0.x", "5.4.x", "6.x"],
        "external_module": ["1.0"],
        "sip": ["2.0"],
    }

    def __init__(self, config: Dict[str, Any], **kwargs):
        """Initialize Yate adapter."""
        super().__init__(config, **kwargs)
        self.yate_socket: Optional[socket.socket] = None
        self.server_version: Optional[str] = None
        self._event_thread: Optional[threading.Thread] = None
        self._event_running = False
        self._event_buffer: deque = deque(maxlen=1000)

        # Channel ID mapping (Yate channel IDs <-> IF.bus call IDs)
        self._yate_id_to_call_id: Dict[str, str] = {}
        self._call_id_to_yate_id: Dict[str, str] = {}

        # Protocol state
        self._role: str = "global"
        self._connected_role: Optional[str] = None
        self._watched_events: set = set()
        self._installed_handlers: Dict[str, int] = {}  # message_type -> priority

        # Message sequence tracking
        self._message_seq = 0
        self._lock_seq = threading.Lock()

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
        Connect to Yate via External Module Protocol.

        Args:
            host: Yate server hostname/IP
            port: External module port (default 5039)
            auth_config: Dict with 'role' (global, channel, play, record, playrec)

        Returns:
            True if connection successful
        """
        try:
            self._update_connection_state(
                ConnectionState.CONNECTING,
                "Connecting to Yate External Module"
            )

            # Get role from auth config
            self._role = auth_config.get("role", "global")

            # Create TCP socket
            self.yate_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.yate_socket.settimeout(self.config.get("timeout", 30))

            # Connect
            self.yate_socket.connect((host, port))
            self.logger.info(f"Connected to Yate at {host}:{port}")

            # Send connection handshake
            handshake = YateProtocol.build_connect(self._role)
            self.yate_socket.sendall(handshake.encode())
            self.logger.debug(f"Sent handshake: {handshake.strip()}")

            # Read connection response
            response = self._read_line()
            self.logger.info(f"Yate connection response: {response.strip()}")

            # Parse response
            parsed = YateProtocol.parse_message(response)
            if parsed.get('command') == 'connect':
                self._connected_role = parsed.get('type') or parsed.get('role', self._role)
                self.logger.info(f"Connected with role: {self._connected_role}")
            else:
                raise ConnectionError(f"Unexpected connection response: {response}")

            self._update_connection_state(
                ConnectionState.CONNECTED,
                f"Connected to Yate with role {self._connected_role}"
            )

            # Subscribe to events
            self._subscribe_to_events()

            # Start event listener thread
            self._start_event_listener()

            # Query server version
            self._query_server_version()

            return True

        except socket.timeout:
            self._update_connection_state(
                ConnectionState.ERROR,
                "Connection timeout"
            )
            raise ConnectionError(f"Connection timeout to {host}:{port}")

        except socket.error as e:
            self._update_connection_state(
                ConnectionState.ERROR,
                f"Socket error: {e}"
            )
            raise ConnectionError(f"Socket error: {e}")

        except Exception as e:
            self._update_connection_state(
                ConnectionState.ERROR,
                f"Connection failed: {e}"
            )
            self.logger.exception(f"Connection error: {e}")
            raise ConnectionError(f"Connection failed: {e}")

    def disconnect(self) -> bool:
        """
        Disconnect from Yate.

        Hangup all calls before disconnecting.
        """
        try:
            # Stop event listener
            self._stop_event_listener()

            # Hangup active calls
            with self._lock:
                call_ids = list(self._active_calls.keys())

            for call_id in call_ids:
                try:
                    self.hangup(call_id)
                except Exception as e:
                    self.logger.warning(f"Error hanging up {call_id}: {e}")

            # Unwatch all events
            for event in list(self._watched_events):
                try:
                    self._send_command(YateProtocol.build_unwatch(event))
                except Exception:
                    pass

            # Close socket
            if self.yate_socket:
                self.yate_socket.close()

            self.yate_socket = None
            self._yate_id_to_call_id.clear()
            self._call_id_to_yate_id.clear()
            self._watched_events.clear()
            self._installed_handlers.clear()

            self._update_connection_state(
                ConnectionState.DISCONNECTED,
                "Disconnected from Yate"
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
        Initiate outbound call via call.execute message.

        Args:
            from_number: Calling number (SIP URI or extension)
            to_number: Called number
            options: Optional parameters
                - timeout: Ring timeout (seconds)
                - caller_id_name: Display name
                - caller_id_num: Caller ID number
                - target: Target destination
                - context: Call context

        Returns:
            call_id: Unique call identifier
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Yate")

        call_id = self.generate_call_id()
        request_id = self.generate_request_id()

        try:
            # Generate Yate channel ID
            yate_channel_id = self._generate_yate_channel_id()

            # Map call IDs
            self._call_id_to_yate_id[call_id] = yate_channel_id
            self._yate_id_to_call_id[yate_channel_id] = call_id

            # Build call.execute message
            timeout = options.get("timeout", 60) * 1000  # Convert to ms
            caller_id_name = options.get("caller_id_name", "InfraFabric")
            caller_id_num = options.get("caller_id_num", from_number)
            target = options.get("target", to_number)

            # Build callto parameter
            # Format: sip/sip:user@domain or protocol/destination
            if not from_number.startswith("sip:"):
                callto = f"sip/sip:{from_number}"
            else:
                callto = f"sip/{from_number}"

            # Build message parameters
            params = {
                "id": yate_channel_id,
                "callto": callto,
                "target": target,
                "caller": caller_id_num,
                "callername": caller_id_name,
                "timeout": timeout,
                "if_call_id": call_id,
                "if_request_id": request_id,
            }

            # Add custom options
            for key, value in options.items():
                if key not in ["timeout", "caller_id_name", "caller_id_num", "target"]:
                    params[key] = value

            # Send call.execute message
            message = YateProtocol.build_message("call.execute", **params)
            self.logger.debug(f"Originating call {call_id}: {from_number} -> {to_number}")
            self.logger.debug(f"Yate message: {message.strip()}")

            self._send_command(message)

            # Track call
            self._add_active_call(call_id, {
                "from_number": from_number,
                "to_number": to_number,
                "state": CallState.DIALING,
                "start_time": time.time(),
                "request_id": request_id,
                "yate_id": yate_channel_id,
            })

            # Emit event
            self.emit_call_state_changed(
                call_id=call_id,
                state=CallState.DIALING,
                from_number=from_number,
                to_number=to_number,
            )

            self.metrics.record_call(success=True)

            return call_id

        except Exception as e:
            self.logger.exception(f"Error making call: {e}")
            self.emit_error(
                code=500,
                message=f"Call initiation failed: {e}",
                severity=ErrorSeverity.ERROR,
                call_id=call_id,
            )
            self.metrics.record_call(success=False)
            raise CallError(f"Failed to originate call: {e}")

    def hangup(self, call_id: str) -> bool:
        """
        Hangup call via chan.hangup message.

        Args:
            call_id: Call identifier

        Returns:
            True if successful
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Yate")

        try:
            # Get Yate channel ID
            yate_id = self._call_id_to_yate_id.get(call_id)
            if not yate_id:
                # Try to get from active call data
                call_data = self._get_active_call(call_id)
                if call_data:
                    yate_id = call_data.get("yate_id")

            if not yate_id:
                raise CallError(f"Cannot find Yate channel ID for call {call_id}")

            # Send chan.hangup message
            message = YateProtocol.build_message(
                "chan.hangup",
                id=yate_id,
                reason="normal"
            )
            self._send_command(message)

            # Update state
            self._remove_active_call(call_id)
            self._call_id_to_yate_id.pop(call_id, None)
            self._yate_id_to_call_id.pop(yate_id, None)

            self.emit_call_state_changed(
                call_id=call_id,
                state=CallState.TERMINATED,
            )

            return True

        except Exception as e:
            self.logger.exception(f"Error hanging up {call_id}: {e}")
            raise CallError(f"Failed to hangup call: {e}")

    def get_status(self, call_id: str) -> Dict[str, Any]:
        """
        Query call status.

        Args:
            call_id: Call identifier

        Returns:
            Call status dictionary
        """
        call_data = self._get_active_call(call_id)
        if not call_data:
            raise CallError(f"Call not found: {call_id}")

        # Get Yate channel ID
        yate_id = call_data.get("yate_id")

        # Query Yate for channel info (via chan.locate)
        channel_info = {}
        if yate_id:
            try:
                channel_info = self._locate_channel(yate_id)
            except Exception as e:
                self.logger.warning(f"Could not locate channel: {e}")

        duration = time.time() - call_data.get("start_time", time.time())

        return {
            "call_id": call_id,
            "state": call_data.get("state", CallState.CREATED).value,
            "from_number": call_data.get("from_number"),
            "to_number": call_data.get("to_number"),
            "duration": duration,
            "codec": channel_info.get("format", "mulaw"),
            "jitter": 0,  # Would need RTP stats
            "packet_loss": 0,
            "rtp_quality": 95,
            "details": {
                "request_id": call_data.get("request_id"),
                "adapter": "yate",
                "yate_id": yate_id,
                "channel_info": channel_info,
            }
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Return health metrics.

        Returns:
            Health status dictionary
        """
        metrics = self.metrics.get_metrics()
        metrics["active_calls"] = self._get_active_calls_count()

        # Add Yate-specific metrics
        yate_metrics = {
            "connected_role": self._connected_role,
            "watched_events": len(self._watched_events),
            "installed_handlers": len(self._installed_handlers),
        }

        # Determine health status
        if not self.is_connected():
            status = HealthStatus.CRITICAL
        elif metrics["call_success_rate"] < 0.8:
            status = HealthStatus.CRITICAL
        elif metrics["latency"]["avg_ms"] > 300 or metrics["call_success_rate"] < 0.9:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY

        return {
            "adapter": self.adapter_type,
            "server_version": self.server_version,
            "connected": self.is_connected(),
            "uptime_seconds": metrics["uptime_seconds"],
            "metrics": metrics,
            "yate_metrics": yate_metrics,
            "last_check": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": status.value,
        }

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate Yate-specific configuration.

        Returns:
            True if valid
        """
        try:
            # Check type
            if config.get("type") != "yate":
                raise ConfigurationError("Invalid adapter type for Yate")

            # Check host and port
            host = config.get("host")
            port = config.get("port")
            if not host or not (1024 <= port <= 65535):
                raise ConfigurationError("Invalid host/port")

            # Check auth (role required)
            auth = config.get("auth", {})
            role = auth.get("role", "global")
            valid_roles = ["global", "channel", "play", "record", "playrec"]
            if role not in valid_roles:
                raise ConfigurationError(
                    f"Invalid role '{role}'. Must be one of: {valid_roles}"
                )

            return True

        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError(f"Configuration validation failed: {e}")

    # ========================================================================
    # Optional Methods
    # ========================================================================

    def transfer(
        self,
        call_id: str,
        destination: str,
        attended: bool = False,
        **options
    ) -> bool:
        """
        Transfer call via call.transfer message.

        Args:
            call_id: Call to transfer
            destination: Transfer destination
            attended: If True, establish second call first

        Returns:
            True if successful
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Yate")

        try:
            # Get Yate channel ID
            yate_id = self._call_id_to_yate_id.get(call_id)
            if not yate_id:
                call_data = self._get_active_call(call_id)
                if call_data:
                    yate_id = call_data.get("yate_id")

            if not yate_id:
                raise CallError(f"Cannot find Yate channel ID for call {call_id}")

            # Send call.transfer message
            params = {
                "id": yate_id,
                "target": destination,
                "attended": "true" if attended else "false",
            }

            message = YateProtocol.build_message("call.transfer", **params)
            self._send_command(message)

            self.emit_call_state_changed(
                call_id=call_id,
                state=CallState.TRANSFERRING,
            )

            return True

        except Exception as e:
            raise CallError(f"Transfer failed: {e}")

    def hold(self, call_id: str) -> bool:
        """
        Place call on hold via chan.masquerade.

        Yate doesn't have a direct hold command, but we can use
        chan.masquerade to redirect media to music on hold.

        Returns:
            True if successful
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Yate")

        try:
            # Get Yate channel ID
            yate_id = self._call_id_to_yate_id.get(call_id)
            if not yate_id:
                call_data = self._get_active_call(call_id)
                if call_data:
                    yate_id = call_data.get("yate_id")

            if not yate_id:
                raise CallError(f"Cannot find Yate channel ID for call {call_id}")

            # Send chan.masquerade to music on hold
            params = {
                "id": yate_id,
                "message": "chan.attach",
                "source": "moh/default",
                "notify": yate_id,
            }

            message = YateProtocol.build_message("chan.masquerade", **params)
            self._send_command(message)

            # Update call state
            call_data = self._get_active_call(call_id)
            if call_data:
                call_data["state"] = CallState.ON_HOLD
                self._add_active_call(call_id, call_data)

            self.emit_call_state_changed(
                call_id=call_id,
                state=CallState.ON_HOLD,
            )

            return True

        except Exception as e:
            raise CallError(f"Hold failed: {e}")

    def resume(self, call_id: str) -> bool:
        """
        Resume held call.

        Returns:
            True if successful
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Yate")

        try:
            # Get Yate channel ID
            yate_id = self._call_id_to_yate_id.get(call_id)
            if not yate_id:
                call_data = self._get_active_call(call_id)
                if call_data:
                    yate_id = call_data.get("yate_id")

            if not yate_id:
                raise CallError(f"Cannot find Yate channel ID for call {call_id}")

            # Send chan.masquerade to restore connection
            params = {
                "id": yate_id,
                "message": "chan.attach",
                "source": "wave/play//dev/null",
                "consumer": "wave/record//dev/null",
                "notify": yate_id,
            }

            message = YateProtocol.build_message("chan.masquerade", **params)
            self._send_command(message)

            # Update call state
            call_data = self._get_active_call(call_id)
            if call_data:
                call_data["state"] = CallState.CONNECTED
                self._add_active_call(call_id, call_data)

            self.emit_call_state_changed(
                call_id=call_id,
                state=CallState.CONNECTED,
            )

            return True

        except Exception as e:
            raise CallError(f"Resume failed: {e}")

    def conference(self, call_ids: List[str], **options) -> str:
        """
        Merge multiple calls into conference.

        Yate uses conference rooms for multi-party calls.

        Args:
            call_ids: List of call IDs to conference
            options: Conference options (room, maxusers, etc.)

        Returns:
            conference_id: Unique conference identifier
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Yate")

        try:
            # Generate conference room ID
            conference_id = f"conf-{int(time.time())}"
            room = options.get("room", conference_id)

            # Add each call to the conference
            for call_id in call_ids:
                yate_id = self._call_id_to_yate_id.get(call_id)
                if not yate_id:
                    call_data = self._get_active_call(call_id)
                    if call_data:
                        yate_id = call_data.get("yate_id")

                if not yate_id:
                    self.logger.warning(f"Cannot find Yate ID for call {call_id}")
                    continue

                # Send chan.masquerade to conference room
                params = {
                    "id": yate_id,
                    "message": "chan.attach",
                    "source": f"conf/{room}",
                    "consumer": f"conf/{room}",
                    "notify": yate_id,
                }

                message = YateProtocol.build_message("chan.masquerade", **params)
                self._send_command(message)

            self.logger.info(f"Conference {conference_id} created with {len(call_ids)} participants")

            return conference_id

        except Exception as e:
            raise CallError(f"Conference creation failed: {e}")

    def record(
        self,
        call_id: str,
        format: str = "wav",
        **options
    ) -> bool:
        """
        Start recording via chan.record message.

        Args:
            call_id: Call to record
            format: Audio format (wav, gsm, etc.)
            options: Record options

        Returns:
            True if recording started
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Yate")

        try:
            # Get Yate channel ID
            yate_id = self._call_id_to_yate_id.get(call_id)
            if not yate_id:
                call_data = self._get_active_call(call_id)
                if call_data:
                    yate_id = call_data.get("yate_id")

            if not yate_id:
                raise CallError(f"Cannot find Yate channel ID for call {call_id}")

            # Build filename
            filename = f"/var/spool/yate/recordings/{call_id}.{format}"

            # Send chan.record message
            params = {
                "id": yate_id,
                "call": yate_id,
                "peer": yate_id,
                "maxlen": options.get("maxlen", "0"),
                "filename": filename,
            }

            message = YateProtocol.build_message("chan.record", **params)
            self._send_command(message)

            self.logger.info(f"Started recording for call {call_id} to {filename}")

            return True

        except Exception as e:
            raise CallError(f"Recording failed: {e}")

    # ========================================================================
    # Private Utility Methods - Protocol & Communication
    # ========================================================================

    def _send_command(self, command: str) -> None:
        """
        Send command to Yate server.

        Args:
            command: Command string to send
        """
        if not self.yate_socket:
            raise ConnectionError("Not connected to Yate")

        try:
            self.yate_socket.sendall(command.encode())
        except socket.timeout:
            raise TimeoutError("Command send timeout")
        except Exception as e:
            raise ConnectionError(f"Failed to send command: {e}")

    def _read_line(self) -> str:
        """Read a single line from socket (up to \\n)."""
        line = b""
        while True:
            try:
                char = self.yate_socket.recv(1)
                if not char:
                    break
                if char == b"\n":
                    break
                line += char
            except socket.timeout:
                break
        return line.decode("utf-8", errors="ignore")

    def _subscribe_to_events(self) -> None:
        """Subscribe to Yate events."""
        try:
            # Watch important events
            events = [
                "call.execute",
                "call.answered",
                "call.hangup",
                "call.drop",
                "chan.hangup",
                "chan.notify",
            ]

            for event in events:
                watch_cmd = YateProtocol.build_watch(event)
                self._send_command(watch_cmd)
                self._watched_events.add(event)
                self.logger.debug(f"Watching event: {event}")

            # Install handlers for call routing
            install_cmd = YateProtocol.build_install(50, "call.route")
            self._send_command(install_cmd)
            self._installed_handlers["call.route"] = 50

            self.logger.info(f"Subscribed to {len(events)} events")

        except Exception as e:
            self.logger.error(f"Failed to subscribe to events: {e}")

    def _start_event_listener(self) -> None:
        """Start background thread to listen for events."""
        if self._event_running:
            return

        self._event_running = True
        self._event_thread = threading.Thread(target=self._event_listener_loop, daemon=True)
        self._event_thread.start()
        self.logger.info("Event listener thread started")

    def _stop_event_listener(self) -> None:
        """Stop event listener thread."""
        self._event_running = False
        if self._event_thread:
            self._event_thread.join(timeout=5)
            self._event_thread = None
        self.logger.info("Event listener thread stopped")

    def _event_listener_loop(self) -> None:
        """Background loop to receive and process events."""
        while self._event_running:
            try:
                if not self.yate_socket:
                    break

                # Set short timeout to allow checking _event_running
                self.yate_socket.settimeout(1.0)

                line = self._read_line()
                if line:
                    self._process_message(line)

            except socket.timeout:
                continue
            except Exception as e:
                if self._event_running:
                    self.logger.error(f"Event listener error: {e}")
                break

    def _process_message(self, line: str) -> None:
        """Process incoming Yate message."""
        try:
            if not line.strip():
                return

            # Parse message
            parsed = YateProtocol.parse_message(line)
            command = parsed.get("command")
            msg_type = parsed.get("type")

            self.logger.debug(f"Received: command={command}, type={msg_type}, data={parsed}")

            # Handle different message types
            if command == "message":
                self._handle_message_event(msg_type, parsed)
            elif command == "install":
                self._handle_install_response(parsed)
            elif command == "watch":
                self._handle_watch_response(parsed)
            elif command == "setlocal":
                self._handle_setlocal(parsed)

        except Exception as e:
            self.logger.error(f"Error processing message: {e}")

    def _handle_message_event(self, msg_type: str, data: Dict[str, Any]) -> None:
        """Handle message event from Yate."""
        try:
            # Get channel ID
            yate_id = data.get("id") or data.get("chan")

            # Map to our call_id
            call_id = self._yate_id_to_call_id.get(yate_id) if yate_id else None

            # Handle different message types
            if msg_type == "call.execute":
                if call_id:
                    self.emit_call_state_changed(
                        call_id=call_id,
                        state=CallState.DIALING,
                    )

            elif msg_type == "call.answered":
                if call_id:
                    call_data = self._get_active_call(call_id)
                    if call_data:
                        call_data["state"] = CallState.CONNECTED
                        self._add_active_call(call_id, call_data)

                    self.emit_call_state_changed(
                        call_id=call_id,
                        state=CallState.CONNECTED,
                    )

            elif msg_type in ["call.hangup", "call.drop", "chan.hangup"]:
                if call_id:
                    reason = data.get("reason", "normal")

                    self.emit_call_state_changed(
                        call_id=call_id,
                        state=CallState.TERMINATED,
                        reason=reason,
                    )

                    # Clean up
                    self._remove_active_call(call_id)
                    self._call_id_to_yate_id.pop(call_id, None)
                    if yate_id:
                        self._yate_id_to_call_id.pop(yate_id, None)

            elif msg_type == "call.route":
                # Incoming call
                caller = data.get("caller")
                called = data.get("called")
                if caller and called:
                    # Generate call_id for incoming call
                    incoming_call_id = self.generate_call_id()
                    if yate_id:
                        self._call_id_to_yate_id[incoming_call_id] = yate_id
                        self._yate_id_to_call_id[yate_id] = incoming_call_id

                    self.emit_incoming_call(
                        call_id=incoming_call_id,
                        from_number=caller,
                        to_number=called,
                        details=data,
                    )

        except Exception as e:
            self.logger.error(f"Error handling message event: {e}")

    def _handle_install_response(self, data: Dict[str, Any]) -> None:
        """Handle install command response."""
        # Installation acknowledged
        self.logger.debug(f"Install response: {data}")

    def _handle_watch_response(self, data: Dict[str, Any]) -> None:
        """Handle watch command response."""
        # Watch acknowledged
        self.logger.debug(f"Watch response: {data}")

    def _handle_setlocal(self, data: Dict[str, Any]) -> None:
        """Handle setlocal command."""
        # Server setting local parameters
        self.logger.debug(f"Setlocal: {data}")

    def _locate_channel(self, yate_id: str) -> Dict[str, Any]:
        """
        Locate channel and get info.

        Args:
            yate_id: Yate channel ID

        Returns:
            Dictionary with channel information
        """
        try:
            # Send chan.locate message
            message = YateProtocol.build_message("chan.locate", id=yate_id)
            self._send_command(message)

            # In a real implementation, we'd wait for the response
            # For now, return empty dict
            return {}

        except Exception as e:
            self.logger.warning(f"Failed to locate channel: {e}")
            return {}

    def _generate_yate_channel_id(self) -> str:
        """Generate unique Yate channel ID."""
        with self._lock_seq:
            self._message_seq += 1
            return f"yate/{int(time.time())}/{self._message_seq}"

    def _query_server_version(self) -> None:
        """Query Yate server version."""
        try:
            # Yate doesn't have a direct version query via external module
            # We'd need to parse initial connection message or use status messages
            self.server_version = "5.x"
            self.logger.info(f"Yate version: {self.server_version}")
        except Exception as e:
            self.logger.warning(f"Could not query server version: {e}")
            self.server_version = "unknown"


if __name__ == "__main__":
    """Example usage of YateAdapter."""
    import logging
    logging.basicConfig(level=logging.DEBUG)

    config = {
        "type": "yate",
        "host": "192.168.1.100",
        "port": 5039,
        "auth": {
            "role": "global"
        },
        "timeout": 30,
    }

    # Create adapter (would fail without real Yate server)
    try:
        adapter = YateAdapter(config)
        print(f"Adapter created: {adapter.adapter_type}")
        print(f"Supported versions: {adapter.SUPPORTED_VERSIONS}")
        print(f"Protocol complexity: HIGH (custom message-based)")

        # Example: Test protocol encoding
        test_value = "Hello:World=Test%Special"
        encoded = YateProtocol.encode_value(test_value)
        decoded = YateProtocol.decode_value(encoded)
        print(f"\nProtocol encoding test:")
        print(f"  Original: {test_value}")
        print(f"  Encoded:  {encoded}")
        print(f"  Decoded:  {decoded}")

        # Example: Build messages
        connect_msg = YateProtocol.build_connect("global")
        print(f"\nConnect message: {connect_msg.strip()}")

        watch_msg = YateProtocol.build_watch("call.execute")
        print(f"Watch message: {watch_msg.strip()}")

        call_msg = YateProtocol.build_message(
            "call.execute",
            id="yate/123/1",
            callto="sip/sip:1000@domain.com",
            target="2000"
        )
        print(f"Call message: {call_msg.strip()}")

    except Exception as e:
        print(f"Error: {e}")
