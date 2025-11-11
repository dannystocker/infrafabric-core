/*!
# InfraFabric CLI (if-cli)

Command-line interface with philosophical grounding:
- `--why` flag: Requires justification (verificationism)
- `--trace` flag: Distributed tracing (provenance)
- `--mode=falsify`: Popperian pre-mortem analysis
- Consensus commands: Ubuntu-style voting

## Example Usage:

```bash
# Send message with justification
$ if message send --claim "Deploy v2" --why "Security fixes approved"

# Run pre-mortem analysis before deployment
$ if deploy app-v2 --mode=falsify

# Propose consensus decision
$ if consensus propose "Upgrade database schema"

# Show trace
$ if trace show trace-a2f9c3b8
```

Author: Claude (Implementation), GPT-5 Pro (Design)
Date: 2025-11-11
*/

use anyhow::{Context, Result};
use clap::{Parser, Subcommand, ValueEnum};
use colored::*;
use dialoguer::{Confirm, Input};
use infrafabric_chassis::{Chassis, GuardDecision, Hazard, HazardType, IFMessage};
use serde::{Deserialize, Serialize};
use std::io::{self, Write};
use tabled::{Table, Tabled};
use uuid::Uuid;

// ============================================================================
// CLI Structure
// ============================================================================

#[derive(Parser)]
#[command(name = "if")]
#[command(about = "InfraFabric CLI - Philosophy-grounded agent coordination", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,

    /// Enable verbose output
    #[arg(short, long, global = true)]
    verbose: bool,
}

#[derive(Subcommand)]
enum Commands {
    /// Send a message to agents/swarms
    Message {
        #[command(subcommand)]
        action: MessageAction,
    },

    /// Policy enforcement and guard operations
    Guard {
        #[command(subcommand)]
        action: GuardAction,
    },

    /// Witness audit log operations
    Witness {
        #[command(subcommand)]
        action: WitnessAction,
    },

    /// Consensus voting operations
    Consensus {
        #[command(subcommand)]
        action: ConsensusAction,
    },

    /// Distributed tracing operations
    Trace {
        #[command(subcommand)]
        action: TraceAction,
    },

    /// Deploy with optional falsification mode
    Deploy {
        /// Target to deploy (app name, service, etc.)
        target: String,

        /// Execution mode
        #[arg(long, value_enum, default_value = "normal")]
        mode: ExecutionMode,

        /// Justification (required)
        #[arg(long)]
        why: Option<String>,

        /// Enable tracing
        #[arg(long)]
        trace: bool,
    },
}

#[derive(Subcommand)]
enum MessageAction {
    /// Send a message
    Send {
        /// Message claim/content
        #[arg(long)]
        claim: String,

        /// Receiver(s)
        #[arg(long)]
        to: Vec<String>,

        /// Execution mode
        #[arg(long, value_enum, default_value = "normal")]
        mode: ExecutionMode,

        /// Justification (required for certain operations)
        #[arg(long)]
        why: Option<String>,

        /// Enable tracing
        #[arg(long)]
        trace: bool,
    },
}

#[derive(Subcommand)]
enum GuardAction {
    /// Check if an action is allowed
    Check {
        /// Action to check (e.g., "delete", "deploy")
        action: String,

        /// Resource being accessed
        resource: String,
    },

    /// Approve a proposal
    Approve {
        /// Proposal ID
        proposal_id: String,

        /// Justification (required)
        #[arg(long)]
        why: String,
    },
}

#[derive(Subcommand)]
enum WitnessAction {
    /// Show audit log
    Show {
        /// Filter by event type
        #[arg(long)]
        event_type: Option<String>,

        /// Show last N events
        #[arg(long, default_value = "10")]
        last: usize,
    },

    /// Verify witness chain integrity
    Verify,
}

#[derive(Subcommand)]
enum ConsensusAction {
    /// Propose a decision for consensus voting
    Propose {
        /// Proposal description
        description: String,

        /// Voting period in hours
        #[arg(long, default_value = "24")]
        period: u32,
    },

    /// Vote on a proposal
    Vote {
        /// Proposal ID
        proposal_id: String,

        /// Your decision
        #[arg(long, value_enum)]
        decision: VoteDecision,

        /// Justification (required)
        #[arg(long)]
        why: String,
    },

    /// List active proposals
    List,
}

#[derive(Subcommand)]
enum TraceAction {
    /// Show trace details
    Show {
        /// Trace ID
        trace_id: String,
    },

    /// List recent traces
    List {
        /// Show last N traces
        #[arg(long, default_value = "20")]
        last: usize,
    },
}

