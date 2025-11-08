#!/usr/bin/env python3
import argparse, json, time
from pathlib import Path
import importlib.util


def load_redactor(root: Path):
    src = root / 'code' / 'yologuard' / 'src' / 'IF.yologuard_v3.py'
    spec = importlib.util.spec_from_file_location('yologuard_v3', str(src))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.SecretRedactorV3()


def main():
    ap = argparse.ArgumentParser(description='IF.yologuard FP evaluator (assumes clean corpus)')
    ap.add_argument('--root', required=True, help='Directory to scan recursively')
    ap.add_argument('--exclude', action='append', default=['.git', 'node_modules', 'dist', 'build'], help='Exclude dirs (repeatable)')
    ap.add_argument('--json', help='Write JSON report to file')
    args = ap.parse_args()

    root = Path(args.root).resolve()
    project_root = Path(__file__).resolve().parents[2]
    redactor = load_redactor(project_root.parent)

    binary_ext = {'.db','.sqlite','.sqlite3','.jpg','.jpeg','.png','.gif','.bmp','.ico','.webp','.pdf','.doc','.docx','.xls','.xlsx','.zip','.tar','.gz','.bz2','.7z','.rar','.exe','.dll','.so','.dylib','.bin','.dat','.pyc','.pyo'}

    files = [p for p in root.rglob('*') if p.is_file() and p.suffix.lower() not in binary_ext and not any(ex in p.parts for ex in args.exclude)]
    start = time.time()
    total_dets = 0
    bytes_scanned = 0
    for f in files:
        try:
            s = f.stat().st_size
            bytes_scanned += s
            dets = redactor.scan_file(f)
            total_dets += len(dets)
        except Exception:
            pass
    dur = time.time() - start

    report = {
        'root': str(root),
        'files': len(files),
        'bytes_scanned': bytes_scanned,
        'detections': total_dets,
        'detections_per_1k_files': (total_dets / len(files) * 1000) if files else 0.0,
        'detections_per_mb': (total_dets / (bytes_scanned/1_000_000)) if bytes_scanned else 0.0,
        'duration_sec': round(dur, 3),
    }

    print(json.dumps(report, indent=2))
    if args.json:
        with open(args.json, 'w') as f:
            json.dump(report, f, indent=2)

if __name__ == '__main__':
    main()

