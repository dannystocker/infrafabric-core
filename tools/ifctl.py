#!/usr/bin/env python3
import sys, json, yaml, argparse
from pathlib import Path
def Y(p): return yaml.safe_load(Path(p).read_text(encoding='utf-8'))
def check_keys(d, req): return [k for k in req if k not in d]
def lint_persona_registry(p):
    out=[]; data=Y(p)
    if 'personas' not in data: return [{'ok': False, 'msg':'root.personas missing'}]
    for pid, spec in data['personas'].items():
        miss = check_keys(spec, ['id','uri','version','archetype'])
        out.append({'ok': not miss, 'msg': f'persona[{pid}] ' + ('OK' if not miss else f'missing {miss}')})
    return out
def lint_philosophy_db(p):
    out=[]; data=Y(p)
    if 'philosophers' not in data: return [{'ok': False, 'msg':'root.philosophers missing'}]
    req=['name','tradition','era','key_concept','if_components','if_principles','practical_application']
    for k,spec in data['philosophers'].items():
        miss = check_keys(spec, req)
        out.append({'ok': not miss, 'msg': f'philosophers[{k}] ' + ('OK' if not miss else f'missing {miss}')})
    return out
def lint_guard(p):
    c = Y(p).get('if.guard.constitution',{})
    checks=[
        ('council_size', isinstance(c.get('council_size'),int) and c.get('council_size')>0),
        ('approval_threshold', 0< c.get('approval_threshold',0)<=1),
        ('supermajority_advice', 0< c.get('supermajority_advice',0)<=1),
        ('contrarian_veto_threshold', 0< c.get('contrarian_veto_threshold',0)<=1)
    ]
    return [{'ok': ok, 'msg': f'guard.{k} valid'} for k,ok in checks]
def lint_aliases(p):
    a = Y(p).get('aliases',{}); bad=[k for k,v in a.items() if k==v]
    return [{'ok': len(bad)==0, 'msg': f'no self-alias collisions: {bad}'}]
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['lint'])
    ap.add_argument('--persona', default='FINAL.IF.persona-registry.yaml')
    ap.add_argument('--philosophy', default='FINAL.IF.philosophy-database.yaml')
    ap.add_argument('--guard', default='FIX.guard-constitution.yaml')
    ap.add_argument('--aliases', default='FIX.component-canonicalization.yaml')
    args=ap.parse_args()
    results=[]
    results += lint_persona_registry(args.persona)
    results += lint_philosophy_db(args.philosophy)
    results += lint_guard(args.guard)
    results += lint_aliases(args.aliases)
    okc=sum(1 for r in results if r['ok']); fc=len(results)-okc
    print(json.dumps({'ok': fc==0, 'ok_checks': okc, 'fail_checks': fc, 'results': results}, indent=2))
    sys.exit(0 if fc==0 else 2)
if __name__=='__main__': main()
