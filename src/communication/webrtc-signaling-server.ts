/**
 * WebRTC Signaling Server for IF.swarm
 *
 * Purpose:
 * - Relay SDP offers/answers between agents
 * - Relay ICE candidates
 * - Log all signaling events to IF.witness
 *
 * Philosophy:
 * - Transparent: All signaling visible and logged
 * - Traceable: Each SDP/ICE exchange tracked
 * - Trustworthy: Integrity verified through IF.witness
 */

import { WebSocketServer, WebSocket } from 'ws';
import { createHash } from 'crypto';

/**
 * Connected agent registry
 */
interface ConnectedAgent {
  agentId: string;
  ws: WebSocket;
  connectedAt: Date;
}

/**
 * Signaling message types
 */
interface SignalingMessage {
  type: 'register' | 'offer' | 'answer' | 'ice-candidate';
  agent_id?: string;
  from?: string;
  to?: string;
  offer?: RTCSessionDescriptionInit;
  answer?: RTCSessionDescriptionInit;
  candidate?: RTCIceCandidateInit;
}

/**
 * IF.witness event logger
 */
interface WitnessLogger {
  log(event: {
    event: string;
    timestamp: string;
    metadata?: Record<string, unknown>;
  }): Promise<void>;
}

/**
 * Signaling Server Configuration
 */
export interface SignalingServerConfig {
  port?: number;
  host?: string;
  witnessLogger?: WitnessLogger;
}

/**
 * WebRTC Signaling Server
 *
 * Implements WebSocket-based signaling for WebRTC peer connections:
 * 1. Agents register with their ID
 * 2. Server relays SDP offers/answers between agents
 * 3. Server relays ICE candidates
 * 4. All events logged to IF.witness
 */
export class WebRTCSignalingServer {
  private wss: WebSocketServer;
  private agents: Map<string, ConnectedAgent> = new Map();
  private witnessLogger?: WitnessLogger;
  private port: number;
  private host: string;

  constructor(config: SignalingServerConfig = {}) {
    this.port = config.port || 8443;
    this.host = config.host || '0.0.0.0';
    this.witnessLogger = config.witnessLogger;

    this.wss = new WebSocketServer({
      port: this.port,
      host: this.host
    });

    this.setupServer();
  }

  /**
   * Setup WebSocket server
   */
  private setupServer(): void {
    this.wss.on('connection', (ws: WebSocket) => {
      console.log(`New WebSocket connection`);

      ws.on('message', (data: Buffer) => {
        this.handleMessage(ws, data);
      });

      ws.on('close', () => {
        this.handleDisconnect(ws);
      });

      ws.on('error', (error) => {
        console.error('WebSocket error:', error);
      });
    });

    this.wss.on('listening', () => {
      console.log(`WebRTC Signaling Server listening on ${this.host}:${this.port}`);
      this.logToWitness({
        event: 'signaling_server_started',
        timestamp: new Date().toISOString(),
        metadata: {
          host: this.host,
          port: this.port
        }
      });
    });

    this.wss.on('error', (error) => {
      console.error('WebSocket server error:', error);
    });
  }

  /**
   * Handle incoming message
   */
  private async handleMessage(ws: WebSocket, data: Buffer): Promise<void> {
    try {
      const message: SignalingMessage = JSON.parse(data.toString());

      switch (message.type) {
        case 'register':
          await this.handleRegister(ws, message);
          break;

        case 'offer':
          await this.handleOffer(message);
          break;

        case 'answer':
          await this.handleAnswer(message);
          break;

        case 'ice-candidate':
          await this.handleIceCandidate(message);
          break;

        default:
          console.warn(`Unknown message type: ${message.type}`);
      }
    } catch (error) {
      console.error('Failed to handle message:', error);
      ws.send(JSON.stringify({
        type: 'error',
        message: String(error)
      }));
    }
  }

  /**
   * Handle agent registration
   */
  private async handleRegister(ws: WebSocket, message: SignalingMessage): Promise<void> {
    const agentId = message.agent_id;
    if (!agentId) {
      throw new Error('Missing agent_id in register message');
    }

    // Register agent
    this.agents.set(agentId, {
      agentId,
      ws,
      connectedAt: new Date()
    });

    console.log(`Agent registered: ${agentId}`);

    // Send confirmation
    ws.send(JSON.stringify({
      type: 'registered',
      agent_id: agentId,
      connected_agents: Array.from(this.agents.keys()).filter(id => id !== agentId)
    }));

    // Notify other agents
    this.broadcast({
      type: 'agent-joined',
      agent_id: agentId
    }, agentId);

    await this.logToWitness({
      event: 'agent_registered',
      timestamp: new Date().toISOString(),
      metadata: {
        agent_id: agentId,
        total_agents: this.agents.size
      }
    });
  }

  /**
   * Handle SDP offer
   */
  private async handleOffer(message: SignalingMessage): Promise<void> {
    const { from, to, offer } = message;
    if (!from || !to || !offer) {
      throw new Error('Invalid offer message');
    }

    const targetAgent = this.agents.get(to);
    if (!targetAgent) {
      throw new Error(`Agent ${to} not found`);
    }

    // Relay offer to target
    targetAgent.ws.send(JSON.stringify({
      type: 'offer',
      from,
      to,
      offer
    }));

    console.log(`Relayed offer: ${from} → ${to}`);

    await this.logToWitness({
      event: 'sdp_offer_relayed',
      timestamp: new Date().toISOString(),
      metadata: {
        from,
        to,
        sdp_hash: this.hashSDP(offer.sdp || ''),
        sdp_type: offer.type
      }
    });
  }

