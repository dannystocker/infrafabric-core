#!/usr/bin/env python3
"""
Cost Monitoring Agent for IF.witness
Autonomous monitoring of session costs against budget limits with real-time alerts.

Philosophy: IF.ground Principle 8 - Observability without fragility.
Monitor costs in real-time, alert before budget overruns, maintain audit trail.
"""

import logging
import threading
import time
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
import sys

import click


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('cost-monitor')


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EXCEEDED = "exceeded"


@dataclass
class Alert:
    """Cost alert with metadata"""
    timestamp: datetime
    level: AlertLevel
    message: str
    threshold: float  # Percentage (0-1)
    budget_type: str  # "daily", "weekly", "monthly", "total", "component"
    budget_name: Optional[str]  # Component name if applicable
    current_cost: float
    budget_limit: float
    percentage: float  # Current usage as percentage

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.value,
            'message': self.message,
            'threshold': self.threshold,
            'budget_type': self.budget_type,
            'budget_name': self.budget_name,
            'current_cost': self.current_cost,
            'budget_limit': self.budget_limit,
            'percentage': self.percentage,
        }


@dataclass
class BudgetStatus:
    """Current budget status"""
    budget_type: str
    budget_name: Optional[str]
    limit: float
    current: float
    percentage: float
    remaining: float
    status: str  # "ok", "warning", "exceeded"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CostMonitor:
    """
    Autonomous cost monitoring agent for IF.witness sessions.

    Monitors:
    - Daily, weekly, monthly budgets
    - Per-component budgets
    - Total session budget
    - Triggers alerts at 50%, 75%, 90%, 100% thresholds
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        budget_limits: Optional[Dict[str, float]] = None,
        check_interval: int = 60,
    ):
        """
        Initialize cost monitor.

        Args:
            db_path: Path to witness database (default: ~/.if-witness/witness.db)
            budget_limits: Dict with keys: daily, weekly, monthly, total
                          e.g., {'daily': 10, 'weekly': 50, 'monthly': 200, 'total': 500}
            check_interval: Seconds between cost checks (default: 60)
        """
        # Resolve database path
        if db_path is None:
            self.db_path = Path.home() / '.if-witness' / 'witness.db'
        else:
            self.db_path = Path(db_path).expanduser()

        # Budget configuration
        self.budget_limits = budget_limits or {
            'daily': 10.0,
            'weekly': 50.0,
            'monthly': 200.0,
            'total': 500.0,
        }

        # Monitoring configuration
        self.check_interval = check_interval
        self.thresholds = [0.5, 0.75, 0.9, 1.0]  # 50%, 75%, 90%, 100%

        # Monitoring state
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False

        # Alert management
        self._alerts: List[Alert] = []
        self._alert_callbacks: Dict[float, List[Callable]] = {
            t: [] for t in self.thresholds
        }
        self._alert_cooldown: Dict[str, datetime] = {}  # key: "{budget_type}:{name}", value: cooldown_until
        self._cooldown_minutes = 5

        # Thread safety
        self._lock = threading.Lock()
        self._status_lock = threading.Lock()

        # Status tracking
        self._last_status: Dict[str, BudgetStatus] = {}

        logger.info(f"Cost monitor initialized: {self.db_path}")
        logger.info(f"Budget limits: {self.budget_limits}")

    def start(self) -> None:
        """Start monitoring in background thread"""
        if self._running:
            logger.warning("Monitor is already running")
            return

        self._running = True
        self._stop_event.clear()

        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="CostMonitorThread"
        )
        self._monitor_thread.start()
        logger.info("Cost monitor started")

    def stop(self) -> None:
        """Stop monitoring gracefully"""
        if not self._running:
            logger.warning("Monitor is not running")
            return

        logger.info("Stopping cost monitor...")
        self._stop_event.set()
        self._running = False

        if self._monitor_thread:
            self._monitor_thread.join(timeout=10)
            logger.info("Cost monitor stopped")

    def register_callback(self, threshold: float, callback: Callable[[Alert], None]) -> None:
        """
        Register callback for alert threshold.

        Args:
            threshold: Percentage threshold (0.5, 0.75, 0.9, 1.0)
            callback: Function to call with Alert object
        """
        if threshold not in self.thresholds:
            raise ValueError(f"Invalid threshold {threshold}. Must be one of {self.thresholds}")

        with self._lock:
            if callback not in self._alert_callbacks[threshold]:
                self._alert_callbacks[threshold].append(callback)
                logger.info(f"Registered callback for {threshold*100}% threshold")

    def check_costs(self) -> Dict[str, BudgetStatus]:
        """
        Check current costs against budgets.

        Returns:
            Dict mapping budget names to BudgetStatus
        """
        try:
            if not self.db_path.exists():
                logger.warning(f"Database not found: {self.db_path}")
                return {}

            statuses = {}

            # Check daily budget
            daily_cost = self._get_cost_for_period('day')
            statuses['daily'] = self._make_budget_status('daily', None, daily_cost)

            # Check weekly budget
            weekly_cost = self._get_cost_for_period('week')
            statuses['weekly'] = self._make_budget_status('weekly', None, weekly_cost)

            # Check monthly budget
            monthly_cost = self._get_cost_for_period('month')
            statuses['monthly'] = self._make_budget_status('monthly', None, monthly_cost)

            # Check total budget
            total_cost = self._get_total_cost()
            statuses['total'] = self._make_budget_status('total', None, total_cost)

            # Check per-component budgets (if configured)
            if 'components' in self.budget_limits:
                comp_budgets = self.budget_limits['components']
                for component, limit in comp_budgets.items():
                    comp_cost = self._get_cost_for_component(component)
                    statuses[f'component:{component}'] = self._make_budget_status(
                        'component', component, comp_cost, limit
                    )

            with self._status_lock:
                self._last_status = statuses

            return statuses

        except Exception as e:
            logger.error(f"Error checking costs: {e}")
            return {}

    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        with self._status_lock:
            return {
                'running': self._running,
                'db_path': str(self.db_path),
                'budget_limits': self.budget_limits,
                'check_interval': self.check_interval,
                'last_check': datetime.now().isoformat(),
                'budgets': {k: v.to_dict() for k, v in self._last_status.items()},
                'recent_alerts': [a.to_dict() for a in self._alerts[-10:]],
            }

    # Private methods

    def _monitor_loop(self) -> None:
        """Background monitoring loop"""
        logger.info(f"Monitor loop started (interval: {self.check_interval}s)")

        while not self._stop_event.is_set():
            try:
                # Check costs and detect threshold crossings
                self.check_costs()
                self._check_thresholds()

            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")

            # Wait for next check or stop signal
            self._stop_event.wait(self.check_interval)

        logger.info("Monitor loop ended")

    def _check_thresholds(self) -> None:
        """Check if any thresholds have been crossed"""
        with self._status_lock:
            for budget_name, status in self._last_status.items():
                # Check each threshold
                for threshold in self.thresholds:
                    if status.percentage >= threshold:
                        self._trigger_alert(status, threshold)

    def _trigger_alert(self, status: BudgetStatus, threshold: float) -> None:
        """Trigger alert if not in cooldown"""
        alert_key = f"{status.budget_type}:{status.budget_name}"

        # Check cooldown
        with self._lock:
            if alert_key in self._alert_cooldown:
                if datetime.now() < self._alert_cooldown[alert_key]:
                    return  # Still in cooldown
            else:
                # Set cooldown
                self._alert_cooldown[alert_key] = datetime.now() + timedelta(minutes=self._cooldown_minutes)

        # Determine alert level
        if status.percentage >= 1.0:
            level = AlertLevel.EXCEEDED
        elif status.percentage >= 0.9:
            level = AlertLevel.CRITICAL
        else:
            level = AlertLevel.WARNING

        # Create alert
        alert = Alert(
            timestamp=datetime.now(),
            level=level,
            message=self._format_alert_message(status),
            threshold=threshold,
            budget_type=status.budget_type,
            budget_name=status.budget_name,
            current_cost=status.current,
            budget_limit=status.limit,
            percentage=status.percentage,
        )

        # Store alert
        with self._lock:
            self._alerts.append(alert)

        # Log alert
        logger.log(
            logging.ERROR if level in [AlertLevel.CRITICAL, AlertLevel.EXCEEDED] else logging.WARNING,
            f"{level.value.upper()}: {alert.message}"
        )

        # Call callbacks
        self._call_callbacks(threshold, alert)

    def _call_callbacks(self, threshold: float, alert: Alert) -> None:
        """Call registered callbacks for threshold"""
        callbacks = self._alert_callbacks.get(threshold, [])
        for callback in callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error calling alert callback: {e}")

    def _format_alert_message(self, status: BudgetStatus) -> str:
        """Format human-readable alert message"""
        name = status.budget_name or status.budget_type
        pct = status.percentage * 100
        return (
            f"{status.budget_type.title()} budget '{name}' at {pct:.1f}% "
            f"(${status.current:.2f} of ${status.limit:.2f})"
        )

    def _make_budget_status(
        self,
        budget_type: str,
        budget_name: Optional[str],
        current_cost: float,
        limit: Optional[float] = None,
    ) -> BudgetStatus:
        """Create BudgetStatus from costs and limits"""
        if limit is None:
            # Get limit from budget_limits config
            if budget_type == 'component':
                limit = self.budget_limits.get('components', {}).get(budget_name, 0)
            else:
                limit = self.budget_limits.get(budget_type, 0)

        if limit <= 0:
            limit = 0.01  # Avoid division by zero

        percentage = min(current_cost / limit, 1.0)
        remaining = max(limit - current_cost, 0)

        # Determine status
        if percentage >= 1.0:
            status_str = 'exceeded'
        elif percentage >= 0.9:
            status_str = 'critical'
        elif percentage >= 0.75:
            status_str = 'warning'
        else:
            status_str = 'ok'

        return BudgetStatus(
            budget_type=budget_type,
            budget_name=budget_name,
            limit=limit,
            current=current_cost,
            percentage=percentage,
            remaining=remaining,
            status=status_str,
        )

    def _get_cost_for_period(self, period: str) -> float:
        """Get total cost for time period"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row

            # Calculate date range
            now = datetime.utcnow()
            if period == 'day':
                start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == 'week':
                start = now - timedelta(days=now.weekday())
                start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == 'month':
                start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                start = None

            # Query
            query = "SELECT COALESCE(SUM(cost_usd), 0) as total FROM witness_entries WHERE 1=1"
            params = []

            if start:
                query += " AND timestamp >= ?"
                params.append(start.isoformat())

            cursor = conn.execute(query, params)
            result = cursor.fetchone()
            total = result['total'] if result else 0.0

            conn.close()
            return float(total)

        except Exception as e:
            logger.error(f"Error getting cost for period {period}: {e}")
            return 0.0

    def _get_total_cost(self) -> float:
        """Get total cost across all entries"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row

            cursor = conn.execute(
                "SELECT COALESCE(SUM(cost_usd), 0) as total FROM witness_entries"
            )
            result = cursor.fetchone()
            total = result['total'] if result else 0.0

            conn.close()
            return float(total)

        except Exception as e:
            logger.error(f"Error getting total cost: {e}")
            return 0.0

    def _get_cost_for_component(self, component: str) -> float:
        """Get total cost for specific component"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row

            cursor = conn.execute(
                "SELECT COALESCE(SUM(cost_usd), 0) as total FROM witness_entries WHERE component = ?",
                (component,)
            )
            result = cursor.fetchone()
            total = result['total'] if result else 0.0

            conn.close()
            return float(total)

        except Exception as e:
            logger.error(f"Error getting cost for component {component}: {e}")
            return 0.0


