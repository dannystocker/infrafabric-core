"""
IF CLI Error Handling Module

Provides contextual error messages with recovery suggestions for all CLI commands.

Philosophy: IF.ground Principle 8 - Observability without fragility
Errors should guide users toward resolution, not just report failure.
"""

import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any
import click


class CLIError(Exception):
    """Base class for CLI errors with context and recovery suggestions"""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None,
                 recovery: Optional[str] = None, example: Optional[str] = None):
        """
        Initialize CLI error with helpful context.

        Args:
            message: Primary error message
            context: Additional context (command, args, environment)
            recovery: Suggested recovery actions
            example: Example of correct usage
        """
        self.message = message
        self.context = context or {}
        self.recovery = recovery
        self.example = example
        super().__init__(self.message)

    def format_error(self) -> str:
        """Format error with context and recovery suggestions"""
        lines = [f"❌ Error: {self.message}"]

        if self.context:
            lines.append("\n📋 Context:")
            for key, value in self.context.items():
                lines.append(f"  • {key}: {value}")

        if self.recovery:
            lines.append(f"\n💡 Recovery:")
            for line in self.recovery.split('\n'):
                if line.strip():
                    lines.append(f"  {line}")

        if self.example:
            lines.append(f"\n✅ Example:")
            for line in self.example.split('\n'):
                if line.strip():
                    lines.append(f"  {line}")

        return '\n'.join(lines)


class DatabaseError(CLIError):
    """Database-related errors"""
    pass


class ValidationError(CLIError):
    """Input validation errors"""
    pass


class ConfigurationError(CLIError):
    """Configuration-related errors"""
    pass


class NetworkError(CLIError):
    """Network/connectivity errors"""
    pass


def handle_json_decode_error(error: json.JSONDecodeError, payload: str, command: str) -> CLIError:
    """
    Handle JSON parsing errors with helpful context.

    Args:
        error: Original JSONDecodeError
        payload: The payload that failed to parse
        command: The command that was being executed

    Returns:
        CLIError with context and recovery suggestions
    """
    # Show snippet around error position
    snippet_start = max(0, error.pos - 20)
    snippet_end = min(len(payload), error.pos + 20)
    snippet = payload[snippet_start:snippet_end]
    error_pos_in_snippet = error.pos - snippet_start

    return ValidationError(
        message=f"Invalid JSON in --payload argument",
        context={
            "command": command,
            "error": str(error),
            "position": f"character {error.pos}",
            "snippet": f"...{snippet}...",
            "marker": " " * (3 + error_pos_in_snippet) + "^"
        },
        recovery="""
1. Ensure JSON is properly formatted with double quotes
2. Escape special characters (use single quotes around JSON)
3. Test JSON validity with: echo '<json>' | jq
4. For complex payloads, use a JSON file: --payload "$(cat payload.json)"
        """,
        example="""
# Correct usage:
if witness log --event test --component IF.test --trace-id abc123 \\
  --payload '{"key": "value", "count": 42}'

# For complex payloads:
echo '{"data": "complex"}' > payload.json
if witness log ... --payload "$(cat payload.json)"
        """
    )


def handle_database_connection_error(db_path: Path, error: Exception) -> CLIError:
    """
    Handle database connection errors.

    Args:
        db_path: Path to database file
        error: Original exception

    Returns:
        CLIError with context and recovery suggestions
    """
    # Check if directory exists
    db_dir = db_path.parent
    dir_exists = db_dir.exists()
    dir_writable = db_dir.exists() and db_dir.stat().st_mode & 0o200

    return DatabaseError(
        message=f"Cannot access witness database",
        context={
            "database_path": str(db_path),
            "directory_exists": dir_exists,
            "directory_writable": dir_writable if dir_exists else "N/A",
            "error_type": type(error).__name__,
            "error_message": str(error)
        },
        recovery=f"""
1. Check database directory exists: mkdir -p {db_dir}
2. Check permissions: ls -la {db_dir}
3. Try with explicit path: --db /tmp/witness.db
4. Check disk space: df -h {db_dir}
5. Verify SQLite installed: sqlite3 --version
        """,
        example=f"""
# Create database directory if missing:
mkdir -p {db_dir}

# Use custom database location:
if witness --db /tmp/test.db log --event test ...

# Check existing database:
sqlite3 {db_path} "SELECT COUNT(*) FROM witness_entries;"
        """
    )


