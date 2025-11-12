"""
Unit tests for CLI error handler module

Tests error formatting, context, recovery suggestions, and helper functions.
"""

import pytest
import json
from pathlib import Path
from src.cli.error_handler import (
    CLIError,
    DatabaseError,
    ValidationError,
    ConfigurationError,
    NetworkError,
    handle_json_decode_error,
    handle_database_connection_error,
    handle_hash_chain_verification_error,
    handle_trace_not_found_error,
    handle_network_error,
    handle_permission_error,
    safe_json_parse
)


class TestCLIError:
    """Test base CLIError class"""

    def test_basic_error(self):
        """Test error with just message"""
        error = CLIError("Something went wrong")
        assert error.message == "Something went wrong"
        assert error.context == {}
        assert error.recovery is None
        assert error.example is None

    def test_error_with_context(self):
        """Test error with context"""
        error = CLIError(
            "Failed to connect",
            context={"host": "localhost", "port": 2379}
        )
        formatted = error.format_error()
        assert "❌ Error: Failed to connect" in formatted
        assert "📋 Context:" in formatted
        assert "host: localhost" in formatted
        assert "port: 2379" in formatted

    def test_error_with_recovery(self):
        """Test error with recovery suggestions"""
        error = CLIError(
            "Connection failed",
            recovery="1. Check network\n2. Verify service is running"
        )
        formatted = error.format_error()
        assert "💡 Recovery:" in formatted
        assert "1. Check network" in formatted
        assert "2. Verify service is running" in formatted

    def test_error_with_example(self):
        """Test error with example"""
        error = CLIError(
            "Invalid syntax",
            example="if witness log --event test --payload '{\"key\": \"value\"}'"
        )
        formatted = error.format_error()
        assert "✅ Example:" in formatted
        assert "if witness log" in formatted

    def test_full_error(self):
        """Test error with all fields"""
        error = CLIError(
            message="Test error",
            context={"command": "test", "arg": "value"},
            recovery="Fix it",
            example="do this"
        )
        formatted = error.format_error()
        assert "❌ Error:" in formatted
        assert "📋 Context:" in formatted
        assert "💡 Recovery:" in formatted
        assert "✅ Example:" in formatted


class TestErrorTypes:
    """Test specific error types"""

    def test_database_error(self):
        """Test DatabaseError subclass"""
        error = DatabaseError("DB failed")
        assert isinstance(error, CLIError)
        assert error.message == "DB failed"

    def test_validation_error(self):
        """Test ValidationError subclass"""
        error = ValidationError("Invalid input")
        assert isinstance(error, CLIError)
        assert error.message == "Invalid input"

    def test_configuration_error(self):
        """Test ConfigurationError subclass"""
        error = ConfigurationError("Config missing")
        assert isinstance(error, CLIError)
        assert error.message == "Config missing"

    def test_network_error(self):
        """Test NetworkError subclass"""
        error = NetworkError("Connection refused")
        assert isinstance(error, CLIError)
        assert error.message == "Connection refused"


class TestJSONErrorHandler:
    """Test JSON parsing error handler"""

    def test_handle_json_decode_error_basic(self):
        """Test handling of JSON decode error"""
        payload = '{"key": invalid}'
        try:
            json.loads(payload)
        except json.JSONDecodeError as e:
            error = handle_json_decode_error(e, payload, "if witness log")

        assert isinstance(error, ValidationError)
        assert "Invalid JSON" in error.message
        assert "command" in error.context
        assert error.context["command"] == "if witness log"
        assert error.recovery is not None
        assert error.example is not None

    def test_handle_json_decode_error_with_position(self):
        """Test JSON error shows position"""
        payload = '{"key": "value", "bad": }'
        try:
            json.loads(payload)
        except json.JSONDecodeError as e:
            error = handle_json_decode_error(e, payload, "test")

        formatted = error.format_error()
        assert "position" in error.context
        assert "snippet" in error.context

    def test_handle_json_decode_error_recovery(self):
        """Test JSON error includes recovery steps"""
        payload = "invalid json"
        try:
            json.loads(payload)
        except json.JSONDecodeError as e:
            error = handle_json_decode_error(e, payload, "test")

        assert "double quotes" in error.recovery
        assert "jq" in error.recovery
        assert error.example is not None