# CLI Interface

@click.group()
def cli():
    """Cost monitoring agent for IF.witness"""
    pass


@cli.command()
@click.option('--db', type=click.Path(), help='Database path')
@click.option('--budget-daily', type=float, help='Daily budget limit (USD)')
@click.option('--budget-weekly', type=float, help='Weekly budget limit (USD)')
@click.option('--budget-monthly', type=float, help='Monthly budget limit (USD)')
@click.option('--budget-total', type=float, help='Total budget limit (USD)')
@click.option('--check-interval', type=int, default=60, help='Check interval (seconds)')
def start(db, budget_daily, budget_weekly, budget_monthly, budget_total, check_interval):
    """Start cost monitor"""
    # Build budget limits
    budgets = {}
    if budget_daily:
        budgets['daily'] = budget_daily
    if budget_weekly:
        budgets['weekly'] = budget_weekly
    if budget_monthly:
        budgets['monthly'] = budget_monthly
    if budget_total:
        budgets['total'] = budget_total

    # Create and start monitor
    monitor = CostMonitor(
        db_path=db,
        budget_limits=budgets or None,
        check_interval=check_interval,
    )

    # Register simple log callback
    def log_alert(alert: Alert):
        level_emoji = {
            AlertLevel.INFO: 'ℹ',
            AlertLevel.WARNING: '⚠',
            AlertLevel.CRITICAL: '🚨',
            AlertLevel.EXCEEDED: '❌',
        }
        emoji = level_emoji.get(alert.level, '•')
        click.echo(f"{emoji} {alert.message}")

    for threshold in monitor.thresholds:
        monitor.register_callback(threshold, log_alert)

    monitor.start()

    try:
        click.echo("Cost monitor running (press Ctrl+C to stop)...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\nStopping monitor...")
        monitor.stop()
        click.echo("Done")


