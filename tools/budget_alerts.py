#!/usr/bin/env python3
"""
Budget Alert System for IF.witness Sessions
Monitors costs and triggers alerts based on configurable thresholds.

Philosophy: Sessions should get instant budget alerts without managing monitoring.
This integrates with the cost_monitor to provide real-time budget visibility.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

import click

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.witness.database import WitnessDatabase


class AlertPeriod(Enum):
    """Alert period types"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class AlertAction(Enum):
    """Alert action types"""
    LOG = "log"
    EMAIL = "email"
    WEBHOOK = "webhook"
    PRINT = "print"
    CALLBACK = "callback"


@dataclass
class AlertRule:
    """Configuration for a single alert rule"""
    name: str
    threshold: float  # USD
    period: AlertPeriod
    action: AlertAction
    message: str = ""
    target: Optional[str] = None  # email, webhook URL, or function name
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'threshold': self.threshold,
            'period': self.period.value,
            'action': self.action.value,
            'message': self.message,
            'target': self.target,
            'enabled': self.enabled,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlertRule':
        """Create from dictionary"""
        return cls(
            name=data['name'],
            threshold=data['threshold'],
            period=AlertPeriod(data['period']),
            action=AlertAction(data['action']),
            message=data.get('message', ''),
            target=data.get('target'),
            enabled=data.get('enabled', True),
            created_at=data.get('created_at', datetime.utcnow().isoformat())
        )


@dataclass
class AlertState:
    """Track state of triggered alerts to avoid spam"""
    rule_name: str
    last_triggered: Optional[str] = None
    trigger_count: int = 0
    suppressed: bool = False
    suppressed_until: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlertState':
        """Create from dictionary"""
        return cls(**data)

    def is_suppressed(self) -> bool:
        """Check if alert is currently suppressed"""
        if not self.suppressed or not self.suppressed_until:
            return False
        return datetime.fromisoformat(self.suppressed_until) > datetime.utcnow()

    def suppress(self, duration_minutes: int = 30):
        """Suppress alert for specified duration"""
        self.suppressed = True
        self.suppressed_until = (
            datetime.utcnow() + timedelta(minutes=duration_minutes)
        ).isoformat()


