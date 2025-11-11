#!/usr/bin/env python3
import sys, json, yaml, argparse
from pathlib import Path

def load_yaml(p): return yaml.safe_load(Path(p).read_text(encoding="utf-8"))

def lint_persona(p):
    try:
        data = load_yaml(p)
    except Exception as e:
        return [{"ok": False, "msg": f"persona parse error: {e}"}]
    out=[]
    if "personas" not in data: return [{"ok": False, "msg": "root.personas missing"}]
    req = ["id","uri","version","archetype"]
    for pid,spec in data["personas"].items():
        miss=[k for k in req if k not in spec]
        out.append({"ok": not miss, "msg": f"persona[{pid}] OK" if not miss else f"persona[{pid}] missing {miss}"})
    return out

def lint_philosophy(p):
    try:
        data = load_yaml(p)
    except Exception as e:
        return [{"ok": False, "msg": f"philosophy parse error: {e}"}]
    out=[]
    if "philosophers" not in data: return [{"ok": False, "msg": "root.philosophers missing"}]
    req=["name","tradition","era","key_concept","if_components","if_principles","practical_application"]
    for k,spec in data["philosophers"].items():
        miss=[r for r in req if r not in spec]
        out.append({"ok": not miss, "msg": f"philosophers[{k}] OK" if not miss else f"philosophers[{k}] missing {miss}"})
    return out

def lint_guard(p):
    try:
        data = load_yaml(p)
    except Exception as e:
        return [{"ok": False, "msg": f"guard parse error: {e}"}]
    c = data.get("if.guard.constitution", {})
    checks = [
        ("council_size", lambda v: isinstance(v,int) and v>0),
        ("approval_threshold", lambda v: 0<v<=1),
        ("supermajority_advice", lambda v: 0<v<=1),
        ("contrarian_veto_threshold", lambda v: 0<v<=1),
    ]
    out=[]
    for k,pred in checks:
        v=c.get(k)
        out.append({"ok": pred(v), "msg": f"guard.{k}={v} valid"})
    return out

def lint_aliases(p):
    try:
        data = load_yaml(p)
    except Exception as e:
        return [{"ok": False, "msg": f"aliases parse error: {e}"}]
    aliases=data.get("aliases",{})
    bad=[k for k,v in aliases.items() if k==v]
    return [{"ok": len(bad)==0, "msg": f"no self-alias collisions: {bad}"}]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["lint"])
    ap.add_argument("--persona", default="FINAL.IF.persona-registry.yaml")
    ap.add_argument("--philosophy", default="FINAL.IF.philosophy-database.yaml")
    ap.add_argument("--guard", default="FIX.guard-constitution.yaml")
    ap.add_argument("--aliases", default="FIX.component-canonicalization.yaml")
    args=ap.parse_args()

    results=[]
    results+=lint_persona(args.persona)
    results+=lint_philosophy(args.philosophy)
    results+=lint_guard(args.guard)
    results+=lint_aliases(args.aliases)
    okc=sum(1 for r in results if r["ok"]); fc=len(results)-okc
    print(json.dumps({"ok": fc==0, "ok_checks": okc, "fail_checks": fc, "results": results}, indent=2))
    sys.exit(0 if fc==0 else 2)

if __name__=="__main__":
    main()
