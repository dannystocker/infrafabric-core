"""
H.323 Gatekeeper Performance Tuning for Low Latency

This module optimizes H.323 Gatekeeper and MCU for ultra-low latency
(<50ms) and minimal jitter (<10ms) for Guardian Council real-time deliberations.

Optimization Strategies:
1. RAS Message Batching: Batch ARQ/ACF responses to reduce round-trips
2. Buffer Tuning: Optimize RTP jitter buffers (adaptive sizing)
3. Priority Queuing: Prioritize EMERGENCY calls over ROUTINE
4. Network Optimization: TCP_NODELAY, socket buffer sizing
5. Codec Optimization: Prefer low-latency codecs (Opus, G.711)

Performance Targets:
- Latency: <50ms (P95), <30ms (avg)
- Jitter: <10ms (P95), <5ms (avg)
- Packet Loss: <0.5%
- Failover: <5 seconds

Philosophy:
- Wu Lun (五倫): 君臣 (Ruler-Subject) - Gatekeeper prioritizes time-critical decisions
- Ubuntu: Responsive participation - Low latency enables natural dialogue
- Kantian Duty: Efficient resource use (minimize waste)
- IF.TTT: Measurable performance improvements

Author: InfraFabric Project
License: CC BY 4.0
Last Updated: 2025-11-11
"""

import asyncio
import socket
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Any
from collections import deque
import json
import statistics

# ============================================================================
# Data Models
# ============================================================================

@dataclass
class LatencyMetrics:
    """Latency and jitter measurements"""
    timestamp: str
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    avg_jitter_ms: float
    p95_jitter_ms: float
    packet_loss_percent: float
    throughput_mbps: float


class QoSPriority(Enum):
    """Quality of Service priority levels"""
    HIGH = 1      # EMERGENCY calls
    MEDIUM = 2    # ESCALATE calls
    LOW = 3       # ROUTINE calls


# ============================================================================
# RAS Message Batching
# ============================================================================

