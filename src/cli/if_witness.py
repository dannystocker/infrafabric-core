#!/usr/bin/env python3
"""
IF.witness CLI - Provenance, Tracing, and Audit Tool

Commands:
  log     - Create new witness entry
  verify  - Verify hash chain integrity
  trace   - Follow full trace chain
  cost    - Show token/$ costs
  export  - Export audit trail

Philosophy: IF.ground Principle 8 - Observability without fragility
Every operation logged with provenance (who, what, when, why)
"""

import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

import click

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from witness.database import WitnessDatabase
from witness.models import Cost
from witness.crypto import WitnessCrypto


@click.group()
@click.option('--db', type=click.Path(), help='Database path (default: ~/.if-witness/witness.db)')
@click.pass_context
def cli(ctx, db):
    """IF.witness - Provenance and audit trail system"""
    ctx.ensure_object(dict)
    ctx.obj['db'] = WitnessDatabase(Path(db) if db else None)


@cli.command()
@click.option('--event', required=True, help='Event type (e.g., yologuard_scan)')
@click.option('--component', required=True, help='Component name (e.g., IF.yologuard)')
@click.option('--trace-id', required=True, help='Trace ID linking related operations')
@click.option('--payload', required=True, help='Event payload (JSON string)')
@click.option('--tokens-in', type=int, help='Input tokens used')
@click.option('--tokens-out', type=int, help='Output tokens used')
@click.option('--cost', type=float, help='Cost in USD')
@click.option('--model', help='Model used (e.g., claude-sonnet-4.5)')
@click.pass_context
def log(ctx, event, component, trace_id, payload, tokens_in, tokens_out, cost, model):
    """Create new witness entry"""
    db: WitnessDatabase = ctx.obj['db']

    try:
        # Parse payload
        payload_data = json.loads(payload)

        # Create cost object if provided
        cost_obj = None
        if any([tokens_in, tokens_out, cost, model]):
            cost_obj = Cost(
                tokens_in=tokens_in or 0,
                tokens_out=tokens_out or 0,
                cost_usd=cost or 0.0,
                model=model or 'unknown'
            )

        # Create entry
        entry = db.create_entry(
            event=event,
            component=component,
            trace_id=trace_id,
            payload=payload_data,
            cost=cost_obj
        )

        # Verify hash chain
        is_valid, error_msg, count = db.verify_all()

        click.echo(f"✓ Witness entry created: {entry.id}")
        click.echo(f"✓ Hash chain verified (entry {count - 1} → {count})")
        click.echo(f"✓ Signature: ed25519:{entry.signature[:16]}...")
        click.echo(f"✓ Content hash: {entry.content_hash[:16]}...")

        if cost_obj:
            click.echo(f"✓ Cost: ${cost_obj.cost_usd:.6f} ({cost_obj.tokens_in + cost_obj.tokens_out} tokens)")

    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON payload: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error creating entry: {e}", err=True)
        sys.exit(1)
    finally:
        db.close()


