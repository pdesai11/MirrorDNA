"""
Benchmarking suite for MirrorDNA protocol.

Provides comprehensive performance benchmarks for all core operations.
"""

import time
import tempfile
import statistics
from pathlib import Path
from typing import Dict, List, Any, Callable
from dataclasses import dataclass, field, asdict
import json

from .identity import IdentityManager
from .checksum import compute_file_checksum, compute_state_checksum
from .continuity import ContinuityTracker
from .memory import MemoryManager
from .state_snapshot import capture_snapshot, save_snapshot
from .storage import JSONFileStorage
from .timeline import Timeline


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    name: str
    iterations: int
    total_time: float
    min_time: float
    max_time: float
    mean_time: float
    median_time: float
    p95_time: float
    p99_time: float
    operations_per_second: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class Benchmark:
    """Base benchmark class."""

    def __init__(self, name: str, iterations: int = 100):
        """
        Initialize benchmark.

        Args:
            name: Benchmark name
            iterations: Number of iterations to run
        """
        self.name = name
        self.iterations = iterations
        self.times: List[float] = []

    def setup(self):
        """Setup before benchmark (override in subclasses)."""
        pass

    def teardown(self):
        """Teardown after benchmark (override in subclasses)."""
        pass

    def run_once(self):
        """Run benchmark once (override in subclasses)."""
        raise NotImplementedError

    def run(self) -> BenchmarkResult:
        """Run benchmark and collect results."""
        self.setup()

        for _ in range(self.iterations):
            start = time.time()
            self.run_once()
            end = time.time()
            self.times.append(end - start)

        self.teardown()

        return self._calculate_results()

    def _calculate_results(self) -> BenchmarkResult:
        """Calculate benchmark statistics."""
        total_time = sum(self.times)
        sorted_times = sorted(self.times)

        p95_index = int(len(sorted_times) * 0.95)
        p99_index = int(len(sorted_times) * 0.99)

        return BenchmarkResult(
            name=self.name,
            iterations=self.iterations,
            total_time=total_time,
            min_time=min(self.times),
            max_time=max(self.times),
            mean_time=statistics.mean(self.times),
            median_time=statistics.median(self.times),
            p95_time=sorted_times[p95_index],
            p99_time=sorted_times[p99_index],
            operations_per_second=self.iterations / total_time
        )


# =================================================================
# Checksum Benchmarks
# =================================================================

class ChecksumBenchmark(Benchmark):
    """Benchmark checksum operations."""

    def setup(self):
        """Create test data."""
        self.test_data = {"key": "value", "number": 42, "nested": {"data": "test"}}
        self.test_string = "test" * 100

    def run_once(self):
        """Compute checksum."""
        compute_state_checksum(self.test_data)