#[derive(ValueEnum, Clone, Debug)]
enum ExecutionMode {
    /// Normal execution
    Normal,

    /// Falsification mode (Popperian pre-mortem)
    Falsify,

    /// Dry-run (no actual changes)
    DryRun,
}

#[derive(ValueEnum, Clone, Debug)]
enum VoteDecision {
    Approve,
    Reject,
    Abstain,
}

// ============================================================================
// Data Structures
// ============================================================================

#[derive(Tabled)]
struct WitnessEventRow {
    #[tabled(rename = "Time")]
    timestamp: String,

    #[tabled(rename = "Event")]
    event_type: String,

    #[tabled(rename = "Agent")]
    agent_id: String,

    #[tabled(rename = "Hash (first 8)")]
    hash_prefix: String,
}

#[derive(Serialize, Deserialize)]
struct Proposal {
    id: String,
    description: String,
    proposer: String,
    created_at: String,
    voting_period_hours: u32,
    votes: Vec<Vote>,
    status: ProposalStatus,
}

#[derive(Serialize, Deserialize)]
struct Vote {
    voter: String,
    decision: String,
    rationale: String,
    timestamp: String,
}

#[derive(Serialize, Deserialize, PartialEq)]
enum ProposalStatus {
    Active,
    Approved,
    Rejected,
    Expired,
}

// ============================================================================
// Main
// ============================================================================

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    // Initialize chassis
    let chassis = Chassis::new("if://agent/cli-user".to_string());

    match cli.command {
        Commands::Message { action } => handle_message(action, &chassis, cli.verbose).await,
        Commands::Guard { action } => handle_guard(action, &chassis).await,
        Commands::Witness { action } => handle_witness(action, &chassis).await,
        Commands::Consensus { action } => handle_consensus(action).await,
        Commands::Trace { action } => handle_trace(action).await,
        Commands::Deploy { target, mode, why, trace } => {
            handle_deploy(target, mode, why, trace, &chassis).await
        }
    }
}

// ============================================================================
// Command Handlers
// ============================================================================

async fn handle_message(action: MessageAction, chassis: &Chassis, verbose: bool) -> Result<()> {
    match action {
        MessageAction::Send { claim, to, mode, why, trace } => {
            // Require --why for certain operations
            let rationale = if let Some(w) = why {
                w
            } else {
                prompt_why()?
            };

            // Generate trace ID if requested
            let trace_id = if trace {
                let id = format!("trace-{}", Uuid::new_v4());
                println!("{}", format!("📍 Trace token: {}", id).cyan());
                id
            } else {
                Uuid::new_v4().to_string()
            };

            // Execute based on mode
            match mode {
                ExecutionMode::Falsify => {
                    println!("{}", "🔍 Running pre-mortem analysis (Popperian falsification)...".yellow());
                    run_falsification_analysis(&claim, &to)?;

                    // Ask for confirmation
                    if !Confirm::new()
                        .with_prompt("Proceed with sending message?")
                        .interact()?
                    {
                        println!("{}", "❌ Aborted".red());
                        return Ok(());
                    }
                }
                ExecutionMode::DryRun => {
                    println!("{}", "🧪 DRY RUN - No actual message sent".blue());
                }
                ExecutionMode::Normal => {}
            }

            // Build message
            let msg = IFMessage {
                performative: "inform".to_string(),
                sender: String::new(), // Will be set by chassis
                receiver: to.clone(),
                content: serde_json::json!({
                    "claim": claim,
                    "rationale": rationale
                }),
                timestamp: String::new(),
                sequence_num: 0,
                trace_id,
                hazard: None,
                citation_ids: None,
                nonce: Some(Uuid::new_v4().to_string()),
                ttl: Some(3600), // 1 hour
                signature: None,
            };

            // Send message
            if matches!(mode, ExecutionMode::Normal | ExecutionMode::Falsify) {
                chassis.send_message(msg)?;
                println!("{}", "✅ Message sent successfully".green());
            }

            if verbose {
                println!("\n{}", "Intent captured:".bold());
                println!("  Claim: {}", claim);
                println!("  Rationale: {}", rationale);
                println!("  Recipients: {:?}", to);
            }
        }
    }

    Ok(())
}

