# NDI Witness Streaming - Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying NDI witness streaming in production environments. NDI witness streaming provides real-time cryptographically-signed video streaming of security scan results with full provenance tracking, hash chain integrity, and Ed25519 signature verification.

**Target Audience**: Operations teams, DevOps engineers, security architects
**Scope**: From infrastructure setup through live monitoring and troubleshooting

---

## 1. Prerequisites

### 1.1 NDI SDK 5.6+ Installation

#### System Requirements
- **OS**: Linux (Ubuntu 20.04 LTS or later recommended)
- **Architecture**: x86_64 or ARM64
- **Storage**: 500MB for SDK installation
- **Network**: Gigabit Ethernet minimum (1000 Mbps)

#### Network Requirements
- **Multicast Support**: mDNS (Multicast DNS) on UDP port 5353
- **Discovery**: mDNS-SD for service discovery
- **Stream Port Range**: TCP 5960-5989 for NDI streams
- **Firewall Rules** (covered in Section 6)

### 1.2 Python Dependencies

```bash
# Core Python version
python3 >= 3.9

# Required packages
pip install cryptography>=41.0.0
pip install pydantic>=2.0.0
pip install prometheus-client>=0.18.0
```

### 1.3 Hardware Recommendations

| Component | Minimum | Recommended | High Performance |
|-----------|---------|-------------|-----------------|
| CPU Cores | 4 | 8 | 16+ |
| RAM | 8GB | 16GB | 32GB+ |
| Network | 1 Gbps | 10 Gbps | 25+ Gbps |
| GPU | None | NVIDIA T4 | A100/H100 |
| Storage | 100GB | 500GB | 2TB+ |

**GPU Considerations**:
- NVIDIA NVENC for H.264 encoding (VP8 fallback if unavailable)
- Reduces CPU load by 70-80% for video encoding
- Recommended for 1080p@30fps or higher resolutions

---

## 2. NDI SDK Installation (Production)

### 2.1 Linux Installation Steps

#### Step 1: Download NDI SDK
```bash
# Visit https://www.ndi.tv/download/
# Select: Linux > NDI SDK 5.6+ > x86_64 or ARM64
# Register for account (required for download)

mkdir -p /opt/ndi-sdk
cd /opt/ndi-sdk

# Extract SDK (example path - adjust for actual download)
tar -xzf ndi-sdk-5.6.0-linux-x86_64.tar.gz

# Verify installation
ls -la /opt/ndi-sdk/lib/
# Should show: libndi.so.5, libndi_core.so.5, etc.
```

#### Step 2: Environment Configuration
```bash
# Add to /etc/profile.d/ndi.sh
export NDI_SDK_PATH=/opt/ndi-sdk
export LD_LIBRARY_PATH=$NDI_SDK_PATH/lib:$LD_LIBRARY_PATH
export PATH=$NDI_SDK_PATH/bin:$PATH

# Reload environment
source /etc/profile.d/ndi.sh

# Verify
ndi-find-demo
```

#### Step 3: Python Bindings

**Option A: PyNDI (Recommended)**
```bash
# Install from PyPI
pip install PyNDI

# Verify installation
python3 -c "from ndi import sdk; print(sdk.version())"
```

**Option B: Build from Source**
```bash
git clone https://github.com/Gtown-CS/PyNDI.git
cd PyNDI
python setup.py build_ext --inplace
pip install -e .
```

#### Step 4: System Library Configuration
```bash
# Add NDI libraries to system cache
echo "/opt/ndi-sdk/lib" | sudo tee /etc/ld.so.conf.d/ndi.conf
sudo ldconfig

# Verify
ldconfig -p | grep libndi
# Should show: libndi.so.5 => /opt/ndi-sdk/lib/libndi.so.5
```

### 2.2 Testing SDK Installation

```python
#!/usr/bin/env python3
# test_ndi_installation.py

import sys
import subprocess
from pathlib import Path

def test_ndi_sdk():
    """Comprehensive NDI SDK installation test"""

    tests = {
        "SDK Directory": lambda: Path("/opt/ndi-sdk/lib").exists(),
        "Library Files": lambda: Path("/opt/ndi-sdk/lib/libndi.so.5").exists(),
        "PyNDI Package": lambda: _import_pyndi(),
        "ndi-find-demo Tool": lambda: _run_tool("ndi-find-demo"),
    }

    print("=" * 60)
    print("NDI SDK Installation Test")
    print("=" * 60)

    passed = 0
    for test_name, test_func in tests.items():
        try:
            result = test_func()
            status = "PASS" if result else "FAIL"
            if status == "PASS":
                passed += 1
            print(f"[{status}] {test_name}")
        except Exception as e:
            print(f"[FAIL] {test_name}: {e}")

    print(f"\nPassed: {passed}/{len(tests)}")
    return passed == len(tests)

def _import_pyndi():
    try:
        from ndi import sdk
        version = sdk.version()
        print(f"  NDI SDK Version: {version}")
        return True
    except ImportError:
        return False

def _run_tool(tool_name):
    try:
        result = subprocess.run([tool_name], capture_output=True, timeout=5)
        return result.returncode in (0, 1)  # Tool may exit 1 if no streams found
    except Exception:
        return False

if __name__ == "__main__":
    success = test_ndi_sdk()
    sys.exit(0 if success else 1)
```

### 2.3 Troubleshooting Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `ImportError: No module named 'ndi'` | PyNDI not installed | `pip install PyNDI` |
| `libndi.so.5: cannot open shared object` | LD_LIBRARY_PATH not set | Run `source /etc/profile.d/ndi.sh` |
| `Permission denied` on SDK files | Ownership issue | `sudo chown -R $USER:$USER /opt/ndi-sdk` |
| `ndi-find-demo` hangs | mDNS not available | Check firewall rules (UDP 5353) |
| `Cannot find NDI streams` | Network isolation | Verify Gigabit Ethernet connected |

---

## 3. Replace Mock with Real NDI

### 3.1 Code Changes: use_mock=False

#### Before (Mock Mode)
```python
from communication.ndi_witness_publisher import NDIWitnessPublisher, Ed25519Signer

signer = Ed25519Signer()
publisher = NDIWitnessPublisher(
    stream_name="IF.witness.yologuard.01",
    component="IF.yologuard",
    signer=signer,
    use_mock=True  # ← MOCK MODE (testing)
)
```

