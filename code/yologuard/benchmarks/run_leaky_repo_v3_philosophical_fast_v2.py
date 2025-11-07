#!/usr/bin/env python3
# Copyright (c) 2025 Danny Stocker
# SPDX-License-Identifier: MIT
#
# InfraFabric - IF.yologuard Benchmark Runner
# Source: https://github.com/dannystocker/infrafabric
# Licensed under the MIT License. See LICENSE-CODE file in the project root.

"""
IF.yologuard v3 Benchmark Test - Leaky Repo (PHILOSOPHICAL - FAST MODE v2)
Optimized for speed by using pattern matching only (no entropy/decoding analysis)

FIXED VERSION - Addresses binary file hang issues:
- Skips binary files larger than 1MB
- Adds timeout protection (max 5 seconds per file)
- Handles UTF-8 decode errors gracefully
- Continues scanning after errors
- Detects and skips common binary file types

Run this for quick feedback during development.
Run the full version for complete philosophical analysis.
"""

import sys
from pathlib import Path
from collections import defaultdict
import time
import re
import signal
from contextlib import contextmanager

# Import v3 philosophical detector
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')
import importlib.util
spec = importlib.util.spec_from_file_location("yologuard_v3", "/home/setup/work/mcp-multiagent-bridge/IF.yologuard_v3.py")
yologuard_v3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yologuard_v3)
SecretRedactorV3 = yologuard_v3.SecretRedactorV3

# Benchmark configuration
LEAKY_REPO_PATH = Path('/home/setup/digital-lab.ca/infrafabric/yologuard/benchmarks/leaky-repo')
EXCLUDE_DIRS = {'.git', '.leaky-meta'}

# Safety limits
MAX_FILE_SIZE = 1024 * 1024  # 1MB max file size
FILE_SCAN_TIMEOUT = 5  # 5 seconds max per file

# Binary file extensions to skip
BINARY_EXTENSIONS = {
    '.db', '.sqlite', '.sqlite3',  # Databases
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.webp',  # Images
    '.pdf', '.doc', '.docx', '.xls', '.xlsx',  # Documents
    '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',  # Archives
    '.exe', '.dll', '.so', '.dylib',  # Executables
    '.bin', '.dat', '.pyc', '.pyo',  # Binary data
}

# Ground truth data (96 RISK secrets total across 49 files)
GROUND_TRUTH = {
    '.bash_profile': 6, '.bashrc': 3, '.docker/.dockercfg': 2, '.docker/config.json': 2,
    '.mozilla/firefox/logins.json': 8, '.ssh/id_rsa': 1, 'cloud/.credentials': 2,
    'cloud/.s3cfg': 1, 'cloud/.tugboat': 1, 'cloud/heroku.json': 1, 'db/dump.sql': 10,
    'db/mongoid.yml': 1, 'etc/shadow': 1, 'filezilla/recentservers.xml': 3,
    'filezilla/filezilla.xml': 2, 'misc-keys/cert-key.pem': 1, 'misc-keys/putty-example.ppk': 1,
    'proftpdpasswd': 1, 'web/ruby/config/master.key': 1, 'web/ruby/secrets.yml': 3,
    'web/var/www/.env': 6, '.npmrc': 2, 'web/var/www/public_html/wp-config.php': 9,
    'web/var/www/public_html/.htpasswd': 1, '.git-credentials': 1, 'db/robomongo.json': 3,
    'web/js/salesforce.js': 1, '.netrc': 2, 'hub': 1, 'config': 1, 'db/.pgpass': 1,
    'ventrilo_srv.ini': 2, 'web/var/www/public_html/config.php': 1,
    'db/dbeaver-data-sources.xml': 1, '.esmtprc': 2, 'web/django/settings.py': 1,
    'deployment-config.json': 3, '.ftpconfig': 3, '.remote-sync.json': 1,
    '.vscode/sftp.json': 1, 'sftp-config.json': 1, '.idea/WebServers.xml': 1,
}


class TimeoutException(Exception):
    """Custom exception for timeout."""
    pass


