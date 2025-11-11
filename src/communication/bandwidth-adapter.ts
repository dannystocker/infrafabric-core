/**
 * Bandwidth Adaptation for WebRTC Agent Mesh
 *
 * Monitors DataChannel bufferedAmount and adapts message throughput
 * to prevent congestion in degraded network conditions.
 *
 * Features:
 * - Real-time buffer monitoring
 * - Three quality modes: HIGH, MEDIUM, LOW
 * - Adaptive message batching
 * - IF.witness logging for bandwidth events
 *
 * Performance Strategy:
 * - HIGH: No batching, immediate send (0ms delay)
 * - MEDIUM: Moderate batching (50ms delay)
 * - LOW: Aggressive batching (200ms delay)
 *
 * Thresholds:
 * - HIGH → MEDIUM: 512KB buffered
 * - MEDIUM → LOW: 1MB buffered
 * - LOW → MEDIUM: 256KB buffered (improvement)
 * - MEDIUM → HIGH: 128KB buffered (improvement)
 */

import { IFMessage, WitnessEvent } from './webrtc-agent-mesh';

/**
 * Quality modes for bandwidth adaptation
 */
export enum QualityMode {
  HIGH = 'HIGH',     // No throttling, full message rate
  MEDIUM = 'MEDIUM', // Moderate throttling, reduced message rate
  LOW = 'LOW'        // Aggressive throttling, minimal message rate
}

/**
 * Bandwidth adaptation configuration
 */
export interface BandwidthConfig {
  // Buffer threshold in bytes (default: 1MB)
  bufferThreshold: number;
  // Check interval in milliseconds (default: 100ms)
  checkIntervalMs: number;
  // Quality mode thresholds
  thresholds: {
    highToMedium: number;  // bytes (default: 512KB)
    mediumToLow: number;   // bytes (default: 1MB)
    lowToMedium: number;   // bytes (default: 256KB)
    mediumToHigh: number;  // bytes (default: 128KB)
  };
  // Message batching delays per quality mode (ms)
  batchDelays: {
    [QualityMode.HIGH]: number;
    [QualityMode.MEDIUM]: number;
    [QualityMode.LOW]: number;
  };
}

/**
 * Default bandwidth configuration
 */
export const DEFAULT_BANDWIDTH_CONFIG: BandwidthConfig = {
  bufferThreshold: 1024 * 1024, // 1MB
  checkIntervalMs: 100,
  thresholds: {
    highToMedium: 512 * 1024,   // 512KB
    mediumToLow: 1024 * 1024,   // 1MB
    lowToMedium: 256 * 1024,    // 256KB
    mediumToHigh: 128 * 1024    // 128KB
  },
  batchDelays: {
    [QualityMode.HIGH]: 0,      // No delay
    [QualityMode.MEDIUM]: 50,   // 50ms delay
    [QualityMode.LOW]: 200      // 200ms delay
  }
};

/**
 * Bandwidth statistics for a peer
 */
export interface BandwidthStats {
  peerId: string;
  bufferedAmount: number;
  qualityMode: QualityMode;
  queuedMessages: number;
  lastQualityChange?: number;
}

/**
 * Bandwidth Adapter
 *
 * Monitors DataChannel buffer and adapts message sending rate
 */
export class BandwidthAdapter {
  private agentId: string;
  private config: BandwidthConfig;
  private currentQualityMode: QualityMode = QualityMode.HIGH;
  private lastQualityChange: number = Date.now();

  // Message queues: peer_id -> IFMessage[]
  private messageQueues: Map<string, IFMessage[]> = new Map();

  // Batch timers: peer_id -> timeout handle
  private batchTimers: Map<string, NodeJS.Timeout> = new Map();

  // Monitor interval
  private monitorInterval?: NodeJS.Timeout;

  // Data channels for monitoring (peer_id -> RTCDataChannel)
  private dataChannels: Map<string, RTCDataChannel> = new Map();

  // IF.witness logger
  private witnessLogger?: (event: WitnessEvent) => Promise<void>;
  private currentTraceId: string;

