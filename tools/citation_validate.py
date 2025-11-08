#!/usr/bin/env python3
import json, sys
from pathlib import Path

def main():
    if len(sys.argv) < 3:
        print("Usage: citation_validate.py <schema.json> <citation.json>")
        sys.exit(2)
    try:
        import jsonschema
    except Exception:
        print("Install jsonschema: pip install jsonschema")
        sys.exit(3)
    schema = json.loads(Path(sys.argv[1]).read_text())
    data = json.loads(Path(sys.argv[2]).read_text())
    jsonschema.validate(data, schema)
    print("✅ Citation valid")

if __name__ == '__main__':
    main()