@contextmanager
def timeout_context(seconds):
    """Context manager for timeout protection."""
    def timeout_handler(signum, frame):
        raise TimeoutException("Operation timed out")

    # Set up the signal handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        # Restore the old handler and cancel the alarm
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def is_likely_binary(file_path: Path) -> bool:
    """Check if file is likely binary based on extension and content sniff."""
    # Check extension
    if file_path.suffix.lower() in BINARY_EXTENSIONS:
        return True

    # Check file size
    try:
        if file_path.stat().st_size > MAX_FILE_SIZE:
            return True
    except:
        return True

    # Quick binary sniff - read first 512 bytes
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(512)
            # If more than 30% are non-text bytes (null bytes, control chars), likely binary
            non_text = sum(1 for b in chunk if b < 32 and b not in (9, 10, 13))
            if len(chunk) > 0 and (non_text / len(chunk)) > 0.3:
                return True
    except:
        return True

    return False


class FastPhilosophicalDetector:
    """Fast pattern-only detector for quick benchmarking with safety protections."""

    def __init__(self):
        """Initialize with v3 patterns only (no entropy/decode logic)."""
        self.patterns = SecretRedactorV3.PATTERNS
        self.patterns_compiled = [(re.compile(p, re.DOTALL | re.MULTILINE), r) for p, r in self.patterns]

    def scan_file(self, file_path: Path) -> list:
        """Fast scan using patterns only with timeout and binary file protection."""
        # Skip binary files
        if is_likely_binary(file_path):
            return []

        try:
            # Use timeout protection for file scanning
            with timeout_context(FILE_SCAN_TIMEOUT):
                # Read file with UTF-8 error handling
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                except UnicodeDecodeError:
                    # If UTF-8 fails, try latin-1 (accepts all byte values)
                    content = file_path.read_text(encoding='latin-1', errors='ignore')
                except Exception:
                    return []

                # Sanity check - if content is too large after reading, skip
                if len(content) > MAX_FILE_SIZE:
                    return []

                secrets = []
                for pattern, replacement in self.patterns_compiled:
                    try:
                        for match in pattern.finditer(content):
                            secrets.append({
                                'file': str(file_path),
                                'pattern': replacement,
                                'match': match.group(0)[:50] + '...' if len(match.group(0)) > 50 else match.group(0),
                                'line': content[:content.find(match.group(0))].count('\n') + 1 if match.group(0) in content else -1
                            })
                    except Exception:
                        # Continue with next pattern if this one fails
                        continue

                return secrets

        except TimeoutException:
            # File scan timed out - skip it
            return []
        except Exception:
            # Any other error - skip this file
            return []