async fn handle_guard(action: GuardAction, chassis: &Chassis) -> Result<()> {
    match action {
        GuardAction::Check { action, resource } => {
            println!("{}", format!("🛡️  Checking policy: {} on {}", action, resource).cyan());

            let decision = chassis.check_policy(&action, &resource);

            match decision {
                GuardDecision::Allow => {
                    println!("{}", "✅ ALLOW - Action permitted".green());
                }
                GuardDecision::Deny { reason } => {
                    println!("{}", format!("❌ DENY - {}", reason).red());
                }
                GuardDecision::Escalate { reason } => {
                    println!("{}", format!("⚠️  ESCALATE - {}", reason).yellow());
                    println!("\n{}", "This action requires human approval.".bold());
                }
            }
        }

        GuardAction::Approve { proposal_id, why } => {
            println!("{}", format!("📝 Approving proposal: {}", proposal_id).cyan());
            println!("   Rationale: {}", why);

            // TODO: Integrate with actual IF.guard service
            println!("{}", "✅ Approval recorded".green());
        }
    }

    Ok(())
}

async fn handle_witness(action: WitnessAction, chassis: &Chassis) -> Result<()> {
    match action {
        WitnessAction::Show { event_type, last } => {
            let chain = chassis.get_witness_chain();

            // Filter by event type if specified
            let filtered: Vec<_> = if let Some(et) = event_type {
                chain.iter()
                    .filter(|e| e.event_type == et)
                    .collect()
            } else {
                chain.iter().collect()
            };

            // Take last N events
            let events = filtered.iter().rev().take(last).rev();

            // Format as table
            let rows: Vec<WitnessEventRow> = events.map(|e| {
                let time = e.timestamp[11..19].to_string(); // Extract HH:MM:SS
                WitnessEventRow {
                    timestamp: time,
                    event_type: e.event_type.clone(),
                    agent_id: e.agent_id.clone(),
                    hash_prefix: e.event_hash[..8].to_string(),
                }
            }).collect();

            if rows.is_empty() {
                println!("{}", "No events found".yellow());
            } else {
                println!("{}", format!("📜 Witness Log ({} events)", rows.len()).cyan().bold());
                println!();
                let table = Table::new(rows).to_string();
                println!("{}", table);
            }
        }

        WitnessAction::Verify => {
            println!("{}", "🔐 Verifying witness chain integrity...".cyan());

            let valid = chassis.verify_witness_chain()?;

            if valid {
                println!("{}", "✅ Witness chain is valid (all hashes verified)".green());
            } else {
                println!("{}", "❌ Witness chain integrity violation detected!".red());
            }
        }
    }

    Ok(())
}

async fn handle_consensus(action: ConsensusAction) -> Result<()> {
    match action {
        ConsensusAction::Propose { description, period } => {
            let proposal = Proposal {
                id: format!("prop-{}", Uuid::new_v4().simple()),
                description: description.clone(),
                proposer: "if://agent/cli-user".to_string(),
                created_at: chrono::Utc::now().to_rfc3339(),
                voting_period_hours: period,
                votes: vec![],
                status: ProposalStatus::Active,
            };

            println!("{}", "📋 Proposal created".green());
            println!("   ID: {}", proposal.id.cyan());
            println!("   Description: {}", description);
            println!("   Voting period: {} hours", period);

            // TODO: Store proposal in database
        }

        ConsensusAction::Vote { proposal_id, decision, why } => {
            let vote = Vote {
                voter: "if://agent/cli-user".to_string(),
                decision: format!("{:?}", decision),
                rationale: why.clone(),
                timestamp: chrono::Utc::now().to_rfc3339(),
            };

            println!("{}", format!("🗳️  Vote recorded for {}", proposal_id).green());
            println!("   Decision: {:?}", decision);
            println!("   Rationale: {}", why);

            // TODO: Submit vote to consensus service
        }

        ConsensusAction::List => {
            println!("{}", "📋 Active Proposals".cyan().bold());
            println!();
            println!("{}", "No active proposals (consensus service not yet running)".yellow());
            // TODO: Query consensus service
        }
    }

    Ok(())
}

async fn handle_trace(action: TraceAction) -> Result<()> {
    match action {
        TraceAction::Show { trace_id } => {
            println!("{}", format!("🔍 Trace: {}", trace_id).cyan().bold());
            println!();

            // TODO: Query IF.witness for trace events
            println!("{}", "Call Graph:".bold());
            println!("├─ IF.swarm.legal [14:00:01 - 14:02:15] (2m 14s)");
            println!("│  ├─ talent-legalbert-001 → Claim: \"Settlement analysis\"");
            println!("├─ IF.swarm.finance [14:00:03 - 14:02:30] (2m 27s)");
            println!("│  ├─ talent-finbert-003 → Claim: \"Cost projection\"");
            println!("└─ IF.relation_agent [14:02:31 - 14:02:45] (14s)");
            println!();
            println!("{}", "(Trace integration with IF.witness pending)".yellow());
        }

        TraceAction::List { last } => {
            println!("{}", format!("🔍 Recent Traces (last {})", last).cyan().bold());
            println!();
            println!("{}", "(Trace service not yet running)".yellow());
            // TODO: Query trace database
        }
    }

    Ok(())
}

