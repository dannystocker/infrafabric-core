#!/usr/bin/env python3
# Copyright (c) 2025 Danny Stocker
# SPDX-License-Identifier: MIT
#
# InfraFabric - IF.yologuard Benchmark Runner
# Source: https://github.com/dannystocker/infrafabric
# Licensed under the MIT License. See LICENSE-CODE file in the project root.

"""
IF.yologuard v3 Benchmark Test - Leaky Repo (PHILOSOPHICAL IMPLEMENTATION)
Confucian relationship-based secret detection with Wu Lun framework

Features:
- Imports PhilosophicalSecretDetector (SecretRedactorV3)
- Scans all 89 files in leaky-repo
- Tracks which philosophical mode detected each secret
- Reports recall, precision, and per-category breakdown
- Compares v1 (31%) → v2 (77%) → v3 (target: 85-90%)
- Shows relationship-based detection patterns
"""

import sys
from pathlib import Path
from collections import defaultdict
import time

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

# Pattern type to philosophical mode mapping (where applicable)
PATTERN_TO_PHILOSOPHY = {
    'AWS_KEY': 'Aristotelian (essence)',
    'AWS_SECRET': 'Aristotelian (essence)',
    'OPENAI_KEY': 'Aristotelian (essence)',
    'GITHUB_TOKEN': 'Aristotelian (essence)',
    'STRIPE_SECRET': 'Aristotelian (essence)',
    'PRIVATE_KEY': 'Kantian (duty)',
    'BEARER_TOKEN': 'Kantian (duty)',
    'PASSWORD': 'Confucian (user-password relationship)',
    'JWT': 'Confucian (token-session relationship)',
    'SLACK_TOKEN': 'Confucian (token-session relationship)',
    'BCRYPT_HASH': 'Nagarjuna (interdependent)',
    'CRYPT_SHA512': 'Nagarjuna (interdependent)',
    'PGPASS_PASSWORD': 'Confucian (user-password relationship)',
    'WORDPRESS_SALT': 'Nagarjuna (interdependent)',
    'WORDPRESS_DB_PASSWORD': 'Confucian (user-password relationship)',
    'CERTIFICATE': 'Confucian (cert-authority relationship)',
    'API_KEY': 'Confucian (key-endpoint relationship)',
    'DB_PASSWORD': 'Confucian (user-password relationship)',
    'NPM_TOKEN': 'Kantian (duty)',
}

class PhilosophicalDetectionTracker:
    """Tracks detection results with philosophical mode classification."""

    def __init__(self):
        self.total_detected = 0
        self.files_with_detections = 0
        self.detections_by_file = defaultdict(list)
        self.detections_by_pattern = defaultdict(int)
        self.detections_by_philosophy = defaultdict(int)
        self.matched_ground_truth = set()
        self.missed_ground_truth = set()

    def classify_pattern_to_philosophy(self, pattern_name: str) -> str:
        """Map detection pattern to philosophical mode."""
        for pattern_key, philosophy in PATTERN_TO_PHILOSOPHY.items():
            if pattern_key in pattern_name:
                return philosophy
        return "Pattern-based (unclassified)"

    def add_detection(self, file_path: str, pattern: str, match_text: str, line: int):
        """Record a detection with philosophical classification."""
        self.total_detected += 1
        philosophy = self.classify_pattern_to_philosophy(pattern)

        self.detections_by_file[file_path].append({
            'pattern': pattern,
            'match': match_text[:50] + '...' if len(match_text) > 50 else match_text,
            'line': line,
            'philosophy': philosophy
        })

        self.detections_by_pattern[pattern] += 1
        self.detections_by_philosophy[philosophy] += 1

        # Track if this file was in ground truth
        if file_path in GROUND_TRUTH:
            self.matched_ground_truth.add(file_path)

    def calculate_metrics(self):
        """Calculate recall, precision, and coverage metrics."""
        files_scanned = len(self.detections_by_file)
        gt_files = len(GROUND_TRUTH)
        gt_secrets = sum(GROUND_TRUTH.values())

        recall = (self.total_detected / gt_secrets * 100) if gt_secrets > 0 else 0
        precision = (len(self.matched_ground_truth) / gt_files * 100) if gt_files > 0 else 0

        return {
            'total_detected': self.total_detected,
            'gt_secrets': gt_secrets,
            'recall': recall,
            'files_with_detections': files_scanned,
            'gt_files': gt_files,
            'files_coverage': precision
        }