  constructor(
    agentId: string,
    config: Partial<BandwidthConfig> = {},
    witnessLogger?: (event: WitnessEvent) => Promise<void>,
    traceId?: string
  ) {
    this.agentId = agentId;
    this.config = { ...DEFAULT_BANDWIDTH_CONFIG, ...config };
    this.witnessLogger = witnessLogger;
    this.currentTraceId = traceId || this.generateTraceId();
  }

  /**
   * Register data channel for monitoring
   */
  registerDataChannel(peerId: string, dataChannel: RTCDataChannel): void {
    this.dataChannels.set(peerId, dataChannel);
    this.messageQueues.set(peerId, []);
  }

  /**
   * Unregister data channel
   */
  unregisterDataChannel(peerId: string): void {
    // Flush any queued messages
    this.flushQueue(peerId);

    // Clear batch timer
    const timer = this.batchTimers.get(peerId);
    if (timer) {
      clearTimeout(timer);
      this.batchTimers.delete(peerId);
    }

    // Remove from maps
    this.dataChannels.delete(peerId);
    this.messageQueues.delete(peerId);
  }

  /**
   * Start bandwidth monitoring
   */
  startMonitoring(): void {
    if (this.monitorInterval) {
      return; // Already monitoring
    }

    this.monitorInterval = setInterval(() => {
      this.monitorBandwidth();
    }, this.config.checkIntervalMs);
  }

  /**
   * Stop bandwidth monitoring
   */
  stopMonitoring(): void {
    if (this.monitorInterval) {
      clearInterval(this.monitorInterval);
      this.monitorInterval = undefined;
    }

    // Flush all queues
    for (const peerId of this.messageQueues.keys()) {
      this.flushQueue(peerId);
    }

    // Clear all timers
    for (const timer of this.batchTimers.values()) {
      clearTimeout(timer);
    }
    this.batchTimers.clear();
  }

  /**
   * Queue message for sending (with bandwidth adaptation)
   */
  async queueMessage(
    peerId: string,
    message: IFMessage,
    sendImmediate: (msg: IFMessage) => Promise<void>
  ): Promise<void> {
    const batchDelay = this.config.batchDelays[this.currentQualityMode];

    if (batchDelay === 0) {
      // HIGH quality: send immediately
      await sendImmediate(message);
      return;
    }

    // Queue message for batching
    const queue = this.messageQueues.get(peerId);
    if (!queue) {
      console.warn(`No message queue for peer ${peerId}`);
      await sendImmediate(message);
      return;
    }

    queue.push(message);

    // Clear existing timer
    const existingTimer = this.batchTimers.get(peerId);
    if (existingTimer) {
      clearTimeout(existingTimer);
    }

    // Set new batch timer
    const timer = setTimeout(async () => {
      await this.flushQueue(peerId, sendImmediate);
    }, batchDelay);

    this.batchTimers.set(peerId, timer);
  }

  /**
   * Flush message queue for peer
   */
  private async flushQueue(
    peerId: string,
    sendImmediate?: (msg: IFMessage) => Promise<void>
  ): Promise<void> {
    const queue = this.messageQueues.get(peerId);
    if (!queue || queue.length === 0) {
      return;
    }

    if (!sendImmediate) {
      // Just clear the queue if no sender provided
      queue.length = 0;
      return;
    }

    // Send all queued messages
    const messages = [...queue];
    queue.length = 0; // Clear queue

    for (const message of messages) {
      try {
        await sendImmediate(message);
      } catch (error) {
        console.error(`Failed to send queued message to ${peerId}:`, error);
      }
    }

    // Clear timer
    this.batchTimers.delete(peerId);
  }

