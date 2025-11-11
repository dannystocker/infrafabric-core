/**
 * WebRTC Agent Mesh with Bandwidth Adaptation
 *
 * Extends IFAgentWebRTC with bandwidth adaptation capabilities.
 * This wrapper integrates BandwidthAdapter with the WebRTC agent mesh.
 *
 * Usage:
 * ```typescript
 * const agent = new IFAgentWebRTCWithBandwidth({
 *   agentId: 'agent-1',
 *   bandwidthConfig: {
 *     bufferThreshold: 1024 * 1024, // 1MB
 *     checkIntervalMs: 100
 *   }
 * });
 * ```
 */

import { IFAgentWebRTC, IFWebRTCConfig, IFMessage, WitnessEvent } from './webrtc-agent-mesh';
import { BandwidthAdapter, QualityMode, BandwidthConfig, BandwidthStats } from './bandwidth-adapter';

/**
 * Extended configuration with bandwidth adaptation
 */
export interface IFWebRTCConfigWithBandwidth extends IFWebRTCConfig {
  bandwidthConfig?: Partial<BandwidthConfig>;
  enableBandwidthAdaptation?: boolean; // Default: true
}

/**
 * WebRTC Agent Mesh with Bandwidth Adaptation
 */
export class IFAgentWebRTCWithBandwidth extends IFAgentWebRTC {
  private bandwidthAdapter?: BandwidthAdapter;
  private originalSendMethod: (peerId: string, message: IFMessage) => Promise<void>;

  constructor(config: IFWebRTCConfigWithBandwidth) {
    super(config);

    // Initialize bandwidth adapter if enabled
    if (config.enableBandwidthAdaptation !== false) {
      this.bandwidthAdapter = new BandwidthAdapter(
        config.agentId,
        config.bandwidthConfig,
        config.witnessLogger,
        this.getCurrentTraceId()
      );

      // Start monitoring
      this.bandwidthAdapter.startMonitoring();
    }

    // Store original send method
    this.originalSendMethod = this.sendIFMessage.bind(this);

    // Override sendIFMessage to use bandwidth adaptation
    if (this.bandwidthAdapter) {
      this.sendIFMessage = this.sendIFMessageWithBandwidth.bind(this);
    }
  }

  /**
   * Override createOffer to register data channel with bandwidth adapter
   */
  async createOffer(peerId: string): Promise<RTCSessionDescriptionInit> {
    const offer = await super.createOffer(peerId);

    // Register data channel with bandwidth adapter after creation
    if (this.bandwidthAdapter) {
      // Wait a bit for data channel to be set up
      setTimeout(() => {
        const dataChannel = this.getDataChannel(peerId);
        if (dataChannel) {
          this.bandwidthAdapter!.registerDataChannel(peerId, dataChannel);
        }
      }, 100);
    }

    return offer;
  }

  /**
   * Send IFMessage with bandwidth adaptation
   */
  private async sendIFMessageWithBandwidth(peerId: string, message: IFMessage): Promise<void> {
    if (!this.bandwidthAdapter) {
      // Fallback to original send if bandwidth adapter not available
      return this.originalSendMethod(peerId, message);
    }

    // Use bandwidth adapter to queue/send message
    await this.bandwidthAdapter.queueMessage(
      peerId,
      message,
      async (msg: IFMessage) => {
        await this.originalSendMethod(peerId, msg);
      }
    );
  }

  /**
   * Override disconnectPeer to unregister from bandwidth adapter
   */
  async disconnectPeer(peerId: string): Promise<void> {
    if (this.bandwidthAdapter) {
      this.bandwidthAdapter.unregisterDataChannel(peerId);
    }
    await super.disconnectPeer(peerId);
  }

  /**
   * Override disconnect to stop bandwidth monitoring
   */
  async disconnect(): Promise<void> {
    if (this.bandwidthAdapter) {
      this.bandwidthAdapter.stopMonitoring();
    }
    await super.disconnect();
  }

  /**
   * Get current quality mode
   */
  getQualityMode(): QualityMode {
    return this.bandwidthAdapter?.getQualityMode() || QualityMode.HIGH;
  }

  /**
   * Get bandwidth statistics for all peers
   */
  getBandwidthStats(): BandwidthStats[] {
    return this.bandwidthAdapter?.getBandwidthStats() || [];
  }

  /**
   * Get bandwidth statistics for specific peer
   */
  getPeerBandwidthStats(peerId: string): BandwidthStats | undefined {
    return this.bandwidthAdapter?.getPeerBandwidthStats(peerId);
  }

  /**
   * Get bandwidth adapter instance (for advanced usage)
   */
  getBandwidthAdapter(): BandwidthAdapter | undefined {
    return this.bandwidthAdapter;
  }
}

/**
 * Export for convenience
 */
export { QualityMode, BandwidthConfig, BandwidthStats } from './bandwidth-adapter';
