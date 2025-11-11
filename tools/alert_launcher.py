#!/usr/bin/env python3
"""
Alert Launcher - Instant alert spawner for budget monitoring

Provides quick access to budget alert functionality for any session.
Fast, non-blocking alert checks and monitoring setup.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import click


class AlertLauncher:
    """
    Launches budget alert commands quickly in background processes

    Attributes:
        alerts_tool_path: Path to budget_alerts.py
        monitor_tool_path: Path to cost_monitor.py
        processes: List of spawned background processes
    """

    def __init__(self):
        """Initialize AlertLauncher with automatic tool discovery"""
        self.base_dir = Path(__file__).parent.parent
        self.alerts_tool_path = self.base_dir / 'tools' / 'budget_alerts.py'
        self.monitor_tool_path = self.base_dir / 'src' / 'cost_monitor.py'
        self.processes: List[Dict[str, Any]] = []

        if not self.alerts_tool_path.exists():
            raise FileNotFoundError(f"Budget alerts tool not found: {self.alerts_tool_path}")
        if not self.monitor_tool_path.exists():
            raise FileNotFoundError(f"Cost monitor not found: {self.monitor_tool_path}")

    def add_alert(self, name: str, threshold: float, period: str = 'day',
                  action: str = 'print', message: Optional[str] = None) -> Dict:
        """
        Add budget alert rule

        Args:
            name: Alert rule name
            threshold: Cost threshold in USD
            period: Time period (hour/day/week/month)
            action: Alert action (log/print/email/webhook)
            message: Custom alert message

        Returns:
            Dict with process info
        """
        cmd = [
            sys.executable,
            str(self.alerts_tool_path),
            'add',
            '--name', name,
            '--threshold', str(threshold),
            '--period', period,
            '--action', action
        ]

        if message:
            cmd.extend(['--message', message])

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        proc_info = {
            'id': len(self.processes),
            'type': 'add_alert',
            'name': name,
            'process': proc
        }
        self.processes.append(proc_info)

        return proc_info

    def check_alerts(self) -> Dict:
        """
        Check all alert rules and trigger actions

        Returns:
            Dict with process info
        """
        cmd = [
            sys.executable,
            str(self.alerts_tool_path),
            'check'
        ]

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        proc_info = {
            'id': len(self.processes),
            'type': 'check_alerts',
            'process': proc
        }
        self.processes.append(proc_info)

        return proc_info

    def list_alerts(self) -> Dict:
        """
        List all configured alert rules

        Returns:
            Dict with process info
        """
        cmd = [
            sys.executable,
            str(self.alerts_tool_path),
            'list'
        ]

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        proc_info = {
            'id': len(self.processes),
            'type': 'list_alerts',
            'process': proc
        }
        self.processes.append(proc_info)

        return proc_info

    def status(self) -> Dict:
        """
        Get alert system status

        Returns:
            Dict with process info
        """
        cmd = [
            sys.executable,
            str(self.alerts_tool_path),
            'status'
        ]

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        proc_info = {
            'id': len(self.processes),
            'type': 'status',
            'process': proc
        }
        self.processes.append(proc_info)

        return proc_info

    def start_monitor(self, budget_daily: Optional[float] = None,
                     budget_weekly: Optional[float] = None,
                     budget_monthly: Optional[float] = None,
                     check_interval: int = 60) -> Dict:
        """
        Start cost monitoring agent

        Args:
            budget_daily: Daily budget limit in USD
            budget_weekly: Weekly budget limit in USD
            budget_monthly: Monthly budget limit in USD
            check_interval: Check interval in seconds

        Returns:
            Dict with process info
        """
        cmd = [
            sys.executable,
            str(self.monitor_tool_path),
            'start',
            '--check-interval', str(check_interval)
        ]

        if budget_daily:
            cmd.extend(['--budget-daily', str(budget_daily)])
        if budget_weekly:
            cmd.extend(['--budget-weekly', str(budget_weekly)])
        if budget_monthly:
            cmd.extend(['--budget-monthly', str(budget_monthly)])

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        proc_info = {
            'id': len(self.processes),
            'type': 'start_monitor',
            'process': proc
        }
        self.processes.append(proc_info)

        return proc_info

    def monitor_status(self, format: str = 'table') -> Dict:
        """
        Get cost monitor status

        Args:
            format: Output format (table/json)

        Returns:
            Dict with process info
        """
        cmd = [
            sys.executable,
            str(self.monitor_tool_path),
            'status',
            '--format', format
        ]

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        proc_info = {
            'id': len(self.processes),
            'type': 'monitor_status',
            'process': proc
        }
        self.processes.append(proc_info)

        return proc_info

    def wait(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for all spawned processes to complete

        Args:
            timeout: Maximum wait time in seconds (None = wait forever)

        Returns:
            True if all processes completed, False if timeout
        """
        try:
            for proc_info in self.processes:
                proc = proc_info['process']
                proc.wait(timeout=timeout)
            return True
        except subprocess.TimeoutExpired:
            return False

    def get_output(self, proc_id: Optional[int] = None) -> List[Dict]:
        """
        Get output from spawned processes

        Args:
            proc_id: Specific process ID, or None for all processes

        Returns:
            List of dicts with stdout, stderr, returncode
        """
        if proc_id is not None:
            if proc_id >= len(self.processes):
                raise ValueError(f"Invalid process ID: {proc_id}")
            processes = [self.processes[proc_id]]
        else:
            processes = self.processes

        results = []
        for proc_info in processes:
            proc = proc_info['process']
            stdout, stderr = proc.communicate()

            results.append({
                'id': proc_info['id'],
                'type': proc_info['type'],
                'name': proc_info.get('name'),
                'stdout': stdout,
                'stderr': stderr,
                'returncode': proc.returncode
            })

        return results

    def wait_and_check(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for processes and check for success

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            True if all processes succeeded (returncode 0)
        """
        if not self.wait(timeout):
            return False

        outputs = self.get_output()
        return all(out['returncode'] == 0 for out in outputs)


# CLI Interface
@click.group()
def cli():
    """Alert Launcher - Quick budget alert and monitoring commands"""
    pass


@cli.command()
@click.option('--name', required=True, help='Alert rule name')
@click.option('--threshold', required=True, type=float, help='Cost threshold (USD)')
@click.option('--period', default='day', help='Time period (hour/day/week/month)')
@click.option('--action', default='print', help='Alert action (log/print/email/webhook)')
@click.option('--message', help='Custom alert message')
def add(name: str, threshold: float, period: str, action: str, message: Optional[str]):
    """Add budget alert rule"""
    launcher = AlertLauncher()
    launcher.add_alert(name, threshold, period, action, message)
    launcher.wait()

    outputs = launcher.get_output()
    for out in outputs:
        if out['stdout']:
            click.echo(out['stdout'])
        if out['stderr']:
            click.echo(out['stderr'], err=True)

        if out['returncode'] != 0:
            sys.exit(out['returncode'])


@cli.command()
def check():
    """Check all alert rules and trigger actions"""
    launcher = AlertLauncher()
    launcher.check_alerts()
    launcher.wait()

    outputs = launcher.get_output()
    for out in outputs:
        if out['stdout']:
            click.echo(out['stdout'])
        if out['stderr']:
            click.echo(out['stderr'], err=True)


@cli.command()
def list():
    """List all configured alert rules"""
    launcher = AlertLauncher()
    launcher.list_alerts()
    launcher.wait()

    outputs = launcher.get_output()
    for out in outputs:
        if out['stdout']:
            click.echo(out['stdout'])
        if out['stderr']:
            click.echo(out['stderr'], err=True)


@cli.command()
def status():
    """Get alert system status"""
    launcher = AlertLauncher()
    launcher.status()
    launcher.wait()

    outputs = launcher.get_output()
    for out in outputs:
        if out['stdout']:
            click.echo(out['stdout'])
        if out['stderr']:
            click.echo(out['stderr'], err=True)


@cli.command()
@click.option('--budget-daily', type=float, help='Daily budget limit (USD)')
@click.option('--budget-weekly', type=float, help='Weekly budget limit (USD)')
@click.option('--budget-monthly', type=float, help='Monthly budget limit (USD)')
@click.option('--check-interval', default=60, help='Check interval (seconds)')
def monitor(budget_daily: Optional[float], budget_weekly: Optional[float],
           budget_monthly: Optional[float], check_interval: int):
    """Start cost monitoring agent"""
    launcher = AlertLauncher()
    launcher.start_monitor(budget_daily, budget_weekly, budget_monthly, check_interval)

    click.echo("Cost monitor started in background")
    click.echo(f"Check interval: {check_interval}s")
    if budget_daily:
        click.echo(f"Daily budget: ${budget_daily}")
    if budget_weekly:
        click.echo(f"Weekly budget: ${budget_weekly}")
    if budget_monthly:
        click.echo(f"Monthly budget: ${budget_monthly}")


@cli.command()
@click.option('--format', default='table', help='Output format (table/json)')
def monitor_status(format: str):
    """Get cost monitor status"""
    launcher = AlertLauncher()
    launcher.monitor_status(format)
    launcher.wait()

    outputs = launcher.get_output()
    for out in outputs:
        if out['stdout']:
            click.echo(out['stdout'])
        if out['stderr']:
            click.echo(out['stderr'], err=True)


if __name__ == '__main__':
    cli()
