"""IF.chassis resource limits implementation

This module implements CPU, memory, and API rate limiting for swarm execution.

Features:
- Memory limits (max_memory_mb)
- CPU limits (max_cpu_percent)
- API rate limiting (token bucket algorithm)
- OS-level resource enforcement (setrlimit)
- Resource violation tracking

Philosophy: IF.ground (Wu Lun - 五倫)
- Security through isolation
- Fair resource allocation
- Noisy neighbor prevention

Part of Phase 0: P0.3.2 - Resource Limits
"""

import os
import time
import threading
from typing import Dict, Optional, Any
from dataclasses import dataclass, field

try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False

from infrafabric.witness import log_operation


@dataclass
class ResourceLimits:
    """Resource limits for swarm execution

    Attributes:
        max_memory_mb: Maximum memory allocation in MB
        max_cpu_percent: Maximum CPU usage percentage (0-100)
        max_api_calls_per_second: Maximum API calls per second
        max_execution_time_seconds: Maximum execution time
        enable_os_limits: Whether to use OS-level limits (setrlimit)
    """
    max_memory_mb: int = 512
    max_cpu_percent: int = 50
    max_api_calls_per_second: float = 10.0
    max_execution_time_seconds: float = 300.0
    enable_os_limits: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'max_memory_mb': self.max_memory_mb,
            'max_cpu_percent': self.max_cpu_percent,
            'max_api_calls_per_second': self.max_api_calls_per_second,
            'max_execution_time_seconds': self.max_execution_time_seconds,
            'enable_os_limits': self.enable_os_limits,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourceLimits':
        """Create from dictionary"""
        return cls(
            max_memory_mb=data.get('max_memory_mb', 512),
            max_cpu_percent=data.get('max_cpu_percent', 50),
            max_api_calls_per_second=data.get('max_api_calls_per_second', 10.0),
            max_execution_time_seconds=data.get('max_execution_time_seconds', 300.0),
            enable_os_limits=data.get('enable_os_limits', True),
        )


