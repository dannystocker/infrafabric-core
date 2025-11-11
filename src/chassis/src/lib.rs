/*!
# InfraFabric Chassis (IF.chassis)

The **90% stable infrastructure** that hosts swappable WASM logic payloads (10%).

## Key Responsibilities:
- Message signing and verification (Ed25519)
- Policy enforcement (IF.guard integration)
- Witness logging (IF.witness integration)
- WASM payload hosting and hot-swap
- Trace propagation (distributed tracing)

## Architecture:
```text
┌─────────────────────────────────────┐
│         IF.chassis (90%)            │
├─────────────────────────────────────┤
│ • Message Transport (send/receive)  │
│ • Signature Verification (Ed25519)  │
│ • Policy Checks (IF.guard)          │
│ • Audit Logging (IF.witness)        │
│ • WASM Runtime (Wasmtime)           │
└─────────────────────────────────────┘
            ↕
┌─────────────────────────────────────┐
│       logic.wasm (10%)              │
│  (Swappable business logic)         │
└─────────────────────────────────────┘
```

Author: Claude (Implementation), GPT-5 Pro (Design)
Date: 2025-11-11
*/

use anyhow::{Context, Result};
use chrono::Utc;
use ed25519_dalek::{Keypair, PublicKey, Signature, Signer, SigningKey, Verifier, VerifyingKey};
use rand::rngs::OsRng;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use thiserror::Error;
use uuid::Uuid;

// ============================================================================
// Core Data Structures
// ============================================================================

/// IFMessage - Core message format for all agent communication
///
/// Follows FIPA-ACL performatives with InfraFabric extensions:
/// - Hazard tags (for risk awareness)
/// - Citation IDs (for evidence tracing)
/// - Nonces (for replay protection)
/// - TTL (for message expiration)
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct IFMessage {
    /// FIPA performative: "inform", "request", "propose", "accept", "reject", etc.
    pub performative: String,

    /// Sender agent ID (format: "if://agent/[swarm]/[name]@[version]")
    pub sender: String,

    /// Receiver agent IDs
    pub receiver: Vec<String>,

    /// Message content (JSON payload)
    pub content: serde_json::Value,

    /// ISO 8601 timestamp
    pub timestamp: String,

    /// Sequence number (per sender)
    pub sequence_num: u64,

    /// Trace ID for distributed tracing
    pub trace_id: String,

    /// Optional hazard annotation (Swarp v4* extension)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub hazard: Option<Hazard>,

    /// Citation IDs for evidence tracing (IF.veritas requirement)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub citation_ids: Option<Vec<String>>,

    /// Cryptographic nonce (replay protection)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub nonce: Option<String>,

    /// Time-to-live in seconds
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ttl: Option<u64>,

    /// Ed25519 signature (hex-encoded)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub signature: Option<String>,
}