  /**
   * Monitor bandwidth and adapt quality mode
   */
  private async monitorBandwidth(): Promise<void> {
    let maxBufferedAmount = 0;
    let totalBufferedAmount = 0;
    let channelCount = 0;

    // Check all data channels
    for (const [peerId, dataChannel] of this.dataChannels) {
      if (dataChannel.readyState === 'open') {
        const buffered = dataChannel.bufferedAmount;
        maxBufferedAmount = Math.max(maxBufferedAmount, buffered);
        totalBufferedAmount += buffered;
        channelCount++;
      }
    }

    if (channelCount === 0) {
      return; // No channels to monitor
    }

    const avgBufferedAmount = totalBufferedAmount / channelCount;
    const newQualityMode = this.determineQualityMode(maxBufferedAmount, avgBufferedAmount);

    // Update quality mode if changed
    if (newQualityMode !== this.currentQualityMode) {
      const oldMode = this.currentQualityMode;
      this.currentQualityMode = newQualityMode;
      this.lastQualityChange = Date.now();

      await this.logToWitness({
        event: 'bandwidth_quality_changed',
        agent_id: this.agentId,
        trace_id: this.currentTraceId,
        timestamp: new Date().toISOString(),
        metadata: {
          old_mode: oldMode,
          new_mode: newQualityMode,
          max_buffered: maxBufferedAmount,
          avg_buffered: avgBufferedAmount,
          channel_count: channelCount,
          threshold_high_to_medium: this.config.thresholds.highToMedium,
          threshold_medium_to_low: this.config.thresholds.mediumToLow
        }
      });
    }
  }

  /**
   * Determine quality mode based on buffer levels
   */
  private determineQualityMode(maxBuffered: number, avgBuffered: number): QualityMode {
    const thresholds = this.config.thresholds;

    switch (this.currentQualityMode) {
      case QualityMode.HIGH:
        // Degrade to MEDIUM if buffer is high
        if (maxBuffered > thresholds.highToMedium) {
          return QualityMode.MEDIUM;
        }
        return QualityMode.HIGH;

      case QualityMode.MEDIUM:
        // Degrade to LOW if buffer is very high
        if (maxBuffered > thresholds.mediumToLow) {
          return QualityMode.LOW;
        }
        // Upgrade to HIGH if buffer is low
        if (maxBuffered < thresholds.mediumToHigh && avgBuffered < thresholds.mediumToHigh) {
          return QualityMode.HIGH;
        }
        return QualityMode.MEDIUM;

      case QualityMode.LOW:
        // Upgrade to MEDIUM if buffer is reduced
        if (maxBuffered < thresholds.lowToMedium && avgBuffered < thresholds.lowToMedium) {
          return QualityMode.MEDIUM;
        }
        return QualityMode.LOW;

      default:
        return QualityMode.HIGH;
    }
  }

  /**
   * Get current quality mode
   */
  getQualityMode(): QualityMode {
    return this.currentQualityMode;
  }

  /**
   * Get bandwidth statistics for all peers
   */
  getBandwidthStats(): BandwidthStats[] {
    const stats: BandwidthStats[] = [];

    for (const [peerId, dataChannel] of this.dataChannels) {
      if (dataChannel.readyState === 'open') {
        stats.push({
          peerId,
          bufferedAmount: dataChannel.bufferedAmount,
          qualityMode: this.currentQualityMode,
          queuedMessages: this.messageQueues.get(peerId)?.length || 0,
          lastQualityChange: this.lastQualityChange
        });
      }
    }

    return stats;
  }

  /**
   * Get bandwidth statistics for specific peer
   */
  getPeerBandwidthStats(peerId: string): BandwidthStats | undefined {
    const dataChannel = this.dataChannels.get(peerId);
    if (!dataChannel || dataChannel.readyState !== 'open') {
      return undefined;
    }

    return {
      peerId,
      bufferedAmount: dataChannel.bufferedAmount,
      qualityMode: this.currentQualityMode,
      queuedMessages: this.messageQueues.get(peerId)?.length || 0,
      lastQualityChange: this.lastQualityChange
    };
  }

  /**
   * Set trace ID
   */
  setTraceId(traceId: string): void {
    this.currentTraceId = traceId;
  }

  /**
   * Log to IF.witness
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
    return Array.from(bytes)
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }
}