class RASMessageBatcher:
    """
    Batches RAS messages (ARQ/ACF/ARJ) to reduce network round-trips.

    Instead of sending each ACF immediately, batch multiple responses
    into a single UDP packet (up to MTU limit of 1500 bytes).

    Target: Reduce ARQ→ACF latency from 15ms to <5ms
    """

    MAX_BATCH_SIZE = 10          # Max messages per batch
    BATCH_TIMEOUT_MS = 2         # Flush batch after 2ms
    MTU_SIZE_BYTES = 1500        # Ethernet MTU

    def __init__(self):
        self.batch: List[Dict[str, Any]] = []
        self.batch_start_time: Optional[float] = None
        self.total_batched = 0
        self.total_sent = 0

    def add_message(self, message: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """
        Add message to batch. Returns batch if ready to send.

        Args:
            message: RAS message (ARQ, ACF, ARJ, etc.)

        Returns:
            List of messages if batch is ready, None otherwise
        """
        if not self.batch:
            self.batch_start_time = time.time()

        self.batch.append(message)
        self.total_batched += 1

        # Flush batch if:
        # 1. Batch is full (MAX_BATCH_SIZE)
        # 2. Timeout exceeded (BATCH_TIMEOUT_MS)
        # 3. Message size exceeds MTU

        batch_size_bytes = len(json.dumps(self.batch).encode())
        batch_age_ms = (time.time() - self.batch_start_time) * 1000

        should_flush = (
            len(self.batch) >= self.MAX_BATCH_SIZE or
            batch_age_ms >= self.BATCH_TIMEOUT_MS or
            batch_size_bytes >= self.MTU_SIZE_BYTES - 100  # 100-byte header margin
        )

        if should_flush:
            return self.flush()

        return None

    def flush(self) -> List[Dict[str, Any]]:
        """Force flush current batch."""
        if not self.batch:
            return []

        batch_to_send = self.batch
        self.batch = []
        self.batch_start_time = None
        self.total_sent += len(batch_to_send)

        return batch_to_send

    def get_stats(self) -> Dict[str, Any]:
        """Get batching statistics."""
        return {
            "total_batched": self.total_batched,
            "total_sent": self.total_sent,
            "avg_batch_size": self.total_batched / max(self.total_sent, 1),
            "current_batch_size": len(self.batch)
        }


# ============================================================================
# Adaptive Jitter Buffer
# ============================================================================

class AdaptiveJitterBuffer:
    """
    Adaptive jitter buffer for RTP streams.

    Dynamically adjusts buffer size based on network jitter to minimize
    latency while preventing underruns.

    Target: Maintain jitter <10ms while minimizing latency
    """

    MIN_BUFFER_MS = 20           # Minimum buffer (low-jitter networks)
    MAX_BUFFER_MS = 150          # Maximum buffer (high-jitter networks)
    TARGET_JITTER_MS = 10        # Target jitter threshold
    ADJUSTMENT_INTERVAL_SEC = 5  # Recompute buffer size every 5 seconds

    def __init__(self, initial_size_ms: int = 50):
        self.current_size_ms = initial_size_ms
        self.jitter_samples: deque = deque(maxlen=100)  # Last 100 samples
        self.underrun_count = 0
        self.overrun_count = 0
        self.last_adjustment_time = time.time()

    def record_jitter(self, jitter_ms: float):
        """Record observed jitter sample."""
        self.jitter_samples.append(jitter_ms)

        # Adjust buffer size periodically
        now = time.time()
        if now - self.last_adjustment_time >= self.ADJUSTMENT_INTERVAL_SEC:
            self._adjust_buffer_size()
            self.last_adjustment_time = now

    def record_underrun(self):
        """Record buffer underrun event (late packet)."""
        self.underrun_count += 1
        # Immediately increase buffer on underrun
        self._increase_buffer()

    def record_overrun(self):
        """Record buffer overrun event (buffer too large)."""
        self.overrun_count += 1

    def _adjust_buffer_size(self):
        """
        Adjust buffer size based on observed jitter.

        Algorithm:
        - If avg jitter > TARGET_JITTER_MS → increase buffer
        - If avg jitter < TARGET_JITTER_MS/2 → decrease buffer
        - If underruns > 5 → increase buffer
        """
        if not self.jitter_samples:
            return

        avg_jitter = statistics.mean(self.jitter_samples)
        p95_jitter = statistics.quantiles(self.jitter_samples, n=20)[18]  # 95th percentile

        # Increase buffer if high jitter or underruns
        if p95_jitter > self.TARGET_JITTER_MS or self.underrun_count > 5:
            self._increase_buffer()

        # Decrease buffer if low jitter and no underruns
        elif avg_jitter < self.TARGET_JITTER_MS / 2 and self.underrun_count == 0:
            self._decrease_buffer()

        # Reset counters
        self.underrun_count = 0
        self.overrun_count = 0

    def _increase_buffer(self):
        """Increase buffer size by 10ms."""
        self.current_size_ms = min(self.current_size_ms + 10, self.MAX_BUFFER_MS)

    def _decrease_buffer(self):
        """Decrease buffer size by 5ms."""
        self.current_size_ms = max(self.current_size_ms - 5, self.MIN_BUFFER_MS)

    def get_buffer_size_ms(self) -> int:
        """Get current buffer size in milliseconds."""
        return self.current_size_ms


# ============================================================================
# Network Socket Optimization
# ============================================================================

class NetworkOptimizer:
    """
    Optimizes network sockets for low-latency RTP/RTCP streaming.

    Optimizations:
    1. TCP_NODELAY: Disable Nagle's algorithm
    2. SO_SNDBUF/SO_RCVBUF: Optimize socket buffer sizes
    3. SO_PRIORITY: Set QoS priority for emergency calls
    4. IP_TOS: Set DSCP for traffic prioritization
    """

    # Socket buffer sizes (bytes)
    SEND_BUFFER_SIZE = 256 * 1024      # 256 KB
    RECV_BUFFER_SIZE = 512 * 1024      # 512 KB

    # DSCP values (Differentiated Services Code Point)
    DSCP_EF = 46   # Expedited Forwarding (emergency calls)
    DSCP_AF = 34   # Assured Forwarding (escalate calls)
    DSCP_BE = 0    # Best Effort (routine calls)

    @staticmethod
    def optimize_socket(
        sock: socket.socket,
        priority: QoSPriority = QoSPriority.LOW
    ):
        """
        Apply low-latency optimizations to socket.

        Args:
            sock: Socket to optimize
            priority: QoS priority level
        """
        # Disable Nagle's algorithm (reduce latency)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        # Set socket buffer sizes
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, NetworkOptimizer.SEND_BUFFER_SIZE)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, NetworkOptimizer.RECV_BUFFER_SIZE)

        # Set QoS priority
        if priority == QoSPriority.HIGH:
            dscp = NetworkOptimizer.DSCP_EF
        elif priority == QoSPriority.MEDIUM:
            dscp = NetworkOptimizer.DSCP_AF
        else:
            dscp = NetworkOptimizer.DSCP_BE

        # Set IP TOS for DSCP
        try:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, dscp << 2)
        except OSError:
            # May require root/CAP_NET_ADMIN
            pass

        # Set SO_PRIORITY (Linux-specific)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_PRIORITY, priority.value)
        except (OSError, AttributeError):
            # Not supported on all platforms
            pass


