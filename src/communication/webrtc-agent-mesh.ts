/**
 * WebRTC Agent Mesh for IF.swarm
 *
 * Philosophy Grounding:
 * - Wu Lun (五倫) Relationship: 兄弟 (Siblings) — Agents are parallel peers, coordinated but equal
 * - Indra's Net: Every node reflects every other node (full mesh topology)
 * - IF.ground: Verifiable signaling (SDP logged to IF.witness)
 * - IF.TTT: Traceable, Transparent, Trustworthy (Ed25519 signed messages)
 */

import * as ed25519 from '@noble/ed25519';
import { WebSocket } from 'ws';
import { createHash } from 'crypto';
import { SRTPKeyManager, SRTPKeyRotationEvent } from './srtp-key-manager';

/**
 * IFMessage v2.1 Schema
 * Extends v1.0 with signature field for cryptographic integrity
 */
export interface IFMessage {
  id: string;
  timestamp: string;
  level: number;
  source: string;
  destination: string;
  traceId?: string;
  version: string;
  payload: Record<string, unknown>;

  // v2.1 extensions
  performative?: string;
  conversation_id?: string;
  sequence_num?: number;
  citation_ids?: string[];

  // Cryptographic signature (Ed25519)
  signature?: {
    algorithm: 'ed25519';
    public_key: string;
    signature_bytes: string;
    signed_fields: string[];
  };
}

/**
 * TURN server credentials
 */
export interface TURNServerConfig {
  urls: string;
  username: string;
  credential: string;
}

/**
 * WebRTC Peer Connection Configuration
 */
export interface IFWebRTCConfig {
  agentId: string;
  privateKey?: Uint8Array;
  publicKey?: Uint8Array;
  signalingServerUrl?: string;
  stunServers?: string[];
  turnServers?: TURNServerConfig[];
  witnessLogger?: (event: WitnessEvent | SRTPKeyRotationEvent) => Promise<void>;
  turnFallbackTimeout?: number; // ms to wait before falling back to TURN (default: 5000)

  // Security configuration
  productionMode?: boolean; // Enables strict security checks (default: false)
  iceTransportPolicy?: 'all' | 'relay'; // 'relay' forces TURN usage for high-security mode
  allowSelfSignedCerts?: boolean; // Allow self-signed certificates (default: true in dev, false in production)
  enableCertValidation?: boolean; // Validate DTLS certificates (default: true in production)
  enableSRTPKeyRotation?: boolean; // Enable SRTP key rotation (default: true)
  srtpKeyRotationInterval?: number; // SRTP key rotation interval in ms (default: 24 hours)
}

/**
 * IF.witness Event for logging
 */
export interface WitnessEvent {
  event: string;
  agent_id: string;
  peer_id?: string;
  sdp_hash?: string;
  ice_candidate?: string;
  trace_id: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

/**
 * Connection Quality Metrics
 */
export interface ConnectionQuality {
  peerId: string;
  state: RTCPeerConnectionState;
  iceConnectionState: string; // RTCIceConnectionState (compatible with @types/webrtc)
  iceGatheringState: string; // RTCIceGatheringState (compatible with @types/webrtc)
  candidateType?: 'host' | 'srflx' | 'relay' | 'prflx'; // relay = TURN
  bytesReceived: number;
  bytesSent: number;
  packetsLost: number;
  roundTripTime?: number; // ms
  lastUpdated: string;
}

/**
 * WebRTC Agent Mesh Implementation
 *
 * Implements peer-to-peer communication using:
 * - RTCPeerConnection for WebRTC connectivity
 * - RTCDataChannel for IFMessage transport
 * - Ed25519 signatures for message integrity
 * - WebSocket signaling for SDP/ICE exchange
 */
export class IFAgentWebRTC {
  private agentId: string;
  private privateKey: Uint8Array;
  private publicKey: Uint8Array;

  // WebRTC connections: peer_id -> RTCPeerConnection
  private peerConnections: Map<string, RTCPeerConnection> = new Map();

  // Data channels: peer_id -> RTCDataChannel
  private dataChannels: Map<string, RTCDataChannel> = new Map();

  // Signaling WebSocket
  private signalingWs?: WebSocket;
  private signalingServerUrl: string;

  // STUN/TURN servers
  private iceServers: RTCIceServer[];
  private turnServers: TURNServerConfig[];
  private turnFallbackTimeout: number;

  // TURN fallback tracking: peer_id -> timeout handle
  private turnFallbackTimers: Map<string, NodeJS.Timeout> = new Map();
  private usingTurn: Map<string, boolean> = new Map();

