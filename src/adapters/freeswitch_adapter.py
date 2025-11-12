"""
FreeSWITCH SIP Adapter Implementation

Connects to FreeSWITCH via ESL (Event Socket Library) protocol.

Requirements:
- FreeSWITCH >= 1.6
- ESL enabled and accessible on port 8021 (default)
- ESL password configured (default: "ClueCon")

Example Configuration:
```yaml
type: freeswitch
host: 192.168.1.100
port: 8021
auth:
  password: ClueCon
timeout: 30
retry_count: 3
pool_size: 10
```

Author: Agent 2 (FreeSWITCH specialist)
Version: 1.0.0
"""

import logging
import socket
import time
import threading
import re
from typing import Any, Dict, Optional, List
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


class FreeSWITCHAdapter(SIPAdapterBase):
    """
    FreeSWITCH SIP adapter via ESL protocol.

    Supports:
    - Outbound calls (bgapi originate command)
    - Inbound call handling (CHANNEL_CREATE events)
    - Call state tracking (CHANNEL_* events)
    - Call transfer (uuid_transfer command)
    - Call hold/resume (uuid_hold command)
    - Call recording (uuid_record command)
    - UUID-based call control

    Features:
    - Event-driven architecture
    - Inbound ESL connection mode
    - Plain text protocol over TCP
    - Password-only authentication
    - Direct hold/resume commands
    """

    adapter_type = "freeswitch"
    SUPPORTED_VERSIONS = {
        "freeswitch": ["1.6.x", "1.8.x", "1.10.x"],
        "esl": ["1.0"],
        "sip": ["2.0"],
    }

    def __init__(self, config: Dict[str, Any], **kwargs):
        """Initialize FreeSWITCH adapter."""
        super().__init__(config, **kwargs)
        self.esl_socket: Optional[socket.socket] = None
        self.server_version: Optional[str] = None
        self._event_thread: Optional[threading.Thread] = None
        self._event_running = False
        self._event_buffer: deque = deque(maxlen=1000)
        self._uuid_to_call_id: Dict[str, str] = {}  # Map FreeSWITCH UUID to our call_id
        self._call_id_to_uuid: Dict[str, str] = {}  # Map our call_id to FreeSWITCH UUID

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
        Connect to FreeSWITCH via ESL.

        Args:
            host: FreeSWITCH server hostname/IP
            port: ESL port (default 8021)
            auth_config: Dict with password

        Returns:
            True if connection successful
        """
        try:
            self._update_connection_state(
                ConnectionState.CONNECTING,
                "Connecting to FreeSWITCH ESL"
            )

            # Create TCP socket
            self.esl_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.esl_socket.settimeout(self.config.get("timeout", 30))

            # Connect
            self.esl_socket.connect((host, port))

            # Read ESL greeting (Content-Type: auth/request)
            greeting = self._read_esl_response()
            self.logger.info(f"ESL Connection greeting: {greeting.get('Content-Type', 'unknown')}")

            # Send auth command
            password = auth_config.get("password", "ClueCon")
            self._send_esl_command(f"auth {password}")

            # Read auth response
            auth_response = self._read_esl_response()
            if auth_response.get("Reply-Text") != "+OK accepted":
                raise ConnectionError("ESL authentication failed")

            self.logger.info("ESL authentication successful")

            # Subscribe to events
            self._subscribe_to_events()

            self._update_connection_state(
                ConnectionState.CONNECTED,
                "Connected to FreeSWITCH ESL"
            )

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
        Disconnect from FreeSWITCH.

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

            # Send exit command
            if self.esl_socket:
                try:
                    self._send_esl_command("exit")
                except Exception:
                    pass

                self.esl_socket.close()

            self.esl_socket = None
            self._uuid_to_call_id.clear()
            self._call_id_to_uuid.clear()

            self._update_connection_state(
                ConnectionState.DISCONNECTED,
                "Disconnected from FreeSWITCH"
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
        Initiate outbound call via bgapi originate.

        Args:
            from_number: Calling number (SIP URI or extension)
            to_number: Called number
            options: Optional parameters
                - timeout: Ring timeout (seconds)
                - caller_id_name: Display name
                - caller_id_num: Caller ID number
                - context: Dialplan context
                - record: Record call (True/False or format)

        Returns:
            call_id: Unique call identifier
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to FreeSWITCH")

        call_id = self.generate_call_id()
        request_id = self.generate_request_id()

        try:
            # Build originate command
            timeout = options.get("timeout", 60)
            caller_id_name = options.get("caller_id_name", "InfraFabric")
            caller_id_num = options.get("caller_id_num", from_number)
            context = options.get("context", "default")

            # FreeSWITCH originate format:
            # bgapi originate {origination_caller_id_name='Name',origination_caller_id_number='1234'}sofia/internal/from@domain dest_ext XML context
            # For simplicity, using &echo application
            originate_cmd = (
                f"bgapi originate "
                f"{{origination_caller_id_name='{caller_id_name}',"
                f"origination_caller_id_number='{caller_id_num}',"
                f"originate_timeout={timeout},"
                f"if_call_id='{call_id}'}} "
                f"sofia/internal/{from_number} "
                f"&bridge(sofia/internal/{to_number})"
            )

            self.logger.debug(f"Originating call {call_id}: {from_number} -> {to_number}")
            response = self._send_esl_command(originate_cmd)

            # Extract Job-UUID from response
            job_uuid = response.get("Job-UUID")
            if job_uuid:
                self._call_id_to_uuid[call_id] = job_uuid
                self._uuid_to_call_id[job_uuid] = call_id

            # Track call
            self._add_active_call(call_id, {
                "from_number": from_number,
                "to_number": to_number,
                "state": CallState.DIALING,
                "start_time": time.time(),
                "request_id": request_id,
                "uuid": job_uuid,
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
        Hangup call via uuid_kill command.

        Args:
            call_id: Call identifier

        Returns:
            True if successful
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to FreeSWITCH")

        try:
            # Get UUID for this call
            uuid = self._call_id_to_uuid.get(call_id)
            if not uuid:
                # Try to get from active call data
                call_data = self._get_active_call(call_id)
                if call_data:
                    uuid = call_data.get("uuid")

            if not uuid:
                raise CallError(f"Cannot find UUID for call {call_id}")

            # Send uuid_kill command
            self._send_esl_command(f"api uuid_kill {uuid}")

            # Update state
            self._remove_active_call(call_id)
            self._call_id_to_uuid.pop(call_id, None)
            self._uuid_to_call_id.pop(uuid, None)

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

        # Get UUID
        uuid = call_data.get("uuid")

        # Query FreeSWITCH for channel info
        channel_info = {}
        if uuid:
            try:
                response = self._send_esl_command(f"api uuid_dump {uuid}")
                channel_info = self._parse_uuid_dump(response)
            except Exception as e:
                self.logger.warning(f"Could not get channel info: {e}")

        duration = time.time() - call_data.get("start_time", time.time())

        return {
            "call_id": call_id,
            "state": call_data.get("state", CallState.CREATED).value,
            "from_number": call_data.get("from_number"),
            "to_number": call_data.get("to_number"),
            "duration": duration,
            "codec": channel_info.get("read_codec", "PCMU"),
            "jitter": 0,  # Would need to parse RTP stats
            "packet_loss": 0,
            "rtp_quality": 95,
            "details": {
                "request_id": call_data.get("request_id"),
                "adapter": "freeswitch",
                "uuid": uuid,
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

        # Query FreeSWITCH status
        fs_status = {}
        if self.is_connected():
            try:
                response = self._send_esl_command("api status")
                fs_status = self._parse_status_response(response)
            except Exception as e:
                self.logger.warning(f"Could not get FreeSWITCH status: {e}")

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
            "freeswitch_status": fs_status,
            "last_check": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": status.value,
        }

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate FreeSWITCH-specific configuration.

        Returns:
            True if valid
        """
        try:
            # Check type
            if config.get("type") != "freeswitch":
                raise ConfigurationError("Invalid adapter type for FreeSWITCH")

            # Check host and port
            host = config.get("host")
            port = config.get("port")
            if not host or not (1024 <= port <= 65535):
                raise ConfigurationError("Invalid host/port")

            # Check auth (password required)
            auth = config.get("auth", {})
            if not auth.get("password"):
                raise ConfigurationError("Missing ESL password")

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
        Transfer call via uuid_transfer command.

        Args:
            call_id: Call to transfer
            destination: Transfer destination
            attended: If True, establish second call first

        Returns:
            True if successful
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to FreeSWITCH")

        try:
            # Get UUID
            uuid = self._call_id_to_uuid.get(call_id)
            if not uuid:
                call_data = self._get_active_call(call_id)
                if call_data:
                    uuid = call_data.get("uuid")

            if not uuid:
                raise CallError(f"Cannot find UUID for call {call_id}")

            # Send uuid_transfer command
            # Format: uuid_transfer <uuid> [-bleg|-both] <dest> [<dialplan>] [<context>]
            transfer_type = "-both" if attended else ""
            self._send_esl_command(
                f"api uuid_transfer {uuid} {transfer_type} {destination} XML default"
            )

            self.emit_call_state_changed(
                call_id=call_id,
                state=CallState.TRANSFERRING,
            )

            return True

        except Exception as e:
            raise CallError(f"Transfer failed: {e}")

    def hold(self, call_id: str) -> bool:
        """
        Place call on hold via uuid_hold command.

        Returns:
            True if successful
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to FreeSWITCH")

        try:
            # Get UUID
            uuid = self._call_id_to_uuid.get(call_id)
            if not uuid:
                call_data = self._get_active_call(call_id)
                if call_data:
                    uuid = call_data.get("uuid")

            if not uuid:
                raise CallError(f"Cannot find UUID for call {call_id}")

            # Send uuid_hold command
            self._send_esl_command(f"api uuid_hold {uuid}")

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
        Resume held call via uuid_hold off command.

        Returns:
            True if successful
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to FreeSWITCH")

        try:
            # Get UUID
            uuid = self._call_id_to_uuid.get(call_id)
            if not uuid:
                call_data = self._get_active_call(call_id)
                if call_data:
                    uuid = call_data.get("uuid")

            if not uuid:
                raise CallError(f"Cannot find UUID for call {call_id}")

            # Send uuid_hold off command
            self._send_esl_command(f"api uuid_hold off {uuid}")

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

    def record(
        self,
        call_id: str,
        format: str = "wav",
        **options
    ) -> bool:
        """
        Start recording via uuid_record command.

        Args:
            call_id: Call to record
            format: Audio format (wav, mp3)
            options: Record options

        Returns:
            True if recording started
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to FreeSWITCH")

        try:
            # Get UUID
            uuid = self._call_id_to_uuid.get(call_id)
            if not uuid:
                call_data = self._get_active_call(call_id)
                if call_data:
                    uuid = call_data.get("uuid")

            if not uuid:
                raise CallError(f"Cannot find UUID for call {call_id}")

            # Build filename
            filename = f"/var/recordings/{call_id}.{format}"

            # Send uuid_record command
            # Format: uuid_record <uuid> [start|stop|mask|unmask] <path> [<limit>]
            self._send_esl_command(f"api uuid_record {uuid} start {filename}")

            return True

        except Exception as e:
            raise CallError(f"Recording failed: {e}")

    # ========================================================================
    # Private Utility Methods - ESL Protocol
    # ========================================================================

    def _send_esl_command(self, command: str) -> Dict[str, Any]:
        """
        Send ESL command and read response.

        Args:
            command: ESL command to send

        Returns:
            Parsed response dictionary
        """
        if not self.esl_socket:
            raise ConnectionError("Not connected to FreeSWITCH")

        try:
            # Send command with newline terminators
            self.esl_socket.sendall(f"{command}\n\n".encode())

            # Read response
            response = self._read_esl_response()

            return response

        except socket.timeout:
            raise TimeoutError("ESL command timeout")
        except Exception as e:
            raise ConnectionError(f"ESL command failed: {e}")

    def _read_esl_response(self) -> Dict[str, Any]:
        """
        Read and parse ESL response.

        ESL responses are in HTTP-like format:
        Content-Type: text/event-plain
        Content-Length: 123

        Header1: Value1
        Header2: Value2

        Returns:
            Dictionary of headers and body
        """
        headers = {}

        # Read headers
        while True:
            line = self._read_line()
            if not line or line == "":
                break

            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()

        # Read body if Content-Length present
        content_length = headers.get("Content-Length")
        if content_length:
            body_bytes = self.esl_socket.recv(int(content_length))
            headers["_body"] = body_bytes.decode("utf-8", errors="ignore")

        return headers

    def _read_line(self) -> str:
        """Read a single line from socket (up to \n)."""
        line = b""
        while True:
            char = self.esl_socket.recv(1)
            if not char:
                break
            if char == b"\n":
                break
            line += char
        return line.decode("utf-8", errors="ignore").strip()

    def _subscribe_to_events(self) -> None:
        """Subscribe to FreeSWITCH events."""
        try:
            # Subscribe to channel events
            events = [
                "CHANNEL_CREATE",
                "CHANNEL_ANSWER",
                "CHANNEL_HANGUP",
                "CHANNEL_HANGUP_COMPLETE",
                "CHANNEL_BRIDGE",
                "CHANNEL_UNBRIDGE",
            ]

            event_list = " ".join(events)
            response = self._send_esl_command(f"event plain {event_list}")

            if response.get("Reply-Text") == "+OK event listener enabled plain":
                self.logger.info(f"Subscribed to events: {event_list}")
            else:
                self.logger.warning(f"Event subscription may have failed: {response}")

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
                if not self.esl_socket:
                    break

                # Set short timeout to allow checking _event_running
                self.esl_socket.settimeout(1.0)

                event = self._read_esl_response()
                if event.get("Content-Type") == "text/event-plain":
                    self._process_event(event)

            except socket.timeout:
                continue
            except Exception as e:
                if self._event_running:
                    self.logger.error(f"Event listener error: {e}")
                break

    def _process_event(self, event: Dict[str, Any]) -> None:
        """Process incoming FreeSWITCH event."""
        try:
            event_name = event.get("Event-Name")
            uuid = event.get("Unique-ID") or event.get("Channel-Call-UUID")

            if not uuid:
                return

            # Map UUID to our call_id
            call_id = self._uuid_to_call_id.get(uuid)
            if not call_id:
                # Check if it's in active calls by UUID
                for cid, data in self._active_calls.items():
                    if data.get("uuid") == uuid:
                        call_id = cid
                        break

            self.logger.debug(f"Event: {event_name} for UUID: {uuid}, call_id: {call_id}")

            # Handle different event types
            if event_name == "CHANNEL_CREATE":
                if call_id:
                    self.emit_call_state_changed(
                        call_id=call_id,
                        state=CallState.CREATED,
                    )

            elif event_name == "CHANNEL_ANSWER":
                if call_id:
                    call_data = self._get_active_call(call_id)
                    if call_data:
                        call_data["state"] = CallState.CONNECTED
                        self._add_active_call(call_id, call_data)

                    self.emit_call_state_changed(
                        call_id=call_id,
                        state=CallState.CONNECTED,
                    )

            elif event_name in ["CHANNEL_HANGUP", "CHANNEL_HANGUP_COMPLETE"]:
                if call_id:
                    hangup_cause = event.get("Hangup-Cause", "NORMAL_CLEARING")

                    self.emit_call_state_changed(
                        call_id=call_id,
                        state=CallState.TERMINATED,
                        reason=hangup_cause,
                    )

                    # Clean up
                    self._remove_active_call(call_id)
                    self._call_id_to_uuid.pop(call_id, None)
                    self._uuid_to_call_id.pop(uuid, None)

        except Exception as e:
            self.logger.error(f"Error processing event: {e}")

    def _parse_uuid_dump(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse uuid_dump response into dictionary."""
        info = {}
        body = response.get("_body", "")

        for line in body.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()

        return info

    def _parse_status_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse status command response."""
        status = {}
        body = response.get("_body", "")

        # Parse lines like "UP 0 years, 1 days, 2 hours, 30 minutes, 45 seconds"
        # This is simplified - real implementation would parse properly
        status["raw"] = body

        return status

    def _query_server_version(self) -> None:
        """Query FreeSWITCH server version."""
        try:
            response = self._send_esl_command("api version")
            version_str = response.get("_body", "")

            # Extract version from response like "FreeSWITCH Version 1.10.7..."
            match = re.search(r"FreeSWITCH Version ([\d.]+)", version_str)
            if match:
                self.server_version = match.group(1)
            else:
                self.server_version = "unknown"

            self.logger.info(f"FreeSWITCH version: {self.server_version}")

        except Exception as e:
            self.logger.warning(f"Could not query server version: {e}")
            self.server_version = "unknown"


if __name__ == "__main__":
    """Example usage of FreeSWITCHAdapter."""
    import logging
    logging.basicConfig(level=logging.DEBUG)

    config = {
        "type": "freeswitch",
        "host": "192.168.1.100",
        "port": 8021,
        "auth": {
            "password": "ClueCon"
        },
        "timeout": 30,
    }

    # Create adapter (would fail without real FreeSWITCH server)
    try:
        adapter = FreeSWITCHAdapter(config)
        print(f"Adapter created: {adapter.adapter_type}")
        print(f"Supported versions: {adapter.SUPPORTED_VERSIONS}")

        # Example: Connect to server
        # adapter.connect(
        #     host=config["host"],
        #     port=config["port"],
        #     auth_config=config["auth"]
        # )

        # Example: Make a call
        # call_id = adapter.make_call(
        #     from_number="1000",
        #     to_number="2000",
        #     caller_id_name="Test Call"
        # )

        # Example: Check health
        # health = adapter.health_check()
        # print(f"Health: {health}")

    except Exception as e:
        print(f"Error: {e}")