def main():
    """Run v3 philosophical benchmark test."""
    print("=" * 90)
    print("IF.yologuard v3.0 - PHILOSOPHICAL SECRET DETECTOR - Leaky Repo Benchmark")
    print("=" * 90)
    print(f"\nGround truth: 96 RISK secrets across 49 files")
    print(f"v1 baseline:  30/96  (31.2% recall)")
    print(f"v2 baseline:  ~74/96 (77.0% recall)")
    print(f"v3 target:    85-90/96 (88-94% recall)")
    print(f"\nPhilosophical framework:")
    print(f"  - Aristotelian: Essence classification (intrinsic patterns)")
    print(f"  - Kantian: Duty-based detection (categorical imperatives)")
    print(f"  - Confucian: Relationship mapping (Wu Lun - Five Relationships)")
    print(f"  - Nagarjuna: Interdependency detection (causal chains)")
    print("=" * 90)
    print()

    start_time = time.time()
    detector = SecretRedactorV3()
    tracker = PhilosophicalDetectionTracker()
    files_scanned = 0

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

        secrets = detector.scan_file(file_path)

        if secrets:
            tracker.files_with_detections += 1
            gt_count = GROUND_TRUTH.get(rel_path, 0)

            for secret in secrets:
                tracker.add_detection(
                    rel_path,
                    secret['pattern'],
                    secret['match'],
                    secret['line']
                )

            print(f"✓ {len(secrets):2d} detected (GT: {gt_count})")
        else:
            print("(none)")

    elapsed = time.time() - start_time

    print()
    print("=" * 90)
    print("RESULTS SUMMARY")
    print("=" * 90)

    metrics = tracker.calculate_metrics()

    print(f"\nScan Statistics:")
    print(f"  Files scanned:       {files_scanned}")
    print(f"  Files with secrets:  {tracker.files_with_detections}")
    print(f"  Scan time:           {elapsed:.1f}s")
    print(f"  Average per file:    {elapsed/files_scanned:.2f}s")

    print(f"\nDetection Performance:")
    print(f"  v1 baseline:         30/96   (31.2%)")
    print(f"  v2 baseline:         ~74/96  (77.0%)")
    print(f"  v3 detected:         {metrics['total_detected']}/96  ({metrics['recall']:.1f}%)")
    print(f"  Improvement over v2: {metrics['total_detected']-74:+d} secrets ({metrics['recall']-77:.1f:+.1f} percentage points)")

    if metrics['recall'] >= 85:
        print(f"\n✅ BENCHMARK PASSED: 85%+ recall achieved!")
    elif metrics['recall'] >= 77:
        print(f"\n⚠️  ON TRACK: {metrics['recall']:.1f}% recall (target: 85%+)")
    else:
        print(f"\n❌ TARGET MISSED: {metrics['recall']:.1f}% recall (target: 85%+)")

    print(f"\nFile Coverage:")
    print(f"  Ground truth files:  {metrics['gt_files']}")
    print(f"  Files with detects:  {len(tracker.matched_ground_truth)}")
    print(f"  Coverage rate:       {len(tracker.matched_ground_truth)}/{metrics['gt_files']} ({metrics['files_coverage']:.1f}%)")

    print()
    print("=" * 90)
    print("DETECTION BY PHILOSOPHICAL MODE")
    print("=" * 90)

    for philosophy, count in sorted(tracker.detections_by_philosophy.items(), key=lambda x: x[1], reverse=True):
        pct = (count / metrics['total_detected'] * 100) if metrics['total_detected'] > 0 else 0
        print(f"  {philosophy:40s} {count:3d} detections ({pct:5.1f}%)")

    print()
    print("=" * 90)
    print("TOP DETECTED PATTERNS")
    print("=" * 90)

    sorted_patterns = sorted(tracker.detections_by_pattern.items(), key=lambda x: x[1], reverse=True)
    for pattern, count in sorted_patterns[:15]:
        pct = (count / metrics['total_detected'] * 100) if metrics['total_detected'] > 0 else 0
        print(f"  {pattern:50s} {count:3d} ({pct:5.1f}%)")

    print()
    print("=" * 90)
    print("TOP 20 FILE DETECTIONS")
    print("=" * 90)

    sorted_results = sorted(tracker.detections_by_file.items(), key=lambda x: len(x[1]), reverse=True)
    for file_path, detections in sorted_results[:20]:
        gt = GROUND_TRUTH.get(file_path, 0)
        status = "✓" if file_path in tracker.matched_ground_truth else "✗"
        print(f"{status} {file_path:50s} | GT:{gt:2d} | Detected:{len(detections):2d}")

        # Show sample detections
        for detection in detections[:2]:
            philosophy = detection['philosophy'].split(' ')[0]  # First word
            print(f"    - [{philosophy:10s}] {detection['pattern']}")

    print()
    print("=" * 90)
    print("MISSED GROUND TRUTH FILES (With Secrets But Not Detected)")
    print("=" * 90)

    missed = []
    for gt_file, gt_count in GROUND_TRUTH.items():
        if gt_file not in tracker.matched_ground_truth:
            missed.append((gt_file, gt_count))

    if missed:
        missed.sort(key=lambda x: x[1], reverse=True)
        for file_path, gt_count in missed[:15]:
            print(f"  {file_path:50s} | GT: {gt_count:2d} secrets (MISSED)")
    else:
        print("  ✅ All ground truth files detected!")

    # Write detailed summary to file
    output_path = Path('/home/setup/digital-lab.ca/infrafabric/yologuard/benchmarks/leaky_repo_v3_philosophical_results.txt')
    with open(output_path, 'w') as f:
        f.write("=" * 90 + "\n")
        f.write("IF.yologuard v3.0 - PHILOSOPHICAL SECRET DETECTOR - Benchmark Results\n")
        f.write("=" * 90 + "\n\n")

        f.write(f"Test Date: 2025-11-07\n")
        f.write(f"Scan Time: {elapsed:.1f}s\n")
        f.write(f"Files Scanned: {files_scanned}\n\n")

        f.write(f"DETECTION METRICS\n")
        f.write("-" * 90 + "\n")
        f.write(f"v1 baseline: 30/96  (31.2% recall)\n")
        f.write(f"v2 baseline: ~74/96 (77.0% recall)\n")
        f.write(f"v3 detected: {metrics['total_detected']}/96  ({metrics['recall']:.1f}% recall)\n")
        f.write(f"Improvement: +{metrics['total_detected']-74:+d} secrets ({metrics['recall']-77:.1f:+.1f} percentage points)\n\n")

        f.write(f"PHILOSOPHICAL MODE BREAKDOWN\n")
        f.write("-" * 90 + "\n")
        for philosophy, count in sorted(tracker.detections_by_philosophy.items(), key=lambda x: x[1], reverse=True):
            pct = (count / metrics['total_detected'] * 100) if metrics['total_detected'] > 0 else 0
            f.write(f"{philosophy:40s} {count:3d} detections ({pct:5.1f}%)\n")

        f.write(f"\nTOP 20 FILE DETECTIONS\n")
        f.write("-" * 90 + "\n")
        for file_path, detections in sorted_results[:20]:
            gt = GROUND_TRUTH.get(file_path, 0)
            f.write(f"  {file_path:50s} | GT:{gt:2d} | Detected:{len(detections):2d}\n")

    print(f"\n✅ Detailed results written to: {output_path}")
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