@cli.command()
@click.pass_context
def verify(ctx):
    """Verify hash chain integrity"""
    db: WitnessDatabase = ctx.obj['db']

    try:
        is_valid, error_msg, count = db.verify_all()

        if is_valid:
            click.echo(f"✓ {count} entries verified")
            click.echo("✓ Hash chain intact (no tampering)")
            click.echo("✓ All signatures valid")
        else:
            click.echo(f"❌ Verification failed: {error_msg}", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Error during verification: {e}", err=True)
        sys.exit(1)
    finally:
        db.close()


@cli.command()
@click.argument('trace_id')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
@click.pass_context
def trace(ctx, trace_id, format):
    """Follow full trace chain"""
    db: WitnessDatabase = ctx.obj['db']

    try:
        trace_info = db.get_trace(trace_id)

        if not trace_info.entries:
            click.echo(f"❌ No entries found for trace_id: {trace_id}", err=True)
            sys.exit(1)

        if format == 'json':
            click.echo(json.dumps(trace_info.to_dict(), indent=2))
        else:
            # Text format
            click.echo(f"\nTrace: {trace_id}")
            click.echo(f"Components: {', '.join(trace_info.components)}\n")

            for i, entry_dict in enumerate(trace_info.entries, 1):
                timestamp = datetime.fromisoformat(entry_dict['timestamp']).strftime('%H:%M:%S')
                click.echo(f"{i}. [{timestamp}] {entry_dict['component']}: {entry_dict['event']}")

                # Show payload summary
                payload = json.loads(entry_dict['payload']) if isinstance(entry_dict['payload'], str) else entry_dict['payload']
                payload_str = json.dumps(payload, indent=2)
                if len(payload_str) > 100:
                    payload_str = payload_str[:97] + "..."
                click.echo(f"   Payload: {payload_str}")

                # Show cost if available
                if entry_dict.get('cost_usd'):
                    tokens = (entry_dict.get('tokens_in') or 0) + (entry_dict.get('tokens_out') or 0)
                    click.echo(f"   Cost: ${entry_dict['cost_usd']:.6f} ({tokens} tokens, {entry_dict.get('model')})")

            click.echo(f"\nDuration: {trace_info.duration_seconds:.2f}s")
            click.echo(f"Total Cost: ${trace_info.total_cost_usd:.6f} ({trace_info.total_tokens} tokens)")

    except Exception as e:
        click.echo(f"❌ Error retrieving trace: {e}", err=True)
        sys.exit(1)
    finally:
        db.close()


@cli.command()
@click.option('--trace-id', help='Filter by trace ID')
@click.option('--component', help='Filter by component')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD)')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
@click.pass_context
def cost(ctx, trace_id, component, start_date, end_date, format):
    """Show token/$ costs breakdown"""
    db: WitnessDatabase = ctx.obj['db']

    try:
        if trace_id:
            # Show cost for specific trace
            trace_info = db.get_trace(trace_id)

            if format == 'json':
                click.echo(json.dumps({
                    'trace_id': trace_id,
                    'total_cost_usd': trace_info.total_cost_usd,
                    'total_tokens': trace_info.total_tokens,
                    'entries': trace_info.entries
                }, indent=2))
            else:
                click.echo(f"\nCost Breakdown (trace: {trace_id})\n")

                if not trace_info.entries:
                    click.echo("No entries found")
                    return

                # Print header
                click.echo(f"{'Component':<30} {'Tokens':<10} {'Cost':<12} {'Model':<20}")
                click.echo("-" * 72)

                # Group by component
                component_costs = {}
                for entry_dict in trace_info.entries:
                    comp = entry_dict['component']
                    if comp not in component_costs:
                        component_costs[comp] = {
                            'tokens': 0,
                            'cost': 0.0,
                            'model': entry_dict.get('model', 'unknown')
                        }

                    tokens = (entry_dict.get('tokens_in') or 0) + (entry_dict.get('tokens_out') or 0)
                    component_costs[comp]['tokens'] += tokens
                    component_costs[comp]['cost'] += entry_dict.get('cost_usd') or 0.0

                # Print rows
                for comp, data in component_costs.items():
                    click.echo(f"{comp:<30} {data['tokens']:<10} ${data['cost']:<11.6f} {data['model']:<20}")

                click.echo("-" * 72)
                click.echo(f"{'Total':<30} {trace_info.total_tokens:<10} ${trace_info.total_cost_usd:<11.6f}")

        else:
            # Show cost by component (with optional filters)
            start_dt = datetime.fromisoformat(start_date) if start_date else None
            end_dt = datetime.fromisoformat(end_date) if end_date else None

            cost_data = db.get_cost_by_component(component, start_dt, end_dt)

            if format == 'json':
                click.echo(json.dumps(cost_data, indent=2))
            else:
                click.echo("\nCost Breakdown by Component\n")

                if not cost_data:
                    click.echo("No cost data found")
                    return

                # Print header
                click.echo(f"{'Component':<30} {'Operations':<12} {'Tokens':<10} {'Cost':<12} {'Model':<20}")
                click.echo("-" * 84)

                total_ops = 0
                total_tokens = 0
                total_cost = 0.0

                for row in cost_data:
                    click.echo(f"{row['component']:<30} {row['operations']:<12} {row['total_tokens'] or 0:<10} "
                             f"${row['total_cost'] or 0.0:<11.6f} {row['model'] or 'unknown':<20}")
                    total_ops += row['operations']
                    total_tokens += row['total_tokens'] or 0
                    total_cost += row['total_cost'] or 0.0

                click.echo("-" * 84)
                click.echo(f"{'Total':<30} {total_ops:<12} {total_tokens:<10} ${total_cost:<11.6f}")

    except Exception as e:
        click.echo(f"❌ Error retrieving costs: {e}", err=True)
        sys.exit(1)
    finally:
        db.close()


