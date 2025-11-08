#!/usr/bin/env python3
"""
Yolo Stats: quick dual-mode stats over a directory.

Outputs total detections, usable/component split, and severity distribution.

Usage:
  python3 infrafabric/code/yologuard/tools/yolo_stats.py --root /path/to/repo
"""
import argparse, json
from pathlib import Path
import importlib.util


def load_redactor(project_root: Path):
    src = project_root / 'code' / 'yologuard' / 'src' / 'IF.yologuard_v3.py'
    spec = importlib.util.spec_from_file_location('yologuard_v3', str(src))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.SecretRedactorV3()


def main():
    ap = argparse.ArgumentParser(description='IF.yologuard dual-mode stats')
    ap.add_argument('--root', required=True, help='Directory to scan recursively')
    ap.add_argument('--exclude', action='append', default=['.git', 'node_modules', 'dist', 'build'], help='Exclude dir names (repeatable)')
    args = ap.parse_args()

    root = Path(args.root).resolve()
    project_root = Path(__file__).resolve().parents[2]
    red = load_redactor(project_root.parent)

    binary_ext = {'.db','.sqlite','.sqlite3','.jpg','.jpeg','.png','.gif','.bmp','.ico','.webp','.pdf','.doc','.docx','.xls','.xlsx','.zip','.tar','.gz','.bz2','.7z','.rar','.exe','.dll','.so','.dylib','.bin','.dat','.pyc','.pyo'}
    files = [p for p in root.rglob('*') if p.is_file() and p.suffix.lower() not in binary_ext and not any(ex in p.parts for ex in args.exclude)]

    total = 0
    usable = 0
    comp = 0
    sev = {'ERROR':0,'WARNING':0,'NOTE':0}

    for f in files:
        try:
            dets = red.scan_file(f)
            for d in dets:
                total += 1
                cls = d.get('classification','usable')
                if cls == 'component':
                    comp += 1
                else:
                    usable += 1
                # derive severity like CLI (simplified)
                rel = float(d.get('relationship_score') or 0.0)
                pat = d.get('pattern','')
                always_error = {
                    'PRIVATE_KEY_REDACTED', 'OPENSSH_PRIVATE_REDACTED', 'PASSWORD_REDACTED',
                    'JSON_PASSWORD_REDACTED', 'PHP_PASSWORD_REDACTED', 'AWS_SECRET_REDACTED',
                    'JWT_REDACTED', 'GITHUB_PAT_REDACTED', 'NPM_TOKEN_REDACTED',
                }
                if pat in always_error or (rel >= 0.75 and cls == 'usable'):
                    sev['ERROR'] += 1
                elif rel >= 0.5:
                    sev['WARNING'] += 1
                else:
                    sev['NOTE'] += 1
        except Exception:
            pass

    out = {
        'root': str(root),
        'files': len(files),
        'detections': total,
        'usable': usable,
        'components': comp,
        'severity': sev,
    }
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()

