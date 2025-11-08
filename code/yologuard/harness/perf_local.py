#!/usr/bin/env python3
"""
Local performance check for IF.yologuard.
Measures files/sec and MB/sec on a target directory without changing thresholds.
"""
import argparse, json, time
from pathlib import Path
import importlib.util

def load_redactor(root: Path):
    src = root / "code" / "yologuard" / "src" / "IF.yologuard_v3.py"
    spec = importlib.util.spec_from_file_location("yologuard_v3", str(src))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.SecretRedactorV3()

def main():
    ap = argparse.ArgumentParser(description="Local perf check")
    ap.add_argument("--root", required=True, help="Directory to scan")
    ap.add_argument("--max-files", type=int, default=0, help="Optional limit of files")
    ap.add_argument("--json", help="Write JSON report")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    repo = Path(args.root).resolve()
    red = load_redactor(root)

    files = [p for p in repo.rglob("*") if p.is_file()]
    if args.max_files and len(files) > args.max_files:
        files = files[:args.max_files]

    bytes_scanned = 0
    detections = 0
    start = time.time()
    for f in files:
        try:
            bytes_scanned += f.stat().st_size
            detections += len(red.scan_file(f))
        except Exception:
            pass
    dur = max(time.time() - start, 1e-6)

    report = {
        "files": len(files),
        "bytes_scanned": bytes_scanned,
        "duration_sec": round(dur,3),
        "files_per_sec": round(len(files)/dur,1),
        "mb_per_sec": round((bytes_scanned/1_000_000)/dur,2),
        "detections": detections,
    }
    print(json.dumps(report, indent=2))
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