def _parse_date_range(date_range_str: str) -> tuple[datetime, datetime]:
    """
    Parse date range string in format 'YYYY-MM-DD:YYYY-MM-DD' or 'YYYY-MM-DD'.

    Args:
        date_range_str: Date range string

    Returns:
        Tuple of (start_date, end_date)

    Raises:
        ValueError: If format is invalid
    """
    if not date_range_str:
        return None, None

    if ':' in date_range_str:
        # Range format: start:end
        parts = date_range_str.split(':')
        if len(parts) != 2:
            raise ValueError("Invalid date range format. Use 'YYYY-MM-DD:YYYY-MM-DD'")

        start_date = datetime.fromisoformat(parts[0])
        end_date = datetime.fromisoformat(parts[1])

        # Ensure start is before end
        if start_date > end_date:
            start_date, end_date = end_date, start_date

        # Set end_date to end of day
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        # Single day format
        single_date = datetime.fromisoformat(date_range_str)
        start_date = single_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = single_date.replace(hour=23, minute=59, second=59, microsecond=999999)

    return start_date, end_date


def _get_cost_summary(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate cost summary from entries.

    Args:
        entries: List of witness entries

    Returns:
        Dictionary with cost summary
    """
    total_cost = 0.0
    total_tokens = 0
    component_costs = {}

    for entry in entries:
        cost = entry.get('cost_usd') or 0.0
        tokens_in = entry.get('tokens_in') or 0
        tokens_out = entry.get('tokens_out') or 0
        component = entry.get('component', 'unknown')

        total_cost += cost
        total_tokens += tokens_in + tokens_out

        if component not in component_costs:
            component_costs[component] = {
                'component': component,
                'operations': 0,
                'total_tokens': 0,
                'total_cost': 0.0
            }

        component_costs[component]['operations'] += 1
        component_costs[component]['total_tokens'] += tokens_in + tokens_out
        component_costs[component]['total_cost'] += cost

    return {
        'total_cost_usd': total_cost,
        'total_tokens': total_tokens,
        'by_component': list(component_costs.values())
    }


@cli.command()
@click.option('--format', type=click.Choice(['json', 'csv', 'pdf']), default='json')
@click.option('--output', type=click.Path(), help='Output file path')
@click.option('--date-range', help='Date range filter (YYYY-MM-DD:YYYY-MM-DD or YYYY-MM-DD)')
@click.pass_context
def export(ctx, format, output, date_range):
    """Export audit trail (JSON, CSV, or PDF compliance report)"""
    db: WitnessDatabase = ctx.obj['db']

    try:
        # Parse date range if provided
        start_date, end_date = None, None
        if date_range:
            try:
                start_date, end_date = _parse_date_range(date_range)
            except ValueError as e:
                click.echo(f"❌ Invalid date range: {e}", err=True)
                sys.exit(1)

        # Export based on format
        if format == 'json':
            # Get all entries (apply date range filtering manually for JSON)
            if start_date or end_date:
                entries = db.get_entries_by_date_range(start_date, end_date)
                data = [e.to_dict() for e in entries]
            else:
                data = db.export_json()

            output_str = json.dumps(data, indent=2)

            if output:
                Path(output).write_text(output_str)
                click.echo(f"✓ Exported {len(data)} entries to {output}")
            else:
                click.echo(output_str)

        elif format == 'csv':
            data = db.export_csv_data(start_date, end_date)

            if not data:
                click.echo("No data to export")
                return

            # Generate default filename if not provided
            if not output:
                today = datetime.utcnow().strftime('%Y-%m-%d')
                output = f"witness_export_{today}.csv"

            with open(output, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            click.echo(f"✓ Exported {len(data)} entries to {output}")

        elif format == 'pdf':
            # Check if reportlab is available
            try:
                from witness.pdf_export import ComplianceReportGenerator
            except ImportError:
                click.echo(
                    "❌ PDF export requires reportlab. Install with: pip install reportlab>=4.0.0",
                    err=True
                )
                sys.exit(1)

            # Get entries
            if start_date or end_date:
                entries = db.get_entries_by_date_range(start_date, end_date)
                entries_dicts = [e.to_dict() for e in entries]
            else:
                entries_dicts = db.export_json()

            if not entries_dicts:
                click.echo("No data to export")
                return

            # Get verification results
            is_valid, error_msg, count = db.verify_all()
            verification_results = (is_valid, error_msg, count)

            # Get cost summary
            cost_summary = _get_cost_summary(entries_dicts)

            # Generate PDF
            generator = ComplianceReportGenerator()

            # Generate default filename if not provided
            if not output:
                today = datetime.utcnow().strftime('%Y-%m-%d')
                output = f"witness_report_{today}.pdf"

            pdf_path = generator.generate_pdf(
                entries=entries_dicts,
                output_path=output,
                verification_results=verification_results,
                cost_summary=cost_summary
            )

            click.echo(f"✓ Generated compliance report with {len(entries_dicts)} entries")
            click.echo(f"✓ Saved to {pdf_path}")

    except Exception as e:
        click.echo(f"❌ Error exporting data: {e}", err=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == '__main__':
    cli(obj={})