@cli.command()
@click.option('--db', type=click.Path(), help='Database path')
@click.option('--format', type=click.Choice(['json', 'table']), default='table', help='Output format')
def status(db, format):
    """Check monitor status"""
    monitor = CostMonitor(db_path=db)
    status_data = monitor.get_status()

    if format == 'json':
        click.echo(json.dumps(status_data, indent=2, default=str))
    else:
        # Table format
        click.echo("\nBudget Status:")
        click.echo("-" * 80)

        for budget_name, budget_data in status_data.get('budgets', {}).items():
            pct = budget_data['percentage'] * 100
            status_color = {
                'ok': click.style('OK', fg='green'),
                'warning': click.style('WARNING', fg='yellow'),
                'critical': click.style('CRITICAL', fg='red'),
                'exceeded': click.style('EXCEEDED', fg='red', bold=True),
            }
            status_str = status_color.get(budget_data['status'], budget_data['status'])

            click.echo(
                f"{budget_name:20} {pct:6.1f}% "
                f"${budget_data['current']:7.2f} / ${budget_data['limit']:7.2f} {status_str}"
            )

        # Recent alerts
        alerts = status_data.get('recent_alerts', [])
        if alerts:
            click.echo("\nRecent Alerts:")
            click.echo("-" * 80)
            for alert in alerts[-5:]:
                click.echo(f"[{alert['level'].upper()}] {alert['message']}")


if __name__ == '__main__':
    cli()