  /**
   * Handle SDP answer
   */
  private async handleAnswer(message: SignalingMessage): Promise<void> {
    const { from, to, answer } = message;
    if (!from || !to || !answer) {
      throw new Error('Invalid answer message');
    }

    const targetAgent = this.agents.get(to);
    if (!targetAgent) {
      throw new Error(`Agent ${to} not found`);
    }

    // Relay answer to target
    targetAgent.ws.send(JSON.stringify({
      type: 'answer',
      from,
      to,
      answer
    }));

    console.log(`Relayed answer: ${from} → ${to}`);

    await this.logToWitness({
      event: 'sdp_answer_relayed',
      timestamp: new Date().toISOString(),
      metadata: {
        from,
        to,
        sdp_hash: this.hashSDP(answer.sdp || ''),
        sdp_type: answer.type
      }
    });
  }

  /**
   * Handle ICE candidate
   */
  private async handleIceCandidate(message: SignalingMessage): Promise<void> {
    const { from, to, candidate } = message;
    if (!from || !to || !candidate) {
      throw new Error('Invalid ICE candidate message');
    }

    const targetAgent = this.agents.get(to);
    if (!targetAgent) {
      // Agent may have disconnected, silently ignore
      return;
    }

    // Relay ICE candidate to target
    targetAgent.ws.send(JSON.stringify({
      type: 'ice-candidate',
      from,
      to,
      candidate
    }));

    await this.logToWitness({
      event: 'ice_candidate_relayed',
      timestamp: new Date().toISOString(),
      metadata: {
        from,
        to,
        candidate: candidate.candidate
      }
    });
  }

  /**
   * Handle agent disconnect
   */
  private async handleDisconnect(ws: WebSocket): Promise<void> {
    // Find agent by WebSocket
    let disconnectedAgentId: string | undefined;
    for (const [agentId, agent] of this.agents.entries()) {
      if (agent.ws === ws) {
        disconnectedAgentId = agentId;
        this.agents.delete(agentId);
        break;
      }
    }

    if (disconnectedAgentId) {
      console.log(`Agent disconnected: ${disconnectedAgentId}`);

      // Notify other agents
      this.broadcast({
        type: 'agent-left',
        agent_id: disconnectedAgentId
      });

      await this.logToWitness({
        event: 'agent_disconnected',
        timestamp: new Date().toISOString(),
        metadata: {
          agent_id: disconnectedAgentId,
          total_agents: this.agents.size
        }
      });
    }
  }

  /**
   * Broadcast message to all agents except sender
   */
  private broadcast(message: any, excludeAgentId?: string): void {
    const messageStr = JSON.stringify(message);
    for (const [agentId, agent] of this.agents.entries()) {
      if (agentId !== excludeAgentId && agent.ws.readyState === WebSocket.OPEN) {
        agent.ws.send(messageStr);
      }
    }
  }

  /**
   * Hash SDP for logging
   */
  private hashSDP(sdp: string): string {
    return createHash('sha256').update(sdp).digest('hex').substring(0, 16);
  }

  /**
   * Log event to IF.witness
   */
  private async logToWitness(event: {
    event: string;
    timestamp: string;
    metadata?: Record<string, unknown>;
  }): Promise<void> {
    if (this.witnessLogger) {
      await this.witnessLogger.log(event);
    } else {
      // Default: console logging
      console.log(`[IF.witness] ${event.event}:`, event.metadata || {});
    }
  }

  /**
   * Get connected agents
   */
  getConnectedAgents(): string[] {
    return Array.from(this.agents.keys());
  }

  /**
   * Get server stats
   */
  getStats(): {
    totalAgents: number;
    agents: Array<{ agentId: string; connectedAt: string }>;
  } {
    return {
      totalAgents: this.agents.size,
      agents: Array.from(this.agents.values()).map(agent => ({
        agentId: agent.agentId,
        connectedAt: agent.connectedAt.toISOString()
      }))
    };
  }

  /**
   * Shutdown server
   */
  async shutdown(): Promise<void> {
    console.log('Shutting down signaling server...');

    // Close all connections
    for (const agent of this.agents.values()) {
      agent.ws.close();
    }
    this.agents.clear();

    // Close server
    return new Promise((resolve) => {
      this.wss.close(() => {
        console.log('Signaling server shut down');
        resolve();
      });
    });
  }
}

/**
 * Main entry point (if run directly)
 */
if (import.meta.url === `file://${process.argv[1]}`) {
  const server = new WebRTCSignalingServer({
    port: parseInt(process.env.PORT || '8443'),
    host: process.env.HOST || '0.0.0.0'
  });

  // Graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\nReceived SIGINT, shutting down...');
    await server.shutdown();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    console.log('\nReceived SIGTERM, shutting down...');
    await server.shutdown();
    process.exit(0);
  });
}
