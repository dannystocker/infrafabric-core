#!/usr/bin/env python3
"""
IF.witness Cost Tracker - Lightweight cost logging utility for sessions.
Wraps WitnessDatabase for quick cost tracking without full CLI overhead.

Usage:
    python3 tools/cost-tracker.py log --component IF.ndi --tokens-in 100 --tokens-out 50 --model claude-haiku-4.5
    python3 tools/cost-tracker.py report --period day
    python3 tools/cost-tracker.py check --budget 10
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import click

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.witness.database import WitnessDatabase
from src.witness.models import Cost
from uuid import uuid4


class CostTracker:
    """
    Lightweight cost tracking wrapper for witness database.

    Optimized for quick cost logging from Sessions 1-4 without
    calling the full CLI infrastructure.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize cost tracker with witness database.

        Args:
            db_path: Path to witness database. Defaults to ~/.if-witness/witness.db
        """
        if db_path:
            self.db = WitnessDatabase(db_path=Path(db_path))
        else:
            self.db = WitnessDatabase()
        self.db_path = self.db.db_path

    def log_cost(
        self,
        component: str,
        tokens_in: int,
        tokens_out: int,
        model: str,
        trace_id: Optional[str] = None,
        event: str = "cost_logged"
    ) -> str:
        """
        Quick cost logging to witness database.

        Args:
            component: Component name (e.g., "IF.ndi", "IF.witness")
            tokens_in: Input tokens consumed
            tokens_out: Output tokens generated
            model: Model identifier (e.g., "claude-haiku-4.5")
            trace_id: Optional trace ID for linking operations
            event: Event type (default: "cost_logged")

        Returns:
            Entry ID for the logged cost
        """
        # Calculate cost (simplified: using rough token pricing)
        # Haiku-4.5: $0.80/$4 per 1M tokens in/out
        # Sonnet-4.5: $3/$15 per 1M tokens
        cost_usd = self._calculate_cost(tokens_in, tokens_out, model)

        # Create cost object
        cost = Cost(
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost_usd,
            model=model
        )

        # Generate trace ID if not provided
        if not trace_id:
            trace_id = str(uuid4())

        # Create witness entry
        entry = self.db.create_entry(
            event=event,
            component=component,
            trace_id=trace_id,
            payload={
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "model": model
            },
            cost=cost
        )

        return entry.id

    def get_total_cost(
        self,
        component: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get total cost summary, optionally filtered by component and date.

        Args:
            component: Optional component filter
            since: Optional start datetime (defaults to start of day)

        Returns:
            Dictionary with cost metrics
        """
        if since is None:
            since = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        cost_data = self.db.get_cost_by_component(
            component=component,
            start_date=since
        )

        total_usd = sum(row['total_cost'] or 0 for row in cost_data)
        total_tokens = sum(row['total_tokens'] or 0 for row in cost_data)
        total_ops = sum(row['operations'] or 0 for row in cost_data)

        return {
            "total_cost_usd": round(total_usd, 6),
            "total_tokens": total_tokens,
            "total_operations": total_ops,
            "period_start": since.isoformat(),
            "breakdown": cost_data
        }

    def check_budget(
        self,
        limit: float,
        period: str = "day"
    ) -> Dict[str, Any]:
        """
        Check if cost is within budget limit.

        Args:
            limit: Budget limit in USD
            period: Time period ("day", "week", "month")

        Returns:
            Dictionary with budget status
        """
        # Calculate period start time
        now = datetime.utcnow()
        if period == "day":
            since = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            since = now - timedelta(days=now.weekday())
            since = since.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "month":
            since = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            raise ValueError(f"Unknown period: {period}")

        cost_data = self.get_total_cost(since=since)
        spent = cost_data["total_cost_usd"]

        return {
            "budget_limit": limit,
            "spent": spent,
            "remaining": round(limit - spent, 6),
            "percent_used": round((spent / limit * 100) if limit > 0 else 0, 2),
            "over_budget": spent > limit,
            "period": period,
            "period_start": cost_data["period_start"]
        }

    def get_report(self, period: str = "day") -> str:
        """
        Generate formatted text report.

        Args:
            period: Time period for report

        Returns:
            Formatted report string
        """
        now = datetime.utcnow()
        if period == "day":
            since = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_label = "Today"
        elif period == "week":
            since = now - timedelta(days=now.weekday())
            since = since.replace(hour=0, minute=0, second=0, microsecond=0)
            period_label = "This Week"
        elif period == "month":
            since = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            period_label = "This Month"
        else:
            raise ValueError(f"Unknown period: {period}")

        cost_data = self.get_total_cost(since=since)

        lines = [
            f"IF.witness Cost Report - {period_label}",
            "=" * 50,
            f"Total Cost:       ${cost_data['total_cost_usd']:.6f}",
            f"Total Tokens:     {cost_data['total_tokens']:,}",
            f"Total Operations: {cost_data['total_operations']}",
            f"Period Start:     {cost_data['period_start']}",
            ""
        ]

        if cost_data['breakdown']:
            lines.append("Breakdown by Component:")
            lines.append("-" * 50)
            for row in cost_data['breakdown']:
                component = row['component']
                cost = row['total_cost'] or 0
                tokens = row['total_tokens'] or 0
                ops = row['operations'] or 0
                model = row['model'] or 'unknown'
                lines.append(f"  {component:20} ${cost:10.6f} ({tokens:,} tokens, {ops} ops) [{model}]")

        return "\n".join(lines)

    def _calculate_cost(self, tokens_in: int, tokens_out: int, model: str) -> float:
        """Calculate approximate cost based on model and token counts."""
        # Pricing as of Nov 2024 (in USD per 1M tokens)
        pricing = {
            "claude-haiku-4.5": (0.80, 4.00),
            "claude-3-5-sonnet": (3.00, 15.00),
            "claude-sonnet-4-5": (3.00, 15.00),
        }

        # Default to haiku pricing if model not found
        in_price, out_price = pricing.get(model, (0.80, 4.00))

        cost = (tokens_in * in_price + tokens_out * out_price) / 1_000_000
        return round(cost, 6)


