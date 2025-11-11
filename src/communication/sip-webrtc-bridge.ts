/**
 * SIP-WebRTC Bridge for InfraFabric Session 4
 *
 * Purpose:
 * - Bridge interface between SIP sessions and WebRTC DataChannel
 * - Allow SIP session to escalate to WebRTC for real-time coordination
 * - Share evidence and artifacts between SIP and WebRTC layers
 *
 * Philosophy Grounding:
 * - Wu Lun (五倫): 兄弟 (Siblings) — SIP and WebRTC are parallel communication channels
 * - IF.ground: Observable artifacts (logged to IF.witness)
 * - IF.TTT: Traceable, Transparent, Trustworthy
 */

import { IFAgentWebRTC, IFMessage, WitnessEvent } from './webrtc-agent-mesh';

/**
 * SIP Session Interface (minimal subset for integration)
 */
export interface SIPSession {
  sessionId: string;
  callId: string;
  fromUri: string;
  toUri: string;
  state: 'initial' | 'establishing' | 'established' | 'terminating' | 'terminated';

  // SIP-specific methods
  accept(): Promise<void>;
  reject(reason?: string): Promise<void>;
  terminate(): Promise<void>;
  sendInfo(contentType: string, body: string): Promise<void>;
}

/**
 * Evidence artifact to share over WebRTC
 */
export interface EvidenceArtifact {
  id: string;
  type: 'document' | 'transcript' | 'reasoning' | 'citation' | 'analysis';
  source: string;
  timestamp: string;
  content: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

/**
 * Bridge configuration
 */
export interface SIPWebRTCBridgeConfig {
  webrtcAgent: IFAgentWebRTC;
  witnessLogger?: (event: WitnessEvent) => Promise<void>;
}

/**
 * SIP-WebRTC Bridge
 *
 * Bridges SIP sessions with WebRTC DataChannel for hybrid communication:
 * - SIP: Used for signaling and traditional voice/video
 * - WebRTC: Used for real-time agent coordination and evidence sharing
 */
export class SIPWebRTCBridge {
  private webrtcAgent: IFAgentWebRTC;
  private witnessLogger?: (event: WitnessEvent) => Promise<void>;

  // Track attached SIP sessions: sessionId -> SIPSession
  private attachedSessions: Map<string, SIPSession> = new Map();

  // Track session-to-peer mappings: sessionId -> peerId
  private sessionPeerMap: Map<string, string> = new Map();

  constructor(config: SIPWebRTCBridgeConfig) {
    this.webrtcAgent = config.webrtcAgent;
    this.witnessLogger = config.witnessLogger;
  }

  /**
   * Attach SIP session to WebRTC bridge
   *
   * Usage:
   *   const bridge = new SIPWebRTCBridge({ webrtcAgent });
   *   await bridge.attachSIPSession(sipSession, 'agent-legal');
   */
  async attachSIPSession(sipSession: SIPSession, peerId: string): Promise<void> {
    // Store session mapping
    this.attachedSessions.set(sipSession.sessionId, sipSession);
    this.sessionPeerMap.set(sipSession.sessionId, peerId);

    // Log to IF.witness
    await this.logToWitness({
      event: 'sip_session_attached',
      agent_id: this.webrtcAgent.getAgentId(),
      peer_id: peerId,
      trace_id: this.webrtcAgent.getCurrentTraceId(),
      timestamp: new Date().toISOString(),
      metadata: {
        session_id: sipSession.sessionId,
        call_id: sipSession.callId,
        from: sipSession.fromUri,
        to: sipSession.toUri,
        state: sipSession.state
      }
    });

    // Set up message handler for this peer
    this.webrtcAgent.onIFMessage((message: IFMessage) => {
      if (message.source === peerId) {
        this.handleWebRTCMessage(sipSession.sessionId, message);
      }
    });
  }

  /**
   * Detach SIP session from WebRTC bridge
   */
  async detachSIPSession(sessionId: string): Promise<void> {
    const session = this.attachedSessions.get(sessionId);
    const peerId = this.sessionPeerMap.get(sessionId);

    if (session && peerId) {
      await this.logToWitness({
        event: 'sip_session_detached',
        agent_id: this.webrtcAgent.getAgentId(),
        peer_id: peerId,
        trace_id: this.webrtcAgent.getCurrentTraceId(),
        timestamp: new Date().toISOString(),
        metadata: {
          session_id: sessionId,
          call_id: session.callId
        }
      });
    }

    this.attachedSessions.delete(sessionId);
    this.sessionPeerMap.delete(sessionId);
  }