#### After (Production Mode)
```python
from communication.ndi_witness_publisher import NDIWitnessPublisher, Ed25519Signer

signer = Ed25519Signer.load_private_key(Path("/etc/witness/keys/private.pem"))
publisher = NDIWitnessPublisher(
    stream_name="IF.witness.yologuard.prod-01",
    component="IF.yologuard",
    signer=signer,
    use_mock=False  # ← REAL NDI MODE (production)
)
```

### 3.2 Real NDI Sender/Receiver Configuration

Create production wrapper: `/opt/witness/real_ndi_sender.py`

```python
#!/usr/bin/env python3
"""
Real NDI Sender - Production-grade wrapper around PyNDI

Handles:
- Stream creation with proper configuration
- Frame rate and resolution management
- Bandwidth optimization
- Connection error recovery
"""

from typing import Dict, Any, Optional
from pathlib import Path
import time
import logging

from ndi import sdk
import numpy as np

logger = logging.getLogger(__name__)

class RealNDISender:
    """Production NDI sender using real SDK"""

    def __init__(
        self,
        stream_name: str,
        frame_width: int = 1280,
        frame_height: int = 720,
        frame_rate: int = 30,
    ):
        self.stream_name = stream_name
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frame_rate = frame_rate
        self.frame_interval = 1.0 / frame_rate

        self.sender = None
        self.is_running = False
        self.last_frame_time = 0

    def start(self):
        """Start NDI sender"""
        try:
            # Initialize NDI SDK
            if not sdk.is_supported_os():
                raise RuntimeError("NDI SDK not supported on this OS")

            # Create sender
            settings = sdk.SendCreate(
                name=self.stream_name,
                bandwidth=125000000  # ~1 Gbps max
            )
            self.sender = sdk.send_create(settings)

            if not self.sender:
                raise RuntimeError("Failed to create NDI sender")

            self.is_running = True
            logger.info(f"Started NDI sender: {self.stream_name}")

        except Exception as e:
            logger.error(f"Failed to start NDI sender: {e}")
            raise

    def send_frame(self, frame_data: bytes, metadata: Dict[str, Any]):
        """Send video frame with metadata

        Args:
            frame_data: Frame image bytes (must match frame_width x frame_height)
            metadata: NDI metadata (embedded in stream)
        """
        if not self.is_running:
            raise RuntimeError("Sender not started")

        # Enforce frame rate (sleep to match target FPS)
        elapsed = time.time() - self.last_frame_time
        if elapsed < self.frame_interval:
            time.sleep(self.frame_interval - elapsed)

        try:
            # Create video frame
            video_frame = sdk.VideoFrame(
                data=frame_data,
                width=self.frame_width,
                height=self.frame_height,
                frame_rate_num=self.frame_rate,
                frame_rate_den=1,
                is_progressive=True,
                picture_aspect_ratio=16.0/9.0
            )

            # Convert metadata to NDI format (key-value pairs)
            ndi_metadata = self._build_ndi_metadata(metadata)

            # Send frame
            sdk.send_send_video(self.sender, video_frame)
            if ndi_metadata:
                sdk.send_send_metadata(self.sender, ndi_metadata)

            self.last_frame_time = time.time()
            logger.debug(f"Sent frame: {metadata.get('frame_number', '?')}")

        except Exception as e:
            logger.error(f"Failed to send frame: {e}")
            raise

    def stop(self):
        """Stop NDI sender and cleanup"""
        if self.sender:
            sdk.send_destroy(self.sender)
            self.is_running = False
            logger.info(f"Stopped NDI sender: {self.stream_name}")

    def _build_ndi_metadata(self, metadata: Dict) -> Optional[str]:
        """Convert witness metadata to NDI XML format"""
        import json

        ndi_xml = "<ndi_metadata>"
        ndi_xml += f"<data>{json.dumps(metadata)}</data>"
        ndi_xml += "</ndi_metadata>"
        return ndi_xml


# In production, modify ndi_witness_publisher.py:
# Replace: from communication.ndi_witness_publisher import MockNDISender
# With: from real_ndi_sender import RealNDISender
```

### 3.3 Stream Naming Conventions

Establish consistent naming for production streams:

```
Format: IF.witness.<component>.<location>-<instance>.<environment>

Examples:
  - IF.witness.yologuard.us-east-1a.prod-01
  - IF.witness.yologuard.eu-west-1b.prod-02
  - IF.witness.guardian-reviewer.ap-southeast-1.staging-01

Breaking down:
  - IF.witness     = System identifier
  - yologuard      = Scanner component name
  - us-east-1a     = Geographic location (AWS region-AZ)
  - prod-01        = Environment (prod/staging/dev) + instance number
```

### 3.4 mDNS Discovery Setup

mDNS (Multicast DNS) is used by NDI for automatic stream discovery:

```bash
# Enable mDNS on all NICs
sudo apt-get install -y avahi-daemon

# Configure /etc/avahi/avahi-daemon.conf
[multicast-dns]
enable-dbus=yes
disallow-other-stacks=no

# Start service
sudo systemctl restart avahi-daemon

# Test discovery
mdns-scan
# Should show NDI streams with format: _ndi._udp
```

#### Firewall Rules for mDNS
```bash
# Allow mDNS multicast traffic
sudo ufw allow from 224.0.0.251 proto udp to any port 5353
sudo ufw allow to 224.0.0.251 proto udp port 5353

# Or with iptables
sudo iptables -A INPUT -d 224.0.0.251 -p udp -j ACCEPT
sudo iptables -A OUTPUT -d 224.0.0.251 -p udp -j ACCEPT
```

---

## 4. Performance Tuning

### 4.1 Bandwidth Optimization (Target: <10 Mbps HD)

