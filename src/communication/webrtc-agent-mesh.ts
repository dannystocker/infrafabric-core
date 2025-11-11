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
 * WebRTC Peer Connection Configuration
 */
export interface IFWebRTCConfig {
  agentId: string;
  privateKey?: Uint8Array;
  publicKey?: Uint8Array;
  signalingServerUrl?: string;
  stunServers?: string[];
  witnessLogger?: (event: WitnessEvent) => Promise<void>;
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

  // Message handlers
  private messageHandlers: Set<(message: IFMessage) => void> = new Set();

  // IF.witness logger
  private witnessLogger?: (event: WitnessEvent) => Promise<void>;

  // Sequence number for outgoing messages
  private sequenceNum: number = 0;

  // Current trace ID
  private currentTraceId: string;

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

    // Configure ICE servers
    const defaultStunServers = config.stunServers || ['stun:stun.l.google.com:19302'];
    this.iceServers = defaultStunServers.map(url => ({ urls: url }));

    // IF.witness logger
    this.witnessLogger = config.witnessLogger;

    // Initialize trace ID
    this.currentTraceId = this.generateTraceId();
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

    const pc = new RTCPeerConnection({
      iceServers: this.iceServers
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
}