def handle_database_corruption_error(db_path: Path, error: Exception) -> CLIError:
    """Handle database corruption errors"""
    return DatabaseError(
        message="Witness database appears to be corrupted",
        context={
            "database_path": str(db_path),
            "error": str(error),
            "file_size": db_path.stat().st_size if db_path.exists() else "N/A"
        },
        recovery=f"""
1. Backup corrupted database: cp {db_path} {db_path}.corrupt
2. Export existing data: if witness export --format json > backup.json
3. Verify hash chain: if witness verify
4. If unrecoverable, delete and recreate: rm {db_path}
5. Report issue with backup file
        """,
        example=f"""
# Backup and recover:
cp {db_path} {db_path}.backup
if witness export --format json > witness_backup.json
rm {db_path}
# Restore from backup using new database
        """
    )


def handle_hash_chain_verification_error(error_msg: str, entry_count: int) -> CLIError:
    """Handle hash chain verification failures"""
    return DatabaseError(
        message="Hash chain verification failed - potential tampering detected",
        context={
            "verification_error": error_msg,
            "total_entries": entry_count,
            "severity": "CRITICAL"
        },
        recovery="""
1. DO NOT modify the database - preserve evidence
2. Export full audit trail immediately: if witness export --format json
3. Check for disk corruption: fsck (if applicable)
4. Review recent system changes (updates, crashes)
5. Contact security team with exported data
6. Check witness log for unauthorized access
        """,
        example="""
# Preserve evidence:
if witness export --format json > evidence_$(date +%Y%m%d_%H%M%S).json
if witness export --format pdf > audit_report.pdf

# Verify specific entries:
if witness query --start-date 2025-11-01 --format json
        """
    )


def handle_signature_verification_error(entry_id: str, component: str) -> CLIError:
    """Handle signature verification failures"""
    return DatabaseError(
        message=f"Signature verification failed for entry {entry_id}",
        context={
            "entry_id": entry_id,
            "component": component,
            "security_impact": "Entry may have been tampered with"
        },
        recovery="""
1. Export entry details: if witness query --trace-id <id> --format json
2. Check public key validity: ls -la ~/.if-witness/public_key.pem
3. Verify key hasn't been rotated unexpectedly
4. Check system time accuracy: timedatectl status
5. Report security incident with entry details
        """,
        example="""
# Investigate failed entry:
if witness query --trace-id <trace-id> --format json > failed_entry.json

# Check key files:
ls -la ~/.if-witness/*.pem
        """
    )


def handle_network_error(host: str, port: int, error: Exception, service: str = "etcd") -> CLIError:
    """
    Handle network connection errors (e.g., etcd, NATS).

    Args:
        host: Target host
        port: Target port
        error: Original exception
        service: Service name (etcd, nats, etc.)

    Returns:
        CLIError with context and recovery suggestions
    """
    return NetworkError(
        message=f"Cannot connect to {service} at {host}:{port}",
        context={
            "service": service,
            "host": host,
            "port": port,
            "error_type": type(error).__name__,
            "error_message": str(error)
        },
        recovery=f"""
1. Check if {service} is running: ps aux | grep {service}
2. Test connectivity: nc -zv {host} {port}
3. Check firewall rules: sudo iptables -L | grep {port}
4. Verify {service} config: {service}ctl status (if applicable)
5. Check network interface: ip addr show
6. Start local {service}: docker run -p {port}:{port} {service}:latest
        """,
        example=f"""
# Start local {service} for development:
docker run -d -p {port}:{port} --name {service}-dev {service}:latest

# Check {service} health:
curl http://{host}:{port}/health

# Use different host:
IF_ETCD_HOST=production-etcd IF_ETCD_PORT={port} if coordinator ...
        """
    )