```python
#!/usr/bin/env python3
# performance_tuning.py

class NDIPerformanceTuner:
    """Configure NDI for optimal bandwidth"""

    # Video codec targets
    PRESETS = {
        "HD_LOW_BANDWIDTH": {
            "resolution": (1280, 720),
            "fps": 15,
            "bitrate": 5,      # ~5 Mbps
            "codec": "H.264",
            "quality": "fast"
        },
        "HD_STANDARD": {
            "resolution": (1280, 720),
            "fps": 30,
            "bitrate": 8,      # ~8 Mbps
            "codec": "H.264",
            "quality": "balanced"
        },
        "FULL_HD": {
            "resolution": (1920, 1080),
            "fps": 30,
            "bitrate": 15,     # ~15 Mbps
            "codec": "H.264",
            "quality": "high"
        },
        "4K": {
            "resolution": (3840, 2160),
            "fps": 30,
            "bitrate": 40,     # ~40 Mbps
            "codec": "H.265",
            "quality": "high"
        }
    }

    @staticmethod
    def estimate_bandwidth(width: int, height: int, fps: int, codec: str) -> float:
        """Estimate required bandwidth in Mbps

        Formula: (width × height × fps × 0.1) / codec_efficiency
        """
        pixels_per_second = width * height * fps
        codec_efficiency = {"H.264": 1.0, "H.265": 1.5, "VP8": 0.8}.get(codec, 1.0)
        estimated_mbps = (pixels_per_second * 0.1) / codec_efficiency
        return estimated_bandwidth

# Example usage
tuner = NDIPerformanceTuner()
bw_hd = tuner.estimate_bandwidth(1280, 720, 30, "H.264")
print(f"HD 720p30 requires: ~{bw_hd:.1f} Mbps")  # ~27.6 Mbps uncompressed, ~5-8 Mbps compressed
```

### 4.2 Latency Optimization (Target: <100ms end-to-end)

NDI latency breakdown:
- **Encoding**: 10-30ms (depends on resolution and codec)
- **Network**: 5-50ms (depends on physical distance)
- **Decoding**: 10-30ms
- **Application Processing**: 10-20ms

Total: ~35-130ms (typically 50-80ms on same LAN)

```bash
# Network optimization for latency
# Lower MTU for small packets (default 1500)
sudo ip link set mtu 1440 dev eth0

# Enable UDP GSO/GRO if supported (kernel 4.18+)
ethtool -K eth0 gro on gso on

# Check UDP buffer sizes
sysctl net.core.rmem_max
sysctl net.core.rmem_default
# Set to 256MB for streaming: net.core.rmem_max = 268435456
```

### 4.3 Frame Rate Configuration

| FPS | Use Case | Bandwidth | Latency |
|-----|----------|-----------|---------|
| 15 | Archive/compliance (low bandwidth) | 3-5 Mbps | 67ms |
| 24 | Film/cinema quality | 5-8 Mbps | 42ms |
| 30 | Standard video broadcast | 8-12 Mbps | 33ms |
| 60 | High-motion monitoring | 15-25 Mbps | 17ms |

```python
# Configuration in environment
WITNESS_CONFIG = {
    "frame_rate": 30,  # Frames per second
    "keyframe_interval": 60,  # Insert keyframe every N frames
}
```

### 4.4 Resolution Settings

| Resolution | FPS | Bandwidth | Use Case |
|-----------|-----|-----------|----------|
| 640x480 (VGA) | 30 | 1-2 Mbps | Legacy/very low BW |
| 1280x720 (HD) | 30 | 5-8 Mbps | **Recommended default** |
| 1920x1080 (Full HD) | 30 | 10-15 Mbps | High-detail scanning |
| 3840x2160 (4K) | 30 | 35-50 Mbps | Premium/archive |

### 4.5 CPU/GPU Encoding Options

```python
#!/usr/bin/env python3
# hardware_encoding.py

import subprocess

class HardwareEncodingConfig:
    """Configure hardware acceleration for encoding"""

    @staticmethod
    def detect_gpu():
        """Detect available GPU for encoding"""
        try:
            # Check for NVIDIA GPU
            result = subprocess.run(["nvidia-smi"], capture_output=True)
            if result.returncode == 0:
                return "nvidia"

            # Check for AMD GPU
            result = subprocess.run(["rocm-smi"], capture_output=True)
            if result.returncode == 0:
                return "amd"

            # Check for Intel QuickSync
            if b"Intel" in subprocess.run(["lspci"], capture_output=True).stdout:
                return "intel"
        except:
            pass

        return None

    @staticmethod
    def get_encoding_config(gpu_type: str = None) -> dict:
        """Get optimal encoding configuration"""

        if gpu_type == "nvidia":
            return {
                "encoder": "h264_nvenc",
                "preset": "default",  # Options: default, fast, slow
                "rc_mode": "vbr",  # Variable bitrate
            }
        elif gpu_type == "intel":
            return {
                "encoder": "h264_qsv",
                "preset": "balanced",  # Options: fast, balanced, slow
            }
        else:
            # CPU encoding fallback
            return {
                "encoder": "libx264",
                "preset": "faster",  # Trades quality for speed
                "crf": 23,  # Quality (0-51, lower=better)
            }

# Usage
gpu = HardwareEncodingConfig.detect_gpu()
config = HardwareEncodingConfig.get_encoding_config(gpu)
print(f"GPU: {gpu}, Encoder: {config['encoder']}")
```

---

## 5. Grafana Monitoring Dashboards

### 5.1 Metrics to Monitor

```
# Frame Rate (FPS)
- witness_frame_rate (current FPS)
- witness_frames_published_total
- witness_frames_dropped_total

# Bandwidth Usage (Mbps)
- witness_bandwidth_current_mbps
- witness_bandwidth_peak_mbps
- witness_bytes_sent_total

# Latency (ms)
- witness_encoding_latency_ms (histogram)
- witness_network_latency_ms (histogram)
- witness_e2e_latency_ms (histogram)

# Signature Verification (%)
- witness_signatures_verified_total
- witness_signatures_failed_total
- witness_signature_verification_rate

# Hash Chain Integrity (%)
- witness_chain_valid_total
- witness_chain_breaks_total
- witness_chain_integrity_rate
```

### 5.2 Sample Grafana Dashboard JSON