  // Connection quality monitoring: peer_id -> metrics
  private connectionQuality: Map<string, ConnectionQuality> = new Map();
  private qualityMonitorIntervals: Map<string, NodeJS.Timeout> = new Map();

  // Message handlers
  private messageHandlers: Set<(message: IFMessage) => void> = new Set();

  // IF.witness logger
  private witnessLogger?: (event: WitnessEvent | SRTPKeyRotationEvent) => Promise<void>;

  // Sequence number for outgoing messages
  private sequenceNum: number = 0;

  // Current trace ID
  private currentTraceId: string;

  // Security configuration
  private productionMode: boolean;
  private iceTransportPolicy: 'all' | 'relay';
  private allowSelfSignedCerts: boolean;
  private enableCertValidation: boolean;

  // SRTP key manager
  private srtpKeyManager?: SRTPKeyManager;

  // DTLS fingerprints: peer_id -> fingerprint hash
  private dtlsFingerprints: Map<string, string> = new Map();

  constructor(config: IFWebRTCConfig) {
    this.agentId = config.agentId;
    this.signalingServerUrl = config.signalingServerUrl || 'ws://localhost:8443';

    // Initialize Ed25519 keypair
    if (config.privateKey && config.publicKey) {
      this.privateKey = config.privateKey;
      this.publicKey = config.publicKey;
    } else {
      // Generate new keypair
      this.privateKey = ed25519.utils.randomPrivateKey();
      this.publicKey = ed25519.getPublicKey(this.privateKey);
    }

    // Configure ICE servers (STUN only - TURN added on fallback)
    const defaultStunServers = config.stunServers || ['stun:stun.l.google.com:19302'];
    this.iceServers = defaultStunServers.map(url => ({ urls: url }));

    // Store TURN servers for fallback
    this.turnServers = config.turnServers || [];
    this.turnFallbackTimeout = config.turnFallbackTimeout || 5000;

    // IF.witness logger
    this.witnessLogger = config.witnessLogger;

    // Initialize trace ID
    this.currentTraceId = this.generateTraceId();

    // Security configuration
    this.productionMode = config.productionMode || false;
    this.iceTransportPolicy = config.iceTransportPolicy || 'all';
    this.allowSelfSignedCerts = config.allowSelfSignedCerts !== undefined
      ? config.allowSelfSignedCerts
      : !this.productionMode; // Default: allow in dev, reject in production
    this.enableCertValidation = config.enableCertValidation !== undefined
      ? config.enableCertValidation
      : this.productionMode; // Default: enabled in production

    // Initialize SRTP key manager if enabled
    if (config.enableSRTPKeyRotation !== false) { // Default: true
      this.srtpKeyManager = new SRTPKeyManager(
        this.agentId,
        this.witnessLogger,
        config.srtpKeyRotationInterval
      );
    }
  }

