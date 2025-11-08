#!/usr/bin/env python3
"""
Corpus Evaluation: clones a small set of public repos and runs FP/perf metrics.

Default repos (shallow clone):
  - https://github.com/psf/requests.git
  - https://github.com/pallets/flask.git

Usage:
  python3 corpus_eval.py --workdir /tmp/yolo-corpus --json corpus_report.json
"""
import argparse, json, subprocess, sys, time
from pathlib import Path
import importlib.util


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def load_redactor(project_root: Path):
    src = project_root / 'code' / 'yologuard' / 'src' / 'IF.yologuard_v3.py'
    spec = importlib.util.spec_from_file_location('yologuard_v3', str(src))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.SecretRedactorV3()


def scan_repo(redactor, path: Path):
    binary_ext = {'.db','.sqlite','.sqlite3','.jpg','.jpeg','.png','.gif','.bmp','.ico','.webp','.pdf','.doc','.docx','.xls','.xlsx','.zip','.tar','.gz','.bz2','.7z','.rar','.exe','.dll','.so','.dylib','.bin','.dat','.pyc','.pyo'}
    exclude = {'.git', 'node_modules', 'dist', 'build'}
    files = [p for p in path.rglob('*') if p.is_file() and p.suffix.lower() not in binary_ext and not any(ex in p.parts for ex in exclude)]
    start = time.time()
    bytes_scanned = 0
    dets = 0
    for f in files:
        try:
            bytes_scanned += f.stat().st_size
            dets += len(redactor.scan_file(f))
        except Exception:
            pass
    dur = time.time() - start
    return {
        'files': len(files),
        'bytes_scanned': bytes_scanned,
        'detections': dets,
        'duration_sec': round(dur, 3),
        'files_per_sec': round(len(files)/dur, 2) if dur else None,
        'mb_per_sec': round((bytes_scanned/1_000_000)/dur, 2) if dur else None,
    }


def main():
    ap = argparse.ArgumentParser(description='IF.yologuard corpus FP/perf evaluation')
    ap.add_argument('--workdir', default='/tmp/yolo-corpus', help='Working directory to clone repos')
    ap.add_argument('--json', help='Write JSON report path')
    ap.add_argument('--repos', nargs='*', help='Repo URLs (default: requests, flask)')
    args = ap.parse_args()

    workdir = Path(args.workdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    repos = args.repos or [
        'https://github.com/psf/requests.git',
        'https://github.com/pallets/flask.git',
    ]

    project_root = Path(__file__).resolve().parents[2]
    red = load_redactor(project_root.parent)

    results = []
    for url in repos:
        name = url.rsplit('/', 1)[-1].replace('.git','')
        dest = workdir / name
        if dest.exists():
            # refresh
            run(['git','-C', str(dest), 'fetch', '--depth','1','origin'])
            run(['git','-C', str(dest), 'reset', '--hard','origin/HEAD'])
        else:
            run(['git','clone','--depth','1', url, str(dest)])
        metrics = scan_repo(red, dest)
        results.append({'repo': url, **metrics})

    report = {
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'workdir': str(workdir),
        'repos': results,
        'summary': {
            'total_repos': len(results),
            'total_files': sum(r['files'] for r in results),
            'total_detections': sum(r['detections'] for r in results),
            'avg_files_per_sec': round(sum(r['files_per_sec'] or 0 for r in results)/len(results),2),
        }
    }
    print(json.dumps(report, indent=2))
    if args.json:
        with open(args.json,'w') as f:
            json.dump(report, f, indent=2)

if __name__ == '__main__':
    main()