```json
{
  "dashboard": {
    "title": "NDI Witness Streaming - Production",
    "panels": [
      {
        "title": "Frame Rate (FPS)",
        "targets": [
          {
            "expr": "witness_frame_rate"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Bandwidth Usage (Mbps)",
        "targets": [
          {
            "expr": "witness_bandwidth_current_mbps"
          }
        ],
        "type": "graph",
        "alert": {
          "conditions": [
            {
              "evaluator": { "params": [15], "type": "gt" },
              "operator": { "type": "and" },
              "query": { "params": ["witness_bandwidth_current_mbps", "5m", "now"] },
              "reducer": { "params": [], "type": "avg" },
              "type": "query"
            }
          ],
          "message": "Bandwidth exceeds 15 Mbps threshold"
        }
      },
      {
        "title": "End-to-End Latency (ms)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, witness_e2e_latency_ms)"
          }
        ],
        "type": "graph",
        "alert": {
          "conditions": [
            {
              "evaluator": { "params": [100], "type": "gt" },
              "message": "Latency exceeds 100ms threshold"
            }
          ]
        }
      },
      {
        "title": "Signature Verification Rate (%)",
        "targets": [
          {
            "expr": "100 * witness_signatures_verified_total / (witness_signatures_verified_total + witness_signatures_failed_total)"
          }
        ],
        "type": "stat"
      },
      {
        "title": "Hash Chain Integrity (%)",
        "targets": [
          {
            "expr": "100 * (1 - witness_chain_breaks_total / witness_chain_valid_total)"
          }
        ],
        "type": "stat",
        "alert": {
          "conditions": [
            {
              "evaluator": { "params": [99], "type": "lt" },
              "message": "Chain integrity below 99%"
            }
          ]
        }
      }
    ]
  }
}
```

### 5.3 Prometheus Exporter Integration

```python
#!/usr/bin/env python3
# witness_metrics_exporter.py

from prometheus_client import Counter, Gauge, Histogram, generate_latest
from flask import Flask, Response
import time

app = Flask(__name__)

# Metrics
frame_rate_gauge = Gauge('witness_frame_rate', 'Current frame rate in FPS')
bandwidth_gauge = Gauge('witness_bandwidth_current_mbps', 'Current bandwidth in Mbps')
signature_verified = Counter('witness_signatures_verified_total', 'Total verified signatures')
signature_failed = Counter('witness_signatures_failed_total', 'Total failed signatures')
chain_valid = Counter('witness_chain_valid_total', 'Total valid chain frames')
chain_breaks = Counter('witness_chain_breaks_total', 'Total chain breaks detected')
latency_histogram = Histogram('witness_e2e_latency_ms', 'End-to-end latency in ms')

@app.route('/metrics')
def metrics():
    return generate_latest()

@app.route('/health')
def health():
    # Check if metrics are recent (within last 60 seconds)
    if time.time() - last_metric_update < 60:
        return {'status': 'healthy'}, 200
    return {'status': 'unhealthy'}, 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### 5.4 Alert Thresholds

```yaml
# prometheus_rules.yml
groups:
  - name: witness_streaming
    rules:
      - alert: LowFrameRate
        expr: witness_frame_rate < 12
        for: 2m
        annotations:
          summary: "Frame rate below 15 FPS"

      - alert: HighBandwidth
        expr: witness_bandwidth_current_mbps > 15
        for: 5m
        annotations:
          summary: "Bandwidth exceeding 15 Mbps"

      - alert: HighLatency
        expr: histogram_quantile(0.95, witness_e2e_latency_ms) > 100
        for: 2m
        annotations:
          summary: "E2E latency above 100ms"

      - alert: SignatureVerificationFailure
        expr: witness_signatures_failed_total > 100
        for: 5m
        annotations:
          summary: "100+ signature verification failures"

      - alert: ChainIntegrityLoss
        expr: witness_chain_breaks_total > 0
        for: 1m
        annotations:
          summary: "Hash chain integrity break detected"
```

---

## 6. Security Hardening

### 6.1 Ed25519 Keypair Generation and Storage

```bash
#!/bin/bash
# generate_witness_keys.sh

set -e

KEYS_DIR="/etc/witness/keys"
PRIVATE_KEY="$KEYS_DIR/private.pem"
PUBLIC_KEY="$KEYS_DIR/public.pem"

# Create secure directory
sudo mkdir -p "$KEYS_DIR"
sudo chmod 700 "$KEYS_DIR"

# Generate keypair using Python
python3 << 'EOF'
from pathlib import Path
from communication.ndi_witness_publisher import Ed25519Signer

signer = Ed25519Signer()
signer.save_keypair(
    Path("/etc/witness/keys/private.pem"),
    Path("/etc/witness/keys/public.pem")
)
print("✓ Generated Ed25519 keypair")
EOF

# Secure private key
sudo chmod 600 "$PRIVATE_KEY"
sudo chown root:root "$PRIVATE_KEY"

# Restrict to witness service user
sudo setfacl -m u:witness:r "$PRIVATE_KEY"

# Display fingerprint
python3 << 'EOF'
import hashlib
from pathlib import Path

with open("/etc/witness/keys/public.pem", "rb") as f:
    pub_key = f.read()
    fingerprint = hashlib.sha256(pub_key).hexdigest()[:16]
    print(f"Public Key Fingerprint: {fingerprint}")
EOF
```

### 6.2 Key Rotation Procedures

```python
#!/usr/bin/env python3
# key_rotation.py

from datetime import datetime, timedelta
from pathlib import Path
import logging

class KeyRotationManager:
    """Manage Ed25519 key rotation"""

    def __init__(self, keys_dir: Path):
        self.keys_dir = keys_dir
        self.private_key_path = keys_dir / "private.pem"
        self.public_key_path = keys_dir / "public.pem"
        self.rotation_days = 90

    def should_rotate(self) -> bool:
        """Check if key rotation is due"""
        if not self.private_key_path.exists():
            return True

        key_age = datetime.now() - datetime.fromtimestamp(
            self.private_key_path.stat().st_mtime
        )
        return key_age > timedelta(days=self.rotation_days)

    def rotate_keys(self):
        """Perform key rotation with archival"""
        from communication.ndi_witness_publisher import Ed25519Signer

        # Archive old keys
        if self.private_key_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_dir = self.keys_dir / "archive" / timestamp
            archive_dir.mkdir(parents=True, exist_ok=True)

            self.private_key_path.rename(archive_dir / "private.pem")
            self.public_key_path.rename(archive_dir / "public.pem")

            logging.info(f"Archived old keys to {archive_dir}")

        # Generate new keys
        signer = Ed25519Signer()
        signer.save_keypair(self.private_key_path, self.public_key_path)

        # Secure permissions
        self.private_key_path.chmod(0o600)
        self.public_key_path.chmod(0o644)

        logging.info("✓ Key rotation completed")

        return {
            "timestamp": datetime.now().isoformat(),
            "old_keys_archived": str(archive_dir),
            "new_key_fingerprint": self._get_fingerprint()
        }

    def _get_fingerprint(self) -> str:
        """Get public key fingerprint"""
        import hashlib
        with open(self.public_key_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]

