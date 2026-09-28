"""Resolve only Stage 2 specialists; returns real instruction paths, not execution."""
from pathlib import Path
import argparse,json,yaml,os
SKILL=Path(__file__).resolve().parents[1]
MANIFEST=yaml.safe_load((SKILL/'manifest.yaml').read_text())
def resolve(name):
    if name not in MANIFEST['allowed_specialists']:raise ValueError('OUTSIDE_STAGE_2: '+name)
    local=Path(os.environ.get('CODEX_HOME', str(Path.home()/'.codex')))/'skills'/name
    if (local/'SKILL.md').is_file():return local.resolve()
    vendor=SKILL.parents[1]/'vendor/nature-skills/skills'/name
    if (vendor/'SKILL.md').is_file():return vendor
    raise FileNotFoundError('SPECIALIST_UNAVAILABLE: '+name)
def route(name,paper_type='original_research',section='experiments'):
    root=resolve(name);paths=[root/'SKILL.md']
    if name=='nature-writing':
        m=yaml.safe_load((root/'manifest.yaml').read_text());paths += [root/'manifest.yaml']+[root/p for p in m['always_load']]
        axes={'task':'manuscript','paper_type':MANIFEST['paper_types'][paper_type]['nature_writing_type'],'section':section,'journal':'generic','language':'en'}
        paths += [root/m['axes'][k]['values'][v] for k,v in axes.items()]
    for p in paths:
        if not p.is_file():raise FileNotFoundError(str(p))
    return {'specialist':name,'paths':[str(p.resolve()) for p in paths],'executed':False,
            'instruction':'Read these resources and apply them to the approved brief. Override generic journal/language with actual user context.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('specialist');p.add_argument('--paper-type',default='original_research',choices=list(MANIFEST['paper_types']));p.add_argument('--section',default='experiments');a=p.parse_args()
    print(json.dumps(route(a.specialist,a.paper_type,a.section),ensure_ascii=False,indent=2))
