#!/usr/bin/env python3
"""
WitnessLauncher - Instant CLI spawner for witness commands

Allows sessions to spawn witness CLI commands quickly without managing
paths and imports. Non-blocking execution with optional wait/output retrieval.

Usage from Python:
    from tools.cli_launcher import WitnessLauncher

    launcher = WitnessLauncher()
    launcher.log_event('event_name', 'component', 'trace-1', {'data': 42})
    launcher.verify_chain()
    launcher.wait()  # Wait for all processes
    output = launcher.get_output()

Usage from CLI:
    python3 tools/cli-launcher.py log event_name component trace-1 '{"data": 42}'
    python3 tools/cli-launcher.py verify
    python3 tools/cli-launcher.py trace trace-1
    python3 tools/cli-launcher.py export --format json --output audit.json
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import os


class WitnessLauncher:
    """Spawns and manages witness CLI commands."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize launcher.

        Args:
            db_path: Path to witness database (default: ~/.if-witness/witness.db)
        """
        self.db_path = db_path or self._get_default_db_path()
        self.cli_path = self._find_cli_path()
        self.processes: List[Tuple[str, subprocess.Popen]] = []
        self.outputs: Dict[str, Dict[str, str]] = {}

    def _get_default_db_path(self) -> str:
        """Get default database path from environment or home directory."""
        env_db = os.getenv('IF_WITNESS_DB')
        if env_db:
            return env_db
        home = Path.home()
        return str(home / '.if-witness' / 'witness.db')

    def _find_cli_path(self) -> str:
        """Find the witness CLI path automatically."""
        # Try relative to this file
        tools_dir = Path(__file__).parent
        cli_path = tools_dir.parent / 'src' / 'cli' / 'if-witness.py'

        if cli_path.exists():
            return str(cli_path)

        # Try in PATH
        result = subprocess.run(
            ['which', 'if-witness'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()

        raise FileNotFoundError(
            f"Could not find if-witness CLI at {cli_path} or in PATH"
        )

    def _spawn(self, name: str, args: List[str]) -> subprocess.Popen:
        """
        Spawn a subprocess for a CLI command.

        Args:
            name: Command name for tracking
            args: Command arguments (excluding python path and db option)

        Returns:
            Popen process object
        """
        cmd = [sys.executable, self.cli_path, '--db', self.db_path] + args

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        self.processes.append((name, proc))
        return proc

    def log_event(
        self,
        event: str,
        component: str,
        trace_id: str,
        payload: Any,
        cost: Optional[float] = None,
        tokens_in: Optional[int] = None,
        tokens_out: Optional[int] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Spawn log command to create witness entry.

        Args:
            event: Event type (e.g., 'ndi_frame_published')
            component: Component name (e.g., 'IF.ndi')
            trace_id: Trace ID linking related operations
            payload: Event data (dict or JSON string)
            cost: Cost in USD (optional)
            tokens_in: Input tokens (optional)
            tokens_out: Output tokens (optional)
            model: Model name (optional)

        Returns:
            Process ID string for tracking
        """
        # Handle payload
        if isinstance(payload, dict):
            payload_str = json.dumps(payload)
        else:
            payload_str = str(payload)

        args = [
            'log',
            '--event', event,
            '--component', component,
            '--trace-id', trace_id,
            '--payload', payload_str
        ]

        if cost is not None:
            args.extend(['--cost', str(cost)])
        if tokens_in is not None:
            args.extend(['--tokens-in', str(tokens_in)])
        if tokens_out is not None:
            args.extend(['--tokens-out', str(tokens_out)])
        if model is not None:
            args.extend(['--model', model])

        proc_id = f"log_{trace_id}"
        self._spawn(proc_id, args)

        return proc_id

    def verify_chain(self) -> str:
        """
        Spawn verify command to check hash chain integrity.

        Returns:
            Process ID string for tracking
        """
        proc_id = 'verify'
        self._spawn(proc_id, ['verify'])
        return proc_id

    def get_trace(self, trace_id: str) -> str:
        """
        Spawn trace command to follow full trace chain.

        Args:
            trace_id: Trace ID to retrieve

        Returns:
            Process ID string for tracking
        """
        proc_id = f"trace_{trace_id}"
        self._spawn(proc_id, ['trace', '--trace-id', trace_id])
        return proc_id

    def export(
        self,
        format: str = 'json',
        output: Optional[str] = None
    ) -> str:
        """
        Spawn export command to export audit trail.

        Args:
            format: Export format ('json' or 'csv')
            output: Output file path (optional, default: stdout)

        Returns:
            Process ID string for tracking
        """
        args = ['export', '--format', format]

        if output:
            args.extend(['--output', output])

        proc_id = f"export_{format}"
        self._spawn(proc_id, args)

        return proc_id

    def wait(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for all spawned processes to complete.

        Args:
            timeout: Maximum seconds to wait

        Returns:
            True if all processes completed, False if timeout
        """
        all_done = True
        for name, proc in self.processes:
            try:
                stdout, stderr = proc.communicate(timeout=timeout)
                self.outputs[name] = {
                    'stdout': stdout,
                    'stderr': stderr,
                    'returncode': proc.returncode
                }
            except subprocess.TimeoutExpired:
                all_done = False

        return all_done

    def get_output(self, proc_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get output from spawned processes.

        Args:
            proc_id: Specific process ID (None for all)

        Returns:
            Dict mapping process IDs to output dicts with 'stdout', 'stderr', 'returncode'
        """
        if proc_id:
            return self.outputs.get(proc_id, {})

        # Collect any pending output
        for name, proc in self.processes:
            if name not in self.outputs:
                try:
                    stdout, stderr = proc.communicate(timeout=0.1)
                    self.outputs[name] = {
                        'stdout': stdout,
                        'stderr': stderr,
                        'returncode': proc.returncode
                    }
                except (subprocess.TimeoutExpired, Exception):
                    pass

        return self.outputs

    def wait_and_check(self, timeout: Optional[float] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Wait for processes and return success status and output.

        Args:
            timeout: Maximum seconds to wait

        Returns:
            Tuple of (all_succeeded, outputs_dict)
        """
        self.wait(timeout)
        outputs = self.get_output()
        all_succeeded = all(
            output.get('returncode') == 0
            for output in outputs.values()
        )
        return all_succeeded, outputs


def main():
    """CLI interface for quick command spawning."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Witness CLI Launcher - Spawn witness commands instantly'
    )
    parser.add_argument('--db', help='Database path (default: ~/.if-witness/witness.db)')

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Log command
    log_parser = subparsers.add_parser('log', help='Create witness entry')
    log_parser.add_argument('event', help='Event type')
    log_parser.add_argument('component', help='Component name')
    log_parser.add_argument('trace_id', help='Trace ID')
    log_parser.add_argument('payload', help='Event payload (JSON string)')
    log_parser.add_argument('--cost', type=float, help='Cost in USD')
    log_parser.add_argument('--tokens-in', type=int, help='Input tokens')
    log_parser.add_argument('--tokens-out', type=int, help='Output tokens')
    log_parser.add_argument('--model', help='Model name')

    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify hash chain')

    # Trace command
    trace_parser = subparsers.add_parser('trace', help='Follow trace chain')
    trace_parser.add_argument('trace_id', help='Trace ID to retrieve')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export audit trail')
    export_parser.add_argument(
        '--format',
        choices=['json', 'csv'],
        default='json',
        help='Export format'
    )
    export_parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    launcher = WitnessLauncher(db_path=args.db)

    try:
        if args.command == 'log':
            launcher.log_event(
                event=args.event,
                component=args.component,
                trace_id=args.trace_id,
                payload=args.payload,
                cost=args.cost,
                tokens_in=args.tokens_in,
                tokens_out=args.tokens_out,
                model=args.model
            )
        elif args.command == 'verify':
            launcher.verify_chain()
        elif args.command == 'trace':
            launcher.get_trace(args.trace_id)
        elif args.command == 'export':
            launcher.export(format=args.format, output=args.output)

        # Wait for process and show output
        launcher.wait()
        outputs = launcher.get_output()

        for proc_id, output in outputs.items():
            if output.get('stdout'):
                print(output['stdout'], end='')
            if output.get('stderr'):
                print(output['stderr'], end='', file=sys.stderr)

        # Return appropriate exit code
        success, _ = launcher.wait_and_check()
        return 0 if success else 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