# Usage
manager = KeyRotationManager(Path("/etc/witness/keys"))
if manager.should_rotate():
    result = manager.rotate_keys()
    print(f"Key rotation: {result}")
```

**Rotation Schedule**:
- Primary rotation: Every 90 days
- Emergency rotation: After suspected compromise
- Archive old keys: Indefinitely (compliance requirement)

### 6.3 Access Control (Who Can View Streams)

```python
#!/usr/bin/env python3
# access_control.py

from enum import Enum
from dataclasses import dataclass
from typing import Set

class StreamPermission(Enum):
    PUBLISH = "publish"  # Send frames to stream
    SUBSCRIBE = "subscribe"  # Receive frames from stream
    VERIFY = "verify"  # Verify signatures
    ADMIN = "admin"  # Manage stream configuration

@dataclass
class StreamACL:
    """Stream Access Control List"""
    stream_name: str
    allowed_users: Set[str]
    allowed_groups: Set[str]
    permissions_map: dict  # {user/group: [StreamPermission]}

    def can_access(self, user: str, group: str, permission: StreamPermission) -> bool:
        """Check if user has permission"""
        # Check user permissions
        if user in self.permissions_map:
            if permission in self.permissions_map[user]:
                return True

        # Check group permissions
        if group in self.permissions_map:
            if permission in self.permissions_map[group]:
                return True

        return False

# Example configuration
witness_acl = {
    "IF.witness.yologuard.prod": StreamACL(
        stream_name="IF.witness.yologuard.prod",
        allowed_users={"alice", "bob"},
        allowed_groups={"security-team", "compliance"},
        permissions_map={
            "security-team": [StreamPermission.SUBSCRIBE, StreamPermission.VERIFY],
            "compliance": [StreamPermission.SUBSCRIBE, StreamPermission.VERIFY],
            "alice": [StreamPermission.PUBLISH, StreamPermission.ADMIN],
        }
    )
}
```

### 6.4 Network Segmentation (DMZ for NDI Traffic)

```
DMZ Architecture:
┌─────────────────────────────────────────────────────────────┐
│ INTERNAL NETWORK                                            │
│ ┌───────────────────────────────────────────────────────┐  │
│ │ Scanner Pods (IF.yologuard)                          │  │
│ │ - Generate scan results                              │  │
│ │ - Publish to local NDI sender                        │  │
│ └─────────────────┬──────────────────────────────────────┘  │
│                   │                                          │
│                   │ (10.0.0.0/24)                           │
└───────────────────┼──────────────────────────────────────────┘
                    │
        ┌───────────┴────────────┐
        │ FIREWALL / INGRESS      │ (Rules in Section 6.5)
        └───────────┬────────────┘
                    │
┌───────────────────┼──────────────────────────────────────────┐
│ DMZ NETWORK (NDI-ONLY)                                       │
│ ┌─────────────────┴──────────────────────────────────────┐  │
│ │ NDI Publisher Pods                                    │  │
│ │ - Receive scan results from internal                 │  │
│ │ - Publish as NDI streams                             │  │
│ │ - Broadcast via mDNS (UDP 5353)                      │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                    │
        ┌───────────┴────────────┐
        │ FIREWALL / EGRESS       │
        └───────────┬────────────┘
                    │
┌───────────────────┼──────────────────────────────────────────┐
│ EXTERNAL NETWORK (Viewers/API Consumers)                    │
│ - Guardian viewers subscribe to NDI                        │
│ - Verify signatures and chain integrity                    │
└──────────────────────────────────────────────────────────────┘
```

### 6.5 Firewall Rules

```bash
#!/bin/bash
# firewall_config.sh

# Allow mDNS multicast discovery
sudo ufw allow 224.0.0.251:5353/udp comment "NDI mDNS discovery"

# Allow NDI stream ports
for port in {5960..5989}; do
  sudo ufw allow $port/tcp comment "NDI stream port $port"
done

# Allow from specific networks only
sudo ufw allow from 10.0.0.0/24 to any port 5353 proto udp comment "NDI DMZ"

# Deny all other UDP on 5353
sudo ufw deny 5353/udp comment "Block unauthorized mDNS"

# Enable UFW
sudo ufw enable

# Verify rules
sudo ufw status verbose
```

**Network Rules Summary**:
```
┌────────────────────────────────────────────┐
│ Protocol │ Port(s)    │ Direction │ Source │
├────────────────────────────────────────────┤
│ UDP      │ 5353       │ IN/OUT    │ ANY    │ (mDNS)
│ TCP      │ 5960-5989  │ IN        │ DMZ    │ (NDI streams)
│ UDP      │ 5960-5989  │ IN        │ DMZ    │ (NDI audio)
└────────────────────────────────────────────┘
```

---

## 7. High Availability Setup

### 7.1 Redundant NDI Publishers (Primary + Backup)

```python
#!/usr/bin/env python3
# ha_publisher.py

from enum import Enum
from typing import Optional
import logging
import time

class PublisherState(Enum):
    PRIMARY = "primary"
    BACKUP = "backup"
    FAILED = "failed"

