#!/usr/bin/env python3
"""
Head-to-head runner: IF.yologuard vs other tools (if installed).

Currently supports:
  - IF.yologuard (built-in)
  - TruffleHog (if `trufflehog` in PATH) -> JSON lines mode

Usage:
  python3 head2head.py --config corpus_config.json --workdir /tmp/yolo-corpus --json comparison.json --md comparison.md
"""
import argparse, json, shutil, subprocess, sys, time
from pathlib import Path
import importlib.util


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def load_redactor(root: Path):
    src = root / 'code' / 'yologuard' / 'src' / 'IF.yologuard_v3.py'
    spec = importlib.util.spec_from_file_location('yologuard_v3', str(src))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.SecretRedactorV3()


def get_files(repo_dir: Path, exclude, binary_ext):
    ex = set(exclude)
    be = set(binary_ext)
    return [p for p in repo_dir.rglob('*') if p.is_file() and p.suffix.lower() not in be and not any(e in p.parts for e in ex)]


def scan_if(red, repo_dir: Path, files):
    count = 0
    start = time.time()
    for f in files:
        try:
            count += len(red.scan_file(f))
        except Exception:
            pass
    dur = time.time() - start
    return {'detections': count, 'duration_sec': round(dur,3)}


def scan_trufflehog(repo_dir: Path):
    if not shutil.which('trufflehog'):
        return {'detections': None, 'duration_sec': None, 'skipped': 'trufflehog not installed'}
    start = time.time()
    proc = run(['trufflehog','filesystem','--directory',str(repo_dir),'--json'])
    dur = time.time() - start
    dets = 0
    # Parse JSON lines (ignore parse errors)
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            dets += 1
        except Exception:
            continue
    return {'detections': dets, 'duration_sec': round(dur,3)}


def scan_gitleaks(repo_dir: Path):
    import tempfile, os
    exe = shutil.which('gitleaks')
    if not exe:
        return {'detections': None, 'duration_sec': None, 'skipped': 'gitleaks not installed'}
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'gitleaks.json'
        start = time.time()
        # --no-banner for cleaner output; --redact to avoid printing secrets
        proc = run(['gitleaks','detect','--source',str(repo_dir),
                    '--report-format','json','--report-path',str(out),
                    '--no-banner','--redact'])
        dur = time.time() - start
        dets = 0
        try:
            if out.exists():
                data = json.load(open(out))
                if isinstance(data, dict) and 'leaks' in data and isinstance(data['leaks'], list):
                    dets = len(data['leaks'])
                elif isinstance(data, list):
                    dets = len(data)
        except Exception:
            pass
    return {'detections': dets, 'duration_sec': round(dur,3)}


def main():
    ap = argparse.ArgumentParser(description='Head-to-head corpus comparison')
    ap.add_argument('--config', default=str(Path(__file__).with_name('corpus_config.json')), help='JSON config with repos/exclude/binary_ext')
    ap.add_argument('--workdir', default='/tmp/yolo-corpus', help='Working directory for clones')
    ap.add_argument('--json', help='Write comparison JSON report')
    ap.add_argument('--md', help='Write comparison Markdown table')
    args = ap.parse_args()

    cfg = json.load(open(args.config))
    repos = cfg.get('repos', [])
    exclude = cfg.get('exclude', [])
    binary_ext = cfg.get('binary_ext', [])

    workdir = Path(args.workdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)

    project_root = Path(__file__).resolve().parents[2]
    red = load_redactor(project_root.parent)

    rows = []
    for entry in repos:
        url = entry['url']
        name = url.rsplit('/',1)[-1].replace('.git','')
        dest = workdir / name
        if dest.exists():
            run(['git','-C',str(dest),'fetch','--depth','1','origin'])
            run(['git','-C',str(dest),'reset','--hard','origin/HEAD'])
        else:
            run(['git','clone','--depth','1',url,str(dest)])

        files = get_files(dest, exclude, binary_ext)
        if_result = scan_if(red, dest, files)
        th_result = scan_trufflehog(dest)
        gl_result = scan_gitleaks(dest)

        rows.append({
            'repo': url,
            'files': len(files),
            'if_detections': if_result['detections'],
            'if_duration_sec': if_result['duration_sec'],
            'trufflehog_detections': th_result['detections'],
            'trufflehog_duration_sec': th_result['duration_sec'],
            'trufflehog_note': th_result.get('skipped'),
            'gitleaks_detections': gl_result['detections'],
            'gitleaks_duration_sec': gl_result['duration_sec'],
            'gitleaks_note': gl_result.get('skipped')
        })

    report = {
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'rows': rows
    }
    print(json.dumps(report, indent=2))
    if args.json:
        with open(args.json,'w') as f:
            json.dump(report,f,indent=2)
    if args.md:
        with open(args.md,'w') as f:
            f.write('| Repo | Files | IF.dets | IF.sec | TH.dets | TH.sec | GL.dets | GL.sec |\n')
            f.write('|------|-------|---------|--------|---------|--------|---------|--------|\n')
            for r in rows:
                f.write(f"| {r['repo']} | {r['files']} | {r['if_detections']} | {r['if_duration_sec']} | {r['trufflehog_detections']} | {r['trufflehog_duration_sec']} | {r['gitleaks_detections']} | {r['gitleaks_duration_sec']} |\n")

if __name__ == '__main__':
    main()
