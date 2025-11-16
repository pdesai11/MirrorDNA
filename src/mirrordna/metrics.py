"""
Performance monitoring and metrics for MirrorDNA protocol.

Provides:
- Operation timing decorators
- Performance metrics collection
- Memory usage tracking
- Metrics export (Prometheus format)
"""

import time
import functools
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class MetricSample:
    """Single metric sample."""
    timestamp: float
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class Metric:
    """Performance metric with samples."""
    name: str
    metric_type: str  # "counter", "gauge", "histogram"
    help_text: str
    samples: List[MetricSample] = field(default_factory=list)
    unit: str = ""

    def add_sample(self, value: float, labels: Optional[Dict[str, str]] = None):
        """Add a metric sample."""
        self.samples.append(MetricSample(
            timestamp=time.time(),
            value=value,
            labels=labels or {}
        ))

    def get_latest(self) -> Optional[float]:
        """Get latest metric value."""
        if not self.samples:
            return None
        return self.samples[-1].value

    def get_average(self, last_n: Optional[int] = None) -> float:
        """Get average of last N samples."""
        samples_to_use = self.samples[-last_n:] if last_n else self.samples
        if not samples_to_use:
            return 0.0
        return sum(s.value for s in samples_to_use) / len(samples_to_use)

    def get_percentile(self, percentile: float, last_n: Optional[int] = None) -> float:
        """Get percentile value."""
        samples_to_use = self.samples[-last_n:] if last_n else self.samples
        if not samples_to_use:
            return 0.0

        values = sorted([s.value for s in samples_to_use])
        index = int(len(values) * percentile / 100)
        return values[min(index, len(values) - 1)]