class TestDatabaseErrorHandlers:
    """Test database error handlers"""

    def test_handle_database_connection_error(self):
        """Test database connection error handler"""
        db_path = Path("/tmp/test.db")
        error = Exception("Connection failed")

        cli_error = handle_database_connection_error(db_path, error)

        assert isinstance(cli_error, DatabaseError)
        assert "witness database" in cli_error.message
        assert "database_path" in cli_error.context
        assert str(db_path) in cli_error.context["database_path"]
        assert "mkdir" in cli_error.recovery
        assert cli_error.example is not None

    def test_handle_hash_chain_verification_error(self):
        """Test hash chain verification error handler"""
        error = handle_hash_chain_verification_error("Entry 5: hash mismatch", 10)

        assert isinstance(error, DatabaseError)
        assert "Hash chain verification failed" in error.message
        assert error.context["verification_error"] == "Entry 5: hash mismatch"
        assert error.context["total_entries"] == 10
        assert error.context["severity"] == "CRITICAL"
        assert "DO NOT modify" in error.recovery
        assert "export" in error.recovery.lower()


class TestTraceErrorHandler:
    """Test trace ID error handler"""

    def test_handle_trace_not_found(self):
        """Test trace not found error handler"""
        error = handle_trace_not_found_error("trace-123")

        assert isinstance(error, ValidationError)
        assert "trace-123" in error.message
        assert error.context["trace_id"] == "trace-123"
        assert "Verify trace ID spelling" in error.recovery
        assert error.example is not None

    def test_handle_trace_not_found_with_component(self):
        """Test trace not found with component filter"""
        error = handle_trace_not_found_error("trace-456", component="IF.swarm")

        assert error.context["component_filter"] == "IF.swarm"
        assert "trace-456" in error.message


class TestNetworkErrorHandler:
    """Test network error handler"""

    def test_handle_network_error_basic(self):
        """Test basic network error"""
        error = Exception("Connection refused")
        cli_error = handle_network_error("localhost", 2379, error, service="etcd")

        assert isinstance(cli_error, NetworkError)
        assert "localhost:2379" in cli_error.message
        assert cli_error.context["host"] == "localhost"
        assert cli_error.context["port"] == 2379
        assert cli_error.context["service"] == "etcd"

    def test_handle_network_error_recovery(self):
        """Test network error includes service-specific recovery"""
        error = Exception("Connection timeout")
        cli_error = handle_network_error("etcd-server", 2379, error, service="etcd")

        assert "etcd" in cli_error.recovery
        assert "docker run" in cli_error.recovery
        assert "2379" in cli_error.recovery

    def test_handle_network_error_different_service(self):
        """Test network error with different service"""
        error = Exception("Connection refused")
        cli_error = handle_network_error("nats-server", 4222, error, service="nats")

        assert "nats" in cli_error.message
        assert cli_error.context["port"] == 4222


class TestPermissionErrorHandler:
    """Test permission error handler"""

    def test_handle_permission_error(self):
        """Test permission error handler"""
        path = Path("/tmp/test.db")
        error = handle_permission_error(path, "write")

        assert isinstance(error, ConfigurationError)
        assert "Permission denied" in error.message
        assert error.context["operation"] == "write"
        assert str(path) in error.context["path"]
        assert "chmod" in error.recovery


class TestSafeJSONParse:
    """Test safe JSON parsing helper"""

    def test_safe_json_parse_valid(self):
        """Test parsing valid JSON"""
        payload = '{"key": "value", "count": 42}'
        result = safe_json_parse(payload, "test")
        assert result == {"key": "value", "count": 42}

    def test_safe_json_parse_invalid(self):
        """Test parsing invalid JSON raises CLIError"""
        payload = '{"invalid": }'
        with pytest.raises(SystemExit):  # print_cli_error calls sys.exit(1)
            safe_json_parse(payload, "test")


class TestErrorFormatting:
    """Test error formatting edge cases"""

    def test_empty_context(self):
        """Test error with empty context dict"""
        error = CLIError("Test", context={})
        formatted = error.format_error()
        assert "❌ Error: Test" in formatted
        # Context section should not appear if empty
        assert formatted.count("📋 Context:") == 0

    def test_multiline_recovery(self):
        """Test recovery with multiple lines"""
        error = CLIError(
            "Test",
            recovery="Line 1\nLine 2\nLine 3"
        )
        formatted = error.format_error()
        assert "Line 1" in formatted
        assert "Line 2" in formatted
        assert "Line 3" in formatted

    def test_special_characters_in_context(self):
        """Test context with special characters"""
        error = CLIError(
            "Test",
            context={
                "payload": '{"key": "value with\nnewline"}',
                "path": "/tmp/test\"file.db"
            }
        )
        formatted = error.format_error()
        assert "payload:" in formatted
        assert "path:" in formatted


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