  /**
   * Connect to signaling server
   */
  async connectToSignaling(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.signalingWs = new WebSocket(this.signalingServerUrl);

      this.signalingWs.on('open', () => {
        // Register with signaling server
        this.signalingWs!.send(JSON.stringify({
          type: 'register',
          agent_id: this.agentId
        }));

        this.logToWitness({
          event: 'signaling_connected',
          agent_id: this.agentId,
          trace_id: this.currentTraceId,
          timestamp: new Date().toISOString()
        });

        resolve();
      });

      this.signalingWs.on('message', (data: Buffer) => {
        this.handleSignalingMessage(JSON.parse(data.toString()));
      });

      this.signalingWs.on('error', (error) => {
        reject(error);
      });
    });
  }

  /**
   * Create offer to connect to peer
   */
  async createOffer(peerId: string): Promise<RTCSessionDescriptionInit> {
    const pc = this.createPeerConnection(peerId);

    // Create data channel
    const dataChannel = pc.createDataChannel('if-agent-messaging', {
      ordered: true,
      maxRetransmits: 3
    });

    this.setupDataChannel(peerId, dataChannel);

    // Create offer
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    // Start TURN fallback timer if TURN servers configured
    this.startTurnFallbackTimer(peerId);

    // Log to IF.witness
    await this.logToWitness({
      event: 'webrtc_offer_created',
      agent_id: this.agentId,
      peer_id: peerId,
      sdp_hash: this.hashSDP(offer.sdp!),
      trace_id: this.currentTraceId,
      timestamp: new Date().toISOString()
    });

    // Send via signaling
    this.signalingWs?.send(JSON.stringify({
      type: 'offer',
      from: this.agentId,
      to: peerId,
      offer: offer
    }));

    return offer;
  }

  /**
   * Handle incoming offer and create answer
   */
  async handleOffer(peerId: string, offer: RTCSessionDescriptionInit): Promise<RTCSessionDescriptionInit> {
    const pc = this.createPeerConnection(peerId);

    // Validate and extract DTLS fingerprint from SDP
    if (this.enableCertValidation && offer.sdp) {
      await this.validateAndStoreDTLSFingerprint(peerId, offer.sdp);
    }

    await pc.setRemoteDescription(new RTCSessionDescription(offer));

    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);

    // Log to IF.witness
    await this.logToWitness({
      event: 'webrtc_answer_created',
      agent_id: this.agentId,
      peer_id: peerId,
      sdp_hash: this.hashSDP(answer.sdp!),
      trace_id: this.currentTraceId,
      timestamp: new Date().toISOString()
    });

    // Send via signaling
    this.signalingWs?.send(JSON.stringify({
      type: 'answer',
      from: this.agentId,
      to: peerId,
      answer: answer
    }));

    return answer;
  }

  /**
   * Handle incoming answer
   */
  async handleAnswer(peerId: string, answer: RTCSessionDescriptionInit): Promise<void> {
    const pc = this.peerConnections.get(peerId);
    if (!pc) {
      throw new Error(`No peer connection for ${peerId}`);
    }

    // Validate and extract DTLS fingerprint from SDP
    if (this.enableCertValidation && answer.sdp) {
      await this.validateAndStoreDTLSFingerprint(peerId, answer.sdp);
    }

    await pc.setRemoteDescription(new RTCSessionDescription(answer));

    await this.logToWitness({
      event: 'webrtc_answer_received',
      agent_id: this.agentId,
      peer_id: peerId,
      sdp_hash: this.hashSDP(answer.sdp!),
      trace_id: this.currentTraceId,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Handle incoming ICE candidate
   */
  async handleIceCandidate(peerId: string, candidate: RTCIceCandidateInit): Promise<void> {
    const pc = this.peerConnections.get(peerId);
    if (!pc) {
      throw new Error(`No peer connection for ${peerId}`);
    }

    await pc.addIceCandidate(new RTCIceCandidate(candidate));
  }

  /**
   * Send IFMessage to peer (with Ed25519 signature)
   */
  async sendIFMessage(peerId: string, message: IFMessage): Promise<void> {
    const dataChannel = this.dataChannels.get(peerId);
    if (!dataChannel || dataChannel.readyState !== 'open') {
      throw new Error(`Data channel to ${peerId} not open`);
    }

    // Add metadata
    message.source = this.agentId;
    message.timestamp = new Date().toISOString();
    message.sequence_num = ++this.sequenceNum;
    message.traceId = this.currentTraceId;

    // Sign message with Ed25519
    const signature = await this.signMessage(message);
    message.signature = signature;

    // Send over data channel
    const messageStr = JSON.stringify(message);
    dataChannel.send(messageStr);

    await this.logToWitness({
      event: 'ifmessage_sent',
      agent_id: this.agentId,
      peer_id: peerId,
      trace_id: this.currentTraceId,
      timestamp: new Date().toISOString(),
      metadata: {
        message_id: message.id,
        sequence_num: message.sequence_num
      }
    });
  }

  /**
   * Broadcast IFMessage to all connected peers
   */
  async broadcastIFMessage(message: IFMessage): Promise<void> {
    const peers = Array.from(this.dataChannels.keys());
    await Promise.all(peers.map(peerId => this.sendIFMessage(peerId, { ...message })));
  }

  /**
   * Register message handler
   */
  onIFMessage(handler: (message: IFMessage) => void): void {
    this.messageHandlers.add(handler);
  }

  /**
   * Remove message handler
   */
  offIFMessage(handler: (message: IFMessage) => void): void {
    this.messageHandlers.delete(handler);
  }

  /**
   * Get list of connected peers
   */
  getConnectedPeers(): string[] {
    return Array.from(this.dataChannels.keys()).filter(
      peerId => this.dataChannels.get(peerId)?.readyState === 'open'
    );
  }

  /**
   * Disconnect from peer
   */
  async disconnectPeer(peerId: string): Promise<void> {
    const pc = this.peerConnections.get(peerId);
    if (pc) {
      pc.close();
      this.peerConnections.delete(peerId);
    }

    this.dataChannels.delete(peerId);

    await this.logToWitness({
      event: 'peer_disconnected',
      agent_id: this.agentId,
      peer_id: peerId,
      trace_id: this.currentTraceId,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Disconnect from all peers and signaling
   */
  async disconnect(): Promise<void> {
    // Close all peer connections
    for (const [peerId, pc] of this.peerConnections) {
      pc.close();
    }
    this.peerConnections.clear();
    this.dataChannels.clear();

    // Close signaling connection
    if (this.signalingWs) {
      this.signalingWs.close();
      this.signalingWs = undefined;
    }

    await this.logToWitness({
      event: 'agent_disconnected',
      agent_id: this.agentId,
      trace_id: this.currentTraceId,
      timestamp: new Date().toISOString()
    });
  }

  // ============ Private Methods ============

  /**
   * Create RTCPeerConnection for peer
   */
  private createPeerConnection(peerId: string): RTCPeerConnection {
    if (this.peerConnections.has(peerId)) {
      return this.peerConnections.get(peerId)!;
    }

    // Determine ICE servers (STUN or STUN+TURN)
    let iceServers = this.iceServers;
    if (this.usingTurn.get(peerId)) {
      // Add TURN servers to ICE servers
      iceServers = [
        ...this.iceServers,
        ...this.turnServers.map(turn => ({
          urls: turn.urls,
          username: turn.username,
          credential: turn.credential
        }))
      ];
    }

    const pc = new RTCPeerConnection({
      iceServers,
      iceTransportPolicy: this.iceTransportPolicy // Enforce security policy
    });

    // ICE candidate handler
    pc.onicecandidate = (event) => {
      if (event.candidate) {
        this.signalingWs?.send(JSON.stringify({
          type: 'ice-candidate',
          from: this.agentId,
          to: peerId,
          candidate: event.candidate
        }));

        this.logToWitness({
          event: 'ice_candidate_sent',
          agent_id: this.agentId,
          peer_id: peerId,
          ice_candidate: event.candidate.candidate,
          trace_id: this.currentTraceId,
          timestamp: new Date().toISOString()
        });
      }
    };

    // Connection state handler
    pc.onconnectionstatechange = () => {
      this.logToWitness({
        event: 'connection_state_changed',
        agent_id: this.agentId,
        peer_id: peerId,
        trace_id: this.currentTraceId,
        timestamp: new Date().toISOString(),
        metadata: {
          state: pc.connectionState
        }
      });

      // Clear TURN fallback timer on successful connection
      if (pc.connectionState === 'connected') {
        this.clearTurnFallbackTimer(peerId);
        this.startConnectionMonitoring(peerId);
      }

      // Stop monitoring on disconnect or failure
      if (pc.connectionState === 'disconnected' || pc.connectionState === 'failed' || pc.connectionState === 'closed') {
        this.stopConnectionMonitoring(peerId);
      }
    };

    // Data channel handler (for answering side)
    pc.ondatachannel = (event) => {
      this.setupDataChannel(peerId, event.channel);
    };

    this.peerConnections.set(peerId, pc);
    return pc;
  }

  /**
   * Setup data channel event handlers
   */
  private setupDataChannel(peerId: string, dataChannel: RTCDataChannel): void {
    this.dataChannels.set(peerId, dataChannel);

    dataChannel.onopen = () => {
      this.logToWitness({
        event: 'datachannel_open',
        agent_id: this.agentId,
        peer_id: peerId,
        trace_id: this.currentTraceId,
        timestamp: new Date().toISOString()
      });
    };

    dataChannel.onmessage = async (event) => {
      await this.handleMessage(peerId, event.data);
    };

    dataChannel.onerror = (error) => {
      this.logToWitness({
        event: 'datachannel_error',
        agent_id: this.agentId,
        peer_id: peerId,
        trace_id: this.currentTraceId,
        timestamp: new Date().toISOString(),
        metadata: {
          error: String(error)
        }
      });
    };

    dataChannel.onclose = () => {
      this.logToWitness({
        event: 'datachannel_closed',
        agent_id: this.agentId,
        peer_id: peerId,
        trace_id: this.currentTraceId,
        timestamp: new Date().toISOString()
      });
    };
  }

  /**
   * Handle signaling message
   */
  private async handleSignalingMessage(msg: any): Promise<void> {
    switch (msg.type) {
      case 'offer':
        await this.handleOffer(msg.from, msg.offer);
        break;

      case 'answer':
        await this.handleAnswer(msg.from, msg.answer);
        break;

      case 'ice-candidate':
        await this.handleIceCandidate(msg.from, msg.candidate);
        break;

      default:
        console.warn(`Unknown signaling message type: ${msg.type}`);
    }
  }

  /**
   * Handle incoming IFMessage
   */
  private async handleMessage(peerId: string, data: string): Promise<void> {
    try {
      const message: IFMessage = JSON.parse(data);

      // Verify signature
      if (message.signature) {
        const valid = await this.verifyMessage(message);
        if (!valid) {
          console.error(`Invalid signature from ${peerId}, message rejected`);
          return;
        }
      }

      // Notify handlers
      this.messageHandlers.forEach(handler => handler(message));

      await this.logToWitness({
        event: 'ifmessage_received',
        agent_id: this.agentId,
        peer_id: peerId,
        trace_id: message.traceId || this.currentTraceId,
        timestamp: new Date().toISOString(),
        metadata: {
          message_id: message.id,
          sequence_num: message.sequence_num
        }
      });
    } catch (error) {
      console.error(`Failed to handle message from ${peerId}:`, error);
    }
  }

  /**
   * Sign IFMessage with Ed25519
   */
  private async signMessage(message: IFMessage): Promise<IFMessage['signature']> {
    const signedFields = [
      'id', 'timestamp', 'level', 'source', 'destination',
      'payload', 'performative', 'conversation_id', 'sequence_num'
    ];

    // Create canonical representation
    const canonical: Record<string, unknown> = {};
    for (const field of signedFields) {
      if (field in message) {
        canonical[field] = message[field as keyof IFMessage];
      }
    }

    const canonicalStr = JSON.stringify(canonical, Object.keys(canonical).sort());
    const messageBytes = new TextEncoder().encode(canonicalStr);

    // Sign with Ed25519
    const signatureBytes = await ed25519.sign(messageBytes, this.privateKey);

    return {
      algorithm: 'ed25519',
      public_key: this.bytesToHex(this.publicKey),
      signature_bytes: this.bytesToHex(signatureBytes),
      signed_fields: signedFields
    };
  }

  /**
   * Verify IFMessage signature
   */
  private async verifyMessage(message: IFMessage): Promise<boolean> {
    if (!message.signature) {
      return false;
    }

    const { public_key, signature_bytes, signed_fields } = message.signature;

    // Reconstruct canonical message
    const canonical: Record<string, unknown> = {};
    for (const field of signed_fields) {
      if (field in message) {
        canonical[field] = message[field as keyof IFMessage];
      }
    }

    const canonicalStr = JSON.stringify(canonical, Object.keys(canonical).sort());
    const messageBytes = new TextEncoder().encode(canonicalStr);

    // Verify signature
    const pubKeyBytes = this.hexToBytes(public_key);
    const sigBytes = this.hexToBytes(signature_bytes);

    return await ed25519.verify(sigBytes, messageBytes, pubKeyBytes);
  }

  /**
   * Hash SDP for IF.witness logging
   */
  private hashSDP(sdp: string): string {
    return createHash('sha256').update(sdp).digest('hex');
  }

  /**
   * Log event to IF.witness
   */
  private async logToWitness(event: WitnessEvent): Promise<void> {
    if (this.witnessLogger) {
      await this.witnessLogger(event);
    }
  }

  /**
   * Generate trace ID
   */
  private generateTraceId(): string {
    const bytes = new Uint8Array(12);
    crypto.getRandomValues(bytes);
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
   * Convert hex string to bytes
   */
  private hexToBytes(hex: string): Uint8Array {
    const bytes = new Uint8Array(hex.length / 2);
    for (let i = 0; i < hex.length; i += 2) {
      bytes[i / 2] = parseInt(hex.substr(i, 2), 16);
    }
    return bytes;
  }

  /**
   * Get agent's public key (for identity verification)
   */
  getPublicKey(): string {
    return this.bytesToHex(this.publicKey);
  }

  /**
   * Get agent ID
   */
  getAgentId(): string {
    return this.agentId;
  }

  // ============ TURN Fallback Methods ============

  /**
   * Start TURN fallback timer for peer connection
   */
  private startTurnFallbackTimer(peerId: string): void {
    if (this.turnServers.length === 0) {
      return; // No TURN servers configured
    }

    // Clear existing timer if any
    const existingTimer = this.turnFallbackTimers.get(peerId);
    if (existingTimer) {
      clearTimeout(existingTimer);
    }

    // Set new timer
    const timer = setTimeout(async () => {
      await this.attemptTurnFallback(peerId);
    }, this.turnFallbackTimeout);

    this.turnFallbackTimers.set(peerId, timer);
  }

  /**
   * Attempt TURN fallback if P2P connection has not succeeded
   */
  private async attemptTurnFallback(peerId: string): Promise<void> {
    const pc = this.peerConnections.get(peerId);
    if (!pc) {
      return; // Connection already closed
    }

    // Check if connection is already established
    const iceConnectionState = (pc as any).iceConnectionState;
    if (pc.connectionState === 'connected' || iceConnectionState === 'connected') {
      await this.logToWitness({
        event: 'turn_fallback_unnecessary',
        agent_id: this.agentId,
        peer_id: peerId,
        trace_id: this.currentTraceId,
        timestamp: new Date().toISOString(),
        metadata: {
          connectionState: pc.connectionState,
          iceConnectionState
        }
      });
      return;
    }

    // Log fallback decision to IF.witness
    await this.logToWitness({
      event: 'turn_fallback_initiated',
      agent_id: this.agentId,
      peer_id: peerId,
      trace_id: this.currentTraceId,
      timestamp: new Date().toISOString(),
      metadata: {
        reason: 'No P2P connection established within timeout',
        timeout_ms: this.turnFallbackTimeout,
        connectionState: pc.connectionState,
        iceConnectionState: (pc as any).iceConnectionState || 'unknown'
      }
    });

    // Close existing connection
    pc.close();
    this.peerConnections.delete(peerId);

    // Create new connection with TURN servers
    this.usingTurn.set(peerId, true);
    const newPc = this.createPeerConnection(peerId);

    // Re-create data channel
    const dataChannel = newPc.createDataChannel('if-agent-messaging', {
      ordered: true,
      maxRetransmits: 3
    });
    this.setupDataChannel(peerId, dataChannel);

    // Create new offer
    const offer = await newPc.createOffer();
    await newPc.setLocalDescription(offer);

    // Send via signaling
    this.signalingWs?.send(JSON.stringify({
      type: 'offer',
      from: this.agentId,
      to: peerId,
      offer: offer
    }));

    await this.logToWitness({
      event: 'turn_fallback_offer_sent',
      agent_id: this.agentId,
      peer_id: peerId,
      trace_id: this.currentTraceId,
      timestamp: new Date().toISOString(),
      metadata: {
        sdp_hash: this.hashSDP(offer.sdp!)
      }
    });
  }

  /**
   * Clear TURN fallback timer for peer
   */
  private clearTurnFallbackTimer(peerId: string): void {
    const timer = this.turnFallbackTimers.get(peerId);
    if (timer) {
      clearTimeout(timer);
      this.turnFallbackTimers.delete(peerId);
    }
  }

  // ============ Connection Quality Monitoring ============

  /**
   * Start monitoring connection quality for peer
   */
  private startConnectionMonitoring(peerId: string): void {
    // Monitor every 2 seconds
    const interval = setInterval(async () => {
      await this.updateConnectionQuality(peerId);
    }, 2000);

    this.qualityMonitorIntervals.set(peerId, interval);
  }

  /**
   * Stop monitoring connection quality for peer
   */
  private stopConnectionMonitoring(peerId: string): void {
    const interval = this.qualityMonitorIntervals.get(peerId);
    if (interval) {
      clearInterval(interval);
      this.qualityMonitorIntervals.delete(peerId);
    }
  }

  /**
   * Update connection quality metrics for peer
   */
  private async updateConnectionQuality(peerId: string): Promise<void> {
    const pc = this.peerConnections.get(peerId);
    if (!pc) {
      return;
    }

    try {
      const stats = await pc.getStats();
      let bytesReceived = 0;
      let bytesSent = 0;
      let packetsLost = 0;
      let roundTripTime: number | undefined;
      let candidateType: ConnectionQuality['candidateType'];

      stats.forEach((stat: any) => {
        if (stat.type === 'inbound-rtp') {
          bytesReceived += stat.bytesReceived || 0;
          packetsLost += stat.packetsLost || 0;
        } else if (stat.type === 'outbound-rtp') {
          bytesSent += stat.bytesSent || 0;
        } else if (stat.type === 'candidate-pair' && stat.state === 'succeeded') {
          roundTripTime = stat.currentRoundTripTime ? stat.currentRoundTripTime * 1000 : undefined;
        } else if (stat.type === 'local-candidate' && stat.candidateType) {
          candidateType = stat.candidateType as ConnectionQuality['candidateType'];
        }
      });

      const quality: ConnectionQuality = {
        peerId,
        state: pc.connectionState,
        iceConnectionState: (pc as any).iceConnectionState || 'unknown',
        iceGatheringState: (pc as any).iceGatheringState || 'unknown',
        candidateType,
        bytesReceived,
        bytesSent,
        packetsLost,
        roundTripTime,
        lastUpdated: new Date().toISOString()
      };

      this.connectionQuality.set(peerId, quality);

      // Log if using TURN (relay)
      if (candidateType === 'relay' && !this.usingTurn.get(peerId)) {
        this.usingTurn.set(peerId, true);
        await this.logToWitness({
          event: 'turn_connection_detected',
          agent_id: this.agentId,
          peer_id: peerId,
          trace_id: this.currentTraceId,
          timestamp: new Date().toISOString(),
          metadata: {
            candidateType
          }
        });
      }
    } catch (error) {
      // Stats may fail in certain states, silently ignore
    }
  }

  /**
   * Get connection quality for peer
   */
  getConnectionQuality(peerId: string): ConnectionQuality | undefined {
    return this.connectionQuality.get(peerId);
  }

  /**
   * Get connection quality for all peers
   */
  getAllConnectionQuality(): Map<string, ConnectionQuality> {
    return new Map(this.connectionQuality);
  }

  // ============ SIP Integration Hooks ============

  /**
   * Get WebRTC instance (for SIP integration)
   * Allows external code to access the WebRTC instance
   */
  getWebRTCInstance(): IFAgentWebRTC {
    return this;
  }

  /**
   * Get peer connection for specific peer (for SIP integration)
   */
  getPeerConnection(peerId: string): RTCPeerConnection | undefined {
    return this.peerConnections.get(peerId);
  }

  /**
   * Get data channel for specific peer (for SIP integration)
   */
  getDataChannel(peerId: string): RTCDataChannel | undefined {
    return this.dataChannels.get(peerId);
  }

  /**
   * Check if peer connection is established and ready
   */
  isPeerReady(peerId: string): boolean {
    const dataChannel = this.dataChannels.get(peerId);
    return dataChannel?.readyState === 'open';
  }

  /**
   * Get current trace ID (for SIP session correlation)
   */
  getCurrentTraceId(): string {
    return this.currentTraceId;
  }

  /**
   * Set trace ID (for SIP session correlation)
   */
  setTraceId(traceId: string): void {
    this.currentTraceId = traceId;
  }

  // ============ Security Validation Methods ============

  /**
   * Validate and store DTLS fingerprint from SDP
   */
  private async validateAndStoreDTLSFingerprint(peerId: string, sdp: string): Promise<void> {
    // Extract fingerprint from SDP
    const fingerprint = this.extractDTLSFingerprint(sdp);

    if (!fingerprint) {
      await this.logToWitness({
        event: 'webrtc_cert_validated',
        agent_id: this.agentId,
        peer_id: peerId,
        trace_id: this.currentTraceId,
        timestamp: new Date().toISOString(),
        metadata: {
          valid: false,
          reason: 'No DTLS fingerprint found in SDP'
        }
      });

      if (this.productionMode) {
        throw new Error(`No DTLS fingerprint found in SDP for peer ${peerId}`);
      }
      return;
    }

    // Validate certificate properties
    const validationResult = await this.validateCertificate(fingerprint, sdp);

    // Log validation result to IF.witness
    await this.logToWitness({
      event: 'webrtc_cert_validated',
      agent_id: this.agentId,
      peer_id: peerId,
      trace_id: this.currentTraceId,
      timestamp: new Date().toISOString(),
      metadata: {
        valid: validationResult.valid,
        reason: validationResult.reason,
        fingerprint: fingerprint.hash,
        algorithm: fingerprint.algorithm,
        self_signed: validationResult.selfSigned
      }
    });

    // Reject if validation failed in production
    if (!validationResult.valid && this.productionMode) {
      throw new Error(`Certificate validation failed for peer ${peerId}: ${validationResult.reason}`);
    }

    // Store fingerprint for later verification
    this.dtlsFingerprints.set(peerId, fingerprint.hash);

    // Generate SRTP keys if key manager is enabled
    if (this.srtpKeyManager) {
      const keyMaterial = await this.srtpKeyManager.generateKeyMaterial(peerId);

      await this.logToWitness({
        event: 'webrtc_session_established',
        agent_id: this.agentId,
        peer_id: peerId,
        trace_id: this.currentTraceId,
        timestamp: new Date().toISOString(),
        metadata: {
          dtls_fingerprint: fingerprint.hash,
          srtp_key_id: keyMaterial.keyId,
          security_level: this.productionMode ? 'production' : 'development',
          ice_policy: this.iceTransportPolicy
        }
      });
    }
  }

  /**
   * Extract DTLS fingerprint from SDP
   */
  private extractDTLSFingerprint(sdp: string): { algorithm: string; hash: string } | null {
    // Match fingerprint line: a=fingerprint:sha-256 XX:XX:XX:...
    const fingerprintMatch = sdp.match(/a=fingerprint:(\S+)\s+([A-F0-9:]+)/i);

    if (!fingerprintMatch) {
      return null;
    }

    return {
      algorithm: fingerprintMatch[1],
      hash: fingerprintMatch[2]
    };
  }

  /**
   * Validate certificate properties
   */
  private async validateCertificate(
    fingerprint: { algorithm: string; hash: string },
    sdp: string
  ): Promise<{ valid: boolean; reason?: string; selfSigned?: boolean }> {
    // Check if certificate validation is enabled
    if (!this.enableCertValidation) {
      return { valid: true };
    }

    // Validate algorithm (should be SHA-256 or stronger)
    const weakAlgorithms = ['sha-1', 'md5'];
    if (weakAlgorithms.includes(fingerprint.algorithm.toLowerCase())) {
      return {
        valid: false,
        reason: `Weak hash algorithm: ${fingerprint.algorithm}`
      };
    }

    // Check for self-signed certificate indicators in SDP
    // In WebRTC, certificates are typically self-signed, but we can check for validity
    const isSelfSigned = this.isCertificateSelfSigned(sdp);

    // In production mode, reject self-signed certs if not allowed
    if (isSelfSigned && !this.allowSelfSignedCerts) {
      return {
        valid: false,
        reason: 'Self-signed certificates not allowed in production mode',
        selfSigned: true
      };
    }

    // Validate fingerprint format
    const fingerprintRegex = /^([A-F0-9]{2}:){31}[A-F0-9]{2}$/i;
    if (fingerprint.algorithm.toLowerCase() === 'sha-256' && !fingerprintRegex.test(fingerprint.hash)) {
      return {
        valid: false,
        reason: 'Invalid SHA-256 fingerprint format'
      };
    }

    return {
      valid: true,
      selfSigned: isSelfSigned
    };
  }

  /**
   * Check if certificate is self-signed (heuristic)
   */
  private isCertificateSelfSigned(sdp: string): boolean {
    // In WebRTC, certificates are typically self-signed
    // We use a heuristic: check if there's no certificate chain in the SDP
    // This is a simplified check - in production, you'd examine the actual certificate

    // For now, assume all WebRTC certs are self-signed unless proven otherwise
    // Real implementation would parse certificate from DTLS handshake
    return true;
  }

  /**
   * Get DTLS fingerprint for peer
   */
  getDTLSFingerprint(peerId: string): string | undefined {
    return this.dtlsFingerprints.get(peerId);
  }

  /**
   * Get SRTP key manager
   */
  getSRTPKeyManager(): SRTPKeyManager | undefined {
    return this.srtpKeyManager;
  }

  /**
   * Manually rotate SRTP keys for a peer
   */
  async rotateSRTPKeys(peerId: string): Promise<void> {
    if (!this.srtpKeyManager) {
      throw new Error('SRTP key manager not enabled');
    }

    await this.srtpKeyManager.rotateKey(peerId, 'manual');
  }

  /**
   * Get security configuration
   */
  getSecurityConfig(): {
    productionMode: boolean;
    iceTransportPolicy: 'all' | 'relay';
    allowSelfSignedCerts: boolean;
    enableCertValidation: boolean;
    srtpKeyRotationEnabled: boolean;
  } {
    return {
      productionMode: this.productionMode,
      iceTransportPolicy: this.iceTransportPolicy,
      allowSelfSignedCerts: this.allowSelfSignedCerts,
      enableCertValidation: this.enableCertValidation,
      srtpKeyRotationEnabled: this.srtpKeyManager !== undefined
    };
  }

  /**
   * Cleanup all security resources
   */
  async cleanupSecurity(): Promise<void> {
    // Cleanup SRTP key manager
    if (this.srtpKeyManager) {
      await this.srtpKeyManager.shutdown();
    }

    // Clear DTLS fingerprints
    this.dtlsFingerprints.clear();
  }
}