class MetricsRegistry:
    """
    Central registry for all metrics.

    Singleton pattern for global metrics collection.
    """
    _instance: Optional['MetricsRegistry'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._metrics: Dict[str, Metric] = {}
        self._enabled = True
        self._initialized = True

    def register(self, name: str, metric_type: str, help_text: str, unit: str = "") -> Metric:
        """Register a new metric."""
        if name not in self._metrics:
            self._metrics[name] = Metric(
                name=name,
                metric_type=metric_type,
                help_text=help_text,
                unit=unit
            )
        return self._metrics[name]

    def get_metric(self, name: str) -> Optional[Metric]:
        """Get metric by name."""
        return self._metrics.get(name)

    def record(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a metric value."""
        if not self._enabled:
            return

        metric = self._metrics.get(name)
        if metric:
            metric.add_sample(value, labels)

    def get_all_metrics(self) -> Dict[str, Metric]:
        """Get all registered metrics."""
        return self._metrics.copy()

    def clear(self):
        """Clear all metrics."""
        self._metrics.clear()

    def disable(self):
        """Disable metrics collection."""
        self._enabled = False

    def enable(self):
        """Enable metrics collection."""
        self._enabled = True

    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus format.

        Returns:
            Metrics in Prometheus text format
        """
        lines = []

        for metric in self._metrics.values():
            # Add help text
            lines.append(f"# HELP {metric.name} {metric.help_text}")

            # Add type
            lines.append(f"# TYPE {metric.name} {metric.metric_type}")

            # Add samples
            for sample in metric.samples:
                labels_str = ""
                if sample.labels:
                    labels_parts = [f'{k}="{v}"' for k, v in sample.labels.items()]
                    labels_str = "{" + ",".join(labels_parts) + "}"

                lines.append(f"{metric.name}{labels_str} {sample.value} {int(sample.timestamp * 1000)}")

        return "\n".join(lines) + "\n"


# Global registry instance
registry = MetricsRegistry()


# ============================================================================
# Performance Decorators
# ============================================================================

def timed(metric_name: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
    """
    Decorator to measure function execution time.

    Args:
        metric_name: Custom metric name (default: function name + "_duration_ms")
        labels: Optional labels to attach to metric

    Example:
        @timed()
        def compute_checksum(data):
            pass

        @timed("custom_operation_time", {"operation": "important"})
        def important_operation():
            pass
    """
    def decorator(func: Callable) -> Callable:
        # Register metric
        name = metric_name or f"{func.__name__}_duration_ms"
        registry.register(
            name=name,
            metric_type="histogram",
            help_text=f"Execution time of {func.__name__} in milliseconds",
            unit="ms"
        )

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start) * 1000
                registry.record(name, duration_ms, labels)

        return wrapper
    return decorator


def counted(metric_name: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
    """
    Decorator to count function calls.

    Args:
        metric_name: Custom metric name (default: function name + "_calls_total")
        labels: Optional labels to attach to metric

    Example:
        @counted()
        def process_event(event):
            pass
    """
    def decorator(func: Callable) -> Callable:
        # Register metric
        name = metric_name or f"{func.__name__}_calls_total"
        registry.register(
            name=name,
            metric_type="counter",
            help_text=f"Total calls to {func.__name__}",
            unit="calls"
        )

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            registry.record(name, 1, labels)
            return func(*args, **kwargs)

        return wrapper
    return decorator


# ============================================================================
# Performance Statistics
# ============================================================================

class PerformanceStats:
    """
    Generate performance statistics from metrics.
    """

    @staticmethod
    def get_operation_stats(operation_pattern: str = "_duration_ms") -> Dict[str, Dict[str, float]]:
        """
        Get statistics for timed operations.

        Args:
            operation_pattern: Pattern to match metric names

        Returns:
            Dict of operation name to stats (avg, p50, p95, p99, count)
        """
        stats = {}

        for name, metric in registry.get_all_metrics().items():
            if operation_pattern in name and metric.samples:
                stats[name] = {
                    "count": len(metric.samples),
                    "average": metric.get_average(),
                    "p50": metric.get_percentile(50),
                    "p95": metric.get_percentile(95),
                    "p99": metric.get_percentile(99),
                    "min": min(s.value for s in metric.samples),
                    "max": max(s.value for s in metric.samples),
                }

        return stats

    @staticmethod
    def print_report():
        """Print human-readable performance report."""
        print("=" * 80)
        print("MirrorDNA Performance Report")
        print("=" * 80)
        print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
        print()

        stats = PerformanceStats.get_operation_stats()

        if not stats:
            print("No performance data collected.")
            return

        # Print operation timings
        print("Operation Timings (milliseconds):")
        print("-" * 80)
        print(f"{'Operation':<40} {'Count':>8} {'Avg':>10} {'P50':>10} {'P95':>10} {'P99':>10}")
        print("-" * 80)

        for name, stat in sorted(stats.items()):
            operation = name.replace("_duration_ms", "")
            print(f"{operation:<40} {stat['count']:>8} "
                  f"{stat['average']:>10.2f} {stat['p50']:>10.2f} "
                  f"{stat['p95']:>10.2f} {stat['p99']:>10.2f}")

        print("=" * 80)

        # Print counter metrics
        counter_metrics = {
            name: metric for name, metric in registry.get_all_metrics().items()
            if metric.metric_type == "counter"
        }

        if counter_metrics:
            print("\nCounters:")
            print("-" * 80)
            for name, metric in sorted(counter_metrics.items()):
                total = sum(s.value for s in metric.samples)
                print(f"{name}: {int(total)}")

        print()


# ============================================================================
# Pre-registered Metrics
# ============================================================================

# Register common metrics
registry.register(
    "mirrordna_checksum_computations_total",
    "counter",
    "Total number of checksum computations"
)

registry.register(
    "mirrordna_crypto_operations_total",
    "counter",
    "Total number of cryptographic operations"
)

registry.register(
    "mirrordna_storage_operations_total",
    "counter",
    "Total number of storage operations"
)

registry.register(
    "mirrordna_identity_creations_total",
    "counter",
    "Total number of identities created"
)

registry.register(
    "mirrordna_sessions_created_total",
    "counter",
    "Total number of sessions created"
)


# ============================================================================
# Convenience Functions
# ============================================================================

def record_checksum_operation(duration_ms: float):
    """Record checksum operation timing."""
    registry.record("mirrordna_checksum_computations_total", 1)
    registry.record("checksum_computation_duration_ms", duration_ms)


def record_crypto_operation(operation_type: str, duration_ms: float):
    """Record cryptographic operation timing."""
    registry.record("mirrordna_crypto_operations_total", 1, {"type": operation_type})
    registry.record("crypto_operation_duration_ms", duration_ms, {"type": operation_type})


def record_storage_operation(operation_type: str, duration_ms: float):
    """Record storage operation timing."""
    registry.record("mirrordna_storage_operations_total", 1, {"type": operation_type})
    registry.record("storage_operation_duration_ms", duration_ms, {"type": operation_type})


def get_performance_summary() -> Dict[str, Any]:
    """Get performance summary as dict."""
    stats = PerformanceStats.get_operation_stats()

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "operations": stats,
        "metrics_count": len(registry.get_all_metrics()),
        "total_samples": sum(len(m.samples) for m in registry.get_all_metrics().values())
    }
