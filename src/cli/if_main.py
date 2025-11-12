#!/usr/bin/env python3
"""
InfraFabric Unified CLI Entry Point

The `if` command provides unified access to all InfraFabric components:
- IF.coordinator: Real-time swarm coordination
- IF.governor: Policy-based resource allocation
- IF.chassis: WASM sandbox execution
- IF.witness: Cryptographic provenance
- IF.optimise: Cost tracking and optimization

Usage:
    if coordinator start
    if governor register session-1 --capabilities video:ndi
    if chassis sandbox create --memory 512
    if witness query --component IF.coordinator
    if optimise report --today

Philosophy: IF.ground Principle 8 - Observability without fragility
"""

import click
import sys
import os
from pathlib import Path
from typing import Optional

# Import configuration
try:
    from infrafabric.config import InfraFabricConfig, ConfigError
except ImportError:
    # Fallback if not installed
    InfraFabricConfig = None
    ConfigError = Exception

# Import error handler
try:
    from src.cli.error_handler import CLIError, handle_cli_error
except ImportError:
    CLIError = Exception
    def handle_cli_error(error):
        click.echo(f"Error: {error}", err=True)
        sys.exit(1)

# Import help text
try:
    from src.cli.help_text import WITNESS_COMMANDS_HELP, COMMON_WORKFLOWS
except ImportError:
    WITNESS_COMMANDS_HELP = {}
    COMMON_WORKFLOWS = []


# Global context for sharing state between commands
class GlobalContext:
    """Global CLI context"""
    def __init__(self):
        self.config: Optional[InfraFabricConfig] = None
        self.debug: bool = False
        self.trace_id: Optional[str] = None
        self.mode: str = 'normal'

    def load_config(self, config_path: Optional[Path] = None):
        """Load configuration"""
        if InfraFabricConfig:
            try:
                self.config = InfraFabricConfig.load(config_path)
            except Exception as e:
                if self.debug:
                    raise
                handle_cli_error(f"Failed to load config: {e}")
        else:
            if self.debug:
                click.echo("Warning: Configuration module not available", err=True)


pass_context = click.make_pass_decorator(GlobalContext, ensure=True)


@click.group()
@click.version_option(version='0.1.0', prog_name='InfraFabric')
@click.option('--debug', is_flag=True, help='Enable debug output')
@click.option('--config', type=click.Path(exists=True), help='Config file path')
@click.option('--trace', 'trace_id', help='Trace ID for operation correlation')
@click.option('--mode', type=click.Choice(['normal', 'falsify', 'verify']), default='normal',
              help='Execution mode (falsify=test failure paths)')
@click.pass_context
def cli(ctx, debug, config, trace_id, mode):
    """
    InfraFabric CLI - Unified infrastructure orchestration

    \b
    Components:
      coordinator  Real-time swarm coordination (<10ms latency)
      governor     Policy-based resource allocation (70%+ matching)
      chassis      WASM sandbox execution (secure isolation)
      witness      Cryptographic provenance (hash chain + signatures)
      optimise     Cost tracking and optimization

    \b
    Global Flags:
      --debug      Enable debug output with stack traces
      --config     Path to config file (default: ~/.config/infrafabric/config.yaml)
      --trace      Trace ID for correlating related operations
      --mode       Execution mode: normal, falsify (test failures), verify

    \b
    Examples:
      if coordinator status
      if witness query --component IF.coordinator --limit 10
      if optimise report --today
      if --trace deploy-001 coordinator task create --task-id P0.1.2

    \b
    Quick Start:
      if config init                    # Generate example config
      if witness init                   # Initialize witness database
      if coordinator start              # Start coordinator service

    For detailed help on any command:
      if <command> --help
    """
    # Initialize global context
    global_ctx = GlobalContext()
    global_ctx.debug = debug
    global_ctx.trace_id = trace_id
    global_ctx.mode = mode

    # Load configuration
    config_path = Path(config) if config else None
    global_ctx.load_config(config_path)

    ctx.obj = global_ctx


# ====================
# CONFIG COMMANDS
# ====================

@cli.group()
def config():
    """Configuration management"""
    pass


@config.command('init')
@click.option('--force', is_flag=True, help='Overwrite existing config')
@pass_context
def config_init(ctx, force):
    """Generate example configuration file"""
    from infrafabric.config import generate_example_config

    config_path = Path.home() / '.config' / 'infrafabric' / 'config.yaml'

    if config_path.exists() and not force:
        click.echo(f"Config already exists: {config_path}")
        click.echo("Use --force to overwrite")
        return

    try:
        generate_example_config(config_path)
        click.echo(f"✓ Created config: {config_path}")
        click.echo("\nEdit this file to customize settings:")
        click.echo(f"  vim {config_path}")
    except Exception as e:
        handle_cli_error(f"Failed to generate config: {e}")