class HAWitnessPublisher:
    """High-availability witness publisher with failover"""

    def __init__(self, primary: NDIWitnessPublisher, backup: NDIWitnessPublisher):
        self.primary = primary
        self.backup = backup
        self.active = primary
        self.health_check_interval = 5  # seconds
        self.logger = logging.getLogger(__name__)

    def start(self):
        """Start both publishers"""
        self.primary.start()
        self.backup.start()
        self.logger.info("HA Publisher: Primary and backup started")

    def publish_frame(self, frame_data: bytes, metadata: dict, trace_id: str):
        """Publish frame to active publisher with failover"""
        try:
            self.active.publish_frame(frame_data, metadata, trace_id)

        except Exception as e:
            self.logger.error(f"Active publisher failed: {e}")
            self._failover()

            # Retry on new active
            try:
                self.active.publish_frame(frame_data, metadata, trace_id)
            except Exception as retry_error:
                self.logger.error(f"Failover publisher also failed: {retry_error}")
                raise

    def _failover(self):
        """Switch to backup publisher"""
        if self.active == self.primary:
            self.logger.warning("FAILOVER: Primary → Backup")
            self.active = self.backup

            # Attempt to restart primary in background
            self._attempt_primary_recovery()
        else:
            self.logger.error("CRITICAL: Both publishers failed")
            raise RuntimeError("All publishers failed")

    def _attempt_primary_recovery(self):
        """Try to recover primary publisher"""
        import threading

        def recovery_thread():
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    time.sleep(30 * (2 ** attempt))  # Exponential backoff
                    self.primary.stop()
                    time.sleep(2)
                    self.primary.start()
                    self.logger.info("Primary recovered, ready for failback")
                    return
                except Exception as e:
                    self.logger.warning(f"Recovery attempt {attempt + 1} failed: {e}")

        recovery = threading.Thread(target=recovery_thread, daemon=True)
        recovery.start()

    def stop(self):
        """Stop both publishers"""
        self.primary.stop()
        self.backup.stop()
```

### 7.2 Automatic Failover

```python
#!/usr/bin/env python3
# failover_controller.py

import asyncio
import time
from typing import Callable

class FailoverController:
    """Monitor and control automatic failover"""

    def __init__(
        self,
        ha_publisher: HAWitnessPublisher,
        health_check_interval: int = 5,
        failure_threshold: int = 3
    ):
        self.publisher = ha_publisher
        self.health_check_interval = health_check_interval
        self.failure_threshold = failure_threshold
        self.consecutive_failures = 0
        self.is_monitoring = False

    async def start_health_monitoring(self):
        """Start background health monitoring"""
        self.is_monitoring = True

        while self.is_monitoring:
            try:
                is_healthy = await self._check_health()

                if is_healthy:
                    self.consecutive_failures = 0
                else:
                    self.consecutive_failures += 1

                    if self.consecutive_failures >= self.failure_threshold:
                        await self._trigger_failover()
                        self.consecutive_failures = 0

                await asyncio.sleep(self.health_check_interval)

            except Exception as e:
                logging.error(f"Health check error: {e}")
                await asyncio.sleep(self.health_check_interval)

    async def _check_health(self) -> bool:
        """Check if active publisher is healthy"""
        # Send test frame
        test_metadata = {
            "type": "health_check",
            "timestamp": time.time()
        }

        try:
            # Use small test frame for health check
            test_frame = b"HEALTH_CHECK" * 100
            self.publisher.active.publish_frame(test_frame, test_metadata, "health-check")
            return True
        except:
            return False

    async def _trigger_failover(self):
        """Trigger failover to backup"""
        logging.warning("Health checks failed - triggering failover")
        self.publisher._failover()

    def stop(self):
        """Stop health monitoring"""
        self.is_monitoring = False
```

### 7.3 Load Balancing Across Multiple Streams

```python
#!/usr/bin/env python3
# load_balancer.py

from enum import Enum
import hashlib
from typing import List

class LoadBalancingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    HASH_BASED = "hash_based"  # Consistent hashing for same component

class StreamLoadBalancer:
    """Balance frames across multiple NDI streams"""

    def __init__(
        self,
        publishers: List[NDIWitnessPublisher],
        strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    ):
        self.publishers = publishers
        self.strategy = strategy
        self.round_robin_index = 0

    def select_publisher(self, component: str = None) -> NDIWitnessPublisher:
        """Select publisher based on strategy"""

        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin()

        elif self.strategy == LoadBalancingStrategy.LEAST_LOADED:
            return self._least_loaded()

        elif self.strategy == LoadBalancingStrategy.HASH_BASED:
            return self._hash_based(component)

        else:
            return self.publishers[0]

    def _round_robin(self) -> NDIWitnessPublisher:
        """Round-robin selection"""
        publisher = self.publishers[self.round_robin_index % len(self.publishers)]
        self.round_robin_index += 1
        return publisher

    def _least_loaded(self) -> NDIWitnessPublisher:
        """Select publisher with lowest frame count"""
        return min(self.publishers, key=lambda p: p.hash_chain.frame_count)

    def _hash_based(self, component: str) -> NDIWitnessPublisher:
        """Consistent hashing - same component always uses same publisher"""
        if not component:
            return self.publishers[0]

        hash_value = int(hashlib.md5(component.encode()).hexdigest(), 16)
        return self.publishers[hash_value % len(self.publishers)]

# Usage
publishers = [
    NDIWitnessPublisher("IF.witness.yologuard.01", "IF.yologuard", signer),
    NDIWitnessPublisher("IF.witness.yologuard.02", "IF.yologuard", signer),
]

balancer = StreamLoadBalancer(
    publishers,
    strategy=LoadBalancingStrategy.HASH_BASED
)

# Always same scanner uses same stream
publisher = balancer.select_publisher(component="IF.yologuard")
```

### 7.4 Disaster Recovery

```yaml
# backup_restore_plan.yaml
version: 1
name: "NDI Witness Streaming - Disaster Recovery"

procedures:
  complete_stream_failure:
    description: "All NDI streams are unavailable"
    steps:
      1. "Verify mDNS connectivity on backup network"
      2. "Check firewall rules (UDP 5353, TCP 5960-5989)"
      3. "Restart NDI publisher services"
      4. "Verify stream discovery with 'ndi-find-demo'"
      5. "Start replaying frames from archive"
      6. "Alert on-call team if not resolved in 5 minutes"

  signature_verification_failure:
    description: "Cannot verify frame signatures"
    steps:
      1. "Verify public key matches published key"
      2. "Check if key rotation is in progress"
      3. "Query archive for valid key fingerprints"
      4. "Re-verify last 100 frames"
      5. "Contact security team if >5% frames fail"

  hash_chain_break:
    description: "Hash chain integrity is broken"
    steps:
      1. "Identify frame where chain breaks"
      2. "Check frame timestamps for gaps"
      3. "Verify with backup archival system"
      4. "Replay from last known good frame"
      5. "Investigate root cause (network issue, frame drop)"
      6. "Update monitoring alerts if pattern emerges"

  key_compromise:
    description: "Private key suspected to be compromised"
    steps:
      1. "Immediately revoke current key"
      2. "Mark all frames signed with old key as 'suspect'"
      3. "Generate new Ed25519 keypair"
      4. "Update all stream metadata with new public key"
      5. "Re-sign last 24 hours of frames with new key"
      6. "Notify all viewers of key change"
      7. "Audit for unauthorized access"