# CLI Interface
@click.group()
def cli():
    """IF.witness Cost Tracker - Quick cost logging utility."""
    pass


@cli.command()
@click.option("--component", required=True, help="Component name (e.g., IF.ndi)")
@click.option("--tokens-in", type=int, required=True, help="Input tokens")
@click.option("--tokens-out", type=int, required=True, help="Output tokens")
@click.option("--model", required=True, help="Model identifier")
@click.option("--trace-id", default=None, help="Optional trace ID")
@click.option("--db-path", default=None, help="Database path (default: ~/.if-witness/witness.db)")
def log(component: str, tokens_in: int, tokens_out: int, model: str, trace_id: str, db_path: str):
    """Log a cost entry to the witness database."""
    try:
        tracker = CostTracker(db_path=db_path)
        entry_id = tracker.log_cost(component, tokens_in, tokens_out, model, trace_id)
        click.echo(f"✓ Cost logged: {entry_id}")
        click.echo(f"  Component: {component}")
        click.echo(f"  Tokens: {tokens_in} in + {tokens_out} out")
        click.echo(f"  Model: {model}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--period", type=click.Choice(["day", "week", "month"]), default="day", help="Report period")
@click.option("--component", default=None, help="Optional component filter")
@click.option("--db-path", default=None, help="Database path")
def report(period: str, component: str, db_path: str):
    """Generate a cost report for the specified period."""
    try:
        tracker = CostTracker(db_path=db_path)
        report_text = tracker.get_report(period=period)
        click.echo(report_text)
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--budget", type=float, required=True, help="Budget limit in USD")
@click.option("--period", type=click.Choice(["day", "week", "month"]), default="day", help="Budget period")
@click.option("--db-path", default=None, help="Database path")
def check(budget: float, period: str, db_path: str):
    """Check budget status."""
    try:
        tracker = CostTracker(db_path=db_path)
        status = tracker.check_budget(limit=budget, period=period)

        icon = "✓" if not status["over_budget"] else "✗"
        click.echo(f"{icon} Budget Check - {period.capitalize()}")
        click.echo(f"  Limit:    ${status['budget_limit']:.2f}")
        click.echo(f"  Spent:    ${status['spent']:.6f}")
        click.echo(f"  Remaining: ${status['remaining']:.6f}")
        click.echo(f"  Used:     {status['percent_used']:.1f}%")

        if status["over_budget"]:
            click.echo(f"\n⚠ OVER BUDGET by ${abs(status['remaining']):.6f}", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