  /**
   * Escalate SIP session to WebRTC DataChannel
   *
   * Establishes WebRTC connection if not already connected,
   * then notifies peer that communication is escalating to WebRTC.
   *
   * Usage:
   *   await bridge.escalateToWebRTC(sipSession.sessionId, {
   *     reason: 'Real-time evidence sharing required',
   *     urgency: 'high'
   *   });
   */
  async escalateToWebRTC(
    sessionId: string,
    options?: {
      reason?: string;
      urgency?: 'low' | 'medium' | 'high';
      metadata?: Record<string, unknown>;
    }
  ): Promise<void> {
    const session = this.attachedSessions.get(sessionId);
    const peerId = this.sessionPeerMap.get(sessionId);

    if (!session || !peerId) {
      throw new Error(`SIP session ${sessionId} not attached`);
    }

    // Check if WebRTC connection already established
    const isPeerReady = this.webrtcAgent.isPeerReady(peerId);

    if (!isPeerReady) {
      // Create WebRTC offer to establish connection
      await this.webrtcAgent.createOffer(peerId);

      // Wait for connection to be established (with timeout)
      await this.waitForPeerReady(peerId, 10000);
    }

    // Send escalation notification via WebRTC
    const escalationMessage: IFMessage = {
      id: this.generateMessageId(),
      timestamp: new Date().toISOString(),
      level: 2,
      source: this.webrtcAgent.getAgentId(),
      destination: peerId,
      version: '2.1',
      performative: 'inform',
      payload: {
        type: 'sip_escalation',
        session_id: sessionId,
        call_id: session.callId,
        reason: options?.reason || 'SIP session escalated to WebRTC',
        urgency: options?.urgency || 'medium',
        metadata: options?.metadata
      }
    };

    await this.webrtcAgent.sendIFMessage(peerId, escalationMessage);

    // Log to IF.witness
    await this.logToWitness({
      event: 'sip_escalated_to_webrtc',
      agent_id: this.webrtcAgent.getAgentId(),
      peer_id: peerId,
      trace_id: this.webrtcAgent.getCurrentTraceId(),
      timestamp: new Date().toISOString(),
      metadata: {
        session_id: sessionId,
        call_id: session.callId,
        reason: options?.reason,
        urgency: options?.urgency,
        was_already_connected: isPeerReady
      }
    });
  }

  /**
   * Share evidence artifact over WebRTC DataChannel
   *
   * Usage:
   *   await bridge.shareEvidence(sipSession.sessionId, {
   *     id: 'evidence-001',
   *     type: 'analysis',
   *     source: 'agent-finance',
   *     timestamp: new Date().toISOString(),
   *     content: {
   *       analysis: 'Market conditions favorable...',
   *       confidence: 0.87
   *     }
   *   });
   */
  async shareEvidence(sessionId: string, evidence: EvidenceArtifact): Promise<void> {
    const session = this.attachedSessions.get(sessionId);
    const peerId = this.sessionPeerMap.get(sessionId);

    if (!session || !peerId) {
      throw new Error(`SIP session ${sessionId} not attached`);
    }

    // Ensure WebRTC connection is ready
    const isPeerReady = this.webrtcAgent.isPeerReady(peerId);
    if (!isPeerReady) {
      throw new Error(`WebRTC connection to ${peerId} not ready. Call escalateToWebRTC() first.`);
    }

    // Create evidence-sharing message
    const evidenceMessage: IFMessage = {
      id: this.generateMessageId(),
      timestamp: new Date().toISOString(),
      level: 2,
      source: this.webrtcAgent.getAgentId(),
      destination: peerId,
      version: '2.1',
      performative: 'inform',
      payload: {
        type: 'evidence_artifact',
        evidence
      },
      citation_ids: [evidence.id]
    };

    await this.webrtcAgent.sendIFMessage(peerId, evidenceMessage);

    // Log to IF.witness
    await this.logToWitness({
      event: 'evidence_shared_via_webrtc',
      agent_id: this.webrtcAgent.getAgentId(),
      peer_id: peerId,
      trace_id: this.webrtcAgent.getCurrentTraceId(),
      timestamp: new Date().toISOString(),
      metadata: {
        session_id: sessionId,
        evidence_id: evidence.id,
        evidence_type: evidence.type,
        evidence_source: evidence.source
      }
    });
  }

  /**
   * Send custom message via WebRTC for SIP session
   */
  async sendMessage(sessionId: string, message: IFMessage): Promise<void> {
    const peerId = this.sessionPeerMap.get(sessionId);
    if (!peerId) {
      throw new Error(`SIP session ${sessionId} not attached`);
    }

    await this.webrtcAgent.sendIFMessage(peerId, message);
  }

  /**
   * Get WebRTC connection quality for SIP session
   */
  getConnectionQuality(sessionId: string) {
    const peerId = this.sessionPeerMap.get(sessionId);
    if (!peerId) {
      return undefined;
    }

    return this.webrtcAgent.getConnectionQuality(peerId);
  }

