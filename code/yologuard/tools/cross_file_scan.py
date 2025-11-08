#!/usr/bin/env python3
"""
Experimental cross-file linking scan.

Runs the redactor, then annotates detections with cross-file relationships when
likely siblings (e.g., USER/PASSWORD, KEY/SECRET, ENDPOINT/TOKEN) are found in
other files within the repository.

Usage:
  python3 infrafabric/code/yologuard/tools/cross_file_scan.py --root /path/to/repo --json out.json
"""
import argparse, json
from pathlib import Path
import re
import importlib.util


def load_redactor(project_root: Path):
    src = project_root / 'code' / 'yologuard' / 'src' / 'IF.yologuard_v3.py'
    spec = importlib.util.spec_from_file_location('yologuard_v3', str(src))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.SecretRedactorV3()


def build_key_index(files):
    # Index likely config keys per file
    key_index = {}
    key_re = re.compile(r'(?i)\b([A-Z0-9_]{3,})\b')
    for f in files:
        try:
            txt = f.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        keys = set(k for k in key_re.findall(txt) if len(k) >= 4)
        key_index[str(f)] = keys
    return key_index


def crossfile_annotate(detections, key_index):
    # Very simple heuristic: if a detection occurs in file A and we find a
    # sibling key in file B (e.g., PASSWORD with USERNAME present), mark a
    # crossfile-sibling relation.
    def sibling_of(pattern_label, keys):
        p = pattern_label.upper()
        if 'PASSWORD' in p or 'SECRET' in p:
            return any(k in keys for k in ('USER', 'USERNAME', 'ACCOUNT'))
        if 'KEY' in p and 'SECRET' not in p:
            return any(k in keys for k in ('SECRET', 'TOKEN'))
        if 'TOKEN' in p or 'JWT' in p:
            return any(k in keys for k in ('SESSION', 'TIMEOUT', 'EXP', 'COOKIE'))
        if 'CERT' in p:
            return any(k in keys for k in ('CA', 'AUTHORITY', 'ISSUER'))
        return False

    for d in detections:
        f = d.get('file')
        if not f:
            continue
        rels = d.get('relations', []) or d.get('relationships', []) or []
        # Scan other files for sibling hints
        for other_file, keys in key_index.items():
            if other_file == f:
                continue
            if sibling_of(d.get('pattern',''), keys):
                rels = list(set(rels + ['crossfile-sibling']))
                d['relations'] = rels
                # bump severity if currently NOTE
                sev = (d.get('severity') or 'NOTE').upper()
                if sev == 'NOTE':
                    d['severity'] = 'WARNING'
                break
    return detections


def main():
    ap = argparse.ArgumentParser(description='IF.yologuard cross-file linking scan (experimental)')
    ap.add_argument('--root', required=True, help='Directory to scan')
    ap.add_argument('--json', required=True, help='Write detections to JSON file')
    args = ap.parse_args()

    root = Path(args.root).resolve()
    project_root = Path(__file__).resolve().parents[2]
    red = load_redactor(project_root.parent)

    binary_ext = {'.db','.sqlite','.sqlite3','.jpg','.jpeg','.png','.gif','.bmp','.ico','.webp','.pdf','.doc','.docx','.xls','.xlsx','.zip','.tar','.gz','.bz2','.7z','.rar','.exe','.dll','.so','.dylib','.bin','.dat','.pyc','.pyo'}
    files = [p for p in root.rglob('*') if p.is_file() and p.suffix.lower() not in binary_ext and '.git' not in p.parts]

    dets = []
    for f in files:
        try:
            dets.extend(red.scan_file(f))
        except Exception:
            pass

    key_index = build_key_index(files)
    dets2 = crossfile_annotate(dets, key_index)

    with open(args.json, 'w') as out:
        json.dump(dets2, out, indent=2)
    print(f"Wrote annotated detections to: {args.json}")

if __name__ == '__main__':
    main()