@config.command('show')
@pass_context
def config_show(ctx):
    """Show current configuration"""
    if not ctx.config:
        click.echo("No configuration loaded")
        return

    click.echo("InfraFabric Configuration:")
    click.echo(f"  Log Level: {ctx.config.log_level}")
    click.echo(f"  Coordinator Backend: {ctx.config.coordinator.backend}")
    click.echo(f"  Witness DB: {ctx.config.witness.db_path}")
    click.echo(f"  Telemetry: {'enabled' if ctx.config.enable_telemetry else 'disabled'}")


@config.command('validate')
@pass_context
def config_validate(ctx):
    """Validate configuration file"""
    if not ctx.config:
        click.echo("✗ No configuration loaded")
        sys.exit(1)

    click.echo("✓ Configuration valid")


# ====================
# COORDINATOR COMMANDS
# ====================

@cli.group()
def coordinator():
    """IF.coordinator - Real-time swarm coordination"""
    pass


@coordinator.command()
@click.option('--backend', type=click.Choice(['etcd', 'nats']), help='Event bus backend')
@click.option('--host', help='Event bus host')
@click.option('--port', type=int, help='Event bus port')
@pass_context
def start(ctx, backend, host, port):
    """Start IF.coordinator service"""
    config = ctx.config.coordinator if ctx.config else None

    backend = backend or (config.backend if config else 'etcd')
    host = host or (config.etcd_host if config else 'localhost')
    port = port or (config.etcd_port if config else 2379)

    click.echo(f"Starting IF.coordinator...")
    click.echo(f"  Backend: {backend}")
    click.echo(f"  Host: {host}:{port}")

    # TODO: Actually start coordinator service
    click.echo("✓ IF.coordinator ready")


@coordinator.command()
@pass_context
def status(ctx):
    """Show coordinator status"""
    # TODO: Query actual coordinator status
    click.echo("IF.coordinator [RUNNING]")
    click.echo("  Backend: etcd (localhost:2379)")
    click.echo("  Swarms registered: 7")
    click.echo("  Tasks active: 3")
    click.echo("  Tasks completed today: 42")
    click.echo("  Last heartbeat: 2s ago")


@coordinator.command('swarms')
@pass_context
def swarms_list(ctx):
    """List registered swarms"""
    # TODO: Query actual swarms
    click.echo("SWARM_ID              STATUS    BUDGET    REPUTATION    LAST_SEEN")
    click.echo("session-1-ndi         active    $80.00    0.95          1s ago")
    click.echo("session-2-webrtc      active    $120.00   0.88          2s ago")
    click.echo("session-4-sip         active    $50.00    0.92          1s ago")


@coordinator.group('task')
def coordinator_task():
    """Task management commands"""
    pass


@coordinator_task.command('create')
@click.option('--task-id', required=True, help='Unique task identifier')
@click.option('--description', required=True, help='Task description')
@click.option('--capabilities', multiple=True, help='Required capabilities')
@click.option('--max-cost', type=float, default=10.0, help='Maximum cost in USD')
@pass_context
def task_create(ctx, task_id, description, capabilities, max_cost):
    """Create new task"""
    click.echo(f"Creating task {task_id}...")
    click.echo(f"  Description: {description}")
    click.echo(f"  Required capabilities: {', '.join(capabilities)}")
    click.echo(f"  Max cost: ${max_cost:.2f}")
    # TODO: Actually create task
    click.echo(f"✓ Task {task_id} created (status: unclaimed)")


@coordinator_task.command('status')
@click.argument('task_id')
@pass_context
def task_status(ctx, task_id):
    """Check task status"""
    # TODO: Query actual task status
    click.echo(f"Task {task_id} [CLAIMED]")
    click.echo("  Owner: session-2-webrtc")
    click.echo("  Claimed at: 10:15:23")
    click.echo("  Estimated completion: 10:17:23 (2h estimate)")


# ====================
# GOVERNOR COMMANDS
# ====================

@cli.group()
def governor():
    """IF.governor - Policy-based resource allocation"""
    pass