def handle_permission_error(path: Path, operation: str) -> CLIError:
    """Handle file permission errors"""
    return ConfigurationError(
        message=f"Permission denied: {operation}",
        context={
            "path": str(path),
            "operation": operation,
            "owner": path.owner() if path.exists() else "N/A",
            "permissions": oct(path.stat().st_mode)[-3:] if path.exists() else "N/A"
        },
        recovery=f"""
1. Check file permissions: ls -la {path}
2. Fix permissions: chmod 644 {path}
3. Check directory permissions: ls -la {path.parent}
4. Fix directory: chmod 755 {path.parent}
5. Check ownership: sudo chown $USER {path}
        """,
        example=f"""
# Fix permissions:
chmod 755 {path.parent}
chmod 644 {path}
chown $USER {path}

# Use alternative location:
if witness --db /tmp/witness.db ...
        """
    )


def handle_trace_not_found_error(trace_id: str, component: Optional[str] = None) -> CLIError:
    """Handle trace ID not found errors"""
    return ValidationError(
        message=f"No entries found for trace ID: {trace_id}",
        context={
            "trace_id": trace_id,
            "component_filter": component or "none"
        },
        recovery="""
1. Verify trace ID spelling (case-sensitive)
2. List recent entries: if witness query --limit 20
3. Search by component: if witness query --component IF.swarm
4. Search by date: if witness query --start-date 2025-11-01
5. Check if trace exists: if witness query --trace-id <partial-id>
        """,
        example="""
# Search for similar trace IDs:
if witness query --format json | jq '.[] | .trace_id' | grep -i "partial"

# List all components:
if witness query --format json | jq '.[] | .component' | sort -u

# Broad search:
if witness query --start-date 2025-11-01 --limit 100
        """
    )


def handle_config_missing_error(config_file: Path, command: str) -> CLIError:
    """Handle missing configuration file errors"""
    return ConfigurationError(
        message=f"Configuration file not found: {config_file}",
        context={
            "config_file": str(config_file),
            "command": command
        },
        recovery=f"""
1. Create default config: if config init
2. Copy template: cp {config_file}.example {config_file}
3. Use command-line args instead of config file
4. Set environment variables (IF_ETCD_HOST, IF_ETCD_PORT)
5. Check config search path: if config show-path
        """,
        example="""
# Create config:
mkdir -p ~/.config/infrafabric
cat > ~/.config/infrafabric/config.yaml <<EOF
coordinator:
  etcd_host: localhost
  etcd_port: 2379
witness:
  db_path: ~/.if-witness/witness.db
EOF

# Use environment variables:
export IF_ETCD_HOST=localhost
export IF_ETCD_PORT=2379
        """
    )


def print_cli_error(error: CLIError, verbose: bool = False):
    """
    Print CLI error to stderr and exit.

    Args:
        error: The CLI error to print
        verbose: Whether to include full traceback
    """
    click.echo(error.format_error(), err=True)

    if verbose:
        click.echo("\n🐛 Debug Information:", err=True)
        import traceback
        click.echo(traceback.format_exc(), err=True)

    sys.exit(1)


def safe_json_parse(payload: str, command: str) -> Dict[str, Any]:
    """
    Safely parse JSON with helpful error messages.

    Args:
        payload: JSON string to parse
        command: Command context for error messages

    Returns:
        Parsed JSON dict

    Raises:
        CLIError: If JSON is invalid
    """
    try:
        return json.loads(payload)
    except json.JSONDecodeError as e:
        error = handle_json_decode_error(e, payload, command)
        print_cli_error(error)


def safe_database_connect(db_path: Path, command: str) -> 'WitnessDatabase':
    """
    Safely connect to database with helpful error messages.

    Args:
        db_path: Path to database file
        command: Command context for error messages

    Returns:
        Connected WitnessDatabase

    Raises:
        CLIError: If connection fails
    """
    from witness.database import WitnessDatabase

    try:
        return WitnessDatabase(db_path)
    except PermissionError as e:
        error = handle_permission_error(db_path, "database access")
        print_cli_error(error)
    except Exception as e:
        if "corrupt" in str(e).lower() or "malformed" in str(e).lower():
            error = handle_database_corruption_error(db_path, e)
        else:
            error = handle_database_connection_error(db_path, e)
        print_cli_error(error)