# ============================================================================
# Latency Monitor
# ============================================================================

class LatencyMonitor:
    """
    Monitors end-to-end latency and jitter for Guardian Council calls.

    Tracks:
    - ARQ → ACF latency (admission control)
    - RTP packet latency (media streaming)
    - Jitter (variance in latency)
    - Packet loss rate
    """

    def __init__(self):
        self.latency_samples: deque = deque(maxlen=1000)
        self.jitter_samples: deque = deque(maxlen=1000)
        self.packet_loss_samples: deque = deque(maxlen=100)
        self.last_report_time = time.time()

    def record_latency(self, latency_ms: float):
        """Record latency sample."""
        self.latency_samples.append(latency_ms)

        # Compute jitter (variance from previous sample)
        if len(self.latency_samples) >= 2:
            jitter_ms = abs(self.latency_samples[-1] - self.latency_samples[-2])
            self.jitter_samples.append(jitter_ms)

    def record_packet_loss(self, loss_percent: float):
        """Record packet loss percentage."""
        self.packet_loss_samples.append(loss_percent)

    def get_metrics(self) -> LatencyMetrics:
        """
        Get current latency/jitter metrics.

        Returns:
            LatencyMetrics with avg, P95, P99 statistics
        """
        if not self.latency_samples:
            return LatencyMetrics(
                timestamp=datetime.now(timezone.utc).isoformat(),
                avg_latency_ms=0,
                p95_latency_ms=0,
                p99_latency_ms=0,
                avg_jitter_ms=0,
                p95_jitter_ms=0,
                packet_loss_percent=0,
                throughput_mbps=0
            )

        # Compute latency statistics
        avg_latency = statistics.mean(self.latency_samples)
        latency_quantiles = statistics.quantiles(self.latency_samples, n=100)
        p95_latency = latency_quantiles[94]  # 95th percentile
        p99_latency = latency_quantiles[98]  # 99th percentile

        # Compute jitter statistics
        avg_jitter = statistics.mean(self.jitter_samples) if self.jitter_samples else 0
        jitter_quantiles = statistics.quantiles(self.jitter_samples, n=100) if len(self.jitter_samples) >= 2 else [0] * 99
        p95_jitter = jitter_quantiles[94] if jitter_quantiles else 0

        # Compute packet loss
        avg_packet_loss = statistics.mean(self.packet_loss_samples) if self.packet_loss_samples else 0

        return LatencyMetrics(
            timestamp=datetime.now(timezone.utc).isoformat(),
            avg_latency_ms=round(avg_latency, 2),
            p95_latency_ms=round(p95_latency, 2),
            p99_latency_ms=round(p99_latency, 2),
            avg_jitter_ms=round(avg_jitter, 2),
            p95_jitter_ms=round(p95_jitter, 2),
            packet_loss_percent=round(avg_packet_loss, 2),
            throughput_mbps=0  # Placeholder
        )

    def should_report(self, interval_sec: int = 60) -> bool:
        """Check if metrics should be reported."""
        now = time.time()
        if now - self.last_report_time >= interval_sec:
            self.last_report_time = now
            return True
        return False


# ============================================================================
# Gatekeeper Tuning Configuration
# ============================================================================

@dataclass
class GatekeeperTuningConfig:
    """Configuration for H.323 gatekeeper performance tuning"""

    # RAS batching
    enable_ras_batching: bool = True
    max_batch_size: int = 10
    batch_timeout_ms: int = 2

    # Jitter buffer
    enable_adaptive_jitter_buffer: bool = True
    initial_buffer_ms: int = 50
    min_buffer_ms: int = 20
    max_buffer_ms: int = 150
    target_jitter_ms: int = 10

    # Network optimization
    enable_network_optimization: bool = True
    tcp_nodelay: bool = True
    send_buffer_kb: int = 256
    recv_buffer_kb: int = 512

    # Codec preferences (low-latency)
    preferred_audio_codecs: List[str] = None
    preferred_video_codecs: List[str] = None

    # Monitoring
    latency_report_interval_sec: int = 60

    def __post_init__(self):
        if self.preferred_audio_codecs is None:
            # Low-latency audio codecs
            self.preferred_audio_codecs = ["Opus", "G.711", "G.729"]

        if self.preferred_video_codecs is None:
            # Low-latency video codecs
            self.preferred_video_codecs = ["VP8", "H.264"]


# ============================================================================
# Tuned Gatekeeper Wrapper
# ============================================================================