class TokenBucket:
    """Token bucket algorithm for API rate limiting

    This implements a classic token bucket for rate limiting.
    Tokens are added at a fixed rate, and each API call consumes one token.

    Example:
        >>> bucket = TokenBucket(rate=10.0, capacity=10)
        >>> if bucket.consume(1):
        ...     # API call allowed
        ...     make_api_call()
    """

    def __init__(self, rate: float, capacity: int = None):
        """Initialize token bucket

        Args:
            rate: Tokens per second (e.g., 10.0 = 10 tokens/second)
            capacity: Maximum tokens in bucket (defaults to rate * 2)
        """
        self.rate = rate
        self.capacity = capacity or int(rate * 2)
        self.tokens = float(self.capacity)
        self.last_update = time.time()
        self.lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        """Attempt to consume tokens

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens consumed, False if insufficient tokens
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update

            # Add tokens based on elapsed time
            self.tokens = min(
                self.capacity,
                self.tokens + (elapsed * self.rate)
            )
            self.last_update = now

            # Try to consume
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            else:
                return False

    def get_available_tokens(self) -> float:
        """Get current available tokens"""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            return min(
                self.capacity,
                self.tokens + (elapsed * self.rate)
            )


class ResourceEnforcer:
    """Enforces resource limits for swarm execution

    This class manages resource limits and tracks violations.

    Example:
        >>> limits = ResourceLimits(max_memory_mb=256, max_api_calls_per_second=5.0)
        >>> enforcer = ResourceEnforcer('session-7', limits)
        >>> enforcer.apply_os_limits()
        >>> if enforcer.check_api_rate_limit():
        ...     make_api_call()
    """

    def __init__(self, swarm_id: str, limits: ResourceLimits):
        """Initialize resource enforcer

        Args:
            swarm_id: Swarm identifier
            limits: Resource limits configuration
        """
        self.swarm_id = swarm_id
        self.limits = limits
        self.api_rate_limiter = TokenBucket(
            rate=limits.max_api_calls_per_second
        )
        self.violation_count = 0
        self.api_calls_blocked = 0
        self.lock = threading.Lock()

        log_operation(
            component='IF.chassis.limits',
            operation='enforcer_initialized',
            params={
                'swarm_id': swarm_id,
                'limits': limits.to_dict(),
            }
        )

    def apply_os_limits(self) -> bool:
        """Apply OS-level resource limits using setrlimit

        Returns:
            True if limits applied successfully, False otherwise

        Note:
            This uses the resource module (Unix/Linux only).
            On Windows or without resource module, this is a no-op.
        """
        if not self.limits.enable_os_limits:
            return False

        if not HAS_RESOURCE:
            log_operation(
                component='IF.chassis.limits',
                operation='os_limits_unavailable',
                params={
                    'swarm_id': self.swarm_id,
                    'reason': 'resource module not available',
                },
                severity='WARN'
            )
            return False

        try:
            # Set memory limit (RLIMIT_AS - address space)
            max_memory_bytes = self.limits.max_memory_mb * 1024 * 1024
            try:
                resource.setrlimit(
                    resource.RLIMIT_AS,
                    (max_memory_bytes, max_memory_bytes)
                )
            except (ValueError, OSError) as e:
                # Some systems don't support RLIMIT_AS
                log_operation(
                    component='IF.chassis.limits',
                    operation='memory_limit_failed',
                    params={
                        'swarm_id': self.swarm_id,
                        'error': str(e),
                    },
                    severity='WARN'
                )

            # Set CPU time limit (RLIMIT_CPU - CPU seconds)
            max_cpu_seconds = int(self.limits.max_execution_time_seconds)
            try:
                resource.setrlimit(
                    resource.RLIMIT_CPU,
                    (max_cpu_seconds, max_cpu_seconds)
                )
            except (ValueError, OSError) as e:
                log_operation(
                    component='IF.chassis.limits',
                    operation='cpu_limit_failed',
                    params={
                        'swarm_id': self.swarm_id,
                        'error': str(e),
                    },
                    severity='WARN'
                )

            log_operation(
                component='IF.chassis.limits',
                operation='os_limits_applied',
                params={
                    'swarm_id': self.swarm_id,
                    'max_memory_mb': self.limits.max_memory_mb,
                    'max_cpu_seconds': max_cpu_seconds,
                }
            )

            return True

        except Exception as e:
            log_operation(
                component='IF.chassis.limits',
                operation='os_limits_error',
                params={
                    'swarm_id': self.swarm_id,
                    'error': str(e),
                },
                severity='WARN'
            )
            return False

    def check_api_rate_limit(self, count: int = 1) -> bool:
        """Check if API call is allowed under rate limit

        Args:
            count: Number of API calls to check

        Returns:
            True if allowed, False if rate limit exceeded
        """
        allowed = self.api_rate_limiter.consume(count)

        if not allowed:
            with self.lock:
                self.api_calls_blocked += 1
                self.violation_count += 1

            log_operation(
                component='IF.chassis.limits',
                operation='api_rate_limit_exceeded',
                params={
                    'swarm_id': self.swarm_id,
                    'api_calls_blocked': self.api_calls_blocked,
                    'rate_limit': self.limits.max_api_calls_per_second,
                },
                severity='WARN'
            )

        return allowed

    def record_violation(self, violation_type: str, details: Dict[str, Any]) -> None:
        """Record resource limit violation

        Args:
            violation_type: Type of violation (memory, cpu, api_rate, timeout)
            details: Violation details
        """
        with self.lock:
            self.violation_count += 1

        log_operation(
            component='IF.chassis.limits',
            operation='resource_violation',
            params={
                'swarm_id': self.swarm_id,
                'violation_type': violation_type,
                'violation_count': self.violation_count,
                'details': details,
            },
            severity='WARN'
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get resource enforcement statistics

        Returns:
            Dictionary with enforcement stats
        """
        return {
            'swarm_id': self.swarm_id,
            'limits': self.limits.to_dict(),
            'violation_count': self.violation_count,
            'api_calls_blocked': self.api_calls_blocked,
            'api_tokens_available': self.api_rate_limiter.get_available_tokens(),
        }

    def reset_stats(self) -> None:
        """Reset violation statistics"""
        with self.lock:
            self.violation_count = 0
            self.api_calls_blocked = 0


def get_current_memory_usage_mb() -> float:
    """Get current process memory usage in MB

    Returns:
        Memory usage in MB, or 0.0 if unavailable
    """
    if not HAS_RESOURCE:
        return 0.0

    try:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        # ru_maxrss is in kilobytes on Linux, bytes on macOS
        # We'll assume Linux for now
        return usage.ru_maxrss / 1024.0  # KB to MB
    except Exception:
        return 0.0


def get_current_cpu_percent() -> float:
    """Get current process CPU usage percentage

    Returns:
        CPU percentage, or 0.0 if unavailable

    Note:
        This is a simplified implementation.
        Production use should use psutil or similar.
    """
    if not HAS_RESOURCE:
        return 0.0

    try:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        # This is user + system CPU time in seconds
        # Not a true percentage, but useful for tracking
        return usage.ru_utime + usage.ru_stime
    except Exception:
        return 0.0