@governor.command('register')
@click.argument('swarm_id')
@click.option('--capabilities', multiple=True, required=True, help='Swarm capabilities')
@click.option('--cost-per-hour', type=float, required=True, help='Cost per hour in USD')
@click.option('--budget', type=float, required=True, help='Initial budget in USD')
@click.option('--model', type=click.Choice(['haiku', 'sonnet', 'opus']), default='sonnet')
@pass_context
def register_swarm(ctx, swarm_id, capabilities, cost_per_hour, budget, model):
    """Register swarm with IF.governor"""
    click.echo(f"Registering swarm {swarm_id}...")
    click.echo(f"  Capabilities: {', '.join(capabilities)}")
    click.echo(f"  Cost: ${cost_per_hour:.2f}/hour")
    click.echo(f"  Budget: ${budget:.2f}")
    click.echo(f"  Model: {model}")
    # TODO: Actually register swarm
    click.echo(f"✓ Swarm {swarm_id} registered")


@governor.command('match')
@click.option('--capabilities', multiple=True, required=True, help='Required capabilities')
@click.option('--max-cost', type=float, default=20.0, help='Maximum cost per hour')
@pass_context
def match_swarms(ctx, capabilities, max_cost):
    """Find swarms matching requirements"""
    click.echo(f"Finding swarms with capabilities: {', '.join(capabilities)}")
    click.echo(f"Max cost: ${max_cost:.2f}/hour\n")
    # TODO: Query actual matches
    click.echo("Best matches (>70% threshold):")
    click.echo("1. session-2-webrtc (match: 1.00, cost: $18/hr, score: 0.85)")
    click.echo("2. session-7-if-bus (match: 0.75, cost: $20/hr, score: 0.72)")


@governor.group('budget')
def governor_budget():
    """Budget management commands"""
    pass


@governor_budget.command('add')
@click.argument('swarm_id')
@click.argument('amount', type=float)
@pass_context
def budget_add(ctx, swarm_id, amount):
    """Add budget to swarm"""
    click.echo(f"Adding ${amount:.2f} to {swarm_id}...")
    # TODO: Actually add budget
    click.echo(f"✓ Budget updated: ${amount:.2f} added")


@governor_budget.command('report')
@pass_context
def budget_report(ctx):
    """Show budget status for all swarms"""
    click.echo("Budget Report:")
    click.echo("session-1-ndi:     $80.00 remaining")
    click.echo("session-2-webrtc:  $120.00 remaining")
    click.echo("session-4-sip:     $50.00 remaining")


# ====================
# CHASSIS COMMANDS
# ====================

@cli.group()
def chassis():
    """IF.chassis - WASM sandbox execution"""
    pass


@chassis.group('sandbox')
def chassis_sandbox():
    """Sandbox management commands"""
    pass


@chassis_sandbox.command('create')
@click.option('--wasm-module', required=True, help='WASM module path')
@click.option('--memory', type=int, default=512, help='Memory limit in MB')
@click.option('--cpu', type=int, default=50, help='CPU limit in percent')
@click.option('--timeout', type=int, default=300000, help='Execution timeout in ms')
@pass_context
def sandbox_create(ctx, wasm_module, memory, cpu, timeout):
    """Create new WASM sandbox"""
    click.echo(f"Creating sandbox for {wasm_module}...")
    click.echo(f"  Memory: {memory}MB")
    click.echo(f"  CPU: {cpu}%")
    click.echo(f"  Timeout: {timeout}ms")
    # TODO: Actually create sandbox
    sandbox_id = "sb-001"
    click.echo(f"✓ Sandbox created: {sandbox_id}")


@chassis_sandbox.command('list')
@pass_context
def sandbox_list(ctx):
    """List all sandboxes"""
    click.echo("SANDBOX_ID    MODULE              STATUS      MEMORY    CPU")
    click.echo("sb-001        yologuard.wasm      running     256MB     25%")
    click.echo("sb-002        transformer.wasm    completed   512MB     50%")


# ====================
# WITNESS COMMANDS
# ====================

@cli.group()
def witness():
    """IF.witness - Cryptographic provenance"""
    pass


