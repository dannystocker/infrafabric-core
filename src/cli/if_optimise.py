#!/usr/bin/env python3
"""
IF.optimise CLI - Cost Tracking and Budget Management

Commands:
  rates     - Show current model rates
  budget    - Set and monitor budget limits
  report    - Generate cost reports
  estimate  - Estimate operation costs

Philosophy: IF.optimise - Cost-aware operations, budget constraints
Track tokens per operation, $ cost per model, budget alerts
"""

import sys
import json
import csv
import io
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

import click

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from witness.database import WitnessDatabase


# Model rates as of 2025-11-11
# Source: Anthropic, OpenAI, Google pricing pages
MODEL_RATES = {
    'gpt-5': {
        'input': 0.00005,   # $0.05 per 1M tokens
        'output': 0.00015,  # $0.15 per 1M tokens
    },
    'claude-sonnet-4.5': {
        'input': 0.000003,   # $3 per 1M tokens
        'output': 0.000015,  # $15 per 1M tokens
    },
    'claude-haiku-4.5': {
        'input': 0.00000025,  # $0.25 per 1M tokens
        'output': 0.00000125, # $1.25 per 1M tokens
    },
    'gemini-2.5-pro': {
        'input': 0.000001,   # $1 per 1M tokens
        'output': 0.000005,  # $5 per 1M tokens
    },
}


def calculate_cost(tokens_in: int, tokens_out: int, model: str) -> float:
    """Calculate cost for given token usage and model"""
    rates = MODEL_RATES.get(model, {'input': 0, 'output': 0})
    return (tokens_in * rates['input']) + (tokens_out * rates['output'])


def format_cost_data_as_csv(cost_data: List[Dict[str, Any]]) -> str:
    """Format cost data as CSV string"""
    if not cost_data:
        return ""

    output = io.StringIO()
    fieldnames = ['component', 'operations', 'total_tokens', 'total_cost', 'model']
    writer = csv.DictWriter(output, fieldnames=fieldnames)

    writer.writeheader()
    for row in cost_data:
        writer.writerow({
            'component': row['component'],
            'operations': row['operations'],
            'total_tokens': row['total_tokens'] or 0,
            'total_cost': row['total_cost'] or 0.0,
            'model': row['model'] or 'unknown'
        })

    return output.getvalue()


@click.group()
@click.option('--db', type=click.Path(), help='Database path (default: ~/.if-witness/witness.db)')
@click.pass_context
def cli(ctx, db):
    """IF.optimise - Cost tracking and budget management"""
    ctx.ensure_object(dict)
    ctx.obj['db'] = WitnessDatabase(Path(db) if db else None)


@cli.command()
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def rates(format):
    """Show current model rates"""
    if format == 'json':
        click.echo(json.dumps(MODEL_RATES, indent=2))
    else:
        click.echo("\nCurrent Model Rates (per token)\n")
        click.echo(f"{'Model':<25} {'Input':<15} {'Output':<15}")
        click.echo("-" * 55)

        for model, rate in MODEL_RATES.items():
            click.echo(f"{model:<25} ${rate['input']:<14.8f} ${rate['output']:<14.8f}")

        click.echo("\nExample: 1M input + 1M output tokens")
        click.echo(f"{'Model':<25} {'Total Cost':<15}")
        click.echo("-" * 40)

        for model, rate in MODEL_RATES.items():
            cost = calculate_cost(1_000_000, 1_000_000, model)
            click.echo(f"{model:<25} ${cost:<14.2f}")


@cli.command()
@click.option('--set', 'budget_amount', type=float, help='Set budget limit in USD')
@click.option('--period', type=click.Choice(['day', 'week', 'month']), default='month', help='Budget period')
@click.option('--component', help='Component filter (optional)')
@click.pass_context
def budget(ctx, budget_amount, period, component):
    """Set and monitor budget limits"""
    db: WitnessDatabase = ctx.obj['db']

    try:
        # Calculate period start date
        now = datetime.utcnow()
        if period == 'day':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        else:  # month
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Get current spending
        cost_data = db.get_cost_by_component(component, start_date, None)

        total_spent = sum(row['total_cost'] or 0.0 for row in cost_data)
        total_tokens = sum(row['total_tokens'] or 0 for row in cost_data)
        total_ops = sum(row['operations'] for row in cost_data)

        if budget_amount:
            # Setting new budget
            budget_file = Path.home() / '.if-witness' / 'budget.json'
            budget_file.parent.mkdir(parents=True, exist_ok=True)

            budget_config = {
                'amount': budget_amount,
                'period': period,
                'component': component,
                'set_at': now.isoformat(),
            }

            budget_file.write_text(json.dumps(budget_config, indent=2))
            click.echo(f"✓ Budget set: ${budget_amount:.2f} per {period}")

        else:
            # Check existing budget
            budget_file = Path.home() / '.if-witness' / 'budget.json'
            if budget_file.exists():
                budget_config = json.loads(budget_file.read_text())
                budget_amount = budget_config['amount']
            else:
                budget_amount = 100.0  # Default budget

        # Calculate usage percentage
        usage_pct = (total_spent / budget_amount * 100) if budget_amount > 0 else 0
        remaining = budget_amount - total_spent

        # Display budget status
        click.echo(f"\n Budget Status ({period})")
        click.echo("-" * 40)
        click.echo(f"Period:       {start_date.strftime('%Y-%m-%d')} - {now.strftime('%Y-%m-%d')}")
        click.echo(f"Budget:       ${budget_amount:.2f}")
        click.echo(f"Spent:        ${total_spent:.6f}")
        click.echo(f"Remaining:    ${remaining:.6f}")
        click.echo(f"Usage:        {usage_pct:.2f}%")
        click.echo(f"Operations:   {total_ops}")
        click.echo(f"Total tokens: {total_tokens:,}")

        # Alert if over threshold
        if usage_pct >= 100:
            click.echo("\n⚠️  ALERT: Budget exceeded!", err=True)
        elif usage_pct >= 80:
            click.echo(f"\n⚠️  WARNING: {usage_pct:.0f}% of budget used")
        elif usage_pct >= 50:
            click.echo(f"\n⚡ NOTICE: {usage_pct:.0f}% of budget used")

        # Show projected monthly cost
        if period == 'day':
            days_elapsed = 1
            days_in_period = 30
        elif period == 'week':
            days_elapsed = (now - start_date).days + 1
            days_in_period = 7
        else:  # month
            days_elapsed = (now - start_date).days + 1
            days_in_period = 30

        if days_elapsed > 0:
            daily_rate = total_spent / days_elapsed
            projected = daily_rate * days_in_period

            click.echo(f"\nProjected {period} total: ${projected:.2f}")

    except Exception as e:
        click.echo(f"❌ Error checking budget: {e}", err=True)
        sys.exit(1)
    finally:
        db.close()


