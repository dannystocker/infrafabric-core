#!/usr/bin/env python3
"""
Forensic secret-by-secret analysis
Compare detection methodology: component pairs vs individual secrets
"""
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import importlib.util
spec = importlib.util.spec_from_file_location(
    "yologuard_v3",
    str(Path(__file__).resolve().parents[1] / 'src' / 'IF.yologuard_v3.py')
)
yologuard_v3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yologuard_v3)
SecretRedactorV3 = yologuard_v3.SecretRedactorV3

LEAKY_REPO_PATH = Path(__file__).resolve().parent / 'leaky-repo'
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

EXCLUDE_DIRS = {'.git', '.leaky-meta'}

redactor = SecretRedactorV3()

# Detailed analysis by file
file_detections = defaultdict(list)
total_individual = 0
total_usable = 0
total_component = 0

all_files = [
    f for f in LEAKY_REPO_PATH.rglob('*')
    if f.is_file() and not any(exc in f.parts for exc in EXCLUDE_DIRS)
]

for file_path in sorted(all_files):
    rel_path = str(file_path.relative_to(LEAKY_REPO_PATH))
    if rel_path not in GROUND_TRUTH:
        continue

    secrets = redactor.scan_file(file_path)

    for secret in secrets:
        total_individual += 1
        classification = secret.get('classification', 'usable')

        if classification == 'component':
            total_component += 1
        else:
            total_usable += 1

        file_detections[rel_path].append({
            'pattern': secret['pattern'],
            'line': secret['line'],
            'classification': classification,
            'match_preview': secret['match'][:30],
        })

# Print detailed analysis
print("=" * 100)
print("FORENSIC SECRET-BY-SECRET ANALYSIS")
print("=" * 100)
print()

# Show files with discrepancies
discrepancy_files = []
for file, expected in sorted(GROUND_TRUTH.items()):
    detections = file_detections[file]
    detected_count = len(detections)
    usable_count = sum(1 for d in detections if d['classification'] == 'usable')
    component_count = sum(1 for d in detections if d['classification'] == 'component')

    if detected_count != expected:
        discrepancy_files.append((file, expected, detected_count, usable_count, component_count, detections))

# Show files matching ground truth
matching_files = []
for file, expected in sorted(GROUND_TRUTH.items()):
    detections = file_detections[file]
    detected_count = len(detections)
    if detected_count == expected:
        matching_files.append((file, expected))

print(f"Files MATCHING ground truth: {len(matching_files)}/42")
print(f"Files with DISCREPANCIES:   {len(discrepancy_files)}/42")
print()

# Detailed breakdown of discrepancies
if discrepancy_files:
    print("=" * 100)
    print("FILES WITH DETECTION DISCREPANCIES:")
    print("=" * 100)
    print()

    for file, expected, detected, usable, component, detections in discrepancy_files:
        print(f"\n📁 {file}")
        print(f"   Ground Truth: {expected} secrets")
        print(f"   Detected:     {detected} secrets ({usable} usable + {component} component)")
        print(f"   Discrepancy:  {detected - expected:+d}")
        print(f"   Details:")
        for i, detection in enumerate(detections, 1):
            marker = "🔧" if detection['classification'] == 'component' else "🔑"
            print(f"     {i}. {marker} Line {detection['line']:3d}: {detection['pattern']:<30} | {detection['match_preview']}")

# Summary statistics
print()
print("=" * 100)
print("COUNTING METHODOLOGY COMPARISON:")
print("=" * 100)
print()
print(f"Ground Truth (Leaky Repo metadata):        96 secrets")
print(f"Individual detections (all):               {total_individual} detections")
print(f"  ├─ Usable secrets:                       {total_usable} detections")
print(f"  └─ Component patterns (FTP_USER, etc.):  {total_component} detections")
print()
print(f"Recall (individual, all):     {total_individual}/96 = {total_individual/96*100:.2f}%")
print(f"Recall (usable-only):         {total_usable}/96 = {total_usable/96*100:.2f}%")
print()
print("=" * 100)
print("INTERPRETATION:")
print("=" * 100)
print()
print(f"If counting COMPONENT patterns separately (GitHub parity):")
print(f"  → {total_individual}/96 = {total_individual/96*100:.2f}% recall (component-inclusive)")
print()
print(f"If excluding COMPONENT patterns (usable-only standard):")
print(f"  → {total_usable}/96 = {total_usable/96*100:.2f}% recall (usable-only)")
print()
print(f"Discrepancy files: {len(discrepancy_files)} files differ from ground truth")
print(f"Likely cause: Ground truth counts secrets differently than individual patterns")
