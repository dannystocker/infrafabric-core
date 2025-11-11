/**
 * SRTP Key Manager for WebRTC Agent Mesh
 *
 * Implements:
 * - Automatic key rotation every 24 hours
 * - Coordinated key changes across peer connections
 * - IF.witness logging for security audit trail
 *
 * Philosophy:
 * - IF.ground: All key rotations are verifiable via IF.witness
 * - IF.TTT: Transparent key lifecycle with full audit trail
 */

import { randomBytes } from 'crypto';
import { createHash } from 'crypto';

/**
 * SRTP Key Material
 * Master key: 256-bit (32 bytes)
 * Master salt: 112-bit (14 bytes)
 */
export interface SRTPKeyMaterial {
  masterKey: Uint8Array; // 32 bytes
  masterSalt: Uint8Array; // 14 bytes
  createdAt: Date;
  expiresAt: Date;
  keyId: string;
}

/**
 * SRTP Key Rotation Event
 */
export interface SRTPKeyRotationEvent {
  event: 'srtp_key_rotated';
  agent_id: string;
  peer_id: string;
  old_key_id: string;
  new_key_id: string;
  rotation_reason: 'scheduled' | 'manual' | 'security_event';
  trace_id: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

/**
 * SRTP Key Manager
 *
 * Manages SRTP encryption keys for WebRTC peer connections with automatic rotation
 */
export class SRTPKeyManager {
  private agentId: string;

  // Current keys for each peer: peer_id -> SRTPKeyMaterial
  private currentKeys: Map<string, SRTPKeyMaterial> = new Map();

  // Pending keys during rotation: peer_id -> SRTPKeyMaterial
  private pendingKeys: Map<string, SRTPKeyMaterial> = new Map();

  // Rotation interval (24 hours in milliseconds)
  private rotationInterval: number = 24 * 60 * 60 * 1000;

  // Rotation timers: peer_id -> NodeJS.Timeout
  private rotationTimers: Map<string, NodeJS.Timeout> = new Map();

  // Witness logger
  private witnessLogger?: (event: SRTPKeyRotationEvent) => Promise<void>;

  // Current trace ID
  private currentTraceId: string;

  constructor(
    agentId: string,
    witnessLogger?: (event: SRTPKeyRotationEvent) => Promise<void>,
    rotationIntervalMs?: number
  ) {
    this.agentId = agentId;
    this.witnessLogger = witnessLogger;
    if (rotationIntervalMs) {
      this.rotationInterval = rotationIntervalMs;
    }
    this.currentTraceId = this.generateTraceId();
  }

  /**
   * Generate new SRTP key material for a peer
   */
  async generateKeyMaterial(peerId: string): Promise<SRTPKeyMaterial> {
    // Generate 32-byte master key (256-bit)
    const masterKey = new Uint8Array(randomBytes(32));

    // Generate 14-byte master salt (112-bit as per SRTP spec)
    const masterSalt = new Uint8Array(randomBytes(14));

    const now = new Date();
    const expiresAt = new Date(now.getTime() + this.rotationInterval);

    // Create unique key ID (hash of key + salt + timestamp)
    const keyId = this.createKeyId(masterKey, masterSalt, now);

    const keyMaterial: SRTPKeyMaterial = {
      masterKey,
      masterSalt,
      createdAt: now,
      expiresAt,
      keyId
    };

    // Store as current key
    this.currentKeys.set(peerId, keyMaterial);

    // Schedule rotation
    this.scheduleKeyRotation(peerId);

    // Log to IF.witness
    await this.logKeyRotation(peerId, '', keyId, 'manual');

    return keyMaterial;
  }

  /**
   * Get current key material for a peer
   */
  getCurrentKey(peerId: string): SRTPKeyMaterial | undefined {
    return this.currentKeys.get(peerId);
  }

  /**
   * Get pending key material for a peer (during rotation)
   */
  getPendingKey(peerId: string): SRTPKeyMaterial | undefined {
    return this.pendingKeys.get(peerId);
  }

  /**
   * Manually rotate key for a peer
   */
  async rotateKey(peerId: string, reason: 'scheduled' | 'manual' | 'security_event' = 'manual'): Promise<SRTPKeyMaterial> {
    const oldKey = this.currentKeys.get(peerId);
    const oldKeyId = oldKey?.keyId || '';

    // Generate new key material
    const masterKey = new Uint8Array(randomBytes(32));
    const masterSalt = new Uint8Array(randomBytes(14));

    const now = new Date();
    const expiresAt = new Date(now.getTime() + this.rotationInterval);
    const keyId = this.createKeyId(masterKey, masterSalt, now);

    const newKeyMaterial: SRTPKeyMaterial = {
      masterKey,
      masterSalt,
      createdAt: now,
      expiresAt,
      keyId
    };

    // Set as pending key first (for coordinated handover)
    this.pendingKeys.set(peerId, newKeyMaterial);

    // Log rotation to IF.witness
    await this.logKeyRotation(peerId, oldKeyId, keyId, reason);

    return newKeyMaterial;
  }

  /**
   * Confirm key rotation (move pending to current)
   */
  confirmKeyRotation(peerId: string): void {
    const pendingKey = this.pendingKeys.get(peerId);
    if (pendingKey) {
      this.currentKeys.set(peerId, pendingKey);
      this.pendingKeys.delete(peerId);

      // Reschedule rotation
      this.scheduleKeyRotation(peerId);
    }
  }