@cli.command()
@click.option('--component', help='Filter by component')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD)')
@click.option('--group-by', type=click.Choice(['component', 'model', 'day']), default='component')
@click.option('--format', type=click.Choice(['text', 'json', 'csv']), default='text')
@click.pass_context
def report(ctx, component, start_date, end_date, group_by, format):
    """Generate cost reports"""
    db: WitnessDatabase = ctx.obj['db']

    try:
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        cost_data = db.get_cost_by_component(component, start_dt, end_dt)

        if format == 'json':
            click.echo(json.dumps(cost_data, indent=2))
        elif format == 'csv':
            csv_output = format_cost_data_as_csv(cost_data)
            click.echo(csv_output)
        else:
            if not cost_data:
                click.echo("No cost data found")
                return

            period_str = ""
            if start_date and end_date:
                period_str = f" ({start_date} to {end_date})"
            elif start_date:
                period_str = f" (from {start_date})"
            elif end_date:
                period_str = f" (until {end_date})"

            click.echo(f"\nIF.optimise Cost Report{period_str}")
            click.echo(f"Group by: {group_by}\n")

            # Print header
            click.echo(f"{'Component':<30} {'Operations':<12} {'Tokens':<12} {'Cost':<12} {'Model':<20}")
            click.echo("-" * 86)

            total_ops = 0
            total_tokens = 0
            total_cost = 0.0

            for row in cost_data:
                click.echo(f"{row['component']:<30} {row['operations']:<12} "
                         f"{row['total_tokens'] or 0:<12,} "
                         f"${row['total_cost'] or 0.0:<11.6f} "
                         f"{row['model'] or 'unknown':<20}")

                total_ops += row['operations']
                total_tokens += row['total_tokens'] or 0
                total_cost += row['total_cost'] or 0.0

            click.echo("-" * 86)
            click.echo(f"{'Total':<30} {total_ops:<12} {total_tokens:<12,} ${total_cost:<11.6f}")

            # Cost efficiency metrics
            if total_ops > 0:
                avg_cost_per_op = total_cost / total_ops
                avg_tokens_per_op = total_tokens / total_ops

                click.echo(f"\nEfficiency Metrics:")
                click.echo(f"  Average cost per operation: ${avg_cost_per_op:.6f}")
                click.echo(f"  Average tokens per operation: {avg_tokens_per_op:,.0f}")

    except Exception as e:
        click.echo(f"❌ Error generating report: {e}", err=True)
        sys.exit(1)
    finally:
        db.close()


@cli.command()
@click.option('--tokens-in', type=int, required=True, help='Estimated input tokens')
@click.option('--tokens-out', type=int, required=True, help='Estimated output tokens')
@click.option('--model', required=True, help='Model name')
@click.option('--operations', type=int, default=1, help='Number of operations')
def estimate(tokens_in, tokens_out, model, operations):
    """Estimate operation costs"""
    if model not in MODEL_RATES:
        click.echo(f"❌ Unknown model: {model}", err=True)
        click.echo(f"Available models: {', '.join(MODEL_RATES.keys())}")
        sys.exit(1)

    cost_per_op = calculate_cost(tokens_in, tokens_out, model)
    total_cost = cost_per_op * operations

    click.echo(f"\nCost Estimate")
    click.echo("-" * 40)
    click.echo(f"Model:          {model}")
    click.echo(f"Input tokens:   {tokens_in:,}")
    click.echo(f"Output tokens:  {tokens_out:,}")
    click.echo(f"Total tokens:   {tokens_in + tokens_out:,}")
    click.echo(f"Cost per op:    ${cost_per_op:.6f}")

    if operations > 1:
        click.echo(f"Operations:     {operations:,}")
        click.echo(f"Total cost:     ${total_cost:.6f}")

    # Show budget impact
    budget_file = Path.home() / '.if-witness' / 'budget.json'
    if budget_file.exists():
        budget_config = json.loads(budget_file.read_text())
        budget_amount = budget_config['amount']
        budget_pct = (total_cost / budget_amount * 100) if budget_amount > 0 else 0

        click.echo(f"\nBudget Impact:")
        click.echo(f"  ${total_cost:.6f} / ${budget_amount:.2f} ({budget_pct:.2f}%)")


if __name__ == '__main__':
    cli(obj={})