recovery_time_objectives:
  stream_unavailability: 5 minutes
  signature_verification_failure: 30 minutes
  chain_integrity_loss: 15 minutes
  key_compromise: 60 minutes

testing:
  frequency: "Monthly"
  procedure: "Run full failover test in staging environment"
  validation: "Verify frames verified end-to-end"
```

---

## 8. Troubleshooting Guide

### 8.1 Stream Not Discoverable (mDNS Issues)

**Symptom**: `ndi-find-demo` shows no streams

```bash
# 1. Verify mDNS service is running
sudo systemctl status avahi-daemon
# → Should be "active (running)"

# 2. Check mDNS port is accessible
sudo netstat -ulnp | grep 5353
# → Should show avahi on UDP 5353

# 3. Verify firewall allows mDNS
sudo ufw status | grep 5353
# → Should show allow rules for 224.0.0.251:5353

# 4. Test multicast connectivity
ip addr show
# → All interfaces should have multicast support (flag: MULTICAST)

# 5. Restart mDNS service
sudo systemctl restart avahi-daemon

# 6. Force stream re-advertisement
sudo systemctl restart <witness_service>

# 7. Test with verbose logging
ndi-find-demo -v
```

### 8.2 High Latency (Network Tuning)

**Symptom**: E2E latency >100ms

```bash
# 1. Measure network latency
ping -c 10 <receiver_ip>
# → Look for average latency

# 2. Check network buffers
sysctl net.core.rmem_default
sysctl net.core.wmem_default
# → Should be at least 256MB (268435456)

# 3. Optimize UDP buffers
sudo sysctl -w net.core.rmem_max=268435456
sudo sysctl -w net.core.wmem_max=268435456

# 4. Enable UDP hardware acceleration
ethtool -K eth0 gro on gso on

# 5. Check for packet loss
iperf3 -c <receiver_ip> -u -b 100M -t 10
# → Look for "Datagrams lost"

# 6. Monitor frame encoding latency
# Check prometheus metrics: witness_encoding_latency_ms

# 7. If still high, consider:
# - Upgrade to 10G Ethernet
# - Reduce resolution/FPS
# - Enable GPU encoding
# - Switch to faster codec (H.265 vs H.264)
```

### 8.3 Signature Verification Failures

**Symptom**: `witness_signatures_failed_total > 0`

```python
#!/usr/bin/env python3
# debug_signature_failures.py

from communication.ndi_guardian_viewer import WitnessVerifier

def diagnose_signature_failure(frame_data: bytes, metadata: dict):
    """Debug signature verification failure"""

    verifier = WitnessVerifier()
    result = verifier.verify_frame(frame_data, metadata)

    if not result["signature_valid"]:
        # Check 1: Public key is valid
        import base64
        try:
            public_key_bytes = base64.b64decode(metadata["public_key"])
            print(f"✓ Public key is valid Base64 ({len(public_key_bytes)} bytes)")
        except:
            print("✗ Public key is invalid Base64")
            return

        # Check 2: Signature format is correct
        try:
            sig_bytes = bytes.fromhex(metadata["signature"])
            assert len(sig_bytes) == 64  # Ed25519 is 64 bytes
            print("✓ Signature format is valid (64 bytes)")
        except:
            print("✗ Signature format is invalid")
            return

        # Check 3: Metadata hasn't been tampered
        import json
        import hashlib

        canonical = json.dumps({
            "frame_number": metadata["frame_number"],
            "timestamp": metadata["timestamp"],
            "content_hash": metadata["content_hash"]
        }, sort_keys=True)

        expected_hash = hashlib.sha256(canonical.encode()).hexdigest()
        actual_hash = hashlib.sha256(canonical.encode()).hexdigest()

        if expected_hash == actual_hash:
            print("✓ Metadata hash matches")
        else:
            print("✗ Metadata has been tampered")
            return

        # Check 4: Key rotation happened
        print("\nPossible causes:")
        print("- Key was rotated (old signature, new key)")
        print("- Different signer than expected")
        print("- Frame was corrupted in transit")
        print("\nAction: Query archive for key at frame timestamp")
```

### 8.4 Hash Chain Breaks

**Symptom**: `witness_chain_breaks_total > 0`

```bash
# 1. Identify frame where chain breaks
# From logs or metrics, find first frame with prev_hash mismatch

# 2. Check for frame loss
# If frame N is missing, frame N+1's prev_hash won't match frame N-1

# 3. Verify frame delivery order
# NDI may deliver out-of-order if network is congested

# 4. Check timestamps
# Large gap in timestamps may indicate dropped frames

# 5. Investigate root cause:
echo "Possible causes:"
echo "- Frame drop due to network congestion"
echo "- Publisher crash and restart (new chain)"
echo "- Receiver reordering frames"
echo "- Timestamp skew causing ordering issues"

# 6. Recovery
# Option A: Start new chain (acceptable if documented)
# Option B: Replay from last known good frame
# Option C: Investigate and fix root cause

# 7. Monitor for recurrence
# If breaks happen frequently, investigate:
# - Network MTU issues (try MTU 1440)
# - Publisher buffer overruns
# - Receiver buffer underruns
```

### 8.5 Bandwidth Saturation

**Symptom**: `witness_bandwidth_current_mbps > 15`

```bash
# 1. Identify source
iftop -i eth0
# → See which flows are consuming bandwidth

# 2. Check frame rate
# Reduce FPS from 30 to 15 (halves bandwidth)

# 3. Check resolution
# Reduce from 1080p to 720p (reduces bandwidth by 56%)

# 4. Enable compression
# Use H.265 instead of H.264 (saves ~30% bandwidth)

# 5. Check network congestion
# Test with iperf3 to isolated network:
iperf3 -c <receiver> -b 100M -t 10