  /**
   * Validate key material (check expiration)
   */
  validateKey(peerId: string): { valid: boolean; reason?: string } {
    const keyMaterial = this.currentKeys.get(peerId);

    if (!keyMaterial) {
      return { valid: false, reason: 'No key material found' };
    }

    const now = new Date();
    if (now > keyMaterial.expiresAt) {
      return { valid: false, reason: 'Key expired' };
    }

    return { valid: true };
  }

  /**
   * Remove keys for a peer (on disconnect)
   */
  async removePeer(peerId: string): Promise<void> {
    // Clear rotation timer
    const timer = this.rotationTimers.get(peerId);
    if (timer) {
      clearTimeout(timer);
      this.rotationTimers.delete(peerId);
    }

    // Remove keys
    this.currentKeys.delete(peerId);
    this.pendingKeys.delete(peerId);
  }

  /**
   * Get all peer IDs with active keys
   */
  getActivePeers(): string[] {
    return Array.from(this.currentKeys.keys());
  }

  /**
   * Export key material as base64 (for transmission)
   */
  exportKeyMaterial(keyMaterial: SRTPKeyMaterial): {
    masterKey: string;
    masterSalt: string;
    keyId: string;
    expiresAt: string;
  } {
    return {
      masterKey: this.bytesToBase64(keyMaterial.masterKey),
      masterSalt: this.bytesToBase64(keyMaterial.masterSalt),
      keyId: keyMaterial.keyId,
      expiresAt: keyMaterial.expiresAt.toISOString()
    };
  }

  /**
   * Import key material from base64
   */
  importKeyMaterial(
    peerId: string,
    data: {
      masterKey: string;
      masterSalt: string;
      keyId: string;
      expiresAt: string;
    }
  ): SRTPKeyMaterial {
    const keyMaterial: SRTPKeyMaterial = {
      masterKey: this.base64ToBytes(data.masterKey),
      masterSalt: this.base64ToBytes(data.masterSalt),
      createdAt: new Date(),
      expiresAt: new Date(data.expiresAt),
      keyId: data.keyId
    };

    this.currentKeys.set(peerId, keyMaterial);
    this.scheduleKeyRotation(peerId);

    return keyMaterial;
  }

  // ============ Private Methods ============

  /**
   * Schedule automatic key rotation
   */
  private scheduleKeyRotation(peerId: string): void {
    // Clear existing timer
    const existingTimer = this.rotationTimers.get(peerId);
    if (existingTimer) {
      clearTimeout(existingTimer);
    }

    // Schedule new rotation
    const timer = setTimeout(async () => {
      await this.rotateKey(peerId, 'scheduled');
    }, this.rotationInterval);

    this.rotationTimers.set(peerId, timer);
  }

  /**
   * Create unique key ID
   */
  private createKeyId(masterKey: Uint8Array, masterSalt: Uint8Array, timestamp: Date): string {
    const combined = new Uint8Array(masterKey.length + masterSalt.length + 8);
    combined.set(masterKey, 0);
    combined.set(masterSalt, masterKey.length);

    // Add timestamp bytes
    const timestampBytes = new Uint8Array(8);
    const view = new DataView(timestampBytes.buffer);
    view.setBigUint64(0, BigInt(timestamp.getTime()), false);
    combined.set(timestampBytes, masterKey.length + masterSalt.length);

    // Hash to create key ID
    return createHash('sha256')
      .update(Buffer.from(combined))
      .digest('hex')
      .substring(0, 16); // Use first 16 chars
  }

  /**
   * Log key rotation to IF.witness
   */
  private async logKeyRotation(
    peerId: string,
    oldKeyId: string,
    newKeyId: string,
    reason: 'scheduled' | 'manual' | 'security_event'
  ): Promise<void> {
    if (!this.witnessLogger) {
      return;
    }

    const event: SRTPKeyRotationEvent = {
      event: 'srtp_key_rotated',
      agent_id: this.agentId,
      peer_id: peerId,
      old_key_id: oldKeyId,
      new_key_id: newKeyId,
      rotation_reason: reason,
      trace_id: this.currentTraceId,
      timestamp: new Date().toISOString(),
      metadata: {
        rotation_interval_ms: this.rotationInterval
      }
    };

    await this.witnessLogger(event);
  }

  /**
   * Generate trace ID
   */
  private generateTraceId(): string {
    const bytes = new Uint8Array(randomBytes(12));
    return this.bytesToHex(bytes);
  }

  /**
   * Convert bytes to hex string
   */
  private bytesToHex(bytes: Uint8Array): string {
    return Array.from(bytes)
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }

  /**
   * Convert bytes to base64
   */
  private bytesToBase64(bytes: Uint8Array): string {
    return Buffer.from(bytes).toString('base64');
  }

  /**
   * Convert base64 to bytes
   */
  private base64ToBytes(base64: string): Uint8Array {
    return new Uint8Array(Buffer.from(base64, 'base64'));
  }

  /**
   * Cleanup all resources
   */
  async shutdown(): Promise<void> {
    // Clear all timers
    for (const timer of this.rotationTimers.values()) {
      clearTimeout(timer);
    }
    this.rotationTimers.clear();

    // Clear all keys
    this.currentKeys.clear();
    this.pendingKeys.clear();
  }
}