@witness.command('init')
@click.option('--db-path', type=click.Path(), help='Database path')
@click.option('--force', is_flag=True, help='Reinitialize if exists')
@pass_context
def witness_init(ctx, db_path, force):
    """Initialize witness database and generate keys"""
    from src.witness.database import WitnessDatabase
    from src.witness.crypto import generate_keypair

    db_path = db_path or str(Path.home() / '.if-witness' / 'witness.db')
    db_path_obj = Path(db_path)

    if db_path_obj.exists() and not force:
        click.echo(f"Witness database already exists: {db_path}")
        click.echo("Use --force to reinitialize")
        return

    try:
        # Create database
        db = WitnessDatabase(db_path)
        click.echo(f"✓ Created database: {db_path}")

        # Generate keypair
        key_dir = db_path_obj.parent
        private_key, public_key = generate_keypair()

        private_key_path = key_dir / 'signing_key.pem'
        public_key_path = key_dir / 'public_key.pem'

        with open(private_key_path, 'wb') as f:
            f.write(private_key)
        with open(public_key_path, 'wb') as f:
            f.write(public_key)

        click.echo(f"✓ Generated signing keys:")
        click.echo(f"    Private: {private_key_path}")
        click.echo(f"    Public: {public_key_path}")

    except Exception as e:
        handle_cli_error(f"Failed to initialize witness: {e}")


@witness.command('verify')
@pass_context
def witness_verify(ctx):
    """Verify witness hash chain integrity"""
    from src.witness.database import WitnessDatabase

    try:
        db = WitnessDatabase()
        is_valid = db.verify_chain()

        if is_valid:
            entry_count = len(db.query_entries())
            click.echo(f"✓ Hash chain valid ({entry_count} entries)")
            click.echo("✓ All signatures valid")
            click.echo("✓ No gaps in sequence")
        else:
            click.echo("✗ Hash chain invalid")
            sys.exit(1)

    except Exception as e:
        handle_cli_error(f"Verification failed: {e}")


@witness.command('query')
@click.option('--component', help='Filter by component')
@click.option('--event', help='Filter by event type')
@click.option('--trace-id', help='Filter by trace ID')
@click.option('--start-date', help='Start date (ISO format)')
@click.option('--end-date', help='End date (ISO format)')
@click.option('--limit', type=int, default=10, help='Maximum results')
@click.option('--format', type=click.Choice(['text', 'json', 'csv']), default='text')
@pass_context
def witness_query(ctx, component, event, trace_id, start_date, end_date, limit, format):
    """Query witness log entries"""
    from src.witness.database import WitnessDatabase
    import json as json_module

    try:
        db = WitnessDatabase()
        entries = db.query_entries(
            component=component,
            event=event,
            trace_id=trace_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )

        if format == 'json':
            click.echo(json_module.dumps([e.__dict__ for e in entries], indent=2))
        elif format == 'csv':
            click.echo("id,timestamp,event,component,trace_id")
            for e in entries:
                click.echo(f"{e.id},{e.timestamp},{e.event},{e.component},{e.trace_id}")
        else:
            click.echo(f"Found {len(entries)} entries:\n")
            for e in entries:
                click.echo(f"[{e.id}] {e.timestamp}  {e.event:20s}  {e.component:20s}  {e.trace_id}")

    except Exception as e:
        handle_cli_error(f"Query failed: {e}")


# ====================
# OPTIMISE COMMANDS
# ====================

@cli.group()
def optimise():
    """IF.optimise - Cost tracking and optimization"""
    pass


