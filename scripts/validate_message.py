#!/usr/bin/env python3
import json, sys
from pathlib import Path

def main():
    if len(sys.argv) < 3:
        print("Usage: validate_message.py <schema.json> <message.json>")
        sys.exit(2)
    schema_path = Path(sys.argv[1])
    msg_path = Path(sys.argv[2])
    try:
        import jsonschema  # type: ignore
    except Exception:
        print("ERROR: jsonschema not installed. pip install jsonschema", file=sys.stderr)
        sys.exit(3)
    schema = json.loads(schema_path.read_text())
    msg = json.loads(msg_path.read_text())
    jsonschema.validate(msg, schema)
    print(f"✅ Valid: {msg_path} against {schema_path}")

if __name__ == '__main__':
    main()