@dataclass
class TriggeredAlert:
    """Alert that has been triggered"""
    rule_name: str
    threshold: float
    current_cost: float
    period: str
    message: str
    triggered_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class BudgetAlerts:
    """
    Budget alert system for IF.witness sessions.
    Monitors costs and triggers alerts based on configured thresholds.
    """

    def __init__(self, config_file: Optional[Path] = None, db_path: Optional[Path] = None):
        """
        Initialize budget alerts system.

        Args:
            config_file: Path to alerts configuration file (default: ~/.witness/alerts.json)
            db_path: Path to witness database (default: ~/.if-witness/witness.db)
        """
        self.config_file = config_file or Path.home() / '.witness' / 'alerts.json'
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.log_file = self.config_file.parent / 'alerts.log'
        self._setup_logging()

        # Load configuration and state
        self.rules: Dict[str, AlertRule] = {}
        self.states: Dict[str, AlertState] = {}
        self.triggered_alerts: List[TriggeredAlert] = []
        self.callbacks: Dict[str, Callable] = {}

        self._load_config()

        # Database for cost queries
        self.db = WitnessDatabase(db_path=db_path)

    def _setup_logging(self):
        """Setup logging for alerts"""
        self.logger = logging.getLogger('budget_alerts')
        self.logger.setLevel(logging.INFO)

        # File handler
        handler = logging.FileHandler(self.log_file)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _load_config(self):
        """Load alert rules from configuration file"""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    data = json.load(f)
                    for rule_data in data.get('alerts', []):
                        rule = AlertRule.from_dict(rule_data)
                        self.rules[rule.name] = rule

                    for state_data in data.get('states', []):
                        state = AlertState.from_dict(state_data)
                        self.states[state.rule_name] = state

                    self.logger.info(f"Loaded {len(self.rules)} alert rules")
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")

    def _save_config(self):
        """Save alert rules and states to configuration file"""
        try:
            data = {
                'alerts': [rule.to_dict() for rule in self.rules.values()],
                'states': [state.to_dict() for state in self.states.values()],
                'saved_at': datetime.utcnow().isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")

    def add_alert(
        self,
        name: str,
        threshold: float,
        period: str = "day",
        action: str = "print",
        message: str = "",
        target: Optional[str] = None
    ) -> bool:
        """
        Add an alert rule.

        Args:
            name: Alert name (unique)
            threshold: Cost threshold in USD
            period: Period type (hour, day, week, month)
            action: Action type (log, email, webhook, print, callback)
            message: Alert message template
            target: Target for action (email, webhook URL, or callback function name)

        Returns:
            True if added successfully, False if already exists
        """
        if name in self.rules:
            self.logger.warning(f"Alert '{name}' already exists")
            return False

        try:
            period_enum = AlertPeriod(period)
            action_enum = AlertAction(action)

            rule = AlertRule(
                name=name,
                threshold=threshold,
                period=period_enum,
                action=action_enum,
                message=message or f"Budget alert: {name}",
                target=target
            )

            self.rules[name] = rule
            self.states[name] = AlertState(rule_name=name)
            self._save_config()

            self.logger.info(f"Added alert '{name}' with threshold ${threshold:.2f}/{period}")
            return True

        except ValueError as e:
            self.logger.error(f"Invalid alert parameters: {e}")
            return False

    def remove_alert(self, name: str) -> bool:
        """
        Remove an alert rule.

        Args:
            name: Alert name to remove

        Returns:
            True if removed, False if not found
        """
        if name not in self.rules:
            self.logger.warning(f"Alert '{name}' not found")
            return False

        del self.rules[name]
        if name in self.states:
            del self.states[name]

        self._save_config()
        self.logger.info(f"Removed alert '{name}'")
        return True

    def register_callback(self, name: str, func: Callable):
        """
        Register a Python callback for alert action.

        Args:
            name: Callback name
            func: Callable to invoke
        """
        self.callbacks[name] = func

    def reset_alert(self, name: str) -> bool:
        """
        Reset alert state (for testing/manual reset).

        Args:
            name: Alert name

        Returns:
            True if reset, False if not found
        """
        if name not in self.states:
            self.logger.warning(f"Alert state '{name}' not found")
            return False

        state = self.states[name]
        state.trigger_count = 0
        state.last_triggered = None
        state.suppressed = False
        state.suppressed_until = None

        self._save_config()
        self.logger.info(f"Reset alert state '{name}'")
        return True

    def get_active_alerts(self) -> List[TriggeredAlert]:
        """
        Get list of currently triggered alerts.

        Returns:
            List of TriggeredAlert objects
        """
        return self.triggered_alerts.copy()

    def _get_period_start(self, period: AlertPeriod) -> datetime:
        """Get start datetime for the given period"""
        now = datetime.utcnow()

        if period == AlertPeriod.HOUR:
            return now.replace(minute=0, second=0, microsecond=0)
        elif period == AlertPeriod.DAY:
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == AlertPeriod.WEEK:
            # Start of week (Monday)
            return now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=now.weekday())
        elif period == AlertPeriod.MONTH:
            return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        return now

    def _check_rule(self, rule: AlertRule) -> Optional[TriggeredAlert]:
        """
        Check if a single alert rule is triggered.

        Returns:
            TriggeredAlert if triggered, None otherwise
        """
        if not rule.enabled:
            return None

        state = self.states.get(rule.name)
        if not state or state.is_suppressed():
            return None

        # Get cost for period
        period_start = self._get_period_start(rule.period)
        costs = self.db.get_cost_by_component(start_date=period_start)

        # Sum total cost across all components
        total_cost = sum(c.get('total_cost', 0) or 0 for c in costs)

        if total_cost >= rule.threshold:
            alert = TriggeredAlert(
                rule_name=rule.name,
                threshold=rule.threshold,
                current_cost=total_cost,
                period=rule.period.value,
                message=rule.message
            )
            return alert

        return None

    def check_all(self) -> List[TriggeredAlert]:
        """
        Check all alert rules and return triggered alerts.

        Returns:
            List of triggered TriggeredAlert objects
        """
        self.triggered_alerts = []

        for rule in self.rules.values():
            alert = self._check_rule(rule)
            if alert:
                self.triggered_alerts.append(alert)
                self._execute_action(rule, alert)
                self._update_state(rule.name)

        return self.triggered_alerts

    def _execute_action(self, rule: AlertRule, alert: TriggeredAlert):
        """Execute the configured action for an alert"""
        try:
            if rule.action == AlertAction.LOG:
                self._action_log(alert)
            elif rule.action == AlertAction.PRINT:
                self._action_print(alert)
            elif rule.action == AlertAction.EMAIL:
                self._action_email(alert, rule.target)
            elif rule.action == AlertAction.WEBHOOK:
                self._action_webhook(alert, rule.target)
            elif rule.action == AlertAction.CALLBACK:
                self._action_callback(alert, rule.target)
        except Exception as e:
            self.logger.error(f"Error executing action for {rule.name}: {e}")

    def _action_log(self, alert: TriggeredAlert):
        """Log alert to file"""
        message = (
            f"BUDGET ALERT: {alert.rule_name} | "
            f"Current: ${alert.current_cost:.2f} / Threshold: ${alert.threshold:.2f} "
            f"({alert.period}) | {alert.message}"
        )
        self.logger.warning(message)

    def _action_print(self, alert: TriggeredAlert):
        """Print alert to console"""
        message = (
            f"\n{'='*70}\n"
            f"BUDGET ALERT: {alert.rule_name}\n"
            f"Current Cost: ${alert.current_cost:.2f}\n"
            f"Threshold: ${alert.threshold:.2f} ({alert.period})\n"
            f"Message: {alert.message}\n"
            f"{'='*70}\n"
        )
        print(message)
        self.logger.info(f"Printed alert: {alert.rule_name}")

    def _action_email(self, alert: TriggeredAlert, target: Optional[str]):
        """Send email alert (stub - requires external integration)"""
        message = f"[STUB] Would send email to {target}: {alert.message}"
        self.logger.info(message)

    def _action_webhook(self, alert: TriggeredAlert, target: Optional[str]):
        """POST to webhook URL (stub - requires requests library)"""
        message = f"[STUB] Would POST to webhook {target}: {alert.rule_name}"
        self.logger.info(message)

    def _action_callback(self, alert: TriggeredAlert, target: Optional[str]):
        """Call registered Python callback"""
        if not target or target not in self.callbacks:
            self.logger.error(f"Callback '{target}' not registered")
            return

        try:
            func = self.callbacks[target]
            func(alert)
            self.logger.info(f"Executed callback '{target}'")
        except Exception as e:
            self.logger.error(f"Error executing callback '{target}': {e}")

    def _update_state(self, rule_name: str):
        """Update alert state after triggering"""
        state = self.states[rule_name]
        state.last_triggered = datetime.utcnow().isoformat()
        state.trigger_count += 1

        # Suppress alert for 30 minutes to avoid spam
        state.suppress(duration_minutes=30)

        self._save_config()

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return {
            'alerts': [rule.to_dict() for rule in self.rules.values()],
            'states': [state.to_dict() for state in self.states.values()]
        }