  /**
   * Check if WebRTC connection is ready for SIP session
   */
  isWebRTCReady(sessionId: string): boolean {
    const peerId = this.sessionPeerMap.get(sessionId);
    if (!peerId) {
      return false;
    }

    return this.webrtcAgent.isPeerReady(peerId);
  }

  /**
   * Get attached SIP sessions
   */
  getAttachedSessions(): Array<{ sessionId: string; peerId: string; session: SIPSession }> {
    const sessions: Array<{ sessionId: string; peerId: string; session: SIPSession }> = [];

    for (const [sessionId, session] of this.attachedSessions) {
      const peerId = this.sessionPeerMap.get(sessionId);
      if (peerId) {
        sessions.push({ sessionId, peerId, session });
      }
    }

    return sessions;
  }

  // ============ Private Methods ============

  /**
   * Handle incoming WebRTC message for SIP session
   */
  private async handleWebRTCMessage(sessionId: string, message: IFMessage): Promise<void> {
    const session = this.attachedSessions.get(sessionId);
    if (!session) {
      return;
    }

    // Log received message
    await this.logToWitness({
      event: 'webrtc_message_received_for_sip',
      agent_id: this.webrtcAgent.getAgentId(),
      peer_id: message.source,
      trace_id: message.traceId || this.webrtcAgent.getCurrentTraceId(),
      timestamp: new Date().toISOString(),
      metadata: {
        session_id: sessionId,
        message_id: message.id,
        performative: message.performative
      }
    });

    // Handle different message types
    const payloadType = (message.payload as any).type;

    switch (payloadType) {
      case 'sip_escalation':
        // Peer is requesting escalation
        console.log(`SIP session ${sessionId} escalation requested by peer`);
        break;

      case 'evidence_artifact':
        // Received evidence from peer
        const evidence = (message.payload as any).evidence as EvidenceArtifact;
        console.log(`Received evidence: ${evidence.id} (${evidence.type})`);
        break;

      default:
        // Generic message
        console.log(`Received WebRTC message for SIP session ${sessionId}:`, message);
    }
  }

  /**
   * Wait for WebRTC peer to be ready
   */
  private async waitForPeerReady(peerId: string, timeoutMs: number = 10000): Promise<void> {
    const startTime = Date.now();

    while (!this.webrtcAgent.isPeerReady(peerId)) {
      if (Date.now() - startTime > timeoutMs) {
        throw new Error(`Timeout waiting for WebRTC connection to ${peerId}`);
      }

      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }

  /**
   * Generate message ID
   */
  private generateMessageId(): string {
    return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Log to IF.witness
   */
  private async logToWitness(event: WitnessEvent): Promise<void> {
    if (this.witnessLogger) {
      await this.witnessLogger(event);
    } else {
      // Fallback to console logging
      console.log(`[IF.witness] ${event.event}:`, event.metadata || {});
    }
  }
}

/**
 * Example Usage for Session 4 (SIP)
 *
 * ```typescript
 * import { IFAgentWebRTC } from './webrtc-agent-mesh';
 * import { SIPWebRTCBridge } from './sip-webrtc-bridge';
 *
 * // Initialize WebRTC agent
 * const webrtcAgent = new IFAgentWebRTC({
 *   agentId: 'agent-finance',
 *   signalingServerUrl: 'ws://localhost:8443',
 *   turnServers: [{
 *     urls: 'turn:turn.example.com:3478',
 *     username: 'user',
 *     credential: 'pass'
 *   }]
 * });
 *
 * await webrtcAgent.connectToSignaling();
 *
 * // Create SIP-WebRTC bridge
 * const bridge = new SIPWebRTCBridge({
 *   webrtcAgent
 * });
 *
 * // When SIP session is established
 * const sipSession = await establishSIPSession(...);
 * await bridge.attachSIPSession(sipSession, 'agent-legal');
 *
 * // Escalate to WebRTC when real-time coordination needed
 * await bridge.escalateToWebRTC(sipSession.sessionId, {
 *   reason: 'Need to share real-time market analysis',
 *   urgency: 'high'
 * });
 *
 * // Share evidence over WebRTC
 * await bridge.shareEvidence(sipSession.sessionId, {
 *   id: 'evidence-market-001',
 *   type: 'analysis',
 *   source: 'agent-finance',
 *   timestamp: new Date().toISOString(),
 *   content: {
 *     market_conditions: 'bullish',
 *     confidence: 0.92,
 *     supporting_data: [...]
 *   }
 * });
 *
 * // Check connection quality
 * const quality = bridge.getConnectionQuality(sipSession.sessionId);
 * console.log('WebRTC quality:', quality);
 * ```
 */