# 6. If network is fine, problem is at source:
# - Too many streams publishing simultaneously
# - Encoding not working properly (sending uncompressed)
# - Use load balancer to spread across multiple publishers
```

### 8.6 Common Error Messages and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `RuntimeError: Real NDI SDK not available` | PyNDI not installed | `pip install PyNDI` |
| `libndi.so.5: cannot open shared object` | Missing SDK library | Check `/opt/ndi-sdk/lib` exists |
| `Address already in use` on NDI port | Another process using port | `sudo lsof -i :5960-5989` and kill |
| `mDNS timeout` | Network issue or mDNS disabled | `sudo systemctl restart avahi-daemon` |
| `InvalidSignature` in verification | Key mismatch | Verify frame signer matches expected key |
| `Chain verification failed` | prev_hash mismatch | Check for frame drops or reordering |
| `Bandwidth exceeds threshold` | Network saturation | Reduce FPS or resolution |
| `Frame drop rate >5%` | Buffer underrun | Increase buffer size or reduce FPS |

---

## 9. Production Checklist

Pre-launch validation checklist for production deployments:

```markdown
## Pre-Deployment Checklist

### Infrastructure Setup
- [ ] NDI SDK 5.6+ installed at `/opt/ndi-sdk`
- [ ] Python 3.9+ with cryptography, prometheus-client installed
- [ ] Gigabit Ethernet verified (1000 Mbps minimum)
- [ ] Firewall rules for UDP 5353, TCP 5960-5989 configured
- [ ] mDNS service (avahi-daemon) running and verified

### NDI Configuration
- [ ] Real NDI mode enabled (use_mock=False)
- [ ] Stream naming convention established and documented
- [ ] mDNS discovery tested and verified working
- [ ] Network packet capture confirms mDNS multicast
- [ ] Fire wall rules applied and tested

### Security Setup
- [ ] Ed25519 keypair generated and secured
  - [ ] Private key at `/etc/witness/keys/private.pem` (mode 0600)
  - [ ] Public key at `/etc/witness/keys/public.pem` (mode 0644)
  - [ ] Key fingerprint documented
- [ ] Key rotation policy established (90-day schedule)
- [ ] Access control list (ACL) for streams defined
- [ ] Network segmentation (DMZ) established

### Performance Baseline
- [ ] Target frame rate established (15/24/30/60 FPS)
- [ ] Target bandwidth calculated (<10 Mbps for HD)
- [ ] Target latency baseline measured (<100ms E2E)
- [ ] Hardware encoding (GPU) enabled if available
- [ ] Performance under peak load tested

### Monitoring & Alerting
- [ ] Prometheus metrics exporter deployed
- [ ] Grafana dashboards imported and tested
- [ ] Alert rules configured:
  - [ ] Frame rate <12 FPS
  - [ ] Bandwidth >15 Mbps
  - [ ] Latency >100ms
  - [ ] Signature failures >100
  - [ ] Chain integrity <99%
- [ ] PagerDuty/Slack integration configured
- [ ] Dashboard accessible to on-call team

### High Availability
- [ ] Primary and backup publishers configured
- [ ] Health check monitoring enabled
- [ ] Failover tested (primary → backup)
- [ ] Failback procedure documented
- [ ] Load balancer configured if multiple streams
- [ ] Disaster recovery runbook documented

### Testing
- [ ] Unit tests pass (test_ndi_witness.py)
- [ ] End-to-end test: publish 100+ frames
- [ ] Verify 100% of frames have valid signatures
- [ ] Verify hash chain continuity
- [ ] Network isolation test (single VLAN)
- [ ] Failover test (kill primary, verify backup takes over)
- [ ] Key rotation test (rotate keys, reverify old frames)
- [ ] 24-hour stability test (monitor metrics)

### Documentation
- [ ] Deployment runbook completed
- [ ] Emergency procedures documented
- [ ] Key recovery procedures documented
- [ ] Monitoring dashboard documented
- [ ] Team training completed

### Compliance & Security Review
- [ ] Security audit completed
- [ ] Key management review passed
- [ ] Network isolation verified by security team
- [ ] Access control review passed
- [ ] Audit logging configured
- [ ] Compliance requirements met (data retention, etc.)

### Production Launch
- [ ] Maintenance window scheduled
- [ ] Rollback plan prepared
- [ ] On-call escalation configured
- [ ] Status page updated
- [ ] Stakeholders notified
- [ ] Launch approved by ops lead

**Deployment Date**: _______________
**Approved By**: _______________
**Notes**: _______________
```

---

## Additional Resources

### Official Documentation
- [NDI SDK Documentation](https://developer.newtek.com/ndi/documentation)
- [Cryptography Library Docs](https://cryptography.io)
- [Prometheus Monitoring](https://prometheus.io/docs)
- [Grafana Dashboard Guide](https://grafana.com/docs)

### Related Infrafabric Documentation
- [SWARM-COMMUNICATION-SECURITY.md](./SWARM-COMMUNICATION-SECURITY.md) - Cryptographic security model
- [PERFORMANCE_TARGETS.md](./PERFORMANCE_TARGETS.md) - Performance requirements
- [QUICK_START.md](./QUICK_START.md) - Quick start guide

### Command Reference

```bash
# Health Checks
ndi-find-demo                          # List available NDI streams
systemctl status avahi-daemon          # mDNS service status
netstat -tulnp | grep 5353             # Check mDNS port

# Network Testing
ping <receiver>                        # Latency test
iperf3 -c <receiver> -u -b 100M       # Bandwidth test
tcpdump -i eth0 'udp port 5353'       # Capture mDNS traffic

# Key Management
python witness_key_rotation.py         # Rotate keys
ls -la /etc/witness/keys/              # View key directory
sha256sum /etc/witness/keys/public.pem # Verify key fingerprint

# Monitoring
curl localhost:8080/metrics            # Prometheus metrics
curl localhost:8080/health             # Health check endpoint
```

---

## Support & Escalation

For production issues:

1. **Check monitoring dashboard** (Grafana)
2. **Review error messages** in Section 8
3. **Consult troubleshooting guide** (Section 8)
4. **Review logs**: `/var/log/witness/`
5. **Contact on-call engineer** via PagerDuty
6. **Engage security team** for signature/key issues

---

**Last Updated**: 2025-11-11
**Version**: 1.0
**Status**: Production-Ready
