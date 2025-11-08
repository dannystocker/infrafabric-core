#!/usr/bin/env python3
import argparse, json
from pathlib import Path
import importlib.util


def load_redactor(root: Path):
    src = root / 'code' / 'yologuard' / 'src' / 'IF.yologuard_v3.py'
    spec = importlib.util.spec_from_file_location('yologuard_v3', str(src))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.SecretRedactorV3()


def scan_dir(red, root: Path):
    binary_ext = {'.db','.sqlite','.sqlite3','.jpg','.jpeg','.png','.gif','.bmp','.ico','.webp','.pdf','.doc','.docx','.xls','.xlsx','.zip','.tar','.gz','.bz2','.7z','.rar','.exe','.dll','.so','.dylib','.bin','.dat','.pyc','.pyo'}
    files = [p for p in root.rglob('*') if p.is_file() and p.suffix.lower() not in binary_ext and '.git' not in p.parts]
    dets = []
    for f in files:
        try:
            dets.extend(red.scan_file(f))
        except Exception:
            pass
    return dets


def classify(dets, error_th, warn_th):
    always_error = {
        'PRIVATE_KEY_REDACTED', 'OPENSSH_PRIVATE_REDACTED', 'PASSWORD_REDACTED',
        'JSON_PASSWORD_REDACTED', 'PHP_PASSWORD_REDACTED', 'AWS_SECRET_REDACTED',
        'JWT_REDACTED', 'GITHUB_PAT_REDACTED', 'NPM_TOKEN_REDACTED',
    }
    sev = {'ERROR':0,'WARNING':0,'NOTE':0}
    for d in dets:
        rel = float(d.get('relationship_score') or 0.0)
        pat = d.get('pattern','')
        cls = d.get('classification','usable')
        if pat in always_error:
            sev['ERROR'] += 1
        elif rel >= error_th and cls == 'usable':
            sev['ERROR'] += 1
        elif rel >= warn_th:
            sev['WARNING'] += 1
        else:
            sev['NOTE'] += 1
    return sev


def main():
    ap = argparse.ArgumentParser(description='Threshold sweep for severity mapping')
    ap.add_argument('--root', required=True, help='Directory to scan')
    ap.add_argument('--errors', nargs='*', type=float, default=[0.6, 0.7, 0.75, 0.8], help='Error thresholds to test')
    ap.add_argument('--warns', nargs='*', type=float, default=[0.4, 0.5, 0.6], help='Warning thresholds to test')
    ap.add_argument('--json', help='Write JSON grid to file')
    args = ap.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    red = load_redactor(project_root.parent)
    dets = scan_dir(red, Path(args.root).resolve())

    grid = []
    for e in args.errors:
        for w in args.warns:
            sev = classify(dets, e, w)
            grid.append({'error_th': e, 'warn_th': w, 'severity': sev, 'detections': len(dets)})

    print(json.dumps({'root': args.root, 'grid': grid}, indent=2))
    if args.json:
        with open(args.json, 'w') as f:
            json.dump({'root': args.root, 'grid': grid}, f, indent=2)

if __name__ == '__main__':
    main()