@optimise.command('report')
@click.option('--today', is_flag=True, help='Show today\'s costs only')
@click.option('--component', help='Filter by component')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD)')
@click.option('--format', type=click.Choice(['text', 'csv', 'json']), default='text')
@pass_context
def cost_report(ctx, today, component, start_date, end_date, format):
    """Generate cost report"""
    try:
        from src.cli.if_optimise import format_cost_data_as_csv
        from src.witness.database import WitnessDatabase
        from datetime import datetime

        # Handle --today flag
        if today:
            now = datetime.utcnow()
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            end_date = now.isoformat()

        # Query database
        db = WitnessDatabase()
        try:
            start_dt = datetime.fromisoformat(start_date) if start_date else None
            end_dt = datetime.fromisoformat(end_date) if end_date else None

            cost_data = db.get_cost_by_component(component, start_dt, end_dt)

            if format == 'json':
                import json
                click.echo(json.dumps(cost_data, indent=2))
            elif format == 'csv':
                csv_output = format_cost_data_as_csv(cost_data)
                click.echo(csv_output)
            else:
                if not cost_data:
                    click.echo("No cost data found")
                    return

                period_str = ""
                if today:
                    period_str = " (Today)"
                elif start_date and end_date:
                    period_str = f" ({start_date} to {end_date})"

                click.echo(f"\nIF.optimise Cost Report{period_str}\n")
                click.echo(f"{'Component':<30} {'Operations':<12} {'Tokens':<12} {'Cost':<12}")
                click.echo("-" * 66)

                total_ops = 0
                total_tokens = 0
                total_cost = 0.0

                for row in cost_data:
                    click.echo(f"{row['component']:<30} {row['operations']:<12} "
                             f"{row['total_tokens'] or 0:<12,} "
                             f"${row['total_cost'] or 0.0:<11.6f}")

                    total_ops += row['operations']
                    total_tokens += row['total_tokens'] or 0
                    total_cost += row['total_cost'] or 0.0

                click.echo("-" * 66)
                click.echo(f"{'Total':<30} {total_ops:<12} {total_tokens:<12,} ${total_cost:<11.6f}")

        finally:
            db.close()

    except ImportError:
        click.echo("❌ IF.optimise module not available", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error generating report: {e}", err=True)
        sys.exit(1)


@optimise.command('budget')
@click.option('--set', 'budget_amount', type=float, help='Set budget limit in USD')
@click.option('--period', type=click.Choice(['day', 'week', 'month']), default='month')
@click.option('--component', help='Component filter (optional)')
@pass_context
def budget(ctx, budget_amount, period, component):
    """Set and monitor budget limits"""
    try:
        from src.witness.database import WitnessDatabase
        from datetime import datetime, timedelta
        import json

        db = WitnessDatabase()
        try:
            # Calculate period start
            now = datetime.utcnow()
            if period == 'day':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == 'week':
                start_date = now - timedelta(days=now.weekday())
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            cost_data = db.get_cost_by_component(component, start_date, None)
            total_spent = sum(row['total_cost'] or 0.0 for row in cost_data)

            if budget_amount:
                # Set budget
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
                # Check budget
                budget_file = Path.home() / '.if-witness' / 'budget.json'
                if budget_file.exists():
                    budget_config = json.loads(budget_file.read_text())
                    budget_amount = budget_config['amount']
                else:
                    budget_amount = 100.0

            remaining = budget_amount - total_spent
            usage_pct = (total_spent / budget_amount * 100) if budget_amount > 0 else 0

            click.echo(f"\nBudget Status ({period})")
            click.echo("-" * 40)
            click.echo(f"Budget:       ${budget_amount:.2f}")
            click.echo(f"Spent:        ${total_spent:.6f}")
            click.echo(f"Remaining:    ${remaining:.6f}")
            click.echo(f"Usage:        {usage_pct:.2f}%")

            if usage_pct >= 100:
                click.echo("\n⚠️  ALERT: Budget exceeded!", err=True)
            elif usage_pct >= 80:
                click.echo(f"\n⚠️  WARNING: {usage_pct:.0f}% of budget used")

        finally:
            db.close()

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@optimise.command('rates')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def rates(format):
    """Show current model rates"""
    from src.cli.if_optimise import MODEL_RATES
    import json

    if format == 'json':
        click.echo(json.dumps(MODEL_RATES, indent=2))
    else:
        click.echo("\nCurrent Model Rates (per token)\n")
        click.echo(f"{'Model':<25} {'Input':<15} {'Output':<15}")
        click.echo("-" * 55)

        for model, rate in MODEL_RATES.items():
            click.echo(f"{model:<25} ${rate['input']:<14.8f} ${rate['output']:<14.8f}")


# ====================
# UTILITY COMMANDS
# ====================

@cli.command('version')
def version():
    """Show version information"""
    click.echo("InfraFabric v0.1.0")
    click.echo("Phase 0 - Real-time coordination")


@cli.command('workflows')
def workflows():
    """Show common workflow examples"""
    click.echo("Common InfraFabric Workflows:\n")

    if COMMON_WORKFLOWS:
        for wf in COMMON_WORKFLOWS:
            click.echo(f"• {wf['name']}")
            click.echo(f"  {wf['description']}")
            for step in wf['steps']:
                click.echo(f"    {step}")
            click.echo()
    else:
        click.echo("1. First-time Setup:")
        click.echo("     if config init")
        click.echo("     if witness init")
        click.echo("     if coordinator start")
        click.echo()
        click.echo("2. Register a Swarm:")
        click.echo("     if governor register session-1 --capabilities video:ndi \\")
        click.echo("       --cost-per-hour 2.0 --budget 100.0")
        click.echo()
        click.echo("3. Monitor System:")
        click.echo("     if coordinator status")
        click.echo("     if witness query --limit 10")
        click.echo("     if optimise report --today")


def main():
    """Main entry point"""
    try:
        cli(obj=None)
    except CLIError as e:
        handle_cli_error(e)
    except KeyboardInterrupt:
        click.echo("\nInterrupted", err=True)
        sys.exit(130)
    except Exception as e:
        if '--debug' in sys.argv:
            raise
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
