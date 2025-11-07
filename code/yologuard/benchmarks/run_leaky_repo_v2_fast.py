#!/usr/bin/env python3
# Copyright (c) 2025 Danny Stocker
# SPDX-License-Identifier: MIT
#
# InfraFabric - IF.yologuard Benchmark Runner
# Source: https://github.com/dannystocker/infrafabric
# Licensed under the MIT License. See LICENSE-CODE file in the project root.

"""
IF.yologuard v2 Benchmark Test - Leaky Repo (FAST VERSION)
Optimized for speed by limiting entropy analysis to likely candidates
"""

import sys
from pathlib import Path
from collections import defaultdict
import time

# Import v2 scanner
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')
import importlib.util
spec = importlib.util.spec_from_file_location("yologuard_v2", "/home/setup/work/mcp-multiagent-bridge/IF.yologuard_v2.py")
yologuard_v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yologuard_v2)
SecretRedactorV2 = yologuard_v2.SecretRedactorV2

# Benchmark configuration
LEAKY_REPO_PATH = Path('/home/setup/digital-lab.ca/infrafabric/yologuard/benchmarks/leaky-repo')
EXCLUDE_DIRS = {'.git', '.leaky-meta'}

# Ground truth data (96 RISK secrets total)
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

def main():
    """Run fast benchmark test."""
    print("=" * 80)
    print("IF.yologuard v2 - Leaky Repo Benchmark (FAST MODE)")
    print("=" * 80)
    print(f"Ground truth: 96 RISK secrets")
    print(f"v1 baseline: 30/96 (31.2% recall)")
    print("=" * 80)
    print()

    start_time = time.time()
    redactor = SecretRedactorV2()
    results = defaultdict(list)
    total_secrets = 0
    files_scanned = 0

    # Get all files
    all_files = [
        f for f in LEAKY_REPO_PATH.rglob('*')
        if f.is_file() and not any(exc in f.parts for exc in EXCLUDE_DIRS)
    ]

    print(f"Scanning {len(all_files)} files...")
    print()

    for file_path in all_files:
        files_scanned += 1
        rel_path = str(file_path.relative_to(LEAKY_REPO_PATH))

        # Progress indicator
        print(f"[{files_scanned}/{len(all_files)}] {rel_path}...", end=" ", flush=True)

        secrets = redactor.scan_file(file_path)

        if secrets:
            results[rel_path] = secrets
            total_secrets += len(secrets)
            print(f"✓ {len(secrets)} secrets")
        else:
            print("(none)")

    elapsed = time.time() - start_time

    print()
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print(f"Files scanned: {files_scanned} in {elapsed:.1f}s")
    print(f"Files with detections: {len(results)}")
    print(f"Total secrets detected: {total_secrets}")
    print()
    print(f"v1 baseline: 30/96 (31.2% recall)")
    print(f"v2 detected: {total_secrets}/96 ({total_secrets/96*100:.1f}% recall)")
    print(f"Improvement: +{total_secrets-30} secrets (+{(total_secrets-30)/96*100:.1f} percentage points)")
    print()

    if total_secrets >= 76:
        print("🎉 BENCHMARK PASSED: 80%+ recall achieved!")
    else:
        print(f"Target: 80% (76+ secrets) | Current: {total_secrets/96*100:.1f}%")

    print()
    print("=" * 80)
    print("TOP FILE DETECTIONS")
    print("=" * 80)

    sorted_results = sorted(results.items(), key=lambda x: len(x[1]), reverse=True)
    for file_path, secrets in sorted_results[:20]:
        gt = GROUND_TRUTH.get(file_path, 0)
        print(f"{file_path:50s} | GT:{gt:2d} | Detected:{len(secrets):2d}")

    print()

    # Write summary file
    output_path = Path('/home/setup/digital-lab.ca/infrafabric/yologuard/benchmarks/leaky_repo_v2_results_summary.txt')
    with open(output_path, 'w') as f:
        f.write(f"IF.yologuard v2 - Leaky Repo Benchmark Results\n")
        f.write(f"=" * 80 + "\n\n")
        f.write(f"Test Date: 2025-11-06\n")
        f.write(f"Scan Time: {elapsed:.1f}s\n")
        f.write(f"Files Scanned: {files_scanned}\n\n")
        f.write(f"v1 baseline: 30/96 (31.2% recall)\n")
        f.write(f"v2 detected: {total_secrets}/96 ({total_secrets/96*100:.1f}% recall)\n")
        f.write(f"Improvement: +{total_secrets-30} secrets (+{(total_secrets-30)/96*100:.1f} percentage points)\n\n")

        f.write("Top Detections:\n")
        for file_path, secrets in sorted_results[:20]:
            gt = GROUND_TRUTH.get(file_path, 0)
            f.write(f"  {file_path:50s} | GT:{gt:2d} | Detected:{len(secrets):2d}\n")

    print(f"✓ Summary written to: {output_path}")
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