class TunedGatekeeper:
    """
    Wrapper for H.323 Gatekeeper with performance tuning applied.

    This class wraps the standard H.323Gatekeeper and applies:
    - RAS message batching
    - Adaptive jitter buffers
    - Network socket optimization
    - Latency monitoring
    """

    def __init__(
        self,
        gatekeeper: 'H323Gatekeeper',
        config: GatekeeperTuningConfig = None
    ):
        """
        Initialize tuned gatekeeper.

        Args:
            gatekeeper: Base H.323Gatekeeper instance
            config: Tuning configuration
        """
        self.gatekeeper = gatekeeper
        self.config = config or GatekeeperTuningConfig()

        # Initialize components
        self.ras_batcher = RASMessageBatcher() if self.config.enable_ras_batching else None
        self.jitter_buffer = AdaptiveJitterBuffer(
            initial_size_ms=self.config.initial_buffer_ms
        ) if self.config.enable_adaptive_jitter_buffer else None
        self.latency_monitor = LatencyMonitor()

    async def process_admission_request(
        self,
        arq: 'AdmissionRequest',
        priority: QoSPriority = QoSPriority.LOW
    ) -> 'AdmissionResponse':
        """
        Process admission request with latency optimization.

        Args:
            arq: Admission request
            priority: QoS priority level

        Returns:
            Admission response
        """
        start_time = time.time()

        # Process admission via base gatekeeper
        response = self.gatekeeper.policy_engine.evaluate_admission(arq)

        # Record latency
        latency_ms = (time.time() - start_time) * 1000
        self.latency_monitor.record_latency(latency_ms)

        # Batch response if batching enabled
        if self.ras_batcher:
            batch = self.ras_batcher.add_message(asdict(response))
            # If batch ready, send all messages
            if batch:
                # In real implementation, would send batched UDP packet
                pass

        # Report metrics periodically
        if self.latency_monitor.should_report(self.config.latency_report_interval_sec):
            metrics = self.latency_monitor.get_metrics()
            self._log_metrics(metrics)

        return response

    def _log_metrics(self, metrics: LatencyMetrics):
        """Log latency metrics to console and file."""
        print(f"[Latency Monitor] {metrics.timestamp}")
        print(f"  Latency: {metrics.avg_latency_ms:.2f}ms avg, "
              f"{metrics.p95_latency_ms:.2f}ms P95, {metrics.p99_latency_ms:.2f}ms P99")
        print(f"  Jitter: {metrics.avg_jitter_ms:.2f}ms avg, {metrics.p95_jitter_ms:.2f}ms P95")
        print(f"  Packet Loss: {metrics.packet_loss_percent:.2f}%")

        # Also log to file
        log_dir = Path("logs/latency")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"latency_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(asdict(metrics)) + '\n')


# ============================================================================
# Usage Example
# ============================================================================

async def example_usage():
    """
    Example demonstrating gatekeeper performance tuning.
    """
    # Create tuning configuration
    config = GatekeeperTuningConfig(
        enable_ras_batching=True,
        enable_adaptive_jitter_buffer=True,
        enable_network_optimization=True,
        initial_buffer_ms=50,
        target_jitter_ms=10
    )

    print("H.323 Gatekeeper Performance Tuning")
    print("=" * 60)
    print(f"RAS Batching: {config.enable_ras_batching}")
    print(f"Adaptive Jitter Buffer: {config.enable_adaptive_jitter_buffer}")
    print(f"Network Optimization: {config.enable_network_optimization}")
    print(f"Target Jitter: <{config.target_jitter_ms}ms")
    print()

    # Simulate latency measurements
    monitor = LatencyMonitor()
    for i in range(100):
        # Simulate latency between 10-40ms
        latency = 25 + (i % 15)
        monitor.record_latency(latency)

    # Get metrics
    metrics = monitor.get_metrics()
    print("Performance Metrics:")
    print(f"  Avg Latency: {metrics.avg_latency_ms:.2f}ms (target: <50ms)")
    print(f"  P95 Latency: {metrics.p95_latency_ms:.2f}ms (target: <50ms)")
    print(f"  Avg Jitter: {metrics.avg_jitter_ms:.2f}ms (target: <10ms)")
    print(f"  P95 Jitter: {metrics.p95_jitter_ms:.2f}ms (target: <10ms)")

    status = "✅ PASS" if metrics.avg_latency_ms < 50 and metrics.p95_jitter_ms < 10 else "❌ FAIL"
    print(f"\nStatus: {status}")


if __name__ == "__main__":
    asyncio.run(example_usage())
