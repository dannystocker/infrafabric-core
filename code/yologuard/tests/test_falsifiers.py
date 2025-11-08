#!/usr/bin/env python3
"""
Simple falsifier checks for IF.yologuard v3.
These aim to catch common near-misses that should NOT be flagged as secrets.
Run with: python3 -m pytest -q (if pytest is available), otherwise run directly.
"""
from pathlib import Path
import importlib.util


def load_redactor():
    src = Path(__file__).resolve().parents[1] / 'src' / 'IF.yologuard_v3.py'
    spec = importlib.util.spec_from_file_location('yologuard_v3', str(src))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.SecretRedactorV3()


def scan_text(redactor, text: str) -> int:
    # Use internal pipeline to scan raw text
    matches = redactor.predecode_and_rescan(text)
    return len(matches)


def test_falsifiers_basic():
    r = load_redactor()

    cases = [
        # Random-looking but benign
        'a3f5c7d9e1b2c3d4e5f60718293a4b5c6d7e8f90',  # hex-ish
        '123e4567-e89b-12d3-a456-426614174000',        # UUID v4
        'commit 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b',  # git sha
        'eyJzb21lIjoiYmFzZTY0LWxpa2UifQ==',             # harmless base64
        'user_id=42&session=abcd1234',                 # params without tokens
    ]

    for s in cases:
        assert scan_text(r, s) == 0


if __name__ == '__main__':
    test_falsifiers_basic()
    print('Falsifier tests passed')

