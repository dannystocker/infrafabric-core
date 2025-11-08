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
    ap = argparse.ArgumentParser(description='IF.yologuard performance benchmark')
    ap.add_argument('--root', required=True, help='Directory to scan recursively')
    ap.add_argument('--max-bytes', type=int, default=100_000_000, help='Max bytes to read (soft cap)')
    ap.add_argument('--json', help='Write JSON report to file')
    args = ap.parse_args()

    root = Path(args.root).resolve()
    project_root = Path(__file__).resolve().parents[2]
    redactor = load_redactor(project_root.parent)

    binary_ext = {'.db','.sqlite','.sqlite3','.jpg','.jpeg','.png','.gif','.bmp','.ico','.webp','.pdf','.doc','.docx','.xls','.xlsx','.zip','.tar','.gz','.bz2','.7z','.rar','.exe','.dll','.so','.dylib','.bin','.dat','.pyc','.pyo'}
    files = [p for p in root.rglob('*') if p.is_file() and p.suffix.lower() not in binary_ext]

    total_dets = 0
    bytes_scanned = 0
    files_scanned = 0
    start = time.time()
    for f in files:
        if bytes_scanned > args.max_bytes:
            break
        try:
            s = f.stat().st_size
            with open(f, 'rb') as _:
                pass
            dets = redactor.scan_file(f)
            bytes_scanned += s
            files_scanned += 1
            total_dets += len(dets)
        except Exception:
            pass
    dur = time.time() - start

    report = {
        'root': str(root),
        'files_scanned': files_scanned,
        'bytes_scanned': bytes_scanned,
        'detections': total_dets,
        'duration_sec': round(dur, 3),
        'files_per_sec': round(files_scanned / dur, 2) if dur else None,
        'mb_per_sec': round((bytes_scanned/1_000_000) / dur, 2) if dur else None,
    }

    print(json.dumps(report, indent=2))
    if args.json:
        with open(args.json, 'w') as f:
            json.dump(report, f, indent=2)

if __name__ == '__main__':
    main()