# CLI Commands
@click.group()
@click.pass_context
def cli(ctx):
    """Budget Alert System - Monitor costs across sessions"""
    ctx.ensure_object(dict)
    ctx.obj['alerts'] = BudgetAlerts()


@cli.command()
@click.option('--name', required=True, help='Alert name')
@click.option('--threshold', type=float, required=True, help='Cost threshold (USD)')
@click.option('--period', default='day', help='Period: hour, day, week, month')
@click.option('--action', default='print', help='Action: log, email, webhook, print, callback')
@click.option('--message', default='', help='Alert message')
@click.option('--target', help='Target for action (email, webhook URL, or callback name)')
@click.pass_context
def add(ctx, name, threshold, period, action, message, target):
    """Add a new alert rule"""
    alerts = ctx.obj['alerts']
    if alerts.add_alert(name, threshold, period, action, message, target):
        click.echo(f"✓ Added alert '{name}'")
    else:
        click.echo(f"✗ Failed to add alert '{name}'", err=True)


@cli.command()
@click.option('--name', required=True, help='Alert name to remove')
@click.pass_context
def remove(ctx, name):
    """Remove an alert rule"""
    alerts = ctx.obj['alerts']
    if alerts.remove_alert(name):
        click.echo(f"✓ Removed alert '{name}'")
    else:
        click.echo(f"✗ Failed to remove alert '{name}'", err=True)


@cli.command()
@click.pass_context
def check(ctx):
    """Check all alert rules and trigger actions"""
    alerts = ctx.obj['alerts']
    triggered = alerts.check_all()

    if triggered:
        click.echo(f"\n{len(triggered)} alert(s) triggered:")
        for alert in triggered:
            click.echo(
                f"  - {alert.rule_name}: "
                f"${alert.current_cost:.2f} / ${alert.threshold:.2f}"
            )
    else:
        click.echo("No alerts triggered")


@cli.command()
@click.pass_context
def list(ctx):
    """List all alert rules"""
    alerts = ctx.obj['alerts']
    config = alerts.get_config()

    if not config['alerts']:
        click.echo("No alerts configured")
        return

    click.echo("\nConfigured Alerts:")
    for rule in config['alerts']:
        status = "enabled" if rule['enabled'] else "disabled"
        click.echo(
            f"  {rule['name']:20} "
            f"${rule['threshold']:8.2f}/{rule['period']:5} "
            f"→ {rule['action']:10} "
            f"[{status}]"
        )


@cli.command()
@click.pass_context
def status(ctx):
    """Show alert status"""
    alerts = ctx.obj['alerts']
    active = alerts.check_all()

    config = alerts.get_config()
    click.echo(f"\nAlert Status:")
    click.echo(f"  Total Rules: {len(config['alerts'])}")
    click.echo(f"  Active Alerts: {len(active)}")

    if active:
        click.echo("\n  Triggered:")
        for alert in active:
            click.echo(
                f"    - {alert.rule_name}: "
                f"${alert.current_cost:.2f} / ${alert.threshold:.2f} ({alert.period})"
            )


@cli.command()
@click.option('--name', required=True, help='Alert name')
@click.pass_context
def reset(ctx, name):
    """Reset alert state"""
    alerts = ctx.obj['alerts']
    if alerts.reset_alert(name):
        click.echo(f"✓ Reset alert '{name}'")
    else:
        click.echo(f"✗ Failed to reset alert '{name}'", err=True)


if __name__ == '__main__':
    cli(obj={})