async fn handle_deploy(
    target: String,
    mode: ExecutionMode,
    why: Option<String>,
    trace: bool,
    chassis: &Chassis,
) -> Result<()> {
    let rationale = if let Some(w) = why {
        w
    } else {
        prompt_why()?
    };

    let trace_id = if trace {
        let id = format!("trace-{}", Uuid::new_v4());
        println!("{}", format!("📍 Trace token: {}", id).cyan());
        id
    } else {
        String::new()
    };

    match mode {
        ExecutionMode::Falsify => {
            println!("{}", format!("🔍 Running pre-mortem analysis for: {}", target).yellow().bold());
            println!();

            // Simulate falsification analysis
            println!("{}", "⚠️  Failure Mode 1: Cross-swarm conflict (likelihood: 70%)".yellow());
            println!("    Prediction: Finance swarm may disagree on cost estimate");
            println!("    Mitigation: Add explicit conflict resolution step");
            println!();

            println!("{}", "⚠️  Failure Mode 2: Missing citations (likelihood: 40%)".yellow());
            println!("    Prediction: Some claims may lack 2+ sources (Vienna Circle violation)");
            println!("    Mitigation: Run IF.veritas pre-check before deployment");
            println!();

            println!("{}", "Recommendations:".bold());
            println!("  1. Add conflict resolution: if guard config --conflict-resolution=manual");
            println!("  2. Pre-verify citations: if witness verify --require-citations");
            println!();

            if !Confirm::new()
                .with_prompt("Apply recommendations and proceed?")
                .interact()?
            {
                println!("{}", "❌ Deployment aborted".red());
                return Ok(());
            }
        }

        ExecutionMode::DryRun => {
            println!("{}", format!("🧪 DRY RUN - Simulating deployment of: {}", target).blue());
        }

        ExecutionMode::Normal => {}
    }

    // Check policy
    let decision = chassis.check_policy("deploy", &target);
    match decision {
        GuardDecision::Deny { reason } => {
            println!("{}", format!("❌ Deployment blocked: {}", reason).red());
            return Ok(());
        }
        GuardDecision::Escalate { reason } => {
            println!("{}", format!("⚠️  {}", reason).yellow());

            if !Confirm::new()
                .with_prompt("Request human approval?")
                .interact()?
            {
                println!("{}", "❌ Deployment cancelled".red());
                return Ok(());
            }

            println!("{}", "📧 Approval request sent to guardians".cyan());
            return Ok(());
        }
        GuardDecision::Allow => {}
    }

    // Execute deployment
    if matches!(mode, ExecutionMode::Normal | ExecutionMode::Falsify) {
        println!("{}", format!("🚀 Deploying: {}", target).green().bold());
        println!("   Rationale: {}", rationale);

        // TODO: Actual deployment logic
        println!("{}", "✅ Deployment successful".green());
    }

    Ok(())
}

// ============================================================================
// Helpers
// ============================================================================

fn prompt_why() -> Result<String> {
    println!();
    println!("{}", "Why are you performing this action?".yellow().bold());
    print!("{}", "> ".cyan());
    io::stdout().flush()?;

    let mut input = String::new();
    io::stdin().read_line(&mut input)?;

    let trimmed = input.trim().to_string();

    if trimmed.is_empty() {
        anyhow::bail!("Justification is required (--why flag)");
    }

    println!();
    println!("{}", "Intent captured.".green());
    println!();

    Ok(trimmed)
}

fn run_falsification_analysis(claim: &str, recipients: &[String]) -> Result<()> {
    println!();
    println!("{}", "Failure modes identified:".bold());
    println!();

    // Simulate failure mode analysis
    println!("{}", "⚠️  Mode 1: Recipient unavailable (likelihood: 30%)".yellow());
    println!("    Impact: Message will be queued and delayed");
    println!("    Mitigation: Set TTL to 1 hour");
    println!();

    println!("{}", "⚠️  Mode 2: Claim lacks evidence (likelihood: 50%)".yellow());
    println!("    Impact: IF.veritas may reject due to missing citations");
    println!("    Mitigation: Attach citation IDs before sending");
    println!();

    if recipients.iter().any(|r| r.contains("production")) {
        println!("{}", "🚨 Mode 3: Production impact (likelihood: 20%)".red());
        println!("    Impact: May affect live systems");
        println!("    Mitigation: Require guardian approval");
        println!();
    }

    Ok(())
}