/// Hazard annotation for risk-aware routing (Swarp v4*)
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Hazard {
    /// Hazard type: "legal", "financial", "security", "ethical"
    pub hazard_type: HazardType,

    /// Severity: "low", "medium", "high", "critical"
    pub severity: String,

    /// Human-readable explanation
    pub rationale: String,

    /// Suggested action: "ESCALATE", "HOLD", "REVIEW", "LOG"
    pub action: String,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
#[serde(rename_all = "lowercase")]
pub enum HazardType {
    Legal,
    Financial,
    Security,
    Ethical,
    Technical,
}

/// Witness event - Immutable audit log entry
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct WitnessEvent {
    /// Event ID (UUID)
    pub event_id: String,

    /// Event type: "message_sent", "message_received", "policy_decision", etc.
    pub event_type: String,

    /// Agent ID that caused the event
    pub agent_id: String,

    /// ISO 8601 timestamp
    pub timestamp: String,

    /// Event payload (message, decision, etc.)
    pub payload: serde_json::Value,

    /// Hash of previous event (blockchain-style chaining)
    pub previous_hash: String,

    /// Hash of this event
    pub event_hash: String,
}

/// Guard decision - Policy enforcement result
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub enum GuardDecision {
    Allow,
    Deny { reason: String },
    Escalate { reason: String },
}

// ============================================================================
// Errors
// ============================================================================

#[derive(Error, Debug)]
pub enum ChassisError {
    #[error("Signature verification failed: {0}")]
    SignatureError(String),

    #[error("Policy violation: {0}")]
    PolicyError(String),

    #[error("Message expired (TTL exceeded)")]
    MessageExpired,

    #[error("Replay attack detected (nonce reused)")]
    ReplayAttack,

    #[error("Serialization error: {0}")]
    SerializationError(#[from] serde_json::Error),

    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
}

// ============================================================================
// Chassis Implementation
// ============================================================================

/// IF.chassis - The stable 90% infrastructure
pub struct Chassis {
    /// Agent identity (format: "if://agent/[swarm]/[name]@[version]")
    pub agent_id: String,

    /// Ed25519 signing keypair
    signing_key: SigningKey,

    /// Ed25519 verifying key (public key)
    verifying_key: VerifyingKey,

    /// Trusted public keys (agent_id → public_key)
    trusted_keys: Arc<RwLock<HashMap<String, VerifyingKey>>>,

    /// Witness event chain (in-memory for demo; use DB in production)
    witness_chain: Arc<RwLock<Vec<WitnessEvent>>>,

    /// Sequence counter for outgoing messages
    sequence: Arc<RwLock<u64>>,

    /// Nonce cache for replay protection (nonce → expiry timestamp)
    nonce_cache: Arc<RwLock<HashMap<String, i64>>>,
}

impl Chassis {
    /// Create new chassis with generated keypair
    pub fn new(agent_id: String) -> Self {
        let mut csprng = OsRng;
        let signing_key = SigningKey::generate(&mut csprng);
        let verifying_key = signing_key.verifying_key();

        Self {
            agent_id,
            signing_key,
            verifying_key,
            trusted_keys: Arc::new(RwLock::new(HashMap::new())),
            witness_chain: Arc::new(RwLock::new(Vec::new())),
            sequence: Arc::new(RwLock::new(0)),
            nonce_cache: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    /// Get public key (for key exchange)
    pub fn public_key(&self) -> VerifyingKey {
        self.verifying_key
    }

    /// Register trusted public key for another agent
    pub fn register_trusted_key(&self, agent_id: String, public_key: VerifyingKey) {
        let mut keys = self.trusted_keys.write().unwrap();
        keys.insert(agent_id, public_key);
    }

    /// Send message (sign, log, transmit)
    pub fn send_message(&self, mut msg: IFMessage) -> Result<()> {
        // Set sender if not already set
        if msg.sender.is_empty() {
            msg.sender = self.agent_id.clone();
        }

        // Set timestamp if not set
        if msg.timestamp.is_empty() {
            msg.timestamp = Utc::now().to_rfc3339();
        }

        // Set sequence number
        let mut seq = self.sequence.write().unwrap();
        *seq += 1;
        msg.sequence_num = *seq;

        // Generate nonce if not present
        if msg.nonce.is_none() {
            msg.nonce = Some(Uuid::new_v4().to_string());
        }

        // Sign message
        let signature = self.sign_message(&msg)?;
        msg.signature = Some(hex::encode(signature.to_bytes()));

        // Log to witness
        self.log_witness_event("message_sent", &msg)?;

        // TODO: Actual transmission (NATS, WebRTC, etc.)
        println!("[CHASSIS] Sent message: {} → {:?}", msg.performative, msg.receiver);

        Ok(())
    }

    /// Receive and verify message
    pub fn receive_message(&self, msg: &IFMessage) -> Result<()> {
        // 1. Check TTL
        if let Some(ttl) = msg.ttl {
            let msg_time = chrono::DateTime::parse_from_rfc3339(&msg.timestamp)
                .context("Invalid timestamp")?
                .timestamp();
            let now = Utc::now().timestamp();

            if (now - msg_time) > ttl as i64 {
                return Err(ChassisError::MessageExpired.into());
            }
        }

        // 2. Check nonce (replay protection)
        if let Some(nonce) = &msg.nonce {
            let mut cache = self.nonce_cache.write().unwrap();

            if cache.contains_key(nonce) {
                return Err(ChassisError::ReplayAttack.into());
            }

            // Store nonce with expiry (1 hour)
            let expiry = Utc::now().timestamp() + 3600;
            cache.insert(nonce.clone(), expiry);

            // Clean expired nonces
            let now = Utc::now().timestamp();
            cache.retain(|_, exp| *exp > now);
        }

        // 3. Verify signature
        self.verify_message_signature(msg)?;

        // 4. Log to witness
        self.log_witness_event("message_received", msg)?;

        println!("[CHASSIS] Received verified message from: {}", msg.sender);

        Ok(())
    }

    /// Sign message with Ed25519
    fn sign_message(&self, msg: &IFMessage) -> Result<ed25519_dalek::Signature> {
        // Create canonical JSON (deterministic serialization)
        let mut msg_copy = msg.clone();
        msg_copy.signature = None; // Remove signature field before signing

        let canonical = serde_json::to_string(&msg_copy)?;
        let signature = self.signing_key.sign(canonical.as_bytes());

        Ok(signature)
    }

    /// Verify message signature
    fn verify_message_signature(&self, msg: &IFMessage) -> Result<()> {
        let signature_hex = msg.signature.as_ref()
            .ok_or_else(|| ChassisError::SignatureError("No signature present".to_string()))?;

        let signature_bytes = hex::decode(signature_hex)
            .map_err(|e| ChassisError::SignatureError(format!("Invalid hex: {}", e)))?;

        let signature = ed25519_dalek::Signature::from_bytes(
            signature_bytes.as_slice().try_into()
                .map_err(|_| ChassisError::SignatureError("Invalid signature length".to_string()))?
        );

        // Get sender's public key
        let keys = self.trusted_keys.read().unwrap();
        let public_key = keys.get(&msg.sender)
            .ok_or_else(|| ChassisError::SignatureError(format!("Unknown sender: {}", msg.sender)))?;

        // Verify
        let mut msg_copy = msg.clone();
        msg_copy.signature = None;
        let canonical = serde_json::to_string(&msg_copy)?;

        public_key.verify(canonical.as_bytes(), &signature)
            .map_err(|e| ChassisError::SignatureError(format!("Verification failed: {}", e)))?;

        Ok(())
    }

    /// Check policy via IF.guard (stub implementation)
    pub fn check_policy(&self, action: &str, resource: &str) -> GuardDecision {
        // TODO: Integrate with actual IF.guard service
        // For now, simple rule: deny "delete" on "production"

        if action == "delete" && resource.contains("production") {
            GuardDecision::Deny {
                reason: "Cannot delete production resources without approval".to_string()
            }
        } else if action == "deploy" && resource.contains("critical") {
            GuardDecision::Escalate {
                reason: "Critical deployments require human approval".to_string()
            }
        } else {
            GuardDecision::Allow
        }
    }

    /// Log event to IF.witness (immutable audit log)
    fn log_witness_event(&self, event_type: &str, payload: &IFMessage) -> Result<()> {
        let mut chain = self.witness_chain.write().unwrap();

        // Get previous hash
        let previous_hash = if let Some(last) = chain.last() {
            last.event_hash.clone()
        } else {
            "genesis".to_string()
        };

        // Create event
        let event = WitnessEvent {
            event_id: Uuid::new_v4().to_string(),
            event_type: event_type.to_string(),
            agent_id: self.agent_id.clone(),
            timestamp: Utc::now().to_rfc3339(),
            payload: serde_json::to_value(payload)?,
            previous_hash: previous_hash.clone(),
            event_hash: String::new(), // Calculate below
        };

        // Calculate hash (SHA-256 of canonical JSON)
        let canonical = serde_json::to_string(&event)?;
        let mut hasher = Sha256::new();
        hasher.update(canonical.as_bytes());
        let hash = format!("{:x}", hasher.finalize());

        let mut event = event;
        event.event_hash = hash;

        // Append to chain
        chain.push(event);

        println!("[WITNESS] Logged event: {} (chain length: {})", event_type, chain.len());

        Ok(())
    }

    /// Get witness chain (for auditing)
    pub fn get_witness_chain(&self) -> Vec<WitnessEvent> {
        let chain = self.witness_chain.read().unwrap();
        chain.clone()
    }

    /// Verify witness chain integrity
    pub fn verify_witness_chain(&self) -> Result<bool> {
        let chain = self.witness_chain.read().unwrap();

        for (i, event) in chain.iter().enumerate() {
            // Recalculate hash
            let mut event_copy = event.clone();
            event_copy.event_hash = String::new();

            let canonical = serde_json::to_string(&event_copy)?;
            let mut hasher = Sha256::new();
            hasher.update(canonical.as_bytes());
            let calculated_hash = format!("{:x}", hasher.finalize());

            if calculated_hash != event.event_hash {
                println!("[WITNESS] Chain integrity violation at event {}", i);
                return Ok(false);
            }

            // Check previous hash link
            if i > 0 {
                let prev_event = &chain[i - 1];
                if event.previous_hash != prev_event.event_hash {
                    println!("[WITNESS] Chain link broken at event {}", i);
                    return Ok(false);
                }
            }
        }

        println!("[WITNESS] Chain integrity verified ({} events)", chain.len());
        Ok(true)
    }
}

// ============================================================================
// Chassis Host API (for WASM payloads)
// ============================================================================

/// Trait that WASM payloads can call back to the chassis
pub trait ChassisHost {
    fn send_message(&self, msg: IFMessage) -> Result<()>;
    fn check_policy(&self, action: &str, resource: &str) -> GuardDecision;
    fn log_event(&self, event_type: &str, data: serde_json::Value) -> Result<()>;
}

impl ChassisHost for Chassis {
    fn send_message(&self, msg: IFMessage) -> Result<()> {
        self.send_message(msg)
    }

    fn check_policy(&self, action: &str, resource: &str) -> GuardDecision {
        self.check_policy(action, resource)
    }

    fn log_event(&self, event_type: &str, data: serde_json::Value) -> Result<()> {
        // Create dummy message for logging
        let dummy_msg = IFMessage {
            performative: "log".to_string(),
            sender: self.agent_id.clone(),
            receiver: vec!["if://witness".to_string()],
            content: data,
            timestamp: Utc::now().to_rfc3339(),
            sequence_num: 0,
            trace_id: Uuid::new_v4().to_string(),
            hazard: None,
            citation_ids: None,
            nonce: None,
            ttl: None,
            signature: None,
        };

        self.log_witness_event(event_type, &dummy_msg)
    }
}

// ============================================================================
// Tests
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_message_signing() {
        let chassis = Chassis::new("if://agent/test".to_string());

        let msg = IFMessage {
            performative: "inform".to_string(),
            sender: "if://agent/test".to_string(),
            receiver: vec!["if://agent/receiver".to_string()],
            content: serde_json::json!({"claim": "test"}),
            timestamp: Utc::now().to_rfc3339(),
            sequence_num: 1,
            trace_id: "trace-123".to_string(),
            hazard: None,
            citation_ids: None,
            nonce: Some("nonce-123".to_string()),
            ttl: Some(60),
            signature: None,
        };

        let signature = chassis.sign_message(&msg).unwrap();
        assert_eq!(signature.to_bytes().len(), 64);
    }

    #[test]
    fn test_witness_chain_integrity() {
        let chassis = Chassis::new("if://agent/test".to_string());

        // Send 3 messages
        for i in 0..3 {
            let msg = IFMessage {
                performative: "inform".to_string(),
                sender: String::new(),
                receiver: vec!["if://agent/receiver".to_string()],
                content: serde_json::json!({"count": i}),
                timestamp: String::new(),
                sequence_num: 0,
                trace_id: format!("trace-{}", i),
                hazard: None,
                citation_ids: None,
                nonce: None,
                ttl: None,
                signature: None,
            };

            chassis.send_message(msg).unwrap();
        }

        // Verify chain
        assert!(chassis.verify_witness_chain().unwrap());

        // Check chain length
        let chain = chassis.get_witness_chain();
        assert_eq!(chain.len(), 3);
    }

    #[test]
    fn test_policy_enforcement() {
        let chassis = Chassis::new("if://agent/test".to_string());

        // Should allow normal operations
        assert_eq!(
            chassis.check_policy("read", "database"),
            GuardDecision::Allow
        );

        // Should deny dangerous operations
        match chassis.check_policy("delete", "production-db") {
            GuardDecision::Deny { .. } => {},
            _ => panic!("Expected Deny decision"),
        }

        // Should escalate critical operations
        match chassis.check_policy("deploy", "critical-service") {
            GuardDecision::Escalate { .. } => {},
            _ => panic!("Expected Escalate decision"),
        }
    }
}