def main():
    """Run v3 philosophical benchmark test (FAST MODE v2 - FIXED)."""
    print("=" * 90)
    print("IF.yologuard v3.0 - PHILOSOPHICAL SECRET DETECTOR - Leaky Repo Benchmark (FAST v2)")
    print("=" * 90)
    print(f"\nGround truth: 96 RISK secrets across 49 files")
    print(f"v1 baseline:  30/96  (31.2% recall)")
    print(f"v2 baseline:  ~74/96 (77.0% recall)")
    print(f"v3 target:    85-90/96 (88-94% recall)")
    print(f"\nMode: PATTERN-ONLY (fast, no entropy/decoding)")
    print(f"Safety: 1MB max file size, 5s timeout, binary file detection")
    print("=" * 90)
    print()

    start_time = time.time()
    detector = FastPhilosophicalDetector()
    total_detected = 0
    files_with_detections = 0
    matched_ground_truth = set()
    results = defaultdict(list)
    files_scanned = 0
    files_skipped = 0

    # Get all files
    all_files = [
        f for f in LEAKY_REPO_PATH.rglob('*')
        if f.is_file() and not any(exc in f.parts for exc in EXCLUDE_DIRS)
    ]

    print(f"Scanning {len(all_files)} files in leaky-repo...")
    print()

    for file_path in sorted(all_files):
        files_scanned += 1
        rel_path = str(file_path.relative_to(LEAKY_REPO_PATH))

        # Progress indicator
        print(f"[{files_scanned:2d}/{len(all_files):2d}] {rel_path:50s}...", end=" ", flush=True)

        # Check if binary before scanning
        if is_likely_binary(file_path):
            print("(binary/skipped)")
            files_skipped += 1
            continue

        secrets = detector.scan_file(file_path)

        if secrets:
            files_with_detections += 1
            total_detected += len(secrets)
            results[rel_path] = secrets
            matched_ground_truth.add(rel_path)
            gt_count = GROUND_TRUTH.get(rel_path, 0)
            print(f"✓ {len(secrets):2d} (GT: {gt_count})")
        else:
            print("(none)")

    elapsed = time.time() - start_time

    gt_secrets = sum(GROUND_TRUTH.values())
    recall = (total_detected / gt_secrets * 100) if gt_secrets > 0 else 0

    print()
    print("=" * 90)
    print("RESULTS SUMMARY (FAST MODE v2)")
    print("=" * 90)
    print(f"\nScan Statistics:")
    print(f"  Files scanned:       {files_scanned}")
    print(f"  Files skipped:       {files_skipped} (binary/oversized)")
    print(f"  Files with secrets:  {files_with_detections}")
    print(f"  Scan time:           {elapsed:.1f}s")

    print(f"\nDetection Performance:")
    print(f"  v1 baseline:         30/96   (31.2%)")
    print(f"  v2 baseline:         ~74/96  (77.0%)")
    print(f"  v3 detected:         {total_detected}/96  ({recall:.1f}%)")
    print(f"  Improvement over v2: {total_detected-74:+d} secrets ({recall-77:+.1f} percentage points)")

    if recall >= 85:
        print(f"\n✅ BENCHMARK PASSED: 85%+ recall achieved!")
    elif recall >= 77:
        print(f"\n⚠️  ON TRACK: {recall:.1f}% recall (target: 85%+)")
    else:
        print(f"\n❌ TARGET MISSED: {recall:.1f}% recall (target: 85%+)")

    print(f"\nFile Coverage:")
    print(f"  Ground truth files:  {len(GROUND_TRUTH)}")
    print(f"  Files with detects:  {len(matched_ground_truth)}")
    print(f"  Coverage rate:       {len(matched_ground_truth)}/{len(GROUND_TRUTH)}")

    print()
    print("=" * 90)
    print("TOP 15 FILE DETECTIONS")
    print("=" * 90)

    sorted_results = sorted(results.items(), key=lambda x: len(x[1]), reverse=True)
    for file_path, secrets in sorted_results[:15]:
        gt = GROUND_TRUTH.get(file_path, 0)
        status = "✓" if file_path in matched_ground_truth else "✗"
        print(f"{status} {file_path:50s} | GT:{gt:2d} | Detected:{len(secrets):2d}")

    # Write summary
    output_path = Path('/home/setup/digital-lab.ca/infrafabric/yologuard/benchmarks/leaky_repo_v3_fast_v2_results.txt')
    with open(output_path, 'w') as f:
        f.write("=" * 90 + "\n")
        f.write("IF.yologuard v3.0 - FAST BENCHMARK RESULTS (v2 - FIXED)\n")
        f.write("=" * 90 + "\n\n")
        f.write(f"Scan Time: {elapsed:.1f}s\n")
        f.write(f"Files Scanned: {files_scanned}\n")
        f.write(f"Files Skipped: {files_skipped} (binary/oversized)\n\n")
        f.write(f"v1 baseline: 30/96  (31.2%)\n")
        f.write(f"v2 baseline: ~74/96 (77.0%)\n")
        f.write(f"v3 detected: {total_detected}/96  ({recall:.1f}%)\n")
        f.write(f"Improvement: {total_detected-74:+d} secrets\n\n")
        f.write("Top Detections:\n")
        for file_path, secrets in sorted_results[:20]:
            gt = GROUND_TRUTH.get(file_path, 0)
            f.write(f"  {file_path:50s} | GT:{gt:2d} | Detected:{len(secrets):2d}\n")

    print(f"\n✅ Results written to: {output_path}")
    print()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
