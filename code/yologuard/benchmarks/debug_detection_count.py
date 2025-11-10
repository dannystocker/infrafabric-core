#!/usr/bin/env python3
"""
Forensic debug: Compare predecode_and_rescan vs scan_file counting
"""
import sys
from pathlib import Path

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

redactor = SecretRedactorV3()

total_predecode = 0
total_scan_file = 0

print("File-by-file comparison:")
print("-" * 80)
print(f"{'File':<45} {'GT':<5} {'Raw':<6} {'Dedup':<6} {'Diff'}")
print("-" * 80)

for file, expected in sorted(GROUND_TRUTH.items()):
    file_path = LEAKY_REPO_PATH / file
    if not file_path.exists():
        print(f"{file:<45} {expected:<5} MISSING")
        continue

    # Method 1: predecode_and_rescan (RAW, no dedup)
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        raw_matches = redactor.predecode_and_rescan(content)
        raw_count = len(raw_matches)
    except:
        raw_count = 0

    # Method 2: scan_file (WITH dedup)
    dedup_secrets = redactor.scan_file(file_path)
    dedup_count = len(dedup_secrets)

    total_predecode += raw_count
    total_scan_file += dedup_count

    diff = raw_count - dedup_count
    marker = " ⚠️" if diff > 0 else ""
    print(f"{file:<45} {expected:<5} {raw_count:<6} {dedup_count:<6} {diff:+d}{marker}")

print("-" * 80)
print(f"{'TOTAL':<45} {96:<5} {total_predecode:<6} {total_scan_file:<6} {total_predecode - total_scan_file:+d}")
print()
print(f"Ground truth:          96 secrets")
print(f"predecode_and_rescan:  {total_predecode} detections (RAW, no dedup)")
print(f"scan_file:             {total_scan_file} detections (WITH dedup)")
print(f"Over-counting:         {total_predecode - total_scan_file} duplicates")
print()
print(f"Correct recall:        {total_scan_file}/96 = {total_scan_file/96*100:.2f}%")