class FileChecksumBenchmark(Benchmark):
    """Benchmark file checksum operations."""

    def setup(self):
        """Create temporary file."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(b"test data" * 1000)
        self.temp_file.close()

    def teardown(self):
        """Remove temporary file."""
        Path(self.temp_file.name).unlink()

    def run_once(self):
        """Compute file checksum."""
        compute_file_checksum(self.temp_file.name)


# =================================================================
# Identity Benchmarks
# =================================================================

class IdentityCreationBenchmark(Benchmark):
    """Benchmark identity creation."""

    def setup(self):
        """Create temporary storage."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = JSONFileStorage(self.temp_dir)
        self.manager = IdentityManager(storage=self.storage)

    def teardown(self):
        """Cleanup."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run_once(self):
        """Create identity."""
        self.manager.create_identity(identity_type="agent")


class SigningBenchmark(Benchmark):
    """Benchmark signing operations."""

    def setup(self):
        """Create identity."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = JSONFileStorage(self.temp_dir)
        self.manager = IdentityManager(storage=self.storage)
        identity = self.manager.create_identity(identity_type="agent")
        self.identity_id = identity["identity_id"]
        self.private_key = identity["_private_key"]
        self.claim = "test claim"

    def teardown(self):
        """Cleanup."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run_once(self):
        """Sign claim."""
        self.manager.sign_claim(self.identity_id, self.claim, self.private_key)


# =================================================================
# Storage Benchmarks
# =================================================================

class StorageWriteBenchmark(Benchmark):
    """Benchmark storage write operations."""

    def __init__(self, *args, batch_size: int = 100, **kwargs):
        super().__init__(*args, **kwargs)
        self.batch_size = batch_size

    def setup(self):
        """Create storage."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = JSONFileStorage(self.temp_dir)
        self.counter = 0

    def teardown(self):
        """Cleanup."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run_once(self):
        """Write records."""
        for i in range(self.batch_size):
            self.storage.create("test_collection", {
                "id": f"test_{self.counter}_{i}",
                "data": "test" * 10
            })
        self.counter += 1


class StorageReadBenchmark(Benchmark):
    """Benchmark storage read operations."""

    def setup(self):
        """Create storage and populate data."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = JSONFileStorage(self.temp_dir)

        # Pre-populate data
        for i in range(1000):
            self.storage.create("test_collection", {
                "id": f"test_{i}",
                "data": "test" * 10
            })

    def teardown(self):
        """Cleanup."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run_once(self):
        """Read records."""
        self.storage.read("test_collection", "test_500")


# =================================================================
# Memory Benchmarks
# =================================================================

class MemoryWriteBenchmark(Benchmark):
    """Benchmark memory write operations."""

    def setup(self):
        """Create memory manager."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = JSONFileStorage(self.temp_dir)
        self.manager = MemoryManager(storage=self.storage, identity_id="test_agent")

    def teardown(self):
        """Cleanup."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run_once(self):
        """Write memory."""
        self.manager.write_memory(
            tier="short_term",
            content="test memory content"
        )


# =================================================================
# Snapshot Benchmarks
# =================================================================

class SnapshotCreationBenchmark(Benchmark):
    """Benchmark snapshot creation."""

    def setup(self):
        """Create test state."""
        self.identity_state = {"identities": [f"id_{i}" for i in range(10)]}
        self.continuity_state = {"sessions": [f"session_{i}" for i in range(20)]}
        self.vault_state = {"entries": [f"entry_{i}" for i in range(50)]}

    def run_once(self):
        """Create snapshot."""
        capture_snapshot(
            identity_state=self.identity_state,
            continuity_state=self.continuity_state,
            vault_state=self.vault_state
        )


# =================================================================
# Benchmark Suite
# =================================================================

class BenchmarkSuite:
    """Collection of benchmarks."""

    def __init__(self):
        """Initialize benchmark suite."""
        self.benchmarks: List[Benchmark] = []
        self.results: List[BenchmarkResult] = []

    def add_benchmark(self, benchmark: Benchmark):
        """Add benchmark to suite."""
        self.benchmarks.append(benchmark)

    def run_all(self) -> List[BenchmarkResult]:
        """Run all benchmarks."""
        print(f"Running {len(self.benchmarks)} benchmarks...\n")

        for i, benchmark in enumerate(self.benchmarks, 1):
            print(f"[{i}/{len(self.benchmarks)}] Running {benchmark.name}...", end=" ")
            result = benchmark.run()
            self.results.append(result)
            print(f"✓ ({result.mean_time*1000:.2f}ms avg)")

        return self.results

    def print_results(self):
        """Print benchmark results in tabular format."""
        print("\n" + "="*100)
        print("Benchmark Results")
        print("="*100)
        print(f"{'Benchmark':<40} {'Iterations':>10} {'Mean':>12} {'Median':>12} {'P95':>12} {'Ops/sec':>12}")
        print("-"*100)

        for result in self.results:
            print(f"{result.name:<40} {result.iterations:>10} "
                  f"{result.mean_time*1000:>11.2f}ms {result.median_time*1000:>11.2f}ms "
                  f"{result.p95_time*1000:>11.2f}ms {result.operations_per_second:>11.1f}")

        print("="*100)

    def export_json(self, filepath: Path):
        """Export results to JSON file."""
        data = {
            "timestamp": time.time(),
            "benchmarks": [r.to_dict() for r in self.results]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


def create_default_suite(iterations: int = 100) -> BenchmarkSuite:
    """Create default benchmark suite."""
    suite = BenchmarkSuite()

    # Checksum benchmarks
    suite.add_benchmark(ChecksumBenchmark("Checksum: State", iterations=iterations))
    suite.add_benchmark(FileChecksumBenchmark("Checksum: File", iterations=iterations))

    # Identity benchmarks
    suite.add_benchmark(IdentityCreationBenchmark("Identity: Creation", iterations=min(50, iterations)))
    suite.add_benchmark(SigningBenchmark("Identity: Signing", iterations=iterations))

    # Storage benchmarks
    suite.add_benchmark(StorageWriteBenchmark("Storage: Write (100 records)", iterations=min(10, iterations), batch_size=100))
    suite.add_benchmark(StorageReadBenchmark("Storage: Read", iterations=iterations))

    # Memory benchmarks
    suite.add_benchmark(MemoryWriteBenchmark("Memory: Write", iterations=min(50, iterations)))

    # Snapshot benchmarks
    suite.add_benchmark(SnapshotCreationBenchmark("Snapshot: Creation", iterations=iterations))

    return suite
